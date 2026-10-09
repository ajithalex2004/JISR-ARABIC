"""
curriculum_catalog_term3.py — Full Curriculum Content Packages for Class 5 Term 3 (Lessons 17 through 22)
Aligned with the official UAE Ministry of Education Textbook: "العربية تجمعنا — المستوى 05 — المجلد الثالث".
Covers:
- Unit 5: التواصل (Communication)
  - Lesson 17: الحمام الزاجل (Carrier Pigeons)
  - Lesson 18: الإعلام (The Media)
  - Lesson 19: وسائل التواصل الحديثة (Modern Social Media)
- Unit 6: كلنا أذكياء (We Are All Smart)
  - Lesson 20: الحيوان والذكاء (Animals and Intelligence)
  - Lesson 21: الإنسان والذكاء (Humans and Intelligence)
  - Lesson 22: مدن ذكية (Smart Cities — Masdar City & Sustainability)
"""

# ============================================================================
# LESSON 17: الحمام الزاجل (Carrier Pigeons) — Unit 5: التواصل
# Pages 6-15 in Student Book (Volume 3)
# ============================================================================
CARRIER_PIGEONS_CONTENT = {
    "lesson_id": "lesson_17_carrier_pigeons",
    "version": "0.2.0",
    "title_ar": "الحمام الزاجل",
    "title_en": "Carrier Pigeons",
    "unit_title_ar": "التواصل",
    "unit_title_en": "Communication",
    "grade": 5,
    "term": 3,
    "start_page": 6,
    "pdf_start_page": 80,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الحمام الزاجل",
        "title_en": "Preparation Check: Carrier Pigeons & Ancient Messaging",
        "description_en": "Prerequisite diagnostic testing postal history and animal navigation instincts.",
        "questions": [
            {
                "id": "prep_cp_01",
                "prompt_ar": "كَيْفَ كَانَ النَّاسُ يَتَبَادَلُونَ الرَّسَائِلَ العَاجِلَةَ قَبْلَ اخْتِرَاعِ الإِنْتَرْنِتِ وَالهَاتِفِ؟",
                "prompt_en": "How did people exchange urgent messages before the invention of the internet and phones?",
                "options": [
                    {"id": "opt_a", "label_ar": "بِوَاسِطَةِ الحَمَامِ الزَّاجِلِ وَالبَرِيدِ", "label_en": "Using carrier pigeons and courier posts"},
                    {"id": "opt_b", "label_ar": "عَبْرَ الرَّسَائِلِ الإِلِكْتُرُونِيَّةِ", "label_en": "Via emails"},
                    {"id": "opt_c", "label_ar": "بِالقِطَارَاتِ السَّرِيعَةِ", "label_en": "By bullet trains"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Carrier pigeons (الحمام الزاجل) were the fastest messaging medium across ancient civilizations."
            },
            {
                "id": "prep_cp_02",
                "prompt_ar": "مَا هِيَ القُدْرَةُ العَجِيبَةُ الَّتِي يَمْتَلِكُهَا الحَمَامُ الزَّاجِلُ؟",
                "prompt_en": "What remarkable ability does the carrier pigeon possess?",
                "options": [
                    {"id": "opt_a", "label_ar": "العَوْدَةُ إِلَى وَطَنِهِ مِنْ مَسَافَاتٍ شَاسِعَةٍ", "label_en": "Returning home accurately over vast distances"},
                    {"id": "opt_b", "label_ar": "الغَوْصُ فِي أَعْمَاقِ البِحَارِ", "label_en": "Diving into deep seas"},
                    {"id": "opt_c", "label_ar": "التَّحَدُّثُ بِلُغَةِ البَشَرِ", "label_en": "Speaking human language"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Carrier pigeons have an innate homing instinct enabling them to fly thousands of kilometers back to their roost."
            },
            {
                "id": "prep_cp_03",
                "prompt_ar": "مَا مَعْنَى كَلِمَة (غَرِيزَة)؟",
                "prompt_en": "What is the meaning of 'ghareezah' (instinct)?",
                "options": [
                    {"id": "opt_a", "label_ar": "السُّلُوكُ الفِطْرِيُّ الطَّبِيعِيُّ دُونَ تَعَلُّمٍ", "label_en": "Inborn natural behavior without prior instruction"},
                    {"id": "opt_b", "label_ar": "كِتَابٌ فِي المَكْتَبَةِ", "label_en": "A book in the library"},
                    {"id": "opt_c", "label_ar": "طَعَامٌ لَذِيذٌ", "label_en": "Delicious food"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "الغريزة is natural instinct bestowed upon living creatures."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary matching with pigeon anatomy and navigation milestones.",
            "target": "Master core terms: حمام زاجل، غريزة، مسافات شاسعة، تاريخ حافل، بلا منازع."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Sentence framing using cognate accusative (المفعول المطلق: طار طيراناً سريعاً).",
            "target": "Construct descriptive sentences detailing pigeon speed and homing accuracy."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Research and contrast ancient pigeon post vs modern satellite telecommunications.",
            "target": "Write an expository essay tracing the evolution of communication from feathers to fiber optics."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَدِلُّ",
            "transliteration": "Astadillu",
            "meaning_en": "I deduce / infer meaning",
            "action_guidance": "Infer word meanings from the surrounding sentence context.",
            "sample_sentence_ar": "أَسْتَدِلُّ عَلَى مَعْنَى الكَلِمَةِ مِنْ سِيَاقِ الجُمْلَةِ.",
            "sample_sentence_en": "I deduce the word meaning from sentence context."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_cp_01",
            "word_ar": "الحَمَامُ الزَّاجِلُ",
            "vowelled_ar": "الحَمَامُ الزَّاجِلُ",
            "meaning_en": "Carrier / Homing Pigeon",
            "definition_ar": "نَوْعٌ مِنَ الحَمَامِ كَانَ يُرْسَلُ لِمَسَافَاتٍ بَعِيدَةٍ حَامِلًا الرَّسَائِلَ.",
            "example_ar": "كَانَ الحَمَامُ الزَّاجِلُ رَسُولَ السَّلَامِ وَالأَخْبَارِ قَدِيمًا.",
            "example_en": "Carrier pigeons were messengers of peace and news in ancient times.",
            "root": "ز-ج-ل",
            "category": "communication"
        },
        {
            "id": "vocab_cp_02",
            "word_ar": "بِلَا مُنَازِعٍ",
            "vowelled_ar": "بِلَا مُنَازِعٍ",
            "meaning_en": "Undisputed / Beyond Doubt",
            "definition_ar": "لَا شَكَّ فِيهِ وَلَا خِلَافَ عَلَى تَفَوُّقِهِ.",
            "example_ar": "يُعَدُّ الحَمَامُ الزَّاجِلُ أَسْرَعَ سَاعِي بَرِيدٍ بِلَا مُنَازِعٍ فِي التَّارِيخِ.",
            "example_en": "The carrier pigeon is the undisputed fastest postman in history.",
            "root": "ن-ز-ع",
            "category": "idiom"
        },
        {
            "id": "vocab_cp_03",
            "word_ar": "حَافِلٌ",
            "vowelled_ar": "حَافِلٌ",
            "meaning_en": "Full Of / Rich With",
            "definition_ar": "مَلِيءٌ بِالإِنجَازَاتِ وَالأَحْدَاثِ العَظِيمَةِ.",
            "example_ar": "تَارِيخُ العَرَبِ حَافِلٌ بِالإِنجَازَاتِ العِلْمِيَّةِ.",
            "example_en": "Arab history is rich with scientific breakthroughs.",
            "root": "ح-ف-ل",
            "category": "descriptive"
        },
        {
            "id": "vocab_cp_04",
            "word_ar": "الشَّاسِعَةُ",
            "vowelled_ar": "الشَّاسِعَةُ",
            "meaning_en": "Vast / Expansive",
            "definition_ar": "الوَاسِعَةُ جِدًّا وَالمُمْتَدَّةُ.",
            "example_ar": "يَقْطَعُ الطَّائِرُ المَسَافَاتِ الشَّاسِعَةَ فَوْقَ الصَّحْرَاءِ.",
            "example_en": "The bird crosses vast distances over the desert.",
            "root": "ش-س-ع",
            "category": "geography"
        },
        {
            "id": "vocab_cp_05",
            "word_ar": "غَرِيزَةٌ",
            "vowelled_ar": "غَرِيزَةٌ",
            "meaning_en": "Instinct / Innate Nature",
            "definition_ar": "السُّلُوكُ الفِطْرِيُّ الَّذِي يُولَدُ مَعَ الكَائِنِ الحَيِّ.",
            "example_ar": "تَهْتَدِي الطُّيُورُ فِي هِجْرَتِهَا بِغَرِيزَةٍ أَوْدَعَهَا اللهُ فِيهَا.",
            "example_en": "Birds navigate their migration by divine instinct.",
            "root": "غ-ر-ز",
            "category": "biology"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: المفعول المطلق المؤكد والمبين للنوع",
        "title_en": "Grammar Lab: Absolute / Cognate Accusative (المفعول المطلق)",
        "sections": [
            {
                "rule_name_ar": "المفعول المطلق (اسم منصوب مشتق من لفظ الفعل)",
                "rule_name_en": "Cognate Accusative: Derived directly from the verb root",
                "explanation_en": "Used to emphasize the action (مؤكد للفعل) or describe its manner (مبين للنوع). Always takes fatha/tanween fath.",
                "examples": [
                    {"phrase_ar": "طَارَ الحَمَامُ طَيَرَانًا سَرِيعًا.", "translation_en": "The pigeon flew a rapid flight (Descriptive)."},
                    {"phrase_ar": "انْتَصَرَ الإِنْسَانُ انْتِصَارًا.", "translation_en": "Man triumphed a decisive triumph (Emphatic)."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: رسائل الحمام الزاجل",
        "title_en": "Sentence Construction Studio: Pigeon Post",
        "challenges": [
            {
                "id": "sb_cp_01",
                "instruction_en": "Arrange the words to describe pigeon navigation:",
                "target_sentence_ar": "يَعُودُ الحَمَامُ الزَّاجِلُ إِلَى وَطَنِهِ عَوْدَةً عَجِيبَةً بِفَضْلِ غَرِيزَتِهِ.",
                "scrambled_tokens": ["عَوْدَةً", "الحَمَامُ", "إِلَى", "يَعُودُ", "غَرِيزَتِهِ.", "الزَّاجِلُ", "عَجِيبَةً", "وَطَنِهِ", "بِفَضْلِ"],
                "translation_en": "The carrier pigeon returns home miraculously thanks to its instinct."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: قصة ساعي البريد الطائر",
        "title_en": "Listen & Speak Studio: Story of the Flying Postman",
        "passage_ar": "يَمْلِكُ الحَمَامُ الزَّاجِلُ قُدْرَةً خَارِقَةً عَلَى مَعْرِفَةِ طَرِيقِ العَوْدَةِ إِلَى مَسْكَنِهِ مَهْمَا كَانَتِ المَسَافَةُ شَاسِعَةً. اعْتَمَدَ عَلَيْهِ العَرَبُ قَدِيمًا فِي إِرْسَالِ الرَّسَائِلِ المَصِيرِيَّةِ، حَيْثُ كَانُوا يَرْبِطُونَ الرِّسَالَةَ فِي سَاقِهِ أَوْ ظَهْرِهِ لِيَطِيرَ بِهَا عَبْرَ الصَّحْرَاءِ.",
        "passage_en": "Carrier pigeons possess an extraordinary ability to find their way home no matter how vast the distance. Ancient Arabs relied on them to deliver critical messages, tying parchment to their legs or backs to soar across the desert.",
        "audio_scripts": [
            {"id": "aud_cp_01", "text_ar": "الحَمَامُ الزَّاجِلُ رَمْزٌ تَارِيخِيٌّ لِلتَّوَاصُلِ الإِنْسَانِيِّ.", "text_en": "Carrier pigeons are a historic symbol of human communication."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_cp_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: استخراج المفعول المطلق",
            "title_en": "Grammar: Identifying Cognate Accusative",
            "prompt_ar": "مَا هُوَ المَفْعُولُ المُطْلَقُ فِي جُمْلَةِ: (حَلَّقَ الطَّائِرُ تَحْلِيقًا مُبْهِرًا)؟",
            "prompt_en": "What is the cognate accusative in 'The bird soared a dazzling soaring'?",
            "options": [
                {"id": "opt_a", "label_ar": "تَحْلِيقًا", "label_en": "Tahleeqan (Cognate verbal noun)"},
                {"id": "opt_b", "label_ar": "حَلَّقَ", "label_en": "Hallaqa (The verb)"},
                {"id": "opt_c", "label_ar": "الطَّائِرُ", "label_en": "At-Ta'iru (The subject)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: رسالة في ساق حمامة",
        "title_en": "Speaking Mission: A Message on a Pigeon's Wing",
        "scenario_en": "Imagine you are an ancient merchant in the Arabian Gulf sending a critical trade update from Basra to Dubai via carrier pigeon. Speak your 25-word message aloud in clear, vowelled Arabic.",
        "prompts_ar": [
            "أُرْسِلُ إِلَيْكُمْ هَذِهِ الرِّسَالَةَ مَعَ طَائِرِي الأَمِينِ.",
            "وَصَلَتِ القَافِلَةُ التِّجَارِيَّةُ بِخَيْرٍ وَسَلَامٍ.",
            "البِضَائِعُ مُمْتَازَةٌ وَالأَسْوَاقُ عَامِرَةٌ."
        ],
        "recording_task_en": "Speak with dramatic historical inflection."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الحمام الزاجل",
        "title_en": "Parent Companion: Carrier Pigeons Lesson",
        "summary_en": "Explores postal communication history, animal homing instincts, and the cognate accusative grammar rule (المفعول المطلق).",
        "dinner_table_prompts": [
            {"arabic": "كَيْفَ يَعُودُ الحَمَامُ إِلَى بَيْتِهِ؟", "english": "How does the pigeon find its way home?", "phonetic": "Kayfa ya'oodu al-hamamu ila baytihi?"}
        ],
        "home_practice_checklist": [
            "Practice identifying cognate accusatives: مشى مشياً، قرأ قراءةً.",
            "Compare carrier pigeons to instant messaging apps with your child."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس الحمام الزاجل",
        "learning_objectives": ["Understand ancient communication mechanisms", "Master maf'ool mutlaq formation and vowelling", "Explain animal navigation biological principles"],
        "misconception_flags": ["Confusing maf'ool bihi (direct object) with maf'ool mutlaq (verbal noun)"],
        "recommended_drills": ["Verb-to-cognate noun derivation drills", "Postal timeline matching"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_cp_01",
                "prompt_ar": "المَفْعُولُ المُطْلَقُ يَكُونُ دَائِمًا:",
                "prompt_en": "The cognate accusative (المفعول المطلق) is always:",
                "options": [
                    {"id": "opt_a", "label_ar": "مَنْصُوبًا بِالفَتْحَةِ", "label_en": "Accusative with fatha"},
                    {"id": "opt_b", "label_ar": "مَرْفُوعًا بِالضَّمَّةِ", "label_en": "Nominative with dammah"},
                    {"id": "opt_c", "label_ar": "مَجْرُورًا بِالكَسْرَةِ", "label_en": "Genitive with kasrah"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 18: الإعلام (The Media) — Unit 5: التواصل
# Pages 16-25 in Student Book (Volume 3)
# ============================================================================
THE_MEDIA_CONTENT = {
    "lesson_id": "lesson_18_the_media",
    "version": "0.2.0",
    "title_ar": "الإعلام",
    "title_en": "The Media",
    "unit_title_ar": "التواصل",
    "unit_title_en": "Communication",
    "grade": 5,
    "term": 3,
    "start_page": 16,
    "pdf_start_page": 90,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الإعلام",
        "title_en": "Preparation Check: Media, Journalism & Ethics",
        "description_en": "Diagnostic evaluating journalism vocabulary and objective reporting.",
        "questions": [
            {
                "id": "prep_md_01",
                "prompt_ar": "مَا هِيَ الصِّفَةُ الأَهَمُّ الَّتِي يَجِبُ أَنْ يَتَحَلَّى بِهَا الصَّحَفِيُّ النَّاجِحُ؟",
                "prompt_en": "What is the most critical quality of a successful journalist?",
                "options": [
                    {"id": "opt_a", "label_ar": "الأَمَانَةُ وَالصِّدْقُ فِي نَقْلِ الخَبَرِ", "label_en": "Integrity and truthfulness in reporting news"},
                    {"id": "opt_b", "label_ar": "تَأْلِيفُ القِصَصِ الخَيَالِيَّةِ", "label_en": "Inventing fictional stories"},
                    {"id": "opt_c", "label_ar": "نَشْرُ الإِشَاعَاتِ", "label_en": "Spreading rumors"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Journalistic integrity (الأمانة والمصداقية) is the foundation of trustworthy media."
            },
            {
                "id": "prep_md_02",
                "prompt_ar": "مَا ضِدُّ كَلِمَة (مُتَحَيِّز)؟",
                "prompt_en": "What is the opposite of 'biased' (متحيز)?",
                "options": [
                    {"id": "opt_a", "label_ar": "مُحَايِدٌ", "label_en": "Neutral / Objective (Muhaayid)"},
                    {"id": "opt_b", "label_ar": "غَاضِبٌ", "label_en": "Angry"},
                    {"id": "opt_c", "label_ar": "سَرِيعٌ", "label_en": "Fast"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "المحايد is someone fair, objective, and unbiased."
            },
            {
                "id": "prep_md_03",
                "prompt_ar": "مَا هُوَ (البَثُّ التِّلْفِزْيُونِيُّ)؟",
                "prompt_en": "What is television broadcast (البث)?",
                "options": [
                    {"id": "opt_a", "label_ar": "إِرْسَالُ الصَّوْتِ وَالصُّورَةِ عَبْرَ الأَقْمَارِ أَوْ الأَسْلَاكِ", "label_en": "Transmitting audio and video via satellites or cables"},
                    {"id": "opt_b", "label_ar": "طِبَاعَةُ الكُتُبِ عَلَى الوَرَقِ", "label_en": "Printing books on paper"},
                    {"id": "opt_c", "label_ar": "صِنَاعَةُ السِّيَارَاتِ", "label_en": "Car manufacturing"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "البث signifies transmitting live audio-visual broadcasts to viewers."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Media role-cards: مذيع، مراسل، محرر، قارئ.",
            "target": "Master media vocabulary: إعلام، محايد، بث، محليات، عمود صحفي."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Grammar drills identifying Subject and Object in verbal sentences (الفاعل والمفعول به).",
            "target": "Construct headline sentences with clear subjects and direct objects."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Write an objective newspaper report covering a school science exhibition.",
            "target": "Produce a formatted news article with headline, dateline, body, and conclusion."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَتَنَبَّأُ",
            "transliteration": "Atanabba'u",
            "meaning_en": "I anticipate / forecast",
            "action_guidance": "Predict tomorrow's top news headline based on current events.",
            "sample_sentence_ar": "أَتَنَبَّأُ بِالخَبَرِ الَّذِي سَيَتَصَدَّرُ الجَرَائِدَ غَدًا.",
            "sample_sentence_en": "I forecast the story that will lead tomorrow's papers."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_md_01",
            "word_ar": "الإِعْلَامُ",
            "vowelled_ar": "الإِعْلَامُ",
            "meaning_en": "The Media / Press",
            "definition_ar": "تَوْفِيرُ الأَخْبَارِ وَالمَعْلُومَاتِ لِلجُمْهُورِ عَبْرَ الصُّحُفِ وَالتِّلْفَازِ وَالشَّبَكَاتِ.",
            "example_ar": "يَلْعَبُ الإِعْلَامُ النَّزِيهُ دَوْرًا كَبِيرًا فِي تَوْعِيَةِ المُجْتَمَعِ.",
            "example_en": "Ethical media plays a major role in educating society.",
            "root": "ع-ل-م",
            "category": "media"
        },
        {
            "id": "vocab_md_02",
            "word_ar": "مُحَايِدٌ",
            "vowelled_ar": "مُحَايِدٌ",
            "meaning_en": "Neutral / Unbiased",
            "definition_ar": "مَنْ لَا يَمِيلُ لِطَرَفٍ دُونَ آخَرَ وَيَنْقُلُ الحَقِيقَةَ بِمَوْضُوعِيَّةٍ.",
            "example_ar": "يَجِبُ أَنْ يَكُونَ الصَّحَفِيُّ مُحَايِدًا فِي تَقْرِيرِهِ.",
            "example_en": "A journalist must remain neutral in their report.",
            "root": "ح-ي-د",
            "category": "ethics"
        },
        {
            "id": "vocab_md_03",
            "word_ar": "البَثُّ",
            "vowelled_ar": "البَثُّ",
            "meaning_en": "Broadcast / Transmission",
            "definition_ar": "إِرْسَالُ البَرَامِجِ عَبْرَ الإِذَاعَةِ أَوِ التِّلْفَازِ.",
            "example_ar": "بَدَأَ البَثُّ المُبَاشِرُ لِحَفْلِ تَخَرُّجِ الطُّلَّابِ.",
            "example_en": "Live broadcast of the student graduation ceremony commenced.",
            "root": "ب-ث-ث",
            "category": "technology"
        },
        {
            "id": "vocab_md_04",
            "word_ar": "الأَمَانَةُ المِهْنِيَّةُ",
            "vowelled_ar": "الأَمَانَةُ المِهْنِيَّةُ",
            "meaning_en": "Professional Integrity",
            "definition_ar": "الصِّدْقُ وَالإِخْلَاصُ فِي أَدَاءِ الوَظِيفَةِ وَنَقْلِ الحَقَائِقِ.",
            "example_ar": "تَتَطَلَّبُ كِتَابَةُ الخَبَرِ تَحَرِّي الصِّدْقِ وَالأَمَانَةِ.",
            "example_en": "Writing news demands pursuing truth and professional integrity.",
            "root": "أ-م-ن",
            "category": "ethics"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: الجملة الفعلية (الفاعل والمفعول به)",
        "title_en": "Grammar Lab: Verbal Sentence (Subject & Object)",
        "sections": [
            {
                "rule_name_ar": "إعراب الفاعل (مرفوع) والمفعول به (منصوب)",
                "rule_name_en": "Subject (Nominative with Dammah) and Object (Accusative with Fatha)",
                "explanation_en": "A verbal sentence begins with a verb. The doer is the Fa'il (marfoo' with dammah) and the recipient is Maf'ool bihi (mansoob with fatha).",
                "examples": [
                    {"phrase_ar": "نَشَرَ الصَّحَفِيُّ الخَبَرَ.", "translation_en": "The journalist published the news story."},
                    {"phrase_ar": "أَذَاعَتِ القَنَاةُ البَرْنَامَجَ.", "translation_en": "The channel broadcasted the program."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: كتابة العناوين الإخبارية",
        "title_en": "Sentence Construction Studio: News Headlines",
        "challenges": [
            {
                "id": "sb_md_01",
                "instruction_en": "Arrange the words to form a news headline:",
                "target_sentence_ar": "أَطْلَقَتْ دَوْلَةُ الإِمَارَاتِ قَمَرًا صِنَاعِيًّا جَدِيدًا لِاسْتِكْشَافِ الفَضَاءِ.",
                "scrambled_tokens": ["صِنَاعِيًّا", "دَوْلَةُ", "لِاسْتِكْشَافِ", "أَطْلَقَتْ", "قَمَرًا", "الإِمَارَاتِ", "الفَضَاءِ.", "جَدِيدًا"],
                "translation_en": "The UAE launched a new satellite for space exploration."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: نشرة الأخبار المدرسية",
        "title_en": "Listen & Speak Studio: School News Broadcast",
        "passage_ar": "مَرْحَبًا بِكُمْ أَعِزَّائِي المُسْتَمِعِينَ فِي نَشْرَةِ الأَخْبَارِ الصَّبَاحِيَّةِ. نَبْدَأُ بِأَهَمِّ الأَنْبَاءِ: افْتَتَحَ مُدِيرُ المَدْرَسَةِ مَعْرِضَ الِابْتِكَارِ وَالذَّكَاءِ الِاصْطِنَاعِيِّ، حَيْثُ قَدَّمَ الطُّلَّابُ مَشَارِيعَ مُبْهِرَةً تُسَاعِدُ فِي تَرْشِيدِ الطَّاقَةِ وَحِمَايَةِ البِيئَةِ.",
        "passage_en": "Welcome listeners to the morning news broadcast. Leading today's news: The school principal inaugurated the Innovation and AI Exhibition, where students presented dazzling projects to conserve energy and preserve the environment.",
        "audio_scripts": [
            {"id": "aud_md_01", "text_ar": "هُنَا إِذَاعَةُ المَدْرَسَةِ، صَوْتُ العِلْمِ وَالأَمَلِ.", "text_en": "Here is the school radio, the voice of science and hope."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_md_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: تحديد الفاعل",
            "title_en": "Grammar: Identifying the Subject",
            "prompt_ar": "عَيِّنِ الفَاعِلَ فِي جُمْلَةِ: (كَتَبَ المُرَاسِلُ تَقْرِيرًا صَحَفِيًّا):",
            "prompt_en": "Identify the subject in 'The reporter wrote a press report':",
            "options": [
                {"id": "opt_a", "label_ar": "المُرَاسِلُ (فاعل مرفوع بالضمة)", "label_en": "Al-Murāsilu (Subject in nominative)"},
                {"id": "opt_b", "label_ar": "تَقْرِيرًا (مفعول به)", "label_en": "Taqreeran (Object)"},
                {"id": "opt_c", "label_ar": "كَتَبَ (فعل ماض)", "label_en": "Kataba (Past verb)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: مذيع الأخبار الصغير",
        "title_en": "Speaking Mission: Junior News Anchor",
        "scenario_en": "Present a 30-second television news headline bulletin announcing your school's victory in the UAE National Robotics Championship.",
        "prompts_ar": [
            "سَيِّدَاتِي وَسَادَتِي، طَابَ صَبَاحُكُمْ وَأَهْلًا بِكُمْ إِلَى مُوجَزِ الأَنْبَاءِ.",
            "حَقَّقَ فَرِيقُ مَدْرَسَتِنَا المَرْكَزَ الأَوَّلَ فِي بُطُولَةِ الرُّوبُوتِ الوَطَنِيَّةِ.",
            "نُهَنِّئُ أَبْطَالَنَا عَلَى هَذَا الإِنجَازِ العِلْمِيِّ المُشَرِّفِ."
        ],
        "recording_task_en": "Deliver with energetic, confident news broadcaster cadence."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الإعلام",
        "title_en": "Parent Companion: Media & Journalism Lesson",
        "summary_en": "Teaches media literacy, objective reporting vs bias, and sentence syntax (فاعل مرفوع ومفعول به منصوب).",
        "dinner_table_prompts": [
            {"arabic": "مَا هُوَ الخَبَرُ السَّارُّ اليَوْمَ؟", "english": "What is the good news today?", "phonetic": "Ma huwa al-khabar as-sarru al-yawm?"}
        ],
        "home_practice_checklist": [
            "Look at a reputable news website together and identify the headline and dateline in Arabic."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس الإعلام",
        "learning_objectives": ["Identify journalistic terminology", "Distinguish Fa'il (dammah) and Maf'ool bihi (fatha)", "Analyze news for neutrality"],
        "misconception_flags": ["Swapping case markers between subject and object"],
        "recommended_drills": ["Headline syntax analysis", "Neutrality debate flashcards"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_md_01",
                "prompt_ar": "عَلَامَةُ إِعْرَابِ المَفْعُولِ بِهِ هِيَ:",
                "prompt_en": "The grammatical case marker of the direct object (المفعول به) is:",
                "options": [
                    {"id": "opt_a", "label_ar": "الفَتْحَةُ (النَّصْبُ)", "label_en": "Fatha (Accusative)"},
                    {"id": "opt_b", "label_ar": "الضَّمَّةُ (الرَّفْعُ)", "label_en": "Dammah (Nominative)"},
                    {"id": "opt_c", "label_ar": "السُّكُونُ (الجَزْمُ)", "label_en": "Sukoon (Jussive)"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 19: وسائل التواصل الحديثة (Social Media) — Unit 5: التواصل
# Pages 26-35 in Student Book (Volume 3)
# ============================================================================
SOCIAL_MEDIA_CONTENT = {
    "lesson_id": "lesson_19_social_media",
    "version": "0.2.0",
    "title_ar": "وسائل التواصل",
    "title_en": "Social Media",
    "unit_title_ar": "التواصل",
    "unit_title_en": "Communication",
    "grade": 5,
    "term": 3,
    "start_page": 26,
    "pdf_start_page": 100,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس وسائل التواصل",
        "title_en": "Preparation Check: Social Media & Cyber Safety",
        "description_en": "Diagnostic covering digital communication networks, screen time, and cyber ethics.",
        "questions": [
            {
                "id": "prep_sm_01",
                "prompt_ar": "مَا هُوَ التَّصَرُّفُ الصَّحِيحُ لِحِمَايَةِ خُصُوصِيَّتِكَ عَبْرَ الإِنْتَرْنِتِ؟",
                "prompt_en": "What is the correct action to protect your online privacy?",
                "options": [
                    {"id": "opt_a", "label_ar": "عَدَمُ مُشَارَكَةِ كَلِمَاتِ المُرُورِ وَالمَعْلُومَاتِ الشَّخْصِيَّةِ", "label_en": "Never sharing passwords or personal info"},
                    {"id": "opt_b", "label_ar": "نَشْرُ عُنْوَانِ المَنْزِلِ لِلْجَمِيعِ", "label_en": "Publishing home address to everyone"},
                    {"id": "opt_c", "label_ar": "التَّحَدُّثُ مَعَ الغُرَبَاءِ بِلَا حَذَرٍ", "label_en": "Talking to strangers without caution"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Cyber safety (الأمان الرقمي) requires keeping personal data and passwords private."
            },
            {
                "id": "prep_sm_02",
                "prompt_ar": "مَا هِيَ (المُدَوَّنَةُ الإِلِكْتُرُونِيَّةُ)؟",
                "prompt_en": "What is a blog (مدونة إلكترونية)?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَوْقِعٌ يُسَجِّلُ فِيهِ الشَّخْصُ آرَاءَهُ وَمَقَالَاتِهِ", "label_en": "A website where someone posts personal articles and reflections"},
                    {"id": "opt_b", "label_ar": "لُعْبَةُ كُرَةِ قَدَمٍ", "label_en": "A football game"},
                    {"id": "opt_c", "label_ar": "جِهَازُ تِلْفَازٍ قَدِيمٌ", "label_en": "An old TV"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "A blog (مدونة) is an online platform for periodic writings and thoughts."
            },
            {
                "id": "prep_sm_03",
                "prompt_ar": "مَا هُوَ خَطَرُ قَضَاءِ سَاعَاتٍ طَوِيلَةٍ جِدًّا أَمَامَ الشَّاشَاتِ؟",
                "prompt_en": "What is the danger of spending excessive hours in front of screens?",
                "options": [
                    {"id": "opt_a", "label_ar": "إِجْهَادُ العَيْنَيْنِ وَإِضَاعَةُ الوَقْتِ", "label_en": "Eye strain and wasting precious time"},
                    {"id": "opt_b", "label_ar": "زِيَادَةُ النَّشَاطِ البَدَنِيِّ", "label_en": "Increased physical fitness"},
                    {"id": "opt_c", "label_ar": "تَحْسِينُ النَّوْمِ", "label_en": "Better sleep"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Excessive screen time damages eye health and undermines healthy physical activity."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary cards of digital social icons and terms.",
            "target": "Master 6 terms: مدونة، صورة رمزية، تعليق، درشة، إعجاب، أمان رقمي."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Grammar practice with negative imperatives (أسلوب النهي: لَا تُفْرِطْ).",
            "target": "Write guidelines for constructive screen usage using (لا الناهية)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Debate benefits vs harms of social networks using polite discourse formulas.",
            "target": "Draft a persuasive essay balancing cyber benefits with empathetic family interaction."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُعَبِّرُ عَنْ رَأْيِي",
            "transliteration": "U'abbiru 'an Ra'yi",
            "meaning_en": "I express my opinion politely",
            "action_guidance": "State your viewpoint while respecting differing perspectives.",
            "sample_sentence_ar": "أَحْتَرِمُ رَأْيَكَ، لَكِنْ دَعْنِي أُوَضِّحُ وُجْهَةَ نَظَرِي.",
            "sample_sentence_en": "I respect your opinion, but allow me to clarify my viewpoint."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_sm_01",
            "word_ar": "مُدَوَّنَةٌ",
            "vowelled_ar": "مُدَوَّنَةٌ",
            "meaning_en": "Blog / Online Journal",
            "definition_ar": "مَوْقِعٌ شَخْصِيٌّ يَنْشُرُ فِيهِ الفَرْدُ أَفْكَارَهُ وَمَقَالَاتِهِ.",
            "example_ar": "أَنْشَأْتُ مُدَوَّنَةً مَدْرَسِيَّةً لِلتَّشْجِيعِ عَلَى القِرَاءَةِ.",
            "example_en": "I launched a school blog to encourage reading.",
            "root": "د-و-ن",
            "category": "digital"
        },
        {
            "id": "vocab_sm_02",
            "word_ar": "الصُّورَةُ الرَّمْزِيَّةُ",
            "vowelled_ar": "الصُّورَةُ الرَّمْزِيَّةُ",
            "meaning_en": "Avatar / Profile Icon",
            "definition_ar": "الصُّورَةُ الشَّخْصِيَّةُ الَّتِي تُمَثِّلُ المُسْتَخْدِمَ فِي التَّطْبِيقَاتِ.",
            "example_ar": "اخْتَرْتُ صُورَةَ صَقْرٍ لِتَكُونَ صُورَتِي الرَّمْزِيَّةَ.",
            "example_en": "I chose a falcon picture as my profile avatar.",
            "root": "ر-م-ز",
            "category": "digital"
        },
        {
            "id": "vocab_sm_03",
            "word_ar": "التَّعْلِيقُ",
            "vowelled_ar": "التَّعْلِيقُ",
            "meaning_en": "Comment / Feedback Note",
            "definition_ar": "مَا يَكْتُبُهُ القَارِئُ لِلرَّدِّ عَلَى المَنْشُورِ بِأَدَبٍ وَاحْتِرَامٍ.",
            "example_ar": "كَتَبْتُ تَعْلِيقًا إِيجَابِيًّا يُشَجِّعُ زَمِيلِي عَلَى ابْتِكَارِهِ.",
            "example_en": "I posted an encouraging comment on my peer's invention.",
            "root": "ع-ل-ق",
            "category": "social"
        },
        {
            "id": "vocab_sm_04",
            "word_ar": "الأَمَانُ الرَّقْمِيُّ",
            "vowelled_ar": "الأَمَانُ الرَّقْمِيُّ",
            "meaning_en": "Cyber Safety / Digital Security",
            "definition_ar": "حِمَايَةُ الحِسَابَاتِ وَالبَيَانَاتِ مِنَ المَخَاطِرِ الإِلِكْتُرُونِيَّةِ.",
            "example_ar": "يَحْرِصُ الطُّلَّابُ عَلَى تَعَلُّمِ قَوَاعِدِ الأَمَانِ الرَّقْمِيِّ.",
            "example_en": "Students make sure to learn cyber safety rules.",
            "root": "أ-م-ن",
            "category": "safety"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: أسلوب النهي (لَا النَّاهِيَة)",
        "title_en": "Grammar Lab: Negative Imperative (La an-Nahiyah)",
        "sections": [
            {
                "rule_name_ar": "لا الناهية وجزم الفعل المضارع بالسكون",
                "rule_name_en": "Prohibitive La: Demands stopping an action, verb in jussive (sukoon)",
                "explanation_en": "La an-Nahiyah instructs the listener not to perform an act. The present verb after it becomes jussive (majzoom with sukoon). Differs from negative La (النافية) which just states a fact.",
                "examples": [
                    {"phrase_ar": "لَا تُهْدِرْ وَقْتَكَ فِي الشَّاشَاتِ.", "translation_en": "Do not waste your time on screens! (Prohibition)"},
                    {"phrase_ar": "أَنَا لَا أُهْدِرُ وَقْتِي.", "translation_en": "I do not waste my time. (Negation)"}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: نصائح الأمان الرقمي",
        "title_en": "Sentence Construction Studio: Digital Safety Tips",
        "challenges": [
            {
                "id": "sb_sm_01",
                "instruction_en": "Arrange the words to form a digital safety warning:",
                "target_sentence_ar": "لَا تُشَارِكْ مَعْلُومَاتِكَ الشَّخْصِيَّةَ مَعَ الغُرَبَاءِ عَبْرَ الشَّبَكَةِ.",
                "scrambled_tokens": ["عَبْرَ", "تُشَارِكْ", "الغُرَبَاءِ", "لَا", "مَعْلُومَاتِكَ", "الشَّخْصِيَّةَ", "الشَّبَكَةِ.", "مَعَ"],
                "translation_en": "Do not share personal information with strangers across the web."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: مناظرة وسائل التواصل الاجتماعي",
        "title_en": "Listen & Speak Studio: Social Networks Debate",
        "passage_ar": "وَسَائِلُ التَّوَاصُلِ الاجْتِمَاعِيِّ سِلَاحٌ ذُو حَدَّيْنِ. فَهِيَ تُقَرِّبُ المَسَافَاتِ بَيْنَ النَّاسِ وَتُسَهِّلُ تَبَادُلَ العُلُومِ، لَكِنَّ الإِفْرَاطَ فِيهَا يُهْدِرُ الوَقْتَ وَيُضْعِفُ العَلَاقَاتِ الأُسَرِيَّةَ. فَلْنَكُنْ حُكَمَاءَ فِي اسْتِخْدَامِهَا!",
        "passage_en": "Social media is a double-edged sword. It bridges distances between people and eases knowledge sharing, yet excess wastes time and weakens family bonds. Let us be wise in our usage!",
        "audio_scripts": [
            {"id": "aud_sm_01", "text_ar": "اسْتَخْدِمِ التِّكْنُولُوجْيَا بِحِكْمَةٍ وَاعْتِدَالٍ.", "text_en": "Use technology with wisdom and moderation."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_sm_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: التمييز بين لا الناهية ولا النافية",
            "title_en": "Grammar: Prohibitive La vs Negative La",
            "prompt_ar": "أَيُّ الجُمَلِ الآتِيَةِ تَحْتَوِي عَلَى أُسْلُوبِ نَهْيٍ (لَا النَّاهِيَة)؟",
            "prompt_en": "Which sentence contains a negative imperative (prohibition)?",
            "options": [
                {"id": "opt_a", "label_ar": "لَا تَنْشُرْ صُوَرَ الآخَرِينَ دُونَ إِذْنِهِمْ.", "label_en": "Do not publish photos of others without their permission. (Prohibition)"},
                {"id": "opt_b", "label_ar": "عُمَرُ لَا يُحِبُّ إِضَاعَةَ الوَقْتِ.", "label_en": "Omar does not like wasting time. (Negation)"},
                {"id": "opt_c", "label_ar": "هَلْ تَسْتَخْدِمُ الإِنْتَرْنِتَ؟", "label_en": "Do you use the internet? (Question)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: ميثاق الاستخدام الآمن للإنترنت",
        "title_en": "Speaking Mission: Safe Internet Pledge",
        "scenario_en": "Deliver a 30-second presentation outlining 3 golden rules for safe and polite communication in your classroom online group.",
        "prompts_ar": [
            "لَا تَنْشُرْ إِلَّا الكَلِمَاتِ الطَّيِّبَةَ وَالمُفِيدَةَ.",
            "احْرِصْ عَلَى أَمَانِ حِسَابِكَ وَلَا تُشَارِكْ كَلِمَةَ المُرُورِ.",
            "حَدِّدْ وَقْتًا لِلشَّاشَاتِ لِتَقْضِيَ وَقْتًا أَطْوَلَ مَعَ عَائِلَتِكَ."
        ],
        "recording_task_en": "Record clear, respectful guidelines in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس وسائل التواصل",
        "title_en": "Parent Companion: Social Media Lesson",
        "summary_en": "Covers digital citizenship, cyber safety, screen balance, and prohibitive commands with La an-Nahiyah (لا تفعل).",
        "dinner_table_prompts": [
            {"arabic": "كَيْفَ نَحْمِي أَنْفُسَنَا عَبْرَ الإِنْتَرْنِتِ؟", "english": "How do we protect ourselves online?", "phonetic": "Kayfa nahmee anfusana 'abra al-internet?"}
        ],
        "home_practice_checklist": [
            "Review family screen time guidelines together.",
            "Practice distinguishing prohibition (لا تفعل!) from negation (أنا لا أفعل)."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس وسائل التواصل",
        "learning_objectives": ["Identify cyber safety terms", "Distinguish prohibitive La (jussive) from negative La (indicative)", "Structure balanced digital debate"],
        "misconception_flags": ["Confusing prohibition (طلب الكف عن الفعل) with mere factual negation"],
        "recommended_drills": ["La an-Nahiyah vs La an-Nafiyah sentence sorting", "Cyber ethics scenarios"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_sm_01",
                "prompt_ar": "الفِعْلُ المُضَارِعُ بَعْدَ (لَا النَّاهِيَةِ) يَكُونُ:",
                "prompt_en": "The present tense verb after prohibitive La is:",
                "options": [
                    {"id": "opt_a", "label_ar": "مَجْزُومًا بِالسُّكُونِ", "label_en": "Jussive with sukoon (Majzoom)"},
                    {"id": "opt_b", "label_ar": "مَرْفُوعًا بِالضَّمَّةِ", "label_en": "Nominative with dammah"},
                    {"id": "opt_c", "label_ar": "مَنْصُوبًا بِالفَتْحَةِ", "label_en": "Accusative with fatha"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 20: الحيوان والذكاء (Animal Intelligence) — Unit 6: كلنا أذكياء
# Pages 36-45 in Student Book (Volume 3)
# ============================================================================
ANIMAL_INTELLIGENCE_CONTENT = {
    "lesson_id": "lesson_20_animal_intelligence",
    "version": "0.2.0",
    "title_ar": "الحيوان والذكاء",
    "title_en": "Animals and Intelligence",
    "unit_title_ar": "كلنا أذكياء",
    "unit_title_en": "We Are All Smart",
    "grade": 5,
    "term": 3,
    "start_page": 36,
    "pdf_start_page": 110,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الحيوان والذكاء",
        "title_en": "Preparation Check: Animal Intelligence & Problem Solving",
        "description_en": "Prerequisite diagnostic testing cognitive feats in the animal kingdom.",
        "questions": [
            {
                "id": "prep_ai_01",
                "prompt_ar": "أَيُّ الحَيَوَانَاتِ البَحْرِيَّةِ يَشْتَهِرُ بِذَكَائِهِ وَاسْتِخْدَامِ الصَّدَى لِتَحْدِيدِ المَوَاقِعِ؟",
                "prompt_en": "Which marine mammal is famous for intelligence and using echolocation?",
                "options": [
                    {"id": "opt_a", "label_ar": "الدُّلْفِينُ", "label_en": "The Dolphin"},
                    {"id": "opt_b", "label_ar": "قِنْدِيلُ البَحْرِ", "label_en": "Jellyfish"},
                    {"id": "opt_c", "label_ar": "نَجْمُ البَحْرِ", "label_en": "Starfish"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Dolphins (الدلافين) are remarkably intelligent creatures capable of complex sonar navigation and social cooperation."
            },
            {
                "id": "prep_ai_02",
                "prompt_ar": "مَا مَعْنَى كَلِمَة (نَبِيهَة)؟",
                "prompt_en": "What is the meaning of 'nabeeha' (clever / alert)?",
                "options": [
                    {"id": "opt_a", "label_ar": "ذَكِيَّةٌ وَسَرِيعَةُ الفَهْمِ", "label_en": "Smart and quick-witted"},
                    {"id": "opt_b", "label_ar": "كَسُولَةٌ وَنَائِمَةٌ", "label_en": "Lazy and asleep"},
                    {"id": "opt_c", "label_ar": "بَطِيئَةُ الحَرَكَةِ", "label_en": "Slow moving"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "النبيهة means intelligent, observant, and sharp-minded."
            },
            {
                "id": "prep_ai_03",
                "prompt_ar": "كَيْفَ يَحُلُّ الغُرَابُ المَشَاكِلَ فِي الطَّبِيعَةِ؟",
                "prompt_en": "How do crows solve problems in nature?",
                "options": [
                    {"id": "opt_a", "label_ar": "بِاسْتِخْدَامِ الأَدَوَاتِ مِثْلِ العِصِيِّ وَإِلْقَاءِ الحِجَارَةِ", "label_en": "Using tools such as sticks and dropping stones"},
                    {"id": "opt_b", "label_ar": "بِالبُكَاءِ الطَّوِيلِ", "label_en": "By crying"},
                    {"id": "opt_c", "label_ar": "بِالنَّوْمِ شِتَاءً", "label_en": "By sleeping in winter"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Crows use natural tools and drop stones into narrow pitchers to raise water levels."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary matching: نبيه، صدى مائي، استثنائي، حوت أبيض، خمول.",
            "target": "Recognize cognitive traits in dolphins, sea lions, and crows."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Sentence building with (كَانَ وَأَخَوَاتُهَا): كَانَ الحَيَوَانُ ذَكِيًّا.",
            "target": "Master the effect of Kana on nominal sentences (رفع المبتدأ ونصب الخبر)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Compose an investigative article on animal communication and sonar navigation.",
            "target": "Write a 3-paragraph nature report evaluating whether animal behavior is pure instinct or learned intelligence."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أُمَيِّزُ",
            "transliteration": "Umayyizu",
            "meaning_en": "I distinguish / differentiate",
            "action_guidance": "Distinguish between verified scientific fact and folklore myths.",
            "sample_sentence_ar": "أُمَيِّزُ بَيْنَ الحَقِيقَةِ العِلْمِيَّةِ وَالخَيَالِ فِي سُلُوكِ الحَيَوَانِ.",
            "sample_sentence_en": "I distinguish between scientific fact and myth in animal behavior."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_ai_01",
            "word_ar": "نَبِيهَةٌ",
            "vowelled_ar": "نَبِيهَةٌ",
            "meaning_en": "Alert / Clever / Quick-Witted",
            "definition_ar": "ذَكِيَّةٌ وَفَطِنَةٌ وَسَرِيعَةُ الإِدْرَاكِ.",
            "example_ar": "تَمْتَلِكُ القِطَّةُ حَوَاسَّ نَبِيهَةً تُسَاعِدُهَا عَلَى الصَّيْدِ.",
            "example_en": "The cat possesses keen senses that assist its hunting.",
            "root": "ن-ب-ه",
            "category": "intelligence"
        },
        {
            "id": "vocab_ai_02",
            "word_ar": "اسْتِثْنَائِيٌّ",
            "vowelled_ar": "اسْتِثْنَائِيٌّ",
            "meaning_en": "Exceptional / Extraordinary",
            "definition_ar": "فَرِيدٌ وَغَيْرُ مُعْتَادٍ فِي قُدْرَتِهِ.",
            "example_ar": "يَتَمَتَّعُ الدُّلْفِينُ بِذَكَاءٍ اسْتِثْنَائِيٍّ فِي البَحْرِ.",
            "example_en": "The dolphin enjoys extraordinary intelligence in the sea.",
            "root": "ث-ن-ي",
            "category": "descriptive"
        },
        {
            "id": "vocab_ai_03",
            "word_ar": "الصَّدَى المَائِيُّ",
            "vowelled_ar": "الصَّدَى المَائِيُّ",
            "meaning_en": "Underwater Sonar / Echolocation",
            "definition_ar": "ارْتِدَادُ الأَصْوَاتِ لِتَحْدِيدِ مَوَاقِعِ الأَشْيَاءِ تَحْتَ المَاءِ.",
            "example_ar": "تَسْتَخْدِمُ الحِيتَانُ الصَّدَى المَائِيَّ لِلتَّوَاصُلِ عَبْرَ المُحِيطَاتِ.",
            "example_en": "Whales use underwater echolocation to communicate across oceans.",
            "root": "ص-د-ي",
            "category": "science"
        },
        {
            "id": "vocab_ai_04",
            "word_ar": "الخُمُولُ",
            "vowelled_ar": "الخُمُولُ",
            "meaning_en": "Lethargy / Inactivity",
            "definition_ar": "الكَسَلُ وَقِلَّةُ الحَرَكَةِ.",
            "example_ar": "يَبْتَعِدُ الحَيَوَانُ النَّشِيطُ عَنِ الخُمُولِ فِي الصَّبَاحِ.",
            "example_en": "The active animal avoids lethargy in the morning.",
            "root": "خ-م-ل",
            "category": "behavior"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: كَانَ وَأَخَوَاتُهَا (الأَفْعَالُ النَّاسِخَةُ)",
        "title_en": "Grammar Lab: Kana and its Sisters (الأفعال الناسخة)",
        "sections": [
            {
                "rule_name_ar": "عمل كان وأخواتها (رفع المبتدأ ونصب الخبر)",
                "rule_name_en": "Function of Kana: Enters nominal sentence, subject remains nominative, predicate becomes accusative",
                "explanation_en": "Kana (كان), Asbaha (أصبح), Sara (صار), Laysa (ليس). The Ism Kana is marfoo' (dammah); the Khabar Kana is mansoob (fatha).",
                "examples": [
                    {"phrase_ar": "كَانَ الحَيَوَانُ نَبِيهًا.", "translation_en": "The animal was alert."},
                    {"phrase_ar": "أَصْبَحَ الدُّلْفِينُ مُدَرَّبًا.", "translation_en": "The dolphin became trained."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: ذكاء الكائنات البحرية",
        "title_en": "Sentence Construction Studio: Marine Intelligence",
        "challenges": [
            {
                "id": "sb_ai_01",
                "instruction_en": "Arrange the words using Kana:",
                "target_sentence_ar": "كَانَ الدُّلْفِينُ سَرِيعًا فِي تَعَلُّمِ الحَرَكَاتِ المَائِيَّةِ.",
                "scrambled_tokens": ["سَرِيعًا", "تَعَلُّمِ", "كَانَ", "الحَرَكَاتِ", "فِي", "الدُّلْفِينُ", "المَائِيَّةِ."],
                "translation_en": "The dolphin was fast in learning aquatic movements."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: الدلافين وأسود البحر الذكية",
        "title_en": "Listen & Speak Studio: Dolphins and Sea Lions",
        "passage_ar": "أَثْبَتَتِ الدِّرَاسَاتُ العِلْمِيَّةُ أَنَّ بَعْضَ الحَيَوَانَاتِ تَمْتَلِكُ ذَكَاءً خَارِقًا. فَالدَّلَافِينُ تَسْتَطِيعُ التَّعَرُّفَ عَلَى أَنْفُسِهَا فِي المِرْآةِ، وَتَتَعَاوَنُ فِيمَا بَيْنَهَا لِصَيْدِ الأَسْمَاكِ، كَمَا تَسْتَخْدِمُ الصَّدَى لِرُؤْيَةِ كُلِّ شَيْءٍ فِي أَعْمَاقِ البَحْرِ المُظْلِمَةِ.",
        "passage_en": "Scientific studies proved that certain animals possess astonishing intelligence. Dolphins recognize themselves in mirrors, cooperate to herd schools of fish, and use sonar to 'see' through the darkest ocean depths.",
        "audio_scripts": [
            {"id": "aud_ai_01", "text_ar": "ذَكَاءُ الحَيَوَانَاتِ دَلِيلٌ عَلَى إِبْدَاعِ الطَّبِيعَةِ.", "text_en": "Animal intelligence is testimony to nature's creativity."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_ai_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: خبر كان وأخواتها",
            "title_en": "Grammar: Predicate of Kana",
            "prompt_ar": "مَا هُوَ الضَّبْطُ الصَّحِيحُ لِكَلِمَةِ (ذَكِيّ) فِي جُمْلَةِ: (أَصْبَحَ القِرْدُ ........)؟",
            "prompt_en": "What is the correct vowelling for 'thaki' in 'Asbaha al-qirdu ........'?",
            "options": [
                {"id": "opt_a", "label_ar": "ذَكِيًّا (مَنْصُوبٌ بِالفَتْحَةِ)", "label_en": "Thakiyyan (Accusative with fatha)"},
                {"id": "opt_b", "label_ar": "ذَكِيٌّ (مَرْفُوعٌ بِالضَّمَّةِ)", "label_en": "Thakiyyun (Nominative)"},
                {"id": "opt_c", "label_ar": "ذَكِيٍّ (مَجْرُورٌ بِالكَسْرَةِ)", "label_en": "Thakiyyin (Genitive)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: حكاية الحيوان العبقري",
        "title_en": "Speaking Mission: Tale of the Genius Animal",
        "scenario_en": "Narrate a 30-second factual story to your classmates about an animal (crow, dolphin, or rescue dog) solving a clever puzzle.",
        "prompts_ar": [
            "كَانَ الغُرَابُ عَطْشَانًا فَرَأَى جَرَّةَ مَاءٍ ضَيِّقَةً.",
            "أَلْقَى الحِجَارَةَ فِيهَا حَتَّى ارْتَفَعَ المَاءُ إِلَى أَعْلَى.",
            "هَذَا دَلِيلٌ عَلَى أَنَّ الحَيَوَانَاتِ قَادِرَةٌ عَلَى حَلِّ المَشَاكِلِ."
        ],
        "recording_task_en": "Speak with expressive storytelling tone."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الحيوان والذكاء",
        "title_en": "Parent Companion: Animal Intelligence Lesson",
        "summary_en": "Covers cognitive biology, tool usage in wildlife, and Kana syntax (كان الولدُ ذكياً).",
        "dinner_table_prompts": [
            {"arabic": "مَا هُوَ أَذْكَى حَيَوَانٍ تَعْرِفُهُ؟", "english": "What is the smartest animal you know?", "phonetic": "Ma huwa athka hayawan ta'rifuhu?"}
        ],
        "home_practice_checklist": [
            "Practice sentences with Kana: كان الجوُ جميلاً، أصبحت الغرفةُ نظيفةً.",
            "Ask your child how dolphins communicate underwater."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس الحيوان والذكاء",
        "learning_objectives": ["Understand animal problem-solving traits", "Master Kana and its sisters vowelling rules", "Differentiate instinct from learned adaptation"],
        "misconception_flags": ["Leaving khabar kana in nominative case (dhammah) instead of accusative (fatha)"],
        "recommended_drills": ["Kana sentence transformation tables", "Marine biology vocabulary matching"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_ai_01",
                "prompt_ar": "خَبَرُ (كَانَ) يَكُونُ دَائِمًا:",
                "prompt_en": "The predicate of Kana is always:",
                "options": [
                    {"id": "opt_a", "label_ar": "مَنْصُوبًا", "label_en": "Accusative (Mansoob)"},
                    {"id": "opt_b", "label_ar": "مَرْفُوعًا", "label_en": "Nominative (Marfoo')"},
                    {"id": "opt_c", "label_ar": "مَجْرُورًا", "label_en": "Genitive (Majroor)"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 21: الإنسان والذكاء (Human Intelligence) — Unit 6: كلنا أذكياء
# Pages 46-55 in Student Book (Volume 3)
# ============================================================================
HUMAN_INTELLIGENCE_CONTENT = {
    "lesson_id": "lesson_21_human_intelligence",
    "version": "0.2.0",
    "title_ar": "الإنسان والذكاء",
    "title_en": "Humans and Intelligence",
    "unit_title_ar": "كلنا أذكياء",
    "unit_title_en": "We Are All Smart",
    "grade": 5,
    "term": 3,
    "start_page": 46,
    "pdf_start_page": 120,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس الإنسان والذكاء",
        "title_en": "Preparation Check: Human Intelligence & Creativity",
        "description_en": "Diagnostic covering types of intelligence, continuous learning, and innovation.",
        "questions": [
            {
                "id": "prep_hi_01",
                "prompt_ar": "مَا هِيَ نَظَرِيَّةُ الذَّكَاءَاتِ المُتَعَدِّدَةِ لَدَى الإِنْسَانِ؟",
                "prompt_en": "What is the theory of multiple intelligences in humans?",
                "options": [
                    {"id": "opt_a", "label_ar": "كُلُّ إِنْسَانٍ يَمْتَلِكُ مَوَاهِبَ مُخْتَلِفَةً كَاللُّغَوِيِّ وَالرِّيَاضِيِّ وَالفَنِّيِّ", "label_en": "Every human possesses different strengths: linguistic, math, artistic"},
                    {"id": "opt_b", "label_ar": "الجَمِيعُ لَدَيْهِمْ مَوْهِبَةٌ وَاحِدَةٌ فَقَطْ", "label_en": "Everyone has only one single talent"},
                    {"id": "opt_c", "label_ar": "الذَّكَاءُ لَا يَتَطَوَّرُ أَبَدًا", "label_en": "Intelligence never develops"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Human intelligence is multifaceted: linguistic, logical-mathematical, spatial, musical, and interpersonal."
            },
            {
                "id": "prep_hi_02",
                "prompt_ar": "كَيْفَ يُطَوِّرُ الإِنْسَانُ ذَكَاءَهُ وَقُدْرَاتِهِ؟",
                "prompt_en": "How does a person develop their intelligence and abilities?",
                "options": [
                    {"id": "opt_a", "label_ar": "بِالقِرَاءَةِ وَالتَّعَلُّمِ المُسْتَمِرِّ وَحَلِّ الأَلْغَازِ", "label_en": "Through reading, lifelong learning, and problem-solving"},
                    {"id": "opt_b", "label_ar": "بِتَجَنُّبِ المَوَادِّ الدِّرَاسِيَّةِ", "label_en": "By avoiding school subjects"},
                    {"id": "opt_c", "label_ar": "بِالِاعْتِمَادِ عَلَى الآخَرِينَ فِي كُلِّ شَيْءٍ", "label_en": "Relying on others for everything"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Reading, brain exercises, and perseverance expand neural cognitive pathways."
            },
            {
                "id": "prep_hi_03",
                "prompt_ar": "مَا مَعْنَى كَلِمَة (المَوْهِبَة)؟",
                "prompt_en": "What is the meaning of 'talent' (موهبة)?",
                "options": [
                    {"id": "opt_a", "label_ar": "القُدْرَةُ الفِطْرِيَّةُ الخَاصَّةُ فِي مَجَالٍ مُعَيَّنٍ", "label_en": "Special innate aptitude in a given domain"},
                    {"id": "opt_b", "label_ar": "السَّفَرُ إِلَى الخَارِجِ", "label_en": "Traveling abroad"},
                    {"id": "opt_c", "label_ar": "شِرَاءُ المَلَابِسِ", "label_en": "Buying clothes"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "الموهبة is innate aptitude nurtured through deliberate practice."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Identifying areas of personal intelligence (words, numbers, nature, art).",
            "target": "Master 6 core terms: موهبة، ابتكار، تفكير نقدي، عبقرية، مهارة، فضول."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Sentence building with (إِنَّ وَأَخَوَاتُهَا): إِنَّ العِلْمَ نُورٌ.",
            "target": "Master the effect of Inna on nominal sentences (نصب الاسم ورفع الخبر)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Compose an autobiographical self-portrait highlighting unique personal strengths.",
            "target": "Draft a reflective portfolio outlining how you utilize your intelligence to benefit the community."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَكْشِفُ",
            "transliteration": "Astakshifu",
            "meaning_en": "I explore / discover",
            "action_guidance": "Discover your personal unique intelligences and strengths.",
            "sample_sentence_ar": "أَسْتَكْشِفُ مَوَاهِبِي فِي الرَّسْمِ وَالكِتَابَةِ الإِبْدَاعِيَّةِ.",
            "sample_sentence_en": "I discover my talents in drawing and creative writing."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_hi_01",
            "word_ar": "المَوْهِبَةُ",
            "vowelled_ar": "المَوْهِبَةُ",
            "meaning_en": "Talent / Gift",
            "definition_ar": "قُدْرَةٌ مُمَيَّزَةٌ يَمْنَحُهَا اللهُ لِلإِنْسَانِ وَيُنَمِّيهَا بِالتَّدْرِيبِ.",
            "example_ar": "يَمْتَلِكُ أَخِي مَوْهِبَةً رَائِعَةً فِي حِفْظِ الشِّعْرِ العَرَبِيِّ.",
            "example_en": "My brother possesses a wonderful talent for memorizing Arabic poetry.",
            "root": "و-ه-ب",
            "category": "education"
        },
        {
            "id": "vocab_hi_02",
            "word_ar": "الابْتِكَارُ",
            "vowelled_ar": "الابْتِكَارُ",
            "meaning_en": "Innovation / Inventiveness",
            "definition_ar": "اخْتِرَاعُ حُلُولٍ جَدِيدَةٍ لِخِدْمَةِ الإِنْسَانِيَّةِ.",
            "example_ar": "تُشَجِّعُ دَوْلَةُ الإِمَارَاتِ الِابْتِكَارَ فِي جَمِيعِ المَجَالَاتِ.",
            "example_en": "The UAE encourages innovation across all fields.",
            "root": "ب-ك-ر",
            "category": "innovation"
        },
        {
            "id": "vocab_hi_03",
            "word_ar": "التَّفْكِيرُ النَّقْدِيُّ",
            "vowelled_ar": "التَّفْكِيرُ النَّقْدِيُّ",
            "meaning_en": "Critical Thinking",
            "definition_ar": "التَّحْلِيلُ المَنْطِقِيُّ لِلتَّمْيِيزِ بَيْنَ الصَّحِيحِ وَالخَاطِئِ.",
            "example_ar": "يُسَاعِدُنَا التَّفْكِيرُ النَّقْدِيُّ عَلَى حَلِّ المَسَائِلِ الصَّعْبَةِ.",
            "example_en": "Critical thinking helps us resolve complex problems.",
            "root": "ف-ك-ر",
            "category": "cognition"
        },
        {
            "id": "vocab_hi_04",
            "word_ar": "العَبْقَرِيَّةُ",
            "vowelled_ar": "العَبْقَرِيَّةُ",
            "meaning_en": "Genius / Brilliance",
            "definition_ar": "التَّفَوُّقُ العَقْلِيُّ العَالِي جِدًّا.",
            "example_ar": "عُرِفَ عُلَمَاءُ العَرَبِ بِالعَبْقَرِيَّةِ فِي الفَلَكِ وَالطِّبِّ.",
            "example_en": "Arab scholars were renowned for brilliance in astronomy and medicine.",
            "root": "ع-ب-ق-ر",
            "category": "intelligence"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: إِنَّ وَأَخَوَاتُهَا (الحُرُوفُ النَّاسِخَةُ)",
        "title_en": "Grammar Lab: Inna and its Sisters (الحروف الناسخة)",
        "sections": [
            {
                "rule_name_ar": "عمل إن وأخواتها (نصب المبتدأ ورفع الخبر)",
                "rule_name_en": "Function of Inna: Enters nominal sentence, subject becomes accusative, predicate remains nominative",
                "explanation_en": "Inna (إِنَّ - certainty), Anna (أَنَّ), Ka'anna (كَأَنَّ - simile), Layta (لَيْتَ - wish), La'alla (لَعَلَّ - hope), Lakinna (لَكِنَّ). Ism Inna is mansoob (fatha); Khabar Inna is marfoo' (dammah). Exactly opposite of Kana!",
                "examples": [
                    {"phrase_ar": "إِنَّ العِلْمَ نُورٌ.", "translation_en": "Indeed knowledge is light."},
                    {"phrase_ar": "إِنَّ الإِنْسَانَ مُبْدِعٌ.", "translation_en": "Truly man is creative."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: قوة العقل البشري",
        "title_en": "Sentence Construction Studio: Power of Human Mind",
        "challenges": [
            {
                "id": "sb_hi_01",
                "instruction_en": "Arrange the words using Inna:",
                "target_sentence_ar": "إِنَّ الذَّكَاءَ يَتَطَوَّرُ بِالقِرَاءَةِ وَالتَّعَلُّمِ المُسْتَمِرِّ.",
                "scrambled_tokens": ["بِالقِرَاءَةِ", "يَتَطَوَّرُ", "إِنَّ", "المُسْتَمِرِّ.", "وَالتَّعَلُّمِ", "الذَّكَاءَ"],
                "translation_en": "Indeed intelligence develops with reading and continuous learning."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: قصة علماء العرب والمخترعين",
        "title_en": "Listen & Speak Studio: Arab Inventors and Scholars",
        "passage_ar": "مَيَّزَ اللهُ الإِنْسَانَ بِالعَقْلِ وَالتَّفْكِيرِ، وَأَلْهَمَهُ القُدْرَةَ عَلَى ابْتِكَارِ العُلُومِ. قَدَّمَ عُلَمَاءُ الحَضَارَةِ العَرَبِيَّةِ وَالإِسْلَامِيَّةِ مِثْلَ ابْنِ الهَيْثَمِ فِي البَصَرِيَّاتِ، وَالخَوَارِزْمِيِّ فِي الرِّيَاضِيَّاتِ، وَابْنِ سِينَا فِي الطِّبِّ، اخْتِرَاعَاتٍ غَيَّرَتْ مَجْرَى العَالَمِ.",
        "passage_en": "The Creator graced humanity with intellect and contemplation, inspiring scientific invention. Arab and Islamic civilization luminaries—Ibn Al-Haytham in optics, Al-Khwarizmi in algebra, and Ibn Sina in medicine—pioneered inventions that reshaped the world.",
        "audio_scripts": [
            {"id": "aud_hi_01", "text_ar": "العَقْلُ هُوَ أَعْظَمُ نِعْمَةٍ وُهِبَتْ لِلإِنْسَانِ.", "text_en": "The intellect is the greatest blessing bestowed upon humanity."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_hi_01",
            "type": "multiple_choice",
            "title_ar": "القواعد: اسم إن وأخواتها",
            "title_en": "Grammar: Subject of Inna",
            "prompt_ar": "مَا هُوَ الضَّبْطُ الصَّحِيحُ لِكَلِمَةِ (العَقْل) فِي جُمْلَةِ: (إِنَّ ........ نِعْمَةٌ عَظِيمَةٌ)؟",
            "prompt_en": "What is the correct vowelling for 'al-'aql' in 'Inna ........ ni'matun 'azeemah'?",
            "options": [
                {"id": "opt_a", "label_ar": "العَقْلَ (مَنْصُوبٌ بِالفَتْحَةِ)", "label_en": "Al-'Aqla (Accusative with fatha)"},
                {"id": "opt_b", "label_ar": "العَقْلُ (مَرْفُوعٌ بِالضَّمَّةِ)", "label_en": "Al-'Aqlu (Nominative)"},
                {"id": "opt_c", "label_ar": "العَقْلِ (مَجْرُورٌ بِالكَسْرَةِ)", "label_en": "Al-'Aqli (Genitive)"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: كيف سأخدم وطني بذكائي؟",
        "title_en": "Speaking Mission: How I Will Serve My Nation",
        "scenario_en": "Deliver an inspiring 30-second speech describing your dream profession (doctor, engineer, AI scientist, or astronaut) and how your talents will contribute to the UAE's progress.",
        "prompts_ar": [
            "أَحْلَمُ أَنْ أَكُونَ مُهَنْدِسًا مُبْتَكِرًا يَخْدِمُ بِلَادِي.",
            "سَأُوَظِّفُ ذَكَائِي فِي تَطْوِيرِ تِكْنُولُوجْيَا الطَّاقَةِ النَّظِيفَةِ.",
            "إِنَّ دَوْلَةَ الإِمَارَاتِ تَسْتَحِقُّ مِنَّا كُلَّ الجُهْدِ وَالإِبْدَاعِ."
        ],
        "recording_task_en": "Record with passion and patriotic pride in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس الإنسان والذكاء",
        "title_en": "Parent Companion: Human Intelligence Lesson",
        "summary_en": "Celebrates diverse talents, Arab inventors in history, and Inna grammar rules (اسم إن منصوب وخبرها مرفوع).",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ مَوْهِبَتُكَ الَّتِي تُحِبُّهَا؟", "english": "What is the talent you love?", "phonetic": "Ma hiya mawhibatuka allati tuhibbuha?"}
        ],
        "home_practice_checklist": [
            "Encourage your child's specific strengths (drawing, coding, languages, mathematics).",
            "Practice sentences with Inna: إنّ العلمَ نورٌ، إنّ الصدقَ منجاةٌ."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس الإنسان والذكاء",
        "learning_objectives": ["Identify multiple intelligence dimensions", "Master Inna and its sisters vowelling (opposing Kana)", "Recognize historical Arab scientific achievements"],
        "misconception_flags": ["Confusing Inna (accusative noun) with Kana (nominative noun)"],
        "recommended_drills": ["Kana vs Inna contrasting tables", "Arab inventors history quiz"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_hi_01",
                "prompt_ar": "اسْمُ (إِنَّ) يَكُونُ دَائِمًا:",
                "prompt_en": "The subject of Inna is always:",
                "options": [
                    {"id": "opt_a", "label_ar": "مَنْصُوبًا بِالفَتْحَةِ", "label_en": "Accusative with fatha"},
                    {"id": "opt_b", "label_ar": "مَرْفُوعًا بِالضَّمَّةِ", "label_en": "Nominative with dammah"},
                    {"id": "opt_c", "label_ar": "مَجْرُورًا بِالكَسْرَةِ", "label_en": "Genitive with kasrah"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}


# ============================================================================
# LESSON 22: مدن ذكية (Smart Cities) — Unit 6: كلنا أذكياء
# Pages 56-65 in Student Book (Volume 3)
# ============================================================================
SMART_CITIES_CONTENT = {
    "lesson_id": "lesson_22_smart_cities",
    "version": "0.2.0",
    "title_ar": "مدن ذكية",
    "title_en": "Smart Cities",
    "unit_title_ar": "كلنا أذكياء",
    "unit_title_en": "We Are All Smart",
    "grade": 5,
    "term": 3,
    "start_page": 56,
    "pdf_start_page": 130,

    "prep_check": {
        "title_ar": "اختبار الاستعداد لدرس مدن ذكية",
        "title_en": "Preparation Check: Smart Cities & Sustainability",
        "description_en": "Prerequisite diagnostic testing concepts of clean energy, Masdar City, and AI.",
        "questions": [
            {
                "id": "prep_sc_01",
                "prompt_ar": "مَا هِيَ المَدِينَةُ الإِمَارَاتِيَّةُ الشَّهِيرَةُ عَالَمِيًّا كَنَمُوذَجٍ لِلطَّاقَةِ النَّظِيفَةِ وَالاسْتِدَامَةِ؟",
                "prompt_en": "What UAE city is globally acclaimed as a model for clean energy and sustainability?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَدِينَةُ مَصْدَرٍ فِي أَبُوظَبِي", "label_en": "Masdar City in Abu Dhabi"},
                    {"id": "opt_b", "label_ar": "مَدِينَةُ الضَّبَابِ", "label_en": "City of Fog"},
                    {"id": "opt_c", "label_ar": "مَدِينَةُ المَلَاهِي", "label_en": "Amusement city"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Masdar City (مدينة مصدر) in Abu Dhabi is a pioneer in zero-carbon urban living."
            },
            {
                "id": "prep_sc_02",
                "prompt_ar": "مَاذَا تَعْنِي (الطَّاقَةُ المُتَجَدِّدَةُ)؟",
                "prompt_en": "What does 'renewable energy' mean?",
                "options": [
                    {"id": "opt_a", "label_ar": "طَاقَةٌ نَظِيفَةٌ لَا تَنْفَدُ مِثْلَ الشَّمْسِ وَالرِّيَاحِ", "label_en": "Clean, inexhaustible energy like solar and wind"},
                    {"id": "opt_b", "label_ar": "وَقُودُ الفَحْمِ المُلَوِّثُ", "label_en": "Polluting coal fuel"},
                    {"id": "opt_c", "label_ar": "المِيَاهُ الغَازِيَّةُ", "label_en": "Carbonated water"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Renewable energy (طاقة متجددة) harnesses natural replenished sources without polluting the air."
            },
            {
                "id": "prep_sc_03",
                "prompt_ar": "كَيْفَ تَسِيرُ السِّيَارَاتُ ذَاتِيَّةُ القِيَادَةِ فِي المَدِينَةِ الذَّكِيَّةِ؟",
                "prompt_en": "How do self-driving vehicles navigate in a smart city?",
                "options": [
                    {"id": "opt_a", "label_ar": "بِوَاسِطَةِ أَنْظِمَةِ الذَّكَاءِ الِاصْطِنَاعِيِّ وَالحَسَّاسَاتِ", "label_en": "Using AI algorithms and smart sensors"},
                    {"id": "opt_b", "label_ar": "بِوَاسِطَةِ الخُيُولِ", "label_en": "Pulled by horses"},
                    {"id": "opt_c", "label_ar": "بِالرِّيَاحِ فَقَطْ", "label_en": "By wind only"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Autonomous transport uses sensors, radar, and artificial intelligence to navigate safely."
            }
        ]
    },

    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Vocabulary matching with futuristic Masdar City icons.",
            "target": "Master 6 core terms: مدينة ذكية، طاقة متجددة، استدامة، ذكاء اصطناعي، انبعاثات كربونية."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Future tense phrasing (السين وسوف: سَنَبْنِي مُدُنًا ذَكِيَّةً).",
            "target": "Draft statements expressing futuristic vision using future markers (سـ / سوف)."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Design your own futuristic zero-carbon smart city proposal for UAE Centennial 2071.",
            "target": "Write a comprehensive urban project overview featuring autonomous drones, vertical farms, and solar arrays."
        }
    },

    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَشْرِفُ المُسْتَقْبَلَ",
            "transliteration": "Astashrifu al-Mustaqbal",
            "meaning_en": "I foresee / envision the future",
            "action_guidance": "Envision innovative solutions that make cities eco-friendly and smart.",
            "sample_sentence_ar": "أَسْتَشْرِفُ مُسْتَقْبَلَ المُدُنِ الذَّكِيَّةِ فِي دَوْلَةِ الإِمَارَاتِ.",
            "sample_sentence_en": "I envision the future of smart cities in the UAE."
        }
    ],

    "vocabulary_cards": [
        {
            "id": "vocab_sc_01",
            "word_ar": "مَدِينَةٌ ذَكِيَّةٌ",
            "vowelled_ar": "مَدِينَةٌ ذَكِيَّةٌ",
            "meaning_en": "Smart City",
            "definition_ar": "مَدِينَةٌ حَدِيثَةٌ تُوَظِّفُ التِّكْنُولُوجْيَا الرَّقْمِيَّةَ وَالطَّاقَةَ النَّظِيفَةَ لِخِدْمَةِ الإِنْسَانِ.",
            "example_ar": "مَدِينَةُ مَصْدَرٍ فِي أَبُوظَبِي نَمُوذَجٌ عَالَمِيٌّ لِلمُدُنِ الذَّكِيَّةِ.",
            "example_en": "Masdar City in Abu Dhabi is a global model for smart cities.",
            "root": "م-د-ن / ذ-ك-ي",
            "category": "urban"
        },
        {
            "id": "vocab_sc_02",
            "word_ar": "الاسْتِدَامَةُ",
            "vowelled_ar": "الاسْتِدَامَةُ",
            "meaning_en": "Sustainability",
            "definition_ar": "الحِفَاظُ عَلَى المَوَارِدِ الطَّبِيعِيَّةِ لِفَائِدَةِ الأَجْيَالِ القَادِمَةِ.",
            "example_ar": "تُرَكِّزُ دَوْلَةُ الإِمَارَاتِ عَلَى مَشَارِيعِ الاسْتِدَامَةِ البِيئِيَّةِ.",
            "example_en": "The UAE focuses on environmental sustainability projects.",
            "root": "د-و-م",
            "category": "environment"
        },
        {
            "id": "vocab_sc_03",
            "word_ar": "الطَّاقَةُ الشَّمْسِيَّةُ",
            "vowelled_ar": "الطَّاقَةُ الشَّمْسِيَّةُ",
            "meaning_en": "Solar Energy",
            "definition_ar": "تَوْلِيدُ الكَهْرَبَاءِ النَّظِيفَةِ مِنْ ضَوْءِ وَحَرَارَةِ الشَّمْسِ.",
            "example_ar": "تَعْتَمِدُ مَدِينَةُ مَصْدَرٍ عَلَى أَلْوَاحِ الطَّاقَةِ الشَّمْسِيَّةِ.",
            "example_en": "Masdar City relies on solar energy panels.",
            "root": "ش-م-س",
            "category": "energy"
        },
        {
            "id": "vocab_sc_04",
            "word_ar": "الذَّكَاءُ الِاصْطِنَاعِيُّ",
            "vowelled_ar": "الذَّكَاءُ الِاصْطِنَاعِيُّ",
            "meaning_en": "Artificial Intelligence (AI)",
            "definition_ar": "قُدْرَةُ الأَجْهِزَةِ وَالحَوَاسِيبِ عَلَى مُحَاكَاةِ القُدُرَاتِ الذِّهْنِيَّةِ البَشَرِيَّةِ.",
            "example_ar": "يُدِيرُ الذَّكَاءُ الِاصْطِنَاعِيُّ حَرَكَةَ المُرُورِ فِي المَدِينَةِ الذَّكِيَّةِ.",
            "example_en": "Artificial intelligence manages traffic in the smart city.",
            "root": "ص-ن-ع",
            "category": "technology"
        }
    ],

    "grammar_lab": {
        "title_ar": "مختبر القواعد: التعبير عن المستقبل (السين وسوف)",
        "title_en": "Grammar Lab: Future Tense Particles (Sa- and Sawfa)",
        "sections": [
            {
                "rule_name_ar": "حروف الاستقبال (السين للقريب، سوف للبعيد)",
                "rule_name_en": "Future Particles: 'Sa-' for near future, 'Sawfa' for distant future",
                "explanation_en": "Prefixing 'Sa-' (سـ) directly to present verb indicates near future. 'Sawfa' (سَوْفَ) is a standalone particle indicating broader long-term future. The verb remains in the indicative (marfoo' with dammah).",
                "examples": [
                    {"phrase_ar": "سَنَبْنِي مُدُنًا نَظِيفَةً.", "translation_en": "We will build clean cities (Near future)."},
                    {"phrase_ar": "سَوْفَ تَحْمِي الاسْتِدَامَةُ كَوْكَبَنَا.", "translation_en": "Sustainability will protect our planet (Long-term)."}
                ]
            }
        ]
    },

    "sentence_builder": {
        "title_ar": "باني الجمل: مدينة مصدر المستدامة",
        "title_en": "Sentence Construction Studio: Masdar Eco-City",
        "challenges": [
            {
                "id": "sb_sc_01",
                "instruction_en": "Arrange the words to describe Masdar City:",
                "target_sentence_ar": "تَسْتَخْدِمُ مَدِينَةُ مَصْدَرٍ الطَّاقَةَ النَّظِيفَةَ لِتَقْلِيلِ الانْبِعَاثَاتِ الضَّارَّةِ.",
                "scrambled_tokens": ["مَصْدَرٍ", "تَسْتَخْدِمُ", "لِتَقْلِيلِ", "مَدِينَةُ", "الضَّارَّةِ.", "النَّظِيفَةَ", "الطَّاقَةَ", "الانْبِعَاثَاتِ"],
                "translation_en": "Masdar City uses clean energy to reduce harmful emissions."
            }
        ]
    },

    "listen_speak_studio": {
        "title_ar": "استوديو الاستماع والتحدث: جولة في مدينة مصدر",
        "title_en": "Listen & Speak Studio: Tour of Masdar City",
        "passage_ar": "مَدِينَةُ مَصْدَرٍ هِيَ أَوَّلُ مَدِينَةٍ خَالِيَةٍ مِنَ الكَرْبُونِ وَالنِّفَايَاتِ فِي الشَّرْقِ الأَوْسَطِ. تُسَيِّرُ المَدِينَةُ حَافِلَاتٍ كَهْرَبَائِيَّةً ذَاتِيَّةَ القِيَادَةِ تَحْتَ الأَرْضِ، وَتَعْتَمِدُ عَلَى الشَّمْسِ لِتَوْلِيدِ كُلِّ كَهْرَبَائِهَا، لِتَكُونَ مُلْهِمَةً لِكُلِّ مُدُنِ العَالَمِ فِي الحِفَاظِ عَلَى كَوْكَبِ الأَرْضِ.",
        "passage_en": "Masdar City is the Middle East's first carbon-neutral, zero-waste community. The city operates driverless underground electric shuttles and harnesses the sun for all its electricity, inspiring global cities in planetary preservation.",
        "audio_scripts": [
            {"id": "aud_sc_01", "text_ar": "مَدِينَةُ مَصْدَرٍ فَخْرُ الاسْتِدَامَةِ الإِمَارَاتِيَّةِ.", "text_en": "Masdar City is the pride of Emirati sustainability."}
        ]
    },

    "practice_activities": [
        {
            "id": "act_sc_01",
            "type": "multiple_choice",
            "title_ar": "فهم المقروء: مواصلات مدينة مصدر",
            "title_en": "Reading Comprehension: Masdar Transit",
            "prompt_ar": "كَيْفَ تَعْمَلُ المَرْكَبَاتُ فِي مَدِينَةِ مَصْدَرٍ؟",
            "prompt_en": "How do vehicles operate in Masdar City?",
            "options": [
                {"id": "opt_a", "label_ar": "مَرْكَبَاتٌ كَهْرَبَائِيَّةٌ ذَاتِيَّةُ القِيَادَةِ دُونَ انْبِعَاثَاتٍ", "label_en": "Autonomous electric zero-emission pods"},
                {"id": "opt_b", "label_ar": "سَيَّارَاتٌ تَعْمَلُ بِالفَحْمِ", "label_en": "Cars powered by coal"},
                {"id": "opt_c", "label_ar": "شَاحِنَاتٌ كَبِيرَةٌ مُلَوِّثَةٌ", "label_en": "Large polluting trucks"}
            ],
            "correct_answer": "opt_a",
            "points": 10
        }
    ],

    "speaking_mission": {
        "title_ar": "مهمة التحدث: أنا مهندس مدينة المستقبل",
        "title_en": "Speaking Mission: Architect of the Future City",
        "scenario_en": "Present your vision for a futuristic UAE smart school in 2071, explaining how solar panels, AI tutors, and green gardens will make learning joyful and sustainable.",
        "prompts_ar": [
            "سَتَكُونُ مَدْرَسَتُنَا الذَّكِيَّةُ خَالِيَةً تَمَامًا مِنَ الانْبِعَاثَاتِ.",
            "سَوْفَ نَسْتَخْدِمُ الرُّوبُوتَاتِ لِمُسَاعَدَةِ الطُّلَّابِ فِي التَّجَارِبِ.",
            "الاسْتِدَامَةُ هِيَ مِفْتَاحُ الحَيَاةِ الجَمِيلَةِ لِلأَجْيَالِ القَادِمَةِ."
        ],
        "recording_task_en": "Speak with forward-looking enthusiasm in Arabic."
    },

    "parent_companion": {
        "title_ar": "دليل ولي الأمر: درس مدن ذكية",
        "title_en": "Parent Companion: Smart Cities Lesson",
        "summary_en": "Explores clean energy, Masdar City sustainability, AI innovation, and future tense markers (سـ / سوف).",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ مَدِينَةُ مَصْدَرٍ؟", "english": "What is Masdar City?", "phonetic": "Ma hiya madeenatu masdar?"}
        ],
        "home_practice_checklist": [
            "Practice future tense sentences with 'Sa-' and 'Sawfa' (سنحافظ على بيئتنا، سوف نبتكر).",
            "Discuss recycling and saving electricity at home as a family."
        ]
    },

    "tutor_handover": {
        "title_ar": "بطاقة المعلم: درس مدن ذكية",
        "learning_objectives": ["Identify smart city and clean energy terminology", "Master future tense particle usage (سـ vs سوف)", "Explain Masdar City sustainable innovations"],
        "misconception_flags": ["Using English will without prefixing Arabic Sin or Sawfa to the verb"],
        "recommended_drills": ["Future tense verb prefixing drills", "Eco-city diagram labeling"]
    },

    "exam_practice": {
        "objective_questions": [
            {
                "id": "ep_sc_01",
                "prompt_ar": "حَرْفُ الِاسْتِقْبَالِ الَّذِي يَدُلُّ عَلَى المُسْتَقْبَلِ القَرِيبِ هُوَ:",
                "prompt_en": "The particle indicating near future prefixed to the present verb is:",
                "options": [
                    {"id": "opt_a", "label_ar": "السِّينُ (سَـ)", "label_en": "Sin (Sa-)"},
                    {"id": "opt_b", "label_ar": "قَدْ", "label_en": "Qad"},
                    {"id": "opt_c", "label_ar": "لَمْ", "label_en": "Lam"}
                ],
                "correct_answer": "opt_a",
                "marks": 10
            }
        ]
    }
}

# Catalog dictionary mapping lesson_id to full package for Term 3
TERM3_CURRICULUM_CATALOG = {
    "lesson_17_carrier_pigeons": CARRIER_PIGEONS_CONTENT,
    "lesson_18_the_media": THE_MEDIA_CONTENT,
    "lesson_19_social_media": SOCIAL_MEDIA_CONTENT,
    "lesson_20_animal_intelligence": ANIMAL_INTELLIGENCE_CONTENT,
    "lesson_21_human_intelligence": HUMAN_INTELLIGENCE_CONTENT,
    "lesson_22_smart_cities": SMART_CITIES_CONTENT
}
