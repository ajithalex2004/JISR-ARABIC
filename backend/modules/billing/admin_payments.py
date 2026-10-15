"""Admin payments overview: who paid for which grade and term, when and how, by family."""
import datetime
from decimal import Decimal

from sqlalchemy import or_

from backend.models import ChildProfile, PaymentTransaction, User
from backend.modules.identity.access import require_roles

ADMIN_ONLY = ("admin",)
LIST_LIMIT = 500


def _money(value) -> float:
    if value is None:
        return 0.0
    return float(value if not isinstance(value, Decimal) else round(value, 2))


def is_paid(txn: PaymentTransaction) -> bool:
    return txn.status == "succeeded" and txn.refunded_at is None


def is_voucher(txn: PaymentTransaction) -> bool:
    return bool(txn.voucher_code) or (txn.payment_method or "").endswith("voucher")


def serialize_payment(txn: PaymentTransaction, parent: User | None, child: ChildProfile | None) -> dict:
    status = "refunded" if txn.refunded_at else txn.status
    return {
        "id": txn.id,
        "created_at": txn.created_at.isoformat() if txn.created_at else None,
        "parent_id": txn.parent_id or txn.anonymized_parent_id,
        "parent_name": parent.full_name if parent else None,
        "parent_email": parent.email if parent else None,
        "child_id": txn.child_id,
        "child_name": child.name if child else ("(deleted student)" if not txn.child_id else None),
        "grade": txn.grade,
        "term": txn.term,
        "package_type": txn.package_type,
        "amount_usd": _money(txn.amount_usd),
        "vat_amount_usd": _money(txn.vat_amount_usd),
        "discount_amount_usd": _money(txn.discount_amount_usd),
        "currency": txn.currency or "USD",
        "payment_method": txn.payment_method,
        "voucher_code": txn.voucher_code,
        "promo_code": txn.promo_code,
        "receipt_number": txn.receipt_number,
        "tax_invoice_number": txn.tax_invoice_number,
        "status": status,
        "refunded_at": txn.refunded_at.isoformat() if txn.refunded_at else None,
    }


def summarize(transactions) -> dict:
    paid = [t for t in transactions if is_paid(t)]
    return {
        "count": len(transactions),
        "paid_count": len(paid),
        "revenue_usd": round(sum(_money(t.amount_usd) for t in paid), 2),
        "vat_usd": round(sum(_money(t.vat_amount_usd) for t in paid), 2),
        "voucher_redemptions": sum(1 for t in transactions if is_voucher(t) and t.status == "succeeded"),
        "pending_count": sum(1 for t in transactions if t.status == "pending"),
        "refunded_count": sum(1 for t in transactions if t.refunded_at is not None),
    }


def list_payments(*, actor, db, q=None, method=None, status=None, parent_id=None, days=None, limit=LIST_LIMIT) -> dict:
    """Matching payments, newest first; limit=None returns all of them (used by the export)."""
    require_roles(actor, ADMIN_ONLY)
    query = (
        db.query(PaymentTransaction, User, ChildProfile)
        .outerjoin(User, User.id == PaymentTransaction.parent_id)
        .outerjoin(ChildProfile, ChildProfile.id == PaymentTransaction.child_id)
    )
    term = (q or "").strip()
    if term:
        like = f"%{term}%"
        query = query.filter(or_(
            User.full_name.ilike(like), User.email.ilike(like), ChildProfile.name.ilike(like),
            PaymentTransaction.receipt_number.ilike(like), PaymentTransaction.voucher_code.ilike(like),
        ))
    if method == "voucher":
        query = query.filter(or_(PaymentTransaction.voucher_code.isnot(None), PaymentTransaction.payment_method.like("%voucher")))
    elif method:
        query = query.filter(PaymentTransaction.payment_method == method)
    if status == "refunded":
        query = query.filter(PaymentTransaction.refunded_at.isnot(None))
    elif status:
        query = query.filter(PaymentTransaction.status == status, PaymentTransaction.refunded_at.is_(None))
    if parent_id:
        query = query.filter(or_(PaymentTransaction.parent_id == parent_id, PaymentTransaction.anonymized_parent_id == parent_id))
    if days:
        since = datetime.datetime.utcnow() - datetime.timedelta(days=int(days))
        query = query.filter(PaymentTransaction.created_at >= since)

    rows = query.order_by(PaymentTransaction.created_at.desc()).all()
    return {
        "summary": summarize([txn for txn, _, _ in rows]),
        "payments": [serialize_payment(txn, parent, child) for txn, parent, child in (rows if limit is None else rows[:limit])],
        "truncated": limit is not None and len(rows) > limit,
    }
