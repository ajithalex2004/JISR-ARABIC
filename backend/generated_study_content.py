"""
Grade-aware study content generator.

The hand-authored banks (``malazim_bank`` and ``capsules_bank``) only cover a few
grades (5, 6 and 7).  For every other grade the study modules previously fell back
to the Grade 5 "Ball Games" content, so switching to e.g. Grade 8 in the admin
portal kept showing Grade 5 material.

This module builds Smart Study Booklets, Learning Capsules and Mindmap chapters
for any grade/term directly from the official syllabus registry
(``backend.modules.curriculum.syllabus_data``) so each module always reflects the
chapters shown in Curriculum & Lessons for the selected grade.
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.modules.curriculum.syllabus_data import (
    GRADE_GRAMMAR_MAP,
    get_syllabus_for_grade_and_term,
)

_LESSON_ID_RE = re.compile(r"^lesson_g(\d+)_t(\d+)_ch(\d+)$")
_GRADE_ALIAS_RE = re.compile(r"^(?:grade_?|g)?(\d{1,2})$")
_GENERATED_CAPSULE_RE = re.compile(r"^capsule_g(\d+)_t(\d+)_(\d+)$")

_ARABIC_ORDINALS = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس",
                    "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر", "الثاني عشر"]

# Grade-appropriate core skill vocabulary used for generated glossary sections.
_GRADE_SKILL_VOCAB: Dict[str, List[Tuple[str, str, str]]] = {
    "primary": [
        ("القِرَاءَةُ", "Reading", "ق-ر-أ"),
        ("الكِتَابَةُ", "Writing", "ك-ت-ب"),
        ("الاسْتِمَاعُ", "Listening", "س-م-ع"),
        ("المُحَادَثَةُ", "Conversation", "ح-د-ث"),
    ],
    "middle": [
        ("الفَصَاحَةُ", "Eloquence", "ف-ص-ح"),
        ("الحِكْمَةُ", "Wisdom", "ح-ك-م"),
        ("الإِبْدَاعُ", "Creativity", "ب-د-ع"),
        ("التَّحْلِيلُ", "Analysis", "ح-ل-ل"),
    ],
    "secondary": [
        ("البَلَاغَةُ", "Rhetoric", "ب-ل-غ"),
        ("النَّقْدُ", "Criticism", "ن-ق-د"),
        ("البُرْهَانُ", "Evidence / Proof", "ب-ر-ه"),
        ("الاسْتِنْتَاجُ", "Inference", "ن-ت-ج"),
    ],
}


def _vocab_for_grade(grade: int) -> List[Tuple[str, str, str]]:
    if grade <= 4:
        return _GRADE_SKILL_VOCAB["primary"]
    if grade <= 8:
        return _GRADE_SKILL_VOCAB["middle"]
    return _GRADE_SKILL_VOCAB["secondary"]


def _ordinal_ar(n: int) -> str:
    return _ARABIC_ORDINALS[n - 1] if 1 <= n <= len(_ARABIC_ORDINALS) else str(n)


def _grammar(grade: int) -> Dict[str, Any]:
    return GRADE_GRAMMAR_MAP.get(grade) or GRADE_GRAMMAR_MAP[5]


def _chapter(grade: int, term: int, order: int) -> Optional[Dict[str, Any]]:
    syllabus = get_syllabus_for_grade_and_term(grade, term)
    for item in syllabus:
        if item.get("lesson_order") == order:
            return item
    return syllabus[0] if syllabus else None


def parse_lesson_reference(lesson_id: str) -> Optional[Tuple[int, int, int]]:
    """Return (grade, term, chapter_order) for ``lesson_gX_tY_chZZ`` or grade aliases."""
    lid = str(lesson_id or "").strip().lower()
    m = _LESSON_ID_RE.match(lid)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = _GRADE_ALIAS_RE.match(lid)
    if m:
        grade = int(m.group(1))
        if 1 <= grade <= 12:
            return grade, 1, 1
    return None


def lesson_id_for_grade(grade: int, term: int = 1, order: int = 1) -> str:
    """Canonical chapter lesson id used by Curriculum & Lessons for a grade."""
    if grade == 5 and term == 1 and order == 1:
        return "lesson_01_ball_games"
    return f"lesson_g{grade}_t{term}_ch{order:02d}"


# ---------------------------------------------------------------------------
# Smart Study Booklets (Malazim)
# ---------------------------------------------------------------------------
def generate_booklet(grade: int, term: int = 1, order: int = 1) -> Optional[Dict[str, Any]]:
    ch = _chapter(grade, term, order)
    if ch is None:
        return None
    lesson_id = ch["id"]
    title_ar, title_en = ch["title_ar"], ch["title_en"]
    unit_ar, unit_en = ch["unit_title_ar"], ch["unit_title_en"]
    start_page = int(ch.get("start_page", 6))
    gram = _grammar(grade)
    ex1 = gram["examples"][0]
    ex2 = gram["examples"][-1]
    vocab = _vocab_for_grade(grade)
    p = f"g{grade}_t{term}_ch{order:02d}"

    vocab_lines_ar = "\n".join(f"- {w}: (الجذر {r}) — {en}" for w, en, r in vocab)
    vocab_lines_en = "\n".join(f"- {en} ({w}) — root {r}" for w, en, r in vocab)

    return {
        "lesson_id": lesson_id,
        "title_ar": f"ملزمة {title_ar} — {unit_ar}",
        "title_en": f"{title_en} Smart Booklet — Grade {grade} Term {term}",
        "grade": grade,
        "term": term,
        "pages_reference": f"Pages {start_page}–{start_page + 9} (UAE MoE Student Book Grade {grade})",
        "curriculum_alignment": f"UAE Ministry of Education Arabic Grade {grade}",
        "is_generated": True,
        "study_mode": {
            "mode_title_ar": f"وضع المذاكرة التفاعلية الشاملة (الصف {grade})",
            "mode_title_en": f"Comprehensive Interactive Study Mode (Grade {grade})",
            "estimated_minutes": 25,
            "sections": [
                {
                    "section_id": f"sec_{p}_01_reading",
                    "title_ar": f"١. نص الدرس: {title_ar}",
                    "title_en": f"1. Lesson Text: {title_en}",
                    "content_ar": (
                        f"يَتَنَاوَلُ الدَّرْسُ {_ordinal_ar(order)} مِنَ الفَصْلِ الدِّرَاسِيِّ {_ordinal_ar(term)} "
                        f"مَوْضُوعَ ({title_ar}) ضِمْنَ وَحْدَةِ ({unit_ar}). يَقْرَأُ الطَّالِبُ النَّصَّ قِرَاءَةً "
                        "وَاعِيَةً، وَيَسْتَخْرِجُ الأَفْكَارَ الرَّئِيسَةَ وَالفَرْعِيَّةَ، وَيُحَلِّلُ القِيَمَ وَالمَعَانِيَ "
                        "الَّتِي يَحْمِلُهَا النَّصُّ."
                    ),
                    "content_en": (
                        f"Chapter {order} of Term {term} explores '{title_en}' within the unit '{unit_en}'. "
                        "Students read the text attentively, extract the main and supporting ideas, and analyse "
                        "the values and meanings it conveys."
                    ),
                    "key_takeaways_ar": [
                        f"الفكرة المحورية: {title_ar}.",
                        f"الوحدة الدراسية: {unit_ar}.",
                    ],
                    "key_takeaways_en": [
                        f"Core theme: {title_en}.",
                        f"Curriculum unit: {unit_en}.",
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا عُنْوَانُ الدَّرْسِ الَّذِي تَدْرُسُهُ فِي هَذِهِ المُلْزَمَةِ؟",
                        "question_en": "What is the title of the lesson covered in this booklet?",
                        "options": [title_ar, "أَلْعَابُ الكُرَةِ", "رِحْلَةٌ إِلَى البَحْرِ"],
                        "options_en": [title_en, "Ball Games", "A Trip to the Sea"],
                        "correct_index": 0,
                        "explanation_ar": f"أحسنت! هذه الملزمة مخصصة لدرس ({title_ar}) في الصف {grade}.",
                        "explanation_en": f"Well done! This booklet covers '{title_en}' for Grade {grade}.",
                    },
                },
                {
                    "section_id": f"sec_{p}_02_grammar",
                    "title_ar": f"٢. التراكيب اللغوية: {gram['rule_ar']}",
                    "title_en": f"2. Grammar Focus: {gram['rule_en']}",
                    "content_ar": (
                        f"القَاعِدَةُ المُقَرَّرَةُ لِلصَّفِّ {grade}: {gram['rule_ar']}.\n"
                        f"مِثَالٌ (١): {ex1['phrase_ar']}\n"
                        f"مِثَالٌ (٢): {ex2['phrase_ar']}"
                    ),
                    "content_en": (
                        f"{gram['explanation']}\n"
                        f"Example 1: {ex1['translation_en']}\n"
                        f"Example 2: {ex2['translation_en']}"
                    ),
                    "key_takeaways_ar": [
                        f"القاعدة: {gram['rule_ar']}.",
                        f"تطبيق: {ex1['phrase_ar']}",
                    ],
                    "key_takeaways_en": [
                        f"Rule: {gram['rule_en']}.",
                        gram["explanation"],
                    ],
                    "inline_exercise": {
                        "question_ar": f"مَا القَاعِدَةُ النَّحْوِيَّةُ المُقَرَّرَةُ فِي هَذَا الدَّرْسِ لِلصَّفِّ {grade}؟",
                        "question_en": f"Which grammar topic is studied in this Grade {grade} lesson?",
                        "options": [
                            "الحُرُوفُ الهِجَائِيَّةُ فَقَطْ",
                            gram["rule_ar"],
                            "عَلَامَاتُ التَّرْقِيمِ فَقَطْ",
                        ],
                        "options_en": [
                            "The alphabet only",
                            gram["rule_en"],
                            "Punctuation marks only",
                        ],
                        "correct_index": 1,
                        "explanation_ar": f"صحيح! قاعدة الصف {grade} هي: {gram['rule_ar']}.",
                        "explanation_en": f"Correct! The Grade {grade} grammar focus is {gram['rule_en']}.",
                    },
                },
                {
                    "section_id": f"sec_{p}_03_glossary",
                    "title_ar": "٣. قَامُوسِيَ الخَاصُّ: مُفْرَدَاتُ الدَّرْسِ",
                    "title_en": "3. My Glossary: Lesson Vocabulary",
                    "content_ar": f"مُفْرَدَاتٌ أَسَاسِيَّةٌ لِدَرْسِ ({title_ar}):\n{vocab_lines_ar}",
                    "content_en": f"Key vocabulary for '{title_en}':\n{vocab_lines_en}",
                    "key_takeaways_ar": [f"{vocab[0][0]}: {vocab[0][1]}", f"{vocab[1][0]}: {vocab[1][1]}"],
                    "key_takeaways_en": [f"{vocab[0][1]} ({vocab[0][0]})", f"{vocab[1][1]} ({vocab[1][0]})"],
                    "inline_exercise": {
                        "question_ar": f"مَا جَذْرُ كَلِمَةِ ({vocab[1][0]})؟",
                        "question_en": f"What is the root of '{vocab[1][0]}' ({vocab[1][1]})?",
                        "options": ["ك-ت-ب", vocab[1][2], "ل-ع-ب"],
                        "options_en": ["K-T-B", vocab[1][2], "L-A-B"],
                        "correct_index": 1,
                        "explanation_ar": f"ممتاز! جذر ({vocab[1][0]}) هو ({vocab[1][2]}).",
                        "explanation_en": f"Excellent! The root of '{vocab[1][0]}' is {vocab[1][2]}.",
                    },
                },
            ],
        },
        "quick_review_mode": {
            "mode_title_ar": f"وضع الملاحظات المركزة ومراجعة الـ 15 دقيقة (الصف {grade})",
            "mode_title_en": f"15-Minute Exam Revision & Golden Rules (Grade {grade})",
            "estimated_minutes": 15,
            "high_yield_summary": [
                {
                    "bullet_ar": f"موضوع الدرس: ({title_ar}) ضمن وحدة ({unit_ar}).",
                    "bullet_en": f"Lesson theme: '{title_en}' in the unit '{unit_en}'.",
                },
                {
                    "bullet_ar": f"القاعدة النحوية المقررة: {gram['rule_ar']}.",
                    "bullet_en": f"Core grammar rule: {gram['rule_en']}.",
                },
                {
                    "bullet_ar": "اقرأ النص بالضبط السليم، واستخرج الفكرة الرئيسة والأفكار الداعمة.",
                    "bullet_en": "Read the text with correct vowelling and extract the main and supporting ideas.",
                },
            ],
            "essential_formulas": [
                {
                    "title_ar": f"تطبيق القاعدة: {gram['rule_ar']}",
                    "title_en": f"Applying: {gram['rule_en']}",
                    "formula_ar": gram["rule_ar"],
                    "formula_en": gram["explanation"],
                    "example_ar": ex1["phrase_ar"],
                    "example_en": ex1["translation_en"],
                },
                {
                    "title_ar": "مثال تطبيقي ثانٍ",
                    "title_en": "Second Worked Example",
                    "formula_ar": gram["rule_ar"],
                    "formula_en": gram["rule_en"],
                    "example_ar": ex2["phrase_ar"],
                    "example_en": ex2["translation_en"],
                },
            ],
            "exam_pitfall_warnings": [
                {
                    "warning_ar": "انتبه إلى الحركات الإعرابية في أواخر الكلمات عند الضبط بالشكل في الاختبار الوزاري.",
                    "warning_en": "Pay attention to case endings when vowelling words in MoE exam questions.",
                },
                {
                    "warning_ar": f"لا تخلط بين أمثلة قاعدة ({gram['rule_ar']}) والقواعد المشابهة لها.",
                    "warning_en": f"Do not confuse examples of {gram['rule_en']} with similar rules.",
                },
            ],
        },
    }


# ---------------------------------------------------------------------------
# Learning Capsules
# ---------------------------------------------------------------------------
def _build_capsule(grade: int, term: int, idx: int, ch: Dict[str, Any]) -> Dict[str, Any]:
    gram = _grammar(grade)
    title_ar, title_en = ch["title_ar"], ch["title_en"]
    is_grammar = idx % 2 == 0
    ex = gram["examples"][idx % len(gram["examples"])]
    capsule_id = f"capsule_g{grade}_t{term}_{idx:02d}"
    if is_grammar:
        return {
            "id": capsule_id,
            "grade": grade,
            "term": term,
            "lesson_id": ch["id"],
            "title_ar": f"{title_ar}: {gram['rule_ar']}",
            "title_en": f"{title_en}: {gram['rule_en']}",
            "duration_minutes": 4,
            "difficulty": "Medium",
            "topic": "Grammar & Syntax (القواعد والتراكيب)",
            "summary_ar": f"تطبيق قاعدة ({gram['rule_ar']}) من خلال درس ({title_ar}).",
            "summary_en": f"Apply {gram['rule_en']} through the lesson '{title_en}'.",
            "audio_script_ar": f"مرحباً بطل الصف {grade}! في درس ({title_ar}) نتعلم: {gram['rule_ar']}. مثال: {ex['phrase_ar']}",
            "audio_script_en": f"Welcome Grade {grade} champion! In '{title_en}' we learn {gram['rule_en']}. {gram['explanation']}",
            "rule_steps": [
                {
                    "step_number": 1,
                    "title_ar": "القاعدة",
                    "title_en": "1. The Rule",
                    "explanation_ar": gram["rule_ar"],
                    "explanation_en": gram["explanation"],
                },
                {
                    "step_number": 2,
                    "title_ar": "التطبيق",
                    "title_en": "2. Application",
                    "explanation_ar": ex["phrase_ar"],
                    "explanation_en": ex["translation_en"],
                },
            ],
            "examples": [
                {"sentence_ar": e["phrase_ar"], "translation_en": e["translation_en"], "type": "مثال تطبيقي"}
                for e in gram["examples"]
            ],
            "quiz": [
                {
                    "question_ar": f"ما القاعدة النحوية التي يركز عليها هذا الدرس في الصف {grade}؟",
                    "question_en": f"Which grammar rule does this Grade {grade} capsule focus on?",
                    "options": ["أسماء الإشارة فقط", gram["rule_ar"], "حروف الهجاء فقط"],
                    "options_en": ["Demonstratives only", gram["rule_en"], "Alphabet only"],
                    "correct_index": 1,
                    "explanation_ar": f"أحسنت! القاعدة هي: {gram['rule_ar']}.",
                    "explanation_en": f"Well done! The rule is {gram['rule_en']}.",
                }
            ],
        }
    vocab = _vocab_for_grade(grade)
    return {
        "id": capsule_id,
        "grade": grade,
        "term": term,
        "lesson_id": ch["id"],
        "title_ar": f"{title_ar}: المفردات والفهم",
        "title_en": f"{title_en}: Vocabulary & Comprehension",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Vocabulary & Context (المفردات والمعاجم)",
        "summary_ar": f"أبرز أفكار ومفردات درس ({title_ar}) في وحدة ({ch['unit_title_ar']}).",
        "summary_en": f"Key ideas and vocabulary of '{title_en}' in the unit '{ch['unit_title_en']}'.",
        "audio_script_ar": f"لنتعرف معاً على درس ({title_ar}). من مفرداته: " + "، ".join(w for w, _, _ in vocab) + ".",
        "audio_script_en": f"Let's explore '{title_en}'. Key words: " + ", ".join(en for _, en, _ in vocab) + ".",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "الفكرة الرئيسة",
                "title_en": "1. Main Idea",
                "explanation_ar": f"يدور الدرس حول ({title_ar}).",
                "explanation_en": f"The lesson centres on '{title_en}'.",
            },
            {
                "step_number": 2,
                "title_ar": "المفردات الأساسية",
                "title_en": "2. Core Vocabulary",
                "explanation_ar": " / ".join(f"{w} ({r})" for w, _, r in vocab),
                "explanation_en": " / ".join(f"{en} ({r})" for _, en, r in vocab),
            },
        ],
        "examples": [
            {"word_ar": w, "translation_en": en, "type": f"الجذر: {r}"} for w, en, r in vocab
        ],
        "quiz": [
            {
                "question_ar": "ما عنوان الدرس الذي تتناوله هذه الكبسولة؟",
                "question_en": "Which lesson does this capsule cover?",
                "options": ["أَلْعَابُ الكُرَةِ", title_ar, "رُكُوبُ الخَيْلِ"],
                "options_en": ["Ball Games", title_en, "Horse Riding"],
                "correct_index": 1,
                "explanation_ar": f"صحيح! الكبسولة مخصصة لدرس ({title_ar}).",
                "explanation_en": f"Correct! This capsule covers '{title_en}'.",
            }
        ],
    }


def generate_capsules(grade: int, term: int = 1, limit: int = 5) -> List[Dict[str, Any]]:
    syllabus = get_syllabus_for_grade_and_term(grade, term)[:limit]
    return [_build_capsule(grade, term, idx + 1, ch) for idx, ch in enumerate(syllabus)]


def get_generated_capsule(capsule_id: str) -> Optional[Dict[str, Any]]:
    m = _GENERATED_CAPSULE_RE.match(str(capsule_id or ""))
    if not m:
        return None
    grade, term, idx = int(m.group(1)), int(m.group(2)), int(m.group(3))
    syllabus = get_syllabus_for_grade_and_term(grade, term)
    if not 1 <= idx <= len(syllabus):
        return None
    return _build_capsule(grade, term, idx, syllabus[idx - 1])


# ---------------------------------------------------------------------------
# Mindmaps & Flowcharts
# ---------------------------------------------------------------------------
_CHAPTER_COLORS = ["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626",
                   "#0891B2", "#4F46E5", "#16A34A", "#EA580C", "#DB2777"]


def generate_mindmap_chapters(grade: int, term: int = 1) -> List[Dict[str, Any]]:
    """Return chapters shaped like the frontend ``MindmapChapter`` interface."""
    gram = _grammar(grade)
    vocab = _vocab_for_grade(grade)
    syllabus = get_syllabus_for_grade_and_term(grade, term)
    chapters = []
    for idx, ch in enumerate(syllabus):
        start = int(ch.get("start_page", 6))
        siblings = [s for s in syllabus if s["unit_id"] == ch["unit_id"] and s["id"] != ch["id"]][:4]
        chapters.append({
            "id": ch["id"],
            "titleAr": ch["title_ar"],
            "titleEn": ch["title_en"],
            "unitAr": ch["unit_title_ar"],
            "unitEn": ch["unit_title_en"],
            "pages": f"{start} - {start + 9}",
            "color": _CHAPTER_COLORS[idx % len(_CHAPTER_COLORS)],
            "summaryAr": f"خريطة مفاهيم درس ({ch['title_ar']}): الأفكار الرئيسة، المفردات، وقاعدة {gram['rule_ar']}.",
            "summaryEn": f"Concept map for '{ch['title_en']}': key ideas, vocabulary and {gram['rule_en']}.",
            "branches": [
                {
                    "titleAr": "المفردات وجذور الكلمات",
                    "titleEn": "Core Vocabulary & Roots",
                    "color": "#0284C7",
                    "items": [
                        {"ar": w, "en": en, "root": r} for w, en, r in vocab
                    ],
                },
                {
                    "titleAr": "الأفكار الرئيسة للدرس",
                    "titleEn": "Key Lesson Ideas",
                    "color": "#059669",
                    "items": [
                        {
                            "ar": f"الموضوع: {ch['title_ar']}",
                            "en": f"Theme: {ch['title_en']}",
                            "meaningAr": f"الدرس {_ordinal_ar(ch['lesson_order'])} من الفصل الدراسي {_ordinal_ar(term)}.",
                            "meaningEn": f"Chapter {ch['lesson_order']} of Term {term}, Grade {grade}.",
                        },
                        {
                            "ar": f"الوحدة: {ch['unit_title_ar']}",
                            "en": f"Unit: {ch['unit_title_en']}",
                        },
                        {
                            "ar": "الفكرة الرئيسة والأفكار الداعمة",
                            "en": "Main idea & supporting details",
                            "meaningAr": "استخرج الفكرة المحورية للنص ثم الأفكار الفرعية التي تدعمها.",
                            "meaningEn": "Identify the central idea, then the supporting sub-ideas.",
                        },
                    ],
                },
                {
                    "titleAr": f"القواعد المرتبطة: {gram['rule_ar']}",
                    "titleEn": f"Grammar: {gram['rule_en']}",
                    "color": "#7C3AED",
                    "items": [
                        {
                            "ar": e["phrase_ar"],
                            "en": e["translation_en"],
                            "meaningEn": gram["explanation"],
                        }
                        for e in gram["examples"]
                    ],
                },
                {
                    "titleAr": "دروس الوحدة المترابطة",
                    "titleEn": "Connected Unit Lessons",
                    "color": "#D97706",
                    "items": [
                        {"ar": s["title_ar"], "en": s["title_en"]} for s in siblings
                    ] or [{"ar": ch["unit_title_ar"], "en": ch["unit_title_en"]}],
                },
            ],
        })
    return chapters
