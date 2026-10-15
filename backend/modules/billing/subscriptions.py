"""Checkout (one-off or auto-renewing) and the subscription lifecycle.

A parent picks one term, two terms or the full year, optionally with auto-renew:
  * term plan: USD 10, renews every 4 months and each renewal unlocks the next term (1 -> 2 -> 3,
    then Term 1 of the child's registered grade at that time);
  * annual plan: USD 25.50 (30 less 15%), renews every 12 months and unlocks all three terms of the
    child's registered grade at that time.
A promo code applies to the first payment only.

With Stripe configured (FAHIM_PAYMENT_PROVIDER=stripe and STRIPE_SECRET_KEY) the parent pays on
Stripe's hosted page; access is unlocked by the signed webhook, which also records every renewal
with its own receipt number and UAE tax invoice. Without Stripe, outside production, checkout is
simulated so the flow can be tried end to end.
"""
import calendar
import datetime
import os
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import ChildProfile, PaymentTransaction, Subscription, TermAccess, User
from backend.modules.billing import pricing, stripe_api

CARD_SUBSCRIPTION = "card_subscription"


def _now() -> datetime.datetime:
    return datetime.datetime.utcnow()


def _is_prod() -> bool:
    return os.getenv("FAHIM_ENV", "development").lower() == "production"


def app_url() -> str:
    return (os.getenv("FAHIM_APP_URL") or "https://app.jisrarabic.com").rstrip("/")


def provider() -> str:
    if stripe_api.enabled():
        return "stripe"
    return "unavailable" if _is_prod() else "simulated"


def add_months(moment: datetime.datetime, months: int) -> datetime.datetime:
    month = moment.month - 1 + months
    year, month = moment.year + month // 12, month % 12 + 1
    return moment.replace(year=year, month=month, day=min(moment.day, calendar.monthrange(year, month)[1]))


def _plan_terms(plan: str, terms: Optional[List[int]], term: Optional[int]) -> List[int]:
    return [1, 2, 3] if plan == "annual" else pricing.clean_terms(terms, term)


def _promo_pct(code: str, parent_id, db) -> float:
    from backend.modules.billing.service import promo_pct_for
    return promo_pct_for((code or "").strip().upper(), parent_id=parent_id, db=db, is_prod=_is_prod())


def _child(child_id: str, db) -> ChildProfile:
    child = db.get(ChildProfile, child_id)
    if child is None:
        raise ApplicationError(404, "Child profile not found")
    return child


# --- quote & checkout -------------------------------------------------------------------------

def get_quote(*, child_id: str, plan: str, terms, term, promo_code: str, auto_renew: bool, db) -> dict:
    child = _child(child_id, db)
    chosen = _plan_terms(plan, terms, term)
    _check_auto_renew(chosen, auto_renew)
    price = pricing.quote(chosen, promo_pct=_promo_pct(promo_code, child.parent_id, db) if promo_code else 0.0)
    plan_name = "annual" if len(chosen) == 3 else "term"
    return {
        **price,
        "promo_code": (promo_code or "").strip().upper() or None,
        "auto_renew": auto_renew,
        "renewal_price_usd": pricing.renewal_price(plan_name) if auto_renew else None,
        "renewal_months": (pricing.ANNUAL_RENEWAL_MONTHS if plan_name == "annual" else pricing.TERM_RENEWAL_MONTHS) if auto_renew else None,
        "provider": provider(),
        "prices": pricing.price_list(),
    }


def _check_auto_renew(terms: List[int], auto_renew: bool) -> None:
    if auto_renew and len(terms) == 2:
        raise ApplicationError(400, "Auto-renew is available for one term at a time or for the full year.")


def start_checkout(*, child_id: str, grade: int, plan: str, terms, term, promo_code: str, auto_renew: bool,
                   parent: User, db: Session) -> dict:
    """Begin a purchase: a Stripe hosted-checkout URL, or (outside production, without Stripe) a simulated payment."""
    child = _child(child_id, db)
    chosen = _plan_terms(plan, terms, term)
    _check_auto_renew(chosen, auto_renew)
    promo = (promo_code or "").strip().upper()
    promo_pct = _promo_pct(promo, child.parent_id, db) if promo else 0.0
    price = pricing.quote(chosen, promo_pct=promo_pct)
    plan_name = "annual" if len(chosen) == 3 else "term"

    mode = provider()
    if mode == "stripe":
        return {"provider": "stripe", "checkout_url": _stripe_session(child, grade, chosen, plan_name, price, promo,
                                                                      promo_pct, auto_renew, parent)["url"]}
    if mode == "unavailable":
        raise ApplicationError(503, "Online card payments are not set up yet. Please use a school voucher or contact us.")

    # Simulated (development / testing without Stripe).
    if auto_renew:
        sub = Subscription(parent_id=child.parent_id, child_id=child.id, grade=grade, plan=plan_name,
                           next_term=chosen[0] if plan_name == "term" else None, status="active", provider="simulated",
                           amount_usd=pricing.renewal_price(plan_name), promo_code=promo or None)
        db.add(sub)
        db.flush()
        txn = apply_cycle(sub, amount_usd=price["total_usd"], provider_ref=f"sim-{uuid.uuid4()}", promo=promo, db=db)
        db.commit()
        _email(txn, db)
        return {"provider": "simulated", "status": "succeeded", "receipt_number": txn.receipt_number,
                "tax_invoice_number": txn.tax_invoice_number, "subscription_id": sub.id, "amount_usd": float(txn.amount_usd)}
    from backend.modules.billing.service import checkout_term
    from backend.schemas import PaymentCheckoutRequest
    result = checkout_term(PaymentCheckoutRequest(child_id=child.id, grade=grade, term=chosen[0], terms=chosen,
                                                  package_type=plan_name, promo_code=promo or None), db=db)
    return {"provider": "simulated", "status": result.status, "receipt_number": result.receipt_number,
            "tax_invoice_number": result.tax_invoice_number, "subscription_id": None, "amount_usd": result.amount_usd}


def _stripe_session(child, grade, terms, plan_name, price, promo, promo_pct, auto_renew, parent) -> dict:
    meta = {"flow": "checkout_v2", "child_id": child.id, "parent_id": child.parent_id or "", "grade": str(grade),
            "terms": ",".join(map(str, terms)), "plan": plan_name, "promo_code": promo or ""}
    label = "Annual pass (Terms 1, 2 and 3)" if plan_name == "annual" else f"Term{'s' if len(terms) > 1 else ''} {', '.join(map(str, terms))}"
    product = {"name": f"JISR Arabic - Class {grade} - {label}",
               "description": f"For {child.name}. Price includes 5% UAE VAT."}
    params = {
        "success_url": f"{app_url()}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{app_url()}/?payment=cancelled",
        "client_reference_id": child.id,
        "metadata": meta,
        "line_items": [{"quantity": 1, "price_data": {"currency": "usd", "product_data": product}}],
    }
    if parent and parent.email:
        params["customer_email"] = parent.email
    if auto_renew:
        months = pricing.ANNUAL_RENEWAL_MONTHS if plan_name == "annual" else pricing.TERM_RENEWAL_MONTHS
        params["mode"] = "subscription"
        params["line_items"][0]["price_data"]["unit_amount"] = int(round(pricing.renewal_price(plan_name) * 100))
        params["line_items"][0]["price_data"]["recurring"] = (
            {"interval": "year"} if months == 12 else {"interval": "month", "interval_count": months})
        params["subscription_data"] = {"metadata": meta}
        if promo_pct:
            params["discounts"] = [{"coupon": stripe_api.ensure_once_coupon(promo_pct)}]
    else:
        params["mode"] = "payment"
        params["line_items"][0]["price_data"]["unit_amount"] = int(round(price["total_usd"] * 100))
    return stripe_api.create_checkout_session(params)


# --- recording payments -----------------------------------------------------------------------

def _unlock(child_id: str, grade: int, terms: List[int], receipt: str, db) -> None:
    for t in terms:
        access = db.query(TermAccess).filter(TermAccess.child_id == child_id, TermAccess.grade == grade,
                                             TermAccess.term == t).first()
        if access is None:
            db.add(TermAccess(child_id=child_id, grade=grade, term=t, is_unlocked=True,
                              unlocked_at=_now(), transaction_ref=receipt))
        else:
            access.is_unlocked, access.unlocked_at, access.transaction_ref = True, _now(), receipt


def record_purchase(*, child: ChildProfile, grade: int, terms: List[int], amount_usd: float, provider_ref: str,
                    payment_method: str, promo: str = "", subscription: Optional[Subscription] = None,
                    db: Session) -> PaymentTransaction:
    """Store a confirmed payment with its receipt and tax invoice numbers, and unlock its terms (idempotent)."""
    prior = db.query(PaymentTransaction).filter(PaymentTransaction.provider_event_id == provider_ref).first()
    if prior:
        return prior
    amount = pricing.money(amount_usd)
    list_price = pricing.quote(terms)["list_price_usd"]
    subtotal, vat = pricing.tax_breakdown(amount)
    txn_id = str(uuid.uuid4())
    stamp = _now().strftime("%Y%m%d")
    txn = PaymentTransaction(
        id=txn_id, parent_id=child.parent_id, child_id=child.id, grade=grade,
        term=terms[0] if len(terms) == 1 else 0, amount_usd=amount, subtotal_usd=subtotal, vat_amount_usd=vat,
        discount_amount_usd=pricing.money(max(0.0, list_price - amount)), amount_cents=int(round(amount * 100)),
        currency="USD", package_type="annual" if len(terms) == 3 else "term", status="succeeded",
        payment_method=payment_method, card_last4=None, promo_code=promo or None,
        receipt_number=f"FHM-{stamp}-{txn_id[:8].upper()}", tax_invoice_number=f"INV-{stamp}-{txn_id[:6].upper()}",
        provider_event_id=provider_ref, terms_purchased=",".join(map(str, terms)),
        subscription_id=subscription.id if subscription else None,
    )
    db.add(txn)
    _unlock(child.id, grade, terms, txn.receipt_number, db)
    if not child.default_grade:
        child.default_grade = grade
    if promo:
        pricing.record_promo_use(promo, parent_id=child.parent_id, payment_id=txn_id, db=db)
    return txn


def apply_cycle(sub: Subscription, *, amount_usd: float, provider_ref: str, db: Session, promo: str = "",
                period_end: Optional[datetime.datetime] = None) -> PaymentTransaction:
    """One paid period of a subscription: unlock its term(s) and record the payment."""
    prior = db.query(PaymentTransaction).filter(PaymentTransaction.provider_event_id == provider_ref).first()
    if prior:
        return prior
    child = _child(sub.child_id, db)
    first = not db.query(PaymentTransaction).filter(PaymentTransaction.subscription_id == sub.id).first()
    grade = sub.grade if first or not child.default_grade else child.default_grade
    if sub.plan == "annual":
        terms = [1, 2, 3]
    else:
        terms = [sub.next_term or 1]
        sub.next_term = terms[0] % 3 + 1
    sub.grade = grade
    months = pricing.ANNUAL_RENEWAL_MONTHS if sub.plan == "annual" else pricing.TERM_RENEWAL_MONTHS
    sub.current_period_end = period_end or add_months(_now(), months)
    if sub.status in ("incomplete", "past_due"):
        sub.status = "active"
    method = CARD_SUBSCRIPTION if sub.provider == "stripe" else "simulated_subscription"
    return record_purchase(child=child, grade=grade, terms=terms, amount_usd=amount_usd, provider_ref=provider_ref,
                           payment_method=method, promo=promo if first else "", subscription=sub, db=db)


def _email(txn: PaymentTransaction, db) -> None:
    from backend.modules.billing.service import send_receipt_email
    send_receipt_email(txn, db=db)


# --- Stripe webhook events --------------------------------------------------------------------

def _ts(value) -> Optional[datetime.datetime]:
    try:
        return datetime.datetime.utcfromtimestamp(int(value)) if value else None
    except (TypeError, ValueError):
        return None


def _subscription_from_meta(provider_id: str, meta: dict, db) -> Optional[Subscription]:
    sub = db.query(Subscription).filter(Subscription.provider_subscription_id == provider_id).first()
    if sub or not meta.get("child_id"):
        return sub
    terms = [int(t) for t in (meta.get("terms") or "1").split(",") if t.strip().isdigit()] or [1]
    plan = meta.get("plan") or ("annual" if len(terms) == 3 else "term")
    sub = Subscription(parent_id=meta.get("parent_id") or None, child_id=meta["child_id"], grade=int(meta.get("grade") or 1),
                       plan=plan, next_term=terms[0] if plan == "term" else None, status="incomplete", provider="stripe",
                       provider_subscription_id=provider_id, amount_usd=pricing.renewal_price(plan),
                       promo_code=meta.get("promo_code") or None)
    db.add(sub)
    db.flush()
    return sub


def handle_event(event_type: str, obj: dict, db: Session) -> Optional[dict]:
    """Process a verified Stripe event for the new checkout; returns None for events it doesn't own."""
    meta = obj.get("metadata") or {}
    if event_type == "checkout.session.completed" and (meta.get("flow") == "checkout_v2" or obj.get("mode") == "subscription"):
        if obj.get("mode") == "subscription":
            sub = _subscription_from_meta(obj.get("subscription") or "", meta, db)
            if sub is not None:
                sub.provider_customer_id = obj.get("customer")
            db.commit()
            return {"received": True, "subscription": sub.id if sub else None}
        if obj.get("payment_status") not in (None, "paid", "no_payment_required"):
            return {"received": True, "status": obj.get("payment_status")}
        child = _child(meta["child_id"], db)
        terms = [int(t) for t in meta.get("terms", "1").split(",") if t.strip().isdigit()] or [1]
        txn = record_purchase(child=child, grade=int(meta.get("grade") or child.default_grade or 1), terms=terms,
                              amount_usd=(obj.get("amount_total") or 0) / 100, provider_ref=obj.get("id"),
                              payment_method="card", promo=meta.get("promo_code") or "", db=db)
        db.commit()
        _email(txn, db)
        return {"received": True, "receipt_number": txn.receipt_number}

    if event_type in ("invoice.paid", "invoice.payment_succeeded"):
        parent_details = (obj.get("parent") or {}).get("subscription_details") or {}
        provider_id = obj.get("subscription") or parent_details.get("subscription")
        if not provider_id:
            return {"received": True}
        sub_meta = (obj.get("subscription_details") or {}).get("metadata") or parent_details.get("metadata") or {}
        sub = _subscription_from_meta(provider_id, sub_meta, db)
        if sub is None:
            return {"received": True, "unknown_subscription": provider_id}
        lines = (obj.get("lines") or {}).get("data") or []
        period_end = _ts(((lines[0] if lines else {}).get("period") or {}).get("end"))
        txn = apply_cycle(sub, amount_usd=(obj.get("amount_paid") or 0) / 100, provider_ref=obj.get("id"),
                          promo=sub.promo_code or "", period_end=period_end, db=db)
        db.commit()
        _email(txn, db)
        return {"received": True, "receipt_number": txn.receipt_number}

    if event_type == "invoice.payment_failed":
        provider_id = obj.get("subscription") or ((obj.get("parent") or {}).get("subscription_details") or {}).get("subscription")
        sub = db.query(Subscription).filter(Subscription.provider_subscription_id == provider_id).first() if provider_id else None
        if sub:
            sub.status = "past_due"
            db.commit()
        return {"received": True}

    if event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = db.query(Subscription).filter(Subscription.provider_subscription_id == obj.get("id")).first()
        if sub is None:
            return {"received": True}
        status = obj.get("status")
        sub.status = ("canceled" if event_type.endswith("deleted") or status in ("canceled", "incomplete_expired")
                      else "past_due" if status in ("past_due", "unpaid")
                      else "incomplete" if status == "incomplete" else "active")
        sub.cancel_at_period_end = bool(obj.get("cancel_at_period_end"))
        items = (obj.get("items") or {}).get("data") or []
        sub.current_period_end = _ts(obj.get("current_period_end") or (items[0] if items else {}).get("current_period_end")) or sub.current_period_end
        if sub.status == "canceled" and not sub.canceled_at:
            sub.canceled_at = _now()
        db.commit()
        return {"received": True, "status": sub.status}
    return None


# --- managing subscriptions -------------------------------------------------------------------

def serialize(sub: Subscription, child: Optional[ChildProfile] = None, parent: Optional[User] = None) -> dict:
    return {
        "id": sub.id, "child_id": sub.child_id, "child_name": child.name if child else None,
        "parent_name": parent.full_name if parent else None, "parent_email": parent.email if parent else None,
        "grade": sub.grade, "plan": sub.plan, "next_term": sub.next_term, "status": sub.status,
        "provider": sub.provider, "renewal_price_usd": float(sub.amount_usd or pricing.renewal_price(sub.plan)),
        "renewal_months": pricing.ANNUAL_RENEWAL_MONTHS if sub.plan == "annual" else pricing.TERM_RENEWAL_MONTHS,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        "cancel_at_period_end": bool(sub.cancel_at_period_end), "promo_code": sub.promo_code,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


def list_for_parent(parent_id: str, db) -> List[dict]:
    rows = db.query(Subscription, ChildProfile).outerjoin(ChildProfile, ChildProfile.id == Subscription.child_id) \
        .filter(Subscription.parent_id == parent_id).order_by(Subscription.created_at.desc()).all()
    return [serialize(sub, child) for sub, child in rows]


def list_all(db) -> List[dict]:
    rows = db.query(Subscription, ChildProfile, User) \
        .outerjoin(ChildProfile, ChildProfile.id == Subscription.child_id) \
        .outerjoin(User, User.id == Subscription.parent_id).order_by(Subscription.created_at.desc()).all()
    return [serialize(sub, child, parent) for sub, child, parent in rows]


def set_auto_renew(subscription_id: str, *, renew: bool, actor_id: str, is_admin: bool, db) -> dict:
    """Turn auto-renew off (cancel at the end of the paid period) or back on."""
    sub = db.get(Subscription, subscription_id)
    if sub is None or (not is_admin and sub.parent_id != actor_id):
        raise ApplicationError(404, "Subscription not found")
    if sub.status == "canceled":
        raise ApplicationError(400, "This subscription has already ended; start a new one from the plans page.")
    if sub.provider == "stripe" and sub.provider_subscription_id:
        stripe_api.update_subscription(sub.provider_subscription_id, {"cancel_at_period_end": not renew})
    sub.cancel_at_period_end = not renew
    db.commit()
    return serialize(sub, db.get(ChildProfile, sub.child_id))


def renew_due_simulated(db, now: Optional[datetime.datetime] = None) -> int:
    """Renew simulated subscriptions whose period has ended (Stripe renews real ones itself)."""
    now = now or _now()
    renewed = 0
    for sub in db.query(Subscription).filter(Subscription.provider == "simulated", Subscription.status == "active",
                                             Subscription.current_period_end <= now).all():
        if sub.cancel_at_period_end:
            sub.status, sub.canceled_at = "canceled", now
            continue
        apply_cycle(sub, amount_usd=pricing.renewal_price(sub.plan), provider_ref=f"sim-{uuid.uuid4()}",
                    period_end=add_months(sub.current_period_end, pricing.ANNUAL_RENEWAL_MONTHS if sub.plan == "annual"
                                          else pricing.TERM_RENEWAL_MONTHS), db=db)
        renewed += 1
    db.commit()
    return renewed
