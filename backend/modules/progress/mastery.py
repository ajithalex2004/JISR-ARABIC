"""Application operations; callers provide explicit database sessions and actors."""
import json
import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from backend.models import ChildProfile, ConceptMastery, GamificationProfile, SpacedReviewLog, LearnerAttempt, ExamSimulationResult
from backend.schemas import MasteryHeatmapResponse, ConceptMasteryItemSchema, GapReviewSessionResponse, GapReviewQuestion, RecordDrillAnswerRequest, RecordDrillAnswerResponse
from backend.errors import ApplicationError

CURRICULUM_CONCEPTS_REGISTRY = [
    ("vocab_sports", "المفردات والدلالة اللغوية", "Curriculum Vocabulary & Roots", "vocabulary"),
    ("reading_fluency", "الطلاقة وفهم المقروء", "Reading Fluency & Comprehension", "reading"),
    ("syntax_nominal", "الجملة الاسمية (المبتدأ والخبر)", "Nominal Sentence (Mubtada & Khabar)", "grammar"),
    ("conjugation_past", "تصريف الأفعال والضمائر", "Verb Conjugation & Tenses", "grammar"),
    ("ortho_taa_marbutah", "التاء المربوطة والهاء", "Taa Marbutah vs. Haa", "orthography"),
    ("plurals_sound", "جمع المذكر والمؤنث السالم", "Sound Plurals (Masculine & Feminine)", "grammar"),
    ("prepositions_jar", "حروف الجر والتراكيب", "Prepositions & Genitive Case", "grammar"),
    ("oral_pronunciation", "النطق السليم ومخارج الحروف", "Oral Articulation & Phonics", "speaking"),
]


def _get_status_and_color(pct: float, is_gap: bool, total_attempts: int = 1):
    if total_attempts == 0:
        return "Not Started", "لم يبدأ بعد", "#94a3b8"
    if is_gap or pct < 70.0:
        return "Knowledge Gap", "فجوة معرفية تحتاج مراجعة", "#dc2626"
    if pct >= 85.0:
        return "Mastered", "متقن بامتياز", "#064e3b"
    if pct >= 70.0:
        return "Proficient", "متمكن", "#059669"
    return "Developing", "قيد التطوير", "#d97706"


def get_mastery_heatmap(child_id: str, *, db: Session):
    """
    Returns real-time concept mastery percentages, color-coded heatmap data,
    and isolates persistent knowledge gaps derived strictly from verified events.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    items = db.query(ConceptMastery).filter(ConceptMastery.child_id == child.id).all()

    # Reset any legacy mock records that have total_attempts == 8 and no real attempts
    has_real_attempts = db.query(LearnerAttempt).filter(LearnerAttempt.child_id == child.id).first() is not None or \
                        db.query(ExamSimulationResult).filter(ExamSimulationResult.child_id == child.id).first() is not None

    if items and not has_real_attempts:
        legacy_mock = any(it.total_attempts == 8 for it in items)
        if legacy_mock:
            for it in items:
                it.mastery_percentage = 0.0
                it.total_attempts = 0
                it.correct_attempts = 0
                it.is_gap = False
                it.persistent_mistake_count = 0
                it.interval_days = 1
                it.ease_factor = 2.5
                it.repetition_count = 0
            db.commit()
            items = db.query(ConceptMastery).filter(ConceptMastery.child_id == child.id).all()

    if not items:
        # Check if child has completed diagnostic onboarding
        diagnostic_calibrated = {}
        if child.diagnostic_completed and child.diagnostic_details:
            try:
                diag = json.loads(child.diagnostic_details)
                if isinstance(diag, dict):
                    diagnostic_calibrated = diag
            except Exception:
                diagnostic_calibrated = {}

        for c_key, n_ar, n_en, cat in CURRICULUM_CONCEPTS_REGISTRY:
            pct = 0.0
            tot = 0
            corr = 0
            gap = False

            if diagnostic_calibrated:
                if cat == "reading" and "reading" in diagnostic_calibrated:
                    d_stat = diagnostic_calibrated["reading"]
                    tot = d_stat.get("total", 0)
                    corr = d_stat.get("correct", 0)
                    pct = d_stat.get("percentage", 0.0)
                    gap = (pct < 70.0 and tot > 0)
                elif cat == "vocabulary" and "vocabulary" in diagnostic_calibrated:
                    d_stat = diagnostic_calibrated["vocabulary"]
                    tot = d_stat.get("total", 0)
                    corr = d_stat.get("correct", 0)
                    pct = d_stat.get("percentage", 0.0)
                    gap = (pct < 70.0 and tot > 0)
                elif cat == "grammar" and "grammar" in diagnostic_calibrated:
                    d_stat = diagnostic_calibrated["grammar"]
                    tot = d_stat.get("total", 0)
                    corr = d_stat.get("correct", 0)
                    pct = d_stat.get("percentage", 0.0)
                    gap = (pct < 70.0 and tot > 0)

            cm = ConceptMastery(
                child_id=child.id,
                concept_key=c_key,
                concept_name_ar=n_ar,
                concept_name_en=n_en,
                category=cat,
                mastery_percentage=pct,
                total_attempts=tot,
                correct_attempts=corr,
                is_gap=gap,
                persistent_mistake_count=1 if gap else 0,
                interval_days=1,
                ease_factor=2.5,
                repetition_count=0
            )
            db.add(cm)
        db.commit()
        items = db.query(ConceptMastery).filter(ConceptMastery.child_id == child.id).all()

    by_cat: Dict[str, List[ConceptMasteryItemSchema]] = {}
    gaps: List[ConceptMasteryItemSchema] = []
    total_pct = 0.0
    active_attempts_count = 0

    for it in items:
        status_en, status_ar, color = _get_status_and_color(it.mastery_percentage, it.is_gap, it.total_attempts)
        schema_item = ConceptMasteryItemSchema(
            concept_key=it.concept_key,
            concept_name_ar=it.concept_name_ar,
            concept_name_en=it.concept_name_en,
            category=it.category,
            mastery_percentage=round(it.mastery_percentage, 1),
            total_attempts=it.total_attempts,
            correct_attempts=it.correct_attempts,
            is_gap=it.is_gap,
            persistent_mistake_count=it.persistent_mistake_count,
            status_label_en=status_en,
            status_label_ar=status_ar,
            color_hex=color,
            last_practiced_at=it.last_practiced_at.isoformat() if it.last_practiced_at else None,
            next_scheduled_review=it.next_scheduled_review.isoformat() if it.next_scheduled_review else None
        )
        total_pct += it.mastery_percentage
        if it.total_attempts > 0:
            active_attempts_count += 1

        if it.category not in by_cat:
            by_cat[it.category] = []
        by_cat[it.category].append(schema_item)

        if it.is_gap:
            gaps.append(schema_item)

    overall_pct = round(total_pct / len(items), 1) if items else 0.0

    return MasteryHeatmapResponse(
        child_id=child.id,
        child_name=child.name,
        grade=child.default_grade,
        overall_mastery_pct=overall_pct,
        total_concepts_tracked=len(items),
        active_gaps_count=len(gaps),
        concepts_by_category=by_cat,
        knowledge_gaps=gaps
    )


GAP_QUESTIONS_BANK = {
    "conjugation_past": [
        GapReviewQuestion(
            id="q_conj_01",
            concept_key="conjugation_past",
            concept_name_ar="تصريف الأفعال والضمائر",
            concept_name_en="Verb Conjugation & Tenses",
            prompt_ar="حَوِّلِ الْجُمْلَةَ: (اللَّاعِبُ رَكَضَ فِي الْمَلْعَبِ) إِلَى جَمْعِ الْمُذَكَّرِ:",
            prompt_en="Convert the sentence: 'The player ran in the field' to masculine plural:",
            options=[
                "اللَّاعِبُونَ رَكَضُوا فِي الْمَلْعَبِ",
                "اللَّاعِبُونَ رَكَضْنَ فِي الْمَلْعَبِ",
                "اللَّاعِبُونَ يَرْكُضُ فِي الْمَلْعَبِ",
                "اللَّاعِبُونَ رَكَضَا فِي الْمَلْعَبِ"
            ],
            correct_index=0,
            explanation_ar="مع جمع المذكر السالم للغائب (هم)، يتصل بالفعل واو الجماعة: ركضوا.",
            explanation_en="With masculine plural third-person (they), the verb attaches Waw of Plurality: ركضوا."
        ),
        GapReviewQuestion(
            id="q_conj_02",
            concept_key="conjugation_past",
            concept_name_ar="تصريف الأفعال والضمائر",
            concept_name_en="Verb Conjugation & Tenses",
            prompt_ar="اخْتَرِ التَّصْرِيفَ الصَّحِيحَ مَعَ ضَمِيرِ الْمُخَاطَبِ (أَنْتَ):",
            prompt_en="Choose the correct conjugation with second person (You - masc. singular):",
            options=[
                "أَنْتَ لَعِبْتَ بِالْكُرَةِ بِحَمَاسٍ",
                "أَنْتَ لَعِبْتِ بِالْكُرَةِ بِحَمَاسٍ",
                "أَنْتَ لَعِبْتُمْ بِالْكُرَةِ بِحَمَاسٍ",
                "أَنْتَ يَلْعَبُ بِالْكُرَةِ بِحَمَاسٍ"
            ],
            correct_index=0,
            explanation_ar="تاء الفاعل للمذكر المخاطب تكون مفتوحة: لَعِبْتَ.",
            explanation_en="The subject-Ta for masculine singular addressee takes Fatha: لَعِبْتَ."
        )
    ],
    "ortho_taa_marbutah": [
        GapReviewQuestion(
            id="q_ortho_01",
            concept_key="ortho_taa_marbutah",
            concept_name_ar="التاء المربوطة والهاء",
            concept_name_en="Taa Marbutah vs. Haa",
            prompt_ar="أَيُّ الْكَلِمَاتِ التَّالِيَةِ كُتِبَتْ فِيهَا (التَّاءُ الْمَرْبُوطَةُ) بِشَكْلٍ صَحِيحٍ؟",
            prompt_en="Which word correctly uses the Taa Marbutah (ة)?",
            options=[
                "مُبَارَاةٌ حَمَاسِيَّةٌ",
                "مُبَارَاه حَمَاسِيَّة",
                "مُبَارَات حَمَاسِيَّة",
                "مُبَارَاة حَمَاسِيَّه"
            ],
            correct_index=0,
            explanation_ar="تُنطق تاءً عند التنوين (مباراةٌ) وهاءً عند الوقف، لذلك تُكتب تاءً مربوطة بنقطتين.",
            explanation_en="Pronounced as 'T' with tanween (mubaaraatun) and 'H' on pause, thus requiring 2 dots."
        ),
        GapReviewQuestion(
            id="q_ortho_02",
            concept_key="ortho_taa_marbutah",
            concept_name_ar="التاء المربوطة والهاء",
            concept_name_en="Taa Marbutah vs. Haa",
            prompt_ar="اخْتَرِ الْكَلِمَةَ الَّتِي تَنْتَهِي بِـ (هَاءٍ أَصْلِيَّةٍ) دُونَ نُقَاطٍ:",
            prompt_en="Choose the word that ends in an authentic Haa (ه) without dots:",
            options=[
                "مِيَاه",
                "حَدِيقَة",
                "مَدْرَسَة",
                "كُرَة"
            ],
            correct_index=0,
            explanation_ar="كلمة (مياه) تنتهي بهاء أصلية تُنطق هاءً في الوقف والوصل (مياهٌ عذبة).",
            explanation_en="The word (مياه) ends in an authentic Haa pronounced as 'H' both on pause and in flow."
        )
    ],
    "syntax_nominal": [
        GapReviewQuestion(
            id="q_synt_01",
            concept_key="syntax_nominal",
            concept_name_ar="الجملة الاسمية (المبتدأ والخبر)",
            concept_name_en="Nominal Sentence (Mubtada & Khabar)",
            prompt_ar="حَدِّدِ المبتدأ والخبر في جملة: (العِلْمُ نُورٌ):",
            prompt_en="Identify the Mubtada and Khabar in: (Knowledge is light):",
            options=[
                "العلمُ: مبتدأ مرفوع، نورٌ: خبر مرفوع",
                "العلمُ: فاعل مرفوع، نورٌ: مفعول به",
                "العلمُ: خبر مقدم، نورٌ: مبتدأ مؤخر",
                "العلمُ: مضاف، نورٌ: مضاف إليه"
            ],
            correct_index=0,
            explanation_ar="الجملة الاسمية تبدأ بالمبتدأ المرفوع، ويتمم معناه الخبر المرفوع.",
            explanation_en="A nominal sentence begins with the nominative Mubtada, completed in meaning by the nominative Khabar."
        ),
        GapReviewQuestion(
            id="q_synt_02",
            concept_key="syntax_nominal",
            concept_name_ar="الجملة الاسمية (المبتدأ والخبر)",
            concept_name_en="Nominal Sentence (Mubtada & Khabar)",
            prompt_ar="اخْتَرِ الضَّبْطَ الصَّحِيحَ لأَوَاخِرِ الكَلِمَاتِ فِي الْجُمْلَةِ الاسْمِيَّةِ:",
            prompt_en="Choose the correct diacritical vowel endings for the nominal sentence:",
            options=[
                "السَّاحَةُ وَاسِعَةٌ",
                "السَّاحَةَ وَاسِعَةً",
                "السَّاحَةِ وَاسِعَةٍ",
                "السَّاحَةُ وَاسِعَةً"
            ],
            correct_index=0,
            explanation_ar="المبتدأ والخبر المفردان يرفعان بالضمة دائماً: الساحةُ واسعةٌ.",
            explanation_en="Both singular subject and predicate in a nominal sentence take Damma (nominative): الساحةُ واسعةٌ."
        )
    ],
    "vocab_sports": [
        GapReviewQuestion(
            id="q_voc_01",
            concept_key="vocab_sports",
            concept_name_ar="المفردات والدلالة اللغوية",
            concept_name_en="Curriculum Vocabulary & Roots",
            prompt_ar="مَا مَعْنَى كَلِمَةِ (مِضْمَار) فِي سِيَاقِ الرِّيَاضَةِ؟",
            prompt_en="What does the word (مِضْمَار - Midmar) mean in sports context?",
            options=[
                "مَيْدَانُ السِّبَاقِ وَالرَّكْضِ",
                "قَاعَةُ الطَّعَامِ",
                "شَبَكَةُ كُرَةِ الطَّائِرَةِ",
                "مَقَاعِدُ الْجُمْهُورِ"
            ],
            correct_index=0,
            explanation_ar="المضمار هو الميدان أو الحلبة المخصصة لسباقات الخيل أو الجري.",
            explanation_en="Midmar refers to the dedicated racetrack or course designated for horses or runners."
        ),
        GapReviewQuestion(
            id="q_voc_02",
            concept_key="vocab_sports",
            concept_name_ar="المفردات والدلالة اللغوية",
            concept_name_en="Curriculum Vocabulary & Roots",
            prompt_ar="مَا الجَذْرُ اللُّغَوِيُّ الثُّلَاثِيُّ لِكَلِمَةِ (مُبَارَاة)؟",
            prompt_en="What is the 3-letter linguistic root of the word (مباراة - Match)?",
            options=[
                "ب - ر - ي",
                "م - ب - ر",
                "ر - و - ي",
                "ب - و - ر"
            ],
            correct_index=0,
            explanation_ar="الجذر هو (ب ر ي) ومنه بارى يباري مباراة ومباراة تعني المنافسة.",
            explanation_en="The root is (ب-ر-ي), meaning to vie, contest, or compete."
        )
    ],
    "reading_fluency": [
        GapReviewQuestion(
            id="q_read_01",
            concept_key="reading_fluency",
            concept_name_ar="الطلاقة وفهم المقروء",
            concept_name_en="Reading Fluency & Comprehension",
            prompt_ar="أَيٌّ مِنَ الآتِي يُمَثِّلُ الفِكْرَةَ الرَّئِيسِيَّةَ لِدَرْسِ (أَلْعَابُ الكُرَةِ)؟",
            prompt_en="Which of the following represents the central theme of the 'Ball Games' lesson?",
            options=[
                "أَهَمِّيَّةُ الرِّيَاضَةِ لِلصِّحَّةِ وَتَعْزِيزِ التَّعَاوُنِ بَيْنَ النَّاسِ",
                "طَرِيقَةُ صِنَاعَةِ الكُرَاتِ الجِلْدِيَّةِ فَقَطْ",
                "تَارِيخُ قَوَانِينِ الكُرَةِ الطَّائِرَةِ دُونَ غَيْرِهَا",
                "تَفْضِيلُ مُشَاهَدَةِ التِّلْفَازِ عَلَى مُلَاعَبَةِ الزُّمَلَاءِ"
            ],
            correct_index=0,
            explanation_ar="الدرس يعلم أن ممارسة ألعاب الكرة تبني صحة الجسد وتنمي روح الفريق والتعاون والمحبة.",
            explanation_en="The lesson teaches that ball sports cultivate physical health, collaboration, and sportsmanship."
        )
    ],
    "plurals_sound": [
        GapReviewQuestion(
            id="q_plur_01",
            concept_key="plurals_sound",
            concept_name_ar="جمع المذكر والمؤنث السالم",
            concept_name_en="Sound Plurals (Masculine & Feminine)",
            prompt_ar="مَا جَمْعُ المُذَكَّرِ السَّالِمِ لِكَلِمَةِ (مُعَلِّم) فِي حَالَةِ الرَّفْعِ؟",
            prompt_en="What is the sound masculine plural of (معلم - Teacher) in nominative case?",
            options=[
                "مُعَلِّمُونَ",
                "مُعَلِّمِينَ",
                "مُعَلِّمَات",
                "عُلَمَاء"
            ],
            correct_index=0,
            explanation_ar="يُرفع جمع المذكر السالم بالواو والنون: معلمون.",
            explanation_en="The sound masculine plural takes Waw-and-Nun in nominative: معلمون."
        )
    ],
    "prepositions_jar": [
        GapReviewQuestion(
            id="q_prep_01",
            concept_key="prepositions_jar",
            concept_name_ar="حروف الجر والتراكيب",
            concept_name_en="Prepositions & Genitive Case",
            prompt_ar="اخْتَرِ الجُمْلَةَ الَّتِي تَحْوِي حَرْفَ جَرٍّ صَحِيحاً مَعَ ضَبْطِ الاسْمِ المَجْرُورِ:",
            prompt_en="Choose the sentence with correct preposition and genitive noun vowel:",
            options=[
                "ذَهَبَ التِّلْمِيذُ إِلَى المَدْرَسَةِ",
                "ذَهَبَ التِّلْمِيذُ إِلَى المَدْرَسَةُ",
                "ذَهَبَ التِّلْمِيذُ إِلَى المَدْرَسَةَ",
                "ذَهَبَ التِّلْمِيذُ عَلَى المَدْرَسَةُ"
            ],
            correct_index=0,
            explanation_ar="حرف الجر (إلى) يجر الاسم بعده بالكسرة: المدرسةِ.",
            explanation_en="The preposition (إلى) causes the subsequent noun to take Kasra: المدرسةِ."
        )
    ],
    "oral_pronunciation": [
        GapReviewQuestion(
            id="q_oral_01",
            concept_key="oral_pronunciation",
            concept_name_ar="النطق السليم ومخارج الحروف",
            concept_name_en="Oral Articulation & Phonics",
            prompt_ar="مَا المَخْرَجُ الصَّحِيحُ لِحَرْفِ (الثَّاءِ - ث) لِلتَّمْيِيزِ بَيْنَهُ وَبَيْنَ (السِّينِ - س)؟",
            prompt_en="What is the correct articulation point of (Thaa - ث) to distinguish from (Seen - س)?",
            options=[
                "إِخْرَاجُ طَرَفِ اللِّسَانِ مَعَ أَطْرَافِ الثَّنَايَا العُلْيَا",
                "إِبْقَاءُ اللِّسَانِ خَلْفَ الأَسْنَانِ السُّفْلَى",
                "ضَمُّ الشَّفَتَيْنِ مَعاً",
                "إِخْرَاجُ الصَّوْتِ مِنَ الحَلْقِ"
            ],
            correct_index=0,
            explanation_ar="حرف الثاء من الحروف اللثوية ويخرج بطرف اللسان بين الأسنان.",
            explanation_en="Thaa is an interdental sound articulated by placing the tongue tip at the edges of upper incisors."
        )
    ]
}


def get_gap_review_session(child_id: str, *, db: Session):
    """
    Automatically creates a personalized review session targeting the child's
    active knowledge gaps and due items using SM-2 spaced repetition methodology.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    now = datetime.datetime.now(datetime.UTC)

    # Check for active gaps OR items due for review (next_scheduled_review <= now)
    gaps = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.is_gap == True
    ).all()

    due_items = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.next_scheduled_review != None,
        ConceptMastery.next_scheduled_review <= now
    ).all()

    target_keys = set([g.concept_key for g in gaps] + [d.concept_key for d in due_items])

    selected_questions: List[GapReviewQuestion] = []
    if target_keys:
        for key in target_keys:
            if key in GAP_QUESTIONS_BANK:
                selected_questions.extend(GAP_QUESTIONS_BANK[key])
    else:
        # If no explicit gaps or due items, select from lowest mastery or general bank
        concepts_sorted = db.query(ConceptMastery).filter(
            ConceptMastery.child_id == child.id
        ).order_by(ConceptMastery.mastery_percentage.asc()).all()

        for c in concepts_sorted[:3]:
            if c.concept_key in GAP_QUESTIONS_BANK:
                selected_questions.extend(GAP_QUESTIONS_BANK[c.concept_key][:1])

        if not selected_questions:
            # Fallback to standard core bank
            for q_list in GAP_QUESTIONS_BANK.values():
                selected_questions.extend(q_list[:1])

    return GapReviewSessionResponse(
        child_id=child.id,
        session_title_ar="جلسة المعالجة وسد الفجوات المجدولة (SM-2)",
        session_title_en="Scheduled Spaced-Repetition Review (SM-2)",
        targeted_gaps_count=len(target_keys) if target_keys else 1,
        questions=selected_questions
    )


def record_drill_answer(req: RecordDrillAnswerRequest, *, db: Session):
    """
    Records an answer in the gap recovery drill using SM-2 spaced repetition,
    recalibrates mastery percentage, schedules next review date, and awards XP.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    session = get_gap_review_session(req.child_id, db=db)
    question = next((q for q in session.questions if q.id == req.question_id), None)
    if question is None or req.selected_index < 0 or req.selected_index >= len(question.options):
        raise ApplicationError(422, "Invalid drill question or answer")
    verified_correct = req.selected_index == question.correct_index

    cm = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.concept_key == req.concept_key
    ).first()

    if not cm:
        # Create on demand if not found
        cm = ConceptMastery(
            child_id=child.id,
            concept_key=req.concept_key,
            concept_name_ar="المهارة المستهدفة",
            concept_name_en=req.concept_key.replace("_", " ").title(),
            category="grammar",
            mastery_percentage=0.0,
            total_attempts=0,
            correct_attempts=0,
            is_gap=True,
            interval_days=1,
            ease_factor=2.5,
            repetition_count=0
        )
        db.add(cm)

    cm.total_attempts += 1

    # SM-2 Algorithm Implementation
    if cm.interval_days is None or cm.interval_days < 1:
        cm.interval_days = 1
    if cm.ease_factor is None or cm.ease_factor < 1.3:
        cm.ease_factor = 2.5
    if cm.repetition_count is None:
        cm.repetition_count = 0

    now = datetime.datetime.now(datetime.UTC)

    if verified_correct:
        cm.correct_attempts += 1
        cm.repetition_count += 1
        if cm.repetition_count == 1:
            cm.interval_days = 1
        elif cm.repetition_count == 2:
            cm.interval_days = 3
        else:
            cm.interval_days = max(1, int(round(cm.interval_days * cm.ease_factor)))
        cm.ease_factor = min(3.0, round(cm.ease_factor + 0.1, 2))
        attempt_pct = round((cm.correct_attempts / cm.total_attempts) * 100.0, 1)
        cm.mastery_percentage = min(100.0, max(round(cm.mastery_percentage + 6.0, 1), attempt_pct))

        if cm.mastery_percentage >= 75.0:
            cm.is_gap = False
            if cm.persistent_mistake_count > 0:
                cm.persistent_mistake_count -= 1

        xp_awarded = 25
        feedback_ar = f"ممتاز يا بطل! أتقنت المراجعة بنجاح. المراجعة القادمة مجدولة بعد {cm.interval_days} يوم."
        feedback_en = f"Excellent! You recalled correctly. Next review scheduled in {cm.interval_days} day(s)."
    else:
        cm.repetition_count = 0
        cm.interval_days = 1
        cm.ease_factor = max(1.3, round(cm.ease_factor - 0.2, 2))
        cm.mastery_percentage = round((cm.correct_attempts / cm.total_attempts) * 100.0, 1)
        cm.is_gap = True
        cm.persistent_mistake_count += 1
        xp_awarded = 5
        feedback_ar = "محاولة جيدة، ستتم إعادة جدولة المراجعة غداً لتثبيت القاعدة اللغوية."
        feedback_en = "Good effort. Review rescheduled for tomorrow to reinforce this rule."

    cm.last_practiced_at = now
    cm.next_scheduled_review = now + datetime.timedelta(days=cm.interval_days)

    # Persist in SpacedReviewLog
    review_log = SpacedReviewLog(
        child_id=child.id,
        concept_key=cm.concept_key,
        question_id=req.question_id,
        is_correct=verified_correct,
        interval_days=cm.interval_days,
        ease_factor=cm.ease_factor,
        repetition_count=cm.repetition_count,
        review_date=now
    )
    db.add(review_log)

    # Update Gamification Profile XP
    gp = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    if gp:
        gp.total_xp += xp_awarded
        gp.weekly_study_minutes += 5

    db.commit()

    return RecordDrillAnswerResponse(
        child_id=child.id,
        concept_key=cm.concept_key,
        new_mastery_pct=round(cm.mastery_percentage, 1),
        is_gap_resolved=(not cm.is_gap),
        xp_awarded=xp_awarded,
        feedback_ar=feedback_ar,
        feedback_en=feedback_en
    )
