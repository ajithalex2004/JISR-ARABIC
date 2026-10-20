"""Read the Arabic text off a scanned textbook page image with Gemini vision.

Ministry textbook PDFs are scans: their pages are pictures with no text layer, so text
extraction from the PDF itself returns nothing. Each page is rendered to PNG and, when the
PDF has no usable text, Gemini transcribes the picture. Results still go through the
existing teacher review before reaching learners.
"""
import logging
import re
from typing import Optional

from backend.ai.errors import AIUnavailable

logger = logging.getLogger(__name__)

_ARABIC = re.compile(r"[؀-ۿ]")
MIN_ARABIC_CHARS = 20

# Some textbook PDFs have a text layer that places every glyph cluster on its own, so extraction
# returns "ت داَ رْ فُ ري مْ ثُ" instead of words. Real Arabic prose has under a quarter of its
# words at one or two letters; broken pages are mostly such fragments.
FRAGMENTED_STATUS = "text_fragmented"
_LETTER = re.compile(r"[\u0621-\u063A\u0641-\u064A\u0671-\u06D3]")  # letters only: no harakat or tatweel
MAX_SHORT_WORD_SHARE = 0.5
MIN_WORDS_TO_JUDGE = 8

_PROMPT = (
    "This image is one page of a UAE Ministry of Education Arabic-language school textbook. "
    "Transcribe every piece of Arabic text on the page exactly as printed, in reading order "
    "(right to left, top to bottom), keeping the diacritics (tashkeel) where they are printed. "
    "Put each paragraph, heading, list item or exercise line on its own line. "
    "Do not translate, explain, summarise or add anything. Do not describe pictures. "
    "If the page has no text, reply with nothing."
)


def short_word_share(text: str) -> float:
    """Share of the Arabic words in the text that have only one or two letters."""
    words = [len(_LETTER.findall(word)) for word in (text or "").split()]
    words = [letters for letters in words if letters]
    return sum(1 for letters in words if letters <= 2) / len(words) if words else 0.0


def is_fragmented(text: str) -> bool:
    """Text broken into isolated letters and diacritics instead of whole words."""
    words = sum(1 for word in (text or "").split() if _LETTER.search(word))
    return words >= MIN_WORDS_TO_JUDGE and short_word_share(text) > MAX_SHORT_WORD_SHARE


def readable_scan(page) -> bool:
    """A stored page whose text can be shown to learners (not split into letters or flagged so)."""
    return bool(page is not None and page.ocr_text_ar and page.review_status != FRAGMENTED_STATUS
                and not is_fragmented(page.ocr_text_ar))


def has_usable_text(text: str) -> bool:
    return len(_ARABIC.findall(text or "")) >= MIN_ARABIC_CHARS and not is_fragmented(text)


def transcribe_page_image(png_bytes: bytes, *, page_label: str = "") -> Optional[str]:
    """Arabic text of a page image, or None when the AI fails on this page.

    Raises AIUnavailable (GeminiQuotaExhausted when out of credits or quota) when no AI provider
    can answer, so the caller pauses the book instead of failing every remaining page.
    """
    from backend.ai import gateway
    from backend.modules.tutoring.assistant import _record_gemini_failure

    if not png_bytes or not gateway.available():
        return None
    try:
        response = gateway.generate(gateway.AIRequest(
            feature="textbook_reading", prompt=_PROMPT, attachments=[(png_bytes, "image/png")],
            temperature=0.0, child_safe=False, tier="strong", retry_on_rate_limit=True,
        ))
        text = (response.text or "").strip()
        # Drop a Markdown code fence if the model wrapped its answer in one.
        text = re.sub(r"^```[a-z]*\s*|\s*```$", "", text).strip()
        return text or None
    except AIUnavailable:
        # Every further page would fail the same way: the caller pauses the book instead.
        # (The gateway has already recorded each provider's failure.)
        raise
    except Exception as exc:
        logger.warning("Gemini page OCR failed for %s: %s", page_label or "page", exc)
        _record_gemini_failure(f"Textbook OCR {page_label}".strip(), exc)
        return None
