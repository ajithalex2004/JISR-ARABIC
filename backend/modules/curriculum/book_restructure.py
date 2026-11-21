"""Re-cut a term's chapters to match the textbook's own lessons, without disturbing learners.

Class 1 Terms 2 and 3 were imported as six 15-page chapters, while each book has ten letter
lessons (e.g. «الأرنب (أ)», «البطة (ب)»), so app chapters started mid-lesson. The new chapters are
added as *staged* lessons: hidden from learners, drafted from their exact book pages by the
admin "Draft from book" action, and reviewed and published by a teacher as usual. Once every
staged lesson of a term has a published version, the term switches over in one step: the old
chapters become *retired* (kept, with their history, but no longer listed or opened) and the
staged ones go live. Until then learners keep the old chapters.

Page numbers below were read from the scanned books (Class 1, 2023 edition): the PDF page where
each lesson starts (its "learning outcomes" page) and the printed page shown to learners.
"""
import datetime
import json
import uuid
from typing import Dict, List, Optional, Tuple

from sqlalchemy import inspect, text

STAGED = "staged"
RETIRED = "retired"
HIDDEN_STATUSES = (STAGED, RETIRED)

# (grade, term) -> last PDF page of the last lesson, and each lesson: (Arabic, English, printed page, PDF page)
BOOK_LESSONS: Dict[Tuple[int, int], Dict] = {
    (1, 2): {"last_pdf_page": 94, "lessons": [
        ("الأرنب (أ)", "The Rabbit (أ)", 8, 7),
        ("البطة (ب)", "The Duck (ب)", 18, 17),
        ("التمساح (ت)", "The Crocodile (ت)", 28, 27),
        ("الثعلب (ث)", "The Fox (ث)", 38, 37),
        ("الجمل (ج)", "The Camel (ج)", 48, 47),
        ("الحوت (ح)", "The Whale (ح)", 56, 55),
        ("الخروف (خ)", "The Sheep (خ)", 64, 63),
        ("الدب والذئب (د/ذ)", "The Bear and the Wolf (د/ذ)", 72, 71),
        ("الريم والزرافة (ر/ز)", "The Gazelle and the Giraffe (ر/ز)", 80, 79),
        ("السنجاب والشبل (س/ش)", "The Squirrel and the Cub (س/ش)", 88, 87),
    ]},
    (1, 3): {"last_pdf_page": 91, "lessons": [
        ("الصوص الصغير (ص)", "The Little Chick (ص)", 6, 6),
        ("الضفدع الضعيف (ض)", "The Weak Frog (ض)", 14, 14),
        ("الطاووس الجميل (ط/ظ)", "The Beautiful Peacock (ط/ظ)", 23, 23),
        ("العصفور والغراب (ع/غ)", "The Sparrow and the Crow (ع/غ)", 31, 31),
        ("الفأر والقط (ف/ق)", "The Mouse and the Cat (ف/ق)", 39, 39),
        ("الكلب واللامة (ك/ل)", "The Dog and the Llama (ك/ل)", 47, 47),
        ("الماعز والنحلة (م/ن)", "The Goat and the Bee (م/ن)", 55, 55),
        ("الهدهد والوطواط (هـ/و)", "The Hoopoe and the Bat (هـ/و)", 63, 63),
        ("اليمامة (ي)", "The Dove (ي)", 71, 71),
        ("الحروف العربية", "The Arabic Letters", 79, 79),
    ]},
}


def staged_id(grade: int, term: int, order: int) -> str:
    return f"lesson_g{grade}_t{term}_bk{order:02d}"


def _staged_pages() -> Dict[str, Tuple[int, int]]:
    """lesson id -> (first PDF page, last PDF page) for every book-aligned lesson."""
    out = {}
    for (grade, term), spec in BOOK_LESSONS.items():
        lessons = spec["lessons"]
        for i, (_, _, _, pdf_start) in enumerate(lessons):
            end = lessons[i + 1][3] - 1 if i + 1 < len(lessons) else spec["last_pdf_page"]
            out[staged_id(grade, term, i + 1)] = (pdf_start, end)
    return out


STAGED_PAGES = _staged_pages()


def book_pages(lesson_id: str) -> Optional[List[int]]:
    """The exact PDF pages of a book-aligned lesson, or None for any other lesson."""
    span = STAGED_PAGES.get(lesson_id)
    return list(range(span[0], span[1] + 1)) if span else None


def _audit(conn, lesson_id: str, action: str, details: dict) -> None:
    if "curriculum_audit_events" not in inspect(conn).get_table_names():
        return
    conn.execute(text(
        "INSERT INTO curriculum_audit_events (id, actor_id, action, lesson_id, version_id, version_tag, details_json, "
        "created_at) VALUES (:id, NULL, :a, :l, '', NULL, :d, :now)"),
        {"id": str(uuid.uuid4()), "a": action, "l": lesson_id, "d": json.dumps(details, ensure_ascii=False),
         "now": datetime.datetime.now(datetime.UTC).replace(tzinfo=None)})


def stage_book_lessons(conn) -> int:
    """Create the staged, book-aligned lessons that don't exist yet; returns how many were added."""
    if "lessons" not in inspect(conn).get_table_names():
        return 0
    added = 0
    for (grade, term), spec in BOOK_LESSONS.items():
        live = conn.execute(text(
            "SELECT id, unit_id FROM lessons WHERE grade=:g AND term=:t AND (status IS NULL OR status NOT IN (:s, :r)) "
            "ORDER BY lesson_order"), {"g": grade, "t": term, "s": STAGED, "r": RETIRED}).fetchall()
        if not live:
            continue  # nothing imported for this term: nothing to re-cut
        first_unit, second_unit = live[0].unit_id, live[-1].unit_id
        half = len(spec["lessons"]) // 2
        for order, (title_ar, title_en, printed, _) in enumerate(spec["lessons"], start=1):
            lesson_id = staged_id(grade, term, order)
            if conn.execute(text("SELECT 1 FROM lessons WHERE id=:id"), {"id": lesson_id}).first():
                continue
            conn.execute(text(
                "INSERT INTO lessons (id, unit_id, grade, term, lesson_order, title_ar, title_en, start_page, "
                "is_first_chapter_demo, status) VALUES (:id, :u, :g, :t, :o, :ar, :en, :p, :free, :s)"),
                {"id": lesson_id, "u": first_unit if order <= half else second_unit, "g": grade, "t": term,
                 "o": order, "ar": title_ar, "en": title_en, "p": printed, "free": False, "s": STAGED})
            _audit(conn, lesson_id, "lesson_staged", {"grade": grade, "term": term, "order": order,
                                                       "pdf_pages": list(STAGED_PAGES[lesson_id])})
            added += 1
    return added


def promote_ready_terms(conn, grade: Optional[int] = None, term: Optional[int] = None) -> List[Tuple[int, int]]:
    """Switch every term whose staged lessons all have a published version; returns the terms switched."""
    tables = inspect(conn).get_table_names()
    if "lessons" not in tables or "lesson_versions" not in tables:
        return []
    switched = []
    for (g, t) in BOOK_LESSONS:
        if (grade is not None and g != grade) or (term is not None and t != term):
            continue
        staged = [row.id for row in conn.execute(text(
            "SELECT id FROM lessons WHERE grade=:g AND term=:t AND status=:s"), {"g": g, "t": t, "s": STAGED})]
        if not staged:
            continue
        published = {row.lesson_id for row in conn.execute(text(
            "SELECT DISTINCT lesson_id FROM lesson_versions WHERE status='published' AND is_active=:a"), {"a": True})}
        if not set(staged) <= published:
            continue
        retired = [row.id for row in conn.execute(text(
            "SELECT id FROM lessons WHERE grade=:g AND term=:t AND (status IS NULL OR status NOT IN (:s, :r))"),
            {"g": g, "t": t, "s": STAGED, "r": RETIRED})]
        if retired:
            conn.execute(text(f"UPDATE lessons SET status=:r WHERE id IN ({', '.join(':x%d' % i for i in range(len(retired)))})"),
                         {"r": RETIRED, **{f"x{i}": lid for i, lid in enumerate(retired)}})
        conn.execute(text("UPDATE lessons SET status='published' WHERE grade=:g AND term=:t AND status=:s"),
                     {"g": g, "t": t, "s": STAGED})
        for lesson_id in staged:
            _audit(conn, lesson_id, "lesson_promoted", {"grade": g, "term": t, "replaces": retired})
        switched.append((g, t))
    return switched


def version_states(db, lesson_ids: List[str]) -> Dict[str, str]:
    """Each lesson's furthest version: 'published' (active), else 'approved', else 'content_pending'."""
    from backend.models import LessonVersion
    if not lesson_ids:
        return {}
    rank = {"content_pending": 1, "approved": 2, "published": 3}
    out: Dict[str, str] = {}
    for lesson_id, status, active in db.query(LessonVersion.lesson_id, LessonVersion.status, LessonVersion.is_active).filter(
            LessonVersion.lesson_id.in_(lesson_ids), LessonVersion.status.in_(tuple(rank))):
        if status == "published" and not active:
            continue
        if rank[status] > rank.get(out.get(lesson_id, ""), 0):
            out[lesson_id] = status
    return out


def staged_progress(db, grade: int, term: int) -> Dict:
    """How close a re-cut term is to switching: its staged chapters and which still need a published version."""
    from backend.models import Lesson
    staged = (db.query(Lesson.id, Lesson.lesson_order, Lesson.title_en).filter(
        Lesson.grade == grade, Lesson.term == term, Lesson.status == STAGED).order_by(Lesson.lesson_order).all())
    states = version_states(db, [s.id for s in staged])
    waiting = [{"id": s.id, "lesson_order": s.lesson_order, "title_en": s.title_en, "version_state": states.get(s.id, "none")}
               for s in staged if states.get(s.id) != "published"]
    return {"total": len(staged), "published": len(staged) - len(waiting), "waiting": waiting}


def is_hidden(lesson) -> bool:
    return getattr(lesson, "status", None) in HIDDEN_STATUSES
