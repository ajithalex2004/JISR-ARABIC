import React, { useEffect, useMemo, useState } from 'react';
import { Blocks, CheckCircle2, Circle, Crown, RotateCcw, Volume2, ArrowRight } from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ChildProfile } from '../../types';

// ---------------------------------------------------------------------------------------------
// Course shape (backend/foundation_data.py)
// ---------------------------------------------------------------------------------------------

type Example = { ar: string; en: string; note?: string };
type QuizItem = { question_en: string; question_ar?: string; options: string[]; correct_index: number; explain_en: string };
type Activity =
  | { type: 'alphabet' }
  | { type: 'letter_shapes' }
  | { type: 'vowel_grid'; marks: string[] }
  | { type: 'sort'; prompt_en: string; buckets: { id: string; label: string }[]; items: { text: string; bucket: string }[] }
  | { type: 'syllables'; items: { word: string; parts: string[] }[] }
  | { type: 'builder'; items: { words: string[]; en: string }[] };
type Lesson = {
  id: string; title_ar: string; title_en: string; summary_en: string; points: string[]; examples: Example[];
  quiz: QuizItem[]; table?: { headers: string[]; rows: string[][] }; activity?: Activity;
};
type Stage = { id: 'A' | 'B' | 'C' | 'D'; title_ar: string; title_en: string; summary_en: string; lessons: Lesson[] };
type Letter = { letter: string; name: string; sound_en: string; king: boolean };
type Course = { title_ar: string; title_en: string; summary_en: string; alphabet: Letter[]; stages: Stage[] };

const ARABIC = /[؀-ۿ]/;
const play = (text: string) => audioManager.playArabic(text);

// Lessons finished on this device, per learner (a convenience: the course itself is on the server).
const progressKey = (childId?: string) => `jisr.foundation.v1.${childId || 'guest'}`;
function loadProgress(childId?: string): string[] {
  try {
    const raw = localStorage.getItem(progressKey(childId));
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}
function saveProgress(childId: string | undefined, done: string[]) {
  try { localStorage.setItem(progressKey(childId), JSON.stringify(done)); } catch { /* private mode */ }
}

/** Text that may mix Arabic and English: Arabic runs are shown right-to-left in the Arabic font. */
const Mixed: React.FC<{ text: string; className?: string }> = ({ text, className = '' }) => (
  <span className={className} dir="auto">
    {text.split(/([\u0600-\u06FF](?:[\u0600-\u06FF\u064B-\u0652\u0670\u0640]|[\s.\u2026]+(?=[\u0600-\u06FF]))*)/).map((part, i) =>
      ARABIC.test(part)
        ? <bdi key={i} className="font-arabic text-[1.08em] font-bold text-slate-900">{part}</bdi>
        : <React.Fragment key={i}>{part}</React.Fragment>)}
  </span>
);

const SpeakButton: React.FC<{ text: string; label?: string }> = ({ text, label = 'Listen' }) => (
  <button type="button" onClick={() => play(text)} aria-label={`${label}: ${text}`}
    className="shrink-0 p-1.5 border border-slate-300 text-slate-600 hover:text-emerald-800 hover:border-emerald-700">
    <Volume2 className="w-4 h-4" />
  </button>
);

// ---------------------------------------------------------------------------------------------
// Activities
// ---------------------------------------------------------------------------------------------

const AlphabetBoard: React.FC<{ alphabet: Letter[] }> = ({ alphabet }) => (
  <div>
    <p className="text-xs text-slate-600 mb-2">Tap a letter to hear its name. <Crown className="inline w-3.5 h-3.5 text-amber-600" /> marks the six King letters.</p>
    <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2" dir="rtl">
      {alphabet.map((l) => (
        <button key={l.letter} type="button" onClick={() => play(l.name)}
          className="relative border-2 border-slate-200 hover:border-emerald-700 bg-white p-2 text-center">
          {l.king && <Crown className="absolute top-1 left-1 w-3 h-3 text-amber-600" aria-label="King letter" />}
          <span className="block text-3xl font-arabic font-black text-emerald-950 leading-tight">{l.letter}</span>
          <span className="block text-xs font-arabic text-slate-700">{l.name}</span>
          <span className="block text-[10px] text-slate-500" dir="ltr">{l.sound_en}</span>
        </button>
      ))}
    </div>
  </div>
);

const LetterPicker: React.FC<{ letters: string[]; value: string; onChange: (l: string) => void }> = ({ letters, value, onChange }) => (
  <div className="flex flex-wrap gap-1 mb-3" dir="rtl" role="radiogroup" aria-label="Choose a letter">
    {letters.map((l) => (
      <button key={l} type="button" role="radio" aria-checked={value === l} onClick={() => onChange(l)}
        className={`w-9 h-9 text-lg font-arabic font-bold border ${value === l ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white border-slate-300 hover:border-emerald-700'}`}>
        {l}
      </button>
    ))}
  </div>
);

const LetterShapes: React.FC<{ alphabet: Letter[] }> = ({ alphabet }) => {
  const letters = alphabet.filter((l) => l.letter !== 'ء');
  const [letter, setLetter] = useState('ع');
  const king = letters.find((l) => l.letter === letter)?.king;
  const shapes = [
    { label: 'Alone', ar: 'مُنْفَصِل', form: letter },
    { label: 'Start', ar: 'أَوَّل الكَلِمَة', form: king ? letter : `${letter}ـ` },
    { label: 'Middle', ar: 'وَسَط الكَلِمَة', form: king ? `ـ${letter}` : `ـ${letter}ـ` },
    { label: 'End', ar: 'آخِر الكَلِمَة', form: `ـ${letter}` },
  ];
  return (
    <div>
      <LetterPicker letters={letters.map((l) => l.letter)} value={letter} onChange={setLetter} />
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2" dir="rtl">
        {shapes.map((s) => (
          <div key={s.label} className="border-2 border-slate-200 bg-white p-3 text-center">
            <span className="block text-4xl font-arabic font-black text-emerald-950">{s.form}</span>
            <span className="block text-xs font-arabic text-slate-700 mt-1">{s.ar}</span>
            <span className="block text-[10px] text-slate-500" dir="ltr">{s.label}</span>
          </div>
        ))}
      </div>
      {king && (
        <p className="mt-2 text-xs text-amber-900 bg-amber-50 border border-amber-200 px-3 py-2">
          <Crown className="inline w-3.5 h-3.5" /> <bdi className="font-arabic font-bold">{letter}</bdi> is a King letter: it never joins the letter after it, so its start and middle shapes don't reach forward.
        </p>
      )}
    </div>
  );
};

const MARKS: Record<string, { label: string; make: (l: string) => string }> = {
  fatha: { label: 'Fatha (a)', make: (l) => `${l}َ` },
  kasra: { label: 'Kasra (i)', make: (l) => `${l}ِ` },
  damma: { label: 'Damma (u)', make: (l) => `${l}ُ` },
  // A letter with sukun can't be said alone: it closes a syllable (أَبْ).
  sukun: { label: 'Sukun (no vowel)', make: (l) => `أَ${l}ْ` },
  long_a: { label: 'Long aa', make: (l) => `${l}َا` },
  long_i: { label: 'Long ii', make: (l) => `${l}ِي` },
  long_u: { label: 'Long uu', make: (l) => `${l}ُو` },
  tanween_fath: { label: 'Tanween fath (an)', make: (l) => `${l}ًا` },
  tanween_kasr: { label: 'Tanween kasr (in)', make: (l) => `${l}ٍ` },
  tanween_damm: { label: 'Tanween damm (un)', make: (l) => `${l}ٌ` },
  shadda_fatha: { label: 'Shadda + fatha', make: (l) => `أَ${l}َّ` },
  shadda_kasra: { label: 'Shadda + kasra', make: (l) => `أَ${l}ِّ` },
  shadda_damma: { label: 'Shadda + damma', make: (l) => `أَ${l}ُّ` },
};

const VowelGrid: React.FC<{ alphabet: Letter[]; marks: string[] }> = ({ alphabet, marks }) => {
  const letters = alphabet.map((l) => l.letter).filter((l) => l !== 'ء' && l !== 'ا');
  const [letter, setLetter] = useState('ب');
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">Choose a letter, then tap a sound to hear it.</p>
      <LetterPicker letters={letters} value={letter} onChange={setLetter} />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {marks.filter((m) => MARKS[m]).map((m) => {
          const text = MARKS[m].make(letter);
          return (
            <button key={m} type="button" onClick={() => play(text)}
              className="border-2 border-slate-200 hover:border-emerald-700 bg-white p-3 text-center">
              <span className="block text-3xl font-arabic font-black text-emerald-950" dir="rtl">{text}</span>
              <span className="block text-[11px] text-slate-600">{MARKS[m].label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

const SortGame: React.FC<{ activity: Extract<Activity, { type: 'sort' }> }> = ({ activity }) => {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const correct = activity.items.filter((it, i) => answers[i] === it.bucket).length;
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">{activity.prompt_en}</p>
      <div className="space-y-2">
        {activity.items.map((item, i) => {
          const chosen = answers[i];
          const right = chosen === item.bucket;
          return (
            <div key={i} className={`flex flex-wrap items-center gap-2 border p-2 ${chosen ? (right ? 'border-emerald-600 bg-emerald-50' : 'border-red-400 bg-red-50') : 'border-slate-200 bg-white'}`}>
              <button type="button" onClick={() => play(item.text)} className="min-w-[4.5rem] text-2xl font-arabic font-black text-slate-900 text-center" dir="rtl" aria-label={`Listen: ${item.text}`}>
                {item.text}
              </button>
              <div className="flex flex-wrap gap-1.5">
                {activity.buckets.map((b) => (
                  <button key={b.id} type="button" aria-pressed={chosen === b.id}
                    onClick={() => setAnswers((prev) => ({ ...prev, [i]: b.id }))}
                    className={`px-2.5 py-1 text-xs font-bold border ${chosen === b.id ? (right ? 'bg-emerald-800 text-white border-emerald-900' : 'bg-red-700 text-white border-red-800') : 'bg-white border-slate-300 hover:border-emerald-700 text-slate-800'}`}>
                    <Mixed text={b.label} />
                  </button>
                ))}
              </div>
              {chosen && <span className="text-xs font-bold ml-auto">{right ? '✓ Correct' : '✗ Try again'}</span>}
            </div>
          );
        })}
      </div>
      <div className="mt-2 flex items-center gap-3 text-sm">
        <span className="font-bold text-slate-800">{correct} / {activity.items.length} correct</span>
        <button type="button" onClick={() => setAnswers({})} className="text-xs text-slate-600 hover:text-slate-900 inline-flex items-center gap-1"><RotateCcw className="w-3.5 h-3.5" /> Start again</button>
      </div>
    </div>
  );
};

const Syllables: React.FC<{ activity: Extract<Activity, { type: 'syllables' }> }> = ({ activity }) => {
  const [shown, setShown] = useState<Record<number, boolean>>({});
  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-600">Say the word, split it yourself, then tap "Split" to check. Tap a syllable to hear it.</p>
      {activity.items.map((item, i) => (
        <div key={i} className="flex flex-wrap items-center gap-3 border border-slate-200 bg-white p-2">
          <button type="button" onClick={() => play(item.word)} className="text-2xl font-arabic font-black text-slate-900 min-w-[7rem] text-center" dir="rtl">{item.word}</button>
          {shown[i] ? (
            <div className="flex flex-wrap gap-1.5" dir="rtl">
              {item.parts.map((p, k) => (
                <button key={k} type="button" onClick={() => play(p)} className="px-2 py-1 bg-emerald-50 border border-emerald-300 text-xl font-arabic font-bold text-emerald-950">{p}</button>
              ))}
              <span className="self-center text-xs text-slate-500" dir="ltr">{item.parts.length} syllables</span>
            </div>
          ) : (
            <button type="button" onClick={() => setShown((s) => ({ ...s, [i]: true }))} className="px-3 py-1 text-xs font-bold bg-emerald-900 text-white">Split</button>
          )}
        </div>
      ))}
    </div>
  );
};

const SentenceBuilder: React.FC<{ activity: Extract<Activity, { type: 'builder' }> }> = ({ activity }) => {
  const [index, setIndex] = useState(0);
  const item = activity.items[index];
  // Shown in reverse so the right order is never the starting order.
  const tiles = useMemo(() => item.words.map((w, i) => ({ w, i })).reverse(), [item]);
  const [picked, setPicked] = useState<number[]>([]);
  useEffect(() => setPicked([]), [index]);
  const done = picked.length === item.words.length;
  const right = done && picked.every((p, k) => p === k);
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">Tap the words in the right order. ({index + 1} of {activity.items.length}) · {item.en}</p>
      <div className="min-h-[3.25rem] border-2 border-dashed border-slate-300 bg-white p-2 flex flex-wrap gap-2 mb-2" dir="rtl">
        {picked.map((p) => (
          <button key={p} type="button" onClick={() => setPicked((prev) => prev.filter((x) => x !== p))}
            className="px-2 py-1 bg-emerald-900 text-white text-xl font-arabic font-bold">{item.words[p]}</button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 mb-2" dir="rtl">
        {tiles.filter((t) => !picked.includes(t.i)).map((t) => (
          <button key={t.i} type="button" onClick={() => setPicked((prev) => [...prev, t.i])}
            className="px-2 py-1 bg-white border-2 border-slate-300 hover:border-emerald-700 text-xl font-arabic font-bold text-slate-900">{t.w}</button>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-3 text-sm">
        {done && <span className={`font-bold ${right ? 'text-emerald-800' : 'text-red-700'}`}>{right ? '✓ Well done!' : '✗ Not quite: tap a word to take it back.'}</span>}
        {right && <SpeakButton text={item.words.join(' ')} />}
        <button type="button" onClick={() => setPicked([])} className="text-xs text-slate-600 inline-flex items-center gap-1"><RotateCcw className="w-3.5 h-3.5" /> Clear</button>
        {right && index < activity.items.length - 1 && (
          <button type="button" onClick={() => setIndex(index + 1)} className="px-3 py-1 text-xs font-bold bg-emerald-900 text-white">Next sentence</button>
        )}
      </div>
    </div>
  );
};

const ActivityView: React.FC<{ activity: Activity; alphabet: Letter[] }> = ({ activity, alphabet }) => {
  switch (activity.type) {
    case 'alphabet': return <AlphabetBoard alphabet={alphabet} />;
    case 'letter_shapes': return <LetterShapes alphabet={alphabet} />;
    case 'vowel_grid': return <VowelGrid alphabet={alphabet} marks={activity.marks} />;
    case 'sort': return <SortGame activity={activity} />;
    case 'syllables': return <Syllables activity={activity} />;
    case 'builder': return <SentenceBuilder activity={activity} />;
    default: return null;
  }
};

// ---------------------------------------------------------------------------------------------
// Quiz
// ---------------------------------------------------------------------------------------------

const Quiz: React.FC<{ items: QuizItem[]; onAllCorrect: () => void }> = ({ items, onAllCorrect }) => {
  const [chosen, setChosen] = useState<Record<number, number>>({});
  const allCorrect = items.every((q, i) => chosen[i] === q.correct_index);
  useEffect(() => { if (allCorrect) onAllCorrect(); }, [allCorrect]);
  return (
    <div className="space-y-3">
      {items.map((q, i) => {
        const pick = chosen[i];
        const answered = pick !== undefined;
        const right = pick === q.correct_index;
        return (
          <div key={i} className="border border-slate-200 bg-white p-3">
            <p className="text-sm font-bold text-slate-900 mb-2"><Mixed text={`${i + 1}. ${q.question_en}`} /></p>
            <div className="flex flex-wrap gap-2">
              {q.options.map((opt, k) => (
                <button key={k} type="button" aria-pressed={pick === k}
                  onClick={() => setChosen((prev) => ({ ...prev, [i]: k }))}
                  className={`px-3 py-1.5 border-2 text-sm ${pick === k ? (right ? 'bg-emerald-800 text-white border-emerald-900' : 'bg-red-700 text-white border-red-800') : 'bg-white border-slate-300 hover:border-emerald-700 text-slate-900'}`}>
                  {ARABIC.test(opt) && !/[A-Za-z]/.test(opt) ? <bdi className="font-arabic text-lg font-bold">{opt}</bdi> : <Mixed text={opt} />}
                </button>
              ))}
            </div>
            {answered && (
              <p className={`mt-2 text-xs ${right ? 'text-emerald-900' : 'text-red-800'}`}>
                {right ? '✓ ' : '✗ Try again. '}{right && <Mixed text={q.explain_en} />}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------------------------

interface FoundationViewerProps {
  activeChild?: ChildProfile | null;
}

export const FoundationViewer: React.FC<FoundationViewerProps> = ({ activeChild }) => {
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState('');
  const [stageId, setStageId] = useState<Stage['id']>('A');
  const [lessonId, setLessonId] = useState<string>('');
  const [done, setDone] = useState<string[]>(() => loadProgress(activeChild?.id));

  useEffect(() => { setDone(loadProgress(activeChild?.id)); }, [activeChild?.id]);
  useEffect(() => {
    api.getFoundation()
      .then((res) => setCourse(res))
      .catch((err) => setError(err instanceof Error ? err.message : 'The Foundation course could not be loaded.'));
  }, []);

  const stage = course?.stages.find((s) => s.id === stageId);
  const lessons = stage?.lessons || [];
  const lesson = lessons.find((l) => l.id === lessonId) || lessons[0];
  useEffect(() => { if (stage) setLessonId(stage.lessons[0]?.id || ''); }, [stageId, course]);

  const markDone = (id: string) => {
    setDone((prev) => {
      if (prev.includes(id)) return prev;
      const next = [...prev, id];
      saveProgress(activeChild?.id, next);
      return next;
    });
  };

  if (error) return <div className="max-w-5xl mx-auto px-4 py-8"><p role="alert" className="text-red-700">{error}</p></div>;
  if (!course || !stage || !lesson) {
    return <div className="max-w-5xl mx-auto px-4 py-16 text-center text-slate-600"><Blocks className="w-8 h-8 mx-auto mb-2 animate-pulse text-emerald-800" />Loading…</div>;
  }

  const total = course.stages.reduce((n, s) => n + s.lessons.length, 0);
  const doneTotal = course.stages.reduce((n, s) => n + s.lessons.filter((l) => done.includes(l.id)).length, 0);
  const index = lessons.findIndex((l) => l.id === lesson.id);
  const next = lessons[index + 1];
  const nextStage = course.stages[course.stages.findIndex((s) => s.id === stageId) + 1];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      {/* Banner */}
      <div className="bg-emerald-950 text-white border-2 border-slate-900 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-300 text-xs font-bold uppercase tracking-wider"><Blocks className="w-4 h-4" /> {course.title_en}</div>
          <h1 className="text-2xl font-black font-arabic mt-1">{course.title_ar}</h1>
          <p className="text-xs text-emerald-100 mt-1 max-w-xl">{course.summary_en}</p>
        </div>
        <div className="bg-slate-900 border border-emerald-700 px-4 py-2 text-sm">
          <div className="text-[11px] text-emerald-200">Your progress</div>
          <div className="font-black">{doneTotal} / {total} lessons</div>
          <div className="w-40 h-1.5 bg-emerald-900 mt-1"><div className="h-1.5 bg-amber-400" style={{ width: `${(doneTotal / total) * 100}%` }} /></div>
        </div>
      </div>

      {/* Stages */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2" role="tablist" aria-label="Stages">
        {course.stages.map((s) => {
          const n = s.lessons.filter((l) => done.includes(l.id)).length;
          return (
            <button key={s.id} type="button" role="tab" aria-selected={s.id === stageId} onClick={() => setStageId(s.id)}
              className={`text-left p-3 border-2 ${s.id === stageId ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white border-slate-200 hover:border-emerald-700 text-slate-900'}`}>
              <div className="text-xs font-black">Stage {s.id} · {n}/{s.lessons.length}</div>
              <div className="font-arabic font-bold text-sm" dir="rtl">{s.title_ar}</div>
              <div className={`text-[11px] ${s.id === stageId ? 'text-emerald-100' : 'text-slate-500'}`}>{s.title_en}</div>
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[17rem_1fr] gap-4">
        {/* Lesson list */}
        <nav aria-label={`Stage ${stage.id} lessons`} className="bg-white border border-slate-200 p-2 space-y-1 self-start">
          <p className="text-[11px] text-slate-600 px-1 pb-1">{stage.summary_en}</p>
          {lessons.map((l, i) => (
            <button key={l.id} type="button" onClick={() => setLessonId(l.id)} aria-current={l.id === lesson.id ? 'true' : undefined}
              className={`w-full text-left px-2 py-1.5 flex items-start gap-2 ${l.id === lesson.id ? 'bg-emerald-50 border-l-4 border-emerald-800' : 'hover:bg-slate-50 border-l-4 border-transparent'}`}>
              {done.includes(l.id) ? <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" aria-label="Done" /> : <Circle className="w-4 h-4 text-slate-300 shrink-0 mt-0.5" />}
              <span>
                <span className="block text-xs font-bold text-slate-900">{stage.id}{i + 1}. {l.title_en}</span>
                <span className="block text-xs font-arabic text-slate-600" dir="rtl">{l.title_ar}</span>
              </span>
            </button>
          ))}
        </nav>

        {/* Lesson */}
        <article className="space-y-4">
          <header className="bg-white border-2 border-slate-900 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-[11px] font-black text-emerald-800">STAGE {stage.id} · LESSON {index + 1}</div>
                <h2 className="text-xl font-black font-arabic text-slate-900" dir="rtl">{lesson.title_ar}</h2>
                <p className="text-sm font-bold text-slate-700">{lesson.title_en}</p>
              </div>
              {done.includes(lesson.id) && <span className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 px-2 py-1">✓ Completed</span>}
            </div>
            <p className="text-sm text-slate-700 mt-2"><Mixed text={lesson.summary_en} /></p>
          </header>

          <section className="bg-white border border-slate-200 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2">The rule</h3>
            <ul className="space-y-1.5 list-disc pl-5 text-sm text-slate-800">
              {lesson.points.map((p, i) => <li key={i}><Mixed text={p} /></li>)}
            </ul>
          </section>

          <section className="bg-white border border-slate-200 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2">Examples: tap a word to hear it</h3>
            <div className="space-y-2">
              {lesson.examples.map((e, i) => (
                <div key={i} className="flex items-start gap-3 border-b border-slate-100 pb-2 last:border-0">
                  <SpeakButton text={e.ar} />
                  <div className="flex-1">
                    <div className="text-xl font-arabic font-bold text-slate-900" dir="rtl"><ArabicWordSpans text={e.ar} /></div>
                    <div className="text-xs text-slate-600"><Mixed text={e.en} /></div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {lesson.table && (
            <section className="bg-white border border-slate-200 p-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr>{lesson.table.headers.map((h, i) => <th key={i} className="text-left bg-slate-50 px-2 py-1.5 text-xs text-slate-600 border-b">{h}</th>)}</tr></thead>
                <tbody>
                  {lesson.table.rows.map((row, r) => (
                    <tr key={r} className="border-b border-slate-100">
                      {row.map((cell, c) => <td key={c} className="px-2 py-1.5"><Mixed text={cell} /></td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {lesson.activity && (
            <section className="bg-amber-50/40 border-2 border-amber-300 p-4">
              <h3 className="text-xs font-black uppercase tracking-wider text-amber-900 mb-2">Practice</h3>
              <ActivityView key={lesson.id} activity={lesson.activity} alphabet={course.alphabet} />
            </section>
          )}

          <section className="bg-white border-2 border-emerald-800 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-emerald-900 mb-2">Check yourself: answer every question correctly to finish the lesson</h3>
            <Quiz key={lesson.id} items={lesson.quiz} onAllCorrect={() => markDone(lesson.id)} />
          </section>

          <div className="flex justify-end">
            {next ? (
              <button type="button" onClick={() => setLessonId(next.id)} className="px-4 py-2 bg-emerald-900 text-white text-sm font-bold inline-flex items-center gap-2">
                Next: {next.title_en} <ArrowRight className="w-4 h-4" />
              </button>
            ) : nextStage ? (
              <button type="button" onClick={() => setStageId(nextStage.id)} className="px-4 py-2 bg-emerald-900 text-white text-sm font-bold inline-flex items-center gap-2">
                Go to Stage {nextStage.id}: {nextStage.title_en} <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <span className="text-sm font-bold text-emerald-800">🎉 That's the whole Foundation course.</span>
            )}
          </div>
        </article>
      </div>
    </div>
  );
};
