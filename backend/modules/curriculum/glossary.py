"""English meanings for single Arabic words that the client-side dictionary does not cover.

The web and mobile word tooltips ship a static dictionary; any word missing from it
is looked up here. Gemini gives a short, context-aware gloss; Google Translate is the
fallback when Gemini is unavailable; machine translations that would mislead (lists of
alternatives, bare function words) are dropped. Results are cached in-process and in the
shared cache (so they survive restarts), keyed by word and sentence.

gloss_words() looks up every unknown word of a sentence with one AI call, so the apps can
fetch meanings before the student taps a word instead of waiting on each tap.
"""
import hashlib
import json
import logging
import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_ARABIC = re.compile(r"[؀-ۿ]")
_PARTS_OF_SPEECH = {"noun", "verb", "adjective", "particle", "pronoun", "adverb"}
_CACHE_MAX = 5000
_SHARED_TTL = 30 * 24 * 3600
MAX_BATCH_WORDS = 40
_cache: "OrderedDict[tuple[str, str], dict]" = OrderedDict()

_SYSTEM_PROMPT = (
    "You are an Arabic-English dictionary for school students learning Modern Standard Arabic. "
    "Given one Arabic word (with any attached prefixes or suffixes) and optionally the sentence it "
    "appears in, give its English meaning as used in that sentence. Include attached particles in "
    "the meaning (e.g. وَسِيلَة in 'وسيلة لتحقيق' -> 'a means'; وَالرَّغَبَاتِ -> 'and the desires'). "
    'Reply with JSON only: {"translation": "<1-5 English words>", "part_of_speech": '
    '"noun|verb|adjective|particle|pronoun|adverb"}'
)


_BATCH_PROMPT = (
    "You are an Arabic-English dictionary for school students learning Modern Standard Arabic. "
    "Given a sentence and a numbered list of Arabic words from it (with any attached prefixes or "
    "suffixes), give each word's English meaning as used in that sentence, including attached "
    "particles (e.g. وَالرَّغَبَاتِ -> 'and the desires'). Reply with JSON only: "
    '{"glosses": [{"n": <number>, "translation": "<1-5 English words>", '
    '"part_of_speech": "noun|verb|adjective|particle|pronoun|adverb"}]}'
)


def _clean(text: str, limit: int) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()[:limit]


def _shared_key(key: tuple) -> str:
    return "gloss:v1:" + hashlib.sha1("\u0000".join(key).encode("utf-8")).hexdigest()


def _cached(key: tuple) -> Optional[dict]:
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    from backend.redis_client import cache_get
    result = cache_get(_shared_key(key))
    if isinstance(result, dict) and result.get("translation"):
        _remember(key, result, shared=False)
        return result
    return None


def _remember(key: tuple, result: dict, shared: bool = True) -> None:
    _cache[key] = result
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)
    if shared:
        from backend.redis_client import cache_set
        cache_set(_shared_key(key), result, _SHARED_TTL)


def _checked(data: dict, source: str) -> Optional[dict]:
    translation = _clean(str(data.get("translation", "")), 80)
    if not translation or _ARABIC.search(translation):
        return None
    pos = str(data.get("part_of_speech", "")).lower()
    return {"translation": translation, "part_of_speech": pos if pos in _PARTS_OF_SPEECH else None, "source": source}


def _gemini_gloss(word: str, context: str) -> Optional[dict]:
    from backend.ai import gateway
    from backend.ai.errors import AIUnavailable

    if not gateway.available():
        return None
    try:
        prompt = f"Word: {word}" + (f"\nSentence: {context}" if context else "")
        response = gateway.generate(gateway.AIRequest(
            feature="word_meaning", prompt=prompt, system=_SYSTEM_PROMPT, temperature=0.0, json=True,
        ))
        return _checked(json.loads(response.text or "{}"), response.provider)
    except AIUnavailable as exc:
        logger.warning("AI word gloss unavailable for %r: %s", word, exc)  # already recorded by the gateway
        return None
    except Exception as exc:
        logger.warning("AI word gloss failed for %r: %s", word, exc)
        from backend.alerts import record_failure
        record_failure("gemini", f"Word meanings: {exc}")
        return None


# Function words a lone-word machine translation sometimes returns on its own ("TO THE").
_FUNCTION_WORDS = {
    "a", "an", "the", "to", "of", "for", "in", "on", "at", "by", "with", "from", "and", "or",
    "so", "as", "is", "it", "be", "will", "that", "this",
}


def _acceptable_machine_translation(text: str) -> Optional[str]:
    """Return a cleaned single-word translation, or None when it would mislead a learner."""
    text = _clean(text, 80).strip(" .")
    if not text or _ARABIC.search(text):
        return None
    # Dictionary-style lists of alternatives ("mean, contrivance, instrument, ...").
    if re.search(r"[,;/|]", text):
        return None
    words = text.split()
    if len(words) > 4 or all(w.lower() in _FUNCTION_WORDS for w in words):
        return None
    if text.isupper():
        text = text.lower()
    return text


def _google_word_translation(word: str) -> Optional[str]:
    import urllib.parse
    import urllib.request

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q=" + urllib.parse.quote(word)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "".join(seg[0] for seg in data[0] if seg and seg[0])
    except Exception as exc:
        logger.warning("Google word translation failed for %r: %s", word, exc)
        return None


def _machine_translation(word: str) -> Optional[dict]:
    # Google only: the MyMemory fallback used for paragraphs returns lists of
    # alternatives or bare function words for single words, which is worse than nothing.
    translation = _acceptable_machine_translation(_google_word_translation(word) or "")
    if translation is None:
        return None
    return {"translation": translation, "part_of_speech": None, "source": "machine_translation"}


def gloss_word(word: str, context: str = "") -> Optional[dict]:
    """Return {"translation", "part_of_speech", "source"} for an Arabic word, or None."""
    word = _clean(word, 40)
    context = _clean(context, 300)
    if not word or not _ARABIC.search(word):
        return None

    key = (word, context)
    cached = _cached(key)
    if cached is not None:
        return cached

    result = _gemini_gloss(word, context) or _machine_translation(word)
    if result is not None:
        _remember(key, result)
    return result


def _gemini_gloss_many(words: List[str], context: str) -> Dict[str, dict]:
    from backend.ai import gateway
    from backend.ai.errors import AIUnavailable

    if not gateway.available():
        return {}
    try:
        listing = "\n".join(f"{n}. {w}" for n, w in enumerate(words, 1))
        prompt = (f"Sentence: {context}\n" if context else "") + f"Words:\n{listing}"
        response = gateway.generate(gateway.AIRequest(
            feature="word_meaning", prompt=prompt, system=_BATCH_PROMPT, temperature=0.0, json=True,
        ))
        data = json.loads(response.text or "{}")
        found: Dict[str, dict] = {}
        for item in data.get("glosses") or []:
            if not isinstance(item, dict):
                continue
            try:
                word = words[int(item.get("n")) - 1]
            except (TypeError, ValueError, IndexError):
                continue
            result = _checked(item, response.provider)
            if result is not None:
                found[word] = result
        return found
    except AIUnavailable as exc:
        logger.warning("AI word glosses unavailable: %s", exc)
        return {}
    except Exception as exc:
        logger.warning("AI word glosses failed: %s", exc)
        from backend.alerts import record_failure
        record_failure("gemini", f"Word meanings: {exc}")
        return {}


def gloss_words(words: List[str], context: str = "") -> Dict[str, Optional[dict]]:
    """Meanings for several words of one sentence: cached ones first, the rest with one AI call
    (machine translation, in parallel, for any the AI leaves out). Keys are the words as sent."""
    context = _clean(context, 300)
    cleaned = {}
    for raw in words[:MAX_BATCH_WORDS]:
        word = _clean(raw, 40)
        if word and _ARABIC.search(word):
            cleaned.setdefault(raw, word)

    results: Dict[str, Optional[dict]] = {}
    missing: List[str] = []
    for raw, word in cleaned.items():
        results[raw] = _cached((word, context))
        if results[raw] is None and word not in missing:
            missing.append(word)

    found = _gemini_gloss_many(missing, context) if missing else {}
    leftover = [w for w in missing if w not in found]
    if leftover:
        with ThreadPoolExecutor(max_workers=min(6, len(leftover))) as pool:
            for word, result in zip(leftover, pool.map(_machine_translation, leftover)):
                if result is not None:
                    found[word] = result
    for word, result in found.items():
        _remember((word, context), result)
    for raw, word in cleaned.items():
        if results[raw] is None:
            results[raw] = found.get(word)
    return results
