import json
import hashlib
from sqlalchemy.orm import Session
from backend.models import (
    School, BookEdition, Unit, Lesson, LessonVersion, ScannedPage,
    User, ChildProfile, TermAccess, GamificationProfile, LearnerBadge, ConceptMastery, VoucherCode
)
from backend.security import hash_password
from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG

BALL_GAMES_CONTENT_V02 = {
    "lesson_id": "lesson_01_ball_games",
    "version": "0.2.0",
    "title_ar": "ألعاب الكرة",
    "title_en": "Ball Games",
    "unit_title_ar": "الرياضات والهوايات",
    "unit_title_en": "Sports and Hobbies",
    "grade": 5,
    "term": 1,
    "start_page": 6,
    "pdf_start_page": 8,
    
    # 1. Preparation Check
    "prep_check": {
        "title_ar": "اختبار الاستعداد والمتطلبات السابقة",
        "title_en": "Preparation Check & Prerequisite Diagnostic",
        "description_en": "Quick 3-question diagnostic to ensure readiness before starting Ball Games.",
        "questions": [
            {
                "id": "prep_01",
                "prompt_ar": "ما معنى كلمة (رِيَاضَة)؟",
                "prompt_en": "What is the meaning of the word (Sport)?",
                "options": [
                    {"id": "opt_a", "label_ar": "نَشَاطٌ بَدَنِيٌّ مُفِيدٌ", "label_en": "Beneficial physical activity"},
                    {"id": "opt_b", "label_ar": "نَوْمٌ عَمِيقٌ", "label_en": "Deep sleep"},
                    {"id": "opt_c", "label_ar": "طَعَامٌ لَذِيذٌ", "label_en": "Delicious food"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "Sport (رِيَاضَة) refers to physical exercise and sports activities."
            },
            {
                "id": "prep_02",
                "prompt_ar": "أَيُّ الكَلِمَاتِ الآتِيَةِ تَدُلُّ عَلَى عَدَدٍ؟",
                "prompt_en": "Which of the following words indicates a number?",
                "options": [
                    {"id": "opt_a", "label_ar": "مَلْعَب", "label_en": "Stadium / Pitch"},
                    {"id": "opt_b", "label_ar": "أَرْبَعَة", "label_en": "Four (4)"},
                    {"id": "opt_c", "label_ar": "كُرَة", "label_en": "Ball"}
                ],
                "correct_answer": "opt_b",
                "explanation_en": "أَرْبَعَة means four (4)."
            },
            {
                "id": "prep_03",
                "prompt_ar": "مَا ضِدُّ كَلِمَة (كَبِيرَة)؟",
                "prompt_en": "What is the opposite of the word (Large / Big)?",
                "options": [
                    {"id": "opt_a", "label_ar": "صَغِيرَة", "label_en": "Small"},
                    {"id": "opt_b", "label_ar": "ثَقِيلَة", "label_en": "Heavy"},
                    {"id": "opt_c", "label_ar": "جَمِيلَة", "label_en": "Beautiful"}
                ],
                "correct_answer": "opt_a",
                "explanation_en": "صَغِيرَة (small) is the direct opposite of كَبِيرَة (big/large)."
            }
        ]
    },

    # 2. Three Learning Paths
    "learning_paths": {
        "foundation": {
            "title_ar": "المسار التأسيسي",
            "title_en": "Foundation Path",
            "pacing": "Supported step-by-step with bilingual glosses, visual icons, and audio cues.",
            "target": "Master core 8 glossary items and identify team vs individual games."
        },
        "guided": {
            "title_ar": "المسار الموجه",
            "title_en": "Guided Path",
            "pacing": "Structured exercises with sentence framing and grammar checks.",
            "target": "Construct sentences describing football pitch dimensions and rules."
        },
        "independent": {
            "title_ar": "المسار المستقل",
            "title_en": "Independent Path",
            "pacing": "Full immersion with authentic Arabic reading and original paragraph writing.",
            "target": "Analyse game strategies and write a coherent sports report."
        }
    },

    # 3. Instruction Decoder
    "instruction_decoder": [
        {
            "verb_ar": "أَسْتَمِعُ",
            "transliteration": "Astami'u",
            "meaning_en": "I listen",
            "action_guidance": "Put on your headphones or turn up volume. Listen to the Arabic recording carefully.",
            "sample_sentence_ar": "أَسْتَمِعُ إِلَى النَّصِّ بِانْتِبَاهٍ.",
            "sample_sentence_en": "I listen to the text attentively."
        },
        {
            "verb_ar": "أَقْرَأُ",
            "transliteration": "Aqra'u",
            "meaning_en": "I read",
            "action_guidance": "Read the text silently first, then aloud with proper vowels (tashkeel).",
            "sample_sentence_ar": "أَقْرَأُ نَصَّ (السَّاحِرَةِ المُسْتَدِيرَةِ).",
            "sample_sentence_en": "I read the text of 'The Round Magician'."
        },
        {
            "verb_ar": "أَتَحَدَّثُ",
            "transliteration": "Atahaddathu",
            "meaning_en": "I speak / discuss",
            "action_guidance": "Practise speaking in Arabic with your peer or record your voice.",
            "sample_sentence_ar": "أَتَحَدَّثُ عَنْ رِيَاضَتِي المُفَضَّلَةِ.",
            "sample_sentence_en": "I speak about my favorite sport."
        },
        {
            "verb_ar": "أَكْتُبُ",
            "transliteration": "Aktubu",
            "meaning_en": "I write",
            "action_guidance": "Compose sentences using the target connectors: يجب أن، كذلك، أيضاً.",
            "sample_sentence_ar": "أَكْتُبُ فِقْرَةً عَنْ قَوَانِينِ اللُّعْبَةِ.",
            "sample_sentence_en": "I write a paragraph about the game rules."
        },
        {
            "verb_ar": "أُصَنِّفُ",
            "transliteration": "Usannifu",
            "meaning_en": "I classify / categorize",
            "action_guidance": "Sort items into groups: team vs individual, heavy vs light.",
            "sample_sentence_ar": "أُصَنِّفُ الكُرَاتِ إِلَى كَبِيرَةٍ وَصَغِيرَةٍ.",
            "sample_sentence_en": "I classify balls into large and small."
        },
        {
            "verb_ar": "أَبْحَثُ عَنِ الخَطَأِ",
            "transliteration": "Ab-hathu 'ani al-khata'",
            "meaning_en": "I spot the mistake",
            "action_guidance": "Read the statement carefully, identify the factually incorrect word and correct it.",
            "sample_sentence_ar": "أَبْحَثُ عَنِ الخَطَأِ فِي الجُمَلِ الآتِيَةِ.",
            "sample_sentence_en": "I find the error in the following sentences."
        }
    ],

    # Vocabulary & Glossary Cards (from printed pages 7-10)
    "vocabulary_cards": [
        {
            "id": "vocab_01",
            "word_ar": "الكُرَةُ",
            "vowelled_ar": "الكُرَةُ",
            "meaning_en": "The ball",
            "definition_ar": "كُلُّ جِسْمٍ مُسْتَدِيرٍ.",
            "example_ar": "هُنَاكَ أَنْوَاعٌ مُخْتَلِفَةٌ لِلْكُرَةِ فِي الْمَتْجَرِ.",
            "example_en": "There are different types of balls in the store.",
            "root": "ك-ر-ر",
            "category": "sports"
        },
        {
            "id": "vocab_02",
            "word_ar": "الحَجْمُ",
            "vowelled_ar": "الحَجْمُ",
            "meaning_en": "The size / volume",
            "definition_ar": "المِقْدَارُ.",
            "example_ar": "الكِتَابُ صَغِيرُ الحَجْمِ.",
            "example_en": "The book is small in size.",
            "root": "ح-ج-م",
            "category": "measurement"
        },
        {
            "id": "vocab_03",
            "word_ar": "النَّوْعُ",
            "vowelled_ar": "النَّوْعُ",
            "meaning_en": "The kind / type",
            "definition_ar": "الصِّنْفُ.",
            "example_ar": "الكُرَاتُ أَنْوَاعٌ كَكُرَةِ اليَدِ، وَكُرَةِ القَدَمِ.",
            "example_en": "Balls have types such as handball and football.",
            "root": "ن-و-ع",
            "category": "classification"
        },
        {
            "id": "vocab_04",
            "word_ar": "مُسْتَدِيرٌ",
            "vowelled_ar": "مُسْتَدِيرٌ",
            "meaning_en": "Round / circular",
            "definition_ar": "عَلَى هَيْئَةِ دَائِرَةٍ.",
            "example_ar": "الكُرَةُ مُسْتَدِيرَةُ الشَّكْلِ.",
            "example_en": "The ball is round in shape.",
            "root": "د-و-ر",
            "category": "shapes"
        },
        {
            "id": "vocab_05",
            "word_ar": "جَمَاعِيٌّ",
            "vowelled_ar": "جَمَاعِيٌّ",
            "meaning_en": "Team / collective",
            "definition_ar": "يَشْتَرِكُ فِيهِ أَكْثَرُ مِنْ شَخْصٍ.",
            "example_ar": "كُرَةُ الطَّائِرَةِ لُعْبَةٌ جَمَاعِيَّةٌ.",
            "example_en": "Volleyball is a team game.",
            "root": "ج-م-ع",
            "category": "sports_type"
        },
        {
            "id": "vocab_06",
            "word_ar": "فَرْدِيٌّ",
            "vowelled_ar": "فَرْدِيٌّ",
            "meaning_en": "Individual / solo",
            "definition_ar": "يَقُومُ بِهِ فَرْدٌ وَاحِدٌ.",
            "example_ar": "الرَّسْمُ نَشَاطٌ فَرْدِيٌّ.",
            "example_en": "Drawing is an individual activity.",
            "root": "ف-ر-د",
            "category": "sports_type"
        },
        {
            "id": "vocab_07",
            "word_ar": "البَيْضَوِيُّ",
            "vowelled_ar": "البَيْضَوِيُّ",
            "meaning_en": "Oval / egg-shaped",
            "definition_ar": "أَحَدُ الأَشْكَالِ الَّذِي يُشْبِهُ البَيْضَةَ.",
            "example_ar": "كُرَةُ الرَّجْبِي بَيْضَاوِيَّةٌ.",
            "example_en": "A rugby ball is oval.",
            "root": "ب-ي-ض",
            "category": "shapes"
        },
        {
            "id": "vocab_08",
            "word_ar": "المُبَارَاةُ",
            "vowelled_ar": "المُبَارَاةُ",
            "meaning_en": "The match / game",
            "definition_ar": "مُنَافَسَةٌ بَيْنَ فَرْدَيْنِ أَوْ مَجْمُوعَتَيْنِ.",
            "example_ar": "سَتَكُونُ المُبَارَاةُ فِي كَأْسِ العَالَمِ بَيْنَ البَرَازِيلِ وَالأَرْجَنْتِينِ.",
            "example_en": "The match in the World Cup will be between Brazil and Argentina.",
            "root": "ب-ر-ي",
            "category": "sports"
        }
    ],

    # 4. Grammar & Patterns
    "grammar_lab": {
        "title_ar": "قواعد التراكيب والضمائر وتطابق الصفة",
        "title_en": "Grammar, Patterns & Adjective Agreement",
        "sections": [
            {
                "rule_name_ar": "تطابق الصفة والموصوف في التذكير والتأنيث",
                "rule_name_en": "Adjective-Noun Agreement (Gender)",
                "explanation_en": "In Arabic, the adjective follows the noun and agrees with it in gender (masculine/feminine).",
                "examples": [
                    {
                        "phrase_ar": "مَلْعَبٌ مُسْتَطِيلٌ",
                        "translation_en": "A rectangular pitch (both masculine)",
                        "gender": "masculine"
                    },
                    {
                        "phrase_ar": "كُرَةٌ مُسْتَدِيرَةٌ",
                        "translation_en": "A round ball (both feminine with Taa Marbuta ة)",
                        "gender": "feminine"
                    },
                    {
                        "phrase_ar": "لُعْبَةٌ جَمَاعِيَّةٌ",
                        "translation_en": "A team game (both feminine)",
                        "gender": "feminine"
                    }
                ]
            },
            {
                "rule_name_ar": "ضمائر الملكية المتصلة (ـي، ـهُ، ـهَا)",
                "rule_name_en": "Attached Possessive Pronouns (-i, -hu, -ha)",
                "explanation_en": "Suffixes added to nouns denote possession: -i (my), -hu (his), -ha (her).",
                "examples": [
                    {
                        "phrase_ar": "رِيَاضَتِي (رياضتي)",
                        "translation_en": "My sport",
                        "person": "first_person"
                    },
                    {
                        "phrase_ar": "رِيَاضَتُهُ (رياضته)",
                        "translation_en": "His sport",
                        "person": "third_person_masculine"
                    },
                    {
                        "phrase_ar": "رِيَاضَتُهَا (رياضتها)",
                        "translation_en": "Her sport",
                        "person": "third_person_feminine"
                    },
                    {
                        "phrase_ar": "لُعْبَتِي - لُعْبَتُهُ - لُعْبَتُهَا",
                        "translation_en": "My game - His game - Her game",
                        "person": "all"
                    }
                ]
            }
        ]
    },

    # 5. Sentence Builder
    "sentence_builder": {
        "title_ar": "باني الجمل التفاعلي",
        "title_en": "Interactive Sentence Builder",
        "challenges": [
            {
                "id": "sb_01",
                "target_en": "Football is the primary popular game in the world.",
                "target_ar": "كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الشَّعْبِيَّةُ الأُولَى فِي العَالَمِ",
                "tiles": ["كُرَةُ", "القَدَمِ", "هِيَ", "اللُّعْبَةُ", "الشَّعْبِيَّةُ", "الأُولَى", "فِي", "العَالَمِ"],
                "distractors": ["السَّلَّةِ", "صَغِيرَةٌ"]
            },
            {
                "id": "sb_02",
                "target_en": "A match consists of two halves.",
                "target_ar": "المُبَارَاةُ تَتَكَوَّنُ مِنْ شَوْطَيْنِ",
                "tiles": ["المُبَارَاةُ", "تَتَكَوَّنُ", "مِنْ", "شَوْطَيْنِ"],
                "distractors": ["ثَلاثَةِ", "أَيَّامٍ"]
            },
            {
                "id": "sb_03",
                "target_en": "A rugby ball is oval in shape.",
                "target_ar": "كُرَةُ الرَّجْبِي بَيْضَاوِيَّةُ الشَّكْلِ",
                "tiles": ["كُرَةُ", "الرَّجْبِي", "بَيْضَاوِيَّةُ", "الشَّكْلِ"],
                "distractors": ["مُسْتَدِيرَةُ", "خَفِيفٌ"]
            }
        ]
    },

    # 6. Listen & Speak Studio
    "listen_speak_studio": {
        "title_ar": "أستمع وأتحدث - الساحرة المستديرة",
        "title_en": "Listen & Speak Studio — The Round Magician",
        "passage_ar": "كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الشَّعْبِيَّةُ الأُولَى فِي العَالَمِ، وَلِأَنَّهَا سَحَرَتْ عُقُولَ أَكْثَرَ مِنْ مِلْيَارِ مُتَابِعٍ حَوْلَ العَالَمِ سُمِّيَتْ بِالسَّاحِرَةِ المُسْتَدِيرَةِ. وَهِيَ لُعْبَةٌ جَمَاعِيَّةٌ وَلَيْسَتْ فَرْدِيَّةً، تَتَكَوَّنُ المُبَارَاةُ مِنْ فَرِيقَيْنِ فِي كُلٍّ مِنْهُمَا 11 لاعِبًا، يَفُوزُ الفَرِيقُ الَّذِي يُسَجِّلُ أَهْدَافًا أَكْثَرَ.",
        "passage_en": "Football is the premier popular game in the world. Because it charmed the minds of over one billion fans worldwide, it was dubbed 'The Round Magician'. It is a team sport and not an individual one. A match consists of two teams with 11 players each; the team scoring more goals wins.",
        "audio_scripts": [
            {"id": "aud_01", "text_ar": "كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الشَّعْبِيَّةُ الأُولَى فِي العَالَمِ.", "text_en": "Football is the number one popular game in the world."},
            {"id": "aud_02", "text_ar": "سُمِّيَتْ بِالسَّاحِرَةِ المُسْتَدِيرَةِ لِأَنَّهَا سَحَرَتْ عُقُولَ المَلَايِينِ.", "text_en": "It was called 'The Round Magician' because it captivated millions of minds."},
            {"id": "aud_03", "text_ar": "تَتَكَوَّنُ المُبَارَاةُ مِنْ فَرِيقَيْنِ فِي كُلٍّ مِنْهُمَا 11 لاعِبًا.", "text_en": "A match consists of two teams with 11 players in each."},
            {"id": "aud_04", "text_ar": "يَجِبُ أَنْ يَكُونَ فِي كُلِّ مُبَارَاةٍ أَرْبَعَةُ حُكَّامٍ.", "text_en": "Every match must have four referees."}
        ]
    },

    # 7. Interactive Practice Activities (Printed pages 9, 13)
    "practice_activities": [
        {
            "id": "act_01",
            "type": "choice",
            "title_ar": "عدد متابعي كرة القدم حول العالم",
            "title_en": "Number of football followers worldwide",
            "prompt_ar": "كَمْ عَدَدُ مُتَابِعِي كُرَةِ القَدَمِ حَوْلَ العَالَمِ كَمَا وَرَدَ فِي النَّصِّ؟",
            "prompt_en": "How many football followers are there around the world according to the text?",
            "options": [
                {"id": "opt_1", "label_ar": "20 أَلْفًا", "label_en": "20 Thousand"},
                {"id": "opt_2", "label_ar": "مِلْيُون", "label_en": "One Million"},
                {"id": "opt_3", "label_ar": "أَكْثَرُ مِنْ مِلْيَار", "label_en": "More than one billion"},
                {"id": "opt_4", "label_ar": "أَلْف مُتَابِع", "label_en": "One Thousand"}
            ],
            "correct_answer": "opt_3",
            "points": 1.0
        },
        {
            "id": "act_02",
            "type": "choice",
            "title_ar": "نوع لعبة كرة القدم",
            "title_en": "Type of Football Game",
            "prompt_ar": "لُعْبَةُ كُرَةِ القَدَمِ لُعْبَةٌ:",
            "prompt_en": "Football is a game that is:",
            "options": [
                {"id": "opt_1", "label_ar": "فَرْدِيَّةٌ", "label_en": "Individual"},
                {"id": "opt_2", "label_ar": "ثُنَائِيَّةٌ", "label_en": "Pairs"},
                {"id": "opt_3", "label_ar": "جَمَاعِيَّةٌ", "label_en": "Team / Collective"}
            ],
            "correct_answer": "opt_3",
            "points": 1.0
        },
        {
            "id": "act_03",
            "type": "choice",
            "title_ar": "شكل ملعب كرة القدم",
            "title_en": "Shape of the football pitch",
            "prompt_ar": "المَلْعَبُ قِطْعَةٌ مِنَ الأَرْضِ عَلَى شَكْلِ:",
            "prompt_en": "The stadium pitch is a piece of land in the shape of a:",
            "options": [
                {"id": "opt_1", "label_ar": "دَائِرَة", "label_en": "Circle"},
                {"id": "opt_2", "label_ar": "مُرَبَّع", "label_en": "Square"},
                {"id": "opt_3", "label_ar": "مُسْتَطِيل", "label_en": "Rectangle"}
            ],
            "correct_answer": "opt_3",
            "points": 1.0
        },
        {
            "id": "act_04",
            "type": "choice",
            "title_ar": "عدد الحكام في كل مباراة",
            "title_en": "Number of referees in each match",
            "prompt_ar": "عَدَدُ الحُكَّامِ فِي كُلِّ مُبَارَاةٍ كُرَةِ قَدَمٍ هُوَ:",
            "prompt_en": "The number of referees in each football match is:",
            "options": [
                {"id": "opt_1", "label_ar": "ثَلاثَة", "label_en": "Three"},
                {"id": "opt_2", "label_ar": "أَرْبَعَة", "label_en": "Four"},
                {"id": "opt_3", "label_ar": "خَمْسَة", "label_en": "Five"}
            ],
            "correct_answer": "opt_2",
            "points": 1.0
        },
        {
            "id": "act_05",
            "type": "choice",
            "title_ar": "أبحث عن الخطأ: حجم الكرات",
            "title_en": "Spot the Error: Ball sizes",
            "prompt_ar": "مَا الخَطَأُ فِي الجُمْلَةِ: (الكُرَاتُ كَثِيرَةٌ وَمُتَنَوِّعَةٌ، وَلَهَا الحَجْمُ نَفْسُهُ)؟",
            "prompt_en": "What is the error in: 'Balls are many and varied, and have the exact same size'?",
            "options": [
                {"id": "opt_1", "label_ar": "كَلِمَة (كَثِيرَةٌ)", "label_en": "The word 'many'"},
                {"id": "opt_2", "label_ar": "عِبَارَة (لَهَا الحَجْمُ نَفْسُهُ) لِأَنَّ أَحْجَامَهَا مُخْتَلِفَةٌ", "label_en": "'have the same size' because their sizes differ"},
                {"id": "opt_3", "label_ar": "كَلِمَة (مُتَنَوِّعَةٌ)", "label_en": "The word 'varied'"}
            ],
            "correct_answer": "opt_2",
            "points": 1.0
        }
    ],

    # 8. Real-Life Speaking Mission
    "speaking_mission": {
        "title_ar": "مهمة التحدث: في النادي الرياضي بدبي وأبوظبي",
        "title_en": "Speaking Mission: At the Sports Club in Dubai & Abu Dhabi",
        "scenario_en": "You are joining the after-school sports club at your school in the UAE. Introduce yourself to the sports captain, state your favorite game, and explain why you like it using Modern Standard Arabic.",
        "prompts_ar": [
            "مَرْحَبًا، أَنَا أُحِبُّ رِيَاضَةَ كُرَةِ القَدَمِ.",
            "كُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ مُفِيدَةٌ وَمُمْتِعَةٌ.",
            "أَتَدَرَّبُ مَعَ زُمَلائِي يَوْمَ السَّبْتِ فِي المَلْعَبِ."
        ],
        "prompts_en": [
            "Hello, I love the sport of football.",
            "Football is a beneficial and enjoyable team game.",
            "I train with my classmates on Saturday at the stadium."
        ],
        "recording_task_en": "Click the microphone button below, say one or all of the sentences in clear Arabic, and listen to your recording!"
    },

    # 9. Parent Companion Card
    "parent_companion": {
        "title_ar": "بطاقة المتابعة لولي الأمر",
        "title_en": "Parent Companion Card (Grade 5, Term 1, Lesson 1)",
        "summary_en": "In this chapter, your child learned sports vocabulary, the distinction between team (جماعية) and individual (فردية) sports, and how to read details from a factual sports text.",
        "dinner_table_prompts": [
            {"arabic": "مَا هِيَ رِيَاضَتُكَ المُفَضَّلَةُ؟", "english": "What is your favorite sport?", "phonetic": "Ma hiya riyadatuka al-mufaddalah?"},
            {"arabic": "هَلْ كُرَةُ السَّلَّةِ لُعْبَةٌ جَمَاعِيَّةٌ أَمْ فَرْدِيَّةٌ؟", "english": "Is basketball a team game or individual?", "phonetic": "Hal kurat as-sallati lu'batun jama'iyyatun am fardiyyah?"}
        ],
        "home_practice_checklist": [
            "Ask your child to show you the difference between 'مُسْتَدِير' (round) and 'بَيْضَوِي' (oval).",
            "Listen to them read the short 'Round Magician' passage aloud with proper vowels.",
            "Verify they have completed their practice quiz."
        ]
    },

    # 10. Evidence-Based Tutor Handover Card
    "tutor_handover": {
        "title_ar": "بطاقة المعلم الخصوصي والملاحظات التقويمية",
        "title_en": "Tutor Handover Card",
        "learner_focus": "CBSE Grade 5 Arabic non-native foundations",
        "unobserved_fields_note": "Fields with no submitted attempts are intentionally left blank.",
        "rubric_categories": [
            {"key": "tashkeel_accuracy", "name_en": "Vocalization (Tashkeel) Accuracy", "weight": "25%"},
            {"key": "vocab_recall", "name_en": "Glossary Retrieval", "weight": "25%"},
            {"key": "sentence_structure", "name_en": "Sentence Construction & Connectors", "weight": "25%"},
            {"key": "spoken_fluency", "name_en": "Oral Pronunciation & Joining", "weight": "25%"}
        ]
    },

    # 11. Exam-Style Practice (CBSE / MoE UAE Aligned)
    "exam_practice": {
        "title_ar": "الاختبار التجريبي وفق الهيكل الوزاري",
        "title_en": "Mock Assessment (UAE Ministry & CBSE Structure)",
        "total_marks": 10,
        "objective_questions": [
            {
                "id": "exam_q1",
                "prompt_ar": "كَمْ لاعِبًا فِي كُلِّ فَرِيقٍ فِي كُرَةِ القَدَمِ؟",
                "prompt_en": "How many players are in each team in football?",
                "options": [
                    {"id": "a", "label_ar": "9 لاعِبِينَ", "label_en": "9 players"},
                    {"id": "b", "label_ar": "11 لاعِبًا", "label_en": "11 players"},
                    {"id": "c", "label_ar": "15 لاعِبًا", "label_en": "15 players"}
                ],
                "correct_answer": "b",
                "marks": 2
            },
            {
                "id": "exam_q2",
                "prompt_ar": "مُدَّةُ كُلِّ شَوْطٍ فِي مُبَارَاةِ كُرَةِ القَدَمِ هِيَ:",
                "prompt_en": "The duration of each half in a football match is:",
                "options": [
                    {"id": "a", "label_ar": "30 دَقِيقَةً", "label_en": "30 minutes"},
                    {"id": "b", "label_ar": "45 دَقِيقَةً", "label_en": "45 minutes"},
                    {"id": "c", "label_ar": "60 دَقِيقَةً", "label_en": "60 minutes"}
                ],
                "correct_answer": "b",
                "marks": 2
            },
            {
                "id": "exam_q3",
                "prompt_ar": "أَيُّ هَذِهِ الكُرَاتِ شَكْلُهَا بَيْضَوِيٌّ؟",
                "prompt_en": "Which of these balls has an oval shape?",
                "options": [
                    {"id": "a", "label_ar": "كُرَةُ القَدَمِ", "label_en": "Football"},
                    {"id": "b", "label_ar": "كُرَةُ التِّنِسِ", "label_en": "Tennis ball"},
                    {"id": "c", "label_ar": "كُرَةُ الرَّجْبِي", "label_en": "Rugby ball"}
                ],
                "correct_answer": "c",
                "marks": 2
            }
        ],
        "writing_task": {
            "id": "exam_writing_1",
            "prompt_ar": "اُكْتُبْ ثَلاثَ جُمَلٍ عَنْ رِيَاضَتِكَ المُفَضَّلَةِ مُسْتَعِينًا بِـ (يَجِبُ أَنْ - كَذَلِكَ - أَيْضًا).",
            "prompt_en": "Write three coherent sentences about your favorite sport using connectors: (يجب أن - كذلك - أيضاً).",
            "marks": 4
        }
    },

    # 12. Spaced Recall & Concept Links
    "spaced_recall": {
        "title_ar": "التذكر المتباعد والربط المفاهيمي",
        "title_en": "Spaced Recall & Cross-Lesson Connections",
        "linked_concepts": [
            {
                "concept_name_ar": "أَنْوَاعُ الرِّيَاضَاتِ",
                "concept_name_en": "Sport Types",
                "source_lesson": "Ball Games (ألعاب الكرة)",
                "target_lesson": "Running (الجري) & Horse Riding (ركوب الخيل)",
                "recall_question_ar": "هَلْ رُكُوبُ الخَيْلِ رِيَاضَةٌ فَرْدِيَّةٌ أَمْ جَمَاعِيَّةٌ؟",
                "recall_question_en": "Is horse riding an individual or team sport?"
            },
            {
                "concept_name_ar": "ضَمَائِرُ المِلْكِيَّةِ",
                "concept_name_en": "Possessive Suffixes",
                "source_lesson": "Ball Games (رياضتي، رياضته)",
                "target_lesson": "At My School (مدرستي) & At My Home (بيتي)",
                "recall_question_ar": "كَيْفَ تَقُولُ (My School) بِاسْتِخْدَامِ يَاءِ المِلْكِيَّةِ؟",
                "recall_question_en": "How do you say 'My School' using the possessive yaa? (مَدْرَسَتِي)"
            }
        ]
    }
}


def seed_database(db: Session, include_demo_data: bool = True):
    """Seed initial schools, book editions, units, lessons, and admin account."""
    
    # 1. Seed School
    school = db.query(School).filter(School.id == "sunrise_abu_dhabi").first()
    if not school:
        school = School(
            id="sunrise_abu_dhabi",
            name="Sunrise International School, Abu Dhabi",
            country="United Arab Emirates",
            curriculum_type="CBSE & UAE Ministry of Education"
        )
        db.add(school)

    # 2. Seed Book Editions (Volumes 1, 2, and 3)
    editions_data = [
        ("moe_gr5_vol1_2023", "العربية تجمعنا - المستوى الخامس - كتاب الطالب - المجلد الأول", 1, "1693219092.pdf", 108),
        ("moe_gr5_vol2_2023", "العربية تجمعنا - المستوى الخامس - كتاب الطالب - المجلد الثاني", 2, "1693219150.pdf", 112),
        ("moe_gr5_vol3_2023", "العربية تجمعنا - المستوى الخامس - كتاب الطالب - المجلد الثالث", 3, "1693219200.pdf", 110),
    ]
    for ed_id, ed_title, ed_vol, ed_pdf, ed_pages in editions_data:
        edition = db.query(BookEdition).filter(BookEdition.id == ed_id).first()
        if not edition:
            edition = BookEdition(
                id=ed_id,
                title=ed_title,
                series_name="العربية تجمعنا",
                volume=ed_vol,
                academic_year="2023–2024",
                publication_year="2023–2024",
                pdf_filename=ed_pdf,
                total_pages=ed_pages
            )
            db.add(edition)

    # 3. Seed Units for all 3 Volumes
    units_data = [
        ("unit_01_sports", "moe_gr5_vol1_2023", 1, "الرياضات والهوايات", "Sports and Hobbies"),
        ("unit_02_rights", "moe_gr5_vol1_2023", 2, "حقوقي وواجباتي", "My Rights and Responsibilities"),
        ("unit_03_global_cities", "moe_gr5_vol2_2023", 3, "مدن عالمية", "Global Cities"),
        ("unit_04_wonders", "moe_gr5_vol2_2023", 4, "غرائب وعجائب", "Wonders and Curiosities"),
        ("unit_05_communication", "moe_gr5_vol3_2023", 5, "التواصل", "Communication"),
        ("unit_06_intelligence", "moe_gr5_vol3_2023", 6, "كلنا أذكياء", "We Are All Intelligent"),
    ]
    for u_id, ed_id, u_num, ar_title, en_title in units_data:
        unit = db.query(Unit).filter(Unit.id == u_id).first()
        if not unit:
            unit = Unit(
                id=u_id,
                book_edition_id=ed_id,
                unit_number=u_num,
                title_ar=ar_title,
                title_en=en_title
            )
            db.add(unit)

    db.commit()

    # 4. Seed Lessons for Class 5 across all 3 Terms (Lessons 1 through 22)
    lessons_catalog = [
        # Term 1 — Unit 1: الرياضات والهوايات
        ("lesson_01_ball_games", "unit_01_sports", 5, 1, 1, "ألعاب الكرة", "Ball Games", 6, True, "published"),
        ("lesson_02_horse_riding", "unit_01_sports", 5, 1, 2, "ركوب الخيل", "Horse Riding", 16, False, "published"),
        ("lesson_03_running", "unit_01_sports", 5, 1, 3, "الجري", "Running", 26, False, "published"),
        ("lesson_04_arts", "unit_01_sports", 5, 1, 4, "الفنون", "Arts", 36, False, "published"),
        ("lesson_05_reading", "unit_01_sports", 5, 1, 5, "القراءة", "Reading", 46, False, "published"),
        # Term 1 — Unit 2: حقوقي وواجباتي
        ("lesson_06_at_school", "unit_02_rights", 5, 1, 6, "في مدرستي", "At My School", 56, False, "published"),
        ("lesson_07_at_home", "unit_02_rights", 5, 1, 7, "في بيتي", "At My Home", 66, False, "published"),
        ("lesson_08_my_food", "unit_02_rights", 5, 1, 8, "طعامي", "My Food", 76, False, "published"),
        ("lesson_09_my_clothes", "unit_02_rights", 5, 1, 9, "ملابسي", "My Clothes", 86, False, "published"),
        ("lesson_10_fun_time", "unit_02_rights", 5, 1, 10, "وقت المرح", "Fun Time", 96, False, "published"),
        # Term 2 — Unit 3: مدن عالمية
        ("lesson_11_arab_cities", "unit_03_global_cities", 5, 2, 11, "مدن عربية", "Arab Cities", 6, False, "published"),
        ("lesson_12_london", "unit_03_global_cities", 5, 2, 12, "لندن", "London", 16, False, "published"),
        ("lesson_13_shanghai", "unit_03_global_cities", 5, 2, 13, "شنغهاي", "Shanghai", 26, False, "published"),
        # Term 2 — Unit 4: غرائب وعجائب
        ("lesson_14_seven_wonders", "unit_04_wonders", 5, 2, 14, "عجائب الدنيا السبع", "Seven Wonders of the World", 36, False, "published"),
        ("lesson_15_caves_and_islands", "unit_04_wonders", 5, 2, 15, "الكهوف والجزر العجيبة", "Wondrous Caves and Islands", 46, False, "published"),
        ("lesson_16_living_creatures", "unit_04_wonders", 5, 2, 16, "عجائب الكائنات الحية", "Wonders of Living Creatures", 56, False, "published"),
        # Term 3 — Unit 5: التواصل
        ("lesson_17_carrier_pigeons", "unit_05_communication", 5, 3, 17, "الحمام الزاجل", "Carrier Pigeons", 6, False, "published"),
        ("lesson_18_the_media", "unit_05_communication", 5, 3, 18, "الإعلام المرئي والمسموع", "Visual and Audio Media", 16, False, "published"),
        ("lesson_19_social_media", "unit_05_communication", 5, 3, 19, "وسائل التواصل الحديثة", "Modern Social Media", 26, False, "published"),
        # Term 3 — Unit 6: كلنا أذكياء
        ("lesson_20_animal_intelligence", "unit_06_intelligence", 5, 3, 20, "الحيوان والذكاء", "Animals and Intelligence", 36, False, "published"),
        ("lesson_21_human_intelligence", "unit_06_intelligence", 5, 3, 21, "الإنسان والذكاء", "Human and Intelligence", 46, False, "published"),
        ("lesson_22_smart_cities", "unit_06_intelligence", 5, 3, 22, "مدن ذكية: مدينة مصدر", "Smart Cities: Masdar City", 56, False, "published"),
    ]

    for l_id, u_id, grade, term, order, ar, en, page, is_demo, st in lessons_catalog:
        existing = db.query(Lesson).filter(Lesson.id == l_id).first()
        if not existing:
            lesson = Lesson(
                id=l_id,
                unit_id=u_id,
                grade=grade,
                term=term,
                lesson_order=order,
                title_ar=ar,
                title_en=en,
                start_page=page,
                is_first_chapter_demo=is_demo,
                status=st
            )
            db.add(lesson)
        else:
            existing.unit_id = u_id
            existing.grade = grade
            existing.term = term
            existing.lesson_order = order
            existing.status = st
            existing.title_ar = ar
            existing.title_en = en
            existing.start_page = page
            existing.is_first_chapter_demo = is_demo

    db.commit()

    # 5. Seed Lesson Versions (v0.2.0) for Ball Games and Lessons 2 through 22
    all_lesson_packages = [("lesson_01_ball_games", BALL_GAMES_CONTENT_V02)]
    for lesson_id, pkg in FULL_CURRICULUM_CATALOG.items():
        all_lesson_packages.append((lesson_id, pkg))

    for lesson_id, pkg in all_lesson_packages:
        ver_id = f"ver_{lesson_id}_020"
        pkg_str = json.dumps(pkg, ensure_ascii=False)
        pkg_hash = hashlib.sha256(pkg_str.encode("utf-8")).hexdigest()
        existing_ver = db.query(LessonVersion).filter(LessonVersion.id == ver_id).first()
        if not existing_ver:
            ver = LessonVersion(
                id=ver_id,
                lesson_id=lesson_id,
                version_tag="0.2.0",
                content_json=pkg_str,
                content_hash=pkg_hash,
                is_active=True,
                status="published"
            )
            db.add(ver)
        else:
            existing_ver.content_json = pkg_str
            existing_ver.content_hash = pkg_hash
            existing_ver.is_active = True
            existing_ver.status = "published"
    db.commit()

    # 6. Seed Demo Parent & Learner Account
    if not include_demo_data:
        return
    demo_parent = db.query(User).filter(User.email == "parent@fahim.ae").first()
    if not demo_parent:
        demo_parent = User(
            email="parent@fahim.ae",
            password_hash=hash_password("FahimPass2026!"),
            full_name="Fatima Al-Nuaimi",
            phone_number="+971501234567",
            role="parent",
            is_verified=True
        )
        db.add(demo_parent)
        db.commit()
    else:
        if not demo_parent.phone_number:
            demo_parent.phone_number = "+971501234567"
            db.commit()

    # Seed child profile 1 (Zayed Al-Nuaimi)
    child1 = db.query(ChildProfile).filter(ChildProfile.parent_id == demo_parent.id, ChildProfile.name == "Zayed Al-Nuaimi").first()
    if not child1:
        child1 = ChildProfile(
            parent_id=demo_parent.id,
            name="Zayed Al-Nuaimi",
            gender="Boy",
            age=10,
            school_name="Sunrise International School, Abu Dhabi",
            default_grade=5,
            avatar_id="avatar_falcon",
            curriculum_stream="MoE / CBSE Arabic (Non-Arabs)",
            access_pin="1234",
            diagnostic_completed=False,
            diagnostic_level="intermediate"
        )
        db.add(child1)
        db.commit()

        # Term 1 access initially FALSE (so Chapter 1 Ball Games runs as Free Demo, and unlocking full term requires $33)
        access = TermAccess(
            child_id=child1.id,
            grade=5,
            term=1,
            is_unlocked=False
        )
        db.add(access)
        db.commit()
    else:
        if not getattr(child1, "access_pin", None):
            child1.access_pin = "1234"
        if not getattr(child1, "avatar_id", None):
            child1.avatar_id = "avatar_falcon"
        if not getattr(child1, "curriculum_stream", None):
            child1.curriculum_stream = "MoE / CBSE Arabic (Non-Arabs)"
        db.commit()

    # Seed child profile 2 (Maryam Al-Nuaimi)
    child2 = db.query(ChildProfile).filter(ChildProfile.parent_id == demo_parent.id, ChildProfile.name == "Maryam Al-Nuaimi").first()
    if not child2:
        child2 = ChildProfile(
            parent_id=demo_parent.id,
            name="Maryam Al-Nuaimi",
            gender="Girl",
            age=8,
            school_name="Sunrise International School, Abu Dhabi",
            default_grade=3,
            avatar_id="avatar_gazelle",
            curriculum_stream="MoE / CBSE Arabic (Non-Arabs)",
            access_pin="5678",
            diagnostic_completed=True,
            diagnostic_level="beginner"
        )
        db.add(child2)
        db.commit()

        access2 = TermAccess(
            child_id=child2.id,
            grade=3,
            term=1,
            is_unlocked=False
        )
        db.add(access2)
        db.commit()
    else:
        if not getattr(child2, "access_pin", None):
            child2.access_pin = "5678"
        if not getattr(child2, "avatar_id", None):
            child2.avatar_id = "avatar_gazelle"
        if not getattr(child2, "curriculum_stream", None):
            child2.curriculum_stream = "MoE / CBSE Arabic (Non-Arabs)"
        db.commit()

    # 7. Seed Demo Tutor Account
    demo_tutor = db.query(User).filter(User.email == "tutor@fahim.ae").first()
    if not demo_tutor:
        demo_tutor = User(
            email="tutor@fahim.ae",
            password_hash=hash_password("TutorPass2026!"),
            full_name="Ustadh Ahmad Al-Hashemi",
            role="tutor",
            is_verified=True
        )
        db.add(demo_tutor)
        db.commit()

    # 8. Seed Admin Account (Sole Administrator)
    demo_admin = db.query(User).filter(User.email == "alex@exlsolutions.ae").first()
    if not demo_admin:
        demo_admin = User(
            email="alex@exlsolutions.ae",
            password_hash=hash_password("exlsolutions@2026"),
            full_name="Alex (EXL Administrator)",
            role="admin",
            is_verified=True
        )
        db.add(demo_admin)
        db.commit()

    # 9. Seed Gamification Profiles & Badges
    if child1:
        g_profile = db.query(GamificationProfile).filter(GamificationProfile.child_id == child1.id).first()
        if not g_profile:
            g_profile = GamificationProfile(
                child_id=child1.id,
                total_xp=450,
                level=2,
                heritage_rank_ar="فارس الكلمات",
                heritage_rank_en="Knight of Words",
                current_streak_days=4,
                longest_streak_days=7,
                weekly_study_minutes=135,
                capsules_completed_count=3,
                quizzes_completed_count=4,
                avg_quiz_score=86.5
            )
            db.add(g_profile)
            db.commit()
        else:
            g_profile.total_xp = max(g_profile.total_xp, 450)
            g_profile.current_streak_days = max(g_profile.current_streak_days, 4)
            db.commit()

        # Seed Badges for child1
        badges_data = [
            ("streak_champion", "بطل الاستمرارية", "Streak Champion", "حافظ على مذاكرة اللغة العربية 4 أيام متتالية", "Maintained an active 4-day Arabic study streak", "⚡", "streak", True),
            ("falcon_eye", "عين الصقر", "Falcon Eye", "أحرز درجة كاملة 100% في التقييم المبدئي", "Scored 100% on the baseline diagnostic assessment", "🦅", "mastery", True),
            ("capsule_master", "خبير الكبسولات", "Capsule Master", "أتم بنجاح 3 كبسولات لغوية سريعة", "Successfully completed 3 microlearning grammar capsules", "💊", "capsule", True),
            ("mistake_conqueror", "قاهر الأخطاء", "Mistake Conqueror", "صحح 3 أخطاء في دفتر المراجعة الذاتي", "Resolved 3 linguistic items in the Mistake Notebook", "🔍", "recovery", False),
            ("grammar_guru", "فارس النحو", "Grammar Guru", "أتقن مهارة إعراب المبتدأ والخبر بنسبة تفوق 85%", "Mastered nominal sentence syntax with 85%+ accuracy", "🏆", "grammar", False),
            ("reading_pro", "القارئ الماهر", "Fluent Reader", "أكمل قراءة نص ألعاب الكرة وفهم مفرداته", "Completed reading fluency for Ball Games text", "📖", "reading", True)
        ]
        for b_key, t_ar, t_en, d_ar, d_en, icon, cat, unlocked in badges_data:
            badge = db.query(LearnerBadge).filter(LearnerBadge.child_id == child1.id, LearnerBadge.badge_key == b_key).first()
            if not badge:
                badge = LearnerBadge(
                    child_id=child1.id,
                    badge_key=b_key,
                    title_ar=t_ar,
                    title_en=t_en,
                    description_ar=d_ar,
                    description_en=d_en,
                    icon=icon,
                    category=cat,
                    is_unlocked=unlocked
                )
                db.add(badge)
        db.commit()

        # 10. Seed Concept Mastery Records for child1 (Zayed)
        concept_data = [
            ("vocab_sports", "المفردات والدلالة الرياضية", "Sports Glossary & Vocabulary", "vocabulary", 92.0, 12, 11, False, 0),
            ("reading_fluency", "الطلاقة وفهم المقروء", "Reading Fluency & Comprehension", "reading", 78.0, 10, 8, False, 1),
            ("syntax_nominal", "الجملة الاسمية (المبتدأ والخبر)", "Nominal Sentence (Mubtada & Khabar)", "grammar", 85.0, 8, 7, False, 0),
            ("conjugation_past", "تصريف الأفعال والضمائر", "Verb Conjugation & Tenses", "grammar", 64.0, 10, 6, True, 3), # Knowledge Gap!
            ("ortho_taa_marbutah", "التاء المربوطة والهاء", "Taa Marbutah vs. Haa", "orthography", 68.0, 9, 6, True, 2), # Knowledge Gap!
            ("plurals_sound", "جمع المذكر والمؤنث السالم", "Sound Plurals (Masculine & Feminine)", "grammar", 88.0, 8, 7, False, 0),
            ("prepositions_jar", "حروف الجر والتراكيب", "Prepositions & Genitive Case", "grammar", 90.0, 10, 9, False, 0),
            ("oral_pronunciation", "النطق السليم ومخارج الحروف", "Oral Articulation & Phonics", "speaking", 75.0, 6, 5, False, 1)
        ]
        for c_key, n_ar, n_en, cat, pct, attempts, correct, is_gap, mistakes in concept_data:
            cm = db.query(ConceptMastery).filter(ConceptMastery.child_id == child1.id, ConceptMastery.concept_key == c_key).first()
            if not cm:
                cm = ConceptMastery(
                    child_id=child1.id,
                    concept_key=c_key,
                    concept_name_ar=n_ar,
                    concept_name_en=n_en,
                    category=cat,
                    mastery_percentage=pct,
                    total_attempts=attempts,
                    correct_attempts=correct,
                    is_gap=is_gap,
                    persistent_mistake_count=mistakes
                )
                db.add(cm)
        db.commit()

    # 11. Seed Cohort Peer Learners for Grade 5 Leaderboard
    cohort_parent = db.query(User).filter(User.email == "cohort.parents@sunrise.ae").first()
    if not cohort_parent:
        cohort_parent = User(
            email="cohort.parents@sunrise.ae",
            password_hash=hash_password("CohortPass2026!"),
            full_name="Sunrise Parent Cohort",
            role="parent",
            is_verified=True
        )
        db.add(cohort_parent)
        db.commit()

    cohort_peers = [
        ("Tariq Al-Hashimi", "Boy", 10, "avatar_falcon", 580, 6),
        ("Fatima Al-Zahra", "Girl", 10, "avatar_gazelle", 510, 5),
        ("Rohan Sharma", "Boy", 11, "avatar_camel", 390, 3),
        ("Ryan Al-Falasi", "Boy", 10, "avatar_oryx", 340, 4),
        ("Aarav Patel", "Boy", 10, "avatar_palm", 290, 2),
        ("Layla Mansoor", "Girl", 10, "avatar_gazelle", 210, 1)
    ]
    for p_name, p_gender, p_age, p_avatar, p_xp, p_streak in cohort_peers:
        peer = db.query(ChildProfile).filter(ChildProfile.name == p_name).first()
        if not peer:
            peer = ChildProfile(
                parent_id=cohort_parent.id,
                name=p_name,
                gender=p_gender,
                age=p_age,
                school_name="Sunrise International School, Abu Dhabi",
                default_grade=5,
                avatar_id=p_avatar,
                curriculum_stream="MoE / CBSE Arabic (Non-Arabs)",
                access_pin="8888",
                diagnostic_completed=True
            )
            db.add(peer)
            db.commit()
        else:
            peer.parent_id = cohort_parent.id
            db.commit()


        peer_g = db.query(GamificationProfile).filter(GamificationProfile.child_id == peer.id).first()
        if not peer_g:
            peer_g = GamificationProfile(
                child_id=peer.id,
                total_xp=p_xp,
                level=2 if p_xp >= 400 else 1,
                heritage_rank_ar="فارس الكلمات" if p_xp >= 400 else "مستكشف الصحراء",
                heritage_rank_en="Knight of Words" if p_xp >= 400 else "Desert Explorer",
                current_streak_days=p_streak,
                longest_streak_days=p_streak + 2,
                weekly_study_minutes=p_xp // 3,
                capsules_completed_count=p_xp // 100,
                quizzes_completed_count=p_xp // 120,
                avg_quiz_score=82.0 + (p_xp % 10)
            )
            db.add(peer_g)
    db.commit()

    # 12. Seed School-Sponsored Voucher Codes
    vouchers = [
        ("SUNRISE2026", "sunrise_abu_dhabi", "annual", 100.0, 500, "Sunrise International School - Annual Sponsored Arabic Pass"),
        ("ADEK-ARABIC-100", None, "annual", 100.0, 1000, "ADEK Abu Dhabi - Full Academic Year Arabic Sponsorship"),
        ("DUBAI-TERM1", None, "term", 100.0, 250, "Dubai Schools Arabic Literacy Initiative - Term 1 Pass"),
        ("SCHOOLDISCOUNT50", None, "annual", 50.0, 300, "School Partner 50% Tuition Discount Code")
    ]
    for code, sch_id, pkg_type, disc, max_red, notes in vouchers:
        v = db.query(VoucherCode).filter(VoucherCode.code == code).first()
        if not v:
            v = VoucherCode(
                code=code,
                school_id=sch_id,
                package_type=pkg_type,
                discount_pct=disc,
                max_redemptions=max_red,
                redeemed_count=0,
                is_active=True,
                notes=notes
            )
            db.add(v)
    db.commit()
