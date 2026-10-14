"""Admin management of parent accounts: list with their children, grades and payments; add, edit, delete."""
import datetime
import re
from collections import defaultdict

from sqlalchemy import or_

from backend.errors import ApplicationError
from backend.models import ChildProfile, PaymentTransaction, TermAccess, User
from backend.modules.billing.admin_payments import is_paid, is_voucher, serialize_payment, summarize
from backend.modules.identity.access import require_roles
from backend.security import hash_password

ADMIN_ONLY = ("admin",)
LIST_LIMIT = 100
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _children_by_parent(parent_ids, db):
    children = db.query(ChildProfile).filter(ChildProfile.parent_id.in_(parent_ids)).order_by(ChildProfile.name).all() if parent_ids else []
    unlocked = defaultdict(set)
    if children:
        for access in db.query(TermAccess).filter(
            TermAccess.child_id.in_([c.id for c in children]), TermAccess.is_unlocked == True  # noqa: E712
        ).all():
            unlocked[access.child_id].add((access.grade, access.term))
    grouped = defaultdict(list)
    for child in children:
        paid_grades = {g for g, _ in unlocked[child.id]}
        grouped[child.parent_id].append({
            "id": child.id,
            "name": child.name,
            "default_grade": child.default_grade,
            "entitled_grades": sorted(paid_grades | ({child.default_grade} if child.default_grade else set())),
            "unlocked_terms": [f"grade_{g}_term_{t}" for g, t in sorted(unlocked[child.id])],
            "school_name": child.school_name,
        })
    return grouped


def _payments_by_parent(parent_ids, db):
    grouped = defaultdict(list)
    if parent_ids:
        for txn in db.query(PaymentTransaction).filter(PaymentTransaction.parent_id.in_(parent_ids)).all():
            grouped[txn.parent_id].append(txn)
    return grouped


def _serialize_parent(user: User, children: list, payments: list) -> dict:
    paid = [t for t in payments if is_paid(t)]
    last = max((t.created_at for t in payments if t.created_at), default=None)
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_verified": bool(user.is_verified),
        "weekly_report_email": bool(user.weekly_report_email),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "students_count": len(children),
        "students": children,
        "payments_count": len(payments),
        "paid_count": len(paid),
        "total_paid_usd": summarize(payments)["revenue_usd"],
        "voucher_redemptions": sum(1 for t in payments if is_voucher(t) and t.status == "succeeded"),
        "last_payment_at": last.isoformat() if last else None,
    }


def _family_query(db):
    # Parent accounts, plus any other account (e.g. an admin) that has learners of its own.
    has_children = db.query(ChildProfile.parent_id)
    return db.query(User).filter(or_(User.role == "parent", User.id.in_(has_children)))


def list_parents(q=None, *, actor, db) -> list:
    require_roles(actor, ADMIN_ONLY)
    query = _family_query(db)
    term = (q or "").strip()
    if term:
        like = f"%{term}%"
        matching_children = db.query(ChildProfile.parent_id).filter(ChildProfile.name.ilike(like))
        query = query.filter(or_(
            User.full_name.ilike(like), User.email.ilike(like), User.phone_number.ilike(like),
            User.id.in_(matching_children),
        ))
    users = query.order_by(User.created_at.desc()).limit(LIST_LIMIT).all()
    ids = [u.id for u in users]
    children = _children_by_parent(ids, db)
    payments = _payments_by_parent(ids, db)
    return [_serialize_parent(u, children[u.id], payments[u.id]) for u in users]


def _get_family_account(parent_id: str, db) -> User:
    user = db.get(User, parent_id)
    if user is None or (user.role != "parent" and not db.query(ChildProfile).filter(ChildProfile.parent_id == user.id).first()):
        raise ApplicationError(404, "Parent not found.")
    return user


def get_parent(parent_id: str, *, actor, db) -> dict:
    require_roles(actor, ADMIN_ONLY)
    user = _get_family_account(parent_id, db)
    children = _children_by_parent([user.id], db)[user.id]
    payments = sorted(_payments_by_parent([user.id], db)[user.id], key=lambda t: t.created_at or datetime.datetime.min, reverse=True)
    child_rows = {c.id: c for c in db.query(ChildProfile).filter(ChildProfile.parent_id == user.id).all()}
    detail = _serialize_parent(user, children, payments)
    detail["payments"] = [serialize_payment(t, user, child_rows.get(t.child_id)) for t in payments]
    return detail


def _clean_email(email) -> str:
    email = (email or "").strip().lower()
    if not _EMAIL.match(email):
        raise ApplicationError(400, "Enter a valid email address.")
    return email


def _check_password(password) -> str:
    password = password or ""
    if len(password) < 8:
        raise ApplicationError(400, "Password must be at least 8 characters.")
    return password


def create_parent(payload, *, actor, db) -> dict:
    require_roles(actor, ADMIN_ONLY)
    email = _clean_email(payload.email)
    if db.query(User).filter(User.email == email).first():
        raise ApplicationError(409, "An account with this email already exists.")
    user = User(
        email=email,
        full_name=(payload.full_name or "").strip() or None,
        phone_number=(payload.phone_number or "").strip() or None,
        password_hash=hash_password(_check_password(payload.password)),
        role="parent",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _serialize_parent(user, [], [])


def update_parent(parent_id: str, payload, *, actor, db) -> dict:
    require_roles(actor, ADMIN_ONLY)
    user = _get_family_account(parent_id, db)
    if payload.email is not None:
        email = _clean_email(payload.email)
        if email != user.email and db.query(User).filter(User.email == email).first():
            raise ApplicationError(409, "An account with this email already exists.")
        user.email = email
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip() or None
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number.strip() or None
    if payload.weekly_report_email is not None:
        user.weekly_report_email = payload.weekly_report_email
    if payload.password:
        user.password_hash = hash_password(_check_password(payload.password))
    db.commit()
    db.refresh(user)
    return get_parent(user.id, actor=actor, db=db)


def delete_parent(parent_id: str, *, actor, db) -> dict:
    """Delete a parent account with all its students; payment records are kept anonymised."""
    from backend.modules.identity.service import delete_account

    require_roles(actor, ADMIN_ONLY)
    user = _get_family_account(parent_id, db)
    if user.role != "parent":
        raise ApplicationError(400, "Only parent accounts can be deleted here.")
    label = user.full_name or user.email
    delete_account(user=user, db=db)
    return {"success": True, "id": parent_id, "message": f"{label} and their students were deleted."}
