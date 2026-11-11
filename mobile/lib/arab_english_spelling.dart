/// Letter-by-letter Arab-English (Arabizi) spelling of one vowelled Arabic word.
///
/// Line-for-line port of frontend/src/services/arabEnglishSpelling.ts (the rules are
/// documented there); change both together. Kept free of Flutter so it can be tested with
/// plain `dart test`.
library;

const _fatha = 'َ';
const _damma = 'ُ';
const _kasra = 'ِ';
const _sukun = 'ْ';
const _shadda = 'ّ';
const _tanweenFath = 'ً';
const _tanweenDamm = 'ٌ';
const _tanweenKasr = 'ٍ';
const _daggerAlif = 'ٰ';
const _tatweel = 'ـ';

const _vowelSigns = {_fatha, _damma, _kasra, _tanweenFath, _tanweenDamm, _tanweenKasr, _shadda};
const _marks = {_fatha, _damma, _kasra, _sukun, _shadda, _tanweenFath, _tanweenDamm, _tanweenKasr, _daggerAlif, _tatweel};

const _consonants = {
  'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dh', 'ر': 'r',
  'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'dh', 'ع': "'", 'غ': 'gh',
  'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
};

const _hamzaSeatsStart = {'أ', 'إ', 'ٱ', 'ا'};

final _allMarks = RegExp(r'[ً-ٰٟـ]');

/// Splits a leading article (ال, وال, فال, بال, كال, لل) off a vowelled word.
({String prefix, String stem}) splitArticle(String rawWord) {
  final plain = rawWord.replaceAll(_allMarks, '');
  if (plain.startsWith('لل') && plain.length > 3) {
    final m = RegExp(r'^ل[ً-ْ]*ل[ْ]?').firstMatch(rawWord);
    if (m != null) return (prefix: 'lil-', stem: rawWord.substring(m.end));
  }
  if (plain.startsWith('ال') && plain.length > 2) {
    final m = RegExp(r'^[اٱ][ً-ْ]*ل[ْ]?').firstMatch(rawWord);
    if (m != null) return (prefix: 'al-', stem: rawWord.substring(m.end));
  }
  // wa-, fa-, bi-, ka- + al-: the article's alif is not pronounced after the prefix.
  const lead = {'و': 'wal-', 'ف': 'fal-', 'ب': 'bil-', 'ك': 'kal-'};
  if (plain.isNotEmpty && lead.containsKey(plain[0]) && plain.substring(1).startsWith('ال') && plain.length > 3) {
    final m = RegExp(r'^[وفبك][ً-ْ]*[اٱ][ً-ْ]*ل[ْ]?').firstMatch(rawWord);
    if (m != null) return (prefix: lead[plain[0]]!, stem: rawWord.substring(m.end));
  }
  return (prefix: '', stem: rawWord);
}

/// Arab-English spelling of a word with its article already removed.
String spellStem(String stem, {bool afterArticle = false}) {
  final chars = stem.runes.map(String.fromCharCode).toList();
  String? at(int i) => i >= 0 && i < chars.length ? chars[i] : null;
  bool isVowelSign(String? c) => c != null && _vowelSigns.contains(c);
  List<String> marksAfter(int i) {
    final marks = <String>[];
    for (var j = i + 1; j < chars.length && _marks.contains(chars[j]); j++) {
      marks.add(chars[j]);
    }
    return marks;
  }

  var out = '';
  var lastConsonant = '';
  var consonantEnd = 0; // where the last consonant ends in `out`, so a shadda doubles it before its vowel
  var firstLetterSeen = false;
  var skipShadda = false;

  void add(String s, [String consonant = '']) {
    out += s;
    if (consonant.isNotEmpty) {
      lastConsonant = consonant;
      consonantEnd = out.length;
    }
  }

  void lengthen(String short, String long) {
    if (out.endsWith(short) && !out.endsWith(long)) {
      out = out.substring(0, out.length - short.length) + long;
    } else if (!out.endsWith(long)) {
      out += long;
    }
  }

  for (var i = 0; i < chars.length; i++) {
    final ch = chars[i];
    final isFirstLetter = !firstLetterSeen && !_marks.contains(ch);
    if (!_marks.contains(ch)) firstLetterSeen = true;
    // The sun letter after al- carries a shadda that is not written twice (al-riyaada).
    if (isFirstLetter && afterArticle && marksAfter(i).contains(_shadda)) skipShadda = true;

    switch (ch) {
      case _fatha:
        add('a');
        continue;
      case _damma:
        add('u');
        continue;
      case _kasra:
        add('i');
        continue;
      case _sukun:
      case _tatweel:
        continue;
      case _tanweenFath:
        add('an');
        continue;
      case _tanweenDamm:
        add('un');
        continue;
      case _tanweenKasr:
        add('in');
        continue;
      case _daggerAlif:
        lengthen('a', 'aa');
        continue;
      case _shadda:
        if (skipShadda) {
          skipShadda = false;
          continue;
        }
        if (lastConsonant.isNotEmpty) {
          // Text stores the vowel before or after the shadda; the doubled letter goes before it.
          out = out.substring(0, consonantEnd) + lastConsonant + out.substring(consonantEnd);
          consonantEnd += lastConsonant.length;
        }
        continue;
    }

    final cons = _consonants[ch];
    if (cons != null) {
      add(cons, cons);
      continue;
    }

    if (i == 0 && _hamzaSeatsStart.contains(ch)) {
      // The vowel sign after it is the sound; unvowelled, guess from the seat.
      if (!(at(i + 1) != null && _marks.contains(at(i + 1)))) {
        // A bare alif before a letter with sukun is the hamzat wasl of اِخْتِبَار: read "i".
        final nextLetterSilent = ch == 'ا' && marksAfter(i + 1).contains(_sukun);
        add(ch == 'إ' || nextLetterSilent ? 'i' : 'a');
      }
      lastConsonant = '';
      continue;
    }

    switch (ch) {
      case 'ء':
      case 'ئ':
      case 'ؤ':
      case 'أ':
      case 'إ':
        add("'", "'");
        break;
      case 'آ':
        add(i == 0 ? 'aa' : "'aa");
        lastConsonant = '';
        break;
      case 'ا':
        // Silent next to tanween fath: دَائِمًا / دَائِماً
        if (at(i + 1) == _tanweenFath || at(i - 1) == _tanweenFath) break;
        lengthen('a', 'aa');
        lastConsonant = '';
        break;
      case 'ى':
        if (at(i + 1) == _tanweenFath || at(i - 1) == _tanweenFath) break;
        if (!out.endsWith('a')) add('a');
        lastConsonant = '';
        break;
      case 'ة':
        if (marksAfter(i).any((m) => isVowelSign(m) && m != _shadda)) {
          add('t', 't');
        } else if (out.endsWith('a')) {
          add('h');
        } else {
          add('ah');
        }
        break;
      case 'و':
      case 'ي':
        final consonant = ch == 'و' ? 'w' : 'y';
        // The previous letter's vowel, looking past a shadda stored after it (الرُّوحُ).
        var k = i - 1;
        while (k >= 0 && (chars[k] == _shadda || chars[k] == _tatweel)) {
          k--;
        }
        final prev = at(k);
        // A consonant at the start, before a vowel sign, or right after an unvowelled initial
        // hamza seat (أيضاً -> aydan).
        final afterBareSeat = i == 1 && _hamzaSeatsStart.contains(chars[0]);
        if (i == 0 || afterBareSeat || marksAfter(i).any(isVowelSign)) {
          add(consonant, consonant);
        } else if (prev == (ch == 'و' ? _damma : _kasra)) {
          lengthen(ch == 'و' ? 'u' : 'i', ch == 'و' ? 'oo' : 'ee');
          lastConsonant = '';
        } else if (prev == _fatha || prev == _sukun) {
          add(consonant, consonant); // diphthong aw / ay, or a consonant after a silent letter
        } else {
          add(ch == 'و' ? 'oo' : 'ee');
          lastConsonant = '';
        }
        break;
      default:
        break;
    }
  }

  return out
      .replaceAll(RegExp(r'a{3,}'), 'aa')
      .replaceAll(RegExp(r'e{3,}'), 'ee')
      .replaceAll(RegExp(r'o{3,}'), 'oo');
}

/// Arab-English spelling of one Arabic word (article handled), or '' if nothing is spellable.
String spellArabicWord(String rawWord) {
  final parts = splitArticle(rawWord);
  final body = spellStem(parts.stem, afterArticle: parts.prefix.isNotEmpty);
  return body.isEmpty ? '' : '${parts.prefix}$body';
}
