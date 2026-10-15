"""Prices, the annual discount and promo codes: the single source of every amount a parent pays.

All prices are in USD and include 5% UAE VAT.
  * One term: USD 10. Two terms: USD 20.
  * All three terms bought together (the annual plan): USD 30 less 15% = USD 25.50.
  * A promo code (e.g. JISR10, set up by an admin) takes a further percentage off; each code is
    limited to a number of families (max_users) and a validity window, and each parent may use a
    code once. On an auto-renewing plan the promo applies to the first payment only.
"""
import datetime
from typing import Iterable, List, Optional

from sqlalchemy import func

from backend.errors import ApplicationError

PRICE_PER_TERM_USD = 10.0
ANNUAL_DISCOUNT_PCT = 15.0
ANNUAL_LIST_PRICE_USD = PRICE_PER_TERM_USD * 3                                            # 30.00
PRICE_ANNUAL_PASS_USD = round(ANNUAL_LIST_PRICE_USD * (1 - ANNUAL_DISCOUNT_PCT / 100), 2)  # 25.50
VAT_RATE = 0.05
TERM_RENEWAL_MONTHS = 4
ANNUAL_RENEWAL_MONTHS = 12


def money(value: float) -> float:
    return round(float(value) + 1e-9, 2)


def tax_breakdown(total: float):
    """(subtotal excl. VAT, VAT) of a VAT-inclusive total."""
    if total <= 0:
        return 0.0, 0.0
    subtotal = round(total / (1 + VAT_RATE), 2)
    return subtotal, round(total - subtotal, 2)


def clean_terms(terms: Optional[Iterable[int]], term: Optional[int] = None) -> List[int]:
    chosen = sorted({int(t) for t in (terms or []) if int(t) in (1, 2, 3)})
    if not chosen and term in (1, 2, 3):
        chosen = [int(term)]
    if not chosen:
        raise ApplicationError(400, "Choose at least one term (1, 2 or 3).")
    return chosen


def quote(terms: List[int], *, promo_pct: float = 0.0) -> dict:
    """Price of a purchase: list price, annual discount, promo discount, total and VAT."""
    annual = len(terms) == 3
    list_price = money(PRICE_PER_TERM_USD * len(terms))
    annual_discount = money(list_price - PRICE_ANNUAL_PASS_USD) if annual else 0.0
    after_plan = money(list_price - annual_discount)
    promo_discount = money(after_plan * promo_pct / 100) if promo_pct else 0.0
    total = money(after_plan - promo_discount)
    subtotal, vat = tax_breakdown(total)
    return {
        "terms": terms,
        "package_type": "annual" if annual else "term",
        "list_price_usd": list_price,
        "annual_discount_usd": annual_discount,
        "promo_discount_usd": promo_discount,
        "discount_usd": money(annual_discount + promo_discount),
        "total_usd": total,
        "subtotal_usd": subtotal,
        "vat_usd": vat,
    }


def renewal_price(plan: str) -> float:
    return PRICE_ANNUAL_PASS_USD if plan == "annual" else PRICE_PER_TERM_USD


def price_list() -> dict:
    return {
        "currency": "USD",
        "vat_included": True,
        "term_usd": PRICE_PER_TERM_USD,
        "two_terms_usd": money(PRICE_PER_TERM_USD * 2),
        "annual_list_usd": ANNUAL_LIST_PRICE_USD,
        "annual_discount_pct": ANNUAL_DISCOUNT_PCT,
        "annual_usd": PRICE_ANNUAL_PASS_USD,
        "term_renewal_months": TERM_RENEWAL_MONTHS,
        "annual_renewal_months": ANNUAL_RENEWAL_MONTHS,
    }


# --- promo codes ----------------------------------------------------------------------------

def _now() -> datetime.datetime:
    return datetime.datetime.utcnow()


def promo_uses(promo, db) -> int:
    from backend.models import PromoRedemption
    return db.query(func.count(PromoRedemption.id)).filter(PromoRedemption.promo_code_id == promo.id).scalar() or 0


def find_promo(code: str, *, parent_id: Optional[str], db):
    """The active promo code for `code`, or an error saying why it can't be used."""
    from backend.models import PromoCode, PromoRedemption

    clean = (code or "").strip().upper()
    if not clean:
        return None
    promo = db.query(PromoCode).filter(func.upper(PromoCode.code) == clean).first()
    if promo is None or not promo.is_active:
        raise ApplicationError(400, f"Promo code {clean} is not valid.")
    now = _now()
    if promo.valid_from and now < promo.valid_from:
        raise ApplicationError(400, f"Promo code {clean} starts on {promo.valid_from:%d %b %Y}.")
    if promo.valid_until and now > promo.valid_until:
        raise ApplicationError(400, f"Promo code {clean} expired on {promo.valid_until:%d %b %Y}.")
    if parent_id and db.query(PromoRedemption).filter(
            PromoRedemption.promo_code_id == promo.id, PromoRedemption.parent_id == parent_id).first():
        raise ApplicationError(400, f"You have already used promo code {clean}.")
    if promo.max_users is not None and promo_uses(promo, db) >= promo.max_users:
        raise ApplicationError(400, f"Promo code {clean} has been used by its maximum of {promo.max_users} families.")
    return promo


def record_promo_use(code: Optional[str], *, parent_id: Optional[str], payment_id: Optional[str], db) -> None:
    """Count a successful payment against its promo code (once per parent)."""
    from backend.models import PromoCode, PromoRedemption

    clean = (code or "").strip().upper()
    if not clean or not parent_id:
        return
    promo = db.query(PromoCode).filter(func.upper(PromoCode.code) == clean).first()
    if promo is None or db.query(PromoRedemption).filter(
            PromoRedemption.promo_code_id == promo.id, PromoRedemption.parent_id == parent_id).first():
        return
    db.add(PromoRedemption(promo_code_id=promo.id, code=promo.code, parent_id=parent_id, payment_id=payment_id))
