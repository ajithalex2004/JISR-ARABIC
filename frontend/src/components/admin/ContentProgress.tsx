import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

type Stage = 'published' | 'published_unsourced' | 'in_review' | 'ready_to_draft' | 'reading' | 'uploaded' | 'no_book';
type Cell = {
  grade: number;
  term: number;
  edition_id: string;
  uploaded: boolean;
  total_pages: number | null;
  pages_read: number;
  pages_failed: number;
  pages_curated: number;
  book_read: boolean;
  pdf_stored: boolean;
  reading_queued: boolean;
  draft_lesson_ids: string[];
  drafting_queued: boolean;
  lessons: { total: number; published: number; in_review: number; not_started: number; auto_generated: number; from_book: number; ai_drafts: number };
  stage: Stage;
};
type Progress = {
  summary: Record<Stage, number> & {
    lessons_published: number; lessons_total: number; lessons_auto_generated: number;
    books_missing: number; books_missing_list: string[]; books_unread: number; pages_failed: number; books_to_read: number;
    lessons_from_book: number; lessons_ai_drafts: number; terms_to_draft: number;
  };
  grades: { grade: number; terms: Cell[] }[];
};

const STAGES: Record<Stage, { label: string; className: string; next: string }> = {
  published: { label: 'Published from the book', className: 'bg-emerald-100 border-emerald-300 text-emerald-950', next: 'Learners can use every lesson.' },
  published_unsourced: { label: 'Published, not from the book', className: 'bg-amber-100 border-amber-400 text-amber-950', next: 'Draft the lessons from the book, then review and publish the drafts.' },
  in_review: { label: 'Drafts to review', className: 'bg-sky-50 border-sky-300 text-sky-950', next: 'Review and publish the drafts in Curriculum Review.' },
  ready_to_draft: { label: 'Ready to draft', className: 'bg-amber-50 border-amber-300 text-amber-950', next: 'Draft the lessons with AI in Curriculum Review.' },
  reading: { label: 'Reading pages', className: 'bg-amber-50 border-amber-300 text-amber-950', next: 'Re-upload the PDF in Upload & OCR to finish reading.' },
  uploaded: { label: 'Uploaded', className: 'bg-slate-50 border-slate-300 text-slate-800', next: 'Pages are not read yet: re-upload in Upload & OCR.' },
  no_book: { label: 'No book', className: 'bg-white border-slate-200 text-slate-400', next: 'Upload the textbook PDF in Upload & OCR.' },
};

function needsReading(cell: Cell) {
  return cell.pdf_stored && (cell.pages_failed > 0 || !cell.total_pages || cell.pages_read < cell.total_pages);
}

type Actions = { busy: boolean; onRead: (cell: Cell) => void; onDraft: (cell: Cell) => void };

function CellCard({ cell, busy, onRead, onDraft }: { cell: Cell } & Actions) {
  const stage = STAGES[cell.stage];
  const { lessons } = cell;
  const unread = cell.total_pages ? Math.max(0, cell.total_pages - cell.pages_read - cell.pages_failed) : 0;
  return <div className={`border p-2 text-xs space-y-0.5 ${stage.className}`} title={stage.next}>
    <div className="font-bold">{stage.label}</div>
    {!cell.uploaded && !cell.book_read && cell.stage !== 'no_book' && <div className="font-semibold">Book not uploaded</div>}
    {cell.stage !== 'no_book' && (cell.uploaded || cell.book_read) && <div>
      Pages read: {cell.pages_read + cell.pages_curated}{cell.total_pages ? ` / ${cell.total_pages}` : ''}
      {cell.pages_curated > 0 && <span className="opacity-75"> ({cell.pages_curated} hand-checked)</span>}
      {cell.pages_failed > 0 && <span className="text-red-700"> · {cell.pages_failed} failed</span>}
    </div>}
    {lessons.total > 0 && <div>
      Lessons: {lessons.published}/{lessons.total} published{lessons.in_review ? ` · ${lessons.in_review} to review` : ''}
    </div>}
    {lessons.total > 0 && <div className="font-semibold">From the book: {lessons.from_book}/{lessons.total} lessons</div>}
    {lessons.ai_drafts > 0 && <div className="text-sky-900">{lessons.ai_drafts} drafted from the book, waiting for review</div>}
    {lessons.auto_generated > 0 && <div className="text-amber-900">
      Students see {lessons.auto_generated} auto-generated (not teacher-reviewed)
    </div>}
    {cell.stage !== 'published' && cell.stage !== 'no_book' && <div className="opacity-75 italic">
      Next: {cell.stage === 'published_unsourced' && !cell.book_read ? 'Read the textbook pages, then draft from the book.' : stage.next}
    </div>}
    {cell.reading_queued && <div className="font-semibold text-sky-900">Reading pages… refresh to see progress</div>}
    {!cell.reading_queued && needsReading(cell) && <button type="button" disabled={busy} onClick={() => onRead(cell)}
      className="mt-1 mr-1 border border-slate-500 bg-white text-slate-900 px-2 py-0.5 font-semibold disabled:opacity-50">
      {cell.pages_read === 0 && cell.pages_failed === 0 ? 'Read pages'
        : `Read ${[cell.pages_failed && `${cell.pages_failed} failed`, unread && `${unread} unread`].filter(Boolean).join(' + ') || 'remaining'} pages`}
    </button>}
    {cell.drafting_queued && <div className="font-semibold text-sky-900">Drafting lessons… drafts appear in Curriculum Review</div>}
    {!cell.drafting_queued && cell.draft_lesson_ids.length > 0 && <button type="button" disabled={busy} onClick={() => onDraft(cell)}
      className="mt-1 border border-emerald-700 bg-white text-emerald-900 px-2 py-0.5 font-semibold disabled:opacity-50">
      Draft {cell.draft_lesson_ids.length} lesson{cell.draft_lesson_ids.length === 1 ? '' : 's'} from the book
    </button>}
  </div>;
}

export function ContentProgress() {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    setError('');
    try { setProgress(await api.adminContentProgress()); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  const read = async (cell?: Cell) => {
    setBusy(true); setError(''); setNotice('');
    try {
      const res = await api.adminReadTextbookPages(cell?.edition_id);
      const count = cell ? 1 : res.queued.length;
      setNotice(count
        ? `Reading started for ${cell ? `Grade ${cell.grade} Term ${cell.term}` : `${count} book${count === 1 ? '' : 's'}`}. Books are read one after another; pages already read are skipped.`
        : 'No uploaded book has pages left to read.');
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setBusy(false); }
  };

  const draft = async (cell?: Cell) => {
    setBusy(true); setError(''); setNotice('');
    try {
      const res = await api.adminDraftFromBook(cell ? { grade: cell.grade, term: cell.term } : undefined);
      const lessons = res.queued.reduce((n: number, q: { lessons: number }) => n + q.lessons, 0);
      setNotice(res.queued.length
        ? `AI is drafting ${lessons} lesson${lessons === 1 ? '' : 's'} from the book${cell ? ` for Grade ${cell.grade} Term ${cell.term}` : ''}. Drafts appear in Curriculum Review; learners keep the current lessons until you publish a draft.`
        : 'No term has lessons left to draft from a read book.');
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setBusy(false); }
  };

  const s = progress?.summary;
  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Content progress</h2>
      <div className="flex flex-wrap gap-2">
        {s && s.books_to_read > 0 && <button type="button" disabled={busy} onClick={() => read()}
          className="border border-emerald-700 bg-emerald-700 text-white px-3 py-1.5 text-sm font-semibold disabled:opacity-50">
          Read all uploaded books ({s.books_to_read})
        </button>}
        {s && s.terms_to_draft > 0 && <button type="button" disabled={busy} onClick={() => draft()}
          className="border border-sky-800 bg-sky-800 text-white px-3 py-1.5 text-sm font-semibold disabled:opacity-50">
          Draft all read books ({s.terms_to_draft} term{s.terms_to_draft === 1 ? '' : 's'})
        </button>}
        <button type="button" onClick={load} className="border border-slate-400 px-3 py-1.5 text-sm">Refresh</button>
      </div>
    </div>
    <p className="text-sm text-slate-600">
      Each textbook goes through: upload the PDF → pages are read → AI drafts the lessons → you review and publish.
    </p>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {notice && <p role="status" className="text-sm border border-sky-300 bg-sky-50 text-sky-950 p-3">{notice}</p>}
    {s && <div className="grid gap-2 grid-cols-2 sm:grid-cols-3 text-sm">
      <div className="border border-emerald-300 bg-emerald-50 p-3"><div className="text-xs text-slate-500">Terms published from the book</div><div className="text-lg font-bold">{s.published} / 36</div></div>
      <div className="border border-amber-400 bg-amber-50 p-3"><div className="text-xs text-slate-500">Published, not from the book</div><div className="text-lg font-bold">{s.published_unsourced}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Lessons from the book</div><div className="text-lg font-bold">{s.lessons_from_book} / {s.lessons_total}</div>
        {s.lessons_ai_drafts > 0 && <div className="text-xs text-sky-900">{s.lessons_ai_drafts} drafts waiting for review</div>}</div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Books not uploaded</div><div className="text-lg font-bold">{s.books_missing}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Books uploaded, pages not read</div><div className="text-lg font-bold">{s.books_unread}</div></div>
      <div className={`border p-3 ${s.pages_failed ? 'border-red-300 bg-red-50' : 'border-slate-200 bg-slate-50'}`}><div className="text-xs text-slate-500">Pages that failed to read</div><div className="text-lg font-bold">{s.pages_failed}</div></div>
    </div>}
    {s && s.published_unsourced > 0 && <p className="text-sm border border-amber-400 bg-amber-50 text-amber-950 p-3">
      <strong>{s.published_unsourced} terms</strong> have published lessons that were not drafted from their textbook.
      Those lessons were built from the syllabus, not matched to the Ministry book. Read each book's pages,
      then draft from the book: learners keep the current lessons until a teacher publishes the new draft.
    </p>}
    {s && s.books_missing > 0 && <details className="text-sm border border-slate-200 p-3">
      <summary className="cursor-pointer font-semibold text-slate-800">Textbooks still to upload ({s.books_missing})</summary>
      <p className="mt-2 text-slate-600">{s.books_missing_list.join(' · ')}</p>
    </details>}
    {s && s.lessons_auto_generated > 0 && <p className="text-sm border border-amber-300 bg-amber-50 text-amber-950 p-3">
      <strong>{s.lessons_auto_generated} of {s.lessons_total} lessons</strong> are shown to students as auto-generated content
      that no teacher has reviewed yet. Publishing a reviewed version in Curriculum Review replaces it.
    </p>}
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
            {row.terms.map(cell => <td key={cell.term} className="py-1 px-1 align-top"><CellCard cell={cell} busy={busy} onRead={read} onDraft={draft} /></td>)}
          </tr>)}
        </tbody>
      </table>
    </div>}
  </section>;
}
