import React, { useEffect, useState } from 'react';
import { ArrowRight, FileText, Printer, RefreshCw } from 'lucide-react';
import { ChildProfile, PaymentReceipt, Subscription, TaxInvoiceData } from '../../types';
import { api } from '../../services/api';

const date = (iso: string | null) => iso ? new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : '—';

function receiptLabel(r: PaymentReceipt) {
  const terms = (r.terms_purchased || '').split(',').filter(Boolean);
  const what = r.package_type === 'annual' || terms.length === 3 ? 'Full year (Terms 1, 2 & 3)'
    : terms.length > 1 ? `Terms ${terms.join(', ')}` : `Term ${terms[0] || r.term}`;
  return `${what} · Class ${r.grade}${r.subscription_id ? ' · auto-renewing' : ''}`;
}

function SubscriptionRow({ sub, onChange }: { sub: Subscription; onChange: (s: Subscription) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const toggle = async (renew: boolean) => {
    if (!renew && !window.confirm(`Turn off auto-renew for ${sub.child_name}? Access stays until ${date(sub.current_period_end)}.`)) return;
    setBusy(true); setError('');
    try { onChange(await api.setAutoRenew(sub.id, renew)); } catch (e: any) { setError(e.message); } finally { setBusy(false); }
  };
  const ended = sub.status === 'canceled';
  return <div className="p-4 flex flex-wrap items-center justify-between gap-3">
    <div>
      <div className="font-bold text-slate-800">
        {sub.plan === 'annual' ? 'Full year' : 'Per term'} · {sub.child_name} · Class {sub.grade}
      </div>
      <div className="text-xs text-slate-500">
        USD {sub.renewal_price_usd.toFixed(2)} every {sub.renewal_months} months
        {sub.plan === 'term' && sub.next_term ? ` · next: Term ${sub.next_term}` : ''}
      </div>
      <div className={`text-xs font-semibold ${ended ? 'text-slate-500' : sub.status === 'past_due' ? 'text-red-700' : 'text-emerald-800'}`}>
        {ended ? 'Ended'
          : sub.status === 'past_due' ? 'Renewal payment failed: please update your card'
          : sub.cancel_at_period_end ? `Auto-renew off · access until ${date(sub.current_period_end)}`
          : `Renews on ${date(sub.current_period_end)}`}
      </div>
      {error && <div role="alert" className="text-xs text-red-700">{error}</div>}
    </div>
    {!ended && (sub.cancel_at_period_end
      ? <button disabled={busy} onClick={() => toggle(true)} className="px-3 py-1.5 text-xs font-bold bg-emerald-800 text-white disabled:opacity-50">Turn auto-renew back on</button>
      : <button disabled={busy} onClick={() => toggle(false)} className="px-3 py-1.5 text-xs font-bold border border-slate-400 disabled:opacity-50">Cancel auto-renew</button>)}
  </div>;
}

export const SubscriptionView: React.FC<{ activeChild: ChildProfile | null; onBack: () => void; onOpenPaywall: () => void }> = ({ activeChild, onBack, onOpenPaywall }) => {
  const [receipts, setReceipts] = useState<PaymentReceipt[]>([]);
  const [subs, setSubs] = useState<Subscription[]>([]);
  const [invoice, setInvoice] = useState<TaxInvoiceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = async () => {
    setLoading(true); setError('');
    try {
      const [r, s] = await Promise.all([
        activeChild?.id ? api.getReceipts(activeChild.id) : Promise.resolve([]),
        api.mySubscriptions().catch(() => []),
      ]);
      setReceipts(r); setSubs(s);
    } catch (e: any) { setError(e.message || 'Unable to load subscriptions'); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [activeChild?.id]);
  const showInvoice = async (receipt: string) => { try { setInvoice(await api.getTaxInvoice(receipt)); } catch (e: any) { setError(e.message || 'Unable to load invoice'); } };

  return <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <div className="flex items-center justify-between"><button onClick={onBack} className="text-sm font-bold text-slate-600 flex items-center gap-2"><ArrowRight className="w-4 h-4" />Back to Profile</button><button onClick={onOpenPaywall} className="px-4 py-2 bg-emerald-800 text-white text-xs font-bold">Purchase Access</button></div>
    <div><h1 className="text-xl font-black text-[#58337E]">My Subscriptions &amp; Invoices</h1><p className="text-xs text-slate-500 mt-1">Auto-renewing plans for your family, and the receipts and tax invoices for {activeChild?.name || 'your student'}</p></div>
    {error && <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs">{error}</div>}

    <section className="space-y-2">
      <h2 className="font-bold text-slate-800 flex items-center gap-1.5"><RefreshCw className="w-4 h-4" /> Auto-renewing plans</h2>
      {loading ? <div className="p-4 text-sm text-slate-500">Loading…</div>
        : subs.length === 0 ? <div className="p-4 bg-white border border-slate-200 text-sm text-slate-600">No auto-renewing plans. You can turn on auto-renew when you buy a term or the full year.</div>
        : <div className="bg-white border border-slate-200 divide-y">{subs.map(s => <SubscriptionRow key={s.id} sub={s} onChange={u => setSubs(list => list.map(x => x.id === u.id ? { ...x, ...u } : x))} />)}</div>}
    </section>

    <section className="space-y-2">
      <h2 className="font-bold text-slate-800 flex items-center gap-1.5"><FileText className="w-4 h-4" /> Receipts &amp; tax invoices</h2>
      {loading ? <div className="p-4 text-sm text-slate-500">Loading transaction history…</div>
        : receipts.length === 0 ? <div className="p-4 bg-white border border-slate-200 text-sm text-slate-600">No payments yet.</div>
        : <div className="bg-white border border-slate-200 divide-y">{receipts.map((r) => <div key={r.receipt_number} className="p-4 flex items-center justify-between gap-3">
          <div>
            <div className="font-bold text-slate-800">{receiptLabel(r)}</div>
            <div className="text-xs text-slate-500">{date(r.created_at)} · Receipt {r.receipt_number} · Invoice {r.tax_invoice_number} · USD {r.amount_usd.toFixed(2)} · {r.status}</div>
          </div>
          <button onClick={() => showInvoice(r.receipt_number)} className="text-xs font-bold text-[#58337E] flex items-center gap-1 shrink-0"><FileText className="w-4 h-4" />View Invoice</button>
        </div>)}</div>}
    </section>

    {invoice && <div className="p-5 bg-white border-2 border-slate-900 space-y-3 text-xs print:border-none">
      <div className="flex justify-between items-start">
        <div>
          <div className="font-black text-base">TAX INVOICE / فاتورة ضريبية</div>
          <div className="font-mono">{invoice.invoice_number} · {invoice.issue_date}</div>
          <div className="text-slate-600">JISR Arabic Educational Technologies FZ-LLC · TRN {invoice.trn}</div>
        </div>
        <div className="flex gap-2 print:hidden">
          <button onClick={() => window.print()} className="px-2 py-1 bg-slate-900 text-white font-bold flex items-center gap-1"><Printer className="w-3.5 h-3.5" />Print</button>
          <button onClick={() => setInvoice(null)} className="px-2 py-1 border border-slate-400 font-bold">Close</button>
        </div>
      </div>
      <div>Customer: <strong>{invoice.parent_name}</strong> ({invoice.parent_email}) · Student: <strong>{invoice.student_name}</strong>, Class {invoice.grade}</div>
      <table className="w-full border border-slate-300">
        <thead className="bg-slate-100"><tr><th className="p-1.5 text-left">Description</th><th className="p-1.5 text-right">Price</th><th className="p-1.5 text-right">Discount</th><th className="p-1.5 text-right">VAT 5%</th><th className="p-1.5 text-right">Total</th></tr></thead>
        <tbody>{invoice.items.map((item, i) => <tr key={i} className="border-t border-slate-200">
          <td className="p-1.5">{item.description_en}<div dir="rtl" className="text-slate-500">{item.description_ar}</div></td>
          <td className="p-1.5 text-right font-mono">{item.unit_price_usd.toFixed(2)}</td>
          <td className="p-1.5 text-right font-mono">{(item.discount_usd || 0).toFixed(2)}</td>
          <td className="p-1.5 text-right font-mono">{item.vat_amount_usd.toFixed(2)}</td>
          <td className="p-1.5 text-right font-mono font-bold">{item.total_usd.toFixed(2)}</td>
        </tr>)}</tbody>
      </table>
      <div className="text-right space-y-0.5">
        <div>Taxable amount: <span className="font-mono">USD {invoice.subtotal_usd.toFixed(2)}</span></div>
        <div>VAT 5%: <span className="font-mono">USD {invoice.vat_amount_usd.toFixed(2)}</span></div>
        <div className="font-black">Total: <span className="font-mono">USD {invoice.total_usd.toFixed(2)} (AED {invoice.total_aed.toFixed(2)})</span></div>
        <div className="text-slate-500">Payment: {invoice.payment_method} · {invoice.status}</div>
      </div>
    </div>}
  </div>;
};
