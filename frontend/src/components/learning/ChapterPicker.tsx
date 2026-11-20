import React, { useEffect, useState } from 'react';
import { Lock } from 'lucide-react';
import { api } from '../../services/api';
import { LessonSummary, TermSummary } from '../../types';

/** A grade's Chapter 1 lesson id (Grade 5 uses its own lesson ids). */
export const firstChapterId = (grade: number) => (grade === 5 ? 'lesson_01_ball_games' : `lesson_g${grade}_t1_ch01`);

export const isOpenableChapter = (c: LessonSummary) => c.is_accessible && !c.coming_soon && c.status !== 'coming_soon';

export interface ChapterPickerState {
  terms: TermSummary[];
  selectedTerm: number;
  setSelectedTerm: (term: number) => void;
  chapters: LessonSummary[];
  selectedLessonId: string;
  setSelectedLessonId: (id: string) => void;
}

/**
 * Term and chapter selection with the same term/chapter lists (and lock states) as Curriculum &
 * Lessons. Changing grade goes back to Term 1, Chapter 1; changing term opens that term's first
 * chapter the learner can open ('' when there is none).
 */
export function useChapterPicker(grade: number, childId?: string, enabled = true): ChapterPickerState {
  const [terms, setTerms] = useState<TermSummary[]>([]);
  const [selectedTerm, setSelectedTerm] = useState<number>(1);
  const [chapters, setChapters] = useState<LessonSummary[]>([]);
  const [selectedLessonId, setSelectedLessonId] = useState<string>(() => firstChapterId(grade));

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    setSelectedTerm(1);
    setSelectedLessonId(firstChapterId(grade));
    api.getTerms(grade, childId)
      .then((list) => { if (!cancelled) setTerms(Array.isArray(list) ? list : []); })
      .catch(() => { if (!cancelled) setTerms([]); });
    return () => { cancelled = true; };
  }, [grade, childId, enabled]);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    api.getLessons(grade, selectedTerm, childId)
      .then((list) => {
        if (cancelled) return;
        const rows = Array.isArray(list) ? [...list].sort((a, b) => a.lesson_order - b.lesson_order) : [];
        setChapters(rows);
        // Keep the open chapter if it is in this term; otherwise open the term's first available chapter.
        setSelectedLessonId((current) => (rows.some((c) => c.id === current && isOpenableChapter(c))
          ? current
          : (rows.find(isOpenableChapter)?.id ?? '')));
      })
      .catch(() => { if (!cancelled) setChapters([]); });
    return () => { cancelled = true; };
  }, [grade, selectedTerm, childId, enabled]);

  return { terms, selectedTerm, setSelectedTerm, chapters, selectedLessonId, setSelectedLessonId };
}

interface ChapterPickerProps {
  picker: ChapterPickerState;
  /** The chapter shown as selected (defaults to the picker's own selection). */
  activeId?: string;
  loading?: boolean;
  className?: string;
}

/** The term bar and the scrollable row of chapter cards (locked and coming-soon ones disabled). */
export const ChapterPicker: React.FC<ChapterPickerProps> = ({ picker, activeId, loading, className = '' }) => {
  const { terms, selectedTerm, setSelectedTerm, chapters, setSelectedLessonId } = picker;
  const current = activeId ?? picker.selectedLessonId;
  return (
    <div className={`bg-white border border-slate-200 p-3 rounded-sm shadow-2xs space-y-2.5 ${className}`}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-bold text-slate-800">الفصل الدراسي (Term):</span>
        {(terms.length ? terms.map((t) => t.term) : [1, 2, 3]).map((t) => {
          const info = terms.find((x) => x.term === t);
          return (
            <button
              key={t}
              type="button"
              aria-pressed={selectedTerm === t}
              onClick={() => setSelectedTerm(t)}
              className={`px-3 py-1 rounded-sm text-xs font-bold transition-all flex items-center gap-1 ${
                selectedTerm === t ? 'bg-emerald-800 text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {info && !info.is_unlocked && <Lock className="w-3 h-3" aria-label="locked" />}
              الفصل {t} (Term {t})
            </button>
          );
        })}
        {loading && <span className="text-[11px] text-slate-500">جَارٍ التَّحْمِيلُ… · Loading…</span>}
      </div>
      <div>
        <span className="text-xs font-bold text-slate-800 block mb-1.5">الدرس (Chapter):</span>
        <div className="flex gap-2 overflow-x-auto pb-1" role="list">
          {chapters.map((c, idx) => {
            const open = isOpenableChapter(c);
            const comingSoon = c.coming_soon || c.status === 'coming_soon';
            const active = c.id === current;
            return (
              <button
                key={c.id}
                type="button"
                role="listitem"
                disabled={!open}
                aria-current={active ? 'true' : undefined}
                title={!open ? (comingSoon ? 'Coming soon' : (c.lock_reason || 'Locked: unlock this term to open it')) : c.title_en}
                onClick={() => open && setSelectedLessonId(c.id)}
                className={`shrink-0 text-right px-3 py-2 border-2 rounded-sm transition-all min-w-[9rem] ${
                  active
                    ? 'bg-emerald-800 border-emerald-900 text-white'
                    : open
                      ? 'bg-emerald-50 border-emerald-200 text-slate-900 hover:bg-emerald-100'
                      : 'bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed'
                }`}
              >
                <span className="flex items-center justify-between gap-2 text-[10px] font-bold">
                  <span>{idx + 1}</span>
                  {!open && (comingSoon ? <span>Coming soon</span> : <Lock className="w-3 h-3" aria-label="locked" />)}
                </span>
                <span className="block text-sm font-black font-arabic leading-snug" dir="rtl">{c.title_ar}</span>
                <span className={`block text-[10px] ${active ? 'text-emerald-100' : 'text-slate-500'}`}>{c.title_en}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
