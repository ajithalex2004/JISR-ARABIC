import '../chapter1_data.dart';

/// Unified model for a lesson item in the syllabus catalogue
class CurriculumLessonItem {
  final String id;
  final int order;
  final String titleAr;
  final String titleEn;
  final String unitTitleAr;
  final String unitTitleEn;
  final int startPage;
  final bool isFirstChapterDemo;
  final bool isAccessible;
  final String? lockReason;

  const CurriculumLessonItem({
    required this.id,
    required this.order,
    required this.titleAr,
    required this.titleEn,
    required this.unitTitleAr,
    required this.unitTitleEn,
    required this.startPage,
    required this.isFirstChapterDemo,
    required this.isAccessible,
    this.lockReason,
  });

  factory CurriculumLessonItem.fromMap(Map<String, dynamic> map) {
    final bool isDemo = map['is_first_chapter_demo'] == true ||
        map['id'] == 'lesson_01_ball_games' ||
        map['lesson_order'] == 1;

    return CurriculumLessonItem(
      id: map['id']?.toString() ?? '',
      order: map['lesson_order'] is int
          ? map['lesson_order'] as int
          : (int.tryParse(map['lesson_order']?.toString() ?? '1') ?? 1),
      titleAr: map['title_ar']?.toString() ?? '',
      titleEn: map['title_en']?.toString() ?? '',
      unitTitleAr: map['unit_title_ar']?.toString() ?? '',
      unitTitleEn: map['unit_title_en']?.toString() ?? '',
      startPage: map['start_page'] is int
          ? map['start_page'] as int
          : (int.tryParse(map['start_page']?.toString() ?? '1') ?? 1),
      isFirstChapterDemo: isDemo,
      isAccessible: map['is_accessible'] == true || isDemo,
      lockReason: map['lock_reason']?.toString(),
    );
  }
}

/// Fallback catalogue of all 10 UAE MoE Class 5 Term 1 Lessons
const List<CurriculumLessonItem> kClass5Term1Catalogue = [
  CurriculumLessonItem(
    id: 'lesson_01_ball_games',
    order: 1,
    titleAr: 'أَلْعَابُ الكُرَةِ',
    titleEn: 'Ball Games',
    unitTitleAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitTitleEn: 'Sports and Hobbies',
    startPage: 6,
    isFirstChapterDemo: true,
    isAccessible: true,
  ),
  CurriculumLessonItem(
    id: 'lesson_02_horse_riding',
    order: 2,
    titleAr: 'رُكُوبُ الخَيْلِ',
    titleEn: 'Horse Riding',
    unitTitleAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitTitleEn: 'Sports and Hobbies',
    startPage: 16,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_03_running',
    order: 3,
    titleAr: 'الجَرْيُ',
    titleEn: 'Running',
    unitTitleAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
    unitTitleEn: 'Sports and Hobbies',
    startPage: 26,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_04_arts',
    order: 4,
    titleAr: 'الفُنُونُ',
    titleEn: 'Arts',
    unitTitleAr: 'الفُنُونُ وَالإِبْدَاعُ',
    unitTitleEn: 'Arts and Creativity',
    startPage: 36,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_05_reading',
    order: 5,
    titleAr: 'القِرَاءَةُ',
    titleEn: 'Reading',
    unitTitleAr: 'الفُنُونُ وَالإِبْدَاعُ',
    unitTitleEn: 'Arts and Creativity',
    startPage: 46,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_06_at_school',
    order: 6,
    titleAr: 'فِي المَدْرَسَةِ',
    titleEn: 'At School',
    unitTitleAr: 'حَيَاتُنَا المَدْرَسِيَّةُ',
    unitTitleEn: 'Our School Life',
    startPage: 56,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_07_at_home',
    order: 7,
    titleAr: 'فِي البَيْتِ',
    titleEn: 'At Home',
    unitTitleAr: 'حَيَاتُنَا المَدْرَسِيَّةُ',
    unitTitleEn: 'Our School Life',
    startPage: 66,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_08_my_food',
    order: 8,
    titleAr: 'طَعَامِي',
    titleEn: 'My Food',
    unitTitleAr: 'الصِّحَّةُ وَالغِذَاءُ',
    unitTitleEn: 'Health and Nutrition',
    startPage: 76,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_09_my_clothes',
    order: 9,
    titleAr: 'مَلَابِسِي',
    titleEn: 'My Clothes',
    unitTitleAr: 'الهُوِيَّةُ وَالتُّرَاثُ',
    unitTitleEn: 'Identity and Heritage',
    startPage: 86,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
  CurriculumLessonItem(
    id: 'lesson_10_fun_time',
    order: 10,
    titleAr: 'وَقْتُ المَرَحِ',
    titleEn: 'Fun Time',
    unitTitleAr: 'الهُوِيَّةُ وَالتُّرَاثُ',
    unitTitleEn: 'Identity and Heritage',
    startPage: 96,
    isFirstChapterDemo: false,
    isAccessible: false,
    lockReason: r'Payment required ($33/term)',
  ),
];

/// Represents an interactive lesson page with vocalizable text and dual English translations
class LessonContentPage {
  final int printedPage;
  final int pdfPage;
  final String titleAr;
  final String titleEn;
  final List<String> paragraphsAr;
  final List<String> paragraphsEn;

  const LessonContentPage({
    required this.printedPage,
    required this.pdfPage,
    required this.titleAr,
    required this.titleEn,
    required this.paragraphsAr,
    required this.paragraphsEn,
  });

  factory LessonContentPage.fromChapterPage(ChapterPage cp) {
    return LessonContentPage(
      printedPage: cp.printedPage,
      pdfPage: cp.pdfPage,
      titleAr: cp.titleAr,
      titleEn: cp.titleEn,
      paragraphsAr: cp.paragraphsAr,
      paragraphsEn: cp.paragraphsEn,
    );
  }
}

/// Display modes for lesson viewing
enum LessonViewMode {
  textbookReader,
  lparSequence,
}

/// Unified lesson package supporting both static demo fallback and dynamic backend catalog packages
class CurriculumLessonPackage {
  final String lessonId;
  final String titleAr;
  final String titleEn;
  final String unitTitleAr;
  final String unitTitleEn;
  final int grade;
  final int term;
  final int startPage;
  final List<LessonContentPage> pages;
  final List<Map<String, dynamic>> instructionDecoder;
  final List<Map<String, dynamic>> vocabularyCards;
  final Map<String, dynamic>? grammarLab;
  final Map<String, dynamic>? sentenceBuilder;
  final Map<String, dynamic>? listenSpeakStudio;
  final List<Map<String, dynamic>> practiceDrills;
  final Map<String, dynamic>? diagnosticCheck;
  final Map<String, dynamic>? familyGuidance;
  final Map<String, dynamic> rawContent;

  const CurriculumLessonPackage({
    required this.lessonId,
    required this.titleAr,
    required this.titleEn,
    required this.unitTitleAr,
    required this.unitTitleEn,
    required this.grade,
    required this.term,
    required this.startPage,
    required this.pages,
    this.instructionDecoder = const [],
    this.vocabularyCards = const [],
    this.grammarLab,
    this.sentenceBuilder,
    this.listenSpeakStudio,
    this.practiceDrills = const [],
    this.diagnosticCheck,
    this.familyGuidance,
    this.rawContent = const {},
  });

  factory CurriculumLessonPackage.fromStaticChapter1() {
    return CurriculumLessonPackage(
      lessonId: 'lesson_01_ball_games',
      titleAr: 'أَلْعَابُ الكُرَةِ',
      titleEn: 'Ball Games',
      unitTitleAr: 'الرِّيَاضَاتُ وَالهِوَايَاتُ',
      unitTitleEn: 'Sports and Hobbies',
      grade: 5,
      term: 1,
      startPage: 6,
      pages: kChapter1Pages.map((cp) => LessonContentPage.fromChapterPage(cp)).toList(),
      instructionDecoder: const [
        {
          'verb_ar': 'أَسْتَمِعُ',
          'transliteration': "Astami'u",
          'meaning_en': 'I listen',
          'action_guidance': 'Listen to the commentator describing the ball games.',
          'sample_sentence_ar': 'أَسْتَمِعُ إِلَى تَعلِيقِ المُبَارَاةِ.',
        },
        {
          'verb_ar': 'أَقْرَأُ',
          'transliteration': "Aqra'u",
          'meaning_en': 'I read',
          'action_guidance': 'Read the sports text about football and basketball rules.',
          'sample_sentence_ar': 'أَقْرَأُ نَصَّ أَلْعَابِ الكُرَةِ.',
        },
        {
          'verb_ar': 'أُقَارِنُ',
          'transliteration': 'Uqarinu',
          'meaning_en': 'I compare',
          'action_guidance': 'Compare individual and team ball sports.',
          'sample_sentence_ar': 'أُقَارِنُ بَيْنَ كُرَةِ القَدَمِ وَكُرَةِ السَّلَّةِ.',
        },
      ],
      vocabularyCards: const [
        {
          'word_ar': 'كُرَةُ القَدَمِ',
          'meaning_en': 'Football / Soccer',
          'root': 'ق-د-م',
          'example_ar': 'كُرَةُ القَدَمِ هِيَ الرِّيَاضَةُ الأَكْثَرُ شَعْبِيَّةً.',
        },
        {
          'word_ar': 'كُرَةُ السَّلَّةِ',
          'meaning_en': 'Basketball',
          'root': 'س-ل-ل',
          'example_ar': 'نَرْمِي الكُرَةَ دَاخِلَ السَّلَّةِ لِتَسْجِيلِ النِّقَاطِ.',
        },
        {
          'word_ar': 'المَلْعَبُ',
          'meaning_en': 'Playground / Stadium',
          'root': 'ل-ع-ب',
          'example_ar': 'يَجْتَمِعُ التَّلَامِيذُ فِي المَلْعَبِ صَبَاحًا.',
        },
        {
          'word_ar': 'الفَرِيقُ',
          'meaning_en': 'Team / Squad',
          'root': 'ف-ر-ق',
          'example_ar': 'فَرِيقُنَا المَدْرَسِيُّ فَازَ بِالمُبَارَاةِ.',
        },
      ],
      grammarLab: const {
        'title_ar': 'مختبر القواعد: الجملة الفعلية (الفعل والفاعل)',
        'title_en': 'Grammar Lab: Verbal Sentences (Verb and Subject)',
        'rule_ar': 'تبدأ الجملة الفعلية بفعل (يَلْعَبُ) يليه الفاعل المرفوع بالضمة (الفَرِيقُ).',
        'rule_en': 'Verbal sentences begin with a verb followed by the nominative subject.',
        'example_ar': 'يَلْعَبُ الطُّلَّابُ كُرَةَ القَدَمِ بِنَشَاطٍ.',
        'example_en': 'The students play football actively.',
      },
      sentenceBuilder: const {
        'title_ar': 'باني الجمل الرياضية',
        'title_en': 'Sentence Construction Studio',
        'target_sentence_ar': 'يَلْعَبُ الفَرِيقُ كُرَةَ القَدَمِ فِي المَلْعَبِ.',
        'scrambled_tokens': ['فِي', 'كُرَةَ', 'المَلْعَبِ.', 'يَلْعَبُ', 'الفَرِيقُ', 'القَدَمِ'],
        'translation_en': 'The team plays football in the stadium.',
      },
      listenSpeakStudio: const {
        'title_ar': 'استوديو الاستماع والتحدث: مباريات الكرة',
        'title_en': 'Listen & Speak Studio: Ball Matches',
        'listening_passage_ar': 'تَبْدَأُ المُبَارَاةُ بِصَافِرَةِ الحَكَمِ، وَيَتَعَاوَنُ أَعْضَاءُ الفَرِيقِ لِتَسْجِيلِ الهَدَفِ.',
        'pronunciation_target_ar': 'يَتَعَاوَنُ الفَرِيقُ لِتَحْقِيقِ الفَوْزِ فِي المَلْعَبِ.',
        'pronunciation_target_en': 'The team cooperates to achieve victory in the playground.',
      },
      diagnosticCheck: const {
        'title_ar': 'اختبار الإتقان لدرس ألعاب الكرة',
        'title_en': 'Formative Mastery Diagnostic',
        'questions': [
          {
            'prompt_ar': 'مَا هُوَ شَرْطُ تَسْجِيلِ النِّقَاطِ فِي كُرَةِ السَّلَّةِ؟',
            'prompt_en': 'What is the condition to score points in basketball?',
            'options': [
              {'label_ar': 'إِدْخَالُ الكُرَةِ فِي السَّلَّةِ', 'label_en': 'Putting the ball inside the basket', 'is_correct': true},
              {'label_ar': 'رَكْلُ الكُرَةِ بِالقَدَمِ', 'label_en': 'Kicking the ball with foot', 'is_correct': false},
              {'label_ar': 'الجَرْيُ دُونَ كُرَةٍ', 'label_en': 'Running without ball', 'is_correct': false},
            ],
          },
          {
            'prompt_ar': 'أَيْنَ يُقَامُ سِبَاقُ وَمُبَارَيَاتُ الكُرَةِ المَدْرَسِيَّةِ؟',
            'prompt_en': 'Where are school ball matches held?',
            'options': [
              {'label_ar': 'فِي المَلْعَبِ الرِّيَاضِيِّ', 'label_en': 'In the sports field', 'is_correct': true},
              {'label_ar': 'فِي غُرْفَةِ الصَّفِّ', 'label_en': 'In the classroom', 'is_correct': false},
              {'label_ar': 'فِي المَكْتَبَةِ', 'label_en': 'In the library', 'is_correct': false},
            ],
          }
        ]
      },
      familyGuidance: const {
        'title_en': 'Family Guidance for Ball Games',
        'tip_en': "Encourage your child to name 3 ball sports in Arabic: 'Kurat Al-Qadam' (football), 'Kurat As-Sallah' (basketball), and 'Kurat At-Tawilah' (table tennis)!",
      },
    );
  }

  factory CurriculumLessonPackage.fromBackend(String lessonId, Map<String, dynamic> rawJson) {
    final content = rawJson['content'] is Map<String, dynamic>
        ? rawJson['content'] as Map<String, dynamic>
        : (rawJson['content'] is Map
            ? Map<String, dynamic>.from(rawJson['content'] as Map)
            : rawJson);

    final lessonMeta = rawJson['lesson'] is Map
        ? Map<String, dynamic>.from(rawJson['lesson'] as Map)
        : <String, dynamic>{};

    final titleAr = lessonMeta['title_ar']?.toString() ??
        content['title_ar']?.toString() ??
        'دَرْسٌ جَدِيدٌ';
    final titleEn = lessonMeta['title_en']?.toString() ??
        content['title_en']?.toString() ??
        'Lesson';
    final unitTitleAr =
        content['unit_title_ar']?.toString() ?? 'المِنْهَاجُ الدِّرَاسِيُّ';
    final unitTitleEn =
        content['unit_title_en']?.toString() ?? 'Curriculum Unit';
    final grade = lessonMeta['grade'] is int
        ? lessonMeta['grade'] as int
        : (content['grade'] is int ? content['grade'] as int : 5);
    final term = lessonMeta['term'] is int
        ? lessonMeta['term'] as int
        : (content['term'] is int ? content['term'] as int : 1);
    final startPage = content['start_page'] is int
        ? content['start_page'] as int
        : 6;
    final pdfStart = content['pdf_start_page'] is int
        ? content['pdf_start_page'] as int
        : startPage + 2;

    final pages = <LessonContentPage>[];

    // Page 1: نَوَاتِجُ التَّعَلُّمِ وَالمَسَارَاتُ (Learning Outcomes & Paths)
    final learningPaths = content['learning_paths'] as Map?;
    final p1Ar = <String>[];
    final p1En = <String>[];
    if (learningPaths != null) {
      learningPaths.forEach((key, val) {
        if (val is Map) {
          final tAr = val['title_ar']?.toString() ?? '';
          final tEn = val['title_en']?.toString() ?? '';
          final target = val['target']?.toString() ?? '';
          final pacing = val['pacing']?.toString() ?? '';
          if (tAr.isNotEmpty && target.isNotEmpty) {
            p1Ar.add('$tAr: $target');
            p1En.add('$tEn: $pacing');
          }
        }
      });
    }
    if (p1Ar.isEmpty) {
      p1Ar.add(
          'نَوَاتِجُ التَّعَلُّمِ: أَنْ يَقْرَأَ الطَّالِبُ نَصَّ ($titleAr) قِرَاءَةً جَهْرِيَّةً مُعَبِّرَةً، وَيَفْهَمَ مَعَانِيَ الكَلِمَاتِ الجَدِيدَةِ.');
      p1En.add(
          'Learning Outcomes: The student reads the text of ($titleEn) with expressive fluency and understands new vocabulary.');
    }
    pages.add(LessonContentPage(
      printedPage: startPage,
      pdfPage: pdfStart,
      titleAr: 'نَوَاتِجُ التَّعَلُّمِ - $titleAr',
      titleEn: 'Learning Outcomes - $titleEn',
      paragraphsAr: p1Ar,
      paragraphsEn: p1En,
    ));

    // Page 2: قَامُوسِي وَالمُفْرَدَاتُ (Vocabulary Bank & Glossary)
    final vocabCards =
        (content['vocabulary_cards'] as List?)?.whereType<Map>().toList() ?? [];
    final p2Ar = <String>[];
    final p2En = <String>[];
    for (final v in vocabCards) {
      final word = v['vowelled_ar'] ?? v['word_ar'] ?? '';
      final defAr = v['definition_ar'] ?? '';
      final exAr = v['example_ar'] ?? '';
      final meaningEn = v['meaning_en'] ?? '';
      final exEn = v['example_en'] ?? '';
      if (word.isNotEmpty) {
        p2Ar.add('$word: $defAr مِثَالٌ: $exAr');
        p2En.add('$meaningEn. Example: $exEn');
      }
    }
    if (p2Ar.isNotEmpty) {
      pages.add(LessonContentPage(
        printedPage: startPage + 1,
        pdfPage: pdfStart + 1,
        titleAr: 'قَامُوسِي وَالمُفْرَدَاتُ',
        titleEn: 'My Glossary & Vocabulary Bank',
        paragraphsAr: p2Ar,
        paragraphsEn: p2En,
      ));
    }

    // Page 3: النَّصُّ القِرَائِيُّ وَالاسْتِمَاعُ (Reading Text & Listening Studio)
    final studio = content['listen_speak_studio'] as Map?;
    final passageAr = studio?['passage_ar']?.toString() ?? '';
    final passageEn = studio?['passage_en']?.toString() ?? '';
    final p3Ar = <String>[];
    final p3En = <String>[];
    if (passageAr.isNotEmpty) {
      final arSentences = passageAr
          .split(RegExp(r'(?<=[.؟!])\s+'))
          .where((s) => s.trim().isNotEmpty)
          .toList();
      final enSentences = passageEn
          .split(RegExp(r'(?<=[.?!])\s+'))
          .where((s) => s.trim().isNotEmpty)
          .toList();
      if (arSentences.isNotEmpty) {
        for (var i = 0; i < arSentences.length; i++) {
          p3Ar.add(arSentences[i]);
          p3En.add(i < enSentences.length ? enSentences[i] : '');
        }
      } else {
        p3Ar.add(passageAr);
        p3En.add(passageEn);
      }
    } else {
      p3Ar.add(
          'النَّصُّ القِرَائِيُّ لِدَرْسِ ($titleAr): يُعَدُّ هَذَا المَوْضُوعُ مِنْ أَهَمِّ المَوْضُوعَاتِ فِي ثَقَافَةِ وَتُرَاثِ دَوْلَةِ الإِمَارَاتِ.');
      p3En.add(
          'Reading passage for ($titleEn): This topic is one of the most prominent aspects of UAE culture and heritage.');
    }
    pages.add(LessonContentPage(
      printedPage: startPage + 2,
      pdfPage: pdfStart + 2,
      titleAr: studio?['title_ar']?.toString() ?? 'النَّصُّ القِرَائِيُّ',
      titleEn: studio?['title_en']?.toString() ?? 'Reading Text & Audio Studio',
      paragraphsAr: p3Ar,
      paragraphsEn: p3En,
    ));

    // Page 4: مُفَكِّكُ التَّعْلِيمَاتِ (Instruction Decoder)
    final decoders =
        (content['instruction_decoder'] as List?)?.whereType<Map>().toList() ??
            [];
    if (decoders.isNotEmpty) {
      final p4Ar = <String>[];
      final p4En = <String>[];
      for (final d in decoders) {
        final verbAr = d['verb_ar'] ?? '';
        final sAr = d['sample_sentence_ar'] ?? '';
        final meanEn = d['meaning_en'] ?? '';
        final actionEn = d['action_guidance'] ?? '';
        p4Ar.add('$verbAr: $sAr');
        p4En.add('$meanEn: $actionEn');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 3,
        pdfPage: pdfStart + 3,
        titleAr: 'مُفَكِّكُ التَّعْلِيمَاتِ الصَّفِّيَّةِ',
        titleEn: 'Classroom Instruction Decoder',
        paragraphsAr: p4Ar,
        paragraphsEn: p4En,
      ));
    }

    // Page 5: مُخْتَبَرُ القَوَاعِدِ (Grammar Lab)
    final grammarLabMap = content['grammar_lab'] as Map?;
    if (grammarLabMap != null) {
      final sections =
          (grammarLabMap['sections'] as List?)?.whereType<Map>().toList() ?? [];
      final p5Ar = <String>[];
      final p5En = <String>[];
      for (final s in sections) {
        final ruleAr = s['rule_name_ar'] ?? '';
        final ruleEn = s['rule_name_en'] ?? '';
        final expEn = s['explanation_en'] ?? '';
        final examples =
            (s['examples'] as List?)?.whereType<Map>().toList() ?? [];
        final exArJoined =
            examples.map((e) => e['phrase_ar']).whereType<String>().join(' | ');
        final exEnJoined = examples
            .map((e) => e['translation_en'])
            .whereType<String>()
            .join(' | ');

        p5Ar.add('القَاعِدَةُ: $ruleAr. أَمْثِلَةٌ: $exArJoined');
        p5En.add('$ruleEn: $expEn Examples: $exEnJoined');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 4,
        pdfPage: pdfStart + 4,
        titleAr: grammarLabMap['title_ar']?.toString() ?? 'مُخْتَبَرُ القَوَاعِدِ',
        titleEn: grammarLabMap['title_en']?.toString() ?? 'Grammar Lab',
        paragraphsAr: p5Ar,
        paragraphsEn: p5En,
      ));
    }

    // Page 6: بَانِي الجُمَلِ (Sentence Builder Studio)
    final sentenceBuilderMap = content['sentence_builder'] as Map?;
    if (sentenceBuilderMap != null) {
      final challenges =
          (sentenceBuilderMap['challenges'] as List?)?.whereType<Map>().toList() ??
              [];
      final p6Ar = <String>[];
      final p6En = <String>[];
      for (final c in challenges) {
        final targetAr = c['target_sentence_ar'] ?? '';
        final transEn = c['translation_en'] ?? '';
        final instEn = c['instruction_en'] ?? '';
        p6Ar.add('الجُمْلَةُ المُسْتَهْدَفَةُ: $targetAr');
        p6En.add('$instEn: $transEn');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 5,
        pdfPage: pdfStart + 5,
        titleAr: sentenceBuilderMap['title_ar']?.toString() ?? 'بَانِي الجُمَلِ',
        titleEn:
            sentenceBuilderMap['title_en']?.toString() ?? 'Sentence Construction Studio',
        paragraphsAr: p6Ar,
        paragraphsEn: p6En,
      ));
    }

    // Page 7: الأَنْشِطَةُ التَّطْبِيقِيَّةُ (Practice Activities)
    final activities =
        (content['practice_activities'] as List?)?.whereType<Map>().toList() ??
            [];
    if (activities.isNotEmpty) {
      final p7Ar = <String>[];
      final p7En = <String>[];
      for (final a in activities) {
        final promptAr = a['prompt_ar'] ?? '';
        final promptEn = a['prompt_en'] ?? '';
        final opts =
            (a['options'] as List?)?.whereType<Map>().toList() ?? [];
        final optArJoined =
            opts.map((o) => o['label_ar']).whereType<String>().join(' ، ');
        p7Ar.add('السُّؤَالُ: $promptAr (الخِيَارَاتُ: $optArJoined)');
        p7En.add('Exercise: $promptEn');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 6,
        pdfPage: pdfStart + 6,
        titleAr: 'الأَنْشِطَةُ وَالتَّدْرِيبَاتُ',
        titleEn: 'Practice Activities & Checks',
        paragraphsAr: p7Ar,
        paragraphsEn: p7En,
      ));
    }

    // Page 8: اسْتُودْيُو الاسْتِمَاعِ وَالنُّطْقِ (Speaking Scripts)
    final audioScripts =
        (studio?['audio_scripts'] as List?)?.whereType<Map>().toList() ?? [];
    if (audioScripts.isNotEmpty) {
      final p8Ar = <String>[];
      final p8En = <String>[];
      for (final scr in audioScripts) {
        p8Ar.add(scr['text_ar']?.toString() ?? '');
        p8En.add(scr['text_en']?.toString() ?? '');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 7,
        pdfPage: pdfStart + 7,
        titleAr: 'اسْتُودْيُو الاسْتِمَاعِ وَالنُّطْقِ',
        titleEn: 'Speaking & Pronunciation Studio',
        paragraphsAr: p8Ar,
        paragraphsEn: p8En,
      ));
    }

    // Page 9: اخْتِبَارُ الاسْتِعْدَادِ (Prep Check & Diagnostic)
    final prepCheck = content['prep_check'] as Map?;
    if (prepCheck != null) {
      final questions =
          (prepCheck['questions'] as List?)?.whereType<Map>().toList() ?? [];
      final p9Ar = <String>[];
      final p9En = <String>[];
      for (final q in questions) {
        final promptAr = q['prompt_ar'] ?? '';
        final promptEn = q['prompt_en'] ?? '';
        final expEn = q['explanation_en'] ?? '';
        p9Ar.add('سُؤَالُ التَّشْخِيصِ: $promptAr');
        p9En.add('$promptEn (Explanation: $expEn)');
      }
      pages.add(LessonContentPage(
        printedPage: startPage + 8,
        pdfPage: pdfStart + 8,
        titleAr: prepCheck['title_ar']?.toString() ?? 'اخْتِبَارُ الاسْتِعْدَادِ',
        titleEn:
            prepCheck['title_en']?.toString() ?? 'Prerequisite Diagnostic Check',
        paragraphsAr: p9Ar,
        paragraphsEn: p9En,
      ));
    }

    // Page 10: المُرَاجَعَةُ الشَّامِلَةُ وَتَوْجِيهَاتُ الأُسْرَةِ
    final parentTips =
        (content['parent_coaching_tips'] as List?)?.whereType<String>().toList() ??
            [];
    final p10Ar = <String>[
      'مُرَاجَعَةُ الدَّرْسِ: قَامَ الطَّالِبُ بِإِتْمَامِ كَافَّةِ فَقَرَاتِ دَرْسِ ($titleAr).',
      'تَوْجِيهَاتٌ عَائِلِيَّةٌ: شَجِّعْ طِفْلَكَ عَلَى التَّحَدُّثِ بِاللُّغَةِ العَرَبِيَّةِ عَنْ هَذَا المَوْضُوعِ فِي المَنْزِلِ.',
    ];
    final p10En = <String>[
      'Lesson Review: The student completed all interactive sections of ($titleEn).',
      parentTips.isNotEmpty
          ? 'Family Guidance: ${parentTips.first}'
          : 'Encourage your child to discuss this topic in Arabic at home.',
    ];
    pages.add(LessonContentPage(
      printedPage: startPage + 9,
      pdfPage: pdfStart + 9,
      titleAr: 'المُرَاجَعَةُ الشَّامِلَةُ وَتَوْجِيهَاتُ الأُسْرَةِ',
      titleEn: 'Chapter Review & Family Guidance',
      paragraphsAr: p10Ar,
      paragraphsEn: p10En,
    ));

    final instructionDecoder = (content['instruction_decoder'] as List? ?? [])
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    final vocabularyCards = (content['vocabulary_cards'] as List? ?? [])
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    final grammarLab = content['grammar_lab'] is Map
        ? Map<String, dynamic>.from(content['grammar_lab'] as Map)
        : null;

    final sentenceBuilder = content['sentence_builder'] is Map
        ? Map<String, dynamic>.from(content['sentence_builder'] as Map)
        : null;

    final listenSpeakStudio = content['listen_speak_studio'] is Map
        ? Map<String, dynamic>.from(content['listen_speak_studio'] as Map)
        : null;

    final practiceDrills = (content['practice_drills'] as List? ?? [])
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    final diagnosticCheck = content['diagnostic_check'] is Map
        ? Map<String, dynamic>.from(content['diagnostic_check'] as Map)
        : (content['prep_check'] is Map
            ? Map<String, dynamic>.from(content['prep_check'] as Map)
            : null);

    final familyGuidance = content['family_guidance'] is Map
        ? Map<String, dynamic>.from(content['family_guidance'] as Map)
        : null;

    return CurriculumLessonPackage(
      lessonId: lessonId,
      titleAr: titleAr,
      titleEn: titleEn,
      unitTitleAr: unitTitleAr,
      unitTitleEn: unitTitleEn,
      grade: grade,
      term: term,
      startPage: startPage,
      pages: pages,
      instructionDecoder: instructionDecoder,
      vocabularyCards: vocabularyCards,
      grammarLab: grammarLab,
      sentenceBuilder: sentenceBuilder,
      listenSpeakStudio: listenSpeakStudio,
      practiceDrills: practiceDrills,
      diagnosticCheck: diagnosticCheck,
      familyGuidance: familyGuidance,
      rawContent: content,
    );
  }
}

/// Dynamic total textbook pages lookup across UAE MoE Grades 1-10 and Terms 1-3.
int getTextbookPageCount(int grade, int term) {
  switch (grade) {
    case 1:
      if (term == 1) return 112;
      if (term == 2) return 99;
      if (term == 3) return 93;
      return 112;
    case 2:
      if (term == 1) return 112;
      if (term == 2) return 74;
      if (term == 3) return 68;
      return 112;
    case 3:
      if (term == 1) return 112;
      if (term == 2) return 71;
      if (term == 3) return 47;
      return 112;
    case 4:
      if (term == 1) return 112;
      if (term == 2) return 72;
      if (term == 3) return 68;
      return 112;
    case 5:
      if (term == 1) return 112;
      if (term == 2) return 72;
      if (term == 3) return 46;
      return 112;
    case 6:
      if (term == 1) return 116;
      if (term == 2) return 72;
      if (term == 3) return 67;
      return 116;
    case 7:
      if (term == 1) return 112;
      if (term == 2) return 73;
      if (term == 3) return 68;
      return 112;
    case 8:
      if (term == 1) return 51;
      if (term == 2) return 72;
      if (term == 3) return 67;
      return 72;
    case 9:
      if (term == 1) return 100;
      if (term == 2) return 73;
      if (term == 3) return 67;
      return 100;
    case 10:
      if (term == 1) return 63;
      if (term == 2) return 71;
      if (term == 3) return 67;
      return 71;
    default:
      return 112;
  }
}
