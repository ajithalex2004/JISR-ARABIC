import React, { useEffect, useMemo, useState } from 'react';
import { Combine, Info, Scissors, Volume2 } from 'lucide-react';
import { audioManager } from '../../services/audio';
import { stripTashkeel, useTashkeel } from '../../services/tashkeel';
import { LETTER_FORM_NAMES, POSITION_LABEL, SplitLetter, shapedLetter, splitWord, wordsOf } from '../../services/wordSplit';

type AlphabetLetter = { letter: string; name: string; sound_en: string };

// One colour per letter, kept the same in the joined word and in the split letters.
const COLOURS = ['text-blue-700', 'text-amber-700', 'text-emerald-700', 'text-rose-700', 'text-violet-700', 'text-cyan-700', 'text-orange-700', 'text-fuchsia-700'];
const BORDERS = ['border-blue-300', 'border-amber-300', 'border-emerald-300', 'border-rose-300', 'border-violet-300', 'border-cyan-300', 'border-orange-300', 'border-fuchsia-300'];

const play = (text: string) => audioManager.playArabic(text);

/** An English note with Arabic letters in it: each Arabic run kept right-to-left, in the Arabic font. */
const NoteText: React.FC<{ text: string }> = ({ text }) => (
  <>{text.split(/([\u0600-\u06FF\u200D]+(?:\s*\+\s*[\u0600-\u06FF\u200D]+)*)/).map((part, i) =>
    /[\u0600-\u06FF]/.test(part)
      ? <bdi key={i} dir="rtl" className="font-arabic text-sm font-bold text-slate-900 whitespace-nowrap">{part}</bdi>
      : <React.Fragment key={i}>{part}</React.Fragment>)}</>
);

interface Props {
  /** A word, phrase or sentence; a phrase offers each of its words. */
  text: string;
  alphabet: AlphabetLetter[];
  /** Start split (the letters apart) instead of joined. */
  startSplit?: boolean;
}

/**
 * Shows how a word is built from its letters: the joined word with each letter in its own colour,
 * and, split apart, each letter in the shape it has in the word (start, middle, end or on its own)
 * with its normal shape and name. Tap a letter to hear it.
 */
export const WordSplitter: React.FC<Props> = ({ text, alphabet, startSplit = true }) => {
  const words = useMemo(() => wordsOf(text), [text]);
  const [wordIndex, setWordIndex] = useState(() => Math.max(0, words.findIndex((w) => splitWord(w).letters.length > 1)));
  const [split, setSplit] = useState(startSplit);
  const [tashkeelMode] = useTashkeel();
  const hideTashkeel = tashkeelMode === 'plain';
  useEffect(() => { setWordIndex(Math.max(0, words.findIndex((w) => splitWord(w).letters.length > 1))); }, [words]);

  const word = words[wordIndex] || '';
  const result = useMemo(() => splitWord(word), [word]);
  const names = useMemo(() => new Map(alphabet.map((a) => [a.letter, a])), [alphabet]);
  if (!result.letters.length) return null;
  const withMarks = !hideTashkeel;

  // Tapping a letter says it with its vowel (e.g. «بَ»); a letter with no vowel says its name.
  const say = (l: SplitLetter) => {
    const vowel = l.marks.replace(/[ّْ]/g, '');
    play(vowel ? `${l.base}${l.marks}` : names.get(l.base)?.name || l.base);
  };
  const watchJoin = () => {
    setSplit(true);
    window.setTimeout(() => setSplit(false), 700);
  };

  return (
    <div className="border-2 border-sky-300 bg-sky-50/60 p-3 space-y-3" aria-label={`How ${word} is written`}>
      {words.length > 1 && (
        <div className="flex flex-wrap items-center gap-1.5" dir="rtl" role="radiogroup" aria-label="Choose a word to split">
          {words.map((w, i) => (
            <button key={`${w}-${i}`} type="button" role="radio" aria-checked={i === wordIndex}
              onClick={() => { setWordIndex(i); setSplit(true); }}
              className={`px-2 py-0.5 text-base font-arabic border ${i === wordIndex ? 'bg-sky-800 text-white border-sky-900' : 'bg-white border-slate-300 hover:border-sky-700'}`}>
              {hideTashkeel ? stripTashkeel(w) : w}
            </button>
          ))}
        </div>
      )}

      {/* The word: letters slide apart when split and back together when joined. */}
      <div className="flex justify-center py-2" dir="rtl">
        <div role="list" aria-label={`${result.letters.length} letters`}
          className={`flex items-start transition-all duration-700 ease-in-out ${split ? 'gap-2 sm:gap-3' : 'gap-0'}`}>
          {result.letters.map((l, i) => {
            const hiddenInLigature = !split && i > 0 && result.letters[i - 1].lamAlif;
            return (
              <button key={i} type="button" role="listitem" onClick={() => say(l)}
                aria-label={`${l.base}: ${names.get(l.base)?.name || LETTER_FORM_NAMES[l.base] || l.base}, ${POSITION_LABEL[l.position]} of the word`}
                className={`flex flex-col items-center transition-all duration-700 ease-in-out ${
                  split ? `bg-white border-2 ${BORDERS[i % BORDERS.length]} px-2 pt-1 pb-1.5 min-w-[3.5rem] hover:shadow-md` : 'border-0 p-0 bg-transparent'
                } ${hiddenInLigature ? 'hidden' : ''}`}
                style={{ transitionDelay: split ? `${i * 60}ms` : '0ms' }}>
                <span className={`font-arabic font-bold leading-[1.6] text-4xl sm:text-5xl ${COLOURS[i % COLOURS.length]} ${l.silent ? 'opacity-60' : ''}`}>
                  {/* Joined, ل+ا are drawn as the one shape لا. */}
                  {!split && l.lamAlif
                    ? `${l.joinsPrev ? '‍' : ''}${l.base}${withMarks ? l.marks : ''}${result.letters[i + 1].base}${withMarks ? result.letters[i + 1].marks : ''}`
                    : shapedLetter(l, withMarks)}
                </span>
                {split && (
                  <span className="flex flex-col items-center text-center">
                    <span className="text-[10px] font-bold uppercase tracking-wide text-slate-500">{POSITION_LABEL[l.position]}</span>
                    <span className="text-lg font-arabic text-slate-800 leading-tight" title="The letter on its own">{l.base}</span>
                    <span className="text-[10px] text-slate-600 leading-tight" dir="auto">
                      {names.get(l.base)?.name || LETTER_FORM_NAMES[l.base] || ''}
                    </span>
                    {l.doubled && <span className="mt-0.5 text-[9px] font-bold bg-amber-200 text-amber-950 px-1">said twice</span>}
                    {l.silent && <span className="mt-0.5 text-[9px] font-bold bg-slate-200 text-slate-700 px-1">silent</span>}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        <button type="button" onClick={() => setSplit((s) => !s)}
          className="px-3 py-1.5 text-xs font-bold bg-sky-800 hover:bg-sky-900 text-white inline-flex items-center gap-1.5">
          {split ? <><Combine className="w-3.5 h-3.5" /> Join the letters</> : <><Scissors className="w-3.5 h-3.5" /> Split into letters</>}
        </button>
        <button type="button" onClick={watchJoin}
          className="px-3 py-1.5 text-xs font-bold border border-sky-700 text-sky-900 bg-white hover:bg-sky-50">
          Watch it join
        </button>
        <button type="button" onClick={() => play(word)} aria-label={`Listen: ${word}`}
          className="px-3 py-1.5 text-xs font-bold border border-slate-300 bg-white hover:border-emerald-700 inline-flex items-center gap-1.5">
          <Volume2 className="w-3.5 h-3.5" /> Say the word
        </button>
      </div>

      <div className="text-xs text-slate-700 space-y-1">
        <p className="flex items-start gap-1.5">
          <Info className="w-3.5 h-3.5 mt-0.5 text-sky-800 shrink-0" />
          <span>
            <b>{result.letters.length} letters</b>{result.pieces === 1 ? ', all joined' : ''}.
            Each letter changes shape with its place in the word: tap one to hear it.
          </span>
        </p>
        {result.notes.map((n) => <p key={n} className="ps-5" dir="ltr"><NoteText text={n} /></p>)}
      </div>
    </div>
  );
};
