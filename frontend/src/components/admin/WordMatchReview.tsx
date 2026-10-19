import React, { useCallback, useEffect, useState } from 'react';
import { Check, Pencil, RefreshCw, Search, X } from 'lucide-react';
import { api } from '../../services/api';
import { splitWords } from '../../services/alignment';

type Chunk = { ar: number[]; en: number[] };
type Status = 'ai' | 'approved' | 'rejected' | 'unusable';
type Item = {
  id: string;
  arabic: string;
  english: string;
  chunks: Chunk[];
  status: Status;
  provider: string | null;
  created_at: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
};

const STATUSES: { key: Status; label: string; hint: string }[] = [
  { key: 'ai', label: 'To review', hint: 'Matched by AI; learners see these until you reject them.' },
  { key: 'approved', label: 'Approved', hint: 'Checked by a teacher.' },
  { key: 'rejected', label: 'Rejected', hint: 'Hidden from learners.' },
  { key: 'unusable', label: "AI couldn't match", hint: 'No highlighting is shown: pair the words yourself, or ask the AI again.' },
];

// One colour per match, with its number shown too so colour is never the only cue.
const COLORS = [
  'bg-emerald-100 border-emerald-500 text-emerald-950',
  'bg-sky-100 border-sky-500 text-sky-950',
  'bg-amber-100 border-amber-500 text-amber-950',
  'bg-rose-100 border-rose-500 text-rose-950',
  'bg-violet-100 border-violet-500 text-violet-950',
  'bg-lime-100 border-lime-600 text-lime-950',
  'bg-orange-100 border-orange-500 text-orange-950',
  'bg-teal-100 border-teal-500 text-teal-950',
];

const isConsecutive = (indexes: number[]) => {
  const sorted = [...indexes].sort((a, b) => a - b);
  return sorted.every((v, i) => i === 0 || v === sorted[i - 1] + 1);
};

function Words({
  text, side, chunks, hovered, selected, onHover, onToggle,
}: {
  text: string;
  side: 'ar' | 'en';
  chunks: Chunk[];
  hovered: number | null;
  selected?: Set<number>;
  onHover: (chunk: number | null) => void;
  onToggle?: (index: number) => void;
}) {
  return (
    <div dir={side === 'ar' ? 'rtl' : 'ltr'} lang={side === 'ar' ? 'ar' : 'en'}
      className={`flex flex-wrap gap-1.5 ${side === 'ar' ? 'font-arabic text-xl' : 'text-sm'}`}>
      {splitWords(text).map((word, i) => {
        const chunk = chunks.findIndex((c) => c[side].includes(i));
        const isSelected = selected?.has(i);
        const color = chunk >= 0 ? COLORS[chunk % COLORS.length] : 'bg-white border-slate-200 text-slate-500';
        return (
          <button
            key={i}
            type="button"
            disabled={!onToggle && chunk < 0}
            onClick={() => onToggle?.(i)}
            onMouseEnter={() => onHover(chunk >= 0 ? chunk : null)}
            onMouseLeave={() => onHover(null)}
            onFocus={() => onHover(chunk >= 0 ? chunk : null)}
            onBlur={() => onHover(null)}
            aria-pressed={onToggle ? !!isSelected : undefined}
            className={`relative border px-2 py-0.5 leading-snug ${color} ${
              hovered !== null && chunk === hovered ? 'ring-2 ring-slate-900' : ''
            } ${isSelected ? 'outline outline-2 outline-offset-2 outline-purple-700' : ''} ${onToggle ? 'cursor-pointer' : 'cursor-default'}`}
          >
            {word}
            {chunk >= 0 && (
              <span className="absolute -top-2 -left-1.5 bg-slate-900 text-white text-[9px] font-sans font-bold px-1 leading-tight" dir="ltr">
                {chunk + 1}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function ReviewCard({ item, onDone }: { item: Item; onDone: (id: string, message: string) => void }) {
  const [hovered, setHovered] = useState<number | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<Chunk[]>(item.chunks);
  const [selAr, setSelAr] = useState<Set<number>>(new Set());
  const [selEn, setSelEn] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const act = async (action: 'approve' | 'reject' | 'regenerate', chunks?: Chunk[]) => {
    setBusy(true);
    setError('');
    try {
      await api.reviewAlignment(item.id, action, chunks);
      onDone(item.id, action === 'approve' ? 'Approved.' : action === 'reject' ? 'Rejected: learners will no longer see it.'
        : 'Sent back to the AI: it will be matched again the next time a learner opens it.');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const toggle = (set: Set<number>, setter: (s: Set<number>) => void) => (i: number) => {
    const next = new Set(set);
    if (next.has(i)) next.delete(i); else next.add(i);
    setter(next);
  };

  const pair = () => {
    const ar = [...selAr].sort((a, b) => a - b);
    const en = [...selEn].sort((a, b) => a - b);
    if (!ar.length || !en.length) return setError('Select at least one Arabic word and one English word to pair.');
    if (!isConsecutive(ar)) return setError('The Arabic words in one match must be next to each other.');
    // Selected words leave any match they were in.
    const rest = draft
      .map((c) => ({ ar: c.ar.filter((i) => !selAr.has(i)), en: c.en.filter((i) => !selEn.has(i)) }))
      .filter((c) => c.ar.length && c.en.length && isConsecutive(c.ar));
    setDraft([...rest, { ar, en }].sort((a, b) => a.ar[0] - b.ar[0]));
    setSelAr(new Set());
    setSelEn(new Set());
    setError('');
  };

  const chunks = editing ? draft : item.chunks;
  const when = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString() : '');

  return (
    <div className="sharp-card bg-white border border-slate-300 p-4 space-y-3">
      <Words text={item.arabic} side="ar" chunks={chunks} hovered={hovered} onHover={setHovered}
        selected={editing ? selAr : undefined} onToggle={editing ? toggle(selAr, setSelAr) : undefined} />
      <Words text={item.english} side="en" chunks={chunks} hovered={hovered} onHover={setHovered}
        selected={editing ? selEn : undefined} onToggle={editing ? toggle(selEn, setSelEn) : undefined} />

      {editing && (
        <div className="bg-purple-50 border border-purple-200 p-3 space-y-2 text-xs">
          <p className="text-purple-950">
            Tap Arabic words and their English meaning, then <strong>Pair selected</strong>. Remove a wrong match with its ×.
          </p>
          <div className="flex flex-wrap gap-1.5">
            {draft.map((c, i) => (
              <span key={i} className={`border px-1.5 py-0.5 inline-flex items-center gap-1 ${COLORS[i % COLORS.length]}`}>
                <strong>{i + 1}</strong>
                <span dir="rtl" lang="ar" className="font-arabic">{c.ar.map((w) => splitWords(item.arabic)[w]).join(' ')}</span>
                = {c.en.map((w) => splitWords(item.english)[w]).join(' ')}
                <button type="button" aria-label={`Remove match ${i + 1}`} onClick={() => setDraft(draft.filter((_, k) => k !== i))}
                  className="ml-0.5 hover:text-red-700"><X className="w-3 h-3" /></button>
              </span>
            ))}
            {draft.length === 0 && <span className="text-slate-500">No matches yet.</span>}
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={pair} className="px-3 py-1 bg-purple-800 text-white font-bold">Pair selected</button>
            <button type="button" disabled={busy || draft.length === 0} onClick={() => act('approve', draft)}
              className="px-3 py-1 bg-emerald-800 text-white font-bold disabled:opacity-50">Save &amp; approve</button>
            <button type="button" onClick={() => { setEditing(false); setDraft(item.chunks); setSelAr(new Set()); setSelEn(new Set()); setError(''); }}
              className="px-3 py-1 border border-slate-300 bg-white font-bold">Cancel</button>
          </div>
        </div>
      )}

      {error && <p role="alert" className="text-xs text-red-700 font-bold">{error}</p>}

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 pt-2">
        <span className="text-[11px] text-slate-500">
          {item.reviewed_at ? `Reviewed ${when(item.reviewed_at)}` : `Matched by ${item.provider || 'AI'} ${when(item.created_at)}`}
        </span>
        {!editing && (
          <div className="flex flex-wrap gap-1.5 text-xs font-bold">
            {item.status !== 'approved' && item.status !== 'unusable' && (
              <button type="button" disabled={busy} onClick={() => act('approve')}
                className="px-3 py-1.5 bg-emerald-800 text-white inline-flex items-center gap-1 disabled:opacity-50">
                <Check className="w-3.5 h-3.5" /> Approve
              </button>
            )}
            <button type="button" disabled={busy} onClick={() => { setEditing(true); setDraft(item.chunks); }}
              className="px-3 py-1.5 border border-purple-400 text-purple-900 bg-white inline-flex items-center gap-1">
              <Pencil className="w-3.5 h-3.5" /> {item.status === 'unusable' ? 'Pair words myself' : 'Edit'}
            </button>
            {item.status !== 'rejected' && item.status !== 'unusable' && (
              <button type="button" disabled={busy} onClick={() => act('reject')}
                className="px-3 py-1.5 border border-red-300 text-red-800 bg-white inline-flex items-center gap-1 disabled:opacity-50">
                <X className="w-3.5 h-3.5" /> Reject
              </button>
            )}
            <button type="button" disabled={busy} onClick={() => act('regenerate')}
              className="px-3 py-1.5 border border-slate-300 text-slate-700 bg-white inline-flex items-center gap-1 disabled:opacity-50">
              <RefreshCw className="w-3.5 h-3.5" /> Ask AI again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Teacher review of the Arabic–English word matches learners see when they tap or hear a word.
 */
export const WordMatchReview: React.FC = () => {
  const [status, setStatus] = useState<Status>('ai');
  const [query, setQuery] = useState('');
  const [items, setItems] = useState<Item[]>([]);
  const [counts, setCounts] = useState<Record<Status, number>>({ ai: 0, approved: 0, rejected: 0, unusable: 0 });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async (offset = 0) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.listAlignmentsForReview(status, query, offset);
      setCounts(data.counts);
      setTotal(data.total);
      setItems((prev) => (offset ? [...prev, ...data.items] : data.items));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [status, query]);

  useEffect(() => {
    const timer = setTimeout(() => load(0), query ? 300 : 0);
    return () => clearTimeout(timer);
  }, [load, query]);

  const done = (id: string, message: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
    setTotal((t) => Math.max(0, t - 1));
    setNotice(message);
    api.listAlignmentsForReview(status, query, 0).then((data) => setCounts(data.counts)).catch(() => {});
  };

  return (
    <div className="space-y-4">
      <div className="sharp-card p-4 bg-white border border-slate-300">
        <h2 className="font-black text-slate-900 text-lg">
          Word Matches Review · <span className="font-arabic" lang="ar">مراجعة مطابقة الكلمات</span>
        </h2>
        <p className="text-xs text-slate-600 mt-1">
          When a learner taps or hears an Arabic word, its English meaning lights up. The AI suggested these matches;
          check that each numbered Arabic word matches the English with the same number and colour.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div role="tablist" aria-label="Match status" className="flex flex-wrap gap-1">
          {STATUSES.map((s) => (
            <button key={s.key} type="button" role="tab" aria-selected={status === s.key} title={s.hint}
              onClick={() => { setStatus(s.key); setNotice(''); }}
              className={`px-3 py-1.5 text-xs font-bold border ${status === s.key ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-700 border-slate-300 hover:border-slate-500'}`}>
              {s.label} <span className="font-mono opacity-80">{counts[s.key] ?? 0}</span>
            </button>
          ))}
        </div>
        <label className="ml-auto flex items-center gap-1.5 border border-slate-300 bg-white px-2 py-1 text-xs">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search Arabic or English"
            aria-label="Search sentences" className="outline-none w-48" />
        </label>
      </div>

      <p className="text-xs text-slate-500">{STATUSES.find((s) => s.key === status)!.hint}</p>
      {notice && <p role="status" className="text-xs font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 p-2">{notice}</p>}
      {error && <p role="alert" className="text-xs font-bold text-red-700">{error}</p>}

      <div className="space-y-3">
        {items.map((item) => <ReviewCard key={item.id} item={item} onDone={done} />)}
        {!loading && items.length === 0 && !error && (
          <p className="text-sm text-slate-500 bg-white border border-dashed border-slate-300 p-6 text-center">
            Nothing here. Matches appear after learners open lessons and textbook pages.
          </p>
        )}
      </div>

      {items.length < total && (
        <button type="button" disabled={loading} onClick={() => load(items.length)}
          className="w-full py-2 border border-slate-300 bg-white text-sm font-bold text-slate-700 disabled:opacity-50">
          {loading ? 'Loading…' : `Show more (${total - items.length} left)`}
        </button>
      )}
    </div>
  );
};
