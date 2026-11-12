import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../services/api';
import { canonicalArabic, getTeacherCorrection, listBuiltInEntries, loadWordCorrections } from '../../services/arabicDictionary';

type Tab = 'ai' | 'builtin';
type Item = { word: string; translation: string | null; part_of_speech?: string | null; source?: string | null; status?: string; review_note?: string | null };
const POS = ['', 'noun', 'verb', 'adjective', 'particle', 'pronoun', 'adverb'];
const PAGE = 50;

/** Teacher review of the English meanings shown in word popups: AI meanings and the built-in dictionary. */
export default function WordReviewQueue() {
  const [tab, setTab] = useState<Tab>('ai');
  const [status, setStatus] = useState<'pending' | 'reviewed'>('pending');
  const [q, setQ] = useState('');
  const [offset, setOffset] = useState(0);
  const [queue, setQueue] = useState<{ total: number; counts: Record<string, number>; items: Item[] } | null>(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState({ translation: '', pos: '', note: '' });
  const [, setVersion] = useState(0);

  const loadQueue = useCallback(async () => {
    if (tab !== 'ai') return;
    setError('');
    try { setQueue(await api.getWordGlossQueue(status, q, offset, PAGE)); } catch (e: any) { setError(e.message); }
  }, [tab, status, q, offset]);
  useEffect(() => { loadQueue(); }, [loadQueue]);
  useEffect(() => { loadWordCorrections(true).then(() => setVersion((v) => v + 1)); }, []);

  // Built-in entries, one per normalized word, with their review state from the teacher corrections.
  const builtIn = useMemo(() => {
    const seen = new Set<string>();
    return listBuiltInEntries().filter((e) => { const k = canonicalArabic(e.word); if (!k || seen.has(k)) return false; seen.add(k); return true; });
  }, []);
  const builtInRows = useMemo(() => {
    const needle = canonicalArabic(q);
    const rows = builtIn.filter((e) => {
      const reviewed = !!getTeacherCorrection(e.word);
      return (status === 'reviewed' ? reviewed : !reviewed) && (!needle || canonicalArabic(e.word).includes(needle) || e.translation.toLowerCase().includes(q.toLowerCase()));
    });
    return rows;
  }, [builtIn, status, q, queue]);
  const builtInReviewed = builtIn.filter((e) => getTeacherCorrection(e.word)).length;

  const decide = async (item: Item, action: 'approve' | 'correct' | 'reject') => {
    setError('');
    try {
      await api.reviewWordGloss({
        word: item.word, action, current: item.translation || '', source: item.source || (tab === 'builtin' ? 'dictionary' : ''),
        ...(action === 'correct' ? { translation: draft.translation, part_of_speech: draft.pos } : {}),
        ...(action === 'approve' && item.part_of_speech ? { part_of_speech: item.part_of_speech } : {}),
        note: draft.note,
      });
      setMessage(`${item.word}: ${action === 'approve' ? 'meaning approved' : action === 'correct' ? 'meaning corrected' : 'meaning rejected (no meaning will be shown)'}.`);
      setEditing(null);
      setDraft({ translation: '', pos: '', note: '' });
      await loadWordCorrections(true);
      setVersion((v) => v + 1);
      await loadQueue();
    } catch (e: any) { setError(e.message); }
  };

  const rows: Item[] = tab === 'ai'
    ? (queue?.items || [])
    : builtInRows.slice(offset, offset + PAGE).map((e) => {
        const c = getTeacherCorrection(e.word);
        return { word: e.word, translation: c ? c.translation : e.translation, part_of_speech: (c?.part_of_speech ?? e.partOfSpeech) || null, source: 'dictionary', status: c ? (c.translation ? 'reviewed' : 'rejected') : 'pending' };
      });
  const total = tab === 'ai' ? (queue?.total ?? 0) : builtInRows.length;

  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-600">
        The English meanings in word popups come from the built-in dictionary and, for other words, from AI. A teacher's
        decision here is what learners see: approved and corrected meanings are shown; a rejected meaning is hidden.
      </p>
      <div className="grid gap-2 grid-cols-1 sm:grid-cols-3 text-sm">
        <div className="border border-amber-400 bg-amber-50 p-2"><div className="text-xs text-slate-500">AI meanings to review</div><div className="text-lg font-bold">{queue?.counts?.pending ?? '…'}</div></div>
        <div className="border border-slate-200 bg-slate-50 p-2"><div className="text-xs text-slate-500">AI meanings reviewed</div><div className="text-lg font-bold">{queue ? (queue.counts.approved + queue.counts.corrected + queue.counts.rejected) : '…'}</div></div>
        <div className="border border-amber-400 bg-amber-50 p-2"><div className="text-xs text-slate-500">Built-in words reviewed</div><div className="text-lg font-bold">{builtInReviewed} / {builtIn.length}</div></div>
      </div>
      <div className="flex flex-wrap gap-2 items-center text-sm">
        {(['ai', 'builtin'] as Tab[]).map((t) => (
          <button key={t} type="button" aria-pressed={tab === t} onClick={() => { setTab(t); setOffset(0); }}
            className={`px-3 py-1.5 border ${tab === t ? 'bg-slate-900 text-white border-slate-900' : 'border-slate-300'}`}>
            {t === 'ai' ? 'AI meanings' : 'Built-in dictionary'}
          </button>
        ))}
        <select value={status} onChange={(e) => { setStatus(e.target.value as any); setOffset(0); }} className="border border-slate-300 px-2 py-1.5" aria-label="Show">
          <option value="pending">Waiting for review</option>
          <option value="reviewed">Reviewed</option>
        </select>
        <input value={q} onChange={(e) => { setQ(e.target.value); setOffset(0); }} placeholder="Search a word or meaning" className="border border-slate-300 px-2 py-1.5 flex-1 min-w-[180px]" aria-label="Search" />
      </div>
      {message && <p role="status" className="text-sm text-emerald-800">{message}</p>}
      {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
      <table className="w-full text-sm border-collapse">
        <thead><tr className="text-left text-xs text-slate-500 border-b"><th className="py-1.5">Word</th><th>Meaning</th><th>Type</th><th>From</th><th className="text-right">Decision</th></tr></thead>
        <tbody>
          {rows.map((item) => (
            <React.Fragment key={item.word}>
              <tr className="border-b border-slate-100 align-top">
                <td className="py-1.5 font-arabic text-lg" dir="rtl" lang="ar">{item.word}</td>
                <td className="py-1.5">{item.translation ?? <span className="text-slate-400">(no meaning shown)</span>}</td>
                <td className="py-1.5 text-slate-600">{item.part_of_speech || '—'}</td>
                <td className="py-1.5 text-slate-500 text-xs">{item.source}{item.status && item.status !== 'pending' ? ` · ${item.status}` : ''}</td>
                <td className="py-1.5 text-right whitespace-nowrap">
                  <button type="button" onClick={() => decide(item, 'approve')} disabled={!item.translation} className="px-2 py-1 bg-emerald-700 text-white text-xs disabled:opacity-40">Approve</button>{' '}
                  <button type="button" onClick={() => { setEditing(item.word); setDraft({ translation: item.translation || '', pos: item.part_of_speech || '', note: '' }); }} className="px-2 py-1 border border-slate-400 text-xs">Correct</button>{' '}
                  <button type="button" onClick={() => decide(item, 'reject')} className="px-2 py-1 border border-red-400 text-red-800 text-xs">Reject</button>
                </td>
              </tr>
              {editing === item.word && (
                <tr className="bg-slate-50"><td colSpan={5} className="p-2">
                  <div className="flex flex-wrap gap-2 items-center">
                    <label className="text-xs" htmlFor="wr-meaning">Correct meaning</label>
                    <input id="wr-meaning" value={draft.translation} onChange={(e) => setDraft({ ...draft, translation: e.target.value })} className="border border-slate-300 px-2 py-1 flex-1 min-w-[160px]" />
                    <select value={draft.pos} onChange={(e) => setDraft({ ...draft, pos: e.target.value })} className="border border-slate-300 px-2 py-1" aria-label="Word type">
                      {POS.map((p) => <option key={p} value={p}>{p || 'word type…'}</option>)}
                    </select>
                    <input value={draft.note} onChange={(e) => setDraft({ ...draft, note: e.target.value })} placeholder="Note (optional)" className="border border-slate-300 px-2 py-1 min-w-[140px]" aria-label="Note" />
                    <button type="button" onClick={() => decide(item, 'correct')} className="px-2 py-1 bg-slate-900 text-white text-xs">Save correction</button>
                    <button type="button" onClick={() => setEditing(null)} className="px-2 py-1 border border-slate-300 text-xs">Cancel</button>
                  </div>
                </td></tr>
              )}
            </React.Fragment>
          ))}
          {rows.length === 0 && <tr><td colSpan={5} className="py-4 text-center text-slate-500">Nothing here.</td></tr>}
        </tbody>
      </table>
      <div className="flex justify-between items-center text-xs text-slate-600">
        <span>{total ? `${offset + 1}–${Math.min(offset + PAGE, total)} of ${total}` : ''}</span>
        <span className="flex gap-2">
          <button type="button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE))} className="px-2 py-1 border disabled:opacity-40">Previous</button>
          <button type="button" disabled={offset + PAGE >= total} onClick={() => setOffset(offset + PAGE)} className="px-2 py-1 border disabled:opacity-40">Next</button>
        </span>
      </div>
    </div>
  );
}
