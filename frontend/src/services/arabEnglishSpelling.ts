/**
 * Letter-by-letter Arab-English (Arabizi) spelling of one vowelled Arabic word.
 *
 * Kept free of React so it can be tested on its own. The mobile app has a line-for-line Dart
 * port in mobile/lib/arab_english_service.dart (_spellStem); change both together.
 *
 * Rules, for fully vowelled curriculum text (unvowelled words fall back to sensible defaults):
 *  - و / ي are consonants (w / y) when a vowel, tanween or shadda follows them, or at the start;
 *    after a matching short vowel they lengthen it (u + و -> oo, i + ي -> ee); after fatha
 *    they make a diphthong (aw / ay).
 *  - ا lengthens a fatha (a -> aa) and is silent next to tanween fath (دَائِمًا -> daa'iman).
 *  - A hamza seat at the start of a word (أ إ ٱ ا) carries no sound of its own when a vowel
 *    sign follows it; elsewhere hamza is written '.
 *  - ة is t when a vowel or tanween follows it (كُرَةُ -> kuratu), otherwise h (pause: kurah).
 *  - ى after fatha adds nothing (إِلَى -> ila).
 *  - Shadda doubles the consonant before it (including digraphs: sh -> shsh), except the sun
 *    letter right after al-, written once (الرِّيَاضَة -> al-riyaada...), as in the curated map.
 */

const FATHA = 'َ';
const DAMMA = 'ُ';
const KASRA = 'ِ';
const SUKUN = 'ْ';
const SHADDA = 'ّ';
const TANWEEN_FATH = 'ً';
const TANWEEN_DAMM = 'ٌ';
const TANWEEN_KASR = 'ٍ';
const DAGGER_ALIF = 'ٰ';
const TATWEEL = 'ـ';

const VOWEL_SIGNS = new Set([FATHA, DAMMA, KASRA, TANWEEN_FATH, TANWEEN_DAMM, TANWEEN_KASR, SHADDA]);
const MARKS = new Set([FATHA, DAMMA, KASRA, SUKUN, SHADDA, TANWEEN_FATH, TANWEEN_DAMM, TANWEEN_KASR, DAGGER_ALIF, TATWEEL]);

const CONSONANTS: Record<string, string> = {
  'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dh', 'ر': 'r',
  'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'dh', 'ع': "'", 'غ': 'gh',
  'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
};

const HAMZA_SEATS_START = new Set(['أ', 'إ', 'ٱ', 'ا']);

/** Split a leading article (ال, وال, فال, بال, كال, لل) off a vowelled word. */
export function splitArticle(rawWord: string): { prefix: string; stem: string } {
  const plain = rawWord.replace(/[ً-ٰٟـ]/g, '');
  // لِلْ... (li + al-): "lil-"
  if (plain.startsWith('لل') && plain.length > 3) {
    const m = rawWord.match(/^ل[ً-ْ]*ل[ْ]?/);
    if (m) return { prefix: 'lil-', stem: rawWord.slice(m[0].length) };
  }
  if (plain.startsWith('ال') && plain.length > 2) {
    const m = rawWord.match(/^[اٱ][ً-ْ]*ل[ْ]?/);
    if (m) return { prefix: 'al-', stem: rawWord.slice(m[0].length) };
  }
  // wa-, fa-, bi-, ka- + al-: the article's alif is not pronounced after the prefix.
  const lead: Record<string, string> = { 'و': 'wal-', 'ف': 'fal-', 'ب': 'bil-', 'ك': 'kal-' };
  if (lead[plain[0]] && plain.slice(1).startsWith('ال') && plain.length > 3) {
    const m = rawWord.match(/^[وفبك][ً-ْ]*[اٱ][ً-ْ]*ل[ْ]?/);
    if (m) return { prefix: lead[plain[0]], stem: rawWord.slice(m[0].length) };
  }
  return { prefix: '', stem: rawWord };
}

/** Arab-English spelling of a word with its article already removed. */
export function spellStem(stem: string, afterArticle = false): string {
  const chars = Array.from(stem);
  const next = (i: number) => chars[i + 1];
  const isVowelSign = (c?: string) => !!c && VOWEL_SIGNS.has(c);
  let out = '';
  let lastConsonant = '';
  let consonantEnd = 0; // where the last consonant ends in `out`, so a shadda doubles it before its vowel
  let firstLetterSeen = false;
  let skipShadda = false;

  const add = (s: string, consonant = '') => {
    out += s;
    if (consonant) { lastConsonant = consonant; consonantEnd = out.length; }
  };
  // The marks written on the letter at i (vowel, shadda, ...), whatever their order.
  const marksAfter = (i: number) => {
    const marks: string[] = [];
    for (let j = i + 1; j < chars.length && MARKS.has(chars[j]); j++) marks.push(chars[j]);
    return marks;
  };
  const lengthen = (short: string, long: string) => {
    if (out.endsWith(short) && !out.endsWith(long)) out = out.slice(0, -short.length) + long;
    else if (!out.endsWith(long)) out += long;
  };

  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i];
    const isFirstLetter = !firstLetterSeen && !MARKS.has(ch);
    if (!MARKS.has(ch)) firstLetterSeen = true;
    // The sun letter after al- carries a shadda that is not written twice (al-riyaada).
    if (isFirstLetter && afterArticle && marksAfter(i).includes(SHADDA)) skipShadda = true;

    switch (ch) {
      case FATHA: add('a'); continue;
      case DAMMA: add('u'); continue;
      case KASRA: add('i'); continue;
      case SUKUN: case TATWEEL: continue;
      case TANWEEN_FATH: add('an'); continue;
      case TANWEEN_DAMM: add('un'); continue;
      case TANWEEN_KASR: add('in'); continue;
      case DAGGER_ALIF: lengthen('a', 'aa'); continue;
      case SHADDA:
        if (skipShadda) { skipShadda = false; continue; }
        if (lastConsonant) {
          // Text stores the vowel before or after the shadda; the doubled letter goes before it.
          out = out.slice(0, consonantEnd) + lastConsonant + out.slice(consonantEnd);
          consonantEnd += lastConsonant.length;
        }
        continue;
    }

    if (CONSONANTS[ch]) { add(CONSONANTS[ch], CONSONANTS[ch]); continue; }

    if (i === 0 && HAMZA_SEATS_START.has(ch)) {
      // The vowel sign after it is the sound; unvowelled, guess from the seat.
      if (!(next(i) && MARKS.has(next(i)!))) {
        // A bare alif before a letter with sukun is the hamzat wasl of اِخْتِبَار: read "i".
        const nextLetterSilent = ch === 'ا' && marksAfter(i + 1).includes(SUKUN);
        add(ch === 'إ' || nextLetterSilent ? 'i' : 'a');
      }
      lastConsonant = '';
      continue;
    }

    switch (ch) {
      case 'ء': case 'ئ': case 'ؤ': case 'أ': case 'إ':
        add("'", "'");
        break;
      case 'آ':
        add(i === 0 ? 'aa' : "'aa");
        lastConsonant = '';
        break;
      case 'ا':
        // Silent next to tanween fath: دَائِمًا / دَائِماً
        if (next(i) === TANWEEN_FATH || chars[i - 1] === TANWEEN_FATH) break;
        lengthen('a', 'aa');
        lastConsonant = '';
        break;
      case 'ى':
        if (next(i) === TANWEEN_FATH || chars[i - 1] === TANWEEN_FATH) break;
        if (!out.endsWith('a')) add('a');
        lastConsonant = '';
        break;
      case 'ة':
        if (marksAfter(i).some(m => isVowelSign(m) && m !== SHADDA)) add('t', 't');
        else if (out.endsWith('a')) add('h');
        else add('ah');
        break;
      case 'و':
      case 'ي': {
        const cons = ch === 'و' ? 'w' : 'y';
        // The previous letter's vowel, looking past a shadda stored after it (الرُّوحُ).
        let k = i - 1;
        while (k >= 0 && (chars[k] === SHADDA || chars[k] === TATWEEL)) k--;
        const prev = chars[k];
        // A consonant at the start, before a vowel sign, or right after an unvowelled initial
        // hamza seat (أيضاً -> aydan).
        const afterBareSeat = i === 1 && HAMZA_SEATS_START.has(chars[0]);
        if (i === 0 || afterBareSeat || marksAfter(i).some(isVowelSign)) {
          add(cons, cons);
        } else if (prev === (ch === 'و' ? DAMMA : KASRA)) {
          lengthen(ch === 'و' ? 'u' : 'i', ch === 'و' ? 'oo' : 'ee');
          lastConsonant = '';
        } else if (prev === FATHA || prev === SUKUN) {
          add(cons, cons); // diphthong aw / ay, or a consonant after a silent letter
        } else {
          add(ch === 'و' ? 'oo' : 'ee');
          lastConsonant = '';
        }
        break;
      }
      default:
        break;
    }
  }

  return out.replace(/a{3,}/g, 'aa').replace(/e{3,}/g, 'ee').replace(/o{3,}/g, 'oo');
}

/** Arab-English spelling of one Arabic word (article handled), or '' if nothing is spellable. */
export function spellArabicWord(rawWord: string): string {
  const { prefix, stem } = splitArticle(rawWord);
  const body = spellStem(stem, !!prefix);
  return body ? `${prefix}${body}` : '';
}
