"""Where each grade/term stands on the way to learners: book uploaded, pages read, lessons drafted
and published. Shown on Admin > Content so gaps are visible before launch."""
from typing import Any, Dict, List

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.config import content_root
from backend.models import BookEdition, Lesson, LessonVersion, ScannedPage

GRADES = range(1, 13)
TERMS = (1, 2, 3)
# Same set the OCR task treats as "read" (backend.tasks.handlers._READ_STATUSES).
READ_STATUSES = ("ai_ocr", "automatic_extracted", "verified", "reviewed", "approved")
# Lessons written by hand against the scanned Ministry book (backend/curriculum_catalog.py, 1693219092.pdf).
AUTHORED_FROM_BOOK = {"moe_gr5_vol1_2023"}


def edition_id(grade: int, term: int) -> str:
    return f"moe_gr{grade}_vol{term}_2023"


def curated_pages() -> Dict[str, int]:
    """Pages transcribed and checked by hand, shipped with the code (the Volume 1 readers of grades 5-8).
    They count as read even though no scanned page row exists for them."""
    from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA
    from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA, TEXTBOOK_PAGES_DATA
    sets = {5: TEXTBOOK_PAGES_DATA, 6: GRADE_6_TEXTBOOK_PAGES_DATA, 7: GRADE_7_TEXTBOOK_PAGES_DATA, 8: GRADE_8_TEXTBOOK_PAGES_DATA}
    return {edition_id(grade, 1): len({str(page) for page in data}) for grade, data in sets.items()}


def pages_on_disk() -> Dict[str, Dict[str, int]]:
    """Page images and page text that each book has on the content volume.

    Books loaded with the bulk content upload (scripts/upload_content.py) have their pages only
    here: page_N.png in pdf_pages_sample/<book>/ and page_N.json (the text the Reading tab
    shows) in vision-output-new/ or vision-output/. They have no PDF and no scanned-page rows,
    so counting only those made a book that learners can read look missing.
    """
    root = content_root()
    found: Dict[str, Dict[str, set]] = {}
    for folder, kind, suffix in (("pdf_pages_sample", "images", ".png"), ("vision-output-new", "text", ".json"),
                                 ("vision-output", "text", ".json")):
        base = root / folder
        if not base.is_dir():
            continue
        for book in base.iterdir():
            if not book.is_dir():
                continue
            pages = {f.stem for f in book.glob(f"page_*{suffix}")}
            if pages:
                found.setdefault(book.name, {"images": set(), "text": set()})[kind] |= pages
    return {book: {kind: len(pages) for kind, pages in kinds.items()} for book, kinds in found.items()}


def _stage(cell: Dict[str, Any]) -> str:
    lessons = cell["lessons"]
    if lessons["total"] and lessons["published"] == lessons["total"]:
        # Lessons published without being drafted from the book's pages came from the syllabus.
        return "published" if lessons["from_book"] == lessons["total"] else "published_unsourced"
    if lessons["published"] or lessons["in_review"]:
        return "in_review"
    read = max(cell["pages_read"] + cell["pages_curated"], cell.get("pages_text_on_disk", 0))
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

    from backend.modules.curriculum.drafting import AI_DRAFTER
    # Published versions drafted from textbook pages (an AI draft, kept as is or edited by a teacher).
    book_versions = {lesson_id for (lesson_id,) in db.query(LessonVersion.lesson_id).filter(
        LessonVersion.status == "published",
        or_(LessonVersion.created_by == AI_DRAFTER, LessonVersion.content_json.like('%"source_pdf_pages"%')))}
    ai_drafts = {lesson_id for (lesson_id,) in db.query(LessonVersion.lesson_id).filter(
        LessonVersion.created_by == AI_DRAFTER, LessonVersion.status.in_(("content_pending", "approved")))}

    # Live versions a teacher has signed off (the explicit review, not the approve/publish clicks).
    teacher_reviewed = {lesson_id for (lesson_id,) in db.query(LessonVersion.lesson_id).filter(
        LessonVersion.status == "published", LessonVersion.is_active == True,  # noqa: E712
        LessonVersion.reviewed_at.isnot(None))}

    lessons: Dict[tuple, Dict[str, int]] = {}
    to_draft: Dict[tuple, List[str]] = {}
    for lesson in db.query(Lesson.id, Lesson.grade, Lesson.term).order_by(Lesson.lesson_order):
        key = (lesson.grade, lesson.term)
        entry = lessons.setdefault(key, {"total": 0, "published": 0, "in_review": 0, "from_book": 0, "ai_drafts": 0,
                                         "teacher_reviewed": 0})
        entry["total"] += 1
        states = version_states.get(lesson.id, set())
        if "published" in states:
            entry["published"] += 1
            if lesson.id in teacher_reviewed:
                entry["teacher_reviewed"] += 1
        elif states & {"content_pending", "approved"}:
            entry["in_review"] += 1
        if lesson.id in book_versions or edition_id(*key) in AUTHORED_FROM_BOOK:
            entry["from_book"] += 1
        elif lesson.id in ai_drafts:
            entry["ai_drafts"] += 1
        else:
            to_draft.setdefault(key, []).append(lesson.id)

    from backend.modules.curriculum.page_reading import books_being_read, terms_being_drafted
    curated = curated_pages()
    on_disk = pages_on_disk()
    reading = books_being_read()
    drafting = terms_being_drafted()
    uploads = content_root() / "uploads"
    rows: List[Dict[str, Any]] = []
    for grade in GRADES:
        cells = []
        for term in TERMS:
            book_id = edition_id(grade, term)
            edition = editions.get(book_id)
            read = pages.get(book_id, {"read": 0, "failed": 0})
            lesson_counts = lessons.get((grade, term), {"total": 0, "published": 0, "in_review": 0, "from_book": 0,
                                                        "ai_drafts": 0, "teacher_reviewed": 0})
            pdf_stored = (uploads / f"{book_id}.pdf").is_file()
            disk = on_disk.get(book_id, {"images": 0, "text": 0})
            cell = {
                "grade": grade,
                "term": term,
                "edition_id": book_id,
                "uploaded": pdf_stored or bool(read["read"] or read["failed"] or disk["images"]),
                # The PDF is on disk, so its pages can be read again without re-uploading.
                "pdf_stored": pdf_stored,
                "reading_queued": book_id in reading,
                "total_pages": edition.total_pages if edition else None,
                "pages_read": read["read"],
                "pages_failed": read["failed"],
                "pages_curated": curated.get(book_id, 0),
                # Pages on the content volume (bulk content upload): images, and the text learners read.
                "page_images_on_disk": disk["images"],
                "pages_text_on_disk": disk["text"],
                "book_read": bool(read["read"] or curated.get(book_id, 0) or disk["text"]),
                # Lessons not yet drafted from the book; drafting needs page images, so scanned pages.
                "draft_lesson_ids": to_draft.get((grade, term), []) if read["read"] else [],
                "drafting_queued": (grade, term) in drafting,
                "lessons": {**lesson_counts,
                            "not_started": lesson_counts["total"] - lesson_counts["published"] - lesson_counts["in_review"],
                            # Live for students but not yet checked by a teacher.
                            "published_unreviewed": lesson_counts["published"] - lesson_counts["teacher_reviewed"],
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
    missing = [cell for cell in all_cells if not cell["uploaded"] and not cell["book_read"]]
    summary["books_missing"] = len(missing)
    summary["books_missing_list"] = [f"Grade {cell['grade']} Term {cell['term']}" for cell in missing]
    summary["books_unread"] = sum(1 for cell in all_cells if cell["uploaded"] and not cell["book_read"])
    summary["pages_failed"] = sum(cell["pages_failed"] for cell in all_cells)
    from backend.modules.curriculum.page_reading import needs_reading
    summary["books_to_read"] = sum(1 for cell in all_cells if needs_reading(cell) and not cell["reading_queued"])
    summary["lessons_published"] = sum(cell["lessons"]["published"] for cell in all_cells)
    summary["lessons_total"] = sum(cell["lessons"]["total"] for cell in all_cells)
    summary["lessons_auto_generated"] = summary["lessons_total"] - summary["lessons_published"]
    summary["lessons_from_book"] = sum(cell["lessons"]["from_book"] for cell in all_cells)
    summary["lessons_ai_drafts"] = sum(cell["lessons"]["ai_drafts"] for cell in all_cells)
    summary["lessons_teacher_reviewed"] = sum(cell["lessons"]["teacher_reviewed"] for cell in all_cells)
    summary["lessons_published_unreviewed"] = summary["lessons_published"] - summary["lessons_teacher_reviewed"]
    summary["terms_to_draft"] = sum(1 for cell in all_cells if cell["draft_lesson_ids"] and not cell["drafting_queued"])
    return {"summary": summary, "grades": rows}
