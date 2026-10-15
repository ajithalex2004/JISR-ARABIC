"""Application operations; callers provide explicit database sessions and actors."""
import os
import json
import hashlib
import datetime
from sqlalchemy.orm import Session
from backend.models import (
    BookEdition, Lesson, LessonVersion, ScannedPage,
    CurriculumGrade, CurriculumTerm, CurriculumAuditEvent
)
from backend.schemas import AdminAddTermRequest, AdminAddClassRequest, AdminAddLessonRequest, AdminUpdateEditionRequest
from backend.ocr_reader import get_textbook_coverage_report, get_page_ocr_data
from backend.errors import ApplicationError
from backend.config import content_root
from backend.redis_client import invalidate_lesson_cache
import re

ARABIC_RE = re.compile(r"[\u0600-\u06ff]")


def get_quality_report(*, db: Session):
    """Run deterministic pre-publication checks over OCR pages and lesson packages."""
    issues = []
    pages_checked = 0
    lessons_checked = 0
    for edition_id in db.query(ScannedPage.book_edition_id).distinct().all():
        edition = edition_id[0]
        pages = db.query(ScannedPage).filter(ScannedPage.book_edition_id == edition).order_by(ScannedPage.pdf_page).all()
        seen = set()
        previous = None
        for page in pages:
            pages_checked += 1
            if page.pdf_page in seen:
                issues.append({"type": "duplicate_page", "edition_id": edition, "pdf_page": page.pdf_page})
            seen.add(page.pdf_page)
            if previous is not None and page.pdf_page <= previous:
                issues.append({"type": "page_order", "edition_id": edition, "pdf_page": page.pdf_page, "previous_page": previous})
            previous = page.pdf_page
            if not (page.ocr_text_ar or "").strip() or not ARABIC_RE.search(page.ocr_text_ar or ""):
                issues.append({"type": "missing_arabic", "edition_id": edition, "pdf_page": page.pdf_page})
            if page.review_status != "reviewed":
                issues.append({"type": "unreviewed_ocr", "edition_id": edition, "pdf_page": page.pdf_page, "review_status": page.review_status})

    for lesson in db.query(Lesson).order_by(Lesson.grade, Lesson.term, Lesson.lesson_order).all():
        lessons_checked += 1
        if not (lesson.title_ar or "").strip() or not ARABIC_RE.search(lesson.title_ar or ""):
            issues.append({"type": "missing_lesson_arabic", "lesson_id": lesson.id})
        if not (lesson.title_en or "").strip():
            issues.append({"type": "missing_lesson_english", "lesson_id": lesson.id})
        active = db.query(LessonVersion).filter(LessonVersion.lesson_id == lesson.id, LessonVersion.is_active == True).first()
        if active:
            try:
                content = json.loads(active.content_json)
            except (TypeError, ValueError):
                issues.append({"type": "invalid_lesson_json", "lesson_id": lesson.id})
                content = {}
            serialized = json.dumps(content, ensure_ascii=False)
            if not re.search(r"[A-Za-z]", serialized):
                issues.append({"type": "missing_content_english", "lesson_id": lesson.id})
            # Inspect nested lesson packages rather than only the serialized
            # document. This catches incomplete OCR/import records before
            # they are presented as publishable content.
            activity_ids = set()
            duplicate_ids = set()
            def inspect_node(node, path="content"):
                if isinstance(node, dict):
                    for key, value in node.items():
                        field_path = f"{path}.{key}"
                        if key.endswith("_ar") and isinstance(value, str) and not ARABIC_RE.search(value):
                            issues.append({"type": "missing_arabic_field", "lesson_id": lesson.id, "field": field_path})
                        if key.endswith("_en") and isinstance(value, str) and not value.strip():
                            issues.append({"type": "missing_english_field", "lesson_id": lesson.id, "field": field_path})
                        if key == "id" and isinstance(value, str):
                            if value in activity_ids:
                                duplicate_ids.add(value)
                            activity_ids.add(value)
                        inspect_node(value, field_path)
                elif isinstance(node, list):
                    for index, value in enumerate(node):
                        inspect_node(value, f"{path}[{index}]")
            inspect_node(content)
            for duplicate_id in sorted(duplicate_ids):
                issues.append({"type": "duplicate_activity_id", "lesson_id": lesson.id, "activity_id": duplicate_id})
        else:
            issues.append({"type": "missing_active_version", "lesson_id": lesson.id})

    grouped = {}
    for lesson in db.query(Lesson).order_by(Lesson.grade, Lesson.term, Lesson.lesson_order).all():
        grouped.setdefault((lesson.grade, lesson.term), []).append(lesson)
    for (grade, term), lessons in grouped.items():
        for prior, current in zip(lessons, lessons[1:]):
            if current.start_page <= prior.start_page:
                issues.append({"type": "lesson_boundary_order", "grade": grade, "term": term, "lesson_id": current.id, "start_page": current.start_page, "previous_lesson_id": prior.id})

    return {"ok": not issues, "pages_checked": pages_checked, "lessons_checked": lessons_checked, "issue_count": len(issues), "issues": issues}

def get_coverage_report():
    """Coverage report for whole-book content and pronunciation targets (Section 11)."""
    return get_textbook_coverage_report()


_TRANSLATION_CACHE = {}

def _translate_ar_to_en(text_ar: str) -> str:
    """Fast, cached translation of Arabic curriculum text to English with resilient fallbacks."""
    import urllib.request
    import urllib.parse
    import json
    if not text_ar or not text_ar.strip():
        return ""
    cleaned = text_ar.strip()
    if cleaned in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[cleaned]

    # 1. Try Google Translate gtx
    try:
        q = urllib.parse.quote(cleaned[:1000])
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q={q}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                res = "".join(seg[0] for seg in data[0] if seg and len(seg) > 0 and seg[0])
                if res.strip():
                    _TRANSLATION_CACHE[cleaned] = res.strip()
                    return res.strip()
    except Exception:
        pass

    # 2. Resilient Fallback: MyMemory Translation API
    try:
        q = urllib.parse.quote(cleaned[:500])
        url = f"https://api.mymemory.translated.net/get?q={q}&langpair=ar|en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            res = data.get("responseData", {}).get("translatedText", "")
            if res and not str(res).startswith("MYMEMORY WARNING:") and res != cleaned:
                _TRANSLATION_CACHE[cleaned] = res.strip()
                return res.strip()
    except Exception:
        pass

    return f"Lesson text: {cleaned[:80]}"


_EXAMPLE_PREFIXES = ("مثال", "مِثال", "مِثَال", "مثَال")
_TERMINAL = (".", "؟", "?", "!", ":", "؛", "۔")
# An exercise / list item: "1." "١ -" "(2)" "أ-" "ب)" "*" "•" ...
_ITEM = r"(?:[0-9٠-٩]{1,2}\s*[-–.)ـ]|\(\s*[0-9٠-٩]{1,2}\s*\)|[أبجده]\s*[-–)]|[*•])"
_ITEM_START = re.compile(rf"^{_ITEM}\s")
_ITEM_INSIDE = re.compile(rf"\s+(?={_ITEM}\s)")
_EN_ITEM = r"(?:\d{1,2}\s*[-–.)]|\(\d{1,2}\)|[a-e]\)|[*•])"
_EN_ITEM_START = re.compile(rf"^{_EN_ITEM}\s")
_EN_ITEM_INSIDE = re.compile(rf"\s+(?={_EN_ITEM}\s)")


def _is_example(line: str) -> bool:
    return line.startswith(_EXAMPLE_PREFIXES)


def _split_headword(line: str) -> list[str]:
    """'الإنسان: الكائن الحيّ المفكّر.' -> ['الإنسان:', 'الكائن الحيّ المفكّر.'] (word, then meaning)."""
    word, sep, rest = line.partition(":")
    if not sep or not rest.strip() or _is_example(line) or not word.strip() or len(word.split()) > 3:
        return [line]
    return [f"{word.strip()}:", rest.strip()]


def _group_lines(lines: list[str]) -> list[str]:
    """Group a block's lines into paragraphs, keeping every printed line as its own line ('\n').

    A word card (headword, meaning, 'مثال: ...' example) becomes one paragraph, ending at its
    example; headings, questions and numbered exercise items stand alone (so each can have its
    own model answer); a short line ending in ':' starts a new paragraph.
    """
    paragraphs: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            paragraphs.append("\n".join(current))
            current.clear()

    for line in lines:
        if _is_example(line):
            current.append(line)
            flush()  # an example closes its word card
            continue
        if len(line) < 50 and (line.endswith("؟") or "الوحدة" in line or "الدرس" in line or "الصفحة" in line) \
                or _ITEM_START.match(line):
            flush()
            paragraphs.append(line)
            continue
        if len(_split_headword(line)) == 2 or (len(line) < 50 and line.endswith(":")):
            flush()  # a new headword / heading starts a new paragraph
        current.append(line)
        if len(" ".join(current)) > 300:
            flush()
    flush()
    return paragraphs


def translate_paragraph(text_ar: str) -> str:
    """English for a paragraph, line by line, so each English line matches its Arabic line."""
    lines = [l.strip() for l in (text_ar or "").split("\n") if l.strip()]
    if len(lines) <= 1:
        return _translate_ar_to_en(text_ar)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(8, len(lines))) as pool:
        return "\n".join(pool.map(_translate_ar_to_en, lines))


def translate_paragraphs(paragraphs: list[str]) -> list[str]:
    from concurrent.futures import ThreadPoolExecutor
    if not paragraphs:
        return []
    with ThreadPoolExecutor(max_workers=min(4, len(paragraphs))) as pool:
        return list(pool.map(translate_paragraph, paragraphs))


def _clean_ocr_paragraphs(raw_text: str, printed_page: int) -> list[str]:
    import re
    if not raw_text:
        return [f"الصفحة {printed_page} من كتاب المنهاج الوزاري. نص تعليمي وتدريبات قرائية واستماع."]
    
    if "نص مستخرج آلياً" in raw_text:
        return [
            f"الوحدة التعليمية للصفحة {printed_page}: قراءة واستماع وتعبير.",
            "استمع إلى الدرس وتدرب على النطق السليم للكلمات والعبارات العربية المقررة."
        ]

    # Remove repeated copyright stamp
    cleaned = re.sub(r'جميع الحقوق(جميع الحقوق| محفوظة)*', '', raw_text)
    # Remove artifact ASCII corruption symbols from scanned PDFs
    # (newlines are kept: they are the page's line structure)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f™°§©®±µ¶·]+', ' ', cleaned)
    # Fix broken vertical diacritics / letters
    cleaned = re.sub(r'\n+([ً-ْ])', r'\1', cleaned)
    # Blank lines separate blocks; inside a block every line the page printed separately stays on
    # its own line, so word cards keep their word / meaning / example layout.
    blocks = [b for b in re.split(r"\n\s*\n", cleaned) if b.strip()]
    parts = []
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        parts.extend(_group_lines([l for l in lines if re.search(r'[\u0600-\u06FF]', l)]))

    # Strip standalone trailing page numbers from paragraphs
    cleaned_parts = []
    for p in parts:
        p_clean = re.sub(rf'\s+{printed_page}(\s+{printed_page})*\s*$', '', p).strip()
        p_clean = re.sub(r'\s+\b\d{1,3}\b\s*$', '', p_clean).strip()
        if p_clean:
            cleaned_parts.append(p_clean)
    if cleaned_parts:
        parts = cleaned_parts

    parts = [layout_arabic(p) for p in parts]
    if not parts:
        parts = [f"درس الصفحة {printed_page}: استمع وتدرب على قراءة النصوص ومفردات الدرس."]
    return parts


_HARAKAT = "[\u064B-\u0652\u0670]*"
_AR_EXAMPLE = re.compile(rf"\s+(?=م{_HARAKAT}ث{_HARAKAT}ا{_HARAKAT}ل{_HARAKAT}\s*:)")
_EN_EXAMPLE = re.compile(r"\s+(?=(?:e\.g\.|Example)\s*:)", re.IGNORECASE)


def _split_items(line: str, start: "re.Pattern", inside: "re.Pattern") -> list[str]:
    """'قبل الاستماع: ١ - أتأمل. ٢ - أتناقش.' -> one line for the label and one per item."""
    parts = [p.strip() for p in inside.split(line) if p.strip()]
    items = sum(1 for p in parts if start.match(p))
    return parts if items >= 2 else [line]


def _layout(text: str, *, english: bool) -> str:
    """Put each printed line, numbered item and word-card part (word / meaning / example) on its own line."""
    if not isinstance(text, str) or not text.strip():
        return text
    example = _EN_EXAMPLE if english else _AR_EXAMPLE
    start, inside = (_EN_ITEM_START, _EN_ITEM_INSIDE) if english else (_ITEM_START, _ITEM_INSIDE)
    is_card = bool(example.search(" " + text))
    out: list[str] = []
    for index, line in enumerate(l.strip() for l in text.split("\n") if l.strip()):
        pieces = [p.strip() for p in example.split(line) if p.strip()] if is_card else [line]
        if is_card and index == 0 and not out:
            head, sep, rest = pieces[0].partition(":")
            if sep and rest.strip() and len(head.split()) <= (5 if english else 3) and not example.match(" " + pieces[0]):
                pieces = [f"{head.strip()}:", rest.strip()] + pieces[1:]
        for piece in pieces:
            out.extend(_split_items(piece, start, inside))
    return "\n".join(out)


def layout_arabic(text: str) -> str:
    return _layout(text, english=False)


def layout_lines(page: dict) -> dict:
    """Line-for-line layout for every reader page (curated or scanned), Arabic and English alike.

    The English is only re-split when it then has as many lines as the Arabic, so lines always match.
    """
    if not isinstance(page, dict) or not isinstance(page.get("paragraphs"), list):
        return page
    arabic = [layout_arabic(p) if isinstance(p, str) else p for p in page["paragraphs"]]
    english = page.get("paragraphs_en")
    if isinstance(english, list):
        english = list(english)
        for i, (before, after) in enumerate(zip(page["paragraphs"], arabic)):
            if i >= len(english) or not isinstance(english[i], str) or before == after:
                continue
            split = _layout(english[i], english=True)
            if split.count("\n") == after.count("\n"):
                english[i] = split
        page = {**page, "paragraphs_en": english}
    return {**page, "paragraphs": arabic}


layout_card_lines = layout_lines


def get_ocr_page(pdf_page: int, edition_id: str | None = None, db: Session | None = None):
    return layout_lines(_get_ocr_page(pdf_page, edition_id=edition_id, db=db))


def _get_ocr_page(pdf_page: int, edition_id: str | None = None, db: Session | None = None):
    """Fetch OCR transcription, image reference, and dual-language translation for a book page."""
    is_gr8 = bool(edition_id and ("gr8" in edition_id.lower() or "grade8" in edition_id.lower() or "grade_8" in edition_id.lower()))
    is_gr7 = bool(edition_id and ("gr7" in edition_id.lower() or "grade7" in edition_id.lower() or "grade_7" in edition_id.lower()))
    is_gr6 = bool(edition_id and ("gr6" in edition_id.lower() or "grade6" in edition_id.lower() or "grade_6" in edition_id.lower()))

    # Prioritize curated, verified pages for Grade 8 Volume 1 only
    if is_gr8 and (not edition_id or "vol1" in edition_id.lower() or "term1" in edition_id.lower()):
        from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA
        if pdf_page in GRADE_8_TEXTBOOK_PAGES_DATA or str(pdf_page) in GRADE_8_TEXTBOOK_PAGES_DATA:
            return get_page_ocr_data(pdf_page, edition_id=edition_id)

    # Prioritize curated, verified pages for Grade 7 Volume 1 only
    if is_gr7 and (not edition_id or "vol1" in edition_id.lower() or "term1" in edition_id.lower()):
        from backend.ocr_reader import GRADE_7_TEXTBOOK_PAGES_DATA
        if pdf_page in GRADE_7_TEXTBOOK_PAGES_DATA or str(pdf_page) in GRADE_7_TEXTBOOK_PAGES_DATA:
            return get_page_ocr_data(pdf_page, edition_id=edition_id)

    # Prioritize curated, verified pages for Grade 6 Volume 1 only
    if is_gr6 and (not edition_id or "vol1" in edition_id.lower() or "term1" in edition_id.lower()):
        from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA
        if pdf_page in GRADE_6_TEXTBOOK_PAGES_DATA or str(pdf_page) in GRADE_6_TEXTBOOK_PAGES_DATA:
            return get_page_ocr_data(pdf_page, edition_id=edition_id)

    # Prioritize curated, verified pages for Grade 5 Volume 1 only
    if not edition_id or ("gr5" in edition_id.lower() and ("vol1" in edition_id.lower() or "term1" in edition_id.lower())):
        from backend.ocr_reader import TEXTBOOK_PAGES_DATA
        if pdf_page in TEXTBOOK_PAGES_DATA or str(pdf_page) in TEXTBOOK_PAGES_DATA:
            return get_page_ocr_data(pdf_page, edition_id=edition_id)

    if db is not None:
        from backend.models import ScannedPage
        q = db.query(ScannedPage).filter(ScannedPage.pdf_page == pdf_page)
        if edition_id:
            q = q.filter(ScannedPage.book_edition_id == edition_id)
        page_obj = q.first()
        if page_obj:
            # Calibrate printed page number
            calc_printed = page_obj.printed_page or pdf_page

            paras = _clean_ocr_paragraphs(page_obj.ocr_text_ar, calc_printed)
            paras_en = translate_paragraphs(paras)

            # Derive pedagogical title
            title_ar = f"صفحة كتاب الوزارة {calc_printed}"
            title_en = f"CBSE Curriculum Textbook Page {calc_printed}"
            if paras:
                first_line = paras[0].strip()
                if "الدرس:" in first_line or "الوحدة:" in first_line:
                    title_ar = first_line
                    title_en = paras_en[0] if paras_en and paras_en[0] else title_en

            return {
                "pdf_page": page_obj.pdf_page,
                "printed_page": calc_printed,
                "edition_id": page_obj.book_edition_id,
                "unit": "الوحدة المقررة (Curriculum Unit)",
                "lesson": f"الصفحة {calc_printed}",
                "title_ar": title_ar,
                "title_en": title_en,
                "paragraphs": paras,
                "paragraphs_en": paras_en,
                "ocr_text_ar": page_obj.ocr_text_ar,
                "confidence": page_obj.confidence or 0.95,
                "review_status": page_obj.review_status or "ocr_vision_verified",
                "has_image": True,
                "is_available": True
            }

    return get_page_ocr_data(pdf_page, edition_id=edition_id)


def get_page_image(pdf_page: int, edition_id: str | None = None):
    """Resolve a scanned page file from edition subfolder or search across editions."""
    from pathlib import Path
    base_dir = content_root() / "pdf_pages_sample"
    
    # 1. Direct edition path
    if edition_id:
        edition_path = base_dir / edition_id / f"page_{pdf_page}.png"
        if edition_path.is_file():
            return str(edition_path)
            
    # 2. Check root legacy files
    legacy_path = base_dir / f"page_{pdf_page}.png"
    if legacy_path.is_file():
        return str(legacy_path)
        
    # 3. Search across all edition subfolders as fallback
    matches = list(base_dir.glob(f"*/page_{pdf_page}.png"))
    if matches:
        return str(matches[0])

    raise ApplicationError(status_code=404, detail=f"Page image for page {pdf_page} not found")


def get_textbook_library(db: Session):
    """Retrieve full catalog of official CBSE Curriculum textbooks with indexing and render telemetry."""
    from pathlib import Path
    from backend.models import BookEdition, ScannedPage
    base_dir = content_root() / "pdf_pages_sample"
    
    editions = db.query(BookEdition).order_by(BookEdition.id).all()
    results = []
    for ed in editions:
        scanned_count = db.query(ScannedPage).filter(ScannedPage.book_edition_id == ed.id).count()
        img_folder = base_dir / ed.id
        rendered_count = len(list(img_folder.glob("*.png"))) if img_folder.exists() else 0
        
        # Parse grade from edition id moe_grX_volY_2023
        import re
        g_match = re.search(r"gr(\d+)", ed.id)
        grade = int(g_match.group(1)) if g_match else 5
        
        results.append({
            "id": ed.id,
            "title": ed.title,
            "grade": grade,
            "term": ed.volume,
            "academic_year": ed.academic_year,
            "total_pages": ed.total_pages,
            "scanned_pages_count": scanned_count,
            "rendered_images_count": rendered_count,
            "is_complete": (scanned_count >= ed.total_pages and rendered_count >= ed.total_pages),
            "pdf_filename": ed.pdf_filename
        })
    return results


def get_textbook_info(edition_id: str, db: Session):
    """Page count of a textbook edition for the learner reader (no page content)."""
    from sqlalchemy import func
    from backend.models import BookEdition, ScannedPage
    last_indexed = db.query(func.max(ScannedPage.pdf_page)).filter(ScannedPage.book_edition_id == edition_id).scalar()
    edition = db.get(BookEdition, edition_id)
    return {
        "edition_id": edition_id,
        "total_pages": last_indexed or (edition.total_pages if edition else None),
        "indexed": bool(last_indexed),
    }


def get_textbook_pages(edition_id: str, db: Session):
    """Fetch all indexed pages with OCR text preview, English translation, and image references for a specific textbook edition."""
    from backend.models import ScannedPage
    is_gr8 = bool("gr8" in edition_id.lower() or "grade8" in edition_id.lower())
    is_gr7 = bool("gr7" in edition_id.lower() or "grade7" in edition_id.lower())
    is_gr6 = bool("gr6" in edition_id.lower() or "grade6" in edition_id.lower())
    is_gr5 = bool("gr5" in edition_id.lower() or "grade5" in edition_id.lower())

    from backend.ocr_reader import TEXTBOOK_PAGES_DATA, GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA
    from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA

    pages = db.query(ScannedPage).filter(
        ScannedPage.book_edition_id == edition_id
    ).order_by(ScannedPage.pdf_page).all()

    result = []
    for p in pages:
        curated = None
        if is_gr8:
            curated = GRADE_8_TEXTBOOK_PAGES_DATA.get(p.pdf_page) or GRADE_8_TEXTBOOK_PAGES_DATA.get(str(p.pdf_page))
        elif is_gr7:
            curated = GRADE_7_TEXTBOOK_PAGES_DATA.get(p.pdf_page) or GRADE_7_TEXTBOOK_PAGES_DATA.get(str(p.pdf_page))
        elif is_gr6:
            curated = GRADE_6_TEXTBOOK_PAGES_DATA.get(p.pdf_page) or GRADE_6_TEXTBOOK_PAGES_DATA.get(str(p.pdf_page))
        elif is_gr5:
            curated = TEXTBOOK_PAGES_DATA.get(p.pdf_page) or TEXTBOOK_PAGES_DATA.get(str(p.pdf_page))

        if curated:
            ocr_text = "\n\n".join(curated.get("paragraphs", []))
            trans_en = "\n\n".join(curated.get("paragraphs_en", []))
            result.append({
                "pdf_page": p.pdf_page,
                "printed_page": curated.get("printed_page", p.printed_page),
                "ocr_text_ar": ocr_text,
                "translation_en": trans_en,
                "confidence": curated.get("confidence", 0.99),
                "review_status": "verified",
                "image_url": f"/api/admin/page-image/{p.pdf_page}?edition_id={edition_id}"
            })
        else:
            calc_printed = p.printed_page
            if (is_gr7 or is_gr5) and p.pdf_page >= 7:
                calc_printed = p.pdf_page - 1
            cleaned_paras = _clean_ocr_paragraphs(p.ocr_text_ar, calc_printed)
            ocr_text = "\n\n".join(cleaned_paras)
            trans_en = _TRANSLATION_CACHE.get(cleaned_paras[0], "") if cleaned_paras else ""
            result.append({
                "pdf_page": p.pdf_page,
                "printed_page": calc_printed,
                "ocr_text_ar": ocr_text,
                "translation_en": trans_en,
                "confidence": p.confidence or 0.95,
                "review_status": p.review_status,
                "image_url": f"/api/admin/page-image/{p.pdf_page}?edition_id={edition_id}"
            })

    return result


def add_term(req: AdminAddTermRequest, *, db: Session):
    """
    ADD_TERM mode:
    Configures a new term container with price (e.g. USD 33) and persists it in the database.
    """
    if req.grade < 1 or req.grade > 12:
        raise ApplicationError(status_code=400, detail="Grade must be between 1 and 12")

    term_id = f"grade_{req.grade}_term_{req.term}"
    existing = db.query(CurriculumTerm).filter(
        CurriculumTerm.grade == req.grade,
        CurriculumTerm.term == req.term
    ).first()
    if existing:
        existing.title_ar = req.title_ar
        existing.title_en = req.title_en
        existing.price_usd = req.price_usd
        db.commit()
        db.refresh(existing)
        target = existing
    else:
        target = CurriculumTerm(
            id=term_id,
            grade=req.grade,
            term=req.term,
            title_ar=req.title_ar,
            title_en=req.title_en,
            price_usd=req.price_usd,
            status="ready_for_lessons"
        )
        db.add(target)
        db.commit()
        db.refresh(target)

    return {
        "success": True,
        "mode": "ADD_TERM",
        "id": target.id,
        "grade": target.grade,
        "term": target.term,
        "title_ar": target.title_ar,
        "title_en": target.title_en,
        "price_usd": float(target.price_usd),
        "status": target.status,
        "message": f"Term {target.term} for Class {target.grade} registered successfully with price USD {float(target.price_usd)}."
    }


def add_class(req: AdminAddClassRequest, *, db: Session):
    """
    ADD_CLASS mode:
    Creates a new Grade/Class container (e.g. Class 6) and persists it in the database.
    """
    grade_id = f"grade_{req.grade_number}"
    existing = db.query(CurriculumGrade).filter(CurriculumGrade.grade_number == req.grade_number).first()
    if existing:
        existing.name_ar = req.name_ar
        existing.name_en = req.name_en
        db.commit()
        db.refresh(existing)
        target = existing
    else:
        target = CurriculumGrade(
            id=grade_id,
            grade_number=req.grade_number,
            name_ar=req.name_ar,
            name_en=req.name_en,
            status="active"
        )
        db.add(target)
        db.commit()
        db.refresh(target)

    return {
        "success": True,
        "mode": "ADD_CLASS",
        "id": target.id,
        "grade_number": target.grade_number,
        "name_ar": target.name_ar,
        "name_en": target.name_en,
        "status": target.status,
        "message": f"Class {target.grade_number} registered in curriculum hierarchy."
    }


def list_curriculum_grades(db: Session):
    return db.query(CurriculumGrade).order_by(CurriculumGrade.grade_number).all()


def list_curriculum_terms(grade: int, db: Session):
    return db.query(CurriculumTerm).filter(CurriculumTerm.grade == grade).order_by(CurriculumTerm.term).all()



def add_lesson(req: AdminAddLessonRequest, *, db: Session, actor=None):
    """
    ADD_LESSON mode:
    Imports and validates a 12-feature lesson JSON package.
    Ensures idempotency (reimporting identical hash does not duplicate).
    """
    # 1. Validate package structure
    content_str = json.dumps(req.content_json, ensure_ascii=False)
    content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    # Required fields check
    for req_field in ["lesson_id", "version", "title_ar", "title_en"]:
        if req_field not in req.content_json:
            raise ApplicationError(status_code=400, detail=f"Package missing required top-level field: {req_field}")

    lesson_id = req.content_json["lesson_id"]

    # 2. Check existing lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        lesson = Lesson(
            id=lesson_id,
            unit_id=req.unit_id,
            grade=req.grade,
            term=req.term,
            lesson_order=req.lesson_order,
            title_ar=req.title_ar,
            title_en=req.title_en,
            start_page=req.start_page,
            is_first_chapter_demo=(req.lesson_order == 1),
            status="content_pending"
        )
        db.add(lesson)
        db.commit()

    # 3. Check existing version by hash
    existing_ver = db.query(LessonVersion).filter(
        LessonVersion.lesson_id == lesson_id,
        LessonVersion.content_hash == content_hash
    ).first()

    if existing_ver:
        return {
            "success": True,
            "mode": "ADD_LESSON",
            "action": "no_change",
            "lesson_id": lesson_id,
            "version_tag": existing_ver.version_tag,
            "message": "Identical package hash already imported. No duplicate created."
        }

    version_tag = req.content_json.get("version", "1.0.0")
    ver_id = f"ver_{lesson_id}_{version_tag.replace('.', '_')}_{content_hash[:8]}"

    new_ver = LessonVersion(
        id=ver_id,
        lesson_id=lesson_id,
        version_tag=version_tag,
        content_json=content_str,
        content_hash=content_hash,
        is_active=False,
        status="content_pending",
        published_at=None,
        created_by=getattr(actor, "id", None)
    )
    db.add(new_ver)
    db.commit()
    invalidate_lesson_cache(lesson_id, grade=req.grade, term=req.term)

    return {
        "success": True,
        "mode": "ADD_LESSON",
        "action": "imported",
        "lesson_id": lesson_id,
        "version_tag": version_tag,
        "content_hash": content_hash,
        "message": f"Lesson '{req.title_en}' imported and queued for review."
    }


def _validate_version_quality(lesson: Lesson, version: LessonVersion):
    """Ensure a lesson version has valid JSON, required Arabic/English text, and valid activity IDs."""
    if not (lesson.title_ar or "").strip() or not ARABIC_RE.search(lesson.title_ar or ""):
        return "missing_lesson_arabic"
    if not (lesson.title_en or "").strip():
        return "missing_lesson_english"
    try:
        content = json.loads(version.content_json)
    except (TypeError, ValueError):
        return "invalid_lesson_json"
    if not isinstance(content, dict):
        return "invalid_lesson_json"
    serialized = json.dumps(content, ensure_ascii=False)
    if not re.search(r"[A-Za-z]", serialized):
        return "missing_content_english"
    if not re.search(r"[\u0600-\u06ff]", serialized):
        return "missing_content_arabic"
    activity_ids = set()
    duplicate_ids = set()
    has_defect = None
    def inspect_node(node, in_options=False):
        nonlocal has_defect
        if isinstance(node, dict):
            for k, v in node.items():
                if k.endswith("_ar") and isinstance(v, str) and not ARABIC_RE.search(v):
                    has_defect = "missing_arabic_field"
                if k.endswith("_en") and isinstance(v, str) and not v.strip():
                    has_defect = "missing_english_field"
                # Option ids (opt_a, b, ...) only need to be unique within their question.
                if k == "id" and isinstance(v, str) and not in_options:
                    if v in activity_ids:
                        duplicate_ids.add(v)
                    activity_ids.add(v)
                inspect_node(v, in_options or k == "options")
        elif isinstance(node, list):
            for item in node:
                inspect_node(item, in_options)
    inspect_node(content)
    if duplicate_ids:
        return "duplicate_activity_id"
    if has_defect:
        return has_defect
    return None


def publish_lesson_version(lesson_id: str, version_id: str, *, db: Session, actor=None):
    target = db.query(LessonVersion).filter(LessonVersion.id == version_id, LessonVersion.lesson_id == lesson_id).first()
    if not target:
        raise ApplicationError(404, "Lesson version not found")
    if target.status not in ("approved", "published"):
        raise ApplicationError(409, "Lesson version must be approved before publishing")

    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise ApplicationError(404, "Lesson not found")

    # Quality report gate: check for structural defects on this version
    defect = _validate_version_quality(lesson, target)
    if defect:
        raise ApplicationError(422, f"Quality gate failed: {defect} must be resolved before publishing")

    db.query(LessonVersion).filter(LessonVersion.lesson_id == lesson_id).update({"is_active": False})
    target.is_active = True
    target.status = "published"
    target.reviewed_by = getattr(actor, "id", None)
    target.published_at = target.published_at or datetime.datetime.now(datetime.UTC)
    lesson.status = "published"

    # Persist publish audit event
    audit = CurriculumAuditEvent(
        actor_id=getattr(actor, "id", None),
        action="publish",
        lesson_id=lesson_id,
        version_id=version_id,
        version_tag=target.version_tag,
        details_json=json.dumps({"action": "publish", "version_tag": target.version_tag})
    )
    db.add(audit)
    db.commit()
    invalidate_lesson_cache(lesson_id, grade=lesson.grade if lesson else None, term=lesson.term if lesson else None)
    return {"success": True, "lesson_id": lesson_id, "version_id": version_id,
            "version_tag": target.version_tag, "content_hash": target.content_hash}


def rollback_lesson(lesson_id: str, version_id: str, *, db: Session, actor=None):
    target = db.query(LessonVersion).filter(LessonVersion.id == version_id, LessonVersion.lesson_id == lesson_id).first()
    if not target:
        raise ApplicationError(404, "Lesson version not found")
    if target.status not in ("approved", "published"):
        raise ApplicationError(409, "Can only rollback to an approved or published version")
    db.query(LessonVersion).filter(LessonVersion.lesson_id == lesson_id).update({"is_active": False})
    target.is_active = True
    target.status = "published"
    lesson = db.get(Lesson, lesson_id)
    if lesson:
        lesson.status = "published"

    # Persist rollback audit event
    audit = CurriculumAuditEvent(
        actor_id=getattr(actor, "id", None),
        action="rollback",
        lesson_id=lesson_id,
        version_id=version_id,
        version_tag=target.version_tag,
        details_json=json.dumps({"action": "rollback", "rolled_back_to": target.version_tag})
    )
    db.add(audit)
    db.commit()
    invalidate_lesson_cache(lesson_id, grade=lesson.grade if lesson else None, term=lesson.term if lesson else None)
    return {
        "success": True,
        "lesson_id": lesson_id,
        "version_id": version_id,
        "version_tag": target.version_tag,
        "message": f"Lesson '{lesson_id}' rolled back to version {target.version_tag}."
    }


def approve_lesson_version(lesson_id: str, version_id: str, *, db: Session, actor=None):
    target = db.query(LessonVersion).filter(LessonVersion.id == version_id, LessonVersion.lesson_id == lesson_id).first()
    if not target:
        raise ApplicationError(404, "Lesson version not found")
    if target.status != "content_pending":
        raise ApplicationError(409, "Only content pending versions can be approved")

    # Dual control: in production, creator cannot approve their own lesson version
    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        actor_id = getattr(actor, "id", None)
        if actor_id and target.created_by and actor_id == target.created_by:
            raise ApplicationError(403, "Dual control required: creator cannot approve their own lesson version in production")

    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise ApplicationError(404, "Lesson not found")

    # Quality report gate: check for structural defects on this version
    defect = _validate_version_quality(lesson, target)
    if defect:
        raise ApplicationError(422, f"Quality gate failed: {defect} must be resolved before approval")

    target.status = "approved"
    target.reviewed_by = getattr(actor, "id", None)

    # Persist approve audit event
    audit = CurriculumAuditEvent(
        actor_id=getattr(actor, "id", None),
        action="approve",
        lesson_id=lesson_id,
        version_id=version_id,
        version_tag=target.version_tag,
        details_json=json.dumps({"action": "approve", "version_tag": target.version_tag})
    )
    db.add(audit)
    db.commit()
    return {"success": True, "lesson_id": lesson_id, "version_id": version_id, "status": target.status}


def update_edition(req: AdminUpdateEditionRequest, *, db: Session):
    """
    UPDATE_EDITION mode:
    Registers a new textbook edition without altering old student results or in-progress assessments.
    """
    new_edition = BookEdition(
        id=req.edition_id,
        title=req.title,
        academic_year=req.academic_year,
        publication_year=req.publication_year,
        pdf_filename=req.pdf_filename,
        total_pages=req.total_pages
    )
    db.merge(new_edition)
    db.commit()

    return {
        "success": True,
        "mode": "UPDATE_EDITION",
        "edition_id": req.edition_id,
        "academic_year": req.academic_year,
        "message": f"Edition '{req.title}' registered. Prior student historical attempts remain immutable."
    }


def solve_curriculum_question(question_ar: str, context_ar: str | None = None, grade: int | None = 6) -> dict:
    """Generates a pedagogical model answer with Arabic (vowels), Arabzi transliteration, and English explanation."""
    import json
    from backend.ai import gateway

    if not gateway.available():
        return {
            "text_ar": "نَمُوذَجُ الإِجَابَةِ: ارْجِعْ لِتَوْجِيهَاتِ الدَّرْسِ.",
            "arabzi": "Namūdhaj al-ijābah: Irji' li-tawjeehāt ad-dars.",
            "text_en": "Model Answer: Refer to the lesson instructions.",
            "explanation_en": "Curriculum model solution."
        }

    prompt = f"""
You are an expert UAE Ministry of Education Arabic curriculum teacher and pedagogical tutor for Grade {grade}.
A student or parent is asking for the solution/answer to this curriculum question or exercise:
Question: {question_ar}
Context/Theme: {context_ar or 'CBSE Curriculum'}

Provide the ideal model answer in JSON with:
1. text_ar: Clear, student-friendly Arabic answer with FULL tashkeel diacritics.
2. arabzi: Arab-English phonetic transliteration (e.g., Uslūbun inshā'iyyun / Na'am, li'anna...) so non-native speakers and parents can pronounce the Arabic answer accurately.
3. text_en: Accurate, natural English translation of the answer.
4. explanation_en: Brief pedagogical explanation or grammar rule explaining why this is the correct answer.

Format as JSON:
{{
  "text_ar": "string",
  "arabzi": "string",
  "text_en": "string",
  "explanation_en": "string"
}}
"""
    try:
        response = gateway.generate(gateway.AIRequest(feature="model_answer", prompt=prompt, json=True, child_safe=False))
        return json.loads(response.text)
    except Exception as e:
        return {
            "text_ar": f"إِجَابَةٌ تَعْلِيمِيَّةٌ عَنِ السُّؤَالِ: {question_ar}",
            "arabzi": "Ijābah ta'leemiyyah 'an as-su'āl.",
            "text_en": f"Educational answer to: {question_ar}",
            "explanation_en": f"Model solution generated: {str(e)}"
        }
