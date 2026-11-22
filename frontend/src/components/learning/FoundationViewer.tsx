import React, { useEffect, useMemo, useState } from 'react';
import { Blocks, CheckCircle2, Circle, Crown, RotateCcw, Volume2, ArrowRight, BookOpen, Languages, Lock, Scissors, Sparkles, Timer } from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ChildProfile } from '../../types';
import { tone } from '../common/cardTones';
import { UpgradeCard } from '../payment/UpgradeCard';
import { WordSplitter } from './WordSplitter';
import { LetterGamesRound, gameWords } from './LetterGames';

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
  | { type: 'builder'; items: { words: string[]; en: string }[] }
  | { type: 'cards'; prompt_en: string; items: { ar: string; en: string }[] }
  | { type: 'fluency'; items: string[] }
  | { type: 'roots'; families: { root: string; meaning_en: string; words: { ar: string; en: string }[] }[] };
type Lesson = {
  id: string; title_ar: string; title_en: string; summary_en: string; points: string[]; examples: Example[];
  quiz: QuizItem[]; table?: { headers: string[]; rows: string[][] }; activity?: Activity;
};
// A stage on the paid plan comes with only its lessons' titles (locked) for learners without a plan.
type Stage = { id: 'A' | 'B' | 'C' | 'D' | 'E'; title_ar: string; title_en: string; summary_en: string; lessons: Lesson[]; locked?: boolean };
type Letter = { letter: string; name: string; sound_en: string; king: boolean };
type VowelMark = { id: string; label_en: string; pattern: string };
type Course = {
  title_ar: string; title_en: string; summary_en: string; alphabet: Letter[]; stages: Stage[];
  vowel_marks: VowelMark[]; grid_letters: string[];
};
type TextbookLink = { lesson_id: string; grade: number; term: number; lesson_order: number; title_ar: string; title_en: string; rule: string };
type Explanation = {
  lang: string; language: string; native_name: string; dir: 'ltr' | 'rtl'; title: string; summary: string;
  points: string[]; examples: string[]; example_arabic: string[];
};

// Parent languages offered for the "explain for parents" panel (translated by the server).
const PARENT_LANGUAGES = [
  { code: 'hi', label: 'हिन्दी', name: 'Hindi' },
  { code: 'ml', label: 'മലയാളം', name: 'Malayalam' },
  { code: 'ur', label: 'اردو', name: 'Urdu' },
];

const ARABIC = /[؀-ۿ]/;
const play = (text: string) => audioManager.playArabic(text);

// Lessons finished, as cached on this device per learner. Signed-in learners' progress lives on the
// account (the server); this copy serves signed-out visitors and keeps lessons finished offline until
// they reach the account.
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
function clearProgress(childId: string | undefined) {
  try { localStorage.removeItem(progressKey(childId)); } catch { /* private mode */ }
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

const VowelGrid: React.FC<{ course: Course; marks: string[] }> = ({ course, marks }) => {
  const [letter, setLetter] = useState('ب');
  const shown = course.vowel_marks.filter((m) => marks.includes(m.id));
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">Choose a letter, then tap a sound to hear it.</p>
      <LetterPicker letters={course.grid_letters} value={letter} onChange={setLetter} />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {shown.map((m) => {
          const text = m.pattern.split('{L}').join(letter);
          return (
            <button key={m.id} type="button" onClick={() => play(text)}
              className="border-2 border-slate-200 hover:border-emerald-700 bg-white p-3 text-center">
              <span className="block text-3xl font-arabic font-black text-emerald-950" dir="rtl">{text}</span>
              <span className="block text-[11px] text-slate-600">{m.label_en}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

const WordCards: React.FC<{ activity: Extract<Activity, { type: 'cards' }> }> = ({ activity }) => (
  <div>
    <p className="text-xs text-slate-600 mb-2">{activity.prompt_en}</p>
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
      {activity.items.map((c, i) => (
        <button key={i} type="button" onClick={() => play(c.ar)}
          className="border-2 border-slate-200 hover:border-emerald-700 bg-white p-3 text-center">
          <span className="block text-2xl font-arabic font-black text-emerald-950" dir="rtl">{c.ar}</span>
          <span className="block text-[11px] text-slate-600">{c.en}</span>
        </button>
      ))}
    </div>
  </div>
);

/** Read a sentence aloud and time it: words per minute, best time kept for this session. */
const Fluency: React.FC<{ activity: Extract<Activity, { type: 'fluency' }> }> = ({ activity }) => {
  const [index, setIndex] = useState(0);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [seconds, setSeconds] = useState<Record<number, number>>({});
  const sentence = activity.items[index];
  const words = sentence.split(/\s+/).filter(Boolean).length;
  const time = seconds[index];
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">1. Listen. 2. Press Start and read the sentence aloud. 3. Press Done. ({index + 1} of {activity.items.length})</p>
      <div className="flex items-start gap-3 bg-white border-2 border-slate-200 p-3">
        <SpeakButton text={sentence} label="Listen to the model" />
        <p className="flex-1 text-2xl font-arabic font-bold text-slate-900 leading-loose" dir="rtl">{sentence}</p>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
        {startedAt === null ? (
          <button type="button" onClick={() => setStartedAt(Date.now())} className="px-3 py-1.5 bg-emerald-900 text-white text-xs font-bold inline-flex items-center gap-1"><Timer className="w-3.5 h-3.5" /> Start</button>
        ) : (
          <button type="button" onClick={() => {
            const took = Math.max(1, (Date.now() - startedAt) / 1000);
            setSeconds((prev) => ({ ...prev, [index]: prev[index] ? Math.min(prev[index], took) : took }));
            setStartedAt(null);
          }} className="px-3 py-1.5 bg-amber-500 text-slate-950 text-xs font-bold">Done</button>
        )}
        {time !== undefined && (
          <span className="font-bold text-emerald-900">Best: {time.toFixed(1)} s · {Math.round((words / time) * 60)} words a minute</span>
        )}
        {index < activity.items.length - 1 && time !== undefined && (
          <button type="button" onClick={() => setIndex(index + 1)} className="px-3 py-1.5 border border-slate-300 text-xs font-bold">Next sentence</button>
        )}
      </div>
    </div>
  );
};

const RootFamilies: React.FC<{ activity: Extract<Activity, { type: 'roots' }> }> = ({ activity }) => {
  const [open, setOpen] = useState(0);
  const family = activity.families[open];
  return (
    <div>
      <p className="text-xs text-slate-600 mb-2">Choose a root to see its word family. Tap a word to hear it.</p>
      <div className="flex flex-wrap gap-2 mb-3">
        {activity.families.map((f, i) => (
          <button key={f.root} type="button" aria-pressed={open === i} onClick={() => setOpen(i)}
            className={`px-3 py-1.5 border-2 text-sm ${open === i ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white border-slate-300 hover:border-emerald-700'}`}>
            <bdi className="font-arabic text-lg font-black">{f.root}</bdi> <span className="text-xs">({f.meaning_en})</span>
          </button>
        ))}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {family.words.map((w) => (
          <button key={w.ar} type="button" onClick={() => play(w.ar)} className="border-2 border-slate-200 hover:border-emerald-700 bg-white p-3 text-center">
            <span className="block text-2xl font-arabic font-black text-emerald-950" dir="rtl">{w.ar}</span>
            <span className="block text-[11px] text-slate-600">{w.en}</span>
          </button>
        ))}
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

const ActivityView: React.FC<{ activity: Activity; course: Course }> = ({ activity, course }) => {
  const alphabet = course.alphabet;
  switch (activity.type) {
    case 'alphabet': return <AlphabetBoard alphabet={alphabet} />;
    case 'letter_shapes': return <LetterShapes alphabet={alphabet} />;
    case 'vowel_grid': return <VowelGrid course={course} marks={activity.marks} />;
    case 'cards': return <WordCards activity={activity} />;
    case 'fluency': return <Fluency activity={activity} />;
    case 'roots': return <RootFamilies activity={activity} />;
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
  /** The class whose textbook chapters are linked (the learner's grade). */
  grade?: number;
  /** Open a textbook chapter in Curriculum & Lessons. */
  onOpenChapter?: (lessonId: string) => void;
  /** Open Ask Fahim with this question (locked on the free plan: the app shows the plans instead). */
  onAskFahim?: (question: string) => void;
  askFahimLocked?: boolean;
  /** Whether a user is signed in (parent-language explanations need an account). */
  signedIn?: boolean;
  /** The learner whose progress is kept on the account (unset for signed-out visitors: device only). */
  progressChildId?: string;
}

/** A lesson's examples; each can open the word splitter (how its letters join). */
const ExampleList: React.FC<{ examples: Example[]; alphabet: Letter[]; openFirst?: boolean }> = ({ examples, alphabet, openFirst = false }) => {
  const [open, setOpen] = useState<number[]>(openFirst && examples.length ? [0] : []);
  const toggle = (i: number) => setOpen((o) => (o.includes(i) ? o.filter((x) => x !== i) : [...o, i]));
  return (
    <div className="space-y-2">
      {examples.map((e, i) => {
        const isOpen = open.includes(i);
        return (
          <div key={i} className="border-b border-slate-100 pb-2 last:border-0 space-y-2">
            <div className="flex items-start gap-3">
              <SpeakButton text={e.ar} />
              <div className="flex-1">
                <div className="text-xl font-arabic font-bold text-slate-900" dir="rtl"><ArabicWordSpans text={e.ar} /></div>
                <div className="text-xs text-slate-600"><Mixed text={e.en} /></div>
              </div>
              <button type="button" onClick={() => toggle(i)} aria-expanded={isOpen}
                className={`shrink-0 px-2 py-1 text-[11px] font-bold border inline-flex items-center gap-1 ${isOpen ? 'bg-sky-800 text-white border-sky-900' : 'bg-white border-sky-300 text-sky-900 hover:border-sky-700'}`}>
                <Scissors className="w-3.5 h-3.5" /> {isOpen ? 'Hide letters' : 'Split into letters'}
              </button>
            </div>
            {isOpen && <WordSplitter text={e.ar} alphabet={alphabet} />}
          </div>
        );
      })}
    </div>
  );
};

export const FoundationViewer: React.FC<FoundationViewerProps> = ({ activeChild, grade = 5, onOpenChapter, onAskFahim, askFahimLocked = false, signedIn = true, progressChildId }) => {
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState('');
  const [stageId, setStageId] = useState<Stage['id']>('A');
  const [lessonId, setLessonId] = useState<string>('');
  const deviceKey = progressChildId || activeChild?.id;
  const [done, setDone] = useState<string[]>(() => loadProgress(deviceKey));
  // Where progress is kept: on the account, on this device only, or not yet saved (offline).
  const [saveState, setSaveState] = useState<'account' | 'device' | 'pending' | 'retry'>(progressChildId ? 'pending' : 'device');
  const [links, setLinks] = useState<Record<string, TextbookLink[]>>({});
  const [parentLang, setParentLang] = useState<string>(() => {
    try { return localStorage.getItem('jisr.foundation.parentLang') || ''; } catch { return ''; }
  });
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [explainError, setExplainError] = useState('');

  // Signed in: the account's progress, plus anything finished on this device (including as a
  // signed-out visitor) that the account doesn't have yet, which is uploaded once.
  useEffect(() => {
    const local = loadProgress(deviceKey);
    setDone(local);
    if (!progressChildId) { setSaveState('device'); return; }
    let cancelled = false;
    setSaveState('pending');
    const guest = loadProgress(undefined);
    api.getFoundationProgress(progressChildId)
      .then(async (res) => {
        const account: string[] = Array.isArray(res.completed) ? res.completed : [];
        const missing = Array.from(new Set([...local, ...guest])).filter((id) => !account.includes(id));
        const merged = missing.length ? (await api.saveFoundationProgress(progressChildId, missing)).completed : account;
        if (cancelled) return;
        setDone(merged);
        saveProgress(deviceKey, merged);
        if (guest.length) clearProgress(undefined);  // a visitor's progress belongs to this learner now
        setSaveState('account');
      })
      .catch(() => { if (!cancelled) setSaveState('retry'); });
    return () => { cancelled = true; };
  }, [progressChildId, deviceKey]);
  // Reloaded when the plan changes (signing in, or a payment): Stages B-E come with a paid plan.
  useEffect(() => {
    api.getFoundation()
      .then((res) => setCourse(res))
      .catch((err) => setError(err instanceof Error ? err.message : 'The Foundation course could not be loaded.'));
  }, [askFahimLocked, signedIn]);

  const stage = course?.stages.find((s) => s.id === stageId);
  const lessons = stage?.lessons || [];
  const lesson = lessons.find((l) => l.id === lessonId) || lessons[0];
  useEffect(() => { if (stage) setLessonId(stage.lessons[0]?.id || ''); }, [stageId, course]);

  useEffect(() => {
    let cancelled = false;
    api.getFoundationTextbookLinks(grade)
      .then((res) => { if (!cancelled) setLinks(res.links || {}); })
      .catch(() => { if (!cancelled) setLinks({}); });
    return () => { cancelled = true; };
  }, [grade]);

  // The lesson in the parent's chosen language (translated once on the server, then saved).
  const currentLessonId = lesson?.id;
  useEffect(() => {
    setExplanation(null);
    setExplainError('');
    if (!parentLang || !currentLessonId || stage?.locked) return;  // a locked stage has no lesson to explain
    if (!signedIn) { setExplainError('Sign in to read the explanation in your language.'); return; }
    let cancelled = false;
    setExplaining(true);
    api.getFoundationExplanation(currentLessonId, parentLang)
      .then((res) => { if (!cancelled) setExplanation(res); })
      .catch((err) => { if (!cancelled) setExplainError(err instanceof Error ? err.message : 'The translation could not be loaded.'); })
      .finally(() => { if (!cancelled) setExplaining(false); });
    return () => { cancelled = true; };
  }, [parentLang, currentLessonId, signedIn, stage?.locked]);

  // '' is English (the lesson as written); the other codes show the parent-language panel.
  const chooseParentLang = (code: string) => {
    const next = code;
    setParentLang(next);
    try { localStorage.setItem('jisr.foundation.parentLang', next); } catch { /* private mode */ }
  };

  const markDone = (id: string) => {
    if (done.includes(id)) return;
    const next = [...done, id];
    setDone(next);
    saveProgress(deviceKey, next);  // kept on the device too, so it is not lost if the save fails
    if (progressChildId) {
      api.saveFoundationProgress(progressChildId, [id])
        .then(() => setSaveState('account'))
        .catch(() => setSaveState('retry'));
    }
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
          <div className="text-[10px] text-emerald-200 mt-1" role="status">
            {saveState === 'account' ? '✓ Saved to your account'
              : saveState === 'pending' ? 'Saving to your account…'
              : saveState === 'retry' ? 'Not saved to your account yet: kept on this device, retried next visit'
              : 'Saved on this device · sign in to keep it'}
          </div>
        </div>
      </div>

      {/* Stages */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2" role="tablist" aria-label="Stages">
        {course.stages.map((s, si) => {
          const n = s.lessons.filter((l) => done.includes(l.id)).length;
          return (
            <button key={s.id} type="button" role="tab" aria-selected={s.id === stageId} onClick={() => setStageId(s.id)}
              className={`text-left p-3 border-2 ${s.id === stageId ? tone(si).active : tone(si).idle}`}>
              <div className="text-xs font-black flex items-center gap-1">
                {s.locked && <Lock className="w-3 h-3" aria-label="locked" />}
                Stage {s.id} · {s.locked ? 'Paid' : `${n}/${s.lessons.length}`}
              </div>
              <div className="font-arabic font-bold text-sm" dir="rtl">{s.title_ar}</div>
              <div className={`text-[11px] ${s.id === stageId ? tone(si).sub : 'text-slate-600'}`}>{s.title_en}</div>
            </button>
          );
        })}
      </div>

      {stage.locked ? (
        <div className="grid grid-cols-1 lg:grid-cols-[17rem_1fr] gap-4">
          <nav aria-label={`Stage ${stage.id} lessons (locked)`} className="bg-white border border-slate-200 p-2 space-y-1 self-start">
            <p className="text-[11px] text-slate-600 px-1 pb-1">{stage.summary_en}</p>
            {stage.lessons.map((l, i) => (
              <div key={l.id} className="px-2 py-1.5 flex items-start gap-2 border-2 bg-slate-50 border-slate-200 text-slate-500">
                <Lock className="w-3.5 h-3.5 shrink-0 mt-0.5" aria-label="locked" />
                <span>
                  <span className="block text-xs font-bold">{stage.id}{i + 1}. {l.title_en}</span>
                  <span className="block text-xs font-arabic" dir="rtl">{l.title_ar}</span>
                </span>
              </div>
            ))}
          </nav>
          <UpgradeCard reason="foundation_stage" stage={stage.id} stageTitle={stage.title_en} grade={grade} className="self-start" />
        </div>
      ) : (
      <div className="grid grid-cols-1 lg:grid-cols-[17rem_1fr] gap-4">
        {/* Lesson list */}
        <nav aria-label={`Stage ${stage.id} lessons`} className="bg-white border border-slate-200 p-2 space-y-1 self-start">
          <p className="text-[11px] text-slate-600 px-1 pb-1">{stage.summary_en}</p>
          {lessons.map((l, i) => (
            <button key={l.id} type="button" onClick={() => setLessonId(l.id)} aria-current={l.id === lesson.id ? 'true' : undefined}
              className={`w-full text-left px-2 py-1.5 flex items-start gap-2 border-2 ${l.id === lesson.id ? tone(i).active : tone(i).idle}`}>
              {done.includes(l.id)
                ? <CheckCircle2 className={`w-4 h-4 shrink-0 mt-0.5 ${l.id === lesson.id ? 'text-white' : 'text-emerald-700'}`} aria-label="Done" />
                : <Circle className={`w-4 h-4 shrink-0 mt-0.5 ${l.id === lesson.id ? 'text-white/70' : 'text-slate-400'}`} />}
              <span>
                <span className="block text-xs font-bold">{stage.id}{i + 1}. {l.title_en}</span>
                <span className={`block text-xs font-arabic ${l.id === lesson.id ? tone(i).sub : 'text-slate-600'}`} dir="rtl">{l.title_ar}</span>
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
            <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3">
              <span className="text-xs font-bold text-slate-700 inline-flex items-center gap-1"><Languages className="w-4 h-4" /> Explain for parents in:</span>
              <button type="button" aria-pressed={!parentLang} onClick={() => chooseParentLang('')} title="English (the lesson as written)"
                className={`px-2.5 py-1 text-sm border ${!parentLang ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white border-slate-300 hover:border-emerald-700'}`}>
                English
              </button>
              {PARENT_LANGUAGES.map((l) => (
                <button key={l.code} type="button" aria-pressed={parentLang === l.code} onClick={() => chooseParentLang(l.code)} title={l.name}
                  className={`px-2.5 py-1 text-sm border ${parentLang === l.code ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white border-slate-300 hover:border-emerald-700'}`}>
                  {l.label}
                </button>
              ))}
              {onAskFahim && (
                <button type="button"
                  onClick={() => onAskFahim(`Please explain this Arabic rule simply, with two easy examples and English under each Arabic sentence: "${lesson.title_en}" (${lesson.title_ar}). ${lesson.summary_en}`)}
                  className="ml-auto px-3 py-1.5 text-xs font-bold bg-gradient-to-r from-[#6C5CE7] to-[#8E44AD] text-white inline-flex items-center gap-1.5"
                  title={askFahimLocked ? 'Ask Fahim is part of the paid plan' : 'Ask Fahim to explain this rule'}>
                  {askFahimLocked ? <Lock className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5 text-amber-300" />}
                  Ask Fahim to explain this rule{askFahimLocked ? ' (paid plan)' : ''}
                </button>
              )}
            </div>
          </header>

          {parentLang && (
            <section className="bg-sky-50 border-2 border-sky-300 p-4" aria-live="polite">
              {explaining && <p className="text-sm text-slate-600">Translating… (the first time can take a few seconds)</p>}
              {explainError && <p role="alert" className="text-sm text-red-800">{explainError}</p>}
              {explanation && (
                <div dir={explanation.dir} lang={explanation.lang}>
                  <div className="text-[11px] font-black uppercase tracking-wider text-sky-900 mb-1" dir="ltr">For parents · {explanation.language} ({explanation.native_name})</div>
                  {explanation.title && <h3 className="text-base font-bold text-slate-900">{explanation.title}</h3>}
                  <p className="text-sm text-slate-800 mt-1"><Mixed text={explanation.summary} /></p>
                  <ul className="mt-2 space-y-1 list-disc ps-5 text-sm text-slate-800">
                    {explanation.points.map((p, i) => <li key={i}><Mixed text={p} /></li>)}
                  </ul>
                  {explanation.examples.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {explanation.examples.map((e, i) => (
                        <div key={i} className="text-sm text-slate-800 flex flex-wrap items-baseline gap-2">
                          <bdi className="font-arabic font-bold text-base text-slate-900">{explanation.example_arabic[i]}</bdi>
                          <span>— {e}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="mt-3 text-[11px] text-slate-500" dir="ltr">Machine translation of the English explanation; the Arabic is unchanged. Please tell us if something reads wrongly.</p>
                </div>
              )}
            </section>
          )}

          <section className="bg-white border border-slate-200 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2">The rule</h3>
            <ul className="space-y-1.5 list-disc pl-5 text-sm text-slate-800">
              {lesson.points.map((p, i) => <li key={i}><Mixed text={p} /></li>)}
            </ul>
          </section>

          <section className="bg-white border border-slate-200 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2">Examples: tap a word to hear it, or split it into its letters</h3>
            <ExampleList key={lesson.id} examples={lesson.examples} alphabet={course.alphabet}
              openFirst={stage.id === 'A'} />
          </section>

          {/* Letters and reading stages: build each example word and spot letters in it. */}
          {(stage.id === 'A' || stage.id === 'B') && gameWords(lesson.examples.map((e) => e.ar)).length > 0 && (
            <section className="bg-sky-50/50 border-2 border-sky-300 p-4">
              <h3 className="text-xs font-black uppercase tracking-wider text-sky-900 mb-2">Letter games: build the words and find the letters</h3>
              <LetterGamesRound key={lesson.id} texts={lesson.examples.map((e) => e.ar)} alphabet={course.alphabet} />
            </section>
          )}

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
              <ActivityView key={lesson.id} activity={lesson.activity} course={course} />
            </section>
          )}

          {(links[lesson.id] || []).length > 0 && (
            <section className="bg-white border border-slate-200 p-4">
              <h3 className="text-xs font-black uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5"><BookOpen className="w-4 h-4" /> In your textbook (Class {grade})</h3>
              <ul className="space-y-1.5">
                {links[lesson.id].map((l) => (
                  <li key={l.lesson_id}>
                    <button type="button" onClick={() => onOpenChapter?.(l.lesson_id)} disabled={!onOpenChapter}
                      className="w-full text-left flex flex-wrap items-baseline gap-x-2 px-2 py-1.5 border border-slate-200 hover:border-emerald-700 hover:bg-emerald-50">
                      <span className="text-xs font-bold text-emerald-900">Term {l.term} · Chapter {l.lesson_order}</span>
                      <bdi className="font-arabic font-bold text-slate-900">{l.title_ar}</bdi>
                      <span className="text-xs text-slate-600">{l.title_en}</span>
                      {l.rule && <span className="text-[11px] text-slate-500 w-full"><Mixed text={`Rule: ${l.rule}`} /></span>}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section className="bg-white border-2 border-emerald-800 p-4">
            <h3 className="text-xs font-black uppercase tracking-wider text-emerald-900 mb-2">Check yourself: answer every question correctly to finish the lesson</h3>
            <Quiz key={lesson.id} items={lesson.quiz} onAllCorrect={() => markDone(lesson.id)} />
          </section>

          {/* A finished stage is the moment to show what the paid curriculum adds (free learners only). */}
          {!next && stage.lessons.every((l) => done.includes(l.id)) && (
            <UpgradeCard reason="foundation" grade={grade} />
          )}

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
      )}
    </div>
  );
};
