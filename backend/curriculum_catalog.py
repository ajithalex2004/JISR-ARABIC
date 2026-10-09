"""
curriculum_catalog.py — Full Curriculum Content Packages for Class 5 Term 1 (Lessons 2 through 10)
Aligned with the official UAE Ministry of Education Textbook: "العربية تجمعنا — المستوى 05 — المجلد الأول".
"""

# ============================================================================
# LESSON 02: ركوب الخيل (Horse Riding) — Unit 1: الرياضات والهوايات
# Pages 16-25 in Student Book
# ============================================================================
HORSE_RIDING_CONTENT = {
    "lesson_id": "lesson_02_horse_riding",
    "version": "0.2.0",
    "title_ar": "ركوب الخيل",
    "title_en": "Horse Riding",
    "unit_title_ar": "الرياضات والهوايات",
    "unit_title_en": "Sports and Hobbies",
    "grade": 5,
    "term": 1,
    "start_page": 16,
    "pdf_start_page": 18,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس ركوب الخيل",
        "title_en": "Preparation Check & Prerequisite Diagnostic",
        "description_en": "Quick 3-question check on equestrian terminology and UAE horse racing heritage.",
        "questions": [
            {
                "id": "prep_hr_01",
                "prompt_ar": "مَاذَا نُسَمِّي الشَّخْصَ المَاهِرَ فِي رُكُوبِ الخَيْلِ؟",
                "prompt_en": "What do we call a skilled person who rides horses?",
                "options": [
                    {"id": "opt_a", "label_ar": "فَارِس", "label_en": "Knight / Equestrian"},
                    {"id": "opt_b", "label_ar": "سَبَّاح", "label_en": "Swimmer"},
                    {"id": "opt_c", "label_ar": "حَكَم", "label_en": "Referee"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "فارس (Faris) is the Arabic term for horse rider or knight."
            },
            {
                "id": "prep_hr_02",
                "prompt_ar": "مَا هُوَ الشَّيْءُ الَّذِي يُوضَعُ عَلَى ظَهْرِ الحِصَانِ لِلرُّكُوبِ؟",
                "prompt_en": "What object is placed on the horse's back to sit on?",
                "options": [
                    {"id": "opt_a", "label_ar": "السَّرْج", "label_en": "Saddle"},
                    {"id": "opt_b", "label_ar": "الحَاجِز", "label_en": "Hurdle"},
                    {"id": "opt_c", "label_ar": "اللِّجَام", "label_en": "Bridle"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "السرج (Al-Sarj) is the saddle placed on the horse's back."
            },
            {
                "id": "prep_hr_03",
                "prompt_ar": "أَيْنَ يُقَامُ كَأْسُ دُبَي العَالَمِي لِرُكُوبِ الخَيْلِ؟",
                "prompt_en": "Where is the Dubai World Cup horse race held?",
                "options": [
                    {"id": "opt_a", "label_ar": "مِضْمَار مَيْدَان", "label_en": "Meydan Racecourse"},
                    {"id": "opt_b", "label_ar": "مَلْعَب الجُولْف", "label_en": "Golf Course"},
                    {"id": "opt_c", "label_ar": "حَوْض السِّبَاحَة", "label_en": "Swimming Pool"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The world-famous Dubai World Cup takes place at Meydan Racecourse (مضمار ميدان)."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Supported step-by-step with bilingual glosses and equestrian visuals.",
            "target": "Recognize horse gear terms (سرج، لجام) and identify equestrian roles (فارس، مدرب)."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Structured exercises writing descriptive sentences about racehorses.",
            "target": "Compose sentences describing jumping over hurdles (قفز الحواجز)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Full immersion with authentic sports journalism and event advertising.",
            "target": "Design a complete sports announcement for an equestrian championship in the UAE."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَمِعُ",
            "transliteration": "Astami'u",
            "meaning_en": "I listen",
            "action_guidance": "Listen to the sports commentator describing the horse race.",
            "sample_sentence_ar": "أَسْتَمِعُ إِلَى مُعَلِّقِ السِّبَاقِ.",
            "sample_sentence_en": "I listen to the race commentator."
        },
        {
            "verb_ar": "أَقْرَأُ",
            "transliteration": "Aqra'u",
            "meaning_en": "I read",
            "action_guidance": "Read the sports advertisement from Al-Emarat Al-Youm newspaper.",
            "sample_sentence_ar": "أَقْرَأُ إِعْلَانَ كَأْسِ دُبَي لِلْخَيْلِ.",
            "sample_sentence_en": "I read the Dubai World Cup announcement."
        },
        {
            "verb_ar": "أُقَارِنُ",
            "transliteration": "Uqarinu",
            "meaning_en": "I compare",
            "action_guidance": "Compare the rider's skill before and after professional training.",
            "sample_sentence_ar": "أُقَارِنُ بَيْنَ حَالِ الفَارِسِ قَبْلَ التَّدْرِيبِ وَبَعْدَهُ.",
            "sample_sentence_en": "I compare the rider's state before and after training."
        },
        {
            "verb_ar": "أُصَمِّمُ إِعْلَانًا",
            "transliteration": "Usammimu I'lanan",
            "meaning_en": "I design an advertisement",
            "action_guidance": "Write an announcement including title, advertiser, and dates.",
            "sample_sentence_ar": "أُصَمِّمُ إِعْلَانًا لِمُسَابَقَةِ رُكُوبِ الخَيْلِ.",
            "sample_sentence_en": "I design an ad for the horse riding competition."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_hr_01",
            "word_ar": "فَارِسٌ",
            "vowelled_ar": "فَارِسٌ",
            "meaning_en": "Knight / Skilled Rider",
            "definition_ar": "المَاهِرُ فِي رُكُوبِ الخَيْلِ.",
            "example_ar": "الشَّيْخُ حَمْدَانُ بْنُ مُحَمَّدِ بْنِ رَاشِدٍ فَارِسٌ مَاهِرٌ.",
            "example_en": "Sheikh Hamdan bin Mohammed bin Rashid is a skilled equestrian.",
            "root": "ف-ر-س",
            "category": "sports"
        },
        {
            "id": "vocab_hr_02",
            "word_ar": "مُدَرِّبٌ",
            "vowelled_ar": "مُدَرِّبٌ",
            "meaning_en": "Trainer / Coach",
            "definition_ar": "مَنْ يَقُومُ بِتَعْلِيمِ الآخَرِينَ.",
            "example_ar": "مُدَرِّبِي يُعَلِّمُنِي رُكُوبَ الخَيْلِ.",
            "example_en": "My coach teaches me horse riding.",
            "root": "د-ر-ب",
            "category": "sports"
        },
        {
            "id": "vocab_hr_03",
            "word_ar": "حَاجِزٌ",
            "vowelled_ar": "حَاجِزٌ",
            "meaning_en": "Hurdle / Obstacle",
            "definition_ar": "الفَاصِلُ بَيْنَ شَيْئَيْنِ.",
            "example_ar": "لِسِبَاقِ الخَيْلِ عِدَّةُ حَوَاجِزَ.",
            "example_en": "The horse race has several hurdles.",
            "root": "ح-ج-ز",
            "category": "sports"
        },
        {
            "id": "vocab_hr_04",
            "word_ar": "رُكُوبُ الخَيْلِ",
            "vowelled_ar": "رُكُوبُ الخَيْلِ",
            "meaning_en": "Horseback Riding / Equestrianism",
            "definition_ar": "الفُرُوسِيَّةُ، وَامْتِطَاءُ الأَحْصِنَةِ.",
            "example_ar": "أُخَطِّطُ لِلاشْتِرَاكِ فِي رِيَاضَةِ رُكُوبِ الخَيْلِ.",
            "example_en": "I plan to participate in equestrian sports.",
            "root": "ر-ك-ب",
            "category": "sports"
        },
        {
            "id": "vocab_hr_05",
            "word_ar": "النَّشْرَةُ الرِّيَاضِيَّةُ",
            "vowelled_ar": "النَّشْرَةُ الرِّيَاضِيَّةُ",
            "meaning_en": "Sports Bulletin / Sports News",
            "definition_ar": "البَيَانُ الرِّيَاضِيُّ الَّذِي يُنْشَرُ لِيُعْلَمَ مَا فِيهِ.",
            "example_ar": "أُتَابِعُ النَّشْرَةَ الرِّيَاضِيَّةَ كُلَّ يَوْمٍ.",
            "example_en": "I follow the sports bulletin every day.",
            "root": "ن-ش-ر",
            "category": "media"
        },
        {
            "id": "vocab_hr_06",
            "word_ar": "العَالَمُ",
            "vowelled_ar": "العَالَمُ",
            "meaning_en": "The World",
            "definition_ar": "الخَلْقُ كُلُّهُ.",
            "example_ar": "لَقَدْ شَهِدَ العَالَمُ تَقَدُّمًا كَبِيرًا.",
            "example_en": "The world witnessed great progress.",
            "root": "ع-ل-م",
            "category": "general"
        },
        {
            "id": "vocab_hr_07",
            "word_ar": "مَلْيُونٌ",
            "vowelled_ar": "مَلْيُونٌ",
            "meaning_en": "One Million (1,000,000)",
            "definition_ar": "أَلْفُ أَلْفٍ (1000000).",
            "example_ar": "سَأُشَارِكُ فِي مُسَابَقَةٍ فِيهَا جَوَائِزُ بِمَلَايِينِ الدَّرَاهِمِ.",
            "example_en": "I will take part in a competition with million-dirham prizes.",
            "root": "م-ل-ن",
            "category": "numbers"
        },
        {
            "id": "vocab_hr_08",
            "word_ar": "حَوْلَ",
            "vowelled_ar": "حَوْلَ",
            "meaning_en": "Around",
            "definition_ar": "الجِهَاتُ المُحِيطَةُ بِالشَّيْءِ.",
            "example_ar": "المَلَابِسُ التَّقْلِيدِيَّةُ مُخْتَلِفَةٌ حَوْلَ العَالَمِ.",
            "example_en": "Traditional clothes differ around the world.",
            "root": "ح-و-ل",
            "category": "prepositions"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: الجملة الاسمية والتراكيب الوصفية",
        "title_en": "Grammar Lab: Nominal Sentence and Prepositions of Location",
        "sections": [
            {
                "rule_name_ar": "الجملة الاسمية (المبتدأ والخبر)",
                "rule_name_en": "Nominal Sentence (Subject & Predicate)",
                "explanation_en": "A sentence starting with a noun. Both parts are in the nominative case (marfoo' with dammah).",
                "examples": [
                    {"phrase_ar": "الحِصَانُ سَرِيعٌ.", "translation_en": "The horse is fast."},
                    {"phrase_ar": "الفَارِسُ شُجَاعٌ.", "translation_en": "The rider is brave."}
                ]
            },
            {
                "rule_name_ar": "حروف الجر المكانية (في، على، حول)",
                "rule_name_en": "Locational Prepositions (in, on, around)",
                "explanation_en": "Prepositions cause the following noun to take a kasrah (majroor).",
                "examples": [
                    {"phrase_ar": "السَّرْجُ عَلَى ظَهْرِ الحِصَانِ.", "translation_en": "The saddle is on the horse's back."},
                    {"phrase_ar": "يَقْفِزُ الفَارِسُ حَوْلَ الحَوَاجِزِ.", "translation_en": "The rider jumps around the hurdles."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل الرياضية",
        "title_en": "Sentence Construction Studio",
        "challenges": [
            {
                "id": "sb_hr_01",
                "instruction_en": "Arrange the words to form a sentence about the skilled rider:",
                "target_sentence_ar": "الفَارِسُ المَاهِرُ يَقْفِزُ فَوْقَ الحَوَاجِزِ.",
                "scrambled_tokens": ["فَوْقَ", "الفَارِسُ", "الحَوَاجِزِ.", "المَاهِرُ", "يَقْفِزُ"],
                "translation_en": "The skilled equestrian jumps over the hurdles."
            },
            {
                "id": "sb_hr_02",
                "instruction_en": "Arrange the words to describe Dubai World Cup prize money:",
                "target_sentence_ar": "جَوَائِزُ سِبَاقِ الخَيْلِ تَصِلُ إِلَى ثَلَاثِينَ مَلْيُونَ دَوْلَارٍ.",
                "scrambled_tokens": ["سِبَاقِ", "تَصِلُ", "ثَلَاثِينَ", "جَوَائِزُ", "الخَيْلِ", "دَوْلَارٍ.", "إِلَى", "مَلْيُونَ"],
                "translation_en": "Horse race prizes reach thirty million dollars."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: كأس دبي لركوب الخيل",
        "title_en": "Listen & Speak Studio: Dubai World Cup",
        "passage_ar": "يُعَدُّ كَأْسُ دُبَي العَالَمِي لِرُكُوبِ الخَيْلِ أَغْنَى سِبَاقٍ فِي العَالَمِ. يُقَامُ هَذَا الحَدَثُ الضَّخْمُ فِي آخِرِ شَهْرِ مَارِسَ مِنْ كُلِّ عَامٍ عَلَى مِضْمَارِ مَيْدَانَ فِي إِمَارَةِ دُبَي. يَجْتَمِعُ أَفْضَلُ الفُرْسَانِ مِنْ مُخْتَلِفِ أَنْحَاءِ العَالَمِ لِلتَّنَافُسِ عَلَى جَوَائِزَ قِيمَتُهَا ثَلَاثُونَ مَلْيُونَ دَوْلَارٍ.",
        "passage_en": "The Dubai World Cup for horse racing is the richest race in the world. This major event is held in late March every year at Meydan racecourse in Dubai. Top riders from all over the world gather to compete for thirty million dollars in prizes.",
        "audio_scripts": [
            {"id": "aud_hr_01", "text_ar": "مَرْحَبًا بِكُمْ فِي مِضْمَارِ مَيْدَانَ لِسِبَاقِ الخَيْلِ.", "text_en": "Welcome to Meydan racecourse for the horse race."},
            {"id": "aud_hr_02", "text_ar": "الفَارِسُ يَمْتَطِي حِصَانَهُ بِثِقَةٍ وَمَهَارَةٍ.", "text_en": "The equestrian mounts his horse with confidence and skill."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_hr_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: كأس دبي لركوب الخيل",
            "title_en": "Reading Comprehension: Dubai World Cup",
            "prompt_ar": "أَيْنَ يُقَامُ كَأْسُ دُبَي العَالَمِي لِرُكُوبِ الخَيْلِ؟",
            "prompt_en": "Where is the Dubai World Cup for horse riding held?",
            "options": [
                {"id": "opt_a", "label_ar": "عَلَى مِضْمَارِ مَيْدَانَ فِي دُبَي", "label_en": "At Meydan racecourse in Dubai"},
                {"id": "opt_b", "label_ar": "فِي نَادِي كُرَةِ القَدَمِ", "label_en": "At the football club"},
                {"id": "opt_c", "label_ar": "فِي مَلْعَبِ المَدْرَسَةِ", "label_en": "At the school playground"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        },
        {
            "id": "act_hr_02",
            "type": "fill_in_blank",
            "title_ar": "إكمال الفراغ بالمفردة المناسبة",
            "title_en": "Fill in the Blank: Equestrian Vocabulary",
            "prompt_ar": "يُسَاعِدُ الـ ........ الفَارِسَ عَلَى تَعَلُّمِ قَفْزِ الحَوَاجِزِ.",
            "prompt_en": "The ........ helps the rider learn to jump hurdles.",
            "options": [
                {"id": "opt_a", "label_ar": "المُدَرِّبُ", "label_en": "Trainer / Coach"},
                {"id": "opt_b", "label_ar": "اللِّجَامُ", "label_en": "Bridle"},
                {"id": "opt_c", "label_ar": "المَلْعَبُ", "label_en": "Playground"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: مقابلة مع الفارس الماهر",
        "title_en": "Speaking Mission: Interviewing a UAE Equestrian",
        "scenario_en": "Imagine you are a sports journalist for Abu Dhabi TV. Prepare 3 questions to ask a champion rider about their daily training and horse care.",
        "prompts_ar": [
            "كَمْ سَاعَةً تَتَدَرَّبُ يَوْمِيًّا مَعَ حِصَانِكَ؟",
            "مَا هِيَ أَصْعَبُ الحَوَاجِزِ الَّتِي وَاجَهْتَهَا فِي مِضْمَارِ مَيْدَانَ؟",
            "مَا نَصِيحَتُكَ لِلأَطْفَالِ الرَّاغِبِينَ فِي تَعَلُّمِ رُكُوبِ الخَيْلِ؟"
        ],
        "recording_task_en": "Record yourself speaking one greeting and one question in clear, vowelled Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس ركوب الخيل",
        "title_en": "Parent Companion: Horse Riding Lesson",
        "summary_en": "This lesson introduces equestrianism, UAE racing heritage (Meydan), horse equipment (saddle/bridle), and nominal sentence structure.",
        "dinner_table_prompts": [
            {"arabic": "مَنْ هُوَ الفَارِسُ؟", "english": "Who is the equestrian/knight?", "phonetic": "Man huwa al-faris?"},
            {"arabic": "الحِصَانُ سَرِيعٌ جِدًّا.", "english": "The horse is very fast.", "phonetic": "Al-hisanu saree'un jiddan."}
        ],
        "home_practice_checklist": [
            "Ask your child to show you the difference between a saddle (سرج) and bridle (لجام).",
            "Praise their ability to say 'Faris' (فارس) with correct pronunciation."
        ]
    }
}

# ============================================================================
# LESSON 03: الجري (Running) — Unit 1: الرياضات والهوايات
# Pages 26-35 in Student Book
# ============================================================================
RUNNING_CONTENT = {
    "lesson_id": "lesson_03_running",
    "version": "0.2.0",
    "title_ar": "الجري",
    "title_en": "Running",
    "unit_title_ar": "الرياضات والهوايات",
    "unit_title_en": "Sports and Hobbies",
    "grade": 5,
    "term": 1,
    "start_page": 26,
    "pdf_start_page": 28,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الجري",
        "title_en": "Preparation Check: Running & Track Athletics",
        "description_en": "Check understanding of running terms, sportsmanship, and medals.",
        "questions": [
            {
                "id": "prep_run_01",
                "prompt_ar": "مَا هِيَ المَيْدَالِيَةُ الَّتِي يَحْصُلُ عَلَيْهَا الفَائِزُ بِالمَرْكَزِ الأَوَّلِ؟",
                "prompt_en": "Which medal does the 1st place winner receive?",
                "options": [
                    {"id": "opt_a", "label_ar": "الذَّهَبِيَّة", "label_en": "Gold medal"},
                    {"id": "opt_b", "label_ar": "الفِضِّيَّة", "label_en": "Silver medal"},
                    {"id": "opt_c", "label_ar": "البُرُونْزِيَّة", "label_en": "Bronze medal"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The first-place winner receives the gold medal (الميدالية الذهبية)."
            },
            {
                "id": "prep_run_02",
                "prompt_ar": "مَاذَا نُطْلِقُ فِي دَوْلَةِ الإِمَارَاتِ عَلَى أَصْحَابِ الاحْتِيَاجَاتِ الخَاصَّةِ؟",
                "prompt_en": "What respectful title is used in the UAE for people with disabilities?",
                "options": [
                    {"id": "opt_a", "label_ar": "ذَوُو الهِمَم", "label_en": "People of Determination"},
                    {"id": "opt_b", "label_ar": "اللَّاعِبُون", "label_en": "The Players"},
                    {"id": "opt_c", "label_ar": "المُدَرِّبُون", "label_en": "The Trainers"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The UAE officially calls people with disabilities 'ذوو الهمم' (People of Determination)."
            },
            {
                "id": "prep_run_03",
                "prompt_ar": "مَا هُوَ سِبَاقُ الجَرْي لِمَسَافَاتٍ طَوِيلَةٍ؟",
                "prompt_en": "What is a long-distance running race called?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَارَاثُون", "label_en": "Marathon"},
                    {"id": "opt_b", "label_ar": "سِبَاحَة", "label_en": "Swimming"},
                    {"id": "opt_c", "label_ar": "بُولِينْج", "label_en": "Bowling"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "A marathon (ماراثون) is a long-distance running race."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Focus on medals (ذهبي، فضي) and past-tense verbs (شاركتُ، فزتُ).",
            "target": "Master 8 vocabulary cards and write simple sentences about running races."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Guided reading of a grandchild's letter and past tense conjugation exercises.",
            "target": "Compose a personal letter expressing determination to win gold next year."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Full immersion into Paralympic wheelchair racing and sports journalism.",
            "target": "Write an inspiring sports article about People of Determination at the Dubai Marathon."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَذَكَّرُ",
            "transliteration": "Atadhakkaru",
            "meaning_en": "I recall / remember",
            "action_guidance": "Remember past tense verb endings when talking about myself: شاركتُ، فزتُ.",
            "sample_sentence_ar": "أَتَذَكَّرُ يَوْمَ السِّبَاقِ بِفَرَحٍ.",
            "sample_sentence_en": "I remember race day with joy."
        },
        {
            "verb_ar": "أَكْتُبُ رِسَالَةً",
            "transliteration": "Aktubu Risalatan",
            "meaning_en": "I write a letter",
            "action_guidance": "Include date, addressee, greeting, body, conclusion, and signature.",
            "sample_sentence_ar": "أَكْتُبُ رِسَالَةً لِجَدِّي الحَبِيبِ.",
            "sample_sentence_en": "I write a letter to my beloved grandfather."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_rn_01",
            "word_ar": "الذَّهَبِيُّ",
            "vowelled_ar": "الذَّهَبِيُّ",
            "meaning_en": "Golden / Gold",
            "definition_ar": "لَوْنٌ يُشْبِهُ الذَّهَبَ.",
            "example_ar": "حَصَلْتُ عَلَى المَيْدَالِيَةِ الذَّهَبِيَّةِ فِي السِّبَاقِ.",
            "example_en": "I won the gold medal in the race.",
            "root": "ذ-ه-ب",
            "category": "sports"
        },
        {
            "id": "vocab_rn_02",
            "word_ar": "الفِضِّيُّ",
            "vowelled_ar": "الفِضِّيُّ",
            "meaning_en": "Silver",
            "definition_ar": "لَوْنٌ يُشْبِهُ الفِضَّةَ.",
            "example_ar": "زُيِّنَتِ الهَدِيَّةُ بِوَرَقٍ فِضِّيٍّ.",
            "example_en": "The gift was decorated with silver wrapping.",
            "root": "ف-ض-ض",
            "category": "sports"
        },
        {
            "id": "vocab_rn_03",
            "word_ar": "ذَوُو الهِمَمِ",
            "vowelled_ar": "ذَوُو الهِمَمِ",
            "meaning_en": "People of Determination",
            "definition_ar": "أَصْحَابُ الاحْتِيَاجَاتِ الخَاصَّةِ.",
            "example_ar": "تَمَّ اسْتِبْدَالُ مُصْطَلَحِ الإِعَاقَةِ بِـ(ذَوِي الهِمَمِ).",
            "example_en": "The term disability was replaced with 'People of Determination'.",
            "root": "ه-م-م",
            "category": "society"
        },
        {
            "id": "vocab_rn_04",
            "word_ar": "المَيْدَالِيَّةُ",
            "vowelled_ar": "المَيْدَالِيَّةُ",
            "meaning_en": "Medal / Badge of Honor",
            "definition_ar": "وِسَامٌ مِنَ الذَّهَبِ أَوِ الفِضَّةِ أَوِ البُرُونْزِ.",
            "example_ar": "طُمُوحِي الحُصُولُ عَلَى المَيْدَالِيَةِ الأُولَى.",
            "example_en": "My ambition is to obtain the top medal.",
            "root": "م-د-ل",
            "category": "sports"
        },
        {
            "id": "vocab_rn_05",
            "word_ar": "مَارَاثُونٌ",
            "vowelled_ar": "مَارَاثُونٌ",
            "meaning_en": "Marathon",
            "definition_ar": "سِبَاقٌ لِمَسَافَاتٍ مُحَدَّدَةٍ طَوِيلَةٍ.",
            "example_ar": "أُشَارِكُ كُلَّ عَامٍ فِي مَارَاثُونِ المَدِينَةِ.",
            "example_en": "I participate every year in the city marathon.",
            "root": "م-ر-ث",
            "category": "sports"
        },
        {
            "id": "vocab_rn_06",
            "word_ar": "الحَفِيدُ",
            "vowelled_ar": "الحَفِيدُ",
            "meaning_en": "Grandchild / Grandson",
            "definition_ar": "وَلَدُ الوَلَدِ أَوِ البِنْتِ.",
            "example_ar": "فَرِحَ الجَدُّ بِزِيَارَةِ الحَفِيدِ.",
            "example_en": "The grandfather was delighted by the grandchild's visit.",
            "root": "ح-ف-د",
            "category": "family"
        },
        {
            "id": "vocab_rn_07",
            "word_ar": "اشْتَقْتُ إِلَيْكَ",
            "vowelled_ar": "اشْتَقْتُ إِلَيْكَ",
            "meaning_en": "I missed you",
            "definition_ar": "تَعْبِيرٌ لِلرَّغْبَةِ فِي اللِّقَاءِ.",
            "example_ar": "اشْتَقْتُ إِلَيْكَ يَا مُعَلِّمِي الحَبِيبَ.",
            "example_en": "I missed you, my dear teacher.",
            "root": "ش-و-ق",
            "category": "expressions"
        },
        {
            "id": "vocab_rn_08",
            "word_ar": "القِصَصُ",
            "vowelled_ar": "القِصَصُ",
            "meaning_en": "Stories",
            "definition_ar": "جَمْعُ (قِصَّة)، حِكَايَاتٌ مُسْتَمَدَّةٌ مِنَ الخَيَالِ أَوِ الوَاقِعِ.",
            "example_ar": "أَفْضَلُ قِرَاءَةَ القِصَصِ الخَيَالِيَّةِ وَالرِّيَاضِيَّةِ.",
            "example_en": "I prefer reading fictional and sports stories.",
            "root": "ق-ص-ص",
            "category": "literature"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: تصريف الفعل الماضي مع تاء الفاعل",
        "title_en": "Grammar Lab: Past Tense Conjugation with First-Person 'Taa'",
        "sections": [
            {
                "rule_name_ar": "الفعل الماضي مع المتكلم (أنا فَعَلْتُ)",
                "rule_name_en": "First Person Past Tense (I did)",
                "explanation_en": "When describing personal achievements in the past, add the vowelled 'tu' (تُ) suffix.",
                "examples": [
                    {"phrase_ar": "فُزْتُ بِالمَيْدَالِيَةِ الفِضِّيَّةِ.", "translation_en": "I won the silver medal."},
                    {"phrase_ar": "شَارَكْتُ فِي سِبَاقِ الجَرْيِ.", "translation_en": "I participated in the running race."},
                    {"phrase_ar": "اشْتَقْتُ إِلَى قَصَصِ الجَدِّ.", "translation_en": "I missed grandfather's stories."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل رسائل الأبطال",
        "title_en": "Letter Sentence Studio",
        "challenges": [
            {
                "id": "sb_rn_01",
                "instruction_en": "Arrange the words to express determination to win gold:",
                "target_sentence_ar": "قَرَّرْتُ أَنْ أَتَدَرَّبَ أَكْثَرَ لِتَكُونَ المَيْدَالِيَةُ الذَّهَبِيَّةُ لِي.",
                "scrambled_tokens": ["أَنْ", "قَرَّرْتُ", "المَيْدَالِيَةُ", "لِي.", "أَتَدَرَّبَ", "أَكْثَرَ", "الذَّهَبِيَّةُ", "لِتَكُونَ"],
                "translation_en": "I decided to train more so the gold medal will be mine."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "رسالة سهيل إلى الجد ماجد",
        "title_en": "Suhail's Letter to Grandfather Majed",
        "passage_ar": "جَدِّي العَزِيزَ مَاجِدًا، تَحِيَّةً طَيِّبَةً وَبَعْدُ، أَتَمَنَّى أَنْ تَصِلَكَ رِسَالَتِي وَأَنْتَ فِي أَتَمِّ الصِّحَّةِ. اشْتَقْتُ إِلَيْكَ كَثِيرًا وَأَفْتَقِدُ الاسْتِمَاعَ إِلَى قِصَصِكَ المُشَوِّقَةِ. أُحِبُّ أَنْ أُخْبِرَكَ أَنَّنِي حَصَلْتُ عَلَى المَيْدَالِيَةِ الفِضِّيَّةِ فِي الجَرْيِ لِهَذَا العَامِ فِي المَدْرَسَةِ. كُنْتُ حَزِينًا فِي البِدَايَةِ لأَنَّنِي تَمَنَّيْتُ الذَّهَبِيَّةَ، لَكِنَّنِي قَرَّرْتُ أَنْ أَتَدَرَّبَ أَكْثَرَ لِتَكُونَ الذَّهَبِيَّةُ لِي فِي العَامِ القَادِمِ.",
        "passage_en": "Dear grandfather Majed, warm greetings. I hope my letter finds you in perfect health. I missed you so much and miss hearing your exciting stories. I want to tell you that I won the silver medal in running this year at school. I was sad at first because I hoped for gold, but I decided to train harder so the gold will be mine next year.",
        "audio_scripts": [
            {"id": "aud_rn_01", "text_ar": "حَصَلْتُ عَلَى المَيْدَالِيَةِ الفِضِّيَّةِ فِي الجَرْيِ.", "text_en": "I obtained the silver medal in running."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_rn_01",
            "type": "multiple_choice",
            "title_ar": "فهم نص الرسالة الشخصية",
            "title_en": "Letter Comprehension Check",
            "prompt_ar": "مَاذَا قَرَّرَ سُهَيْلٌ بَعْدَ حُصُولِهِ عَلَى الفِضِّيَّةِ؟",
            "prompt_en": "What did Suhail decide after winning the silver medal?",
            "options": [
                {"id": "opt_a", "label_ar": "أَنْ يَتَدَرَّبَ أَكْثَرَ لِيَنَالَ الذَّهَبِيَّةَ", "label_en": "To train harder to earn the gold"},
                {"id": "opt_b", "label_ar": "أَنْ يَتْرُكَ الرِّيَاضَةَ نِهَائِيًّا", "label_en": "To quit sports completely"},
                {"id": "opt_c", "label_ar": "أَنْ يَنَامَ طَوَالَ اليَوْمِ", "label_en": "To sleep all day"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "التحدث عن يوم رياضي وبطولة ذوي الهمم",
        "title_en": "Speaking Mission: People of Determination Champions",
        "scenario_en": "Speak for 1 minute about the inspirational race of People of Determination in the Dubai Marathon.",
        "prompts_ar": ["أَبْطَالُ ذَوِي الهِمَمِ يَمْتَلِكُونَ إِرَادَةً قَوِيَّةً جِدًّا."],
        "recording_task_en": "Express admiration for athletes of determination using the phrase 'ذوو الهمم'."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الجري والرسائل الشخصية",
        "title_en": "Parent Companion: Running & Personal Letters",
        "summary_en": "This lesson covers athletics, growth mindset (turning silver into gold through practice), respectful terms for people of determination, and past tense conjugation.",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ المَيْدَالِيَةُ الذَّهَبِيَّةُ؟", "english": "What is the gold medal?", "phonetic": "Ma hiya al-meedaliyyatu adh-dhahabiyyah?"}
        ],
        "home_practice_checklist": [
            "Encourage your child when they face a setback: 'We learn from silver to reach gold!'"
        ]
    }
}

# ============================================================================
# LESSON 04: الفنون (Arts) — Unit 1: الرياضات والهوايات
# Pages 36-45 in Student Book
# ============================================================================
ARTS_CONTENT = {
    "lesson_id": "lesson_04_arts",
    "version": "0.2.0",
    "title_ar": "الفنون",
    "title_en": "Arts",
    "unit_title_ar": "الرياضات والهوايات",
    "unit_title_en": "Sports and Hobbies",
    "grade": 5,
    "term": 1,
    "start_page": 36,
    "pdf_start_page": 38,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الفنون",
        "title_en": "Preparation Check: Arts & Calligraphy",
        "description_en": "Test familiarity with world masterpieces, sculpting, and Arabic calligraphy.",
        "questions": [
            {
                "id": "prep_art_01",
                "prompt_ar": "مَنْ رَسَمَ لَوْحَةَ (المُونَالِيزَا) الشَّهِيرَةَ؟",
                "prompt_en": "Who painted the famous Mona Lisa painting?",
                "options": [
                    {"id": "opt_a", "label_ar": "لِيُونَارْدُو دَافِنْشِي", "label_en": "Leonardo da Vinci"},
                    {"id": "opt_b", "label_ar": "بِيكَاسُو", "label_en": "Picasso"},
                    {"id": "opt_c", "label_ar": "أَحْمَد شَوْقِي", "label_en": "Ahmed Shawqi"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Leonardo da Vinci painted the world-famous Mona Lisa."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Learn artistic nouns (رسم، نحت، تمثال، خط عربي).",
            "target": "Distinguish between painting on glass, stone sculpting, and calligraphy."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "VR museum tour descriptions and art exhibition dialogues.",
            "target": "Describe an artwork using rich sensory adjectives."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Art critique comparing historical sculptures with modern Arabic calligraphy.",
            "target": "Author a 2-paragraph critique of an Arabic art exhibition in the UAE."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَأَمَّلُ",
            "transliteration": "Ata'ammalu",
            "meaning_en": "I contemplate / observe closely",
            "action_guidance": "Look closely at the painting colors and Islamic calligraphy curves.",
            "sample_sentence_ar": "أَتَأَمَّلُ جَمَالَ الخَطِّ العَرَبِيِّ.",
            "sample_sentence_en": "I contemplate the beauty of Arabic calligraphy."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_art_01",
            "word_ar": "النَّحْتُ",
            "vowelled_ar": "النَّحْتُ",
            "meaning_en": "Sculpting",
            "definition_ar": "فَنُّ تَحْوِيلِ الحِجَارَةِ إِلَى تَمَاثِيلَ جَمِيلَةٍ.",
            "example_ar": "النَّحْتُ فَنٌّ قَدِيمٌ شَهِيرٌ.",
            "example_en": "Sculpting is a famous ancient art.",
            "root": "ن-ح-ت",
            "category": "arts"
        },
        {
            "id": "vocab_art_02",
            "word_ar": "الزُّجَاجُ",
            "vowelled_ar": "الزُّجَاجُ",
            "meaning_en": "Glass",
            "definition_ar": "جِسْمٌ شَفَّافٌ تُصْنَعُ مِنْهُ أَشْيَاءُ كَثِيرَةٌ، وَيُرْسَمُ عَلَيْهِ.",
            "example_ar": "أُحِبُّ الرَّسْمَ عَلَى الزُّجَاجِ.",
            "example_en": "I love painting on glass.",
            "root": "ز-ج-ج",
            "category": "materials"
        },
        {
            "id": "vocab_art_03",
            "word_ar": "الابْتِسَامَةُ",
            "vowelled_ar": "الابْتِسَامَةُ",
            "meaning_en": "Smile",
            "definition_ar": "انْفِرَاجُ الشَّفَتَيْنِ لِلضَّحِكِ دُونَ صَوْتٍ.",
            "example_ar": "يُصْبِحُ شَكْلُ الوَجْهِ جَمِيلًا بِالابْتِسَامَةِ.",
            "example_en": "The face looks beautiful with a smile.",
            "root": "ب-س-م",
            "category": "expressions"
        },
        {
            "id": "vocab_art_04",
            "word_ar": "الرَّسْمُ",
            "vowelled_ar": "الرَّسْمُ",
            "meaning_en": "Drawing / Painting",
            "definition_ar": "فَنٌّ يَقُومُ عَلَى التَّخْطِيطِ بِالقَلَمِ أَوِ الفُرْشَاةِ.",
            "example_ar": "يُمْكِنُنِي الرَّسْمُ عَلَى الرِّمَالِ بِأُصْبُعِي.",
            "example_en": "I can draw on sand with my finger.",
            "root": "ر-س-م",
            "category": "arts"
        },
        {
            "id": "vocab_art_05",
            "word_ar": "الفُنُونُ",
            "vowelled_ar": "الفُنُونُ",
            "meaning_en": "The Arts",
            "definition_ar": "كُلُّ الإِبْدَاعَاتِ الجَمِيلَةِ كَالرَّسْمِ وَالكِتَابَةِ وَالمُوسِيقَى.",
            "example_ar": "الرَّسْمُ وَالكِتَابَةُ مِنَ الفُنُونِ الجَمِيلَةِ.",
            "example_en": "Painting and writing are part of fine arts.",
            "root": "ف-ن-ن",
            "category": "arts"
        },
        {
            "id": "vocab_art_06",
            "word_ar": "التِّمْثَالُ",
            "vowelled_ar": "التِّمْثَالُ",
            "meaning_en": "Statue / Sculpture",
            "definition_ar": "مَا يَنْحَتُهُ النَّحَّاتُ مِنْ صُوَرٍ وَمُجَسَّمَاتٍ.",
            "example_ar": "تِمْثَالُ أَبُو الهَوْلِ مِنْ أَقْدَمِ التَّمَاثِيلِ فِي العَالَمِ.",
            "example_en": "The Great Sphinx is one of the oldest statues in the world.",
            "root": "م-ث-ل",
            "category": "arts"
        },
        {
            "id": "vocab_art_07",
            "word_ar": "الخَطُّ العَرَبِيُّ",
            "vowelled_ar": "الخَطُّ العَرَبِيُّ",
            "meaning_en": "Arabic Calligraphy",
            "definition_ar": "أَحَدُ فُنُونِ كِتَابَةِ اللُّغَةِ العَرَبِيَّةِ بِأَشْكَالٍ هَنْدَسِيَّةٍ جَمِيلَةٍ.",
            "example_ar": "خَطُّ النَّسْخِ مِنْ أَشْهَرِ الخُطُوطِ العَرَبِيَّةِ.",
            "example_en": "Naskh script is among the most famous Arabic calligraphies.",
            "root": "خ-ط-ط",
            "category": "arts"
        },
        {
            "id": "vocab_art_08",
            "word_ar": "الهِوَايَةُ",
            "vowelled_ar": "الهِوَايَةُ",
            "meaning_en": "Hobby",
            "definition_ar": "مُمَارَسَةُ الفَرْدِ لِفَنٍّ أَوْ نَشَاطٍ يَقْضِي فِيهِ أَوْقَاتَ فَرَاغِهِ بِمُتْعَةٍ.",
            "example_ar": "هِوَايَتِي المُفَضَّلَةُ هِيَ الرَّسْمُ وَالخَطُّ.",
            "example_en": "My favorite hobby is painting and calligraphy.",
            "root": "ه-و-ي",
            "category": "general"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: النعت والصفات الجمالية",
        "title_en": "Grammar Lab: Expressive Adjectives in Art Descriptions",
        "sections": [
            {
                "rule_name_ar": "الصفة والموصوف في التعبير الفني",
                "rule_name_en": "Adjectives Matching Nouns in Art",
                "explanation_en": "Adjectives follow the noun in gender, definiteness, and case.",
                "examples": [
                    {"phrase_ar": "لَوْحَةٌ جَمِيلَةٌ.", "translation_en": "A beautiful painting."},
                    {"phrase_ar": "الخَطُّ العَرَبِيُّ الأَصِيلُ.", "translation_en": "The authentic Arabic calligraphy."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل الوصف الفني",
        "title_en": "Art Descriptive Sentence Studio",
        "challenges": [
            {
                "id": "sb_art_01",
                "instruction_en": "Form a sentence describing Leonardo da Vinci's masterpiece:",
                "target_sentence_ar": "رَسَمَ لِيُونَارْدُو دَافِنْشِي لَوْحَةَ المُونَالِيزَا بِاحْتِرَافٍ.",
                "scrambled_tokens": ["لَوْحَةَ", "بِاحْتِرَافٍ.", "رَسَمَ", "المُونَالِيزَا", "لِيُونَارْدُو", "دَافِنْشِي"],
                "translation_en": "Leonardo da Vinci painted the Mona Lisa with mastery."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الفنون: لوحة الشيخ زايد بالخط العربي",
        "title_en": "Arts Studio: Sheikh Zayed Portrait in Calligraphy",
        "passage_ar": "فِي مَعْرِضِ المَدْرَسَةِ السَّنَوِيِّ لِلْفُنُونِ، قَدَّمَ الطَّالِبُ مَاجِدٌ لَوْحَةً مُمَيَّزَةً لِلْمَغْفُورِ لَهُ الشَّيْخِ زَايِدِ بْنِ سُلْطَانَ آلِ نَهْيَانَ مُسْتَخْدِمًا فَنَّ الخَطِّ العَرَبِيِّ الأَصِيلِ. كَانَتِ الكَلِمَاتُ تُشَكِّلُ مَلَامِحَ الوَجْهِ بِدِقَّةٍ وَإِبْدَاعٍ، مِمَّا أَبْهَرَ الزُّوَّارَ وَالمُعَلِّمِينَ.",
        "passage_en": "At the annual school arts exhibition, student Majed presented a distinctive portrait of the late Sheikh Zayed bin Sultan Al Nahyan using authentic Arabic calligraphy. The words delicately formed facial contours with precision and creativity, amazing visitors and teachers.",
        "audio_scripts": [
            {"id": "aud_art_01", "text_ar": "الخَطُّ العَرَبِيُّ هُوَ فَنٌّ إِسْلَامِيٌّ عَرِيقٌ.", "text_en": "Arabic calligraphy is a prestigious Islamic art."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_art_01",
            "type": "multiple_choice",
            "title_ar": "فنون عالمية",
            "title_en": "World Arts Check",
            "prompt_ar": "مَا هُوَ سِرُّ الشُّهْرَةِ فِي لَوْحَةِ المُونَالِيزَا؟",
            "prompt_en": "What is the secret of fame in the Mona Lisa painting?",
            "options": [
                {"id": "opt_a", "label_ar": "الابْتِسَامَةُ الغَامِضَةُ لِلسَّيِّدَةِ", "label_en": "The lady's mysterious smile"},
                {"id": "opt_b", "label_ar": "لَوْنُ الإِطَارِ الخَشَبِيِّ", "label_en": "The wooden frame color"},
                {"id": "opt_c", "label_ar": "سِعْرُ الفُرْشَاةِ", "label_en": "The paintbrush price"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "جولة افتراضية في متحف اللوفر أبوظبي",
        "title_en": "Virtual Tour of Louvre Abu Dhabi",
        "scenario_en": "Using your VR headset or imagination, guide a friend through the galleries of Louvre Abu Dhabi.",
        "prompts_ar": ["أُشَاهِدُ تِمْثَالًا قَدِيمًا وَلَوْحَاتٍ رَائِعَةً."],
        "recording_task_en": "Speak for 45 seconds describing your favorite painting or statue in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الفنون",
        "title_en": "Parent Companion: Arts Lesson",
        "summary_en": "Focuses on fine arts, calligraphy, and cultural landmarks like Louvre Abu Dhabi and the Sphinx.",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ هِوَايَتُكَ الفَنِّيَّةُ؟", "english": "What is your artistic hobby?", "phonetic": "Ma hiya hiwayatuka al-fanniyyah?"}
        ],
        "home_practice_checklist": [
            "Ask your child to draw something and explain it using Arabic color and art words."
        ]
    }
}

# ============================================================================
# LESSON 05: القراءة (Reading) — Unit 1: الرياضات والهوايات
# Pages 46-55 in Student Book
# ============================================================================
READING_CONTENT = {
    "lesson_id": "lesson_05_reading",
    "version": "0.2.0",
    "title_ar": "القراءة",
    "title_en": "Reading",
    "unit_title_ar": "الرياضات والهوايات",
    "unit_title_en": "Sports and Hobbies",
    "grade": 5,
    "term": 1,
    "start_page": 46,
    "pdf_start_page": 48,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس القراءة",
        "title_en": "Preparation Check: Arab Reading Challenge",
        "description_en": "Test readiness on library skills and reading initiatives.",
        "questions": [
            {
                "id": "prep_rd_01",
                "prompt_ar": "كَمْ كِتَابًا يَقْرَأُ الطَّالِبُ فِي تَحَدِّي القِرَاءَةِ العَرَبِيِّ؟",
                "prompt_en": "How many books does a student read in the Arab Reading Challenge?",
                "options": [
                    {"id": "opt_a", "label_ar": "خَمْسُونَ (50) كِتَابًا", "label_en": "50 books"},
                    {"id": "opt_b", "label_ar": "خَمْسَةُ (5) كُتُبٍ", "label_en": "5 books"},
                    {"id": "opt_c", "label_ar": "كِتَابٌ وَاحِدٌ", "label_en": "1 book"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The Arab Reading Challenge passport involves reading and summarizing 50 books."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary for books, encyclopedia, author, and reading logs.",
            "target": "Distinguish between fictional stories (قصص خيالية) and scientific books (كتب علمية)."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Dialogue practice at the Abu Dhabi International Book Fair.",
            "target": "Write questions using question tools (من، ماذا، أين، كم)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Complete analytical book reviews and summaries.",
            "target": "Write a 50-word book review analyzing characters, plot, and lessons."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْأَلُ",
            "transliteration": "As'alu",
            "meaning_en": "I ask",
            "action_guidance": "Formulate inquiry questions using: هل، ماذا، من، كيف.",
            "sample_sentence_ar": "أَسْأَلُ زَمِيلِي عَنْ كِتَابِهِ المُفَضَّلِ.",
            "sample_sentence_en": "I ask my classmate about their favorite book."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_rd_01",
            "word_ar": "المَوْسُوعَةُ العِلْمِيَّةُ",
            "vowelled_ar": "المَوْسُوعَةُ العِلْمِيَّةُ",
            "meaning_en": "Scientific Encyclopedia",
            "definition_ar": "كِتَابٌ يَحْتَوِي عَلَى مَعْلُومَاتٍ عِلْمِيَّةٍ كَثِيرَةٍ وَمُتَنَوِّعَةٍ.",
            "example_ar": "يُحِبُّ أَخِي القِرَاءَةَ فِي المَوْسُوعَاتِ العِلْمِيَّةِ.",
            "example_en": "My brother loves reading in scientific encyclopedias.",
            "root": "و-س-ع",
            "category": "books"
        },
        {
            "id": "vocab_rd_02",
            "word_ar": "تَحَدِّي القِرَاءَةِ العَرَبِيِّ",
            "vowelled_ar": "تَحَدِّي القِرَاءَةِ العَرَبِيِّ",
            "meaning_en": "Arab Reading Challenge",
            "definition_ar": "مُسَابَقَةٌ لِلْقِرَاءَةِ عَلَى مُسْتَوَى الوَطَنِ العَرَبِيِّ أَطْلَقَتْهَا دَوْلَةُ الإِمَارَاتِ.",
            "example_ar": "رُؤْيَةُ تَحَدِّي القِرَاءَةِ هِيَ غَرْسُ حُبِّ القِرَاءَةِ فِي نُفُوسِ الصِّغَارِ.",
            "example_en": "The vision of the Arab Reading Challenge is instilling a love of reading in youth.",
            "root": "ح-د-ي",
            "category": "initiatives"
        },
        {
            "id": "vocab_rd_03",
            "word_ar": "الكَاتِبُ",
            "vowelled_ar": "الكَاتِبُ",
            "meaning_en": "The Author / Writer",
            "definition_ar": "المُؤَلِّفُ الَّذِي يَكْتُبُ الكُتُبَ وَالقِصَصَ.",
            "example_ar": "نَجِدُ اسْمَ الكَاتِبِ عَلَى غِلَافِ الكِتَابِ دَائِمًا.",
            "example_en": "We always find the author's name on the book cover.",
            "root": "ك-ت-ب",
            "category": "literature"
        },
        {
            "id": "vocab_rd_04",
            "word_ar": "المَعْرِضُ",
            "vowelled_ar": "المَعْرِضُ",
            "meaning_en": "Fair / Exhibition",
            "definition_ar": "مَكَانٌ عَامٌّ تُعْرَضُ فِيهِ المُنْتَجَاتُ العِلْمِيَّةُ أَوِ الكُتُبُ.",
            "example_ar": "ذَهَبْتُ مَعَ أُسْرَتِي إِلَى مَعْرِضِ الكِتَابِ فِي أَبُوظَبِي.",
            "example_en": "I went with my family to the Abu Dhabi Book Fair.",
            "root": "ع-ر-ض",
            "category": "places"
        },
        {
            "id": "vocab_rd_05",
            "word_ar": "الخَيَالِيَّةُ",
            "vowelled_ar": "الخَيَالِيَّةُ",
            "meaning_en": "Fictional / Imaginary",
            "definition_ar": "مَا لَيْسَ لَهُ وُجُودٌ حَقِيقِيٌّ فِي الوَاقِعِ.",
            "example_ar": "كَثِيرٌ مِنَ القِصَصِ خَيَالِيَّةٌ وَمُشَوِّقَةٌ.",
            "example_en": "Many stories are fictional and exciting.",
            "root": "خ-ي-ل",
            "category": "literature"
        },
        {
            "id": "vocab_rd_06",
            "word_ar": "الذَّاكِرَةُ",
            "vowelled_ar": "الذَّاكِرَةُ",
            "meaning_en": "Memory",
            "definition_ar": "مَكَانُ الاحْتِفَاظِ بِالتَّجَارِبِ وَالمَعْلُومَاتِ السَّابِقَةِ فِي العَقْلِ.",
            "example_ar": "القِرَاءَةُ تُقَوِّي الذَّاكِرَةَ وَتَزِيدُ المَعْرِفَةَ.",
            "example_en": "Reading strengthens memory and expands knowledge.",
            "root": "ذ-ك-ر",
            "category": "mind"
        },
        {
            "id": "vocab_rd_07",
            "word_ar": "الطَّالِبُ",
            "vowelled_ar": "الطَّالِبُ",
            "meaning_en": "Student",
            "definition_ar": "الَّذِي يَطْلُبُ العِلْمَ فِي المَدْرَسَةِ.",
            "example_ar": "الطَّالِبُ المُجْتَهِدُ يَقْرَأُ كُلَّ يَوْمٍ.",
            "example_en": "The diligent student reads every day.",
            "root": "ط-ل-ب",
            "category": "school"
        },
        {
            "id": "vocab_rd_08",
            "word_ar": "العِلْمِيَّةُ",
            "vowelled_ar": "العِلْمِيَّةُ",
            "meaning_en": "Scientific",
            "definition_ar": "الاسْتِنَادُ إِلَى الحَقَائِقِ وَالتَّجَارِبِ.",
            "example_ar": "كُتُبُ الطِّبِّ وَالجُغْرَافِيَا كُتُبٌ عِلْمِيَّةٌ.",
            "example_en": "Medicine and geography books are scientific books.",
            "root": "ع-ل-م",
            "category": "science"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: أدوات الاستفهام",
        "title_en": "Grammar Lab: Question Words (أدوات الاستفهام)",
        "sections": [
            {
                "rule_name_ar": "أدوات الاستفهام (مَنْ، مَاذَا، كَمْ، أَيْنَ، كَيْفَ)",
                "rule_name_en": "Interrogative Particles",
                "explanation_en": "Used to ask about people (مَنْ), things (ماذا), quantity (كم), location (أين), and manner (كيف).",
                "examples": [
                    {"phrase_ar": "كَمْ كِتَابًا قَرَأْتَ هَذَا الشَّهْرَ؟", "translation_en": "How many books did you read this month?"},
                    {"phrase_ar": "مَنْ هُوَ كَاتِبُ هَذِهِ القِصَّةِ؟", "translation_en": "Who is the author of this story?"}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل استعراض الكتب",
        "title_en": "Book Review Sentence Studio",
        "challenges": [
            {
                "id": "sb_rd_01",
                "instruction_en": "Arrange the words explaining the benefit of reading:",
                "target_sentence_ar": "القِرَاءَةُ تُسَاعِدُنِي عَلَى أَنْ أَعْرِفَ شَيْئًا عَنْ كُلِّ شَيْءٍ.",
                "scrambled_tokens": ["أَعْرِفَ", "القِرَاءَةُ", "شَيْئًا", "عَنْ", "تُسَاعِدُنِي", "كُلِّ", "عَلَى", "أَنْ", "شَيْءٍ."],
                "translation_en": "Reading helps me know something about everything."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "حوار جاك وسمير في معرض الكتاب الدولي",
        "title_en": "Jack & Samir at Abu Dhabi Book Fair",
        "passage_ar": "مَرْحَبًا يَا جَاك، كَيْفَ حَالُكَ؟ سَأَذْهَبُ اليَوْمَ إِلَى مَعْرِضِ الكِتَابِ الدَّوْلِيِّ فِي أَبُوظَبِي، هَلْ تُرِيدُ الذَّهَابَ مَعِي؟ أَهْلًا يَا سَمِير، فِكْرَةٌ رَائِعَةٌ، أُحِبُّ الكُتُبَ كَثِيرًا. أَنَا مُتَشَوِّقٌ لِشِرَاءِ القِصَصِ الخَيَالِيَّةِ، وَأَنْتَ أَيَّ نَوْعٍ مِنَ الكُتُبِ سَتَشْتَرِي؟ أَنَا سَأَشْتَرِي المَوْسُوعَةَ العِلْمِيَّةَ، لأَنَّنِي أُحِبُّ أَنْ أَعْرِفَ شَيْئًا عَنْ كُلِّ شَيْءٍ.",
        "passage_en": "Hello Jack, how are you? Today I am going to the Abu Dhabi International Book Fair, do you want to come with me? Welcome Samir, great idea, I love books so much. I am excited to buy fictional stories, and you, what kind of books will you buy? I will buy the scientific encyclopedia because I like to know something about everything.",
        "audio_scripts": [
            {"id": "aud_rd_01", "text_ar": "القِرَاءَةُ رِحْلَةٌ مُمْتِعَةٌ تَجْعَلُنِي مُبْدِعًا.", "text_en": "Reading is an enjoyable journey making me creative."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_rd_01",
            "type": "multiple_choice",
            "title_ar": "حوار معرض الكتاب",
            "title_en": "Book Fair Dialogue Check",
            "prompt_ar": "لِمَاذَا يُفَضِّلُ سَمِيرٌ شِرَاءَ المَوْسُوعَةِ العِلْمِيَّةِ؟",
            "prompt_en": "Why does Samir prefer to buy the scientific encyclopedia?",
            "options": [
                {"id": "opt_a", "label_ar": "لأَنَّهُ يُحِبُّ أَنْ يَعْرِفَ شَيْئًا عَنْ كُلِّ شَيْءٍ", "label_en": "Because he likes to know something about everything"},
                {"id": "opt_b", "label_ar": "لأَنَّهَا تَحْتَوِي عَلَى صُوَرِ كُرَةِ القَدَمِ فَقَطْ", "label_en": "Because it only contains football pictures"},
                {"id": "opt_c", "label_ar": "لأَنَّهُ يُرِيدُ أَنْ يَنَامَ", "label_en": "Because he wants to sleep"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "قطار شخصيات الكتب المفضلة",
        "title_en": "Favorite Book Character Train",
        "scenario_en": "Talk about a memorable character from an Arabic story (such as Sindbad or Aladdin) for 1 minute.",
        "prompts_ar": ["شَخْصِيَّتِي المُفَضَّلَةُ هِيَ السَّنْدِبَادُ البَحْرِيُّ الشُّجَاعُ."],
        "recording_task_en": "Name the character and give two reasons why you admire them."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس القراءة",
        "title_en": "Parent Companion: Reading Lesson",
        "summary_en": "Explores reading habits, fiction vs encyclopedias, and the Arab Reading Challenge.",
        "dinner_table_prompts": [
            {"arabic": "مَا هُوَ كِتَابُكَ المُفَضَّلُ؟", "english": "What is your favorite book?", "phonetic": "Ma huwa kitabuka al-mufaddal?"}
        ],
        "home_practice_checklist": [
            "Read 15 minutes of Arabic with your child before bed."
        ]
    }
}

# ============================================================================
# LESSON 06: في مدرستي (At My School) — Unit 2: حقوقي وواجباتي
# Pages 56-65 in Student Book
# ============================================================================
AT_SCHOOL_CONTENT = {
    "lesson_id": "lesson_06_at_school",
    "version": "0.2.0",
    "title_ar": "في مدرستي",
    "title_en": "At My School",
    "unit_title_ar": "حقوقي وواجباتي",
    "unit_title_en": "My Rights and Responsibilities",
    "grade": 5,
    "term": 1,
    "start_page": 56,
    "pdf_start_page": 58,

    "prep_check": {
        "title_ar": "اختبار الاستعداد: الحقوق والواجبات المدرسية",
        "title_en": "Preparation Check: Rights & Responsibilities",
        "description_en": "Check understanding of school rules and student obligations.",
        "questions": [
            {
                "id": "prep_sc_01",
                "prompt_ar": "مَا هُوَ المَقْصُودُ بِـ(الحَقِّ) فِي المَدْرَسَةِ؟",
                "prompt_en": "What is meant by a 'Right' (حق) at school?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَا يَحِقُّ لِلطَّالِبِ الحُصُولُ عَلَيْهِ كَالتَّعْلِيمِ وَالأَمْنِ", "label_en": "What a student is entitled to receive, like education and safety"},
                    {"id": "opt_b", "label_ar": "اللَّعِبُ طَوَالَ الوَقْتِ دُونَ دِرَاسَةٍ", "label_en": "Playing all the time without studying"},
                    {"id": "opt_c", "label_ar": "عَدَمُ احْتِرَامِ القَوَانِينِ", "label_en": "Not respecting rules"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "A Right (الحق) represents educational security, safety, and care guaranteed to children."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Master core terms: حقوق، واجبات، مدير المدرسة، نظيفة، آمنة.",
            "target": "Categorize school situations into Rights (حقوق) vs Duties (واجبات)."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Reading comprehension of 'What Happened Today?' (ماذا حدث اليوم؟).",
            "target": "Master Tanween Fath rules (ألف تنوين الفتح: كتاباً، قلماً)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Drafting school charters for the International Children's Rights Day.",
            "target": "Author a 2-paragraph charter of student rights and school responsibilities."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُصَنِّفُ الحُقُوقَ وَالوَاجِبَاتِ",
            "transliteration": "Usannifu al-huquq wal-wajibāt",
            "meaning_en": "I classify rights and duties",
            "action_guidance": "Distinguish between what the school owes you and what you owe the school.",
            "sample_sentence_ar": "التَّعْلِيمُ حَقٌّ، وَحِفْظُ النِّظَامِ وَاجِبٌ.",
            "sample_sentence_en": "Education is a right, and keeping order is a duty."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_sc_01",
            "word_ar": "حُقُوقٌ",
            "vowelled_ar": "حُقُوقٌ",
            "meaning_en": "Rights",
            "definition_ar": "الامْتِيَازَاتُ الَّتِي يَسْتَحِقُّهَا كُلُّ إِنْسَانٍ.",
            "example_ar": "التَّعْلِيمُ حَقٌّ أَسَاسِيٌّ مِنْ حُقُوقِي.",
            "example_en": "Education is a fundamental right of mine.",
            "root": "ح-ق-ق",
            "category": "rights"
        },
        {
            "id": "vocab_sc_02",
            "word_ar": "وَاجِبَاتٌ",
            "vowelled_ar": "وَاجِبَاتٌ",
            "meaning_en": "Responsibilities / Duties",
            "definition_ar": "الأُمُورُ اللَّازِمَةُ الَّتِي يَتَحَتَّمُ عَلَيَّ أَنْ أَفْعَلَهَا.",
            "example_ar": "مِنْ وَاجِبَاتِي تَنْظِيفُ غُرْفَتِي وَحَلُّ دُرُوسِي.",
            "example_en": "It is my duty to clean my room and do my homework.",
            "root": "و-ج-ب",
            "category": "duties"
        },
        {
            "id": "vocab_sc_03",
            "word_ar": "القَوَانِينُ المَدْرَسِيَّةُ",
            "vowelled_ar": "القَوَانِينُ المَدْرَسِيَّةُ",
            "meaning_en": "School Rules",
            "definition_ar": "النُّظُمُ وَالقَوَاعِدُ الَّتِي تَضَعُهَا إِدَارَةُ المَدْرَسَةِ لِلانْضِبَاطِ.",
            "example_ar": "لَابُدَّ مِنِ احْتِرَامِ القَوَانِينِ المَدْرَسِيَّةِ.",
            "example_en": "School rules must be respected.",
            "root": "ق-ن-ن",
            "category": "rules"
        },
        {
            "id": "vocab_sc_04",
            "word_ar": "مُدِيرُ المَدْرَسَةِ",
            "vowelled_ar": "مُدِيرُ المَدْرَسَةِ",
            "meaning_en": "School Principal",
            "definition_ar": "المَسْؤُولُ عَنْ إِدَارَةِ المَدْرَسَةِ وَرِعَايَةِ طُلَّابِهَا.",
            "example_ar": "أَلْقَى مُدِيرُ المَدْرَسَةِ كَلِمَةً مُشَجِّعَةً فِي الطَّابُورِ.",
            "example_en": "The principal gave an encouraging speech at morning assembly.",
            "root": "د-و-ر",
            "category": "school"
        },
        {
            "id": "vocab_sc_05",
            "word_ar": "المَرْكَزُ",
            "vowelled_ar": "المَرْكَزُ",
            "meaning_en": "Center / Headquarters",
            "definition_ar": "المَقَرُّ الرَّئِيسِيُّ لِمُؤَسَّسَةٍ أَوْ هَيْئَةٍ.",
            "example_ar": "سَأَزُورُ مَرْكَزَ مُحَمَّدِ بْنِ رَاشِدٍ لِلْفَضَاءِ.",
            "example_en": "I will visit the Mohammed bin Rashid Space Centre.",
            "root": "ر-ك-ز",
            "category": "places"
        },
        {
            "id": "vocab_sc_06",
            "word_ar": "آمِنَةٌ",
            "vowelled_ar": "آمِنَةٌ",
            "meaning_en": "Safe / Secure",
            "definition_ar": "مَوْثُوقٌ بِهَا، لَا خَطَرَ مِنْهَا.",
            "example_ar": "رَبْطُ حِزَامِ الأَمَانِ يَجْعَلُ القِيَادَةَ آمِنَةً.",
            "example_en": "Fastening the seatbelt makes driving safe.",
            "root": "أ-م-ن",
            "category": "safety"
        },
        {
            "id": "vocab_sc_07",
            "word_ar": "نَظِيفَةٌ",
            "vowelled_ar": "نَظِيفَةٌ",
            "meaning_en": "Clean / Tidy",
            "definition_ar": "نَقِيَّةٌ، خَالِيَةٌ مِنَ الأَوْسَاخِ.",
            "example_ar": "مَلَابِسِي المَدْرَسِيَّةُ دَائِمًا نَظِيفَةٌ وَمُرَتَّبَةٌ.",
            "example_en": "My school uniform is always clean and neat.",
            "root": "ن-ظ-ف",
            "category": "hygiene"
        },
        {
            "id": "vocab_sc_08",
            "word_ar": "الوَاجِبَاتُ المَدْرَسِيَّةُ",
            "vowelled_ar": "الوَاجِبَاتُ المَدْرَسِيَّةُ",
            "meaning_en": "Homework / School Tasks",
            "definition_ar": "المَهَامُّ الَّتِي يُكَلَّفُ بِهَا الطُّلَّابُ لِلتَّأَكُّدِ مِنْ فَهْمِهِمْ.",
            "example_ar": "أُنْجِزُ وَاجِبَاتِي المَدْرَسِيَّةَ فِي وَقْتِهَا.",
            "example_en": "I complete my homework on time.",
            "root": "و-ج-ب",
            "category": "school"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر الإملاء: ألف تنوين الفتح",
        "title_en": "Orthography Lab: Alif of Tanween Fath (ألف تنوين الفتح)",
        "sections": [
            {
                "rule_name_ar": "قاعدة ألف تنوين الفتح والاستثناءات",
                "rule_name_en": "Rules of Tanween Fath",
                "explanation_en": "Tanween Fath adds an extra Alif (كتاباً, قلماً), EXCEPT on words ending in Taa Marbutah (مدرسةً), or Hamza after Alif (سماءً).",
                "examples": [
                    {"phrase_ar": "اشْتَرَيْتُ كِتَابًا جَدِيدًا.", "translation_en": "I bought a new book (adds Alif)."},
                    {"phrase_ar": "زُرْتُ مَدْرَسَةً نَظِيفَةً.", "translation_en": "I visited a clean school (no Alif on Taa Marbutah)."},
                    {"phrase_ar": "رَأَيْتُ سَمَاءً صَافِيَةً.", "translation_en": "I saw a clear sky (no Alif on Hamza preceded by Alif)."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل الانضباط المدرسي",
        "title_en": "School Discipline Studio",
        "challenges": [
            {
                "id": "sb_sc_01",
                "instruction_en": "Arrange the words about classroom rules:",
                "target_sentence_ar": "احْتِرَامُ القَوَانِينِ المَدْرَسِيَّةِ يُحَقِّقُ بِيئَةً آمِنَةً لِلْجَمِيعِ.",
                "scrambled_tokens": ["يُحَقِّقُ", "القَوَانِينِ", "لِلْجَمِيعِ.", "احْتِرَامُ", "آمِنَةً", "المَدْرَسِيَّةِ", "بِيئَةً"],
                "translation_en": "Respecting school rules creates a safe environment for everyone."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "قصة ماذا حدث اليوم؟",
        "title_en": "What Happened Today? (Story)",
        "passage_ar": "تَسْتَقْبِلُ الأُمُّ أَبْنَاءَهَا الثَّلَاثَةَ بَعْدَ عَوْدَتِهِمْ مِنَ المَدْرَسَةِ، وَتَسْأَلُهُمْ عَنْ يَوْمِهِمُ المَدْرَسِيِّ. قَالَتِ الأُمُّ: مَرْحَبًا بِكُمْ يَا صِغَارِي، كَيْفَ كَانَ يَوْمُكُمْ؟ قَالَ آدَمُ: تَجْرِبَتِي كَانَتْ سَعِيدَةً جِدًّا، لَقَدْ فَازَ صَفِّي بِالمَرْكَزِ الأَوَّلِ فِي اتِّبَاعِ القَوَانِينِ المَدْرَسِيَّةِ! وَقَالَ رَيَّانُ: أَمَّا أَنَا فَقَدْ نَسِيتُ مَلَابِسَ الرِّيَاضَةِ، فَتَعَلَّمْتُ أَهَمِّيَّةَ التَّنْظِيمِ. وَقَالَتْ إِيمَا: زُرْنَا مَرْكَزَ مُحَمَّدِ بْنِ رَاشِدٍ لِلْفَضَاءِ وَكَانَتْ رِحْلَةً مُثِيرَةً.",
        "passage_en": "The mother welcomes her three children upon returning from school, asking about their day. She asks: 'Welcome my children, how was your day?' Adam says: 'My day was very happy, our class won first place in following school rules!' Rayan says: 'I forgot my sports uniform, so I learned the importance of organizing.' Emma says: 'We visited the Mohammed bin Rashid Space Centre and it was an exciting trip.'",
        "audio_scripts": [
            {"id": "aud_sc_01", "text_ar": "لَقَدْ فَازَ صَفِّي بِالمَرْكَزِ الأَوَّلِ.", "text_en": "Our class won first place."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_sc_01",
            "type": "multiple_choice",
            "title_ar": "قواعد تنوين الفتح",
            "title_en": "Tanween Fath Application",
            "prompt_ar": "أَيُّ الكَلِمَاتِ الآتِيَةِ كُتِبَتْ بِتَنْوِينِ الفَتْحِ بِشَكْلٍ صَحِيحٍ؟",
            "prompt_en": "Which word is written correctly with Tanween Fath?",
            "options": [
                {"id": "opt_a", "label_ar": "كِتَابًا", "label_en": "كتاباً (with added Alif)"},
                {"id": "opt_b", "label_ar": "كِتَابَن", "label_en": "كتابن (wrong with Nun)"},
                {"id": "opt_c", "label_ar": "مَدْرَسَةًا", "label_en": "مدرسةًا (wrong extra Alif on Taa Marbutah)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "التعبير عن تجربة مدرسية مميزة",
        "title_en": "School Experience Presentation",
        "scenario_en": "Describe a school event that demonstrated team cooperation or safety rules.",
        "prompts_ar": ["تَعَلَّمْتُ فِي المَدْرَسَةِ أَهَمِّيَّةَ القَوَانِينِ وَالتَّعَاوُنِ."],
        "recording_task_en": "Speak for 45 seconds about why clean and safe schools help you learn better."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: في مدرستي",
        "title_en": "Parent Companion: At My School",
        "summary_en": "Explores student rights, homework duties, following school rules, and Tanween Fath spelling rules.",
        "dinner_table_prompts": [
            {"arabic": "كَيْفَ كَانَ يَوْمُكَ المَدْرَسِيُّ؟", "english": "How was your school day?", "phonetic": "Kayfa kana yawmuka al-madrasiyyu?"}
        ],
        "home_practice_checklist": [
            "Check that your child remembers not to add an Alif to Taa Marbutah when writing Tanween Fath."
        ]
    }
}

# ============================================================================
# LESSON 07: في بيتي (At My Home) — Unit 2: حقوقي وواجباتي
# Pages 66-75 in Student Book
# ============================================================================
AT_HOME_CONTENT = {
    "lesson_id": "lesson_07_at_home",
    "version": "0.2.0",
    "title_ar": "في بيتي",
    "title_en": "At My Home",
    "unit_title_ar": "حقوقي وواجباتي",
    "unit_title_en": "My Rights and Responsibilities",
    "grade": 5,
    "term": 1,
    "start_page": 66,
    "pdf_start_page": 68,

    "prep_check": {
        "title_ar": "اختبار الاستعداد: المهام المنزلية والروتين",
        "title_en": "Preparation Check: Home Chores & Routine",
        "description_en": "Assess understanding of family roles, room organization, and time allocation.",
        "questions": [
            {
                "id": "prep_hm_01",
                "prompt_ar": "مَا هُوَ التَّصَرُّفُ الصَّحِيحُ بَعْدَ العَوْدَةِ إِلَى البَيْتِ؟",
                "prompt_en": "What is the proper action upon returning home?",
                "options": [
                    {"id": "opt_a", "label_ar": "تَرْتِيبُ الحَقِيبَةِ وَأَخْذُ قِسْطٍ مِنَ الرَّاحَةِ", "label_en": "Organize school bag and rest"},
                    {"id": "opt_b", "label_ar": "رَمْيُ المَلَابِسِ عَلَى الأَرْضِ", "label_en": "Throwing clothes on the floor"},
                    {"id": "opt_c", "label_ar": "مُشَاهَدَةُ التِّلْفَازِ سَبْعَ سَاعَاتٍ", "label_en": "Watching TV for seven hours"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Organizing one's bag and resting is the healthy home routine."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary for home chores (قائمة المهام، أعود، نصف ساعة، أدرس).",
            "target": "Sequence the daily routine: return, eat, study, play."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Read about 'House without Rules' and write conditional comparisons.",
            "target": "Use sequence connectors (أولاً، ثم، بعد ذلك) in home writing."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Analyze work-life-play balance among family members.",
            "target": "Create a household daily planner ensuring rights and chores are balanced."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُرَتِّبُ",
            "transliteration": "Urottibu",
            "meaning_en": "I organize / arrange",
            "action_guidance": "Put daily chores in logical chronological sequence.",
            "sample_sentence_ar": "أُرَتِّبُ مَهَامِّي المَنْزِلِيَّةَ فِي قَائِمَةٍ.",
            "sample_sentence_en": "I arrange my home tasks in a list."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_hm_01",
            "word_ar": "قَائِمَةٌ",
            "vowelled_ar": "قَائِمَةٌ",
            "meaning_en": "List / Checklist",
            "definition_ar": "سِجِلٌّ لِعَدَدٍ مِنَ الأَسْمَاءِ أَوِ الأَشْيَاءِ أَوِ المَهَامِّ.",
            "example_ar": "أَعْدَدْتُ قَائِمَةً بِمَهَامِّي اليَوْمِيَّةِ فِي البَيْتِ.",
            "example_en": "I prepared a checklist for my daily tasks at home.",
            "root": "ق-و-م",
            "category": "organization"
        },
        {
            "id": "vocab_hm_02",
            "word_ar": "نِصْفُ سَاعَةٍ",
            "vowelled_ar": "نِصْفُ سَاعَةٍ",
            "meaning_en": "Half an Hour (30 minutes)",
            "definition_ar": "ثَلَاثُونَ دَقِيقَةً مِنَ الوَقْتِ.",
            "example_ar": "مُدَّةُ مُسَاعَدَةِ وَالِدَتِي نِصْفُ سَاعَةٍ.",
            "example_en": "The time I spend helping my mother is half an hour.",
            "root": "ن-ص-ف",
            "category": "time"
        },
        {
            "id": "vocab_hm_03",
            "word_ar": "أَعُودُ",
            "vowelled_ar": "أَعُودُ",
            "meaning_en": "I return / come back",
            "definition_ar": "أَرْجِعُ إِلَى مَكَانِي.",
            "example_ar": "أَعُودُ مِنَ المَدْرَسَةِ عِنْدَ الظُّهْرِ.",
            "example_en": "I return from school at midday.",
            "root": "ع-و-د",
            "category": "verbs"
        },
        {
            "id": "vocab_hm_04",
            "word_ar": "المَهَامُّ",
            "vowelled_ar": "المَهَامُّ",
            "meaning_en": "Tasks / Chores",
            "definition_ar": "الأَعْمَالُ وَالمَسْؤُولِيَّاتُ المَطْلُوبُ إِنْجَازُهَا.",
            "example_ar": "تَرْتِيبُ سَرِيرِي مِنْ أَهَمِّ المَهَامِّ الصَّبَاحِيَّةِ.",
            "example_en": "Making my bed is among the top morning chores.",
            "root": "ه-م-م",
            "category": "chores"
        },
        {
            "id": "vocab_hm_05",
            "word_ar": "القَلَقُ",
            "vowelled_ar": "القَلَقُ",
            "meaning_en": "Anxiety / Worry",
            "definition_ar": "الانْزِعَاجُ وَعَدَمُ الاطْمِئْنَانِ.",
            "example_ar": "التَّنْظِيمُ يُبْعِدُ القَلَقَ عَنِ الأُسْرَةِ.",
            "example_en": "Organization removes worry from the family.",
            "root": "ق-ل-ق",
            "category": "feelings"
        },
        {
            "id": "vocab_hm_06",
            "word_ar": "الطَّوَارِئُ",
            "vowelled_ar": "الطَّوَارِئُ",
            "meaning_en": "Emergencies",
            "definition_ar": "الحَادِثُ المُفَاجِئُ الَّذِي يَتَطَلَّبُ تَدَخُّلًا سَرِيعًا.",
            "example_ar": "نَحْفَظُ أَرْقَامَ الطَّوَارِئِ فِي مَكَانٍ وَاضِحٍ بِالبَيْتِ.",
            "example_en": "We keep emergency numbers in a clear place at home.",
            "root": "ط-ر-أ",
            "category": "safety"
        },
        {
            "id": "vocab_hm_07",
            "word_ar": "أَدْرُسُ",
            "vowelled_ar": "أَدْرُسُ",
            "meaning_en": "I study",
            "definition_ar": "أَقْرَأُ وَأَفْهَمُ وَأَتَعَلَّمُ الدُّرُوسَ.",
            "example_ar": "أَدْرُسُ لُغَتِي العَرَبِيَّةَ بِجِدٍّ وَاهْتِمَامٍ.",
            "example_en": "I study my Arabic language with diligence and interest.",
            "root": "د-ر-س",
            "category": "verbs"
        },
        {
            "id": "vocab_hm_08",
            "word_ar": "أُشَاهِدُ",
            "vowelled_ar": "أُشَاهِدُ",
            "meaning_en": "I watch",
            "definition_ar": "أَرَى وَأُعَايِنُ بِعَيْنِي.",
            "example_ar": "أُشَاهِدُ بَرْنَامَجِي المُفَضَّلَ بَعْدَ إِنْهَاءِ دُرُوسِي.",
            "example_en": "I watch my favorite program after finishing my lessons.",
            "root": "ش-ه-د",
            "category": "verbs"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: حروف العطف والترتيب الزمني",
        "title_en": "Grammar Lab: Conjunctions of Sequence (ثم، بعد ذلك)",
        "sections": [
            {
                "rule_name_ar": "الترتيب الزمني باستخدام (أولاً، ثم، بعد ذلك)",
                "rule_name_en": "Chronological Sequence Connectors",
                "explanation_en": "Used to describe steps in daily routines smoothly.",
                "examples": [
                    {"phrase_ar": "أَعُودُ إِلَى البَيْتِ، ثُمَّ أَتَنَاوَلُ طَعَامِي.", "translation_en": "I return home, then I eat my meal."},
                    {"phrase_ar": "أَدْرُسُ سَاعَةً، وَبَعْدَ ذَلِكَ أَلْعَبُ.", "translation_en": "I study for an hour, and after that I play."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل الروتين المنزلي",
        "title_en": "Home Routine Studio",
        "challenges": [
            {
                "id": "sb_hm_01",
                "instruction_en": "Arrange the words into a balanced home routine:",
                "target_sentence_ar": "أُنْهِي قَائِمَةَ المَهَامِّ ثُمَّ أُشَاهِدُ التِّلْفَازَ نِصْفَ سَاعَةٍ.",
                "scrambled_tokens": ["التِّلْفَازَ", "أُنْهِي", "سَاعَةٍ.", "المَهَامِّ", "ثُمَّ", "قَائِمَةَ", "نِصْفَ", "أُشَاهِدُ"],
                "translation_en": "I finish my task checklist then I watch TV for half an hour."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع: أصدقاء البيت الثلاثة",
        "title_en": "Three Friends Home Routine",
        "passage_ar": "تَقُولُ سُوزَانُ: أَعُودُ كُلَّ يَوْمٍ مُتَحَمِّسَةً، فَأَتَنَاوَلُ طَعَامِي ثُمَّ أَلْعَبُ مَعَ أَصْدِقَائِي، بَعْدَ ذَلِكَ أُشَاهِدُ التِّلْفَازَ ثُمَّ أَنَامُ. أَمَّا جُون فَيَقُولُ: أُحِبُّ القِرَاءَةَ، وَبَعْدَ المَدْرَسَةِ أَلْعَبُ لِمُدَّةِ سَاعَةٍ ثُمَّ أُسَاعِدُ أُسْرَتِي. وَقَالَتْ سَارَةُ: أَنَا أَبْدَأُ أَوَّلًا بِمَهَامِّي المَنْزِلِيَّةِ وَمُشَارَكَةِ عَائِلَتِي فِي إِعْدَادِ الطَّعَامِ.",
        "passage_en": "Susan says: I return home excited every day, eat my food, play with friends, watch TV, then sleep. John says: I love reading, and after school I play for an hour then help my family. Sarah says: I start first with my household chores and helping my family prepare food.",
        "audio_scripts": [
            {"id": "aud_hm_01", "text_ar": "التَّعَاوُنُ فِي البَيْتِ يُسْعِدُ الأُسْرَةَ.", "text_en": "Cooperation at home makes the family happy."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_hm_01",
            "type": "multiple_choice",
            "title_ar": "فهم الروتين الأسري",
            "title_en": "Family Routine Check",
            "prompt_ar": "بِمَاذَا تَبْدَأُ سَارَةُ عِنْدَ عَوْدَتِهَا إِلَى البَيْتِ؟",
            "prompt_en": "What does Sarah start with upon returning home?",
            "options": [
                {"id": "opt_a", "label_ar": "بِمَهَامِّهَا المَنْزِلِيَّةِ وَمُسَاعَدَةِ أُسْرَتِهَا", "label_en": "Her home chores and helping her family"},
                {"id": "opt_b", "label_ar": "بِمُشَاهَدَةِ التِّلْفَازِ طَوَالَ النَّهَارِ", "label_en": "Watching TV all day"},
                {"id": "opt_c", "label_ar": "بِالنَّوْمِ دُونَ طَعَامٍ", "label_en": "Sleeping without food"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "ماذا لو عشنا في بيت بلا قواعد؟",
        "title_en": "What If Our House Had No Rules?",
        "scenario_en": "Imagine a home without any bedtime, mealtime, or cleaning rules. Describe the chaos and why rules are necessary for love and peace.",
        "prompts_ar": ["القَوَاعِدُ فِي البَيْتِ تَحْمِينَا وَتَجْعَلُ حَيَاتَنَا هَادِئَةً."],
        "recording_task_en": "Speak for 45 seconds explaining your top home rule in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: في بيتي",
        "title_en": "Parent Companion: At My Home",
        "summary_en": "Focuses on daily chores, time allocation, family cooperation, and sequential writing.",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ مَهَامُّكَ اليَوْمِيَّةُ؟", "english": "What are your daily tasks?", "phonetic": "Ma hiya mahammuka al-yawmiyyah?"}
        ],
        "home_practice_checklist": [
            "Create a small Arabic chores chart on the fridge with words like 'أرتّب' and 'أساعد'."
        ]
    }
}

# ============================================================================
# LESSON 08: طعامي (My Food) — Unit 2: حقوقي وواجباتي
# Pages 76-85 in Student Book
# ============================================================================
MY_FOOD_CONTENT = {
    "lesson_id": "lesson_08_my_food",
    "version": "0.2.0",
    "title_ar": "طعامي",
    "title_en": "My Food",
    "unit_title_ar": "حقوقي وواجباتي",
    "unit_title_en": "My Rights and Responsibilities",
    "grade": 5,
    "term": 1,
    "start_page": 76,
    "pdf_start_page": 78,

    "prep_check": {
        "title_ar": "اختبار الاستعداد: الغذاء الصحي ورحلة القمح",
        "title_en": "Preparation Check: Food Journey & Nutrition",
        "description_en": "Check understanding of agricultural stages, wheat, and healthy foods.",
        "questions": [
            {
                "id": "prep_fd_01",
                "prompt_ar": "مَا هِيَ المَرْحَلَةُ الأُولَى فِي صِنَاعَةِ الخُبْزِ؟",
                "prompt_en": "What is the first stage in making bread?",
                "options": [
                    {"id": "opt_a", "label_ar": "الزِّرَاعَةُ فِي التُّرْبَةِ", "label_en": "Planting in the soil"},
                    {"id": "opt_b", "label_ar": "الطَّحْنُ فِي المَطَاحِنِ", "label_en": "Grinding in mills"},
                    {"id": "opt_c", "label_ar": "البَيْعُ فِي المَتَاجِرِ", "label_en": "Selling in shops"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Bread begins with planting wheat seeds in fertile soil (الزراعة)."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary for food stages: قمح، تربة، حصاد، طحن، خبز.",
            "target": "Sequence the 4 stages from wheat field to dining table."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Reading 'From the Field to the Table' and using colon punctuation.",
            "target": "Apply colon punctuation rules (النقطتان الرأسيتان:)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Discuss global food security and food waste prevention.",
            "target": "Write an action plan for reducing food waste at school and home."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَتَبَّعُ المَرَاحِلَ",
            "transliteration": "Atatabba'u al-marahil",
            "meaning_en": "I trace the stages",
            "action_guidance": "Trace the step-by-step journey of food production.",
            "sample_sentence_ar": "أَتَتَبَّعُ مَرَاحِلَ صُنْعِ الخُبْزِ اللَّذِيذِ.",
            "sample_sentence_en": "I trace the stages of making delicious bread."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_fd_01",
            "word_ar": "القَمْحُ",
            "vowelled_ar": "القَمْحُ",
            "meaning_en": "Wheat",
            "definition_ar": "نَبَاتٌ عُشْبِيٌّ يَنْمُو فِي سَنَابِلَ تُصْنَعُ مِنْهُ الحُبُوبُ.",
            "example_ar": "حَبَّةُ القَمْحِ تَتَحَوَّلُ إِلَى طَحِينٍ أَبْيَضَ.",
            "example_en": "The wheat grain turns into white flour.",
            "root": "ق-م-ح",
            "category": "agriculture"
        },
        {
            "id": "vocab_fd_02",
            "word_ar": "التُّرْبَةُ",
            "vowelled_ar": "التُّرْبَةُ",
            "meaning_en": "Soil / Earth",
            "definition_ar": "طَبَقَةُ الأَرْضِ الصَّالِحَةُ لِلزِّرَاعَةِ.",
            "example_ar": "تَحْتَاجُ الزِّرَاعَةُ إِلَى تُرْبَةٍ جَيِّدَةٍ وَمِيَاهٍ عَذْبَةٍ.",
            "example_en": "Farming needs fertile soil and fresh water.",
            "root": "ت-ر-ب",
            "category": "nature"
        },
        {
            "id": "vocab_fd_03",
            "word_ar": "الحَصَادُ",
            "vowelled_ar": "الحَصَادُ",
            "meaning_en": "Harvest",
            "definition_ar": "وَقْتُ قَطْعِ الزَّرْعِ وَجَنْيِهِ.",
            "example_ar": "وَقْتُ الحَصَادِ مَوْسِمُ فَرَحٍ لِلْمُزَارِعِينَ.",
            "example_en": "Harvest time is a season of joy for farmers.",
            "root": "ح-ص-د",
            "category": "agriculture"
        },
        {
            "id": "vocab_fd_04",
            "word_ar": "الجُوعُ",
            "vowelled_ar": "الجُوعُ",
            "meaning_en": "Hunger",
            "definition_ar": "خُلُوُّ المَعِدَةِ مِنَ الطَّعَامِ وَالحَاجَةُ إِلَيْهِ.",
            "example_ar": "أَشْعُرُ بِالجُوعِ عِنْدَ الظَّهِيرَةِ.",
            "example_en": "I feel hunger at noon.",
            "root": "ج-و-ع",
            "category": "health"
        },
        {
            "id": "vocab_fd_05",
            "word_ar": "الحَلُّ",
            "vowelled_ar": "الحَلُّ",
            "meaning_en": "Solution",
            "definition_ar": "الكَشْفُ وَالعِلَاجُ الصَّحِيحُ لِلْمَسْأَلَةِ.",
            "example_ar": "وَجَدْنَا الحَلَّ لِمُشْكِلَةِ هَدْرِ الطَّعَامِ.",
            "example_en": "We found the solution to the food waste problem.",
            "root": "ح-ل-ل",
            "category": "problem_solving"
        },
        {
            "id": "vocab_fd_06",
            "word_ar": "آلَاتٌ",
            "vowelled_ar": "آلَاتٌ",
            "meaning_en": "Machines / Tools",
            "definition_ar": "أَجْهِزَةٌ مِيكَانِيكِيَّةٌ تُؤَدِّي عَمَلًا كَبِيرًا.",
            "example_ar": "يَسْتَخْدِمُ الفَلَّاحُ آلَاتٍ حَدِيثَةً لِلْحَصَادِ.",
            "example_en": "The farmer uses modern machines for harvesting.",
            "root": "أ-و-ل",
            "category": "technology"
        },
        {
            "id": "vocab_fd_07",
            "word_ar": "مَصَانِعُ",
            "vowelled_ar": "مَصَانِعُ",
            "meaning_en": "Factories",
            "definition_ar": "أَمَاكِنُ كَبِيرَةٌ تُصْنَعُ فِيهَا الأَغْذِيَةُ وَالمَوَادُّ.",
            "example_ar": "تَقُومُ المَصَانِعُ بِطَحْنِ القَمْحِ وَإِنْتَاجِ الطَّحِينِ.",
            "example_en": "Factories grind wheat and produce flour.",
            "root": "ص-ن-ع",
            "category": "industry"
        },
        {
            "id": "vocab_fd_08",
            "word_ar": "المُشْكِلَةُ",
            "vowelled_ar": "المُشْكِلَةُ",
            "meaning_en": "The Problem",
            "definition_ar": "القَضِيَّةُ الَّتِي تَحْتَاجُ إِلَى عِلَاجٍ وَحَلٍّ.",
            "example_ar": "هَدْرُ الطَّعَامِ مُشْكِلَةٌ تَحْتَاجُ إِلَى تَوْعِيَةٍ.",
            "example_en": "Food waste is a problem needing awareness.",
            "root": "ش-ك-ل",
            "category": "general"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر الترقيم: النقطتان الرأسيتان (:)",
        "title_en": "Punctuation Lab: The Colon (:)",
        "sections": [
            {
                "rule_name_ar": "مواضع استخدام النقطتين الرأسيتين",
                "rule_name_en": "Colon Usage in Arabic",
                "explanation_en": "Placed after speaking verbs (قال:), and before listing constituent categories.",
                "examples": [
                    {"phrase_ar": "قَالَتْ أُمِّي: الطَّعَامُ جَاهِزٌ.", "translation_en": "My mother said: The food is ready."},
                    {"phrase_ar": "الوِجَبَاتُ الرَّئِيسَةُ ثَلَاثٌ: الإِفْطَارُ، وَالغَدَاءُ، وَالعَشَاءُ.", "translation_en": "Main meals are three: breakfast, lunch, and dinner."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل رحلة القمح",
        "title_en": "Wheat Journey Studio",
        "challenges": [
            {
                "id": "sb_fd_01",
                "instruction_en": "Arrange the stages from agriculture to bread:",
                "target_sentence_ar": "تَبْدَأُ رِحْلَةُ الخُبْزِ مِنْ حَبَّةِ القَمْحِ ثُمَّ الطَّحْنِ فِي المَصَانِعِ.",
                "scrambled_tokens": ["مِنْ", "الخُبْزِ", "تَبْدَأُ", "فِي", "القَمْحِ", "رِحْلَةُ", "المَصَانِعِ.", "الطَّحْنِ", "حَبَّةِ", "ثُمَّ"],
                "translation_en": "The journey of bread begins with the wheat grain then grinding in factories."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "من الحقل إلى المائدة",
        "title_en": "From the Field to the Table",
        "passage_ar": "تَبْدَأُ رِحْلَةُ الخُبْزِ مِنْ حَبَّةِ القَمْحِ الَّتِي يَزْرَعُهَا الفَلَّاحُ فِي تُرْبَةٍ جَيِّدَةٍ. عِنْدَمَا يَنْمُو القَمْحُ وَيُصْبِحُ ذَهَبِيَّ اللَّوْنِ، يَقُومُ المُزَارِعُ بِالحَصَادِ بِاسْتِخْدَامِ الآلَاتِ الحَدِيثَةِ. ثُمَّ يُنْقَلُ إِلَى المَصَانِعِ لِطَحْنِهِ، وَفِي النِّهَايَةِ يَصْنَعُ الخَبَّازُ الخُبْزَ اللَّذِيذَ الَّذِي نَتَنَاوَلُهُ فِي وِجَبَاتِنَا.",
        "passage_en": "The journey of bread begins with the grain of wheat that the farmer plants in good soil. When wheat grows and turns golden, the farmer harvests it using modern machinery. Then it is transported to factories for milling, and finally the baker makes the delicious bread we eat in our meals.",
        "audio_scripts": [
            {"id": "aud_fd_01", "text_ar": "نَشْكُرُ اللهَ عَلَى نِعْمَةِ الطَّعَامِ.", "text_en": "We thank Allah for the blessing of food."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_fd_01",
            "type": "multiple_choice",
            "title_ar": "ترقيم النقطتين الرأسيتين",
            "title_en": "Colon Punctuation Practice",
            "prompt_ar": "أَيْنَ نَضَعُ النُّقْطَتَيْنِ الرَّأْسِيَّتَيْنِ (:) فِي الجُمْلَةِ الآتِيَةِ؟",
            "prompt_en": "Where do we place the colon in the following sentence?",
            "options": [
                {"id": "opt_a", "label_ar": "بَعْدَ القَوْلِ (قَالَ الفَلَّاحُ:)", "label_en": "After speech (The farmer said:)"},
                {"id": "opt_b", "label_ar": "فِي نِهَايَةِ الجُمْلَةِ", "label_en": "At the end of the sentence"},
                {"id": "opt_c", "label_ar": "بَيْنَ كُلِّ كَلِمَتَيْنِ", "label_en": "Between every two words"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "حل مشكلة الجوع وهدر الطعام",
        "title_en": "Solving Food Waste & Hunger",
        "scenario_en": "Deliver a 45-second presentation to your class on how students can prevent throwing away sandwich leftovers.",
        "prompts_ar": ["حِفْظُ الطَّعَامِ وَعَدَمُ الإِسْرَافِ وَاجِبٌ أَخْلَاقِيٌّ."],
        "recording_task_en": "Suggest 2 concrete ways to preserve food at home."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس طعامي",
        "title_en": "Parent Companion: My Food",
        "summary_en": "Explains food supply chains, the wheat-to-bread cycle, colon punctuation, and gratefulness for sustenance.",
        "dinner_table_prompts": [
            {"arabic": "مِنْ أَيْنَ يَأْتِي الخُبْزُ؟", "english": "Where does bread come from?", "phonetic": "Min ayna ya'ti al-khubz?"}
        ],
        "home_practice_checklist": [
            "Involve your child in plating dinner and practicing Arabic food words."
        ]
    }
}

# ============================================================================
# LESSON 09: ملابسي (My Clothes) — Unit 2: حقوقي وواجباتي
# Pages 86-95 in Student Book
# ============================================================================
MY_CLOTHES_CONTENT = {
    "lesson_id": "lesson_09_my_clothes",
    "version": "0.2.0",
    "title_ar": "ملابسي",
    "title_en": "My Clothes",
    "unit_title_ar": "حقوقي وواجباتي",
    "unit_title_en": "My Rights and Responsibilities",
    "grade": 5,
    "term": 1,
    "start_page": 86,
    "pdf_start_page": 88,

    "prep_check": {
        "title_ar": "اختبار الاستعداد: الملابس التقليدية والهوية",
        "title_en": "Preparation Check: Traditional Attire",
        "description_en": "Check recognition of traditional UAE garments and world cultures.",
        "questions": [
            {
                "id": "prep_cl_01",
                "prompt_ar": "مَا هُوَ الزِّيُّ التَّقْلِيدِيُّ لِلرِّجَالِ فِي دَوْلَةِ الإِمَارَاتِ؟",
                "prompt_en": "What is the traditional attire for men in the UAE?",
                "options": [
                    {"id": "opt_a", "label_ar": "الكَنْدُورَةُ وَالغُتْرَةُ وَالعِقَالُ", "label_en": "Kandura, Ghutrah, and Egal"},
                    {"id": "opt_b", "label_ar": "السَّارِي الهِنْدِيُّ", "label_en": "Indian Saree"},
                    {"id": "opt_c", "label_ar": "الكِيمُونُو اليَابَانِيُّ", "label_en": "Japanese Kimono"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The Kandura, Ghutrah, and Egal constitute national Emirati attire."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Learn clothing items: ثوب، قبعة، حذاء، ملابس تقليدية.",
            "target": "Match 8 international traditional costumes with their countries."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Adjective-noun agreement (كندورة بيضاء، ثوب طويل).",
            "target": "Apply agreement in gender, number, and definiteness."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Cultural diversity essay for International Day at school.",
            "target": "Write an article celebrating multicultural harmony through fashion in the UAE."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَصِفُ المَلَابِسَ",
            "transliteration": "Asifu al-malabis",
            "meaning_en": "I describe clothing",
            "action_guidance": "Mention color, fabric, length, and origin accurately.",
            "sample_sentence_ar": "أَصِفُ مَلَابِسِي التَّقْلِيدِيَّةَ بِفَخْرٍ.",
            "sample_sentence_en": "I describe my traditional clothes with pride."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_cl_01",
            "word_ar": "تَقْلِيدِيَّةٌ",
            "vowelled_ar": "تَقْلِيدِيَّةٌ",
            "meaning_en": "Traditional / Heritage",
            "definition_ar": "مَا تَوَارَثَهُ النَّاسُ جِيلًا بَعْدَ جِيلٍ مِنَ العَادَاتِ.",
            "example_ar": "يَلْبَسُ جَدِّي المَلَابِسَ التَّقْلِيدِيَّةَ فِي الأَعْيَادِ.",
            "example_en": "My grandfather wears traditional clothing on Eid.",
            "root": "ق-ل-د",
            "category": "heritage"
        },
        {
            "id": "vocab_cl_02",
            "word_ar": "أَنِيقٌ",
            "vowelled_ar": "أَنِيقٌ",
            "meaning_en": "Elegant / Stylish",
            "definition_ar": "حَسَنُ المَظْهَرِ وَالمَلْبَسِ.",
            "example_ar": "يَبْدُو الطَّالِبُ أَنِيقًا فِي زِيِّهِ المَدْرَسِيِّ.",
            "example_en": "The student looks elegant in his school uniform.",
            "root": "أ-ن-ق",
            "category": "appearance"
        },
        {
            "id": "vocab_cl_03",
            "word_ar": "مُرِيحَةٌ",
            "vowelled_ar": "مُرِيحَةٌ",
            "meaning_en": "Comfortable",
            "definition_ar": "تَبْعَثُ عَلَى الرَّاحَةِ وَالاطْمِئْنَانِ.",
            "example_ar": "أَحْرِصُ عَلَى ارْتِدَاءِ مَلَابِسَ رِيَاضِيَّةٍ مُرِيحَةٍ.",
            "example_en": "I ensure wearing comfortable sportswear.",
            "root": "ر-و-ح",
            "category": "comfort"
        },
        {
            "id": "vocab_cl_04",
            "word_ar": "المَمْلَكَةُ المَغْرِبِيَّةُ",
            "vowelled_ar": "المَمْلَكَةُ المَغْرِبِيَّةُ",
            "meaning_en": "Kingdom of Morocco",
            "definition_ar": "دَوْلَةٌ عَرَبِيَّةٌ تَقَعُ فِي شَمَالِ إِفْرِيقْيَا، زِيُّهَا القَفْطَانُ.",
            "example_ar": "القَفْطَانُ زِيٌّ شَهِيرٌ فِي المَمْلَكَةِ المَغْرِبِيَّةِ.",
            "example_en": "The Kaftan is a famous garment in the Kingdom of Morocco.",
            "root": "غ-ر-ب",
            "category": "geography"
        },
        {
            "id": "vocab_cl_05",
            "word_ar": "المَكْسِيكُ",
            "vowelled_ar": "المَكْسِيكُ",
            "meaning_en": "Mexico",
            "definition_ar": "دَوْلَةٌ تَقَعُ فِي أَمْرِيكَا، شَهِيرَةٌ بِقُبَّعَةِ السَّمْبْرِيرُو.",
            "example_ar": "قُبَّعَةُ السَّمْبْرِيرُو مَصْنُوعَةٌ مِنَ القَشِّ فِي المَكْسِيكِ.",
            "example_en": "The Sombrero hat is made of straw in Mexico.",
            "root": "م-ك-س",
            "category": "geography"
        },
        {
            "id": "vocab_cl_06",
            "word_ar": "غَدًا",
            "vowelled_ar": "غَدًا",
            "meaning_en": "Tomorrow",
            "definition_ar": "اليَوْمُ الَّذِي يَأْتِي بَعْدَ اليَوْمِ الحَالِي.",
            "example_ar": "سَنَحْتَفِلُ غَدًا بِاليَوْمِ العَالَمِيِّ فِي المَدْرَسَةِ.",
            "example_en": "We will celebrate International Day at school tomorrow.",
            "root": "غ-د-و",
            "category": "time"
        },
        {
            "id": "vocab_cl_07",
            "word_ar": "مَفْقُودَةٌ",
            "vowelled_ar": "مَفْقُودَةٌ",
            "meaning_en": "Lost / Missing",
            "definition_ar": "ضَائِعَةٌ غَيْرُ مَوْجُودَةٍ.",
            "example_ar": "وَجَدْتُ نَظَّارَةَ السِّبَاحَةِ بَعْدَمَا كَانَتْ مَفْقُودَةً.",
            "example_en": "I found the swim goggles after they had been lost.",
            "root": "ف-ق-د",
            "category": "status"
        },
        {
            "id": "vocab_cl_08",
            "word_ar": "التَّعَجُّبُ",
            "vowelled_ar": "التَّعَجُّبُ",
            "meaning_en": "Wonder / Astonishment",
            "definition_ar": "الشُّعُورُ بِالدَّهْشَةِ وَالإِعْجَابِ.",
            "example_ar": "تَعَجَّبَ الحُضُورُ مِنْ جَمَالِ الأَزْيَاءِ التَّقْلِيدِيَّةِ.",
            "example_en": "The audience was astonished by the beauty of traditional costumes.",
            "root": "ع-ج-ب",
            "category": "emotions"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: مطابقة الصفة للموصوف",
        "title_en": "Grammar Lab: Adjective-Noun Concord (مطابقة الصفة للموصوف)",
        "sections": [
            {
                "rule_name_ar": "مطابقة الصفة للموصوف في التذكير والتأنيث والتعريف",
                "rule_name_en": "Concord Rules in Gender and Definiteness",
                "explanation_en": "The adjective matches the noun in gender (masculine/feminine), number, and definiteness (with or without 'Al-').",
                "examples": [
                    {"phrase_ar": "كَنْدُورَةٌ بَيْضَاءُ (مؤنث).", "translation_en": "A white Kandura (feminine matching)."},
                    {"phrase_ar": "ثَوْبٌ طَوِيلٌ (مذكر).", "translation_en": "A long garment (masculine matching)."},
                    {"phrase_ar": "القُبَّعَةُ الكَبِيرَةُ.", "translation_en": "The large hat (both have Al-)."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل الأزياء العالمية",
        "title_en": "Global Fashion Studio",
        "challenges": [
            {
                "id": "sb_cl_01",
                "instruction_en": "Arrange the words describing traditional Emirati attire:",
                "target_sentence_ar": "أَلْبَسُ الكَنْدُورَةَ البَيْضَاءَ وَالغُتْرَةَ وَالعِقَالَ فِي الأَعْيَادِ.",
                "scrambled_tokens": ["البَيْضَاءَ", "الكَنْدُورَةَ", "فِي", "وَالعِقَالَ", "أَلْبَسُ", "الأَعْيَادِ.", "وَالغُتْرَةَ"],
                "translation_en": "I wear the white Kandura, Ghutrah, and Egal on holidays."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "اليوم العالمي في مدرستنا",
        "title_en": "International Day at School",
        "passage_ar": "تَحْتَفِلُ المَدْرَسَةُ كُلَّ عَامٍ بِاليَوْمِ العَالَمِيِّ، إِنَّهُ أَجْمَلُ يَوْمٍ! ارْتَدَتْ صَدِيقَتِي إِلِيشَا السَّارِيَ الهِنْدِيَّ الطَّوِيلَ، وَلَبِسَ كَارْلُوس قُبَّعَةَ السَّمْبْرِيرُو المَصْنُوعَةَ مِنَ القَشِّ مِنْ بَلَدِهِ المَكْسِيكِ. أَمَّا يُوكُو فَلَبِسَتِ الكِيمُونُو اليَابَانِيَّ الأَنِيقَ، وَارْتَدَتْ مَرْيَمُ القَفْطَانَ المَغْرِبِيَّ المُطَرَّزَ. وَأَنَا ارْتَدَيْتُ كَنْدُورَتِي الإِمَارَاتِيَّةَ البَيْضَاءَ مَعَ الغُتْرَةِ وَالعِقَالِ، مُعَبِّرًا عَنْ فَخْرِي بِهُوِيَّتِي.",
        "passage_en": "The school celebrates International Day every year, it is the most beautiful day! My friend Elisha wore the long Indian Saree, and Carlos wore the straw Sombrero hat from Mexico. Yoko wore the elegant Japanese Kimono, and Maryam wore the embroidered Moroccan Kaftan. As for me, I wore my white Emirati Kandura with the Ghutrah and Egal, expressing pride in my identity.",
        "audio_scripts": [
            {"id": "aud_cl_01", "text_ar": "كُلُّ زِيٍّ يَعْكِسُ ثَقَافَةَ بَلَدِهِ وَتَارِيخَهُ.", "text_en": "Every garment reflects its country's culture and history."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_cl_01",
            "type": "multiple_choice",
            "title_ar": "مطابقة الصفة للموصوف",
            "title_en": "Adjective Agreement Exercise",
            "prompt_ar": "اخْتَرِ الصِّفَةَ المُنَاسِبَةَ: ارْتَدَيْتُ كَنْدُورَةً ........",
            "prompt_en": "Choose the correct matching adjective: I wore a ........ Kandura",
            "options": [
                {"id": "opt_a", "label_ar": "بَيْضَاءَ أَنِيقَةً (مؤنث)", "label_en": "White and elegant (feminine)"},
                {"id": "opt_b", "label_ar": "أَبْيَضَ (مذكر)", "label_en": "White (masculine - wrong agreement)"},
                {"id": "opt_c", "label_ar": "طَوِيلٌ", "label_en": "Long (masculine - wrong agreement)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "تصميم زي للمستقبل يجمع بين التقاليد والحداثة",
        "title_en": "Future Fashion Designer",
        "scenario_en": "Present a design for an outfit that combines traditional Emirati elegance with modern breathable materials.",
        "prompts_ar": ["صَمَّمْتُ زِيًّا مَرِيحًا يَحْمِلُ رُوحَ التُّرَاثِ."],
        "recording_task_en": "Describe the fabric, colors, and national identity touches in your design."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس ملابسي",
        "title_en": "Parent Companion: My Clothes",
        "summary_en": "Celebrates cultural diversity, traditional costumes worldwide, and grammar rules for adjective-noun concord.",
        "dinner_table_prompts": [
            {"arabic": "مَاذَا تَلْبَسُ فِي العِيدِ؟", "english": "What do you wear on Eid?", "phonetic": "Madha talbasu fi al-eid?"}
        ],
        "home_practice_checklist": [
            "Point to items in the wardrobe and practice adjective agreement: قميص أزرق / قبعة زرقاء."
        ]
    }
}

# ============================================================================
# LESSON 10: وقت المرح (Fun Time) — Unit 2: حقوقي وواجباتي
# Pages 96-105 in Student Book
# ============================================================================
FUN_TIME_CONTENT = {
    "lesson_id": "lesson_10_fun_time",
    "version": "0.2.0",
    "title_ar": "وقت المرح",
    "title_en": "Fun Time",
    "unit_title_ar": "حقوقي وواجباتي",
    "unit_title_en": "My Rights and Responsibilities",
    "grade": 5,
    "term": 1,
    "start_page": 96,
    "pdf_start_page": 98,

    "prep_check": {
        "title_ar": "اختبار الاستعداد: قضاء وقت الفراغ والآداب الرقمية",
        "title_en": "Preparation Check: Leisure Time & Digital Etiquette",
        "description_en": "Check understanding of online kindness, hobbies, and vacation safety.",
        "questions": [
            {
                "id": "prep_fn_01",
                "prompt_ar": "مَا هُوَ التَّصَرُّفُ الصَّحِيحُ عِنْدَ رُؤْيَةِ تَعْلِيقٍ سَيِّءٍ عَلَى الإِنْتَرْنِت؟",
                "prompt_en": "What is the proper response when seeing an unkind comment online?",
                "options": [
                    {"id": "opt_a", "label_ar": "تَجَاهُلُهُ وَإِبْلَاغُ الوَالِدَيْنِ أَوِ المُعَلِّمِ", "label_en": "Ignore it and inform parents or teacher"},
                    {"id": "opt_b", "label_ar": "الرَّدُّ بِسُخْرِيَةٍ وَغَضَبٍ", "label_en": "Replying with mockery and anger"},
                    {"id": "opt_c", "label_ar": "إِغْلَاقُ عَيْنَيَّ دُونَ فِعْلِ شَيْءٍ", "label_en": "Closing eyes without doing anything"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Cyber safety rules require ignoring unkind words and seeking adult guidance."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary for digital leisure and outdoor fun: سفاري، منشور، إنترنت، فيلم.",
            "target": "Distinguish between polite online interaction and harmful teasing."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Negative imperative vs affirmative advice (أسلوب النهي وأسلوب الأمر).",
            "target": "Formulate advice sentences using: لا تسخر، احترم، تجاهل."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Composing a formal email recounting a vacation or safari trip.",
            "target": "Write an electronic mail (رسالة إلكترونية) with full email headers and formal tone."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَنْصَحُ",
            "transliteration": "Ansahu",
            "meaning_en": "I advise",
            "action_guidance": "Offer constructive advice using polite imperative forms.",
            "sample_sentence_ar": "أَنْصَحُ زَمِيلِي بِقَضَاءِ وَقْتِ فَرَاغٍ مُفِيدٍ.",
            "sample_sentence_en": "I advise my friend to spend leisure time beneficially."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_fn_01",
            "word_ar": "سُخْرِيَةٌ",
            "vowelled_ar": "سُخْرِيَةٌ",
            "meaning_en": "Mockery / Teasing",
            "definition_ar": "الاسْتِهْزَاءُ بِالآخَرِينَ وَإِحْرَاجُهُمْ.",
            "example_ar": "السُّخْرِيَةُ سُلُوكٌ سَيِّءٌ لَا يَلِيقُ بِالطَّالِبِ المُؤَدَّبِ.",
            "example_en": "Mockery is bad behavior unbecoming of a polite student.",
            "root": "س-خ-ر",
            "category": "ethics"
        },
        {
            "id": "vocab_fn_02",
            "word_ar": "شَبَكَةُ الإِنْتَرْنِت",
            "vowelled_ar": "شَبَكَةُ الإِنْتَرْنِت",
            "meaning_en": "The Internet",
            "definition_ar": "الشَّبَكَةُ المَعْلُومَاتِيَّةُ العَالَمِيَّةُ الَّتِي تَرْبِطُ العَالَمَ.",
            "example_ar": "أَسْتَطِيعُ البَحْثَ بِسُهُولَةٍ فِي شَبَكَةِ الإِنْتَرْنِت.",
            "example_en": "I can easily search on the internet.",
            "root": "ن-ت-ت",
            "category": "technology"
        },
        {
            "id": "vocab_fn_03",
            "word_ar": "مَنْشُورٌ",
            "vowelled_ar": "مَنْشُورٌ",
            "meaning_en": "Social Media Post",
            "definition_ar": "نَصٌّ أَوْ صُورَةٌ تُشَارَكُ فِي وَسَائِلِ التَّوَاصُلِ لِلْقِرَاءَةِ.",
            "example_ar": "كَتَبْتُ مَنْشُورًا أُعَبِّرُ فِيهِ عَنْ حُبِّي لِأَصْدِقَائِي.",
            "example_en": "I wrote a post expressing love for my friends.",
            "root": "ن-ش-ر",
            "category": "media"
        },
        {
            "id": "vocab_fn_04",
            "word_ar": "أَشْكُرُكُمْ جَمِيعًا",
            "vowelled_ar": "أَشْكُرُكُمْ جَمِيعًا",
            "meaning_en": "Thank You All",
            "definition_ar": "عِبَارَةٌ لِلْامْتِنَانِ وَالعِرْفَانِ بِالجَمِيلِ.",
            "example_ar": "أَرْسَلَ المُدِيرُ رِسَالَةً قَائِلًا: أَشْكُرُكُمْ جَمِيعًا عَلَى جُهُودِكُمْ.",
            "example_en": "The principal sent a message saying: I thank you all for your efforts.",
            "root": "ش-ك-ر",
            "category": "expressions"
        },
        {
            "id": "vocab_fn_05",
            "word_ar": "تَجَاهُلٌ",
            "vowelled_ar": "تَجَاهُلٌ",
            "meaning_en": "Ignoring / Disregarding",
            "definition_ar": "عَدَمُ الاهْتِمَامِ بِالأُمُورِ المُزْعِجَةِ.",
            "example_ar": "أَفْضَلُ رَدٍّ عَلَى الإِسَاءَةِ هُوَ التَّجَاهُلُ وَالتَّحَلِّي بِالأَخْلَاقِ.",
            "example_en": "The best response to mistreatment is ignoring and behaving with high ethics.",
            "root": "ج-ه-ل",
            "category": "ethics"
        },
        {
            "id": "vocab_fn_06",
            "word_ar": "رِحْلَةُ سَفَارِي",
            "vowelled_ar": "رِحْلَةُ سَفَارِي",
            "meaning_en": "Safari Trip",
            "definition_ar": "الانْتِقَالُ إِلَى الصَّحْرَاءِ أَوْ المَحْمِيَّاتِ لِلتَّرْفِيهِ وَالمُغَامَرَةِ.",
            "example_ar": "ذَهَبْتُ مَعَ عَائِلَتِي فِي رِحْلَةِ سَفَارِي مُمْتِعَةٍ فِي صَحْرَاءِ الإِمَارَاتِ.",
            "example_en": "I went with my family on an enjoyable safari in the UAE desert.",
            "root": "س-ف-ر",
            "category": "leisure"
        },
        {
            "id": "vocab_fn_07",
            "word_ar": "فِيلْمٌ",
            "vowelled_ar": "فِيلْمٌ",
            "meaning_en": "Movie / Film",
            "definition_ar": "شَرِيطٌ مُصَوَّرٌ يَعْرِضُ قِصَّةً مَرْئِيَّةً.",
            "example_ar": "أُحِبُّ مُشَاهَدَةَ الأَفْلَامِ الوَثَائِقِيَّةِ عَنِ الحَيَوَانَاتِ.",
            "example_en": "I love watching documentary movies about animals.",
            "root": "ف-ل-م",
            "category": "media"
        },
        {
            "id": "vocab_fn_08",
            "word_ar": "سَيِّءٌ",
            "vowelled_ar": "سَيِّءٌ",
            "meaning_en": "Bad / Unkind",
            "definition_ar": "القَبِيحُ الَّذِي لَا يُرْضِي الأَخْلَاقَ.",
            "example_ar": "الكَلَامُ السَّيِّءُ يُؤْذِي المَشَاعِرَ.",
            "example_en": "Unkind words hurt feelings.",
            "root": "س-و-أ",
            "category": "ethics"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر الأساليب: أسلوب النهي (لا + الفعل المضارع)",
        "title_en": "Grammar Lab: Prohibition / Negative Imperative (أسلوب النهي)",
        "sections": [
            {
                "rule_name_ar": "أسلوب النهي باستخدام (لا الناهية)",
                "rule_name_en": "Prohibition with 'La' (Do not...)",
                "explanation_en": "Used to firmly and politely prohibit an undesirable action.",
                "examples": [
                    {"phrase_ar": "لَا تَحْزَنْ يَا صَدِيقِي.", "translation_en": "Do not grieve, my friend."},
                    {"phrase_ar": "لَا تَسْخَرْ مِنْ زُمَلَائِكَ.", "translation_en": "Do not tease your classmates."},
                    {"phrase_ar": "لَا تُؤَجِّلْ وَاجِبَاتِكَ.", "translation_en": "Do not postpone your duties."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني جمل الصداقة الرقمية",
        "title_en": "Digital Friendship Studio",
        "challenges": [
            {
                "id": "sb_fn_01",
                "instruction_en": "Arrange the words offering support to a hurt friend:",
                "target_sentence_ar": "نَحْنُ نَمْرَحُ مَعًا وَلَا نَسْخَرُ مِنْ أَحَدٍ أَبَدًا.",
                "scrambled_tokens": ["مِنْ", "وَلَا", "نَمْرَحُ", "أَبَدًا.", "نَسْخَرُ", "نَحْنُ", "أَحَدٍ", "مَعًا"],
                "translation_en": "We have fun together and never mock anyone."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "منشور جاد والدعم الإيجابي من الأصدقاء",
        "title_en": "Jad's Post and Friends' Positive Support",
        "passage_ar": "كَتَبَ جَادٌ مَنْشُورًا فِي مَوْقِعِ التَّوَاصُلِ: أُحِبُّ أَنْ أَقْضِيَ وَقْتَ فَرَاغِي مَعَ أَصْدِقَائِي، لَكِنَّنِي انْزَعَجْتُ مِنْ سُخْرِيَةِ أَحَدِهِمْ فِي اللَّعِبِ. رَدَّ سَمِيرٌ: لَا تَحْزَنْ يَا جَاد، فَأَنْتَ صَدِيقٌ مُمَيَّزٌ. وَرَدَّتْ لَانَا: تَجَاهَلْ هَذَا الكَلَامَ السَّيِّءَ، نَحْنُ نَمْرَحُ وَلَا نَسْخَرُ. وَقَالَ كِيدِن: كُلُّنَا نَخْسَرُ أَحْيَانًا فِي الشَّطْرَنَجِ وَالمُهِمُّ هُوَ المَرَحُ. شَعَرَ جَادٌ بِالفَرَحِ وَكَتَبَ: تَعْلِيقَاتُكُمْ أَسْعَدَتْنِي كَثِيرًا، أَشْكُرُكُمْ جَمِيعًا.",
        "passage_en": "Jad wrote a post: I like to spend free time with friends, but I was upset by someone's teasing during play. Samir replied: Do not be sad Jad, you are a special friend. Lana replied: Disregard this unkind talk, we have fun and never tease. Kaden said: We all lose sometimes in chess, what matters is having fun. Jad felt happy and wrote: Your comments made me so happy, thank you all.",
        "audio_scripts": [
            {"id": "aud_fn_01", "text_ar": "الكَلِمَةُ الطَّيِّبَةُ تَزْرَعُ المَحَبَّةَ.", "text_en": "A kind word plants love."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_fn_01",
            "type": "multiple_choice",
            "title_ar": "تطبيق أسلوب النهي",
            "title_en": "Negative Imperative Identification",
            "prompt_ar": "أَيُّ الجُمَلِ الآتِيَةِ تُمَثِّلُ (أُسْلُوبَ نَهْيٍ) صَحِيحًا؟",
            "prompt_en": "Which sentence represents a correct negative imperative (prohibition)?",
            "options": [
                {"id": "opt_a", "label_ar": "لَا تَسْخَرْ مِنْ غَيْرِكَ.", "label_en": "Do not tease others. (Prohibition)"},
                {"id": "opt_b", "label_ar": "أَنَا لَا أُحِبُّ المَوْزَ.", "label_en": "I do not like bananas. (Negation)"},
                {"id": "opt_c", "label_ar": "كَيْفَ حَالُكَ اليَوْمَ؟", "label_en": "How are you today? (Question)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "عطلة نهاية الأسبوع في صحراء دبي",
        "title_en": "Weekend in the Dubai Desert",
        "scenario_en": "Recount an exciting weekend safari trip with family, describing the sand dunes, camel rides, and starry night sky.",
        "prompts_ar": ["قَضَيْتُ عُطْلَةً رَائِعَةً فِي رِحْلَةِ سَفَارِي مُثِيرَةٍ."],
        "recording_task_en": "Speak for 45 seconds about your ideal leisure weekend."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس وقت المرح",
        "title_en": "Parent Companion: Fun Time",
        "summary_en": "Focuses on constructive leisure, cyber safety, empathetic peer support, and negative imperative syntax (لا تفعل).",
        "dinner_table_prompts": [
            {"arabic": "كَيْفَ قَضَيْتَ عُطْلَةَ نِهَايَةِ الأُسْبُوعِ؟", "english": "How did you spend the weekend?", "phonetic": "Kayfa qadayta 'utlata nihayati al-usboo'?"}
        ],
        "home_practice_checklist": [
            "Review your child's digital screen habits and discuss cyber kindness in Arabic."
        ]
    }
}

# Catalog dictionary mapping lesson_id to full package (Terms 1, 2, and 3)
from backend.curriculum_catalog_term2 import TERM2_CURRICULUM_CATALOG
from backend.curriculum_catalog_term3 import TERM3_CURRICULUM_CATALOG

FULL_CURRICULUM_CATALOG = {
    "lesson_02_horse_riding": HORSE_RIDING_CONTENT,
    "lesson_03_running": RUNNING_CONTENT,
    "lesson_04_arts": ARTS_CONTENT,
    "lesson_05_reading": READING_CONTENT,
    "lesson_06_at_school": AT_SCHOOL_CONTENT,
    "lesson_07_at_home": AT_HOME_CONTENT,
    "lesson_08_my_food": MY_FOOD_CONTENT,
    "lesson_09_my_clothes": MY_CLOTHES_CONTENT,
    "lesson_10_fun_time": FUN_TIME_CONTENT,
    **TERM2_CURRICULUM_CATALOG,
    **TERM3_CURRICULUM_CATALOG,
}

