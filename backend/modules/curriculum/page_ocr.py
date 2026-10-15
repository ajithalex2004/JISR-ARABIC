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

_PROMPT = (
    "This image is one page of a UAE Ministry of Education Arabic-language school textbook. "
    "Transcribe every piece of Arabic text on the page exactly as printed, in reading order "
    "(right to left, top to bottom), keeping the diacritics (tashkeel) where they are printed. "
    "Put each paragraph, heading, list item or exercise line on its own line. "
    "Do not translate, explain, summarise or add anything. Do not describe pictures. "
    "If the page has no text, reply with nothing."
)


def has_usable_text(text: str) -> bool:
    return len(_ARABIC.findall(text or "")) >= MIN_ARABIC_CHARS


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
