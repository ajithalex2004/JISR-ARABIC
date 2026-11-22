/**
 * Split an Arabic word into its letters, with the shape each letter takes in the word.
 *
 * Worked out from the text itself (no AI, no server): every letter keeps its vowel marks, and its
 * position in the word (start, middle, end or alone) follows from which neighbours it joins.
 * Six letters (ا د ذ ر ز و, and their hamza and ة forms) never join the letter after them, so a word
 * can be written in several pieces.
 */

export type Position = 'initial' | 'medial' | 'final' | 'isolated';

export interface SplitLetter {
  /** The base letter, e.g. ب */
  base: string;
  /** Vowel and other marks written on it (fatha, shadda, sukun, tanween, ...). */
  marks: string;
  position: Position;
  joinsPrev: boolean;
  joinsNext: boolean;
  /** Written once but said twice (it carries a shadda). */
  doubled: boolean;
  /** ل followed by an alif: the two are written as one shape, لا. */
  lamAlif: boolean;
  /** The ل of ال before a sun letter: written but not said. */
  silent: boolean;
}

export interface WordSplit {
  word: string;
  letters: SplitLetter[];
  /** How many separate pieces the word is written in. */
  pieces: number;
  notes: string[];
}

const ZWJ = '‍';
const MARK = /[ً-ٰٟۖ-ۭ]/;
const LETTER = /[ء-غف-يٱ-ۓ]/;
const SHADDA = 'ّ';
const ALIFS = 'اأإآٱ';
/** Letters that join the letter before them but never the one after. */
const RIGHT_JOINING = new Set([...'اأإآٱدذرزوؤة']);
/** Letters that join neither neighbour. */
const NON_JOINING = new Set(['ء']);
/** The letters after which ال's ل is silent. */
const SUN_LETTERS = new Set([...'تثدذرزسشصضطظلن']);

/** Letters written in a form with no entry of their own in the alphabet board. */
export const LETTER_FORM_NAMES: Record<string, string> = {
  'أ': 'alif with hamza above', 'إ': 'alif with hamza below', 'آ': 'alif with madda', 'ٱ': 'alif (silent)',
  'ؤ': 'hamza on waaw', 'ئ': 'hamza on yaa', 'ء': 'hamza', 'ة': 'taa marbuuta', 'ى': 'alif maqsuura',
};

export const POSITION_LABEL: Record<Position, string> = {
  initial: 'start', medial: 'middle', final: 'end', isolated: 'on its own',
};

const joinsForward = (base: string) => !RIGHT_JOINING.has(base) && !NON_JOINING.has(base);
const joinsBackward = (base: string) => !NON_JOINING.has(base);

/** The word without punctuation or tatweel (ـ), e.g. «أَيْنَ؟» → «أَيْنَ». */
export function cleanWord(word: string): string {
  return word.replace(/ـ/g, '').replace(/[^ء-ٰٟ-ۓۖ-ۭ]/g, '');
}

/** The Arabic words of a phrase or sentence, in reading order. */
export function wordsOf(text: string): string[] {
  return text.split(/\s+/).map(cleanWord).filter((w) => LETTER.test(w));
}

export function splitWord(raw: string): WordSplit {
  const word = cleanWord(raw);
  const units: { base: string; marks: string }[] = [];
  for (const ch of word) {
    if (LETTER.test(ch)) units.push({ base: ch, marks: '' });
    else if (MARK.test(ch) && units.length) units[units.length - 1].marks += ch;
  }
  const letters: SplitLetter[] = units.map((u, i) => {
    const prev = units[i - 1];
    const next = units[i + 1];
    const joinsPrev = !!prev && joinsForward(prev.base) && joinsBackward(u.base);
    const joinsNext = !!next && joinsForward(u.base) && joinsBackward(next.base);
    const position: Position = joinsPrev ? (joinsNext ? 'medial' : 'final') : joinsNext ? 'initial' : 'isolated';
    return {
      ...u, position, joinsPrev, joinsNext,
      doubled: u.marks.includes(SHADDA),
      lamAlif: u.base === 'ل' && !!next && ALIFS.includes(next.base),
      silent: false,
    };
  });
  // ال + sun letter: the ل is not said (the sun letter takes a shadda instead).
  if (letters.length > 2 && ALIFS.includes(letters[0].base) && letters[1].base === 'ل' && !letters[1].marks
      && SUN_LETTERS.has(letters[2].base) && letters[2].doubled) {
    letters[1].silent = true;
  }

  let pieces = 0;
  letters.forEach((l) => { if (!l.joinsPrev) pieces += 1; });
  return { word, letters, pieces, notes: notesFor(letters, pieces) };
}

function notesFor(letters: SplitLetter[], pieces: number): string[] {
  const notes: string[] = [];
  const breakers = [...new Set(letters.slice(0, -1).filter((l) => !l.joinsNext).map((l) => l.base))];
  if (pieces > 1 && breakers.length) {
    notes.push(`Written in ${pieces} pieces: ${breakers.join(' ')} ${breakers.length === 1 ? 'does' : 'do'} not join the letter after ${breakers.length === 1 ? 'it' : 'them'}.`);
  }
  letters.filter((l) => l.doubled).forEach((l) => {
    const vowel = l.marks.replace(SHADDA, '');
    notes.push(`${l.base}${SHADDA} has a shadda: written once but said twice (${l.base}ْ + ${l.base}${vowel}).`);
  });
  if (letters.some((l) => l.lamAlif)) notes.push('ل + ا join into one special shape: لا.');
  if (letters.some((l) => l.silent)) notes.push('ال before a sun letter: the ل is written but not said.');
  if (letters.some((l) => l.base === 'ة')) notes.push('ة (taa marbuuta) comes only at the end of a word; stopping on it, say «ه».');
  if (letters.length > 1 && letters[letters.length - 1].base === 'ى') notes.push('ى at the end is said as a long «aa», like ا.');
  return notes;
}

/** The letter as it looks at its place in the word (zero-width joiners keep its joined shape on its own). */
export function shapedLetter(l: SplitLetter, withMarks = true): string {
  return `${l.joinsPrev ? ZWJ : ''}${l.base}${withMarks ? l.marks : ''}${l.joinsNext ? ZWJ : ''}`;
}
