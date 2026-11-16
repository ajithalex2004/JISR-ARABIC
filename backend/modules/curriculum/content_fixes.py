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
] + [
    # Free-chapter pre-check (Classes 1-10, Term 1 chapter 1), confirmed by the content team.
    # Each wrong text is matched exactly as it stands in the live lesson.
    ("lesson_g1_t1_ch01", "تَصْبَحُ عَلَى خَيْرٍ", "تُصْبِحُ عَلَى خَيْرٍ", "Good night: tusbihu, not tasbahu."),
    ("lesson_g1_t1_ch01", "العَشْبِ", "العُشْبِ", "Grass is al-'ushb."),
    ("lesson_g1_t1_ch01", "^أ-ن-ا$", "", "The pronoun أَنَا has no root."),
    ("lesson_g1_t1_ch01", 'اللَّو(?:ۡ|َّ)نَ', 'اللَّوْنَ', "Wrong sukun character / stray shadda in the colour word."),
    ("lesson_g2_t1_ch01", r" \((?:ends with Baa|contains Baa in middle|starts with Baa)\)", "", "Exam Q2 English options gave the answer away."),
    ("lesson_g2_t1_ch01", r"\bBatten\b", "Batn", "Typo in the transliteration of بَطْنٌ."),
    ("lesson_g3_t1_ch01", "ร", "ر", "A Thai letter inside فَتْرَةُ رَاحَةٍ."),
    ("lesson_g3_t1_ch01", "شَعُورٌ", "شُعُورٌ", "Shu'ur, not sha'ur."),
    ("lesson_g3_t1_ch01", 'صَفُّكَا', "صَفُّكَ", "Not a valid form; your class is صَفُّكَ."),
    ("lesson_g4_t1_ch01", 'مَجَلاَّتٌ\\ تِجَارِيَّةٌ', "مَحَلَّاتٌ تِجَارِيَّةٌ", "Magazines written where shops are meant."),
    ("lesson_g4_t1_ch01", "مِنْ المَتْجَرِ", "مِنَ المَتْجَرِ", "Min takes fatha before al-."),
    ("lesson_g4_t1_ch01", "دُبَي[َُّ]*", "دُبَيّ", "One spelling of Dubai."),
    ("lesson_01_ball_games", 'تَتَكُونُ|تَتَكُوَّنُ', "تَتَكَوَّنُ", "Tatakawwanu, not tatakuwwanu."),
    ("lesson_01_ball_games", "فَرَدَيْنِ", "فَرْدَيْنِ", "Fardayn, not faradayn."),
    ("lesson_01_ball_games", 'أَحَدُ\\ الأَشْكَالِ\\ الَّذِي\\ يُشْبِهُ\\ البَيْضَةَ', "شَكْلٌ يُشْبِهُ البَيْضَةَ", "Definition of oval: agreement error."),
    ("lesson_01_ball_games", "بَيْضَوِي", "بَيْضَاوِي", "One spelling of oval (بَيْضَاوِيّ), as in the example sentences."),
    ("lesson_g6_t1_ch01", "الكَاكِئِنُ", "الكَائِنُ", "Typo in the living creature."),
    ("lesson_g6_t1_ch01", 'الطَّعَامُ\\ المَفْضُولُ', "الطَّعَامُ المُفَضَّلُ", "Favourite food is al-mufaddal."),
    ("lesson_g6_t1_ch01", "بَهِيظُ", "بَاهِظُ", "Expensive is bahiz."),
    ("lesson_g6_t1_ch01", "أَوْلَوِيَاتِ", "أَوْلَوِيَّاتِ", "Priorities carries a shadda."),
    ("lesson_g6_t1_ch01", "إِفْتِقَارٌ", "افْتِقَارٌ", "Iftiqar starts with hamzat wasl."),
    ("lesson_g6_t1_ch01", 'يُقْنِعُ\\ وَيُمِيلُ\\ الرَّأْيَ\\ أَوْ\\ السُّلُوكَ', "يُحْدِثُ تَغْيِيرًا فِي الرَّأْيِ أَوِ السُّلُوكِ", "Definition of to affect, not to persuade."),
    ("lesson_g6_t1_ch01", "المِتَابَعَةِ", "المُتَابَعَةِ", "Al-mutaba'a."),
    ("lesson_g7_t1_ch01", 'يُعَدُّ\\ زِيَارَةُ', "تُعَدُّ زِيَارَةُ", "Feminine subject."),
    ("lesson_g7_t1_ch01", "مَغَامَرَ", "مُغَامَرَ", "Adventure is mughamara."),
    ("lesson_g7_t1_ch01", 'النَّظَامُ', "النِّظَامُ", "System is an-nizam."),
    ("lesson_g7_t1_ch01", "^ر-و-ت$", "", "Routine is a borrowed word with no Arabic root."),
    ("lesson_g7_t1_ch01", 'مِنْ\\ الرِّحْلَةِ', "مِنَ الرِّحْلَةِ", "Min takes fatha before al-."),
    ("lesson_g8_t1_ch01", r" / التآزر\)", ")", "Exam Q3 English prompt gave the answer away."),
    ("lesson_g8_t1_ch01", "المَشْتَرَك", "المُشْتَرَك", "Shared is al-mushtarak."),
    ("lesson_g9_t1_ch01", 'يَؤُدِّي', "يُؤَدِّي", "Yu'addi."),
    ("lesson_g9_t1_ch01", r"\bAs size of a needle hole\b", "The Size of a Needle's Eye", "English title of the reading text."),
    ("lesson_g10_t1_ch01", "المَصَابِينَ", "المُصَابِينَ", "The injured are al-musabin."),
    ("lesson_g10_t1_ch01", "المَسْتَشْفَى", "المُسْتَشْفَى", "Hospital is al-mustashfa."),
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
    grouped = {}
    for lesson_id, pattern, replacement, reason in fixes:
        grouped.setdefault(lesson_id, []).append((pattern, replacement, reason))
    fixed = []
    for lesson_id, items in grouped.items():
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
        reasons = []
        for pattern, replacement, reason in items:
            # Count a fix only when it changes the text, so a deploy after it has run does nothing.
            fixed_data, _ = _replace_in(data, re.compile(pattern), replacement)
            if fixed_data != data:
                data = fixed_data
                reasons.append(reason)
        if not reasons:
            continue
        reason = " | ".join(reasons)
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
