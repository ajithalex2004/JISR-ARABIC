import React, { useState } from 'react';
import { ArabicWordSpans } from './ArabicWordSpans';
import { Alignment, splitWords } from '../../services/alignment';

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
  const chunkOfEn = (i: number) => chunks.findIndex((c) => c.en.includes(i));
  const current = active !== null && active >= 0 ? chunks[active] : undefined;

  const englishWords = splitWords(en);

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
        {chunks.length === 0
          ? en
          : englishWords.map((word, i) => {
              const chunk = chunkOfEn(i);
              const isMatched = current?.en.includes(i);
              return (
                <React.Fragment key={i}>
                  {i > 0 && ' '}
                  {chunk >= 0 ? (
                    <span
                      tabIndex={0}
                      role="button"
                      aria-label={`${word}: show the matching Arabic`}
                      onMouseEnter={() => setActive(chunk)}
                      onMouseLeave={() => setActive(null)}
                      onFocus={() => setActive(chunk)}
                      onBlur={() => setActive(null)}
                      onClick={() => setActive(chunk)}
                      className={`cursor-pointer rounded-sm px-0.5 underline decoration-dotted decoration-slate-400 underline-offset-4 transition-colors ${
                        isMatched ? 'bg-sky-100 text-sky-950 not-italic font-bold decoration-solid decoration-sky-600 decoration-2' : 'hover:bg-sky-50'
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
      </div>
    </>
  );
};
