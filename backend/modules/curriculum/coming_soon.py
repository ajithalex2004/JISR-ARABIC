"""Lessons with no real content yet are shown to learners as "Coming soon" instead of opened.

A lesson is "coming soon" when what a learner would get is the placeholder template from
syllabus_data.generate_dynamic_lesson_content rather than the lesson itself:
  - it has no published version, so the template would be generated on the fly, or
  - its published version is that same template (its vocabulary is the generic set
    الريادة / التعاون / الابتكار, the same in every class and term).

Admins still see and open these lessons so the content team can work on them. Publishing a
real version clears the lesson-list cache (invalidate_lesson_cache), so the lesson opens for
learners as soon as it is published.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, Optional, Set

from sqlalchemy.orm import Session

from backend.models import Lesson, LessonVersion

COMING_SOON_STATUS = "coming_soon"
COMING_SOON_REASON = "Coming soon"

# The vocabulary every placeholder lesson carries, with tashkeel removed.
PLACEHOLDER_VOCAB = frozenset({"الريادة", "التعاون", "الابتكار"})

_MARKS = re.compile(r"[ً-ٰٟـ]")


def _plain(word: str) -> str:
    return _MARKS.sub("", word or "").strip()


def is_placeholder_content(content: Any) -> bool:
    """True if a lesson package's content is the generic placeholder template."""
    if not isinstance(content, dict):
        return False
    words = {_plain(c.get("word_ar", "")) for c in content.get("vocabulary_cards") or [] if isinstance(c, dict)}
    return PLACEHOLDER_VOCAB <= words


def coming_soon_ids(db: Session, lesson_ids: Iterable[str]) -> Set[str]:
    """The lessons among lesson_ids that learners would only see placeholder content for."""
    ids = list(lesson_ids)
    if not ids:
        return set()
    versions = db.query(LessonVersion.lesson_id, LessonVersion.content_json).filter(
        LessonVersion.lesson_id.in_(ids),
        LessonVersion.is_active == True,  # noqa: E712
        LessonVersion.status == "published",
    ).all()
    real = set()
    for lesson_id, content_json in versions:
        try:
            content = json.loads(content_json or "{}")
        except (TypeError, ValueError):
            content = {}
        if not is_placeholder_content(content):
            real.add(lesson_id)
    return set(ids) - real


def lesson_is_coming_soon(db: Session, lesson_id: str) -> bool:
    return lesson_id in coming_soon_ids(db, [lesson_id])


def term_is_coming_soon(db: Session, grade: int, term: int) -> bool:
    """True when no lesson of a class's term has real content yet (nothing to sell)."""
    ids = [row[0] for row in db.query(Lesson.id).filter(Lesson.grade == grade, Lesson.term == term).all()]
    # Classes with no lessons in the database are served from the syllabus outline: all placeholders.
    return not ids or coming_soon_ids(db, ids) == set(ids)


def coming_soon_terms(db: Session, grade: int, terms: Optional[Iterable[int]] = None) -> Set[int]:
    return {t for t in (terms or (1, 2, 3)) if term_is_coming_soon(db, grade, t)}


def coming_soon_message(grade: int, term: Optional[int] = None) -> str:
    where = f"Class {grade} Term {term}" if term else f"Class {grade}"
    return f"{where} is coming soon. It will open here as soon as its lessons are ready."


def learner_view(item: Dict[str, Any]) -> Dict[str, Any]:
    """A lesson-list entry as a learner sees a coming-soon lesson: listed, not openable, not free."""
    return {**item, "is_first_chapter_demo": False, "is_accessible": False,
            "status": COMING_SOON_STATUS, "lock_reason": COMING_SOON_REASON}
