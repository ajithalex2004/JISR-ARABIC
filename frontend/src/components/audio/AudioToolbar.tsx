import React, { useState, useEffect } from 'react';
import { Volume2, Square, RotateCcw, X } from 'lucide-react';
import { audioManager, PlaybackSpeed, RepeatCount } from '../../services/audio';

export const AudioToolbar: React.FC = () => {
  const preferredArabicVoices = ['Microsoft Hoda', 'Microsoft Hamed', 'Google Arabic', 'Microsoft Fatima', 'Microsoft Salma', 'Microsoft Naayf'];
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentText, setCurrentText] = useState<string>('');
  const [speed, setSpeed] = useState<PlaybackSpeed>(1.0);
  const [repeats, setRepeats] = useState<RepeatCount>(1);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState<number>(0);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    const unsubscribe = audioManager.subscribe((state) => {
      setIsPlaying(state.isPlaying);
      setCurrentText(state.text);
    });

    const vList = audioManager.getVoices().filter(v => /^ar([_-]|$)/i.test(v.lang) || /arabic|hoda|hamed|fatima|salma|naayf/i.test(v.name));
    vList.sort((a, b) => {
      const ai = preferredArabicVoices.findIndex(name => a.name.toLowerCase().includes(name.toLowerCase()));
      const bi = preferredArabicVoices.findIndex(name => b.name.toLowerCase().includes(name.toLowerCase()));
      return (ai < 0 ? 99 : ai) - (bi < 0 ? 99 : bi);
    });
    setVoices(vList);

    return unsubscribe;
  }, []);

  const handleSpeedChange = (newSpeed: PlaybackSpeed) => {
    setSpeed(newSpeed);
    audioManager.setSpeed(newSpeed);
  };

  const handleRepeatsChange = (newRepeats: RepeatCount) => {
    setRepeats(newRepeats);
    audioManager.setRepeats(newRepeats);
  };

  const handleVoiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idx = parseInt(e.target.value, 10);
    setSelectedVoiceIndex(idx);
    if (voices[idx]) {
      audioManager.setVoice(voices[idx]);
    }
  };

  const handleStop = () => {
    audioManager.stop();
  };

  if (!isOpen) return <button onClick={() => setIsOpen(true)} className="fixed bottom-3 right-3 z-50 bg-slate-900 text-white px-3 py-2 text-xs font-bold shadow-lg" aria-label="Show audio toolbar">Show audio controls</button>;

  return (
    <div className="bg-slate-900 text-white border-t-2 border-slate-950 px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs shadow-md relative">
      <button onClick={() => { audioManager.stop(); setIsOpen(false); }} aria-label="Close audio toolbar" title="Close audio toolbar" className="absolute right-2 top-2 p-1 text-slate-300 hover:text-white"><X className="w-4 h-4" /></button>
      {/* Playback Status & Synthetic Notice */}
      <div className="flex items-center gap-2.5 min-w-[220px]">
        <div className={`p-1.5 ${isPlaying ? 'bg-emerald-600 animate-pulse' : 'bg-slate-800'}`}>
          <Volume2 className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5 font-semibold">
            <span>{isPlaying ? 'Speaking Arabic...' : 'Audio Ready'}</span>
            <span className="bg-amber-800/80 text-amber-200 px-1 py-0.2 text-[10px] uppercase tracking-wider font-bold">
              Synthetic Speech (نطق آلي)
            </span>
          </div>
          <div className="text-white truncate max-w-xs font-arabic font-semibold">
            {currentText || 'Click any Arabic word or sentence to listen'}
          </div>
        </div>
      </div>

      {/* Speed Controls */}
      <div className="flex items-center gap-1">
        <span className="text-slate-200 mr-1 font-semibold">Speed:</span>
        <button
          onClick={() => handleSpeedChange(1.0)}
          className={`px-2 py-1 border font-bold transition-all ${
            speed === 1.0 ? 'bg-emerald-700 text-white border-emerald-600' : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
          title="Normal Speed (1.0x)"
        >
          Normal 1.0x
        </button>
        <button
          onClick={() => handleSpeedChange(0.6)}
          className={`px-2 py-1 border font-bold transition-all ${
            speed === 0.6 ? 'bg-emerald-700 text-white border-emerald-600' : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
          title="Slow Speed (0.6x)"
        >
          Slow 0.6x
        </button>
        <button
          onClick={() => handleSpeedChange(0.3)}
          className={`px-2 py-1 border font-bold transition-all ${
            speed === 0.3 ? 'bg-emerald-700 text-white border-emerald-600' : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
          title="Very slow speed (0.3x)"
        >
          Very slow 0.3x
        </button>
      </div>

      {/* Repeat Controls */}
      <div className="flex items-center gap-1">
        <span className="text-slate-200 mr-1 flex items-center gap-1 font-semibold">
          <RotateCcw className="w-3 h-3" />
          <span>Repeat:</span>
        </span>
        {[1, 2, 3].map((num) => (
          <button
            key={num}
            onClick={() => handleRepeatsChange(num as RepeatCount)}
            className={`px-2 py-1 border font-bold transition-all ${
              repeats === num ? 'bg-amber-700 text-white border-amber-600' : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            {num}x
          </button>
        ))}
      </div>

      {/* Voice Selector & Stop Button */}
      <div className="flex items-center gap-2">
        {voices.length > 0 ? (
          <select
            value={selectedVoiceIndex}
            onChange={handleVoiceChange}
            className="bg-slate-800 text-slate-200 border border-slate-700 px-2 py-1 text-xs outline-none cursor-pointer"
          >
            {voices.map((v, i) => (
              <option key={v.name} value={i}>
                {v.name.slice(0, 20)} ({v.lang})
              </option>
            ))}
          </select>
        ) : (
          <span className="bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 px-2 py-1 rounded text-[11px] font-bold flex items-center gap-1">
            <Volume2 className="w-3 h-3 text-emerald-400" />
            <span>صوت السيرفر العربي (Native Cloud Audio)</span>
          </span>
        )}

        {isPlaying && (
          <button
            onClick={handleStop}
            className="bg-red-800 hover:bg-red-700 text-white px-2.5 py-1 font-bold flex items-center gap-1 border border-red-700"
          >
            <Square className="w-3 h-3" />
            <span>Stop</span>
          </button>
        )}
      </div>
    </div>
  );
};
