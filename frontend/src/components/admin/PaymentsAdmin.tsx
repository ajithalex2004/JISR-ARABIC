import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

export type Payment = {
  id: string;
  created_at: string | null;
  parent_id?: string | null;
  parent_name?: string | null;
  parent_email?: string | null;
  child_name?: string | null;
  grade: number;
  term: number;
  package_type?: string | null;
  amount_usd: number;
  vat_amount_usd: number;
  payment_method?: string | null;
  voucher_code?: string | null;
  promo_code?: string | null;
  receipt_number: string;
  status: string;
};

type Summary = {
  count: number;
  paid_count: number;
  revenue_usd: number;
  vat_usd: number;
  voucher_redemptions: number;
  pending_count: number;
  refunded_count: number;
};

export const formatDate = (iso?: string | null) =>
  iso ? new Date(iso.endsWith('Z') || iso.includes('+') ? iso : `${iso}Z`).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : '—';

export const usd = (n: number) => `$${(n || 0).toFixed(2)}`;

const METHOD_LABELS: Record<string, string> = { card: 'Card', school_voucher: 'Voucher', voucher: 'Voucher', school_license: 'School licence' };

const STATUS_LABELS: Record<string, string> = { succeeded: 'paid' };

const STATUS_STYLES: Record<string, string> = {
  succeeded: 'bg-emerald-100 text-emerald-900',
  pending: 'bg-amber-100 text-amber-900',
  refunded: 'bg-slate-200 text-slate-700',
};

export function PaymentsTable({ payments, showFamily = true }: { payments: Payment[]; showFamily?: boolean }) {
  return <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-slate-500 border-b border-slate-200">
          <th className="py-2 pr-3">Date</th>
          {showFamily && <th className="py-2 pr-3">Family</th>}
          <th className="py-2 pr-3">Student</th>
          <th className="py-2 pr-3">Grade / term</th>
          <th className="py-2 pr-3">Paid with</th>
          <th className="py-2 pr-3 text-right">Amount</th>
          <th className="py-2 pr-3">Status</th>
          <th className="py-2">Receipt</th>
        </tr>
      </thead>
      <tbody>
        {payments.map(p => <tr key={p.id} className="border-b border-slate-100 align-top">
          <td className="py-2 pr-3 whitespace-nowrap">{formatDate(p.created_at)}</td>
          {showFamily && <td className="py-2 pr-3">{p.parent_name || '—'}<div className="text-xs text-slate-500 break-all">{p.parent_email || '(deleted account)'}</div></td>}
          <td className="py-2 pr-3">{p.child_name || '—'}</td>
          <td className="py-2 pr-3 whitespace-nowrap">Grade {p.grade} · {p.package_type === 'annual' ? 'Full year' : `Term ${p.term}`}</td>
          <td className="py-2 pr-3">
            {METHOD_LABELS[p.payment_method || ''] || p.payment_method || '—'}
            {p.voucher_code && <div className="text-xs text-slate-500">Code {p.voucher_code}</div>}
            {p.promo_code && <div className="text-xs text-slate-500">Promo {p.promo_code}</div>}
          </td>
          <td className="py-2 pr-3 text-right font-mono">{usd(p.amount_usd)}</td>
          <td className="py-2 pr-3"><span className={`px-2 py-0.5 text-xs font-bold ${STATUS_STYLES[p.status] || 'bg-red-100 text-red-800'}`}>{STATUS_LABELS[p.status] || p.status}</span></td>
          <td className="py-2 text-xs font-mono break-all">{p.receipt_number}</td>
        </tr>)}
        {!payments.length && <tr><td colSpan={showFamily ? 8 : 7} className="py-3 text-slate-500">No payments found.</td></tr>}
      </tbody>
    </table>
  </div>;
}

function downloadCsv(payments: Payment[]) {
  const header = ['Date', 'Parent', 'Parent email', 'Student', 'Grade', 'Term', 'Package', 'Method', 'Voucher', 'Amount USD', 'VAT USD', 'Status', 'Receipt'];
  const rows = payments.map(p => [p.created_at, p.parent_name, p.parent_email, p.child_name, p.grade, p.term, p.package_type,
    p.payment_method, p.voucher_code, p.amount_usd, p.vat_amount_usd, p.status, p.receipt_number]);
  const csv = [header, ...rows].map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `jisr-payments-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

export function PaymentsAdmin() {
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('');
  const [status, setStatus] = useState('');
  const [days, setDays] = useState('');
  const [data, setData] = useState<{ summary: Summary; payments: Payment[]; truncated: boolean } | null>(null);
  const [error, setError] = useState('');

  const load = async () => {
    setError('');
    try { setData(await api.adminListPayments({ q: query, method, status, days: days ? Number(days) : undefined })); }
    catch (e: any) { setError(e.message); }
  };
  useEffect(() => { load(); }, [method, status, days]);

  const s = data?.summary;
  const tiles: Array<[string, string]> = s ? [
    ['Revenue (paid)', usd(s.revenue_usd)],
    ['Paid transactions', String(s.paid_count)],
    ['Voucher redemptions', String(s.voucher_redemptions)],
    ['Pending', String(s.pending_count)],
    ['Refunded', String(s.refunded_count)],
  ] : [];

  return <section className="border border-slate-300 bg-white p-4 space-y-3">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h2 className="font-bold text-emerald-950">Payments</h2>
      <button type="button" disabled={!data?.payments.length} onClick={() => data && downloadCsv(data.payments)} className="border border-slate-400 px-3 py-1.5 text-sm disabled:opacity-40">Download CSV</button>
    </div>
    <p className="text-sm text-slate-600">Every card payment and voucher redemption, newest first. Search by parent, student, receipt number or voucher code.</p>
    <form className="flex flex-wrap gap-2" onSubmit={e => { e.preventDefault(); load(); }}>
      <input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Family, student, receipt or voucher" aria-label="Search payments" className="border border-slate-400 p-2 flex-1 min-w-[12rem]" />
      <select aria-label="Payment method" value={method} onChange={e => setMethod(e.target.value)} className="border border-slate-400 p-2">
        <option value="">All methods</option><option value="card">Card</option><option value="voucher">Vouchers</option>
      </select>
      <select aria-label="Status" value={status} onChange={e => setStatus(e.target.value)} className="border border-slate-400 p-2">
        <option value="">All statuses</option><option value="succeeded">Paid</option><option value="pending">Pending</option><option value="refunded">Refunded</option>
      </select>
      <select aria-label="Period" value={days} onChange={e => setDays(e.target.value)} className="border border-slate-400 p-2">
        <option value="">All time</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option><option value="365">Last 12 months</option>
      </select>
      <button className="bg-emerald-900 text-white px-4 py-2">Search</button>
    </form>
    {error && <p role="alert" className="text-red-700 text-sm">{error}</p>}
    {s && <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
      {tiles.map(([label, value]) => <div key={label} className="border border-slate-200 bg-slate-50 p-3">
        <div className="text-xs text-slate-500">{label}</div>
        <div className="text-lg font-bold text-slate-900 font-mono">{value}</div>
      </div>)}
    </div>}
    {data && <PaymentsTable payments={data.payments} />}
    {data?.truncated && <p className="text-xs text-slate-500">Showing the newest 500. Narrow the search to see older payments; the totals above include all of them.</p>}
  </section>;
}
