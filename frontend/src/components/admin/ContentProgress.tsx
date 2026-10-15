import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

type Stage = 'published' | 'in_review' | 'ready_to_draft' | 'reading' | 'uploaded' | 'no_book';
type Cell = {
  grade: number;
  term: number;
  edition_id: string;
  uploaded: boolean;
  total_pages: number | null;
  pages_read: number;
  pages_failed: number;
  lessons: { total: number; published: number; in_review: number; not_started: number };
  stage: Stage;
};
type Progress = {
  summary: Record<Stage, number> & { lessons_published: number; lessons_total: number };
  grades: { grade: number; terms: Cell[] }[];
};

const STAGES: Record<Stage, { label: string; className: string; next: string }> = {
  published: { label: 'Published', className: 'bg-emerald-100 border-emerald-300 text-emerald-950', next: 'Learners can use every lesson.' },
  in_review: { label: 'Drafts to review', className: 'bg-sky-50 border-sky-300 text-sky-950', next: 'Review and publish the drafts in Curriculum Review.' },
  ready_to_draft: { label: 'Ready to draft', className: 'bg-amber-50 border-amber-300 text-amber-950', next: 'Draft the lessons with AI in Curriculum Review.' },
  reading: { label: 'Reading pages', className: 'bg-amber-50 border-amber-300 text-amber-950', next: 'Re-upload the PDF in Upload & OCR to finish reading.' },
  uploaded: { label: 'Uploaded', className: 'bg-slate-50 border-slate-300 text-slate-800', next: 'Pages are not read yet: re-upload in Upload & OCR.' },
  no_book: { label: 'No book', className: 'bg-white border-slate-200 text-slate-400', next: 'Upload the textbook PDF in Upload & OCR.' },
};

function CellCard({ cell }: { cell: Cell }) {
  const stage = STAGES[cell.stage];
  const { lessons } = cell;
  return <div className={`border p-2 text-xs space-y-0.5 ${stage.className}`} title={stage.next}>
    <div className="font-bold">{stage.label}</div>
    {cell.stage !== 'no_book' && <div>
      Pages read: {cell.pages_read}{cell.total_pages ? ` / ${cell.total_pages}` : ''}
      {cell.pages_failed > 0 && <span className="text-red-700"> · {cell.pages_failed} failed</span>}
    </div>}
    {lessons.total > 0 && <div>
      Lessons: {lessons.published}/{lessons.total} published{lessons.in_review ? ` · ${lessons.in_review} to review` : ''}
    </div>}
    {cell.stage !== 'published' && cell.stage !== 'no_book' && <div className="opacity-75 italic">Next: {stage.next}</div>}
  </div>;
}

export function ContentProgress() {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState('');

  const load = async () => {
    setError('');
    try { setProgress(await api.adminContentProgress()); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  const s = progress?.summary;
  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Content progress</h2>
      <button type="button" onClick={load} className="border border-slate-400 px-3 py-1.5 text-sm">Refresh</button>
    </div>
    <p className="text-sm text-slate-600">
      Each textbook goes through: upload the PDF → pages are read → AI drafts the lessons → you review and publish.
    </p>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {s && <div className="grid gap-2 grid-cols-2 sm:grid-cols-4 text-sm">
      <div className="border border-emerald-300 bg-emerald-50 p-3"><div className="text-xs text-slate-500">Terms fully published</div><div className="text-lg font-bold">{s.published} / 36</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Lessons published</div><div className="text-lg font-bold">{s.lessons_published} / {s.lessons_total}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Terms in progress</div><div className="text-lg font-bold">{s.in_review + s.ready_to_draft + s.reading + s.uploaded}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Books not uploaded</div><div className="text-lg font-bold">{s.no_book}</div></div>
    </div>}
    {progress && <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse min-w-[640px] table-fixed">
        <thead>
          <tr className="text-left text-xs text-slate-500">
            <th className="py-1 pr-2 w-20">Grade</th>
            <th className="py-1 px-1">Term 1</th>
            <th className="py-1 px-1">Term 2</th>
            <th className="py-1 px-1">Term 3</th>
          </tr>
        </thead>
        <tbody>
          {progress.grades.map(row => <tr key={row.grade}>
            <td className="py-1 pr-2 font-semibold text-slate-800 align-top">Grade {row.grade}</td>
            {row.terms.map(cell => <td key={cell.term} className="py-1 px-1 align-top"><CellCard cell={cell} /></td>)}
          </tr>)}
        </tbody>
      </table>
    </div>}
  </section>;
}
