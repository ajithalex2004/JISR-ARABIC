import React, { useEffect, useState } from 'react';
import { Blocks, X } from 'lucide-react';
import { api } from '../../services/api';
import { onWordSplit } from '../../services/wordSplitBus';
import { WordSplitter } from './WordSplitter';

type AlphabetLetter = { letter: string; name: string; sound_en: string };
let alphabetCache: AlphabetLetter[] | null = null;

/**
 * The word splitter for any word in the app (textbook chapters, the reader, booklets...): opened
 * from a word's pop-up with "Split into letters". Letter names come from the Foundation course.
 */
export const WordSplitModal: React.FC<{ onOpenFoundation?: () => void }> = ({ onOpenFoundation }) => {
  const [word, setWord] = useState('');
  const [alphabet, setAlphabet] = useState<AlphabetLetter[]>(alphabetCache || []);

  useEffect(() => onWordSplit(setWord), []);
  useEffect(() => {
    if (!word || alphabetCache) return;
    api.getFoundation()
      .then((course: { alphabet?: AlphabetLetter[] }) => { alphabetCache = course.alphabet || []; setAlphabet(alphabetCache); })
      .catch(() => { /* the splitter works without names */ });
  }, [word]);
  useEffect(() => {
    if (!word) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setWord(''); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [word]);

  if (!word) return null;
  return (
    <div className="fixed inset-0 z-[1000000] bg-slate-950/60 flex items-center justify-center p-3" onClick={() => setWord('')}>
      <div role="dialog" aria-modal="true" aria-label={`How ${word} is written`}
        className="bg-white border-2 border-slate-900 w-full max-w-xl max-h-[92vh] overflow-y-auto p-4 space-y-3 shadow-2xl"
        onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-[11px] font-black uppercase tracking-wider text-sky-800">How this word is written</div>
            <div className="text-3xl font-arabic font-black text-slate-900" dir="rtl">{word}</div>
          </div>
          <button type="button" onClick={() => setWord('')} aria-label="Close" autoFocus
            className="p-1 text-slate-500 hover:text-slate-900 border border-transparent hover:border-slate-300">
            <X className="w-5 h-5" />
          </button>
        </div>
        <WordSplitter key={word} text={word} alphabet={alphabet} />
        {onOpenFoundation && (
          <button type="button" onClick={() => { setWord(''); onOpenFoundation(); }}
            className="w-full text-xs font-bold text-emerald-900 border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 py-2 inline-flex items-center justify-center gap-1.5">
            <Blocks className="w-4 h-4" /> Learn how letters join: Foundation in Basic Arabic (free course)
          </button>
        )}
      </div>
    </div>
  );
};
