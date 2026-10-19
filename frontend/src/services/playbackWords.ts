/**
 * Which word of a sentence is being spoken, for word-by-word highlighting while audio plays.
 *
 * The cloud voice gives no word timings, so the position is estimated from playback progress:
 * each word gets time in proportion to its letters, with a short pause after punctuation.
 * Mirrors mobile/lib/playback_words.dart.
 */

const MARKS = /[\u064B-\u065F\u0670\u0640]/g;
const LETTERS = /[\p{L}\p{N}]/gu;
const PAUSE = /[.،,؛;:؟?!]$/;

export function playbackWords(text: string): string[] {
  return text.split(/\s+/).filter(Boolean);
}

function letterCount(word: string): number {
  return (word.replace(MARKS, '').match(LETTERS) || []).length;
}

/** Index of the word being spoken at `position` of `duration` seconds, or -1 before it starts. */
export function estimateWordIndex(words: string[], position: number, duration: number): number {
  if (!words.length || !(duration > 0) || position < 0) return -1;
  // Synthesized clips start and end with a little silence.
  const lead = Math.min(0.12, duration * 0.05);
  const tail = Math.min(0.15, duration * 0.05);
  const progress = Math.min(1, Math.max(0, (position - lead) / Math.max(0.01, duration - lead - tail)));
  const weights = words.map((w) => Math.max(1, letterCount(w)) + (PAUSE.test(w) ? 2 : 0));
  const total = weights.reduce((a, b) => a + b, 0);
  let elapsed = progress * total;
  for (let i = 0; i < weights.length; i++) {
    if (elapsed < weights[i]) return i;
    elapsed -= weights[i];
  }
  return words.length - 1;
}

/** Word index for a character offset into the space-joined words (browser speech boundaries). */
export function wordIndexAtChar(words: string[], charIndex: number): number {
  let end = -1;
  for (let i = 0; i < words.length; i++) {
    end += words[i].length + 1;
    if (charIndex <= end) return i;
  }
  return words.length - 1;
}

const normalize = (word: string) => (word.replace(MARKS, '').match(LETTERS) || []).join('');

/**
 * The spoken word's index within `text`, when `text` is the played text or part of it
 * (a line of a played paragraph); -1 otherwise. Punctuation-only words are skipped on both sides.
 */
export function localWordIndex(playedText: string, playedIndex: number, text: string): number {
  if (playedIndex < 0 || !playedText || !text) return -1;
  const played = playbackWords(playedText).map((w, i) => ({ key: normalize(w), i })).filter((w) => w.key);
  const own = playbackWords(text).map((w, i) => ({ key: normalize(w), i })).filter((w) => w.key);
  if (!own.length || own.length > played.length) return -1;
  const spoken = played.findIndex((w) => w.i >= playedIndex);
  if (spoken < 0) return -1;
  for (let start = 0; start + own.length <= played.length; start++) {
    if (own.every((w, k) => played[start + k].key === w.key)) {
      const offset = spoken - start;
      return offset >= 0 && offset < own.length ? own[offset].i : -1;
    }
  }
  return -1;
}
