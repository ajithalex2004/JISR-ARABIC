"""Admin management of learners: find a student by their own or their parent's name, add,
edit or delete them, and correct their grade."""
import re

import bcrypt
from sqlalchemy import or_

from backend.errors import ApplicationError
from backend.models import ChildProfile, TermAccess, User
from backend.modules.curriculum.entitlements import entitled_grades
from backend.modules.identity.access import require_roles

ADMIN_ONLY = ("admin",)
SEARCH_LIMIT = 50


def _serialize(child: ChildProfile, parent: User | None, db) -> dict:
    unlocked = sorted(
        (a.grade, a.term)
        for a in db.query(TermAccess).filter(TermAccess.child_id == child.id, TermAccess.is_unlocked == True).all()  # noqa: E712
    )
    return {
        "id": child.id,
        "name": child.name,
        "default_grade": child.default_grade,
        "entitled_grades": entitled_grades(child, db),
        "unlocked_terms": [f"grade_{g}_term_{t}" for g, t in unlocked],
        "school_name": child.school_name,
        "gender": child.gender,
        "age": child.age,
        "has_pin": bool(child.access_pin),
        "parent_name": parent.full_name if parent else None,
        "parent_email": parent.email if parent else None,
    }


def search_students(q: str | None, *, actor, db) -> list[dict]:
    require_roles(actor, ADMIN_ONLY)
    query = db.query(ChildProfile, User).outerjoin(User, User.id == ChildProfile.parent_id)
    term = (q or "").strip()
    if term:
        like = f"%{term}%"
        query = query.filter(or_(
            ChildProfile.name.ilike(like),
            User.full_name.ilike(like),
            User.email.ilike(like),
        ))
    rows = query.order_by(ChildProfile.name).limit(SEARCH_LIMIT).all()
    return [_serialize(child, parent, db) for child, parent in rows]


def _require_grade(grade) -> int:
    if not isinstance(grade, int) or not 1 <= grade <= 12:
        raise ApplicationError(400, "Grade must be between 1 and 12.")
    return grade


def _hash_pin(pin: str) -> str:
    pin = (pin or "").strip()
    if not re.fullmatch(r"\d{4}", pin):
        raise ApplicationError(400, "PIN must be exactly 4 digits.")
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def _require_name(name) -> str:
    name = (name or "").strip()
    if not name:
        raise ApplicationError(400, "Student name is required.")
    return name[:255]


def _get_child(child_id: str, db) -> ChildProfile:
    child = db.get(ChildProfile, child_id)
    if child is None:
        raise ApplicationError(404, "Student not found.")
    return child


def create_student(payload, *, actor, db) -> dict:
    """Add a student under an existing parent account (looked up by email)."""
    require_roles(actor, ADMIN_ONLY)
    email = (payload.parent_email or "").strip().lower()
    parent = db.query(User).filter(User.email == email).first() if email else None
    if parent is None or parent.role not in ("parent", "admin"):
        raise ApplicationError(404, "No parent account with that email. The parent must sign up first.")
    grade = _require_grade(payload.grade)
    if payload.age is not None and not 3 <= payload.age <= 20:
        raise ApplicationError(400, "Age must be between 3 and 20.")
    child = ChildProfile(
        parent_id=parent.id,
        name=_require_name(payload.name),
        gender=payload.gender or "Boy",
        age=payload.age or 10,
        school_name=(payload.school_name or "").strip() or "Sunrise International School, Abu Dhabi",
        default_grade=grade,
        access_pin=_hash_pin(payload.access_pin) if payload.access_pin else None,
        diagnostic_completed=True,
        diagnostic_level="standard",
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return _serialize(child, parent, db)


def update_student(child_id: str, payload, *, actor, db) -> dict:
    """Edit a student's details; admins may set any grade without payment."""
    require_roles(actor, ADMIN_ONLY)
    child = _get_child(child_id, db)
    if payload.name is not None:
        child.name = _require_name(payload.name)
    if payload.grade is not None:
        child.default_grade = _require_grade(payload.grade)
    if payload.school_name is not None:
        child.school_name = payload.school_name.strip() or child.school_name
    if payload.gender is not None:
        child.gender = payload.gender
    if payload.age is not None:
        if not 3 <= payload.age <= 20:
            raise ApplicationError(400, "Age must be between 3 and 20.")
        child.age = payload.age
    if payload.access_pin:
        child.access_pin = _hash_pin(payload.access_pin)
    db.commit()
    db.refresh(child)
    return _serialize(child, db.get(User, child.parent_id), db)


def delete_student(child_id: str, *, actor, db) -> dict:
    """Permanently delete a student and their learning records; paid transactions are kept anonymised."""
    from backend.modules.identity.service import purge_children

    require_roles(actor, ADMIN_ONLY)
    child = _get_child(child_id, db)
    name = child.name
    purge_children([child.id], db=db, anonymized_parent_id=child.parent_id)
    db.commit()
    return {"success": True, "id": child_id, "message": f"{name} was deleted."}


def set_student_grade(child_id: str, grade: int, *, actor, db) -> dict:
    """Admins may set any grade 1-12; this is how a wrongly saved grade is corrected."""
    require_roles(actor, ADMIN_ONLY)
    grade = _require_grade(grade)
    child = _get_child(child_id, db)
    child.default_grade = grade
    db.commit()
    db.refresh(child)
    return _serialize(child, db.get(User, child.parent_id), db)
