"""A teacher's check of one textbook page's machine-read text against its scan.

Most page text was read by OCR software; labels such as "ocr_vision_verified" are the
software's own and don't mean a person checked it. Marking a page reviewed records who checked
it and when (review_status becomes "reviewed", which the admin quality report counts), and can
save a corrected text that the Reading tab then shows.
"""
import datetime
import json

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import CurriculumAuditEvent, ScannedPage


def mark_page_reviewed(db: Session, edition_id: str, pdf_page: int, *, actor_id: str, note: str = "",
                       corrected_text=None) -> dict:
    page = db.query(ScannedPage).filter(ScannedPage.book_edition_id == edition_id, ScannedPage.pdf_page == pdf_page).first()
    if page is None:
        raise ApplicationError(404, f"Page {pdf_page} of {edition_id} has no stored text to review")
    corrected = None
    if corrected_text is not None and corrected_text.strip() and corrected_text.strip() != (page.ocr_text_ar or "").strip():
        corrected = corrected_text.strip()
        page.ocr_text_ar = corrected
    page.review_status = "reviewed"
    page.reviewed_by = actor_id
    page.reviewed_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    page.review_note = (note or "").strip()[:2000] or None
    db.add(CurriculumAuditEvent(actor_id=actor_id, action="page_review", lesson_id=edition_id,
                                version_id=f"page_{pdf_page}",
                                details_json=json.dumps({"note": page.review_note, "text_corrected": bool(corrected)},
                                                        ensure_ascii=False)))
    db.commit()
    return {"success": True, "edition_id": edition_id, "pdf_page": pdf_page, "review_status": page.review_status,
            "reviewed_by": actor_id, "reviewed_at": page.reviewed_at.isoformat(), "text_corrected": bool(corrected)}
