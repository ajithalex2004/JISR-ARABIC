"""AI-assisted lesson drafting from scanned MoE textbook pages.

For each lesson, Gemini reads the chapter's page images and drafts a lesson package in
the same schema as the hand-authored Grade 5 lessons. Drafts are stored as
``content_pending`` lesson versions created by ``ai-drafter``: a teacher must approve and
publish them through the curriculum review workflow before any learner sees them.
"""
import copy
import datetime
import hashlib
import json
import re
import logging
import os
import secrets
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.config import content_root
from backend.errors import ApplicationError
from backend.models import CurriculumAuditEvent, Lesson, LessonVersion, Unit

logger = logging.getLogger("fahim.drafting")

AI_DRAFTER = "ai-drafter"
MAX_CHAPTER_PAGES = 14
DEFAULT_CHAPTER_PAGES = 10

# Lesson sections drafted per Gemini call, keeping each reply within output limits.
SECTION_GROUPS: Dict[str, List[str]] = {
    "reading": ["vocabulary_cards", "grammar_lab", "listen_speak_studio", "sentence_builder", "instruction_decoder"],
    "assessment": ["prep_check", "practice_activities", "exam_practice", "spaced_recall"],
    "support": ["learning_paths", "speaking_mission", "parent_companion", "tutor_handover"],
}

# A generator receives (prompt, page image paths) and returns the parsed JSON object.
Generator = Callable[[str, List[Path]], Dict[str, Any]]


def _reference_package() -> Dict[str, Any]:
    from backend.curriculum_seed import BALL_GAMES_CONTENT_V02
    return BALL_GAMES_CONTENT_V02


def _edition_id(lesson: Lesson) -> str:
    return f"moe_gr{lesson.grade}_vol{lesson.term}_2023"


def _pdf_start(lesson: Lesson, db: Session) -> int:
    """PDF page where a lesson starts: the active version's pdf_start_page, else the syllabus offset."""
    version = db.query(LessonVersion).filter(
        LessonVersion.lesson_id == lesson.id, LessonVersion.is_active == True  # noqa: E712
    ).first()
    if version:
        try:
            pdf_start = json.loads(version.content_json).get("pdf_start_page")
            if isinstance(pdf_start, int) and pdf_start > 0:
                return pdf_start
        except (TypeError, ValueError):
            pass
    offset = 1 if (lesson.grade in (5, 7) and lesson.term == 1) else 0
    return (lesson.start_page or 1) + offset


def chapter_pages(lesson: Lesson, db: Session) -> List[int]:
    """PDF pages of a lesson: from its start up to the next lesson's start (bounded)."""
    start = _pdf_start(lesson, db)
    following = db.query(Lesson).filter(
        Lesson.grade == lesson.grade, Lesson.term == lesson.term, Lesson.lesson_order > lesson.lesson_order
    ).order_by(Lesson.lesson_order).first()
    end = _pdf_start(following, db) - 1 if following else start + DEFAULT_CHAPTER_PAGES - 1
    end = max(start, min(end, start + MAX_CHAPTER_PAGES - 1))
    return list(range(start, end + 1))


def chapter_images(lesson: Lesson, db: Session) -> List[Path]:
    folder = content_root() / "pdf_pages_sample" / _edition_id(lesson)
    return [p for p in (folder / f"page_{n}.png" for n in chapter_pages(lesson, db)) if p.is_file()]


def _build_prompt(lesson: Lesson, group: str, sections: List[str], page_numbers: List[int]) -> str:
    reference = _reference_package()
    example = {key: reference[key] for key in sections}
    return f"""You are an expert UAE Ministry of Education teacher of Arabic for non-native speakers.
The attached images are pages {page_numbers[0]}–{page_numbers[-1]} of the official Grade {lesson.grade},
Term {lesson.term} Arabic textbook, covering the lesson currently titled "{lesson.title_ar}" ({lesson.title_en}).

Draft the "{group}" sections of an interactive lesson for Grade {lesson.grade} learners.
Rules:
- Base every item on the actual texts, vocabulary and exercises on these pages. Do not invent topics.
- Arabic must be correct Modern Standard Arabic; give vocabulary and example sentences full tashkeel.
- Every *_en field is a natural English translation or explanation for parents and learners.
- Pitch difficulty at Grade {lesson.grade}; keep content safe and appropriate for children.
- Multiple-choice "correct_answer" must equal the "id" of one of that question's options.
- Return ONLY a JSON object with exactly these keys: {", ".join(sections)}.
- Follow the structure, field names and list sizes of this example from a Grade 5 lesson
  (copy its shape, not its content):
{json.dumps(example, ensure_ascii=False)}
"""


DRAFT_ATTEMPTS = 3


def parse_model_json(text: str) -> Any:
    """json.loads, tolerating the slips models make in long JSON replies.

    Tries the text as-is first; then strips a Markdown fence and // or /* */ comments and drops
    trailing commas before } or ]. Raises ValueError when it still isn't valid JSON.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)
    # Twice: removing a comment can expose a trailing comma that sat in front of it.
    cleaned = _strip_outside_strings(_strip_outside_strings(cleaned))
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(str(exc)) from exc


def _strip_outside_strings(text: str) -> str:
    """Remove comments and trailing commas, leaving the contents of JSON strings untouched."""
    out, i, n = [], 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
        elif ch == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1  # trailing comma
            else:
                out.append(ch)
                i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def gemini_generator() -> Generator:
    """Default generator: uploads page images and asks Gemini for a JSON section group."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ApplicationError(503, "GEMINI_API_KEY is not configured; AI drafting is unavailable")
    from google import genai
    from google.genai import types
    from backend.modules.tutoring.assistant import GEMINI_MODEL, _child_safety_settings

    client = genai.Client(api_key=api_key)
    model = os.getenv("FAHIM_DRAFT_MODEL") or GEMINI_MODEL
    uploaded: Dict[Path, Any] = {}

    def generate(prompt: str, images: List[Path]) -> Dict[str, Any]:
        files = []
        for path in images:
            if path not in uploaded:
                uploaded[path] = client.files.upload(file=str(path))
            files.append(uploaded[path])
        last_error = None
        # Long Arabic drafts occasionally come back as slightly malformed JSON; repair what can be
        # repaired and otherwise ask again, so one bad reply doesn't fail the whole chapter.
        for attempt in range(DRAFT_ATTEMPTS):
            response = client.models.generate_content(
                model=model,
                contents=[*files, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.4 if attempt == 0 else 0.2,
                    max_output_tokens=16384,
                    response_mime_type="application/json",
                    safety_settings=_child_safety_settings(types),
                ),
            )
            if not response or not response.text:
                last_error = "Gemini returned an empty draft"
                continue
            try:
                return parse_model_json(response.text)
            except ValueError as exc:
                last_error = f"Gemini returned malformed JSON ({exc})"
                logger.warning("Draft attempt %s/%s unreadable: %s", attempt + 1, DRAFT_ATTEMPTS, exc)
        raise ApplicationError(502, f"{last_error} after {DRAFT_ATTEMPTS} attempts")

    generate.model = model  # type: ignore[attr-defined]
    return generate


def _list_template(reference: list) -> Any:
    """What every item of a list must look like: for objects, only the keys all reference items share."""
    if not reference or not isinstance(reference[0], (dict, list)):
        return None
    if not all(isinstance(item, dict) for item in reference):
        return reference[0]
    shared = set(reference[0]).intersection(*(set(item) for item in reference[1:]))
    template = {}
    for key, value in reference[0].items():
        if key not in shared:
            continue
        if isinstance(value, list) and all(isinstance(item[key], list) for item in reference):
            # Pool sibling lists so nested items are held only to what they all share.
            value = [v for item in reference for v in item[key]]
        template[key] = value
    return template


def _shape_errors(candidate: Any, reference: Any, path: str) -> List[str]:
    """Compare a drafted value to the reference schema (keys, types, non-empty lists)."""
    if isinstance(reference, dict):
        if not isinstance(candidate, dict):
            return [f"{path}: expected object"]
        errors = []
        for key, ref_value in reference.items():
            if key not in candidate:
                errors.append(f"{path}.{key}: missing")
            else:
                errors.extend(_shape_errors(candidate[key], ref_value, f"{path}.{key}"))
        return errors
    if isinstance(reference, list):
        if not isinstance(candidate, list) or not candidate:
            return [f"{path}: expected a non-empty list"]
        template = _list_template(reference)
        if template is not None:
            return [e for i, item in enumerate(candidate) for e in _shape_errors(item, template, f"{path}[{i}]")]
        return []
    if isinstance(reference, str):
        return [] if isinstance(candidate, str) and candidate.strip() else [f"{path}: expected text"]
    if isinstance(reference, (int, float)) and not isinstance(reference, bool):
        return [] if isinstance(candidate, (int, float)) and not isinstance(candidate, bool) else [f"{path}: expected a number"]
    return []


def _answer_errors(node: Any, path: str = "") -> List[str]:
    """Every multiple-choice correct_answer must name one of its own options."""
    errors = []
    if isinstance(node, dict):
        options = node.get("options")
        if "correct_answer" in node and isinstance(options, list) and options and isinstance(options[0], dict):
            option_ids = {o.get("id") for o in options if isinstance(o, dict)}
            if node["correct_answer"] not in option_ids:
                errors.append(f"{path}: correct_answer '{node['correct_answer']}' is not one of {sorted(map(str, option_ids))}")
        for key, value in node.items():
            errors.extend(_answer_errors(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            errors.extend(_answer_errors(item, f"{path}[{i}]"))
    return errors


def _assign_ids(section_key: str, node: Any, lesson_id: str, counter: List[int]) -> None:
    """Give every activity a lesson-unique id; option ids stay local to their question."""
    if isinstance(node, dict):
        if "id" in node:
            counter[0] += 1
            node["id"] = f"{lesson_id}_{section_key}_{counter[0]:02d}"
        for key, value in node.items():
            if key != "options":
                _assign_ids(section_key, value, lesson_id, counter)
    elif isinstance(node, list):
        for item in node:
            _assign_ids(section_key, item, lesson_id, counter)


def draft_lesson_package(lesson: Lesson, db: Session, generate: Optional[Generator] = None) -> Dict[str, Any]:
    """Draft and validate a full lesson package for one lesson (not yet stored)."""
    images = chapter_images(lesson, db)
    if not images:
        raise ApplicationError(404, f"No textbook page images found for {lesson.id}; upload the scans first")
    generate = generate or gemini_generator()
    page_numbers = [int(p.stem.split("_")[1]) for p in images]
    reference = _reference_package()

    package: Dict[str, Any] = {
        "lesson_id": lesson.id,
        "version": "ai-draft",
        "title_ar": lesson.title_ar,
        "title_en": lesson.title_en,
        "unit_title_ar": reference["unit_title_ar"],
        "unit_title_en": reference["unit_title_en"],
        "grade": lesson.grade,
        "term": lesson.term,
        "start_page": lesson.start_page,
        "pdf_start_page": page_numbers[0],
    }
    unit = db.get(Unit, lesson.unit_id) if lesson.unit_id else None
    if unit is not None:
        package["unit_title_ar"] = unit.title_ar or package["unit_title_ar"]
        package["unit_title_en"] = unit.title_en or package["unit_title_en"]

    errors: List[str] = []
    for group, sections in SECTION_GROUPS.items():
        drafted = generate(_build_prompt(lesson, group, sections, page_numbers), images)
        if not isinstance(drafted, dict):
            raise ApplicationError(502, f"Gemini returned a non-object for the {group} sections")
        for key in sections:
            value = copy.deepcopy(drafted.get(key))
            errors.extend(_shape_errors(value, reference[key], key))
            _assign_ids(key, value, lesson.id, [0])
            package[key] = value

    errors.extend(_answer_errors(package))
    if errors:
        raise ApplicationError(422, "Draft failed validation: " + "; ".join(errors[:8]))

    package["provenance"] = {
        "source": "ai_draft",
        "model": getattr(generate, "model", "custom"),
        "source_edition": _edition_id(lesson),
        "source_pdf_pages": page_numbers,
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "review_required": True,
    }
    return package


def store_draft(lesson: Lesson, package: Dict[str, Any], db: Session, actor_id: Optional[str] = None) -> LessonVersion:
    from backend.modules.curriculum.authoring import _validate_version_quality

    content_str = json.dumps(package, ensure_ascii=False)
    content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M")
    version = LessonVersion(
        id=f"ver_{lesson.id}_ai_{stamp}_{secrets.token_hex(4)}",
        lesson_id=lesson.id,
        version_tag=f"ai-{stamp}",
        content_json=content_str,
        content_hash=content_hash,
        is_active=False,
        status="content_pending",
        created_by=AI_DRAFTER,
    )
    defect = _validate_version_quality(lesson, version)
    if defect:
        raise ApplicationError(422, f"Draft failed the quality gate: {defect}")
    db.add(version)
    db.add(CurriculumAuditEvent(
        actor_id=actor_id,
        action="ai_draft",
        lesson_id=lesson.id,
        version_id=version.id,
        version_tag=version.version_tag,
        details_json=json.dumps({"action": "ai_draft", "source_pdf_pages": package["provenance"]["source_pdf_pages"]}),
    ))
    db.commit()
    return version


def pending_ai_draft(lesson_id: str, db: Session) -> Optional[LessonVersion]:
    return db.query(LessonVersion).filter(
        LessonVersion.lesson_id == lesson_id,
        LessonVersion.created_by == AI_DRAFTER,
        LessonVersion.status == "content_pending",
    ).first()


def draft_lessons(grade: int, term: int, *, db: Session, lesson_ids: Optional[List[str]] = None,
                  overwrite: bool = False, generate: Optional[Generator] = None,
                  actor_id: Optional[str] = None, progress: Callable[[int], None] = lambda pct: None) -> Dict[str, Any]:
    """Draft every lesson of a grade/term (or the listed lessons); one failure never stops the batch."""
    query = db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term)
    if lesson_ids:
        query = query.filter(Lesson.id.in_(lesson_ids))
    lessons = query.order_by(Lesson.lesson_order).all()
    if not lessons:
        raise ApplicationError(404, f"No lessons found for Grade {grade} Term {term}")

    results = []
    for index, lesson in enumerate(lessons, start=1):
        existing = pending_ai_draft(lesson.id, db)
        if existing and not overwrite:
            results.append({"lesson_id": lesson.id, "status": "skipped", "detail": f"AI draft {existing.version_tag} awaits review"})
        else:
            try:
                package = draft_lesson_package(lesson, db, generate=generate)
                if existing:
                    existing.status = "superseded"
                version = store_draft(lesson, package, db, actor_id=actor_id)
                results.append({"lesson_id": lesson.id, "status": "drafted", "version_id": version.id,
                                "pages": package["provenance"]["source_pdf_pages"]})
            except Exception as exc:  # keep drafting the rest of the term
                db.rollback()
                detail = exc.detail if isinstance(exc, ApplicationError) else f"{type(exc).__name__}: {exc}"
                logger.warning("AI draft failed for %s: %s", lesson.id, detail)
                results.append({"lesson_id": lesson.id, "status": "failed", "detail": detail})
        progress(int(index / len(lessons) * 95))

    summary = {status: sum(1 for r in results if r["status"] == status) for status in ("drafted", "skipped", "failed")}
    return {"grade": grade, "term": term, "summary": summary, "lessons": results}
