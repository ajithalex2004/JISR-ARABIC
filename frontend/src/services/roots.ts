/**
 * Root families for the Root Tree Explorer, from /api/curriculum/root-family,
 * plus the letter matching used to highlight a root inside a word.
 * The matching mirrors backend/modules/curriculum/roots.py.
 */
import { createApiUrl } from './api';

export interface RootLessonWord {
  word_ar: string;
  meaning_en: string;
  lesson_id: string;
  lesson_title_en: string;
  lesson_title_ar: string;
  grade: number | null;
  term: number | null;
}

export interface RootFamilyWord {
  word_ar: string;
  meaning_en: string;
  pattern: string | null;
  kind: string;
}

export interface RootFamily {
  root: string | null;
  roots: string[];
  borrowed: boolean;
  note_en: string | null;
  letters: string[];
  core_meaning_en: string | null;
  curriculum_words: RootLessonWord[];
  family: RootFamilyWord[];
  /** "ai": AI-suggested and checked against the root letters; "unavailable": AI is down; "none": not offered. */
  family_source: 'ai' | 'unavailable' | 'none';
}

const cache = new Map<string, Promise<RootFamily>>();

export function fetchRootFamily(root: string, word = ''): Promise<RootFamily> {
  const key = `${root}\u0000${word}`;
  const cached = cache.get(key);
  if (cached) return cached;
  const url = createApiUrl('/api/curriculum/root-family');
  if (root) url.searchParams.set('root', root);
  if (word) url.searchParams.set('word', word);
  const request = fetch(url.toString()).then((res) => {
    if (!res.ok) throw new Error(`Root family request failed (${res.status})`);
    return res.json() as Promise<RootFamily>;
  });
  cache.set(key, request);
  request.catch(() => cache.delete(key));
  return request;
}

const MARK = /[ً-ْٖ-ٰٟـ]/;
const HAMZA = new Set('أإآءؤئ');
const WEAK = new Set('اوىي');

function sameLetter(letter: string, rootLetter: string): boolean {
  if (letter === rootLetter) return true;
  if (HAMZA.has(rootLetter) || rootLetter === 'ا') return HAMZA.has(letter) || letter === 'ا';
  if (WEAK.has(rootLetter)) return WEAK.has(letter) || HAMZA.has(letter);
  return false;
}

/** Indexes, among the word's letters (vowel marks ignored), of the root's letters; null if absent. */
export function rootLetterPositions(word: string, root: string): number[] | null {
  const letters = Array.from(word).filter((c) => !MARK.test(c));
  const rootLetters = root.split('-');

  const match = (i: number, end: number): number[] | null => {
    if (i < 0) return [];
    const target = rootLetters[i];
    const exact: number[] = [];
    const similar: number[] = [];
    for (let j = end - 1; j >= 0; j--) {
      if (letters[j] === target) exact.push(j);
      else if (sameLetter(letters[j], target)) similar.push(j);
    }
    for (const j of [...exact, ...similar]) {
      const rest = match(i - 1, j);
      if (rest) return [...rest, j];
    }
    const doubled = i + 1 < rootLetters.length && rootLetters[i + 1] === target;
    return WEAK.has(target) || doubled ? match(i - 1, end) : null;
  };

  return match(rootLetters.length - 1, letters.length);
}

export interface WordSegment {
  text: string;
  isRoot: boolean;
}

/**
 * Splits a (possibly multi-word) phrase into segments, marking the root letters of the
 * first word that contains the root. Each letter keeps its vowel marks.
 */
export function segmentRootLetters(phrase: string, root: string | null): WordSegment[] {
  if (!root) return [{ text: phrase, isRoot: false }];
  const parts = phrase.split(/(\s+)/);
  let done = false;
  const segments: WordSegment[] = [];
  for (const part of parts) {
    const positions = !done && part.trim() ? rootLetterPositions(part, root) : null;
    if (!positions || positions.length === 0) {
      segments.push({ text: part, isRoot: false });
      continue;
    }
    done = true;
    const wanted = new Set(positions);
    let letterIndex = -1;
    for (const ch of Array.from(part)) {
      if (!MARK.test(ch)) letterIndex++;
      const isRoot = wanted.has(letterIndex);
      const last = segments[segments.length - 1];
      if (last && last.isRoot === isRoot) last.text += ch;
      else segments.push({ text: ch, isRoot });
    }
  }
  return segments;
}
