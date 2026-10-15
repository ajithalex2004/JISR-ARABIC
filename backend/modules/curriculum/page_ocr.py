"""Read the Arabic text off a scanned textbook page image with Gemini vision.

Ministry textbook PDFs are scans: their pages are pictures with no text layer, so text
extraction from the PDF itself returns nothing. Each page is rendered to PNG and, when the
PDF has no usable text, Gemini transcribes the picture. Results still go through the
existing teacher review before reaching learners.
"""
import logging
import re
from typing import Optional

from backend.gemini_quota import GeminiQuotaExhausted, call_with_quota_retry

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
    """Arabic text of a page image, or None when Gemini is unavailable or fails.

    Raises GeminiQuotaExhausted when Gemini is out of credits or quota.
    """
    from backend.modules.tutoring.assistant import GEMINI_MODEL, _get_gemini_client, _record_gemini_failure

    client = _get_gemini_client()
    if client is None or not png_bytes:
        return None
    try:
        from google.genai import types

        response = call_with_quota_retry(lambda: client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[types.Part.from_bytes(data=png_bytes, mime_type="image/png"), _PROMPT],
            config=types.GenerateContentConfig(temperature=0.0),
        ), label=f"Textbook OCR {page_label}".strip())
        text = (response.text or "").strip()
        # Drop a Markdown code fence if the model wrapped its answer in one.
        text = re.sub(r"^```[a-z]*\s*|\s*```$", "", text).strip()
        return text or None
    except GeminiQuotaExhausted as exc:
        # Every further page would fail the same way: the caller pauses the book instead.
        _record_gemini_failure(f"Textbook OCR {page_label}".strip(), exc)
        raise
    except Exception as exc:
        logger.warning("Gemini page OCR failed for %s: %s", page_label or "page", exc)
        _record_gemini_failure(f"Textbook OCR {page_label}".strip(), exc)
        return None
