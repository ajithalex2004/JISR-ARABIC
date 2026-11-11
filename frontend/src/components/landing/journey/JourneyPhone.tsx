import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ArabEnglishHelper } from '../../../services/arabEnglishService';
import { prefersReducedMotion } from '../useReveal';
import {
  bareArabic, loadActivity, loadChapter, loadGloss, loadLessons,
  type ChapterContent, type JourneyLesson, type LessonActivity, type Session,
} from './journeyApi';
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

const say = (ar: string) => { try { return ArabEnglishHelper.transliterate(ar); } catch { return ''; } };

const STEPS = ['Your journey', 'New words', 'Read the book', 'Ask Fahim', 'Quick check', 'Progress'] as const;
const STEP_MS = 5200;

type Load<T> = { state: 'loading' } | { state: 'ok'; data: T } | { state: 'error' };

interface Props {
  grade: number;
  session: Session | null | undefined;
  onOpenApp: () => void;
  onSignup: () => void;
}

export function JourneyPhone({ grade, session, onOpenApp, onSignup }: Props) {
  const [term, setTerm] = useState(1);
  const [lessons, setLessons] = useState<Load<JourneyLesson[]>>({ state: 'loading' });
  const [chapter, setChapter] = useState<Load<ChapterContent | null>>({ state: 'loading' });
  const [activity, setActivity] = useState<LessonActivity[]>([]);
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(() => !prefersReducedMotion());
  const [reload, setReload] = useState(0);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => { loadAudio().catch(() => {}); }, []);
  // A new class starts the tour again from its chapter list.
  useEffect(() => { setTerm(1); setStep(0); }, [grade]);

  // Chapters of the class and term (with this family's access when signed in).
  useEffect(() => {
    if (session === undefined) return;
    const ctl = new AbortController();
    setLessons({ state: 'loading' });
    loadLessons(grade, term, session, ctl.signal)
      .then((data) => setLessons({ state: 'ok', data: [...data].sort((a, b) => a.lesson_order - b.lesson_order) }))
      .catch((e) => { if (e?.name !== 'AbortError') setLessons({ state: 'error' }); });
    return () => ctl.abort();
  }, [grade, term, session, reload]);

  // The child's own activity in this class and term.
  useEffect(() => {
    setActivity([]);
    if (!session || session.grade !== grade) return;
    const ctl = new AbortController();
    loadActivity(session, grade, term, ctl.signal).then(setActivity).catch(() => {});
    return () => ctl.abort();
  }, [grade, term, session]);

  const items = lessons.state === 'ok' ? lessons.data : [];
  const done = useMemo(() => new Map(activity.map((a) => [a.lesson_id, a])), [activity]);
  const soon = (l: JourneyLesson) => l.status === 'coming_soon';
  const termSoon = items.length > 0 && items.every(soon);
  // The welcome page shows one open chapter per class, for everyone (signed in or not, whatever
  // they've paid for): the class's free first chapter of Term 1. Every other chapter shows locked.
  const focus = useMemo(() => {
    if (term !== 1) return null;
    const real = items.filter((l) => !soon(l));
    return real.find((l) => l.is_first_chapter_demo) ?? real[0] ?? null;
  }, [items, term]);

  useEffect(() => {
    if (lessons.state !== 'ok') return;
    if (!focus) { setChapter({ state: 'ok', data: null }); return; }
    const ctl = new AbortController();
    setChapter({ state: 'loading' });
    loadChapter(focus.id, session ?? null, ctl.signal)
      .then((data) => setChapter({ state: 'ok', data }))
      .catch((e) => { if (e?.name !== 'AbortError') setChapter({ state: 'error' }); });
    return () => ctl.abort();
  }, [focus?.id, lessons.state, session]);

  const content = chapter.state === 'ok' ? chapter.data : null;
  const words = content?.words ?? [];
  // Screens that have something real to show for this chapter.
  const available = useMemo(() => STEPS.map((_, i) => {
    if (i === 0 || i === 5) return true;
    if (!content || words.length === 0) return false;
    if (i === 2) return words.some((w) => w.example_ar);
    if (i === 4) return words.length >= 3;
    return true;
  }), [content, words]);

  const go = useCallback((i: number, byUser: boolean) => {
    setStep(i);
    if (byUser) setPlaying(false);
  }, []);

  useEffect(() => {
    window.clearTimeout(timer.current);
    if (!playing) return;
    timer.current = window.setTimeout(() => {
      let next = step;
      do { next = (next + 1) % STEPS.length; } while (!available[next] && next !== step);
      setStep(next);
    }, STEP_MS);
    return () => window.clearTimeout(timer.current);
  }, [step, playing, available]);

  useEffect(() => { if (!available[step]) setStep(0); }, [available, step]);

  const headSub = session && session.grade === grade ? `${session.childName} · Class ${grade}` : `Class ${grade} · Term ${term}`;

  return (
    <div className="jp">
      <div className="jp-phone" role="region" aria-label="The JISR app: your child's learning journey">
        <div className="jp-screen">
          <div className="jp-status" aria-hidden="true"><span>9:41</span><span className="jp-island" /><span className="jp-bars"><i /><i /><i /><i /></span></div>
          <div className="jp-head">
            <span className="jp-avatar" aria-hidden="true" lang="ar">ف</span>
            <span className="jp-who"><strong>Fahim</strong><span>{headSub}</span></span>
            <span className="jp-tag">{step === 3 ? 'Online' : STEPS[step]}</span>
          </div>
          <div className="jp-views">
            <View active={step === 0} label="Your journey">
              <JourneyView grade={grade} term={term} setTerm={(t) => { setTerm(t); go(0, true); }} lessons={lessons} done={done}
                focusId={focus?.id ?? null} termSoon={termSoon} onRetry={() => setReload((n) => n + 1)} />
              <div className="jp-next">
                {focus && available[1]
                  ? <button type="button" className="jp-btn jp-btn--go" onClick={() => go(1, true)}>{done.has(focus.id) ? 'Review' : 'Start'} chapter {focus.lesson_order}</button>
                  : <button type="button" className="jp-btn jp-btn--go" onClick={onSignup}>Create an account</button>}
                <button type="button" className="jp-btn jp-btn--alt" onClick={onOpenApp}>Open the app</button>
              </div>
            </View>

            <View active={step === 1} label="New words">
              {content && available[1] && <WordsView content={content} />}
              <div className="jp-next"><button type="button" className="jp-btn jp-btn--go" onClick={() => go(2, true)}>Read the book page</button></div>
            </View>

            <View active={step === 2} label="Read the book">
              {content && available[2] && <ReadView content={content} active={step === 2} autoplay={playing} />}
              <div className="jp-next"><button type="button" className="jp-btn jp-btn--go" onClick={() => go(3, true)}>I have a question</button></div>
            </View>

            <View active={step === 3} label="Ask Fahim">
              {content && available[3] && <FahimView content={content} active={step === 3} />}
              <div className="jp-next">
                <button type="button" className="jp-btn jp-btn--go" onClick={() => go(4, true)}>Check what I learnt</button>
                <button type="button" className="jp-btn jp-btn--alt" onClick={onOpenApp}>Ask my own</button>
              </div>
            </View>

            <View active={step === 4} label="Quick check">
              {content && available[4] && <QuizView content={content} active={step === 4} autoplay={playing} onAnswer={() => setPlaying(false)} />}
              <div className="jp-next"><button type="button" className="jp-btn jp-btn--go" onClick={() => go(5, true)}>See progress</button></div>
            </View>

            <View active={step === 5} label="Progress">
              <ProgressView session={session ?? null} grade={grade} term={term} items={items} done={done} active={step === 5} />
              <div className="jp-next">
                {session
                  ? <button type="button" className="jp-btn jp-btn--go" onClick={onOpenApp}>Continue in the app</button>
                  : <button type="button" className="jp-btn jp-btn--go" onClick={onSignup}>Create an account</button>}
                <button type="button" className="jp-btn jp-btn--alt" onClick={() => go(0, true)}>Back to journey</button>
              </div>
            </View>
          </div>
          {chapter.state === 'loading' && step > 0 && step < 5 && <div className="jp-loading" role="status">Loading the chapter…</div>}
        </div>
      </div>

      <div className="jp-player">
        <div className="jp-dots" role="group" aria-label="Journey steps">
          {STEPS.map((name, i) => (
            <button key={name} type="button" aria-label={`${i + 1}. ${name}`} aria-current={step === i ? 'step' : undefined}
              disabled={!available[i]} onClick={() => go(i, true)} />
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

function JourneyView({ grade, term, setTerm, lessons, done, focusId, termSoon, onRetry }: {
  grade: number; term: number; setTerm: (t: number) => void; lessons: Load<JourneyLesson[]>;
  done: Map<string, LessonActivity>; focusId: string | null; termSoon: boolean; onRetry: () => void;
}) {
  const items = lessons.state === 'ok' ? lessons.data : [];
  return (
    <>
      <div className="jp-titlerow">
        <div><h3>Class {grade} journey</h3><p className="jp-sub">{items[0]?.unit_title_en || 'Your child’s Arabic book'}</p></div>
        <div className="jp-terms" role="group" aria-label="Term">
          {[1, 2, 3].map((t) => <button key={t} type="button" aria-pressed={term === t} onClick={() => setTerm(t)}>T{t}</button>)}
        </div>
      </div>
      {lessons.state === 'loading' && <ul className="jp-path jp-path--skeleton" aria-hidden="true">{[0, 1, 2, 3, 4].map((i) => <li key={i}><span className="jp-node" /><span className="jp-bar" /></li>)}</ul>}
      {lessons.state === 'error' && (
        <div className="jp-msg">Couldn’t load the chapters. Check your connection. <button type="button" className="jp-link" onClick={onRetry}>Try again</button></div>
      )}
      {lessons.state === 'ok' && termSoon && <div className="jp-msg jp-msg--soon">Term {term} of Class {grade} is coming soon. Here’s what it will cover.</div>}
      {lessons.state === 'ok' && (
        <ol className="jp-path">
          {items.map((l) => {
            const a = done.get(l.id);
            const state = l.status === 'coming_soon' ? 'soon' : l.id === focusId ? (a ? 'done' : 'now') : 'locked';
            const label = { soon: 'Soon', done: `${a?.correct ?? 0}/${a?.attempts ?? 0} right`, now: 'Now', open: 'Open', locked: 'Locked' }[state];
            return (
              <li key={l.id} className={`is-${state}`}>
                <span className="jp-node">{state === 'done' ? '✓' : l.lesson_order}</span>
                <span className="jp-t"><span lang="ar" dir="rtl">{l.title_ar}</span><small>{l.title_en}</small></span>
                <span className={`jp-state jp-state--${state}`}>{label}</span>
              </li>
            );
          })}
        </ol>
      )}
    </>
  );
}

function WordsView({ content }: { content: ChapterContent }) {
  const [main, ...rest] = content.words;
  const [playingWord, setPlayingWord] = useState(false);
  if (!main) return null;
  const ar = main.vowelled_ar || main.word_ar;
  return (
    <>
      <div><h3>New words</h3><p className="jp-sub">Chapter: {content.titleEn} · <span lang="ar" dir="rtl">{content.titleAr}</span></p></div>
      <div className="jp-word">
        <span className="jp-word__ar" lang="ar" dir="rtl">{ar}</span>
        <span className="jp-word__say">{say(ar)}</span>
        <span className="jp-word__mean">{main.meaning_en}</span>
        <button type="button" className={`jp-listen${playingWord ? ' is-playing' : ''}`}
          onClick={() => { speak(ar); setPlayingWord(true); window.setTimeout(() => setPlayingWord(false), 1600); }}>
          <span className="jp-listen__play" aria-hidden="true"><svg viewBox="0 0 12 12"><path d="M2 1l9 5-9 5z" /></svg></span>
          <span className="jp-wave" aria-hidden="true"><i /><i /><i /><i /><i /></span>
          <span>Hear it</span>
        </button>
      </div>
      <div className="jp-words">
        {rest.slice(0, 3).map((w) => {
          const a = w.vowelled_ar || w.word_ar;
          return (
            <button key={a} type="button" onClick={() => speak(a)} aria-label={`${a}: ${w.meaning_en}. Hear it`}>
              <span lang="ar" dir="rtl">{a}</span><small>{say(a)}</small><small className="jp-words__mean">{w.meaning_en}</small>
            </button>
          );
        })}
      </div>
    </>
  );
}

function ReadView({ content, active, autoplay }: { content: ChapterContent; active: boolean; autoplay: boolean }) {
  const card = content.words.find((w) => w.example_ar)!;
  const sentence = (card.example_ar || '').trim();
  const tokens = useMemo(() => sentence.split(/\s+/).filter(Boolean), [sentence]);
  const [picked, setPicked] = useState(0);
  const [gloss, setGloss] = useState<Record<number, string | null | undefined>>({});

  const meaningFor = useCallback((i: number) => {
    const bare = bareArabic(tokens[i]);
    const hit = content.words.find((w) => bareArabic(w.word_ar) === bare);
    if (hit) return hit.meaning_en;
    return gloss[i];
  }, [tokens, content.words, gloss]);

  const pick = useCallback((i: number, sound: boolean) => {
    setPicked(i);
    if (sound) speak(tokens[i]);
  }, [tokens]);

  // A new chapter's sentence: forget the meanings looked up for the previous one.
  useEffect(() => { setGloss({}); setPicked(0); }, [sentence]);

  // Look up the shown word's meaning when it isn't one of the chapter's vocabulary cards.
  useEffect(() => {
    if (!active || !tokens[picked]) return;
    const bare = bareArabic(tokens[picked]);
    if (content.words.some((w) => bareArabic(w.word_ar) === bare) || gloss[picked] !== undefined) return;
    const i = picked;
    setGloss((g) => ({ ...g, [i]: null }));
    loadGloss(tokens[i].replace(/[.,،؟!:؛]/g, ''), sentence).then((t) => setGloss((g) => ({ ...g, [i]: t ?? '' })));
  }, [active, picked, tokens, content.words, gloss, sentence]);

  // While the tour plays, step through the words of the sentence.
  useEffect(() => {
    if (!active || !autoplay) return;
    let i = 0; pick(0, false);
    const iv = window.setInterval(() => { i += 1; if (i >= tokens.length) { window.clearInterval(iv); return; } pick(i, false); }, 1000);
    return () => window.clearInterval(iv);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, autoplay, sentence]);

  const meaning = meaningFor(picked);
  return (
    <>
      <div><h3>Read the book</h3><p className="jp-sub">Tap any word to hear it and see what it means</p></div>
      <div className="jp-page">
        <span className="jp-page__pg">{content.titleEn}{content.startPage ? ` · from page ${content.startPage}` : ''}</span>
        <div className="jp-sentence" dir="rtl">
          {tokens.map((t, i) => (
            <button key={`${t}-${i}`} type="button" className={`jp-tok${picked === i ? ' is-on' : ''}`} onClick={() => pick(i, true)}>
              <span lang="ar">{t}</span><small dir="ltr">{say(t)}</small>
            </button>
          ))}
        </div>
        {card.example_en && <p className="jp-page__en">{card.example_en}</p>}
      </div>
      <div className="jp-gloss" aria-live="polite">
        <span lang="ar" dir="rtl">{tokens[picked]}</span>
        <b>{say(tokens[picked] || '')}</b>
        <span>{meaning === null || meaning === undefined ? 'Looking it up…' : meaning || 'No English meaning for this word yet.'}</span>
      </div>
    </>
  );
}

function FahimView({ content, active }: { content: ChapterContent; active: boolean }) {
  const w = content.words.find((x) => x.example_ar && x !== content.words[0]) ?? content.words[0];
  const ar = w.vowelled_ar || w.word_ar;
  const [typing, setTyping] = useState(true);
  useEffect(() => {
    if (!active) { setTyping(true); return; }
    const t = window.setTimeout(() => setTyping(false), prefersReducedMotion() ? 0 : 900);
    return () => window.clearTimeout(t);
  }, [active]);
  return (
    <div className="jp-chat">
      <div className="jp-bubble jp-bubble--me">What does <span lang="ar" dir="rtl">{ar}</span> mean, and how do I use it?</div>
      {typing ? <div className="jp-bubble jp-bubble--him" aria-label="Fahim is typing"><span className="jp-typing"><i /><i /><i /></span></div> : (
        <>
          <div className="jp-bubble jp-bubble--him"><span lang="ar" dir="rtl">{ar}</span> ({say(ar)}) means <b>{w.meaning_en.toLowerCase()}</b>.</div>
          {w.example_ar && (
            <div className="jp-bubble jp-bubble--him">Your book uses it like this: <span lang="ar" dir="rtl" className="jp-bubble__ar">{w.example_ar}</span>
              {w.example_en && <em>{w.example_en}</em>}</div>
          )}
        </>
      )}
      <p className="jp-note">From chapter “{content.titleEn}”. Sign in to ask Fahim your own questions.</p>
    </div>
  );
}

function QuizView({ content, active, autoplay, onAnswer }: { content: ChapterContent; active: boolean; autoplay: boolean; onAnswer: () => void }) {
  const words = content.words.slice(0, 6);
  const [round, setRound] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const q = words[round % words.length];
  // Three different meanings: the right one and the next two words' (stable order, no shuffle flicker).
  const options = useMemo(() => {
    const others = words.filter((w) => w.meaning_en !== q.meaning_en).slice(0, 2).map((w) => w.meaning_en);
    const all = [q.meaning_en, ...others];
    const shift = round % all.length;
    return [...all.slice(shift), ...all.slice(0, shift)];
  }, [q, words, round]);
  const ar = q.vowelled_ar || q.word_ar;

  useEffect(() => {
    if (!active) { setPicked(null); return; }
    if (!autoplay) return;
    const t = window.setTimeout(() => setPicked(options.indexOf(q.meaning_en)), 2200);
    return () => window.clearTimeout(t);
  }, [active, autoplay, options, q]);

  const right = picked !== null && options[picked] === q.meaning_en;
  return (
    <>
      <div><h3>Quick check</h3><p className="jp-sub">From chapter “{content.titleEn}”</p></div>
      <div className="jp-q"><span>What does this word mean?</span><span lang="ar" dir="rtl" className="jp-q__ar">{ar}</span><small>{say(ar)}</small></div>
      <div className="jp-opts">
        {options.map((o, i) => (
          <button key={`${i}-${o}`} type="button" className={`jp-opt${picked === i ? (o === q.meaning_en ? ' is-right' : ' is-wrong') : ''}`}
            onClick={() => { setPicked(i); onAnswer(); }}>{o}</button>
        ))}
      </div>
      <div className="jp-feedback" aria-live="polite">
        {picked === null ? '' : right ? 'Right!' : `Not quite. It means “${q.meaning_en}”.`}
        {picked !== null && words.length > 1 && <button type="button" className="jp-link" onClick={() => { setRound((r) => r + 1); setPicked(null); onAnswer(); }}>Next word</button>}
      </div>
    </>
  );
}

function ProgressView({ session, grade, term, items, done, active }: {
  session: Session | null; grade: number; term: number; items: JourneyLesson[]; done: Map<string, LessonActivity>; active: boolean;
}) {
  const real = items.filter((l) => l.status !== 'coming_soon');
  const practised = real.filter((l) => done.has(l.id));
  const pct = real.length ? practised.length / real.length : 0;
  const C = 2 * Math.PI * 32;
  if (!session || session.grade !== grade) {
    return (
      <>
        <div><h3>Progress</h3><p className="jp-sub">Class {grade} · Term {term}</p></div>
        <div className="jp-msg">
          {session
            ? `${session.childName} is in Class ${session.grade}. Pick Class ${session.grade} to see their progress here.`
            : 'Once your child starts, this screen shows each chapter they’ve practised and how many answers they got right.'}
        </div>
        <ul className="jp-steps">
          <li>Chapters practised in each term</li>
          <li>Answers right, chapter by chapter</li>
          <li>When they last practised</li>
        </ul>
      </>
    );
  }
  const last = practised.map((l) => done.get(l.id)!.last_activity).filter(Boolean).sort().pop();
  return (
    <>
      <div><h3>{session.childName}’s progress</h3><p className="jp-sub">Class {grade} · Term {term}</p></div>
      <div className="jp-ringrow">
        <svg className="jp-ring" viewBox="0 0 80 80" aria-hidden="true">
          <circle className="jp-ring__bg" cx="40" cy="40" r="32" />
          <circle className="jp-ring__fg" cx="40" cy="40" r="32" strokeDasharray={C} strokeDashoffset={active ? C * (1 - pct) : C} />
          <text x="40" y="46" textAnchor="middle">{practised.length}/{real.length}</text>
        </svg>
        <div><strong>{practised.length} of {real.length} chapters practised</strong>
          <span className="jp-sub">{last ? `Last practised ${new Date(last).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}` : 'Nothing practised in this term yet'}</span></div>
      </div>
      <ul className="jp-steps jp-steps--done">
        {practised.slice(0, 4).map((l) => {
          const a = done.get(l.id)!;
          return <li key={l.id}><i aria-hidden="true">✓</i>{l.title_en} · {a.correct} of {a.attempts} right</li>;
        })}
      </ul>
    </>
  );
}
