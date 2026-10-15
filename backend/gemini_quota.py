"""Recognise Gemini "out of quota / out of credits" errors so long jobs pause instead of failing.

When the Gemini key runs out of prepaid credits (402) or hits its quota (429), every further
call fails the same way. Textbook OCR and lesson drafting would otherwise mark each remaining
page or lesson as failed; instead they stop, keep what was done, and tell the admin what to fix.
A short per-minute rate limit is retried after a wait before giving up.
"""
import logging
import time
from typing import Callable, Sequence, TypeVar

from backend.ai.errors import AIUnavailable

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Waits (seconds) before retrying a rate-limited call; credits running out is never retried.
QUOTA_RETRY_DELAYS: Sequence[int] = (30, 60)
_sleep = time.sleep


class GeminiQuotaExhausted(AIUnavailable):
    """AI refuses calls until billing or quota is fixed; the message says what to do."""


def _code(exc: BaseException):
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    return None


def is_credits_exhausted(exc: BaseException) -> bool:
    text = str(exc).lower()
    return _code(exc) == 402 or "credits are depleted" in text or "prepayment" in text


def is_quota_error(exc: BaseException) -> bool:
    if isinstance(exc, GeminiQuotaExhausted):
        return True
    text = str(exc)
    return (_code(exc) in (402, 429) or "RESOURCE_EXHAUSTED" in text
            or text.lstrip().startswith(("402", "429")) or is_credits_exhausted(exc))


def pause_message(exc: BaseException) -> str:
    if isinstance(exc, GeminiQuotaExhausted):
        return str(exc)
    if is_credits_exhausted(exc):
        return ("Gemini's prepaid credits are used up. Add credits in Google AI Studio "
                "(ai.studio/projects > Billing), then run this again: finished work is kept.")
    return ("Gemini's usage quota is used up for now. Wait for it to reset or raise the limit / "
            "enable billing in Google AI Studio, then run this again: finished work is kept.")


def call_with_quota_retry(call: Callable[[], T], *, label: str = "Gemini call",
                          delays: Sequence[int] = None) -> T:
    """Run ``call``; on a rate limit wait and retry, and raise GeminiQuotaExhausted if it persists."""
    delays = QUOTA_RETRY_DELAYS if delays is None else delays
    for attempt in range(len(delays) + 1):
        try:
            return call()
        except Exception as exc:
            if not is_quota_error(exc):
                raise
            if is_credits_exhausted(exc) or attempt >= len(delays):
                raise GeminiQuotaExhausted(pause_message(exc)) from exc
            logger.warning("%s rate-limited, retrying in %ss: %s", label, delays[attempt], exc)
            _sleep(delays[attempt])
    raise AssertionError("unreachable")
