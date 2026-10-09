"""
curriculum_catalog_term2.py — Full Curriculum Content Packages for Class 5 Term 2 (Lessons 11 through 16)
Aligned with the official UAE Ministry of Education Textbook: "العربية تجمعنا — المستوى 05 — المجلد الثاني".
Covers:
- Unit 3: مدن عالمية (Global Cities)
  - Lesson 11: مدن عربية (Arab Cities)
  - Lesson 12: لندن (London)
  - Lesson 13: شنغهاي (Shanghai)
- Unit 4: غرائب وعجائب (Oddities & Wonders)
  - Lesson 14: عجائب الدنيا السبع (Seven Wonders of the World)
  - Lesson 15: الكهوف والجزر (Caves and Islands)
  - Lesson 16: عجائب الكائنات الحية (Wonders of Living Creatures)
"""

# ============================================================================
# LESSON 11: مدن عربية (Arab Cities) — Unit 3: مدن عالمية
# Pages 8-17 in Student Book
# ============================================================================
ARAB_CITIES_CONTENT = {
    "lesson_id": "lesson_11_arab_cities",
    "version": "0.2.0",
    "title_ar": "مدن عربية",
    "title_en": "Arab Cities",
    "unit_title_ar": "مدن عالمية",
    "unit_title_en": "Global Cities",
    "grade": 5,
    "term": 2,
    "start_page": 8,
    "pdf_start_page": 8,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس مدن عربية",
        "title_en": "Preparation Check: Arab Cities & Capitals",
        "description_en": "Prerequisite diagnostic testing geographical and city terminology.",
        "questions": [
            {
                "id": "prep_ac_01",
                "prompt_ar": "مَا هِيَ عَاصِمَةُ جُمْهُورِيَّةِ مِصْرَ العَرَبِيَّةِ؟",
                "prompt_en": "What is the capital of the Arab Republic of Egypt?",
                "options": [
                    {"id": "opt_a", "label_ar": "القَاهِرَةُ", "label_en": "Cairo"},
                    {"id": "opt_b", "label_ar": "دُبَيُّ", "label_en": "Dubai"},
                    {"id": "opt_c", "label_ar": "بَيْرُوتُ", "label_en": "Beirut"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "القاهرة (Cairo) is the historic capital of Egypt and one of the oldest cities in the Arab world."
            },
            {
                "id": "prep_ac_02",
                "prompt_ar": "كَمْ إِمَارَةً تَتَكَوَّنُ مِنْهَا دَوْلَةُ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ؟",
                "prompt_en": "How many emirates make up the United Arab Emirates?",
                "options": [
                    {"id": "opt_a", "label_ar": "خَمْسُ إِمَارَاتٍ", "label_en": "Five emirates"},
                    {"id": "opt_b", "label_ar": "سَبْعُ إِمَارَاتٍ", "label_en": "Seven emirates"},
                    {"id": "opt_c", "label_ar": "عَشْرُ إِمَارَاتٍ", "label_en": "Ten emirates"}
                ],
                "correct_answer": "opt_b",
                "explanation_en": "The UAE consists of seven emirates: Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, and Fujairah."
            },
            {
                "id": "prep_ac_03",
                "prompt_ar": "مَا هُوَ النَّهْرُ العَظِيمُ الَّذِي يَمُرُّ فِي مِصْرَ وَالسُّودَانِ؟",
                "prompt_en": "What is the great river that flows through Egypt and Sudan?",
                "options": [
                    {"id": "opt_a", "label_ar": "نَهْرُ النِّيلِ", "label_en": "Nile River"},
                    {"id": "opt_b", "label_ar": "نَهْرُ التَّيْمْزِ", "label_en": "Thames River"},
                    {"id": "opt_c", "label_ar": "نَهْرُ الفُرَاتِ", "label_en": "Euphrates River"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Nile River (نهر النيل) is the lifeblood of Egypt and Sudan."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Supported step-by-step with city flashcards, landmarks, and map identification.",
            "target": "Identify Arab capitals and recognize vocabulary: موقع جغرافي، مناخ، عراقة."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Structured comparison between traditional desert heritage and modern skyscrapers.",
            "target": "Write short paragraphs contrasting past and present Dubai using demonstrative pronouns."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Autonomous travel guide writing and presentation of Arab cultural heritage.",
            "target": "Synthesize a multimedia tourist bulletin for Dubai and Cairo highlighting cultural landmarks."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَأَمَّلُ",
            "transliteration": "Ata'ammalu",
            "meaning_en": "I contemplate / examine closely",
            "action_guidance": "Look at the world map and examine city locations and trade routes.",
            "sample_sentence_ar": "أَتَأَمَّلُ مَوْقِعَ مَدِينَةِ دُبَي عَلَى خَرِيطَةِ العَالَمِ.",
            "sample_sentence_en": "I examine the location of Dubai on the world map."
        },
        {
            "verb_ar": "أَصِفُ",
            "transliteration": "Asifu",
            "meaning_en": "I describe",
            "action_guidance": "Use descriptive adjectives to portray the historical monuments.",
            "sample_sentence_ar": "أَصِفُ مَعَالِمَ القَاهِرَةِ التَّارِيخِيَّةَ بِجُمَلٍ جَمِيلَةٍ.",
            "sample_sentence_en": "I describe the historical landmarks of Cairo with beautiful sentences."
        },
        {
            "verb_ar": "أُقَارِنُ",
            "transliteration": "Uqarinu",
            "meaning_en": "I compare",
            "action_guidance": "Contrast life in the desert past with present modern smart cities.",
            "sample_sentence_ar": "أُقَارِنُ بَيْنَ دُبَي فِي المَاضِي وَدُبَي فِي الحَاضِرِ.",
            "sample_sentence_en": "I compare Dubai in the past and Dubai in the present."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_ac_01",
            "word_ar": "القَاهِرَةُ",
            "vowelled_ar": "القَاهِرَةُ",
            "meaning_en": "Cairo",
            "definition_ar": "عَاصِمَةُ دَوْلَةِ مِصْرَ، وَمِنْ أَقْدَمِ المُدُنِ العَرَبِيَّةِ.",
            "example_ar": "زُرْتُ مَدِينَةَ القَاهِرَةِ وَشَاهَدْتُ الأَهْرَامَاتِ.",
            "example_en": "I visited Cairo and saw the Pyramids.",
            "root": "ق-ه-ر",
            "category": "geography"
        },
        {
            "id": "vocab_ac_02",
            "word_ar": "المَوْقِعُ الجُغْرَافِيُّ",
            "vowelled_ar": "المَوْقِعُ الجُغْرَافِيُّ",
            "meaning_en": "Geographical Location",
            "definition_ar": "المَكَانُ وَالجِهَةُ عَلَى خَرِيطَةِ الأَرْضِ.",
            "example_ar": "تَتَمَيَّزُ دَوْلَةُ الإِمَارَاتِ بِمَوْقِعٍ جُغْرَافِيٍّ فَرِيدٍ.",
            "example_en": "The UAE boasts a unique geographical location.",
            "root": "و-ق-ع",
            "category": "geography"
        },
        {
            "id": "vocab_ac_03",
            "word_ar": "عَرَاقَةٌ",
            "vowelled_ar": "عَرَاقَةٌ",
            "meaning_en": "Ancient Heritage / Nobility",
            "definition_ar": "أَصَالَةٌ وَقِدَمٌ تَارِيخِيٌّ عَظِيمٌ.",
            "example_ar": "تَشْتَهِرُ المُدُنُ العَرَبِيَّةُ بِعَرَاقَتِهَا وَتَارِيخِهَا.",
            "example_en": "Arab cities are renowned for their ancient heritage.",
            "root": "ع-ر-ق",
            "category": "heritage"
        },
        {
            "id": "vocab_ac_04",
            "word_ar": "زَاخِرَةٌ",
            "vowelled_ar": "زَاخِرَةٌ",
            "meaning_en": "Abundant / Teeming With",
            "definition_ar": "مَلِيئَةٌ بِالخَيْرَاتِ وَالمَعَالِمِ.",
            "example_ar": "المَتَاحِفُ العَرَبِيَّةُ زَاخِرَةٌ بِالتُّحَفِ الثَّمِينَةِ.",
            "example_en": "Arab museums are teeming with precious artifacts.",
            "root": "ز-خ-ر",
            "category": "descriptive"
        },
        {
            "id": "vocab_ac_05",
            "word_ar": "خَالِدَةٌ",
            "vowelled_ar": "خَالِدَةٌ",
            "meaning_en": "Immortal / Everlasting",
            "definition_ar": "دَائِمَةٌ وَبَاقِيَةٌ عَلَى مَرِّ العُصُورِ.",
            "example_ar": "تَبْقَى إِنجَازَاتُ القَادَةِ خَالِدَةً فِي تَارِيخِ الأُمَّةِ.",
            "example_en": "The achievements of leaders remain immortal in the nation's history.",
            "root": "خ-ل-د",
            "category": "heritage"
        },
        {
            "id": "vocab_ac_06",
            "word_ar": "المُنَاخُ",
            "vowelled_ar": "المُنَاخُ",
            "meaning_en": "Climate",
            "definition_ar": "حَالَةُ الطَّقْسِ عَلَى مَدَى فَتْرَةٍ طَوِيلَةٍ.",
            "example_ar": "يَتَّسِمُ مُنَاخُ الخَلِيجِ العَرَبِيِّ بِالدِّفْءِ شِتَاءً.",
            "example_en": "The Arabian Gulf climate is characterized by warm winters.",
            "root": "ن-و-خ",
            "category": "science"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: أسماء الإشارة والمعرفة والنكرة",
        "title_en": "Grammar Lab: Demonstrative Pronouns & Definite vs Indefinite Nouns",
        "sections": [
            {
                "rule_name_ar": "أسماء الإشارة (هَذَا، هَذِهِ، هَؤُلَاءِ)",
                "rule_name_en": "Demonstrative Pronouns (This [m], This [f], These)",
                "explanation_en": "Used to point to nouns near the speaker. Non-human plural nouns take (هذه).",
                "examples": [
                    {"phrase_ar": "هَذَا بُرْجٌ شَاهِقٌ.", "translation_en": "This is a towering skyscraper."},
                    {"phrase_ar": "هَذِهِ مُدُنٌ عَرَبِيَّةٌ عَرِيقَةٌ.", "translation_en": "These are ancient Arab cities."}
                ]
            },
            {
                "rule_name_ar": "المعرفة والنكرة (التعريف بـ أل)",
                "rule_name_en": "Definite vs Indefinite Nouns (Al- prefix)",
                "explanation_en": "A noun without (ال) is indefinite (nakirah). Adding (ال) makes it specific and definite (ma'rifah).",
                "examples": [
                    {"phrase_ar": "مَدِينَةٌ (نكرة) — المَدِينَةُ (معرفة)", "translation_en": "A city (indefinite) — The city (definite)"}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: وصف المدن العربية",
        "title_en": "Sentence Construction Studio: Describing Arab Cities",
        "challenges": [
            {
                "id": "sb_ac_01",
                "instruction_en": "Arrange the words to describe Cairo's ancient heritage:",
                "target_sentence_ar": "القَاهِرَةُ مَدِينَةٌ عَرِيقَةٌ زَاخِرَةٌ بِالمَعَالِمِ التَّارِيخِيَّةِ.",
                "scrambled_tokens": ["بِالمَعَالِمِ", "القَاهِرَةُ", "التَّارِيخِيَّةِ.", "مَدِينَةٌ", "عَرِيقَةٌ", "زَاخِرَةٌ"],
                "translation_en": "Cairo is an ancient city teeming with historical landmarks."
            },
            {
                "id": "sb_ac_02",
                "instruction_en": "Arrange the words to describe Dubai between past and present:",
                "target_sentence_ar": "تَجْمَعُ دُبَي بَيْنَ أَصَالَةِ المَاضِي وَتَطَوُّرِ الحَاضِرِ.",
                "scrambled_tokens": ["وَتَطَوُّرِ", "أَصَالَةِ", "تَجْمَعُ", "الحَاضِرِ.", "بَيْنَ", "دُبَي", "المَاضِي"],
                "translation_en": "Dubai combines ancestral authenticity with modern progress."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: دبي بين الماضي والحاضر",
        "title_en": "Listen & Speak Studio: Dubai Between Past and Present",
        "passage_ar": "سَافَرَ زَاكْ إِلَى دَوْلَةِ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ. رَأَى الصَّحْرَاءَ الذَّهَبِيَّةَ وَالخِيَامَ وَالإِبِلَ، وَتَعَرَّفَ عَلَى كَرَمِ الضِّيَافَةِ الإِمَارَاتِيَّةِ حَيْثُ قُدِّمَتْ لَهُ القَهْوَةُ وَالتَّمْرُ. ثُمَّ شَاهَدَ مَدِينَةَ دُبَي الحَدِيثَةَ بِمَبَانِيهَا الشَّاهِقَةِ مِثْلَ بُرْجِ خَلِيفَةَ، وَشَبَكَةِ المِتْرُو المُتَطَوِّرَةِ، وَالمَطَارِ العَالَمِيِّ، فَقَالَ: رَائِعَةٌ دُبَي فِي المَاضِي وَالحَاضِرِ!",
        "passage_en": "Zack traveled to the UAE. He saw the golden dunes, tents, and camels, experiencing authentic Emirati hospitality with dates and Arabic coffee. Then he marveled at modern Dubai with its towering Burj Khalifa, driverless metro network, and international airport, exclaiming: 'Wonderful is Dubai in the past and present!'",
        "audio_scripts": [
            {"id": "aud_ac_01", "text_ar": "مَرْحَبًا بِكُمْ فِي مَدِينَةِ دُبَي زَهْرَةِ الشَّرْقِ.", "text_en": "Welcome to the city of Dubai, jewel of the East."},
            {"id": "aud_ac_02", "text_ar": "القَاهِرَةُ مَدِينَةُ الأَلْفِ مِئْذَنَةٍ.", "text_en": "Cairo is the city of a thousand minarets."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_ac_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: قصة زاك في دبي",
            "title_en": "Reading Comprehension: Zack in Dubai",
            "prompt_ar": "مَا الَّذِي أَدْهَشَ زَاكْ فِي مَدِينَةِ دُبَي الحَدِيثَةِ؟",
            "prompt_en": "What amazed Zack in modern Dubai?",
            "options": [
                {"id": "opt_a", "label_ar": "بُرْجُ خَلِيفَةَ وَالمِتْرُو وَالمَطَارُ الجَدِيدُ", "label_en": "Burj Khalifa, Metro, and new airport"},
                {"id": "opt_b", "label_ar": "البُرُودَةُ الشَّدِيدَةُ وَتَسَاقُطُ الثَّلْجِ", "label_en": "Extreme cold and snowfall"},
                {"id": "opt_c", "label_ar": "اخْتِفَاءُ السِّيَارَاتِ مِنَ الشَّوَارِعِ", "label_en": "Disappearance of cars"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        },
        {
            "id": "act_ac_02",
            "type": "fill_in_blank",
            "title_ar": "إكمال الفراغ باسم الإشارة المناسب",
            "title_en": "Fill in the Blank: Demonstrative Pronoun",
            "prompt_ar": "........ مُدُنٌ عَرَبِيَّةٌ تَزْخَرُ بِالتَّارِيخِ وَالأَصَالَةِ.",
            "prompt_en": "........ are Arab cities teeming with history and authenticity.",
            "options": [
                {"id": "opt_a", "label_ar": "هَذِهِ", "label_en": "These (feminine/non-human plural)"},
                {"id": "opt_b", "label_ar": "هَذَا", "label_en": "This (masculine singular)"},
                {"id": "opt_c", "label_ar": "هَذَانِ", "label_en": "These two (masculine dual)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: أنا مرشد سياحي في مدينتي",
        "title_en": "Speaking Mission: Tourist Guide for an Arab City",
        "scenario_en": "You are presenting an Arab city to international visitors at the school cultural fair. Introduce the city, name 2 key landmarks, and welcome visitors in Modern Standard Arabic.",
        "prompts_ar": [
            "أَهْلًا وَسَهْلًا بِكُمْ فِي مَدِينَةِ دُبَي الحَدِيثَةِ.",
            "أَدْعُوكُمْ لِزِيَارَةِ بُرْجِ خَلِيفَةَ وَمُتْحَفِ المُسْتَقْبَلِ.",
            "دُبَي تُرَحِّبُ بِكُلِّ زُوَّارِهَا مِنْ جَمِيعِ أَنْحَاءِ العَالَمِ."
        ],
        "recording_task_en": "Record 30 seconds introducing an Arab city and its most impressive attraction."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس مدن عربية",
        "title_en": "Parent Companion: Arab Cities",
        "summary_en": "Focuses on Arab geography (Cairo, Dubai), historical heritage vs modern innovation, and demonstrative pronouns (هذا / هذه).",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ عَاصِمَةُ مِصْرَ؟", "english": "What is the capital of Egypt?", "phonetic": "Ma hiya 'asimat misr?"},
            {"arabic": "كَمْ إِمَارَةً فِي دَوْلَةِ الإِمَارَاتِ؟", "english": "How many emirates in the UAE?", "phonetic": "Kam imaratan fee dawlat al-imarat?"}
        ],
        "home_practice_checklist": [
            "Ask your child to name 3 landmarks in Dubai or Cairo.",
            "Practice pointing to household objects with 'Hatha' (هذا) and 'Hathihi' (هذه)."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس مدن عربية",
        "learning_objectives": ["Identify 6 geographical vocabulary terms", "Contrast past vs present Dubai", "Master non-human plural demonstrative (هذه مدن)"],
        "misconception_flags": ["Using هؤلاء instead of هذه for non-human plurals like مدن"],
        "recommended_drills": ["City matching flashcards", "Demonstrative pronoun cloze drills"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_ac_01",
                "prompt_ar": "مَا هُوَ النَّهْرُ الَّذِي يَجْرِي فِي مَدِينَةِ القَاهِرَةِ؟",
                "prompt_en": "Which river flows through Cairo?",
                "options": [
                    {"id": "opt_a", "label_ar": "نَهْرُ النِّيلِ", "label_en": "Nile River"},
                    {"id": "opt_b", "label_ar": "نَهْرُ دِجْلَةَ", "label_en": "Tigris River"},
                    {"id": "opt_c", "label_ar": "نَهْرُ السِّينِ", "label_en": "Seine River"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 12: لندن (London) — Unit 3: مدن عالمية
# Pages 18-27 in Student Book
# ============================================================================
LONDON_CONTENT = {
    "lesson_id": "lesson_12_london",
    "version": "0.2.0",
    "title_ar": "لندن",
    "title_en": "London",
    "unit_title_ar": "مدن عالمية",
    "unit_title_en": "Global Cities",
    "grade": 5,
    "term": 2,
    "start_page": 18,
    "pdf_start_page": 18,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس لندن",
        "title_en": "Preparation Check: London & Travel Vocabulary",
        "description_en": "Checks basic international geography and transport concepts.",
        "questions": [
            {
                "id": "prep_ld_01",
                "prompt_ar": "بِمَاذَا تُعْرَفُ مَدِينَةُ لَنْدَنَ عَالَمِيًّا؟",
                "prompt_en": "What nickname is London globally known for?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَدِينَةُ الضَّبَابِ", "label_en": "The City of Fog"},
                    {"id": "opt_b", "label_ar": "مَدِينَةُ الشَّمْسِ", "label_en": "The City of Sun"},
                    {"id": "opt_c", "label_ar": "مَدِينَةُ الذَّهَبِ", "label_en": "The City of Gold"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "London is famously known as the City of Fog (مدينة الضباب) due to historical mist and weather."
            },
            {
                "id": "prep_ld_02",
                "prompt_ar": "مَا هُوَ اسْمُ النَّهْرِ الشَّهِيرِ الَّذِي يَمُرُّ فِي وَسَطِ لَنْدَنَ؟",
                "prompt_en": "What is the famous river running through central London?",
                "options": [
                    {"id": "opt_a", "label_ar": "نَهْرُ التَّيْمْزِ", "label_en": "Thames River"},
                    {"id": "opt_b", "label_ar": "نَهْرُ النِّيلِ", "label_en": "Nile River"},
                    {"id": "opt_c", "label_ar": "نَهْرُ الأَمَازُونِ", "label_en": "Amazon River"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The River Thames (نهر التيمز) flows through London."
            },
            {
                "id": "prep_ld_03",
                "prompt_ar": "مَا مَعْنَى كَلِمَة (المُغْتَرِب)؟",
                "prompt_en": "What is the meaning of the word 'al-mughtarib' (expatriate)?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَنْ سَافَرَ عَنْ وَطَنِهِ لِلعَمَلِ أَوِ الدِّرَاسَةِ", "label_en": "One who travels from homeland for work or study"},
                    {"id": "opt_b", "label_ar": "مَنْ يَعِيشُ فِي وَطَنِهِ دَائِمًا", "label_en": "One who always lives in homeland"},
                    {"id": "opt_c", "label_ar": "قَبْطَانُ السَّفِينَةِ", "label_en": "Ship captain"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "المغترب refers to someone living abroad away from their native country."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary matching with London landmarks (Big Ben, London Eye, red buses).",
            "target": "Master core 6 terms: ضباب، مغترب، تحديات، تنوع، نصيحة، فرص."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Sentence building with prepositions and conjunctions (و، فـ، ثم).",
            "target": "Describe transport and daily life in London using temporal adverbs."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Write an advice letter to an Emirati student traveling abroad to study.",
            "target": "Compose a structured advisory essay tackling cultural diversity and study tips."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَمِعُ",
            "transliteration": "Astami'u",
            "meaning_en": "I listen",
            "action_guidance": "Listen to the travel audio guide describing the City of Fog.",
            "sample_sentence_ar": "أَسْتَمِعُ إِلَى حَقَائِقَ عَنْ مَدِينَةِ الضَّبَابِ.",
            "sample_sentence_en": "I listen to facts about the City of Fog."
        },
        {
            "verb_ar": "أُعَمِّقُ فَهْمِي",
            "transliteration": "U'ammiqu Fahmi",
            "meaning_en": "I deepen my understanding",
            "action_guidance": "Answer comprehension questions about expatriate experiences.",
            "sample_sentence_ar": "أُعَمِّقُ فَهْمِي لِحَيَاةِ الطُّلَّابِ فِي لَنْدَنَ.",
            "sample_sentence_en": "I deepen my understanding of student life in London."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_ld_01",
            "word_ar": "الضَّبَابُ",
            "vowelled_ar": "الضَّبَابُ",
            "meaning_en": "Fog / Mist",
            "definition_ar": "رَذَاذُ المَاءِ المُتَصَاعِدُ يُغَطِّي الأَرْضَ.",
            "example_ar": "تَأَخَّرَتِ الرِّحْلَةُ الجَوِّيَّةُ بِسَبَبِ الضَّبَابِ الكَثِيفِ.",
            "example_en": "The flight was delayed due to thick fog.",
            "root": "ض-ب-ب",
            "category": "weather"
        },
        {
            "id": "vocab_ld_02",
            "word_ar": "المُغْتَرِبُ",
            "vowelled_ar": "المُغْتَرِبُ",
            "meaning_en": "Expatriate / Living Abroad",
            "definition_ar": "مَنْ سَافَرَ بَعِيدًا عَنْ وَطَنِهِ.",
            "example_ar": "أَخِي مُغْتَرِبٌ فِي بَرِيطَانْيَا لِدِرَاسَةِ الطِّبِّ.",
            "example_en": "My brother is living abroad in Britain to study medicine.",
            "root": "غ-ر-ب",
            "category": "lifestyle"
        },
        {
            "id": "vocab_ld_03",
            "word_ar": "التَّحَدِّيَاتُ",
            "vowelled_ar": "التَّحَدِّيَاتُ",
            "meaning_en": "Challenges / Obstacles",
            "definition_ar": "الصُّعُوبَاتُ الَّتِي يَتَغَلَّبُ عَلَيْهَا الإِنْسَانُ.",
            "example_ar": "يَتَحَقَّقُ النَّجَاحُ بِالصَّبْرِ وَمُوَاجَهَةِ التَّحَدِّيَاتِ.",
            "example_en": "Success is achieved with patience and facing challenges.",
            "root": "ح-د-ي",
            "category": "academic"
        },
        {
            "id": "vocab_ld_04",
            "word_ar": "التَّنَوُّعُ",
            "vowelled_ar": "التَّنَوُّعُ",
            "meaning_en": "Diversity / Variety",
            "definition_ar": "الاخْتِلَافُ وَالتَّعَدُّدُ الإِيجَابِيُّ.",
            "example_ar": "تَتَمَيَّزُ لَنْدَنُ بِالتَّنَوُّعِ الثَّقَافِيِّ الكَبِيرِ.",
            "example_en": "London is characterized by great cultural diversity.",
            "root": "ن-و-ع",
            "category": "culture"
        },
        {
            "id": "vocab_ld_05",
            "word_ar": "فُرَصٌ",
            "vowelled_ar": "فُرَصٌ",
            "meaning_en": "Opportunities",
            "definition_ar": "مُفْرَدُهَا فُرْصَةٌ، وَهِيَ الوَقْتُ المُنَاسِبُ لِلنَّجَاحِ.",
            "example_ar": "المُدُنُ الكَبِيرَةُ تُوَفِّرُ فُرَصًا لِلتَّعَلُّمِ.",
            "example_en": "Big cities offer opportunities for learning.",
            "root": "ف-ر-ص",
            "category": "general"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: حروف العطف وظروف المكان",
        "title_en": "Grammar Lab: Conjunctions (و، فـ، ثم) and Adverbs of Place",
        "sections": [
            {
                "rule_name_ar": "حروف العطف (الواو، الفاء، ثُمَّ)",
                "rule_name_en": "Conjunctions: Wa (and), Fa (immediate sequence), Thumma (delayed sequence)",
                "explanation_en": "Connects words or sentences. 'Wa' indicates partnership; 'Fa' immediate succession; 'Thumma' succession with time lapse.",
                "examples": [
                    {"phrase_ar": "زُرْتُ سَاعَةَ بِيغْ بِنْ ثُمَّ رَكِبْتُ القَطَارَ.", "translation_en": "I visited Big Ben then rode the train."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: يوم في لندن",
        "title_en": "Sentence Construction Studio: A Day in London",
        "challenges": [
            {
                "id": "sb_ld_01",
                "instruction_en": "Arrange the words to form a sentence about London transport:",
                "target_sentence_ar": "رَكِبَ الطُّلَّابُ الحَافِلَةَ الحَمْرَاءَ لِمُشَاهَدَةِ نَهْرِ التَّيْمْزِ.",
                "scrambled_tokens": ["الحَمْرَاءَ", "نَهْرِ", "رَكِبَ", "لِمُشَاهَدَةِ", "الطُّلَّابُ", "التَّيْمْزِ.", "الحَافِلَةَ"],
                "translation_en": "The students boarded the red bus to see the River Thames."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: معالم لندن الشهيرة",
        "title_en": "Listen & Speak Studio: Landmarks of London",
        "passage_ar": "تُعْتَبَرُ مَدِينَةُ لَنْدَنَ إِحْدَى أَهَمِّ العَوَاصِمِ العَالَمِيَّةِ. تَشْتَهِرُ بِسَاعَةِ بِيغْ بِنْ التَّارِيخِيَّةِ، وَعَجَلَةِ عَيْنِ لَنْدَنَ الَّتِي تَمْنَحُ الرَّاكِبَ مَنْظَرًا بَانُورَامِيًّا لِنَهْرِ التَّيْمْزِ، وَالحَافِلَاتِ الحَمْرَاءِ ذَاتِ الطَّابَقَيْنِ.",
        "passage_en": "London is one of the most prominent world capitals. It is famous for historic Big Ben clock, London Eye observation wheel with panoramic views of River Thames, and iconic red double-decker buses.",
        "audio_scripts": [
            {"id": "aud_ld_01", "text_ar": "مَدِينَةُ لَنْدَنَ تَجْمَعُ بَيْنَ العَرَاقَةِ وَالتَّطَوُّرِ.", "text_en": "The city of London combines antiquity with modern progress."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_ld_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: معالم مدينة الضباب",
            "title_en": "Reading Comprehension: Fog City Landmarks",
            "prompt_ar": "مَا هِيَ العَجَلَةُ السَّيَاحِيَّةُ المَشْهُورَةُ فِي لَنْدَنَ؟",
            "prompt_en": "What is the famous tourist observation wheel in London?",
            "options": [
                {"id": "opt_a", "label_ar": "عَيْنُ لَنْدَنَ (London Eye)", "label_en": "London Eye"},
                {"id": "opt_b", "label_ar": "عَيْنُ دُبَي (Ain Dubai)", "label_en": "Ain Dubai"},
                {"id": "opt_c", "label_ar": "سَاعَةُ مَكَّةَ", "label_en": "Makkah Clock"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: نصيحة لطالب مغترب",
        "title_en": "Speaking Mission: Advice to a Student Abroad",
        "scenario_en": "Record a 30-second encouraging message to your cousin who just traveled to London to study, offering advice on coping with weather and embracing learning opportunities.",
        "prompts_ar": [
            "أَتَمَنَّى لَكَ التَّوْفِيقَ فِي دِرَاسَتِكَ فِي لَنْدَنَ.",
            "احْرِصْ عَلَى اسْتِغْلَالِ الفُرَصِ وَالتَّعَرُّفِ عَلَى الثَّقَافَاتِ.",
            "لَا تَقْلَقْ مِنَ الضَّبَابِ وَالأَمْطَارِ، فَهِيَ مَدِينَةٌ جَمِيلَةٌ."
        ],
        "recording_task_en": "Speak clearly with positive encouraging tone in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس لندن",
        "title_en": "Parent Companion: London Lesson",
        "summary_en": "Introduces world capitals, weather vocabulary (ضباب), life abroad (مغترب), and conjunctions (و، فـ، ثم).",
        "dinner_table_prompts": [
            {"arabic": "مَا هُوَ اسْمُ النَّهْرِ فِي لَنْدَنَ؟", "english": "What is the river in London?", "phonetic": "Ma huwa ism an-nahr fee London?"}
        ],
        "home_practice_checklist": [
            "Discuss how students study abroad and what challenges they face.",
            "Review conjunction words: و (wa), فـ (fa), ثم (thumma)."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس لندن",
        "learning_objectives": ["Understand London geography and landmarks", "Master conjunction particle sequencing (ثم vs فـ)", "Expand travel vocabulary"],
        "misconception_flags": ["Confusing then (ثم with delay) with immediately (فـ)"],
        "recommended_drills": ["Conjunction ordering sentences", "Landmark flashcards"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_ld_01",
                "prompt_ar": "يُسَمَّى رَذَاذُ المَاءِ مَعَ الغُبَارِ الَّذِي يُغَطِّي الأَرْضَ:",
                "prompt_en": "Water vapor and mist covering the ground is called:",
                "options": [
                    {"id": "opt_a", "label_ar": "الضَّبَابَ", "label_en": "Fog / Mist"},
                    {"id": "opt_b", "label_ar": "الصَّحْرَاءَ", "label_en": "Desert"},
                    {"id": "opt_c", "label_ar": "البَحْرَ", "label_en": "Sea"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 13: شنغهاي (Shanghai) — Unit 3: مدن عالمية
# Pages 28-37 in Student Book
# ============================================================================
SHANGHAI_CONTENT = {
    "lesson_id": "lesson_13_shanghai",
    "version": "0.2.0",
    "title_ar": "شنغهاي",
    "title_en": "Shanghai",
    "unit_title_ar": "مدن عالمية",
    "unit_title_en": "Global Cities",
    "grade": 5,
    "term": 2,
    "start_page": 28,
    "pdf_start_page": 28,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس شنغهاي",
        "title_en": "Preparation Check: Shanghai & Asian Hubs",
        "description_en": "Checks knowledge of global commerce, ports, and technology.",
        "questions": [
            {
                "id": "prep_sh_01",
                "prompt_ar": "فِي أَيِّ دَوْلَةٍ تَقَعُ مَدِينَةُ شَنْغَهَاي؟",
                "prompt_en": "In which country is the city of Shanghai located?",
                "options": [
                    {"id": "opt_a", "label_ar": "دَوْلَةِ الصِّينِ", "label_en": "China"},
                    {"id": "opt_b", "label_ar": "دَوْلَةِ الهِنْدِ", "label_en": "India"},
                    {"id": "opt_c", "label_ar": "دَوْلَةِ اليَابَانِ", "label_en": "Japan"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Shanghai is the largest economic metropolis in China (الصين)."
            },
            {
                "id": "prep_sh_02",
                "prompt_ar": "مَا هُوَ البُرْجُ الشَّهِيرُ فِي شَنْغَهَاي الَّذِي يُشْبِهُ اللُّؤْلُؤَةَ؟",
                "prompt_en": "What is the famous Shanghai tower nicknamed the Pearl?",
                "options": [
                    {"id": "opt_a", "label_ar": "بُرْجُ لُؤْلُؤَةِ الشَّرْقِ", "label_en": "Oriental Pearl Tower"},
                    {"id": "opt_b", "label_ar": "بُرْجُ إِيفِل", "label_en": "Eiffel Tower"},
                    {"id": "opt_c", "label_ar": "بُرْجُ بِيَزَا", "label_en": "Leaning Tower of Pisa"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The Oriental Pearl Tower (برج لؤلؤة الشرق) is Shanghai's most recognized skyline monument."
            },
            {
                "id": "prep_sh_03",
                "prompt_ar": "مَا هُوَ الفُنْدُقُ الرَّاقِي جِدًّا حَسَبَ تَصْنِيفِ النُّجُومِ؟",
                "prompt_en": "What is a luxury hotel called according to star ratings?",
                "options": [
                    {"id": "opt_a", "label_ar": "فُنْدُقُ خَمْسِ نُجُومٍ", "label_en": "Five-star hotel"},
                    {"id": "opt_b", "label_ar": "فُنْدُقُ نَجْمَةٍ وَاحِدَةٍ", "label_en": "One-star hotel"},
                    {"id": "opt_c", "label_ar": "نَزْلٌ قَدِيمٌ", "label_en": "Old hostel"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "فندق خمس نجوم signifies high quality and premium hospitality services."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Interactive matching of commercial and hotel terms with pictures.",
            "target": "Recognize vocabulary: إقامة، ترفيه، وفد، تصفح، خمس نجوم."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Comparative structure practice (أسرع، أكبر، أعلى).",
            "target": "Form comparative sentences about Shanghai's high-speed train and skyline."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Design a complete hotel booking dialog and commercial trade overview.",
            "target": "Draft a travel article evaluating Shanghai's modern public transport and riverside sights."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَصَفَّحُ",
            "transliteration": "Atasaffahu",
            "meaning_en": "I browse / skim through",
            "action_guidance": "Skim through news articles or magazines to find information quickly.",
            "sample_sentence_ar": "أَتَصَفَّحُ جَرِيدَةَ الصَّبَاحِ لِمَعْرِفَةِ أَخْبَارِ التِّجَارَةِ.",
            "sample_sentence_en": "I browse the morning paper to learn business news."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_sh_01",
            "word_ar": "الإِقَامَةُ",
            "vowelled_ar": "الإِقَامَةُ",
            "meaning_en": "Stay / Residence",
            "definition_ar": "البَقَاءُ فِي مَكَانٍ مُحَدَّدٍ كَالفُنْدُقِ.",
            "example_ar": "حَجَزْنَا الإِقَامَةَ فِي فُنْدُقٍ قَرِيبٍ مِنَ النَّهْرِ.",
            "example_en": "We booked accommodation in a hotel near the river.",
            "root": "ق-و-م",
            "category": "travel"
        },
        {
            "id": "vocab_sh_02",
            "word_ar": "التَّرْفِيهُ",
            "vowelled_ar": "التَّرْفِيهُ",
            "meaning_en": "Entertainment / Leisure",
            "definition_ar": "التَّسْلِيَةُ وَالمَرَحُ وَقَضَاءُ وَقْتٍ مُمْتِعٍ.",
            "example_ar": "تَضُمُّ شَنْغَهَاي مَرَاكِزَ تَرْفِيهٍ حَدِيثَةً لِلأَطْفَالِ.",
            "example_en": "Shanghai includes modern entertainment centers for children.",
            "root": "ر-ف-ه",
            "category": "lifestyle"
        },
        {
            "id": "vocab_sh_03",
            "word_ar": "الوَفْدُ",
            "vowelled_ar": "الوَفْدُ",
            "meaning_en": "Delegation / Official Group",
            "definition_ar": "جَمَاعَةٌ مِنَ النَّاسِ تُمَثِّلُ دَوْلَةً أَوْ شَرِكَةً.",
            "example_ar": "وَصَلَ الوَفْدُ التِّجَارِيُّ الإِمَارَاتِيُّ إِلَى شَنْغَهَاي.",
            "example_en": "The Emirati trade delegation arrived in Shanghai.",
            "root": "و-ف-د",
            "category": "business"
        },
        {
            "id": "vocab_sh_04",
            "word_ar": "خَمْسُ نُجُومٍ",
            "vowelled_ar": "خَمْسُ نُجُومٍ",
            "meaning_en": "Five Stars (Premium Rating)",
            "definition_ar": "مِعْيَارٌ عَالَمِيٌّ لِتَصْنِيفِ الفَنَادِقِ المُمْتَازَةِ.",
            "example_ar": "أَقَامَ السَّائِحُ فِي فُنْدُقٍ خَمْسِ نُجُومٍ فَخْمٍ.",
            "example_en": "The tourist stayed in a luxurious five-star hotel.",
            "root": "ن-ج-م",
            "category": "travel"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: اسم التفضيل (أَفْعَلُ التَّفْضِيل)",
        "title_en": "Grammar Lab: Superlative and Comparative Form (Af'alu)",
        "sections": [
            {
                "rule_name_ar": "اسم التفضيل (أكبر، أسرع، أحدث)",
                "rule_name_en": "Superlative / Comparative Pattern (أَفْعَل)",
                "explanation_en": "Used to compare two entities sharing a quality, where one exceeds the other. Pattern: أَفْعَل + مِنْ.",
                "examples": [
                    {"phrase_ar": "قِطَارُ شَنْغَهَاي أَسْرَعُ قِطَارٍ فِي العَالَمِ.", "translation_en": "Shanghai train is the fastest train in the world."},
                    {"phrase_ar": "بُرْجُ خَلِيفَةَ أَعْلَى مِنْ بُرْجِ لُؤْلُؤَةِ الشَّرْقِ.", "translation_en": "Burj Khalifa is taller than the Oriental Pearl Tower."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: قطارات وأبراج شنغهاي",
        "title_en": "Sentence Construction Studio: High-Tech Shanghai",
        "challenges": [
            {
                "id": "sb_sh_01",
                "instruction_en": "Arrange the words to describe Shanghai's high-speed train:",
                "target_sentence_ar": "يَسِيرُ قِطَارُ المَاغْلِيفِ بِسُرْعَةٍ فَائِقَةٍ دُونَ أَنْ يَلْمِسَ السِّكَّةَ.",
                "scrambled_tokens": ["فَائِقَةٍ", "السِّكَّةَ.", "المَاغْلِيفِ", "يَسِيرُ", "بِسُرْعَةٍ", "يَلْمِسَ", "قِطَارُ", "دُونَ", "أَنْ"],
                "translation_en": "The Maglev train runs at extreme speed without touching the track."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: شَنْغَهَاي مَدِينَةُ المُسْتَقْبَلِ",
        "title_en": "Listen & Speak Studio: Shanghai City of the Future",
        "passage_ar": "شَنْغَهَاي هِيَ المَرْكَزُ المَالِيُّ وَالصِّنَاعِيُّ الأَكْبَرُ فِي الصِّينِ. تَقَعُ عَلَى ضَفَافِ نَهْرِ هَوَانْغْبُو، وَتَتَمَيَّزُ بِبُرْجِ لُؤْلُؤَةِ الشَّرْقِ وَالمَرْكَزِ المَالِيِّ العَالَمِيِّ، وَالقِطَارِ المَغْنَاطِيسِيِّ السَّرِيعِ الَّذِي يَرْبِطُ المَطَارَ بِقَلْبِ المَدِينَةِ فِي سَبْعِ دَقَائِقَ فَقَطْ.",
        "passage_en": "Shanghai is the largest financial and manufacturing hub in China. Located along the banks of the Huangpu River, it boasts the Oriental Pearl Tower, World Financial Center, and high-speed magnetic levitation train connecting the airport to the city center in just seven minutes.",
        "audio_scripts": [
            {"id": "aud_sh_01", "text_ar": "مَدِينَةُ شَنْغَهَاي زَاخِرَةٌ بِالتِّجَارَةِ وَالتِّكْنُولُوجْيَا.", "text_en": "Shanghai is bustling with commerce and technology."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_sh_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: قطار شنغهاي المغناطيسي",
            "title_en": "Reading Comprehension: Maglev Train",
            "prompt_ar": "كَمْ يَسْتَغْرِقُ قِطَارُ المَاغْلِيفِ لِلْوُصُولِ مِنْ المَطَارِ إِلَى المَدِينَةِ؟",
            "prompt_en": "How long does the Maglev train take from the airport to the city?",
            "options": [
                {"id": "opt_a", "label_ar": "سَبْعَ دَقَائِقَ فَقَطْ", "label_en": "Only seven minutes"},
                {"id": "opt_b", "label_ar": "سَاعَتَيْنِ كَامِلَتَيْنِ", "label_en": "Two full hours"},
                {"id": "opt_c", "label_ar": "يَوْمًا كَامِلًا", "label_en": "A full day"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: حجز فندقي في شنغهاي",
        "title_en": "Speaking Mission: Hotel Booking Dialog in Arabic",
        "scenario_en": "Roleplay calling a hotel in Shanghai to book a room for 3 nights for your family. State arrival date, room preference, and inquire about breakfast.",
        "prompts_ar": [
            "مَرْحَبًا، أُرِيدُ حَجْزَ غُرْفَةٍ لِعَائِلَتِي لِمُدَّةِ ثَلَاثِ لَيَالٍ.",
            "هَلْ يَشْمَلُ الحَجْزُ وَجْبَةَ الإِفْطَارِ الصَّبَاحِيِّ؟",
            "أَفَضِّلُ غُرْفَةً مُطِلَّةً عَلَى نَهْرِ هَوَانْغْبُو."
        ],
        "recording_task_en": "Record 30 seconds of courteous Arabic hotel booking inquiry."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس شنغهاي",
        "title_en": "Parent Companion: Shanghai Lesson",
        "summary_en": "Focuses on technology, commerce, hotel star rating, and comparative adjectives (أسرع، أكبر).",
        "dinner_table_prompts": [
            {"arabic": "مَا هُوَ أَسْرَعُ قِطَارٍ فِي العَالَمِ؟", "english": "What is the fastest train in the world?", "phonetic": "Ma huwa asra' qitar fee al-'alam?"}
        ],
        "home_practice_checklist": [
            "Practice comparing objects around the house with 'Asra' (أسرع) and 'Akbar' (أكبر)."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس شنغهاي",
        "learning_objectives": ["Understand high-speed transit vocabulary", "Master superlative/comparative pattern أفعَل", "Conduct simple travel transactions"],
        "misconception_flags": ["Using 'more fast' translation instead of native morphological pattern أسرع"],
        "recommended_drills": ["Comparative adjective drills (طويل -> أطول, سريع -> أسرع)"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_sh_01",
                "prompt_ar": "صِيغَةُ التَّفْضِيلِ مِنْ كَلِمَةِ (سَرِيع) هِيَ:",
                "prompt_en": "The superlative/comparative form of 'سريع' (fast) is:",
                "options": [
                    {"id": "opt_a", "label_ar": "أَسْرَعُ", "label_en": "Faster / Fastest (Asra')"},
                    {"id": "opt_b", "label_ar": "مُسْرِعٌ", "label_en": "Speeding (Musri')"},
                    {"id": "opt_c", "label_ar": "سُرْعَةٌ", "label_en": "Speed (Sur'ah)"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 14: عجائب الدنيا السبع (Seven Wonders) — Unit 4: غرائب وعجائب
# Pages 38-47 in Student Book
# ============================================================================
SEVEN_WONDERS_CONTENT = {
    "lesson_id": "lesson_14_seven_wonders",
    "version": "0.2.0",
    "title_ar": "عجائب الدنيا السبع",
    "title_en": "Seven Wonders of the World",
    "unit_title_ar": "غرائب وعجائب",
    "unit_title_en": "Oddities and Wonders",
    "grade": 5,
    "term": 2,
    "start_page": 38,
    "pdf_start_page": 38,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس عجائب الدنيا السبع",
        "title_en": "Preparation Check: Wonders of the World",
        "description_en": "Checks understanding of historical architecture and ancient achievements.",
        "questions": [
            {
                "id": "prep_sw_01",
                "prompt_ar": "مَا هُوَ المَعْلَمُ العَظِيمُ الَّذِي يَمْتَدُّ لآلَافِ الكِيلُومِتْرَاتِ فِي الصِّينِ؟",
                "prompt_en": "What great landmark stretches for thousands of kilometers in China?",
                "options": [
                    {"id": "opt_a", "label_ar": "سُورُ الصِّينِ العَظِيمُ", "label_en": "Great Wall of China"},
                    {"id": "opt_b", "label_ar": "بُرْجُ إِيفِل", "label_en": "Eiffel Tower"},
                    {"id": "opt_c", "label_ar": "الأَهْرَامَاتُ", "label_en": "Pyramids"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The Great Wall of China (سور الصين العظيم) is an engineering wonder stretching over 2,400 km."
            },
            {
                "id": "prep_sw_02",
                "prompt_ar": "مَا مَعْنَى كَلِمَة (الإِبْدَاع)؟",
                "prompt_en": "What is the meaning of 'al-ibda' (creativity / innovation)?",
                "options": [
                    {"id": "opt_a", "label_ar": "ابْتِكَارُ شَيْءٍ جَدِيدٍ وَفَرِيدٍ", "label_en": "Creating something new and unique"},
                    {"id": "opt_b", "label_ar": "تَقْلِيدُ الآخَرِينَ", "label_en": "Imitating others"},
                    {"id": "opt_c", "label_ar": "النَّوْمُ الطَّوِيلُ", "label_en": "Long sleep"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "الإبداع signifies creating something uniquely original and masterful."
            },
            {
                "id": "prep_sw_03",
                "prompt_ar": "مَا هُوَ التَّشْبِيهُ المُنَاسِبُ لِلسُّورِ الَّذِي يَتَعَرَّجُ بَيْنَ الجِبَالِ؟",
                "prompt_en": "What is a fitting metaphor for a wall winding through mountains?",
                "options": [
                    {"id": "opt_a", "label_ar": "تِنِّينٌ أُسْطُورِيٌّ يَتَلَوَّى فَوْقَ القِمَمِ", "label_en": "A mythical dragon winding over peaks"},
                    {"id": "opt_b", "label_ar": "سَفِينَةٌ فِي البَحْرِ", "label_en": "A ship at sea"},
                    {"id": "opt_c", "label_ar": "طَائِرَةٌ فِي السَّمَاءِ", "label_en": "An airplane in the sky"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The textbook compares the Great Wall to a mythical dragon winding over rugged peaks."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary drills on architectural terms: إبداع، عظيم، معارك، حصن.",
            "target": "Identify key historical facts about the Great Wall and Pyramids."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Practice crafting poetic similes (التشبيه: كاف التشبيه).",
            "target": "Construct descriptive sentences employing (كـ / مِثْل) to describe monumental structures."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Analytical essay on preserving world cultural heritage for future generations.",
            "target": "Write a 3-paragraph investigative report on how engineering wonders were constructed."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُشَبِّهُ",
            "transliteration": "Ushabbihu",
            "meaning_en": "I compare / create a simile",
            "action_guidance": "Connect two different things sharing a striking characteristic.",
            "sample_sentence_ar": "أُشَبِّهُ سُورَ الصِّينِ بِالتِّنِّينِ الأُسْطُورِيِّ.",
            "sample_sentence_en": "I compare the Great Wall to a mythical dragon."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_sw_01",
            "word_ar": "الإِبْدَاعُ",
            "vowelled_ar": "الإِبْدَاعُ",
            "meaning_en": "Creativity / Innovation",
            "definition_ar": "إِيجَادُ شَيْءٍ فَرِيدٍ وَمُبْتَكَرٍ.",
            "example_ar": "تَدُلُّ عَجَائِبُ الدُّنْيَا عَلَى إِبْدَاعِ الإِنْسَانِ القَدِيمِ.",
            "example_en": "Wonders of the world demonstrate ancient human creativity.",
            "root": "ب-د-ع",
            "category": "arts"
        },
        {
            "id": "vocab_sw_02",
            "word_ar": "عَظِيمٌ",
            "vowelled_ar": "عَظِيمٌ",
            "meaning_en": "Grand / Magnificent",
            "definition_ar": "هَائِلٌ وَفَخْمٌ وَذُو شَأْنٍ كَبِيرٍ.",
            "example_ar": "مَا أَجْمَلَ سُورَ الصِّينِ العَظِيمَ!",
            "example_en": "How magnificent is the Great Wall of China!",
            "root": "ع-ظ-م",
            "category": "descriptive"
        },
        {
            "id": "vocab_sw_03",
            "word_ar": "المَعَارِكُ",
            "vowelled_ar": "المَعَارِكُ",
            "meaning_en": "Battles / Historic Conflicts",
            "definition_ar": "مُفْرَدُهَا مَعْرَكَةٌ، وَهِيَ الحُرُوبُ الدِّفَاعِيَّةُ.",
            "example_ar": "شَهِدَ هَذَا الحِصْنُ العَدِيدَ مِنَ المَعَارِكِ الدِّفَاعِيَّةِ.",
            "example_en": "This fortress witnessed numerous defensive battles.",
            "root": "ع-ر-ك",
            "category": "history"
        },
        {
            "id": "vocab_sw_04",
            "word_ar": "الخَطُّ المُلْتَوِي",
            "vowelled_ar": "الخَطُّ المُلْتَوِي",
            "meaning_en": "Winding / Zigzag Path",
            "definition_ar": "الطَّرِيقُ المُتَعَرِّجُ غَيْرُ المُسْتَقِيمِ.",
            "example_ar": "صُمِّمَ السُّورُ عَلَى شَكْلِ خَطٍّ مُلْتَوٍ بَيْنَ التِّلَالِ.",
            "example_en": "The wall was designed as a winding path between hills.",
            "root": "ل-و-ي",
            "category": "shapes"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: أسلوب التشبيه البلاغي",
        "title_en": "Grammar Lab: Rhetorical Similes (التشبيه بالكاف ومثل)",
        "sections": [
            {
                "rule_name_ar": "أركان التشبيه (المشبه، المشبه به، أداة التشبيه)",
                "rule_name_en": "Elements of Simile: Subject, Reference, Particle (كـ / مِثْل)",
                "explanation_en": "Connecting two things sharing a common trait using the prefix 'Ka-' (كـ) or 'Mithl' (مِثْل).",
                "examples": [
                    {"phrase_ar": "السُّورُ كَالتِّنِّينِ فِي تَوَاؤِهِ.", "translation_en": "The wall is like a dragon in its winding curves."},
                    {"phrase_ar": "قَلْبُ الفَارِسِ كَالصَّخْرِ فِي الشَّجَاعَةِ.", "translation_en": "The knight's heart is like rock in courage."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: بناء العجائب الهندسية",
        "title_en": "Sentence Construction Studio: Architectural Feats",
        "challenges": [
            {
                "id": "sb_sw_01",
                "instruction_en": "Arrange the words to describe the Great Wall:",
                "target_sentence_ar": "يَبْلُغُ طُولُ سُورِ الصِّينِ العَظِيمِ أَلْفَيْنِ وَأَرْبَعَمِائَةِ كِيلُومِتْرٍ.",
                "scrambled_tokens": ["العَظِيمِ", "طُولُ", "سُورِ", "يَبْلُغُ", "الصِّينِ", "كِيلُومِتْرٍ.", "وَأَرْبَعَمِائَةِ", "أَلْفَيْنِ"],
                "translation_en": "The length of the Great Wall reaches 2,400 kilometers."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: قصة بناء سور الصين العظيم",
        "title_en": "Listen & Speak Studio: The Story of the Great Wall",
        "passage_ar": "تَمَّ اخْتِيَارُ سُورِ الصِّينِ العَظِيمِ مِنْ عَجَائِبِ الدُّنْيَا السَّبْعِ الجَدِيدَةِ؛ لِأَنَّهُ أَعْظَمُ بِحِثٍ هَنْدَسِيٍّ دِفَاعِيٍّ فِي التَّارِيخِ. شَارَكَ فِي بِنَائِهِ مَلَايِينُ العُمَّالِ عَبْرَ أَجْيَالٍ مُتَعَاقِبَةٍ، وَيَتَكَوَّنُ مِنْ أَبْرَاجِ مُرَاقَبَةٍ وَمَمَرَّاتٍ طَوِيلَةٍ تَحْمِي البِلَادَ.",
        "passage_en": "The Great Wall of China was chosen among the New Seven Wonders because it is the greatest defensive engineering construction in history. Millions of workers took part in its building across generations, comprising watchtowers and vast pathways protecting the land.",
        "audio_scripts": [
            {"id": "aud_sw_01", "text_ar": "عَجَائِبُ الدُّنْيَا شَاهِدَةٌ عَلَى هِمَّةِ الشُّعُوبِ.", "text_en": "Wonders of the world bear witness to human determination."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_sw_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: طول سور الصين العظيم",
            "title_en": "Reading Comprehension: Length of Great Wall",
            "prompt_ar": "كَمْ يَبْلُغُ طُولُ سُورِ الصِّينِ العَظِيمِ تَقْرِيبًا؟",
            "prompt_en": "How long approximately is the Great Wall of China?",
            "options": [
                {"id": "opt_a", "label_ar": "2400 كِيلُومِتْرٍ تَقْرِيبًا", "label_en": "Approximately 2,400 km"},
                {"id": "opt_b", "label_ar": "100 كِيلُومِتْرٍ فَقَطْ", "label_en": "Only 100 km"},
                {"id": "opt_c", "label_ar": "50 كِيلُومِتْرٍ", "label_en": "50 km"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: عجيبة من عجائب الدنيا",
        "title_en": "Speaking Mission: Presenting a World Wonder",
        "scenario_en": "Speak for 30 seconds about your favorite ancient wonder (the Great Wall, Pyramids, or Hanging Gardens), explaining why it captures your imagination.",
        "prompts_ar": [
            "أُعْجِبْتُ بِسُورِ الصِّينِ العَظِيمِ لِأَنَّهُ تُحْفَةٌ هَنْدَسِيَّةٌ نَادِرَةٌ.",
            "يَتَمَيَّزُ هَذَا المَعْلَمُ بِطُولِهِ الشَّاهِقِ وَأَبْرَاجِ مُرَاقَبَتِهِ.",
            "مِنَ الوَاجِبِ حِمَايَةُ هَذِهِ الآثَارِ لِتَبْقَى شَاهِدَةً عَلَى الإِبْدَاعِ."
        ],
        "recording_task_en": "Record yourself using at least one simile (التشبيه) in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس عجائب الدنيا",
        "title_en": "Parent Companion: Seven Wonders Lesson",
        "summary_en": "Teaches world history, engineering feats (Great Wall), creative similes (كـ / مثل), and preservation vocabulary.",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ عَجِيبَتُكَ المُفَضَّلَةُ؟", "english": "What is your favorite world wonder?", "phonetic": "Ma hiya 'ajeebatuka al-mufaddalah?"}
        ],
        "home_practice_checklist": [
            "Explore a picture of the Great Wall together and spot the watchtowers.",
            "Help your child practice forming a simile with 'Ka-' (الثوب أبيض كالثلج)."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس عجائب الدنيا",
        "learning_objectives": ["Identify 7 Wonders milestones", "Construct rhetorical similes using كـ and مثل", "Describe scale and dimensions"],
        "misconception_flags": ["Confusing simile particle كـ with preposition of location"],
        "recommended_drills": ["Simile builder exercises", "Engineering history flashcards"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_sw_01",
                "prompt_ar": "فِي جُمْلَةِ (السُّورُ كَالتِّنِّينِ)، نَوْعُ الأُسْلُوبِ البَلَاغِيِّ هُوَ:",
                "prompt_en": "In the sentence 'The wall is like a dragon', the rhetorical style is:",
                "options": [
                    {"id": "opt_a", "label_ar": "أُسْلُوبُ تَشْبِيهٍ", "label_en": "Simile (Tashbeeh)"},
                    {"id": "opt_b", "label_ar": "أُسْلُوبُ اسْتِفْهَامٍ", "label_en": "Question style"},
                    {"id": "opt_c", "label_ar": "أُسْلُوبُ نَهْيٍ", "label_en": "Prohibition style"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 15: الكهوف والجزر (Caves and Islands) — Unit 4: غرائب وعجائب
# Pages 48-57 in Student Book
# ============================================================================
CAVES_AND_ISLANDS_CONTENT = {
    "lesson_id": "lesson_15_caves_and_islands",
    "version": "0.2.0",
    "title_ar": "الكهوف والجزر",
    "title_en": "Caves and Islands",
    "unit_title_ar": "غرائب وعجائب",
    "unit_title_en": "Oddities and Wonders",
    "grade": 5,
    "term": 2,
    "start_page": 48,
    "pdf_start_page": 48,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الكهوف والجزر",
        "title_en": "Preparation Check: Geological Wonders & Islands",
        "description_en": "Prerequisite diagnostic on caves, islands, and natural wonders.",
        "questions": [
            {
                "id": "prep_ci_01",
                "prompt_ar": "مَا هِيَ الجَزِيرَةُ؟",
                "prompt_en": "What is an island?",
                "options": [
                    {"id": "opt_a", "label_ar": "أَرْضٌ تُحِيطُ بِهَا المِيَاهُ مِنْ جَمِيعِ الجِهَاتِ", "label_en": "Land surrounded by water on all sides"},
                    {"id": "opt_b", "label_ar": "جَبَلٌ مُرْتَفِعٌ جِدًّا فِي الصَّحْرَاءِ", "label_en": "High mountain in the desert"},
                    {"id": "opt_c", "label_ar": "نَهْرٌ صَغِيرٌ فِي الغَابَةِ", "label_en": "Small river in forest"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "An island (جزيرة) is land completely surrounded by water."
            },
            {
                "id": "prep_ci_02",
                "prompt_ar": "مَا هُوَ شَكْلُ جُزُرِ النَّخْلَةِ الشَّهِيرَةِ فِي دُبَي؟",
                "prompt_en": "What is the shape of the famous Palm Islands in Dubai?",
                "options": [
                    {"id": "opt_a", "label_ar": "عَلَى شَكْلِ شَجَرَةِ نَخْلَةٍ", "label_en": "Shaped like a date palm tree"},
                    {"id": "opt_b", "label_ar": "عَلَى شَكْلِ مُرَبَّعٍ كَبِيرٍ", "label_en": "Shaped like a large square"},
                    {"id": "opt_c", "label_ar": "عَلَى شَكْلِ دَائِرَةٍ بَسِيطَةٍ", "label_en": "Shaped like a simple circle"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Palm Jumeirah in Dubai is engineered in the shape of a majestic date palm tree."
            },
            {
                "id": "prep_ci_03",
                "prompt_ar": "مَا ضِدُّ كَلِمَة (طَبِيعِيَّة)؟",
                "prompt_en": "What is the opposite of 'natural' (طبيعية)?",
                "options": [
                    {"id": "opt_a", "label_ar": "اصْطِنَاعِيَّةٌ", "label_en": "Artificial / Man-made"},
                    {"id": "opt_b", "label_ar": "جَمِيلَةٌ", "label_en": "Beautiful"},
                    {"id": "opt_c", "label_ar": "قَدِيمَةٌ", "label_en": "Old"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "The opposite of natural (طبيعية) is artificial/man-made (اصطناعية)."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Interactive pictures of glowing caves, stalactites, and man-made islands.",
            "target": "Master 6 core terms: كهف، جزيرة اصطناعية، الخليج العربي، سعف، اكتشاف."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Grammar training on the exclamatory style (أسلوب التعجب: ما أَفْعَلَ!).",
            "target": "Express wonder at nature using exclamations like (ما أغرب هذا الكهف!)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Narrate an adventurous exploration journey into an underground river cave.",
            "target": "Draft a creative story recounting spelunking in bioluminescent glowworm caves."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَعَجَّبُ",
            "transliteration": "Ata'ajjabu",
            "meaning_en": "I express wonder / exclaim",
            "action_guidance": "Use 'Ma af'ala!' to express admiration of strange natural beauty.",
            "sample_sentence_ar": "أَتَعَجَّبُ مِنْ جَمَالِ الجَزِيرَةِ: مَا أَرْوَعَ هَذِهِ الجَزِيرَةَ!",
            "sample_sentence_en": "I marvel at the island's beauty: How wonderful is this island!"
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_ci_01",
            "word_ar": "الخَلِيجُ العَرَبِيُّ",
            "vowelled_ar": "الخَلِيجُ العَرَبِيُّ",
            "meaning_en": "Arabian Gulf",
            "definition_ar": "مِسَاحَةٌ مَائِيَّةٌ تَحْتَضِنُ شَوَاطِئَ دَوْلَةِ الإِمَارَاتِ.",
            "example_ar": "تَقَعُ جُزُرُ النَّخْلَةِ فِي مِيَاهِ الخَلِيجِ العَرَبِيِّ.",
            "example_en": "The Palm Islands are situated in the waters of the Arabian Gulf.",
            "root": "خ-ل-ج",
            "category": "geography"
        },
        {
            "id": "vocab_ci_02",
            "word_ar": "اصْطِنَاعِيَّةٌ",
            "vowelled_ar": "اصْطِنَاعِيَّةٌ",
            "meaning_en": "Artificial / Man-Made",
            "definition_ar": "مَا صَنَعَهُ الإِنْسَانُ وَلَيْسَ مِنْ أَصْلِ الطَّبِيعَةِ.",
            "example_ar": "تُعَدُّ نَخْلَةُ جُمَيْرَا جَزِيرَةً اصْطِنَاعِيَّةً مُبْهِرَةً.",
            "example_en": "Palm Jumeirah is a dazzling man-made island.",
            "root": "ص-ن-ع",
            "category": "engineering"
        },
        {
            "id": "vocab_ci_03",
            "word_ar": "السَّعَفُ",
            "vowelled_ar": "السَّعَفُ",
            "meaning_en": "Palm Fronds",
            "definition_ar": "أَوْرَاقُ النَّخْلِ الخَضْرَاءُ الطَّوِيلَةُ.",
            "example_ar": "صُمِّمَتْ فُرُوعُ الجَزِيرَةِ عَلَى شَكْلِ سَعَفِ النَّخِيلِ.",
            "example_en": "The island's branches were designed like date palm fronds.",
            "root": "س-ع-ف",
            "category": "nature"
        },
        {
            "id": "vocab_ci_04",
            "word_ar": "الاكْتِشَافُ",
            "vowelled_ar": "الاكْتِشَافُ",
            "meaning_en": "Discovery / Exploration",
            "definition_ar": "إِظْهَارُ الشَّيْءِ المَجْهُولِ وَالتَّعَرُّفُ عَلَيْهِ.",
            "example_ar": "يُحِبُّ المُغَامِرُونَ اكْتِشَافَ الكُهُوفِ العَمِيقَةِ.",
            "example_en": "Adventurers love discovering deep subterranean caves.",
            "root": "ك-ش-ف",
            "category": "adventure"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: أسلوب التعجب (مَا أَفْعَلَ!)",
        "title_en": "Grammar Lab: Exclamatory Style (Ma Af'ala!)",
        "sections": [
            {
                "rule_name_ar": "صيغة التعجب القياسية (ما + أَفْعَلَ + المفعول المنصوب)",
                "rule_name_en": "Standard Exclamatory Pattern: Ma + Af'ala + Object",
                "explanation_en": "Used to convey awe and emotional wonder. The verb takes fatha and the noun is in the accusative (mansoob with fatha). Ends with exclamation mark (!).",
                "examples": [
                    {"phrase_ar": "مَا أَغْرَبَ هَذَا الكَهْفَ!", "translation_en": "How strange is this cave!"},
                    {"phrase_ar": "مَا أَجْمَلَ جُزُرَ الإِمَارَاتِ!", "translation_en": "How beautiful are the UAE islands!"}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: في أعماق الكهف المضيء",
        "title_en": "Sentence Construction Studio: Bioluminescent Caves",
        "challenges": [
            {
                "id": "sb_ci_01",
                "instruction_en": "Arrange the words to form an exclamatory sentence about the island:",
                "target_sentence_ar": "مَا أَرْوَعَ هَذِهِ الجَزِيرَةَ الاصْطِنَاعِيَّةَ فِي الخَلِيجِ العَرَبِيِّ!",
                "scrambled_tokens": ["فِي", "الاصْطِنَاعِيَّةَ", "مَا", "الجَزِيرَةَ", "الخَلِيجِ", "أَرْوَعَ", "هَذِهِ", "العَرَبِيِّ!"],
                "translation_en": "How marvelous is this man-made island in the Arabian Gulf!"
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: مغامرة في الكهوف العجيبة",
        "title_en": "Listen & Speak Studio: Adventure in Wonderful Caves",
        "passage_ar": "خَاضَ المُغَامِرُ الصَّغِيرُ رِحْلَةً مُثِيرَةً فِي كُهُوفِ الحَشَرَاتِ المُضِيئَةِ. سَارَ بِقَارِبِهِ فِي نَهْرٍ جَوْفِيٍّ عَمِيقٍ تَحْتَ الأَرْضِ، حَيْثُ تَلَأْلَأَتْ جُدْرَانُ الكَهْفِ بِآلَافِ الأَنْوَارِ الزَّرْقَاءِ، فَهَتَفَ: مَا أَعْجَبَ قُدْرَةَ الخَالِقِ فِي هَذِهِ الطَّبِيعَةِ السَّاحِرَةِ!",
        "passage_en": "The young adventurer undertook an exciting journey through caves of bioluminescent glowworms. He navigated his boat in a deep subterranean river under the earth, where cave walls glittered with thousands of blue lights, prompting him to exclaim: 'How astonishing is the Creator's power in this enchanting nature!'",
        "audio_scripts": [
            {"id": "aud_ci_01", "text_ar": "مَا أَغْرَبَ هَذِهِ الكُهُوفَ المُضِيئَةَ!", "text_en": "How astonishing are these glowing caves!"}
        ]
    },

    "practice_activities": [
        {
            "id": "act_ci_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: تمييز أسلوب التعجب",
            "title_en": "Grammar: Identifying Exclamatory Sentences",
            "prompt_ar": "أَيُّ الجُمَلِ الآتِيَةِ تُمَثِّلُ أُسْلُوبَ تَعَجُّبٍ صَحِيحًا؟",
            "prompt_en": "Which of the following is a grammatically correct exclamation?",
            "options": [
                {"id": "opt_a", "label_ar": "مَا أَجْمَلَ مِيَاهَ الخَلِيجِ العَرَبِيِّ!", "label_en": "How beautiful are the waters of the Arabian Gulf!"},
                {"id": "opt_b", "label_ar": "أَيْنَ تَقَعُ جَزِيرَةُ النَّخْلَةِ؟", "label_en": "Where is Palm Island located? (Question)"},
                {"id": "opt_c", "label_ar": "هَذِهِ جَزِيرَةٌ صَغِيرَةٌ.", "label_en": "This is a small island. (Statement)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: وصف جزيرة النخلة بدبي",
        "title_en": "Speaking Mission: Describing Dubai's Palm Island",
        "scenario_en": "Describe Palm Jumeirah in Dubai to a foreign tourist, highlighting that it is shaped like a date palm frond and built into the Arabian Gulf.",
        "prompts_ar": [
            "نَخْلَةُ جُمَيْرَا جَزِيرَةٌ اصْطِنَاعِيَّةٌ هَنْدَسِيَّةٌ فَرِيدَةٌ.",
            "مَا أَبْدَعَ تَصْمِيمَهَا الَّذِي يُشْبِهُ شَجَرَةَ النَّخْلِ!",
            "تَحْتَوِي الجَزِيرَةُ عَلَى فَنَادِقَ خَمْسِ نُجُومٍ وَشَوَاطِئَ جَمِيلَةٍ."
        ],
        "recording_task_en": "Record 30 seconds using exclamatory tone (ما أبدع / ما أجمل)."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الكهوف والجزر",
        "title_en": "Parent Companion: Caves & Islands Lesson",
        "summary_en": "Covers natural vs man-made wonders, the Arabian Gulf, and the exclamatory grammar pattern (ما أفعل!).",
        "dinner_table_prompts": [
            {"arabic": "مَا أَجْمَلَ هَذَا الطَّعَامَ!", "english": "How delicious is this food!", "phonetic": "Ma ajmala hatha at-ta'am!"}
        ],
        "home_practice_checklist": [
            "Practice saying 'Ma ajmala!' (ما أجمل) about everyday pleasant things.",
            "Look at photos of Palm Jumeirah and underground glowworm caves together."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس الكهوف والجزر",
        "learning_objectives": ["Identify island and cave terminology", "Construct exclamatory sentences using ما أفعل!", "Contrast natural vs artificial landforms"],
        "misconception_flags": ["Confusing exclamatory ما with question particle ما (what)"],
        "recommended_drills": ["Exclamation transformation drills", "Island geography matching"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_ci_01",
                "prompt_ar": "عَلَامَةُ التَّرْقِيمِ الَّتِي تُوضَعُ فِي نِهَايَةِ جُمْلَةِ (مَا أَعْجَبَ هَذَا الكَهْفَ) هِيَ:",
                "prompt_en": "The punctuation mark placed at the end of 'ما أعجب هذا الكهف' is:",
                "options": [
                    {"id": "opt_a", "label_ar": "عَلَامَةُ التَّعَجُّبِ (!)", "label_en": "Exclamation mark (!)"},
                    {"id": "opt_b", "label_ar": "عَلَامَةُ الاسْتِفْهَامِ (؟)", "label_en": "Question mark (?)"},
                    {"id": "opt_c", "label_ar": "النُّقْطَتَانِ الرَّأْسِيَّتَانِ (:)", "label_en": "Colon (:)"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 16: عجائب الكائنات الحية (Wonders of Living Creatures) — Unit 4
# Pages 58-67 in Student Book
# ============================================================================
LIVING_CREATURES_CONTENT = {
    "lesson_id": "lesson_16_living_creatures",
    "version": "0.2.0",
    "title_ar": "عجائب الكائنات الحية",
    "title_en": "Wonders of Living Creatures",
    "unit_title_ar": "غرائب وعجائب",
    "unit_title_en": "Oddities and Wonders",
    "grade": 5,
    "term": 2,
    "start_page": 58,
    "pdf_start_page": 58,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس عجائب الكائنات الحية",
        "title_en": "Preparation Check: Animal Classes & Biological Marvels",
        "description_en": "Checks animal classification and adaptation mechanisms.",
        "questions": [
            {
                "id": "prep_lc_01",
                "prompt_ar": "إِلَى أَيِّ صِنْفٍ تَنْتَمِي الضَّفَادِعُ الَّتِي تَعِيشُ فِي البَرِّ وَالمَاءِ؟",
                "prompt_en": "To which class do frogs belong that live on land and in water?",
                "options": [
                    {"id": "opt_a", "label_ar": "البَرْمَائِيَّاتُ", "label_en": "Amphibians"},
                    {"id": "opt_b", "label_ar": "الطُّيُورُ", "label_en": "Birds"},
                    {"id": "opt_c", "label_ar": "الزَّوَاحِفُ", "label_en": "Reptiles"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Amphibians (البرمائيات) are animals that spend parts of their lifecycle in water and on land."
            },
            {
                "id": "prep_lc_02",
                "prompt_ar": "كَيْفَ يَتَنَفَّسُ السَّمَكُ تَحْتَ المَاءِ؟",
                "prompt_en": "How do fish breathe under water?",
                "options": [
                    {"id": "opt_a", "label_ar": "بِوَاسِطَةِ الخَيَاشِيمِ", "label_en": "Through gills"},
                    {"id": "opt_b", "label_ar": "بِوَاسِطَةِ الأَنْفِ", "label_en": "Through the nose"},
                    {"id": "opt_c", "label_ar": "بِالأَجْنِحَةِ", "label_en": "With wings"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Fish extract dissolved oxygen from water using gills (الخياشيم)."
            },
            {
                "id": "prep_lc_03",
                "prompt_ar": "مَا هُوَ التَّمْوِيهُ فِي عَالَمِ الحَيَوَانِ؟",
                "prompt_en": "What is camouflage in the animal kingdom?",
                "options": [
                    {"id": "opt_a", "label_ar": "تَغْيِيرُ اللَّوْنِ لِلتَّخَفِّي مِنَ الأَعْدَاءِ", "label_en": "Changing color to blend in and hide from predators"},
                    {"id": "opt_b", "label_ar": "الجَرْيُ بِسُرْعَةٍ عَالِيَةٍ", "label_en": "Running at high speed"},
                    {"id": "opt_c", "label_ar": "النَّوْمُ فِي الشِّتَاءِ", "label_en": "Winter hibernation"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Camouflage (التمويه) enables animals like chameleons and octopuses to blend with their surroundings."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Categorizing creatures into amphibians, fish, reptiles, birds, and mammals.",
            "target": "Master classification nouns: برمائيات، زواحف، حشرات، طيور."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Conjugate verbs for animal groups (يسبحون، يطيرون، يتخفون).",
            "target": "Compose structured descriptive sentences on survival adaptations."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Create a narrated nature documentary script on marine wonders.",
            "target": "Script a 1-minute science video describing deep sea creatures and bioluminescence."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُصَنِّفُ",
            "transliteration": "Usannifu",
            "meaning_en": "I classify / categorize",
            "action_guidance": "Group animals into scientific categories based on shared attributes.",
            "sample_sentence_ar": "أُصَنِّفُ الحَيَوَانَاتِ إِلَى طُيُورٍ وَزَوَاحِفَ وَأَسْمَاكٍ.",
            "sample_sentence_en": "I classify animals into birds, reptiles, and fish."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_lc_01",
            "word_ar": "بَرْمَائِيَّاتٌ",
            "vowelled_ar": "بَرْمَائِيَّاتٌ",
            "meaning_en": "Amphibians",
            "definition_ar": "حَيَوَانَاتٌ تَعِيشُ فِي البَرِّ وَالمَاءِ.",
            "example_ar": "الضِّفْدَعُ مِنْ أَشْهَرِ البَرْمَائِيَّاتِ.",
            "example_en": "The frog is one of the most famous amphibians.",
            "root": "ب-ر-م",
            "category": "science"
        },
        {
            "id": "vocab_lc_02",
            "word_ar": "زَوَاحِفُ",
            "vowelled_ar": "زَوَاحِفُ",
            "meaning_en": "Reptiles",
            "definition_ar": "حَيَوَانَاتٌ تَدِبُّ عَلَى بَطْنِهَا أَوْ بِأَرْجُلٍ قَصِيرَةٍ.",
            "example_ar": "السِّلَحْفَاةُ وَالحِرْبَاءُ مِنَ الزَّوَاحِفِ.",
            "example_en": "The turtle and chameleon are reptiles.",
            "root": "ز-ح-ف",
            "category": "science"
        },
        {
            "id": "vocab_lc_03",
            "word_ar": "التَّمْوِيهُ",
            "vowelled_ar": "التَّمْوِيهُ",
            "meaning_en": "Camouflage",
            "definition_ar": "قُدْرَةُ الكَائِنِ عَلَى التَّخَفِّي فِي بِيئَتِهِ.",
            "example_ar": "تَسْتَخْدِمُ الحِرْبَاءُ التَّمْوِيهَ لِحِمَايَةِ نَفْسِهَا.",
            "example_en": "The chameleon uses camouflage to protect itself.",
            "root": "م-و-ه",
            "category": "biology"
        },
        {
            "id": "vocab_lc_04",
            "word_ar": "مَدِينَةُ الجِسْمِ",
            "vowelled_ar": "مَدِينَةُ الجِسْمِ",
            "meaning_en": "The Body Metropolis (Human Anatomy)",
            "definition_ar": "تَشْبِيهُ أَعْضَاءِ جِسْمِ الإِنْسَانِ بِمَدِينَةٍ كَامِلَةِ الوَظَائِفِ.",
            "example_ar": "القَلْبُ وَالعَقْلُ هُمَا قَائِدَا مَدِينَةِ الجِسْمِ.",
            "example_en": "Heart and brain are the directors of the body metropolis.",
            "root": "ج-س-م",
            "category": "health"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: تصريف الفعل المضارع مع واو الجماعة",
        "title_en": "Grammar Lab: Present Tense Verbs with Plural Waw (يَفْعَلُونَ)",
        "sections": [
            {
                "rule_name_ar": "الأفعال الخمسة وواو الجماعة",
                "rule_name_en": "Five Verbs Form with Plural Waw (e.g., يسبحون / يطيرون)",
                "explanation_en": "When a masculine plural subject performs an action, the present tense verb ends with '-oona' (ـُونَ) in the indicative mood.",
                "examples": [
                    {"phrase_ar": "الدَّلَافِينُ يَسْبَحُونَ فِي أَمْوَاجِ البَحْرِ.", "translation_en": "The dolphins swim in the sea waves."},
                    {"phrase_ar": "الطُّيُورُ يُهَاجِرُونَ فِي فَصْلِ الخَرِيفِ.", "translation_en": "The birds migrate in autumn."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: تكيف الكائنات الحية",
        "title_en": "Sentence Construction Studio: Animal Adaptation",
        "challenges": [
            {
                "id": "sb_lc_01",
                "instruction_en": "Arrange the words to describe animal camouflage:",
                "target_sentence_ar": "تَتَخَفَّى الحِرْبَاءُ عَنِ الأَعْدَاءِ بِتَغْيِيرِ لَوْنِ جِلْدِهَا فِي الطَّبِيعَةِ.",
                "scrambled_tokens": ["عَنِ", "بِتَغْيِيرِ", "الحِرْبَاءُ", "تَتَخَفَّى", "الطَّبِيعَةِ.", "الأَعْدَاءِ", "جِلْدِهَا", "لَوْنِ", "فِي"],
                "translation_en": "The chameleon disguises itself from predators by changing skin color in nature."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: رحلة إلى مدينة الجسم العجيبة",
        "title_en": "Listen & Speak Studio: Journey into the Body Metropolis",
        "passage_ar": "أَعْظَمُ رِحْلَةٍ يَقُومُ بِهَا العَقْلُ هِيَ اسْتِكْشَافُ جِسْمِ الإِنْسَانِ. القَلْبُ يَنْبِضُ مِثْلَ مُحَرِّكٍ دَؤُوبٍ يَضُخُّ الحَيَاةَ لِكُلِّ خَلِيَّةٍ، وَالرِّئَتَانِ تَعْمَلَانِ لَيْلَ نَهَارَ لِتَزْوِيدِ الدَّمِ بِالأُكْسِجِينِ، فَهِيَ مَدِينَةٌ حَيَّةٌ مُتَكَامِلَةٌ شَدِيدَةُ الإِبْدَاعِ.",
        "passage_en": "The greatest journey the mind can undertake is exploring the human body. The heart beats like a tireless engine pumping life to every cell, while the lungs work day and night providing oxygen to the blood — a living, integrated metropolis of extreme wonder.",
        "audio_scripts": [
            {"id": "aud_lc_01", "text_ar": "سُبْحَانَ الخَالِقِ فِي دِقَّةِ صُنْعِ الكَائِنَاتِ الحَيَّةِ.", "text_en": "Glory be to the Creator in the precision of living creatures."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_lc_01",
            "type": "multiple_choice",
            "title_ar": "تصنيف: الكائنات الحية",
            "title_en": "Classification: Living Creatures",
            "prompt_ar": "إِلَى أَيِّ صِنْفٍ تَنْتَمِي السِّلَحْفَاةُ؟",
            "prompt_en": "To which class does the turtle belong?",
            "options": [
                {"id": "opt_a", "label_ar": "الزَّوَاحِفُ", "label_en": "Reptiles"},
                {"id": "opt_b", "label_ar": "الأَسْمَاكُ", "label_en": "Fish"},
                {"id": "opt_c", "label_ar": "الحَشَرَاتُ", "label_en": "Insects"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: كائن حي عجيب",
        "title_en": "Speaking Mission: An Amazing Creature",
        "scenario_en": "Act as a wildlife documentarian. Present a 30-second spoken commentary on an animal of your choice (dolphin, camel, or falcon), describing its unique superpower.",
        "prompts_ar": [
            "يَتَمَيَّزُ الصَّقْرُ الإِمَارَاتِيُّ بِبَصَرِهِ الحَادِّ وَسُرْعَتِهِ.",
            "الجَمَلُ سَفِينَةُ الصَّحْرَاءِ يَتَحَمَّلُ العَطَشَ لِأَيَّامٍ طَوِيلَةٍ.",
            "الدَّلَافِينُ تَسْتَخْدِمُ الصَّدَى لِتَحْدِيدِ المَوَاقِعِ بِذَكَاءٍ."
        ],
        "recording_task_en": "Record 30 seconds describing animal adaptation in fluent Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس عجائب الكائنات الحية",
        "title_en": "Parent Companion: Living Creatures Lesson",
        "summary_en": "Covers biological classification (reptiles, amphibians), animal adaptations (camouflage), and plural verb conjugation (يفعلون).",
        "dinner_table_prompts": [
            {"arabic": "كَيْفَ تَتَخَفَّى الحِرْبَاءُ؟", "english": "How does the chameleon hide?", "phonetic": "Kayfa tatakhaffa al-hirba'?"}
        ],
        "home_practice_checklist": [
            "Watch a short nature video clip together and identify the animal class in Arabic."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس عجائب الكائنات الحية",
        "learning_objectives": ["Classify animals scientifically in Arabic", "Conjugate present verbs with waw al-jama'ah", "Explain biological adaptation concepts"],
        "misconception_flags": ["Confusing amphibians with reptiles"],
        "recommended_drills": ["Scientific classification cards", "Plural verb conjugation drills"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_lc_01",
                "prompt_ar": "تُسَمَّى الحَيَوَانَاتُ الَّتِي تَعِيشُ فِي المَاءِ وَاليَابِسَةِ مَعًا:",
                "prompt_en": "Animals that live in water and on land together are called:",
                "options": [
                    {"id": "opt_a", "label_ar": "بَرْمَائِيَّاتٍ", "label_en": "Amphibians"},
                    {"id": "opt_b", "label_ar": "ثَدْيِيَّاتٍ", "label_en": "Mammals"},
                    {"id": "opt_c", "label_ar": "طُيُورًا", "label_en": "Birds"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}

# Catalog dictionary mapping lesson_id to full package for Term 2
TERM2_CURRICULUM_CATALOG = {
    "lesson_11_arab_cities": ARAB_CITIES_CONTENT,
    "lesson_12_london": LONDON_CONTENT,
    "lesson_13_shanghai": SHANGHAI_CONTENT,
    "lesson_14_seven_wonders": SEVEN_WONDERS_CONTENT,
    "lesson_15_caves_and_islands": CAVES_AND_ISLANDS_CONTENT,
    "lesson_16_living_creatures": LIVING_CREATURES_CONTENT
}
