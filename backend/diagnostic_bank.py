"""
Diagnostic Question Bank and Evaluation Engine for Fahim AI (فاهم).
Tests reading comprehension, vocabulary in context, and grammar foundations.
Calibrates student starting level and generates personalized 4-week learning roadmap.
"""

from typing import Dict, List, Any

DIAGNOSTIC_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "diag_q1",
        "competency": "reading",
        "competency_ar": "فهم المقروء",
        "competency_en": "Reading Comprehension",
        "difficulty": "medium",
        "passage_ar": "يُعَدُّ الصَّقْرُ رَمْزًا أَصِيلًا فِي دَوْلَةِ الْإِمَارَاتِ الْعَرَبِيَّةِ الْمُتَّحِدَةِ. يَمْتَازُ بِبَصَرِهِ الْحَادِّ وَسُرْعَتِهِ الْفَائِقَةِ فِي الصَّيْدِ، وَيَحْظَى بِمَكَانَةٍ رَفِيعَةٍ فِي التُّرَاثِ وَالثَّقَافَةِ الْوَطَنِيَّةِ.",
        "question_ar": "مَا هِيَ الصِّفَةُ الَّتِي تُمَيِّزُ الصَّقْرَ بِحَسَبِ النَّصِّ؟",
        "question_en": "What quality distinguishes the falcon according to the text?",
        "options": [
            {"id": 0, "text_ar": "لَوْنُهُ الْأَبْيَضُ النَّاصِعُ", "text_en": "His bright white color"},
            {"id": 1, "text_ar": "بَصَرُهُ الْحَادُّ وَسُرْعَتُهُ الْفَائِقَةُ", "text_en": "His sharp vision and extreme speed"},
            {"id": 2, "text_ar": "حُبُّهُ لِلسِّبَاحَةِ فِي مِيَاهِ الْبَحْرِ", "text_en": "His love for swimming in the sea"},
            {"id": 3, "text_ar": "نَوْمُهُ الطَّوِيلُ فِي وَضَحِ النَّهَارِ", "text_en": "His long sleep during daytime"}
        ],
        "correct_index": 1,
        "explanation_ar": "جاء في النص صراحةً: 'يمتاز ببصره الحاد وسرعته الفائقة في الصيد'.",
        "explanation_en": "The passage states explicitly that the falcon is characterized by sharp vision and great speed."
    },
    {
        "id": "diag_q2",
        "competency": "vocabulary",
        "competency_ar": "المفردات والسياق",
        "competency_en": "Vocabulary & Context",
        "difficulty": "medium",
        "passage_ar": None,
        "question_ar": "مَا مَعْنَى كَلِمَةِ «مَغْمُورًا» فِي جُمْلَةِ: «كَانَ الطَّالِبُ مَغْمُورًا بِالسَّعَادَةِ عِنْدَ اسْتِلَامِ جَائِزَتِهِ»؟",
        "question_en": "What is the meaning of the word 'مغموراً' in the sentence?",
        "options": [
            {"id": 0, "text_ar": "حَزِينًا وَمُتَرَدِّدًا", "text_en": "Sad and hesitant"},
            {"id": 1, "text_ar": "غَارِقًا وَمَمْلُوءًا بِالْفَرَحِ", "text_en": "Filled and overwhelmed with joy"},
            {"id": 2, "text_ar": "خَائِفًا وَمُضْطَرِبًا", "text_en": "Afraid and disturbed"},
            {"id": 3, "text_ar": "نَائِمًا فِي مَكَانِهِ", "text_en": "Asleep in his seat"}
        ],
        "correct_index": 1,
        "explanation_ar": "«مغموراً بالسعادة» تعبير مجازي يعني أن الفرح غطاه وملأ نفسه بالكامل.",
        "explanation_en": "'مغموراً بالسعادة' is a metaphor meaning overwhelmed or deeply filled with happiness."
    },
    {
        "id": "diag_q3",
        "competency": "grammar",
        "competency_ar": "القواعد والتراكيب",
        "competency_en": "Grammar & Structure",
        "difficulty": "easy",
        "passage_ar": None,
        "question_ar": "اخْتَرِ الْجُمْلَةَ الاسْمِيَّةَ الصَّحِيحَةَ نَحْوِيًّا (مُبْتَدَأٌ وَخَبَرٌ مَرْفُوعَانِ):",
        "question_en": "Select the grammatically correct nominal sentence (Subject & Predicate in Nominative):",
        "options": [
            {"id": 0, "text_ar": "اَلْأَشْجَارُ مُثْمِرَةٌ", "text_en": "Al-ashjaru muthmiratun (Nominative case)"},
            {"id": 1, "text_ar": "اَلْأَشْجَارَ مُثْمِرَةً", "text_en": "Al-ashjara muthmiratan (Accusative)"},
            {"id": 2, "text_ar": "اَلْأَشْجَارِ مُثْمِرٌ", "text_en": "Al-ashjari muthmirun (Genitive)"},
            {"id": 3, "text_ar": "اَلْأَشْجَارُ مُثْمِرٍ", "text_en": "Al-ashjaru muthmirin (Mismatched)"}
        ],
        "correct_index": 0,
        "explanation_ar": "المبتدأ والخبر كلاهما مرفوع بالضمة الظاهرة: 'الأشجارُ مثمرةٌ'.",
        "explanation_en": "Both the subject and predicate in a simple Arabic nominal sentence take the nominative case (Damma)."
    },
    {
        "id": "diag_q4",
        "competency": "reading",
        "competency_ar": "فهم المقروء",
        "competency_en": "Reading Comprehension",
        "difficulty": "medium",
        "passage_ar": "تُسْهِمُ الْقِرَاءَةُ الْيَوْمِيَّةُ فِي بِنَاءِ شَخْصِيَّةِ الطِّفْلِ؛ فَهِيَ تُوَسِّعُ آفَاقَهُ الْمَعْرِفِيَّةَ، وَتَمْنَحُهُ الْقُدْرَةَ عَلَى التَّعْبِيرِ عَنْ مَشَاعِرِهِ وَأَفْكَارِهِ بِوُضُوحٍ وَثِقَةٍ.",
        "question_ar": "مَا هِيَ الْفِكْرَةُ الرَّئِيسَةُ لِهَذِهِ الْفِقْرَةِ؟",
        "question_en": "What is the central idea of this paragraph?",
        "options": [
            {"id": 0, "text_ar": "أَهَمِّيَّةُ أَلْعَابِ الْحَاسُوبِ فِي وَقْتِ الْفَرَاغِ", "text_en": "The importance of computer games in leisure time"},
            {"id": 1, "text_ar": "دَوْرُ الْقِرَاءَةِ فِي تَنْمِيَةِ شَخْصِيَّةِ الطِّفْلِ وَتَعْبِيرِهِ", "text_en": "The role of reading in developing a child's character and expression"},
            {"id": 2, "text_ar": "تَارِيخُ طِبَاعَةِ الْكُتُبِ فِي الْعَالَمِ", "text_en": "The history of book printing in the world"},
            {"id": 3, "text_ar": "كَيْفِيَّةُ شِرَاءِ الْقِصَصِ الْمُصَوَّرَةِ", "text_en": "How to purchase illustrated storybooks"}
        ],
        "correct_index": 1,
        "explanation_ar": "الفقرة تتحدث بالكامل عن أثر القراءة اليومية الإيجابي على فكر الطفل وثقته في التعبير.",
        "explanation_en": "The passage centers on the vital impact of daily reading on expanding knowledge and self-expression."
    },
    {
        "id": "diag_q5",
        "competency": "vocabulary",
        "competency_ar": "المفردات والسياق",
        "competency_en": "Vocabulary & Context",
        "difficulty": "easy",
        "passage_ar": None,
        "question_ar": "مَا هُوَ ضِدُّ (عَكْسُ) كَلِمَةِ «الشَّجَاعَة»؟",
        "question_en": "What is the antonym (opposite) of 'الشجاعة' (Courage)?",
        "options": [
            {"id": 0, "text_ar": "اَلْجُبْنُ وَالْخَوْفُ", "text_en": "Cowardice and fear"},
            {"id": 1, "text_ar": "اَلْقُوَّةُ وَالْبَأْسُ", "text_en": "Strength and bravery"},
            {"id": 2, "text_ar": "اَلْكَرَمُ وَالْعَطَاءُ", "text_en": "Generosity and giving"},
            {"id": 3, "text_ar": "اَلصَّبْرُ وَالْأَنَاةُ", "text_en": "Patience and composure"}
        ],
        "correct_index": 0,
        "explanation_ar": "ضد الشجاعة والإقدام هو الجبن والخور.",
        "explanation_en": "The direct antonym of courage (الشجاعة) is cowardice (الجبن)."
    },
    {
        "id": "diag_q6",
        "competency": "grammar",
        "competency_ar": "القواعد والتراكيب",
        "competency_en": "Grammar & Structure",
        "difficulty": "hard",
        "passage_ar": None,
        "question_ar": "أَكْمِلِ الْفَرَاغَ بِالْفِعْلِ الْمُنَاسِبِ: «الطَّالِبَاتُ ________ فِي الْمُسَابَقَةِ الْوَطَنِيَّةِ بِجَدَارَةٍ.»",
        "question_en": "Complete the blank with the grammatically matched verb for feminine plural:",
        "options": [
            {"id": 0, "text_ar": "شَارَكُوا", "text_en": "Sharako (Masculine plural)"},
            {"id": 1, "text_ar": "شَارَكْنَ", "text_en": "Sharakna (Feminine plural with Noon an-Niswah)"},
            {"id": 2, "text_ar": "شَارَكَتَا", "text_en": "Sharakata (Feminine dual)"},
            {"id": 3, "text_ar": "يُشَارِكُ", "text_en": "Yushariku (Masculine singular)"}
        ],
        "correct_index": 1,
        "explanation_ar": "الفعل يتصل بنون النسوة عند الإسناد إلى جمع المؤنث الغائب: 'الطالباتُ شارَكْنَ'.",
        "explanation_en": "When a past verb refers to a feminine plural subject, it attaches Noon an-Niswah (شَارَكْنَ)."
    },
    {
        "id": "diag_q7",
        "competency": "vocabulary",
        "competency_ar": "المفردات والسياق",
        "competency_en": "Vocabulary & Context",
        "difficulty": "easy",
        "passage_ar": None,
        "question_ar": "مَا هُوَ جَمْعُ التَّكْسِيرِ الصَّحِيحُ لِكَلِمَةِ «قَلَم»؟",
        "question_en": "What is the correct broken plural for 'قلم' (pen)?",
        "options": [
            {"id": 0, "text_ar": "قَلَمُونَ", "text_en": "Qalamoona (Incorrect regular)"},
            {"id": 1, "text_ar": "قَلَمَاتٌ", "text_en": "Qalamat (Incorrect feminine)"},
            {"id": 2, "text_ar": "أَقْلَامٌ", "text_en": "Aqlam (Correct broken plural)"},
            {"id": 3, "text_ar": "قُلَمَاءُ", "text_en": "Qulamaa (Incorrect pattern)"}
        ],
        "correct_index": 2,
        "explanation_ar": "جمع قلم هو أقلام على وزن أفعال وهو جمع تكسير قياسي.",
        "explanation_en": "The correct broken plural form of Qalam is Aqlam (أقلام)."
    },
    {
        "id": "diag_q8",
        "competency": "grammar",
        "competency_ar": "القواعد والتراكيب",
        "competency_en": "Grammar & Structure",
        "difficulty": "easy",
        "passage_ar": None,
        "question_ar": "اخْتَرِ حَرْفَ الْجَرِّ الْمُنَاسِبَ لِإِكْمَالِ الْجُمْلَةِ: «انْطَلَقَ الْفَارِسُ سَرِيعًا ________ الْمَيْدَانِ.»",
        "question_en": "Select the correct preposition meaning towards / to:",
        "options": [
            {"id": 0, "text_ar": "عَلَى", "text_en": "On / upon"},
            {"id": 1, "text_ar": "إِلَى", "text_en": "To / towards (indicating destination)"},
            {"id": 2, "text_ar": "عَنْ", "text_en": "About / away from"},
            {"id": 3, "text_ar": "مِنْ أَجْلِ", "text_en": "For the sake of"}
        ],
        "correct_index": 1,
        "explanation_ar": "'إلى' حرف جر يفيد انتهاء الغاية المكانية (الذهاب إلى الميدان).",
        "explanation_en": "'إلى' (Ila) indicates destination or direction toward a place."
    }
]


def get_diagnostic_questions_for_student(grade: int = 5, stream: str = None) -> List[Dict[str, Any]]:
    """
    Returns the diagnostic question set without exposing the answer key or internal explanations.
    """
    safe_questions = []
    for q in DIAGNOSTIC_QUESTIONS:
        safe_q = {
            "id": q["id"],
            "competency": q["competency"],
            "competency_ar": q["competency_ar"],
            "competency_en": q["competency_en"],
            "difficulty": q["difficulty"],
            "passage_ar": q.get("passage_ar"),
            "question_ar": q["question_ar"],
            "question_en": q["question_en"],
            "options": q["options"]
        }
        safe_questions.append(safe_q)
    return safe_questions


def evaluate_diagnostic_submission(answers: Dict[str, int], grade: int = 5, stream: str = "MoE / CBSE Arabic (Non-Arabs)") -> Dict[str, Any]:
    """
    Server-side evaluation of diagnostic responses.
    Prevents client tampering, computes granular competency breakdowns,
    classifies starting tier, and crafts a 4-week tailored learning roadmap.
    """
    total_questions = len(DIAGNOSTIC_QUESTIONS)
    correct_count = 0

    competency_stats: Dict[str, Dict[str, Any]] = {
        "reading": {"name_ar": "فهم المقروء", "name_en": "Reading Comprehension", "total": 0, "correct": 0},
        "vocabulary": {"name_ar": "المفردات والسياق", "name_en": "Vocabulary & Context", "total": 0, "correct": 0},
        "grammar": {"name_ar": "القواعد والتراكيب", "name_en": "Grammar & Structure", "total": 0, "correct": 0}
    }

    item_evaluations = []

    for q in DIAGNOSTIC_QUESTIONS:
        qid = q["id"]
        comp = q["competency"]
        competency_stats[comp]["total"] += 1

        selected_ans = answers.get(qid)
        is_correct = (selected_ans is not None and selected_ans == q["correct_index"])

        if is_correct:
            correct_count += 1
            competency_stats[comp]["correct"] += 1

        item_evaluations.append({
            "question_id": qid,
            "competency": comp,
            "selected_option": selected_ans,
            "correct_option": q["correct_index"],
            "is_correct": is_correct,
            "explanation_ar": q["explanation_ar"],
            "explanation_en": q["explanation_en"]
        })

    # Overall percentage
    overall_score = round((correct_count / total_questions) * 100.0, 1) if total_questions > 0 else 0.0

    # Competency percentages
    competency_breakdown = {}
    strengths = []
    growth_areas = []

    for comp_key, stats in competency_stats.items():
        pct = round((stats["correct"] / stats["total"]) * 100.0, 1) if stats["total"] > 0 else 0.0
        competency_breakdown[comp_key] = {
            "name_ar": stats["name_ar"],
            "name_en": stats["name_en"],
            "correct": stats["correct"],
            "total": stats["total"],
            "percentage": pct
        }
        if pct >= 75.0:
            strengths.append(f"{stats['name_ar']} ({stats['name_en']})")
        else:
            growth_areas.append(f"{stats['name_ar']} ({stats['name_en']})")

    # Classification tier
    if overall_score >= 80.0:
        level_tier = "independent"
        level_title_ar = "المسار المستقل (متمكن)"
        level_title_en = "Independent Stream (Proficient)"
        level_summary_ar = "أداء متميز واستيعاب لغوي متين. تم تخصيص محتوى تفاعلي إثرائي يركز على التطبيقات المتقدمة والبلاغة والطلاقة اللغوية."
        level_summary_en = "Outstanding performance and solid linguistic foundation. Your curriculum is accelerated with enriched expressions and advanced comprehension."
    elif overall_score >= 50.0:
        level_tier = "guided"
        level_title_ar = "المسار الموجه (متوسط)"
        level_title_en = "Guided Stream (Intermediate)"
        level_summary_ar = "أساس لغوي جيد ومبشر. تم تصميم المسار لتعزيز القواعد والتراكيب ودعم الفهم القرائي مع تلميحات ومساعد فاهم الذكي."
        level_summary_en = "Good baseline with promising language skills. Your path focuses on strengthening syntax and vocabulary with Fahim's adaptive guidance."
    else:
        level_tier = "foundation"
        level_title_ar = "المسار التأسيسي (مبتدئ)"
        level_title_en = "Foundation Stream (Elementary)"
        level_summary_ar = "مسار داعم وتأسيسي يركز على بناء المفردات خطوة بخطوة، والتراكيب الجملية البسيطة مع نطق صوتي تفاعلي كامل."
        level_summary_en = "Supportive stepping-stone curriculum prioritizing vocabulary acquisition, essential sentence structures, and multi-sensory audio-visual cues."

    # Personalized 4-Week Milestone Roadmap
    milestones = [
        {
            "week": 1,
            "title_ar": "الأسبوع الأول: بناء الثقة والتأسيس اللغوي",
            "title_en": "Week 1: Confidence Building & Core Foundations",
            "focus_ar": "التعرف على المفردات المحورية وقراءة النصوص البسيطة مع المساعد الصوتي",
            "focus_en": "Key vocabulary acquisition, guided short reading passages with voice playback",
            "target_activities": ["ألعاب الكلمات التفاعلية", "استماع ونطق الحروف والكلمات", "اختبار قصير رقم 1"],
            "estimated_hours": 3.0
        },
        {
            "week": 2,
            "title_ar": "الأسبوع الثاني: التراكيب والجمل الاسمية والفعلية",
            "title_en": "Week 2: Sentence Dynamics & Syntax Mastery",
            "focus_ar": "التمييز بين الجملة الاسمية والفعلية ومطابقة الفعل والفاعل",
            "focus_en": "Nominal vs. verbal sentences, subject-verb agreement, and basic conjugations",
            "target_activities": ["تدريب المبتدأ والخبر", "تمرين ربط الجمل بالسياق", "تحدي السرعة اللغوية"],
            "estimated_hours": 3.5
        },
        {
            "week": 3,
            "title_ar": "الأسبوع الثالث: الفهم القرائي والاستنتاج السياقي",
            "title_en": "Week 3: Deep Comprehension & Contextual Deduction",
            "focus_ar": "تحليل النصوص التراثية والحديثة واستخراج المعاني والأضداد",
            "focus_en": "Analyzing cultural and modern texts, deducing synonyms, antonyms, and subtext",
            "target_activities": ["فهم مقروء تفاعلي (قصة الصقر)", "بنك الكلمات الذكي", "محاكاة أسئلة الوزارة"],
            "estimated_hours": 4.0
        },
        {
            "week": 4,
            "title_ar": "الأسبوع الرابع: التعبير والتقييم الختامي للشهر",
            "title_en": "Week 4: Applied Expression & Milestone Assessment",
            "focus_ar": "كتابة جمل متناسقة واجتياز التحدي الشهري لنيل وسام فاهم الذهبي",
            "focus_en": "Composing coherent Arabic paragraphs and mastering the end-of-milestone challenge",
            "target_activities": ["مختبر الكتابة التعبيرية", "اختبار التقييم الشهري الذكي", "فتح وسام التفوق التراثي"],
            "estimated_hours": 4.0
        }
    ]

    learning_plan = {
        "calibrated_level": level_tier,
        "level_title_ar": level_title_ar,
        "level_title_en": level_title_en,
        "level_summary_ar": level_summary_ar,
        "level_summary_en": level_summary_en,
        "overall_score": overall_score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "competency_breakdown": competency_breakdown,
        "strengths": strengths if strengths else ["استعداد عالٍ للتعلم والتطور"],
        "growth_areas": growth_areas if growth_areas else ["تعميق المهارات الإثرائية والبلاغة"],
        "recommended_grade": grade,
        "stream": stream,
        "recommended_first_chapter": "أَلْعَابُ الْكُرَةِ (Ball Games - Class 5 Chapter 1)",
        "milestones": milestones
    }

    return {
        "score": overall_score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "calibrated_level": level_tier,
        "level_title_ar": level_title_ar,
        "level_title_en": level_title_en,
        "competency_breakdown": competency_breakdown,
        "item_evaluations": item_evaluations,
        "learning_plan": learning_plan
    }
