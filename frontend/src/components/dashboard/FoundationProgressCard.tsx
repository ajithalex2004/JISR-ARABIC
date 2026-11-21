import React, { useEffect, useState } from 'react';
import { ArrowRight, Blocks, CheckCircle2 } from 'lucide-react';
import { api } from '../../services/api';

type CourseLesson = { id: string; title_en: string; title_ar: string };
type CourseStage = { id: string; title_en: string; title_ar: string; lessons: CourseLesson[] };
type Item = { lesson_id: string; completed_at: string | null };

interface Props {
  childId: string;
  childName?: string;
  onOpenFoundation?: () => void;
}

const formatDate = (iso: string | null) => {
  if (!iso) return '';
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : `${iso}Z`);
  return isNaN(d.getTime()) ? '' : d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
};

/** The child's Basic Foundation of Arabic progress (kept on their account), for the Parent Dashboard. */
export const FoundationProgressCard: React.FC<Props> = ({ childId, childName, onOpenFoundation }) => {
  const [stages, setStages] = useState<CourseStage[] | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setError('');
    Promise.all([api.getFoundation(), api.getFoundationProgress(childId)])
      .then(([course, progress]) => {
        if (cancelled) return;
        setStages(course.stages || []);
        setItems(Array.isArray(progress.items) ? progress.items
          : (progress.completed || []).map((id: string) => ({ lesson_id: id, completed_at: null })));
      })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : 'Foundation progress could not be loaded.'); });
    return () => { cancelled = true; };
  }, [childId]);

  const who = childName || 'Your child';
  if (error) {
    return <div className="sharp-card p-5 border border-slate-300 bg-white text-sm text-slate-600">Basic Foundation of Arabic: {error}</div>;
  }
  if (!stages) {
    return <div className="sharp-card p-5 border border-slate-300 bg-white text-sm text-slate-500">Loading Foundation progress…</div>;
  }

  const lessons = stages.flatMap((s) => s.lessons.map((l) => ({ ...l, stage: s.id })));
  const done = new Set(items.map((i) => i.lesson_id));
  const doneCount = lessons.filter((l) => done.has(l.id)).length;
  const pct = lessons.length ? Math.round((doneCount / lessons.length) * 100) : 0;
  const byId = new Map(lessons.map((l) => [l.id, l]));
  const recent = items.filter((i) => byId.has(i.lesson_id)).slice(-3).reverse();
  const next = lessons.find((l) => !done.has(l.id));

  return (
    <div className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
      <div className="border-b border-slate-200 pb-2 flex flex-wrap justify-between items-start gap-3">
        <div>
          <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight flex items-center gap-1.5">
            <Blocks className="w-4 h-4 text-emerald-800" /> Basic Foundation of Arabic
          </h2>
          <p className="text-xs text-slate-500">
            {doneCount === 0
              ? `${who} hasn't started the free Foundation course yet: letters, reading rules, first grammar and everyday Arabic.`
              : `${who} has finished ${doneCount} of ${lessons.length} lessons. Saved to the account, on every device.`}
          </p>
        </div>
        {onOpenFoundation && (
          <button type="button" onClick={onOpenFoundation}
            className="px-3 py-1.5 text-xs font-bold bg-emerald-900 text-white inline-flex items-center gap-1.5">
            {doneCount === 0 ? 'Start the course' : 'Open Foundation'} <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div>
        <div className="flex justify-between text-xs font-bold text-slate-700">
          <span>Overall</span><span>{doneCount} / {lessons.length} lessons · {pct}%</span>
        </div>
        <div className="h-2.5 bg-slate-100 mt-1" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Foundation progress">
          <div className="h-2.5 bg-emerald-700" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
        {stages.map((s) => {
          const n = s.lessons.filter((l) => done.has(l.id)).length;
          const sp = s.lessons.length ? Math.round((n / s.lessons.length) * 100) : 0;
          return (
            <div key={s.id} className="p-2 border border-slate-200 bg-slate-50">
              <div className="flex justify-between items-baseline">
                <span className="text-xs font-black text-slate-900">Stage {s.id}</span>
                <span className="text-[11px] font-bold text-slate-600">{n}/{s.lessons.length}</span>
              </div>
              <div className="text-[11px] text-slate-600 truncate" title={s.title_en}>{s.title_en}</div>
              <div className="h-1.5 bg-slate-200 mt-1"><div className="h-1.5 bg-emerald-600" style={{ width: `${sp}%` }} /></div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div>
          <div className="font-bold text-slate-700 mb-1">Recently finished</div>
          {recent.length === 0 ? <p className="text-slate-500">Nothing yet.</p> : (
            <ul className="space-y-1">
              {recent.map((i) => {
                const l = byId.get(i.lesson_id)!;
                return (
                  <li key={i.lesson_id} className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                    <span className="text-slate-800">{l.stage}. {l.title_en}</span>
                    {i.completed_at && <span className="text-slate-500">· {formatDate(i.completed_at)}</span>}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        <div>
          <div className="font-bold text-slate-700 mb-1">Next up</div>
          {next ? (
            <p className="text-slate-800">
              Stage {next.stage}: {next.title_en} <bdi className="font-arabic text-slate-600" dir="rtl">({next.title_ar})</bdi>
            </p>
          ) : <p className="text-emerald-800 font-bold">🎉 The whole Foundation course is finished.</p>}
        </div>
      </div>
    </div>
  );
};
