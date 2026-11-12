"""Teacher review of English word meanings (the word tooltips).

Meanings come from the website's built-in dictionary and, for words it lacks, from the AI
(glossary.py). None of them had been checked by a person. This module keeps a review queue in
word_glosses: AI meanings are recorded there as "pending" the first time they are served, and a
teacher approves, corrects or rejects any word (built-in ones included). A reviewed word's
decision then wins over both sources:
  - approved / corrected: that meaning is served (by the AI lookup and, through
    word_corrections(), by the website's built-in dictionary);
  - rejected: no meaning is shown for the word.
"""
import datetime
import logging
import re
from typing import Dict, Iterable, Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import WordGloss

logger = logging.getLogger(__name__)

REVIEWED = ("approved", "corrected", "rejected")
PARTS_OF_SPEECH = {"noun", "verb", "adjective", "particle", "pronoun", "adverb"}
_MARKS = re.compile(r"[ً-ٰٟـ]")
_PUNCT = re.compile(r"[؟!.,،؛:'\"()\[\]\-—/\\«»<>]")
CORRECTIONS_CACHE_KEY = "word_corrections:v1"


def canonical_word(word: str) -> str:
    """Same key as the website's canonicalArabic(): no tashkeel or punctuation, alif/ta marbuta/ya unified."""
    w = _PUNCT.sub("", _MARKS.sub("", word or "")).strip()
    return re.sub(r"[إأآ]", "ا", w).replace("ة", "ه").replace("ى", "ي")[:80]


def teacher_decisions(db: Optional[Session], words: Iterable[str]) -> Dict[str, Optional[dict]]:
    """Reviewed words among `words` (keys as given): a meaning dict, or None when rejected."""
    if db is None:
        return {}
    by_key: Dict[str, list] = {}
    for w in words:
        key = canonical_word(w)
        if key:
            by_key.setdefault(key, []).append(w)
    if not by_key:
        return {}
    try:
        rows = db.query(WordGloss).filter(WordGloss.word.in_(list(by_key)), WordGloss.status.in_(REVIEWED)).all()
    except Exception as exc:  # the table may not exist yet on an old database
        logger.warning("Word review lookup failed: %s", exc)
        db.rollback()
        return {}
    out: Dict[str, Optional[dict]] = {}
    for row in rows:
        meaning = None if row.status == "rejected" or not row.translation else {
            "translation": row.translation, "part_of_speech": row.part_of_speech, "source": "teacher"}
        for w in by_key[row.word]:
            out[w] = meaning
    return out


def record_ai_meanings(db: Optional[Session], meanings: Dict[str, Optional[dict]]) -> int:
    """Queue AI/machine meanings for review the first time a word is served; returns rows added."""
    if db is None:
        return 0
    fresh = {}
    for word, m in meanings.items():
        key = canonical_word(word)
        if key and m and m.get("translation") and m.get("source") != "teacher":
            fresh.setdefault(key, (word, m))
    if not fresh:
        return 0
    try:
        known = {w for (w,) in db.query(WordGloss.word).filter(WordGloss.word.in_(list(fresh)))}
        added = 0
        for key, (word, m) in fresh.items():
            if key in known:
                continue
            db.add(WordGloss(word=key, word_display=word[:80], translation=str(m["translation"])[:160],
                             part_of_speech=m.get("part_of_speech"), source=str(m.get("source") or "ai")[:40]))
            added += 1
        db.commit()
        return added
    except Exception as exc:
        logger.warning("Recording word meanings for review failed: %s", exc)
        db.rollback()
        return 0


def list_queue(db: Session, status: str = "pending", q: str = "", limit: int = 50, offset: int = 0) -> dict:
    query = db.query(WordGloss)
    if status == "reviewed":
        query = query.filter(WordGloss.status.in_(REVIEWED))
    elif status != "all":
        query = query.filter(WordGloss.status == status)
    if q:
        query = query.filter(WordGloss.word.contains(canonical_word(q)))
    total = query.count()
    rows = query.order_by(WordGloss.created_at.desc()).offset(max(0, offset)).limit(min(200, max(1, limit))).all()
    counts = {s: db.query(WordGloss).filter(WordGloss.status == s).count() for s in ("pending",) + REVIEWED}
    return {"total": total, "counts": counts, "items": [_row(r) for r in rows]}


def _row(r: WordGloss) -> dict:
    return {"id": r.id, "word": r.word_display, "key": r.word, "translation": r.translation,
            "part_of_speech": r.part_of_speech, "source": r.source, "status": r.status,
            "reviewed_by": r.reviewed_by, "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
            "review_note": r.review_note}


def review_word(db: Session, *, word: str, action: str, actor_id: str, translation: str = "",
                part_of_speech: str = "", note: str = "", current: str = "", source: str = "") -> dict:
    """Record a teacher's decision on a word: approve its current meaning, correct it, or reject it.

    `current` and `source` describe the meaning being judged when the word isn't queued yet
    (a built-in dictionary word reviewed from the admin screen)."""
    key = canonical_word(word)
    if not key:
        raise ApplicationError(400, "Give an Arabic word")
    if action not in ("approve", "correct", "reject"):
        raise ApplicationError(400, "Action must be approve, correct or reject")
    pos = (part_of_speech or "").strip().lower() or None
    if pos and pos not in PARTS_OF_SPEECH:
        raise ApplicationError(400, f"Word type must be one of: {', '.join(sorted(PARTS_OF_SPEECH))}")
    row = db.query(WordGloss).filter(WordGloss.word == key).first()
    if row is None:
        row = WordGloss(word=key, word_display=word.strip()[:80], translation=(current or "").strip()[:160] or None,
                        part_of_speech=pos, source=(source or "dictionary")[:40])
        db.add(row)
    if action == "correct":
        if not translation.strip():
            raise ApplicationError(400, "Give the corrected meaning")
        row.translation = translation.strip()[:160]
        row.part_of_speech = pos or row.part_of_speech
        row.status = "corrected"
    elif action == "approve":
        if not (row.translation or "").strip():
            raise ApplicationError(400, "There is no meaning to approve; correct it instead")
        if pos:
            row.part_of_speech = pos
        row.status = "approved"
    else:
        row.status = "rejected"
    row.reviewed_by = actor_id
    row.reviewed_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    row.review_note = (note or "").strip()[:2000] or None
    db.commit()
    from backend.redis_client import cache_delete
    cache_delete(CORRECTIONS_CACHE_KEY)
    return _row(row)


def word_corrections(db: Session) -> Dict[str, dict]:
    """Every reviewed word, for the website's built-in dictionary: {key: {translation, part_of_speech}}.
    A rejected word has translation null (show no meaning)."""
    from backend.redis_client import cache_get, cache_set
    cached = cache_get(CORRECTIONS_CACHE_KEY)
    if isinstance(cached, dict):
        return cached
    try:
        rows = db.query(WordGloss).filter(WordGloss.status.in_(REVIEWED)).all()
    except Exception:
        db.rollback()
        return {}
    out = {r.word: {"translation": None if r.status == "rejected" else r.translation,
                    "part_of_speech": r.part_of_speech} for r in rows}
    cache_set(CORRECTIONS_CACHE_KEY, out, ttl_seconds=600)
    return out
