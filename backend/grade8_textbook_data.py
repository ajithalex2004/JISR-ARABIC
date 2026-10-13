"""
Official UAE Ministry of Education (MoE) Grade 8 Arabic Textbook Dataset
Edition: moe_gr8_vol1_2023 (العربية تجمعنا - الصف الثامن - الجزء الأول)
Covers Chapter 1 / Unit 1: Coexistence & Tolerance (التعايش والتسامح)
Pages 6 to 16 with verified Arabic texts, precise English translations, and model answers.
"""
from typing import Dict, Any

GRADE_8_TEXTBOOK_PAGES_DATA: Dict[Any, Dict[str, Any]] = {
    "6": {
        "printed_page": 6,
        "unit": "التَّعَايُشُ وَالتَّسَامُحُ (Coexistence & Tolerance)",
        "lesson": "مُقَدِّمَةُ المِنْهَاجِ: لَا لِلتَّنَمُّرِ (Curriculum Intro: No to Bullying)",
        "title_ar": "لَا لِلتَّنَمُّرِ",
        "title_en": "No to Bullying",
        "paragraphs": [
            "كَشَفَتْ إِحْصَائِيَّاتٌ حَدِيثَةٌ (لِلْيُونِسْكُو) أَنَّ رُبْعَ مِلْيَارِ طِفْلٍ يَتَعَرَّضُونَ لِلتَّنَمُّرِ فِي المَدَارِسِ مِنْ إِجْمَالِي مِلْيَارِ طِفْلٍ يَدْرُسُونَ حَوْلَ العَالَمِ.",
            "وَأُجْرِيَتِ الدِّرَاسَةُ عَلَى 19 دَوْلَةً، وَأَسْفَرَتْ نَتَائِجُهَا عَنْ نِسَبٍ مُذْهِلَةٍ، مِنْهَا أَنَّ 34% مِنَ الطُّلَّابِ تَعَرَّضُوا لِلتَّنَمُّرِ الجَسَدِيِّ أَوْ اللَّفْظِيِّ.",
            "تَدْعُو دَوْلَةُ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ إِلَى تَرْسِيخِ الأَمْنِ وَالأَمَانِ فِي المَدَارِسِ وَخَلْقِ بِيئَةٍ تَعْلِيمِيَّةٍ إِيجَابِيَّةٍ خَالِيَةٍ مِنَ التَّنَمُّرِ."
        ],
        "paragraphs_en": [
            "Recent UNESCO statistics revealed that a quarter of a billion children experience bullying in schools out of one billion students worldwide.",
            "The study was conducted across 19 countries, yielding striking results showing that 34% of students were subjected to physical or verbal bullying.",
            "The United Arab Emirates promotes security and safety in schools, creating a positive educational environment free from bullying."
        ],
        "model_answers": {
            "0": {
                "text_ar": "التنمر سلوك عدواني غير مقبول يضر بالصحة النفسية والجسدية للأطفال في المدارس.",
                "arabzi": "al-tanamur sulook 'udwaani ghayr maqbool yadurr bil-sihha al-nafsiyya.",
                "text_en": "Bullying is unacceptable aggressive behavior that harms children's mental and physical health in schools.",
                "explanation_en": "Core awareness message promoting empathetic school culture."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "7": {
        "printed_page": 7,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "نَوَاتِجُ التَّعَلُّمِ وَقَامُوسِي الخَاصُّ (Learning Outcomes & Lexicon)",
        "title_ar": "نَوَاتِجُ التَّعَلُّمِ وَقَامُوسِي الخَاصُّ - عَامُ التَّسَامُحِ",
        "title_en": "Learning Outcomes & Lexicon - Year of Tolerance",
        "paragraphs": [
            "1. يَسْتَمِعُ وَيَفْهَمُ المَعْنَى الكُلِّيَّ لِنُصُوصٍ مُوَسَّعَةٍ فِي مَوْضُوعَاتٍ وَصْفِيَّةٍ وَفِكْرِيَّةٍ.",
            "2. يَسْتَمِعُ وَيُحَدِّدُ النِّقَاطَ الرَّئِيسَةَ وَالمَعْلُومَاتِ المُحَدَّدَةَ فِي نُصُوصٍ مُوَسَّعَةٍ.",
            "3. يُنْتِجُ حَدِيثًا مُتَرَابِطًا مُسْتَخْدِمًا التَّنْغِيمَ وَالإِيقَاعَ الصَّحِيحَيْنِ فِي الحِوَارِ.",
            "4. يَقْرَأُ وَيَفْهَمُ المَعْنَى الكُلِّيَّ وَيُحَدِّدُ النِّقَاطَ الرَّئِيسَةَ لِنُصُوصٍ مُوَسَّعَةٍ.",
            "5. يَحْتَفِظُ بِدَرَجَةٍ مِنَ الضَّبْطِ لِتَرَاكِيبِ اللُّغَةِ البَسِيطَةِ وَالمُرَكَّبَةِ فِي الكِتَابَةِ.",
            "قَامُوسِي الخَاصُّ: التَّسَامُحُ: قَبُولُ الآخَرِ وَاحْتِرَامُ الاختِلَافِ. الأَمَانُ: الطُّمَأْنِينَةُ وَالسَّلَامُ. التَّعَايُشُ: العَيْشُ بِمَحَبَّةٍ وَتَعَاوُنٍ بَيْنَ مُخْتَلَفِ الثَّقَافَاتِ."
        ],
        "paragraphs_en": [
            "1. Listens to and comprehends the overarching meaning of extended texts on descriptive and intellectual topics.",
            "2. Listens and identifies core points and specific detailed facts in extended discourse.",
            "3. Produces coherent spoken speech applying appropriate vocal intonation and rhythm in dialogue.",
            "4. Reads, grasps overall themes, and determines key points in extended passages.",
            "5. Maintains accuracy in using simple and compound grammatical structures in writing.",
            "My Lexicon: Tolerance: Accepting others and respecting differences. Safety: Peace and tranquility. Coexistence: Living in harmony and cooperation across cultures."
        ],
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "8": {
        "printed_page": 8,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَسْتَمِعُ: عَامُ التَّسَامُحِ (Listening: Year of Tolerance)",
        "title_ar": "أَسْتَمِعُ: عَامُ التَّسَامُحِ",
        "title_en": "Listening: Year of Tolerance",
        "paragraphs": [
            "قَبْلَ الِاسْتِمَاعِ: 1. أَتَوَفَّعُ الأَفْكَارَ الَّتِي سَيَطْرَحُهَا النَّصُّ المَسْمُوعُ.",
            "2. أُنَاقِشُ مُعَلِّمِي وَالزُّمَلَاءَ فِي مَعْنَى التَّسَامُحِ بِالنِّسْبَةِ لِي.",
            "أَثْنَاءَ الِاسْتِمَاعِ: أُنْصِتُ جَيِّدًا لِلْمَادَّةِ المَطْرُوحَةِ، وَأُسَجِّلُ المَلْحُوظَاتِ: الأَفْكَارَ الرَّئِيسَةَ وَالفَرْعِيَّةَ، المُفْرَدَاتِ الجَدِيدَةَ، أَهْدَافَ عَامِ التَّسَامُحِ فِي دَوْلَةِ الإِمَارَاتِ.",
            "بَعْدَ الِاسْتِمَاعِ - سُؤَالٌ 1: مَا الفِكْرَةُ الرَّئِيسَةُ الَّتِي يَطْرَحُهَا النَّصُّ؟",
            "سُؤَالٌ 2: مَتَى انْطَلَقَ عَامُ التَّسَامُحِ فِي الإِمَارَاتِ؟ وَمَنْ أَطْلَقَهُ؟ وَمَا أَهْدَافُهُ؟",
            "سُؤَالٌ 3: كَيْفَ حَقَّقَتِ الإِمَارَاتُ التَّسَامُحَ بَيْنَ سُكَّانِهَا؟ أُنَاقِشُ الإِجَابَةَ مَعَ مُعَلِّمِي وَزُمَلَائِي مُدَعِّمًا ذَلِكَ بِالأَمْثِلَةِ الوَاقِعِيَّةِ.",
            "سُؤَالٌ 4: أَكْتُبُ تَحْتَ كُلِّ صُورَةٍ مَا يُنَاسِبُهَا: (عَامُ الخَيْرِ 2017 - عَامُ التَّسَامُحِ 2019 - عَامُ زَايِد 2018 - عَامُ القِرَاءَةِ 2016).",
            "سُؤَالٌ 5: أُسَجِّلُ المُفْرَدَاتِ الجَدِيدَةَ فِي الفَرَاغَاتِ، وَأَبْحَثُ عَنْ مَعَانِيهَا فِي المُعْجَمِ."
        ],
        "paragraphs_en": [
            "Before Listening: 1. I predict the main themes and ideas that the audio text will address.",
            "2. I discuss with my teacher and peers what tolerance means to me personally.",
            "During Listening: I listen attentively to the presented recording and take notes on main and supporting ideas, new vocabulary, and the objectives of the Year of Tolerance in the UAE.",
            "Post-Listening - Question 1: What is the main central idea presented by the text?",
            "Question 2: When was the Year of Tolerance launched in the UAE? Who launched it, and what were its objectives?",
            "Question 3: How did the UAE achieve tolerance among its multicultural residents? Discuss your answer with teacher and peers supported by real-life examples.",
            "Question 4: Write the appropriate initiative under each commemorative logo: (Year of Giving 2017 - Year of Tolerance 2019 - Year of Zayed 2018 - Year of Reading 2016).",
            "Question 5: Record newly acquired vocabulary words in the blanks and search for their meanings in the dictionary."
        ],
        "model_answers": {
            "3": {
                "text_ar": "الفِكْرَةُ الرَّئِيسَةُ هِيَ إِبْرَازُ دَوْرِ دَوْلَةِ الإِمَارَاتِ كَعَاصِمَةٍ عَالَمِيَّةٍ لِلتَّسَامُحِ وَالتَّعَايُشِ السِّلْمِيِّ بَيْنَ الشُّعُوبِ.",
                "arabzi": "al-fikra al-ra'eesa hiya ibraaz dawr dawlat al-imaraat ka-'aasima 'aalamiyya lil-tasaamuh wal-ta'aayush.",
                "text_en": "The central idea is highlighting the UAE's role as a global capital for tolerance and peaceful coexistence among nations.",
                "explanation_en": "Primary theme of the listening passage."
            },
            "4": {
                "text_ar": "انْطَلَقَ عَامُ التَّسَامُحِ فِي عَامِ 2019م، وَأَطْلَقَهُ المَغْفُورُ لَهُ الشَّيْخُ خَلِيفَةُ بْنُ زَايِد آل نَهْيَان، بِهَدَفِ تَرْسِيخِ قِيَمِ الحِوَارِ وَالانْفِتَاحِ الثَّقَافِيِّ.",
                "arabzi": "intalaqa 'aam al-tasaamuh fee 'aam 2019, wa-atlaqahu al-shaykh khalifa bin zayed, bi-hadaf tarsseekh qiyam al-hiwaar.",
                "text_en": "The Year of Tolerance was launched in 2019 by Sheikh Khalifa bin Zayed Al Nahyan, aiming to institutionalize dialogue and cultural openness.",
                "explanation_en": "Historical context and national milestone."
            },
            "5": {
                "text_ar": "حَقَّقَتِ الإِمَارَاتُ ذَلِكَ بِسَنِّ قَوَانِينَ مُكَافَحَةِ التَّمْيِيزِ، وَإِنْشَاءِ وَزَارَةِ التَّسَامُحِ، وَاحْتِضَانِ أَكْثَرَ مِنْ 200 جِنْسِيَّةٍ فِي أَمْنٍ وَسَلَامٍ.",
                "arabzi": "haqqaqat al-imaraat dhalika bi-sann qawaneen mukaafahat al-tamyeez, wa-inshaa' wizarat al-tasaamuh fee amn wa-salaam.",
                "text_en": "The UAE achieved this by enacting anti-discrimination laws, establishing a Ministry of Tolerance, and hosting over 200 nationalities in safety and peace.",
                "explanation_en": "Institutional and social evidence."
            },
            "6": {
                "text_ar": "التَّرْتِيبُ الزَّمَنِيُّ: 2016: عَامُ القِرَاءَةِ، 2017: عَامُ الخَيْرِ، 2018: عَامُ زَايِد، 2019: عَامُ التَّسَامُحِ.",
                "arabzi": "al-tarteeb: 2016 'aam al-qiraa'a, 2017 'aam al-khayr, 2018 'aam zayed, 2019 'aam al-tasaamuh.",
                "text_en": "Chronological order: 2016: Year of Reading, 2017: Year of Giving, 2018: Year of Zayed, 2019: Year of Tolerance.",
                "explanation_en": "Official UAE commemorative years sequence."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "9": {
        "printed_page": 9,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَتَحَدَّثُ: الإِمَارَاتُ تُعَزِّزُ التَّسَامُحَ (Speaking: UAE Promotes Tolerance)",
        "title_ar": "أَتَحَدَّثُ: الإِمَارَاتُ تُعَزِّزُ التَّسَامُحَ بَيْنَ الجِنْسِيَّاتِ المُتَعَدِّدَةِ",
        "title_en": "Speaking: UAE Promotes Tolerance Across Diverse Nationalities",
        "paragraphs": [
            "تَفْخَرُ دَوْلَةُ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ مُنْذُ تَأْسِيسِهَا عَامَ 1971 بِتَعْزِيزِ التَّسَامُحِ وَالتَّعَايُشِ بَيْنَ سُكَّانِهَا مُتَعَدِّدِي الجِنْسِيَّاتِ.",
            "وَلَا يَخْفَى عَلَى أَحَدٍ أَنَّ دَوْلَةَ الإِمَارَاتِ تَتَمَتَّعُ بِتَارِيخٍ مُشَرِّفٍ مِنَ الحِوَارِ بَيْنَ الأَدْيَانِ وَنَشْرِ السَّلَامِ فِي العَالَمِ.",
            "قَبْلَ المُحَادَثَةِ: أَقْرَأُ الفِقْرَةَ وَأُدَوِّنُ الأَفْكَارَ الرَّئِيسَةَ الَّتِي سَتُسَاعِدُنِي فِي التَّحَدُّثِ أَمَامَ زُمَلَائِي.",
            "أَثْنَاءَ المُحَادَثَةِ: أَتَحَدَّثُ بِلُغَةٍ سَلِيمَةٍ وَتَنْغِيمٍ مُعَبِّرٍ عَنْ دَوْرِ الإِمَارَاتِ فِي احْتِضَانِ الثَّقَافَاتِ المُخْتَلِفَةِ.",
            "بَعْدَ المُحَادَثَةِ: أُقَيِّمُ أَدَائِي وَأَسْتَمِعُ إِلَى تَعْلِيقَاتِ المُعَلِّمِ وَالزُّمَلَاءِ لِتَطْوِيرِ مَهَارَاتِ الإِلْقَاءِ."
        ],
        "paragraphs_en": [
            "The United Arab Emirates has taken pride since its founding in 1971 in promoting tolerance and coexistence among its multi-national population.",
            "It is evident to all that the UAE enjoys an honorable history of interfaith dialogue and spreading peace globally.",
            "Before Speaking: I read the paragraph and jot down main ideas that will support my presentation in front of my peers.",
            "During Speaking: I speak with clear articulation and expressive intonation about the UAE's role in embracing different cultures.",
            "After Speaking: I assess my performance and listen to feedback from my teacher and peers to develop my presentation skills."
        ],
        "model_answers": {
            "3": {
                "text_ar": "تعتبر دولة الإمارات نموذجاً ملهماً في التسامح باحتضانها أكثر من 200 جنسية يعيشون في وئام واحترام للقوانين.",
                "arabzi": "tu'tabar al-imaraat namoodhajan fee al-tasaamuh bi-ihtidaaniha akthar min 200 jinsiyya fee wi'aam.",
                "text_en": "The UAE is an inspiring model of tolerance, hosting over 200 nationalities living in harmony and respect for the law.",
                "explanation_en": "Key presentation speaking point."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "10": {
        "printed_page": 10,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَقْرَأُ: عَامُ التَّسَامُحِ (Reading: Year of Tolerance)",
        "title_ar": "أَقْرَأُ: عَامُ التَّسَامُحِ",
        "title_en": "Reading: Year of Tolerance",
        "paragraphs": [
            "إِنَّ التَّسَامُحَ مِنْ أَهَمِّ القِيَمِ الَّتِي يَهْتَمُّ بِهَا قَادَةُ دَوْلَةِ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ، وَهَذِهِ القِيمَةُ أَضَافَتْ لِلشَّعْبِ مَعَانِيَ عَمِيقَةً.",
            "أَطْلَقَ المَغْفُورُ لَهُ الشَّيْخُ خَلِيفَةُ بْنُ زَايِد آل نَهْيَان عَلَى عَامِ 2019 شِعَارَ (عَامُ التَّسَامُحِ) لِتَرْسِيخِ دَوْلَةِ الإِمَارَاتِ عَاصِمَةً عَالَمِيَّةً لِلتَّلَاقِي وَالحِوَارِ.",
            "وَأَكَّدَ صَاحِبُ السُّمُوِّ الشَّيْخُ مُحَمَّدُ بْنُ رَاشِدٍ آل مَكْتُوم: «تَرَبَّيْنَا فِي مَدْرَسَةِ زَايِدٍ عَلَى قِيَمٍ نَبِيلَةٍ عَدِيدَةٍ مِنْ أَهَمِّهَا التَّسَامُحُ، وَالإِمَارَاتُ سَتَظَلُّ النَّمُوذَجَ وَالقُدْوَةَ فِي الِانْفِتَاحِ الوَاعِي عَلَى الآخَرِ».",
            "سُؤَالٌ 1: مَا دَوَاعِي اهْتِمَامِ قَادَةِ دَوْلَةِ الإِمَارَاتِ بِالتَّسَامُحِ؟",
            "سُؤَالٌ 2: كَيْفَ يَتَجَلَّى التَّسَامُحُ عَلَى أَرْضِ الوَاقِعِ فِي دَوْلَةِ الإِمَارَاتِ؟",
            "سُؤَالٌ 3: مَا نَتَائِجُ نَشْرِ التَّسَامُحِ بَيْنَ النَّاسِ وَاعْتِمَادِهِ كَقِيمَةٍ أَسَاسِيَّةٍ فِي التَّعَامُلِ؟",
            "سُؤَالٌ 4: أَسْتَخْرِجُ مَعَانِيَ الكَلِمَاتِ وَأَضْدَادَهَا: (التَّسَامُحُ / التَّعَصُّبُ)، (الاِسْتِقْرَارُ / الِاضْطِرَابُ)، (التَّعَاوُنُ / التَّخَاذُلُ)، (الاِخْتِلَافُ / التَّشَابُهُ)."
        ],
        "paragraphs_en": [
            "Tolerance is among the most essential values championed by the leaders of the UAE, adding profound meaning to society.",
            "The late Sheikh Khalifa bin Zayed Al Nahyan designated 2019 as the 'Year of Tolerance' to cement the UAE as a global capital for encounter and dialogue.",
            "His Highness Sheikh Mohammed bin Rashid Al Maktoum affirmed: 'We were raised in Zayed’s school on noble values, foremost among them tolerance, and the UAE will remain the model in conscious openness to others.'",
            "Question 1: What are the motives behind UAE leaders' dedication to tolerance?",
            "Question 2: How is tolerance manifested tangibly on the ground across the UAE?",
            "Question 3: What are the societal outcomes of spreading tolerance as a fundamental value?",
            "Question 4: Identify word meanings and antonyms: (Tolerance / Fanaticism), (Stability / Turmoil), (Cooperation / Abandonment), (Difference / Sameness)."
        ],
        "model_answers": {
            "3": {
                "text_ar": "دواعي الاهتمام تنبع من الإرث الإنساني للمغفور له الشيخ زايد بن سلطان آل نهيان، والإيمان بأن التسامح هو أساس الاستقرار والازدهار.",
                "arabzi": "dawaa'i al-ihtimaam tanba'u min irth al-shaykh zayed, wal-eemaan bi-anna al-tasaamuh asaasu al-istiqraar.",
                "text_en": "The dedication stems from the humanitarian legacy of Sheikh Zayed and the belief that tolerance is the bedrock of stability and prosperity.",
                "explanation_en": "Analysis of leadership vision."
            },
            "4": {
                "text_ar": "يتجلى التسامح في التعايش السلمي، وكفالة حرية ممارسة الشعائر الدينية، وتوفير بيئة عمل عادلة تضمن كرامة الإنسان لكافة الجنسيات.",
                "arabzi": "yatajalla al-tasaamuh fee al-ta'aayush al-silmi, wa-kafaalat hurriyat al-sha'aa'ir, wa-bee'at 'amal 'aadila.",
                "text_en": "Tolerance is manifested in peaceful coexistence, freedom of worship, and fair workplaces guaranteeing dignity for all nationalities.",
                "explanation_en": "Real-world manifestations in the UAE."
            },
            "5": {
                "text_ar": "نتائج نشر التسامح: تعزيز الأمان الاجتماعي، تقليل النزاعات، دفع عجلة الابتكار، وجذب المواهب العالمية للعمل والبناء المشترك.",
                "arabzi": "nataa'ij nashr al-tasaamuh: ta'zeez al-amaan al-ijtimaa'i, daf' al-ibtikaar, wa-jadhb al-mawaahib.",
                "text_en": "Outcomes: Enhancing social safety, reducing conflicts, driving innovation, and attracting international talent for shared progress.",
                "explanation_en": "Socioeconomic impact."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "11": {
        "printed_page": 11,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "قَوَاعِدُ النَّحْوِ: الجُمْلَةُ البَسِيطَةُ وَالجُمْلَةُ المُرَكَّبَةُ (Grammar: Simple & Compound Sentences)",
        "title_ar": "قَوَاعِدُ النَّحْوِ: الجُمْلَةُ البَسِيطَةُ وَالجُمْلَةُ المُرَكَّبَةُ",
        "title_en": "Grammar: Simple & Compound Sentences",
        "paragraphs": [
            "فَائِدَةٌ نَحْوِيَّةٌ: الجُمْلَةُ البَسِيطَةُ وَالجُمْلَةُ المُرَكَّبَةُ:",
            "الجُمْلَةُ البَسِيطَةُ: هِيَ كَلَامٌ نُعَبِّرُ بِهِ عَنْ مَعْنًى مُفِيدٍ بِجُمْلَةٍ وَاحِدَةٍ، كُلُّ عُنْصُرٍ مِنْ عَنَاصِرِهَا الأَصْلِيَّةِ يَكُونُ لَفْظًا وَاحِدًا. مِثَالٌ: التَّسَامُحُ نِعْمَةٌ - نُحِبُّ المُسَاوَاةَ.",
            "الجُمْلَةُ المُرَكَّبَةُ: هِيَ جُمْلَةٌ أَحَدُ عَنَاصِرِهَا الأَصْلِيَّةِ أَوِ المُتَمِّمَةِ جُمْلَةٌ فِعْلِيَّةٌ أَوْ اسْمِيَّةٌ أَوْ مَصْدَرٌ مُؤَوَّلٌ. مِثَالٌ: التَّسَامُحُ يَقُودُنَا إِلَى فِعْلِ الخَيْرِ - يَنْبَغِي أَنْ نَتَحَلَّى بِالتَّعَاوُنِ.",
            "المُهِمَّةُ الكِتَابِيَّةُ: كِتَابَةُ مَقَالٍ أَتَحَدَّثُ فِيهِ عَنْ إِنْجَازَاتِ دَوْلَةِ الإِمَارَاتِ فِي تَعْزِيزِ التَّسَامُحِ، مُنَوِّعًا بَيْنَ الجُمَلِ البَسِيطَةِ وَالمُرَكَّبَةِ.",
            "بَعْدَ الكِتَابَةِ: أُرَاجِعُ مَا كَتَبْتُ وَأَتَأَكَّدُ مِنْ خُلُوِّهِ مِنَ الأَخْطَاءِ الإِمْلَائِيَّةِ، وَأُقَسِّمُ المَوْضُوعَ إِلَى فِقْرَاتٍ (مُقَدِّمَةٍ، عَرْضٍ، خَاتِمَةٍ)."
        ],
        "paragraphs_en": [
            "Grammar Note: Simple and Compound Sentences:",
            "Simple Sentence: An expression conveying a complete meaning in a single clause where each core constituent is a single word. Example: Tolerance is a blessing (al-tasaamuh ni'mah) - We love equality.",
            "Compound Sentence: A sentence in which one of its core or completing constituents is an embedded verbal clause, nominal clause, or interpreted infinitive. Example: Tolerance leads us to do good - It is essential that we embody cooperation.",
            "Writing Task: Write an essay discussing the UAE's achievements in promoting tolerance, diversifying between simple and compound sentences.",
            "Post-Writing: Proofread your work for spelling accuracy and ensure proper paragraph organization (Introduction, Body, Conclusion)."
        ],
        "model_answers": {
            "3": {
                "text_ar": "جملة بسيطة: التسامح ركيزة أساسية. جملة مركبة: تسعى الإمارات أن تنشر السلام بين شعوب الأرض.",
                "arabzi": "jumla baseeta: al-tasaamuh rakeezat asaasiyya. jumla murakkaba: tas'aa al-imaraat an tanshur al-salaam.",
                "text_en": "Simple sentence: Tolerance is a vital pillar. Compound sentence: The UAE strives to spread peace across global nations.",
                "explanation_en": "Syntactic parsing distinction between simple and compound syntax."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "12": {
        "printed_page": 12,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "نَوَاتِجُ التَّعَلُّمِ: صَدِيقِي الغَرِيبُ (Learning Outcomes: My Strange Friend)",
        "title_ar": "نَوَاتِجُ التَّعَلُّمِ: صَدِيقِي الغَرِيبُ",
        "title_en": "Learning Outcomes: My Strange Friend",
        "paragraphs": [
            "الوَحْدَةُ الأُولَى - الدَّرْسُ الثَّانِي: صَدِيقِي الغَرِيبُ (قَبُولُ الآخَرِ):",
            "1. يَسْتَمِعُ وَيَفْهَمُ المَعْنَى الكُلِّيَّ لِنُصُوصٍ مُوَسَّعَةٍ فِي مَوْضُوعَاتٍ وَصْفِيَّةٍ وَفِكْرِيَّةٍ.",
            "2. يَسْتَمِعُ وَيُحَدِّدُ النِّقَاطَ الرَّئِيسَةَ فِي نُصُوصٍ مُوَسَّعَةٍ.",
            "3. يُنْتِجُ حَدِيثًا مُتَرَابِطًا مُسْتَخْدِمًا التَّنْغِيمَ الصَّحِيحَ لِلتَّعْبِيرِ عَنِ المَشَاعِرِ وَالمَوَاقِفِ.",
            "4. يَقْرَأُ نَصَّ (صَدِيقِي الغَرِيبُ) وَيُحَلِّلُ العَلَاقَاتِ الإِنْسَانِيَّةَ وَقِيمَةَ الصَّدَاقَةِ عَبْرَ الثَّقَافَاتِ."
        ],
        "paragraphs_en": [
            "Unit 1 - Lesson 2: My Strange Friend (Acceptance of the Other):",
            "1. Listens to and comprehends the overarching meaning of extended texts on descriptive and reflective themes.",
            "2. Listens and identifies core points in extended listening materials.",
            "3. Produces connected speech utilizing proper intonation to express feelings and perspectives.",
            "4. Reads the text 'My Strange Friend' and analyzes human relationships and intercultural friendship."
        ],
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "13": {
        "printed_page": 13,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَسْتَمِعُ: صَدِيقِي الغَرِيبُ (Listening: My Strange Friend)",
        "title_ar": "أَسْتَمِعُ: صَدِيقِي الغَرِيبُ",
        "title_en": "Listening: My Strange Friend",
        "paragraphs": [
            "قَبْلَ الِاسْتِمَاعِ: أُنَاقِشُ العُنْوَانَ مَعَ المُعَلِّمِ وَالزُّمَلَاءِ فِي الصَّفِّ: هَلْ أَنَا مِمَّنْ يَتَقَبَّلُ وُجُودَ الآخَرِ إِلَى جَانِبِهِ؟ وَلِمَاذَا؟",
            "أُسَجِّلُ الأَفْكَارَ الَّتِي أَتَوَقَّعُ أَنْ يَتَضَمَّنَهَا الدَّرْسُ حَوْلَ قَبُولِ الاخْتِلَافِ الثَّقَافِيِّ.",
            "أَثْنَاءَ الِاسْتِمَاعِ: أُنْصِتُ بِانْتِبَاهٍ لِقِصَّةِ التَّعَارُفِ بَيْنَ الصَّدِيقَيْنِ، وَكَيْفَ تَجَاوَزَا حَوَاجِزَ اللُّغَةِ وَالعَادَاتِ.",
            "بَعْدَ الِاسْتِمَاعِ: أُجِيبُ عَنِ الأَسْئِلَةِ: كَيْفَ يُثْرِي الصَّدِيقُ القَادِمُ مِنْ ثَقَافَةٍ أُخْرَى حَيَاتَنَا وَمَعَارِفَنَا؟"
        ],
        "paragraphs_en": [
            "Before Listening: I discuss the title with my teacher and classmates: Am I someone who embraces the presence of others alongside me? Why?",
            "I write down the concepts I anticipate the lesson will address regarding cultural acceptance.",
            "During Listening: I listen attentively to the story of friendship between the two peers, and how they bridged language and cultural boundaries.",
            "After Listening: I answer the questions: How does a friend from another culture enrich our lives and knowledge?"
        ],
        "model_answers": {
            "0": {
                "text_ar": "نعم، أتقبل وجود الآخر لأن الاختلاف والتنوع سنة كونية تثري خبراتنا وتوسع مداركنا.",
                "arabzi": "na'am, ataqabbal wujood al-aakhar li-anna al-tanawwu' yuthri khibraatina.",
                "text_en": "Yes, I embrace others because diversity is a universal principle that enriches our experiences and broadens our perspectives.",
                "explanation_en": "Empathetic self-reflection."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "14": {
        "printed_page": 14,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَتَحَدَّثُ: قَبُولُ الآخَرِ (Speaking: Accepting Others)",
        "title_ar": "أَتَحَدَّثُ: قَبُولُ الآخَرِ",
        "title_en": "Speaking: Accepting Others",
        "paragraphs": [
            "يَعْتَقِدُ كَثِيرُونَ أَنَّ قَبُولَ الآخَرِ لَيْسَ سَهْلًا، لَكِنَّ الحَقِيقَةَ هِيَ العَكْسُ تَمَامًا، فَجَمِيعُ الاخْتِلَافَاتِ فِي العَالَمِ تَصْنَعُ جَمَالَ الحَيَاةِ.",
            "قَبْلَ المُحَادَثَةِ: 1. أَقْرَأُ الفِقْرَةَ. 2. أُدَوِّنُ بَعْضَ الأَفْكَارِ الَّتِي سَتُسَاعِدُنِي فِي التَّحَدُّثِ. 3. أَسْتَفْسِرُ مِنَ المُعَلِّمِ عَنِ المَفَاهِيمِ.",
            "أَثْنَاءَ المُحَادَثَةِ: أَتَحَدَّثُ عَنْ أَهَمِّيَّةِ كَسْرِ الحَوَاجِزِ النَّفْسِيَّةِ عِنْدَ لِقَاءِ أَشْخَاصٍ جُدُدٍ مِنْ جِنْسِيَّاتٍ مُخْتَلِفَةٍ.",
            "بَعْدَ المُحَادَثَةِ: أُنَاقِشُ زُمَلَائِي حَوْلَ أَفْضَلِ الطُّرُقِ لِبِنَاءِ صَدَاقَاتٍ قَائِمَةٍ عَلَى الِاحْتِرَامِ المُتَبَادَلِ."
        ],
        "paragraphs_en": [
            "Many believe that accepting the other is difficult, but the reality is quite the opposite; differences across the world create the beauty of life.",
            "Before Speaking: 1. I read the passage. 2. I note down key ideas to guide my speech. 3. I inquire with my teacher about concepts.",
            "During Speaking: I talk about the significance of overcoming psychological barriers when meeting people from diverse nationalities.",
            "After Speaking: I discuss with my peers the best methods to build friendships grounded in mutual respect."
        ],
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "15": {
        "printed_page": 15,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَقْرَأُ: تَقَبُّلُ الغَرِيبِ (Reading: Embracing the Stranger)",
        "title_ar": "أَقْرَأُ: تَقَبُّلُ الغَرِيبِ",
        "title_en": "Reading: Embracing the Stranger",
        "paragraphs": [
            "هُنَاكَ العَدِيدُ مِنَ الدِّرَاسَاتِ النَّفْسِيَّةِ وَالتَّرْبَوِيَّةِ عَنْ أَسْبَابِ التَّعَصُّبِ وَعَدَمِ التَّسَامُحِ، وَعَدَمِ تَقَبُّلِ الآخَرِينَ، وَعَلَيْنَا أَنْ نَقِفَ سَوِيًّا لِتَهْيِئَةِ الجِيلِ القَادِمِ لِثَقَافَةِ التَّعَدُّدِيَّةِ.",
            "فِي البِدَايَةِ يَجِبُ أَنْ نَعْرِفَ أَنَّ الآخَرَ هُوَ كُلُّ إِنْسَانٍ مُخْتَلِفٍ عَنِّي؛ شَكْلِيًّا أَوْ عِرْقِيًّا أَوْ ثَقَافِيًّا، لَكِنْ تَجْمَعُنَا الإِنْسَانِيَّةُ.",
            "إِنَّ الاخْتِلَافَ جَعَلَ التَّنَوُّعَ كَحَدِيقَةٍ تَمَازَجَتْ بِهَا الأَزْهَارُ بِمُخْتَلَفِ أَلْوَانِهَا وَتَنَاسُقِهَا، فَأَخْرَجَتْ مَنْظَرًا بَدِيعًا فَرِيدًا مِنْ نَوْعِهِ.",
            "سُؤَالٌ 1: مَا فِكْرَةُ النَّصِّ الرَّئِيسَةُ؟",
            "سُؤَالٌ 2: لِمَ يُعَدُّ تَقَبُّلُ الآخَرِ الغَرِيبِ مُهِمًّا فِي حَيَاتِنَا المُعَاصِرَةِ؟",
            "سُؤَالٌ 3: مَنْ هُوَ (الآخَرُ) بِحَسَبِ مَا وَرَدَ فِي النَّصِّ؟"
        ],
        "paragraphs_en": [
            "Numerous psychological and educational studies address the causes of prejudice and intolerance; we must unite to prepare future generations for cultural pluralism.",
            "First, we must understand that 'the other' is any individual differing from me in appearance, ethnicity, or culture, yet united with us in shared humanity.",
            "Diversity makes humanity akin to a garden blending flowers of varied vibrant colors, presenting a unique and magnificent panorama.",
            "Question 1: What is the main idea of the reading passage?",
            "Question 2: Why is embracing the stranger essential in our contemporary life?",
            "Question 3: Who is 'the other' according to the passage?"
        ],
        "model_answers": {
            "3": {
                "text_ar": "فكرة النص هي أن التنوع البشري نعمة وجمال كألوان الحديقة، وقبول الاختلاف ركيزة للتعايش الإنساني.",
                "arabzi": "fikrat al-nass anna al-tanawwu' al-bashari ni'ma ka-azhaar al-hadeeqa.",
                "text_en": "The central idea is that human diversity is a blessing akin to a colorful garden, and accepting difference is essential for coexistence.",
                "explanation_en": "Literary analysis of metaphor."
            },
            "4": {
                "text_ar": "يعد تقبل الآخر مهماً لأنه يمنع النزاعات، ويثري الفكر، ويبني مجتمعات متماسكة تنعم بالأمان والسلام.",
                "arabzi": "yuhaddidu taqabbul al-aakhar li-annahu yamna'u al-nizaa'aat wa-yuthri al-fikr.",
                "text_en": "Embracing others is vital because it prevents strife, enriches intellect, and builds cohesive societies enjoying peace.",
                "explanation_en": "Societal justification."
            },
            "5": {
                "text_ar": "الآخر هو كل إنسان يختلف عني في العرق أو اللغة أو الثقافة أو الرأي، لكن تجمعه بي الرابطة الإنسانية.",
                "arabzi": "al-aakhar huwa kullu insaan yakhtalifu 'anni fee al-'irq aw al-lugha lakin tajma'una al-insaaniyya.",
                "text_en": "The other is any fellow human who differs from me in race, language, culture, or perspective, yet shares human dignity.",
                "explanation_en": "Definition according to text."
            }
        },
        "confidence": 0.99,
        "review_status": "reviewed"
    },
    "16": {
        "printed_page": 16,
        "unit": "الوَحْدَةُ الأُولَى: التَّعَايُشُ وَالتَّسَامُحُ (Unit 1: Coexistence & Tolerance)",
        "lesson": "أَكْتُبُ: عِلاقَتِي مَعَ صَدِيقِي الغَرِيبِ (Writing: My Relationship with My Foreign Friend)",
        "title_ar": "أَكْتُبُ: عَلَاقَتِي مَعَ صَدِيقِي الغَرِيبِ",
        "title_en": "Writing: My Relationship with My Foreign Friend",
        "paragraphs": [
            "نَحْنُ نَحْتَاجُ الأَصْدِقَاءَ فِي حَيَاتِنَا، نَحْتَاجُ الاخْتِلَافَ فِي الخِبْرَةِ وَالمَعْرِفَةِ لِنَتَعَرَّفَ الطَّرَفَ الآخَرَ مِنَ الكُرَةِ الأَرْضِيَّةِ، لِنَتَوَاصَلَ وَنَتَبَادَلَ الأَفْكَارَ.",
            "فَعَلَاقَتِي مَعَ صَدِيقِي الغَرِيبِ فِي ثَقَافَتِهِ وَجِنْسِيَّتِهِ هِيَ عَلَاقَةٌ تَكَامُلِيَّةٌ مُتَكَافِئَةٌ، يَنْتُجُ مِنْ خِلَالِهَا اتِّسَاعُ مَدَى الرُّؤْيَةِ لِلْعَالَمِ.",
            "المُهِمَّةُ: كِتَابَةُ نَصٍّ أُوَضِّحُ فِيهِ حَاجَتِي إِلَى الآخَرِ مُوَضِّحًا الأَسْبَابَ وَالنَّتَائِجَ الإِيجَابِيَّةَ لِهَذِهِ العَلَاقَةِ.",
            "إِرْشَادَاتُ الكِتَابَةِ: 1. أَحْرِصُ عَلَى كِتَابَةِ عُنْوَانٍ شَيِّقٍ. 2. أُقَسِّمُ المَوْضُوعَ إِلَى (مُقَدِّمَةٍ - عَرْضٍ - خَاتِمَةٍ). 3. أُرَاعِي عَلَامَاتِ التَّرْقِيمِ وَسَلَامَةَ اللُّغَةِ."
        ],
        "paragraphs_en": [
            "We need friends in our lives; we need diversity of experience and knowledge to discover the other half of our planet, to connect and exchange ideas.",
            "My relationship with my foreign friend in culture and nationality is a complementary, egalitarian bond expanding my worldview.",
            "Task: Compose a text explaining our need for others, highlighting reasons and positive outcomes of this collaborative relationship.",
            "Writing Guidelines: 1. Select an engaging title. 2. Organize into (Introduction - Body - Conclusion). 3. Observe correct punctuation and grammatical precision."
        ],
        "confidence": 0.99,
        "review_status": "reviewed"
    }
}

# Add integer keys for convenience and backwards-compatibility
for _k, _v in list(GRADE_8_TEXTBOOK_PAGES_DATA.items()):
    if isinstance(_k, str) and _k.isdigit():
        GRADE_8_TEXTBOOK_PAGES_DATA[int(_k)] = _v
