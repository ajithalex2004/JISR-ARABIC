"""Corrections to published lesson content, applied on deploy (backend/migrations.py).

A fix never edits a stored version in place (each version keeps its integrity hash): the
corrected content becomes a new published version and the old one stays in the history, so the
change can be rolled back from the admin screens. A fix applies only while its wrong text is
still in the lesson's active version, so it runs once and leaves later edits alone.
"""
import datetime
import hashlib
import json
import re
import uuid

from sqlalchemy import inspect, text

# Optional tashkeel between and after letters.
_M = "[ً-ٰٟـ]*"


def _word(letters: str) -> str:
    return "".join(ch + _M for ch in letters)


# (lesson_id, wrong word as a regex, replacement, reason)
CONTENT_FIXES = [
    (
        "lesson_g3_t2_ch02",
        "ال" + _M + _word("مغنومات"),
        "البَضَائِعُ",
        "Card مَتْجَرٌ (shop): \"a place where spoils of war (المغنومات) and clothes are sold\"; now \"goods (البضائع)\".",
    ),
]

FIX_ACTOR = "content-fix"


def _replace_in(node, regex, replacement):
    """Replace regex matches in every string of a parsed JSON value; returns (value, count)."""
    if isinstance(node, str):
        new, n = regex.subn(replacement, node)
        return new, n
    if isinstance(node, list):
        out, total = [], 0
        for item in node:
            v, n = _replace_in(item, regex, replacement)
            out.append(v); total += n
        return out, total
    if isinstance(node, dict):
        out, total = {}, 0
        for k, item in node.items():
            v, n = _replace_in(item, regex, replacement)
            out[k] = v; total += n
        return out, total
    return node, 0


def apply_content_fixes(conn, fixes=CONTENT_FIXES) -> list:
    """Publish a corrected version for each fix whose wrong text is still live; returns lesson ids."""
    if "lesson_versions" not in inspect(conn).get_table_names():
        return []
    has_audit = "curriculum_audit_events" in inspect(conn).get_table_names()
    fixed = []
    for lesson_id, pattern, replacement, reason in fixes:
        row = conn.execute(text(
            "SELECT id, version_tag, content_json FROM lesson_versions "
            "WHERE lesson_id=:l AND is_active=:a AND status='published'"), {"l": lesson_id, "a": True}).first()
        if row is None:
            continue
        try:
            data = json.loads(row.content_json or "")
        except ValueError:
            continue
        # Work on the parsed strings: stored JSON may hold Arabic as \\uXXXX escapes.
        data, hits = _replace_in(data, re.compile(pattern), replacement)
        if not hits:
            continue
        content = json.dumps(data, ensure_ascii="\\u06" in (row.content_json or ""))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        new_id = f"{row.id}_fix_{digest[:8]}"[:100]
        tag = f"{row.version_tag or 'v'}-fix"[:50]
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        conn.execute(text("UPDATE lesson_versions SET is_active=:f WHERE lesson_id=:l"), {"f": False, "l": lesson_id})
        conn.execute(text(
            "INSERT INTO lesson_versions (id, lesson_id, version_tag, content_json, content_hash, is_active, status, "
            "published_at, created_by, published_by, created_at) VALUES (:id, :l, :tag, :c, :h, :t, 'published', "
            ":now, :actor, :actor, :now)"),
            {"id": new_id, "l": lesson_id, "tag": tag, "c": content, "h": digest, "t": True, "now": now, "actor": FIX_ACTOR})
        if has_audit:
            conn.execute(text(
                "INSERT INTO curriculum_audit_events (id, actor_id, action, lesson_id, version_id, version_tag, details_json, created_at) "
                "VALUES (:id, NULL, 'content_fix', :l, :v, :tag, :d, :now)"),
                {"id": str(uuid.uuid4()), "l": lesson_id, "v": new_id, "tag": tag, "now": now,
                 "d": json.dumps({"action": "content_fix", "replaces": row.id, "reason": reason}, ensure_ascii=False)})
        fixed.append(lesson_id)
    return fixed
