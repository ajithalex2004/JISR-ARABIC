"""Root families for the Root Tree Explorer.

Every vocabulary card in the authored Class 5 catalogue names its root (e.g. ك-ت-ب). For a
root this module returns the words a learner has met in their lessons that share it, plus a
few more common words from the same family suggested by Gemini. Suggested words are checked
against the root letters and dropped if they do not contain them, then cached; they are
labelled as AI-suggested because no teacher has reviewed them.

Families are only generated for roots that appear in the catalogue, so the public endpoint
cannot be used to run arbitrary AI requests.
"""
import json
import logging
import re
from functools import lru_cache
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

FAMILY_CACHE_VERSION = "v1"
FAMILY_CACHE_TTL = 30 * 86400
MAX_FAMILY_WORDS = 8

_TASHKEEL = re.compile(r"[ً-ْٖ-ٰٟـ]")
_ARABIC_LETTER = re.compile(r"^[ء-ي]$")
_HAMZA = set("أإآءؤئ")
_WEAK = set("اوىي")
_KINDS = {"verb", "noun", "adjective", "doer", "object", "place", "instrument", "plural", "other"}

_SYSTEM_PROMPT = (
    "You are an Arabic morphology teacher for 10-year-old non-native learners studying Modern "
    "Standard Arabic. Given an Arabic root, give its core meaning in English and up to 8 common "
    "words derived from it that a school student is likely to meet. Every word must really be "
    "built from that root, be written with full tashkeel, and be standard MSA. Prefer a variety: "
    "the past-tense verb, the doer (فاعل), the done-to (مفعول), a place (مَفْعَل), a verbal noun. "
    "Give each word's own root; leave out any word whose root is different. "
    'Reply with JSON only: {"core_meaning_en": "<2-5 words>", "words": [{"word_ar": "...", "root": "<x-y-z>", '
    '"meaning_en": "<1-5 words>", "pattern": "<the وزن, e.g. فَاعِل>", '
    '"kind": "verb|noun|adjective|doer|object|place|instrument|plural|other"}]}'
)


def strip_tashkeel(text: str) -> str:
    return _TASHKEEL.sub("", text or "")


def normalize_root(text: Optional[str]) -> Optional[str]:
    """'كَ - تَ - بَ' or 'ك ت ب' -> 'ك-ت-ب'; None unless it is 3 or 4 Arabic letters."""
    letters = [c for c in strip_tashkeel(text or "") if not c.isspace() and c not in "-–—،,/"]
    if not 3 <= len(letters) <= 4 or not all(_ARABIC_LETTER.match(c) for c in letters):
        return None
    return "-".join(letters)


def split_roots(text: Optional[str]) -> List[str]:
    """A card's root field may hold two roots for a compound ('م-د-ن / ذ-ك-ي')."""
    return [r for r in (normalize_root(part) for part in (text or "").split("/")) if r]


def _same_letter(word_letter: str, root_letter: str) -> bool:
    if word_letter == root_letter:
        return True
    if root_letter in _HAMZA or root_letter == "ا":
        return word_letter in _HAMZA or word_letter == "ا"
    if root_letter in _WEAK:
        return word_letter in _WEAK or word_letter in _HAMZA
    return False


def root_letter_positions(word: str, root: str, strict: bool = False) -> Optional[List[int]]:
    """Indexes (into the word without tashkeel) of the root's letters, or None if absent.

    Matching runs from the end of the word so prefixes such as ال are not mistaken for root
    letters. A weak root letter (و ي ا) may be missing, as in قَالَ from ق-و-ل, and a doubled
    letter may be written once with shadda, as in مَدَّ from م-د-د. With ``strict`` only a first
    or last weak letter may be missing (وَجَدَ -> جِهَة, كُرَة from ك-ر-و), which stops مَدْرَسَة
    passing as a word from د-و-ر.
    """
    letters = strip_tashkeel(word)
    root_letters = root.split("-")

    def match(i: int, end: int) -> Optional[List[int]]:
        if i < 0:
            return []
        target = root_letters[i]
        candidates = [j for j in range(end - 1, -1, -1) if letters[j] == target]
        candidates += [j for j in range(end - 1, -1, -1)
                       if letters[j] != target and _same_letter(letters[j], target)]
        for j in candidates:
            rest = match(i - 1, j)
            if rest is not None:
                return rest + [j]
        doubled = i + 1 < len(root_letters) and root_letters[i + 1] == target
        edge = i in (0, len(root_letters) - 1)
        if (target in _WEAK and (edge or not strict)) or doubled:
            return match(i - 1, end)
        return None

    return match(len(root_letters) - 1, len(letters))


@lru_cache(maxsize=1)
def _catalogue():
    """(root -> words met in lessons, plain word -> card) from the authored catalogue."""
    from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG
    from backend.curriculum_seed import BALL_GAMES_CONTENT_V02

    packages = {"lesson_01_ball_games": BALL_GAMES_CONTENT_V02, **FULL_CURRICULUM_CATALOG}
    by_root: Dict[str, List[dict]] = {}
    by_word: Dict[str, dict] = {}
    for lesson_id, pkg in packages.items():
        for card in pkg.get("vocabulary_cards", []):
            word = card.get("vowelled_ar") or card.get("word_ar") or ""
            roots = split_roots(card.get("root"))
            entry = {
                "word_ar": word,
                "meaning_en": card.get("meaning_en", ""),
                "lesson_id": lesson_id,
                "lesson_title_en": pkg.get("title_en", ""),
                "lesson_title_ar": pkg.get("title_ar", ""),
                "grade": pkg.get("grade"),
                "term": pkg.get("term"),
            }
            by_word[strip_tashkeel(word)] = {"roots": roots, "note_en": card.get("root_note_en")}
            for root in roots:
                by_root.setdefault(root, []).append(entry)
    return by_root, by_word


def catalogue_roots() -> List[str]:
    return sorted(_catalogue()[0])


def _ai_family(root: str) -> Optional[dict]:
    from backend.ai import gateway
    from backend.ai.errors import AIUnavailable

    if not gateway.available():
        return None
    try:
        response = gateway.generate(gateway.AIRequest(
            feature="root_family", prompt=f"Root: {root.replace('-', ' - ')}",
            system=_SYSTEM_PROMPT, temperature=0.0, json=True,
        ))
        data = json.loads(response.text or "{}")
    except AIUnavailable as exc:
        logger.warning("AI root family unavailable for %s: %s", root, exc)
        return None
    except Exception as exc:
        logger.warning("AI root family failed for %s: %s", root, exc)
        return None

    words, seen = [], set()
    for item in data.get("words") or []:
        if not isinstance(item, dict):
            continue
        word = re.sub(r"\s+", " ", str(item.get("word_ar", ""))).strip()
        meaning = str(item.get("meaning_en", "")).strip()[:60]
        plain = strip_tashkeel(word)
        if (not word or " " in word or not meaning or re.search(r"[؀-ۿ]", meaning)
                or plain in seen or normalize_root(str(item.get("root", ""))) != root
                or root_letter_positions(word, root, strict=True) is None):
            continue
        seen.add(plain)
        kind = str(item.get("kind", "")).lower()
        words.append({
            "word_ar": word,
            "meaning_en": meaning,
            "pattern": str(item.get("pattern", "")).strip()[:20] or None,
            "kind": kind if kind in _KINDS else "other",
        })
    core = str(data.get("core_meaning_en", "")).strip()[:60]
    return {"core_meaning_en": core if core and not re.search(r"[؀-ۿ]", core) else None,
            "words": words[:MAX_FAMILY_WORDS], "provider": response.provider}


def _family(root: str) -> Optional[dict]:
    from backend.redis_client import cache_get, cache_set

    key = f"root_family:{FAMILY_CACHE_VERSION}:{root}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    family = _ai_family(root)
    if family is not None and family["words"]:
        cache_set(key, family, ttl_seconds=FAMILY_CACHE_TTL)
    return family


def root_family(root: Optional[str] = None, word: Optional[str] = None) -> Optional[dict]:
    """Everything the Root Tree Explorer shows for one root or vocabulary word; None if neither is usable."""
    by_root, by_word = _catalogue()
    note = None
    roots: List[str] = []
    card = by_word.get(strip_tashkeel(word or "").strip()) if word else None
    if card is not None:
        # The catalogue is the corrected source, so prefer it over a root sent by an older client.
        roots, note = card["roots"], card["note_en"]
        if not roots:
            return {"root": None, "roots": [], "borrowed": True, "note_en": note, "letters": [],
                    "core_meaning_en": None, "curriculum_words": [], "family": [],
                    "family_source": "none"}
    else:
        roots = split_roots(root)
    if not roots:
        return None

    requested = normalize_root(root) if root else None
    chosen = requested if requested in roots else roots[0]
    known = chosen in by_root
    family = _family(chosen) if known else None
    lesson_words = by_root.get(chosen, [])
    lesson_plain = {strip_tashkeel(w["word_ar"]) for w in lesson_words}
    return {
        "root": chosen,
        "roots": roots,
        "borrowed": False,
        "note_en": note,
        "letters": chosen.split("-"),
        "core_meaning_en": (family or {}).get("core_meaning_en"),
        "curriculum_words": lesson_words,
        "family": [w for w in (family or {}).get("words", []) if strip_tashkeel(w["word_ar"]) not in lesson_plain],
        # "ai": suggested by AI, checked against the root letters, not reviewed by a teacher.
        "family_source": "ai" if family and family["words"] else ("unavailable" if known else "none"),
    }
