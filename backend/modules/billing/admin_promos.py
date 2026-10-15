"""Admin management of promo codes (e.g. JISR10): discount, number of families, validity window."""
import datetime

from sqlalchemy import func

from backend.errors import ApplicationError
from backend.models import PromoCode, PromoRedemption
from backend.modules.billing.pricing import promo_uses
from backend.modules.identity.access import require_roles

ADMIN_ONLY = ("admin",)


def _date(value):
    if value in (None, ""):
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ApplicationError(400, f"Invalid date: {value}") from exc


def serialize(promo: PromoCode, db) -> dict:
    now = datetime.datetime.utcnow()
    used = promo_uses(promo, db)
    state = ("inactive" if not promo.is_active else "scheduled" if promo.valid_from and now < promo.valid_from
             else "expired" if promo.valid_until and now > promo.valid_until
             else "used up" if promo.max_users is not None and used >= promo.max_users else "active")
    return {
        "id": promo.id, "code": promo.code, "discount_pct": promo.discount_pct, "max_users": promo.max_users,
        "used": used, "valid_from": promo.valid_from.isoformat() if promo.valid_from else None,
        "valid_until": promo.valid_until.isoformat() if promo.valid_until else None,
        "is_active": bool(promo.is_active), "notes": promo.notes, "state": state,
        "redemptions": [
            {"parent_id": r.parent_id, "payment_id": r.payment_id, "at": r.created_at.isoformat() if r.created_at else None}
            for r in db.query(PromoRedemption).filter(PromoRedemption.promo_code_id == promo.id)
            .order_by(PromoRedemption.created_at).all()
        ],
    }


def _apply(promo: PromoCode, payload: dict) -> None:
    if "discount_pct" in payload and payload["discount_pct"] is not None:
        pct = float(payload["discount_pct"])
        if not 0 < pct <= 100:
            raise ApplicationError(400, "Discount must be between 1 and 100 percent.")
        promo.discount_pct = pct
    if "max_users" in payload:
        value = payload["max_users"]
        if value not in (None, "") and int(value) < 1:
            raise ApplicationError(400, "Number of families must be at least 1 (leave empty for unlimited).")
        promo.max_users = None if value in (None, "") else int(value)
    if "valid_from" in payload:
        promo.valid_from = _date(payload["valid_from"])
    if "valid_until" in payload:
        promo.valid_until = _date(payload["valid_until"])
    if promo.valid_from and promo.valid_until and promo.valid_until <= promo.valid_from:
        raise ApplicationError(400, "The end date must be after the start date.")
    if "is_active" in payload and payload["is_active"] is not None:
        promo.is_active = bool(payload["is_active"])
    if "notes" in payload:
        promo.notes = (payload["notes"] or "").strip() or None


def list_promos(*, actor, db) -> list:
    require_roles(actor, ADMIN_ONLY)
    return [serialize(p, db) for p in db.query(PromoCode).order_by(PromoCode.created_at.desc()).all()]


def create_promo(payload: dict, *, actor, db) -> dict:
    require_roles(actor, ADMIN_ONLY)
    code = (payload.get("code") or "").strip().upper()
    if not code or not code.replace("-", "").replace("_", "").isalnum() or len(code) > 50:
        raise ApplicationError(400, "Use letters, digits, - or _ for the code (up to 50 characters).")
    if db.query(PromoCode).filter(func.upper(PromoCode.code) == code).first():
        raise ApplicationError(400, f"Promo code {code} already exists.")
    promo = PromoCode(code=code, discount_pct=10.0, max_users=10, is_active=True)
    _apply(promo, {"discount_pct": 10.0, "max_users": 10, **payload})
    db.add(promo)
    db.commit()
    return serialize(promo, db)


def update_promo(promo_id: str, payload: dict, *, actor, db) -> dict:
    require_roles(actor, ADMIN_ONLY)
    promo = db.get(PromoCode, promo_id)
    if promo is None:
        raise ApplicationError(404, "Promo code not found.")
    _apply(promo, payload)
    db.commit()
    return serialize(promo, db)
