import React from 'react';
import { Volume2, VolumeX, Sparkles } from 'lucide-react';
import { useArabEnglish } from '../../services/arabEnglishService';

interface ArabEnglishToggleSwitchProps {
  compact?: boolean;
  className?: string;
}

export const ArabEnglishToggleSwitch: React.FC<ArabEnglishToggleSwitchProps> = ({
  compact = false,
  className = ''
}) => {
  const [isEnabled, toggle] = useArabEnglish();

  if (compact) {
    return (
      <button
        type="button"
        role="switch"
        aria-checked={isEnabled}
        onClick={() => toggle()}
        title={
          isEnabled
            ? 'Arab-English Pronunciation: ON (نطق الكلمات بالحروف اللاتينية مفعّل - انقر للإيقاف)'
            : 'Arab-English Pronunciation: OFF (نطق الكلمات بالحروف اللاتينية معطّل - انقر للتفعيل)'
        }
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold transition-all shadow-xs select-none ${
          isEnabled
            ? 'bg-amber-400 text-purple-950 border border-amber-300 hover:bg-amber-300'
            : 'bg-white/10 text-purple-200 border border-purple-400/30 hover:bg-white/20'
        } ${className}`}
      >
        {isEnabled ? (
          <Volume2 className="w-3.5 h-3.5 text-purple-900 shrink-0" />
        ) : (
          <VolumeX className="w-3.5 h-3.5 text-purple-300 shrink-0" />
        )}
        <span className="tracking-wide">
          عربيزي <span className="font-mono text-[10px]">{isEnabled ? 'ON' : 'OFF'}</span>
        </span>
      </button>
    );
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isEnabled}
      onClick={() => toggle()}
      title={
        isEnabled
          ? 'Arab-English Pronunciation: ON — Displays phonetic Latin transliteration under Arabic words'
          : 'Arab-English Pronunciation: OFF — Click to show phonetic Latin transliteration'
      }
      className={`group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all shadow-sm select-none border ${
        isEnabled
          ? 'bg-gradient-to-r from-[#6C5CE7] to-[#4F46E5] text-white border-purple-400/50 hover:brightness-105 ring-2 ring-purple-300/40'
          : 'bg-white text-slate-700 border-slate-200 hover:border-purple-300 hover:bg-purple-50/50'
      } ${className}`}
    >
      <div className="flex items-center gap-1.5">
        {isEnabled ? (
          <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse shrink-0" />
        ) : (
          <Volume2 className="w-3.5 h-3.5 text-slate-400 group-hover:text-purple-600 shrink-0" />
        )}
        <span className="font-arabic font-bold">عربيزي</span>
        <span className="text-[11px] font-medium opacity-90 hidden sm:inline">(Arab-English)</span>
      </div>

      <div
        className={`w-7 h-4 rounded-full transition-colors relative flex items-center p-0.5 ${
          isEnabled ? 'bg-amber-400' : 'bg-slate-300'
        }`}
      >
        <div
          className={`w-3 h-3 rounded-full bg-white shadow-xs transform transition-transform duration-200 ${
            isEnabled ? 'translate-x-3 bg-purple-900' : 'translate-x-0'
          }`}
        />
      </div>
    </button>
  );
};
