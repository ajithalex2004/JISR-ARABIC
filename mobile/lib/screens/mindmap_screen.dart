import 'package:flutter/material.dart';
import '../arab_english_service.dart';

/// Interactive Mindmaps and Grammar Flowcharts for UAE MoE Arabic Curriculum.
/// Includes visual concept trees for each lesson and syntax decision flowcharts for grammar topics.
/// Grounded for non-native Arabic learners with bilingual Arabic-English translations below every concept.
class MindmapsScreen extends StatefulWidget {
  final bool isArabic;
  final int initialGrade;
  final Function(String text)? onVocalize;
  final Function(String query)? onAskFahim;
  final VoidCallback onBack;

  const MindmapsScreen({
    super.key,
    required this.isArabic,
    this.initialGrade = 5,
    this.onVocalize,
    this.onAskFahim,
    required this.onBack,
  });

  @override
  State<MindmapsScreen> createState() => _MindmapsScreenState();
}

class _MindmapsScreenState extends State<MindmapsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late int _selectedGrade;
  int _selectedChapterIndex = 0;
  String _selectedGrammarTopicKey = 'sentence_types';

  // UAE MoE Class 5 Term 1 Chapters
  final List<Map<String, dynamic>> _chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'أَلْعَابُ الكُرَةِ',
      'titleEn': 'Ball Games',
      'unitAr': 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
      'unitEn': 'Sports and Hobbies',
      'icon': Icons.sports_soccer_rounded,
      'color': const Color(0xFF2563EB),
      'pages': '6 - 15',
      'summaryAr': 'أنواع الكرات، كرة القدم الساحرة المستديرة، مخطط الأصابع الخمسة، وروابط التراكيب اللغوية.',
      'summaryEn': 'Ball categories, football rules & pitch specs, 5-finger framework, and syntactic connectives.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الكُرَةُ (ج: كُرَات)',
              'en': 'The Ball (pl. Balls)',
              'root': 'ك - ر - ر (K-R-R)',
              'pattern': 'فُعْلَة (Fu\'lah)',
              'meaningAr': 'كُلُّ جِسْمٍ مُسْتَدِيرٍ يُسْتَخْدَمُ فِي اللَّعِبِ.',
              'meaningEn': 'Any spherical / round body used for sports.',
            },
            {
              'ar': 'مُسْتَدِيرٌ',
              'en': 'Spherical / Round',
              'root': 'د - و - ر (D-W-R)',
              'pattern': 'مُسْتَفْعِل (Mustaf\'il)',
              'meaningAr': 'عَلَى هَيْئَةِ دَائِرَةٍ مُنْتَظَمَةٍ.',
              'meaningEn': 'In the circular shape of a round ball.',
            },
            {
              'ar': 'جَمَاعِيٌّ (عكس: فَرْدِيٌّ)',
              'en': 'Team / Collective (opp. Individual)',
              'root': 'ج - م - ع (J-M-A\')',
              'pattern': 'فَعَالِيّ (Fa\'aaliyy)',
              'meaningAr': 'نَشَاطٌ رِيَاضِيٌّ يَشْتَرِكُ فِيهِ فَرِيقٌ كَامِلٌ.',
              'meaningEn': 'A sport involving collaborative teamwork.',
            },
            {
              'ar': 'المُبَارَاةُ (ج: مُبَارَيَات)',
              'en': 'The Match / Tournament',
              'root': 'ب - ر - ي (B-R-Y)',
              'pattern': 'مُفَاعَلَة (Mufa\'alah)',
              'meaningAr': 'مُنَافَسَةٌ رِيَاضِيَّةٌ مُنَظَّمَةٌ بَيْنَ فَرِيقَيْنِ.',
              'meaningEn': 'A structured athletic fixture between two teams.',
            },
          ],
        },
        {
          'titleAr': 'حقائق ومواصفات الدرس',
          'titleEn': 'Reading Facts & Specifications',
          'icon': Icons.analytics_outlined,
          'color': const Color(0xFF059669),
          'items': [
            {
              'ar': 'اللَّقَبُ: السَّاحِرَةُ المُسْتَدِيرَةُ',
              'en': 'Moniker: The Round Magician / Enchantress',
              'meaningAr': 'سَمَّوْهَا السَّاحِرَةَ المُسْتَدِيرَةَ لِأَنَّهَا سَحَرَتْ عُقُولَ أَكْثَرَ مِنْ مِلْيَارِ مُتَابِعٍ.',
              'meaningEn': 'Football is dubbed "The Round Magician" because it enchants over 1 billion fans.',
            },
            {
              'ar': 'عَدَدُ اللاعِبِينَ: 11 لاعِبًا لِكُلِّ فَرِيقٍ',
              'en': 'Squad Size: 11 players per team',
              'meaningAr': 'يَتَكَوَّنُ الفَرِيقَانِ مِنْ 22 لاعِبًا عَلَى أَرْضِ المَلْعَبِ.',
              'meaningEn': 'Total of 22 players on the pitch during match play.',
            },
            {
              'ar': 'المَلْعَبُ: قِطْعَةُ أَرْضٍ مُسْتَطِيلَةٌ',
              'en': 'Pitch: Rectangular turfed grass ground',
              'meaningAr': 'طُولُ المَلْعَبِ بَيْنَ 100 إِلَى 110م، وَعَرْضُهُ 64 إِلَى 75م.',
              'meaningEn': 'Length: 100-110m, Width: 64-75m with green grass turf.',
            },
            {
              'ar': 'مُدَّةُ المُبَارَاةِ: شَوْطَانِ (45 دَقِيقَة لِكُلِّ شَوْطٍ)',
              'en': 'Duration: 2 halves of 45 mins each',
              'meaningAr': 'تَفْصِلُ بَيْنَهُمَا اسْتِرَاحَةٌ مُدَّتُهَا 15 دَقِيقَةً، وَيُشْرِفُ عَلَيْهَا 4 حُكَّامٍ.',
              'meaningEn': 'Includes a 15-minute intermission, officiated by 4 referees.',
            },
          ],
        },
        {
          'titleAr': 'مخطط الأصابع الخمسة للفهم',
          'titleEn': '5-Finger Questioning Framework',
          'icon': Icons.pan_tool_outlined,
          'color': const Color(0xFFD97706),
          'items': [
            {
              'ar': 'الإِبْهَامُ: لِمَاذَا تُفَضِّلُ هَذِهِ اللُّعْبَةَ؟',
              'en': 'Thumb: Why do you prefer this game?',
              'meaningAr': 'لِأَنَّهَا تُعَلِّمُنَا التَّعَاوُنَ الجَمَاعِيَّ وَاللِّيَاقَةَ البَدَنِيَّةَ.',
              'meaningEn': 'Because it fosters teamwork, collective cooperation, and stamina.',
            },
            {
              'ar': 'السَّبَّابَةُ: مَتَى تَعَلَّمْتَهَا؟',
              'en': 'Index: When did you learn it?',
              'meaningAr': 'تَعَلَّمْتُهَا فِي المَدْرَسَةِ مُنْذُ عَامَيْنِ مَعَ مُعَلِّمِ الرِّيَاضَةِ.',
              'meaningEn': 'I learned it at school two years ago with my PE coach.',
            },
            {
              'ar': 'الوُسْطَى: مَا المَخَاطِرُ؟',
              'en': 'Middle: What hazards / risks exist?',
              'meaningAr': 'التَّصَادُمُ، السُّقُوطُ، وَإِجْهَادُ العَضَلَاتِ عِنْدَ الإِهْمَالِ.',
              'meaningEn': 'Collisions, falling down, and muscle strain if careless.',
            },
            {
              'ar': 'البِنْصِرُ: أَيْنَ تَلْعَبُ؟',
              'en': 'Ring: Where is it played?',
              'meaningAr': 'فِي مَلْعَبِ المَدْرَسَةِ أَوْ فِي الصَّالَةِ الرِّيَاضِيَّةِ المُغْلَقَةِ.',
              'meaningEn': 'At the school pitch or inside the indoor sports hall.',
            },
            {
              'ar': 'الخِنْصِرُ: كَمْ عَدَدُ اللاعِبِينَ؟',
              'en': 'Pinky: How many players participate?',
              'meaningAr': '11 لاعِبًا فِي كُرَةِ القَدَمِ، وَ5 فِي كُرَةِ السَّلَّةِ.',
              'meaningEn': '11 players in football, and 5 players in basketball.',
            },
          ],
        },
        {
          'titleAr': 'التراكيب والروابط اللغوية',
          'titleEn': 'Cohesive Sentence Connectives',
          'icon': Icons.link_rounded,
          'color': const Color(0xFF7C3AED),
          'items': [
            {
              'ar': 'يَجِبُ أَنْ...',
              'en': 'Must / It is necessary that...',
              'meaningAr': 'يَجِبُ أَنْ يَتَدَرَّبَ الفَرِيقُ بِانْتِظَامٍ لِتَحْقِيقِ الفَوْزِ.',
              'meaningEn': 'The team must train regularly to achieve victory.',
            },
            {
              'ar': 'كَذَلِكَ...',
              'en': 'Likewise / Similarly / As well...',
              'meaningAr': 'يَحْتَاجُ اللاعِبُ لِيَاقَةً، وَكَذَلِكَ خُطَّةً تكتيكية ذَكِيَّةً.',
              'meaningEn': 'The player needs stamina, and likewise a tactical gameplan.',
            },
            {
              'ar': 'كَمَا أَنَّ...',
              'en': 'Furthermore / In addition / Just as...',
              'meaningAr': 'كَمَا أَنَّ الرُّوحَ الرِّيَاضِيَّةَ أَهَمُّ مِنْ مُجَرَّدِ تَسْجِيلِ الأَهْدَافِ.',
              'meaningEn': 'Furthermore, sportsmanship is far more important than just goals.',
            },
            {
              'ar': 'عَلَى الرَّغْمِ مِنْ...',
              'en': 'Despite / Although (Concession)...',
              'meaningAr': 'عَلَى الرَّغْمِ مِنْ صُعُوبَةِ المُبَارَاةِ، اسْتَطَاعَ فَرِيقُنَا الفَوْزَ.',
              'meaningEn': 'Despite the toughness of the match, our team clinched the win.',
            },
          ],
        },
        {
          'titleAr': 'الهوية الإماراتية والروح الرياضية',
          'titleEn': 'UAE Identity & National Values',
          'icon': Icons.flag_rounded,
          'color': const Color(0xFF0D9488),
          'items': [
            {
              'ar': 'الرِّيَاضَاتُ التُّرَاثِيَّةُ فِي الإِمَارَاتِ',
              'en': 'UAE Traditional Heritage Sports',
              'meaningAr': 'سِبَاقَاتُ الهَجَنِ، الصَّيْدُ بِالصُّقُورِ، وَالتَّجْدِيفُ التُّرَاثِيُّ.',
              'meaningEn': 'Camel racing, falconry hunting, and heritage wooden boat rowing.',
            },
            {
              'ar': 'أَخْلَاقُ الفَارِسِ وَالرُّوحُ الرِّيَاضِيَّةُ',
              'en': 'Sportsmanship & Rider Ethics',
              'meaningAr': 'احْتِرَامُ المُنَافِسِ، تَقَبُّلُ النَّتِيجَةِ، وَالتَّوَاضُعُ عِنْدَ الانْتِصَارِ.',
              'meaningEn': 'Respecting opponents, gracious acceptance, and humility in victory.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_2',
      'titleAr': 'رُكُوبُ الخَيْلِ',
      'titleEn': 'Horse Riding (Equestrian)',
      'unitAr': 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
      'unitEn': 'Sports and Hobbies',
      'icon': Icons.pets_rounded,
      'color': const Color(0xFFD97706),
      'pages': '16 - 25',
      'summaryAr': 'رياضة الفروسية الأصيلة، صفات الخيل العربي، أدوات الفارس، والشجاعة والاعتزاز بالتراث.',
      'summaryEn': 'Arabian horse heritage, equestrian gear, rider bravery, and historical cultural pride.',
      'branches': [
        {
          'titleAr': 'مفردات الفروسية',
          'titleEn': 'Equestrian Vocabulary',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الجَوَادُ (ج: جِيَاد / خُيُول)',
              'en': 'The Steed / Purebred Horse',
              'root': 'ج - و - د (J-W-D)',
              'meaningAr': 'الحِصَانُ العَرَبِيُّ الأَصِيلُ عَالِي النَّسَبِ وَالسُّرْعَةِ.',
              'meaningEn': 'Noble purebred Arabian horse celebrated for speed and beauty.',
            },
            {
              'ar': 'السَّرْجُ وَاللِّجَامُ',
              'en': 'Saddle & Bridle',
              'root': 'س - ر - ج (S-R-J)',
              'meaningAr': 'أَدَوَاتٌ تُوضَعُ عَلَى ظَهْرِ الجَوَادِ وَفَمِهِ لِلتَّحَكُّمِ بِهِ.',
              'meaningEn': 'Riding leather equipment placed on horse back and bit for control.',
            },
            {
              'ar': 'المِضْمَارُ',
              'en': 'The Racetrack / Arena',
              'root': 'ض - م - ر (D-M-R)',
              'meaningAr': 'المَكَانُ المُخَصَّصُ لِسِبَاقَاتِ السُّرْعَةِ وَقَفْزِ الحَوَاجِزِ.',
              'meaningEn': 'The specialized circular track for flat racing and jumping.',
            },
          ],
        },
        {
          'titleAr': 'القواعد المرتبطة: الفعل الماضي والفاعل',
          'titleEn': 'Grammar: Past Verb & Agent (Fa\'il)',
          'icon': Icons.alt_route_rounded,
          'color': const Color(0xFF7C3AED),
          'items': [
            {
              'ar': 'رَكِبَ الفَارِسُ الجَوَادَ',
              'en': 'The knight rode the steed',
              'meaningAr': 'رَكِبَ: فِعْلٌ مَاضٍ مَبْنِيٌّ عَلَى الفَتْحِ | الفَارِسُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ.',
              'meaningEn': 'Rakiba: Past Verb (built on Fatha) | Al-Farisu: Doer (Marfoo\' with Damma).',
            },
            {
              'ar': 'تَطَابُقُ الفِعْلِ مَعَ الفَاعِلِ تَأْنِيثًا',
              'en': 'Feminine Verb-Agent Agreement',
              'meaningAr': 'رَكِبَتْ فَاطِمَةُ المُهْرَةَ (إِضَافَةُ تَاءِ التَّأْنِيثِ السَّاكِنَةِ للفِعْلِ).',
              'meaningEn': 'Rakibat Fatima: Adding quiescent Ta (تْ) when the subject is feminine.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_3',
      'titleAr': 'الجَرْيُ',
      'titleEn': 'Running (Athletics)',
      'unitAr': 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
      'unitEn': 'Sports and Hobbies',
      'icon': Icons.directions_run_rounded,
      'color': const Color(0xFF10B981),
      'pages': '26 - 35',
      'summaryAr': 'سباقات الجري السريع والماراثون، التنفس الصحيح، واللياقة البدنية وصحة القلب.',
      'summaryEn': 'Sprint races, marathon endurance, correct breathing technique, and cardiovascular stamina.',
      'branches': [
        {
          'titleAr': 'مفردات ألعاب القوى',
          'titleEn': 'Athletics & Track Vocabulary',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'السِّبَاقُ السَّرِيعُ (السبرنت)',
              'en': 'The Sprint (Short distance race)',
              'meaningAr': 'الجَرْيُ بِأَقْصَى سُرْعَةٍ لِمَسَافَاتٍ قَصِيرَةٍ (100م - 200م).',
              'meaningEn': 'Explosive high-speed running over short distances (100-200m).',
            },
            {
              'ar': 'المَارَاثُونُ (المَسَافَاتُ الطَّوِيلَةُ)',
              'en': 'The Marathon (Long distance endurance)',
              'meaningAr': 'الجَرْيُ لِمَسَافَاتٍ طَوِيلَةٍ مَعَ تَنْظِيمِ التَّنَفُّسِ.',
              'meaningEn': 'Endurance racing over 42km requiring rhythm and hydration.',
            },
          ],
        },
        {
          'titleAr': 'القواعد المرتبطة: ظرفا الزمان والمكان',
          'titleEn': 'Grammar: Adverbs of Time & Place',
          'icon': Icons.schedule_rounded,
          'color': const Color(0xFF7C3AED),
          'items': [
            {
              'ar': 'يَجْرِي العَدَّاءُ صَبَاحًا',
              'en': 'The runner runs in the morning',
              'meaningAr': 'صَبَاحًا: ظَرْفُ زَمَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ.',
              'meaningEn': 'Sabahan: Adverb of Time (Mansoob with Fatha).',
            },
            {
              'ar': 'تَدَرَّبَ الفَرِيقُ أَمَامَ المِنَصَّةِ',
              'en': 'The team trained in front of the podium',
              'meaningAr': 'أَمَامَ: ظَرْفُ مَكَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ.',
              'meaningEn': 'Amama: Adverb of Place (Mansoob with Fatha).',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_4',
      'titleAr': 'الفُنُونُ وَالإِبْدَاعُ',
      'titleEn': 'Arts & Creativity',
      'unitAr': 'الفُنُونُ وَالإِبْدَاعُ',
      'unitEn': 'Arts and Creativity',
      'icon': Icons.palette_rounded,
      'color': const Color(0xFFEC4899),
      'pages': '36 - 45',
      'summaryAr': 'الرسم، الخط العربي والزخرفة الإسلامية، تناسق الألوان، ومعارض اللوحات الفنية.',
      'summaryEn': 'Painting, Arabic calligraphy, Islamic geometry, color palettes, and gallery exhibits.',
      'branches': [
        {
          'titleAr': 'مصطلحات الفنون',
          'titleEn': 'Fine Arts Terminology',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الخَطُّ العَرَبِيُّ (الكُوفِيّ، الرُّقْعَة، النَّسْخ)',
              'en': 'Arabic Calligraphy Styles (Kufi, Ruq\'ah, Naskh)',
              'meaningAr': 'فَنُّ كِتَابَةِ الحُرُوفِ العَرَبِيَّةِ بِأَشْكَالٍ هَنْدَسِيَّةٍ جَمِيلَةٍ.',
              'meaningEn': 'The art of lettering Arabic scripts with rhythmic geometric grace.',
            },
            {
              'ar': 'اللَّوْحَةُ الزَّيْتِيَّةُ',
              'en': 'Oil Painting Canvas',
              'meaningAr': 'رَسْمٌ إِبْدَاعِيٌّ يُبْرِزُ الضَّوْءَ وَالظِّلالَ بِأَلْوَانِ الزَّيْتِ.',
              'meaningEn': 'Creative visual art utilizing oil paints and chiaroscuro.',
            },
          ],
        },
        {
          'titleAr': 'القواعد: النعت والمنعوت (الصفة والموصوف)',
          'titleEn': 'Grammar: Adjective Agreement (Na\'at & Man\'ut)',
          'icon': Icons.brush_rounded,
          'color': const Color(0xFF7C3AED),
          'items': [
            {
              'ar': 'رَسَمْتُ لَوْحَةً جَمِيلَةً',
              'en': 'I painted a beautiful painting',
              'meaningAr': 'جَمِيلَةً: نَعْتٌ مَنْصُوبٌ يَتْبَعُ المَنْعُوتَ (لَوْحَةً) فِي التَّنْكِيرِ وَالإِعْرَابِ.',
              'meaningEn': 'Jameelatan: Adjective matching the indefinite noun in Fatha.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_5',
      'titleAr': 'القِرَاءَةُ نُورُ العَقْلِ',
      'titleEn': 'Reading: Light of the Mind',
      'unitAr': 'الفُنُونُ وَالإِبْدَاعُ',
      'unitEn': 'Arts and Creativity',
      'icon': Icons.local_library_rounded,
      'color': const Color(0xFF6366F1),
      'pages': '46 - 55',
      'summaryAr': 'أهمية المطالعة، مبادرة تحدي القراءة العربي، زيارة المكتبات العامة، وتلخيص القصص.',
      'summaryEn': 'Value of reading, Arab Reading Challenge initiative, library research, and story summaries.',
      'branches': [
        {
          'titleAr': 'مفردات عالم الكتب',
          'titleEn': 'Literary & Reading Vocabulary',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الفِهْرِسُ وَالمُعْجَمُ',
              'en': 'Table of Contents & Lexicon / Dictionary',
              'meaningAr': 'دَلِيلُ البَحْثِ عَنِ المَعَانِي وَالمَصَادِرِ فِي الكُتُبِ.',
              'meaningEn': 'Reference tools to search terms and verify word meanings.',
            },
            {
              'ar': 'المُطَالَعَةُ الحُرَّةُ',
              'en': 'Independent Extracurricular Reading',
              'meaningAr': 'قِرَاءَةُ الكُتُبِ وَالقِصَصِ لِتَوْسِيعِ المَعَارِفِ وَالمَدَارِكِ.',
              'meaningEn': 'Voluntary self-directed reading to expand intellectual breadth.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_6',
      'titleAr': 'فِي المَدْرَسَةِ',
      'titleEn': 'At School',
      'unitAr': 'حَيَاتُنَا المَدْرَسِيَّةُ',
      'unitEn': 'Our School Life',
      'icon': Icons.school_rounded,
      'color': const Color(0xFF0891B2),
      'pages': '56 - 65',
      'summaryAr': 'البيئة المدرسية، احترام المعلمين والزملاء، المختبرات العلمية، والإذاعة المدرسية.',
      'summaryEn': 'School community, honoring educators, lab experiments, and morning broadcasts.',
      'branches': [
        {
          'titleAr': 'مرافق المدرسة والأنشطة',
          'titleEn': 'Campus Facilities & Morning Routine',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'المُخْتَبَرُ العِلْمِيُّ',
              'en': 'The Science Laboratory',
              'meaningAr': 'مَكَانُ إِجْرَاءِ التَّجَارِبِ الاسْتِكْشَافِيَّةِ العِلْمِيَّةِ.',
              'meaningEn': 'Facility equipped for scientific experiments and investigations.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_7',
      'titleAr': 'فِي البَيْتِ',
      'titleEn': 'At Home',
      'unitAr': 'حَيَاتُنَا المَدْرَسِيَّةُ',
      'unitEn': 'Our School Life',
      'icon': Icons.cottage_rounded,
      'color': const Color(0xFF8B5CF6),
      'pages': '66 - 75',
      'summaryAr': 'الترابط الأسري، بر الوالدين، تنظيم الوقت وأداء الواجبات المنزلية، والتعاون بين الإخوة.',
      'summaryEn': 'Family bonding, filial piety, homework schedule management, and sibling cooperation.',
      'branches': [
        {
          'titleAr': 'قيم الأسرة والترابط',
          'titleEn': 'Home & Kinship Values',
          'icon': Icons.family_restroom_rounded,
          'color': const Color(0xFF059669),
          'items': [
            {
              'ar': 'بِرُّ الوَالِدَيْنِ',
              'en': 'Honoring Parents (Filial Piety)',
              'meaningAr': 'طَاعَتُهُمَا وَمُعَامَلَتُهُمَا بِأَدَبٍ وَإِحْسَانٍ وَلِينٍ.',
              'meaningEn': 'Obeying and honoring parents with gentle compassion.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_8',
      'titleAr': 'طَعَامِي الصِّحِّي',
      'titleEn': 'My Healthy Food',
      'unitAr': 'الصِّحَّةُ وَالغِذَاءُ',
      'unitEn': 'Health and Nutrition',
      'icon': Icons.restaurant_rounded,
      'color': const Color(0xFFF59E0B),
      'pages': '76 - 85',
      'summaryAr': 'الهرم الغذائي، الفواكه والخضراوات، الوجبات المتوازنة، وأضرار الوجبات السريعة والسكريات.',
      'summaryEn': 'Nutritional food pyramid, fruit & veg vitamins, balanced meals, avoiding junk food.',
      'branches': [
        {
          'titleAr': 'مفردات الغذاء الصحي',
          'titleEn': 'Nutrition & Wellness Terms',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الغِذَاءُ المُتَوَازِنُ',
              'en': 'Balanced Diet',
              'meaningAr': 'وَجَبَاتٌ تَمُدُّ الجِسْمَ بِالفِيتَامِينَاتِ وَالأَلْيَافِ وَالمَعَادِنِ.',
              'meaningEn': 'Meals providing essential macro and micronutrients for vitality.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_9',
      'titleAr': 'مَلَابِسِي وَهُوِيَّتِي',
      'titleEn': 'My Clothes & Heritage',
      'unitAr': 'الهُوِيَّةُ وَالتُّرَاثُ',
      'unitEn': 'Identity and Heritage',
      'icon': Icons.checkroom_rounded,
      'color': const Color(0xFF0D9488),
      'pages': '86 - 95',
      'summaryAr': 'الزي الوطني الإماراتي (الكندورة، الغترة، والعقال)، ملابس الفصول الأربعة، وأناقة المظهر.',
      'summaryEn': 'Emirati national dress (Kandura, Ghutra, Agal), four seasonal clothes, neat presentation.',
      'branches': [
        {
          'titleAr': 'مفردات الزي الإماراتي الأصيل',
          'titleEn': 'Emirati Traditional Dress Terms',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'الكَنْدُورَةُ الإِمَارَاتِيَّةُ',
              'en': 'Emirati Kandura (Thobe)',
              'meaningAr': 'الثَّوْبُ الوَطَنِيُّ التُّرَاثِيُّ الأَنِيقُ بِدُونِ يَاقَةٍ.',
              'meaningEn': 'The iconic ankle-length white collarless robe of UAE heritage.',
            },
          ],
        },
      ],
    },
    {
      'id': 'chapter_10',
      'titleAr': 'وَقْتُ المَرَحِ وَالعُطْلَةُ',
      'titleEn': 'Fun Time & Vacations',
      'unitAr': 'الهُوِيَّةُ وَالتُّرَاثُ',
      'unitEn': 'Identity and Heritage',
      'icon': Icons.celebration_rounded,
      'color': const Color(0xFFE11D48),
      'pages': '96 - 105',
      'summaryAr': 'استثمار العطلة الصيفية، الرحلات البرية والبحرية، التخييم في صحراء الإمارات، وتنمية المهارات.',
      'summaryEn': 'Holiday camps, desert safari camping in UAE dunes, marine trips, and personal skill development.',
      'branches': [
        {
          'titleAr': 'أنشطة العطلة والمرح',
          'titleEn': 'Holiday Activities & Desert Camping',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {
              'ar': 'التَّخْيِيمُ فِي البَرِّ (الرِّحْلاتُ البَرِّيَّةُ)',
              'en': 'Desert Safari & Dune Camping',
              'meaningAr': 'الاسْتِمْتَاعُ بِجَمَالِ كُثْبَانِ الرِّمَالِ الذَّهَبِيَّةِ فِي الإِمَارَاتِ.',
              'meaningEn': 'Appreciating the beauty of golden sand dunes in the UAE desert.',
            },
          ],
        },
      ],
    },
  ];

  @override
  void initState() {
    super.initState();
    _selectedGrade = widget.initialGrade;
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _speak(String text) {
    if (widget.onVocalize != null) {
      widget.onVocalize!(text);
    }
  }

  @override
  Widget build(BuildContext context) {
    final activeChapter = _chapters[_selectedChapterIndex];

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF1E293B)),
          onPressed: widget.onBack,
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF6C5CE7), Color(0xFF8B5CF6)],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.account_tree_rounded, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.isArabic
                        ? 'خرائط المفاهيم والتدفق الذهني'
                        : 'Mindmaps & Flowcharts',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    widget.isArabic
                        ? 'منهاج وزارة التربية والتعليم - دراسة بصرية ذكية'
                        : 'UAE MoE Syllabus • Visual Concept & Syntax Trees',
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF64748B),
                      fontWeight: FontWeight.w500,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: const [
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 10),
            child: ArabEnglishToggleSwitch(compact: true),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(52),
          child: Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: TabBar(
              controller: _tabController,
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              indicatorColor: const Color(0xFF6C5CE7),
              indicatorWeight: 3,
              labelColor: const Color(0xFF6C5CE7),
              unselectedLabelColor: const Color(0xFF64748B),
              labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500, fontSize: 12.5),
              tabs: [
                Tab(
                  iconMargin: EdgeInsets.zero,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.account_tree_outlined, size: 16),
                      const SizedBox(width: 6),
                      Text(widget.isArabic ? 'خريطة الدرس (Mindmap)' : 'Lesson Mindmap'),
                    ],
                  ),
                ),
                Tab(
                  iconMargin: EdgeInsets.zero,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.alt_route_rounded, size: 16),
                      const SizedBox(width: 6),
                      Text(widget.isArabic ? 'مخطط الإعراب (Syntax)' : 'Syntax Flowchart'),
                    ],
                  ),
                ),
                Tab(
                  iconMargin: EdgeInsets.zero,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.menu_book_outlined, size: 16),
                      const SizedBox(width: 6),
                      Text(widget.isArabic ? 'قواعد النحو (Rules Tree)' : 'Grammar Rules'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // Grade & Chapter Selector Header (Grounded strictly to Profile Grade 5)
          _buildSelectorHeader(),

          // Main Tabs Content
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildLessonMindmapTab(activeChapter),
                _buildSyntaxFlowchartTab(),
                _buildCurriculumRulesTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSelectorHeader() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Single Active Grade Badge grounded to Profile (Class 5 only, no other class chips)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 10, 16, 6),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: const Color(0xFF6C5CE7).withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFF6C5CE7).withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.school_rounded, color: Color(0xFF6C5CE7), size: 15),
                      const SizedBox(width: 6),
                      Text(
                        widget.isArabic ? 'الصَّفُّ: الخَامِسُ (Class 5)' : 'Class: Grade 5',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF6C5CE7),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  widget.isArabic ? '• منهاج الإمارات الرسمي' : '• UAE MoE Official Curriculum',
                  style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),

          // Horizontal Chapter Scroller
          SizedBox(
            height: 48,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: _chapters.length,
              itemBuilder: (context, index) {
                final ch = _chapters[index];
                final isSelected = _selectedChapterIndex == index;
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
                  child: InkWell(
                    onTap: () => setState(() => _selectedChapterIndex = index),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: isSelected ? (ch['color'] as Color).withValues(alpha: 0.15) : Colors.white,
                        border: Border.all(
                          color: isSelected ? (ch['color'] as Color) : Colors.grey.shade300,
                          width: isSelected ? 1.5 : 1.0,
                        ),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            ch['icon'] as IconData,
                            size: 14,
                            color: isSelected ? (ch['color'] as Color) : const Color(0xFF64748B),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            widget.isArabic ? '${index + 1}. ${ch['titleAr']}' : '${index + 1}. ${ch['titleEn']}',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                              color: isSelected ? (ch['color'] as Color) : const Color(0xFF334155),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 1: LESSON CONCEPT MINDMAP (Bilingual Concept Nodes)
  // ---------------------------------------------------------------------------
  Widget _buildLessonMindmapTab(Map<String, dynamic> chapter) {
    final branches = chapter['branches'] as List<Map<String, dynamic>>? ?? [];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Central Concept Hub Card
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                (chapter['color'] as Color).withValues(alpha: 0.95),
                (chapter['color'] as Color).withValues(alpha: 0.80),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: (chapter['color'] as Color).withValues(alpha: 0.3),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.25),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(chapter['icon'] as IconData, color: Colors.white, size: 28),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            widget.isArabic
                                ? 'الصف $_selectedGrade • ${chapter['unitAr']}'
                                : 'Grade $_selectedGrade • ${chapter['unitEn']}',
                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          chapter['titleAr'] ?? '',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          chapter['titleEn'] ?? '',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.white.withValues(alpha: 0.9),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.volume_up_rounded, color: Colors.white, size: 26),
                    tooltip: 'نطق العنوان بالصوت',
                    onPressed: () => _speak(chapter['titleAr'] ?? ''),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      chapter['summaryAr'] ?? '',
                      style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      chapter['summaryEn'] ?? '',
                      style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 11.5, height: 1.3),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.auto_stories, color: Colors.white70, size: 14),
                      const SizedBox(width: 4),
                      Text(
                        'كتاب الوزارة ص ${chapter['pages']}',
                        style: const TextStyle(color: Colors.white70, fontSize: 11),
                      ),
                    ],
                  ),
                  InkWell(
                    onTap: () {
                      if (widget.onAskFahim != null) {
                        widget.onAskFahim!('اشرح لي بالتفصيل خريطة مفاهيم درس: ${chapter['titleAr']}');
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.auto_awesome, color: Color(0xFF6C5CE7), size: 14),
                          const SizedBox(width: 4),
                          Text(
                            widget.isArabic ? 'اسأل فاهم عن الدرس' : 'Ask Fahim AI',
                            style: const TextStyle(color: Color(0xFF6C5CE7), fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // Section Title
        Row(
          children: [
            const Icon(Icons.account_tree_outlined, color: Color(0xFF6C5CE7), size: 18),
            const SizedBox(width: 8),
            Text(
              widget.isArabic ? 'الفروع والمحاور المترابطة (Concept Branches)' : 'Concept Branches & Roots',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
            ),
          ],
        ),

        const SizedBox(height: 12),

        // Render Branches as Bilingual Cards
        ...branches.map((b) => _buildBranchCard(b)),
      ],
    );
  }

  Widget _buildBranchCard(Map<String, dynamic> branch) {
    final items = branch['items'] as List<Map<String, dynamic>>? ?? [];
    final color = branch['color'] as Color? ?? const Color(0xFF6C5CE7);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.25), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Branch Header Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: color.withValues(alpha: 0.08),
              child: Row(
                children: [
                  Icon(branch['icon'] as IconData? ?? Icons.circle, color: color, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          branch['titleAr'] ?? '',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: color,
                          ),
                        ),
                        Text(
                          branch['titleEn'] ?? '',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                            color: color.withValues(alpha: 0.8),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${items.length} ${widget.isArabic ? 'عناصر' : 'nodes'}',
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color),
                    ),
                  ),
                ],
              ),
            ),

            // Branch Nodes
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: items.map((item) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          margin: const EdgeInsets.only(top: 2),
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.circle, size: 8, color: color),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Text(
                                      item['ar'] ?? '',
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF0F172A),
                                      ),
                                    ),
                                  ),
                                  InkWell(
                                    onTap: () => _speak(item['ar'] ?? ''),
                                    child: const Padding(
                                      padding: EdgeInsets.symmetric(horizontal: 4),
                                      child: Icon(Icons.volume_up_outlined, size: 16, color: Color(0xFF6C5CE7)),
                                    ),
                                  ),
                                ],
                              ),
                              ValueListenableBuilder<bool>(
                                valueListenable: ArabEnglishState.notifier,
                                builder: (context, isArabEnOn, _) {
                                  if (!isArabEnOn) return const SizedBox.shrink();
                                  final arabEn = ArabEnglishHelper.transliterate(item['ar'] ?? '');
                                  if (arabEn.isEmpty) return const SizedBox.shrink();
                                  return Container(
                                    margin: const EdgeInsets.only(top: 2, bottom: 2),
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF1F5F9),
                                      borderRadius: BorderRadius.circular(6),
                                      border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                                    ),
                                    child: Text(
                                      '🗣️ $arabEn',
                                      style: const TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        color: Color(0xFF0F172A),
                                      ),
                                    ),
                                  );
                                },
                              ),
                              if (item['en'] != null)
                                Text(
                                  item['en'] ?? '',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF2563EB),
                                  ),
                                ),
                              if (item['root'] != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFFFEF3C7),
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          'الجذر: ${item['root']}',
                                          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFFB45309)),
                                        ),
                                      ),
                                      if (item['pattern'] != null) ...[
                                        const SizedBox(width: 6),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: const Color(0xFFEDE9FE),
                                            borderRadius: BorderRadius.circular(6),
                                          ),
                                          child: Text(
                                            'الوزن: ${item['pattern']}',
                                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF6D28D9)),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                              if (item['meaningAr'] != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    item['meaningAr'] ?? '',
                                    style: const TextStyle(fontSize: 12, color: Color(0xFF1E293B), height: 1.3, fontWeight: FontWeight.w500),
                                  ),
                                ),
                              if (item['meaningEn'] != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 2),
                                  child: Text(
                                    item['meaningEn'] ?? '',
                                    style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 2: SYNTAX & GRAMMAR DECISION FLOWCHART (Complete Bilingual Trees)
  // ---------------------------------------------------------------------------
  Widget _buildSyntaxFlowchartTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Explanatory Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFEEF2FF),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFC7D2FE)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF6C5CE7),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.schema_rounded, color: Colors.white, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.isArabic ? 'خوارزمية الإعراب وتحديد نوع الجملة' : 'Syntax Parsing Decision Tree',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.isArabic
                          ? 'اتبع الخطوات المتسلسلة لتصل إلى إعراب أي كلمة بدقة وسهولة مع الترجمة الإنجليزية.'
                          : 'Follow the algorithmic branches to parse any sentence accurately with English guidance below.',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF4338CA)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 18),

        // STEP 1: ROOT QUESTION
        _buildFlowNode(
          stepNumber: '1',
          titleAr: 'مَا نَوْعُ الكَلِمَةِ الَّتِي تَبْدَأُ بِهَا الجُمْلَةُ؟',
          titleEn: 'What type of word does the sentence begin with?',
          descriptionAr: 'انْظُرْ إِلَى الكَلِمَةِ الأُولَى: هَلْ تَقْبَلُ (أَلْـ) وَالتَّنْوِينَ (اسْمٌ)، أَمْ تَدُلُّ عَلَى حَدَثٍ وَزَمَنٍ (فِعْلٌ)؟',
          descriptionEn: 'Look at the 1st word: Does it accept "Al-" (The) or Nunation (Noun), or signify a timed action (Verb)?',
          color: const Color(0xFF2563EB),
          icon: Icons.help_outline_rounded,
        ),

        _buildFlowConnector(label: widget.isArabic ? 'تَفَرُّعُ القَرَارِ (Decision Split)' : 'Decision Split (تفرع القرار)'),

        // STEP 2: TWO PATHS (NOMINAL VS VERBAL) WITH FULL BILINGUAL LABELS
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // PATH A: NOMINAL SENTENCE (الجملة الاسمية)
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'تَبْدَأُ بِاسْمٍ (الجُمْلَةُ الاسْمِيَّةُ)',
                titleEn: 'Starts with Noun (Nominal Sentence)',
                subtitleAr: 'مِثَالٌ: الكُرَةُ مُسْتَدِيرَةٌ',
                subtitleEn: 'Example: "The ball is round"',
                color: const Color(0xFF0D9488),
                steps: [
                  {
                    'roleAr': 'المُبْتَدَأُ',
                    'roleEn': 'Subject Noun (Mubtada)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ (ـُ)',
                    'caseEn': 'Nominative case with Damma (-u)',
                    'detailAr': 'الكُرَةُ: الاسْمُ الَّذِي نَبْدَأُ بِهِ الكَلامَ.',
                    'detailEn': 'Al-Kuratu: Starting noun introducing the subject.',
                  },
                  {
                    'roleAr': 'الخَبَرُ',
                    'roleEn': 'The Predicate (Khabar)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ (ـٌ)',
                    'caseEn': 'Nominative case with Damma (-un)',
                    'detailAr': 'مُسْتَدِيرَةٌ: الكَلِمَةُ الَّتِي تُتَمِّمُ المَعْنَى.',
                    'detailEn': 'Mustadeeratun: Tells what the subject is / round.',
                  },
                ],
              ),
            ),
            const SizedBox(width: 10),

            // PATH B: VERBAL SENTENCE (الجملة الفعلية)
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'تَبْدَأُ بِفِعْلٍ (الجُمْلَةُ الفِعْلِيَّةُ)',
                titleEn: 'Starts with Verb (Verbal Sentence)',
                subtitleAr: 'مِثَالٌ: سَجَّلَ اللاعِبُ هَدَفًا',
                subtitleEn: 'Example: "The player scored a goal"',
                color: const Color(0xFFEA580C),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ',
                    'roleEn': 'The Action Verb (Fi\'l)',
                    'caseAr': 'مَاضٍ / مُضَارِع / أَمْر',
                    'caseEn': 'Past / Present / Imperative tense',
                    'detailAr': 'سَجَّلَ: فِعْلٌ مَاضٍ مَبْنِيٌّ عَلَى الفَتْحِ.',
                    'detailEn': 'Sajjala: Past tense verb ("scored").',
                  },
                  {
                    'roleAr': 'الفَاعِلُ (مَنْ فَعَلَ؟)',
                    'roleEn': 'The Doer / Subject Agent (Fa\'il)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ (ـُ)',
                    'caseEn': 'Nominative case with Damma (-u)',
                    'detailAr': 'اللاَّعِبُ: هُوَ مَنْ قَامَ بِتَسْجِيلِ الهَدَفِ.',
                    'detailEn': 'Al-La\'ibu: Answers "Who did it?" (The player).',
                  },
                  {
                    'roleAr': 'المَفْعُولُ بِهِ (مَاذَا فَعَلَ؟)',
                    'roleEn': 'Direct Object (Maf\'ul Bihi)',
                    'caseAr': 'مَنْصُوبٌ بِالفَتْحَةِ (ـًا)',
                    'caseEn': 'Accusative case with Fatha (-an)',
                    'detailAr': 'هَدَفًا: الشَّيْءُ الَّذِي وَقَعَ عَلَيْهِ الفِعْلُ.',
                    'detailEn': 'Hadafan: Answers "What was acted upon?" (A goal).',
                  },
                ],
              ),
            ),
          ],
        ),

        const SizedBox(height: 20),

        // FLOW 2: PREPOSITIONS & GENITIVE CASE
        _buildFlowNode(
          stepNumber: '2',
          titleAr: 'مُخَطَّطُ حُرُوفِ الجَرِّ وَالاسْمِ المَجْرُورِ',
          titleEn: 'Prepositions & Genitive Case Flowchart',
          descriptionAr: 'إِذَا سُبِقَتِ الكَلِمَةُ بِأَحَدِ حُرُوفِ الجَرِّ: (مِنْ، إِلَى، عَنْ، عَلَى، فِي، البَاء [بـ]، الكَاف [كـ]، اللام [لـ])',
          descriptionEn: 'When a noun is preceded by a preposition (Min, Ila, \'An, \'Ala, Fi, Bi-, Ka-, Li-):',
          color: const Color(0xFF7C3AED),
          icon: Icons.south_east_rounded,
        ),

        _buildFlowConnector(label: widget.isArabic ? 'القَاعِدَةُ الحَتْمِيَّةُ (Mandatory Rule)' : 'Mandatory Rule (القاعدة الحتمية)'),

        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFFAF5FF),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFDDD6FE)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.check_circle_outline_rounded, color: Color(0xFF7C3AED), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'النَّتِيجَةُ الإِعْرَابِيَّةُ: اسْمٌ مَجْرُورٌ بِالكَسْرَةِ الظَّاهِرَةِ [ـِ]',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF5B21B6)),
                        ),
                        Text(
                          'Grammar Rule: Noun is Majroor (Genitive) marked with Kasra (-i sound)',
                          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 11, color: Color(0xFF6D28D9)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFEDE9FE)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '• فِي المَلْعَبِ: فِي (حَرْفُ جَرٍّ) + المَلْعَبِ (اسْمٌ مَجْرُورٌ بِالكَسْرَةِ).',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    Text(
                      '  "Fi" (Prep: in/on) + "Al-Mal\'ab-i" (Genitive noun with Kasra) = On the pitch.',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '• بِالمَضْرِبِ: البَاءُ (حَرْفُ جَرٍّ) + المَضْرِبِ (اسْمٌ مَجْرُورٌ بِالكَسْرَةِ).',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    Text(
                      '  "Bi" (Prep: with) + "Al-Madrib-i" (Genitive noun with Kasra) = With the racket.',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // FLOW 3: POSSESSIVE PRONOUNS
        _buildFlowNode(
          stepNumber: '3',
          titleAr: 'مُخَطَّطُ ضَمَائِرِ المِلْكِيَّةِ المُتَّصِلَةِ بِالأَسْمَاءِ',
          titleEn: 'Attached Possessive Pronouns Flowchart',
          descriptionAr: 'كُلُّ ضَمِيرٍ يَتَّصِلُ بِاسْمٍ يُفِيدُ المِلْكِيَّةَ وَيُعْرَبُ فِي مَحَلِّ جَرٍّ بِالإِضَافَةِ:',
          descriptionEn: 'Every pronoun attached to a noun signifies possession (Idhafah) with English meaning:',
          color: const Color(0xFF0284C7),
          icon: Icons.person_pin_rounded,
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            _buildPronounBadge(ar: 'لِي (يـ)', word: 'كُرَتِي', en: 'My ball', sub: 'Ball + Me', color: const Color(0xFF2563EB)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'لَهُ (ـهُ)', word: 'كُرَتُهُ', en: 'His ball', sub: 'Ball + Him', color: const Color(0xFF059669)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'لَهَا (ـهَا)', word: 'كُرَتُهَا', en: 'Her ball', sub: 'Ball + Her', color: const Color(0xFFD97706)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'لَنَا (نَا)', word: 'كُرَتُنَا', en: 'Our ball', sub: 'Ball + Us', color: const Color(0xFF7C3AED)),
          ],
        ),
      ],
    );
  }

  Widget _buildFlowNode({
    required String stepNumber,
    required String titleAr,
    required String titleEn,
    required String descriptionAr,
    required String descriptionEn,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              stepNumber,
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titleAr,
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: color),
                ),
                ValueListenableBuilder<bool>(
                  valueListenable: ArabEnglishState.notifier,
                  builder: (context, isArabEnOn, _) {
                    if (!isArabEnOn) return const SizedBox.shrink();
                    final arabEn = ArabEnglishHelper.transliterate(titleAr);
                    if (arabEn.isEmpty) return const SizedBox.shrink();
                    return Container(
                      margin: const EdgeInsets.only(top: 2, bottom: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                      ),
                      child: Text(
                        '🗣️ $arabEn',
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    );
                  },
                ),
                Text(
                  titleEn,
                  style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: color.withValues(alpha: 0.85)),
                ),
                const SizedBox(height: 4),
                Text(
                  descriptionAr,
                  style: const TextStyle(fontSize: 12, color: Color(0xFF1E293B), height: 1.3, fontWeight: FontWeight.w500),
                ),
                ValueListenableBuilder<bool>(
                  valueListenable: ArabEnglishState.notifier,
                  builder: (context, isArabEnOn, _) {
                    if (!isArabEnOn) return const SizedBox.shrink();
                    final arabEn = ArabEnglishHelper.transliterate(descriptionAr);
                    if (arabEn.isEmpty) return const SizedBox.shrink();
                    return Container(
                      margin: const EdgeInsets.only(top: 2, bottom: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Text(
                        '🗣️ $arabEn',
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    );
                  },
                ),
                Text(
                  descriptionEn,
                  style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.volume_up_outlined, size: 20, color: color),
            onPressed: () => _speak(titleAr),
          ),
        ],
      ),
    );
  }

  Widget _buildFlowConnector({required String label}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Center(
        child: Column(
          children: [
            Container(width: 2, height: 14, color: const Color(0xFFCBD5E1)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Text(
                label,
                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
              ),
            ),
            Container(width: 2, height: 14, color: const Color(0xFFCBD5E1)),
          ],
        ),
      ),
    );
  }

  Widget _buildBranchPathway({
    required String titleAr,
    required String titleEn,
    required String subtitleAr,
    required String subtitleEn,
    required Color color,
    required List<Map<String, String>> steps,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.3), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titleAr,
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color),
                ),
                Text(
                  titleEn,
                  style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.w600, color: color.withValues(alpha: 0.9)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtitleAr,
            style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
          ),
          Text(
            subtitleEn,
            style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B), fontStyle: FontStyle.italic),
          ),
          const SizedBox(height: 10),
          ...steps.map((st) {
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: color.withValues(alpha: 0.15)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          st['roleAr'] ?? '',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color),
                        ),
                      ),
                      InkWell(
                        onTap: () => _speak(st['roleAr'] ?? ''),
                        child: Icon(Icons.volume_up_outlined, size: 14, color: color),
                      ),
                    ],
                  ),
                  Text(
                    st['roleEn'] ?? '',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: color.withValues(alpha: 0.85)),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    st['caseAr'] ?? '',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                  ),
                  Text(
                    st['caseEn'] ?? '',
                    style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.w500, color: Color(0xFF475569)),
                  ),
                  const Divider(height: 8, thickness: 0.5),
                  Text(
                    st['detailAr'] ?? '',
                    style: const TextStyle(fontSize: 10, color: Color(0xFF1E293B), fontWeight: FontWeight.w500),
                  ),
                  Text(
                    st['detailEn'] ?? '',
                    style: const TextStyle(fontSize: 9, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildPronounBadge({required String ar, required String word, required String en, required String sub, required Color color}) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Column(
          children: [
            Text(ar, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
            const SizedBox(height: 2),
            Text(word, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
            Text(en, style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
            Text(sub, style: const TextStyle(fontSize: 8.5, color: Color(0xFF64748B))),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: CURRICULUM RULES TREE (Topic-by-topic with complete English Translations)
  // ---------------------------------------------------------------------------
  Widget _buildCurriculumRulesTab() {
    final rules = [
      {
        'key': 'sentence_types',
        'titleAr': 'الجُمْلَةُ الاسْمِيَّةُ وَالجُمْلَةُ الفِعْلِيَّةُ',
        'titleEn': 'Nominal vs Verbal Sentences',
        'badgeAr': 'الوحدة 1',
        'badgeEn': 'Unit 1',
        'ruleAr': 'الجُمْلَةُ الاسْمِيَّةُ تَبْدَأُ بِاسْمٍ وَتَتَكَوَّنُ مِنْ رُكْنَيْنِ رَئِيسَيْنِ: مُبْتَدَأ وَخَبَر، وَكِلاهُمَا مَرْفُوعٌ بِالضَّمَّةِ. أَمَّا الجُمْلَةُ الفِعْلِيَّةُ فَتَبْدَأُ بِفِعْلٍ وَتَتَكَوَّنُ مِنْ فِعْلٍ وَفَاعِلٍ (مَرْفُوع) وَمَفْعُولٍ بِهِ (مَنْصُوب).',
        'ruleEn': 'A Nominal Sentence starts with a noun and consists of two primary pillars: Subject (Mubtada) and Predicate (Khabar), both in the nominative case with Damma. A Verbal Sentence starts with a verb and consists of a Verb, Subject Agent (Fa\'il, Marfoo\'), and Direct Object (Maf\'ul Bihi, Mansoob).',
        'formulaAr': 'جملة اسمية: مُبْتَدَأ (مَرْفُوع) + خَبَر (مَرْفُوع) | جملة فعلية: فِعْل + فَاعِل (مَرْفُوع) + مَفْعُول بِهِ (مَنْصُوب)',
        'formulaEn': 'Nominal: Subject (Damma) + Predicate (Damma) | Verbal: Verb + Doer (Damma) + Object (Fatha)',
        'examples': [
          {
            'sentenceAr': 'الكُرَةُ سَرِيعَةٌ',
            'sentenceEn': 'The ball is fast',
            'analysisAr': 'الكُرَةُ: مُبْتَدَأٌ مَرْفُوعٌ بِالضَّمَّةِ | سَرِيعَةٌ: خَبَرٌ مَرْفُوعٌ بِالضَّمَّةِ.',
            'analysisEn': 'Al-Kuratu: Subject noun (Marfoo\' with Damma) | Saree\'atun: Predicate (Marfoo\' with Damma).',
          },
          {
            'sentenceAr': 'قَذَفَ اللَّاعِبُ الكُرَةَ',
            'sentenceEn': 'The player kicked the ball',
            'analysisAr': 'قَذَفَ: فِعْلٌ مَاضٍ | اللَّاعِبُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ | الكُرَةَ: مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ.',
            'analysisEn': 'Qadhafa: Past verb | Al-La\'ibu: Doer (Marfoo\' with Damma) | Al-Kurata: Object (Mansoob with Fatha).',
          },
        ],
      },
      {
        'key': 'prepositions',
        'titleAr': 'حُرُوفُ الجَرِّ وَالاسْمُ المَجْرُورُ',
        'titleEn': 'Prepositions & Genitive Nouns',
        'badgeAr': 'الوحدة 1',
        'badgeEn': 'Unit 1',
        'ruleAr': 'حُرُوفُ الجَرِّ تَدْخُلُ عَلَى الأَسْمَاءِ فَقَطْ وَتَجُرُّهَا بِالكَسْرَةِ الظَّاهِرَةِ. مِنْ أَشْهَرِهَا: (مِنْ، إِلَى، عَنْ، عَلَى، فِي، البَاء، الكَاف، اللَّام).',
        'ruleEn': 'Prepositions prefix nouns exclusively and cause them to enter the genitive case, marked with a visible Kasra (-i sound). Key prepositions: Min (from), Ila (to), \'An (about), \'Ala (on), Fi (in), Bi- (with), Ka- (like), Li- (for).',
        'formulaAr': 'حَرْفُ جَرٍّ + اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ',
        'formulaEn': 'Preposition (Harf Jarr) + Genitive Noun (Ism Majroor with Kasra)',
        'examples': [
          {
            'sentenceAr': 'يَلْعَبُ الطُّلاَّبُ فِي المَلْعَبِ',
            'sentenceEn': 'The students play on the pitch',
            'analysisAr': 'فِي: حَرْفُ جَرٍّ | المَلْعَبِ: اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ.',
            'analysisEn': 'Fi: Preposition | Al-Mal\'abi: Genitive noun with Kasra (-i).',
          },
          {
            'sentenceAr': 'سَافَرَ الفَرِيقُ إِلَى دُبَيٍّ',
            'sentenceEn': 'The team traveled to Dubai',
            'analysisAr': 'إِلَى: حَرْفُ جَرٍّ | دُبَيٍّ: اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ.',
            'analysisEn': 'Ila: Preposition | Dubayyin: Genitive noun with Kasra (-i).',
          },
        ],
      },
      {
        'key': 'adverbs',
        'titleAr': 'ظَرْفَا الزَّمَانِ وَالمَكَانِ (المَفْعُولُ فِيهِ)',
        'titleEn': 'Adverbs of Time & Place (Maf\'ul Feeh)',
        'badgeAr': 'الوحدة 2',
        'badgeEn': 'Unit 2',
        'ruleAr': 'اسْمٌ مَنْصُوبٌ بِالفَتْحَةِ يَدُلُّ عَلَى زَمَانِ وُقُوعِ الفِعْلِ (ظَرْفُ زَمَانٍ) أَوْ مَكَانِ وُقُوعِهِ (ظَرْفُ مَكَانٍ).',
        'ruleEn': 'An accusative noun (Mansoob with Fatha) specifying the exact time an action took place (Adverb of Time) or the location where it occurred (Adverb of Place).',
        'formulaAr': 'ظَرْفُ زَمَانٍ: (صَبَاحًا، مَسَاءً، لَيْلاً) | ظَرْفُ مَكَانٍ: (أَمَامَ، خَلْفَ، فَوْقَ، تَحْتَ)',
        'formulaEn': 'Time: Sabahan (morning), Masa\'an (evening) | Place: Amama (in front), Khalfa (behind), Fawqa (above)',
        'examples': [
          {
            'sentenceAr': 'تَدَرَّبَ العَدَّاءُ مَسَاءً',
            'sentenceEn': 'The runner trained in the evening',
            'analysisAr': 'مَسَاءً: ظَرْفُ زَمَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ الظَّاهِرَةُ.',
            'analysisEn': 'Masa\'an: Adverb of Time (Mansoob with Fatha).',
          },
          {
            'sentenceAr': 'وَقَفَ الحَكَمُ أَمَامَ المَرْمَى',
            'sentenceEn': 'The referee stood in front of the goal',
            'analysisAr': 'أَمَامَ: ظَرْفُ مَكَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ الظَّاهِرَةُ.',
            'analysisEn': 'Amama: Adverb of Place (Mansoob with Fatha).',
          },
        ],
      },
      {
        'key': 'adjectives',
        'titleAr': 'النَّعْتُ وَالمَنْعُوتُ (الصِّفَةُ وَالمَوْصُوفُ)',
        'titleEn': 'Adjective Agreement (Na\'at & Man\'ut)',
        'badgeAr': 'الوحدة 2',
        'badgeEn': 'Unit 2',
        'ruleAr': 'النَّعْتُ هُوَ تَابِعٌ يَذْكُرُ صِفَةً فِي اسْمٍ قَبْلَهُ (المَنْعُوت). يَتْبَعُ النَّعْتُ مَنْعُوتَهُ فِي 4 أُمُورٍ: الإِعْرَابِ (رَفْعًا وَنَصْبًا وَجَرًّا)، التَّعْرِيفِ وَالتَّنْكِيرِ، التَّذْكِيرِ وَالتَّأْنِيثِ، وَالعَدَدِ.',
        'ruleEn': 'An adjective (Na\'at) describes a preceding noun (Man\'ut). The adjective must strictly agree with its noun across 4 dimensions: Grammatical case (Nominative/Accusative/Genitive), Definiteness (with/without "Al-"), Gender (Masc/Fem), and Number (Singular/Dual/Plural).',
        'formulaAr': 'اسْمٌ مَنْعُوتٌ + اسْمٌ نَعْتٌ (مُطَابَقَةٌ كَامِلَةٌ فِي الحَرَكَةِ وَالتَّعْرِيفِ)',
        'formulaEn': 'Noun (Man\'ut) + Adjective (Na\'at) [100% agreement in vowel case & definiteness]',
        'examples': [
          {
            'sentenceAr': 'شَاهَدْتُ المُبَارَاةَ الحَمَاسِيَّةَ',
            'sentenceEn': 'I watched the thrilling match',
            'analysisAr': 'الحَمَاسِيَّةَ: نَعْتٌ مَنْصُوبٌ بِالفَتْحَةِ يَتْبَعُ (المُبَارَاةَ) فِي التَّعْرِيفِ وَالنَّصْبِ.',
            'analysisEn': 'Al-Hamasiyyata: Adjective (Mansoob with Fatha) agreeing with the definite object.',
          },
          {
            'sentenceAr': 'هَذَا حِصَانٌ عَرَبِيٌّ أَصِيلٌ',
            'sentenceEn': 'This is a purebred Arabian horse',
            'analysisAr': 'عَرَبِيٌّ: نَعْتٌ مَرْفُوعٌ بِالضَّمَّةِ يَتْبَعُ (حِصَانٌ) فِي التَّنْكِيرِ وَالرَّفْعِ.',
            'analysisEn': 'Arabiyyun: Adjective (Marfoo\' with Damma) agreeing in indefinite nominative case.',
          },
        ],
      },
      {
        'key': 'demonstratives',
        'titleAr': 'أَسْمَاءُ الإِشَارَةِ لِلْقَرِيبِ وَالبَعِيدِ',
        'titleEn': 'Demonstrative Pronouns (Asma\' Al-Isharah)',
        'badgeAr': 'الوحدة 3',
        'badgeEn': 'Unit 3',
        'ruleAr': 'أَسْمَاءُ الإِشَارَةِ أَلْفَاظٌ يُشَارُ بِهَا إِلَى شَيْءٍ مُعَيَّنٍ: هَذَا (مُفْرَد مُذَكَّر)، هَذِهِ (مُفْرَد مُؤَنَّث وَجَمْع غَيْر العَاقِل)، هَؤُلاءِ (جَمْع العَاقِل بِنَوْعَيْهِ).',
        'ruleEn': 'Demonstratives point to specific referents: Hatha (singular masculine = "this"), Hathihi (singular feminine & non-human plurals = "this / these"), Ha\'ula\'i (human plurals for both genders = "these").',
        'formulaAr': 'هَذَا (مُذَكَّر) | هَذِهِ (مُؤَنَّث + جَمْع غَيْر عَاقِل) | هَؤُلاءِ (جَمْع عَاقِل)',
        'formulaEn': 'Hatha (Masc sing.) | Hathihi (Fem sing. + Non-human pl.) | Ha\'ula\'i (Human pl.)',
        'examples': [
          {
            'sentenceAr': 'هَذِهِ أَلْعَابٌ رِيَاضِيَّةٌ مُفِيدَةٌ',
            'sentenceEn': 'These are beneficial sports games',
            'analysisAr': 'هَذِهِ: اسْمُ إِشَارَةٍ لِجَمْعِ غَيْرِ العَاقِلِ (أَلْعَابٌ).',
            'analysisEn': 'Hathihi: Demonstrative pronoun used for non-human plural ("Al\'ab").',
          },
          {
            'sentenceAr': 'هَؤُلاءِ طُلاَّبٌ مُجْتَهِدُونَ',
            'sentenceEn': 'These are diligent students',
            'analysisAr': 'هَؤُلاءِ: اسْمُ إِشَارَةٍ لِجَمْعِ العَاقِلِ (طُلاَّبٌ).',
            'analysisEn': 'Ha\'ula\'i: Demonstrative pronoun used for human plural ("Tullab").',
          },
        ],
      },
      {
        'key': 'conjunctions',
        'titleAr': 'حُرُوفُ العَطْفِ وَدَلالَاتُهَا',
        'titleEn': 'Conjunction Particles (Huroof Al-\'Atf)',
        'badgeAr': 'الوحدة 3',
        'badgeEn': 'Unit 3',
        'ruleAr': 'تَرْبِطُ بَيْنَ كَلِمَتَيْنِ وَيَتْبَعُ المَعْطُوفُ المَعْطُوفَ عَلَيْهِ فِي الإِعْرَابِ: الوَاوُ (لِلْمُشَارَكَةِ)، الفَاءُ (لِلتَّرْتِيبِ وَالسُّرْعَةِ)، ثُمَّ (لِلتَّرْتِيبِ مَعَ التَّرَاخِي فِي الوَقْتِ)، أَوْ (لِلتَّخْيِيرِ).',
        'ruleEn': 'Conjunctions link two words where the joined word matches the previous word\'s vowel case: Waw (simultaneous partnership), Fa (immediate sequential order), Thumma (delayed sequence with time gap), Aw (choice or option).',
        'formulaAr': 'مَعْطُوفٌ عَلَيْهِ + حَرْفُ عَطْفٍ (وَ، فَـ، ثُمَّ، أَوْ) + مَعْطُوفٌ (يَتْبَعُهُ فِي الإِعْرَابِ)',
        'formulaEn': 'Base Word + Conjunction (Waw, Fa, Thumma, Aw) + Joined Word (matches case)',
        'examples': [
          {
            'sentenceAr': 'حَضَرَ زَايِدٌ وَرَاشِدٌ',
            'sentenceEn': 'Zayed and Rashid arrived together',
            'analysisAr': 'الوَاوُ: حَرْفُ عَطْفٍ لِلْمُشَارَكَةِ | رَاشِدٌ: مَعْطُوفٌ مَرْفُوعٌ بِالضَّمَّةِ.',
            'analysisEn': 'Waw: Conjunction of partnership | Rashidun: Conjoined noun (Marfoo\' with Damma).',
          },
          {
            'sentenceAr': 'رَمَى اللَّاعِبُ الكُرَةَ فَسَجَّلَ هَدَفًا',
            'sentenceEn': 'The player threw the ball and instantly scored a goal',
            'analysisAr': 'الفَاءُ: حَرْفُ عَطْفٍ يُفِيدُ التَّرْتِيبَ وَالسُّرْعَةَ المُبَاشِرَةَ.',
            'analysisEn': 'Fa: Conjunction indicating immediate, instantaneous sequential action.',
          },
        ],
      },
    ];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Title Bar
        Row(
          children: [
            const Icon(Icons.bookmark_border_rounded, color: Color(0xFF6C5CE7), size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.isArabic ? 'شجرة القواعد النحوية الشاملة' : 'Comprehensive Grammar Rules Tree',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                  ),
                  Text(
                    widget.isArabic
                        ? 'قواعد المنهاج مع التراكيب الرياضية والشواهد الإعرابية والترجمة الكاملة'
                        : 'Curriculum syntax formulas with parsed examples & full English translations',
                    style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        ...rules.map((rule) {
          final isSelected = _selectedGrammarTopicKey == rule['key'];
          final examples = rule['examples'] as List<Map<String, String>>? ?? [];

          return Container(
            margin: const EdgeInsets.only(bottom: 14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isSelected ? const Color(0xFF6C5CE7) : Colors.grey.shade200,
                width: isSelected ? 1.5 : 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.03),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ExpansionTile(
              initiallyExpanded: isSelected,
              onExpansionChanged: (exp) {
                if (exp) setState(() => _selectedGrammarTopicKey = rule['key'] as String);
              },
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              collapsedShape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              leading: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF3F0FF),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.auto_stories_rounded, color: Color(0xFF6C5CE7), size: 20),
              ),
              title: Text(
                rule['titleAr'] as String,
                style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    rule['titleEn'] as String,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF6C5CE7)),
                  ),
                  Text(
                    '${rule['badgeAr']} • ${rule['badgeEn']}',
                    style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8), fontWeight: FontWeight.w500),
                  ),
                ],
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Divider(height: 1),
                      const SizedBox(height: 12),

                      // Rule Arabic
                      Text(
                        rule['ruleAr'] as String,
                        style: const TextStyle(fontSize: 13, color: Color(0xFF1E293B), height: 1.4, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 4),

                      // Rule English
                      Text(
                        rule['ruleEn'] as String,
                        style: const TextStyle(fontSize: 11.5, color: Color(0xFF475569), height: 1.35),
                      ),
                      const SizedBox(height: 12),

                      // Formula Box (Arabic + English)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF3C7),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFFDE68A)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.functions_rounded, color: Color(0xFFB45309), size: 18),
                                const SizedBox(width: 8),
                                const Text(
                                  'المُعَادَلَةُ الإِعْرَابِيَّةُ (Syntax Formula):',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF92400E),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              rule['formulaAr'] as String,
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF78350F),
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              rule['formulaEn'] as String,
                              style: const TextStyle(
                                fontSize: 10.5,
                                color: Color(0xFF92400E),
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 14),

                      // Examples with full breakdown
                      Text(
                        widget.isArabic
                            ? 'أَمْثِلَةٌ إِعْرَابِيَّةٌ مُتَرْجَمَةٌ (Parsed Examples):'
                            : 'Parsed Examples (أمثلة إعرابية تطبيقية):',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF334155)),
                      ),
                      const SizedBox(height: 8),
                      ...examples.map((ex) {
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: Colors.grey.shade200),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Text(
                                      ex['sentenceAr'] ?? '',
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF0F172A),
                                      ),
                                    ),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.volume_up_outlined, size: 18, color: Color(0xFF6C5CE7)),
                                    onPressed: () => _speak(ex['sentenceAr'] ?? ''),
                                  ),
                                ],
                              ),
                              Text(
                                ex['sentenceEn'] ?? '',
                                style: const TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF2563EB),
                                ),
                              ),
                              const Divider(height: 10, thickness: 0.5),
                              Text(
                                ex['analysisAr'] ?? '',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF064E3B)),
                              ),
                              Text(
                                ex['analysisEn'] ?? '',
                                style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}
