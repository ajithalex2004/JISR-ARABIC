"""Where each grade/term stands on the way to learners: book uploaded, pages read, lessons drafted
and published. Shown on Admin > Content so gaps are visible before launch."""
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.config import content_root
from backend.models import BookEdition, Lesson, LessonVersion, ScannedPage

GRADES = range(1, 13)
TERMS = (1, 2, 3)
# Same set the OCR task treats as "read" (backend.tasks.handlers._READ_STATUSES).
READ_STATUSES = ("ai_ocr", "automatic_extracted", "verified", "reviewed", "approved")


def edition_id(grade: int, term: int) -> str:
    return f"moe_gr{grade}_vol{term}_2023"


def curated_pages() -> Dict[str, int]:
    """Pages transcribed and checked by hand, shipped with the code (the Volume 1 readers of grades 5-8).
    They count as read even though no scanned page row exists for them."""
    from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA
    from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA, TEXTBOOK_PAGES_DATA
    sets = {5: TEXTBOOK_PAGES_DATA, 6: GRADE_6_TEXTBOOK_PAGES_DATA, 7: GRADE_7_TEXTBOOK_PAGES_DATA, 8: GRADE_8_TEXTBOOK_PAGES_DATA}
    return {edition_id(grade, 1): len({str(page) for page in data}) for grade, data in sets.items()}


def _stage(cell: Dict[str, Any]) -> str:
    lessons = cell["lessons"]
    if lessons["total"] and lessons["published"] == lessons["total"]:
        # Lessons published while no page of the book was ever read came from the syllabus, not the textbook.
        return "published" if cell["from_book"] else "published_unsourced"
    if lessons["published"] or lessons["in_review"]:
        return "in_review"
    read = cell["pages_read"] + cell["pages_curated"]
    if read:
        return "ready_to_draft" if read >= (cell["total_pages"] or 0) > 0 else "reading"
    return "uploaded" if cell["uploaded"] else "no_book"


def content_progress(db: Session) -> Dict[str, Any]:
    editions = {e.id: e for e in db.query(BookEdition).all()}
    pages: Dict[str, Dict[str, int]] = {}
    for book, status, count in (db.query(ScannedPage.book_edition_id, ScannedPage.review_status, func.count())
                                .group_by(ScannedPage.book_edition_id, ScannedPage.review_status)):
        entry = pages.setdefault(book, {"read": 0, "failed": 0})
        if status in READ_STATUSES:
            entry["read"] += count
        elif status == "extraction_failed":
            entry["failed"] += count

    # Latest state of each lesson: published if any version is live, in review if a draft awaits approval.
    version_states: Dict[str, set] = {}
    for lesson_id, status in db.query(LessonVersion.lesson_id, LessonVersion.status).filter(
            LessonVersion.status.in_(("published", "content_pending", "approved"))):
        version_states.setdefault(lesson_id, set()).add(status)

    lessons: Dict[tuple, Dict[str, int]] = {}
    for lesson in db.query(Lesson.id, Lesson.grade, Lesson.term):
        entry = lessons.setdefault((lesson.grade, lesson.term), {"total": 0, "published": 0, "in_review": 0})
        entry["total"] += 1
        states = version_states.get(lesson.id, set())
        if "published" in states:
            entry["published"] += 1
        elif states & {"content_pending", "approved"}:
            entry["in_review"] += 1

    curated = curated_pages()
    uploads = content_root() / "uploads"
    rows: List[Dict[str, Any]] = []
    for grade in GRADES:
        cells = []
        for term in TERMS:
            book_id = edition_id(grade, term)
            edition = editions.get(book_id)
            read = pages.get(book_id, {"read": 0, "failed": 0})
            lesson_counts = lessons.get((grade, term), {"total": 0, "published": 0, "in_review": 0})
            cell = {
                "grade": grade,
                "term": term,
                "edition_id": book_id,
                "uploaded": (uploads / f"{book_id}.pdf").is_file() or bool(read["read"] or read["failed"]),
                "total_pages": edition.total_pages if edition else None,
                "pages_read": read["read"],
                "pages_failed": read["failed"],
                "pages_curated": curated.get(book_id, 0),
                "from_book": bool(read["read"] or curated.get(book_id, 0)),
                "lessons": {**lesson_counts,
                            "not_started": lesson_counts["total"] - lesson_counts["published"] - lesson_counts["in_review"],
                            # What students see for lessons without a published version: auto-generated content.
                            "auto_generated": lesson_counts["total"] - lesson_counts["published"]},
            }
            cell["stage"] = _stage(cell)
            cells.append(cell)
        rows.append({"grade": grade, "terms": cells})

    all_cells = [cell for row in rows for cell in row["terms"]]
    summary = {stage: sum(1 for cell in all_cells if cell["stage"] == stage)
               for stage in ("published", "published_unsourced", "in_review", "ready_to_draft", "reading", "uploaded",
                             "no_book")}
    # Book-level gaps, whatever the lessons' state: books never uploaded, uploaded but unread, pages to retry.
    missing = [cell for cell in all_cells if not cell["uploaded"] and not cell["from_book"]]
    summary["books_missing"] = len(missing)
    summary["books_missing_list"] = [f"Grade {cell['grade']} Term {cell['term']}" for cell in missing]
    summary["books_unread"] = sum(1 for cell in all_cells if cell["uploaded"] and not cell["from_book"])
    summary["pages_failed"] = sum(cell["pages_failed"] for cell in all_cells)
    summary["lessons_published"] = sum(cell["lessons"]["published"] for cell in all_cells)
    summary["lessons_total"] = sum(cell["lessons"]["total"] for cell in all_cells)
    summary["lessons_auto_generated"] = summary["lessons_total"] - summary["lessons_published"]
    return {"summary": summary, "grades": rows}
