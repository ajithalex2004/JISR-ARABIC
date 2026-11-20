"""
Interactive Study Booklets (الملازم الذكية) — Malazim Hub
Authentic curriculum consolidation for CBSE Curriculum Grade 5 Arabic.
Offers two distinct modes:
1. Study Mode (وضع المذاكرة): Deep conceptual breakdown with step-by-step explanations and inline exercises.
2. Notes / Quick Review Mode (وضع الملاحظات): 15-minute high-yield cheat sheets, flashcards, and exam memory anchors.
"""

from typing import Dict, Any, List

MALAZIM_DATA: Dict[str, Dict[str, Any]] = {
    "lesson_01_ball_games": {
        "lesson_id": "lesson_01_ball_games",
        "title_ar": "مُلْزَمَةُ أَلْعَابِ الكُرَةِ — الوَحْدَةُ الأُولَى",
        "title_en": "Ball Games Smart Booklet — Unit 1",
        "grade": 5,
        "term": 1,
        "pages_reference": "Pages 6–15 (CBSE Curriculum Student Book)",
        "curriculum_alignment": "UAE Ministry of Education & CBSE Arabic (Non-Arabs)",
        
        # -------------------------------------------------------------
        # MODE 1: STUDY MODE (وضع المذاكرة الشامل مع التمارين التفاعلية)
        # -------------------------------------------------------------
        "study_mode": {
            "mode_title_ar": "وضع المذاكرة التفاعلية الشاملة",
            "mode_title_en": "Comprehensive Interactive Study Mode",
            "estimated_minutes": 25,
            "sections": [
                {
                    "section_id": "sec_01_concept",
                    "title_ar": "١. مَفْهُومُ الكُرَةِ وَلَقَبُ (السَّاحِرَةِ المُسْتَدِيرَةِ)",
                    "title_en": "1. Ball Concept & 'The Round Witch' Moniker",
                    "content_ar": "الكُرَةُ هِيَ كُلُّ جِسْمٍ مُسْتَدِيرٍ يُصْنَعُ مِنَ الجِلْدِ أَوِ المَطَّاطِ. وَتُعَدُّ كُرَةُ القَدَمِ اللُّعْبَةَ الأَكْثَرَ شَعْبِيَّةً فِي العَالَمِ، حَيْثُ أَطْلَقَ عَلَيْهَا عُشَّاقُهَا لَقَبَ (السَّاحِرَةِ المُسْتَدِيرَةِ) لِأَنَّهَا سَحَرَتْ عُقُولَ وَقُلُوبَ أَكْثَرَ مِنْ مِلْيَارِ مُشَجِّعٍ حَوْلَ العَالَمِ بِجَمَالِهَا وَإِثَارَتِهَا.",
                    "content_en": "A ball is any spherical object crafted from leather or rubber. Football is the world's most popular sport, famously dubbed 'The Round Witch' (الساحرة المستديرة) because its thrill captivates over a billion fans globally.",
                    "key_takeaways_ar": [
                        "الكُرَةُ: كُلُّ جِسْمٍ مُسْتَدِيرٍ.",
                        "سَبَبُ التَّسْمِيَةِ: سِحْرُهَا لِعُقُولِ وَقُلُوبِ المَلَايِينِ بِحَمَاسِهَا وَشَعْبِيَّتِهَا الجَارِفَةِ."
                    ],
                    "key_takeaways_en": [
                        "The Ball: Any spherical round object.",
                        "Reason for Title: Enchanting the minds and hearts of millions with thrilling excitement."
                    ],
                    "inline_exercise": {
                        "question_ar": "لِمَاذَا سُمِّيَتْ كُرَةُ القَدَمِ بِـ (السَّاحِرَةِ المُسْتَدِيرَةِ)؟",
                        "question_en": "Why was football nicknamed 'The Round Witch' (The Enchantress)?",
                        "options": [
                            "لِأَنَّهَا مَصْنُوعَةٌ مِنْ خَامَاتٍ سِحْرِيَّةٍ",
                            "لِأَنَّهَا جَذَبَتْ وَسَحَرَتْ قُلُوبَ وَعُقُولَ مَلَايِينِ الجَمَاهِيرِ",
                            "لِأَنَّهَا تُلْعَبُ فَقَطْ فِي المَسَاءِ"
                        ],
                        "options_en": [
                            "Because it is made of magical materials",
                            "Because it captivated and enchanted the hearts and minds of millions of fans",
                            "Because it is only played in the evening"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "أَحْسَنْتَ! لُقِّبَتْ بِالسَّاحِرَةِ لِأَنَّ إِثَارَتَهَا وَشَعْبِيَّتَهَا جَذَبَتْ عُقُولَ المُشَجِّعِينَ فِي شَتَّى بِقَاعِ الأَرْضِ.",
                        "explanation_en": "Well done! Nicknamed 'The Enchantress' because its excitement and popularity captivate fans worldwide."
                    }
                },
                {
                    "section_id": "sec_02_rules",
                    "title_ar": "٢. أَبْعَادُ المَلْعَبِ وَالمُوَاصَفَاتُ الرَّسْمِيَّةُ",
                    "title_en": "2. Pitch Dimensions & Official Specifications",
                    "content_ar": "مَلْعَبُ كُرَةِ القَدَمِ مُسْتَطِيلُ الشَّكْلِ وَمُغَطًّى بِالعُشْبِ الأَخْضَرِ (الطَّبِيعِيِّ أَوِ الاصْطِنَاعِيِّ). يَبْلُغُ طُولُ المَلْعَبِ بَيْنَ 100 إِلَى 110 أَمْتَارٍ، وَعَرْضُهُ بَيْنَ 64 إِلَى 75 مِتْرًا. أَمَّا مُحِيطُ الكُرَةِ الرَّسْمِيَّةِ فَيَتَرَاوَحُ بَيْنَ 68 إِلَى 70 سَنْتِيمِتْرًا وَوَزْنُهَا بَيْنَ 410 إِلَى 450 غِرَامًا.",
                    "content_en": "A football pitch is rectangular and turfed with green grass. Length ranges from 100m to 110m, and width from 64m to 75m. The official ball circumference is 68 to 70 cm, weighing 410 to 450 grams.",
                    "key_takeaways_ar": [
                        "شَكْلُ المَلْعَبِ: مُسْتَطِيلٌ وَمَفْرُوشٌ بِالعُشْبِ الأَخْضَرِ.",
                        "أَبْعَادُ الطُّولِ: 100 – 110 م | أَبْعَادُ العَرْضِ: 64 – 75 م.",
                        "مُحِيطُ الكُرَةِ: 68 – 70 سم."
                    ],
                    "key_takeaways_en": [
                        "Pitch shape: Rectangular covered with green turf.",
                        "Dimensions: 100–110m in length | 64–75m in width.",
                        "Ball circumference: 68–70 cm."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا هُوَ مُحِيطُ كُرَةِ القَدَمِ القَانُونِيَّةِ حَسَبَ لَوَائِحِ الاتِّحَادِ الدَّوْلِيِّ؟",
                        "question_en": "What is the official circumference of a regulation football per FIFA rules?",
                        "options": [
                            "50 إِلَى 55 سم",
                            "68 إِلَى 70 سم",
                            "80 إِلَى 85 سم"
                        ],
                        "options_en": [
                            "50 to 55 cm",
                            "68 to 70 cm",
                            "80 to 85 cm"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "صَحِيحٌ تَمَامًا! يَتَرَاوَحُ مُحِيطُ الكُرَةِ الرَّسْمِيَّةِ بَيْنَ 68 إِلَى 70 سم.",
                        "explanation_en": "Spot on! The official regulation ball circumference measures between 68 and 70 cm."
                    }
                },
                {
                    "section_id": "sec_03_referees",
                    "title_ar": "٣. الفَرِيقُ وَالتَّحْكِيمُ فِي المُبَارَاةِ",
                    "title_en": "3. Team Structure & Officiating Crew",
                    "content_ar": "يَتَكَوَّنُ كُلُّ فَرِيقٍ فِي كُرَةِ القَدَمِ مِنْ 11 لَاعِبًا أَسَاسِيًّا، أَحَدُهُمْ حَارِسُ المَرْمَى. وَيَقُودُ المُبَارَاةَ طَاقَمٌ تَحْكِيمِيٌّ مُكَوَّنٌ مِنْ 4 حُكَّامٍ: حَكَمُ السَّاحَةِ الرَّئِيسِيُّ، وَحَكَمَانِ مُسَاعِدَانِ عَلَى خَطَّيِ التَّمَاسِّ (حَامِلَا الرَّايَةِ)، وَالحَكَمُ الرَّابِعُ المُسَاعِدُ.",
                    "content_en": "Each team fields 11 starting players, including one goalkeeper. Matches are governed by 4 referees: the Head Referee, two Assistant Referees (linesmen), and the Fourth Official.",
                    "key_takeaways_ar": [
                        "عَدَدُ لَاعِبِي الفَرِيقِ: 11 لَاعِبًا فِي أَرْضِ المَلْعَبِ.",
                        "مُدَّةُ المُبَارَاةِ: 90 دَقِيقَةً مُقَسَّمَةً إِلَى شَوْطَيْنِ (45 دَقِيقَةً لِكُلِّ شَوْطٍ).",
                        "طَاقَمُ التَّحْكِيمِ: 4 حُكَّامٍ لِتَطْبِيقِ العَدَالَةِ وَقَوَانِينِ اللُّعْبَةِ."
                    ],
                    "key_takeaways_en": [
                        "Team size: 11 starting players on the pitch.",
                        "Match duration: 90 minutes split into two 45-minute halves.",
                        "Officiating crew: 4 match officials upholding fairness and rules."
                    ],
                    "inline_exercise": {
                        "question_ar": "كَمْ عَدَدُ الحُكَّامِ الإِجْمَالِيُّ الَّذِينَ يُدِيرُونَ مُبَارَاةَ كُرَةِ القَدَمِ الرَّسْمِيَّةَ؟",
                        "question_en": "How many total referees officiate an official football match?",
                        "options": [
                            "حَكَمَانِ فَقَطْ",
                            "3 حُكَّامٍ",
                            "4 حُكَّامٍ"
                        ],
                        "options_en": [
                            "Only 2 referees",
                            "3 referees",
                            "4 referees"
                        ],
                        "correct_index": 2,
                        "explanation_ar": "إِجَابَةٌ مُمْتَازَةٌ! يُدِيرُ المُبَارَاةَ 4 حُكَّامٍ (حَكَمُ السَّاحَةِ، حَكَمَانِ مُسَاعِدَانِ، وَالحَكَمُ الرَّابِعُ).",
                        "explanation_en": "Excellent answer! 4 referees manage the match (Head referee, two assistant referees, and the fourth official)."
                    }
                },
                {
                    "section_id": "sec_04_sports_types",
                    "title_ar": "٤. تَصْنِيفُ الرِّيَاضَاتِ: جَمَاعِيَّةٌ وَفَرْدِيَّةٌ",
                    "title_en": "4. Sports Classification: Collective vs. Individual",
                    "content_ar": "تَنْقَسِمُ الرِّيَاضَاتُ إِلَى نَوْعَيْنِ رَئِيسِيَّيْنِ: رِيَاضَاتٍ جَمَاعِيَّةٍ تَتَطَلَّبُ رُوحَ الفَرِيقِ وَالتَّعَاوُنَ (مِثْلَ: كُرَةِ القَدَمِ، كُرَةِ السَّلَّةِ، الكُرَةِ الطَّائِرَةِ)، وَرِيَاضَاتٍ فَرْدِيَّةٍ يَعْتَمِدُ فِيهَا الإِنْجَازُ عَلَى مَهَارَةِ شَخْصٍ وَاحِدٍ (مِثْلَ: الرِّمَايَةِ، رُكُوبِ الخَيْلِ، السِّبَاحَةِ، أَلْعَابِ القُوَى).",
                    "content_en": "Sports are classified into two primary categories: Collective Sports requiring team coordination (football, basketball, volleyball), and Individual Sports relying on solo mastery (archery, horse riding, swimming, athletics).",
                    "key_takeaways_ar": [
                        "الرِّيَاضَةُ الجَمَاعِيَّةُ: يَشْتَرِكُ فِيهَا فَرِيقٌ مُتَعَاوِنٌ.",
                        "الرِّيَاضَةُ الفَرْدِيَّةُ: يُمَارِسُهَا رِيَاضِيٌّ بِمُفْرَدِهِ."
                    ],
                    "key_takeaways_en": [
                        "Collective sport: Involves a collaborative team.",
                        "Individual sport: Practiced by an athlete independently."
                    ],
                    "inline_exercise": {
                        "question_ar": "أَيُّ الرِّيَاضَاتِ التَّالِيَةِ تُعَدُّ رِيَاضَةً فَرْدِيَّةً؟",
                        "question_en": "Which of the following sports is considered an individual sport?",
                        "options": [
                            "كُرَةُ القَدَمِ",
                            "الرِّمَايَةُ وَرُكُوبُ الخَيْلِ",
                            "كُرَةُ السَّلَّةِ"
                        ],
                        "options_en": [
                            "Football",
                            "Archery and horse riding",
                            "Basketball"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "رَائِعٌ! الرِّمَايَةُ وَرُكُوبُ الخَيْلِ رِيَاضَتَانِ فَرْدِيَّتَانِ يَعْتَمِدُ فِيهِمَا اللَّاعِبُ عَلَى قُدُرَاتِهِ الذَّاتِيَّةِ.",
                        "explanation_en": "Superb! Archery and horse riding are individual sports where performance depends on solo skill."
                    }
                }
            ]
        },

        # -------------------------------------------------------------
        # MODE 2: QUICK REVIEW MODE (وضع الملاحظات ومراجعة الـ 15 دقيقة)
        # -------------------------------------------------------------
        "quick_review_mode": {
            "mode_title_ar": "وضع الملاحظات والمراجعة السريعة (15 دقيقة)",
            "mode_title_en": "15-Minute Fast Revision & Cheat-Sheet Mode",
            "target_review_time": "15 minutes",
            "bullet_rules": [
                {
                    "rule_ar": "الكُرَةُ جِسْمٌ مُسْتَدِيرٌ، وَكُرَةُ القَدَمِ تُلَقَّبُ بِـ (السَّاحِرَةِ المُسْتَدِيرَةِ).",
                    "rule_en": "A ball is spherical; football is dubbed 'The Round Witch'."
                },
                {
                    "rule_ar": "عَدَدُ اللَّاعِبِينَ فِي المَلْعَبِ: 11 لَاعِبًا لِكُلِّ فَرِيقٍ (شَوْطَانِ مُدَّةُ كُلٍّ مِنْهُمَا 45 دَقِيقَةً).",
                    "rule_en": "Players per team: 11 on pitch (Two 45-minute halves)."
                },
                {
                    "rule_ar": "طُولُ المَلْعَبِ: 100 إِلَى 110 أَمْتَارٍ | العَرْضُ: 64 إِلَى 75 مِتْرًا.",
                    "rule_en": "Pitch Length: 100-110m | Width: 64-75m."
                },
                {
                    "rule_ar": "طَاقَمُ التَّحْكِيمِ: 4 حُكَّامٍ رَسْمِيِّينَ لِإِدَارَةِ المُبَارَاةِ.",
                    "rule_en": "Officiating crew: 4 official referees."
                },
                {
                    "rule_ar": "الرِّيَاضَاتُ الجَمَاعِيَّةُ: كُرَةُ القَدَمِ وَالسَّلَّةِ وَالطَّائِرَةِ | الفَرْدِيَّةُ: الرِّمَايَةُ وَالفُرُوسِيَّةُ وَالسِّبَاحَةُ.",
                    "rule_en": "Collective: Football, Basketball | Individual: Archery, Falconry, Equestrian."
                }
            ],
            "vocabulary_flashcards": [
                {"word_ar": "المُسْتَدِيرَةُ", "word_en": "The Round (Spherical)", "meaning_ar": "الَّتِي عَلَى شَكْلِ دَائِرَةٍ", "meaning_en": "Having the shape of a circle/sphere", "opposite_ar": "المُرَبَّعَةُ أَوِ المُسْتَقِيمَةُ", "opposite_en": "Square or straight"},
                {"word_ar": "الجَمَاعِيَّةُ", "word_en": "Collective (Team)", "meaning_ar": "يُشَارِكُ فِيهَا أَكْثَرُ مِنْ شَخْصٍ", "meaning_en": "Involving more than one person", "opposite_ar": "الفَرْدِيَّةُ", "opposite_en": "Individual (Solo)"},
                {"word_ar": "المِضْمَارُ", "word_en": "The Track", "meaning_ar": "مَيْدَانُ السِّبَاقِ وَالرَّكْضِ", "meaning_en": "The field for racing and running", "opposite_ar": "—", "opposite_en": "—"},
                {"word_ar": "السَّاحِرَةُ", "word_en": "The Enchantress", "meaning_ar": "الفَاتِنَةُ الجَاذِبَةُ لِلْقُلُوبِ", "meaning_en": "The captivating charmer of hearts", "opposite_ar": "المُنَفِّرَةُ", "opposite_en": "Repelling"}
            ],
            "grammar_formulas": [
                {
                    "title_ar": "الجُمْلَةُ الاسْمِيَّةُ",
                    "title_en": "The Nominal Sentence",
                    "formula_ar": "مُبْتَدَأٌ (مَرْفُوعٌ) + خَبَرٌ (مَرْفُوعٌ)",
                    "formula_en": "Subject (Nominative / Dammah) + Predicate (Nominative / Dammah)",
                    "example_ar": "الكُرَةُ مُسْتَدِيرَةٌ (الكُرَةُ: مُبْتَدَأٌ مَرْفُوعٌ، مُسْتَدِيرَةٌ: خَبَرٌ مَرْفُوعٌ).",
                    "example_en": "The ball is round (Al-Kuratu: nominative subject, mustadeeratun: nominative predicate)."
                },
                {
                    "title_ar": "مُطَابَقَةُ الفِعْلِ لِلْفَاعِلِ",
                    "title_en": "Subject-Verb Gender Agreement",
                    "formula_ar": "مُذَكَّرٌ ← يَلْعَبُ الطَّالِبُ | مُؤَنَّثٌ ← تَلْعَبُ الطَّالِبَةُ",
                    "formula_en": "Masculine Subject -> Verb starts with Yaa | Feminine Subject -> Verb starts with Taa",
                    "example_ar": "يُحِبُّ زَايِدٌ كُرَةَ القَدَمِ / تُحِبُّ مَرْيَمُ كُرَةَ السَّلَّةِ.",
                    "example_en": "Zayed loves football / Maryam loves basketball."
                }
            ],
            "exam_pitfall_warnings": [
                {
                    "warning_ar": "لَا تَخْلِطْ بَيْنَ عَدَدِ الحُكَّامِ (4 حُكَّامٍ) وَعَدَدِ المُسَاعِدِينَ فَقَطْ (حَكَمَانِ مُسَاعِدَانِ).",
                    "warning_en": "Do not confuse total match referees (4 officials) with just assistant referees (2 linesmen)."
                },
                {
                    "warning_ar": "انْتَبِهْ: مُدَّةُ الشَّوْطِ الوَاحِدِ 45 دَقِيقَةً، بَيْنَمَا مُدَّةُ المُبَارَاةِ كَامِلَةً 90 دَقِيقَةً دُونَ الوَقْتِ الإِضَافِيِّ.",
                    "warning_en": "Note: One half is 45 minutes, while the full match is 90 minutes regular time."
                },
                {
                    "warning_ar": "التَّاءُ المَرْبُوطَةُ (ـة/ة) تُنْطَقُ هَاءً عِنْدَ الوَقْفِ وَتَاءً عِنْدَ الوَصْلِ، بِعَكْسِ الهَاءِ (ـه/ه) الَّتِي تُنْطَقُ دَائِمًا هَاءً.",
                    "warning_en": "Taa Marbutah (ـة) sounds as /h/ at pause and /t/ in flow; regular Haa (ـه) always sounds as /h/."
                }
            ]
        }
    },
    "lesson_g6_t1_ch01": {
        "lesson_id": "lesson_g6_t1_ch01",
        "title_ar": "ملزمة احْتِيَاجَاتِي وَرَغَبَاتِي وَالأَسَالِيبُ البَلَاغِيَّةُ — الوحدة الأولى",
        "title_en": "Needs, Desires & Sentence Styles Smart Booklet — Grade 6 Unit 1",
        "grade": 6,
        "term": 1,
        "pages_reference": "Pages 8–18 (CBSE Curriculum Student Book Grade 6)",
        "curriculum_alignment": "UAE Ministry of Education & CBSE Arabic Grade 6",

        # -------------------------------------------------------------
        # MODE 1: STUDY MODE (وضع المذاكرة الشامل مع التمارين التفاعلية)
        # -------------------------------------------------------------
        "study_mode": {
            "mode_title_ar": "وضع المذاكرة التفاعلية الشاملة (الصف السادس)",
            "mode_title_en": "Comprehensive Interactive Study Mode (Grade 6)",
            "estimated_minutes": 25,
            "sections": [
                {
                    "section_id": "sec_g6_01_needs_wants",
                    "title_ar": "١. مفهوم الاحتياجات الضرورية والرغبات الكمالية",
                    "title_en": "1. Needs vs. Desires & Financial Wisdom",
                    "content_ar": "الاحْتِيَاجَاتُ (Needs) هِيَ الأُمُورُ الأَسَاسِيَّةُ الَّتِي لَا يَسْتَطِيعُ الإِنْسَانُ البَقَاءَ عَلَى قَيْدِ الحَيَاةِ بِدُونِهَا مِثْلَ: المَاءِ، وَالطَّعَامِ، وَالدَّوَاءِ، وَالمَسْكَنِ، وَالتَّعْلِيمِ. أَمَّا الرَّغَبَاتُ (Desires) فَهِيَ الأَشْيَاءُ التَّحْسِينِيَّةُ وَالتَّرْفِيهِيَّةُ الَّتِي يُحِبُّهَا الإِنْسَانُ وَيُمْكِنُ تَأْجِيلُهَا دُونَ خَطَرٍ عَلَى حَيَاتِهِ مِثْلَ: الأَلْعَابِ الإِلِكْتُرُونِيَّةِ، وَالسَّفَرِ لِلسِّيَاحَةِ، وَالسَّاعَةِ الفَاخِرَةِ.",
                    "content_en": "Needs are fundamental essentials human beings cannot survive without, such as water, food, medicine, shelter, and basic education. Desires (Wants) are luxury and entertainment upgrades that a person enjoys having, but can easily be postponed without threatening life or well-being, such as video games, leisure travel, and luxury watches.",
                    "key_takeaways_ar": [
                        "الحاجة: ضرورة ملحة للبقاء والاستمرار في الحياة.",
                        "الرغبة: تحسينية وترفيهية يمكن الاستغناء عنها أو تأجيلها."
                    ],
                    "key_takeaways_en": [
                        "Need: An indispensable vital essential for human survival.",
                        "Desire: A luxury or comfort enhancement that can be delayed."
                    ],
                    "inline_exercise": {
                        "question_ar": "أَيُّ هَذِهِ الأُمُورِ يُعَدُّ مِنَ الاحْتِيَاجَاتِ الأَسَاسِيَّةِ لِلْبَقَاءِ؟",
                        "question_en": "Which of the following is considered an essential need for survival?",
                        "options": [
                            "شِرَاءُ هَاتِفٍ ذَكِيٍّ جَدِيدٍ",
                            "تَنَاوُلُ المَاءِ وَالطَّعَامِ الصِّحِّيِّ",
                            "اقْتِنَاءُ سَاعَةٍ يَدَوِيَّةٍ فَاخِرَةٍ"
                        ],
                        "options_en": [
                            "Buying a new smartphone",
                            "Having clean water and healthy food",
                            "Acquiring an expensive luxury watch"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "أحسنت! الماء والغذاء من الحاجات الأساسية التي لا يمكن للإنسان العيش بدونها.",
                        "explanation_en": "Well done! Clean water and food are essential needs that human life cannot survive without."
                    }
                },
                {
                    "section_id": "sec_g6_02_sentence_styles",
                    "title_ar": "٢. الأسلوب الخبري والأسلوب الإنشائي الطلبي",
                    "title_en": "2. Declarative vs. Interrogative/Creative Sentence Styles",
                    "content_ar": "يَنْقَسِمُ الكَلَامُ فِي اللُّغَةِ العَرَبِيَّةِ إِلَى قِسْمَيْنِ رَئِيسَيْنِ:\n١. الأُسْلُوبُ الخَبَرِيُّ: هُوَ كَلَامٌ يُخْبِرُ عَنْ حَقِيقَةٍ أَوْ وَاقِعَةٍ وَيَحْتَمِلُ الصِّدْقَ أَوِ الكَذِبَ، مِثْلَ: (إِنَّ الأَلْعَابَ الإِلِكْتُرُونِيَّةَ مِنَ الرَّغَبَاتِ)، (زِيَادَةُ الرَّغَبَاتِ تُؤَثِّرُ عَلَى البِيئَةِ).\n٢. الأُسْلُوبُ الإِنْشَائِيُّ: كَلَامٌ لَا يَحْتَمِلُ الصِّدْقَ وَالكَذِبَ لِأَنَّهُ يَنْشَأُ وَقْتَ التَّكَلُّمِ، وَمِنْهُ الطَّلَبِيُّ كَالاسْتِفْهَامِ (هَلْ تَعْلَمُ أَنَّ المَاءَ ضَرُورِيٌّ؟)، وَالنِّدَاءِ وَالنَّهْيِ (يَا آدَمُ، لَا تُسْرِفْ فِي الشِّرَاءِ).",
                    "content_en": "Arabic discourse is categorized into two foundational structures:\n1. Declarative Style (الأسلوب الخبري): Expresses a factual proposition or state of affairs that can logically be verified as true or false, such as: 'Video games are desires' or 'Increasing wants affects the environment'.\n2. Creative/Interrogative Style (الأسلوب الإنشائي): Expresses a demand or performative utterance that cannot be judged as true or false, such as Questions/Inquiry (Did you know water is necessary?), Vocative calling, and Prohibition (O Adam, do not spend lavishly!).",
                    "key_takeaways_ar": [
                        "الأسلوب الخبري: يحتمل الصدق أو الكذب (يخبر عن واقعة).",
                        "الأسلوب الإنشائي الطلبي: استفهام (هل/كيف؟)، نداء (يا)، نهي (لا تفعل)، أمر (افعل)."
                    ],
                    "key_takeaways_en": [
                        "Declarative Style: Can be logically verified as true or false.",
                        "Creative Request Style: Inquiries, vocative calls, prohibitions, and commands."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا نَوْعُ الأُسْلُوبِ فِي جُمْلَةِ: (كَيْفَ تُقَسِّمُ مَصْرُوفَكَ الشَّهْرِيَّ؟)؟",
                        "question_en": "What is the style of sentence: 'How do you divide your monthly allowance?'",
                        "options": [
                            "أُسْلُوبٌ خَبَرِيٌّ",
                            "أُسْلُوبٌ إِنْشَائِيٌّ (طَلَبِيٌّ: اسْتِفْهَامٌ)",
                            "أُسْلُوبُ تَعَجُّبٍ"
                        ],
                        "options_en": [
                            "Declarative style",
                            "Creative style (Question/Inquiry)",
                            "Exclamatory style"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "إجابة صحيحة! الجملة بدأت باسم استفهام (كَيْفَ) وانتهت بعلامة استفهام، فهي أسلوب إنشائي طلبي.",
                        "explanation_en": "Correct! The sentence begins with the interrogative particle 'Kayfa' (How) requesting information, which is Creative/Interrogative."
                    }
                },
                {
                    "section_id": "sec_g6_03_vocabulary",
                    "title_ar": "٣. قاموس المفردات وتراث بيت الحكمة في بغداد",
                    "title_en": "3. Vocabulary Glossary & The House of Wisdom",
                    "content_ar": "يَحْتَوِي كِتَابُ الصَّفِّ السَّادِسِ عَلَى مُفْرَدَاتٍ مِحْوَرِيَّةٍ:\n- الضَّرُورِيُّ: اللَّازِمُ الَّذِي لَا بُدَّ مِنْهُ (Essential).\n- البَقَاءُ: الاسْتِمْرَارُ فِي الحَيَاةِ وَالعَيْشِ (Survival).\n- الرَّغْبَةُ: إِرَادَةُ الحُصُولِ عَلَى الشَّيْءِ مَعَ إِمْكَانِيَّةِ الاسْتِغْنَاءِ عَنْهُ (Desire / Want).\n- بَيْتُ الحِكْمَةِ: مَرْكَزٌ عِلْمِيٌّ وَتَرْجَمِيٌّ تَارِيخِيٌّ عَظِيمٌ فِي بَغْدَادَ جَمَعَ عُلَمَاءَ العَالَمِ (House of Wisdom).",
                    "content_en": "Grade 6 Unit 1 covers essential foundational vocabulary:\n- Essential (الضروري): Indispensable and mandatory for life.\n- Survival (البقاء): Continuing to live and endure.\n- Desire (الرغبة): Wanting something that is not strictly necessary.\n- House of Wisdom (بيت الحكمة): The historic intellectual academy in Baghdad that spearheaded world translation and science.",
                    "key_takeaways_ar": [
                        "الضروري: ما لا يمكن الاستغناء عنه.",
                        "بيت الحكمة: رمز الحضارة الإسلامية في الترجمة والعلوم."
                    ],
                    "key_takeaways_en": [
                        "Essential: That which cannot be dispensed with.",
                        "House of Wisdom: Beacon of Islamic civilization in translation and science."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا المَعْنَى المَقْصُودُ بِكَلِمَةِ (البَقَاءِ) فِي سِيَاقِ النَّصِّ؟",
                        "question_en": "What is the intended meaning of 'Survival' (البقاء) in the text context?",
                        "options": [
                            "الرُّكُودُ وَالنَّوْمُ",
                            "الاسْتِمْرَارُ فِي العَيْشِ وَالحَيَاةِ",
                            "السَّفَرُ إِلَى مَكَانٍ بَعِيدٍ"
                        ],
                        "options_en": [
                            "Stagnation and sleep",
                            "Continuing to live and endure",
                            "Traveling far away"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "ممتاز! البقاء يعني دوام العيش والحفاظ على سلامة الحياة واستمرارها.",
                        "explanation_en": "Excellent! 'Al-Baqaa' means survival and sustaining life."
                    }
                }
            ]
        },

        # -------------------------------------------------------------
        # MODE 2: QUICK REVIEW MODE (وضع الملاحظات ومراجعة الـ 15 دقيقة)
        # -------------------------------------------------------------
        "quick_review_mode": {
            "mode_title_ar": "وضع الملاحظات المركزة ومراجعة الـ 15 دقيقة (الصف السادس)",
            "mode_title_en": "15-Minute Exam Revision & Golden Rules (Grade 6)",
            "estimated_minutes": 15,
            "high_yield_summary": [
                {
                    "bullet_ar": "الحاجات ضرورية للبقاء (ماء، طعام، دواء)، والرغبات تحسينية وترفيهية (ألعاب، سفر، ساعات فاخرة).",
                    "bullet_en": "Needs are vital for survival (water, food, medicine); desires are luxury and fun (games, travel, watches)."
                },
                {
                    "bullet_ar": "الأسلوب الخبري يخبر عن أمر يحتمل الصدق والكذب لذاته، مثل: (العلم نور)، (الألعاب من الرغبات).",
                    "bullet_en": "Declarative style states verifiable propositions: 'Knowledge is light', 'Games are wants'."
                },
                {
                    "bullet_ar": "الأسلوب الإنشائي الطلبي يشمل الاستفهام (هل، كيف)، والنداء (يا)، والنهي (لا تسرف).",
                    "bullet_en": "Creative/Interrogative style encompasses Questions (Hal, Kayfa), Calling (Yaa), and Prohibitions (Laa)."
                }
            ],
            "essential_formulas": [
                {
                    "title_ar": "الأسلوب الخبري",
                    "title_en": "The Declarative Sentence",
                    "formula_ar": "جملة تخبر عن واقعة (تحتمل الصدق أو الكذب)",
                    "formula_en": "Informative sentence stating a proposition (Verifiable as true/false)",
                    "example_ar": "زِيَادَةُ الرَّغَبَاتِ تُؤَثِّرُ عَلَى مِيزَانِيَّةِ الأُسْرَةِ.",
                    "example_en": "Increasing wants strains the family budget."
                },
                {
                    "title_ar": "الأسلوب الإنشائي الطلبي: الاستفهام",
                    "title_en": "Interrogative Request Style",
                    "formula_ar": "أداة استفهام + جملة طلبية + علامة استفهام (؟)",
                    "formula_en": "Question particle + Sentence + Question mark (?)",
                    "example_ar": "هَلْ تَعْلَمُ أَنَّ تَرْشِيدَ المَالِ حِكْمَةٌ؟",
                    "example_en": "Did you know that budgeting money is wisdom?"
                },
                {
                    "title_ar": "الأسلوب الإنشائي الطلبي: النداء والنهي",
                    "title_en": "Vocative & Prohibition Style",
                    "formula_ar": "حرف نداء (يا) + لا الناهية + فعل مضارع مجزوم",
                    "formula_en": "Calling particle (Yaa) + Prohibitive (Laa) + Jussive verb",
                    "example_ar": "يَا صَدِيقِي، لَا تُنْفِقْ مَالَكَ فِيمَا لَا يَنْفَعُ.",
                    "example_en": "O my friend, do not spend your money on what does not benefit you."
                }
            ],
            "exam_pitfall_warnings": [
                {
                    "warning_ar": "احذر: لا تخلط بين الأسلوب الخبري والإنشائي في الامتحان؛ إذا وجدت علامة (؟) فالأسلوب إنشائي طلبي (استفهام).",
                    "warning_en": "Caution: Do not confuse declarative with interrogative; if you see (؟), it is Creative Request (Question)."
                },
                {
                    "warning_ar": "تأكيد الجملة بـ (إِنَّ) مثل: (إِنَّ المَاءَ ضَرُورِيٌّ) يُبقيها أسلوباً خبرياً مؤكداً ولا يحولها إلى إنشائي.",
                    "warning_en": "Emphasis with 'Inna' keeps the sentence Declarative (Affirmed) and does NOT make it Creative/Inquiry."
                },
                {
                    "warning_ar": "التمييز بين الحاجة والرغبة يعتمد على شرط البقاء: إذا توقفت الحياة بدونه فهو حاجة، وإلا فهو رغبة.",
                    "warning_en": "Classifying Need vs. Desire relies on survival: if life cannot endure without it, it is a Need; otherwise a Desire."
                }
            ]
        }
    },
    "lesson_g7_t1_ch01": {
        "lesson_id": "lesson_g7_t1_ch01",
        "title_ar": "ملزمة كَيْفَ قَضَيْتُ إِجَازَتِي؟ وَأَدَوَاتُ الجَزْمِ وَقَامُوسِيَ الخَاصُّ — الوحدة الأولى",
        "title_en": "How I Spent My Vacation, Jazam Particles & Vocabulary Smart Booklet — Grade 7 Unit 1",
        "grade": 7,
        "term": 1,
        "pages_reference": "Pages 6–16 (CBSE Curriculum Student Book Grade 7)",
        "curriculum_alignment": "UAE Ministry of Education & CBSE Arabic Grade 7",

        # -------------------------------------------------------------
        # MODE 1: STUDY MODE (وضع المذاكرة الشامل مع التمارين التفاعلية)
        # -------------------------------------------------------------
        "study_mode": {
            "mode_title_ar": "وضع المذاكرة التفاعلية الشاملة (الصف السابع)",
            "mode_title_en": "Comprehensive Interactive Study Mode (Grade 7)",
            "estimated_minutes": 25,
            "sections": [
                {
                    "section_id": "sec_g7_01_vacation_text",
                    "title_ar": "١. نص القراءة: كَيْفَ قَضَيْتُ إِجَازَتِي؟ وَمَعَالِمُ الإِمَارَاتِ",
                    "title_en": "1. Reading Passage: How I Spent My Vacation & UAE Landmarks",
                    "content_ar": "تَنَاوَلَ الدَّرْسُ الأَوَّلُ حِوَارًا شَيِّقًا بَيْنَ الأَصْدِقَاءِ حَوْلَ قَضَاءِ الإِجَازَةِ الصَّيْفِيَّةِ فِي دَوْلَةِ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ. زَارَ الطُّلَّابُ مَعَالِمَ سِيَاحِيَّةً بَارِزَةً مِثْلَ: بُرْجِ خَلِيفَةَ فِي دُبَي، وَالمُرْتَفَعَاتِ وَالجِبَالِ فِي رَأْسِ الخَيْمَةِ وَالعَيْنِ، وَالشَّوَاطِئِ البَحْرِيَّةِ. يُعَلِّمُنَا النَّصُّ كَيْفِيَّةَ التَّعْبِيرِ عَنِ التَّجَارِبِ الشَّخْصِيَّةِ وَالِاسْتِمْتَاعِ بِالوَقْتِ وَتَجْدِيدِ النَّشَاطِ.",
                    "content_en": "The first lesson presents an engaging dialogue among peers recounting their summer vacation across the United Arab Emirates. Students toured prominent landmarks including Burj Khalifa in Dubai, mountain heights in Ras Al Khaimah and Al Ain, and coastal marine beaches. The lesson instructs how to narrate personal experiences, cherish downtime, and revitalize energy.",
                    "key_takeaways_ar": [
                        "مفهوم الإجازة: فرصة للاستجمام والراحة واكتشاف المعالم والأنشطة الجديدة.",
                        "معالم بارزة: برج خليفة، المرتفعات الجبلية، والشواطئ البحرية في دولة الإمارات."
                    ],
                    "key_takeaways_en": [
                        "Vacation Concept: An opportunity for relaxation, leisure, and exploring new landmarks.",
                        "Key UAE Landmarks: Burj Khalifa, elevated mountain ranges, and marine beaches."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا المَعْلَمُ العَالَمِيُّ الشَّهِيرُ الَّذِي وَرَدَ فِي نَصِّ الإِجَازَةِ فِي إِمَارَةِ دُبَي؟",
                        "question_en": "Which world-famous landmark in Dubai was featured in the vacation passage?",
                        "options": [
                            "بُرْجُ إِيفِل",
                            "بُرْجُ خَلِيفَة",
                            "سُورُ الصِّينِ العَظِيم"
                        ],
                        "options_en": [
                            "Eiffel Tower",
                            "Burj Khalifa",
                            "Great Wall of China"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "أحسنت! برج خليفة هو أطول ناطحة سحاب في العالم وهو المعلم الأبرز المذكور في النص.",
                        "explanation_en": "Well done! Burj Khalifa is the tallest skyscraper in the world and the highlight landmark named in the lesson."
                    }
                },
                {
                    "section_id": "sec_g7_02_jazam_particles",
                    "title_ar": "٢. التراكيب اللغوية: أَدَوَاتُ الجَزْمِ (لَمْ، لَا النَّاهِيَةُ، لَامُ الأَمْرِ)",
                    "title_en": "2. Grammar: Jazam Particles (Lam, Prohibitive Laa, Imperative Laam)",
                    "content_ar": "أَدَوَاتُ جَزْمِ الفِعْلِ المُضَارِعِ تَدْخُلُ عَلَى الفِعْلِ المُضَارِعِ فَتُغَيِّرُ حَرَكَتَهُ مِنَ الضَّمَّةِ إِلَى السُّكُونِ (إِذَا كَانَ صَحِيحَ الآخِرِ):\n١. (لَمْ): حَرْفُ نَفْيٍ وَجَزْمٍ وَقَلْبٍ، يَنْفِي حُدُوثَ الفِعْلِ فِي المَاضِي، مِثْلَ: (لَمْ أُسَافِرْ خَارِجَ الدَّوْلَةِ).\n٢. (لَا النَّاهِيَةُ): تُفِيدُ طَلَبَ الكَفِّ عَنِ الفِعْلِ وَالنَّهْيَ عَنْهُ، مِثْلَ: (لَا تُهْمِلْ مُرَاجَعَةَ دُرُوسِكَ).\n٣. (لَامُ الأَمْرِ): تُفِيدُ طَلَبَ إِحْدَاثِ الفِعْلِ، مِثْلَ: (لِتَكْتُبْ تَقْرِيرَ رِحْلَتِكَ).",
                    "content_en": "Jazam particles enter upon the present tense verb and govern it with a Sukun (for regular sound-ending verbs):\n1. 'Lam' (لَمْ): Negative particle of jazam and past inversion (e.g. 'Lam usaafir kharija ad-dawlah' - I did not travel abroad).\n2. Prohibitive 'Laa' (لَا النَّاهِيَةُ): Directs prohibition and restraining from an action (e.g. 'Laa tuhmil duroosaka' - Do not neglect your studies).\n3. Imperative 'Laam' (لَامُ الأَمْرِ): Commands action execution (e.g. 'Li-taktub taqreera rihlatika' - Write your trip report).",
                    "key_takeaways_ar": [
                        "أدوات الجزم الثلاث: لَمْ (للنفي)، لَا النَّاهِيَةُ (للنهي)، لَامُ الأَمْرِ (للطلب والأمر).",
                        "العلامة الإعرابية: السكون الظاهر على آخر الفعل المضارع صحيح الآخر."
                    ],
                    "key_takeaways_en": [
                        "Three Jazam Particles: Lam (negation), Prohibitive Laa (prohibition), Imperative Laam (command).",
                        "Grammatical Mark: Visible Sukun on the last letter of regular sound verbs."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا الضَّبْطُ الصَّحِيحُ لِلْفِعْلِ (يَذْهَب) بَعْدَ دُخُولِ أَدَاةِ الجَزْمِ: (لَمْ يَذْهَبْ....)؟",
                        "question_en": "What is the correct vocalization of 'Yadh-hab' following the Jazam particle: (Lam yadh-hab....)?",
                        "options": [
                            "لَمْ يَذْهَبُ (بالضمة)",
                            "لَمْ يَذْهَبَ (بالفتحة)",
                            "لَمْ يَذْهَبْ (بالسكون)"
                        ],
                        "options_en": [
                            "Lam yadh-habu (with Dammah)",
                            "Lam yadh-haba (with Fathah)",
                            "Lam yadh-hab' (with Sukun)"
                        ],
                        "correct_index": 2,
                        "explanation_ar": "صحيح تماماً! أداة الجزم (لَمْ) تجزم الفعل المضارع بالسكون الظاهر على آخره.",
                        "explanation_en": "Spot on! The Jazam particle 'Lam' governs the present tense verb with a clear Sukun."
                    }
                },
                {
                    "section_id": "sec_g7_03_vacation_glossary",
                    "title_ar": "٣. قَامُوسِيَ الخَاصُّ: مُعْجَمُ الإِجَازَةِ وَالمُرْتَفَعَاتِ",
                    "title_en": "3. Special Glossary: Vacation & Geography Lexicon",
                    "content_ar": "يَشْمَلُ مِنْهَاجُ الصَّفِّ السَّابِعِ مُفْرَدَاتِ الإِجَازَةِ وَالجُغْرَافِيَا:\n- البَارِحَةُ: الأَمْسُ، أَيْ اليَوْمُ المُنْقَضِي قَبْلَ اليَوْمِ الحَالِيِّ (Yesterday).\n- الرَّاحَةُ: الِاسْتِرْخَاءُ وَالهُدُوءُ لِتَجْدِيدِ الطَّاقَةِ (Rest & Relaxation).\n- المُرْتَفَعَاتُ: الأَمَاكِنُ العَالِيَةُ كَالجِبَالِ وَالتِّلَالِ (Highlands / Elevations).\n- القِمَمُ: جَمْعُ قِمَّةٍ، وَهِيَ أَعْلَى نُقْطَةٍ فِي الجَبَلِ (Peaks / Summits).\n- عَصْرًا: وَقْتُ العَصْرِ قُبَيْلَ غُرُوبِ الشَّمْسِ (In the Afternoon).\n- السَّلَاحِفُ: كَائِنَاتٌ زَاحِفَةٌ تَمْتَلِكُ دِرْعًا صُلْبًا (Turtles).",
                    "content_en": "Grade 7 Unit 1 vocabulary introduces descriptive vacation and environmental terms:\n- Yesterday (البارحة): The day preceding today.\n- Rest (الراحة): Tranquility and relaxation renewing vigor.\n- Highlands (المرتفعات): Mountainous elevated terrains.\n- Summits (القمم): Plural of peak, highest mountain apex.\n- In the Afternoon (عصراً): Late afternoon before dusk.\n- Turtles (السلاحف): Reptilian creatures with protective shells.",
                    "key_takeaways_ar": [
                        "البارحة: تعني اليوم السابق (الأمس).",
                        "المرتفعات والقمم: تعبيرات جغرافية تصف الجبال والمناطق العالية."
                    ],
                    "key_takeaways_en": [
                        "Al-Baarihah: Specifically denotes yesterday.",
                        "Highlands & Summits: Geographical vocabulary describing peaks and elevated mountains."
                    ],
                    "inline_exercise": {
                        "question_ar": "مَا مَعْنَى كَلِمَةِ (البَارِحَة) الوَارِدَةِ فِي مُعْجَمِ الدَّرْسِ؟",
                        "question_en": "What is the meaning of the word 'Al-Baarihah' featured in the lesson glossary?",
                        "options": [
                            "الغَدُ المُقْبِلُ",
                            "الأَمْسُ المُنْقَضِي",
                            "الأُسْبُوعُ القَادِمُ"
                        ],
                        "options_en": [
                            "Tomorrow",
                            "Yesterday (the past day)",
                            "Next week"
                        ],
                        "correct_index": 1,
                        "explanation_ar": "ممتاز! (البارحة) في لسان العرب تعني أقرب ليلة أو يوم مضى قبل يومك الحالي (أي الأمس).",
                        "explanation_en": "Excellent! 'Al-Baarihah' strictly denotes yesterday / the immediately preceding day."
                    }
                }
            ]
        },

        # -------------------------------------------------------------
        # MODE 2: QUICK REVIEW MODE (وضع الملاحظات ومراجعة الـ 15 دقيقة)
        # -------------------------------------------------------------
        "quick_review_mode": {
            "mode_title_ar": "وضع الملاحظات المركزة ومراجعة الـ 15 دقيقة (الصف السابع)",
            "mode_title_en": "15-Minute Exam Revision & Golden Rules (Grade 7)",
            "estimated_minutes": 15,
            "high_yield_summary": [
                {
                    "bullet_ar": "أدوات جزم الفعل المضارع المقررة في الوحدة الأولى هي: (لَمْ، لَا النَّاهِيَةُ، لَامُ الأَمْرِ).",
                    "bullet_en": "The core Jazam particles for Grade 7 Unit 1 are: Lam, Prohibitive Laa, and Imperative Laam."
                },
                {
                    "bullet_ar": "علامة جزم الفعل المضارع صحيح الآخر هي السكون الظاهر: (لَمْ يَكْتُبْ، لَا تَتَأَخَّرْ، لِتَقْرَأْ).",
                    "bullet_en": "The grammatical mark of jazam on sound verbs is the visible Sukun."
                },
                {
                    "bullet_ar": "الفرق بين (لا الناهية) و(لا النافية): لا الناهية تفيد طلب الامتناع وتجزم بالسكون، بينما لا النافية تخبر فقط ويبقى الفعل بعدها مرفوعاً بالضمة.",
                    "bullet_en": "Key distinction: Prohibitive Laa commands cessation and governs Sukun, while Negative Laa merely informs leaving the verb in the nominative Dammah."
                }
            ],
            "essential_formulas": [
                {
                    "title_ar": "معادلة أداة الجزم (لَمْ)",
                    "title_en": "Formula for 'Lam' (Negation & Jazam)",
                    "formula_ar": "لَمْ + فِعْلٌ مُضَارِعٌ صَحِيحُ الآخِرِ = فِعْلٌ مَجْزُومٌ بِالسُّكُونِ",
                    "formula_en": "Lam + sound present verb = Jazam governed with Sukun",
                    "example_ar": "لَمْ يُهْمِلْ زَايِدٌ رِحْلَتَهُ التَّعْلِيمِيَّةَ.",
                    "example_en": "Zayed did not neglect his educational trip."
                },
                {
                    "title_ar": "معادلة (لَا النَّاهِيَةُ)",
                    "title_en": "Formula for Prohibitive 'Laa'",
                    "formula_ar": "لَا النَّاهِيَةُ + فِعْلٌ مُضَارِعٌ = نَهْيٌ وَجَزْمٌ بِالسُّكُونِ",
                    "formula_en": "Prohibitive Laa + present verb = Prohibition and Sukun",
                    "example_ar": "يَا صَدِيقِي، لَا تَخَفْ مِنَ صُعُودِ المُرْتَفَعَاتِ.",
                    "example_en": "My friend, do not fear climbing the highlands."
                },
                {
                    "title_ar": "معادلة (لَامُ الأَمْرِ)",
                    "title_en": "Formula for Imperative 'Laam'",
                    "formula_ar": "لِـ (مَكْسُورَةٌ) + فِعْلٌ مُضَارِعٌ = أَمْرٌ وَجَزْمٌ بِالسُّكُونِ",
                    "formula_en": "Imperative Li- + present verb = Command and Sukun",
                    "example_ar": "لِتَسْتَمْتِعْ بِإِجَازَتِكَ فِي رُبُوعِ الوَطَنِ.",
                    "example_en": "Enjoy your vacation across the homeland."
                }
            ],
            "exam_pitfall_warnings": [
                {
                    "warning_ar": "فخ الامتحان الشائع: الخلط بين (لا الناهية) مثل: (لا تَلْعَبْ في الشارع - جازمة) و(لا النافية) مثل: (سالمٌ لا يَلْعَبُ في الشارع - غير جازمة).",
                    "warning_en": "Common Exam Trap: Confusing Prohibitive Laa (demands stopping -> Sukun) with Informative Negative Laa (states a fact -> Dammah remains)."
                },
                {
                    "warning_ar": "تأكد من وضع السكون فوق الحرف الأخير للفعل بعد أدوات الجزم عند الضبط بالشكل في الاختبار الوزاري.",
                    "warning_en": "Ensure placing the Sukun diacritic distinctly above the terminal consonant in CBSE Curriculum exam vocalization questions."
                }
            ]
        }
    }
}

# Aliases for fast grade-based resolution
MALAZIM_DATA["grade_7"] = MALAZIM_DATA["lesson_g7_t1_ch01"]
MALAZIM_DATA["grade7"] = MALAZIM_DATA["lesson_g7_t1_ch01"]
MALAZIM_DATA["g7"] = MALAZIM_DATA["lesson_g7_t1_ch01"]
MALAZIM_DATA["7"] = MALAZIM_DATA["lesson_g7_t1_ch01"]

MALAZIM_DATA["grade_6"] = MALAZIM_DATA["lesson_g6_t1_ch01"]
MALAZIM_DATA["grade6"] = MALAZIM_DATA["lesson_g6_t1_ch01"]
MALAZIM_DATA["g6"] = MALAZIM_DATA["lesson_g6_t1_ch01"]
MALAZIM_DATA["6"] = MALAZIM_DATA["lesson_g6_t1_ch01"]

MALAZIM_DATA["grade_5"] = MALAZIM_DATA["lesson_01_ball_games"]
MALAZIM_DATA["grade5"] = MALAZIM_DATA["lesson_01_ball_games"]
MALAZIM_DATA["g5"] = MALAZIM_DATA["lesson_01_ball_games"]
MALAZIM_DATA["5"] = MALAZIM_DATA["lesson_01_ball_games"]


def get_malazim_booklet(lesson_id: str = "lesson_01_ball_games") -> Dict[str, Any]:
    """Retrieve study booklet data by lesson identifier or grade alias."""
    if not lesson_id:
        return MALAZIM_DATA.get("lesson_01_ball_games")

    lid = str(lesson_id).strip().lower()
    if lid in MALAZIM_DATA:
        return MALAZIM_DATA[lid]

    # Resolve structured ids (lesson_g8_t1_ch01) and grade aliases (grade_8) for
    # grades/chapters without a hand-authored booklet. Previously any id that did
    # not contain "5"/"6"/"7" silently fell back to the Grade 5 booklet.
    from backend.generated_study_content import parse_lesson_reference, generate_booklet
    ref = parse_lesson_reference(lid)
    if ref is not None:
        grade, term, order = ref
        authored = MALAZIM_DATA.get(f"lesson_g{grade}_t{term}_ch{order:02d}")
        if authored is not None:
            return authored
        generated = generate_booklet(grade, term, order)
        if generated is not None:
            return generated

    # Default to requested or fallback to Grade 5
    return MALAZIM_DATA.get(lesson_id) or MALAZIM_DATA.get("lesson_01_ball_games")


def get_malazim_by_grade(grade: int = 5) -> Dict[str, Any]:
    """Retrieve study booklet data for a specific grade."""
    if grade == 7:
        return MALAZIM_DATA["lesson_g7_t1_ch01"]
    if grade == 6:
        return MALAZIM_DATA["lesson_g6_t1_ch01"]
    if grade == 5:
        return MALAZIM_DATA["lesson_01_ball_games"]
    return get_malazim_booklet(f"grade_{grade}")
