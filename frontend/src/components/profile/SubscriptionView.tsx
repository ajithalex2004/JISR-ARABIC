import React, { useEffect, useState } from 'react';
import { ArrowRight, FileText, RefreshCw } from 'lucide-react';
import { ChildProfile, PaymentReceipt, TaxInvoiceData } from '../../types';
import { api } from '../../services/api';

export const SubscriptionView: React.FC<{ activeChild: ChildProfile | null; onBack: () => void; onOpenPaywall: () => void }> = ({ activeChild, onBack, onOpenPaywall }) => {
  const [receipts, setReceipts] = useState<PaymentReceipt[]>([]);
  const [invoice, setInvoice] = useState<TaxInvoiceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = async () => {
    if (!activeChild?.id) return;
    setLoading(true); setError('');
    try { setReceipts(await api.getReceipts(activeChild.id)); } catch (e: any) { setError(e.message || 'Unable to load subscriptions'); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [activeChild?.id]);
  const showInvoice = async (receipt: string) => { try { setInvoice(await api.getTaxInvoice(receipt)); } catch (e: any) { setError(e.message || 'Unable to load invoice'); } };
  return <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <div className="flex items-center justify-between"><button onClick={onBack} className="text-sm font-bold text-slate-600 flex items-center gap-2"><ArrowRight className="w-4 h-4" />Back to Profile</button><button onClick={onOpenPaywall} className="px-4 py-2 bg-emerald-800 text-white text-xs font-bold">Purchase Access</button></div>
    <div><h1 className="text-xl font-black text-[#58337E]">My Subscriptions &amp; Invoices</h1><p className="text-xs text-slate-500 mt-1">Transaction history for {activeChild?.name || 'student'}</p></div>
    {error && <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs">{error}</div>}
    {loading ? <div className="p-6 text-sm text-slate-500">Loading transaction history…</div> : receipts.length === 0 ? <div className="p-6 bg-white border border-slate-200 text-sm text-slate-600">No subscriptions or invoices yet.</div> : <div className="bg-white border border-slate-200 divide-y">{receipts.map((r) => <div key={r.receipt_number} className="p-4 flex items-center justify-between gap-3"><div><div className="font-bold text-slate-800">{r.package_type === 'annual' ? 'Annual Pass' : `Term ${r.term}`}</div><div className="text-xs text-slate-500">{r.receipt_number} · USD {r.amount_usd.toFixed(2)} · {r.status}</div></div><button onClick={() => showInvoice(r.receipt_number)} className="text-xs font-bold text-[#58337E] flex items-center gap-1"><FileText className="w-4 h-4" />View Invoice</button></div>)}</div>}
    {invoice && <div className="p-5 bg-slate-50 border border-slate-300"><div className="flex justify-between"><h2 className="font-black">Invoice {invoice.invoice_number}</h2><button onClick={() => setInvoice(null)}>Close</button></div><div className="text-xs text-slate-600 mt-3">Total: USD {invoice.total_usd.toFixed(2)} · VAT: USD {invoice.vat_amount_usd.toFixed(2)}</div></div>}
  </div>;
};
