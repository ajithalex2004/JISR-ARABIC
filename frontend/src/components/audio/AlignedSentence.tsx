import React, { useState } from 'react';
import { ArabicWordSpans } from './ArabicWordSpans';
import { Alignment, AlignmentChunk, splitWords } from '../../services/alignment';
import { usePlayingWordIndex } from '../../services/usePlayingWord';

interface AlignedSentenceProps {
  ar: string;
  en: string;
  alignment: Alignment;
  arClassName?: string;
  enClassName?: string;
}

/**
 * An Arabic sentence above its English translation. When an alignment is available,
 * hovering, focusing or tapping a word on either side lights up the matching words on both.
 */
export const AlignedSentence: React.FC<AlignedSentenceProps> = ({ ar, en, alignment, arClassName = '', enClassName = '' }) => {
  const [active, setActive] = useState<number | null>(null);
  const chunks = alignment ?? [];
  const chunkOfAr = (i: number | null) => (i === null ? null : chunks.findIndex((c) => c.ar.includes(i)));
  const current = active !== null && active >= 0 ? chunks[active] : undefined;
  // While the sentence plays, the English for the spoken Arabic word lights up too.
  const spoken = usePlayingWordIndex(ar);
  const playingChunk = spoken >= 0 ? chunks.findIndex((c) => c.ar.includes(spoken)) : -1;

  return (
    <>
      <div className="text-right">
        <ArabicWordSpans
          text={ar}
          className={arClassName}
          highlightedWords={current?.ar}
          onWordHover={chunks.length ? (i) => setActive(chunkOfAr(i)) : undefined}
        />
      </div>
      <div className={enClassName} dir="ltr">
        <AlignedEnglish text={en} chunks={chunks} activeChunk={active} playingChunk={playingChunk} onActivate={setActive} />
      </div>
    </>
  );
};

interface AlignedEnglishProps {
  text: string;
  chunks: AlignmentChunk[];
  /** Index into chunks of the highlighted match, or null. */
  activeChunk: number | null;
  /** Index into chunks of the match for the word being spoken, or -1/undefined. */
  playingChunk?: number;
  onActivate: (chunk: number | null) => void;
}

/** English words that light up their Arabic match; plain text when there are no chunks. */
export const AlignedEnglish: React.FC<AlignedEnglishProps> = ({ text, chunks, activeChunk, playingChunk, onActivate }) => {
  if (chunks.length === 0) return <>{text}</>;
  const current = activeChunk !== null && activeChunk >= 0 ? chunks[activeChunk] : undefined;
  const playing = playingChunk !== undefined && playingChunk >= 0 ? chunks[playingChunk] : undefined;
  return (
    <>
      {splitWords(text).map((word, i) => {
        const chunk = chunks.findIndex((c) => c.en.includes(i));
        const isMatched = current?.en.includes(i);
        const isPlaying = !isMatched && playing?.en.includes(i);
        return (
          <React.Fragment key={i}>
            {i > 0 && ' '}
            {chunk >= 0 ? (
              <span
                tabIndex={0}
                role="button"
                aria-label={`${word}: show the matching Arabic`}
                onMouseEnter={() => onActivate(chunk)}
                onMouseLeave={() => onActivate(null)}
                onFocus={() => onActivate(chunk)}
                onBlur={() => onActivate(null)}
                onClick={() => onActivate(chunk)}
                className={`cursor-pointer rounded-sm px-0.5 underline decoration-dotted decoration-slate-400 underline-offset-4 transition-colors ${
                  isMatched
                    ? 'bg-sky-100 text-sky-950 not-italic font-bold decoration-solid decoration-sky-600 decoration-2'
                    : isPlaying
                    ? 'bg-amber-200 text-slate-950 not-italic font-bold decoration-solid decoration-amber-600 decoration-2'
                    : 'hover:bg-sky-50'
                }`}
              >
                {word}
              </span>
            ) : (
              <span>{word}</span>
            )}
          </React.Fragment>
        );
      })}
    </>
  );
};
