"""
Microlearning Units (كبسولات تعليمية) — Capsules Bank
Bite-sized 3–5 minute hyper-focused lessons breaking down critical Arabic rules
for UAE MoE & CBSE non-native learners.
"""

from typing import List, Dict, Any

CAPSULES_DATA: List[Dict[str, Any]] = [
    {
        "id": "capsule_01_taa_marbutah",
        "grade": 5,
        "title_ar": "التاء المربوطة (ـة/ة) والهاء (ـه/ه)",
        "title_en": "Taa Marbutah vs. Haa: The Golden Pause Test",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Orthography & Spelling (الإملاء)",
        "summary_ar": "كيف تفرق بين التاء المربوطة والهاء بسهولة دون أن تخطئ؟",
        "summary_en": "How to effortlessly distinguish between Taa Marbutah and Haa without making mistakes?",
        "audio_script_ar": "مرحباً يا بطل! هل تحتار أحياناً بين كتابة التاء المربوطة والهاء في نهاية الكلمة؟ إليك القاعدة الذهبية: ضع تنويناً أو حركة على الكلمة؛ إذا نطقتها تاءً مثل (كُرَةٌ) فهي تاء مربوطة بنقطتين. أما إذا نطقتها هاءً مثل (مِيَاهٌ) فهي هاء دون نقطتين!",
        "audio_script_en": "Hello champion! Do you ever wonder whether a word ends in Taa Marbutah or Haa? Here is the golden rule: add Tanween or a short vowel. If it sounds like /t/ like (Kurah -> Kuratun), write Taa Marbutah with two dots. If it sounds like /h/ like (Miyah -> Miyahun), write Haa without dots!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "قاعدة الوقف (السكون)",
                "title_en": "1. The Pause Rule (Sukun)",
                "explanation_ar": "عند الوقف بالسكون، كلاهما يُنطق هاءً: كُرَهْ / مِيَاهْ. لذلك لا تعتمد على الوقف فقط.",
                "explanation_en": "When pausing with Sukun, both are pronounced as /h/ (Kurah / Miyah). That is why pause alone is inconclusive."
            },
            {
                "step_number": 2,
                "title_ar": "القاعدة الذهبية (التحريك أو التنوين)",
                "title_en": "2. The Golden Rule (Vowel / Tanween Test)",
                "explanation_ar": "حرّك الكلمة بالضمة أو التنوين: (كُرَةُ القدم / كُرَةٌ) ← نطقت (تاء) فتكتب تاء مربوطة (ـة/ة). (مِيَاهُ النهر / مِيَاهٌ) ← نطقت (هاء) فتكتب هاء (ـه/ه).",
                "explanation_en": "Add a vowel or Tanween: (Kurat-ul-qadam / Kuratun) sounds as /t/, so write Taa Marbutah (ـة). (Miyah-un-nahr / Miyahun) sounds as /h/, so write Haa (ـه)."
            }
        ],
        "examples": [
            {"word_ar": "مَدْرَسَة", "translation_en": "School (Taa Marbutah)", "type": "تاء مربوطة", "test_form": "مَدْرَسَتُنَا / مَدْرَسَةٌ"},
            {"word_ar": "وَجْه", "translation_en": "Face (Haa)", "type": "هاء", "test_form": "وَجْهُهُ / وَجْهٌ"},
            {"word_ar": "كُرَة", "translation_en": "Ball (Taa Marbutah)", "type": "تاء مربوطة", "test_form": "كُرَةُ القَدَمِ"},
            {"word_ar": "مِيَاه", "translation_en": "Water (Haa)", "type": "هاء", "test_form": "مِيَاهُ البَحْرِ"}
        ],
        "quiz": [
            {
                "question_ar": "أي الكلمات التالية تنتهي بتاء مربوطة (ـة) بشكل صحيح؟",
                "question_en": "Which of the following words correctly ends in a Taa Marbutah (ـة)?",
                "options": ["مِيَاه", "كُرَة", "وَجْه"],
                "options_en": ["Water (Miyah)", "Ball (Kurah)", "Face (Wajh)"],
                "correct_index": 1,
                "explanation_ar": "أحسنت! نقول (كُرَةُ السَّلَّةِ) بنطق التاء عند الوصل، فتكتب تاء مربوطة بنقطتين.",
                "explanation_en": "Well done! We say 'Kurat-us-sallah' articulating the /t/ sound in flow, requiring Taa Marbutah with two dots."
            },
            {
                "question_ar": "كيف نختبر الحرف الأخير في كلمة (مُنْتَبِه) لنعرف هل هو هاء أم تاء؟",
                "question_en": "How do we test the final letter of 'Muntabih' to know if it is Haa or Taa?",
                "options": [
                    "نحذفه من الكلمة",
                    "نضع عليه ضمة أو تنويناً وننطقه",
                    "نحوله إلى جمع مؤنث"
                ],
                "options_en": [
                    "Delete it from the word",
                    "Add a Dammah or Tanween and pronounce it",
                    "Convert it to a feminine plural"
                ],
                "correct_index": 1,
                "explanation_ar": "صحيح! التحريك بالضمة (مُنْتَبِهٌ) يظهر صوت الهاء بوضوح دون نقطتين.",
                "explanation_en": "Correct! Adding Dammah (Muntabihun) clearly reveals the /h/ phoneme without dots."
            }
        ]
    },
    {
        "id": "capsule_02_verb_subject_agreement",
        "grade": 5,
        "title_ar": "مطابقة الفعل للفاعل تذكيراً وتأنيثاً",
        "title_en": "Subject-Verb Agreement: Gender Harmony",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Grammar (النحو والتراكيب)",
        "summary_ar": "متى يبدأ الفعل بالياء ومتى يبدأ بالتاء مع الفاعل؟",
        "summary_en": "When does a verb start with Yaa and when does it start with Taa with the subject?",
        "audio_script_ar": "أهلاً بك! في لغتنا الجميلة يتناغم الفعل مع الفاعل. إذا كان الفاعل مذكراً مثل (راشد) يبدأ الفعل المضارع بالياء: (يَرْكُضُ راشد). وإذا كان الفاعل مؤنثاً مثل (فاطمة) يبدأ الفعل بالتاء: (تَرْكُضُ فاطمة).",
        "audio_script_en": "Welcome! In Arabic, the verb harmonizes with the subject's gender. If the subject is masculine like Rashid, the present tense verb begins with Yaa: (Yarkudu Rashid). If the subject is feminine like Fatima, it begins with Taa: (Tarkudu Fatima).",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "مع الفاعل المذكر",
                "title_en": "1. With Masculine Subject",
                "explanation_ar": "الفعل المضارع يبدأ بـ (ياء): يَلْعَبُ الطَّالِبُ / يُسَجِّلُ اللاعِبُ.",
                "explanation_en": "Present tense starts with Yaa (ـيـ): (Yal'abu at-talibu / Yusajjilu al-la'ibu)."
            },
            {
                "step_number": 2,
                "title_ar": "مع الفاعل المؤنث",
                "title_en": "2. With Feminine Subject",
                "explanation_ar": "الفعل المضارع يبدأ بـ (تاء): تَلْعَبُ الطَّالِبَةُ / تُسَجِّلُ اللاعِبَةُ.",
                "explanation_en": "Present tense starts with Taa (ـتـ): (Tal'abu at-talibatu / Tusajjilu al-la'ibatu)."
            }
        ],
        "examples": [
            {"sentence_ar": "يُحِبُّ زَايِدٌ رُكُوبَ الخَيْلِ.", "translation_en": "Zayed loves horse riding.", "gender": "مذكر (زايِد)"},
            {"sentence_ar": "تُحِبُّ مَرْيَمُ السِّبَاحَةَ.", "translation_en": "Maryam loves swimming.", "gender": "مؤنث (مَرْيَم)"}
        ],
        "quiz": [
            {
                "question_ar": "أكمل الفراغ: ......... اللاعِبَةُ الكُرَةَ بِمَهَارَةٍ.",
                "question_en": "Fill in the blank: ......... the female player the ball skillfully.",
                "options": ["يَرْمِي", "تَرْمِي", "يَرْمُونَ"],
                "options_en": ["Throws (Masc)", "Throws (Fem)", "They throw (Plural)"],
                "correct_index": 1,
                "explanation_ar": "ممتاز! الفاعل مؤنث (اللاعِبَةُ)، لذا يبدأ الفعل المضارع بحرف التاء (تَرْمِي).",
                "explanation_en": "Excellent! The subject is feminine (al-la'ibatu), so the present tense verb begins with Taa (tarmi)."
            }
        ]
    },
    {
        "id": "capsule_03_sound_plurals",
        "grade": 5,
        "title_ar": "جمع المذكر السالم وجمع المؤنث السالم",
        "title_en": "Sound Plurals: Regular Masculine & Feminine",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Morphology (الصرف وبنية الكلمة)",
        "summary_ar": "كيف تحول المفرد إلى جمع بإضافة (ـون/ـين) أو (ـات) دون كسر حروف الكلمة؟",
        "summary_en": "How to convert singular to plural by adding (-oon/-een) or (-aat) without altering the root letters?",
        "audio_script_ar": "هل تعلم لماذا يسمى سالماً؟ لأن حروف الكلمة الأصلية تسلم من التغيير! نضيف (ـون/ـين) لجمع المذكر مثل (مُعَلِّم ← مُعَلِّمُونَ)، ونضيف (ـات) لجمع المؤنث مثل (مُعَلِّمَة ← مُعَلِّمَات).",
        "audio_script_en": "Do you know why it is called 'Sound'? Because the singular root letters remain safe and intact! We append (-oon / -een) for masculine (Mu'allim -> Mu'allimoon) and (-aat) for feminine (Mu'allimah -> Mu'allimaat).",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "جمع المذكر السالم",
                "title_en": "1. Sound Masculine Plural",
                "explanation_ar": "مفرد مذكر عاقل + (ـونَ / ـينَ): لاعب ← لاعبونَ / لاعبينَ.",
                "explanation_en": "Singular masculine noun + (-oona / -eena): La'ib -> La'iboona / La'ibeena."
            },
            {
                "step_number": 2,
                "title_ar": "جمع المؤنث السالم",
                "title_en": "2. Sound Feminine Plural",
                "explanation_ar": "مفرد مؤنث مع حذف التاء المربوطة + (ـات): لاعبة ← لاعبات.",
                "explanation_en": "Singular feminine noun minus Taa Marbutah + (-aat): La'ibah -> La'ibaat."
            }
        ],
        "examples": [
            {"singular_ar": "مُدَرِّب", "plural_ar": "مُدَرِّبُونَ / مُدَرِّبِينَ", "translation_en": "Coach -> Coaches (Masc. Plural)", "type": "جمع مذكر سالم"},
            {"singular_ar": "مُبَارَاة", "plural_ar": "مُبَارَيَات", "translation_en": "Match -> Matches (Fem. Plural)", "type": "جمع مؤنث سالم"}
        ],
        "quiz": [
            {
                "question_ar": "ما هو جمع كلمة (مُشَجِّع) جمعاً مذكراً سالماً؟",
                "question_en": "What is the correct sound masculine plural of 'Mushajji' (supporter/fan)?",
                "options": ["مَشَاجِع", "مُشَجِّعُونَ", "مُشَجَّعَات"],
                "options_en": ["Mashaji' (broken)", "Mushajji'oon (sound masc)", "Mushajja'aat (sound fem)"],
                "correct_index": 1,
                "explanation_ar": "رائع! يجمع المذكر السالم بزيادة واو ونون على مفرده السالم: مُشَجِّعُونَ.",
                "explanation_en": "Superb! Sound masculine plural is formed by appending Waw and Noon: Mushajji'oon."
            }
        ]
    },
    {
        "id": "capsule_04_hamza_wasl_qat",
        "grade": 5,
        "title_ar": "همزة الوصل وهمزة القطع",
        "title_en": "Hamzat Al-Wasl vs. Al-Qat': The 'Waw' Test",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Orthography & Spelling (الإملاء)",
        "summary_ar": "اختبار حرف الواو السحري للتمييز بين همزة الوصل (ا) وهمزة القطع (أ/إ).",
        "summary_en": "The magic 'Waw' test to distinguish connecting Hamzah (ا) from cutting Hamzah (أ/إ).",
        "audio_script_ar": "لتكتشف نوع الهمزة في ثانية واحدة، ضع حرف الواو قبل الكلمة وانطقها. إذا سقطت الهمزة في النطق مثل (وَاستَمَعَ) فهي همزة وصل (ا). وإذا بقيت الهمزة واضحة مثل (وَأَكَلَ) فهي همزة قطع برأس العين الصغير (أ)!",
        "audio_script_en": "To identify the Hamzah type in a second, place a 'Waw' before the word. If the glottal stop vanishes like (Wastama'a), it is Hamzat Wasl (bare Alif). If the stop is clearly articulated like (Wa'akala), it is Hamzat Qat' with the Hamzah mark!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "همزة الوصل (ا)",
                "title_en": "1. Connecting Hamzah (Wasl)",
                "explanation_ar": "تُنطق في بداية الكلام وتسقط عند وصلها بما قبلها: العب ← وَالعَبْ (تكتب ألفاً دون همزة).",
                "explanation_en": "Pronounced at the beginning of speech but silent when connected: Il'ab -> Wal'ab (written as bare Alif)."
            },
            {
                "step_number": 2,
                "title_ar": "همزة القطع (أ / إ)",
                "title_en": "2. Cutting Hamzah (Qat')",
                "explanation_ar": "تُنطق دائماً في البداية والوصل: أقبل ← وَأَقْبَلَ (تكتب برأس عين أ أو إ).",
                "explanation_en": "Always pronounced in both initial and connected speech: Aqbala -> Wa'aqbala (written with Hamzah mark)."
            }
        ],
        "examples": [
            {"word_ar": "انْطَلَقَ", "translation_en": "Took off (Wasl - silent in Waw test)", "test_ar": "وَانْطَلَقَ (سقطت)", "type": "همزة وصل"},
            {"word_ar": "أَحْرَزَ", "translation_en": "Scored (Qat' - sounded in Waw test)", "test_ar": "وَأَحْرَزَ (ثبتت)", "type": "همزة قطع"}
        ],
        "quiz": [
            {
                "question_ar": "أي الكلمات الآتية تبدأ بهمزة وصل؟",
                "question_en": "Which of the following words begins with Hamzat Wasl?",
                "options": ["أَحْمَد", "اسْتَعَدَّ", "إِبْرَاهِيم"],
                "options_en": ["Ahmad (Qat')", "Ista'adda (Wasl)", "Ibrahim (Qat')"],
                "correct_index": 1,
                "explanation_ar": "إجابة صحيحة! نضع الواو فنقول (وَاسْتَعَدَّ)، سقطت الهمزة في النطق، فهي همزة وصل.",
                "explanation_en": "Correct answer! Adding Waw gives 'Wasta'adda', where the vowel drops in speech, confirming Hamzat Wasl."
            }
        ]
    },
    {
        "id": "capsule_05_nominal_verbal_sentence",
        "grade": 5,
        "title_ar": "الجملة الاسمية والجملة الفعلية",
        "title_en": "Nominal vs. Verbal Sentences in Sports Context",
        "duration_minutes": 5,
        "difficulty": "Medium",
        "topic": "Syntax & Grammar (النحو والتراكيب)",
        "summary_ar": "كيف تميز بين الجملة التي تبدأ باسم والجملة التي تبدأ بفعل وتحدد أركانها؟",
        "summary_en": "How to distinguish between sentences starting with a noun vs. verb and identify their core pillars?",
        "audio_script_ar": "الجملة في لغتنا نوعان: جملة تبدأ باسم وتسمى اسمية وتتكون من (مبتدأ + خبر) مثل: (المَلْعَبُ كَبِيرٌ). وجملة تبدأ بفعل وتسمى فعلية وتتكون من (فعل + فاعل) مثل: (فَازَ الفَرِيقُ).",
        "audio_script_en": "Sentences in Arabic are of two kinds: Nominal sentences starting with a noun (Subject + Predicate) like (Al-mal'abu kabeerun), and Verbal sentences starting with a verb (Verb + Subject) like (Faaza al-fareequ).",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "الجملة الاسمية",
                "title_en": "1. The Nominal Sentence",
                "explanation_ar": "تبدأ باسم: المبتدأ (مرفوع) + الخبر (مرفوع يكمل المعنى).",
                "explanation_en": "Starts with a noun: Mubtada' (nominative subject) + Khabar (nominative predicate completing meaning)."
            },
            {
                "step_number": 2,
                "title_ar": "الجملة الفعلية",
                "title_en": "2. The Verbal Sentence",
                "explanation_ar": "تبدأ بفعل (ماضٍ أو مضارع أو أمر) + فاعل (من قام بالفعل).",
                "explanation_en": "Starts with a verb (Past, Present, or Imperative) + Faa'il (the doer of the action)."
            }
        ],
        "examples": [
            {"sentence_ar": "الكُرَةُ جَمِيلَةٌ.", "translation_en": "The ball is beautiful. (Nominal sentence)", "type": "جملة اسمية (مبتدأ + خبر)"},
            {"sentence_ar": "سَجَّلَ اللاعِبُ هَدَفاً.", "translation_en": "The player scored a goal. (Verbal sentence)", "type": "جملة فعلية (فعل + فاعل)"}
        ],
        "quiz": [
            {
                "question_ar": "ما نوع الجملة: (الصَّفَّارَةُ أَعْلَنَتْ بِدَايَةَ المُبَارَاةِ)؟",
                "question_en": "What type of sentence is: (The whistle announced the match kickoff)?",
                "options": ["جملة فعلية", "جملة اسمية", "شبه جملة"],
                "options_en": ["Verbal sentence", "Nominal sentence", "Semi-sentence (Prepositional)"],
                "correct_index": 1,
                "explanation_ar": "أحسنت! بدأت الكلمة الأولى بـ (الـ) التعريف (الصَّفَّارَةُ)، وهي اسم، فتكون الجملة اسمية.",
                "explanation_en": "Well done! The first word begins with the definite article 'Al-' (as-saffaratu), making it a noun, hence a nominal sentence."
            }
        ]
    },
    {
        "id": "capsule_06_declarative_interrogative",
        "grade": 6,
        "title_ar": "الأسلوب الخبري والأسلوب الإنشائي الطلبي",
        "title_en": "Declarative vs. Interrogative/Creative Sentence Styles",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Rhetoric & Syntax (البلاغة والتراكيب)",
        "summary_ar": "كيف تفرق بين الكلام الذي يخبر عن حقيقة والكلام الطلبي كالاستفهام والنداء والنهي؟",
        "summary_en": "How to distinguish between factual propositions and performative inquiries or requests?",
        "audio_script_ar": "أهلاً بك يا بطل! الأسلوب الخبري هو كلام يحتمل الصدق أو الكذب؛ يخبرنا بمعلومة مثل: (الألعابُ الإلكترونيةُ من الرغباتِ). أما الأسلوب الإنشائي الطلبي فلا يحتمل الصدق والكذب، بل يطلب عملاً، مثل الاستفهام: (كَيْفَ تُقَسِّمُ مَصْرُوفَكَ؟)، والنهي: (لَا تُسْرِفْ فِي الشِّرَاءِ)!",
        "audio_script_en": "Welcome champion! Declarative sentences convey propositions verifiable as true or false, such as 'Video games are desires'. In contrast, creative sentences express requests or commands that cannot be judged true or false, such as inquiries 'How do you divide your allowance?' or prohibitions 'Do not spend lavishly!'",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "الأسلوب الخبري",
                "title_en": "1. Declarative Style",
                "explanation_ar": "يحتمل الصدق أو الكذب لذاته (إِنَّ الأَلْعَابَ مِنَ الرَّغَبَاتِ / زِيَادَةُ الرَّغَبَاتِ تُؤَثِّرُ عَلَى البِيئَةِ).",
                "explanation_en": "Can be verified as true or false (Video games are desires / Increasing desires affects nature)."
            },
            {
                "step_number": 2,
                "title_ar": "الأسلوب الإنشائي الطلبي",
                "title_en": "2. Creative Request Style",
                "explanation_ar": "لا يحتمل الصدق والكذب؛ يشمل الاستفهام (هل / كيف؟)، والنداء (يا)، والنهي (لا تسرف).",
                "explanation_en": "Expresses requests: Questions (Hal / Kayfa?), Calling (Yaa), Prohibitions (Laa tusrif)."
            }
        ],
        "examples": [
            {"sentence_ar": "إِنَّ الأَلْعَابَ الإِلِكْتُرُونِيَّةَ مِنَ الرَّغَبَاتِ.", "translation_en": "Video games are desires.", "type": "أسلوب خبري مؤكد"},
            {"sentence_ar": "كَيْفَ تُقَسِّمُ مَصْرُوفَكَ الشَّهْرِيَّ؟", "translation_en": "How do you divide your monthly allowance?", "type": "أسلوب إنشائي طلبي (استفهام)"}
        ],
        "quiz": [
            {
                "question_ar": "ما نوع الأسلوب في جملة: (هَلْ تَعْلَمُ أَنَّ المَاءَ مِنَ الاِحْتِيَاجَاتِ الضَّرُورِيَّةِ لِلْبَقَاءِ؟)؟",
                "question_en": "What is the style of: 'Did you know that water is essential for survival?'",
                "options": ["أسلوب خبري", "أسلوب إنشائي طلبي (استفهام)", "أسلوب تعجب"],
                "options_en": ["Declarative style", "Creative request style (Question)", "Exclamatory style"],
                "correct_index": 1,
                "explanation_ar": "ممتاز! تبدأ بأداة استفهام (هل) وتنتهي بعلامة (؟)، فتكون أسلوباً إنشائياً طلبياً.",
                "explanation_en": "Superb! Starts with the question word 'Hal' and ends with (؟), making it a Creative request (Question)."
            }
        ]
    },
    {
        "id": "capsule_07_inna_and_sisters",
        "grade": 6,
        "title_ar": "إنَّ وأخواتها وتوكيد الجملة الاسمية",
        "title_en": "Inna and Its Sisters: Sentence Affirmation",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Grammar (النحو)",
        "summary_ar": "ماذا تفعل (إنَّ) عند دخولها على المبتدأ والخبر في الجملة الاسمية؟",
        "summary_en": "How does 'Inna' transform the subject and predicate in a nominal sentence?",
        "audio_script_ar": "هل تريد توكيد كلامك؟ استخدم (إنَّ وأخواتها): (إنَّ، أنَّ، كأنَّ، لكنَّ، ليتَ، لعلَّ). تدخل على المبتدأ والخبر؛ فتنصب المبتدأ بالفتحة مثل: (إِنَّ المَاءَ)، وترفع الخبر بالضمة: (ضَرُورِيٌّ)!",
        "audio_script_en": "Want to emphasize your words? Use Inna and its sisters! Inna enters the nominal sentence, placing a Fathah on the subject (Inna al-maa'a) and maintaining a Dammah on the predicate (daruriyyun).",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "الجملة الاسمية قبل إنَّ",
                "title_en": "1. Nominal Sentence Before Inna",
                "explanation_ar": "المبتدأ مرفوع بالضمة، والخبر مرفوع بالضمة: المَاءُ ضَرُورِيٌّ.",
                "explanation_en": "Subject is nominative with Dammah, predicate is nominative with Dammah."
            },
            {
                "step_number": 2,
                "title_ar": "الجملة الاسمية بعد دخول إنَّ",
                "title_en": "2. Nominal Sentence With Inna",
                "explanation_ar": "اسم إنَّ منصوب بالفتحة + خبر إنَّ مرفوع بالضمة: إِنَّ المَاءَ ضَرُورِيٌّ.",
                "explanation_en": "Noun of Inna takes Fathah (accusative), predicate of Inna takes Dammah (nominative)."
            }
        ],
        "examples": [
            {"sentence_ar": "إِنَّ التَّعْلِيمَ حَقٌّ لِكُلِّ طِفْلٍ.", "translation_en": "Indeed education is a right for every child.", "type": "إنَّ + اسمها المنصوب + خبرها المرفوع"},
            {"sentence_ar": "إِنَّ الأَلْعَابَ الإِلِكْتُرُونِيَّةَ مِنَ الرَّغَبَاتِ.", "translation_en": "Indeed video games are desires.", "type": "إنَّ مؤكدة"}
        ],
        "quiz": [
            {
                "question_ar": "ما الضبط الصحيح لكلمة (العِلْم) بعد إنَّ في: (إِنَّ ......... نُورٌ)؟",
                "question_en": "What is the correct vocalization of 'Al-Ilm' after Inna: (Inna ......... noorun)?",
                "options": ["العِلْمُ (بالضمة)", "العِلْمَ (بالفتحة)", "العِلْمِ (بالكسرة)"],
                "options_en": ["Al-Ilmu (Dammah)", "Al-Ilma (Fathah)", "Al-Ilmi (Kasrah)"],
                "correct_index": 1,
                "explanation_ar": "أحسنت! اسم إنَّ يكون دائماً منصوباً بالفتحة: (إِنَّ العِلْمَ نُورٌ).",
                "explanation_en": "Well done! The noun of Inna is always in the accusative case with Fathah."
            }
        ]
    },
    {
        "id": "capsule_08_mid_hamza",
        "grade": 6,
        "title_ar": "الهمزة المتوسطة وصراع قوة الحركات",
        "title_en": "The Middle Hamza: Hierarchy of Vowel Strength",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Orthography (الإملاء وبنية الكلمة)",
        "summary_ar": "الكسرة أقوى من الضمة، والضمة أقوى من الفتحة، والفتحة أقوى من السكون.",
        "summary_en": "Kasrah beats Dammah, Dammah beats Fathah, Fathah beats Sukun: choose the winning seat!",
        "audio_script_ar": "قاعدة الهمزة المتوسطة هي صراع الحركات! نقارن بين حركة الهمزة وحركة الحرف الذي قبلها: الأقوى الكسرة وتناسبها الياء أو النبرة (فِئَة)، ثم الضمة وتناسبها الواو (مُؤْمِن)، ثم الفتحة وتناسبها الألف (سَأَلَ)!",
        "audio_script_en": "The middle Hamza rule is a battle of vowels! Compare the vowel on the Hamza with the vowel on the letter before it: Kasrah wins (seat on Nabrah: Fi'ah), then Dammah (seat on Waw: Mu'min), then Fathah (seat on Alif: Sa'ala).",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "ترتيب قوة الحركات",
                "title_en": "1. Hierarchy of Vowel Strength",
                "explanation_ar": "١. الكسرة (أقوى الحركات وتناسبها النبرة ئـ) > ٢. الضمة (تناسبها الواو ؤ) > ٣. الفتحة (تناسبها الألف أ) > ٤. السكون (أضعف شيء).",
                "explanation_en": "1. Kasrah (strongest, seat: ئـ) > 2. Dammah (seat: ؤ) > 3. Fathah (seat: أ) > 4. Sukun (weakest)."
            }
        ],
        "examples": [
            {"word_ar": "رَئِيس", "translation_en": "Leader (on Nabrah)", "type": "كسرة على الهمزة", "reason_ar": "الهمزة مكسورة فكتبت على نبرة"},
            {"word_ar": "مُؤَاخَاة", "translation_en": "Brotherhood (on Waw)", "type": "ضمة قبل الهمزة", "reason_ar": "ما قبلها مضموم فكتبت على واو"}
        ],
        "quiz": [
            {
                "question_ar": "لماذا كتبت الهمزة على نبرة في كلمة (فِئَة)؟",
                "question_en": "Why was the Hamza written on Nabrah (ئـ) in 'Fi'ah'?",
                "options": ["لأن ما قبلها مكسور والكسرة هي الأقوى", "لأنها مفتوحة بعد ساكن", "لأن الكلمة جمع"],
                "options_en": ["Because preceded by Kasrah, which is the strongest vowel", "Because open after Sukun", "Because it is plural"],
                "correct_index": 0,
                "explanation_ar": "صحيح! الحرف السابق مكسور (فِـ)، والكسرة هي أقوى الحركات وتناسبها النبرة.",
                "explanation_en": "Correct! The preceding letter has a Kasrah, which dominates all other vowels."
            }
        ]
    },
    {
        "id": "capsule_09_financial_needs_wants",
        "grade": 6,
        "title_ar": "الوعي المالي: التفريق بين الحاجات والرغبات",
        "title_en": "Financial Literacy: Needs vs. Desires",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Vocabulary & Context (المفردات والثقافة المالية)",
        "summary_ar": "معيار البقاء مقابل معيار الرفاهية: كيف يخطط الطالب ميزانيته الشخصية؟",
        "summary_en": "Survival vs. Luxury: How students balance their personal allowance.",
        "audio_script_ar": "الحاجة هي ما يلزمك لتعيش سالماً: ماء، طعام، دواء، مأوى. أما الرغبة فهي ما يجعلك سعيداً لكنك تستطيع العيش بدونه مثل الألعاب والرحلات. في لغتنا: الحكيم من يقدم الحاجة على الرغبة!",
        "audio_script_en": "A Need is what sustains life: water, food, medicine, shelter. A Desire is an upgrade you enjoy but can survive without. In Arabic wisdom: the wise individual prioritizes Needs before Desires!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "شرط البقاء (الحاجات)",
                "title_en": "1. Survival Criterion (Needs)",
                "explanation_ar": "لا يمكن للإنسان الاستغناء عنها كالدواء والطعام والمسكن.",
                "explanation_en": "Indispensable essentials without which human life cannot endure."
            },
            {
                "step_number": 2,
                "title_ar": "شرط الاستغناء والتأجيل (الرغبات)",
                "title_en": "2. Discretionary Criterion (Desires)",
                "explanation_ar": "أشياء تحسينية وترفيهية يمكن تأجيلها دون خطر على الحياة.",
                "explanation_en": "Comfort and entertainment upgrades that can be postponed safely."
            }
        ],
        "examples": [
            {"word_ar": "الدَّوَاءُ وَالغِذَاءُ", "translation_en": "Medicine & Food", "type": "حاجة أساسية للبقاء"},
            {"word_ar": "السَّاعَةُ الفَاخِرَةُ", "translation_en": "Luxury Watch", "type": "رغبة كمالية وترفيهية"}
        ],
        "quiz": [
            {
                "question_ar": "أي من العناصر التالية يصنف ضمن (الرغبات) وليس (الحاجات)؟",
                "question_en": "Which of the following is classified as a Desire rather than a Need?",
                "options": ["مَسْكَنٌ آمِنٌ", "مِيَاهٌ صَالِحَةٌ لِلشُّرْبِ", "هَاتِفٌ ذَكِيٌّ آخِرُ طِرَازٍ"],
                "options_en": ["Safe shelter", "Clean drinking water", "The latest model smartphone"],
                "correct_index": 2,
                "explanation_ar": "إجابة ممتازة! الهاتف الذكي الأحدث هو رغبة تحسينية وترفيهية وليست حاجة بقاء.",
                "explanation_en": "Excellent! The latest flagship smartphone is a luxury want, not a survival need."
            }
        ]
    },
    {
        "id": "capsule_10_prepositions_and_genitive",
        "grade": 6,
        "title_ar": "حروف الجر وأسرار المعاني وعلامة الكسرة",
        "title_en": "Prepositions & The Genitive Case (Kasrah)",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Grammar (حروف المعاني)",
        "summary_ar": "من، إلى، عن، على، في، الباء، الكاف، اللام: تجر الاسم بعدها بالكسرة.",
        "summary_en": "Arabic prepositions govern nouns into the genitive case, taking a Kasrah mark.",
        "audio_script_ar": "حروف الجر أدوات جميلة تربط أجزاء الجملة! (مِنْ، إِلَى، عَنْ، عَلَى، فِي، الباء، الكاف، اللام). الاسم الذي يأتي بعدها يسمى اسماً مجروراً، وتكون علامته الكسرة: (فِي المَدْرَسَةِ)، (عَلَى المَائِدَةِ)!",
        "audio_script_en": "Prepositions link the parts of a sentence gracefully: min, ilaa, 'an, 'alaa, fee, bi, ka, li. The noun following a preposition is governed in the genitive case with a Kasrah: 'Fee al-madrasati', ''Alaa al-maa'idati'!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "حروف الجر الأساسية",
                "title_en": "1. Common Prepositions",
                "explanation_ar": "مِنْ، إِلَى، عَنْ، عَلَى، فِي، الباء، الكاف، اللام.",
                "explanation_en": "Min (from), Ilaa (to), 'An (about), 'Alaa (on), Fee (in), Bi (with/by), Ka (like), Li (for)."
            },
            {
                "step_number": 2,
                "title_ar": "حركة الاسم المجرور",
                "title_en": "2. Genitive Case Vowel",
                "explanation_ar": "الاسم المفرد بعد حرف الجر يجر بالكسرة الظاهرة: (فِي البَيْتِ / عَلَى المَائِدَةِ).",
                "explanation_en": "Singular nouns governed by a preposition take a clear Kasrah: (Fee al-bayti / 'Alaa al-maa'idati)."
            }
        ],
        "examples": [
            {"sentence_ar": "يُؤَثِّرُ الإِسْرَافُ عَلَى البِيئَةِ.", "translation_en": "Wastefulness impacts the environment.", "type": "على + البيئةِ (اسم مجرور بالكسرة)"},
            {"sentence_ar": "سَافَرَ سَالِمٌ إِلَى دُبَيٍّ.", "translation_en": "Salim traveled to Dubai.", "type": "إلى + دبيٍّ"}
        ],
        "quiz": [
            {
                "question_ar": "ما الضبط الصحيح لكلمة (السُّوق) في: (ذَهَبَ خَالِدٌ إِلَى .........)؟",
                "question_en": "What is the correct vocalization of 'Al-Sooq' in: (Dhahaba Khalidun ilaa .........)?",
                "options": ["السُّوقُ (بالضمة)", "السُّوقَ (بالفتحة)", "السُّوقِ (بالكسرة)"],
                "options_en": ["Al-Sooqu (Dammah)", "Al-Sooqa (Fathah)", "Al-Sooqi (Kasrah)"],
                "correct_index": 2,
                "explanation_ar": "أحسنت! سبقت الكلمة بحرف الجر (إِلَى)، فتجر بالكسرة: (إِلَى السُّوقِ).",
                "explanation_en": "Well done! Preceded by the preposition 'ilaa', it takes the genitive Kasrah."
            }
        ]
    },
    {
        "id": "capsule_11_jazam_particles_lam",
        "grade": 7,
        "title_ar": "أدوات جزم المضارع: لَمْ النافية الجازمة وأثرها على السكون",
        "title_en": "Jazam Particles: 'Lam' (Negation & Sukun)",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Grammar (أدوات الجزم والنحو)",
        "summary_ar": "لَمْ: حرف نفي وجزم وقلب يدخل على الفعل المضارع صحيح الآخر فيجزمه بالسكون.",
        "summary_en": "'Lam' negates and governs the sound present tense verb into the jussive case with Sukun.",
        "audio_script_ar": "مرحباً يا بطل الصف السابع! هل تعلم أن أدوات الجزم تحب السكون والهدوء؟ عندما تدخل (لَمْ) على الفعل المضارع، تنفي حدوثه في الماضي وتغير حركته من الضمة إلى السكون: (يَسَافِرُ) تصبح: (لَمْ يُسَافِرْ)! احرص دائماً على وضع السكون فوق الحرف الأخير!",
        "audio_script_en": "Welcome Grade 7 champ! Jazam particles love stillness (Sukun). When 'Lam' precedes a present tense verb, it negates past action and shifts its ending vowel from Dammah to Sukun: 'Yusaafiru' becomes 'Lam yusaafir'! Always place the Sukun on the final consonant!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "وظيفة (لَمْ)",
                "title_en": "1. Function of 'Lam'",
                "explanation_ar": "حرف نفي وجزم وقلب؛ ينفي معنى الفعل ويقلب زمنه إلى الماضي.",
                "explanation_en": "Negates the verb meaning and inverts its temporal focus to the past."
            },
            {
                "step_number": 2,
                "title_ar": "علامة الجزم (السكون)",
                "title_en": "2. Jussive Mark (Sukun)",
                "explanation_ar": "يجزم الفعل المضارع صحيح الآخر بالسكون الظاهر على آخره: لَمْ يَهْمِلْ، لَمْ يَذْهَبْ.",
                "explanation_en": "Regular sound verbs take a distinct Sukun on the final letter: Lam yuhmil, Lam yadh-hab."
            }
        ],
        "examples": [
            {"sentence_ar": "لَمْ يُسَافِرْ خَالِدٌ خَارِجَ الدَّوْلَةِ فِي الإِجَازَةِ.", "translation_en": "Khalid did not travel abroad during the vacation.", "type": "لَمْ + يُسَافِرْ (مجزوم بالسكون)"},
            {"sentence_ar": "لَمْ يَتَأَخَّرْ سَالِمٌ عَنْ مَوْعِدِ الرِّحْلَةِ.", "translation_en": "Salim was not late for the trip schedule.", "type": "لَمْ + يَتَأَخَّرْ (مجزوم بالسكون)"}
        ],
        "quiz": [
            {
                "question_ar": "ما الضبط الصحيح لآخر الفعل (يُشَاهِد) في: (لَمْ يُشَاهِدْ...... مَعَالِمَ المَدِينَةِ)؟",
                "question_en": "What is the correct vocalization of 'Yushaahid' in: (Lam yushaahid......)?",
                "options": ["يُشَاهِدُ (بالضمة)", "يُشَاهِدَ (بالفتحة)", "يُشَاهِدْ (بالسكون)"],
                "options_en": ["Yushaahidu (with Dammah)", "Yushaahida (with Fathah)", "Yushaahid' (with Sukun)"],
                "correct_index": 2,
                "explanation_ar": "أحسنت! أداة الجزم (لَمْ) تجزم الفعل المضارع صحيح الآخر بالسكون الظاهر.",
                "explanation_en": "Well done! The Jazam particle 'Lam' governs the sound present verb with visible Sukun."
            }
        ]
    },
    {
        "id": "capsule_12_jazam_prohibitive_laa",
        "grade": 7,
        "title_ar": "لَا النَّاهِيَةُ الجازمة مقابل لَا النافية غير الجازمة",
        "title_en": "Prohibitive 'Laa' vs. Informative Negative 'Laa'",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Grammar (النهي والنفي)",
        "summary_ar": "لا الناهية تطلب الكف عن الفعل وتجزم بالسكون، بينما لا النافية تخبر ويبقى الفعل مرفوعاً بالضمة.",
        "summary_en": "Prohibitive Laa commands stopping and governs Sukun; negative Laa merely reports leaving Dammah.",
        "audio_script_ar": "فرق دقيق وهام جداً في الاختبار الوزاري! (لَا النَّاهِيَةُ) تفيد طلباً: (يَا أَحْمَدُ، لَا تُهْمِلْ دُرُوسَكَ!) فهنا تجزم بالسكون. أما (لَا النَّافِيَةُ) فتخبرك فقط دون أمر أو طلب: (أَحْمَدُ لَا يُهْمِلُ دُرُوسَهُ) فيبقى الفعل مرفوعاً بالضمة!",
        "audio_script_en": "A pivotal distinction in MoE exams! Prohibitive 'Laa' directs a command to desist: 'Ya Ahmad, laa tuhmil duroosaka!' governing Sukun. Negative 'Laa' merely states a fact: 'Ahmad laa yuhmilu duroosahu' retaining the nominative Dammah!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "لا الناهية (طلب وكف)",
                "title_en": "1. Prohibitive Laa",
                "explanation_ar": "تطلب الامتناع عن الفعل وتجزم بالسكون: (لَا تَخَفْ، لَا تَقْتَرِبْ).",
                "explanation_en": "Demands refraining from an action and governs Sukun."
            },
            {
                "step_number": 2,
                "title_ar": "لا النافية (إخبار دون طلب)",
                "title_en": "2. Negative Laa",
                "explanation_ar": "تخبر عن عدم وقوع الفعل ولا تجزم، ويبقى الفعل مرفوعاً بالضمة: (المُؤْمِنُ لَا يَكْذِبُ).",
                "explanation_en": "Informs that an action is not happening; verb remains nominative with Dammah."
            }
        ],
        "examples": [
            {"sentence_ar": "لَا تَسْهَرْ طَوِيلاً لَيْلَةَ الِامْتِحَانِ.", "translation_en": "Do not stay up late on exam night.", "type": "لا ناهية جازمة (تَسْهَرْ بالسكون)"},
            {"sentence_ar": "عُمَرُ لَا يَسْهَرُ طَوِيلاً.", "translation_en": "Omar does not stay up late.", "type": "لا نافية غير جازمة (يَسْهَرُ بالضمة)"}
        ],
        "quiz": [
            {
                "question_ar": "أي من الجمل التالية تشتمل على (لَا النَّاهِيَةِ) الجازمة؟",
                "question_en": "Which of the following sentences contains the Jazam Prohibitive 'Laa'?",
                "options": ["الطَّالِبُ لَا يُقَصِّرُ فِي وَاجِبِهِ", "لَا تَقْتَرِبْ مِنَ الأَمَاكِنِ الخَطِرَةِ", "نَحْنُ لَا نُسَافِرُ فِي الشِّتَاءِ"],
                "options_en": ["The student does not neglect his duty", "Do not approach hazardous areas", "We do not travel in winter"],
                "correct_index": 1,
                "explanation_ar": "صحيح! (لَا تَقْتَرِبْ) فيها طلب ونهي، ولذلك جُزم الفعل بالسكون.",
                "explanation_en": "Correct! 'Laa taqtarib' conveys a direct prohibition command, governing the verb with Sukun."
            }
        ]
    },
    {
        "id": "capsule_13_imperative_laam",
        "grade": 7,
        "title_ar": "لَامُ الأَمْرِ الجازمة وصيغة الطلب",
        "title_en": "Imperative 'Laam' & Action Execution",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Grammar (لام الأمر والجزم)",
        "summary_ar": "لام الأمر حرف جزم مكسور (لِـ) يدخل على المضارع لتحويله إلى صيغة أمر تجزم بالسكون.",
        "summary_en": "Imperative Laam (Li-) enters the present verb to express a command governed by Sukun.",
        "audio_script_ar": "أداة الجزم الثالثة هي (لَامُ الأَمْرِ)! وهي لام مكسورة تدخل على الفعل المضارع لتحوله إلى أمر مباشر: (لِتَكْتُبْ تَقْرِيرَكَ)، (لِنَحْرِصْ عَلَى النَّظَافَةِ). وعلامة جزمها أيضاً السكون الظاهر!",
        "audio_script_en": "The third Jazam particle is Imperative 'Laam'! It carries a Kasrah (Li-) and enters present tense verbs to formulate a direct command: 'Li-taktub taqreeraka' (Write your report). Its jussive mark is likewise a clear Sukun!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "صيغة لام الأمر",
                "title_en": "1. Imperative Laam Form",
                "explanation_ar": "لام مكسورة (لِـ) تأتي في أول الفعل المضارع تفيد طلب الفعل: لِـ + تَعْمَلْ = لِتَعْمَلْ.",
                "explanation_en": "Prefixed 'Li-' conveying an imperative request: Li + ta'mal = Li-ta'mal."
            }
        ],
        "examples": [
            {"sentence_ar": "لِتَجْتَهِدْ فِي دِرَاسَتِكَ لِتَحْقِيقِ النَّجَاحِ.", "translation_en": "Exert effort in your studies to achieve success.", "type": "لِـ + تَجْتَهِدْ (مجزوم بالسكون)"},
            {"sentence_ar": "لِنَحْتَفِلْ بِإِنْجَازَاتِ الوَطَنِ.", "translation_en": "Let us celebrate national achievements.", "type": "لِـ + نَحْتَفِلْ (مجزوم بالسكون)"}
        ],
        "quiz": [
            {
                "question_ar": "ما المعنى الذي تفيده اللام في: (لِتَسْتَمْتِعْ بِإِجَازَتِكَ يَا خَالِدُ)؟",
                "question_en": "What meaning does the Laam convey in: 'Li-tastamti' bi-ijaazatika ya Khalid'?",
                "options": ["التَّعْلِيلُ وَبَيَانُ السَّبَبِ", "الأَمْرُ وَطَلَبُ الفِعْلِ", "النَّفْيُ"],
                "options_en": ["Justification / reason", "Imperative command / request", "Negation"],
                "correct_index": 1,
                "explanation_ar": "أحسنت! لام الأمر تفيد توجيه الطلب والأمر المباشر للمخاطب أو الغائب.",
                "explanation_en": "Well done! Imperative Laam conveys a direct command request."
            }
        ]
    },
    {
        "id": "capsule_14_vacation_glossary",
        "grade": 7,
        "title_ar": "قَامُوسِيَ الخَاصُّ: معجم الإجازة والاستجمام في الإمارات",
        "title_en": "Special Glossary: Vacation & Landmark Lexicon",
        "duration_minutes": 3,
        "difficulty": "Easy",
        "topic": "Vocabulary & Context (المفردات والمعاجم)",
        "summary_ar": "مفردات الوحدة الأولى للصف السابع: البارحة، الراحة، المرتفعات، القمم، برج خليفة.",
        "summary_en": "Grade 7 Unit 1 vocabulary: Yesterday, Relaxation, Highlands, Mountain Summits, Burj Khalifa.",
        "audio_script_ar": "مفردات جميلة في منهاج الصف السابع! (البَارِحَةُ) تعني الأمس أو الليلة الماضية. (المُرْتَفَعَاتُ) هي الأماكن الجبلية العالية، و(القِمَمُ) جمع قمة وهي أعلى نقطة في الجبل. و(بُرْجُ خَلِيفَةَ) فخر دبي وأعلى بناء في العالم!",
        "audio_script_en": "Beautiful vocabulary in Grade 7! 'Al-Baarihah' denotes yesterday. 'Al-Murtafa'aat' refers to elevated mountain heights, and 'Al-Qimam' is plural of peak. And 'Burj Khalifa' stands tall as Dubai's pride and the world's highest skyscraper!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "مفردات الزمان والجغرافيا",
                "title_en": "1. Temporal & Geographic Terms",
                "explanation_ar": "البارحة (الأمس) / الراحة (الاسترخاء وتجديد النشاط) / المرتفعات والقمم (الجبال).",
                "explanation_en": "Al-Baarihah (yesterday) / Ar-Raahah (rest) / Murtafa'aat & Qimam (mountain heights)."
            }
        ],
        "examples": [
            {"word_ar": "البَارِحَة", "translation_en": "Yesterday", "type": "ظرف زمان"},
            {"word_ar": "المُرْتَفَعَاتُ وَالقِمَم", "translation_en": "Highlands & Peaks", "type": "تعبير جغرافي"},
            {"word_ar": "بُرْجُ خَلِيفَة", "translation_en": "Burj Khalifa", "type": "معلم سياحي عالمي"}
        ],
        "quiz": [
            {
                "question_ar": "ما مفرد كلمة (القِمَم) الواردة في قاموس الدرس؟",
                "question_en": "What is the singular form of 'Al-Qimam' in the lesson dictionary?",
                "options": ["قَمِيص", "قِمَّة", "قِمَار"],
                "options_en": ["Qamees", "Qimmah (Peak / Summit)", "Qimaar"],
                "correct_index": 1,
                "explanation_ar": "صحيح! مفرد القمم هو (قِمَّة)، وهي أعلى نقطة في الجبل أو البناء.",
                "explanation_en": "Correct! The singular of 'Al-Qimam' is 'Qimmah', meaning mountain peak."
            }
        ]
    },
    {
        "id": "capsule_15_vacation_narration",
        "grade": 7,
        "title_ar": "كَيْفَ أُعَبِّرُ عَنْ قَضَاءِ إِجَازَتِي وَمُغَامَرَاتِي؟",
        "title_en": "How to Narrate Vacation Experiences & Summer Adventures",
        "duration_minutes": 4,
        "difficulty": "Medium",
        "topic": "Writing & Expression (التعبير الكتابي والتحدث)",
        "summary_ar": "خطوات التعبير عن رحلة الإجازة: المكان، الزمان، الأنشطة، المشاعر، والتوصيات.",
        "summary_en": "Key pillars of vacation storytelling: location, timing, activities, reflections, recommendations.",
        "audio_script_ar": "عندما يطلب منك معلمك التحدث عن إجازتك، اتبع الترتيب الذهبي: أين ذهبت؟ متى؟ مع من؟ ماذا شاهدت؟ وما هو شعورك في ختام الرحلة؟ تذكر استخدام المفردات الجديدة مثل: (الاستجمام، المرتفعات، المعالم الرائعة)!",
        "audio_script_en": "When narrating your vacation, follow the golden framework: Where did you go? When? With whom? What did you explore? And how did you feel? Infuse your text with fresh vocabulary like relaxation, highlands, and awe-inspiring landmarks!",
        "rule_steps": [
            {
                "step_number": 1,
                "title_ar": "عناصر نص الإجازة",
                "title_en": "1. Vacation Narrative Structure",
                "explanation_ar": "المقدمة (الزمان والوجهة) -> العرض (الأنشطة والمعالم) -> الخاتمة (المشاعر والذكريات).",
                "explanation_en": "Introduction (date & destination) -> Body (landmarks & activities) -> Conclusion (emotions)."
            }
        ],
        "examples": [
            {"sentence_ar": "قَضَيْتُ إِجَازَتِي الصَّيْفِيَّةَ فِي رُبُوعِ الإِمَارَاتِ مُسْتَمْتِعاً بِالمُرْتَفَعَاتِ الخَلَّابَةِ.", "translation_en": "I spent my summer vacation across the Emirates admiring picturesque mountain heights.", "type": "تعبير وصفي راقٍ"}
        ],
        "quiz": [
            {
                "question_ar": "أي مما يلي يعد أفضل افتتاحية لموضوع تعبير عن (إجازتي الصيفية)؟",
                "question_en": "Which of the following serves as the strongest opening for a vacation composition?",
                "options": ["لَا أُحِبُّ الكِتَابَةَ اليَوْمَ", "مَعَ إِشْرَاقَةِ العُطْلَةِ الصَّيْفِيَّةِ، انْطَلَقْتُ مَعَ عَائِلَتِي فِي رِحْلَةٍ سِيَاحِيَّةٍ مَاتِعَةٍ", "انْتَهَتِ الإِجَازَةُ بِسُرْعَةٍ"],
                "options_en": ["I don't like writing today", "With the dawn of summer break, I embarked with my family on an exciting tour", "Vacation ended quickly"],
                "correct_index": 1,
                "explanation_ar": "ممتاز! هذه بداية مشوقة تجمع بين الزمان والانطلاق الإيجابي نحو الوجهة السياحية.",
                "explanation_en": "Excellent! An engaging hook introducing the time frame and family excursion."
            }
        ]
    }
]

def get_all_capsules(grade: Any = None) -> List[Dict[str, Any]]:
    """Return all available microlearning capsules, optionally filtered by grade."""
    if grade is not None:
        try:
            g = int(grade)
            filtered = [c for c in CAPSULES_DATA if c.get("grade") == g]
            if filtered:
                return filtered
        except (ValueError, TypeError):
            pass
    return CAPSULES_DATA

def get_capsule_by_id(capsule_id: str) -> Dict[str, Any]:
    """Retrieve specific capsule by ID."""
    for c in CAPSULES_DATA:
        if c["id"] == capsule_id:
            return c
    return CAPSULES_DATA[0]
