import React, { useCallback, useEffect, useState } from 'react';
import { DEMO_SENTENCES, MARQUEE_WORDS } from './content';

type Speed = 1 | 0.6;
type AudioModule = typeof import('../../services/audio');

// The app's own audio engine (cloud voice, browser voice as fallback), loaded after the page so the
// landing bundle stays small. It must be loaded before the tap: phones only allow sound started
// during the tap itself, and waiting for the download would end the tap.
let audioModule: AudioModule | null = null;
const loadAudio = () => import('../../services/audio').then((m) => { audioModule = m; return m; });

function speak(text: string, speed: Speed) {
  if (audioModule) {
    audioModule.audioManager.playArabic(text, { speed, repeats: 1 });
    return;
  }
  // Not loaded yet (very first tap on a slow connection): the device voice, started within the tap.
  if ('speechSynthesis' in window) {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'ar-SA'; u.rate = speed;
    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
  }
  loadAudio().catch(() => {});
}

export function WordDemo() {
  const [sentenceIdx, setSentenceIdx] = useState(0);
  const [wordIdx, setWordIdx] = useState(0);
  const [speed, setSpeed] = useState<Speed>(1);
  const [touched, setTouched] = useState(false);
  useEffect(() => { loadAudio().catch(() => {}); }, []);
  const sentence = DEMO_SENTENCES[sentenceIdx];
  const word = sentence.words[wordIdx];

  const pick = useCallback((i: number) => {
    setWordIdx(i); setTouched(true);
    speak(sentence.words[i].ar, speed);
  }, [sentence, speed]);

  return (
    <section id="demo" className="jl-section jl-demo" aria-labelledby="jl-demo-title">
      <div className="jl-wrap">
        <header className="jl-head" data-reveal>
          <p className="jl-kicker">Try it now · no sign-up</p>
          <h2 id="jl-demo-title" className="jl-h2">Tap a word. Hear it. <em>Get it.</em></h2>
          <p className="jl-sub">This is the actual JISR reader, not a video of it. Every word in every lesson works like this.</p>
        </header>

        <div className="jl-demo__stage" data-reveal>
          <div className="jl-demo__tabs">
            <div className="jl-demo__tablist" role="tablist" aria-label="Example sentences">
            {DEMO_SENTENCES.map((s, i) => (
              <button key={s.id} role="tab" type="button" aria-selected={i === sentenceIdx} id={`jl-tab-${s.id}`} aria-controls="jl-demo-panel"
                className="jl-chip" onClick={() => { setSentenceIdx(i); setWordIdx(0); }}>
                {s.label}
              </button>
            ))}
            </div>
            <span className="jl-demo__speed" role="group" aria-label="Playback speed">
              {([1, 0.6] as Speed[]).map((s) => (
                <button key={s} type="button" className="jl-chip jl-chip--sm" aria-pressed={speed === s} onClick={() => setSpeed(s)}>
                  {s === 1 ? 'Normal' : 'Slow 0.6×'}
                </button>
              ))}
            </span>
          </div>

          <div id="jl-demo-panel" role="tabpanel" aria-labelledby={`jl-tab-${sentence.id}`} className="jl-demo__panel">
            <p className="jl-demo__sentence" lang="ar" dir="rtl">
              {sentence.words.map((w, i) => (
                <button key={w.ar} type="button" className="jl-word" aria-pressed={i === wordIdx}
                  aria-label={`${w.ar}, ${w.tr}: ${w.en}. Play pronunciation`} onClick={() => pick(i)}>
                  <span className="jl-word__ar">{w.ar}</span>
                  <span className="jl-word__tr" lang="en" dir="ltr">{w.tr}</span>
                </button>
              ))}
            </p>
            <p className="jl-demo__translation"><span className="jl-label">Line in English</span>{sentence.en}</p>

            <div className="jl-demo__card" aria-live="polite" key={`${sentence.id}-${wordIdx}`}>
              <div className="jl-demo__card-ar" lang="ar" dir="rtl">{word.ar}</div>
              <div>
                <div className="jl-demo__card-en">{word.en}</div>
                <div className="jl-demo__card-tr">{word.tr}</div>
                <p className="jl-demo__card-note">{word.note}</p>
              </div>
              <button type="button" className="jl-play" onClick={() => speak(word.ar, speed)} aria-label={`Play ${word.tr} again`}>
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor" /></svg>
              </button>
            </div>
            {!touched && <p className="jl-hint" aria-hidden="true">↑ Tap any Arabic word</p>}
          </div>
        </div>
      </div>
    </section>
  );
}

export function Marquee() {
  const row = [...MARQUEE_WORDS, ...MARQUEE_WORDS];
  return (
    <div className="jl-marquee" aria-hidden="true">
      <div className="jl-marquee__track">
        {row.map(([ar, en], i) => (
          <span key={i} className="jl-marquee__item"><span lang="ar">{ar}</span><small>{en}</small></span>
        ))}
      </div>
    </div>
  );
}
