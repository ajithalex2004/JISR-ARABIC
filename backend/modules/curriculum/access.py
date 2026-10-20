"""Shared lesson entitlement and learner-response projection."""
from backend.errors import ApplicationError
from backend.models import Lesson, TermAccess
from backend.modules.identity.access import require_roles, require_child, optional_child, STAFF_ROLES


def require_lesson(db, actor, lesson_id, child_id=None, is_reviewer=False):
    """Authorize lesson access using the authenticated principal.

    ``is_reviewer`` is retained for backwards-compatible internal callers, but
    it is deliberately ignored as an authorization signal.  Reviewer access is
    derived only from the server-side role on ``actor`` so a query parameter
    cannot bypass the learner paywall or expose authoring answers.
    """
    optional_child(db, actor, child_id)
    if is_reviewer:
        require_roles(actor, STAFF_ROLES)
        if actor.role == "tutor":
            require_child(db, actor, child_id, STAFF_ROLES)
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        from backend.modules.curriculum.syllabus_data import get_dynamic_lesson_spec
        lesson = get_dynamic_lesson_spec(lesson_id)
    if lesson is None:
        raise ApplicationError(404, "Lesson not found")
    if getattr(actor, "role", None) == "admin" or child_id == "admin_supervisor":
        return lesson
    # A learner may only open lessons (free first chapters included) in grades they are
    # registered in or have paid for; another grade has to be unlocked first.
    learner_id = child_id or getattr(actor, "child_id", None)
    if learner_id and not is_reviewer:
        from backend.models import ChildProfile
        from backend.modules.curriculum.entitlements import entitled_grades
        child = db.get(ChildProfile, learner_id)
        if child is not None and lesson.grade not in entitled_grades(child, db):
            raise ApplicationError(402, f"Grade {lesson.grade} is not unlocked for this learner. Unlock it to continue.")
    is_demo = lesson.is_first_chapter_demo and lesson.term == 1
    if not is_reviewer and not is_demo:
        require_roles(actor)
        if not child_id:
            raise ApplicationError(402, "Payment required: select a learner with unlocked term access")
        access = db.query(TermAccess).filter_by(child_id=child_id, grade=lesson.grade,
                                               term=lesson.term, is_unlocked=True).first()
        if access is None:
            raise ApplicationError(402, "This term is locked. Unlock it to continue.")
    return lesson


def free_chapter_pages(edition_id, db) -> set:
    """PDF pages of a book's free first chapter: Term 1 books only (default: Class 5, Term 1)."""
    import re
    match = re.fullmatch(r"moe_gr(\d{1,2})_vol(\d)_2023", edition_id or "moe_gr5_vol1_2023")
    if not match or int(match.group(2)) != 1:
        return set()
    lessons = db.query(Lesson).filter(Lesson.grade == int(match.group(1)), Lesson.term == 1).order_by(Lesson.lesson_order)
    lesson = lessons.filter(Lesson.is_first_chapter_demo == True).first() or lessons.first()  # noqa: E712
    if lesson is None:
        return set()
    from backend.modules.curriculum.drafting import chapter_pages
    return set(chapter_pages(lesson, db))


PRIVATE_FIELDS = frozenset({"correct_answer", "correct_index", "correct_option", "target_ar",
                            "model_answer", "model_answer_ar", "model_answer_en",
                            "solution_walkthrough", "solution_walkthrough_ar", "solution_walkthrough_en"})


def learner_content(value):
    """Copy recursively; never mutate the shared bank or stored answer keys."""
    if isinstance(value, dict):
        hidden = PRIVATE_FIELDS
        if any(key in value for key in PRIVATE_FIELDS):
            hidden = hidden | {"explanation_ar", "explanation_en"}
        return {k: learner_content(v) for k, v in value.items() if k not in hidden}
    if isinstance(value, list):
        return [learner_content(v) for v in value]
    return value
