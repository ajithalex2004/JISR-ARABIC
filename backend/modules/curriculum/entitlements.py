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
