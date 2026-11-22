import React, { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, RotateCcw, Trophy, Volume2 } from 'lucide-react';
import { audioManager } from '../../services/audio';
import { stripTashkeel, useTashkeel } from '../../services/tashkeel';
import { LETTER_FORM_NAMES, Position, SplitLetter, shapedLetter, splitWord, wordsOf } from '../../services/wordSplit';

type AlphabetLetter = { letter: string; name: string; sound_en: string };

const play = (text: string) => audioManager.playArabic(text);
const WHERE: Record<Position, string> = {
  initial: 'joined only to the letter after it (a start shape)',
  medial: 'joined on both sides (a middle shape)',
  final: 'joined only to the letter before it (an end shape)',
  isolated: 'on its own',
};
const COLOURS = ['text-blue-700', 'text-amber-700', 'text-emerald-700', 'text-rose-700', 'text-violet-700', 'text-cyan-700', 'text-orange-700', 'text-fuchsia-700'];

/** A letter's name for prompts: its alphabet name, or the name of its hamza / ة / ى form. */
const letterName = (base: string, names: Map<string, AlphabetLetter>) => names.get(base)?.name || LETTER_FORM_NAMES[base] || base;

function shuffled<T>(items: T[]): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  // Never hand back the answer already in order.
  if (out.length > 1 && out.every((x, i) => x === items[i])) return [...out.slice(1), out[0]];
  return out;
}

const sameLetter = (a: SplitLetter, b: SplitLetter) => a.base === b.base && a.marks === b.marks;

// ---------------------------------------------------------------------------------------------
// Build the word: put the letters in order (tap, or drag on a computer) and watch them join.
// ---------------------------------------------------------------------------------------------

interface GameProps {
  word: string;
  alphabet: AlphabetLetter[];
  /** Called once when the round is finished, with whether it was done without a mistake. */
  onDone?: (firstTry: boolean) => void;
}

export const BuildWord: React.FC<GameProps> = ({ word, alphabet, onDone }) => {
  const letters = useMemo(() => splitWord(word).letters, [word]);
  const names = useMemo(() => new Map(alphabet.map((a) => [a.letter, a])), [alphabet]);
  const [tray, setTray] = useState<number[]>([]);       // letter indexes still to place, in shuffled order
  const [placed, setPlaced] = useState(0);              // how many letters are in place
  const [mistakes, setMistakes] = useState(0);
  const [wrong, setWrong] = useState<number | null>(null);
  const [tashkeelMode] = useTashkeel();
  const withMarks = tashkeelMode !== 'plain';

  const reset = () => { setTray(shuffled(letters.map((_, i) => i))); setPlaced(0); setMistakes(0); setWrong(null); };
  useEffect(reset, [letters]);

  const done = letters.length > 0 && placed === letters.length;
  useEffect(() => {
    if (!done) return;
    play(word);
    onDone?.(mistakes === 0);
  }, [done]);  // eslint-disable-line react-hooks/exhaustive-deps

  // Any tile with the right letter may go next (a word can repeat a letter).
  const choose = (trayIndex: number) => {
    if (done) return;
    const tile = letters[tray[trayIndex]];
    if (sameLetter(tile, letters[placed])) {
      setTray((t) => t.filter((_, i) => i !== trayIndex));
      setPlaced((p) => p + 1);
      setWrong(null);
    } else {
      setMistakes((m) => m + 1);
      setWrong(trayIndex);
      window.setTimeout(() => setWrong((w) => (w === trayIndex ? null : w)), 600);
    }
  };

  const next = letters[placed];
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-center gap-3">
        <span className="text-sm text-slate-800">Make this word:</span>
        <span className="font-arabic text-4xl font-black text-slate-900 border-2 border-slate-300 bg-white px-3 leading-[1.6]" dir="rtl">
          {withMarks ? word : stripTashkeel(word)}
        </span>
      </div>
      <p className="text-xs text-slate-700 text-center">
        {done ? <span className="font-bold text-emerald-800">Well done! The letters join to make the word.</span>
          : <>Find each letter below and place them in order, starting from the <b>right</b>. Tap a letter{' '}
            <span className="hidden sm:inline">(or drag it to the line)</span> to place it.</>}
      </p>

      {/* The word being built: placed letters take their joined shape; they close up when it is done. */}
      <div className="flex justify-center" dir="rtl">
        <div
          className={`flex items-end transition-all duration-700 ${done ? 'gap-0' : 'gap-1.5'}`}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); const i = Number(e.dataTransfer.getData('text/plain')); if (!Number.isNaN(i)) choose(i); }}
          aria-label={`The word, ${placed} of ${letters.length} letters placed`}>
          {letters.map((l, i) => (
            <span key={i}
              className={`flex items-center justify-center font-arabic font-bold text-3xl sm:text-4xl leading-[1.6] transition-all duration-700 ${
                done ? 'min-w-0 border-0' : `min-w-[2.25rem] sm:min-w-[3rem] border-b-4 ${i === placed ? 'border-sky-600 bg-sky-100/60' : 'border-slate-300'}`
              } ${i < placed ? COLOURS[i % COLOURS.length] : 'text-transparent'}`}>
              {i < placed ? shapedLetter(l, withMarks) : ' '}
            </span>
          ))}
        </div>
      </div>

      {!done && (
        <div className="flex flex-wrap justify-center gap-2" dir="rtl" role="group" aria-label="Letters to place">
          {tray.map((letterIndex, i) => {
            const l = letters[letterIndex];
            return (
              <button key={`${letterIndex}`} type="button" draggable
                onDragStart={(e) => e.dataTransfer.setData('text/plain', String(i))}
                onClick={() => choose(i)}
                aria-label={`Letter ${letterName(l.base, names)}`}
                className={`w-12 h-14 sm:w-14 sm:h-16 bg-white border-2 font-arabic text-2xl sm:text-3xl font-bold shadow-sm cursor-grab transition-transform ${
                  wrong === i ? 'border-rose-500 bg-rose-50 animate-[shake_0.3s]' : 'border-slate-300 hover:border-sky-600 hover:-translate-y-0.5'}`}>
                {l.base}{withMarks ? l.marks : ''}
              </button>
            );
          })}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
        <button type="button" onClick={() => play(word)} className="px-2.5 py-1 border border-slate-300 bg-white inline-flex items-center gap-1 hover:border-emerald-700">
          <Volume2 className="w-3.5 h-3.5" /> Hear the word
        </button>
        {!done && next && (
          <button type="button" onClick={() => play(next.marks.replace(/[ّْ]/g, '') ? `${next.base}${next.marks}` : letterName(next.base, names))}
            className="px-2.5 py-1 border border-slate-300 bg-white hover:border-emerald-700">
            Hint: hear the next letter
          </button>
        )}
        <button type="button" onClick={reset} className="px-2.5 py-1 border border-slate-300 bg-white inline-flex items-center gap-1 hover:border-slate-500">
          <RotateCcw className="w-3.5 h-3.5" /> Start again
        </button>
        {wrong !== null && <span role="status" className="text-rose-700 font-semibold">Not that one yet: look at the word again and find the next letter from the right.</span>}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------------------------
// Find the letter: spot a letter inside the joined word, where its shape has changed.
// ---------------------------------------------------------------------------------------------

/** The letter to look for: preferably one whose shape in the word differs from its shape on its own. */
function pickTarget(letters: SplitLetter[]): number {
  const usable = letters.map((l, i) => i).filter((i) => !letters[i].lamAlif && !(i > 0 && letters[i - 1].lamAlif));
  const changed = usable.filter((i) => letters[i].position !== 'isolated');
  const pool = changed.length ? changed : usable.length ? usable : letters.map((_, i) => i);
  return pool[Math.floor(Math.random() * pool.length)];
}

export const FindLetter: React.FC<GameProps> = ({ word, alphabet, onDone }) => {
  const letters = useMemo(() => splitWord(word).letters, [word]);
  const names = useMemo(() => new Map(alphabet.map((a) => [a.letter, a])), [alphabet]);
  const [target, setTarget] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [found, setFound] = useState(false);
  const [mistakes, setMistakes] = useState(0);
  const [tashkeelMode] = useTashkeel();
  const withMarks = tashkeelMode !== 'plain';

  const reset = () => { setTarget(pickTarget(letters)); setPicked(null); setFound(false); setMistakes(0); };
  useEffect(reset, [letters]);
  if (!letters.length) return null;

  const goal = letters[target];
  const tap = (i: number) => {
    if (found) return;
    setPicked(i);
    if (letters[i].base === goal.base) {
      setFound(true);
      play(`${letters[i].base}${letters[i].marks}`);
      onDone?.(mistakes === 0);
    } else {
      setMistakes((m) => m + 1);
    }
  };
  const times = letters.filter((l) => l.base === goal.base).length;
  const pickedLetter = picked !== null ? letters[picked] : null;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-center gap-3">
        <span className="text-sm text-slate-800">Tap the letter</span>
        <span className="font-arabic text-4xl font-black text-sky-800 border-2 border-sky-300 bg-white px-3 leading-[1.5]">{goal.base}</span>
        <span className="text-sm text-slate-800" dir="auto">({letterName(goal.base, names)}) in this word</span>
        <button type="button" onClick={() => play(names.get(goal.base)?.name || goal.base)} aria-label="Hear the letter's name"
          className="p-1.5 border border-slate-300 bg-white hover:border-emerald-700"><Volume2 className="w-4 h-4" /></button>
      </div>

      {/* The joined word; every letter can be tapped. */}
      <div className="flex justify-center" dir="rtl">
        <div className="flex items-end" role="group" aria-label={`The word ${word}`}>
          {letters.map((l, i) => {
            if (i > 0 && letters[i - 1].lamAlif) return null;  // drawn together with its ل as لا
            const shape = l.lamAlif
              ? `${l.joinsPrev ? '‍' : ''}${l.base}${withMarks ? l.marks : ''}${letters[i + 1].base}${withMarks ? letters[i + 1].marks : ''}`
              : shapedLetter(l, withMarks);
            const state = found && l.base === goal.base ? 'bg-emerald-200 text-emerald-900'
              : picked === i && !found ? 'bg-rose-200 text-rose-900' : 'text-slate-900 hover:bg-sky-100';
            return (
              <button key={i} type="button" onClick={() => tap(i)} aria-label={`Letter ${i + 1}`}
                className={`font-arabic font-bold text-5xl leading-[1.6] px-0 transition-colors ${state}`}>
                {shape}
              </button>
            );
          })}
        </div>
      </div>

      <div role="status" className="text-center text-xs min-h-[2.5rem]">
        {found ? (
          <p className="text-emerald-800 font-semibold inline-flex items-center gap-1 flex-wrap justify-center">
            <CheckCircle2 className="w-4 h-4" /> Yes! Here <bdi className="font-arabic text-base">{goal.base}</bdi>{' '}
            {goal.position === 'isolated'
              ? <>does not join the next letter, so it keeps its own shape</>
              : <>is {WHERE[goal.position]}, so it looks like{' '}
                <bdi className="font-arabic text-xl text-sky-800">{shapedLetter(goal, false)}</bdi></>}.
            {times > 1 && ` It appears ${times} times in this word.`}
          </p>
        ) : pickedLetter ? (
          <p className="text-rose-700 font-semibold">
            That is <bdi className="font-arabic text-base">{pickedLetter.base}</bdi> ({letterName(pickedLetter.base, names)}). Look again!
          </p>
        ) : (
          <p className="text-slate-600">Its shape may be different here from the letter on its own.</p>
        )}
      </div>
      {found && (
        <div className="flex justify-center">
          <button type="button" onClick={reset} className="px-2.5 py-1 text-xs border border-slate-300 bg-white inline-flex items-center gap-1 hover:border-slate-500">
            <RotateCcw className="w-3.5 h-3.5" /> Another letter
          </button>
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------------------------
// A round of games for a lesson: each example word in turn, building and finding letters.
// ---------------------------------------------------------------------------------------------

/** The lesson's words worth playing with: 2 to 7 letters, each once. */
export function gameWords(texts: string[], max = 6): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  texts.flatMap(wordsOf).forEach((w) => {
    const n = splitWord(w).letters.length;
    const key = stripTashkeel(w);
    if (n >= 2 && n <= 7 && !seen.has(key)) { seen.add(key); out.push(w); }
  });
  return out.slice(0, max);
}

export const LetterGamesRound: React.FC<{ texts: string[]; alphabet: AlphabetLetter[] }> = ({ texts, alphabet }) => {
  const words = useMemo(() => gameWords(texts), [texts]);
  // Each word is played as both games: build it, then find a letter in it.
  const rounds = useMemo(() => words.flatMap((w) => [{ word: w, game: 'build' as const }, { word: w, game: 'find' as const }]), [words]);
  const [index, setIndex] = useState(0);
  const [results, setResults] = useState<boolean[]>([]);
  const [roundKey, setRoundKey] = useState(0);
  if (!rounds.length) return null;

  const finished = index >= rounds.length;
  const current = rounds[Math.min(index, rounds.length - 1)];
  const answered = results.length > index;
  const record = (firstTry: boolean) => setResults((r) => (r.length > index ? r : [...r, firstTry]));
  const restart = () => { setIndex(0); setResults([]); setRoundKey((k) => k + 1); };
  const score = results.filter(Boolean).length;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <span className="font-bold text-slate-800">
          {finished ? 'All done!' : `${current.game === 'build' ? 'Build the word' : 'Find the letter'} · ${index + 1} of ${rounds.length}`}
        </span>
        <span className="text-slate-600">First-time right: {score} / {results.length}</span>
      </div>
      <div className="h-1.5 bg-slate-200"><div className="h-1.5 bg-sky-600 transition-all" style={{ width: `${(Math.min(index, rounds.length) / rounds.length) * 100}%` }} /></div>

      {finished ? (
        <div className="text-center space-y-2 py-3">
          <Trophy className="w-8 h-8 text-amber-500 mx-auto" />
          <p className="text-sm font-bold text-slate-900">You got {score} of {rounds.length} right the first time.</p>
          <p className="text-xs text-slate-600">{score === rounds.length ? 'Perfect! You can read how these letters join.' : 'Play again to beat your score.'}</p>
          <button type="button" onClick={restart} className="px-3 py-1.5 text-xs font-bold bg-sky-800 text-white inline-flex items-center gap-1.5">
            <RotateCcw className="w-3.5 h-3.5" /> Play again
          </button>
        </div>
      ) : (
        <>
          {current.game === 'build'
            ? <BuildWord key={`${roundKey}-${index}`} word={current.word} alphabet={alphabet} onDone={record} />
            : <FindLetter key={`${roundKey}-${index}`} word={current.word} alphabet={alphabet} onDone={record} />}
          <div className="flex justify-end">
            <button type="button" disabled={!answered} onClick={() => setIndex((i) => i + 1)}
              className="px-3 py-1.5 text-xs font-bold bg-emerald-900 text-white disabled:opacity-40">
              {index + 1 === rounds.length ? 'See my score' : 'Next'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};
