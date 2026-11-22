import React, { useEffect, useMemo, useRef, useState } from 'react';
import { prefersReducedMotion } from '../useReveal';
import { POSITION_LABEL, shapedLetter, splitWord } from '../../../services/wordSplit';
import { loadFoundationStageA, type FoundationStageA } from './journeyApi';
import './journey.css';

type AudioModule = typeof import('../../../services/audio');
let audioModule: AudioModule | null = null;
const loadAudio = () => import('../../../services/audio').then((m) => { audioModule = m; return m; });
function speak(text: string) {
  if (audioModule) { audioModule.audioManager.playArabic(text, { speed: 1, repeats: 1 }); return; }
  if ('speechSynthesis' in window) {
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'ar-SA';
    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
  }
  loadAudio().catch(() => {});
}

const STEPS = ['Stage A', 'The letters', 'Split a word', 'Quick check'] as const;
const STEP_MS = 5200;
const SPLIT_WORDS = ['كِتَابٌ', 'مَدْرَسَةٌ', 'بَيْتٌ'];
const COLOURS = ['#1d4ed8', '#b45309', '#047857', '#be123c', '#6d28d9', '#0e7490'];

type Load<T> = { state: 'loading' } | { state: 'ok'; data: T } | { state: 'error' };

/**
 * The welcome page phone for "Basics": a tour of Stage A of Foundation in Basic Arabic (free for
 * everyone), from the real course: its lessons, the letters, a word split into its letters, a quiz.
 */
export function FoundationPhone({ onStart }: { onStart: () => void }) {
  const [course, setCourse] = useState<Load<FoundationStageA>>({ state: 'loading' });
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(() => !prefersReducedMotion());
  const [reload, setReload] = useState(0);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => { loadAudio().catch(() => {}); }, []);
  useEffect(() => {
    const ctl = new AbortController();
    setCourse({ state: 'loading' });
    loadFoundationStageA(ctl.signal)
      .then((data) => setCourse({ state: 'ok', data }))
      .catch((e) => { if (e?.name !== 'AbortError') setCourse({ state: 'error' }); });
    return () => ctl.abort();
  }, [reload]);

  useEffect(() => {
    window.clearTimeout(timer.current);
    if (!playing) return;
    timer.current = window.setTimeout(() => setStep((s) => (s + 1) % STEPS.length), STEP_MS);
    return () => window.clearTimeout(timer.current);
  }, [step, playing]);

  const go = (i: number) => { setStep(i); setPlaying(false); };
  const data = course.state === 'ok' ? course.data : null;

  return (
    <div className="jp">
      <div className="jp-phone" role="region" aria-label="The JISR app: Stage A of Foundation in Basic Arabic">
        <div className="jp-screen">
          <div className="jp-status" aria-hidden="true"><span>9:41</span><span className="jp-island" /><span className="jp-bars"><i /><i /><i /><i /></span></div>
          <div className="jp-head">
            <span className="jp-avatar" aria-hidden="true" lang="ar">ف</span>
            <span className="jp-who"><strong>Fahim</strong><span>Basics · Stage A</span></span>
            <span className="jp-tag">{STEPS[step]}</span>
          </div>
          <div className="jp-views">
            {course.state === 'loading' && <div className="jp-loading" role="status">Loading Stage A…</div>}
            {course.state === 'error' && (
              <div className="jp-msg">Couldn’t load the course. Check your connection. <button type="button" className="jp-link" onClick={() => setReload((n) => n + 1)}>Try again</button></div>
            )}
            {data && <>
              <View active={step === 0} label="Stage A">
                <StageView data={data} />
                <div className="jp-next">
                  <button type="button" className="jp-btn jp-btn--go" onClick={onStart}>Start Stage A free</button>
                  <button type="button" className="jp-btn jp-btn--alt" onClick={() => go(1)}>See the letters</button>
                </div>
              </View>
              <View active={step === 1} label="The letters">
                <LettersView data={data} />
                <div className="jp-next"><button type="button" className="jp-btn jp-btn--go" onClick={() => go(2)}>Split a word</button></div>
              </View>
              <View active={step === 2} label="Split a word">
                <SplitView active={step === 2} autoplay={playing} />
                <div className="jp-next"><button type="button" className="jp-btn jp-btn--go" onClick={() => go(3)}>Quick check</button></div>
              </View>
              <View active={step === 3} label="Quick check">
                <QuizView data={data} active={step === 3} onAnswer={() => setPlaying(false)} />
                <div className="jp-next">
                  <button type="button" className="jp-btn jp-btn--go" onClick={onStart}>Start Stage A free</button>
                  <button type="button" className="jp-btn jp-btn--alt" onClick={() => go(0)}>Back to Stage A</button>
                </div>
              </View>
            </>}
          </div>
        </div>
      </div>

      <div className="jp-player">
        <div className="jp-dots" role="group" aria-label="Tour steps">
          {STEPS.map((name, i) => (
            <button key={name} type="button" aria-label={`${i + 1}. ${name}`} aria-current={step === i ? 'step' : undefined} onClick={() => go(i)} />
          ))}
        </div>
        <span className="jp-stepname" aria-live="polite">{step + 1} · {STEPS[step]}</span>
        <button type="button" className="jp-pause" onClick={() => setPlaying((p) => !p)} aria-label={playing ? 'Pause the tour' : 'Play the tour'}>
          {playing
            ? <svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.5" height="12" rx="1" /><rect x="9.5" y="2" width="3.5" height="12" rx="1" /></svg>
            : <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2l10 6-10 6z" /></svg>}
        </button>
      </div>
    </div>
  );
}

function View({ active, label, children }: { active: boolean; label: string; children: React.ReactNode }) {
  return <section className={`jp-view${active ? ' is-active' : ''}`} aria-label={label} aria-hidden={!active}>{children}</section>;
}

function StageView({ data }: { data: FoundationStageA }) {
  return (
    <>
      <div className="jp-titlerow">
        <div><h3>Stage A · {data.stage.title_en}</h3><p className="jp-sub">{data.titleEn} · free for everyone</p></div>
      </div>
      <ol className="jp-path">
        {data.lessons.map((l, i) => (
          <li key={l.id} className={i === 0 ? 'is-now' : 'is-done'}>
            <span className="jp-node">{i + 1}</span>
            <span className="jp-t"><span lang="ar" dir="rtl">{l.title_ar}</span><small>{l.title_en}</small></span>
            <span className={`jp-state jp-state--${i === 0 ? 'now' : 'open'}`}>{i === 0 ? 'Now' : 'Free'}</span>
          </li>
        ))}
        {data.paidStages.length > 0 && (
          <li className="is-locked">
            <span className="jp-node">🔒</span>
            <span className="jp-t"><span>Stages {data.paidStages.map((s) => s.id).join(', ')}</span><small>Reading, grammar, writing, everyday Arabic</small></span>
            <span className="jp-state jp-state--locked">Paid</span>
          </li>
        )}
      </ol>
    </>
  );
}

function LettersView({ data }: { data: FoundationStageA }) {
  return (
    <>
      <div><h3>The Arabic letters</h3><p className="jp-sub">Tap a letter to hear its name</p></div>
      <div className="jp-letters" dir="rtl">
        {data.alphabet.slice(0, 12).map((l) => (
          <button key={l.letter} type="button" onClick={() => speak(l.name)} aria-label={`${l.name}: ${l.sound_en}`}>
            <span lang="ar">{l.letter}</span><small dir="ltr">{l.sound_en.split(' ')[0]}</small>
          </button>
        ))}
      </div>
      <p className="jp-note">All 28 letters, the four shapes of each letter, and the King letters that never join after them.</p>
    </>
  );
}

function SplitView({ active, autoplay }: { active: boolean; autoplay: boolean }) {
  const [index, setIndex] = useState(0);
  const [split, setSplit] = useState(false);
  const word = SPLIT_WORDS[index % SPLIT_WORDS.length];
  const letters = useMemo(() => splitWord(word).letters, [word]);
  // While the tour plays, the word comes apart into its letters.
  useEffect(() => {
    if (!active) { setSplit(false); return; }
    if (!autoplay) return;
    const t = window.setTimeout(() => setSplit(true), 900);
    return () => window.clearTimeout(t);
  }, [active, autoplay, word]);
  return (
    <>
      <div><h3>Split a word</h3><p className="jp-sub">Every letter changes shape with its place in the word</p></div>
      <div className={`jp-split${split ? ' is-split' : ''}`} dir="rtl">
        {letters.map((l, i) => (
          <span key={i} className="jp-split__l">
            <span lang="ar" style={{ color: COLOURS[i % COLOURS.length] }}>{shapedLetter(l, false)}</span>
            <small dir="ltr">{POSITION_LABEL[l.position]}</small>
          </span>
        ))}
      </div>
      <div className="jp-next jp-next--inline">
        <button type="button" className="jp-btn jp-btn--alt" onClick={() => setSplit((s) => !s)}>{split ? 'Join the letters' : 'Split into letters'}</button>
        <button type="button" className="jp-btn jp-btn--alt" onClick={() => speak(word)}>Hear it</button>
        <button type="button" className="jp-btn jp-btn--alt" onClick={() => { setIndex((n) => n + 1); setSplit(false); }}>Another word</button>
      </div>
    </>
  );
}

function QuizView({ data, active, onAnswer }: { data: FoundationStageA; active: boolean; onAnswer: () => void }) {
  const items = useMemo(() => data.lessons.flatMap((l) => l.quiz || []).slice(0, 6), [data]);
  const [round, setRound] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  useEffect(() => { if (!active) setPicked(null); }, [active]);
  const q = items[round % Math.max(1, items.length)];
  if (!q) return <div className="jp-msg">Every Stage A lesson ends with a short quiz.</div>;
  const right = picked === q.correct_index;
  return (
    <>
      <div><h3>Quick check</h3><p className="jp-sub">From Stage A</p></div>
      <div className="jp-q"><span>{q.question_en}</span></div>
      <div className="jp-opts">
        {q.options.map((o, i) => (
          <button key={`${round}-${i}`} type="button" lang={/[؀-ۿ]/.test(o) ? 'ar' : undefined}
            className={`jp-opt${picked === i ? (i === q.correct_index ? ' is-right' : ' is-wrong') : ''}`}
            onClick={() => { setPicked(i); onAnswer(); }}>{o}</button>
        ))}
      </div>
      <div className="jp-feedback" aria-live="polite">
        {picked === null ? '' : right ? 'Right!' : q.explain_en}
        {picked !== null && items.length > 1 && <button type="button" className="jp-link" onClick={() => { setRound((r) => r + 1); setPicked(null); onAnswer(); }}>Next question</button>}
      </div>
    </>
  );
}
