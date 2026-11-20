import React, { useEffect, useRef, useState } from 'react';
import { CheckCircle2, Eye, Loader2, Sparkles, X } from 'lucide-react';
import { api } from '../../services/api';
import { MalazimViewer } from '../learning/MalazimViewer';

type DraftSummary = {
  id: string;
  status: 'draft' | 'published' | 'rejected' | 'superseded';
  model?: string | null;
  cost_usd?: number | null;
  created_at?: string | null;
  reviewed_at?: string | null;
  review_note?: string | null;
};
type Chapter = {
  lesson_id: string;
  lesson_order: number;
  title_ar: string;
  title_en: string;
  has_lesson_content: boolean;
  booklet_source: 'hand_written' | 'published' | 'generated';
  published_draft_id: string | null;
  pending_draft_id: string | null;
  latest: DraftSummary | null;
};
type DraftDetail = DraftSummary & { lesson_id: string; grade: number; term: number; unvowelled_words: string[]; booklet: any };

const GRADES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

function sourceLabel(c: Chapter) {
  if (c.booklet_source === 'hand_written') return { text: 'Hand-written', cls: 'bg-sky-100 text-sky-900' };
  if (c.booklet_source === 'published') return { text: 'Full booklet live', cls: 'bg-emerald-100 text-emerald-900' };
  if (c.pending_draft_id) return { text: 'Draft waiting for review', cls: 'bg-amber-100 text-amber-900' };
  if (!c.has_lesson_content) return { text: 'No lesson published yet', cls: 'bg-slate-100 text-slate-600' };
  return { text: 'Basic booklet only', cls: 'bg-slate-100 text-slate-700' };
}

/**
 * Smart Study Booklets for every chapter. The AI writes each booklet from the chapter's published
 * lesson, in the format and depth of the hand-written Grade 5 Chapter 1 booklet. Learners see a
 * written booklet only after it is published here.
 */
export function BookletsAdmin() {
  const [grade, setGrade] = useState(5);
  const [term, setTerm] = useState(1);
  const [chapters, setChapters] = useState<Chapter[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [draft, setDraft] = useState<DraftDetail | null>(null);
  const [note, setNote] = useState('');
  const polling = useRef(0);

  const load = async () => {
    setError('');
    try {
      const res = await api.getBooklets(grade, term);
      setChapters(res.chapters);
    } catch (e: any) { setError(e.message); }
  };
  useEffect(() => { setChapters(null); setDraft(null); load(); }, [grade, term]);
  useEffect(() => () => { polling.current += 1; }, []);

  const poll = async (taskId: string, run: number) => {
    if (run !== polling.current) return;
    try {
      const task = await api.getTask(taskId);
      if (task.status === 'completed' || task.status === 'succeeded') {
        const s = task.result?.summary || {};
        setBusy(false);
        const cost = s.cost_usd ? ` AI cost about $${Number(s.cost_usd).toFixed(2)}.` : '';
        setMessage(`Finished: ${s.written ?? 0} written, ${s.skipped ?? 0} skipped, ${s.failed ?? 0} failed.${cost} Review and publish each draft below.`);
        const failed = (task.result?.lessons || []).filter((l: any) => l.status === 'failed');
        if (failed.length) setError(failed.map((l: any) => `${l.lesson_id}: ${l.detail}`).join('\n'));
        load();
      } else if (task.status === 'failed') {
        setBusy(false);
        setError(`Writing failed: ${task.error || 'unknown error'}`);
        load();
      } else {
        setMessage(`Writing booklets with AI from the published lessons (${task.progress || 0}%)… about a minute per chapter.`);
        setTimeout(() => poll(taskId, run), 4000);
      }
    } catch (e: any) {
      setBusy(false);
      setError(e.message);
    }
  };

  const write = async (lessonIds?: string[], overwrite = false) => {
    setBusy(true);
    setError('');
    setMessage('Queuing…');
    try {
      const { task_id } = await api.writeBooklets(grade, term, lessonIds, overwrite);
      polling.current += 1;
      poll(task_id, polling.current);
    } catch (e: any) {
      setBusy(false);
      setMessage('');
      setError(e.message);
    }
  };

  const open = async (draftId: string) => {
    setError('');
    try {
      const detail = await api.getBookletDraft(draftId);
      setDraft(detail);
      setNote(detail.review_note || '');
    } catch (e: any) { setError(e.message); }
  };

  const review = async (action: 'publish' | 'unpublish' | 'reject') => {
    if (!draft) return;
    if (action === 'reject' && !window.confirm('Reject this draft? Learners keep their current booklet.')) return;
    setError('');
    try {
      const detail = await api.reviewBookletDraft(draft.id, action, note);
      setDraft(detail);
      setMessage(action === 'publish' ? 'Published: learners now see this booklet.'
        : action === 'unpublish' ? 'Unpublished: learners see the basic booklet again.'
        : 'Draft rejected.');
      load();
    } catch (e: any) { setError(e.message); }
  };

  const writable = (chapters || []).filter(c => c.booklet_source !== 'hand_written' && c.has_lesson_content);
  const todo = writable.filter(c => !c.published_draft_id && !c.pending_draft_id);

  return <div className="space-y-4">
    <div className="bg-white border border-slate-200 p-4 space-y-3">
      <div>
        <h2 className="text-base font-black text-emerald-950 flex items-center gap-1.5"><Sparkles className="w-4 h-4" /> Smart Study Booklets</h2>
        <p className="text-xs text-slate-600 max-w-3xl">
          The AI writes each chapter's booklet from that chapter's published lesson, in the same format and depth as the
          hand-written Grade 5 Chapter 1 booklet (study sections with exercises, quick notes, flashcards, grammar and exam pitfalls),
          with full tashkeel. Nothing reaches learners until you publish it.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-xs font-bold text-slate-700">Grade
          <select value={grade} onChange={e => setGrade(Number(e.target.value))} className="ml-1.5 border border-slate-300 px-2 py-1 text-sm">
            {GRADES.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
        <label className="text-xs font-bold text-slate-700">Term
          <select value={term} onChange={e => setTerm(Number(e.target.value))} className="ml-1.5 border border-slate-300 px-2 py-1 text-sm">
            {[1, 2, 3].map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <button
          type="button"
          disabled={busy || !todo.length}
          onClick={() => write()}
          className="px-3 py-1.5 text-xs font-bold bg-emerald-900 hover:bg-emerald-950 text-white disabled:opacity-50 flex items-center gap-1.5"
        >
          {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          {todo.length
            ? `Write ${todo.length} missing booklet${todo.length === 1 ? '' : 's'} for Grade ${grade} Term ${term}`
            : `No booklets left to write for Grade ${grade} Term ${term}`}
        </button>
      </div>
      {message && <p className="text-xs text-emerald-900 bg-emerald-50 border border-emerald-200 px-3 py-2">{message}</p>}
      {error && <p role="alert" className="text-xs text-red-800 bg-red-50 border border-red-200 px-3 py-2 whitespace-pre-wrap">{error}</p>}
    </div>

    <div className="bg-white border border-slate-200 overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-xs text-slate-600 text-left">
          <tr><th className="px-3 py-2">#</th><th className="px-3 py-2">Chapter</th><th className="px-3 py-2">Booklet</th><th className="px-3 py-2 text-right">Actions</th></tr>
        </thead>
        <tbody>
          {chapters === null && <tr><td colSpan={4} className="px-3 py-4 text-slate-500">Loading…</td></tr>}
          {chapters?.length === 0 && <tr><td colSpan={4} className="px-3 py-4 text-slate-500">No chapters for Grade {grade} Term {term}.</td></tr>}
          {chapters?.map(c => {
            const label = sourceLabel(c);
            const reviewId = c.pending_draft_id || c.published_draft_id;
            const canWrite = c.booklet_source !== 'hand_written' && c.has_lesson_content;
            return <tr key={c.lesson_id} className={`border-t border-slate-100 ${draft?.lesson_id === c.lesson_id ? 'bg-emerald-50/50' : ''}`}>
              <td className="px-3 py-2 text-slate-500">{c.lesson_order}</td>
              <td className="px-3 py-2">
                <div className="font-arabic font-bold" dir="rtl">{c.title_ar}</div>
                <div className="text-xs text-slate-500">{c.title_en}</div>
              </td>
              <td className="px-3 py-2">
                <span className={`text-[11px] font-bold px-2 py-0.5 ${label.cls}`}>{label.text}</span>
                {c.latest?.status === 'rejected' && !c.pending_draft_id && <div className="text-[11px] text-slate-500 mt-1">Last draft rejected</div>}
              </td>
              <td className="px-3 py-2 text-right whitespace-nowrap space-x-1.5">
                {reviewId && <button type="button" onClick={() => open(c.pending_draft_id || c.published_draft_id!)}
                  className="px-2 py-1 text-xs font-bold border border-emerald-300 text-emerald-900 hover:bg-emerald-50 inline-flex items-center gap-1">
                  <Eye className="w-3.5 h-3.5" /> {c.pending_draft_id ? 'Review draft' : 'View live'}
                </button>}
                {canWrite && <button type="button" disabled={busy}
                  onClick={() => write([c.lesson_id], true)}
                  className="px-2 py-1 text-xs font-bold border border-slate-300 text-slate-800 hover:bg-slate-50 disabled:opacity-50">
                  {c.published_draft_id || c.pending_draft_id ? 'Rewrite' : 'Write'}
                </button>}
              </td>
            </tr>;
          })}
        </tbody>
      </table>
    </div>

    {draft && <div className="bg-white border-2 border-emerald-900">
      <div className="flex flex-wrap items-start justify-between gap-3 p-4 border-b border-slate-200 bg-slate-50">
        <div className="space-y-1 text-xs text-slate-700">
          <div className="text-sm font-black text-emerald-950">
            {draft.status === 'published' ? 'Live booklet' : 'Draft for review'} · Grade {draft.grade} Term {draft.term}
          </div>
          <div>Status: <b>{draft.status}</b>{draft.model ? ` · written by ${draft.model}` : ''}{draft.cost_usd ? ` · AI cost $${draft.cost_usd.toFixed(3)}` : ''}</div>
          <div>Check the facts against the textbook chapter, the tashkeel and the right answer to each exercise.</div>
          {draft.unvowelled_words.length > 0 && <div className="text-amber-900">
            Words without tashkeel (they show no Arab-English line): <span className="font-arabic" dir="rtl">{draft.unvowelled_words.join('، ')}</span>
          </div>}
        </div>
        <button type="button" aria-label="Close preview" onClick={() => setDraft(null)} className="p-1 text-slate-500 hover:text-slate-900"><X className="w-5 h-5" /></button>
      </div>
      <div className="flex flex-wrap items-end gap-2 p-4 border-b border-slate-200">
        <label className="text-xs font-bold text-slate-700 flex-1 min-w-[16rem]">Review note (optional)
          <input value={note} onChange={e => setNote(e.target.value)} className="mt-1 w-full border border-slate-300 px-2 py-1.5 text-sm font-normal" placeholder="e.g. Checked against textbook pages 22–31" />
        </label>
        {draft.status !== 'published' && <button type="button" onClick={() => review('publish')}
          className="px-3 py-2 text-xs font-bold bg-emerald-900 hover:bg-emerald-950 text-white inline-flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" /> Publish to learners
        </button>}
        {draft.status === 'published' && <button type="button" onClick={() => review('unpublish')}
          className="px-3 py-2 text-xs font-bold border border-amber-400 text-amber-900 hover:bg-amber-50">Unpublish</button>}
        {draft.status === 'draft' && <button type="button" onClick={() => review('reject')}
          className="px-3 py-2 text-xs font-bold border border-red-300 text-red-800 hover:bg-red-50">Reject</button>}
      </div>
      <MalazimViewer user={{ role: 'admin' } as any} previewBooklet={draft.booklet} />
    </div>}
  </div>;
}
