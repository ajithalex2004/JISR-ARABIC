"""Minimal Stripe REST client (form-encoded HTTPS, no SDK dependency).

Configured with STRIPE_SECRET_KEY. Only the calls the app needs: hosted Checkout Sessions (one-off
payments and auto-renewing subscriptions), one-time promo coupons, subscription updates and refunds.
"""
import os
from urllib.parse import urlencode
from typing import Any, Dict, List, Tuple

from backend.errors import ApplicationError

API = "https://api.stripe.com/v1"


def secret_key() -> str:
    return os.getenv("STRIPE_SECRET_KEY", "").strip()


def enabled() -> bool:
    return os.getenv("FAHIM_PAYMENT_PROVIDER", "").strip().lower() == "stripe" and bool(secret_key())


def _flatten(value: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """{"a": {"b": [1]}} -> [("a[b][0]", "1")] as Stripe expects."""
    out: List[Tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            out.extend(_flatten(item, f"{prefix}[{key}]" if prefix else str(key)))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            out.extend(_flatten(item, f"{prefix}[{index}]"))
    elif isinstance(value, bool):
        out.append((prefix, "true" if value else "false"))
    elif value is not None:
        out.append((prefix, str(value)))
    return out


def request(method: str, path: str, params: Dict[str, Any] | None = None, *, idempotency_key: str | None = None) -> dict:
    import httpx

    key = secret_key()
    if not key:
        raise ApplicationError(503, "Online card payments are not set up yet (STRIPE_SECRET_KEY is missing).")
    headers = {"Authorization": f"Bearer {key}"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    # Encoded here: httpx's `data=` takes only a dict, and Stripe's nested keys need repeated pairs.
    body = None
    if method.upper() == "GET":
        path = f"{path}?{urlencode(_flatten(params))}" if params else path
    else:
        body = urlencode(_flatten(params or {}))
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        response = httpx.request(method, f"{API}{path}", content=body, headers=headers, timeout=30)
    except httpx.HTTPError as exc:
        raise ApplicationError(502, f"Could not reach the payment provider: {exc}") from exc
    data = response.json() if response.content else {}
    if response.status_code >= 400:
        error = (data or {}).get("error") or {}
        raise ApplicationError(502 if response.status_code >= 500 else 400,
                               f"Payment provider error: {error.get('message') or response.text[:200]}")
    return data


def create_checkout_session(params: Dict[str, Any], *, idempotency_key: str | None = None) -> dict:
    return request("POST", "/checkout/sessions", params, idempotency_key=idempotency_key)


def ensure_once_coupon(percent_off: float) -> str:
    """A coupon for `percent_off`% off the first payment only (re-used across promo codes)."""
    pct = round(float(percent_off), 2)
    coupon_id = f"JISR-ONCE-{str(pct).replace('.', '_')}"
    try:
        request("GET", f"/coupons/{coupon_id}")
    except ApplicationError:
        request("POST", "/coupons", {"id": coupon_id, "percent_off": pct, "duration": "once",
                                     "name": f"{pct:g}% off the first payment"})
    return coupon_id


def update_subscription(subscription_id: str, params: Dict[str, Any]) -> dict:
    return request("POST", f"/subscriptions/{subscription_id}", params)


# --- refunds ----------------------------------------------------------------------------------

def invoice_payment_intent(invoice: Dict[str, Any]) -> str | None:
    """The payment intent that paid an invoice, on older (`payment_intent`) and newer (`payments`) API versions."""
    if invoice.get("payment_intent"):
        pi = invoice["payment_intent"]
        return pi.get("id") if isinstance(pi, dict) else pi
    for item in ((invoice.get("payments") or {}).get("data") or []):
        payment = item.get("payment") or {}
        if item.get("status") in (None, "paid") and payment.get("payment_intent"):
            pi = payment["payment_intent"]
            return pi.get("id") if isinstance(pi, dict) else pi
    return None


def refund_target(provider_ref: str, payment_intent: str | None = None) -> Dict[str, str]:
    """What to refund for a recorded payment: {"payment_intent": ...} or {"charge": ...}.

    `provider_ref` is what the app stored when the payment was confirmed: a Checkout Session (cs_),
    an invoice (in_, subscription payments), a payment intent (pi_) or a charge (ch_).
    """
    if payment_intent:
        return {"payment_intent": payment_intent}
    ref = provider_ref or ""
    if ref.startswith("pi_"):
        return {"payment_intent": ref}
    if ref.startswith("ch_"):
        return {"charge": ref}
    if ref.startswith("cs_"):
        session = request("GET", f"/checkout/sessions/{ref}")
        pi = session.get("payment_intent")
        if pi:
            return {"payment_intent": pi.get("id") if isinstance(pi, dict) else pi}
    if ref.startswith("in_"):
        invoice = request("GET", f"/invoices/{ref}", {"expand": ["payments"]})
        pi = invoice_payment_intent(invoice)
        if pi:
            return {"payment_intent": pi}
        if invoice.get("charge"):
            return {"charge": invoice["charge"]}
    raise ApplicationError(409, f"Could not find the Stripe payment for {ref or 'this receipt'}; "
                                "refund it in the Stripe Dashboard instead.")


def create_refund(target: Dict[str, str], *, receipt_number: str) -> dict:
    """Full refund of a payment; the idempotency key makes a retried click refund only once."""
    return request("POST", "/refunds", {**target, "reason": "requested_by_customer",
                                        "metadata": {"receipt_number": receipt_number}},
                   idempotency_key=f"jisr-refund-{receipt_number}")


def purchase_refs_for(payment_intent: str) -> List[str]:
    """The Checkout Session / invoice ids that a payment intent paid (to match a refund to a receipt)."""
    refs: List[str] = []
    try:
        sessions = request("GET", "/checkout/sessions", {"payment_intent": payment_intent, "limit": 1})
        refs += [s["id"] for s in sessions.get("data") or [] if s.get("id")]
    except ApplicationError:
        pass
    if not refs:
        try:
            payments = request("GET", "/invoice_payments", {"payment": {"type": "payment_intent",
                                                                        "payment_intent": payment_intent}, "limit": 1})
            refs += [p["invoice"] for p in payments.get("data") or [] if p.get("invoice")]
        except ApplicationError:
            pass
    return refs
