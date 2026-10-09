import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { audioManager } from '../../services/audio';
import { getWordTranslation, WordDefinition } from '../../services/arabicDictionary';
import { ArabEnglishHelper, useArabEnglish } from '../../services/arabEnglishService';

interface ArabicWordSpansProps {
  text: string;
  className?: string;
  onWordClick?: (word: string) => void;
  tooltipPlacement?: 'top' | 'bottom';
  showAudioPrompt?: boolean;
}

interface TooltipState {
  index: number;
  token: string;
  definition: WordDefinition;
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
  showAudioPrompt = true
}) => {
  const [arabEnglishEnabled] = useArabEnglish();
  const [activePlayingWord, setActivePlayingWord] = useState<string>('');
  const [activeTouchedIndex, setActiveTouchedIndex] = useState<number | null>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const [tooltipState, setTooltipState] = useState<TooltipState | null>(null);
  const lastSpokenRef = useRef<{ word: string; time: number }>({ word: '', time: 0 });

  useEffect(() => {
    const unsubscribe = audioManager.subscribe((state) => {
      if (state.isPlaying && state.activeWord) {
        setActivePlayingWord(state.activeWord);
      } else {
        setActivePlayingWord('');
      }
    });
    return unsubscribe;
  }, []);

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

  if (!text) return null;

  // Split text by whitespace, preserving Arabic characters, diacritics and ligatures intact
  const tokens = text.split(/(\s+)/);

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
          // If whitespace token, render as is
          if (/^\s+$/.test(token)) {
            return <span key={idx}>{token}</span>;
          }

          const cleanWord = token.replace(/[؟!\.,،؛:\'\"()\[\]\-—]/g, '').trim();
          if (!cleanWord) {
            return <span key={idx}>{token}</span>;
          }

          const isPlaying = activePlayingWord && cleanWord && (cleanWord === activePlayingWord || token.includes(activePlayingWord));
          const isHighlighted = hoveredIdx === idx || activeTouchedIndex === idx;
          const arabEn = cleanWord ? ArabEnglishHelper.transliterateWord(cleanWord) : '';

          return (
            <span
              key={idx}
              className="relative inline-block mx-[2px] align-bottom my-0.5"
              onMouseEnter={(e) => handleMouseEnter(token, idx, e)}
              onMouseLeave={handleMouseLeave}
            >
              {/* Clickable & Hoverable Arabic Word Token */}
              <span
                tabIndex={0}
                role="button"
                aria-label={token}
                onClick={(e) => handleSpeakWord(token, idx, e)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSpeakWord(token, idx, e);
                  }
                }}
                className={`arabic-word-target select-text inline-flex flex-col items-center justify-center px-1.5 py-0.5 rounded-lg transition-all duration-150 cursor-pointer ${
                  isPlaying
                    ? 'bg-amber-300 text-slate-950 font-bold ring-2 ring-amber-500 scale-105 shadow-md'
                    : isHighlighted
                    ? 'bg-purple-100 text-[#58337E] font-bold ring-2 ring-[#6C5CE7] shadow-sm'
                    : 'hover:bg-purple-100/80 hover:text-[#58337E] hover:ring-1 hover:ring-purple-400'
                }`}
              >
                <span className="leading-tight">{token}</span>
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
              {tooltipState.definition.translation && !/[\u0600-\u06FF]/.test(tooltipState.definition.translation)
                ? tooltipState.definition.translation
                : 'Curriculum Term'}
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
