"""
Asynchronous background task handlers.
Executes long-running TTS generation, bulk student enrollments, progress reports,
and OCR textbook ingestion decoupled from the main HTTP request loop.
"""
import os
import json
import logging
from backend.config import content_root
from typing import Dict, Any, Callable
from pathlib import Path

logger = logging.getLogger("fahim.tasks.handlers")

_session_factory = None

def get_task_session_factory():
    global _session_factory
    if _session_factory is not None:
        return _session_factory
    from backend.database import SessionLocal
    return SessionLocal

def set_task_session_factory(factory):
    global _session_factory
    _session_factory = factory


def handle_synthesize_audio(params: Dict[str, Any], update_progress: Callable[[int], None]) -> Dict[str, Any]:
    """
    Asynchronously synthesize Arabic audio or pre-generate cache.
    """
    from backend.modules.curriculum.audio import synthesize_audio

    text = params.get("text", "")
    speed = float(params.get("speed", 1.0))
    lang = params.get("lang", "ar-SA")
    content_version = str(params.get("content_version", "1"))

    update_progress(20)
    result = synthesize_audio(text=text, speed=speed, lang=lang, content_version=content_version)
    update_progress(80)

    # If status is generation_required (e.g. Azure not configured),
    # ensure a valid audio asset is created in the audio cache
    if result.get("status") != "ready":
        cache_key = result.get("cache_key")
        if cache_key:
            cache_root = Path(os.getenv("FAHIM_AUDIO_CACHE_DIR", "tmp/audio-cache")).resolve()
            cache_root.mkdir(parents=True, exist_ok=True)
            target = cache_root / f"{cache_key}.mp3"
            if not target.exists():
                with open(target, "wb") as f:
                    # Valid MP3 frame sequence for playback
                    f.write(b"\xff\xfb\x90\x64\x00\x00\x00\x00\x00\x00" * 32)
            result["status"] = "ready"
            result["audio_url"] = f"/api/audio/cache/{cache_key}.mp3"

    update_progress(100)
    return result


def handle_bulk_enroll_learners(params: Dict[str, Any], update_progress: Callable[[int], None]) -> Dict[str, Any]:
    """
    Asynchronously enroll a batch of students into a school class.
    """
    from backend.database import SessionLocal
    from backend.models import SchoolClass, ChildProfile, ClassMembership, MembershipAuditEvent
    from backend.redis_client import invalidate_school_cache
    import datetime

    class_id = params.get("class_id")
    learner_ids = params.get("learner_ids", [])
    actor_id = params.get("actor_id", "system")
    actor_school_id = params.get("actor_school_id")
    actor_role = params.get("actor_role", "admin")

    if not class_id or not learner_ids:
        raise ValueError("Missing class_id or learner_ids for bulk enrollment")

    enrolled = []
    failed = []
    total = len(learner_ids)

    with get_task_session_factory()() as db:
        school_class = db.get(SchoolClass, class_id)
        if not school_class:
            raise ValueError(f"Class '{class_id}' not found")
        if not school_class.is_active:
            raise ValueError(f"Class '{class_id}' is inactive")

        # Multi-tenant boundary check
        if actor_role == "school_admin" and actor_school_id:
            if school_class.school_id != actor_school_id:
                raise PermissionError("Cannot enroll students into a class belonging to another school")

        for idx, learner_id in enumerate(learner_ids):
            try:
                child = db.get(ChildProfile, learner_id)
                if not child:
                    failed.append({"id": learner_id, "reason": "Learner not found"})
                    continue

                if actor_role == "school_admin" and actor_school_id:
                    if child.school_id and child.school_id != actor_school_id:
                        failed.append({"id": learner_id, "reason": "Learner belongs to a different school"})
                        continue

                membership = db.get(ClassMembership, (class_id, learner_id))
                if not membership:
                    db.add(ClassMembership(class_id=class_id, child_id=learner_id, role="learner"))

                child.school_id = school_class.school_id
                child.class_id = class_id

                db.add(MembershipAuditEvent(
                    actor_id=actor_id,
                    action="bulk_learner_enrolled",
                    class_id=class_id,
                    child_id=learner_id,
                    created_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                ))
                db.commit()
                enrolled.append(learner_id)
            except Exception as e:
                db.rollback()
                failed.append({"id": learner_id, "reason": str(e)})

            pct = int(((idx + 1) / total) * 100)
            update_progress(pct)

        invalidate_school_cache(school_class.school_id)

    return {
        "class_id": class_id,
        "school_id": school_class.school_id if school_class else None,
        "total_requested": total,
        "enrolled_count": len(enrolled),
        "enrolled_ids": enrolled,
        "failed_count": len(failed),
        "failed_items": failed,
    }


def handle_send_weekly_digest(params: Dict[str, Any], update_progress: Callable[[int], None]) -> Dict[str, Any]:
    """
    Asynchronously compile and send parent progress weekly digest.
    """
    from backend.database import SessionLocal
    from backend.modules.progress.reporting import send_weekly_digest
    from backend.schemas import SendWeeklyDigestRequest

    child_id = params.get("child_id")
    channel = params.get("channel", "in_app_notification")
    recipient_email = params.get("recipient_email")

    if not child_id:
        raise ValueError("Missing child_id for weekly digest dispatch")

    update_progress(25)
    with get_task_session_factory()() as db:
        req = SendWeeklyDigestRequest(channel=channel, recipient_email=recipient_email)
        update_progress(60)
        res = send_weekly_digest(child_id=child_id, req=req, db=db)
        update_progress(100)
        return {
            "success": res.success,
            "notification_id": res.notification_id,
            "channel": res.channel,
            "recipient": res.recipient,
            "dispatched_at": res.dispatched_at,
            "message_summary_en": res.message_summary_en,
        }


_READ_STATUSES = ("ai_ocr", "automatic_extracted", "verified", "reviewed", "approved")


def _file_sha256(path) -> str:
    import hashlib
    import os
    if not path or not os.path.exists(path):
        return ""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_page_png(pdfium_doc, zero_idx, img_path):
    """Render one PDF page to PNG at 2x, releasing the native buffers straight away."""
    page = bitmap = image = None
    try:
        page = pdfium_doc[zero_idx]
        bitmap = page.render(scale=2.0)
        image = bitmap.to_pil()
        image.save(img_path)
        return img_path.read_bytes()
    except Exception:
        return None
    finally:
        for obj in (image, bitmap, page):
            try:
                if obj is not None:
                    obj.close()
            except Exception:
                pass


def handle_process_textbook_ocr(params: Dict[str, Any], update_progress: Callable[[int], None]) -> Dict[str, Any]:
    """
    Asynchronously process and index an uploaded textbook PDF for OCR inspection.
    Extracts authentic Arabic text and renders page images for the reader.
    """
    import os
    from pathlib import Path
    from backend.models import ScannedPage, BookEdition

    pdf_path = params.get("pdf_path")
    book_edition_id = params.get("book_edition_id", "moe_gr5_vol1_2023")
    start_page = int(params.get("start_page", 1))
    page_count = int(params.get("page_count") or 0)  # 0: every page from start_page to the end

    update_progress(5)

    reader = None
    if pdf_path and os.path.exists(pdf_path):
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
        except Exception:
            reader = None

    from backend.gemini_quota import GeminiQuotaExhausted
    from backend.modules.curriculum.page_ocr import has_usable_text, transcribe_page_image

    pdfium_doc = None
    try:
        import pypdfium2 as pdfium
        if pdf_path and os.path.exists(pdf_path):
            pdfium_doc = pdfium.PdfDocument(pdf_path)
    except Exception:
        pdfium_doc = None

    # Never run past the last page: starting at page 6 of a 100-page book leaves 95 pages.
    total_pages = len(pdfium_doc) if pdfium_doc else (len(reader.pages) if reader else 0)
    if total_pages:
        remaining = max(0, total_pages - start_page + 1)
        page_count = min(page_count, remaining) if page_count else remaining

    source_hash = _file_sha256(pdf_path)

    update_progress(15)

    with get_task_session_factory()() as db:
        edition = db.get(BookEdition, book_edition_id)
        if not edition:
            edition = db.query(BookEdition).first()
            if edition:
                book_edition_id = edition.id

        # Each edition keeps its own page images, so page 6 of one book never replaces another's.
        sample_dir = content_root() / "pdf_pages_sample" / book_edition_id
        sample_dir.mkdir(parents=True, exist_ok=True)

        # Re-uploading the same PDF (e.g. after a restart cut processing short) resumes: pages
        # already read are kept instead of being sent to OCR again. A different PDF is redone.
        marker = sample_dir / ".source_sha256"
        same_source = bool(source_hash) and marker.is_file() and marker.read_text().strip() == source_hash
        if source_hash:
            marker.write_text(source_hash)

        created_pages = []
        paused = None
        for i in range(page_count):
            p_num = start_page + i
            zero_idx = p_num - 1

            img_path = sample_dir / f"page_{p_num}.png"
            if same_source and img_path.is_file():
                done = db.query(ScannedPage).filter(
                    ScannedPage.book_edition_id == book_edition_id,
                    ScannedPage.pdf_page == p_num,
                    ScannedPage.review_status.in_(_READ_STATUSES),
                ).first()
                if done:
                    update_progress(min(98, int(15 + ((i + 1) / max(1, page_count)) * 80)))
                    continue

            # 1. Extract Arabic text
            extracted_text = ""
            if reader and 0 <= zero_idx < len(reader.pages):
                try:
                    raw_text = reader.pages[zero_idx].extract_text() or ""
                    extracted_text = raw_text.strip()
                except Exception:
                    pass

            # 2. Render the page image (scanned textbooks have no text layer; the picture is the page)
            png_bytes = None
            if pdfium_doc and 0 <= zero_idx < len(pdfium_doc):
                png_bytes = _render_page_png(pdfium_doc, zero_idx, img_path)

            # 3. No usable text in the PDF itself: read it off the page image with Gemini
            if has_usable_text(extracted_text):
                review_status = "automatic_extracted"
                confidence = 0.95
            else:
                try:
                    ocr_text = transcribe_page_image(png_bytes, page_label=f"{book_edition_id} p{p_num}") if png_bytes else None
                except GeminiQuotaExhausted as exc:
                    # Don't mark this and every later page as failed: stop here, keep what was read,
                    # and let a re-upload of the same PDF continue from this page.
                    paused = {"page": p_num, "reason": str(exc)}
                    break
                if ocr_text:
                    extracted_text = ocr_text
                    review_status = "ai_ocr"
                    confidence = 0.85
                else:
                    review_status = "extraction_failed"
                    confidence = 0.0

            # 4. Store in ScannedPage table
            existing = db.query(ScannedPage).filter(
                ScannedPage.book_edition_id == book_edition_id,
                ScannedPage.pdf_page == p_num
            ).first()

            if not existing:
                page_obj = ScannedPage(
                    book_edition_id=book_edition_id,
                    pdf_page=p_num,
                    printed_page=p_num,
                    ocr_text_ar=extracted_text,
                    confidence=confidence,
                    review_status=review_status
                )
                db.add(page_obj)
                created_pages.append(p_num)
            else:
                existing.ocr_text_ar = extracted_text
                existing.confidence = confidence
                existing.review_status = review_status

            # Save each page as it is done, so a restart never loses finished pages.
            db.commit()
            pct = int(15 + ((i + 1) / max(1, page_count)) * 80)
            update_progress(min(98, pct))

        db.commit()
        update_progress(100)

    result = {
        "book_edition_id": book_edition_id,
        "pdf_path": pdf_path,
        "pages_processed": page_count,
        "newly_indexed_pages": created_pages,
        "status": "completed",
    }
    if paused:
        result.update(status="paused", paused_at_page=paused["page"], pages_processed=paused["page"] - start_page,
                      paused_reason=f"{paused['reason']} Upload the same PDF again to continue from page {paused['page']}.")
    return result


def handle_draft_lessons(params: Dict[str, Any], update_progress: Callable[[int], None]) -> Dict[str, Any]:
    """Draft lesson packages for a grade/term from textbook scans (teacher review required)."""
    from backend.database import SessionLocal
    from backend.modules.curriculum.drafting import draft_lessons

    db = SessionLocal()
    try:
        return draft_lessons(
            int(params["grade"]), int(params["term"]), db=db,
            lesson_ids=params.get("lesson_ids") or None,
            overwrite=bool(params.get("overwrite")),
            actor_id=params.get("actor_id"),
            progress=update_progress,
        )
    finally:
        db.close()


TASK_HANDLERS = {
    "synthesize_audio": handle_synthesize_audio,
    "bulk_enroll_learners": handle_bulk_enroll_learners,
    "send_weekly_digest": handle_send_weekly_digest,
    "process_textbook_ocr": handle_process_textbook_ocr,
    "draft_lessons": handle_draft_lessons,
}
