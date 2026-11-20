"""Which grades a learner may use.

A child is registered in one grade (``default_grade``). Any other grade becomes
available to that child only once the parent pays for it (an unlocked TermAccess
row for that grade). Lessons, including the free first chapter, are served only
for these grades; moving a child to another grade requires having paid for it.
"""
from typing import List, Optional

from backend.errors import ApplicationError
from backend.models import ChildProfile, TermAccess


def entitled_grades(child: ChildProfile, db=None) -> List[int]:
    """The child's registered grade plus every grade with an unlocked term."""
    grades = set()
    if isinstance(child.default_grade, int):
        grades.add(child.default_grade)
    accesses = None
    if db is not None:
        try:
            accesses = db.query(TermAccess).filter(
                TermAccess.child_id == child.id, TermAccess.is_unlocked == True  # noqa: E712
            ).all()
        except Exception:
            accesses = None
    if accesses is None:
        accesses = [a for a in (getattr(child, "term_accesses", None) or []) if a.is_unlocked]
    grades.update(a.grade for a in accesses if isinstance(a.grade, int))
    return sorted(grades)


def is_admin(actor) -> bool:
    return getattr(actor, "role", None) == "admin"


def require_grade_change_allowed(child: ChildProfile, new_grade: Optional[int], actor, db=None) -> None:
    """Moving a child to a grade they haven't paid for needs payment (admins excepted)."""
    if new_grade is None or new_grade == child.default_grade or is_admin(actor):
        return
    if new_grade not in entitled_grades(child, db):
        raise ApplicationError(
            402,
            f"Grade {new_grade} is not unlocked for {child.name}. Unlock Grade {new_grade} to switch to it.",
        )


# Ask Fahim (chat, the step-by-step mentor, the homework helper and the exam paper assistant) is
# part of the paid plan: free-tier students and parents see it locked.
AI_STAFF_ROLES = {"admin", "tutor", "school_admin"}


def has_paid_plan(db, actor) -> bool:
    """Whether this account may use Ask Fahim.

    Staff always may. A student (learner session) may when their own profile has an unlocked
    (paid or voucher) term; a parent may when any of their children has one.
    """
    if actor is None:
        return False
    role = getattr(actor, "role", None)
    if role in AI_STAFF_ROLES:
        return True
    query = db.query(TermAccess.id).filter(TermAccess.is_unlocked == True)  # noqa: E712
    if role == "learner":
        child_id = getattr(actor, "child_id", None)
        if not child_id:
            return False
        return query.filter(TermAccess.child_id == child_id).first() is not None
    if role == "parent":
        child_ids = db.query(ChildProfile.id).filter(ChildProfile.parent_id == actor.id)
        return query.filter(TermAccess.child_id.in_(child_ids)).first() is not None
    return False


def require_paid_ai(db, actor) -> None:
    """Refuse Ask Fahim to signed-out visitors (401) and free-tier accounts (402)."""
    if actor is None:
        raise ApplicationError(401, "Sign in to use Ask Fahim.")
    if not has_paid_plan(db, actor):
        raise ApplicationError(
            402,
            "Ask Fahim is part of the paid plan. Unlock a term (USD 10) or the full year (USD 25.50) to use it.",
        )
