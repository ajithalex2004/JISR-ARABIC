"""Minimal Stripe REST client (form-encoded HTTPS, no SDK dependency).

Configured with STRIPE_SECRET_KEY. Only the calls the app needs: hosted Checkout Sessions (one-off
payments and auto-renewing subscriptions), one-time promo coupons, and subscription updates.
"""
import os
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
    try:
        response = httpx.request(method, f"{API}{path}", data=_flatten(params or {}), headers=headers, timeout=30)
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
