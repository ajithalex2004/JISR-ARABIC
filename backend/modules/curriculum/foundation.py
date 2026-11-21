"""Basic Foundation of Arabic: textbook links and explanations in a parent's language.

Textbook links: each Foundation lesson lists the chapters of a class that teach the same rule,
found by matching the lesson's keywords (foundation_data.TEXTBOOK_KEYWORDS) against each published
chapter's grammar rules and title.

Parent languages: a lesson's English explanation translated into Hindi, Malayalam or Urdu by the AI,
once per lesson and language, and saved (FoundationTranslation). Arabic words stay in Arabic.
"""
import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.foundation_data import TEXTBOOK_KEYWORDS, all_lessons, get_lesson
from backend.models import FoundationTranslation, Lesson, LessonVersion

logger = logging.getLogger("fahim.foundation")

PARENT_LANGUAGES = {
    "hi": {"name": "Hindi", "native": "हिन्दी", "dir": "ltr"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "dir": "ltr"},
    "ur": {"name": "Urdu", "native": "اردو", "dir": "rtl"},
}
LINKS_PER_LESSON = 6
_TASHKEEL = re.compile("[ً-ْٰـ]")


def _plain(text: str) -> str:
    return _TASHKEEL.sub("", (text or "").lower()).replace("’", "'").replace("`", "'")


# ---------------------------------------------------------------------------------------------
# Textbook links
# ---------------------------------------------------------------------------------------------

def _chapter_topics(content: Dict[str, Any]) -> List[str]:
    lab = (content or {}).get("grammar_lab") or {}
    topics = [lab.get("title_en", ""), lab.get("title_ar", "")]
    for sec in lab.get("sections") or []:
        if isinstance(sec, dict):
            topics += [sec.get("rule_name_en", ""), sec.get("rule_name_ar", "")]
    return [t for t in topics if t]


def textbook_links(db: Session, grade: int) -> Dict[str, List[Dict[str, Any]]]:
    """For each Foundation lesson, the published chapters of this class that teach its rule."""
    from backend.redis_client import cache_get, cache_set
    cache_key = f"foundation:links:{grade}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    lessons = (db.query(Lesson).filter(Lesson.grade == grade).order_by(Lesson.term, Lesson.lesson_order).all())
    chapters = []
    for lesson in lessons:
        version = (db.query(LessonVersion)
                   .filter(LessonVersion.lesson_id == lesson.id, LessonVersion.is_active.is_(True),
                           LessonVersion.status == "published").first())
        if version is None:
            continue
        try:
            content = json.loads(version.content_json)
        except (TypeError, ValueError):
            continue
        rules = _chapter_topics(content)
        chapters.append({"lesson": lesson, "rules": rules,
                         "haystack": _plain(" | ".join(rules + [lesson.title_en or "", lesson.title_ar or ""]))})
    links: Dict[str, List[Dict[str, Any]]] = {}
    for foundation_lesson in all_lessons():
        keywords = [_plain(k) for k in TEXTBOOK_KEYWORDS.get(foundation_lesson["id"], [])]
        found = []
        for chapter in chapters:
            hit = next((k for k in keywords if k and k in chapter["haystack"]), None)
            if not hit:
                continue
            # The rule that matched, to show why the chapter is linked.
            rule = next((r for r in chapter["rules"] if hit in _plain(r)), "")
            lesson = chapter["lesson"]
            found.append({"lesson_id": lesson.id, "grade": lesson.grade, "term": lesson.term,
                          "lesson_order": lesson.lesson_order, "title_ar": lesson.title_ar, "title_en": lesson.title_en,
                          "rule": rule})
            if len(found) >= LINKS_PER_LESSON:
                break
        if found:
            links[foundation_lesson["id"]] = found
    cache_set(cache_key, links, ttl_seconds=3600)
    return links


# ---------------------------------------------------------------------------------------------
# Explanations in a parent's language
# ---------------------------------------------------------------------------------------------

def _source(lesson: Dict[str, Any]) -> Dict[str, Any]:
    """The English parts a parent needs: the summary, the rule points and what each example means."""
    return {"summary": lesson["summary_en"], "points": lesson["points"],
            "examples": [{"ar": e["ar"], "en": e["en"]} for e in lesson["examples"]]}


def _hash(source: Dict[str, Any], lang: str) -> str:
    return hashlib.sha256(json.dumps([lang, source], ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _prompt(lesson: Dict[str, Any], source: Dict[str, Any], lang: str) -> str:
    language = PARENT_LANGUAGES[lang]["name"]
    return f"""Translate this beginner Arabic-grammar lesson for a parent who reads {language} but no Arabic,
so they can help their child. Lesson: "{lesson['title_en']}".

Rules:
- Translate the English into simple, natural {language}.
- Keep every Arabic word, letter and mark exactly as written (do not translate or transliterate it).
- Keep Latin transliterations in brackets, e.g. (haadhaa), as they are.
- Return JSON only: {{"title": "...", "summary": "...", "points": ["..."], "examples": ["..."]}},
  with exactly {len(source['points'])} points and {len(source['examples'])} examples, in the same order.
  Each example is the translation of that example's English meaning.

Lesson (JSON):
{json.dumps({"title": lesson["title_en"], **source}, ensure_ascii=False)}"""


def _check(result: Any, source: Dict[str, Any]) -> Optional[str]:
    if not isinstance(result, dict):
        return "not a JSON object"
    if not isinstance(result.get("summary"), str) or not result["summary"].strip():
        return "missing summary"
    if not isinstance(result.get("points"), list) or len(result["points"]) != len(source["points"]):
        return f"expected {len(source['points'])} points"
    if not isinstance(result.get("examples"), list) or len(result["examples"]) != len(source["examples"]):
        return f"expected {len(source['examples'])} examples"
    return None


def ai_translator():
    from backend.ai import gateway
    from backend.modules.curriculum.drafting import parse_model_json
    from backend.modules.tutoring.assistant import _get_gemini_client
    client = _get_gemini_client()
    if not gateway.available(gemini_client=client):
        raise ApplicationError(503, "Translations are unavailable: no AI provider is configured")

    def translate(prompt: str):
        response = gateway.generate(gateway.AIRequest(
            feature="foundation_translation", prompt=prompt, json=True, temperature=0.2, max_tokens=4096,
            child_safe=False, timeout=120), gemini_client=client)
        translate.model = response.model  # type: ignore[attr-defined]
        return parse_model_json(response.text or "")

    translate.model = None  # type: ignore[attr-defined]
    return translate


def parent_explanation(db: Session, lesson_id: str, lang: str, translator=None) -> Dict[str, Any]:
    """The lesson explained in the parent's language: saved after the first request."""
    if lang not in PARENT_LANGUAGES:
        raise ApplicationError(400, f"Language must be one of: {', '.join(PARENT_LANGUAGES)}")
    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise ApplicationError(404, "Lesson not found")
    source = _source(lesson)
    source_hash = _hash(source, lang)
    row = (db.query(FoundationTranslation)
           .filter(FoundationTranslation.lesson_id == lesson_id, FoundationTranslation.lang == lang,
                   FoundationTranslation.source_hash == source_hash).first())
    if row is None:
        translator = translator or ai_translator()
        prompt, problem, result = _prompt(lesson, source, lang), None, None
        for _ in range(2):
            try:
                result = translator(prompt)
            except ValueError as exc:
                problem = f"unreadable reply ({exc})"
                continue
            problem = _check(result, source)
            if not problem:
                break
        if problem:
            logger.warning("Foundation translation %s/%s failed: %s", lesson_id, lang, problem)
            raise ApplicationError(502, "The translation could not be made right now. Please try again later.")
        content = {"title": str(result.get("title") or "").strip(), "summary": result["summary"].strip(),
                   "points": [str(p).strip() for p in result["points"]],
                   "examples": [str(e).strip() for e in result["examples"]]}
        row = FoundationTranslation(lesson_id=lesson_id, lang=lang, source_hash=source_hash,
                                    content_json=json.dumps(content, ensure_ascii=False),
                                    model=getattr(translator, "model", None))
        db.add(row)
        try:
            db.commit()
        except Exception:  # another request saved the same translation first
            db.rollback()
            row = (db.query(FoundationTranslation)
                   .filter(FoundationTranslation.lesson_id == lesson_id, FoundationTranslation.lang == lang,
                           FoundationTranslation.source_hash == source_hash).first())
    content = json.loads(row.content_json)
    meta = PARENT_LANGUAGES[lang]
    return {"lesson_id": lesson_id, "lang": lang, "language": meta["name"], "native_name": meta["native"],
            "dir": meta["dir"], "machine_translated": True, **content,
            "example_arabic": [e["ar"] for e in lesson["examples"]]}
