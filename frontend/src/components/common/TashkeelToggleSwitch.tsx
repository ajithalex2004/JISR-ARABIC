import React from 'react';
import { useTashkeel } from '../../services/tashkeel';

interface TashkeelToggleSwitchProps {
  compact?: boolean;
  className?: string;
}

/**
 * Shows or hides Arabic vowel marks (tashkeel) everywhere ArabicWordSpans renders text.
 * The label demonstrates the setting: vowelled when marks are on, plain when off.
 */
export const TashkeelToggleSwitch: React.FC<TashkeelToggleSwitchProps> = ({
  compact = false,
  className = ''
}) => {
  const [mode, toggle] = useTashkeel();
  const isOn = mode === 'full';
  const label = isOn ? 'تَشْكِيل' : 'تشكيل';
  const title = isOn
    ? 'Vowel marks: ON. Turn off to practise reading Arabic as it is usually written.'
    : 'Vowel marks: OFF. Tap any word to reveal its vowels, or turn them back on here.';

  if (compact) {
    return (
      <button
        type="button"
        role="switch"
        aria-checked={isOn}
        aria-label="Show vowel marks (tashkeel)"
        onClick={toggle}
        title={title}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold transition-all shadow-xs select-none ${
          isOn
            ? 'bg-emerald-400 text-emerald-950 border border-emerald-300 hover:bg-emerald-300'
            : 'bg-white/10 text-purple-200 border border-purple-400/30 hover:bg-white/20'
        } ${className}`}
      >
        <span className="font-arabic tracking-wide" lang="ar">{label}</span>
        <span className="font-mono text-[10px]">{isOn ? 'ON' : 'OFF'}</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isOn}
      aria-label="Show vowel marks (tashkeel)"
      onClick={toggle}
      title={title}
      className={`group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all shadow-sm select-none border ${
        isOn
          ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white border-emerald-400/50 hover:brightness-105 ring-2 ring-emerald-300/40'
          : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/50'
      } ${className}`}
    >
      <span className="font-arabic font-bold" lang="ar">{label}</span>
      <span className="text-[11px] font-medium opacity-90 hidden sm:inline">(Vowels)</span>
      <div
        className={`w-7 h-4 rounded-full transition-colors relative flex items-center p-0.5 ${
          isOn ? 'bg-emerald-200' : 'bg-slate-300'
        }`}
      >
        <div
          className={`w-3 h-3 rounded-full shadow-xs transform transition-transform duration-200 ${
            isOn ? 'translate-x-3 bg-emerald-900' : 'translate-x-0 bg-white'
          }`}
        />
      </div>
    </button>
  );
};
