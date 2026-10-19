import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { BookOpen, Sparkles, Volume2, X } from 'lucide-react';
import { audioManager } from '../../services/audio';
import { fetchRootFamily, RootFamily, segmentRootLetters } from '../../services/roots';

interface RootTreeExplorerProps {
  /** The root as written on the vocabulary card, e.g. "ك-ت-ب". */
  root: string;
  /** The card's word, so the server can use the catalogue's corrected root. */
  word?: string;
  onClose: () => void;
}

const KIND_LABELS: Record<string, string> = {
  verb: 'Verb',
  noun: 'Noun',
  adjective: 'Describing word',
  doer: 'The one who does it',
  object: 'The thing it is done to',
  place: 'Place',
  instrument: 'Tool',
  plural: 'Plural',
  other: 'Related word',
};

/** A word with its root letters coloured, so the shared letters stand out across the family. */
const RootWord: React.FC<{ word: string; root: string | null; tone: 'emerald' | 'violet' }> = ({ word, root, tone }) => (
  <span className="font-arabic text-2xl font-bold text-slate-900 leading-snug" dir="rtl" lang="ar">
    {segmentRootLetters(word, root).map((seg, i) =>
      seg.isRoot ? (
        <span key={i} className={tone === 'emerald' ? 'text-emerald-600' : 'text-violet-600'}>
          {seg.text}
        </span>
      ) : (
        <React.Fragment key={i}>{seg.text}</React.Fragment>
      )
    )}
  </span>
);

const Branch: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <li className="relative pr-8">
    {/* Twig from the trunk on the right to the card */}
    <span aria-hidden className="absolute right-3 top-1/2 h-0.5 w-5 bg-amber-300" />
    {children}
  </li>
);

/**
 * The Root Tree Explorer: the root's letters as a trunk, with branches for the words
 * the learner met in their lessons and more words from the same family.
 */
export const RootTreeExplorer: React.FC<RootTreeExplorerProps> = ({ root, word, onClose }) => {
  const [family, setFamily] = useState<RootFamily | null>(null);
  const [error, setError] = useState(false);
  const [selectedRoot, setSelectedRoot] = useState(root);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    let cancelled = false;
    setFamily(null);
    setError(false);
    fetchRootFamily(selectedRoot, word)
      .then((data) => { if (!cancelled) setFamily(data); })
      .catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [selectedRoot, word]);

  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onCloseRef.current(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const shownRoot = family?.root ?? null;

  return createPortal(
    <div
      className="fixed inset-0 z-[1000] flex items-end sm:items-center justify-center bg-slate-950/60 backdrop-blur-sm p-0 sm:p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="root-tree-title"
        className="w-full sm:max-w-2xl max-h-[92vh] overflow-y-auto bg-white border border-slate-300 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between gap-3 bg-[#2A1548] text-white px-4 py-3">
          <div>
            <h2 id="root-tree-title" className="font-bold text-base leading-tight">
              Root Tree Explorer · <span className="font-arabic" lang="ar">شَجَرَةُ الجَذْرِ</span>
            </h2>
            <p className="text-[11px] text-purple-200">Arabic words grow from three-letter roots. Words that share a root share a meaning.</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="p-2 hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-amber-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 sm:p-6">
          {error && (
            <p className="text-sm text-rose-700 bg-rose-50 border border-rose-200 p-3">
              We couldn't load this root family. Check your connection and try again.
            </p>
          )}

          {!error && !family && (
            <div className="space-y-3 animate-pulse" aria-label="Loading">
              <div className="mx-auto h-16 w-56 bg-slate-200" />
              <div className="h-16 bg-slate-100" />
              <div className="h-16 bg-slate-100" />
            </div>
          )}

          {family?.borrowed && (
            <div className="border border-amber-300 bg-amber-50 p-4 space-y-2">
              <div className="font-arabic text-3xl font-bold text-slate-900 text-center" dir="rtl" lang="ar">{word}</div>
              <p className="text-sm font-bold text-amber-900">Borrowed word: no Arabic root</p>
              <p className="text-sm text-slate-700">{family.note_en}</p>
              <p className="text-xs text-slate-500">
                Arabic borrows names for new things from other languages, just like English borrows words from Arabic
                (sugar from سُكَّر, coffee from قَهْوَة).
              </p>
            </div>
          )}

          {family && !family.borrowed && (
            <div className="space-y-6">
              {family.roots.length > 1 && (
                <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
                  <span className="text-slate-500">This word joins two roots:</span>
                  {family.roots.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setSelectedRoot(r)}
                      aria-pressed={r === shownRoot}
                      className={`px-3 py-1 font-arabic text-sm border ${
                        r === shownRoot ? 'bg-[#2A1548] text-white border-[#2A1548]' : 'bg-white text-slate-700 border-slate-300 hover:border-[#2A1548]'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              )}

              {/* Trunk: the root letters */}
              <div className="text-center">
                <div className="inline-flex gap-2" dir="rtl" lang="ar" aria-label={`Root ${shownRoot}`}>
                  {family.letters.map((letter, i) => (
                    <span
                      key={i}
                      className="w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center bg-[#2A1548] text-amber-300 font-arabic text-3xl sm:text-4xl font-bold shadow-md"
                    >
                      {letter}
                    </span>
                  ))}
                </div>
                {family.core_meaning_en && (
                  <p className="mt-2 text-sm text-slate-700">
                    Core idea: <strong className="text-slate-900">{family.core_meaning_en}</strong>
                  </p>
                )}
                {family.note_en && <p className="mt-1 text-xs text-slate-500">{family.note_en}</p>}
              </div>

              {/* Branches */}
              <div className="relative">
                <span aria-hidden className="absolute right-3 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-400 via-amber-300 to-amber-100" />

                {family.curriculum_words.length > 0 && (
                  <section className="mb-6">
                    <h3 className="pr-8 mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-emerald-800">
                      <BookOpen className="w-3.5 h-3.5" /> In your lessons
                    </h3>
                    <ul className="space-y-2">
                      {family.curriculum_words.map((w, i) => (
                        <Branch key={`${w.lesson_id}-${i}`}>
                          <button
                            type="button"
                            onClick={() => audioManager.playArabic(w.word_ar)}
                            className="w-full text-left flex items-center justify-between gap-3 border border-emerald-200 bg-emerald-50/60 hover:border-emerald-500 px-3 py-2"
                          >
                            <span className="min-w-0">
                              <span className="block text-sm font-bold text-slate-900">{w.meaning_en}</span>
                              <span className="block text-[11px] text-emerald-800">
                                {w.grade ? `Class ${w.grade} · ` : ''}{w.term ? `Term ${w.term} · ` : ''}{w.lesson_title_en}
                              </span>
                            </span>
                            <span className="flex items-center gap-2 shrink-0">
                              <RootWord word={w.word_ar} root={shownRoot} tone="emerald" />
                              <Volume2 className="w-4 h-4 text-emerald-700" aria-label="Listen" />
                            </span>
                          </button>
                        </Branch>
                      ))}
                    </ul>
                  </section>
                )}

                {family.family.length > 0 && (
                  <section>
                    <h3 className="pr-8 mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-violet-800">
                      <Sparkles className="w-3.5 h-3.5" /> More words from this root
                    </h3>
                    <ul className="space-y-2">
                      {family.family.map((w) => (
                        <Branch key={w.word_ar}>
                          <button
                            type="button"
                            onClick={() => audioManager.playArabic(w.word_ar)}
                            className="w-full text-left flex items-center justify-between gap-3 border border-violet-200 bg-violet-50/50 hover:border-violet-500 px-3 py-2"
                          >
                            <span className="min-w-0">
                              <span className="block text-sm font-bold text-slate-900">{w.meaning_en}</span>
                              <span className="block text-[11px] text-violet-800">
                                {KIND_LABELS[w.kind] || KIND_LABELS.other}
                                {w.pattern && (
                                  <> · pattern <span className="font-arabic text-xs" lang="ar">{w.pattern}</span></>
                                )}
                              </span>
                            </span>
                            <span className="flex items-center gap-2 shrink-0">
                              <RootWord word={w.word_ar} root={shownRoot} tone="violet" />
                              <Volume2 className="w-4 h-4 text-violet-700" aria-label="Listen" />
                            </span>
                          </button>
                        </Branch>
                      ))}
                    </ul>
                    <p className="pr-8 mt-2 text-[11px] text-slate-500">
                      Suggested by AI and checked to contain the root letters. Not yet reviewed by a teacher.
                    </p>
                  </section>
                )}

                {family.family_source === 'unavailable' && (
                  <p className="pr-8 text-xs text-slate-500">More words from this root will appear here soon.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
};
