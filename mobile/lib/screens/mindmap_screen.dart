import 'package:flutter/material.dart';
import '../arab_english_service.dart';

/// Interactive Mindmaps and Grammar Flowcharts for UAE MoE Arabic Curriculum.
/// Includes visual concept trees for each lesson and syntax decision flowcharts for grammar topics.
/// Grounded for non-native Arabic learners with bilingual Arabic-English translations below every concept.
class MindmapsScreen extends StatefulWidget {
  final bool isArabic;
  final int initialGrade;
  final dynamic api;
  final String? token;
  final ValueChanged<int>? onGradeChanged;
  // Grades this account may open; defaults to all for admins and visitors.
  final List<int> allowedGrades;
  final Function(String text)? onVocalize;
  final Function(String query)? onAskFahim;
  final VoidCallback onBack;

  const MindmapsScreen({
    super.key,
    required this.isArabic,
    this.initialGrade = 5,
    this.api,
    this.token,
    this.onGradeChanged,
    this.allowedGrades = const [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
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
  static final List<Map<String, dynamic>> _grade5Chapters = [
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

  // _grade6Chapters
  static final List<Map<String, dynamic>> _grade6Chapters = [
  {
    'id': 'chapter_1',
    'titleAr': 'أَنَا إِمَارَاتِيٌّ وَأَعْتَزُّ بِهُوِيَّتِي',
    'titleEn': 'I am Emirati & Proud of My Identity',
    'unitAr': 'الهُوِيَّةُ وَالوَطَنُ',
    'unitEn': 'National Identity & Homeland',
    'pages': '6 - 15',
    'icon': Icons.auto_stories_rounded,
    'color': const Color(0xFF2563EB),
    'summaryAr': 'ترسيخ الانتماء للوطن، الاعتزاز بالهوية الإماراتية الأصيلة، سنع الأجداد، وقاعدة كان وأخواتها.',
    'summaryEn': 'Strengthening patriotic belonging, pride in authentic Emirati identity, ancestral heritage, and Kana & its sisters grammar.',
    'branches': [
      {
        'titleAr': 'المفردات وجذور الكلمات',
        'titleEn': 'Core Vocabulary & Roots',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF0284C7),
        'items': [
          { 'ar': 'الهُوِيَّةُ', 'en': 'Identity', 'root': 'ه - و - ي', 'meaningAr': 'مَجْمُوعُ السِّمَاتِ وَالقِيَمِ الَّتِي تُمَيِّزُ الفَرْدَ وَالمُجْتَمَعَ.', 'meaningEn': 'The ensemble of traits, values, and traditions distinguishing an individual and society.' },
          { 'ar': 'الاعْتِزَازُ', 'en': 'Pride / Cherishing', 'root': 'ع - ز - ز', 'meaningAr': 'الشُّعُورُ بِالفَخْرِ وَالشَّرَفِ وَالكَرَامَةِ الوَطَنِيَّةِ.', 'meaningEn': 'A profound feeling of pride, honor, and national dignity.' },
          { 'ar': 'الانْتِمَاءُ', 'en': 'Belonging / Allegiance', 'root': 'ن - م - ي', 'meaningAr': 'الارْتِبَاطُ الوَثِيقُ بِالأَرْضِ وَالقِيَادَةِ وَالتُّرَاثِ.', 'meaningEn': 'Steadfast bond and loyalty to the land, leadership, and heritage.' },
          { 'ar': 'السَّنَعُ الإِمَارَاتِيُّ', 'en': 'Emirati San\'a (Etiquette)', 'root': 'س - ن - ع', 'meaningAr': 'الآدَابُ وَالعَادَاتُ وَالأَخْلَاقُ الحَمِيدَةُ المُتَوَارَثَةُ.', 'meaningEn': 'Traditional cultural etiquette, chivalry, and virtuous manners passed down generations.' }
        ]
      },
      {
        'titleAr': 'حقائق ومحاور الدرس',
        'titleEn': 'Reading Facts & National Values',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF059669),
        'items': [
          { 'ar': 'قِيَمُ الوَطَنِ: رُوحُ الاتِّحَادِ', 'en': 'National Values: Spirit of the Union', 'meaningAr': 'تَأْسِيسُ دَوْلَةِ الإِمَارَاتِ عَلَى قِيَمِ الوَحْدَةِ وَالعَطَاءِ.', 'meaningEn': 'Founding of the UAE on principles of unity, cohesion, and benevolence.' },
          { 'ar': 'عَلَمُ الإِمَارَاتِ: رَمْزُ السِّيَادَةِ', 'en': 'UAE Flag: Symbol of Sovereignty', 'meaningAr': 'الأَلْوَانُ الأَرْبَعَةُ: الأَحْمَرُ، الأَخْضَرُ، الأَبْيَضُ، وَالأَسْوَدُ.', 'meaningEn': 'The 4 Pan-Arab colors representing courage, hope, purity, and resolve.' }
        ]
      },
      {
        'titleAr': 'القواعد المرتبطة: كَانَ وَأَخَوَاتُهَا',
        'titleEn': 'Grammar: Kana & Its Sisters',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF7C3AED),
        'items': [
          { 'ar': 'كَانَ الوَطَنُ عَزِيزًا فِي قُلُوبِنَا.', 'en': 'The homeland was cherished in our hearts.', 'meaningEn': 'Kana enters nominal sentence, keeps noun marfoo\' and makes predicate mansoob.' },
          { 'ar': 'أَصْبَحَ العِلْمُ سِلَاحَ الأَجْيَالِ.', 'en': 'Knowledge became the weapon of generations.', 'meaningEn': 'Asbaha acts like Kana, making subject marfoo\' and predicate mansoob.' }
        ]
      }
    ]
  }
];


  // _grade7Chapters
  static final List<Map<String, dynamic>> _grade7Chapters = [
  {
    'id': 'chapter_1',
    'titleAr': 'وَثِيقَةُ الأُخُوَّةِ الإِنْسَانِيَّةِ فِي أَبُوظَبِي',
    'titleEn': 'Document on Human Fraternity',
    'unitAr': 'التَّسَامُحُ وَالأُخُوَّةُ الإِنْسَانِيَّةُ',
    'unitEn': 'Tolerance & Human Fraternity',
    'pages': '6 - 15',
    'icon': Icons.auto_stories_rounded,
    'color': const Color(0xFF059669),
    'summaryAr': 'القيم العالمية لوثيقة الأخوة الإنسانية الموقعة في أبوظبي، ورسالة الإمارات في التعايش والسلام وقاعدة إن وأخواتها.',
    'summaryEn': 'Universal principles of the Human Fraternity Document signed in Abu Dhabi, promoting peace, global coexistence, and Inna & its sisters grammar.',
    'branches': [
      {
        'titleAr': 'مفردات التسامح والإخاء',
        'titleEn': 'Tolerance Vocabulary',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF0284C7),
        'items': [
          { 'ar': 'التَّسَامُحُ', 'en': 'Tolerance & Forbearance', 'root': 'س - م - ح', 'meaningAr': 'قَبُولُ الآخَرِ وَاحْتِرَامُ الِاخْتِلَافِ.', 'meaningEn': 'Embracing diversity and mutual respect.' },
          { 'ar': 'الأُخُوَّةُ', 'en': 'Fraternity / Brotherhood', 'root': 'أ - خ - و', 'meaningAr': 'الرَّابِطَةُ الإِنْسَانِيَّةُ الجَامِعَةُ بَيْنَ البَشَرِ.', 'meaningEn': 'Universal bond of shared humanity.' },
          { 'ar': 'التَّعَايُشُ', 'en': 'Coexistence', 'root': 'ع - ي - ش', 'meaningAr': 'العَيْشُ المُشْتَرَكُ فِي سَلَامٍ وَأَمَانٍ.', 'meaningEn': 'Harmonious mutual living in safety and respect.' }
        ]
      },
      {
        'titleAr': 'المحاور الإنسانية والوطنية',
        'titleEn': 'Humanitarian & National Pillars',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF059669),
        'items': [
          { 'ar': 'وَثِيقَةُ أَبُوظَبِي: نِدَاءُ السَّلَامِ', 'en': 'Abu Dhabi Document: Call for Peace', 'meaningAr': 'تَوْقِيعُ الوَثِيقَةِ التَّارِيخِيَّةِ لِتَعْزِيزِ الحِوَارِ بَيْنَ الأَدْيَانِ.', 'meaningEn': 'Historic signing to foster interfaith dialogue and fraternity.' },
          { 'ar': 'دَوْلَةُ الإِمَارَاتِ: حَاضِنَةُ التَّسَامُحِ', 'en': 'UAE: Global Oasis of Tolerance', 'meaningAr': 'احْتِضَانُ أَكْثَرَ مِنْ 200 جِنْسِيَّةٍ فِي تَنَاغُمٍ وَتَعَايُشٍ.', 'meaningEn': 'Embracing more than 200 nationalities in harmony and solidarity.' }
        ]
      },
      {
        'titleAr': 'القواعد المرتبطة: إِنَّ وَأَخَوَاتُهَا',
        'titleEn': 'Grammar: Inna & Its Sisters',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF7C3AED),
        'items': [
          { 'ar': 'إِنَّ التَّسَامُحَ قِيمَةٌ نَبِيلَةٌ.', 'en': 'Verily, tolerance is a noble value.', 'meaningEn': 'Inna makes the noun accusative (Tasamuh-a) and predicate nominative (Qeemat-un).' },
          { 'ar': 'لَعَلَّ السَّلَامَ يَعُمُّ العَالَمَ.', 'en': 'May peace prevail across the world.', 'meaningEn': 'La\'alla operates like Inna in expressing hopeful desire.' }
        ]
      }
    ]
  }
];


  // _grade8Chapters
  static final List<Map<String, dynamic>> _grade8Chapters = [
  {
    'id': 'chapter_1',
    'titleAr': 'أَبُو الطَّيِّبِ المُتَنَبِّي شَاعِرُ الحِكْمَةِ',
    'titleEn': 'Al-Mutanabbi: Poet of Wisdom',
    'unitAr': 'فُرْسَانُ الكَلِمَةِ وَرَوَائِعُ الأَدَبِ',
    'unitEn': 'Masterpieces of Arabic Literature',
    'pages': '6 - 15',
    'icon': Icons.auto_stories_rounded,
    'color': const Color(0xFF7C3AED),
    'summaryAr': 'روائع شعر أبي الطيب المتنبي، فصاحته، وحكمته الخالدة التي سارت بها الركبان.',
    'summaryEn': 'Immortal literary masterworks of Abu al-Tayyib al-Mutanabbi, classical eloquence, and proverbial wisdom.',
    'branches': [
      {
        'titleAr': 'المفردات البلاغية وجذور الكلمات',
        'titleEn': 'Rhetorical Vocabulary & Roots',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF0284C7),
        'items': [
          { 'ar': 'الفَصَاحَةُ', 'en': 'Eloquence', 'root': 'ف - ص - ح', 'meaningAr': 'خُلُوُّ الكَلَامِ مِنَ العُيُوبِ وَوُضُوحُ الدَّلَالَةِ.', 'meaningEn': 'Clarity and supreme purity of speech.' },
          { 'ar': 'الحِكْمَةُ', 'en': 'Wisdom', 'root': 'ح - ك - م', 'meaningAr': 'وَضْعُ الشَّيْءِ فِي مَوْضِعِهِ المُنَاسِبِ.', 'meaningEn': 'Sound judgment and profound philosophical insight.' }
        ]
      },
      {
        'titleAr': 'القواعد: الفِعْلُ المَبْنِيُّ لِلْمَجْهُولِ',
        'titleEn': 'Grammar: Passive Voice & Pro-Agent',
        'icon': Icons.menu_book_rounded,
        'color': const Color(0xFF7C3AED),
        'items': [
          { 'ar': 'نُظِّمَتِ القَصِيدَةُ بِإِبْدَاعٍ.', 'en': 'The poem was composed with brilliance.', 'meaningEn': 'Direct object takes nominative pro-agent role.' }
        ]
      }
    ]
  }
];


// UAE MoE Class 1 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade1Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'أُسْرَتِي وَبَيْتِي السَّعِيدُ',
      'titleEn': 'My Family & Happy Home',
      'unitAr': 'أَنَا وَأُسْرَتِي',
      'unitEn': 'Me and My Family',
      'icon': Icons.home_rounded,
      'color': const Color(0xFF2563EB),
      'pages': '6 - 15',
      'summaryAr': 'التعرف على أفراد الأسرة، بر الوالدين، الحروف الهجائية، والمدود القصيرة والطويلة.',
      'summaryEn': 'Family members, honoring parents, Arabic alphabet, short and long vowels.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'الأُسْرَةُ (أَبٌ، أُمٌّ، أَخٌ، أُخْتٌ)', 'en': 'The Family (Dad, Mom, Brother, Sister)', 'root': 'أ - س - ر', 'meaningAr': 'العَائِلَةُ المُتَرَابِطَةُ فِي البَيْتِ.', 'meaningEn': 'The loving family household.'},
            {'ar': 'البَيْتُ (الدَّارُ)', 'en': 'The Home / House', 'root': 'ب - ي - ت', 'meaningAr': 'مَسْكَنُ الأُسْرَةِ المَلِيءُ بِالمَحَبَّةِ.', 'meaningEn': 'Home filled with love.'},
          ],
        },
        {
          'titleAr': 'الحركات والمدود',
          'titleEn': 'Vowels & Lengthening (Harakat & Madd)',
          'icon': Icons.record_voice_over_rounded,
          'color': const Color(0xFF059669),
          'items': [
            {'ar': 'الفَتْحَةُ وَمَدُّ الأَلِفِ (بَـ / بَا)', 'en': 'Fatha & Madd Alif (Ba / Baa)', 'meaningAr': 'صَوْتٌ قَصِيرٌ يَمْتَدُّ بِالأَلِفِ.', 'meaningEn': 'Short sound lengthened with Alif.'},
            {'ar': 'الضَّمَّةُ وَمَدُّ الوَاوِ (بُـ / بُو)', 'en': 'Damma & Madd Waw (Bu / Boo)', 'meaningAr': 'صَوْتٌ قَصِيرٌ يَمْتَدُّ بِالوَاوِ.', 'meaningEn': 'Short sound lengthened with Waw.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 2 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade2Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'مَدْرَسَتِي وَأَصْدِقَائِي',
      'titleEn': 'My School & Friends',
      'unitAr': 'حَيَاتُنَا المَدْرَسِيَّةُ',
      'unitEn': 'Our School Life',
      'icon': Icons.school_rounded,
      'color': const Color(0xFF0891B2),
      'pages': '6 - 15',
      'summaryAr': 'البيئة المدرسية، الصداقة والتعاون، أسماء الإشارة، والضمائر المنفصلة.',
      'summaryEn': 'School community, friendship, demonstrative pronouns, and personal pronouns.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'الصَّدِيقُ (ج: أَصْدِقَاء)', 'en': 'The Friend (pl. Friends)', 'root': 'ص - د - ق', 'meaningAr': 'المُخْلِصُ الَّذِي يُعِينُ صَاحِبَهُ.', 'meaningEn': 'Loyal caring companion.'},
            {'ar': 'التَّعَاوُنُ', 'en': 'Cooperation / Teamwork', 'root': 'ع - و - ن', 'meaningAr': 'مُسَاعَدَةُ الآخَرِينَ فِي الخَيْرِ.', 'meaningEn': 'Helping others collaboratively.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 3 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade3Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'وَطَنِي الإِمَارَاتُ مَهْدُ الخَيْرِ',
      'titleEn': 'My Homeland UAE: Cradle of Goodness',
      'unitAr': 'الوَطَنُ وَالانْتِمَاءُ',
      'unitEn': 'Homeland & Belonging',
      'icon': Icons.flag_rounded,
      'color': const Color(0xFF16A34A),
      'pages': '6 - 15',
      'summaryAr': 'معالم الإمارات، فضل الوطن، أقسام الكلمة (اسم، فعل، حرف)، وحروف الجر.',
      'summaryEn': 'UAE landmarks, gratitude to homeland, parts of speech, and prepositions.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'الوَطَنُ (ج: أَوْطَان)', 'en': 'The Homeland', 'root': 'و - ط - ن', 'meaningAr': 'الأَرْضُ الغَالِيَةُ الَّتِي نَعِيشُ فِيهَا.', 'meaningEn': 'The precious land we belong to.'},
            {'ar': 'الخَيْرُ وَالعَطَاءُ', 'en': 'Goodness & Giving', 'root': 'خ - ي - ر', 'meaningAr': 'مُسَاعَدَةُ النَّاسِ وَإِكْرَامُهُمْ.', 'meaningEn': 'Benevolence and generosity.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 4 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade4Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'فِي حُبِّ الإِمَارَاتِ وَإِنْجَازَاتِهَا',
      'titleEn': 'In Love of the UAE & Its Achievements',
      'unitAr': 'إِنْجَازَاتٌ وَطَنِيَّةٌ',
      'unitEn': 'National Achievements',
      'icon': Icons.military_tech_rounded,
      'color': const Color(0xFFD97706),
      'pages': '6 - 15',
      'summaryAr': 'إنجازات الفضاء والصناعة في الإمارات، الجملة الفعلية، والفاعل والمفعول به.',
      'summaryEn': 'UAE space and industrial achievements, verbal sentence structure, subject and object.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'الإِنْجَازُ (ج: إِنْجَازَات)', 'en': 'Achievement / Milestone', 'root': 'ن - ج - ز', 'meaningAr': 'العَمَلُ النَّاجِحُ العَظِيمُ.', 'meaningEn': 'Great successful accomplishment.'},
            {'ar': 'الفَضَاءُ وَالرِّيَادَةُ', 'en': 'Space & Leadership', 'root': 'ف - ض - و', 'meaningAr': 'اسْتِكْشَافُ الكَوَاكِبِ وَالنُّجُومِ.', 'meaningEn': 'Exploration of cosmos and leadership.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 9 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade9Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'الفِكْرُ الفَلْسَفِيُّ وَحَضَارَةُ الإِمَارَاتِ',
      'titleEn': 'Philosophical Thought & UAE Civilization',
      'unitAr': 'الفِكْرُ وَالمُنَاظَرَةُ',
      'unitEn': 'Thought & Debate',
      'icon': Icons.psychology_rounded,
      'color': const Color(0xFF4F46E5),
      'pages': '6 - 15',
      'summaryAr': 'بناء الحجة والمناظرة، المشتقات اللغوية (اسم الفاعل والمفعول)، واقتصاد المعرفة.',
      'summaryEn': 'Logical argumentation, participles, and the knowledge economy.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'المُنَاظَرَةُ', 'en': 'Structured Debate', 'root': 'ن - ظ - ر', 'meaningAr': 'حِوَارٌ فِكْرِيٌّ مُقْنِعٌ بِالحُجَجِ.', 'meaningEn': 'Intellectual persuasive dialogue.'},
            {'ar': 'البُرْهَانُ', 'en': 'Conclusive Proof', 'root': 'ب - ر - ه', 'meaningAr': 'الدَّلِيلُ القَاطِعُ عَلَى صِحَّةِ الفِكْرَةِ.', 'meaningEn': 'Irrefutable empirical evidence.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 10 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade10Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'الأَدَبُ العَرَبِيُّ الجَاهِلِيُّ وَقِيَمُ الفُرُوسِيَّةِ',
      'titleEn': 'Pre-Islamic Arabic Literature & Chivalry',
      'unitAr': 'عُصُورُ الأَدَبِ',
      'unitEn': 'Literary Eras',
      'icon': Icons.auto_stories_rounded,
      'color': const Color(0xFF7C3AED),
      'pages': '6 - 15',
      'summaryAr': 'المعلقات، شجاعة الفرسان، التشبيه البليغ والاستعارة، وعلم الصرف.',
      'summaryEn': 'The Muallaqat odes, chivalry, eloquent similes, metaphors, and morphology.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'المُعَلَّقَاتُ', 'en': 'The Mu\'allaqat Odes', 'root': 'ع - ل - ق', 'meaningAr': 'قَصَائِدُ عَرَبِيَّةٌ خَالِدَةٌ عُلِّقَتْ فِي الكَعْبَةِ.', 'meaningEn': 'Masterpiece ancient Arabian odes.'},
            {'ar': 'الفُرُوسِيَّةُ', 'en': 'Chivalry & Knighthood', 'root': 'ف - ر - س', 'meaningAr': 'الشَّجَاعَةُ وَالنَّجْدَةُ وَالكَرَمُ.', 'meaningEn': 'Bravery, honor, and valor.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 11 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade11Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'الأَدَبُ الأَنْدَلُسِيُّ وَعُلُومُ البَلَاغَةِ',
      'titleEn': 'Andalusian Literature & Rhetorical Sciences',
      'unitAr': 'البَلَاغَةُ وَالأَدَبُ الأَنْدَلُسِيُّ',
      'unitEn': 'Rhetoric & Andalusian Odes',
      'icon': Icons.menu_book_rounded,
      'color': const Color(0xFF059669),
      'pages': '6 - 15',
      'summaryAr': 'الموشحات الأندلسية، جماليات الطبيعة، علم البيان والبديع، والجناس والطباق.',
      'summaryEn': 'Muwashahat poetry, nature descriptions, rhetorical figures, paronomasia and antithesis.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'المُوَشَّحُ (ج: مُوَشَّحَات)', 'en': 'Muwashah (Strophic Ode)', 'root': 'و - ش - ح', 'meaningAr': 'فَنٌّ شِعْرِيٌّ أَنْدَلُسِيٌّ ذُو أَوْزَانٍ مُتَنَوِّعَةٍ.', 'meaningEn': 'Strophic musical poetic form of Andalusia.'},
          ],
        },
      ],
    },
  ];

  // UAE MoE Class 12 Term 1 Chapters
  static final List<Map<String, dynamic>> _grade12Chapters = [
    {
      'id': 'chapter_1',
      'titleAr': 'رُؤْيَةُ الخَمْسِينَ وَالبُحُوثُ الأَدَبِيَّةُ المُتَقَدِّمَةُ',
      'titleEn': 'UAE Centennial 2071 & Advanced Literary Research',
      'unitAr': 'النَّقْدُ وَالمُسْتَقْبَلُ',
      'unitEn': 'Criticism & The Future',
      'icon': Icons.lightbulb_rounded,
      'color': const Color(0xFFEA580C),
      'pages': '6 - 15',
      'summaryAr': 'النقد الأدبي الحديث، الدراسات اللغوية المتقدمة، واستشراف مستقبل الثقافة الإماراتية.',
      'summaryEn': 'Modern literary criticism, advanced linguistic analysis, and UAE cultural futurology.',
      'branches': [
        {
          'titleAr': 'المفردات وجذور الكلمات',
          'titleEn': 'Core Vocabulary & Roots',
          'icon': Icons.menu_book_rounded,
          'color': const Color(0xFF0284C7),
          'items': [
            {'ar': 'الاسْتِشْرَافُ', 'en': 'Foresight & Horizon Scanning', 'root': 'ش - ر - ف', 'meaningAr': 'التَّخْطِيطُ العِلْمِيُّ الذَّكِيُّ لِلْمُسْتَقْبَلِ.', 'meaningEn': 'Strategic scientific planning for future.'},
          ],
        },
      ],
    },
  ];

  List<Map<String, dynamic>> _chapters = [];

  static List<Map<String, dynamic>> _getFallbackChapters(int grade) {
    switch (grade) {
      case 1:
        return _grade1Chapters;
      case 2:
        return _grade2Chapters;
      case 3:
        return _grade3Chapters;
      case 4:
        return _grade4Chapters;
      case 6:
        return _grade6Chapters;
      case 7:
        return _grade7Chapters;
      case 8:
        return _grade8Chapters;
      case 9:
        return _grade9Chapters;
      case 10:
        return _grade10Chapters;
      case 11:
        return _grade11Chapters;
      case 12:
        return _grade12Chapters;
      case 5:
      default:
        return _grade5Chapters;
    }
  }

  static List<Map<String, dynamic>> _castMapList(dynamic list) {
    if (list is! List) return [];
    return list.map((item) {
      if (item is Map) {
        final map = Map<String, dynamic>.from(item);
        if (map['branches'] is List) {
          map['branches'] = (map['branches'] as List).map((b) {
            if (b is Map) {
              final bMap = Map<String, dynamic>.from(b);
              if (bMap['items'] is List) {
                bMap['items'] = (bMap['items'] as List).map((it) => it is Map ? Map<String, dynamic>.from(it) : <String, dynamic>{}).toList();
              }
              if (bMap['color'] is String) {
                bMap['color'] = _parseColor(bMap['color'] as String);
              }
              return bMap;
            }
            return <String, dynamic>{};
          }).toList();
        }
        if (map['color'] is String) {
          map['color'] = _parseColor(map['color'] as String);
        }
        map['icon'] ??= Icons.auto_stories_rounded;
        return map;
      }
      return <String, dynamic>{};
    }).toList();
  }

  static Color _parseColor(String? colorStr) {
    if (colorStr == null || colorStr.isEmpty) return const Color(0xFF2563EB);
    try {
      final hex = colorStr.replaceAll('#', '');
      if (hex.length == 6) {
        return Color(int.parse('FF$hex', radix: 16));
      }
    } catch (_) {}
    return const Color(0xFF2563EB);
  }

  @override
  void initState() {
    super.initState();
    _selectedGrade = widget.initialGrade;
    _tabController = TabController(length: 3, vsync: this);
    _loadChaptersForGrade(_selectedGrade);
  }

  @override
  void didUpdateWidget(covariant MindmapsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialGrade != oldWidget.initialGrade && widget.initialGrade != _selectedGrade) {
      _loadChaptersForGrade(widget.initialGrade);
    }
  }

  void _loadChaptersForGrade(int grade) async {
    setState(() {
      _selectedGrade = grade;
      _selectedChapterIndex = 0;
      _chapters = _getFallbackChapters(grade);
    });

    if (widget.api != null) {
      try {
        final res = await widget.api.mindmaps(grade: grade, term: 1, token: widget.token);
        if (res != null && res['chapters'] is List && (res['chapters'] as List).isNotEmpty && mounted) {
          final live = _castMapList(res['chapters']);
          if (live.isNotEmpty) {
            setState(() {
              _chapters = live;
              if (_selectedChapterIndex >= _chapters.length) {
                _selectedChapterIndex = 0;
              }
            });
          }
        }
      } catch (err) {
        debugPrint('Failed to fetch remote mindmaps for grade $grade: $err');
      }
    }
  }

  void _showGradePicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.isArabic ? 'اختر الصف الدراسي (Select Grade)' : 'Select Grade (اختر الصف)',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: widget.allowedGrades.map((g) {
                  final isSel = g == _selectedGrade;
                  return ChoiceChip(
                    label: Text(widget.isArabic ? 'الصف $g' : 'Grade $g'),
                    selected: isSel,
                    selectedColor: const Color(0xFF6C5CE7),
                    labelStyle: TextStyle(
                      color: isSel ? Colors.white : const Color(0xFF334155),
                      fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                    ),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(ctx);
                        _loadChaptersForGrade(g);
                        widget.onGradeChanged?.call(g);
                      }
                    },
                  );
                }).toList(),
              ),
            ],
          ),
        );
      },
    );
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
    if (_chapters.isEmpty) {
      _chapters = _getFallbackChapters(_selectedGrade);
    }
    if (_selectedChapterIndex >= _chapters.length) {
      _selectedChapterIndex = 0;
    }
    final activeChapter = _chapters.isNotEmpty ? _chapters[_selectedChapterIndex] : _grade5Chapters[0];

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
                  child: InkWell(
                    onTap: () => _showGradePicker(context),
                    borderRadius: BorderRadius.circular(20),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.school_rounded, color: Color(0xFF6C5CE7), size: 15),
                          const SizedBox(width: 6),
                          Text(
                            widget.isArabic ? 'الصَّفُّ: $_selectedGrade (Class $_selectedGrade)' : 'Class: Grade $_selectedGrade',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF6C5CE7),
                            ),
                          ),
                          const SizedBox(width: 4),
                          const Icon(Icons.arrow_drop_down_rounded, color: Color(0xFF6C5CE7), size: 18),
                        ],
                      ),
                    ),
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
  // TAB 2: SYNTAX & GRAMMAR DECISION FLOWCHART (Grade-Adaptive Decision Trees)
  // ---------------------------------------------------------------------------
  Widget _buildSyntaxFlowchartTab() {
    switch (_selectedGrade) {
      case 6:
        return _buildGrade6SyntaxFlowchart();
      case 7:
        return _buildGrade7SyntaxFlowchart();
      case 8:
        return _buildGrade8SyntaxFlowchart();
      case 5:
      default:
        return _buildGrade5SyntaxFlowchart();
    }
  }

  // GRADE 6: KANA & SISTERS (الأفعال الناسخة) SYNTAX FLOWCHART
  Widget _buildGrade6SyntaxFlowchart() {
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
                      widget.isArabic
                          ? 'خوارزمية إعراب الأفعال الناسخة (كان وأخواتها) والجملة التامة'
                          : 'Grade 6: Incomplete Verbs (Kana & Sisters) Parsing Decision Tree',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.isArabic
                          ? 'اتبع المسارات لتحديد الفعل الناسخ واسمه المرفوع وخبره المنصوب في سياق الهوية والوطن.'
                          : 'Follow algorithmic branches to parse Kana and its sisters, Ism Kana, and Khabar Kana accurately.',
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
          titleAr: 'هَلْ سُبِقَتِ الجُمْلَةُ بِفِعْلٍ نَاسِخٍ (كَانَ، أَصْبَحَ، أَمْسَى، صَارَ، لَيْسَ)؟',
          titleEn: 'Is the sentence introduced by an Incomplete Verb (Kana, Asbaha, Sara, Laysa)?',
          descriptionAr: 'تَدْخُلُ الأَفْعَالُ النَّاسِخَةُ عَلَى الجُمْلَةِ الاسْمِيَّةِ فَتَرْفَعُ المُبْتَدَأَ اسْمًا لَهَا وَتَنْصِبُ الخَبَرَ خَبَرًا لَهَا.',
          descriptionEn: 'Incomplete auxiliary verbs preserve the subject as Nominative (Marfoo) and convert the predicate into Accusative (Mansoob).',
          color: const Color(0xFF2563EB),
          icon: Icons.account_balance_rounded,
        ),

        _buildFlowConnector(label: widget.isArabic ? 'تَفَرُّعُ القَرَارِ الإِعْرَابِيِّ (Parsing Decision Split)' : 'Parsing Decision Split (تفرع القرار)'),

        // STEP 2: TWO PATHS (KANA & SISTERS VS COMPLETE VERBAL SENTENCE)
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // PATH A: KANA & SISTERS
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'دَخَلَ عَلَيْهَا فِعْلٌ نَاسِخٌ (كَانَ وَأَخَوَاتُهَا)',
                titleEn: 'Incomplete Verb (Kana & Sisters Clause)',
                subtitleAr: 'مِثَالٌ: كَانَ الوَطَنُ عَزِيزًا',
                subtitleEn: 'Example: "The homeland was cherished"',
                color: const Color(0xFF0D9488),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ النَّاسِخُ',
                    'roleEn': 'Annulled Auxiliary Verb',
                    'caseAr': 'مَاضٍ مَبْنِيٌّ عَلَى الفَتْحِ',
                    'caseEn': 'Past tense verb (Kana)',
                    'detailAr': 'كَانَ: تَرْفَعُ المُبْتَدَأَ وَتَنْصِبُ الخَبَرَ.',
                    'detailEn': 'Kana: Introduces the clause and modifies case.',
                  },
                  {
                    'roleAr': 'اسْمُ كَانَ (المَرْفُوعُ)',
                    'roleEn': 'Subject of Kana (Ism Kana)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ [ـُ]',
                    'caseEn': 'Nominative case with Damma (-u)',
                    'detailAr': 'الوَطَنُ: اسْمُ كَانَ مَرْفُوعٌ بِالضَّمَّةِ الظَّاهِرَةِ.',
                    'detailEn': 'Al-Watanu: The subject being qualified.',
                  },
                  {
                    'roleAr': 'خَبَرُ كَانَ (المَنْصُوبُ)',
                    'roleEn': 'Predicate of Kana (Khabar Kana)',
                    'caseAr': 'مَنْصُوبٌ بِالفَتْحَةِ [ـً]',
                    'caseEn': 'Accusative case with Fatha (-an)',
                    'detailAr': 'عَزِيزًا: خَبَرُ كَانَ مَنْصُوبٌ بِالفَتْحَةِ الظَّاهِرَةِ.',
                    'detailEn': '\'Azeezan: The predicate attribute of the subject.',
                  },
                ],
              ),
            ),
            const SizedBox(width: 10),

            // PATH B: COMPLETE VERBAL SENTENCE
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'جُمْلَةٌ فِعْلِيَّةٌ تَامَّةٌ (فِعْلٌ وَفَاعِلٌ)',
                titleEn: 'Complete Action Verb Sentence',
                subtitleAr: 'مِثَالٌ: يَفْتَخِرُ المُواطِنُ بِهُوِيَّتِهِ',
                subtitleEn: 'Example: "The citizen is proud of his identity"',
                color: const Color(0xFFEA580C),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ التَّامُّ',
                    'roleEn': 'Complete Action Verb',
                    'caseAr': 'مُضَارِعٌ مَرْفُوعٌ بِالضَّمَّةِ [ـُ]',
                    'caseEn': 'Present indicative with Damma',
                    'detailAr': 'يَفْتَخِرُ: حَدَثٌ يَحْتَاجُ فَاعِلاً تَامًّا.',
                    'detailEn': 'Yaftakhiru: Verb expressing active pride.',
                  },
                  {
                    'roleAr': 'الفَاعِلُ (مَنْ يَفْتَخِرُ؟)',
                    'roleEn': 'Subject Agent (Fa\'il)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ [ـُ]',
                    'caseEn': 'Nominative case with Damma (-u)',
                    'detailAr': 'المُواطِنُ: هُوَ مَنْ يَقُومُ بِالاعْتِزَازِ.',
                    'detailEn': 'Al-Muwatinu: The citizen performing action.',
                  },
                  {
                    'roleAr': 'جَارٌّ وَمَجْرُورٌ',
                    'roleEn': 'Prepositional Object',
                    'caseAr': 'مَجْرُورٌ بِالكَسْرَةِ [ـِ]',
                    'caseEn': 'Genitive case with Kasra (-i)',
                    'detailAr': 'بِهُوِيَّتِهِ: البَاءُ حَرْفُ جَرٍّ + هُوِيَّةِ اسْمٌ مَجْرُورٌ.',
                    'detailEn': 'Bi-huwiyyatihi: "In his national identity".',
                  },
                ],
              ),
            ),
          ],
        ),

        const SizedBox(height: 20),

        // FLOW 2: TYPES OF KHABAR KANA
        _buildFlowNode(
          stepNumber: '2',
          titleAr: 'مُخَطَّطُ أَنْوَاعِ خَبَرِ كَانَ (المُفْرَدُ، الجُمْلَةُ، شِبْهُ الجُمْلَةِ)',
          titleEn: 'Khabar Kana Types Flowchart (Single, Clause, Semi-Clause)',
          descriptionAr: 'يَأْتِي خَبَرُ كَانَ عَلَى ثَلَاثَةِ أَنْوَاعٍ رَئِيسَةٍ مَعَ حُكْمِهَا الإِعْرَابِيِّ:',
          descriptionEn: 'The predicate of Kana can be a single noun, a verbal clause, or a prepositional phrase:',
          color: const Color(0xFF7C3AED),
          icon: Icons.alt_route_rounded,
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
                          widget.isArabic ? 'أَنْوَاعُ خَبَرِ كَانَ الثَّلَاثَةُ فِي الإِعْرَابِ:' : 'The 3 Forms of Khabar Kana:',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF5B21B6)),
                        ),
                        Text(
                          widget.isArabic ? 'خَبَرٌ مُفْرَدٌ (مَنْصُوبٌ) | خَبَرٌ جُمْلَةٌ (فِي مَحَلِّ نَصْبٍ) | خَبَرٌ شِبْهُ جُمْلَةٍ (فِي مَحَلِّ نَصْبٍ)' : 'Single Word (Mansoob) | Verbal Clause (In Accusative) | Prepositional Phrase (In Accusative)',
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
                      '• خَبَرٌ مُفْرَدٌ: كَانَ الشَّعْبُ مُتَّحِدًا (مُتَّحِدًا: خَبَرُ كَانَ مَنْصُوبٌ بِالفَتْحَةِ).',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    Text(
                      '  Single Word Predicate: "The people were united" (Mansoob with Fatha).',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '• خَبَرٌ جُمْلَةٌ فِعْلِيَّةٌ: كَانَ الأَجْدَادُ يَحْمُونَ الأَرْضَ (جُمْلَةُ "يَحْمُونَ" فِي مَحَلِّ نَصْبِ خَبَرِ كَانَ).',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    Text(
                      '  Verbal Clause Predicate: "The ancestors protected the land" (Clause in place of accusative).',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '• خَبَرٌ شِبْهُ جُمْلَةٍ: كَانَ العَلَمُ فِي القِمَّةِ ("فِي القِمَّةِ" شِبْهُ جُمْلَةٍ فِي مَحَلِّ نَصْبِ خَبَرِ كَانَ).',
                      style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E1B4B)),
                    ),
                    Text(
                      '  Prepositional Predicate: "The flag was at the peak" (Prepositional phrase in place of accusative).',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // FLOW 3: CONNECTED PRONOUNS AS ISM KANA
        _buildFlowNode(
          stepNumber: '3',
          titleAr: 'مُخَطَّطُ ضَمَائِرِ اسْمِ كَانَ المُتَّصِلَةِ فِي مَحَلِّ رَفْعٍ',
          titleEn: 'Connected Pronouns as Subject of Kana (Ism Kana)',
          descriptionAr: 'عِنْدَ اتِّصَالِ الضَّمِيرِ بِـ (كَانَ أَوْ إِحْدَى أَخَوَاتِهَا) يُعْرَبُ ضَمِيرًا مُتَّصِلاً فِي مَحَلِّ رَفْعِ اسْمِ كَانَ:',
          descriptionEn: 'Pronouns attached directly to Kana serve as its nominative subject noun:',
          color: const Color(0xFF0284C7),
          icon: Icons.person_pin_rounded,
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            _buildPronounBadge(ar: 'أَنَا (تُ)', word: 'كُنْتُ', en: 'I was', sub: 'Kana + Me', color: const Color(0xFF2563EB)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'نَحْنُ (نَا)', word: 'كُنَّا', en: 'We were', sub: 'Kana + Us', color: const Color(0xFF059669)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'هُمْ (واو)', word: 'كَانُوا', en: 'They were', sub: 'Kana + They', color: const Color(0xFFD97706)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'أَنْتُمْ (تُمْ)', word: 'صِرْتُمْ', en: 'You became', sub: 'Sara + You pl.', color: const Color(0xFF7C3AED)),
          ],
        ),
      ],
    );
  }

  // GRADE 7: INNA & SISTERS (الحروف الناسخة) SYNTAX FLOWCHART
  Widget _buildGrade7SyntaxFlowchart() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFBBF7D0)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF16A34A),
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
                      widget.isArabic
                          ? 'خوارزمية إعراب الحروف الناسخة (إنّ وأخواتها) والجملة البحرية'
                          : 'Grade 7: Inna & Sisters Annulled Particles Decision Tree',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF14532D)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.isArabic
                          ? 'اتبع المسارات لتحديد حرف التوكيد واسمه المنصوب وخبره المرفوع في تراث البحر والغوص.'
                          : 'Follow branches to identify Inna and its sisters, its accusative noun, and nominative predicate.',
                      style: const TextStyle(fontSize: 11, color: Color(0xFF15803D)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 18),

        _buildFlowNode(
          stepNumber: '1',
          titleAr: 'هَلْ بُدِئَتِ الجُمْلَةُ بِحَرْفٍ نَاسِخٍ (إِنَّ، أَنَّ، كَأَنَّ، لَكِنَّ، لَيْتَ، لَعَلَّ)؟',
          titleEn: 'Is the sentence introduced by an Annulled Particle (Inna or its sisters)?',
          descriptionAr: 'تَدْخُلُ إِنَّ وَأَخَوَاتُهَا عَلَى الجُمْلَةِ الاسْمِيَّةِ فَتَنْصِبُ المُبْتَدَأَ اسْمًا لَهَا وَتَرْفَعُ الخَبَرَ خَبَرًا لَهَا.',
          descriptionEn: 'Inna and its sisters set the subject noun in Accusative (Fatha) and retain the predicate in Nominative (Damma).',
          color: const Color(0xFF16A34A),
          icon: Icons.security_rounded,
        ),

        _buildFlowConnector(label: widget.isArabic ? 'تَفَرُّعُ القَرَارِ الإِعْرَابِيِّ (Parsing Decision Split)' : 'Decision Split (تفرع القرار)'),

        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'جُمْلَةُ إِنَّ وَأَخَوَاتِهَا (الحُرُوفُ النَّاسِخَةُ)',
                titleEn: 'Inna & Sisters Clause',
                subtitleAr: 'مِثَالٌ: إِنَّ التُّرَاثَ خَالِدٌ',
                subtitleEn: 'Example: "Verily, heritage is immortal"',
                color: const Color(0xFF0D9488),
                steps: [
                  {
                    'roleAr': 'الحَرْفُ النَّاسِخُ',
                    'roleEn': 'Annulled Particle (Inna)',
                    'caseAr': 'حَرْفُ تَوْكِيدٍ وَنَصْبٍ',
                    'caseEn': 'Emphasis & Accusative particle',
                    'detailAr': 'إِنَّ: تَنْصِبُ الاسْمَ وَتَرْفَعُ الخَبَرَ.',
                    'detailEn': 'Inna: Sets subject to Fatha & predicate to Damma.',
                  },
                  {
                    'roleAr': 'اسْمُ إِنَّ (المَنْصُوبُ)',
                    'roleEn': 'Subject of Inna (Ism Inna)',
                    'caseAr': 'مَنْصُوبٌ بِالفَتْحَةِ [ـَ]',
                    'caseEn': 'Accusative case with Fatha (-a)',
                    'detailAr': 'التُّرَاثَ: اسْمُ إِنَّ مَنْصُوبٌ بِالفَتْحَةِ الظَّاهِرَةِ.',
                    'detailEn': 'Al-Turatha: Accusative noun introduced by Inna.',
                  },
                  {
                    'roleAr': 'خَبَرُ إِنَّ (المَرْفُوعُ)',
                    'roleEn': 'Predicate of Inna (Khabar Inna)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ [ـٌ]',
                    'caseEn': 'Nominative case with Damma (-un)',
                    'detailAr': 'خَالِدٌ: خَبَرُ إِنَّ مَرْفُوعٌ بِالضَّمَّةِ الظَّاهِرَةِ.',
                    'detailEn': 'Khalidun: Nominative predicate completing meaning.',
                  },
                ],
              ),
            ),
            const SizedBox(width: 10),

            Expanded(
              child: _buildBranchPathway(
                titleAr: 'الجُمْلَةُ الفِعْلِيَّةُ التُّرَاثِيَّةُ (البَحْرِيَّةُ)',
                titleEn: 'Maritime Verbal Sentence',
                subtitleAr: 'مِثَالٌ: أَبْحَرَ النَّاخُوذَةُ فِي الخَلِيجِ',
                subtitleEn: 'Example: "The captain sailed into the Gulf"',
                color: const Color(0xFF0284C7),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ المَاضِي',
                    'roleEn': 'Past Tense Verb',
                    'caseAr': 'مَبْنِيٌّ عَلَى الفَتْحِ [ـَ]',
                    'caseEn': 'Past action verb with Fatha',
                    'detailAr': 'أَبْحَرَ: حَدَثُ الإِبْحَارِ فِي عُرْضِ البَحْرِ.',
                    'detailEn': 'Abhara: The sailing action initiated.',
                  },
                  {
                    'roleAr': 'الفَاعِلُ (مَنْ أَبْحَرَ؟)',
                    'roleEn': 'Subject Agent (Fa\'il)',
                    'caseAr': 'مَرْفُوعٌ بِالضَّمَّةِ [ـُ]',
                    'caseEn': 'Nominative case with Damma (-u)',
                    'detailAr': 'النَّاخُوذَةُ: رُبَّانُ السَّفِينَةِ الَّذِي قَامَ بِالإِبْحَارِ.',
                    'detailEn': 'Al-Nakhoodhatu: The captain performing the voyage.',
                  },
                  {
                    'roleAr': 'جَارٌّ وَمَجْرُورٌ',
                    'roleEn': 'Prepositional Phrase',
                    'caseAr': 'مَجْرُورٌ بِالكَسْرَةِ [ـِ]',
                    'caseEn': 'Genitive case with Kasra (-i)',
                    'detailAr': 'فِي الخَلِيجِ: فِي حَرْفُ جَرٍّ + الخَلِيجِ اسْمٌ مَجْرُورٌ.',
                    'detailEn': 'Fi al-khaleej-i: In the Arabian Gulf.',
                  },
                ],
              ),
            ),
          ],
        ),

        const SizedBox(height: 20),

        _buildFlowNode(
          stepNumber: '2',
          titleAr: 'مُخَطَّطُ ضَمَائِرِ اسْمِ إِنَّ المُتَّصِلَةِ فِي مَحَلِّ نَصْبٍ',
          titleEn: 'Connected Pronouns Functioning as Ism Inna (In Accusative)',
          descriptionAr: 'عِنْدَ اتِّصَالِ الضَّمِيرِ بِـ (إِنَّ أَوْ إِحْدَى أَخَوَاتِهَا) يُعْرَبُ فِي مَحَلِّ نَصْبِ اسْمِ إِنَّ:',
          descriptionEn: 'Pronouns attached to Inna function as its accusative subject noun:',
          color: const Color(0xFF16A34A),
          icon: Icons.person_pin_rounded,
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            _buildPronounBadge(ar: 'أَنَا (ـنِي)', word: 'إِنَّنِي', en: 'Indeed I am', sub: 'Inna + Me', color: const Color(0xFF16A34A)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'نَحْنُ (ـنَا)', word: 'إِنَّنَا', en: 'Indeed we are', sub: 'Inna + Us', color: const Color(0xFF0284C7)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'هُوَ (ـهُ)', word: 'إِنَّهُ', en: 'Indeed he is', sub: 'Inna + Him', color: const Color(0xFFD97706)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'أَنْتَ (ـكَ)', word: 'إِنَّكَ', en: 'Indeed you are', sub: 'Inna + You', color: const Color(0xFF7C3AED)),
          ],
        ),
      ],
    );
  }

  // GRADE 8: ACCUSATIVES (المفعول المطلق ولأجله والحال) SYNTAX FLOWCHART
  Widget _buildGrade8SyntaxFlowchart() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFBEB),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFFDE68A)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFD97706),
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
                      widget.isArabic
                          ? 'خوارزمية إعراب المنصوبات: المفعول المطلق والمفعول لأجله والحال'
                          : 'Grade 8: Accusative Complements Decision Tree',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF78350F)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.isArabic
                          ? 'اتبع المسارات للتمييز بين المفعول المطلق والمفعول لأجله والحال في بلاغة النصوص.'
                          : 'Follow branches to differentiate absolute object, object of reason, and adverbial states.',
                      style: const TextStyle(fontSize: 11, color: Color(0xFFB45309)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 18),

        _buildFlowNode(
          stepNumber: '1',
          titleAr: 'مَا نَوْعُ الاسْمِ المَنْصُوبِ الزَّائِدِ فِي الجُمْلَةِ الفِعْلِيَّةِ؟',
          titleEn: 'What type of accusative complement appears in the verbal sentence?',
          descriptionAr: 'انْظُرْ هَلْ هُوَ مَصْدَرٌ مِنْ لَفْظِ الفِعْلِ (مُطْلَق)، أَمْ مَصْدَرٌ يُبَيِّنُ سَبَبَ الفِعْلِ (لِأَجْلِهِ)، أَمْ وَصْفٌ يُبَيِّنُ الهَيْئَةَ (حَال)؟',
          descriptionEn: 'Check if it is a cognate verbal noun (Absolute), explains motive (Reason), or describes state (Haal).',
          color: const Color(0xFFD97706),
          icon: Icons.filter_list_rounded,
        ),

        _buildFlowConnector(label: widget.isArabic ? 'تَفَرُّعُ القَرَارِ الإِعْرَابِيِّ (Parsing Decision Split)' : 'Decision Split (تفرع القرار)'),

        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _buildBranchPathway(
                titleAr: 'المَفْعُولُ المُطْلَقُ (مَصْدَرٌ مِنْ لَفْظِ الفِعْلِ)',
                titleEn: 'Absolute Cognate Object (Maf\'ul Mutlaq)',
                subtitleAr: 'مِثَالٌ: انْتَصَرَ الوَطَنُ انْتِصَارًا',
                subtitleEn: 'Example: "The nation triumphed a great victory"',
                color: const Color(0xFF2563EB),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ وَالفَاعِلُ',
                    'roleEn': 'Verb & Doer',
                    'caseAr': 'فِعْلٌ مَاضٍ + فَاعِلٌ [ـُ]',
                    'caseEn': 'Past verb & nominative agent',
                    'detailAr': 'انْتَصَرَ: فِعْلٌ مَاضٍ | الوَطَنُ: فَاعِلٌ مَرْفُوعٌ.',
                    'detailEn': 'Intasara: Action | Al-Watanu: Doer.',
                  },
                  {
                    'roleAr': 'المَفْعُولُ المُطْلَقُ',
                    'roleEn': 'Absolute Cognate Object',
                    'caseAr': 'مَنْصُوبٌ بِالفَتْحَةِ [ـً]',
                    'caseEn': 'Accusative with Fatha (-an)',
                    'detailAr': 'انْتِصَارًا: مَصْدَرٌ مَأْخُوذٌ مِنْ لَفْظِ (انْتَصَرَ).',
                    'detailEn': 'Intisaran: Cognate noun emphasizing victory.',
                  },
                ],
              ),
            ),
            const SizedBox(width: 10),

            Expanded(
              child: _buildBranchPathway(
                titleAr: 'المَفْعُولُ لِأَجْلِهِ (سَبَبُ الفِعْلِ)',
                titleEn: 'Object of Reason (Maf\'ul Li-Ajlih)',
                subtitleAr: 'مِثَالٌ: وَقَفْتُ احْتِرَامًا لِلْعَلَمِ',
                subtitleEn: 'Example: "I stood out of respect for the flag"',
                color: const Color(0xFF059669),
                steps: [
                  {
                    'roleAr': 'الفِعْلُ وَالفَاعِلُ',
                    'roleEn': 'Verb & Subject Pronoun',
                    'caseAr': 'فِعْلٌ + التَّاءُ فَاعِلٌ',
                    'caseEn': 'Past verb with subject pronoun',
                    'detailAr': 'وَقَفْتُ: فِعْلٌ مَاضٍ + التَّاءُ فِي مَحَلِّ رَفْعِ فَاعِلٍ.',
                    'detailEn': 'Waqaftu: "I stood".',
                  },
                  {
                    'roleAr': 'المَفْعُولُ لِأَجْلِهِ (لِمَاذَا؟)',
                    'roleEn': 'Object of Reason (Why?)',
                    'caseAr': 'مَنْصُوبٌ بِالفَتْحَةِ [ـً]',
                    'caseEn': 'Accusative with Fatha (-an)',
                    'detailAr': 'احْتِرَامًا: مَصْدَرٌ قَلْبِيٌّ يُبَيِّنُ سَبَبَ الوُقُوفِ.',
                    'detailEn': 'Ihtiraman: Answers "Why did you stand?".',
                  },
                ],
              ),
            ),
          ],
        ),

        const SizedBox(height: 20),

        _buildFlowNode(
          stepNumber: '2',
          titleAr: 'مُخَطَّطُ الحَالِ المَنْصُوبَةِ (بَيَانُ هَيْئَةِ صَاحِبِ الحَالِ)',
          titleEn: 'Accusative State / Adverbial Condition (Al-Haal)',
          descriptionAr: 'الحَالُ اسْمٌ نَكِرَةٌ مَنْصُوبٌ يُبَيِّنُ هَيْئَةَ صَاحِبِ الحَالِ (المَعْرِفَةِ) عِنْدَ وُقُوعِ الفِعْلِ: (كَيْفَ؟):',
          descriptionEn: 'Al-Haal describes the transient physical or emotional state of the subject when the action took place:',
          color: const Color(0xFFD97706),
          icon: Icons.directions_run_rounded,
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            _buildPronounBadge(ar: 'سَالِمًا', word: 'عَادَ سَالِمًا', en: 'Returned safe', sub: 'Safe state', color: const Color(0xFF059669)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'مُبْتَسِمًا', word: 'أَقْبَلَ مُبْتَسِمًا', en: 'Arrived smiling', sub: 'Smiling state', color: const Color(0xFF2563EB)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'مُفْتَخِرًا', word: 'وَقَفَ مُفْتَخِرًا', en: 'Stood proud', sub: 'Proud state', color: const Color(0xFFD97706)),
            const SizedBox(width: 6),
            _buildPronounBadge(ar: 'مُسْرِعًا', word: 'انْطَلَقَ مُسْرِعًا', en: 'Dashed quickly', sub: 'Speed state', color: const Color(0xFF7C3AED)),
          ],
        ),
      ],
    );
  }

  // GRADE 5 (AND DEFAULT BASELINE): NOMINAL VS VERBAL SENTENCES SYNTAX FLOWCHART
  Widget _buildGrade5SyntaxFlowchart() {
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
    final rules = _getCurriculumRulesForGrade(_selectedGrade);
    if (rules.isNotEmpty && !rules.any((r) => r['key'] == _selectedGrammarTopicKey)) {
      _selectedGrammarTopicKey = rules.first['key'] as String;
    }

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

  static List<Map<String, dynamic>> _getCurriculumRulesForGrade(int grade) {
    switch (grade) {
      case 6:
        return _grade6Rules;
      case 7:
        return _grade7Rules;
      case 8:
        return _grade8Rules;
      case 1:
      case 2:
      case 3:
      case 4:
        return _gradePrimaryRules;
      case 9:
      case 10:
      case 11:
      case 12:
        return _gradeSecondaryRules;
      case 5:
      default:
        return _grade5Rules;
    }
  }

  // GRADE 6 CURRICULUM RULES
  static final List<Map<String, dynamic>> _grade6Rules = [
    {
      'key': 'kana_sisters',
      'titleAr': 'كَانَ وَأَخَوَاتُهَا (الأَفْعَالُ النَّاسِخَةُ)',
      'titleEn': 'Kana & Its Sisters (Incomplete Auxiliary Verbs)',
      'badgeAr': 'الوحدة 1 (الصف 6)',
      'badgeEn': 'Unit 1 (Grade 6)',
      'ruleAr': 'أَفْعَالٌ نَاسِخَةٌ نَاقِصَةٌ تَدْخُلُ عَلَى الجُمْلَةِ الاسْمِيَّةِ، فَتَرْفَعُ المُبْتَدَأَ وَيُسَمَّى اسْمَهَا، وَتَنْصِبُ الخَبَرَ وَيُسَمَّى خَبَرَهَا. مِنْ أَخَوَاتِهَا: (كَانَ، أَصْبَحَ، أَضْحَى، أَمْسَى، ظَلَّ، بَاتَ، صَارَ، لَيْسَ).',
      'ruleEn': 'Incomplete auxiliary verbs entering a nominal sentence. They retain the Subject (Ism Kana) in the nominative case with Damma and convert the Predicate (Khabar Kana) into the accusative case with Fatha. Sisters include: Kana (was), Asbaha (became morning), Sara (became), Laysa (is not).',
      'formulaAr': 'فِعْلٌ نَاسِخٌ + اسْمُ كَانَ (مَرْفُوعٌ بِالضَّمَّةِ [ـُ]) + خَبَرُ كَانَ (مَنْصُوبٌ بِالفَتْحَةِ [ـً])',
      'formulaEn': 'Auxiliary Verb + Subject Noun (Marfoo with Damma) + Predicate (Mansoob with Fatha)',
      'examples': [
        {
          'sentenceAr': 'كَانَ الوَطَنُ عَزِيزًا',
          'sentenceEn': 'The homeland was cherished / dear',
          'analysisAr': 'كَانَ: فِعْلٌ مَاضٍ نَاسِخٌ | الوَطَنُ: اسْمُ كَانَ مَرْفُوعٌ بِالضَّمَّةِ | عَزِيزًا: خَبَرُ كَانَ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Kana: Incomplete verb | Al-Watanu: Subject of Kana (Damma) | Azeezan: Predicate of Kana (Fatha).',
        },
        {
          'sentenceAr': 'أَصْبَحَ الطَّالِبُ مُعْتَزًّا بِهُوِيَّتِهِ',
          'sentenceEn': 'The student became proud of his identity',
          'analysisAr': 'أَصْبَحَ: فِعْلٌ نَاسِخٌ | الطَّالِبُ: اسْمُ أَصْبَحَ مَرْفُوعٌ بِالضَّمَّةِ | مُعْتَزًّا: خَبَرُ أَصْبَحَ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Asbaha: Incomplete verb | Al-Talibu: Subject (Damma) | Mu\'tazzan: Predicate (Fatha).',
        },
        {
          'sentenceAr': 'صَارَ الاتِّحَادُ قُوَّةً',
          'sentenceEn': 'The Union became strength',
          'analysisAr': 'صَارَ: فِعْلٌ نَاسِخٌ لِلتَّحَوُّلِ | الاتِّحَادُ: اسْمُ صَارَ مَرْفُوعٌ بِالضَّمَّةِ | قُوَّةً: خَبَرُ صَارَ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Sara: Verb of transformation | Al-Ittihadu: Subject (Damma) | Quwwatan: Predicate (Fatha).',
        },
      ],
    },
    {
      'key': 'kana_khabar_types',
      'titleAr': 'أَنْوَاعُ خَبَرِ كَانَ (مُفْرَدٌ، جُمْلَةٌ، شِبْهُ جُمْلَةٍ)',
      'titleEn': 'Types of Khabar Kana (Single Word, Clause, Prepositional)',
      'badgeAr': 'الوحدة 2 (الصف 6)',
      'badgeEn': 'Unit 2 (Grade 6)',
      'ruleAr': 'يَأْتِي خَبَرُ كَانَ عَلَى ثَلَاثَةِ أَنْوَاعٍ: 1) مُفْرَدًا (كَلِمَةً وَاحِدَةً مَنْصُوبَةً)، 2) جُمْلَةً (فِعْلِيَّةً أَوْ اسْمِيَّةً فِي مَحَلِّ نَصْبٍ)، 3) شِبْهَ جُمْلَةٍ (جَارٌّ وَمَجْرُورٌ أَوْ ظَرْفٌ فِي مَحَلِّ نَصْبٍ).',
      'ruleEn': 'The predicate of Kana appears as: 1) Single accusative word (Mufrad), 2) Sentence clause (Verbal or Nominal in place of accusative), 3) Prepositional phrase or adverbial clause (Shibh Jumlah).',
      'formulaAr': 'كَانَ + اسْمُ كَانَ + [مُفْرَدٌ مَنْصُوبٌ | جُمْلَةٌ فِعْلِيَّةٌ | شِبْهُ جُمْلَةٍ جَارٌّ وَمَجْرُورٌ]',
      'formulaEn': 'Kana + Ism Kana + [Accusative Single Noun | Verbal Clause | Prepositional Phrase]',
      'examples': [
        {
          'sentenceAr': 'ظَلَّ الجُنْدِيُّ يَحْمِي الوَطَنَ',
          'sentenceEn': 'The soldier remained guarding the homeland',
          'analysisAr': 'ظَلَّ: فِعْلٌ نَاسِخٌ | الجُنْدِيُّ: اسْمُ ظَلَّ مَرْفُوعٌ | يَحْمِي الوَطَنَ: جُمْلَةٌ فِعْلِيَّةٌ فِي مَحَلِّ نَصْبِ خَبَرِ ظَلَّ.',
          'analysisEn': 'Zhalla: Auxiliary verb | Al-Jundiyyu: Subject | Yahmi al-watan: Verbal clause serving as predicate.',
        },
        {
          'sentenceAr': 'بَاتَ العَلَمُ فِي القِمَّةِ',
          'sentenceEn': 'The flag stayed at the peak',
          'analysisAr': 'بَاتَ: فِعْلٌ نَاسِخٌ | العَلَمُ: اسْمُ بَاتَ مَرْفُوعٌ | فِي القِمَّةِ: شِبْهُ جُمْلَةٍ فِي مَحَلِّ نَصْبِ خَبَرِ بَاتَ.',
          'analysisEn': 'Bata: Auxiliary verb | Al-\'Alamu: Subject | Fi al-qimmati: Prepositional phrase as predicate.',
        },
      ],
    },
    {
      'key': 'verbal_identity',
      'titleAr': 'الفَاعِلُ وَالمَفْعُولُ بِهِ فِي سِيَاقِ الوَطَنِ وَالهُوِيَّةِ',
      'titleEn': 'Subject & Direct Object in Patriotic Sentences',
      'badgeAr': 'الوحدة 2 (الصف 6)',
      'badgeEn': 'Unit 2 (Grade 6)',
      'ruleAr': 'الفَاعِلُ اسْمٌ مَرْفُوعٌ بِالضَّمَّةِ يَدُلُّ عَلَى مَنْ فَعَلَ الفِعْلَ، وَالمَفْعُولُ بِهِ اسْمٌ مَنْصُوبٌ بِالفَتْحَةِ يَدُلُّ عَلَى مَنْ وَقَعَ عَلَيْهِ فِعْلُ الفَاعِلِ.',
      'ruleEn': 'The Subject Agent (Fa\'il) is in the nominative case with Damma representing the doer. The Direct Object (Maf\'ul Bihi) is in the accusative case with Fatha receiving the action.',
      'formulaAr': 'فِعْلٌ + فَاعِلٌ (مَرْفُوعٌ بِالضَّمَّةِ [ـُ]) + مَفْعُولٌ بِهِ (مَنْصُوبٌ بِالفَتْحَةِ [ـَ])',
      'formulaEn': 'Verb + Subject Agent (Damma) + Direct Object (Fatha)',
      'examples': [
        {
          'sentenceAr': 'يَصُونُ الإِمَارَاتِيُّ عَهْدَ الأَجْدَادِ',
          'sentenceEn': 'The Emirati honors the covenant of the ancestors',
          'analysisAr': 'يَصُونُ: فِعْلٌ مُضَارِعٌ | الإِمَارَاتِيُّ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ | عَهْدَ: مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Yasoonu: Present verb | Al-Imaratiyyu: Doer (Damma) | \'Ahda: Direct object (Fatha).',
        },
        {
          'sentenceAr': 'رَفَعَ الشَّبَابُ عَلَمَ الإِمَارَاتِ',
          'sentenceEn': 'The youth raised the flag of the UAE',
          'analysisAr': 'رَفَعَ: فِعْلٌ مَاضٍ | الشَّبَابُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ | عَلَمَ: مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Rafa\'a: Past verb | Al-Shabab: Doer (Damma) | \'Alama: Direct object (Fatha).',
        },
      ],
    },
    {
      'key': 'naat_manoot',
      'titleAr': 'النَّعْتُ وَالمَنْعُوتُ فِي سِيَاقِ الهُوِيَّةِ وَالتُّرَاثِ',
      'titleEn': 'Adjective Agreement (Na\'at & Man\'ut) in Heritage',
      'badgeAr': 'الوحدة 3 (الصف 6)',
      'badgeEn': 'Unit 3 (Grade 6)',
      'ruleAr': 'النَّعْتُ تَابِعٌ يَصِفُ المَنْعُوتَ قَبْلَهُ، وَيَتْبَعُهُ فِي الإِعْرَابِ (رَفْعًا وَنَصْبًا وَجَرًّا) وَالتَّعْرِيفِ وَالتَّنْكِيرِ وَالتَّذْكِيرِ وَالتَّأْنِيثِ وَالعَدَدِ.',
      'ruleEn': 'The adjective strictly agrees with the qualified noun in 4 categories: grammatical case, definiteness, gender, and singular/dual/plural number.',
      'formulaAr': 'مَنْعُوتٌ + نَعْتٌ مُطَابِقٌ (ـُـُ / ـَـَ / ـِـِ)',
      'formulaEn': 'Noun + Matching Adjective (Identical vowels & definiteness)',
      'examples': [
        {
          'sentenceAr': 'نَفْتَخِرُ بِالهُوِيَّةِ الإِمَارَاتِيَّةِ الأَصِيلَةِ',
          'sentenceEn': 'We are proud of authentic Emirati identity',
          'analysisAr': 'الإِمَارَاتِيَّةِ: نَعْتٌ مَجْرُورٌ بِالكَسْرَةِ يَتْبَعُ (الهُوِيَّةِ) فِي التَّعْرِيفِ وَالجَرِّ.',
          'analysisEn': 'Al-Imaratiyyati: Adjective matching genitive definite noun in Kasra.',
        },
        {
          'sentenceAr': 'أَسَّسَ القَادَةُ العُظَمَاءُ دَوْلَةً حَدِيثَةً',
          'sentenceEn': 'The great leaders founded a modern state',
          'analysisAr': 'العُظَمَاءُ: نَعْتٌ مَرْفُوعٌ لِـ (القَادَةُ) | حَدِيثَةً: نَعْتٌ مَنْصُوبٌ لِـ (دَوْلَةً).',
          'analysisEn': 'Al-\'Uzama\'u: Nominative adj | Hadeethatan: Accusative adj.',
        },
      ],
    },
    {
      'key': 'cohesive_connectives',
      'titleAr': 'الرَّوَابِطُ التَّرْكِيبِيَّةُ وَأَدَوَاتُ التَّعْلِيلِ وَالاسْتِدْرَاكِ',
      'titleEn': 'Cohesive Connectives, Causation & Concession',
      'badgeAr': 'الوحدة 3 (الصف 6)',
      'badgeEn': 'Unit 3 (Grade 6)',
      'ruleAr': 'أَدَوَاتٌ تَرْبِطُ الجُمَلَ لِبِنَاءِ فَقْرَةٍ مُتَمَاسِكَةٍ: (بِمَا أَنَّ... فَإِنَّ...) لِلتَّعْلِيلِ، (عَلَى الرَّغْمِ مِنْ... إِلَّا أَنَّ...) لِلاسْتِدْرَاكِ، (كَذَلِكَ... كَمَا أَنَّ...) لِلإِضَافَةِ.',
      'ruleEn': 'Syntactic sentence linkers creating cohesive discourse: Bima anna (Since/Given that), \'Ala al-raghmi min (Despite/Although), Kamā anna (Furthermore).',
      'formulaAr': 'بِمَا أَنَّ (السَّبَبُ) + فَإِنَّ (النَّتِيجَةُ) | عَلَى الرَّغْمِ مِنْ (المَانِعُ) + اسْتِطَاعَ (الفِعْلُ)',
      'formulaEn': 'Since [Cause] -> Verily [Result] | Despite [Concession] -> [Accomplishment]',
      'examples': [
        {
          'sentenceAr': 'بِمَا أَنَّنَا أَبْنَاءُ الإِمَارَاتِ، فَإِنَّ وَاجِبَنَا خِدْمَةُ الوَطَنِ',
          'sentenceEn': 'Since we are children of the UAE, our duty is serving the nation',
          'analysisAr': 'رَابِطٌ شَرْطِيٌّ تَعْلِيلِيٌّ يُفِيدُ تَرَتُّبَ النَّتِيجَةِ عَلَى السَّبَبِ.',
          'analysisEn': 'Causal connector linking national belonging to patriotic duty.',
        },
        {
          'sentenceAr': 'عَلَى الرَّغْمِ مِنْ تَطَوُّرِ الحَيَاةِ، نَتَمَسَّكُ بِسَنَعِ الأَجْدَادِ',
          'sentenceEn': 'Despite modern evolution, we cling to ancestral values (San\'a)',
          'analysisAr': 'عَلَى الرَّغْمِ مِنْ: أَدَاةُ اسْتِدْرَاكٍ وَمُفَارَقَةٍ تَرْبِطُ بَيْنَ أَمْرَيْنِ.',
          'analysisEn': 'Concession linker highlighting loyalty to heritage amidst modernity.',
        },
      ],
    },
  ];

  // GRADE 7 CURRICULUM RULES
  static final List<Map<String, dynamic>> _grade7Rules = [
    {
      'key': 'inna_sisters',
      'titleAr': 'إِنَّ وَأَخَوَاتُهَا (الحُرُوفُ النَّاسِخَةُ)',
      'titleEn': 'Inna & Its Sisters (Annulled Accusative Particles)',
      'badgeAr': 'الوحدة 1 (الصف 7)',
      'badgeEn': 'Unit 1 (Grade 7)',
      'ruleAr': 'حُرُوفٌ نَاسِخَةٌ تَدْخُلُ عَلَى الجُمْلَةِ الاسْمِيَّةِ، فَتَنْصِبُ المُبْتَدَأَ وَيُسَمَّى اسْمَهَا، وَتَرْفَعُ الخَبَرَ وَيُسَمَّى خَبَرَهَا. مِنْهَا: (إِنَّ، أَنَّ، كَأَنَّ، لَكِنَّ، لَيْتَ، لَعَلَّ).',
      'ruleEn': 'Annulled particles entering nominal sentences. They make the subject Accusative (Ism Inna with Fatha) and retain the predicate Nominative (Khabar Inna with Damma).',
      'formulaAr': 'حَرْفٌ نَاسِخٌ + اسْمُ إِنَّ (مَنْصُوبٌ بِالفَتْحَةِ [ـَ]) + خَبَرُ إِنَّ (مَرْفُوعٌ بِالضَّمَّةِ [ـُ])',
      'formulaEn': 'Inna Particle + Ism Inna (Mansoob Fatha) + Khabar Inna (Marfoo Damma)',
      'examples': [
        {
          'sentenceAr': 'إِنَّ التُّرَاثَ خَالِدٌ',
          'sentenceEn': 'Verily, heritage is immortal',
          'analysisAr': 'إِنَّ: حَرْفُ تَوْكِيدٍ وَنَصْبٍ | التُّرَاثَ: اسْمُ إِنَّ مَنْصُوبٌ بِالفَتْحَةِ | خَالِدٌ: خَبَرُ إِنَّ مَرْفُوعٌ بِالضَّمَّةِ.',
          'analysisEn': 'Inna: Emphasis particle | Al-Turatha: Ism Inna (Fatha) | Khalidun: Khabar Inna (Damma).',
        },
        {
          'sentenceAr': 'عَلِمْتُ أَنَّ البَحْرَ عَطَاءٌ',
          'sentenceEn': 'I learned that the sea is generous giving',
          'analysisAr': 'أَنَّ: حَرْفٌ نَاسِخٌ | البَحْرَ: اسْمُ أَنَّ مَنْصُوبٌ بِالفَتْحَةِ | عَطَاءٌ: خَبَرُ أَنَّ مَرْفُوعٌ بِالضَّمَّةِ.',
          'analysisEn': 'Anna: Particle | Al-Bahra: Subject (Fatha) | \'Ataa\'un: Predicate (Damma).',
        },
      ],
    },
    {
      'key': 'lazim_mutaaddi',
      'titleAr': 'الفِعْلُ اللَّازِمُ وَالفِعْلُ المُتَعَدِّي',
      'titleEn': 'Intransitive vs Transitive Verbs',
      'badgeAr': 'الوحدة 2 (الصف 7)',
      'badgeEn': 'Unit 2 (Grade 7)',
      'ruleAr': 'الفِعْلُ اللَّازِمُ يَكْتَفِي بِفَاعِلِهِ وَلا يَحْتَاجُ لِمَفْعُولٍ بِهِ. أَمَّا الفِعْلُ المُتَعَدِّي فَيَتَعَدَّى فَاعِلَهُ لِيَنْصِبَ مَفْعُولاً بِهِ وَاحِدًا أَوْ أَكْثَرَ.',
      'ruleEn': 'Intransitive verbs (Lazim) require only a subject to complete meaning. Transitive verbs (Muta\'addi) pass beyond the subject to govern an accusative direct object.',
      'formulaAr': 'لَازِمٌ: فِعْلٌ + فَاعِلٌ | مُتَعَدٍّ: فِعْلٌ + فَاعِلٌ + مَفْعُولٌ بِهِ (مَنْصُوبٌ)',
      'formulaEn': 'Intransitive: Verb + Doer | Transitive: Verb + Doer + Direct Object (Fatha)',
      'examples': [
        {
          'sentenceAr': 'غَاصَ البَحَّارُ فِي الأَعْمَاقِ',
          'sentenceEn': 'The sailor dived into the deep (Intransitive)',
          'analysisAr': 'غَاصَ: فِعْلٌ لَازِمٌ اكْتَفَى بِفَاعِلِهِ (البَحَّارُ) دُونَ مَفْعُولٍ بِهِ.',
          'analysisEn': 'Ghaasa: Intransitive verb completing clause without direct object.',
        },
        {
          'sentenceAr': 'جَمَعَ الغَوَّاصُ المَحَارَ',
          'sentenceEn': 'The diver gathered the oysters (Transitive)',
          'analysisAr': 'جَمَعَ: فِعْلٌ مُتَعَدٍّ نَصَبَ المَفْعُولَ بِهِ (المَحَارَ).',
          'analysisEn': 'Jama\'a: Transitive verb governing object (Al-Mahara).',
        },
      ],
    },
    {
      'key': 'pronouns_types',
      'titleAr': 'الضَّمَائِرُ المُتَّصِلَةُ وَالمُنْفَصِلَةُ وَإِعْرَابُهَا',
      'titleEn': 'Attached & Separate Pronouns and Parsing',
      'badgeAr': 'الوحدة 3 (الصف 7)',
      'badgeEn': 'Unit 3 (Grade 7)',
      'ruleAr': 'الضَّمَائِرُ أَسْمَاءٌ مَعْرِفَةٌ تَدُلُّ عَلَى مُتَكَلِّمٍ أَوْ مُخَاطَبٍ أَوْ غَائِبٍ. تَكُونُ مُنْفَصِلَةً مُسْتَقِلَّةً (أَنَا، أَنْتَ، هُوَ) أَوْ مُتَّصِلَةً بِكَلِمَةٍ أُخْرَى.',
      'ruleEn': 'Pronouns represent 1st, 2nd, or 3rd person entities. They appear as standalone words or attached suffixes carrying nominative, accusative, or genitive roles.',
      'formulaAr': 'مُنْفَصِلٌ: (أَنَا، نَحْنُ، هُوَ) | مُتَّصِلٌ: (ـتُ، ـنَا، ـهُ، ـكَ)',
      'formulaEn': 'Separate: Ana, Nahnu, Huwa | Attached: -tu (Doer), -na (Our/We), -hu (His)',
      'examples': [
        {
          'sentenceAr': 'نَحْنُ أَبْنَاءُ الإِمَارَاتِ',
          'sentenceEn': 'We are children of the UAE',
          'analysisAr': 'نَحْنُ: ضَمِيرٌ مُنْفَصِلٌ فِي مَحَلِّ رَفْعِ مُبْتَدَأٍ.',
          'analysisEn': 'Nahnu: Separate personal pronoun functioning as subject.',
        },
        {
          'sentenceAr': 'شَارَكْتُ فِي سِبَاقِ الهَجَنِ',
          'sentenceEn': 'I took part in the camel race',
          'analysisAr': 'التَّاءُ (ـتُ): ضَمِيرٌ مُتَّصِلٌ فِي مَحَلِّ رَفْعِ فَاعِلٍ.',
          'analysisEn': '-tu: Attached pronoun functioning as nominative doer.',
        },
      ],
    },
  ];

  // GRADE 8 CURRICULUM RULES
  static final List<Map<String, dynamic>> _grade8Rules = [
    {
      'key': 'maful_mutlaq',
      'titleAr': 'المَفْعُولُ المُطْلَقُ وَأَنْوَاعُهُ الثَّلَاثَةُ',
      'titleEn': 'Absolute Object (Maf\'ul Mutlaq) & Its 3 Types',
      'badgeAr': 'الوحدة 1 (الصف 8)',
      'badgeEn': 'Unit 1 (Grade 8)',
      'ruleAr': 'اسْمٌ مَنْصُوبٌ يُذْكَرُ بَعْدَ فِعْلٍ مِنْ لَفْظِهِ لِتَأْكِيدِهِ، أَوْ لِبَيَانِ نَوْعِهِ، أَوْ لِبَيَانِ عَدَدِهِ.',
      'ruleEn': 'An accusative verbal noun derived from the same root as the preceding verb. It serves 3 rhetorical functions: to emphasize the action, specify its quality, or count occurrences.',
      'formulaAr': 'فِعْلٌ + ... + مَصْدَرٌ مَنْصُوبٌ مِنْ لَفْظِ الفِعْلِ [مُؤَكِّد / مُبَيِّن لِلنَّوْع / مُبَيِّن لِلْعَدَد]',
      'formulaEn': 'Verb + Cognate Accusative Noun [Emphasis / Qualitative / Quantitative]',
      'examples': [
        {
          'sentenceAr': 'انْتَصَرَ الوَطَنُ انْتِصَارًا',
          'sentenceEn': 'The nation triumphed a decisive victory (Emphasis)',
          'analysisAr': 'انْتِصَارًا: مَفْعُولٌ مُطْلَقٌ مَنْصُوبٌ بِالفَتْحَةِ مُؤَكِّدٌ لِلْفِعْلِ.',
          'analysisEn': 'Intisaran: Absolute object (Mansoob) emphasizing triumph.',
        },
        {
          'sentenceAr': 'قَرَأَ الطَّالِبُ قِرَاءَةً مُتَأَنِّيَةً',
          'sentenceEn': 'The student read a thoughtful reading (Qualitative)',
          'analysisAr': 'قِرَاءَةً: مَفْعُولٌ مُطْلَقٌ مَنْصُوبٌ مُبَيِّنٌ لِلنَّوْعِ.',
          'analysisEn': 'Qira\'atan: Absolute object accompanied by an adjective describing type.',
        },
      ],
    },
    {
      'key': 'maful_liajlih',
      'titleAr': 'المَفْعُولُ لِأَجْلِهِ وَشُرُوطُ إِعْرَابِهِ',
      'titleEn': 'Object of Reason (Maf\'ul Li-Ajlih)',
      'badgeAr': 'الوحدة 2 (الصف 8)',
      'badgeEn': 'Unit 2 (Grade 8)',
      'ruleAr': 'مَصْدَرٌ قَلْبِيٌّ مَنْصُوبٌ يُذْكَرُ لِبَيَانِ السَّبَبِ الَّذِي دَعَا إِلَى حُدُوثِ الفِعْلِ. يَصْلُحُ جَوَابًا لِسُؤَالِ: (لِمَاذَا؟).',
      'ruleEn': 'An accusative noun of intent or emotion explaining the underlying cause or motive behind an action. Directly answers the question "Why?".',
      'formulaAr': 'فِعْلٌ + ... + مَصْدَرٌ مَنْصُوبٌ [يُجِيبُ عَنْ: لِمَاذَا؟]',
      'formulaEn': 'Action Verb + ... + Accusative Verbal Noun [Answers: Why?]',
      'examples': [
        {
          'sentenceAr': 'وَقَفْتُ احْتِرَامًا لِلْمُعَلِّمِ',
          'sentenceEn': 'I stood out of respect for the teacher',
          'analysisAr': 'احْتِرَامًا: مَفْعُولٌ لِأَجْلِهِ مَنْصُوبٌ بِالفَتْحَةِ بَيَّنَ سَبَبَ الوُقُوفِ.',
          'analysisEn': 'Ihtiraman: Object of reason (Mansoob) explaining the standing.',
        },
        {
          'sentenceAr': 'نَتَدَرَّبُ رَغْبَةً فِي الفَوْزِ',
          'sentenceEn': 'We train out of desire for victory',
          'analysisAr': 'رَغْبَةً: مَفْعُولٌ لِأَجْلِهِ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ.',
          'analysisEn': 'Raghbatan: Object of reason showing motive.',
        },
      ],
    },
    {
      'key': 'al_haal',
      'titleAr': 'الحَالُ المَنْصُوبَةُ وَصَاحِبُ الحَالِ',
      'titleEn': 'The Accusative State (Al-Haal) & Its Subject',
      'badgeAr': 'الوحدة 3 (الصف 8)',
      'badgeEn': 'Unit 3 (Grade 8)',
      'ruleAr': 'اسْمٌ نَكِرَةٌ مَنْصُوبٌ يُبَيِّنُ هَيْئَةَ صَاحِبِهِ (المَعْرِفَةِ) عِنْدَ وُقُوعِ الفِعْلِ. يَصْلُحُ جَوَابًا لِسُؤَالِ: (كَيْفَ؟).',
      'ruleEn': 'An indefinite accusative modifier describing the transient physical or emotional state of a definite noun when an action takes place. Answers "How?".',
      'formulaAr': 'فِعْلٌ + فَاعِلٌ (مَعْرِفَة) + حَالٌ نَكِرَةٌ مَنْصُوبَةٌ [ـً]',
      'formulaEn': 'Verb + Definite Agent + Indefinite Accusative State (-an)',
      'examples': [
        {
          'sentenceAr': 'عَادَ الجُنْدِيُّ سَالِمًا',
          'sentenceEn': 'The soldier returned safe and sound',
          'analysisAr': 'سَالِمًا: حَالٌ مَنْصُوبَةٌ بِالفَتْحَةِ بَيَّنَتْ هَيْئَةَ (الجُنْدِيُّ) عِنْدَ العَوْدَةِ.',
          'analysisEn': 'Saliman: Accusative state modifying the returning soldier.',
        },
      ],
    },
  ];

  // PRIMARY GRADES (1-4) CURRICULUM RULES
  static final List<Map<String, dynamic>> _gradePrimaryRules = [
    {
      'key': 'word_parts',
      'titleAr': 'أَقْسَامُ الكَلِمَةِ (اسْمٌ، فِعْلٌ، حَرْفٌ)',
      'titleEn': 'Parts of Speech (Noun, Verb, Particle)',
      'badgeAr': 'المرحلة التأسيسية',
      'badgeEn': 'Primary Foundations',
      'ruleAr': 'تَنْقَسِمُ الكَلِمَاتُ فِي اللُّغَةِ العَرَبِيَّةِ إِلَى: اسْمٍ (يَدُلُّ عَلَى إِنْسَانٍ أَوْ حَيَوَانٍ أَوْ شَيْءٍ)، وَفِعْلٍ (حَدَثٌ مُرْتَبِطٌ بِزَمَنٍ)، وَحَرْفٍ (يَرْبِطُ الكَلِمَاتِ).',
      'ruleEn': 'Words in Arabic are classified into Nouns (people, places, things), Verbs (actions bound to time), and Particles (connectors).',
      'formulaAr': 'كَلِمَةٌ = [اسْمٌ] أَوْ [فِعْلٌ] أَوْ [حَرْفٌ]',
      'formulaEn': 'Word = [Noun] or [Verb] or [Particle]',
      'examples': [
        {
          'sentenceAr': 'قَرَأَ رَاشِدٌ فِي الكِتَابِ',
          'sentenceEn': 'Rashid read in the book',
          'analysisAr': 'قَرَأَ (فِعْلٌ) | رَاشِدٌ (اسْمٌ) | فِي (حَرْفٌ) | الكِتَابِ (اسْمٌ).',
          'analysisEn': 'Qara\'a (Verb) | Rashid (Noun) | Fi (Particle) | Al-Kitab (Noun).',
        },
      ],
    },
  ];

  // SECONDARY GRADES (9-12) CURRICULUM RULES
  static final List<Map<String, dynamic>> _gradeSecondaryRules = [
    {
      'key': 'morphology_participles',
      'titleAr': 'المُشْتَقَّاتُ: اسْمُ الفَاعِلِ وَاسْمُ المَفْعُولِ وَصِيَغُ المُبَالَغَةِ',
      'titleEn': 'Morphological Derivations (Participles & Intensive Forms)',
      'badgeAr': 'المرحلة الثانوية',
      'badgeEn': 'Secondary Advanced',
      'ruleAr': 'أَسْمَاءٌ تُشْتَقُّ مِنْ حُرُوفِ الفِعْلِ لِتَدُلَّ عَلَى مَنْ قَامَ بِالفِعْلِ (اسْمُ فَاعِلٍ: فَاعِل / مُفْعِل)، أَوْ مَنْ وَقَعَ عَلَيْهِ (اسْمُ مَفْعُولٍ: مَفْعُول / مُفْعَل).',
      'ruleEn': 'Derived nouns denoting the doer of an action (Active Participle), the recipient (Passive Participle), or intensified frequency.',
      'formulaAr': 'فِعْلٌ ثُلَاثِيٌّ -> فَاعِلٌ (كَاتِبٌ) | مَفْعُولٌ (مَكْتُوبٌ)',
      'formulaEn': 'Trilateral Root -> Fa\'il (Active) | Maf\'ool (Passive)',
      'examples': [
        {
          'sentenceAr': 'المُخْتَرِعُ مُبْدِعٌ فِي صِنَاعَةِ المُسْتَقْبَلِ',
          'sentenceEn': 'The inventor is creative in building the future',
          'analysisAr': 'المُخْتَرِعُ: اسْمُ فَاعِلٍ مِنْ فِعْلٍ غَيْرِ ثُلَاثِيٍّ (اخْتَرَعَ).',
          'analysisEn': 'Al-Mukhtari\'u: Active participle derived from verb Ikhtara\'a.',
        },
      ],
    },
  ];

  // GRADE 5 CURRICULUM RULES (STATIC MAP)
  static final List<Map<String, dynamic>> _grade5Rules = [
    {
      'key': 'sentence_types',
      'titleAr': 'الجُمْلَةُ الاسْمِيَّةُ وَالجُمْلَةُ الفِعْلِيَّةُ',
      'titleEn': 'Nominal vs Verbal Sentences',
      'badgeAr': 'الوحدة 1 (الصف 5)',
      'badgeEn': 'Unit 1 (Grade 5)',
      'ruleAr': 'الجُمْلَةُ الاسْمِيَّةُ تَبْدَأُ بِاسْمٍ وَتَتَكَوَّنُ مِنْ رُكْنَيْنِ رَئِيسَيْنِ: مُبْتَدَأ وَخَبَر، وَكِلاهُمَا مَرْفُوعٌ بِالضَّمَّةِ. أَمَّا الجُمْلَةُ الفِعْلِيَّةُ فَتَبْدَأُ بِفِعْلٍ وَتَتَكَوَّنُ مِنْ فِعْلٍ وَفَاعِلٍ (مَرْفُوع) وَمَفْعُولٍ بِهِ (مَنْصُوب).',
      'ruleEn': 'A Nominal Sentence starts with a noun and consists of Subject (Mubtada) and Predicate (Khabar), both in nominative case with Damma. A Verbal Sentence starts with a verb and consists of Verb, Subject Agent (Fa\'il, Marfoo), and Direct Object (Maf\'ul Bihi, Mansoob).',
      'formulaAr': 'جملة اسمية: مُبْتَدَأ (مَرْفُوع) + خَبَر (مَرْفُوع) | جملة فعلية: فِعْل + فَاعِل (مَرْفُوع) + مَفْعُول بِهِ (مَنْصُوب)',
      'formulaEn': 'Nominal: Subject (Damma) + Predicate (Damma) | Verbal: Verb + Doer (Damma) + Object (Fatha)',
      'examples': [
        {
          'sentenceAr': 'الكُرَةُ سَرِيعَةٌ',
          'sentenceEn': 'The ball is fast',
          'analysisAr': 'الكُرَةُ: مُبْتَدَأٌ مَرْفُوعٌ بِالضَّمَّةِ | سَرِيعَةٌ: خَبَرٌ مَرْفُوعٌ بِالضَّمَّةِ.',
          'analysisEn': 'Al-Kuratu: Subject noun (Marfoo with Damma) | Saree\'atun: Predicate (Marfoo with Damma).',
        },
        {
          'sentenceAr': 'قَذَفَ اللَّاعِبُ الكُرَةَ',
          'sentenceEn': 'The player kicked the ball',
          'analysisAr': 'قَذَفَ: فِعْلٌ مَاضٍ | اللَّاعِبُ: فَاعِلٌ مَرْفُوعٌ بِالضَّمَّةِ | الكُرَةَ: مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ.',
          'analysisEn': 'Qadhafa: Past verb | Al-La\'ibu: Doer (Marfoo with Damma) | Al-Kurata: Object (Mansoob with Fatha).',
        },
      ],
    },
    {
      'key': 'prepositions',
      'titleAr': 'حُرُوفُ الجَرِّ وَالاسْمُ المَجْرُورُ',
      'titleEn': 'Prepositions & Genitive Nouns',
      'badgeAr': 'الوحدة 1 (الصف 5)',
      'badgeEn': 'Unit 1 (Grade 5)',
      'ruleAr': 'حُرُوفُ الجَرِّ تَدْخُلُ عَلَى الأَسْمَاءِ فَقَطْ وَتَجُرُّهَا بِالكَسْرَةِ الظَّاهِرَةِ. مِنْ أَشْهَرِهَا: (مِنْ، إِلَى، عَنْ، عَلَى، فِي، البَاء، الكَاف، اللَّام).',
      'ruleEn': 'Prepositions prefix nouns exclusively and cause them to enter the genitive case, marked with Kasra (-i sound).',
      'formulaAr': 'حَرْفُ جَرٍّ + اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ',
      'formulaEn': 'Preposition (Harf Jarr) + Genitive Noun (Ism Majroor with Kasra)',
      'examples': [
        {
          'sentenceAr': 'يَلْعَبُ الطُّلاَّبُ فِي المَلْعَبِ',
          'sentenceEn': 'The students play on the pitch',
          'analysisAr': 'فِي: حَرْفُ جَرٍّ | المَلْعَبِ: اسْمٌ مَجْرُورٌ وَعَلامَةُ جَرِّهِ الكَسْرَةُ الظَّاهِرَةُ.',
          'analysisEn': 'Fi: Preposition | Al-Mal\'abi: Genitive noun with Kasra (-i).',
        },
      ],
    },
    {
      'key': 'adverbs',
      'titleAr': 'ظَرْفَا الزَّمَانِ وَالمَكَانِ (المَفْعُولُ فِيهِ)',
      'titleEn': 'Adverbs of Time & Place (Maf\'ul Feeh)',
      'badgeAr': 'الوحدة 2 (الصف 5)',
      'badgeEn': 'Unit 2 (Grade 5)',
      'ruleAr': 'اسْمٌ مَنْصُوبٌ بِالفَتْحَةِ يَدُلُّ عَلَى زَمَانِ وُقُوعِ الفِعْلِ (ظَرْفُ زَمَانٍ) أَوْ مَكَانِ وُقُوعِهِ (ظَرْفُ مَكَانٍ).',
      'ruleEn': 'An accusative noun specifying the time an action took place (Adverb of Time) or location (Adverb of Place).',
      'formulaAr': 'ظَرْفُ زَمَانٍ: (صَبَاحًا، مَسَاءً) | ظَرْفُ مَكَانٍ: (أَمَامَ، خَلْفَ، فَوْقَ)',
      'formulaEn': 'Time: Sabahan, Masa\'an | Place: Amama, Khalfa, Fawqa',
      'examples': [
        {
          'sentenceAr': 'تَدَرَّبَ العَدَّاءُ مَسَاءً',
          'sentenceEn': 'The runner trained in the evening',
          'analysisAr': 'مَسَاءً: ظَرْفُ زَمَانٍ مَنْصُوبٌ وَعَلامَةُ نَصْبِهِ الفَتْحَةُ الظَّاهِرَةُ.',
          'analysisEn': 'Masa\'an: Adverb of Time (Mansoob with Fatha).',
        },
      ],
    },
    {
      'key': 'adjectives',
      'titleAr': 'النَّعْتُ وَالمَنْعُوتُ (الصِّفَةُ وَالمَوْصُوفُ)',
      'titleEn': 'Adjective Agreement (Na\'at & Man\'ut)',
      'badgeAr': 'الوحدة 2 (الصف 5)',
      'badgeEn': 'Unit 2 (Grade 5)',
      'ruleAr': 'النَّعْتُ هُوَ تَابِعٌ يَذْكُرُ صِفَةً فِي اسْمٍ قَبْلَهُ. يَتْبَعُ النَّعْتُ مَنْعُوتَهُ فِي الإِعْرَابِ وَالتَّعْرِيفِ وَالتَّذْكِيرِ وَالعَدَدِ.',
      'ruleEn': 'An adjective describes a preceding noun, matching across case, definiteness, gender, and number.',
      'formulaAr': 'اسْمٌ مَنْعُوتٌ + اسْمٌ نَعْتٌ (مُطَابَقَةٌ كَامِلَةٌ فِي الحَرَكَةِ)',
      'formulaEn': 'Noun (Man\'ut) + Adjective (Na\'at) [100% agreement]',
      'examples': [
        {
          'sentenceAr': 'شَاهَدْتُ المُبَارَاةَ الحَمَاسِيَّةَ',
          'sentenceEn': 'I watched the thrilling match',
          'analysisAr': 'الحَمَاسِيَّةَ: نَعْتٌ مَنْصُوبٌ بِالفَتْحَةِ يَتْبَعُ (المُبَارَاةَ).',
          'analysisEn': 'Al-Hamasiyyata: Adjective agreeing in definite accusative.',
        },
      ],
    },
    {
      'key': 'demonstratives',
      'titleAr': 'أَسْمَاءُ الإِشَارَةِ لِلْقَرِيبِ وَالبَعِيدِ',
      'titleEn': 'Demonstrative Pronouns (Asma\' Al-Isharah)',
      'badgeAr': 'الوحدة 3 (الصف 5)',
      'badgeEn': 'Unit 3 (Grade 5)',
      'ruleAr': 'أَسْمَاءُ الإِشَارَةِ أَلْفَاظٌ يُشَارُ بِهَا إِلَى شَيْءٍ مُعَيَّنٍ: هَذَا، هَذِهِ، هَؤُلاءِ.',
      'ruleEn': 'Demonstratives point to specific referents: Hatha (Masc sing), Hathihi (Fem sing & Non-human pl), Ha\'ula\'i (Human pl).',
      'formulaAr': 'هَذَا (مُذَكَّر) | هَذِهِ (مُؤَنَّث) | هَؤُلاءِ (جَمْع)',
      'formulaEn': 'Hatha (Masc) | Hathihi (Fem) | Ha\'ula\'i (Plural)',
      'examples': [
        {
          'sentenceAr': 'هَذِهِ أَلْعَابٌ رِيَاضِيَّةٌ مُفِيدَةٌ',
          'sentenceEn': 'These are beneficial sports games',
          'analysisAr': 'هَذِهِ: اسْمُ إِشَارَةٍ لِجَمْعِ غَيْرِ العَاقِلِ.',
          'analysisEn': 'Hathihi: Demonstrative used for non-human plural.',
        },
      ],
    },
    {
      'key': 'conjunctions',
      'titleAr': 'حُرُوفُ العَطْفِ وَدَلالَاتُهَا',
      'titleEn': 'Conjunction Particles (Huroof Al-\'Atf)',
      'badgeAr': 'الوحدة 3 (الصف 5)',
      'badgeEn': 'Unit 3 (Grade 5)',
      'ruleAr': 'تَرْبِطُ بَيْنَ كَلِمَتَيْنِ: الوَاوُ (لِلْمُشَارَكَةِ)، الفَاءُ (لِلتَّرْتِيبِ وَالسُّرْعَةِ)، ثُمَّ (لِلتَّرَاخِي)، أَوْ (لِلتَّخْيِيرِ).',
      'ruleEn': 'Conjunctions linking two words: Waw (partnership), Fa (immediate sequence), Thumma (delayed sequence), Aw (choice).',
      'formulaAr': 'مَعْطُوفٌ عَلَيْهِ + حَرْفُ عَطْفٍ + مَعْطُوفٌ',
      'formulaEn': 'Base Word + Conjunction + Joined Word',
      'examples': [
        {
          'sentenceAr': 'حَضَرَ زَايِدٌ وَرَاشِدٌ',
          'sentenceEn': 'Zayed and Rashid arrived together',
          'analysisAr': 'الوَاوُ: حَرْفُ عَطْفٍ | رَاشِدٌ: مَعْطُوفٌ مَرْفُوعٌ بِالضَّمَّةِ.',
          'analysisEn': 'Waw: Conjunction | Rashid: Conjoined noun (Marfoo).',
        },
      ],
    },
  ];
}
