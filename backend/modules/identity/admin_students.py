"""Admin view of learners: find a student by their own or their parent's name and fix their grade."""
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


def set_student_grade(child_id: str, grade: int, *, actor, db) -> dict:
    """Admins may set any grade 1-12; this is how a wrongly saved grade is corrected."""
    require_roles(actor, ADMIN_ONLY)
    if not isinstance(grade, int) or not 1 <= grade <= 12:
        raise ApplicationError(400, "Grade must be between 1 and 12.")
    child = db.get(ChildProfile, child_id)
    if child is None:
        raise ApplicationError(404, "Student not found.")
    child.default_grade = grade
    db.commit()
    db.refresh(child)
    return _serialize(child, db.get(User, child.parent_id), db)
