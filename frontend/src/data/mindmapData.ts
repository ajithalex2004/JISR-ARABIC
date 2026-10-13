export interface MindmapItem {
  ar: string;
  en: string;
  root?: string;
  pattern?: string;
  meaningAr?: string;
  meaningEn?: string;
}

export interface MindmapBranch {
  titleAr: string;
  titleEn: string;
  iconName?: string;
  color: string;
  items: MindmapItem[];
}

export interface MindmapChapter {
  id: string;
  titleAr: string;
  titleEn: string;
  unitAr: string;
  unitEn: string;
  pages: string;
  color: string;
  summaryAr: string;
  summaryEn: string;
  branches: MindmapBranch[];
}

export interface SyntaxStep {
  roleAr: string;
  roleEn: string;
  caseAr: string;
  caseEn: string;
  detailAr: string;
  detailEn: string;
}

export interface SyntaxPathway {
  titleAr: string;
  titleEn: string;
  subtitleAr: string;
  subtitleEn: string;
  color: string;
  steps: SyntaxStep[];
}

export interface GrammarRuleExample {
  sentenceAr: string;
  sentenceEn: string;
  analysisAr: string;
  analysisEn: string;
}

export interface GrammarRule {
  key: string;
  titleAr: string;
  titleEn: string;
  badgeAr: string;
  badgeEn: string;
  ruleAr: string;
  ruleEn: string;
  formulaAr: string;
  formulaEn: string;
  examples: GrammarRuleExample[];
}

export const MINDMAP_CHAPTERS: MindmapChapter[] = [
  {
    id: 'chapter_1',
    titleAr: 'أَلْعَابُ الكُرَةِ',
    titleEn: 'Ball Games',
    unitAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitEn: 'Sports and Hobbies',
    pages: '6 - 15',
    color: '#2563EB',
    summaryAr: 'أنواع الكرات، كرة القدم الساحرة المستديرة، مخطط الأصابع الخمسة، وروابط التراكيب اللغوية.',
    summaryEn: 'Ball categories, football rules & pitch specs, 5-finger framework, and syntactic connectives.',
    branches: [
      {
        titleAr: 'المفردات وجذور الكلمات',
        titleEn: 'Core Vocabulary & Roots',
        color: '#0284C7',
        items: [
          {
            ar: 'الكُرَةُ (ج: كُرَات)',
            en: 'The Ball (pl. Balls)',
            root: 'ك - ر - ر (K-R-R)',
            pattern: 'فُعْلَة (Fu\'lah)',
            meaningAr: 'كُلُّ جِسْمٍ مُسْتَدِيرٍ يُسْتَخْدَمُ فِي اللَّعِبِ.',
            meaningEn: 'Any spherical / round body used for sports.'
          },
          {
            ar: 'مُسْتَدِيرٌ',
            en: 'Spherical / Round',
            root: 'د - و - ر (D-W-R)',
            pattern: 'مُسْتَفْعِل (Mustaf\'il)',
            meaningAr: 'عَلَى هَيْئَةِ دَائِرَةٍ مُنْتَظَمَةٍ.',
            meaningEn: 'In the circular shape of a round ball.'
          },
          {
            ar: 'جَمَاعِيٌّ (عكس: فَرْدِيٌّ)',
            en: 'Team / Collective (opp. Individual)',
            root: 'ج - م - ع (J-M-A\')',
            pattern: 'فَعَالِيّ (Fa\'aaliyy)',
            meaningAr: 'نَشَاطٌ رِيَاضِيٌّ يَشْتَرِكُ فِيهِ فَرِيقٌ كَامِلٌ.',
            meaningEn: 'A sport involving collaborative teamwork.'
          },
          {
            ar: 'المُبَارَاةُ (ج: مُبَارَيَات)',
            en: 'The Match / Tournament',
            root: 'ب - ر - ي (B-R-Y)',
            pattern: 'مُفَاعَلَة (Mufa\'alah)',
            meaningAr: 'مُنَافَسَةٌ رِيَاضِيَّةٌ مُنَظَّمَةٌ بَيْنَ فَرِيقَيْنِ.',
            meaningEn: 'A structured athletic fixture between two teams.'
          }
        ]
      },
      {
        titleAr: 'حقائق ومواصفات الدرس',
        titleEn: 'Reading Facts & Specifications',
        color: '#059669',
        items: [
          {
            ar: 'اللَّقَبُ: السَّاحِرَةُ المُسْتَدِيرَةُ',
            en: 'Moniker: The Round Magician / Enchantress',
            meaningAr: 'سَمَّوْهَا السَّاحِرَةَ المُسْتَدِيرَةَ لِأَنَّهَا سَحَرَتْ عُقُولَ أَكْثَرَ مِنْ مِلْيَارِ مُتَابِعٍ.',
            meaningEn: 'Football is dubbed "The Round Magician" because it enchants over 1 billion fans.'
          },
          {
            ar: 'عَدَدُ اللاعِبِينَ: 11 لاعِبًا لِكُلِّ فَرِيقٍ',
            en: 'Squad Size: 11 players per team',
            meaningAr: 'يَتَكَوَّنُ الفَرِيقَانِ مِنْ 22 لاعِبًا عَلَى أَرْضِ المَلْعَبِ.',
            meaningEn: 'Total of 22 players on the pitch during match play.'
          },
          {
            ar: 'المَلْعَبُ: قِطْعَةُ أَرْضٍ مُسْتَطِيلَةٌ',
            en: 'Pitch: Rectangular turfed grass ground',
            meaningAr: 'طُولُ المَلْعَبِ بَيْنَ 100 إِلَى 110م، وَعَرْضُهُ 64 إِلَى 75م.',
            meaningEn: 'Length: 100-110m, Width: 64-75m with green grass turf.'
          },
          {
            ar: 'مُدَّةُ المُبَارَاةِ: شَوْطَانِ (45 دَقِيقَة لِكُلِّ شَوْطٍ)',
            en: 'Duration: 2 halves of 45 mins each',
            meaningAr: 'تَفْصِلُ بَيْنَهُمَا اسْتِرَاحَةٌ مُدَّتُهَا 15 دَقِيقَةً، وَيُشْرِفُ عَلَيْهَا 4 حُكَّامٍ.',
            meaningEn: 'Includes a 15-minute intermission, officiated by 4 referees.'
          }
        ]
      },
      {
        titleAr: 'مخطط الأصابع الخمسة للفهم',
        titleEn: '5-Finger Questioning Framework',
        color: '#D97706',
        items: [
          {
            ar: 'الإِبْهَامُ: لِمَاذَا تُفَضِّلُ هَذِهِ اللُّعْبَةَ؟',
            en: 'Thumb: Why do you prefer this game?',
            meaningAr: 'لِأَنَّهَا تُعَلِّمُنَا التَّعَاوُنَ الجَمَاعِيَّ وَاللِّيَاقَةَ البَدَنِيَّةَ.',
            meaningEn: 'Because it fosters teamwork, collective cooperation, and stamina.'
          },
          {
            ar: 'السَّبَّابَةُ: مَتَى تَعَلَّمْتَهَا؟',
            en: 'Index: When did you learn it?',
            meaningAr: 'تَعَلَّمْتُهَا فِي المَدْرَسَةِ مُنْذُ عَامَيْنِ مَعَ مُعَلِّمِ الرِّيَاضَةِ.',
            meaningEn: 'I learned it at school two years ago with my PE coach.'
          },
          {
            ar: 'الوُسْطَى: مَا المَخَاطِرُ؟',
            en: 'Middle: What hazards / risks exist?',
            meaningAr: 'التَّصَادُمُ، السُّقُوطُ، وَإِجْهَادُ العَضَلَاتِ عِنْدَ الإِهْمَالِ.',
            meaningEn: 'Collisions, falling down, and muscle strain if careless.'
          },
          {
            ar: 'البِنْصِرُ: أَيْنَ تَلْعَبُ؟',
            en: 'Ring: Where is it played?',
            meaningAr: 'فِي مَلْعَبِ المَدْرَسَةِ أَوْ فِي الصَّالَةِ الرِّيَاضِيَّةِ المُغْلَقَةِ.',
            meaningEn: 'At the school pitch or inside the indoor sports hall.'
          },
          {
            ar: 'الخِنْصِرُ: كَمْ عَدَدُ اللاعِبِينَ؟',
            en: 'Pinky: How many players participate?',
            meaningAr: '11 لاعِبًا فِي كُرَةِ القَدَمِ، وَ5 فِي كُرَةِ السَّلَّةِ.',
            meaningEn: '11 players in football, and 5 players in basketball.'
          }
        ]
      },
      {
        titleAr: 'التراكيب والروابط اللغوية',
        titleEn: 'Cohesive Sentence Connectives',
        color: '#7C3AED',
        items: [
          {
            ar: 'يَجِبُ أَنْ...',
            en: 'Must / It is necessary that...',
            meaningAr: 'يَجِبُ أَنْ يَتَدَرَّبَ الفَرِيقُ بِانْتِظَامٍ لِتَحْقِيقِ الفَوْزِ.',
            meaningEn: 'The team must train regularly to achieve victory.'
          },
          {
            ar: 'كَذَلِكَ...',
            en: 'Likewise / Similarly / As well...',
            meaningAr: 'يَحْتَاجُ اللاعِبُ لِيَاقَةً، وَكَذَلِكَ خُطَّةً تكتيكية ذَكِيَّةً.',
            meaningEn: 'The player needs stamina, and likewise a tactical gameplan.'
          },
          {
            ar: 'كَمَا أَنَّ...',
            en: 'Furthermore / In addition / Just as...',
            meaningAr: 'كَمَا أَنَّ الرُّوحَ الرِّيَاضِيَّةَ أَهَمُّ مِنْ مُجَرَّدِ تَسْجِيلِ الأَهْدَافِ.',
            meaningEn: 'Furthermore, sportsmanship is far more important than just goals.'
          },
          {
            ar: 'عَلَى الرَّغْمِ مِنْ...',
            en: 'Despite / Although (Concession)...',
            meaningAr: 'عَلَى الرَّغْمِ مِنْ صُعُوبَةِ المُبَارَاةِ، اسْتَطَاعَ فَرِيقُنَا الفَوْزَ.',
            meaningEn: 'Despite the toughness of the match, our team clinched the win.'
          }
        ]
      },
      {
        titleAr: 'الهوية الإماراتية والروح الرياضية',
        titleEn: 'UAE Identity & National Values',
        color: '#0D9488',
        items: [
          {
            ar: 'الرِّيَاضَاتُ التُّرَاثِيَّةُ فِي الإِمَارَاتِ',
            en: 'UAE Traditional Heritage Sports',
            meaningAr: 'سِبَاقَاتُ الهَجَنِ، الصَّيْدُ بِالصُّقُورِ، وَالتَّجْدِيفُ التُّرَاثِيُّ.',
            meaningEn: 'Camel racing, falconry hunting, and heritage wooden boat rowing.'
          },
          {
            ar: 'أَخْلَاقُ الفَارِسِ وَالرُّوحُ الرِّيَاضِيَّةُ',
            en: 'Sportsmanship & Rider Ethics',
            meaningAr: 'احْتِرَامُ المُنَافِسِ، تَقَبُّلُ النَّتِيجَةِ، وَالتَّوَاضُعُ عِنْدَ الانْتِصَارِ.',
            meaningEn: 'Respecting opponents, gracious acceptance, and humility in victory.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_2',
    titleAr: 'رُكُوبُ الخَيْلِ',
    titleEn: 'Horse Riding (Equestrian)',
    unitAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitEn: 'Sports and Hobbies',
    pages: '16 - 25',
    color: '#D97706',
    summaryAr: 'رياضة الفروسية الأصيلة، صفات الخيل العربي، أدوات الفارس، والشجاعة والاعتزاز بالتراث.',
    summaryEn: 'Arabian horse heritage, equestrian gear, rider bravery, and historical cultural pride.',
    branches: [
      {
        titleAr: 'مفردات الفروسية',
        titleEn: 'Equestrian Vocabulary',
        color: '#0284C7',
        items: [
          {
            ar: 'الجَوَادُ (ج: جِيَاد / خُيُول)',
            en: 'The Steed / Purebred Horse',
            root: 'ج - و - د (J-W-D)',
            meaningAr: 'الحِصَانُ العَرَبِيُّ الأَصِيلُ عَالِي النَّسَبِ وَالسُّرْعَةِ.',
            meaningEn: 'Noble purebred Arabian horse celebrated for speed and beauty.'
          },
          {
            ar: 'السَّرْجُ وَاللِّجَامُ',
            en: 'Saddle & Bridle',
            root: 'س - ر - ج (S-R-J)',
            meaningAr: 'أَدَوَاتٌ تُوضَعُ عَلَى ظَهْرِ الجَوَادِ وَفَمِهِ لِلتَّحَكُّمِ بِهِ.',
            meaningEn: 'Riding leather equipment placed on horse back and bit for control.'
          },
          {
            ar: 'المِضْمَارُ',
            en: 'The Racetrack / Arena',
            root: 'ض - م - ر (D-M-R)',
            meaningAr: 'المَكَانُ المُخَصَّصُ لِسِبَاقَاتِ السُّرْعَةِ وَقَفْزِ الحَوَاجِزِ.',
            meaningEn: 'The specialized circular track for flat racing and jumping.'
          }
        ]
      },
      {
        titleAr: 'القواعد المرتبطة: الفعل الماضي والفاعل',
        titleEn: 'Grammar: Past Verb & Agent (Fa\'il)',
        color: '#7C3AED',
        items: [
          {
            ar: 'رَكِبَ الفَارِسُ الجَوَادَ',
            en: 'The knight rode the steed',
            meaningAr: 'رَكِبَ: فِعْلٌ مَاضٍ مَبْنِيٌّ عَلَى الفَتْحِ | الفَارِسُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ.',
            meaningEn: 'Rakiba: Past Verb (built on Fatha) | Al-Farisu: Doer (Marfoo\' with Damma).'
          },
          {
            ar: 'تَطَابُقُ الفِعْلِ مَعَ الفَاعِلِ تَأْنِيثًا',
            en: 'Feminine Verb-Agent Agreement',
            meaningAr: 'رَكِبَتْ فَاطِمَةُ المُهْرَةَ (إِضَافَةُ تَاءِ التَّأْنِيثِ السَّاكِنَةِ للفِعْلِ).',
            meaningEn: 'Rakibat Fatima: Adding quiescent Ta (تْ) when the subject is feminine.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_3',
    titleAr: 'الجَرْيُ',
    titleEn: 'Running (Athletics)',
    unitAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitEn: 'Sports and Hobbies',
    pages: '26 - 35',
    color: '#10B981',
    summaryAr: 'سباقات الجري السريع والماراثون، التنفس الصحيح، واللياقة البدنية وصحة القلب.',
    summaryEn: 'Sprint races, marathon endurance, correct breathing technique, and cardiovascular stamina.',
    branches: [
      {
        titleAr: 'مفردات ألعاب القوى',
        titleEn: 'Athletics & Track Vocabulary',
        color: '#0284C7',
        items: [
          {
            ar: 'السِّبَاقُ السَّرِيعُ (السبرنت)',
            en: 'The Sprint (Short distance race)',
            meaningAr: 'الجَرْيُ بِأَقْصَى سُرْعَةٍ لِمَسَافَاتٍ قَصِيرَةٍ (100م - 200م).',
            meaningEn: 'Explosive high-speed running over short distances (100-200m).'
          },
          {
            ar: 'المَارَاثُونُ (المَسَافَاتُ الطَّوِيلَةُ)',
            en: 'The Marathon (Long distance endurance)',
            meaningAr: 'الجَرْيُ لِمَسَافَاتٍ طَوِيلَةٍ مَعَ تَنْظِيمِ التَّنَفُّسِ.',
            meaningEn: 'Endurance racing over 42km requiring rhythm and hydration.'
          }
        ]
      },
      {
        titleAr: 'القواعد المرتبطة: ظرفا الزمان والمكان',
        titleEn: 'Grammar: Adverbs of Time & Place',
        color: '#7C3AED',
        items: [
          {
            ar: 'يَجْرِي العَدَّاءُ صَبَاحًا',
            en: 'The runner runs in the morning',
            meaningAr: 'صَبَاحًا: ظَرْفُ زَمَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ.',
            meaningEn: 'Sabahan: Adverb of Time (Mansoob with Fatha).'
          },
          {
            ar: 'تَدَرَّبَ الفَرِيقُ أَمَامَ المِنَصَّةِ',
            en: 'The team trained in front of the podium',
            meaningAr: 'أَمَامَ: ظَرْفُ مَكَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ.',
            meaningEn: 'Amama: Adverb of Place (Mansoob with Fatha).'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_4',
    titleAr: 'الفُنُونُ وَالإِبْدَاعُ',
    titleEn: 'Arts & Creativity',
    unitAr: 'الفُنُونُ وَالإِبْدَاعُ',
    unitEn: 'Arts and Creativity',
    pages: '36 - 45',
    color: '#EC4899',
    summaryAr: 'الرسم، الخط العربي والزخرفة الإسلامية، تناسق الألوان، ومعارض اللوحات الفنية.',
    summaryEn: 'Painting, Arabic calligraphy, Islamic geometry, color palettes, and gallery exhibits.',
    branches: [
      {
        titleAr: 'مصطلحات الفنون',
        titleEn: 'Fine Arts Terminology',
        color: '#0284C7',
        items: [
          {
            ar: 'الخَطُّ العَرَبِيُّ (الكُوفِيّ، الرُّقْعَة، النَّسْخ)',
            en: 'Arabic Calligraphy Styles (Kufi, Ruq\'ah, Naskh)',
            meaningAr: 'فَنُّ كِتَابَةِ الحُرُوفِ العَرَبِيَّةِ بِأَشْكَالٍ هَنْدَسِيَّةٍ جَمِيلَةٍ.',
            meaningEn: 'The art of lettering Arabic scripts with rhythmic geometric grace.'
          },
          {
            ar: 'اللَّوْحَةُ الزَّيْتِيَّةُ',
            en: 'Oil Painting Canvas',
            meaningAr: 'رَسْمٌ إِبْدَاعِيٌّ يُبْرِزُ الضَّوْءَ وَالظِّلالَ بِأَلْوَانِ الزَّيْتِ.',
            meaningEn: 'Creative visual art utilizing oil paints and chiaroscuro.'
          }
        ]
      },
      {
        titleAr: 'القواعد: النعت والمنعوت (الصفة والموصوف)',
        titleEn: 'Grammar: Adjective Agreement (Na\'at & Man\'ut)',
        color: '#7C3AED',
        items: [
          {
            ar: 'رَسَمْتُ لَوْحَةً جَمِيلَةً',
            en: 'I painted a beautiful painting',
            meaningAr: 'جَمِيلَةً: نَعْتٌ مَنْصُوبٌ يَتْبَعُ المَنْعُوتَ (لَوْحَةً) فِي التَّنْكِيرِ وَالإِعْرَابِ.',
            meaningEn: 'Jameelatan: Adjective matching the indefinite noun in Fatha.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_5',
    titleAr: 'القِرَاءَةُ نُورُ العَقْلِ',
    titleEn: 'Reading: Light of the Mind',
    unitAr: 'الفُنُونُ وَالإِبْدَاعُ',
    unitEn: 'Arts and Creativity',
    pages: '46 - 55',
    color: '#6366F1',
    summaryAr: 'أهمية المطالعة، مبادرة تحدي القراءة العربي، زيارة المكتبات العامة، وتلخيص القصص.',
    summaryEn: 'Value of reading, Arab Reading Challenge initiative, library research, and story summaries.',
    branches: [
      {
        titleAr: 'مفردات عالم الكتب',
        titleEn: 'Literary & Reading Vocabulary',
        color: '#0284C7',
        items: [
          {
            ar: 'الفِهْرِسُ وَالمُعْجَمُ',
            en: 'Table of Contents & Lexicon / Dictionary',
            meaningAr: 'دَلِيلُ البَحْثِ عَنِ المَعَانِي وَالمَصَادِرِ فِي الكُتُبِ.',
            meaningEn: 'Reference tools to search terms and verify word meanings.'
          },
          {
            ar: 'المُطَالَعَةُ الحُرَّةُ',
            en: 'Independent Extracurricular Reading',
            meaningAr: 'قِرَاءَةُ الكُتُبِ وَالقِصَصِ لِتَوْسِيعِ المَعَارِفِ وَالمَدَارِكِ.',
            meaningEn: 'Voluntary self-directed reading to expand intellectual breadth.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_6',
    titleAr: 'فِي المَدْرَسَةِ',
    titleEn: 'At School',
    unitAr: 'حَيَاتُنَا المَدْرَسِيَّةُ',
    unitEn: 'Our School Life',
    pages: '56 - 65',
    color: '#0891B2',
    summaryAr: 'البيئة المدرسية، احترام المعلمين والزملاء، المختبرات العلمية، والإذاعة المدرسية.',
    summaryEn: 'School community, honoring educators, lab experiments, and morning broadcasts.',
    branches: [
      {
        titleAr: 'مرافق المدرسة والأنشطة',
        titleEn: 'Campus Facilities & Morning Routine',
        color: '#0284C7',
        items: [
          {
            ar: 'المُخْتَبَرُ العِلْمِيُّ',
            en: 'The Science Laboratory',
            meaningAr: 'مَكَانُ إِجْرَاءِ التَّجَارِبِ الاسْتِكْشَافِيَّةِ العِلْمِيَّةِ.',
            meaningEn: 'Facility equipped for scientific experiments and investigations.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_7',
    titleAr: 'فِي البَيْتِ',
    titleEn: 'At Home',
    unitAr: 'حَيَاتُنَا المَدْرَسِيَّةُ',
    unitEn: 'Our School Life',
    pages: '66 - 75',
    color: '#8B5CF6',
    summaryAr: 'الترابط الأسري، بر الوالدين، تنظيم الوقت وأداء الواجبات المنزلية، والتعاون بين الإخوة.',
    summaryEn: 'Family bonding, filial piety, homework schedule management, and sibling cooperation.',
    branches: [
      {
        titleAr: 'قيم الأسرة والترابط',
        titleEn: 'Home & Kinship Values',
        color: '#059669',
        items: [
          {
            ar: 'بِرُّ الوَالِدَيْنِ',
            en: 'Honoring Parents (Filial Piety)',
            meaningAr: 'طَاعَتُهُمَا وَمُعَامَلَتُهُمَا بِأَدَبٍ وَإِحْسَانٍ وَلِينٍ.',
            meaningEn: 'Obeying and honoring parents with gentle compassion.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_8',
    titleAr: 'طَعَامِي الصِّحِّي',
    titleEn: 'My Healthy Food',
    unitAr: 'الصِّحَّةُ وَالغِذَاءُ',
    unitEn: 'Health and Nutrition',
    pages: '76 - 85',
    color: '#F59E0B',
    summaryAr: 'الهرم الغذائي، الفواكه والخضراوات، الوجبات المتوازنة، وأضرار الوجبات السريعة والسكريات.',
    summaryEn: 'Nutritional food pyramid, fruit & veg vitamins, balanced meals, avoiding junk food.',
    branches: [
      {
        titleAr: 'مفردات الغذاء الصحي',
        titleEn: 'Nutrition & Wellness Terms',
        color: '#0284C7',
        items: [
          {
            ar: 'الغِذَاءُ المُتَوَازِنُ',
            en: 'Balanced Diet',
            meaningAr: 'وَجَبَاتٌ تَمُدُّ الجِسْمَ بِالفِيتَامِينَاتِ وَالأَلْيَافِ وَالمَعَادِنِ.',
            meaningEn: 'Meals providing essential macro and micronutrients for vitality.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_9',
    titleAr: 'مَلَابِسِي وَهُوِيَّتِي',
    titleEn: 'My Clothes & Heritage',
    unitAr: 'الهُوِيَّةُ وَالتُّرَاثُ',
    unitEn: 'Identity and Heritage',
    pages: '86 - 95',
    color: '#0D9488',
    summaryAr: 'الزي الوطني الإماراتي (الكندورة، الغترة، والعقال)، ملابس الفصول الأربعة، وأناقة المظهر.',
    summaryEn: 'Emirati national dress (Kandura, Ghutra, Agal), four seasonal clothes, neat presentation.',
    branches: [
      {
        titleAr: 'مفردات الزي الإماراتي الأصيل',
        titleEn: 'Emirati Traditional Dress Terms',
        color: '#0284C7',
        items: [
          {
            ar: 'الكَنْدُورَةُ الإِمَارَاتِيَّةُ',
            en: 'Emirati Kandura (Thobe)',
            meaningAr: 'الثَّوْبُ الوَطَنِيُّ التُّرَاثِيُّ الأَنِيقُ بِدُونِ يَاقَةٍ.',
            meaningEn: 'The iconic ankle-length white collarless robe of UAE heritage.'
          }
        ]
      }
    ]
  },
  {
    id: 'chapter_10',
    titleAr: 'وَقْتُ المَرَحِ وَالعُطْلَةُ',
    titleEn: 'Fun Time & Vacations',
    unitAr: 'الهُوِيَّةُ وَالتُّرَاثُ',
    unitEn: 'Identity and Heritage',
    pages: '96 - 105',
    color: '#E11D48',
    summaryAr: 'استثمار العطلة الصيفية، الرحلات البرية والبحرية، التخييم في صحراء الإمارات، وتنمية المهارات.',
    summaryEn: 'Holiday camps, desert safari camping in UAE dunes, marine trips, and personal skill development.',
    branches: [
      {
        titleAr: 'أنشطة العطلة والمرح',
        titleEn: 'Holiday Activities & Desert Camping',
        color: '#0284C7',
        items: [
          {
            ar: 'التَّخْيِيمُ فِي البَرِّ (الرِّحْلاتُ البَرِّيَّةُ)',
            en: 'Desert Safari & Dune Camping',
            meaningAr: 'الاسْتِمْتَاعُ بِجَمَالِ كُثْبَانِ الرِّمَالِ الذَّهَبِيَّةِ فِي الإِمَارَاتِ.',
            meaningEn: 'Appreciating the beauty of golden sand dunes in the UAE desert.'
          }
        ]
      }
    ]
  }
];

export const CURRICULUM_RULES: GrammarRule[] = [
  {
    key: 'sentence_types',
    titleAr: 'الجُمْلَةُ الاسْمِيَّةُ وَالجُمْلَةُ الفِعْلِيَّةُ',
    titleEn: 'Nominal vs Verbal Sentences',
    badgeAr: 'الوحدة 1',
    badgeEn: 'Unit 1',
    ruleAr: 'الجُمْلَةُ الاسْمِيَّةُ تَبْدَأُ بِاسْمٍ وَتَتَكَوَّنُ مِنْ رُكْنَيْنِ رَئِيسَيْنِ: مُبْتَدَأ وَخَبَر، وَكِلاهُمَا مَرْفُوعٌ بِالضَّمَّةِ. أَمَّا الجُمْلَةُ الفِعْلِيَّةُ فَتَبْدَأُ بِفِعْلٍ وَتَتَكَوَّنُ مِنْ فِعْلٍ وَفَاعِلٍ (مَرْفُوع) وَمَفْعُولٍ بِهِ (مَنْصُوب).',
    ruleEn: 'A Nominal Sentence starts with a noun and consists of two primary pillars: Subject (Mubtada) and Predicate (Khabar), both in the nominative case with Damma. A Verbal Sentence starts with a verb and consists of a Verb, Subject Agent (Fa\'il, Marfoo\'), and Direct Object (Maf\'ul Bihi, Mansoob).',
    formulaAr: 'جملة اسمية: مُبْتَدَأ (مَرْفُوع) + خَبَر (مَرْفُوع) | جملة فعلية: فِعْل + فَاعِل (مَرْفُوع) + مَفْعُول بِهِ (مَنْصُوب)',
    formulaEn: 'Nominal: Subject (Damma) + Predicate (Damma) | Verbal: Verb + Doer (Damma) + Object (Fatha)',
    examples: [
      {
        sentenceAr: 'الكُرَةُ سَرِيعَةٌ',
        sentenceEn: 'The ball is fast',
        analysisAr: 'الكُرَةُ: مُبْتَدَأٌ مَرْفُوعٌ بِالضَّمَّةِ | سَرِيعَةٌ: خَبَرٌ مَرْفُوعٌ بِالضَّمَّةِ.',
        analysisEn: 'Al-Kuratu: Subject noun (Marfoo\' with Damma) | Saree\'atun: Predicate (Marfoo\' with Damma).'
      },
      {
        sentenceAr: 'قَذَفَ اللَّاعِبُ الكُرَةَ',
        sentenceEn: 'The player kicked the ball',
        analysisAr: 'قَذَفَ: فِعْلٌ مَاضٍ | اللَّاعِبُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ | الكُرَةَ: مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ.',
        analysisEn: 'Qadhafa: Past verb | Al-La\'ibu: Doer (Marfoo\' with Damma) | Al-Kurata: Object (Mansoob with Fatha).'
      }
    ]
  },
  {
    key: 'prepositions',
    titleAr: 'حُرُوفُ الجَرِّ وَالاسْمُ المَجْرُورُ',
    titleEn: 'Prepositions & Genitive Nouns',
    badgeAr: 'الوحدة 1',
    badgeEn: 'Unit 1',
    ruleAr: 'حُرُوفُ الجَرِّ تَدْخُلُ عَلَى الأَسْمَاءِ فَقَطْ وَتَجُرُّهَا بِالكَسْرَةِ الظَّاهِرَةِ. مِنْ أَشْهَرِهَا: (مِنْ، إِلَى، عَنْ، عَلَى، فِي، البَاء، الكَاف، اللَّام).',
    ruleEn: 'Prepositions prefix nouns exclusively and cause them to enter the genitive case, marked with a visible Kasra (-i sound). Key prepositions: Min (from), Ila (to), \'An (about), \'Ala (on), Fi (in), Bi- (with), Ka- (like), Li- (for).',
    formulaAr: 'حَرْفُ جَرٍّ + اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ',
    formulaEn: 'Preposition (Harf Jarr) + Genitive Noun (Ism Majroor with Kasra)',
    examples: [
      {
        sentenceAr: 'يَلْعَبُ الطُّلاَّبُ فِي المَلْعَبِ',
        sentenceEn: 'The students play on the pitch',
        analysisAr: 'فِي: حَرْفُ جَرٍّ | المَلْعَبِ: اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ.',
        analysisEn: 'Fi: Preposition | Al-Mal\'abi: Genitive noun with Kasra (-i).'
      },
      {
        sentenceAr: 'سَافَرَ الفَرِيقُ إِلَى دُبَيٍّ',
        sentenceEn: 'The team traveled to Dubai',
        analysisAr: 'إِلَى: حَرْفُ جَرٍّ | دُبَيٍّ: اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ.',
        analysisEn: 'Ila: Preposition | Dubayyin: Genitive noun with Kasra (-i).'
      }
    ]
  },
  {
    key: 'adverbs',
    titleAr: 'ظَرْفَا الزَّمَانِ وَالمَكَانِ (المَفْعُولُ فِيهِ)',
    titleEn: 'Adverbs of Time & Place (Maf\'ul Feeh)',
    badgeAr: 'الوحدة 2',
    badgeEn: 'Unit 2',
    ruleAr: 'اسْمٌ مَنْصُوبٌ بِالفَتْحَةِ يَدُلُّ عَلَى زَمَانِ وُقُوعِ الفِعْلِ (ظَرْفُ زَمَانٍ) أَوْ مَكَانِ وُقُوعِهِ (ظَرْفُ مَكَانٍ).',
    ruleEn: 'An accusative noun (Mansoob with Fatha) specifying the exact time an action took place (Adverb of Time) or the location where it occurred (Adverb of Place).',
    formulaAr: 'ظَرْفُ زَمَانٍ: (صَبَاحًا، مَسَاءً، لَيْلاً) | ظَرْفُ مَكَانٍ: (أَمَامَ، خَلْفَ، فَوْقَ، تَحْتَ)',
    formulaEn: 'Time: Sabahan (morning), Masa\'an (evening) | Place: Amama (in front), Khalfa (behind), Fawqa (above)',
    examples: [
      {
        sentenceAr: 'تَدَرَّبَ العَدَّاءُ مَسَاءً',
        sentenceEn: 'The runner trained in the evening',
        analysisAr: 'مَسَاءً: ظَرْفُ زَمَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ الظَّاهِرَةُ.',
        analysisEn: 'Masa\'an: Adverb of Time (Mansoob with Fatha).'
      },
      {
        sentenceAr: 'وَقَفَ الحَكَمُ أَمَامَ المَرْمَى',
        sentenceEn: 'The referee stood in front of the goal',
        analysisAr: 'أَمَامَ: ظَرْفُ مَكَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ الظَّاهِرَةُ.',
        analysisEn: 'Amama: Adverb of Place (Mansoob with Fatha).'
      }
    ]
  },
  {
    key: 'adjectives',
    titleAr: 'النَّعْتُ وَالمَنْعُوتُ (الصِّفَةُ وَالمَوْصُوفُ)',
    titleEn: 'Adjective Agreement (Na\'at & Man\'ut)',
    badgeAr: 'الوحدة 2',
    badgeEn: 'Unit 2',
    ruleAr: 'النَّعْتُ هُوَ تَابِعٌ يَذْكُرُ صِفَةً فِي اسْمٍ قَبْلَهُ (المَنْعُوت). يَتْبَعُ النَّعْتُ مَنْعُوتَهُ فِي 4 أُمُورٍ: الإِعْرَابِ (رَفْعًا وَنَصْبًا وَجَرًّا)، التَّعْرِيفِ وَالتَّنْكِيرِ، التَّذْكِيرِ وَالتَّأْنِيثِ، وَالعَدَدِ.',
    ruleEn: 'An adjective (Na\'at) describes a preceding noun (Man\'ut). The adjective must strictly agree with its noun across 4 dimensions: Grammatical case (Nominative/Accusative/Genitive), Definiteness (with/without "Al-"), Gender (Masc/Fem), and Number (Singular/Dual/Plural).',
    formulaAr: 'اسْمٌ مَنْعُوتٌ + اسْمٌ نَعْتٌ (مُطَابَقَةٌ كَامِلَةٌ فِي الحَرَكَةِ وَالتَّعْرِيفِ)',
    formulaEn: 'Noun (Man\'ut) + Adjective (Na\'at) [100% agreement in vowel case & definiteness]',
    examples: [
      {
        sentenceAr: 'شَاهَدْتُ المُبَارَاةَ الحَمَاسِيَّةَ',
        sentenceEn: 'I watched the thrilling match',
        analysisAr: 'الحَمَاسِيَّةَ: نَعْتٌ مَنْصُوبٌ بِالفَتْحَةِ يَتْبَعُ (المُبَارَاةَ) فِي التَّعْرِيفِ وَالنَّصْبِ.',
        analysisEn: 'Al-Hamasiyyata: Adjective (Mansoob with Fatha) agreeing with the definite object.'
      },
      {
        sentenceAr: 'هَذَا حِصَانٌ عَرَبِيٌّ أَصِيلٌ',
        sentenceEn: 'This is a purebred Arabian horse',
        analysisAr: 'عَرَبِيٌّ: نَعْتٌ مَرْفُوعٌ بِالضَّمَّةِ يَتْبَعُ (حِصَانٌ) فِي التَّنْكِيرِ وَالرَّفْعِ.',
        analysisEn: 'Arabiyyun: Adjective (Marfoo\' with Damma) agreeing in indefinite nominative case.'
      }
    ]
  },
  {
    key: 'demonstratives',
    titleAr: 'أَسْمَاءُ الإِشَارَةِ لِلْقَرِيبِ وَالبَعِيدِ',
    titleEn: 'Demonstrative Pronouns (Asma\' Al-Isharah)',
    badgeAr: 'الوحدة 3',
    badgeEn: 'Unit 3',
    ruleAr: 'أَسْمَاءُ الإِشَارَةِ أَلْفَاظٌ يُشَارُ بِهَا إِلَى شَيْءٍ مُعَيَّنٍ: هَذَا (مُفْرَد مُذَكَّر)، هَذِهِ (مُفْرَد مُؤَنَّث وَجَمْع غَيْر العَاقِل)، هَؤُلاءِ (جَمْع العَاقِل بِنَوْعَيْهِ).',
    ruleEn: 'Demonstratives point to specific referents: Hatha (singular masculine = "this"), Hathihi (singular feminine & non-human plurals = "this / these"), Ha\'ula\'i (human plurals for both genders = "these").',
    formulaAr: 'هَذَا (مُذَكَّر) | هَذِهِ (مُؤَنَّث + جَمْع غَيْر عَاقِل) | هَؤُلاءِ (جَمْع عَاقِل)',
    formulaEn: 'Hatha (Masc sing.) | Hathihi (Fem sing. + Non-human pl.) | Ha\'ula\'i (Human pl.)',
    examples: [
      {
        sentenceAr: 'هَذِهِ أَلْعَابٌ رِيَاضِيَّةٌ مُفِيدَةٌ',
        sentenceEn: 'These are beneficial sports games',
        analysisAr: 'هَذِهِ: اسْمُ إِشَارَةٍ لِجَمْعِ غَيْرِ العَاقِلِ (أَلْعَابٌ).',
        analysisEn: 'Hathihi: Demonstrative pronoun used for non-human plural ("Al\'ab").'
      },
      {
        sentenceAr: 'هَؤُلاءِ طُلاَّبٌ مُجْتَهِدُونَ',
        sentenceEn: 'These are diligent students',
        analysisAr: 'هَؤُلاءِ: اسْمُ إِشَارَةٍ لِجَمْعِ العَاقِلِ (طُلاَّبٌ).',
        analysisEn: 'Ha\'ula\'i: Demonstrative pronoun used for human plural ("Tullab").'
      }
    ]
  },
  {
    key: 'conjunctions',
    titleAr: 'حُرُوفُ العَطْفِ وَدَلالَاتُهَا',
    titleEn: 'Conjunction Particles (Huroof Al-\'Atf)',
    badgeAr: 'الوحدة 3',
    badgeEn: 'Unit 3',
    ruleAr: 'تَرْبِطُ بَيْنَ كَلِمَتَيْنِ وَيَتْبَعُ المَعْطُوفُ المَعْطُوفَ عَلَيْهِ فِي الإِعْرَابِ: الوَاوُ (لِلْمُشَارَكَةِ)، الفَاءُ (لِلتَّرْتِيبِ وَالسُّرْعَةِ)، ثُمَّ (لِلتَّرْتِيبِ مَعَ التَّرَاخِي فِي الوَقْتِ)، أَوْ (لِلتَّخْيِيرِ).',
    ruleEn: 'Conjunctions link two words where the joined word matches the previous word\'s vowel case: Waw (simultaneous partnership), Fa (immediate sequential order), Thumma (delayed sequence with time gap), Aw (choice or option).',
    formulaAr: 'مَعْطُوفٌ عَلَيْهِ + حَرْفُ عَطْفٍ (وَ، فَـ، ثُمَّ، أَوْ) + مَعْطُوفٌ (يَتْبَعُهُ فِي الإِعْرَابِ)',
    formulaEn: 'Base Word + Conjunction (Waw, Fa, Thumma, Aw) + Joined Word (matches case)',
    examples: [
      {
        sentenceAr: 'حَضَرَ زَايِدٌ وَرَاشِدٌ',
        sentenceEn: 'Zayed and Rashid arrived together',
        analysisAr: 'الوَاوُ: حَرْفُ عَطْفٍ لِلْمُشَارَكَةِ | رَاشِدٌ: مَعْطُوفٌ مَرْفُوعٌ بِالضَّمَّةِ.',
        analysisEn: 'Waw: Conjunction of partnership | Rashidun: Conjoined noun (Marfoo\' with Damma).'
      },
      {
        sentenceAr: 'رَمَى اللَّاعِبُ الكُرَةَ فَسَجَّلَ هَدَفًا',
        sentenceEn: 'The player threw the ball and instantly scored a goal',
        analysisAr: 'الفَاءُ: حَرْفُ عَطْفٍ يُفِيدُ التَّرْتِيبَ وَالسُّرْعَةَ المُبَاشِرَةَ.',
        analysisEn: 'Fa: Conjunction indicating immediate, instantaneous sequential action.'
      }
    ]
  }
];

export const GRADE_6_MINDMAP_CHAPTERS: MindmapChapter[] = [
  {
    id: 'chapter_1',
    titleAr: 'أَنَا إِمَارَاتِيٌّ وَأَعْتَزُّ بِهُوِيَّتِي',
    titleEn: 'I am Emirati & Proud of My Identity',
    unitAr: 'الهُوِيَّةُ وَالوَطَنُ',
    unitEn: 'National Identity & Homeland',
    pages: '6 - 15',
    color: '#2563EB',
    summaryAr: 'ترسيخ الانتماء للوطن، الاعتزاز بالهوية الإماراتية الأصيلة، سنع الأجداد، وقاعدة كان وأخواتها.',
    summaryEn: 'Strengthening patriotic belonging, pride in authentic Emirati identity, ancestral heritage, and Kana & its sisters grammar.',
    branches: [
      {
        titleAr: 'المفردات وجذور الكلمات',
        titleEn: 'Core Vocabulary & Roots',
        color: '#0284C7',
        items: [
          { ar: 'الهُوِيَّةُ', en: 'Identity', root: 'ه - و - ي', meaningAr: 'مَجْمُوعُ السِّمَاتِ وَالقِيَمِ الَّتِي تُمَيِّزُ الفَرْدَ وَالمُجْتَمَعَ.', meaningEn: 'The ensemble of traits, values, and traditions distinguishing an individual and society.' },
          { ar: 'الاعْتِزَازُ', en: 'Pride / Cherishing', root: 'ع - ز - ز', meaningAr: 'الشُّعُورُ بِالفَخْرِ وَالشَّرَفِ وَالكَرَامَةِ الوَطَنِيَّةِ.', meaningEn: 'A profound feeling of pride, honor, and national dignity.' },
          { ar: 'الانْتِمَاءُ', en: 'Belonging / Allegiance', root: 'ن - م - ي', meaningAr: 'الارْتِبَاطُ الوَثِيقُ بِالأَرْضِ وَالقِيَادَةِ وَالتُّرَاثِ.', meaningEn: 'Steadfast bond and loyalty to the land, leadership, and heritage.' },
          { ar: 'السَّنَعُ الإِمَارَاتِيُّ', en: 'Emirati San\'a (Etiquette)', root: 'س - ن - ع', meaningAr: 'الآدَابُ وَالعَادَاتُ وَالأَخْلَاقُ الحَمِيدَةُ المُتَوَارَثَةُ.', meaningEn: 'Traditional cultural etiquette, chivalry, and virtuous manners passed down generations.' }
        ]
      },
      {
        titleAr: 'حقائق ومحاور الدرس',
        titleEn: 'Reading Facts & National Values',
        color: '#059669',
        items: [
          { ar: 'قِيَمُ الوَطَنِ: رُوحُ الاتِّحَادِ', en: 'National Values: Spirit of the Union', meaningAr: 'تَأْسِيسُ دَوْلَةِ الإِمَارَاتِ عَلَى قِيَمِ الوَحْدَةِ وَالعَطَاءِ.', meaningEn: 'Founding of the UAE on principles of unity, cohesion, and benevolence.' },
          { ar: 'عَلَمُ الإِمَارَاتِ: رَمْزُ السِّيَادَةِ', en: 'UAE Flag: Symbol of Sovereignty', meaningAr: 'الأَلْوَانُ الأَرْبَعَةُ: الأَحْمَرُ، الأَخْضَرُ، الأَبْيَضُ، وَالأَسْوَدُ.', meaningEn: 'The 4 Pan-Arab colors representing courage, hope, purity, and resolve.' }
        ]
      },
      {
        titleAr: 'القواعد المرتبطة: كَانَ وَأَخَوَاتُهَا',
        titleEn: 'Grammar: Kana & Its Sisters',
        color: '#7C3AED',
        items: [
          { ar: 'كَانَ الوَطَنُ عَزِيزًا فِي قُلُوبِنَا.', en: 'The homeland was cherished in our hearts.', meaningEn: 'Kana enters nominal sentence, keeps noun marfoo\' and makes predicate mansoob.' },
          { ar: 'أَصْبَحَ العِلْمُ سِلَاحَ الأَجْيَالِ.', en: 'Knowledge became the weapon of generations.', meaningEn: 'Asbaha acts like Kana, making subject marfoo\' and predicate mansoob.' }
        ]
      }
    ]
  }
];

export const GRADE_7_MINDMAP_CHAPTERS: MindmapChapter[] = [
  {
    id: 'chapter_1',
    titleAr: 'وَثِيقَةُ الأُخُوَّةِ الإِنْسَانِيَّةِ فِي أَبُوظَبِي',
    titleEn: 'Document on Human Fraternity',
    unitAr: 'التَّسَامُحُ وَالأُخُوَّةُ الإِنْسَانِيَّةُ',
    unitEn: 'Tolerance & Human Fraternity',
    pages: '6 - 15',
    color: '#059669',
    summaryAr: 'القيم العالمية لوثيقة الأخوة الإنسانية الموقعة في أبوظبي، ورسالة الإمارات في التعايش والسلام وقاعدة إن وأخواتها.',
    summaryEn: 'Universal principles of the Human Fraternity Document signed in Abu Dhabi, promoting peace, global coexistence, and Inna & its sisters grammar.',
    branches: [
      {
        titleAr: 'مفردات التسامح والإخاء',
        titleEn: 'Tolerance Vocabulary',
        color: '#0284C7',
        items: [
          { ar: 'التَّسَامُحُ', en: 'Tolerance & Forbearance', root: 'س - م - ح', meaningAr: 'قَبُولُ الآخَرِ وَاحْتِرَامُ الِاخْتِلَافِ.', meaningEn: 'Embracing diversity and mutual respect.' },
          { ar: 'الأُخُوَّةُ', en: 'Fraternity / Brotherhood', root: 'أ - خ - و', meaningAr: 'الرَّابِطَةُ الإِنْسَانِيَّةُ الجَامِعَةُ بَيْنَ البَشَرِ.', meaningEn: 'Universal bond of shared humanity.' },
          { ar: 'التَّعَايُشُ', en: 'Coexistence', root: 'ع - ي - ش', meaningAr: 'العَيْشُ المُشْتَرَكُ فِي سَلَامٍ وَأَمَانٍ.', meaningEn: 'Harmonious mutual living in safety and respect.' }
        ]
      },
      {
        titleAr: 'المحاور الإنسانية والوطنية',
        titleEn: 'Humanitarian & National Pillars',
        color: '#059669',
        items: [
          { ar: 'وَثِيقَةُ أَبُوظَبِي: نِدَاءُ السَّلَامِ', en: 'Abu Dhabi Document: Call for Peace', meaningAr: 'تَوْقِيعُ الوَثِيقَةِ التَّارِيخِيَّةِ لِتَعْزِيزِ الحِوَارِ بَيْنَ الأَدْيَانِ.', meaningEn: 'Historic signing to foster interfaith dialogue and fraternity.' },
          { ar: 'دَوْلَةُ الإِمَارَاتِ: حَاضِنَةُ التَّسَامُحِ', en: 'UAE: Global Oasis of Tolerance', meaningAr: 'احْتِضَانُ أَكْثَرَ مِنْ 200 جِنْسِيَّةٍ فِي تَنَاغُمٍ وَتَعَايُشٍ.', meaningEn: 'Embracing more than 200 nationalities in harmony and solidarity.' }
        ]
      },
      {
        titleAr: 'القواعد المرتبطة: إِنَّ وَأَخَوَاتُهَا',
        titleEn: 'Grammar: Inna & Its Sisters',
        color: '#7C3AED',
        items: [
          { ar: 'إِنَّ التَّسَامُحَ قِيمَةٌ نَبِيلَةٌ.', en: 'Verily, tolerance is a noble value.', meaningEn: 'Inna makes the noun accusative (Tasamuh-a) and predicate nominative (Qeemat-un).' },
          { ar: 'لَعَلَّ السَّلَامَ يَعُمُّ العَالَمَ.', en: 'May peace prevail across the world.', meaningEn: 'La\'alla operates like Inna in expressing hopeful desire.' }
        ]
      }
    ]
  }
];

export const GRADE_8_MINDMAP_CHAPTERS: MindmapChapter[] = [
  {
    id: 'chapter_1',
    titleAr: 'أَبُو الطَّيِّبِ المُتَنَبِّي شَاعِرُ الحِكْمَةِ',
    titleEn: 'Al-Mutanabbi: Poet of Wisdom',
    unitAr: 'فُرْسَانُ الكَلِمَةِ وَرَوَائِعُ الأَدَبِ',
    unitEn: 'Masterpieces of Arabic Literature',
    pages: '6 - 15',
    color: '#7C3AED',
    summaryAr: 'روائع شعر أبي الطيب المتنبي، فصاحته، وحكمته الخالدة التي سارت بها الركبان.',
    summaryEn: 'Immortal literary masterworks of Abu al-Tayyib al-Mutanabbi, classical eloquence, and proverbial wisdom.',
    branches: [
      {
        titleAr: 'المفردات البلاغية وجذور الكلمات',
        titleEn: 'Rhetorical Vocabulary & Roots',
        color: '#0284C7',
        items: [
          { ar: 'الفَصَاحَةُ', en: 'Eloquence', root: 'ف - ص - ح', meaningAr: 'خُلُوُّ الكَلَامِ مِنَ العُيُوبِ وَوُضُوحُ الدَّلَالَةِ.', meaningEn: 'Clarity and supreme purity of speech.' },
          { ar: 'الحِكْمَةُ', en: 'Wisdom', root: 'ح - ك - م', meaningAr: 'وَضْعُ الشَّيْءِ فِي مَوْضِعِهِ المُنَاسِبِ.', meaningEn: 'Sound judgment and profound philosophical insight.' }
        ]
      },
      {
        titleAr: 'القواعد: الفِعْلُ المَبْنِيُّ لِلْمَجْهُولِ',
        titleEn: 'Grammar: Passive Voice & Pro-Agent',
        color: '#7C3AED',
        items: [
          { ar: 'نُظِّمَتِ القَصِيدَةُ بِإِبْدَاعٍ.', en: 'The poem was composed with brilliance.', meaningEn: 'Direct object takes nominative pro-agent role.' }
        ]
      }
    ]
  }
];

export function getFallbackMindmapChapters(grade: number): MindmapChapter[] {
  if (grade === 6) return GRADE_6_MINDMAP_CHAPTERS;
  if (grade === 7) return GRADE_7_MINDMAP_CHAPTERS;
  if (grade === 8) return GRADE_8_MINDMAP_CHAPTERS;
  return MINDMAP_CHAPTERS;
}

