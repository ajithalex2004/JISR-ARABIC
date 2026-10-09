"""
Smart Adaptive Assessment Engine (الاختبارات الذكية) — Assessment Bank
Features:
1. Bloom's Taxonomy Tagging: Recall (تذكر), Understanding (فهم), Application (تطبيق), Analysis (تحليل).
2. Flow-State Adaptive Engine: Scales difficulty up/down based on performance for all 10 curriculum lessons.
3. Official Exam Simulation (محاكاة نماذج الامتحانات الوزارية): Timed 20-min practice test matching UAE MoE 40/30/20/10 blueprint.
4. Detailed Solution Walkthroughs: In-depth rationale explaining why answers are correct or incorrect.
"""

from typing import List, Dict, Any
from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG

# Official UAE MoE Grade 5 Term 1 Exam Blueprint Bank (100 Marks Total)
# Weighting: 40% Reading Comprehension (40 pts) | 30% Grammar (30 pts) | 20% Vocabulary (20 pts) | 10% Orthography (10 pts)
ASSESSMENT_QUESTIONS: List[Dict[str, Any]] = [
    # =========================================================================
    # PART 1: READING COMPREHENSION — فهم المقروء (40% Weight / 40 Points)
    # =========================================================================
    {
        "id": "q_moe_comp_01",
        "category": "comprehension",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "كم عدد اللاعبين الأساسيين في فريق كرة القدم داخل الملعب؟",
        "question_en": "How many starting players are on a football team on the pitch?",
        "options": ["7 لاعبين", "9 لاعبين", "11 لاعباً", "15 لاعباً"],
        "options_en": ["7 players", "9 players", "11 players", "15 players"],
        "correct_index": 2,
        "solution_walkthrough_ar": "نص الكتاب الوزاري (ص 8) يحدد بوضوح أن فريق كرة القدم يتكون من 11 لاعباً أساسياً، أحدهم حارس المرمى.",
        "solution_walkthrough_en": "Official UAE textbook (p. 8) explicitly states that a football team fields 11 starting players, including the goalkeeper."
    },
    {
        "id": "q_moe_comp_02",
        "category": "comprehension",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "أين يُقام كأس دبي العالمي لركوب الخيل والفروسية سنوياً؟",
        "question_en": "Where is the annual Dubai World Cup for equestrian horse racing held?",
        "options": [
            "على مضمار ميدان في دبي",
            "في استاد هزاع بن زايد",
            "في حديقة خور دبي",
            "في الصالة الرياضية المغلقة"
        ],
        "options_en": [
            "At Meydan Racecourse in Dubai",
            "At Hazza bin Zayed Stadium",
            "At Dubai Creek Park",
            "In the indoor sports hall"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "يقام سباق كأس دبي العالمي للخيول على مضمار (ميدان) العالمي بدبي، وهو من أشهر مضامير الخيل عالمياً.",
        "solution_walkthrough_en": "The prestigious Dubai World Cup is hosted annually at the iconic Meydan Racecourse in Dubai."
    },
    {
        "id": "q_moe_comp_03",
        "category": "comprehension",
        "bloom_level": "analysis",
        "bloom_name_ar": "التحليل والاستنتاج",
        "bloom_name_en": "Analysis & Deduction",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "حلل العبارة: (الرماية والفروسية والصيد بالصقور من رياضات الآباء والأجداد في الإمارات). ما الدلالة التراثية لممارستها اليوم؟",
        "question_en": "Analyze the statement: (Archery, equestrianism, and falconry are heritage sports of UAE ancestors). What cultural significance does practicing them today hold?",
        "options": [
            "الاعتزاز بالهوية الوطنية والتراث الأصيل والشجاعة والصبر",
            "الاعتماد على التقنيات الحديثة فقط",
            "التخلي عن التقاليد القديمة للمجتمع",
            "قضاء أوقات الفراغ دون أي فائدة بدنية"
        ],
        "options_en": [
            "Pride in national identity, authentic heritage, valor, and patience",
            "Relying solely on modern technologies",
            "Abandoning old community traditions",
            "Spending leisure time without physical value"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "رياضات الأجداد تعكس الهوية الإماراتية العريقة، وتغرس في الأجيال خصال الصبر والشجاعة والانضباط.",
        "solution_walkthrough_en": "Heritage sports celebrate UAE national identity, cultivating valor, patience, and historical cultural pride."
    },
    {
        "id": "q_moe_comp_04",
        "category": "comprehension",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "ما الهدف الأسمى من ممارسة ألعاب الكرة والرياضات الجماعية كما يُستفاد من الدرس؟",
        "question_en": "What is the primary overarching goal of participating in team ball sports according to the curriculum?",
        "options": [
            "بناء اللياقة البدنية وتنمية روح التعاون والمحبة بين الزملاء",
            "الفوز بالجوائز المادية الفردية فقط",
            "إضاعة الوقت في اللعب دون دراسة",
            "الابتعاد عن العمل الجماعي والتنافس غير الرياضي"
        ],
        "options_en": [
            "Building physical fitness and nurturing collaboration, camaraderie, and team spirit",
            "Winning solo monetary prizes exclusively",
            "Wasting time playing instead of studying",
            "Avoiding teamwork and engaging in unsportsmanlike rivalry"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الرياضة الجماعية تبني الجسد السليم وتنمي روح التعاون والعمل كفريق متماسك يجمعهم الاحترام المتبادل.",
        "solution_walkthrough_en": "Team sports build a healthy physique while instilling collaboration, respect, and cohesive teamwork."
    },

    # =========================================================================
    # PART 2: GRAMMAR & SYNTACTIC STRUCTURES — القواعد والتراكيب (30% Weight / 30 Points)
    # =========================================================================
    {
        "id": "q_moe_gram_01",
        "category": "grammar",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "عيّن المبتدأ والخبر في جملة: (المَلْعَبُ فَسِيحٌ، وَالجُمْهُورُ مُتَحَمِّسٌ):",
        "question_en": "Identify the subject (Mubtada) and predicate (Khabar) in: (The playground is spacious, and the crowd is enthusiastic):",
        "options": [
            "الملعبُ: مبتدأ مرفوع، فسيحٌ: خبر مرفوع",
            "الملعبُ: فاعل مرفوع، فسيحٌ: مفعول به منصوب",
            "الملعبُ: اسم مجرور، فسيحٌ: حرف عطف",
            "الملعبُ: مضاف، فسيحٌ: مضاف إليه"
        ],
        "options_en": [
            "الملعبُ: nominative subject (Mubtada), فسيحٌ: nominative predicate (Khabar)",
            "الملعبُ: subject-agent (Fail), فسيحٌ: object (Mafool bih)",
            "الملعبُ: genitive noun, فسيحٌ: conjunction",
            "الملعبُ: annexing noun, فسيحٌ: annexed genitive"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الجملة الاسمية تبدأ بالمبتدأ المرفوع بالضمة (الملعبُ)، والخبر المتمم لمعناه هو (فسيحٌ).",
        "solution_walkthrough_en": "A nominal sentence opens with the nominative Mubtada (الملعبُ), and the Khabar (فسيحٌ) completes its core meaning."
    },
    {
        "id": "q_moe_gram_02",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "اختر الجملة التي تحقق المطابقة الإعرابية الصحيحة بين الفعل والفاعل المؤنث:",
        "question_en": "Select the sentence correctly matching verb conjugation with a feminine singular subject:",
        "options": [
            "تَرْكُضُ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ",
            "يَرْكُضُ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ",
            "رَكَضُوا مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ",
            "ارْكُضْ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ"
        ],
        "options_en": [
            "تَرْكُضُ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ (Tarkudu Maryamu - Correct)",
            "يَرْكُضُ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ (Yarkudu - Incorrect masc.)",
            "رَكَضُوا مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ (Rakadoo - Incorrect plural)",
            "ارْكُضْ مَرْيَمُ فِي المِضْمَارِ بِنَشَاطٍ (Urkud - Incorrect masc. imperative)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الفعل المضارع يبدأ بتاء المضارعة عند إسناده للفاعل المؤنث المفرد (تَرْكُضُ مريمُ).",
        "solution_walkthrough_en": "Present tense verbs begin with Ta of conjugation when the subject is feminine singular (ترْكُضُ مريمُ)."
    },
    {
        "id": "q_moe_gram_03",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "اختر الجملة التي ضُبط فيها الاسم المجرور بعد حرف الجر (فِي) ضبطاً إعرابياً صحيحاً:",
        "question_en": "Select the sentence where the genitive noun following preposition (فِي) has the correct case ending:",
        "options": [
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِي الرِّيَاضِيِّ",
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِيَ الرِّيَاضِيَّ",
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِيُ الرِّيَاضِيُّ",
            "تَدَرَّبَ الفَرِيقُ إِلَى النَّادِيُ الرِّيَاضِيُّ"
        ],
        "options_en": [
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِي الرِّيَاضِيِّ (Kasra genitive - Correct)",
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِيَ الرِّيَاضِيَّ (Fatha - Incorrect)",
            "تَدَرَّبَ الفَرِيقُ فِي النَّادِيُ الرِّيَاضِيُّ (Damma - Incorrect)",
            "تَدَرَّبَ الفَرِيقُ إِلَى النَّادِيُ الرِّيَاضِيُّ (Incorrect preposition & case)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "حرف الجر (في) يجر الاسم بعده، وعلامة جره الكسرة المقدرة على الياء للثقل، ونعته مجرور بالكسرة الظاهرة.",
        "solution_walkthrough_en": "Preposition (في) governs the genitive case (Majroor) with Kasra, and its adjective matches in genitive agreement."
    },

    # =========================================================================
    # PART 3: VOCABULARY & LINGUISTIC ROOTS — المفردات والجذور (20% Weight / 20 Points)
    # =========================================================================
    {
        "id": "q_moe_voc_01",
        "category": "vocabulary",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "ما اللقب الشهير الذي أُطلق على كرة القدم لجذبها الملايين حول العالم؟",
        "question_en": "What famous moniker was given to football for captivating billions worldwide?",
        "options": ["الساحرة المستديرة", "ملكة الألعاب", "الكرة الذهبية", "لعبة الميدان"],
        "options_en": ["The Round Witch (The Enchantress)", "Queen of Games", "The Golden Ball", "Game of the Pitch"],
        "correct_index": 0,
        "solution_walkthrough_ar": "لُقبت كرة القدم بـ (الساحرة المستديرة) لما تتمتع به من جاذبية وشعبية ساحرة في كافة القارات.",
        "solution_walkthrough_en": "Football was coined 'The Round Enchantress' (الساحرة المستديرة) for its magical captivation across the globe."
    },
    {
        "id": "q_moe_voc_02",
        "category": "vocabulary",
        "bloom_level": "analysis",
        "bloom_name_ar": "التحليل والاستنتاج",
        "bloom_name_en": "Analysis & Deduction",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "ما هو الجذر اللغوي الثلاثي الأصيل لكلمة (مُبَارَاة)؟",
        "question_en": "What is the fundamental triconsonantal Arabic root of the noun (مباراة - Match / Contest)?",
        "options": [
            "ب - ر - ي",
            "م - ب - ر",
            "ر - و - ي",
            "ب - و - ر"
        ],
        "options_en": [
            "B - R - Y (ب - ر - ي)",
            "M - B - R (م - ب - ر)",
            "R - W - Y (ر - و - ي)",
            "B - W - R (ب - و - ر)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الجذر الأصيل هو (ب ر ي)، ومنه بارى يباري مباراة، أي نافس وتحدى ونازل خصمه في اللعب.",
        "solution_walkthrough_en": "The root is (ب-ر-ي), giving rise to Baraya (to contend/vie) and Mubarah (contest/match)."
    },

    # =========================================================================
    # PART 4: ORTHOGRAPHY & MECHANICS — الإملاء والرسم الكتابي (10% Weight / 10 Points)
    # =========================================================================
    {
        "id": "q_moe_ortho_01",
        "category": "orthography",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "أي العبارات التالية كُتبت فيها (التاء المربوطة) و(الهاء) رسماً هجائياً سليماً؟",
        "question_en": "Which of the following phrases demonstrates correct orthography for Taa Marbutah (ة) and authentic Haa (ه)?",
        "options": [
            "مُبَارَاةٌ حَمَاسِيَّةٌ فِي مِيَاهِ البَحْرِ",
            "مُبَارَاه حَمَاسِيَّة فِي مِيَاهِ البَحْرِ",
            "مُبَارَات حَمَاسِيَّه فِي مِيَاهِ البَحْرِ",
            "مُبَارَاةٌ حَمَاسِيَّه فِي مِيَاة البَحْرِ"
        ],
        "options_en": [
            "مُبَارَاةٌ حَمَاسِيَّةٌ فِي مِيَاهِ البَحْرِ (All correct with dots/no-dots)",
            "مُبَارَاه حَمَاسِيَّة فِي مِيَاهِ البَحْرِ (Missing dots on mubarah)",
            "مُبَارَات حَمَاسِيَّه فِي مِيَاهِ البَحْرِ (Incorrect open taa)",
            "مُبَارَاةٌ حَمَاسِيَّه فِي مِيَاة البَحْرِ (Erroneous dots on authentic haa meeyah)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "(مباراة) و(حماسية) تنتهيان بتاء مربوطة بنقطتين لأنها تلفظ تاء عند التحريك. أما (مياه) فتنتهي بهاء أصلية دون نقاط لأنها تلفظ هاء وصلاً ووقفاً.",
        "solution_walkthrough_en": "(مباراة) and (حماسية) conclude in Taa Marbutah with two dots (pronounced T with vowels). (مياه) concludes in authentic root Haa with no dots."
    }
]

# Official UAE MoE Grade 5 Term 2 Exam Blueprint Bank (100 Marks Total)
# Units 3 & 4 (مدن عالمية & غرائب وعجائب)
# Weighting: 40% Reading Comprehension (40 pts) | 30% Grammar (30 pts) | 20% Vocabulary (20 pts) | 10% Orthography (10 pts)
ASSESSMENT_QUESTIONS_TERM2: List[Dict[str, Any]] = [
    # PART 1: READING COMPREHENSION (40 pts)
    {
        "id": "q_t2_comp_01",
        "category": "comprehension",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "ما هو النهر العظيم الذي قامت على ضفافه مدينة القاهرة القديمة؟",
        "question_en": "What great river does the ancient city of Cairo reside along?",
        "options": ["نهر النيل", "نهر الفرات", "نهر دجلة", "نهر الدانوب"],
        "options_en": ["Nile River", "Euphrates River", "Tigris River", "Danube River"],
        "correct_index": 0,
        "solution_walkthrough_ar": "نص درس (مدن عربية) يوضح أن القاهرة عاصمة مصر قامت على ضفاف نهر النيل الخالد.",
        "solution_walkthrough_en": "Textbook clarifies that Cairo, Egypt's capital, developed along the banks of the historic Nile River."
    },
    {
        "id": "q_t2_comp_02",
        "category": "comprehension",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "ما المعلم الشهير الذي يرتبط ببرج الساعة الشهير في العاصمة البريطانية لندن؟",
        "question_en": "Which landmark is associated with the famous clock tower in London?",
        "options": ["برج إيفل", "ساعة بيغ بن", "تمثال الحرية", "برج خليفة"],
        "options_en": ["Eiffel Tower", "Big Ben Clock", "Statue of Liberty", "Burj Khalifa"],
        "correct_index": 1,
        "solution_walkthrough_ar": "ساعة بيغ بن هي أشهر المعالم التاريخية في مدينة لندن وتقع عند قصر وستمنستر بجانب نهر التايمز.",
        "solution_walkthrough_en": "Big Ben is the most iconic clock tower and landmark of London beside the River Thames."
    },
    {
        "id": "q_t2_comp_03",
        "category": "comprehension",
        "bloom_level": "analysis",
        "bloom_name_ar": "التحليل والاستنتاج",
        "bloom_name_en": "Analysis & Deduction",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "علل: لماذا اعتبر القدماء الأهرامات والجنائن المعلقة من عجائب الدنيا السبع؟",
        "question_en": "Why did ancients categorize the Pyramids and Hanging Gardens as Wonders of the Ancient World?",
        "options": [
            "لدقة بنائها الهندسي الاستثنائي وعظمة إبداعها الحضاري",
            "لأنها بنيت في العصر الحديث باستخدام الآلات",
            "لأنها صغيرة الحجم ويسهل هدمها",
            "بسبب تشابهها التام مع باقي المباني العادية"
        ],
        "options_en": [
            "Due to extraordinary architectural precision and sublime civilizational genius",
            "Because they were constructed in modern times with machinery",
            "Because they are miniature in scale and easily demolished",
            "Due to complete resemblance to regular conventional structures"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "عجائب الدنيا سميت بذلك لما تتميز به من إعجاز معماري وهندسي فاق قدرات العصور القديمة وظل شاهداً على عظمة الإنسان.",
        "solution_walkthrough_en": "They are named Wonders due to unprecedented architectural genius surpassing the engineering limits of ancient civilizations."
    },
    {
        "id": "q_t2_comp_04",
        "category": "comprehension",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "كيف تستفيد الكائنات الحية كالحرباء من التخفي والتمويه في بيئتها الطبيعية؟",
        "question_en": "How do living creatures like chameleons utilize camouflage and mimicry in their natural habitat?",
        "options": [
            "للحماية من الحيوانات المفترسة وصيد الفرائس ببراعة",
            "للفت انتباه الصيادين إليها في الغابة",
            "للنوم في الأماكن المكشوفة دون أمان",
            "للهروب من الماء إلى اليابسة فقط"
        ],
        "options_en": [
            "For defense against predators and stealthily capturing prey",
            "To attract the attention of forest hunters",
            "To sleep in exposed hazardous open spaces",
            "Only to migrate from water to dry land"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "التمويه والتخفي والتلوّن من أهم وسائل التكيف البيئي التي تمنح الحيوان حماية من الأعداء وفرصة لاقتناص طعامه.",
        "solution_walkthrough_en": "Camouflage is a crucial ecological adaptation providing vital predator defense and hunting camouflage."
    },
    # PART 2: GRAMMAR (30 pts)
    {
        "id": "q_t2_gram_01",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "اختر اسم الإشارة المناسب للفراغ: (...... المُدُنُ زَاخِرَةٌ بِالتَّارِيخِ).",
        "question_en": "Choose the correct demonstrative pronoun: (...... cities are rich in history).",
        "options": ["هَذِهِ", "هَؤُلَاءِ", "هَذَا", "هَذَانِ"],
        "options_en": ["هَذِهِ (This - for non-human plural)", "هَؤُلَاءِ (These - for human plural only)", "هَذَا (This - singular masc)", "هَذَانِ (These two)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "جمع غير العاقل (مدن) يعامل معاملة المفردة المؤنثة فيشار إليه بـ (هذه)، ولا يصح استخدام (هؤلاء) لأنها لجمع العاقل.",
        "solution_walkthrough_en": "Non-human plurals in Arabic (like 'cities') take the feminine singular demonstrative (هذه)."
    },
    {
        "id": "q_t2_gram_02",
        "category": "grammar",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "ما المعنى الذي يفيده حرف العطف (ثُمَّ) في الجملة: (زُرْتُ لَنْدَنَ ثُمَّ بَارِيسَ)؟",
        "question_en": "What meaning does the conjunction (ثُمَّ) convey in the sentence: (I visited London, then Paris)?",
        "options": [
            "الترتيب مع التراخي والمهلة الزمنية",
            "الترتيب والسرعة مع التعقيب المباشر",
            "الشك والاختيار بين أمرين",
            "الجمع والمشاركة دون ترتيب"
        ],
        "options_en": [
            "Sequence with a time delay / leisurely interval (ثم)",
            "Immediate rapid sequence without delay (الفاء)",
            "Doubt or choice (أو)",
            "Simple partnership without sequence (الواو)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "(ثم) حرف عطف يفيد الترتيب مع التراخي (أي وجود مهلة وفترة زمنية بين وقوع الفعلين).",
        "solution_walkthrough_en": "(ثم) expresses sequential ordering accompanied by a temporal gap or relaxed interval."
    },
    {
        "id": "q_t2_gram_03",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "صغ اسم تفضيل صحيحاً على وزن (أَفْعَل) للمقارنة في الجملة: (بُرْجُ خَلِيفَةَ ...... مِنْ بُرْجِ إِيفِل).",
        "question_en": "Form the correct superlative/comparative on the pattern (أَفْعَل): (Burj Khalifa is ...... than Eiffel Tower).",
        "options": ["أَعْلَى", "عَالِي", "طَوِيل", "مُرْتَفِع"],
        "options_en": ["أَعْلَى (Higher/Taller - pattern أفعل)", "عَالِي (High - active participle)", "طَوِيل (Tall - adjective)", "مُرْتَفِع (Elevated)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "اسم التفضيل يصاغ من الفعل الثلاثي على وزن (أَفْعَل) للدلالة على المفاضلة: (أعلى).",
        "solution_walkthrough_en": "The Arabic comparative adjective is derived on the measure (أَفْعَل), yielding (أَعْلَى) for taller/higher."
    },
    # PART 3: VOCABULARY & ROOTS (20 pts)
    {
        "id": "q_t2_voc_01",
        "category": "vocabulary",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "ما معنى كلمة (عَرَاقَةٌ) في قولنا: (تَمْتَازُ دِمَشْقُ بِعَرَاقَتِهَا)؟",
        "question_en": "What is the meaning of the word (عَرَاقَة) in: (Damascus is characterized by its ancient nobility)?",
        "options": ["أَصَالَةٌ وَقِدَمٌ تَارِيخِيٌّ عَظِيمٌ", "حَدَاثَةٌ وَتَصْنِيعٌ مُعَاصِرٌ", "صِغَرُ المِسَاحَةِ", "قِلَّةُ السُّكَّانِ"],
        "options_en": ["Ancient historical authenticity & nobility", "Modern industrial novelty", "Small area", "Low population"],
        "correct_index": 0,
        "solution_walkthrough_ar": "العراقة تعني القدم التاريخي المتجذر والأصالة الراسخة عبر القرون.",
        "solution_walkthrough_en": "العراقة signifies profound historical antiquity, heritage roots, and noble longevity."
    },
    {
        "id": "q_t2_voc_02",
        "category": "vocabulary",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "ما الجذر اللغوي الثلاثي لكلمة (مُسْتَكْشِفُونَ)؟",
        "question_en": "What is the three-letter triconsonantal Arabic root of the word (مُسْتَكْشِفُونَ - Explorers)?",
        "options": ["ك-ش-ف", "س-ك-ف", "ش-ف-ن", "م-ك-ش"],
        "options_en": ["ك-ش-ف (K-Sh-F)", "س-ك-ف (S-K-F)", "ش-ف-ن (Sh-F-N)", "م-ك-ش (M-K-Sh)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "جذر الكلمة هو الفعل المجرد (كَشَفَ)، وحروف الزيادة هي الميم والسين والتاء والواو والنون.",
        "solution_walkthrough_en": "The base trilateral root is (ك-ش-ف meaning to reveal or discover), with standard morphological prefixes."
    },
    # PART 4: ORTHOGRAPHY (10 pts)
    {
        "id": "q_t2_ortho_01",
        "category": "orthography",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "أي الجمل التالية كُتب فيها الفعل المتصل بـ (واو الجماعة) وألف التفريق كتابة إملائية صحيحة؟",
        "question_en": "Which sentence demonstrates the correct spelling of a verb suffixed with plural waw and distinguishing alif (ألف التفريق)?",
        "options": [
            "السُّيَّاحُ شَاهَدُوا الآثَارَ العَجِيبَةَ فِي القَاهِرَةِ.",
            "السُّيَّاحُ شَاهَدُو الآثَارَ العَجِيبَةَ فِي القَاهِرَةِ.",
            "السُّيَّاحُ شَاهَدُوَاْ الآثَارَ العَجِيبَةَ فِي القَاهِرَةِ.",
            "السُّيَّاحُ شَاهَدْنَ الآثَارَ العَجِيبَةَ فِي القَاهِرَةِ."
        ],
        "options_en": [
            "السُّيَّاحُ شَاهَدُوا (Correct with terminal distinguishing alif)",
            "السُّيَّاحُ شَاهَدُو (Incorrect: missing distinguishing alif)",
            "السُّيَّاحُ شَاهَدُوَاْ (Erroneous extra alif vowel)",
            "السُّيَّاحُ شَاهَدْنَ (Feminine nun instead of plural waw)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "تزاد ألف التفريق بعد واو الجماعة في الأفعال الماضية والمضارعة المجزومة للتفريق بينها وبين واو العلة أو واو جمع المذكر السالم: (شَاهَدُوا).",
        "solution_walkthrough_en": "Distinguishing Alif (ألف التفريق) is mandatory after verb plural waw (واو الجماعة) to distinguish it from root radical waw."
    }
]

# Official UAE MoE Grade 5 Term 3 Exam Blueprint Bank (100 Marks Total)
# Units 5 & 6 (التواصل & كلنا أذكياء)
# Weighting: 40% Reading Comprehension (40 pts) | 30% Grammar (30 pts) | 20% Vocabulary (20 pts) | 10% Orthography (10 pts)
ASSESSMENT_QUESTIONS_TERM3: List[Dict[str, Any]] = [
    # PART 1: READING COMPREHENSION (40 pts)
    {
        "id": "q_t3_comp_01",
        "category": "comprehension",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "ما الميزة الفطرية الفريدة التي جعلت الحمام الزاجل رسولاً موثوقاً في نقل الرسائل قديماً؟",
        "question_en": "What unique innate ability made carrier pigeons reliable message couriers throughout history?",
        "options": [
            "قدرته الفائقة على معرفة طريق العودة إلى موطنه دائماً مهما بَعُد",
            "سرعته التي تفوق سرعة الطائرات الحديثة",
            "قدرته على قراءة الكلمات والرسائل المكتوبة",
            "عدم حاجته إلى الطعام والشراب أبداً"
        ],
        "options_en": [
            "Homing instinct to unerringly navigate back to its home loft across vast distances",
            "Flight speed that exceeds modern airplanes",
            "Ability to read handwritten messages",
            "Never needing food or water"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الحمام الزاجل يتميز بغريزة العودة إلى موطنه الأصلي بدقة مذهلة بالاعتماد على المجال المغناطيسي للأرض وموقع الشمس.",
        "solution_walkthrough_en": "Carrier pigeons possess a remarkable homing instinct, navigating unerringly back to their origin roost using geomagnetic cues."
    },
    {
        "id": "q_t3_comp_02",
        "category": "comprehension",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "كيف تسهم وسائل الإعلام الحديثة في ربط المجتمعات ونشر المعرفة؟",
        "question_en": "How do modern media outlets foster community connectivity and disseminate knowledge?",
        "options": [
            "بنقل الأخبار والبرامج التثقيفية فور وقوعها إلى مختلف أنحاء العالم",
            "بنشر الشائعات دون التحقق من مصادرها",
            "بعزل الأفراد عن مجتمعاتهم ومحيطهم الأسري",
            "بتقليل تبادل المعلومات بين الشعوب"
        ],
        "options_en": [
            "By transmitting breaking news and educational programming instantly across the globe",
            "By circulating unverified rumors without authentic sources",
            "By isolating individuals from family and community life",
            "By curtailing information exchange between peoples"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الإعلام الهادف جسر ثقافي وحضاري ينقل المعرفة الإنسانية لحظة بلحظة ويوثق الترابط الاجتماعي.",
        "solution_walkthrough_en": "Purposeful media acts as a bridge for instant global knowledge exchange and constructive civic awareness."
    },
    {
        "id": "q_t3_comp_03",
        "category": "comprehension",
        "bloom_level": "analysis",
        "bloom_name_ar": "التحليل والاستنتاج",
        "bloom_name_en": "Analysis & Deduction",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "قارن بين ذكاء الحيوان القائم على الغريزة والذكاء البشري القائم على التفكير والابتكار:",
        "question_en": "Compare instinct-based animal intelligence with human intelligence rooted in cognition and innovation:",
        "options": [
            "الحيوان يتصرف بالغريزة لحفظ البقاء بينما الإنسان يبتكر حلولاً ويبني الحضارات",
            "الحيوان يمتلك قدرة على اختراع الآلات المعقدة دون تدريب",
            "الإنسان يعتمد على الغريزة فقط دون تفكير أو تخطيط",
            "لا يوجد أي فرق بين سلوك الكائنات الحية والإنسان"
        ],
        "options_en": [
            "Animals act on survival instincts while humans innovate solutions, reason, and build civilizations",
            "Animals possess the capability to invent complex machinery spontaneously",
            "Humans rely purely on instinct without cognition or planning",
            "There is no discernible distinction between animal and human behavior"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "ذكاء الحيوان موجه بالفطرة والغريزة لتأمين البقاء، في حين كرم الله الإنسان بالعقل القادر على التجريد والابتكار وبناء المستقبل.",
        "solution_walkthrough_en": "Animal intelligence operates through innate survival mechanisms, whereas human intelligence creates abstract tools and civilization."
    },
    {
        "id": "q_t3_comp_04",
        "category": "comprehension",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "تعد مدينة مصدر في أبوظبي نموذجاً للمدن الذكية المستدامة لأنها:",
        "question_en": "Masdar City in Abu Dhabi represents a pioneering model for sustainable smart cities because it:",
        "options": [
            "تعتمد على الطاقة الشمسية النظيفة والنقل الذكي الخالي من الانبعاثات الكربونية",
            "تعتمد بالكامل على الوقود الأحفوري التقليدي فقط",
            "تمنع استخدام التكنولوجيا الحديثة وحواسيب الذكاء الاصطناعي",
            "تستهلك كميات هائلة من الطاقة غير المتجددة"
        ],
        "options_en": [
            "Relies on clean solar power, sustainable transport, and zero carbon emissions",
            "Relies exclusively on conventional fossil fuels",
            "Prohibits modern technology and artificial intelligence systems",
            "Consumes vast amounts of non-renewable energy"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "مدينة مصدر في أبوظبي هي أول مدينة مستدامة في الشرق الأوسط تعتمد على الطاقة الشمسية وإعادة التدوير والنقل الذكي.",
        "solution_walkthrough_en": "Masdar City is a pioneering zero-carbon eco-city powered by clean solar energy and rapid automated transport."
    },
    # PART 2: GRAMMAR (30 pts)
    {
        "id": "q_t3_gram_01",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "عيّن المفعول المطلق في الجملة الآتية: (انْطَلَقَتِ المَرْكَبَةُ الذَّكِيَّةُ انْطِلاقاً سَرِيعاً).",
        "question_en": "Identify the absolute object (المفعول المطلق) in the sentence: (The smart vehicle accelerated rapidly).",
        "options": ["انْطِلاقاً", "المَرْكَبَةُ", "الذَّكِيَّةُ", "سَرِيعاً"],
        "options_en": ["انْطِلاقاً (Absolute object - verbal noun derived from verb)", "المَرْكَبَةُ (Subject - Fa'il)", "الذَّكِيَّةُ (Adjective - Na'at)", "سَرِيعاً (Adverbial attribute)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "المفعول المطلق اسم منصوب مشتق من لفظ الفعل لتأكيده أو بيان نوعه: (انْطَلَقَ ... انْطِلاقاً).",
        "solution_walkthrough_en": "The cognate accusative (المفعول المطلق) is an accusative masdar derived from the same root as the verb: (انطلاقاً)."
    },
    {
        "id": "q_t3_gram_02",
        "category": "grammar",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "hard",
        "points": 10,
        "question_ar": "ما هو الأثر الإعرابي لفعل ناسخ من أخوات كان عند دخوله على الجملة الاسمية: (صَارَ الجَوُّ مُمْطِراً)؟",
        "question_en": "What is the syntactic case-marking effect of 'Kaan and its sisters' upon entering an equational nominal sentence?",
        "options": [
            "يرفع المبتدأ ويسمى اسمه، وينصب الخبر ويسمى خبره",
            "ينصب المبتدأ ويسمى اسمه، ويرفع الخبر ويسمى خبره",
            "يرفع المبتدأ والخبر معاً بالضمة",
            "يجزم الفعل والمفعول به بالسكون"
        ],
        "options_en": [
            "Elevates the subject in nominative (Marfoo'), and puts the predicate in accusative (Mansoub)",
            "Sets subject to accusative and predicate to nominative (Inna rule)",
            "Leaves both subject and predicate in nominative",
            "Jussives both parts with sukoon"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "كان وأخواتها أفعال ناسخة تدخل على المبتدأ والخبر فترفع الأول اسماً لها وتنصب الثاني خبراً لها.",
        "solution_walkthrough_en": "Kaan and its sisters are defective verbs that keep the subject nominative (ism kaan) and render the predicate accusative (khabar kaan)."
    },
    {
        "id": "q_t3_gram_03",
        "category": "grammar",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "اضبط بالشكل التام اسم (إنَّ) وخبرها في جملة: (إِنَّ العِلْمَ نُورٌ).",
        "question_en": "Apply the correct vowel diacritics to Ism Inna and Khabar Inna in: (إِنَّ العِلْمَ نُورٌ).",
        "options": [
            "العِلْمَ (منصوب بالفتحة) وَ نُورٌ (مرفوع بالضمة)",
            "العِلْمُ (مرفوع بالضمة) وَ نُوراً (منصوب بالفتحة)",
            "العِلْمِ (مجرور بالكسرة) وَ نُورٍ (مجرور بالكسرة)",
            "العِلْمُ (مرفوع) وَ نُورٌ (مرفوع)"
        ],
        "options_en": [
            "العِلْمَ (accusative fatha) and نُورٌ (nominative damma)",
            "العِلْمُ (nominative damma) and نُوراً (accusative fatha)",
            "العِلْمِ (genitive) and نُورٍ (genitive)",
            "العِلْمُ and نُورٌ (both nominative)"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "(إنّ) حرف ناسخ ينصب المبتدأ اسماً له (العلمَ بالفتحة) ويرفع الخبر خبراً له (نورٌ بالضمة).",
        "solution_walkthrough_en": "(Inna) is a particle that governs the subject in the accusative (Al-'Ilma) and the predicate in the nominative (Noorun)."
    },
    # PART 3: VOCABULARY & ROOTS (20 pts)
    {
        "id": "q_t3_voc_01",
        "category": "vocabulary",
        "bloom_level": "understanding",
        "bloom_name_ar": "الفهم والاستيعاب",
        "bloom_name_en": "Understanding & Comprehension",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "ما معنى كلمة (الاسْتِدَامَة) في سياق المشاريع البيئية والمدن الذكية؟",
        "question_en": "What is the meaning of the word (الاسْتِدَامَة - Sustainability) in smart environmental cities?",
        "options": [
            "الحفاظ على الموارد الطبيعية وحمايتها للأجيال القادمة",
            "استنزاف واستهلاك جميع الموارد بسرعة",
            "التوقف عن البناء والتطور الحضاري",
            "زيادة التلوث وانبعاثات الغازات الضارة"
        ],
        "options_en": [
            "Preserving natural resources responsibly for future generations",
            "Rapidly depleting and exhausting all resources",
            "Halting all architectural and civilizational growth",
            "Increasing pollution and harmful gas emissions"
        ],
        "correct_index": 0,
        "solution_walkthrough_ar": "الاستدامة تعني تلبية احتياجات الحاضر دون المساس بقدرة الأجيال المستقبلية على تلبية احتياجاتها البيئية والمعيشية.",
        "solution_walkthrough_en": "Sustainability signifies meeting present requirements without compromising the resources of future generations."
    },
    {
        "id": "q_t3_voc_02",
        "category": "vocabulary",
        "bloom_level": "recall",
        "bloom_name_ar": "التذكر والاسترجاع",
        "bloom_name_en": "Recall & Retrieval",
        "difficulty": "easy",
        "points": 10,
        "question_ar": "ما الجذر اللغوي للكلمات الآتية: (تَوَاصُل - مُوَاصَلَة - اتِّصَال)؟",
        "question_en": "What is the common trilateral root for (تَوَاصُل - مُوَاصَلَة - اتِّصَال)?",
        "options": ["و-ص-ل", "ص-ل-ي", "ت-و-ص", "ص-و-ل"],
        "options_en": ["و-ص-ل (W-S-L)", "ص-ل-ي (S-L-Y)", "ت-و-ص (T-W-S)", "ص-و-ل (S-W-L)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "جميع هذه الكلمات تشترك في المعنى الدلالي وترجع إلى الأصل الثلاثي المجرد (وَصَلَ).",
        "solution_walkthrough_en": "All these morphological derivations share the semantic root of connection (و-ص-ل: Wasala)."
    },
    # PART 4: ORTHOGRAPHY (10 pts)
    {
        "id": "q_t3_ortho_01",
        "category": "orthography",
        "bloom_level": "application",
        "bloom_name_ar": "التطبيق",
        "bloom_name_en": "Application",
        "difficulty": "medium",
        "points": 10,
        "question_ar": "أي الكلمات الآتية تبدأ بـ (همزة وصل) ترسم ألفاً مجردة من الهمزة؟",
        "question_en": "Which of the following words begins with Hamzat Wasl (همزة وصل) rendered as bare Alif without glottal mark?",
        "options": ["ابْتِكَار", "إِرْسَال", "أَخْبَار", "أُعْلُومَة"],
        "options_en": ["ابْتِكَار (Hamzat Wasl - 5-letter infinitive)", "إِرْسَال (Hamzat Qat' - 4-letter infinitive)", "أَخْبَار (Hamzat Qat' - noun)", "أُعْلُومَة (Hamzat Qat' - noun)"],
        "correct_index": 0,
        "solution_walkthrough_ar": "مصدر الفعل الخماسي (ابتكر - ابتكار) يبدأ بهمزة وصل تسقط في درج الكلام وتنطق عند الابتداء دون رسم الهمزة.",
        "solution_walkthrough_en": "The verbal noun of form VIII (quinqueliteral verb: ابتكر -> ابتكار) begins with Hamzat Wasl without diacritic."
    }
]


def get_official_exam_simulation(grade: int = 5, term: int = 1, questions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns a standardized 20-minute UAE Ministry of Education (MoE) practice exam.
    Calibrated to 10 questions and 100 marks total matching the 40/30/20/10 blueprint:
    - 40% Reading Comprehension (40 pts)
    - 30% Grammar & Syntactic Structures (30 pts)
    - 20% Vocabulary & Roots (20 pts)
    - 10% Orthography & Mechanics (10 pts)
    """
    if questions is not None:
        question_pool = questions
    elif grade == 5 and term == 2:
        question_pool = ASSESSMENT_QUESTIONS_TERM2
    elif grade == 5 and term == 3:
        question_pool = ASSESSMENT_QUESTIONS_TERM3
    else:
        question_pool = ASSESSMENT_QUESTIONS
    exam_questions = []


    for q in question_pool:
        bloom_level = q.get("bloom_level", "understanding")
        safe_q = {
            "id": q["id"],
            "category": q.get("category", "comprehension"),
            "bloom_level": bloom_level,
            "bloom_name_ar": q.get("bloom_name_ar", "الفهم والاستيعاب"),
            "bloom_name_en": q.get("bloom_name_en", "Understanding & Comprehension"),
            "difficulty": q.get("difficulty", "medium"),
            "points": q.get("points", 10),
            "question_ar": q.get("question_ar", q.get("prompt_ar", "")),
            "question_en": q.get("question_en", q.get("prompt_en", "")),
            "options": q.get("options", []),
            "options_en": q.get("options_en", [])
        }
        exam_questions.append(safe_q)

    return {
        "exam_title_ar": f"محاكاة الاختبار الوزاري الموحد — الصف {grade} الفصل {term}",
        "exam_title_en": f"Official MoE Exam Simulation — Grade {grade} Term {term}",
        "time_limit_minutes": 20,
        "time_limit_seconds": 1200,
        "blueprint_spec": {
            "reading_comprehension": "40%",
            "grammar_and_syntax": "30%",
            "vocabulary_and_roots": "20%",
            "orthography_and_writing": "10%"
        },
        "total_questions": len(exam_questions),
        "total_marks": sum(q["points"] for q in exam_questions),
        "curriculum": f"Grade {grade} Arabic Curriculum · Term {term} (Official MoE Specification)",
        "questions": exam_questions
    }


def evaluate_exam_submission(answers: Dict[str, int], questions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates exam simulation submission server-side against pinned keys.
    Computes Bloom's Taxonomy mastery radar, blueprint coverage, and full solution walkthrough.
    """
    correct_count = 0
    total_points = 0
    earned_points = 0
    question_bank = questions if questions is not None else ASSESSMENT_QUESTIONS
    total_questions = len(question_bank)

    bloom_stats: Dict[str, Dict[str, Any]] = {
        "recall": {"name_ar": "التذكر", "name_en": "Recall", "total": 0, "correct": 0, "percentage": 0.0},
        "understanding": {"name_ar": "الفهم", "name_en": "Understanding", "total": 0, "correct": 0, "percentage": 0.0},
        "application": {"name_ar": "التطبيق", "name_en": "Application", "total": 0, "correct": 0, "percentage": 0.0},
        "analysis": {"name_ar": "التحليل", "name_en": "Analysis", "total": 0, "correct": 0, "percentage": 0.0}
    }

    category_stats: Dict[str, Dict[str, Any]] = {
        "comprehension": {"name_ar": "فهم المقروء", "name_en": "Comprehension", "total": 0, "correct": 0, "percentage": 0.0},
        "grammar": {"name_ar": "القواعد والتراكيب", "name_en": "Grammar", "total": 0, "correct": 0, "percentage": 0.0},
        "vocabulary": {"name_ar": "المفردات والدلالة", "name_en": "Vocabulary", "total": 0, "correct": 0, "percentage": 0.0},
        "orthography": {"name_ar": "الإملاء والكتابة", "name_en": "Orthography", "total": 0, "correct": 0, "percentage": 0.0}
    }

    detailed_walkthrough = []

    for q in question_bank:
        qid = q["id"]
        bloom = q.get("bloom_level", "understanding")
        cat = q.get("category", "comprehension")
        pts = q.get("points", 10)
        total_points += pts

        if bloom not in bloom_stats:
            bloom_stats[bloom] = {"name_ar": bloom, "name_en": bloom.capitalize(), "total": 0, "correct": 0, "percentage": 0.0}
        bloom_stats[bloom]["total"] += 1

        if cat not in category_stats:
            category_stats[cat] = {"name_ar": cat, "name_en": cat.capitalize(), "total": 0, "correct": 0, "percentage": 0.0}
        category_stats[cat]["total"] += 1

        chosen_idx = answers.get(qid)
        is_correct = (chosen_idx is not None and chosen_idx == q.get("correct_index"))

        if is_correct:
            correct_count += 1
            earned_points += pts
            bloom_stats[bloom]["correct"] += 1
            category_stats[cat]["correct"] += 1

        detailed_walkthrough.append({
            "question_id": qid,
            "category": cat,
            "question_ar": q.get("question_ar", q.get("prompt_ar", "")),
            "question_en": q.get("question_en", q.get("prompt_en", "")),
            "bloom_level": bloom,
            "selected_option": chosen_idx,
            "correct_option": q.get("correct_index"),
            "options": q.get("options", []),
            "options_en": q.get("options_en", []),
            "is_correct": is_correct,
            "solution_walkthrough_ar": q.get("solution_walkthrough_ar", ""),
            "solution_walkthrough_en": q.get("solution_walkthrough_en", "")
        })

    # Calculate Bloom percentages
    for b_key, b_val in bloom_stats.items():
        if b_val["total"] > 0:
            b_val["percentage"] = round((b_val["correct"] / b_val["total"]) * 100.0, 1)

    # Calculate Category percentages
    for c_key, c_val in category_stats.items():
        if c_val["total"] > 0:
            c_val["percentage"] = round((c_val["correct"] / c_val["total"]) * 100.0, 1)

    percentage = round((earned_points / total_points) * 100.0, 1) if total_points > 0 else 0.0

    if percentage >= 90.0:
        grade_letter = "A+"
        feedback_ar = "أداء استثنائي وتفوق باهر! متمكن من كافة مستويات التفكير وفق معايير الاختبار الوزاري الموحد."
        feedback_en = "Exceptional performance! Mastered all cognitive levels according to UAE MoE blueprint standards."
    elif percentage >= 75.0:
        grade_letter = "B+"
        feedback_ar = "مستوى ممتاز مع استيعاب وتطبيق لغوي متين ومطابق لمتطلبات المنهاج."
        feedback_en = "Excellent achievement with strong linguistic comprehension matching curriculum benchmarks."
    elif percentage >= 50.0:
        grade_letter = "C"
        feedback_ar = "أساس جيد، نوصي بمراجعة كبسولات القواعد وسد الفجوات في المراجعة الذكية."
        feedback_en = "Good baseline. We recommend reviewing grammar capsules and completing SM-2 gap review drills."
    else:
        grade_letter = "Needs Practice"
        feedback_ar = "مسار تأسيسي، ننصح بإعادة المذاكرة مع المعلم فاهم خطوة بخطوة لسد الفجوات."
        feedback_en = "Foundational stage. We recommend guided step-by-step revision with Fahim AI."

    return {
        "percentage": percentage,
        "grade_letter": grade_letter,
        "feedback_ar": feedback_ar,
        "feedback_en": feedback_en,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "earned_points": earned_points,
        "total_points": total_points,
        "bloom_breakdown": bloom_stats,
        "category_breakdown": category_stats,
        "solution_walkthrough": detailed_walkthrough
    }


def get_adaptive_flow_questions(lesson_id: str = "lesson_01_ball_games") -> List[Dict[str, Any]]:
    """
    Returns adaptive question pool with dynamic tiers for ANY published lesson.
    Extracts authentic questions from lesson package or catalog.
    """
    if lesson_id == "lesson_01_ball_games":
        return [
            {
                "id": q["id"],
                "bloom_level": q["bloom_level"],
                "difficulty": q["difficulty"],
                "question_ar": q["question_ar"],
                "question_en": q.get("question_en", ""),
                "options": q["options"],
                "options_en": q.get("options_en", []),
                "correct_index": q["correct_index"],
                "hint_ar": "تذكر نص درس ألعاب الكرة وقوانين المباراة." if q["difficulty"] != "easy" else None,
                "hint_en": "Recall the text of the Ball Games lesson and official pitch rules." if q["difficulty"] != "easy" else None,
                "solution_walkthrough_ar": q["solution_walkthrough_ar"],
                "solution_walkthrough_en": q["solution_walkthrough_en"]
            }
            for q in ASSESSMENT_QUESTIONS
        ]

    # For lessons 2 through 10, build adaptive flow from catalog content
    pkg = FULL_CURRICULUM_CATALOG.get(lesson_id)
    if not pkg:
        # Fallback to standard bank
        return [dict(q) for q in ASSESSMENT_QUESTIONS]

    questions = []
    # 1. Add prep check questions as easy/recall
    prep = pkg.get("prep_check", {})
    for idx, q in enumerate(prep.get("questions", [])):
        raw_options = q.get("options", [])
        correct_ans = q.get("correct_answer")
        correct_idx = next((i for i, opt in enumerate(raw_options) if opt.get("id") == correct_ans), 0)
        questions.append({
            "id": f"{lesson_id}_prep_{idx}",
            "bloom_level": "recall",
            "difficulty": "easy",
            "question_ar": q.get("prompt_ar", ""),
            "question_en": q.get("prompt_en", ""),
            "options": [opt.get("label_ar", "") for opt in raw_options],
            "options_en": [opt.get("label_en", "") for opt in raw_options],
            "correct_index": correct_idx,
            "hint_ar": "فكر في المعنى المباشر للدرس.",
            "hint_en": "Think of the direct meaning from the lesson text.",
            "solution_walkthrough_ar": "الإجابة الصحيحة مستنبطة مباشرة من مدخل الدرس وقراءته الاستكشافية.",
            "solution_walkthrough_en": "The correct answer is derived directly from the introductory reading."
        })

    # 2. Add practice activities as medium/application
    for idx, act in enumerate(pkg.get("practice_activities", [])):
        raw_options = act.get("options", [])
        correct_ans = act.get("correct_answer")
        correct_idx = next((i for i, opt in enumerate(raw_options) if opt.get("id") == correct_ans), 0)
        questions.append({
            "id": f"{lesson_id}_act_{idx}",
            "bloom_level": "application",
            "difficulty": "medium",
            "question_ar": act.get("prompt_ar", ""),
            "question_en": act.get("prompt_en", ""),
            "options": [opt.get("label_ar", "") for opt in raw_options],
            "options_en": [opt.get("label_en", "") for opt in raw_options],
            "correct_index": correct_idx,
            "hint_ar": "استحضر القاعدة النحوية أو المعنى السياقي المناسب.",
            "hint_en": "Recall the grammar rule or contextual meaning.",
            "solution_walkthrough_ar": "تطبيق القاعدة اللغوية يحدد الخيار السليم بدقة.",
            "solution_walkthrough_en": "Applying the linguistic rule pinpoints the accurate option."
        })

    return questions if questions else [dict(q) for q in ASSESSMENT_QUESTIONS]
