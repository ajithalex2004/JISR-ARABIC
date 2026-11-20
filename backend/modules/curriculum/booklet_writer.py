"""Write full-depth Smart Study Booklets with AI, from each chapter's published lesson.

Only three chapters have a hand-written booklet (backend/malazim_bank.py); every other chapter
showed a thin booklet generated from its title. This module asks the AI to write a booklet in the
same format and depth as the Grade 5 Chapter 1 booklet, using only the facts in that chapter's
published lesson (its vocabulary, passages, grammar and exercises). Each booklet is checked
(structure, three-option exercises, tashkeel) and stored as a draft; learners see it only once an
admin publishes it.
"""
import datetime
import json
import logging
import os
import random
import re
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import BookletDraft, Lesson, LessonVersion

logger = logging.getLogger("fahim.booklets")

EXAMPLE_LESSON_ID = "lesson_01_ball_games"
ATTEMPTS = 3
MAX_SOURCE_CHARS = 40000
# Arabic words written without vowel marks show no Arab-English line, so allow only a few.
MAX_UNVOWELLED_SHARE = 0.03

# Parts of a lesson package that say nothing about the chapter's content.
_NOISE_KEYS = {"prep_check", "learning_paths", "instruction_decoder", "parent_companion", "tutor_handover",
               "speaking_mission", "spaced_recall", "provenance", "audio_url", "audio", "image", "image_url",
               "pdf_start_page", "version", "rubric_categories"}

_WORD = re.compile(r"[ء-ي][ء-يً-ْٰـ]*")
_VOWELLED = re.compile(r"[ً-ْ]")
_EXEMPT_WORDS = {"م", "سم", "كم", "كجم", "ة", "ه", "ـة", "ـه"}


# ---------------------------------------------------------------------------------------------
# Source: the chapter's published lesson
# ---------------------------------------------------------------------------------------------

def published_version(db: Session, lesson_id: str) -> Optional[LessonVersion]:
    return (db.query(LessonVersion)
            .filter(LessonVersion.lesson_id == lesson_id, LessonVersion.is_active.is_(True),
                    LessonVersion.status == "published")
            .order_by(LessonVersion.created_at.desc()).first())


def _strip_noise(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _strip_noise(v) for k, v in value.items() if k not in _NOISE_KEYS and v not in (None, "", [], {})}
    if isinstance(value, list):
        return [_strip_noise(v) for v in value]
    return value


def chapter_source(version: LessonVersion) -> str:
    """The lesson's content as compact JSON, without the parts that don't describe the chapter."""
    try:
        content = json.loads(version.content_json)
    except (TypeError, ValueError):
        return ""
    text = json.dumps(_strip_noise(content), ensure_ascii=False, separators=(",", ":"))
    return text[:MAX_SOURCE_CHARS]


# ---------------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------------

def learner_arabic(booklet: Dict[str, Any]):
    """Every Arabic text a learner reads in the booklet."""
    for sec in booklet.get("study_mode", {}).get("sections", []):
        ex = sec.get("inline_exercise", {})
        yield from (sec.get("title_ar", ""), sec.get("content_ar", ""), *sec.get("key_takeaways_ar", []),
                    ex.get("question_ar", ""), *ex.get("options", []), ex.get("explanation_ar", ""))
    quick = booklet.get("quick_review_mode", {})
    yield from (r.get("rule_ar", "") for r in quick.get("bullet_rules", []))
    for card in quick.get("vocabulary_flashcards", []):
        yield from (card.get("word_ar", ""), card.get("meaning_ar", ""), card.get("opposite_ar", ""))
    for formula in quick.get("grammar_formulas", []):
        yield from (formula.get("title_ar", ""), formula.get("formula_ar", ""), formula.get("example_ar", ""))
    yield from (w.get("warning_ar", "") for w in quick.get("exam_pitfall_warnings", []))


def unvowelled_words(booklet: Dict[str, Any]) -> List[str]:
    return [w for text in learner_arabic(booklet) for w in _WORD.findall(text or "")
            if w not in _EXEMPT_WORDS and not _VOWELLED.search(w)]


def _arabic_word_count(booklet: Dict[str, Any]) -> int:
    return sum(len(_WORD.findall(text or "")) for text in learner_arabic(booklet))


def _need_text(obj: Dict[str, Any], keys, where: str, errors: List[str]) -> None:
    for key in keys:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            errors.append(f"{where}.{key} is missing or empty")


def booklet_errors(booklet: Any) -> List[str]:
    """What's wrong with a written booklet; an empty list means it can be stored."""
    if not isinstance(booklet, dict):
        return ["the reply is not a JSON object"]
    errors: List[str] = []
    _need_text(booklet, ("title_ar", "title_en"), "booklet", errors)
    sections = booklet.get("study_mode", {}).get("sections") if isinstance(booklet.get("study_mode"), dict) else None
    if not isinstance(sections, list) or len(sections) < 4:
        errors.append("study_mode.sections needs at least 4 sections")
        sections = sections if isinstance(sections, list) else []
    for i, sec in enumerate(sections, 1):
        where = f"study_mode.sections[{i}]"
        if not isinstance(sec, dict):
            errors.append(f"{where} is not an object")
            continue
        _need_text(sec, ("title_ar", "title_en", "content_ar", "content_en"), where, errors)
        ar, en = sec.get("key_takeaways_ar"), sec.get("key_takeaways_en")
        if not isinstance(ar, list) or len(ar) < 2 or not isinstance(en, list) or len(en) != len(ar):
            errors.append(f"{where}: key_takeaways_ar needs 2+ items and key_takeaways_en the same number")
        ex = sec.get("inline_exercise")
        if not isinstance(ex, dict):
            errors.append(f"{where}.inline_exercise is missing")
            continue
        _need_text(ex, ("question_ar", "question_en", "explanation_ar", "explanation_en"), f"{where}.inline_exercise", errors)
        opts, opts_en = ex.get("options"), ex.get("options_en")
        if not isinstance(opts, list) or len(opts) != 3 or not isinstance(opts_en, list) or len(opts_en) != 3:
            errors.append(f"{where}.inline_exercise needs exactly 3 options and 3 options_en")
        elif len({o.strip() for o in opts if isinstance(o, str)}) != 3:
            errors.append(f"{where}.inline_exercise options must be 3 different texts")
        if ex.get("correct_index") not in (0, 1, 2):
            errors.append(f"{where}.inline_exercise.correct_index must be 0, 1 or 2")
    quick = booklet.get("quick_review_mode")
    if not isinstance(quick, dict):
        return errors + ["quick_review_mode is missing"]
    minimums = (("bullet_rules", 5, ("rule_ar", "rule_en")),
                ("vocabulary_flashcards", 4, ("word_ar", "word_en", "meaning_ar", "meaning_en")),
                ("grammar_formulas", 2, ("title_ar", "title_en", "formula_ar", "formula_en", "example_ar", "example_en")),
                ("exam_pitfall_warnings", 3, ("warning_ar", "warning_en")))
    for key, minimum, fields in minimums:
        items = quick.get(key)
        if not isinstance(items, list) or len(items) < minimum:
            errors.append(f"quick_review_mode.{key} needs at least {minimum} items")
            continue
        for i, item in enumerate(items, 1):
            if not isinstance(item, dict):
                errors.append(f"quick_review_mode.{key}[{i}] is not an object")
            else:
                _need_text(item, fields, f"quick_review_mode.{key}[{i}]", errors)
    if not errors:
        missing = unvowelled_words(booklet)
        total = max(_arabic_word_count(booklet), 1)
        if len(missing) / total > MAX_UNVOWELLED_SHARE:
            sample = " ".join(sorted(set(missing))[:25])
            errors.append(f"{len(missing)} of {total} Arabic words have no tashkeel (every word needs full "
                          f"vowel marks), e.g.: {sample}")
    return errors


# ---------------------------------------------------------------------------------------------
# Shaping the AI's reply into a stored booklet
# ---------------------------------------------------------------------------------------------

def _shuffle_options(booklet: Dict[str, Any], seed: str) -> None:
    """Move each correct answer to a random position: models put most of them in the same place."""
    rng = random.Random(seed)
    for sec in booklet["study_mode"]["sections"]:
        ex = sec["inline_exercise"]
        order = [0, 1, 2]
        rng.shuffle(order)
        ex["options"] = [ex["options"][i] for i in order]
        ex["options_en"] = [ex["options_en"][i] for i in order]
        ex["correct_index"] = order.index(ex["correct_index"])


def finish_booklet(raw: Dict[str, Any], lesson: Lesson) -> Dict[str, Any]:
    """Fill the fixed fields (ids, grade, titles of the modes) and keep only the booklet's own keys."""
    sections = []
    for i, sec in enumerate(raw["study_mode"]["sections"], 1):
        ex = sec["inline_exercise"]
        sections.append({
            "section_id": f"sec_{i:02d}",
            "title_ar": sec["title_ar"].strip(), "title_en": sec["title_en"].strip(),
            "content_ar": sec["content_ar"].strip(), "content_en": sec["content_en"].strip(),
            "key_takeaways_ar": [t.strip() for t in sec["key_takeaways_ar"]],
            "key_takeaways_en": [t.strip() for t in sec["key_takeaways_en"]],
            "inline_exercise": {
                "question_ar": ex["question_ar"].strip(), "question_en": ex["question_en"].strip(),
                "options": [o.strip() for o in ex["options"]], "options_en": [o.strip() for o in ex["options_en"]],
                "correct_index": int(ex["correct_index"]),
                "explanation_ar": ex["explanation_ar"].strip(), "explanation_en": ex["explanation_en"].strip(),
            },
        })
    quick = raw["quick_review_mode"]

    def keep(items, fields):
        return [{f: str(item.get(f, "")).strip() for f in fields if item.get(f)} for item in items]

    start_page = lesson.start_page
    booklet = {
        "lesson_id": lesson.id,
        "title_ar": raw["title_ar"].strip(),
        "title_en": raw["title_en"].strip(),
        "grade": lesson.grade,
        "term": lesson.term,
        "pages_reference": f"From page {start_page} (CBSE Curriculum Student Book Grade {lesson.grade})" if start_page else f"Grade {lesson.grade} Term {lesson.term}",
        "curriculum_alignment": "UAE Ministry of Education & CBSE Arabic (Non-Arabs)",
        "study_mode": {
            "mode_title_ar": "وَضْعُ المُذَاكَرَةِ التَّفَاعُلِيَّةِ الشَّامِلَةِ",
            "mode_title_en": "Comprehensive Interactive Study Mode",
            "estimated_minutes": 25,
            "sections": sections,
        },
        "quick_review_mode": {
            "mode_title_ar": "وَضْعُ المُلَاحَظَاتِ وَالمُرَاجَعَةِ السَّرِيعَةِ (15 دَقِيقَةً)",
            "mode_title_en": "15-Minute Fast Revision & Cheat-Sheet Mode",
            "target_review_time": "15 minutes",
            "bullet_rules": keep(quick["bullet_rules"], ("rule_ar", "rule_en")),
            "vocabulary_flashcards": keep(quick["vocabulary_flashcards"],
                                          ("word_ar", "word_en", "meaning_ar", "meaning_en", "opposite_ar", "opposite_en")),
            "grammar_formulas": keep(quick["grammar_formulas"],
                                     ("title_ar", "title_en", "formula_ar", "formula_en", "example_ar", "example_en")),
            "exam_pitfall_warnings": keep(quick["exam_pitfall_warnings"], ("warning_ar", "warning_en")),
        },
        "source": "ai",
    }
    _shuffle_options(booklet, lesson.id)
    return booklet


# ---------------------------------------------------------------------------------------------
# The AI call
# ---------------------------------------------------------------------------------------------

def _example_booklet() -> str:
    from backend.malazim_bank import MALAZIM_DATA
    # The example keeps its answers: the model must write correct_index and explanations too.
    return json.dumps(MALAZIM_DATA[EXAMPLE_LESSON_ID], ensure_ascii=False, indent=1)


def build_prompt(lesson: Lesson, source: str, problems: Optional[List[str]] = None) -> str:
    level = ("young beginners: short, simple sentences" if lesson.grade <= 4 else
             "upper-primary learners: clear sentences, a little more detail" if lesson.grade <= 6 else
             "middle-school learners: fuller explanations and grammar analysis (إعراب) where the lesson has it")
    prompt = f"""You write a Smart Study Booklet (مَلْزَمَة) for one chapter of the CBSE Arabic textbook for
non-native speakers in UAE schools.

Chapter: Grade {lesson.grade}, Term {lesson.term}, chapter {lesson.lesson_order}: {lesson.title_ar} ({lesson.title_en}).
Write for {level}.

THE CHAPTER'S PUBLISHED LESSON (the only source of facts; JSON):
{source}

THE FORMAT AND DEPTH TO MATCH (the Grade 5 Chapter 1 booklet, written by a teacher):
{_example_booklet()}

Write this chapter's booklet as ONE JSON object with exactly the example's structure:
- "title_ar", "title_en": the booklet title, like the example's.
- "study_mode": {{"sections": [...]}} with 4 to 6 sections that together cover the whole chapter: its
  reading passage(s) and main ideas, its key vocabulary, and its grammar rule(s). Each section has
  "title_ar", "title_en", "content_ar" (3 to 5 full sentences), "content_en" (its translation),
  "key_takeaways_ar" and "key_takeaways_en" (2 to 4 matching items), and "inline_exercise" with
  "question_ar", "question_en", "options" (3 Arabic options), "options_en" (their translations, same
  order), "correct_index" (0, 1 or 2), "explanation_ar" and "explanation_en".
- "quick_review_mode" with "bullet_rules" (5 to 7 items: "rule_ar", "rule_en"), "vocabulary_flashcards"
  (5 to 8 of the chapter's own words: "word_ar", "word_en", "meaning_ar", "meaning_en", "opposite_ar",
  "opposite_en"), "grammar_formulas" (2 to 3: "title_ar", "title_en", "formula_ar", "formula_en",
  "example_ar", "example_en") and "exam_pitfall_warnings" (3 to 4: "warning_ar", "warning_en").

Rules:
- Use only facts, words, names, numbers and grammar found in the chapter's lesson above. Never take
  facts from the example booklet (it is a different chapter) and never invent details.
- Write every Arabic word with FULL tashkeel (every letter vowelled, as in the example), including
  options, takeaways and flashcards. Numbers may be digits.
- Every English text is a faithful translation of its Arabic text.
- Exercises test the chapter's content; exactly one option is correct and the other two are plausible
  but clearly wrong.
- Reply with the JSON object only."""
    if problems:
        prompt += "\n\nYour previous reply had these problems; fix all of them:\n- " + "\n- ".join(problems[:20])
    return prompt


def ai_writer() -> Callable[[str], Dict[str, Any]]:
    """Default writer: sends the prompt through the AI gateway and returns the parsed JSON."""
    from backend.ai import gateway
    from backend.ai.errors import ModelNotFound
    from backend.modules.curriculum.drafting import parse_model_json
    from backend.modules.tutoring.assistant import _get_gemini_client

    client = _get_gemini_client()
    if not gateway.available(gemini_client=client):
        raise ApplicationError(503, "No AI provider is configured (GEMINI_API_KEY or ANTHROPIC_API_KEY)")
    model = [os.getenv("FAHIM_BOOKLET_MODEL") or os.getenv("FAHIM_DRAFT_MODEL") or None]

    def write(prompt: str) -> Dict[str, Any]:
        request = dict(feature="booklet_writing", prompt=prompt, json=True, temperature=0.4, max_tokens=16384,
                       tier="strong", child_safe=False, retry_on_rate_limit=True, timeout=300)
        try:
            response = gateway.generate(gateway.AIRequest(gemini_model=model[0], **request), gemini_client=client)
        except ModelNotFound:
            model[0] = None  # a wrong model name in the setting: use the default model
            response = gateway.generate(gateway.AIRequest(**request), gemini_client=client)
        write.model = response.model  # type: ignore[attr-defined]
        write.cost = (write.cost or 0) + (response.cost_usd or 0)  # type: ignore[attr-defined]
        return parse_model_json(response.text or "")

    write.model = None  # type: ignore[attr-defined]
    write.cost = 0.0  # type: ignore[attr-defined]
    return write


# ---------------------------------------------------------------------------------------------
# Writing, storing and publishing
# ---------------------------------------------------------------------------------------------

def hand_written_ids() -> set:
    from backend.malazim_bank import MALAZIM_DATA
    return {key for key, value in MALAZIM_DATA.items() if key.startswith("lesson_") and value.get("lesson_id") == key}


def write_booklet(db: Session, lesson: Lesson, writer: Callable[[str], Dict[str, Any]], *,
                  actor_id: Optional[str] = None) -> BookletDraft:
    """Write one chapter's booklet and store it as a draft. Raises ApplicationError when it can't."""
    version = published_version(db, lesson.id)
    source = chapter_source(version) if version else ""
    if not source:
        raise ApplicationError(409, "This chapter has no published lesson to write the booklet from")
    problems: Optional[List[str]] = None
    cost_before = getattr(writer, "cost", 0) or 0
    for attempt in range(ATTEMPTS):
        try:
            raw = writer(build_prompt(lesson, source, problems))
        except ValueError as exc:
            problems = [f"the reply was not valid JSON ({exc})"]
            continue
        problems = booklet_errors(raw)
        if not problems:
            break
        logger.info("Booklet for %s, attempt %s/%s: %s", lesson.id, attempt + 1, ATTEMPTS, "; ".join(problems[:5]))
    if problems:
        raise ApplicationError(502, "The AI's booklet failed the checks after "
                               f"{ATTEMPTS} attempts: " + "; ".join(problems[:5]))
    booklet = finish_booklet(raw, lesson)
    cost = (getattr(writer, "cost", 0) or 0) - cost_before
    draft = BookletDraft(lesson_id=lesson.id, grade=lesson.grade, term=lesson.term,
                         booklet_json=json.dumps(booklet, ensure_ascii=False), status="draft",
                         source_version_id=version.id, model=getattr(writer, "model", None),
                         cost_usd=round(cost, 4) if cost else None, created_by=actor_id)
    # A newer draft replaces older unreviewed ones for the same chapter.
    db.query(BookletDraft).filter(BookletDraft.lesson_id == lesson.id, BookletDraft.status == "draft") \
        .update({"status": "superseded"}, synchronize_session=False)
    db.add(draft)
    db.commit()
    return draft


def write_booklets(grade: int, term: int, *, db: Session, lesson_ids: Optional[List[str]] = None,
                   overwrite: bool = False, actor_id: Optional[str] = None,
                   writer: Optional[Callable[[str], Dict[str, Any]]] = None,
                   progress: Optional[Callable[[int], None]] = None) -> Dict[str, Any]:
    """Write the booklets of one grade and term (or the given chapters of it).

    Skips hand-written chapters, chapters with no published lesson, and (unless overwrite) chapters
    that already have a draft or a published booklet.
    """
    query = db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term)
    if lesson_ids:
        query = query.filter(Lesson.id.in_(lesson_ids))
    lessons = query.order_by(Lesson.lesson_order).all()
    authored = hand_written_ids()
    results = []
    writer = writer or ai_writer()
    for index, lesson in enumerate(lessons):
        if progress:
            progress(int(index * 100 / max(len(lessons), 1)))
        if lesson.id in authored:
            results.append({"lesson_id": lesson.id, "status": "skipped", "detail": "hand-written booklet"})
            continue
        if not published_version(db, lesson.id):
            results.append({"lesson_id": lesson.id, "status": "skipped", "detail": "no published lesson yet"})
            continue
        existing = db.query(BookletDraft).filter(BookletDraft.lesson_id == lesson.id,
                                                 BookletDraft.status.in_(("draft", "published"))).first()
        if existing and not overwrite:
            results.append({"lesson_id": lesson.id, "status": "skipped", "detail": f"already {existing.status}"})
            continue
        try:
            draft = write_booklet(db, lesson, writer, actor_id=actor_id)
            results.append({"lesson_id": lesson.id, "status": "written", "draft_id": draft.id, "cost_usd": draft.cost_usd})
        except ApplicationError as exc:
            if exc.status_code == 503:
                raise
            db.rollback()
            results.append({"lesson_id": lesson.id, "status": "failed", "detail": exc.detail})
        except Exception as exc:  # one chapter's failure must not stop the rest
            from backend.ai.errors import AIUnavailable
            if isinstance(exc, AIUnavailable):
                raise
            db.rollback()
            logger.exception("Booklet for %s failed", lesson.id)
            results.append({"lesson_id": lesson.id, "status": "failed", "detail": str(exc)[:300]})
    if progress:
        progress(100)
    summary = {s: sum(1 for r in results if r["status"] == s) for s in ("written", "skipped", "failed")}
    summary["cost_usd"] = round(sum(r.get("cost_usd") or 0 for r in results), 4)
    return {"grade": grade, "term": term, "summary": summary, "lessons": results}


def published_booklet(db: Session, lesson_id: str) -> Optional[Dict[str, Any]]:
    row = (db.query(BookletDraft).filter(BookletDraft.lesson_id == lesson_id, BookletDraft.status == "published")
           .order_by(BookletDraft.reviewed_at.desc()).first())
    if row is None:
        return None
    try:
        return json.loads(row.booklet_json)
    except ValueError:
        return None


def review_draft(db: Session, draft_id: str, action: str, *, actor_id: Optional[str], note: str = "") -> BookletDraft:
    """Publish or reject a draft. Publishing retires the chapter's previously published booklet."""
    draft = db.get(BookletDraft, draft_id)
    if draft is None:
        raise ApplicationError(404, "Booklet draft not found")
    if action == "publish":
        if draft.status not in ("draft", "superseded", "rejected"):
            raise ApplicationError(409, f"This booklet is already {draft.status}")
        db.query(BookletDraft).filter(BookletDraft.lesson_id == draft.lesson_id, BookletDraft.status == "published",
                                      BookletDraft.id != draft.id) \
            .update({"status": "superseded"}, synchronize_session=False)
        draft.status = "published"
    elif action == "unpublish":
        if draft.status != "published":
            raise ApplicationError(409, "Only a published booklet can be unpublished")
        draft.status = "draft"
    elif action == "reject":
        if draft.status == "published":
            raise ApplicationError(409, "Unpublish this booklet before rejecting it")
        draft.status = "rejected"
    else:
        raise ApplicationError(400, "action must be publish, unpublish or reject")
    draft.reviewed_by = actor_id
    draft.reviewed_at = datetime.datetime.utcnow()
    if note:
        draft.review_note = note[:2000]
    db.commit()
    return draft


def booklet_overview(db: Session, grade: int, term: int) -> List[Dict[str, Any]]:
    """Each chapter of a grade and term with where its booklet comes from and its latest draft."""
    authored = hand_written_ids()
    lessons = (db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term)
               .order_by(Lesson.lesson_order).all())
    drafts = (db.query(BookletDraft).filter(BookletDraft.lesson_id.in_([l.id for l in lessons]))
              .order_by(BookletDraft.created_at.desc()).all()) if lessons else []
    rows = []
    for lesson in lessons:
        own = [d for d in drafts if d.lesson_id == lesson.id]
        published = next((d for d in own if d.status == "published"), None)
        pending = next((d for d in own if d.status == "draft"), None)
        latest = own[0] if own else None
        source = ("hand_written" if lesson.id in authored else "published" if published else "generated")
        rows.append({
            "lesson_id": lesson.id, "lesson_order": lesson.lesson_order,
            "title_ar": lesson.title_ar, "title_en": lesson.title_en,
            "has_lesson_content": published_version(db, lesson.id) is not None,
            "booklet_source": source,
            "published_draft_id": published.id if published else None,
            "pending_draft_id": pending.id if pending else None,
            "latest": _draft_summary(latest) if latest else None,
        })
    return rows


def _draft_summary(draft: BookletDraft) -> Dict[str, Any]:
    return {"id": draft.id, "status": draft.status, "model": draft.model, "cost_usd": draft.cost_usd,
            "created_at": draft.created_at.isoformat() if draft.created_at else None,
            "reviewed_at": draft.reviewed_at.isoformat() if draft.reviewed_at else None,
            "review_note": draft.review_note}


def draft_detail(db: Session, draft_id: str) -> Dict[str, Any]:
    draft = db.get(BookletDraft, draft_id)
    if draft is None:
        raise ApplicationError(404, "Booklet draft not found")
    booklet = json.loads(draft.booklet_json)
    return {**_draft_summary(draft), "lesson_id": draft.lesson_id, "grade": draft.grade, "term": draft.term,
            "unvowelled_words": sorted(set(unvowelled_words(booklet))), "booklet": booklet}
