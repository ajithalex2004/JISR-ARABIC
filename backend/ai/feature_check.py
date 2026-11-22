"""Daily AI feature check: run each AI feature's own code on a known question and check the answer.

The 20-minute Gemini check (scheduler.run_scheduled_gemini_probe) only asks Gemini to reply. It
can't see a problem in our side of a feature: a reply in a shape the code doesn't expect, a prompt
that stopped working after a model change, a parsing bug. This check calls the same functions
learners use (word meanings, Ask Fahim, Learn with Fahim, parent-language explanations) with fixed
inputs whose right answer is known (كِتَابٌ means "book"), so such a problem shows up here, once a
day before school, instead of in front of a student.

Nothing is saved or cached, and no learner's daily AI allowance is used.
"""
import datetime
import logging
import re
import time
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("fahim.ai_check")

CACHE_KEY = "scheduler:last:ai_feature_check"


class CheckFailed(Exception):
    """The feature answered, but not with what a learner should see."""


def _has(text: Optional[str], *words: str) -> bool:
    text = (text or "").lower()
    return any(re.search(rf"\b{w}", text) for w in words)


def check_word_meaning() -> str:
    from backend.modules.curriculum.glossary import _gemini_gloss
    result = _gemini_gloss("كِتَابٌ", "هَذَا كِتَابٌ جَمِيلٌ")
    if not result:
        raise CheckFailed("No meaning came back for كِتَابٌ")
    if not _has(result.get("translation"), "book"):
        raise CheckFailed(f"كِتَابٌ was given as {result.get('translation')!r}, expected 'book'")
    return f"كِتَابٌ → {result['translation']}"


def check_sentence_meanings() -> str:
    from backend.modules.curriculum.glossary import _gemini_gloss_many
    words = ["الطَّالِبُ", "كِتَابًا"]
    found = _gemini_gloss_many(words, "قَرَأَ الطَّالِبُ كِتَابًا")
    missing = [w for w in words if w not in found]
    if missing:
        raise CheckFailed(f"No meaning came back for {', '.join(missing)}")
    if not _has(found[words[0]]["translation"], "student", "pupil", "learner"):
        raise CheckFailed(f"الطَّالِبُ was given as {found[words[0]]['translation']!r}, expected 'student'")
    if not _has(found[words[1]]["translation"], "book"):
        raise CheckFailed(f"كِتَابًا was given as {found[words[1]]['translation']!r}, expected 'book'")
    return f"الطَّالِبُ → {found[words[0]]['translation']} · كِتَابًا → {found[words[1]]['translation']}"


def check_ask_fahim() -> str:
    from backend.database import SessionLocal
    from backend.modules.tutoring.assistant import _ask_fahim_gemini, _get_gemini_client
    from backend.schemas import AskFahimRequest
    db = SessionLocal()
    try:
        answer = _ask_fahim_gemini(AskFahimRequest(question="What does the Arabic word كِتَاب mean?", grade=5),
                                   _get_gemini_client(), db=db)
    finally:
        db.close()
    if not answer:
        raise CheckFailed("Ask Fahim gave no answer")
    if not (answer.get("answer_ar") or "").strip() or not (answer.get("answer_en") or "").strip():
        raise CheckFailed("Ask Fahim's answer is missing its Arabic or English part")
    if not _has(answer["answer_en"], "book"):
        raise CheckFailed(f"Ask Fahim's answer doesn't say 'book': {answer['answer_en'][:120]!r}")
    return "Answered in Arabic and English"


def check_learn_with_fahim() -> str:
    from backend.modules.tutoring.assistant import _get_gemini_client, _socratic_learn_gemini
    from backend.schemas import SocraticLearnRequest
    reply = _socratic_learn_gemini(SocraticLearnRequest(topic="The definite article ال", grade=5,
                                                        student_input="I think ال means 'the'."), _get_gemini_client())
    if not reply:
        raise CheckFailed("Learn with Fahim gave no reply")
    if not reply.response_ar.strip():
        raise CheckFailed("Learn with Fahim's reply has no Arabic")
    return "Replied"


def check_parent_translation() -> str:
    from backend.foundation_data import all_lessons
    from backend.modules.curriculum.foundation import _check, _prompt, _source, ai_translator
    lesson = next(iter(all_lessons()))
    source = _source(lesson)
    result = ai_translator()(_prompt(lesson, source, "hi"))
    problem = _check(result, source, "hi")
    if problem:
        raise CheckFailed(f"Hindi explanation of “{lesson['title_en']}”: {problem}")
    return f"Hindi explanation of “{lesson['title_en']}”"


CHECKS: List[Dict] = [
    {"key": "word_meaning", "label": "Word meaning (tap a word)", "run": check_word_meaning},
    {"key": "sentence_meanings", "label": "Word meanings for a sentence", "run": check_sentence_meanings},
    {"key": "ask_fahim", "label": "Ask Fahim", "run": check_ask_fahim},
    {"key": "learn_with_fahim", "label": "Learn with Fahim", "run": check_learn_with_fahim},
    {"key": "parent_translation", "label": "Foundation: explanation in a parent's language", "run": check_parent_translation},
]


def _gemini_error_since(started_at: str) -> Optional[str]:
    """The error a feature recorded while it ran (features swallow their errors and record them)."""
    from backend.alerts import recent_failures
    for event in recent_failures("gemini"):
        if event.get("at", "") >= started_at:
            return event.get("detail")
    return None


def _run_one(check: Dict) -> Dict:
    started_at = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
    started = time.perf_counter()
    entry = {"key": check["key"], "label": check["label"], "ok": False, "detail": ""}
    try:
        entry["detail"] = check["run"]()
        entry["ok"] = True
    except CheckFailed as exc:
        entry["detail"] = str(exc)
        cause = _gemini_error_since(started_at)
        if cause:
            entry["detail"] += f" (error: {cause})"
    except Exception as exc:
        entry["detail"] = f"{type(exc).__name__}: {exc}"
    entry["detail"] = " ".join(str(entry["detail"]).split())[:400]
    entry["ms"] = round((time.perf_counter() - started) * 1000)
    return entry


def run_feature_check(checks: Optional[List[Dict]] = None, *, alert: bool = True) -> Dict:
    """Run every check; save the result for System health and alert admins if any failed."""
    from backend import alerts
    from backend.ai import gateway
    from backend.redis_client import cache_set

    at = datetime.datetime.now(datetime.UTC).isoformat()
    if not gateway.available():
        result = {"at": at, "ok": False, "skipped": True, "checks": [],
                  "summary": "Not run: no AI provider is configured (GEMINI_API_KEY)."}
        cache_set(CACHE_KEY, result, ttl_seconds=8 * 86400)
        return result
    results = [_run_one(c) for c in (checks or CHECKS)]
    failed = [r for r in results if not r["ok"]]
    result = {"at": at, "ok": not failed, "skipped": False, "checks": results,
              "summary": (f"All {len(results)} AI features answered correctly." if not failed
                          else f"{len(failed)} of {len(results)} AI features failed: {', '.join(r['label'] for r in failed)}.")}
    cache_set(CACHE_KEY, result, ttl_seconds=8 * 86400)
    logger.info("AI feature check", extra={"event": "ai_feature_check", "error": result["summary"]})
    if failed and alert:
        alerts.alert_now("gemini", f"The daily AI feature check found a problem. {result['summary']} "
                                   "Learners may get no answer or a wrong one from these features.",
                         "; ".join(f"{r['label']}: {r['detail']}" for r in failed))
    return result
