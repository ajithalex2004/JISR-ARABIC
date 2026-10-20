import React, { useEffect, useState } from 'react';
import { X, Keyboard, Volume2, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { audioManager } from '../../services/audio';
import {
  GUIDES, Platform, detectPlatform, hasArabicVoice, markArabicSetupDone, snoozeArabicSetup, typedArabic,
} from '../../services/arabicSetup';

function Steps({ steps }: { steps: string[] }) {
  return <ol className="list-decimal pl-5 space-y-1 text-sm text-slate-700">
    {steps.map(step => <li key={step}>{step}</li>)}
  </ol>;
}

/** First sign-in on a device: check the Arabic keyboard and voice, with steps to turn them on. */
export function ArabicSetupModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [platform, setPlatform] = useState<Platform>(() => detectPlatform());
  const [typed, setTyped] = useState('');
  const [voice, setVoice] = useState<boolean | null>(null);
  const keyboardOk = typedArabic(typed);

  useEffect(() => {
    if (!isOpen) return;
    let alive = true;
    setVoice(null);
    hasArabicVoice().then(found => { if (alive) setVoice(found); });
    return () => { alive = false; };
  }, [isOpen]);

  if (!isOpen) return null;
  const guide = GUIDES[platform];
  const finish = () => { markArabicSetupDone(); onClose(); };
  const later = () => { snoozeArabicSetup(); onClose(); };

  return <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="arabic-setup-title">
    <div className="bg-white w-full max-w-xl max-h-[92vh] overflow-y-auto rounded-2xl shadow-2xl p-5 space-y-4 relative">
      <button type="button" onClick={later} aria-label="Close" className="absolute top-4 right-4 text-slate-500 hover:text-slate-900">
        <X className="w-5 h-5" />
      </button>
      <div>
        <h2 id="arabic-setup-title" className="text-lg font-black text-slate-900">Set up Arabic on this device · جَهِّزِ العَرَبِيَّةَ</h2>
        <p className="text-sm text-slate-600">
          To type your answers and hear Arabic clearly, your {guide.name} needs an Arabic keyboard and voice. It takes two minutes.
        </p>
        <label className="text-xs text-slate-500 flex items-center gap-2 mt-2">
          Steps for
          <select value={platform} onChange={e => setPlatform(e.target.value as Platform)}
            className="border border-slate-300 rounded-lg px-2 py-1 text-xs text-slate-800">
            {(Object.keys(GUIDES) as Platform[]).filter(p => p !== 'other').map(p => <option key={p} value={p}>{GUIDES[p].name}</option>)}
          </select>
        </label>
      </div>

      <section className={`border rounded-xl p-3 space-y-2 ${keyboardOk ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200'}`}>
        <h3 className="font-bold text-slate-900 flex items-center gap-2">
          {keyboardOk ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <Keyboard className="w-5 h-5 text-purple-700" />}
          1. Arabic keyboard {keyboardOk && <span className="text-emerald-700 text-sm">· works!</span>}
        </h3>
        {!keyboardOk && <>
          <Steps steps={guide.keyboard} />
          <p className="text-sm text-slate-700"><span className="font-semibold">Then:</span> {guide.switchKeys}</p>
        </>}
        <label className="block text-sm font-semibold text-slate-700" htmlFor="arabic-keyboard-test">
          Test it: switch to Arabic and type <span className="font-arabic">مرحبا</span>
        </label>
        <input id="arabic-keyboard-test" dir="rtl" value={typed} onChange={e => setTyped(e.target.value)}
          placeholder="اُكْتُبْ هُنَا" className="w-full border border-slate-300 rounded-lg p-2 font-arabic text-lg" />
        {typed && !keyboardOk && <p className="text-xs text-amber-800">Those are English letters. Switch your keyboard to Arabic first.</p>}
      </section>

      <section className={`border rounded-xl p-3 space-y-2 ${voice ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200'}`}>
        <h3 className="font-bold text-slate-900 flex items-center gap-2">
          {voice === null ? <Loader2 className="w-5 h-5 animate-spin text-slate-500" />
            : voice ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <Circle className="w-5 h-5 text-amber-600" />}
          2. Arabic voice <span className="text-xs font-normal text-slate-500">(recommended)</span>
          {voice && <span className="text-emerald-700 text-sm">· found!</span>}
        </h3>
        {voice === false && <>
          <p className="text-sm text-slate-700">
            No Arabic voice on this device yet. Fahim will use the online Arabic voice meanwhile, but a device voice reads words instantly.
          </p>
          <Steps steps={guide.voice} />
        </>}
        <button type="button" onClick={() => audioManager.playArabic('مَرْحَبًا بِكَ فِي جِسْر')}
          className="text-sm font-semibold text-purple-800 flex items-center gap-1 hover:underline">
          <Volume2 className="w-4 h-4" /> Test the voice
        </button>
      </section>

      <div className="flex flex-wrap justify-end gap-2">
        <button type="button" onClick={later} className="px-4 py-2 rounded-lg border border-slate-300 text-sm font-semibold text-slate-700">
          Remind me later
        </button>
        <button type="button" onClick={finish} className="px-4 py-2 rounded-lg bg-purple-700 text-white text-sm font-semibold">
          {keyboardOk ? 'All set' : "I've done this"}
        </button>
      </div>
    </div>
  </div>;
}
