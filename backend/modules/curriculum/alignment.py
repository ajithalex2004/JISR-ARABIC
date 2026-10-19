"""Arabic–English matching highlights.

For a sentence and its English translation, records which Arabic words match which English
words, so tapping a word on one side lights up its match on the other. Matches are phrase
chunks rather than single words, because one Arabic word is often several English words
(وَسَيَكْتُبُونَهَا -> "and they will write it") and some words have no counterpart at all.

Gemini proposes the chunks; every alignment is checked here before it is stored, and a
sentence whose alignment fails the check simply shows no highlighting. Alignments are stored
in sentence_alignments, and only sentences from the authored catalogue are sent to the AI.
"""
import hashlib
import json
import logging
import re
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MAX_NEW_PER_REQUEST = 12
MAX_AR_CHUNK = 5
MAX_EN_CHUNK = 10
MIN_COVERAGE = 0.6

_ARABIC_LETTER = re.compile(r"[ء-ي]")
_LATIN_LETTER = re.compile(r"[A-Za-z]")

_SYSTEM_PROMPT = (
    "You align Arabic sentences with their English translations for children learning Arabic. "
    "For each pair, group the words into the smallest chunks whose meanings match. An Arabic chunk "
    "must be consecutive words; an English chunk may skip words. One Arabic word often matches "
    "several English words (وَسَيَكْتُبُونَهَا -> and they will write it). Leave out words with no "
    "counterpart, such as English 'is'/'are' in an Arabic nominal sentence. Use only the word "
    "numbers given, and use each word at most once. "
    'Reply with JSON only: {"alignments": [{"pair": 0, "chunks": [{"ar": [0], "en": [0, 1]}]}]}'
)


def words(text: str) -> List[str]:
    return (text or "").split()


def pair_id(arabic: str, english: str) -> str:
    key = " ".join(words(arabic)) + "\u0000" + " ".join(words(english))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def split_sentences(arabic: str, english: str) -> List[Tuple[str, str]]:
    """A passage as sentence pairs, split the way the mobile app splits it."""
    ar = [s for s in re.split(r"(?<=[.؟!])\s+", arabic or "") if s.strip()]
    en = [s for s in re.split(r"(?<=[.?!])\s+", english or "") if s.strip()]
    return [(a, en[i]) for i, a in enumerate(ar) if i < len(en)]


def catalogue_sentence_pairs(package: dict) -> List[Tuple[str, str]]:
    """The sentence + translation pairs a lesson shows."""
    pairs = []
    for card in package.get("vocabulary_cards") or []:
        pairs.append((card.get("example_ar"), card.get("example_en")))
    for section in (package.get("grammar_lab") or {}).get("sections") or []:
        for example in section.get("examples") or []:
            pairs.append((example.get("phrase_ar"), example.get("translation_en")))
    for item in package.get("instruction_decoder") or []:
        pairs.append((item.get("sample_sentence_ar"), item.get("sample_sentence_en")))
    studio = package.get("listen_speak_studio") or {}
    for script in studio.get("audio_scripts") or []:
        pairs.append((script.get("text_ar"), script.get("text_en")))
    pairs.extend(split_sentences(studio.get("passage_ar", ""), studio.get("passage_en", "")))
    return [(a, e) for a, e in pairs if isinstance(a, str) and isinstance(e, str) and a.strip() and e.strip()]


@lru_cache(maxsize=1)
def _catalogue_ids() -> frozenset:
    from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG
    from backend.curriculum_seed import BALL_GAMES_CONTENT_V02

    ids = set()
    for package in [BALL_GAMES_CONTENT_V02, *FULL_CURRICULUM_CATALOG.values()]:
        ids.update(pair_id(a, e) for a, e in catalogue_sentence_pairs(package))
    return frozenset(ids)


def validate_chunks(arabic: str, english: str, chunks) -> Optional[List[dict]]:
    """The chunks, cleaned and sorted, if they describe a usable alignment; otherwise None."""
    ar_words, en_words = words(arabic), words(english)
    if not isinstance(chunks, list) or not chunks:
        return None
    used_ar, used_en, clean = set(), set(), []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            return None
        ar, en = chunk.get("ar"), chunk.get("en")
        if not (isinstance(ar, list) and isinstance(en, list) and ar and en):
            return None
        if not all(isinstance(i, int) and not isinstance(i, bool) for i in ar + en):
            return None
        ar, en = sorted(set(ar)), sorted(set(en))
        if ar[0] < 0 or ar[-1] >= len(ar_words) or en[0] < 0 or en[-1] >= len(en_words):
            return None
        if ar[-1] - ar[0] + 1 != len(ar) or len(ar) > MAX_AR_CHUNK or len(en) > MAX_EN_CHUNK:
            return None
        if used_ar.intersection(ar) or used_en.intersection(en):
            return None
        used_ar.update(ar)
        used_en.update(en)
        clean.append({"ar": ar, "en": en})
    arabic_words = [i for i, w in enumerate(ar_words) if _ARABIC_LETTER.search(w)]
    english_words = [i for i, w in enumerate(en_words) if _LATIN_LETTER.search(w)]
    if not arabic_words or not english_words:
        return None
    coverage = sum(1 for i in arabic_words if i in used_ar) / len(arabic_words)
    if coverage < (1.0 if len(arabic_words) <= 2 else MIN_COVERAGE):
        return None
    return sorted(clean, key=lambda c: c["ar"][0])


def _numbered(text: str) -> str:
    return " ".join(f"{i}:{w}" for i, w in enumerate(words(text)))


def _ai_align(pairs: Sequence[Tuple[str, str]]) -> Optional[Tuple[Dict[int, Optional[list]], str]]:
    """{pair index: chunks or None} from one AI call, or None if the AI could not be used."""
    from backend.ai import gateway
    from backend.ai.errors import AIUnavailable

    if not gateway.available():
        return None
    prompt = "\n\n".join(
        f"Pair {i}\nArabic: {_numbered(a)}\nEnglish: {_numbered(e)}" for i, (a, e) in enumerate(pairs)
    )
    try:
        response = gateway.generate(gateway.AIRequest(
            feature="word_alignment", prompt=prompt, system=_SYSTEM_PROMPT, temperature=0.0, json=True,
        ))
        data = json.loads(response.text or "{}")
    except AIUnavailable as exc:
        logger.warning("AI alignment unavailable: %s", exc)
        return None
    except Exception as exc:
        logger.warning("AI alignment failed: %s", exc)
        return None

    results: Dict[int, Optional[list]] = {i: None for i in range(len(pairs))}
    for item in data.get("alignments") or []:
        if not isinstance(item, dict) or not isinstance(item.get("pair"), int):
            continue
        index = item["pair"]
        if 0 <= index < len(pairs):
            results[index] = validate_chunks(pairs[index][0], pairs[index][1], item.get("chunks"))
    return results, response.provider


def get_alignments(db: Session, pairs: Sequence[Tuple[str, str]]) -> List[Optional[List[dict]]]:
    """Chunks for each (arabic, english) pair, in order; None where no alignment is available.

    Stored alignments are returned as they are. Catalogue sentences without one are aligned
    now, up to MAX_NEW_PER_REQUEST per request, so a page fills in over a few visits at most.
    """
    from backend.models import SentenceAlignment

    ids = [pair_id(a, e) for a, e in pairs]
    rows = {r.id: r for r in db.query(SentenceAlignment).filter(SentenceAlignment.id.in_(set(ids))).all()}

    catalogue = _catalogue_ids()
    missing, seen = [], set()
    for (a, e), pid in zip(pairs, ids):
        if pid not in rows and pid in catalogue and pid not in seen:
            seen.add(pid)
            missing.append((pid, a, e))
    missing = missing[:MAX_NEW_PER_REQUEST]

    if missing:
        outcome = _ai_align([(a, e) for _, a, e in missing])
        if outcome is not None:
            results, provider = outcome
            for index, (pid, a, e) in enumerate(missing):
                chunks = results.get(index)
                # A failed check is stored too ("unusable"), so the AI isn't asked again on every visit.
                row = SentenceAlignment(
                    id=pid, arabic=a, english=e, chunks_json=json.dumps(chunks or []),
                    status="ai" if chunks else "unusable", provider=provider,
                )
                try:
                    db.add(row)
                    db.commit()
                except IntegrityError:
                    db.rollback()  # another request stored it first
                    row = db.get(SentenceAlignment, pid)
                if row is not None:
                    rows[pid] = row

    output = []
    for pid in ids:
        row = rows.get(pid)
        if row is None or row.status not in ("ai", "approved"):
            output.append(None)
        else:
            output.append(json.loads(row.chunks_json) or None)
    return output
