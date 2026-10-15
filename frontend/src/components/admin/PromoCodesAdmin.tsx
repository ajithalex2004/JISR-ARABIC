import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { PromoCodeInfo } from '../../types';
import { formatDate } from './PaymentsAdmin';

// <input type="date"> works in local dates; the server stores UTC timestamps.
const toInput = (iso: string | null) => iso ? iso.slice(0, 10) : '';
const fromInput = (value: string, endOfDay = false) => value ? `${value}T${endOfDay ? '23:59:59' : '00:00:00'}` : null;

type Draft = { code: string; discount_pct: string; max_users: string; valid_from: string; valid_until: string; is_active: boolean; notes: string };
const toDraft = (p?: PromoCodeInfo): Draft => ({
  code: p?.code || '', discount_pct: String(p?.discount_pct ?? 10), max_users: p?.max_users == null ? (p ? '' : '10') : String(p.max_users),
  valid_from: toInput(p?.valid_from ?? null), valid_until: toInput(p?.valid_until ?? null), is_active: p?.is_active ?? true, notes: p?.notes || '',
});

const STATE_STYLE: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-900', scheduled: 'bg-sky-100 text-sky-900', expired: 'bg-slate-200 text-slate-700',
  'used up': 'bg-amber-100 text-amber-900', inactive: 'bg-slate-200 text-slate-700',
};

function PromoForm({ promo, onSaved, onCancel }: { promo?: PromoCodeInfo; onSaved: () => void; onCancel: () => void }) {
  const [draft, setDraft] = useState<Draft>(toDraft(promo));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const set = (key: keyof Draft) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setDraft(d => ({ ...d, [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));
  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true); setError('');
    try {
      await api.adminSavePromoCode(promo?.id ?? null, {
        ...(promo ? {} : { code: draft.code.trim() }),
        discount_pct: Number(draft.discount_pct),
        max_users: draft.max_users === '' ? null : Number(draft.max_users),
        valid_from: fromInput(draft.valid_from), valid_until: fromInput(draft.valid_until, true),
        is_active: draft.is_active, notes: draft.notes,
      });
      onSaved();
    } catch (err: any) { setError(err.message); } finally { setBusy(false); }
  };
  const input = 'border border-slate-400 p-2 w-full';
  return <form onSubmit={save} className="border border-emerald-300 bg-emerald-50/40 p-3 grid gap-2 sm:grid-cols-3 text-sm">
    <label>Code<input required disabled={!!promo} value={draft.code} onChange={set('code')} placeholder="e.g. JISR10" className={`${input} uppercase font-mono`} /></label>
    <label>Discount (%)<input required type="number" min={1} max={100} step="0.5" value={draft.discount_pct} onChange={set('discount_pct')} className={input} /></label>
    <label>Number of families<input type="number" min={1} value={draft.max_users} onChange={set('max_users')} placeholder="Unlimited" className={input} /></label>
    <label>Valid from<input type="date" value={draft.valid_from} onChange={set('valid_from')} className={input} /></label>
    <label>Valid until<input type="date" value={draft.valid_until} onChange={set('valid_until')} className={input} /></label>
    <label className="flex items-center gap-2 mt-6"><input type="checkbox" checked={draft.is_active} onChange={set('is_active')} /> Active</label>
    <label className="sm:col-span-3">Notes<input value={draft.notes} onChange={set('notes')} className={input} /></label>
    {error && <p role="alert" className="text-red-700 sm:col-span-3">{error}</p>}
    <div className="flex gap-2 sm:col-span-3">
      <button disabled={busy} className="bg-emerald-900 text-white px-4 py-2 disabled:opacity-50">{busy ? 'Saving…' : 'Save'}</button>
      <button type="button" onClick={onCancel} className="border border-slate-400 px-4 py-2">Cancel</button>
    </div>
  </form>;
}

export function PromoCodesAdmin() {
  const [promos, setPromos] = useState<PromoCodeInfo[]>([]);
  const [editing, setEditing] = useState<PromoCodeInfo | 'new' | null>(null);
  const [error, setError] = useState('');
  const load = async () => {
    setError('');
    try { setPromos(await api.adminPromoCodes()); } catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Promo codes</h2>
      <button type="button" onClick={() => setEditing('new')} className="bg-emerald-900 text-white px-4 py-2">+ New promo code</button>
    </div>
    <p className="text-sm text-slate-600">
      A promo code takes a percentage off a term or full-year purchase. Each family can use a code once; "Number of families" limits how many can use it,
      and the code only works between its dates. On auto-renewing plans it applies to the first payment only.
    </p>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {editing && <PromoForm key={editing === 'new' ? 'new' : editing.id} promo={editing === 'new' ? undefined : editing}
      onCancel={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />}
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse min-w-[640px]">
        <thead><tr className="text-left text-xs text-slate-500 border-b border-slate-200">
          <th className="py-1 pr-2">Code</th><th className="py-1 px-2">Discount</th><th className="py-1 px-2">Used</th>
          <th className="py-1 px-2">Valid</th><th className="py-1 px-2">Status</th><th className="py-1 pl-2"></th>
        </tr></thead>
        <tbody>{promos.map(p => <tr key={p.id} className="border-b border-slate-100">
          <td className="py-1.5 pr-2 font-mono font-bold">{p.code}</td>
          <td className="py-1.5 px-2">{p.discount_pct}%</td>
          <td className="py-1.5 px-2">{p.used} / {p.max_users ?? '∞'} families</td>
          <td className="py-1.5 px-2 text-xs">{p.valid_from ? formatDate(p.valid_from) : 'Any time'} → {p.valid_until ? formatDate(p.valid_until) : 'no end'}</td>
          <td className="py-1.5 px-2"><span className={`text-xs font-bold px-2 py-0.5 ${STATE_STYLE[p.state] || ''}`}>{p.state}</span></td>
          <td className="py-1.5 pl-2 text-right"><button type="button" onClick={() => setEditing(p)} className="text-emerald-900 underline">Edit</button></td>
        </tr>)}
        {!promos.length && <tr><td colSpan={6} className="py-3 text-slate-500">No promo codes yet.</td></tr>}</tbody>
      </table>
    </div>
  </section>;
}

export function SubscriptionsAdmin() {
  const [subs, setSubs] = useState<import('../../types').Subscription[]>([]);
  const [error, setError] = useState('');
  useEffect(() => { api.adminSubscriptions().then(setSubs).catch((e: any) => setError(e.message)); }, []);
  const active = subs.filter(s => s.status === 'active' && !s.cancel_at_period_end);
  const recurring = active.reduce((sum, s) => sum + s.renewal_price_usd * (12 / s.renewal_months), 0);
  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <h2 className="font-bold text-emerald-950">Auto-renewing subscriptions</h2>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    <div className="grid gap-2 grid-cols-2 sm:grid-cols-4 text-sm">
      <div className="border border-emerald-300 bg-emerald-50 p-3"><div className="text-xs text-slate-500">Renewing</div><div className="text-lg font-bold">{active.length}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Expected per year</div><div className="text-lg font-bold">USD {recurring.toFixed(2)}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Auto-renew turned off</div><div className="text-lg font-bold">{subs.filter(s => s.status !== 'canceled' && s.cancel_at_period_end).length}</div></div>
      <div className="border border-slate-200 bg-slate-50 p-3"><div className="text-xs text-slate-500">Payment failed</div><div className="text-lg font-bold">{subs.filter(s => s.status === 'past_due').length}</div></div>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse min-w-[720px]">
        <thead><tr className="text-left text-xs text-slate-500 border-b border-slate-200">
          <th className="py-1 pr-2">Family</th><th className="py-1 px-2">Student</th><th className="py-1 px-2">Plan</th>
          <th className="py-1 px-2">Price</th><th className="py-1 px-2">Status</th><th className="py-1 pl-2">Next renewal</th>
        </tr></thead>
        <tbody>{subs.map(s => <tr key={s.id} className="border-b border-slate-100">
          <td className="py-1.5 pr-2">{s.parent_name || '—'}<div className="text-xs text-slate-500">{s.parent_email}</div></td>
          <td className="py-1.5 px-2">{s.child_name} · Class {s.grade}</td>
          <td className="py-1.5 px-2">{s.plan === 'annual' ? 'Full year' : `Per term${s.next_term ? ` (next: Term ${s.next_term})` : ''}`}</td>
          <td className="py-1.5 px-2">USD {s.renewal_price_usd.toFixed(2)} / {s.renewal_months} mo</td>
          <td className="py-1.5 px-2">{s.status === 'active' && s.cancel_at_period_end ? 'ending' : s.status}</td>
          <td className="py-1.5 pl-2">{s.status === 'canceled' ? '—' : s.current_period_end ? formatDate(s.current_period_end) : '—'}</td>
        </tr>)}
        {!subs.length && <tr><td colSpan={6} className="py-3 text-slate-500">No auto-renewing subscriptions yet.</td></tr>}</tbody>
      </table>
    </div>
  </section>;
}
