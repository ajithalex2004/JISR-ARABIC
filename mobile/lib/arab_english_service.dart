import 'package:flutter/material.dart';

/// Global state controller for ArabEnglish Pronunciation (Latin phonetic transliteration).
/// Default is strictly ON as per user requirements.
class ArabEnglishState {
  ArabEnglishState._();

  static final ValueNotifier<bool> notifier = ValueNotifier<bool>(true);

  static bool get isEnabled => notifier.value;

  static void toggle() {
    notifier.value = !notifier.value;
  }

  static void set(bool value) {
    notifier.value = value;
  }
}

/// Comprehensive Arabic-to-ArabEnglish (phonetic pronunciation) transliterator.
/// Formats Arabic phrases into natural, readable English phonetics (analogous to Manglish).
class ArabEnglishHelper {
  ArabEnglishHelper._();

  // Curated high-frequency dictionary for Grade 5 curriculum, grammar, and exam phrases
  static const Map<String, String> _curatedMap = {
    // Lesson 1 & Ball Games vocabulary
    'سجل اللاعب الهدف': 'Sajjala al-laa\'ibu al-hadaf',
    'سَجَّلَ اللَّاعِبُ الهَدَفَ': 'Sajjala al-laa\'ibu al-hadaf',
    'كرة القدم': 'Kuratu al-qadam',
    'كُرَةُ القَدَمِ': 'Kuratu al-qadam',
    'كرة القدم لعبة جماعية': 'Kuratu al-qadami lu\'batun jamaa\'iyyah',
    'كُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ': 'Kuratu al-qadami lu\'batun jamaa\'iyyah',
    'يركض الفارس في الميدان': 'Yarkudu al-faarisu fee al-maydaan',
    'يَرْكُضُ الفَارِسُ فِي المَيْدَانِ': 'Yarkudu al-faarisu fee al-maydaan',
    'الساحرة المستديرة': 'Al-saahiratu al-mustadeerah',
    'السَّاحِرَةُ المُسْتَدِيرَةُ': 'Al-saahiratu al-mustadeerah',
    'الروح الرياضية': 'Al-roohu al-riyaadiyyah',
    'الرُّوحُ الرِّيَاضِيَّةُ': 'Al-roohu al-riyaadiyyah',
    'الروح الرياضية واللعب النظيف': 'Al-roohu al-riyaadiyyatu wal-la\'ibu al-natheef',
    'الرُّوحُ الرِّيَاضِيَّةُ وَاللَّعِبُ النَّظِيفُ': 'Al-roohu al-riyaadiyyatu wal-la\'ibu al-natheef',
    'ألعاب الكرة': 'Al\'aabu al-kurah',
    'أَلْعَابُ الكُرَةِ': 'Al\'aabu al-kurah',
    'ركوب الخيل': 'Rukoobu al-khayl',
    'رُكُوبُ الخَيْلِ': 'Rukoobu al-khayl',
    'الجري': 'Al-jary',
    'الفنون': 'Al-funoon',
    'القراءة': 'Al-qiraa\'ah',
    'في مدرستي': 'Fee madrasatee',
    'في بيتي': 'Fee baytee',
    'طعامي': 'Ta\'aamee',
    'ملابسي': 'Malaabisee',
    'وقت المرح': 'Waqtu al-marah',
    'مستدير': 'Mustadeer',
    'مُسْتَدِيرٌ': 'Mustadeer',
    'بيضوي': 'Baydawee',
    'بَيْضَوِيٌّ': 'Baydawee',
    'جماعي': 'Jamaa\'ee',
    'جَمَاعِيٌّ': 'Jamaa\'ee',
    'فردي': 'Fardee',
    'فَرْدِيٌّ': 'Fardee',
    'المباراة': 'Al-mubaaraah',
    'المُبَارَاةُ': 'Al-mubaaraah',
    'الفريق': 'Al-fareeq',
    'الفَرِيقُ': 'Al-fareeq',
    'الملعب': 'Al-mal\'ab',
    'المَلْعَبُ': 'Al-mal\'ab',
    'الحكام': 'Al-hukkaam',
    'الحُكَّامُ': 'Al-hukkaam',
    'حكم الساحة': 'Hakamu al-saahah',
    'حارس المرمى': 'Haarisu al-marma',
    'حَارِسُ المَرْمَى': 'Haarisu al-marma',
    'عشب أخضر': '\'Ushbun akhdar',
    'عُشْبٌ أَخْضَرُ': '\'Ushbun akhdar',
    'عدد اللاعبين': '\'Adadu al-laa\'ibeen',
    'عَدَدُ اللَّاعِبِينَ': '\'Adadu al-laa\'ibeen',
    '11 لاعبا': '11 laa\'iban',
    '١١ لاعباً': '11 laa\'iban',
    'شوط المباراة': 'Shawtu al-mubaaraah',
    '45 دقيقة': '45 daqeeqah',
    'أبعاد الملعب': 'Ab\'aadu al-mal\'ab',
    'طول الملعب': 'Toolu al-mal\'ab',
    'عرض الملعب': '\'Ardu al-mal\'ab',

    // Grammar & Capsules
    'التاء المربوطة والهاء': 'Al-taa\'u al-marbootatu wal-haa\'',
    'التاء المربوطة': 'Al-taa\'u al-marbootah',
    'التاء المفتوحة': 'Al-taa\'u al-maftoohah',
    'مطابقة الفعل للفاعل': 'Mutaabaqatu al-fi\'li lil-faa\'il',
    'جمع المذكر السالم': 'Jam\'u al-mudhakkari al-saalim',
    'جمع المؤنث السالم': 'Jam\'u al-mu\'annathi al-saalim',
    'همزة الوصل والقطع': 'Hamzatu al-wasli wal-qat\'',
    'همزة الوصل': 'Hamzatu al-wasl',
    'همزة القطع': 'Hamzatu al-qat\'',
    'الجملة الاسمية والفعلية': 'Al-jumlatu al-ismiyyatu wal-fi\'liyyah',
    'الجملة الاسمية': 'Al-jumlatu al-ismiyyah',
    'الجملة الفعلية': 'Al-jumlatu al-fi\'liyyah',
    'المبتدأ والخبر': 'Al-mubtada\'u wal-khabar',
    'المبتدأ': 'Al-mubtada\'',
    'الخبر': 'Al-khabar',
    'الفعل والفاعل': 'Al-fi\'lu wal-faa\'il',
    'الفعل': 'Al-fi\'l',
    'الفاعل': 'Al-faa\'il',
    'المفعول به': 'Al-maf\'oolu bihi',
    'حروف الجر': 'Huroofu al-jarr',
    'الاسم المجرور': 'Al-ismu al-majroor',
    'النحو والإعراب': 'Al-nahwu wal-i\'raab',
    'المفردات والتضاد': 'Al-mufradaatu wal-tadaadd',
    'فهم المقروء': 'Fahmu al-maqroo\'',
    'الجذور والاشتقاق': 'Al-judhooru wal-ishtiqaaq',

    // Questions & Exam terms
    'حل السؤال الأول': 'Hallu al-su\'aali al-awwal',
    'حل السؤال الثاني': 'Hallu al-su\'aali al-thaanee',
    'حل السؤال الثالث': 'Hallu al-su\'aali al-thaalith',
    'حل السؤال الرابع': 'Hallu al-su\'aali al-raabi\'',
    'حل السؤال الخامس': 'Hallu al-su\'aali al-khaamis',
    'حل السؤال السادس': 'Hallu al-su\'aali al-saadis',
    'حل السؤال السابع': 'Hallu al-su\'aali al-saabi\'',
    'حل السؤال الثامن': 'Hallu al-su\'aali al-thaamin',
    'حل السؤال التاسع': 'Hallu al-su\'aali al-taasi\'',
    'حل السؤال العاشر': 'Hallu al-su\'aali al-\'aashir',
    'حل السؤال الحادي عشر': 'Hallu al-su\'aali al-haadi \'ashar',
    'حل السؤال الثاني عشر': 'Hallu al-su\'aali al-thaanee \'ashar',
    'حل السؤال الثالث عشر': 'Hallu al-su\'aali al-thaalith \'ashar',
    'السؤال الأول': 'Al-su\'aalu al-awwal',
    'السؤال الثاني': 'Al-su\'aalu al-thaanee',
    'السؤال الثالث': 'Al-su\'aalu al-thaalith',
    'السؤال الرابع': 'Al-su\'aalu al-raabi\'',
    'السؤال الخامس': 'Al-su\'aalu al-khaamis',
    'السؤال السادس': 'Al-su\'aalu al-saadis',
    'السؤال السابع': 'Al-su\'aalu al-saabi\'',
    'السؤال الثامن': 'Al-su\'aalu al-thaamin',
    'السؤال التاسع': 'Al-su\'aalu al-taasi\'',
    'السؤال العاشر': 'Al-su\'aalu al-\'aashir',
    'السؤال الحادي عشر': 'Al-su\'aalu al-haadi \'ashar',
    'السؤال الثاني عشر': 'Al-su\'aalu al-thaanee \'ashar',
    'السؤال الثالث عشر': 'Al-su\'aalu al-thaalith \'ashar',
    'الخطوة الأولى': 'Al-khutwatu al-oola',
    'الخطوة الثانية': 'Al-khutwatu al-thaaniyah',
    'الخطوة الثالثة': 'Al-khutwatu al-thaalithah',
    'الإجابة النموذجية': 'Al-ijaabatu al-namoodhajiyyah',
    'الإجابة الصحيحة': 'Al-ijaabatu al-saheehah',
    'الشرح والتوضيح': 'Al-sharhu wal-tawdeeh',
    'القاعدة المستفادة': 'Al-qaa\'idatu al-mustafaadah',
    'أحسنت يا بطل': 'Ahsanta ya batal',
    'ممتاز': 'Mumtaaz',
    'رائع': 'Raa\'i\'',
    'إجابة صحيحة': 'Ijaabatun saheehah',
    'صح أو خطأ': 'Sah aw khata\'',
    'اختر الإجابة الصحيحة': 'Ikhtar al-ijaabata al-saheehah',
  };

  // Common word-level phonetics
  static const Map<String, String> _wordMap = {
    'في': 'fee',
    'فِي': 'fee',
    'من': 'min',
    'مِن': 'min',
    'إلى': 'ila',
    'إِلَى': 'ila',
    'على': '\'ala',
    'عَلَى': '\'ala',
    'عن': '\'an',
    'عَنْ': '\'an',
    'مع': 'ma\'a',
    'مَعَ': 'ma\'a',
    'هو': 'huwa',
    'هُوَ': 'huwa',
    'هي': 'hiya',
    'هِيَ': 'hiya',
    'هم': 'hum',
    'هُمْ': 'hum',
    'أنا': 'ana',
    'أَنَا': 'ana',
    'نحن': 'nahnu',
    'نَحْنُ': 'nahnu',
    'أنت': 'anta',
    'أَنْتَ': 'anta',
    'أنتِ': 'anti',
    'أَنْتِ': 'anti',
    'هذا': 'haadha',
    'هَذَا': 'haadha',
    'هذه': 'haadhihi',
    'هَذِهِ': 'haadhihi',
    'ذلك': 'dhaalika',
    'ذَلِكَ': 'dhaalika',
    'تلك': 'tilka',
    'تِلْكَ': 'tilka',
    'كل': 'kull',
    'كُلُّ': 'kullu',
    'ما': 'maa',
    'مَا': 'maa',
    'ماذا': 'maadha',
    'مَاذَا': 'maadha',
    'لماذا': 'limaadha',
    'لِمَاذَا': 'limaadha',
    'كيف': 'kayfa',
    'كَيْفَ': 'kayfa',
    'أين': 'ayna',
    'أَيْنَ': 'ayna',
    'متى': 'mata',
    'مَتَى': 'mata',
    'كم': 'kam',
    'كَمْ': 'kam',
    'مَنْ': 'man',
    'هل': 'hal',
    'هَلْ': 'hal',
    'نعم': 'na\'am',
    'نَعَمْ': 'na\'am',
    'لا': 'laa',
    'لَا': 'laa',
    'كان': 'kaana',
    'كَانَ': 'kaana',
    'يكون': 'yakoon',
    'يَكُونُ': 'yakoonu',
    'ليس': 'laysa',
    'لَيْسَ': 'laysa',
    'إن': 'inna',
    'إِنَّ': 'inna',
    'أن': 'anna',
    'أَنَّ': 'anna',
    'لأن': 'li\'anna',
    'لِأَنَّ': 'li\'anna',
    'ثم': 'thumma',
    'ثُمَّ': 'thumma',
    'أو': 'aw',
    'أَوْ': 'aw',
    'و': 'wa',
    'وَ': 'wa',
    'ف': 'fa',
    'فَ': 'fa',
    'ب': 'bi',
    'بِ': 'bi',
    'ل': 'li',
    'لِ': 'li',
    'س': 'sa',
    'سَ': 'sa',
    'الكرة': 'al-kurah',
    'الكُرَةُ': 'al-kuratu',
    'القدم': 'al-qadam',
    'القَدَمِ': 'al-qadami',
    'اللاعب': 'al-laa\'ib',
    'اللَّاعِبُ': 'al-laa\'ibu',
    'الهدف': 'al-hadaf',
    'الهَدَفَ': 'al-hadafa',
    'الملعب': 'al-mal\'ab',
    'المَلْعَبُ': 'al-mal\'abu',
    'الفريق': 'al-fareeq',
    'الفَرِيقُ': 'al-fareequ',
    'المباراة': 'al-mubaaraah',
    'المُبَارَاةُ': 'al-mubaaraatu',
    'الحكام': 'al-hukkaam',
    'الحُكَّامُ': 'al-hukkaamu',
    'لعبة': 'lu\'bah',
    'لُعْبَةٌ': 'lu\'batun',
    'جماعية': 'jamaa\'iyyah',
    'جَمَاعِيَّةٌ': 'jamaa\'iyyatun',
    'فردية': 'fardiyyah',
    'فَرْدِيَّةٌ': 'fardiyyatun',
    'مستدير': 'mustadeer',
    'مُسْتَدِيرٌ': 'mustadeerun',
    'بيضوي': 'baydawee',
    'بَيْضَوِيٌّ': 'baydaweeyun',
    'سحر': 'sihr',
    'سَحَرَتْ': 'saharats',
    'عقول': '\'uqool',
    'عُقُولَ': '\'uqoola',
    'أكثر': 'akthar',
    'أَكْثَرَ': 'akthara',
    'مليار': 'milyaar',
    'مِلْيَارِ': 'milyaari',
    'مشجع': 'mushajji\'',
    'مُشَجِّعٍ': 'mushajji\'in',
    'متابع': 'mutaabi\'',
    'مُتَابِعٍ': 'mutaabi\'in',
    'العالم': 'al-\'aalam',
    'العَالَمِ': 'al-\'aalami',
    'الرسمية': 'al-rasmiyyah',
    'الرَّسْمِيَّةُ': 'al-rasmiyyatu',
    'متر': 'metr',
    'أمتار': 'amtaar',
    'أَمْتَارٍ': 'amtaarin',
    'سنتيمتر': 'santimetr',
    'غرام': 'ghraam',
    'غراما': 'ghraaman',
    'غَرَامًا': 'ghraaman',
    'الماء': 'al-maa\'',
    'المَاءُ': 'al-maa\'u',
    'الشمس': 'ash-shams',
    'الشَّمْسُ': 'ash-shamsu',
    'القمر': 'al-qamar',
    'القَمَرُ': 'al-qamaru',
    'مدرسة': 'madrasah',
    'مَدْرَسَةٌ': 'madrasatun',
    'مدرستي': 'madrasatee',
    'مَدْرَسَتِي': 'madrasatee',
    'طالب': 'taalib',
    'طَالِبٌ': 'taalibun',
    'معلم': 'mu\'allim',
    'مُعَلِّمٌ': 'mu\'allimun',
    'الأستاذ': 'al-ustaadh',
    'الأُسْتَاذُ': 'al-ustaadhu',
    'فاهم': 'Fahim',
    'فَاهِمٌ': 'Faahimun',
  };

  /// Main entrypoint: transliterate Arabic text to ArabEnglish phonetics.
  static String transliterate(String text) {
    if (text.trim().isEmpty) return '';

    // If text has no Arabic characters, return empty or as-is
    if (!RegExp(r'[\u0600-\u06FF]').hasMatch(text)) {
      return '';
    }

    final trimmed = text.trim();

    // Check exact curated match first
    if (_curatedMap.containsKey(trimmed)) {
      return _curatedMap[trimmed]!;
    }

    final normalized = trimmed.replaceAll(RegExp(r'[\u064B-\u065F\u0670\u0640]'), '');
    if (_curatedMap.containsKey(normalized)) {
      return _curatedMap[normalized]!;
    }

    // Process line-by-line
    final lines = trimmed.split('\n');
    final resultLines = <String>[];

    for (final line in lines) {
      final lineTrim = line.trim();
      if (lineTrim.isEmpty) {
        resultLines.add('');
        continue;
      }

      // Check if line contains English translation tag or bullet
      String cleanLine = lineTrim;
      String prefix = '';
      final bulletMatch = RegExp(r'^(\d+[\.\-\)]|\*|\-|•|\([0-9]+\))\s*').firstMatch(cleanLine);
      if (bulletMatch != null) {
        prefix = bulletMatch.group(0)!;
        cleanLine = cleanLine.substring(prefix.length).trim();
      }

      // Check if entire line has curated match
      if (_curatedMap.containsKey(cleanLine)) {
        resultLines.add('$prefix${_curatedMap[cleanLine]!}');
        continue;
      }
      final normLine = cleanLine.replaceAll(RegExp(r'[\u064B-\u065F\u0670\u0640]'), '');
      if (_curatedMap.containsKey(normLine)) {
        resultLines.add('$prefix${_curatedMap[normLine]!}');
        continue;
      }

      // Tokenize line into words and delimiters
      final tokens = _tokenizeLine(cleanLine);
      final outTokens = <String>[];

      for (int i = 0; i < tokens.length; i++) {
        final tok = tokens[i];
        if (tok.trim().isEmpty || RegExp(r'^[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>0-9\s]+$').hasMatch(tok)) {
          // Punctuation / number
          outTokens.add(_convertPunctuation(tok));
          continue;
        }

        // Transliterate individual word
        final transWord = _transliterateWord(tok, isFirstWord: i == 0);
        outTokens.add(transWord);
      }

      final formattedLine = outTokens.join('');
      resultLines.add('$prefix${_capitalizeFirst(formattedLine)}');
    }

    return resultLines.join('\n').trim();
  }

  static List<String> _tokenizeLine(String line) {
    final tokens = <String>[];
    final reg = RegExp(r'([\u0600-\u06FF\u064B-\u065F\u0670\u0640]+|[^\u0600-\u06FF\u064B-\u065F\u0670\u0640]+)');
    for (final m in reg.allMatches(line)) {
      tokens.add(m.group(0)!);
    }
    return tokens;
  }

  static String _convertPunctuation(String p) {
    return p
        .replaceAll('،', ',')
        .replaceAll('؛', ';')
        .replaceAll('؟', '?')
        .replaceAll('«', '"')
        .replaceAll('»', '"')
        .replaceAll('١', '1')
        .replaceAll('٢', '2')
        .replaceAll('٣', '3')
        .replaceAll('٤', '4')
        .replaceAll('٥', '5')
        .replaceAll('٦', '6')
        .replaceAll('٧', '7')
        .replaceAll('٨', '8')
        .replaceAll('٩', '9')
        .replaceAll('٠', '0');
  }

  static String _transliterateWord(String rawWord, {bool isFirstWord = false}) {
    if (rawWord.isEmpty) return '';

    // Direct lookup
    if (_wordMap.containsKey(rawWord)) {
      final w = _wordMap[rawWord]!;
      return isFirstWord ? _capitalizeFirst(w) : w;
    }

    final normWord = rawWord.replaceAll(RegExp(r'[\u064B-\u065F\u0670\u0640]'), '');
    if (_wordMap.containsKey(normWord)) {
      final w = _wordMap[normWord]!;
      return isFirstWord ? _capitalizeFirst(w) : w;
    }

    // Check prefix 'al-' (ال)
    String wordToProcess = rawWord;
    String prefixTrans = '';

    if (normWord.startsWith('ال') && normWord.length > 2) {
      // Strip 'ال'
      if (wordToProcess.startsWith('ال') || wordToProcess.startsWith('الْ') || wordToProcess.startsWith('ٱل')) {
        wordToProcess = wordToProcess.replaceFirst(RegExp(r'^(الْ|ال|ٱلْ|ٱل)'), '');
      } else {
        wordToProcess = wordToProcess.substring(2);
      }
      prefixTrans = 'al-';
    } else if ((normWord.startsWith('وال') || normWord.startsWith('فال') || normWord.startsWith('بال')) && normWord.length > 3) {
      final leadChar = normWord[0] == 'و' ? 'w' : (normWord[0] == 'ف' ? 'f' : 'b');
      wordToProcess = wordToProcess.substring(normWord[0] == 'و' ? 3 : 3);
      prefixTrans = '${leadChar}al-';
    }

    // Algorithmic letter-by-letter transliteration
    final sb = StringBuffer();
    final chars = wordToProcess.runes.toList();

    for (int i = 0; i < chars.length; i++) {
      final ch = String.fromCharCode(chars[i]);

      // Diacritic checks
      if (ch == '\u064E') {
        // Fatha
        sb.write('a');
        continue;
      }
      if (ch == '\u064F') {
        // Damma
        sb.write('u');
        continue;
      }
      if (ch == '\u0650') {
        // Kasra
        sb.write('i');
        continue;
      }
      if (ch == '\u0652') {
        // Sukun
        continue;
      }
      if (ch == '\u0651') {
        // Shadda -> repeat last written character if consonant
        final currStr = sb.toString();
        if (currStr.isNotEmpty) {
          final lastChar = currStr[currStr.length - 1];
          if (RegExp(r'[a-zA-Z]').hasMatch(lastChar) && !'aeiou'.contains(lastChar.toLowerCase())) {
            sb.write(lastChar);
          }
        }
        continue;
      }
      if (ch == '\u064B') {
        // Tanween Fath
        sb.write('an');
        continue;
      }
      if (ch == '\u064C') {
        // Tanween Damm
        sb.write('un');
        continue;
      }
      if (ch == '\u064D') {
        // Tanween Kasr
        sb.write('in');
        continue;
      }
      if (ch == '\u0670') {
        // Dagger alif
        sb.write('aa');
        continue;
      }

      // Consonants and letters
      switch (ch) {
        case 'ء':
        case 'ئ':
        case 'ؤ':
          sb.write('\'');
          break;
        case 'أ':
        case 'إ':
        case 'ٱ':
          sb.write(i == 0 ? (ch == 'إ' ? 'i' : 'a') : '\'');
          break;
        case 'آ':
          sb.write('aa');
          break;
        case 'ا':
          // Long vowel Alif
          sb.write('aa');
          break;
        case 'ب':
          sb.write('b');
          break;
        case 'ت':
          sb.write('t');
          break;
        case 'ث':
          sb.write('th');
          break;
        case 'ج':
          sb.write('j');
          break;
        case 'ح':
          sb.write('h');
          break;
        case 'خ':
          sb.write('kh');
          break;
        case 'د':
          sb.write('d');
          break;
        case 'ذ':
          sb.write('dh');
          break;
        case 'ر':
          sb.write('r');
          break;
        case 'ز':
          sb.write('z');
          break;
        case 'س':
          sb.write('s');
          break;
        case 'ش':
          sb.write('sh');
          break;
        case 'ص':
          sb.write('s');
          break;
        case 'ض':
          sb.write('d');
          break;
        case 'ط':
          sb.write('t');
          break;
        case 'ظ':
          sb.write('dh');
          break;
        case 'ع':
          sb.write('\'');
          break;
        case 'غ':
          sb.write('gh');
          break;
        case 'ف':
          sb.write('f');
          break;
        case 'ق':
          sb.write('q');
          break;
        case 'ك':
          sb.write('k');
          break;
        case 'ل':
          sb.write('l');
          break;
        case 'م':
          sb.write('m');
          break;
        case 'ن':
          sb.write('n');
          break;
        case 'ه':
          sb.write('h');
          break;
        case 'و':
          // Consonant 'w' or long vowel 'oo'
          if (i == 0 || (i > 0 && String.fromCharCode(chars[i - 1]) == '\u064E')) {
            sb.write('w');
          } else {
            sb.write('oo');
          }
          break;
        case 'ي':
          // Consonant 'y' or long vowel 'ee'
          if (i == 0 || (i > 0 && String.fromCharCode(chars[i - 1]) == '\u064E')) {
            sb.write('y');
          } else {
            sb.write('ee');
          }
          break;
        case 'ى':
          sb.write('aa');
          break;
        case 'ة':
          sb.write('ah');
          break;
        default:
          break;
      }
    }

    String stemTrans = sb.toString();

    // Clean multiple identical vowels e.g. 'aaaa' -> 'aa'
    stemTrans = stemTrans.replaceAll(RegExp(r'a{3,}'), 'aa');
    stemTrans = stemTrans.replaceAll(RegExp(r'e{3,}'), 'ee');
    stemTrans = stemTrans.replaceAll(RegExp(r'o{3,}'), 'oo');

    // Combine prefix with stem
    String finalWord = '$prefixTrans$stemTrans';
    if (finalWord.isEmpty) return rawWord;

    if (isFirstWord) {
      finalWord = _capitalizeFirst(finalWord);
    }
    return finalWord;
  }

  static String _capitalizeFirst(String s) {
    if (s.isEmpty) return '';
    for (int i = 0; i < s.length; i++) {
      if (RegExp(r'[a-zA-Z]').hasMatch(s[i])) {
        return s.substring(0, i) + s[i].toUpperCase() + s.substring(i + 1);
      }
    }
    return s;
  }
}

/// Student Toggle Switch for ArabEnglish Pronunciation.
/// Automatically syncs across all pages via [ArabEnglishState.notifier].
class ArabEnglishToggleSwitch extends StatelessWidget {
  final bool compact;
  final Color? activeColor;
  final Color? textColor;

  const ArabEnglishToggleSwitch({
    super.key,
    this.compact = false,
    this.activeColor,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: ArabEnglishState.notifier,
      builder: (context, isEnabled, _) {
        final pillActiveColor = activeColor ?? const Color(0xFF6C5CE7);

        if (compact) {
          return Tooltip(
            message: isEnabled
                ? 'ArabEnglish Pronunciation: ON (نطق الحروف بالإنجليزية مفعّل)'
                : 'ArabEnglish Pronunciation: OFF (نطق الحروف بالإنجليزية معطّل)',
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => ArabEnglishState.toggle(),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isEnabled ? pillActiveColor.withValues(alpha: 0.15) : const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isEnabled ? pillActiveColor : const Color(0xFFCBD5E1),
                    width: 1.2,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isEnabled ? Icons.record_voice_over_rounded : Icons.voice_over_off_rounded,
                      size: 13,
                      color: isEnabled ? pillActiveColor : const Color(0xFF64748B),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Aa ${isEnabled ? 'ON' : 'OFF'}',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: isEnabled ? pillActiveColor : const Color(0xFF64748B),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return Tooltip(
          message: isEnabled
              ? 'Click to turn OFF English pronunciation'
              : 'Click to turn ON English pronunciation (ArabEnglish)',
          child: InkWell(
            borderRadius: BorderRadius.circular(20),
            onTap: () => ArabEnglishState.toggle(),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                gradient: isEnabled
                    ? const LinearGradient(
                        colors: [Color(0xFF6C5CE7), Color(0xFF4F46E5)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : null,
                color: isEnabled ? null : const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isEnabled ? const Color(0xFF4338CA) : const Color(0xFFCBD5E1),
                  width: 1.2,
                ),
                boxShadow: isEnabled
                    ? [
                        BoxShadow(
                          color: const Color(0xFF6C5CE7).withValues(alpha: 0.25),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ]
                    : null,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    isEnabled ? Icons.record_voice_over_rounded : Icons.voice_over_off_rounded,
                    size: 14,
                    color: isEnabled ? Colors.white : const Color(0xFF64748B),
                  ),
                  const SizedBox(width: 5),
                  Text(
                    '🗣️ ArabEnglish',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: isEnabled ? Colors.white : (textColor ?? const Color(0xFF334155)),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                    decoration: BoxDecoration(
                      color: isEnabled ? const Color(0xFF22C55E) : const Color(0xFFE2E8F0),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      isEnabled ? 'ON' : 'OFF',
                      style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w900,
                        color: isEnabled ? Colors.white : const Color(0xFF64748B),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Three Tier Visual Card:
/// Tier 1: 🇸🇦 Arabic Text (Arabic script with vowels, bold RTL)
/// Tier 2: 🗣️ ArabEnglish Pronunciation (Rendered in distinct colored Dark text font)
/// Tier 3: 🇬🇧 English Translation (Clean meaning below)
class ThreeTierArabicCard extends StatelessWidget {
  final String arabic;
  final String? arabEnglish;
  final String? english;
  final Function(String)? onVocalize;
  final bool isUser;
  final String? title;
  final EdgeInsetsGeometry? margin;
  final EdgeInsetsGeometry? padding;
  final Color? backgroundColor;

  const ThreeTierArabicCard({
    super.key,
    required this.arabic,
    this.arabEnglish,
    this.english,
    this.onVocalize,
    this.isUser = false,
    this.title,
    this.margin,
    this.padding,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    if (arabic.trim().isEmpty) return const SizedBox.shrink();

    final pronunciation = arabEnglish != null && arabEnglish!.isNotEmpty
        ? arabEnglish!
        : ArabEnglishHelper.transliterate(arabic);

    return ValueListenableBuilder<bool>(
      valueListenable: ArabEnglishState.notifier,
      builder: (context, isArabEnglishOn, _) {
        return Container(
          margin: margin ?? const EdgeInsets.symmetric(vertical: 4),
          padding: padding ?? const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: backgroundColor ??
                (isUser
                    ? const Color(0xFF6C5CE7)
                    : const Color(0xFFFFFFFF)),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isUser
                  ? const Color(0xFF5B4BD8)
                  : const Color(0xFFE2E8F0),
              width: 1,
            ),
            boxShadow: isUser
                ? null
                : [
                    BoxShadow(
                      color: const Color(0xFF6C5CE7).withValues(alpha: 0.04),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ],
          ),
          child: Column(
            crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
            children: [
              if (title != null && title!.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: isUser
                            ? Colors.white.withValues(alpha: 0.2)
                            : const Color(0xFFEDE9FE),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        title!,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: isUser ? Colors.white : const Color(0xFF6D28D9),
                        ),
                      ),
                    ),
                    if (onVocalize != null)
                      InkWell(
                        onTap: () => onVocalize!(arabic),
                        borderRadius: BorderRadius.circular(12),
                        child: Padding(
                          padding: const EdgeInsets.all(2),
                          child: Icon(
                            Icons.volume_up_rounded,
                            size: 15,
                            color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 6),
              ],

              // Tier 1: Arabic Script
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(
                        arabic,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          height: 1.5,
                          color: isUser ? Colors.white : const Color(0xFF0F172A),
                        ),
                      ),
                    ),
                  ),
                  if (title == null && onVocalize != null) ...[
                    const SizedBox(width: 4),
                    InkWell(
                      onTap: () => onVocalize!(arabic),
                      borderRadius: BorderRadius.circular(12),
                      child: Padding(
                        padding: const EdgeInsets.all(3),
                        child: Icon(
                          Icons.volume_up_rounded,
                          size: 15,
                          color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                        ),
                      ),
                    ),
                  ],
                ],
              ),

              // Tier 2: ArabEnglish Pronunciation (Distinct Colored Dark Text Font)
              if (isArabEnglishOn && pronunciation.isNotEmpty) ...[
                const SizedBox(height: 5),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4.5),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Colors.white.withValues(alpha: 0.18)
                        : const Color(0xFFF1F5F9), // Soft contrasting card for dark text
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isUser
                          ? Colors.white.withValues(alpha: 0.3)
                          : const Color(0xFFCBD5E1),
                      width: 1,
                    ),
                  ),
                  child: Directionality(
                    textDirection: TextDirection.ltr,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 2, right: 6),
                          child: Icon(
                            Icons.record_voice_over_rounded,
                            size: 13,
                            color: isUser ? Colors.white : const Color(0xFF312E81), // Dark Indigo Accent
                          ),
                        ),
                        Expanded(
                          child: RichText(
                            text: TextSpan(
                              children: [
                                TextSpan(
                                  text: 'Pronunciation: ',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w800,
                                    color: isUser
                                        ? Colors.white70
                                        : const Color(0xFF4338CA), // Distinct purple-indigo tag
                                  ),
                                ),
                                TextSpan(
                                  text: pronunciation,
                                  style: TextStyle(
                                    fontSize: 12.5,
                                    fontWeight: FontWeight.w700, // Distinct Dark bold text
                                    letterSpacing: 0.25,
                                    height: 1.35,
                                    color: isUser
                                        ? Colors.white
                                        : const Color(0xFF0F172A), // Distinct High-Contrast Slate-900 Dark text font
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],

              // Tier 3: English Translation
              if (english != null && english!.trim().isNotEmpty) ...[
                const SizedBox(height: 4.5),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Colors.white.withValues(alpha: 0.12)
                        : const Color(0xFFFAFAFA),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isUser
                          ? Colors.white.withValues(alpha: 0.22)
                          : const Color(0xFFE2E8F0),
                    ),
                  ),
                  child: Directionality(
                    textDirection: TextDirection.ltr,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 2, right: 5),
                          child: Icon(
                            Icons.translate_rounded,
                            size: 12,
                            color: isUser ? Colors.white70 : const Color(0xFF059669),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            english!,
                            style: TextStyle(
                              fontSize: 11,
                              fontStyle: FontStyle.italic,
                              height: 1.35,
                              color: isUser ? Colors.white70 : const Color(0xFF475569),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
