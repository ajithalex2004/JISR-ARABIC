"""Homework helper (Ask Fahim): explain a school worksheet question by question.

A student photographs a printed worksheet (or uploads a PDF or Word file). The AI reads every
question and returns, per question: the Arabic as printed, an English translation, what the
question asks, a hint (the rule or vocabulary clue), and the answer with its English meaning.
The app shows the hint first and the answer only when asked, so the student can try first. The
student can send their own answer, typed or as a photo of their handwriting, to be told whether
it is right, and the correct answer when it is not.

A hint that still contains the answer is replaced by a generic one, so the hint stays a hint.
"""
import base64
import io
import json
import re
import uuid
import zipfile
from typing import Any, Dict, List, Optional, Tuple

from backend.errors import ApplicationError

SCAN_TTL_SECONDS = 2 * 24 * 3600
MAX_QUESTIONS = 25
MAX_PDF_PAGES = 6
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
PDF_TYPE = "application/pdf"
DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
VERDICTS = ("correct", "almost", "not_yet", "unreadable")

GENERIC_HINT_EN = ("Read the question again slowly and look for the key word. Which rule or new word "
                   "from your lesson does it practise?")
GENERIC_HINT_AR = "اِقْرَأِ السُّؤَالَ مَرَّةً أُخْرَى بِهُدُوءٍ، وَابْحَثْ عَنِ الكَلِمَةِ المُهِمَّةِ فِيهِ."

SCAN_SYSTEM = """You are Fahim, a kind Arabic teacher helping a non-native school child (Grade {grade}) with
homework at home. Their parents cannot read Arabic. You explain each question and give its answer.

Read the worksheet and find every question or exercise item (number them as printed; split
sub-items such as 1a, 1b). For each item give:
- question_ar: the Arabic exactly as printed, with any vowel marks shown.
- question_en: a faithful English translation.
- asks_en: one or two simple sentences saying what the student must do.
- hint_en and hint_ar: a hint, the grammar rule or vocabulary clue needed, as a guiding question
  or reminder. The hint is shown before the answer, so do not state the answer in it.
- answer_format: one of choose, fill_blank, write, match, read, other.
- answer: the correct answer in Arabic, with vowel marks, as the student should write it.
- answer_en: the answer's English meaning, with a one-sentence reason (the rule it uses).
Set is_homework to false when the file is not a school worksheet (then return no questions)."""

CHECK_SYSTEM = """You are Fahim, a kind Arabic teacher checking a non-native school child's (Grade {grade})
homework answer before they hand it in. Compare the student's answer with the question and the
reference answer. Accept answers that are correct even if worded differently, and ignore missing
vowel marks. If the student's answer is a photo of handwriting, first write down what it says.

verdict: correct, almost (small slip such as spelling or one letter), not_yet, or unreadable.
feedback_en and feedback_ar: short and encouraging. If not correct, say where the slip is and
which rule it breaks, then give the correct answer."""

SCAN_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "is_homework": {"type": "BOOLEAN"},
        "title_en": {"type": "STRING"},
        "questions": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "number": {"type": "STRING"},
            "question_ar": {"type": "STRING"},
            "question_en": {"type": "STRING"},
            "asks_en": {"type": "STRING"},
            "hint_en": {"type": "STRING"},
            "hint_ar": {"type": "STRING"},
            "answer_format": {"type": "STRING"},
            "answer": {"type": "STRING"},
            "answer_en": {"type": "STRING"},
        }, "required": ["number", "question_ar", "question_en", "asks_en", "hint_en", "hint_ar", "answer"]}},
    },
    "required": ["is_homework", "questions"],
}

CHECK_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict": {"type": "STRING", "enum": list(VERDICTS)},
        "student_answer_read": {"type": "STRING"},
        "feedback_en": {"type": "STRING"},
        "feedback_ar": {"type": "STRING"},
    },
    "required": ["verdict", "feedback_en", "feedback_ar"],
}

_MARKS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_ALEFS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})


def normalize(text: str) -> str:
    """Letters and digits only, lower case, Arabic without vowel marks or letter-form variants."""
    text = _MARKS.sub("", text or "").translate(_ALEFS).lower()
    return " ".join(re.findall(r"[\w]+", text))


def gives_away(text: str, answer: str, question: str = "") -> bool:
    """Whether `text` contains the answer. Answers that already appear in the question (e.g. a
    word the student must copy) and one-letter answers can't be told apart from a fair hint."""
    target = f" {normalize(answer)} "
    if len(target.replace(" ", "")) < 2:
        return False
    return target in f" {normalize(text)} " and target not in f" {normalize(question)} "


def docx_text(data: bytes) -> str:
    """The paragraphs of a .docx file (Word), read from its XML without extra libraries."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            xml = archive.read("word/document.xml").decode("utf-8", "ignore")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ApplicationError(400, "This Word file could not be opened. Save it as .docx or PDF and try again.") from exc
    paragraphs = []
    for paragraph in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", paragraph))
        if text.strip():
            paragraphs.append(text)
    import html
    return html.unescape("\n".join(paragraphs))


def read_upload(file_base64: str, mime_type: str, file_name: str = "") -> Tuple[List[Tuple[bytes, str]], str]:
    """The worksheet as AI attachments (photo or PDF) or as text (Word)."""
    try:
        data = base64.b64decode(file_base64.split(",", 1)[-1], validate=False)
    except (ValueError, TypeError) as exc:
        raise ApplicationError(400, "The file could not be read.") from exc
    if not data:
        raise ApplicationError(400, "The file is empty.")
    mime = (mime_type or "").lower()
    name = (file_name or "").lower()
    if mime in IMAGE_TYPES:
        return [(data, mime)], ""
    if mime == PDF_TYPE or name.endswith(".pdf"):
        try:
            import pypdf
            pages = len(pypdf.PdfReader(io.BytesIO(data)).pages)
        except Exception as exc:
            raise ApplicationError(400, "This PDF could not be opened.") from exc
        if pages > MAX_PDF_PAGES:
            raise ApplicationError(400, f"Please upload at most {MAX_PDF_PAGES} pages of homework at a time.")
        return [(data, PDF_TYPE)], ""
    if mime == DOCX_TYPE or name.endswith(".docx"):
        text = docx_text(data)
        if not text.strip():
            raise ApplicationError(400, "This Word file has no text. If it holds a picture of the worksheet, upload the picture instead.")
        return [], text[:12000]
    if name.endswith(".doc") or mime == "application/msword":
        raise ApplicationError(400, "Old Word files (.doc) are not supported. Save it as .docx or PDF and try again.")
    raise ApplicationError(400, "Upload a photo (JPG, PNG, WEBP), a PDF or a Word (.docx) file.")


def _generate(feature: str, system: str, prompt: str, schema: Dict[str, Any], attachments, learner_id, tier="fast"):
    from backend.ai import gateway
    from backend.ai.errors import AILimitReached, AIUnavailable
    from backend.modules.curriculum.drafting import parse_model_json
    try:
        reply = gateway.generate(gateway.AIRequest(
            feature=feature, prompt=prompt, system=system, attachments=attachments, json=True, schema=schema,
            temperature=0.2, learner_id=learner_id, tier=tier, max_tokens=8192))
    except AILimitReached as exc:
        raise ApplicationError(429, "You've used today's Fahim requests. Fahim will be back tomorrow!") from exc
    except AIUnavailable as exc:
        raise ApplicationError(503, "Fahim is taking a short break. Please try again in a little while.") from exc
    try:
        result = parse_model_json(reply.text)
    except ValueError as exc:
        raise ApplicationError(502, "Fahim could not read this worksheet clearly. Please try again.") from exc
    if not isinstance(result, dict):
        raise ApplicationError(502, "Fahim could not read this worksheet clearly. Please try again.")
    return result


def _text(value: Any, limit: int = 2000) -> str:
    return str(value or "").strip()[:limit]


def scan_homework(*, file_base64: str, mime_type: str, file_name: str = "", grade: int = 5,
                  learner_id: Optional[str] = None, owner_id: Optional[str] = None) -> Dict[str, Any]:
    from backend.redis_client import cache_set
    attachments, text = read_upload(file_base64, mime_type, file_name)
    prompt = ("Here is the worksheet text:\n\n" + text) if text else "The worksheet is attached."
    result = _generate("homework_scan", SCAN_SYSTEM.format(grade=grade), prompt, SCAN_SCHEMA, attachments,
                       learner_id, tier="strong")

    questions = []
    if result.get("is_homework", True):
        for item in (result.get("questions") or [])[:MAX_QUESTIONS]:
            if not isinstance(item, dict) or not _text(item.get("question_ar")):
                continue
            answer = _text(item.get("answer"), 500)
            question_ar = _text(item.get("question_ar"))
            question = {
                "number": _text(item.get("number"), 20) or str(len(questions) + 1),
                "question_ar": question_ar,
                "question_en": _text(item.get("question_en")),
                "asks_en": _text(item.get("asks_en")),
                "hint_en": _text(item.get("hint_en")),
                "hint_ar": _text(item.get("hint_ar")),
                "answer_format": _text(item.get("answer_format"), 20) or "other",
                "hint_trimmed": False,
                "answer": answer,
                "answer_en": _text(item.get("answer_en"), 1000),
            }
            # The hint comes before the answer, so it must not contain it: fall back to a general nudge.
            if any(gives_away(question[key], answer, question_ar) for key in ("hint_en", "hint_ar", "asks_en")):
                question.update(hint_en=GENERIC_HINT_EN, hint_ar=GENERIC_HINT_AR, hint_trimmed=True)
                if gives_away(question["asks_en"], answer, question_ar):
                    question["asks_en"] = "Answer the question in Arabic."
            questions.append(question)

    scan_id = uuid.uuid4().hex
    cache_set(f"homework:{scan_id}", {"owner": owner_id, "grade": grade, "questions": questions}, SCAN_TTL_SECONDS)
    return {
        "scan_id": scan_id,
        "is_homework": bool(result.get("is_homework", True)) and bool(questions),
        "title_en": _text(result.get("title_en"), 200),
        "questions": questions,
    }


def check_answer(*, scan_id: str, question_number: str, answer_text: Optional[str] = None,
                 answer_image_base64: Optional[str] = None, answer_image_type: Optional[str] = None,
                 learner_id: Optional[str] = None, owner_id: Optional[str] = None) -> Dict[str, Any]:
    from backend.redis_client import cache_get
    scan = cache_get(f"homework:{scan_id}") if re.fullmatch(r"[0-9a-f]{32}", scan_id or "") else None
    if not scan or scan.get("owner") != owner_id:
        raise ApplicationError(404, "This worksheet has expired. Please upload it again.")
    question = next((q for q in scan["questions"] if q["number"] == question_number), None)
    if question is None:
        raise ApplicationError(404, "That question is not on this worksheet.")

    attachments: List[Tuple[bytes, str]] = []
    if answer_image_base64:
        mime = (answer_image_type or "").lower()
        if mime not in IMAGE_TYPES:
            raise ApplicationError(400, "Send the answer as a photo (JPG, PNG or WEBP).")
        try:
            attachments.append((base64.b64decode(answer_image_base64.split(",", 1)[-1]), mime))
        except (ValueError, TypeError) as exc:
            raise ApplicationError(400, "The photo could not be read.") from exc
    elif not _text(answer_text):
        raise ApplicationError(400, "Type your answer or add a photo of it.")

    prompt = json.dumps({
        "question_ar": question["question_ar"],
        "question_en": question["question_en"],
        "reference_answer": question["answer"],
        "student_answer": _text(answer_text, 1000) if not attachments else "(see the attached photo of the student's handwriting)",
    }, ensure_ascii=False)
    result = _generate("homework_check", CHECK_SYSTEM.format(grade=scan.get("grade", 5)), prompt, CHECK_SCHEMA,
                       attachments, learner_id)

    verdict = result.get("verdict") if result.get("verdict") in VERDICTS else "not_yet"
    feedback_en, feedback_ar = _text(result.get("feedback_en")), _text(result.get("feedback_ar"))
    return {
        "question_number": question_number,
        "verdict": verdict,
        "student_answer_read": _text(result.get("student_answer_read"), 1000),
        "feedback_en": feedback_en,
        "feedback_ar": feedback_ar,
        "answer": question["answer"],
        "answer_en": question.get("answer_en", ""),
    }
