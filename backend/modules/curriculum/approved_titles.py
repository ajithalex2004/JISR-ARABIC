"""Chapter titles approved by a teacher against the Ministry textbooks.

The app's chapter titles came from a hand-written syllabus outline, while the lessons were drafted
from the textbook pages, so most titles did not name what the chapter teaches. A teacher checks
each class in the "Chapter Titles for Approval" doc; the approved titles are added to
approved_chapter_titles.json (scripts/approved_titles_from_table.py turns a class's table from
the doc into its entries) and every deploy applies them:

  - the lessons table (title_ar, title_en), which the lesson list, paywall, Parent Dashboard,
    parent tips and mobile app all read;
  - optionally the chapter's unit (title_ar, title_en);
  - the served copy of each lesson's content header (the stored content keeps its integrity hash);
  - the syllabus outline used where a class has no lessons in the database.

Entries are keyed "<class>-<term>-<chapter>" (chapter = lesson_order). Applying is idempotent: a
row is written only when its title differs, and each change is recorded as a "title_update"
audit event with the old and new titles.
"""
import datetime
import json
import re
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

from sqlalchemy import inspect, text

_MARKS = re.compile(r"[\u064b-\u0670\u065f\u0640]")
DATA_FILE = Path(__file__).with_name("approved_chapter_titles.json")
TITLE_FIELDS = ("title_ar", "title_en")
UNIT_FIELDS = ("unit_title_ar", "unit_title_en")


def _key(grade, term, order) -> str:
    return f"{int(grade)}-{int(term)}-{int(order)}"


def validate(data: dict) -> Dict[str, dict]:
    """Check the file's entries; returns {key: entry}. Raises ValueError naming the bad entry."""
    titles = data.get("titles", data)
    out = {}
    for key, entry in titles.items():
        parts = key.split("-")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"{key}: key must be <class>-<term>-<chapter>, e.g. 3-1-2")
        grade, term, order = map(int, parts)
        if not (1 <= grade <= 12 and term in (1, 2, 3) and order >= 1):
            raise ValueError(f"{key}: class 1-12, term 1-3, chapter 1 or more")
        if not isinstance(entry, dict):
            raise ValueError(f"{key}: entry must be an object")
        for field in TITLE_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip() or "?" in value:
                raise ValueError(f"{key}: {field} is missing or still has a '?'")
        for field in UNIT_FIELDS:
            if field in entry and (not isinstance(entry[field], str) or not entry[field].strip()):
                raise ValueError(f"{key}: {field} must be a non-empty text when given")
        extra = set(entry) - set(TITLE_FIELDS) - set(UNIT_FIELDS) - {"approved_by", "note"}
        if extra:
            raise ValueError(f"{key}: unknown field(s) {sorted(extra)}")
        out[_key(grade, term, order)] = {k: v.strip() if isinstance(v, str) else v for k, v in entry.items()}
    return out


@lru_cache(maxsize=1)
def approved_titles() -> Dict[str, dict]:
    if not DATA_FILE.exists():
        return {}
    return validate(json.loads(DATA_FILE.read_text(encoding="utf-8")))


def approved_for(grade, term, order) -> Optional[dict]:
    try:
        return approved_titles().get(_key(grade, term, order))
    except (TypeError, ValueError):
        return None


def apply_approved_titles(conn, titles: Optional[Dict[str, dict]] = None) -> Tuple[int, int]:
    """Write approved titles into lessons (and units); returns (lessons changed, units changed)."""
    titles = approved_titles() if titles is None else titles
    tables = set(inspect(conn).get_table_names())
    if not titles or "lessons" not in tables:
        return 0, 0
    has_audit = "curriculum_audit_events" in tables
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    lessons_changed = units_changed = 0
    for key, entry in titles.items():
        grade, term, order = map(int, key.split("-"))
        rows = conn.execute(text(
            "SELECT id, unit_id, title_ar, title_en FROM lessons WHERE grade=:g AND term=:t AND lesson_order=:o "
            "AND (status IS NULL OR status <> 'retired')"),
            {"g": grade, "t": term, "o": order}).fetchall()
        for row in rows:
            before = {"title_ar": row.title_ar, "title_en": row.title_en}
            after = {f: entry[f] for f in TITLE_FIELDS}
            # Vowel marks don't count: a later deploy step may add tashkeel to an approved title.
            if (_plain(before["title_ar"]), before["title_en"]) != (_plain(after["title_ar"]), after["title_en"]):
                conn.execute(text("UPDATE lessons SET title_ar=:a, title_en=:e WHERE id=:id"),
                             {"a": after["title_ar"], "e": after["title_en"], "id": row.id})
                lessons_changed += 1
                if has_audit:
                    conn.execute(text(
                        "INSERT INTO curriculum_audit_events (id, actor_id, action, lesson_id, version_id, version_tag, "
                        "details_json, created_at) VALUES (:id, NULL, 'title_update', :l, '', NULL, :d, :now)"),
                        {"id": str(uuid.uuid4()), "l": row.id, "now": now,
                         "d": json.dumps({"action": "title_update", "before": before, "after": after,
                                          "approved_by": entry.get("approved_by")}, ensure_ascii=False)})
            if "units" in tables and row.unit_id and any(f in entry for f in UNIT_FIELDS):
                unit = conn.execute(text("SELECT title_ar, title_en FROM units WHERE id=:id"), {"id": row.unit_id}).first()
                if unit is not None:
                    new_ar = entry.get("unit_title_ar", unit.title_ar)
                    new_en = entry.get("unit_title_en", unit.title_en)
                    if (unit.title_ar, unit.title_en) != (new_ar, new_en):
                        conn.execute(text("UPDATE units SET title_ar=:a, title_en=:e WHERE id=:id"),
                                     {"a": new_ar, "e": new_en, "id": row.unit_id})
                        units_changed += 1
    return lessons_changed, units_changed


def _plain(value) -> str:
    return _MARKS.sub("", value or "").strip()


def served_content_titles(lesson, content: dict) -> dict:
    """The lesson's content with its header titles set to the approved ones (served copy only)."""
    entry = approved_for(getattr(lesson, "grade", 0), getattr(lesson, "term", 0), getattr(lesson, "lesson_order", 0))
    if not entry or not isinstance(content, dict):
        return content
    patch = {f: entry[f] for f in TITLE_FIELDS}
    patch.update({f: entry[f] for f in UNIT_FIELDS if f in entry})
    return {**content, **patch}
