"""English meanings for single Arabic words that the client-side dictionary does not cover.

The web and mobile word tooltips ship a static dictionary; any word missing from it
is looked up here. Gemini gives a short, context-aware gloss; Google Translate is the
fallback when Gemini is unavailable; machine translations that would mislead (lists of
alternatives, bare function words) are dropped. Results are cached in-process.
"""
import json
import logging
import re
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)

_ARABIC = re.compile(r"[؀-ۿ]")
_PARTS_OF_SPEECH = {"noun", "verb", "adjective", "particle", "pronoun", "adverb"}
_CACHE_MAX = 5000
_cache: "OrderedDict[tuple[str, str], dict]" = OrderedDict()

_SYSTEM_PROMPT = (
    "You are an Arabic-English dictionary for school students learning Modern Standard Arabic. "
    "Given one Arabic word (with any attached prefixes or suffixes) and optionally the sentence it "
    "appears in, give its English meaning as used in that sentence. Include attached particles in "
    "the meaning (e.g. وَسِيلَة in 'وسيلة لتحقيق' -> 'a means'; وَالرَّغَبَاتِ -> 'and the desires'). "
    'Reply with JSON only: {"translation": "<1-5 English words>", "part_of_speech": '
    '"noun|verb|adjective|particle|pronoun|adverb"}'
)


def _clean(text: str, limit: int) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()[:limit]


def _gemini_gloss(word: str, context: str) -> Optional[dict]:
    from backend.modules.tutoring.assistant import GEMINI_MODEL, _child_safety_settings, _get_gemini_client

    client = _get_gemini_client()
    if client is None:
        return None
    try:
        from google.genai import types

        prompt = f"Word: {word}" + (f"\nSentence: {context}" if context else "")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0.0,
                response_mime_type="application/json",
                safety_settings=_child_safety_settings(types),
            ),
        )
        data = json.loads(response.text or "{}")
        translation = _clean(str(data.get("translation", "")), 80)
        if not translation or _ARABIC.search(translation):
            return None
        pos = str(data.get("part_of_speech", "")).lower()
        return {"translation": translation, "part_of_speech": pos if pos in _PARTS_OF_SPEECH else None, "source": "gemini"}
    except Exception as exc:
        logger.warning("Gemini word gloss failed for %r: %s", word, exc)
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
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]

    result = _gemini_gloss(word, context) or _machine_translation(word)
    if result is not None:
        _cache[key] = result
        if len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)
    return result
