import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { audioManager } from '../../services/audio';
import { getWordTranslation, fetchWordGloss, WordDefinition } from '../../services/arabicDictionary';
import { ArabEnglishHelper, useArabEnglish } from '../../services/arabEnglishService';
import { stripTashkeel, useTashkeel } from '../../services/tashkeel';
import { localWordIndex, playbackWords } from '../../services/playbackWords';

interface ArabicWordSpansProps {
  text: string;
  className?: string;
  onWordClick?: (word: string) => void;
  tooltipPlacement?: 'top' | 'bottom';
  showAudioPrompt?: boolean;
  /** Word positions (whitespace-separated, from 0) to mark as matching the English translation. */
  highlightedWords?: number[];
  /** Called with a word's position when it is hovered, focused or tapped, and null when it is left. */
  onWordHover?: (wordIndex: number | null) => void;
}

interface TooltipState {
  index: number;
  token: string;
  definition: WordDefinition;
  // True while a word missing from the local dictionary is being looked up on the server.
  loading?: boolean;
  rect: {
    top: number;
    bottom: number;
    left: number;
    right: number;
    width: number;
    height: number;
  };
  showBelow: boolean;
}

export const ArabicWordSpans: React.FC<ArabicWordSpansProps> = ({
  text,
  className = '',
  onWordClick,
  tooltipPlacement = 'top',
  showAudioPrompt = true,
  highlightedWords,
  onWordHover
}) => {
  const [arabEnglishEnabled] = useArabEnglish();
  const [tashkeelMode] = useTashkeel();
  const hideTashkeel = tashkeelMode === 'plain';
  // While audio plays: the spoken word's position in this text, or a single clicked word.
  const [spokenIndex, setSpokenIndex] = useState<number>(-1);
  const [spokenWord, setSpokenWord] = useState<string>('');
  const [activeTouchedIndex, setActiveTouchedIndex] = useState<number | null>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const [tooltipState, setTooltipState] = useState<TooltipState | null>(null);
  const lastSpokenRef = useRef<{ word: string; time: number }>({ word: '', time: 0 });

  useEffect(() => {
    const unsubscribe = audioManager.subscribe((state) => {
      const playedWords = state.isPlaying ? playbackWords(state.text) : [];
      setSpokenIndex(state.isPlaying ? localWordIndex(state.text, state.activeWordIndex, text) : -1);
      // A single word played on its own (a tapped word) lights up wherever it appears.
      setSpokenWord(playedWords.length === 1 ? playedWords[0].replace(/[؟!\.,،؛:\'\"()\[\]\-—]/g, '') : '');
    });
    return unsubscribe;
  }, [text]);

  // Close floating portal tooltip when user scrolls any scrollable ancestor
  useEffect(() => {
    if (!tooltipState) return;
    const handleScroll = () => {
      setTooltipState(null);
      setHoveredIdx(null);
      setActiveTouchedIndex(null);
    };
    window.addEventListener('scroll', handleScroll, true);
    return () => window.removeEventListener('scroll', handleScroll, true);
  }, [tooltipState]);

  // Words the local dictionary doesn't know: ask the server, using this passage as context.
  // The short delay avoids a request for every word the pointer merely passes over.
  const pendingIndex = tooltipState?.loading ? tooltipState.index : null;
  const pendingToken = tooltipState?.loading ? tooltipState.token : '';
  useEffect(() => {
    if (pendingIndex === null) return;
    let cancelled = false;
    const timer = setTimeout(() => {
      fetchWordGloss(pendingToken, text).then((definition) => {
        if (cancelled) return;
        setTooltipState((current) =>
          current && current.index === pendingIndex && current.token === pendingToken
            ? { ...current, loading: false, definition: definition ?? { translation: '' } }
            : current
        );
      });
    }, 200);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [pendingIndex, pendingToken, text]);

  if (!text) return null;

  // Split text by whitespace, preserving Arabic characters, diacritics and ligatures intact
  const tokens = text.split(/(\s+)/);
  let wordCount = -1;
  const wordIndexes = tokens.map((t) => (t && !/^\s+$/.test(t) ? ++wordCount : -1));

  const handleMouseEnter = (token: string, idx: number, e: React.MouseEvent<HTMLSpanElement>) => {
    setHoveredIdx(idx);
    const target = e.currentTarget;
    const domRect = target.getBoundingClientRect();
    const definition = getWordTranslation(token);
    // If element is close to top of viewport (less than 130px), place tooltip below to avoid clipping
    const showBelow = tooltipPlacement === 'bottom' || domRect.top < 130;

    setTooltipState({
      index: idx,
      token,
      definition,
      loading: !definition.translation,
      rect: {
        top: domRect.top,
        bottom: domRect.bottom,
        left: domRect.left,
        right: domRect.right,
        width: domRect.width,
        height: domRect.height
      },
      showBelow
    });
  };

  const handleMouseLeave = () => {
    setHoveredIdx(null);
    if (activeTouchedIndex === null) {
      setTooltipState(null);
    }
  };

  const handleSpeakWord = (word: string, index: number, e: React.MouseEvent | React.KeyboardEvent | React.TouchEvent) => {
    e.stopPropagation();
    const cleanWord = word.replace(/[؟!\.,،؛:\'\"()\[\]\-—]/g, '').trim();
    const now = Date.now();
    if (lastSpokenRef.current.word === cleanWord && now - lastSpokenRef.current.time < 350) {
      return;
    }
    lastSpokenRef.current = { word: cleanWord, time: now };

    if (cleanWord) {
      audioManager.playArabic(cleanWord);
      if (onWordClick) onWordClick(cleanWord);
    }

    if (activeTouchedIndex === index) {
      setActiveTouchedIndex(null);
      setTooltipState(null);
    } else {
      setActiveTouchedIndex(index);
      const target = (e.currentTarget as HTMLElement) || (e.target as HTMLElement);
      if (target && target.getBoundingClientRect) {
        const domRect = target.getBoundingClientRect();
        const definition = getWordTranslation(word);
        const showBelow = tooltipPlacement === 'bottom' || domRect.top < 130;
        setTooltipState({
          index,
          token: word,
          definition,
          loading: !definition.translation,
          rect: {
            top: domRect.top,
            bottom: domRect.bottom,
            left: domRect.left,
            right: domRect.right,
            width: domRect.width,
            height: domRect.height
          },
          showBelow
        });
      }
    }
  };

  return (
    <>
      <span className={`inline font-arabic text-right ${className}`} dir="rtl">
        {tokens.map((token, idx) => {
          const wordIndex = wordIndexes[idx];
          // If whitespace token, render as is
          if (/^\s+$/.test(token)) {
            return <span key={idx}>{token}</span>;
          }

          const cleanWord = token.replace(/[؟!\.,،؛:\'\"()\[\]\-—]/g, '').trim();
          if (!cleanWord) {
            return <span key={idx}>{hideTashkeel ? stripTashkeel(token) : token}</span>;
          }

          const isPlaying = spokenIndex >= 0 ? wordIndex === spokenIndex : !!spokenWord && cleanWord === spokenWord;
          const isHighlighted = hoveredIdx === idx || activeTouchedIndex === idx;
          const isMatched = !!highlightedWords?.includes(wordIndex);
          const arabEn = cleanWord ? ArabEnglishHelper.transliterateWord(cleanWord) : '';

          return (
            <span
              key={idx}
              className="relative inline-block mx-[2px] align-bottom my-0.5"
              onMouseEnter={(e) => {
                handleMouseEnter(token, idx, e);
                onWordHover?.(wordIndex);
              }}
              onMouseLeave={() => {
                handleMouseLeave();
                onWordHover?.(null);
              }}
            >
              {/* Clickable & Hoverable Arabic Word Token */}
              <span
                tabIndex={0}
                role="button"
                aria-label={token}
                onClick={(e) => {
                  handleSpeakWord(token, idx, e);
                  onWordHover?.(wordIndex);
                }}
                onFocus={() => onWordHover?.(wordIndex)}
                onBlur={() => onWordHover?.(null)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSpeakWord(token, idx, e);
                  }
                }}
                className={`arabic-word-target select-text inline-flex flex-col items-center justify-center px-1.5 py-0.5 rounded-lg transition-all duration-150 cursor-pointer ${
                  isPlaying
                    ? 'bg-amber-300 text-slate-950 font-bold ring-2 ring-amber-500 scale-105 shadow-md'
                    : isMatched
                    ? 'bg-sky-100 text-sky-950 font-bold ring-2 ring-sky-500 underline decoration-sky-600 decoration-2 underline-offset-4'
                    : isHighlighted
                    ? 'bg-purple-100 text-[#58337E] font-bold ring-2 ring-[#6C5CE7] shadow-sm'
                    : 'hover:bg-purple-100/80 hover:text-[#58337E] hover:ring-1 hover:ring-purple-400'
                }`}
              >
                <span className="leading-tight">{hideTashkeel ? stripTashkeel(token) : token}</span>
                {arabEnglishEnabled && arabEn && (
                  <span
                    className="block text-[11px] font-sans font-bold tracking-tight text-[#4338CA] leading-none select-none text-center mt-0.5 whitespace-nowrap"
                    dir="ltr"
                  >
                    {arabEn}
                  </span>
                )}
              </span>
            </span>
          );
        })}
      </span>

      {/* Floating React Portal Tooltip — Immune to parent overflow:hidden & overflow-y-auto clipping */}
      {tooltipState && typeof document !== 'undefined' && createPortal(
        <div
          style={{
            position: 'fixed',
            top: tooltipState.showBelow
              ? `${tooltipState.rect.bottom + 8}px`
              : `${tooltipState.rect.top - 8}px`,
            left: `${Math.max(120, Math.min(window.innerWidth - 120, tooltipState.rect.left + tooltipState.rect.width / 2))}px`,
            transform: tooltipState.showBelow ? 'translateX(-50%)' : 'translate(-50%, -100%)',
            zIndex: 999999,
            pointerEvents: 'none',
          }}
          className="transition-opacity duration-150 ease-out drop-shadow-2xl"
          dir="ltr"
        >
          <div
            className="bg-[#2A1548] text-white rounded-2xl px-4 py-2.5 border border-purple-400/40 shadow-2xl flex flex-col items-center text-center backdrop-blur-md"
            style={{ minWidth: '140px', maxWidth: '260px' }}
          >
            {/* Arabic Word Display with Diacritics */}
            <span className="font-arabic text-base text-amber-300 font-bold leading-tight drop-shadow-sm" dir="rtl">
              {tooltipState.token}
            </span>
            {hideTashkeel && stripTashkeel(tooltipState.token) !== tooltipState.token && (
              <span className="text-[9px] text-emerald-300 font-bold uppercase tracking-wider mt-0.5">
                Vowels revealed
              </span>
            )}

            {/* Arab-English Phonetic Pronunciation Badge */}
            {(() => {
              const clean = tooltipState.token.replace(/[؟!\.,،؛:\'\"()\[\]\-—]/g, '').trim();
              const phonetics = clean ? ArabEnglishHelper.transliterateWord(clean) : '';
              if (!phonetics) return null;
              return (
                <div
                  className="mt-1 px-2.5 py-0.5 rounded-full bg-white/10 text-amber-200 text-xs font-sans font-bold tracking-wide flex items-center gap-1 border border-amber-300/30 shadow-xs"
                  dir="ltr"
                >
                  <span className="text-[11px]">🗣️</span>
                  <span>{phonetics}</span>
                </div>
              );
            })()}

            {/* Exact English Translation */}
            <span className="font-sans font-extrabold text-white text-xs mt-1.5 leading-snug tracking-wide">
              {tooltipState.loading
                ? 'Looking up meaning…'
                : tooltipState.definition.translation && !/[\u0600-\u06FF]/.test(tooltipState.definition.translation)
                ? tooltipState.definition.translation
                : 'Meaning not available'}
            </span>

            {/* Grammatical Tag Only */}
            {tooltipState.definition.partOfSpeech && (
              <div className="mt-1.5 flex justify-center">
                <span className="text-[9px] px-2 py-0.5 rounded-full bg-purple-900/90 text-purple-200 border border-purple-400/30 uppercase tracking-wider font-bold">
                  {tooltipState.definition.partOfSpeech}
                </span>
              </div>
            )}

            {/* Audio prompt cue */}
            {showAudioPrompt && (
              <div className="mt-2 pt-1.5 border-t border-purple-400/20 text-[9px] text-purple-300/90 flex items-center gap-1 font-medium">
                <span>🔊</span>
                <span>Click to Pronounce</span>
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
    </>
  );
};
