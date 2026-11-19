import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { formatDate } from './PaymentsAdmin';

type StoredPaper = {
  id: number;
  paper_title: string;
  file_name?: string | null;
  file_type?: string | null;
  total_questions: number;
  reuses: number;
  created_at?: string | null;
  last_accessed_at?: string | null;
};
type StoredQuestion = {
  question_number?: number;
  question_text_ar?: string;
  question_text_en?: string;
  model_answer_ar?: string;
  model_answer_en?: string;
};

/**
 * Answers to uploaded question papers are stored and reused, free, when the identical file is
 * uploaded again. If a paper's stored answers are wrong, clear them here: its next upload is read
 * again by the AI.
 */
export function StoredAnswersPanel() {
  const [papers, setPapers] = useState<StoredPaper[] | null>(null);
  const [total, setTotal] = useState(0);
  const [open, setOpen] = useState<number | null>(null);
  const [detail, setDetail] = useState<Record<number, StoredQuestion[]>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = async () => {
    setError('');
    try {
      const res = await api.adminListStoredAnswers();
      setPapers(res.papers);
      setTotal(res.total);
    } catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  const toggle = async (id: number) => {
    if (open === id) { setOpen(null); return; }
    setOpen(id);
    if (detail[id]) return;
    try {
      const res = await api.adminGetStoredAnswers(id);
      setDetail(d => ({ ...d, [id]: res.questions }));
    } catch (e: any) { setError(e.message); }
  };

  const clear = async (paper?: StoredPaper) => {
    const message = paper
      ? `Clear the stored answers for "${paper.paper_title}"?\n\nThe next upload of this paper will be read again by the AI (and cost again).`
      : `Clear ALL ${total} stored paper answers?\n\nEvery paper will be read again by the AI the next time it is uploaded (and cost again).`;
    if (!window.confirm(message)) return;
    setBusy(true); setError(''); setNotice('');
    try {
      const res = await api.adminClearStoredAnswers(paper?.id);
      setNotice(`Cleared ${res.deleted} stored paper${res.deleted === 1 ? '' : 's'}.`);
      setOpen(null);
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setBusy(false); }
  };

  return <section className="border border-slate-200 bg-white p-3 space-y-2" aria-labelledby="stored-answers-title">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h3 id="stored-answers-title" className="font-bold text-slate-900">Stored paper answers</h3>
      <span className="flex gap-2">
        <button type="button" onClick={load} disabled={busy} className="border border-slate-400 px-3 py-1 text-xs disabled:opacity-40">Refresh</button>
        <button type="button" onClick={() => clear()} disabled={busy || !total}
          className="border-2 border-red-700 bg-red-50 text-red-800 px-3 py-1 text-xs font-bold disabled:opacity-40">
          Clear all stored answers
        </button>
      </span>
    </div>
    <p className="text-xs text-slate-600">
      When the exact same question paper file is uploaded again, its answers are reused from here instead of
      asking the AI (no cost). If a paper's answers are wrong, clear them: the next upload is read again by the AI.
    </p>
    {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
    {notice && <p role="status" className="text-sm text-emerald-800">{notice}</p>}
    {papers === null && !error && <p className="text-sm text-slate-500">Loading…</p>}
    {papers && !papers.length && <p className="text-sm text-slate-500">No stored answers yet.</p>}
    {papers && papers.length > 0 && <ul className="divide-y divide-slate-200 border-y border-slate-200">
      {papers.map(p => <li key={p.id} className="py-2 space-y-1.5">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <span className="block font-semibold text-slate-900 break-words">{p.paper_title}</span>
            {p.file_name && p.file_name !== p.paper_title && <span className="block text-xs text-slate-500 break-all">{p.file_name}</span>}
            <span className="block text-xs text-slate-600 mt-0.5">
              {p.total_questions} question{p.total_questions === 1 ? '' : 's'}
              {' · '}<span title="Uploads answered from storage, without the AI">reused {p.reuses} time{p.reuses === 1 ? '' : 's'}</span>
              {' · '}stored {formatDate(p.created_at)}
              {' · '}last used {formatDate(p.last_accessed_at)}
            </span>
          </div>
          <span className="flex gap-1 shrink-0">
            <button type="button" onClick={() => toggle(p.id)} aria-expanded={open === p.id}
              className="border border-slate-400 px-2 py-1 text-xs whitespace-nowrap">
              {open === p.id ? 'Hide answers' : 'View answers'}
            </button>
            <button type="button" onClick={() => clear(p)} disabled={busy} aria-label={`Clear stored answers for ${p.paper_title}`}
              className="border border-red-700 text-red-800 px-2 py-1 text-xs disabled:opacity-40">Clear</button>
          </span>
        </div>
        {open === p.id && <div className="bg-slate-50 border border-slate-200 p-2">
          {!detail[p.id] ? <span className="text-xs text-slate-500">Loading answers…</span> :
            <ol className="space-y-2">{detail[p.id].map((q, i) => <li key={i} className="text-xs space-y-0.5">
              <div className="text-right font-arabic text-slate-900" dir="rtl">{q.question_number}. {q.question_text_ar}</div>
              {q.question_text_en && <div className="text-slate-500 italic">{q.question_text_en}</div>}
              <div className="text-right font-arabic font-bold text-emerald-900" dir="rtl">
                {q.model_answer_ar || <span className="text-amber-800 font-normal">(no answer: not readable on the paper)</span>}
              </div>
              {q.model_answer_en && <div className="text-emerald-800">{q.model_answer_en}</div>}
            </li>)}</ol>}
        </div>}
      </li>)}
    </ul>}
    {papers && total > papers.length && <p className="text-xs text-slate-500">Showing the {papers.length} most recently used of {total}.</p>}
  </section>;
}
