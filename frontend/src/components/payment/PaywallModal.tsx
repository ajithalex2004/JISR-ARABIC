import React, { useEffect, useMemo, useState } from 'react';
import {
  X, Lock, CheckCircle2, ShieldCheck, Receipt, Printer, Building, AlertCircle, RefreshCw, Tag
} from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, PriceQuote, TaxInvoiceData } from '../../types';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
  grade: number;
  term: number;
  chapterName?: string;
  activeChild: ChildProfile | null;
  onPaymentSuccess: () => void;
}

// Prices (USD, 5% UAE VAT included). The server is the source of truth; these only label the plan cards.
const TERM_USD = 10;
const ANNUAL_LIST_USD = 30;
const ANNUAL_USD = 25.5;
const AED = 3.6725;
const usd = (n: number) => `USD ${n.toFixed(2)}`;
const aed = (n: number) => `AED ${(n * AED).toFixed(2)}`;

export const PaywallModal: React.FC<PaywallModalProps> = ({
  isOpen,
  onClose,
  grade,
  term,
  chapterName,
  activeChild,
  onPaymentSuccess
}) => {
  const [selectedPlan, setSelectedPlan] = useState<'term' | 'annual' | 'voucher'>('annual');
  const [terms, setTerms] = useState<number[]>([term]);
  const [autoRenew, setAutoRenew] = useState(true);
  const [promoCode, setPromoCode] = useState('');
  const [appliedPromo, setAppliedPromo] = useState('');
  const [quote, setQuote] = useState<PriceQuote | null>(null);
  const [voucherCode, setVoucherCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [promoMsg, setPromoMsg] = useState('');
  const [successReceipt, setSuccessReceipt] = useState<string | null>(null);
  const [taxInvoice, setTaxInvoice] = useState<TaxInvoiceData | null>(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);

  useEffect(() => { setTerms([term]); }, [term]);

  const plan: 'term' | 'annual' = selectedPlan === 'annual' || terms.length === 3 ? 'annual' : 'term';
  const chosenTerms = plan === 'annual' ? [1, 2, 3] : terms;
  const canAutoRenew = plan === 'annual' || chosenTerms.length === 1;
  const body = useMemo(() => activeChild ? {
    child_id: activeChild.id, plan, terms: chosenTerms, promo_code: appliedPromo || undefined,
    auto_renew: canAutoRenew && autoRenew,
  } : null, [activeChild?.id, plan, chosenTerms.join(','), appliedPromo, autoRenew, canAutoRenew]);

  // Live price from the server (validates the promo code too).
  useEffect(() => {
    if (!isOpen || !body || selectedPlan === 'voucher') return;
    let cancelled = false;
    api.quotePayment(body)
      .then(q => { if (!cancelled) { setQuote(q); setPromoMsg(appliedPromo ? `${appliedPromo} applied: you save ${usd(q.promo_discount_usd)}` : ''); } })
      .catch((e: any) => {
        if (cancelled) return;
        if (appliedPromo) { setPromoMsg(e.message); setAppliedPromo(''); } else setErrorMsg(e.message);
      });
    return () => { cancelled = true; };
  }, [isOpen, body, selectedPlan]);

  if (!isOpen) return null;

  const total = quote?.total_usd ?? (plan === 'annual' ? ANNUAL_USD : TERM_USD * chosenTerms.length);

  const toggleTerm = (t: number) => {
    setTerms(prev => prev.includes(t) ? (prev.length > 1 ? prev.filter(x => x !== t) : prev) : [...prev, t].sort());
  };

  const showReceipt = async (receipt: string) => {
    setSuccessReceipt(receipt);
    try { setTaxInvoice(await api.getTaxInvoice(receipt)); } catch { /* shown on demand */ }
    onPaymentSuccess();
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChild) {
      setErrorMsg('Please select or create a child profile before unlocking.');
      return;
    }
    setErrorMsg('');
    setIsProcessing(true);
    try {
      if (selectedPlan === 'voucher') {
        if (!voucherCode.trim()) {
          setErrorMsg('Please enter your school or institutional voucher code.');
          return;
        }
        const res = await api.redeemVoucher({ child_id: activeChild.id, grade, code: voucherCode.trim() });
        await showReceipt(res.receipt_number);
        return;
      }
      const res = await api.startCheckout({ ...body!, grade });
      if (res.provider === 'stripe' && res.checkout_url) {
        window.location.href = res.checkout_url; // Stripe's secure payment page; it returns to the app afterwards
        return;
      }
      if (res.receipt_number) await showReceipt(res.receipt_number);
    } catch (err: any) {
      setErrorMsg(err.message || 'Payment could not be completed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleViewInvoice = async () => {
    if (taxInvoice) {
      setShowInvoiceModal(true);
    } else if (successReceipt) {
      try {
        setTaxInvoice(await api.getTaxInvoice(successReceipt));
        setShowInvoiceModal(true);
      } catch (err: any) {
        setErrorMsg('Failed to load tax invoice: ' + err.message);
      }
    }
  };

  const planCard = (id: 'annual' | 'term' | 'voucher', content: React.ReactNode, badge?: string) => (
    <button
      type="button"
      onClick={() => { setSelectedPlan(id); setErrorMsg(''); }}
      className={`p-3 text-left border-2 transition-all relative ${
        selectedPlan === id ? 'border-emerald-800 bg-emerald-50/70 shadow-sm' : 'border-slate-300 hover:border-slate-500 bg-white'
      }`}
    >
      {badge && <div className="absolute top-0 right-0 bg-amber-600 text-white text-[9px] font-black px-1.5 py-0.5 uppercase tracking-wider">{badge}</div>}
      {content}
    </button>
  );

  return (
    <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white border-2 border-slate-900 w-full max-w-xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} aria-label="Close" className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 p-1 border border-transparent hover:border-slate-300">
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 pb-3 border-b-2 border-slate-900 mb-4">
          <div className="w-10 h-10 bg-amber-600 text-white flex items-center justify-center shrink-0">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">Fahim AI · الباقات والاشتراكات</div>
            <h2 className="text-base font-black text-slate-900 uppercase tracking-tight">Unlock Curriculum & Exam Bank · Class {grade}</h2>
          </div>
        </div>

        <div className="bg-emerald-50 border-l-4 border-emerald-700 p-3 mb-4 text-xs text-emerald-950">
          <div className="font-bold flex items-center gap-1.5 mb-1 text-emerald-900">
            <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
            <span>Freemium Preview Active (النسخة التجريبية المجانية):</span>
          </div>
          <p className="leading-relaxed">
            Chapter 1{chapterName ? <> (<strong>{chapterName}</strong>)</> : null} of your enrolled grade is 100% free.
            Unlock a term for {usd(TERM_USD)}, or the full year for {usd(ANNUAL_USD)} (save 15%), to open every chapter, the study booklets and the exam practice.
          </p>
        </div>

        {successReceipt ? (
          <div className="space-y-4 py-4">
            <div className="p-4 bg-emerald-100 border-2 border-emerald-600 text-emerald-950">
              <div className="flex items-center gap-2 font-black text-sm mb-1">
                <CheckCircle2 className="w-5 h-5 text-emerald-700" />
                <span>Payment successful (تم الدفع بنجاح)</span>
              </div>
              <p className="text-xs mb-2">Access is now unlocked for {activeChild?.name || 'your student'}. A receipt and UAE tax invoice have been issued.</p>
              <div className="font-mono text-xs bg-white p-2 border border-emerald-400 inline-block font-bold">Receipt Number: {successReceipt}</div>
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
              <button type="button" onClick={handleViewInvoice} className="flex-1 py-3 px-4 bg-slate-900 text-white font-bold text-xs flex items-center justify-center gap-2 hover:bg-slate-800">
                <Receipt className="w-4 h-4 text-amber-400" />
                <span>View UAE Tax Invoice (الفاتورة الضريبية)</span>
              </button>
              <button type="button" onClick={onClose} className="py-3 px-6 bg-emerald-700 text-white font-bold text-xs hover:bg-emerald-800">Start Learning Now</button>
            </div>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Choose a plan (اختر الباقة المناسبة):</div>
              <div className="grid grid-cols-3 gap-2">
                {planCard('annual', <>
                  <div className="text-xs font-black text-slate-900">Full Year</div>
                  <div className="text-[10px] text-slate-600">Terms 1, 2 & 3</div>
                  <div className="mt-2 text-[11px] text-slate-400 line-through">{usd(ANNUAL_LIST_USD)}</div>
                  <div className="text-sm font-black text-emerald-800">{usd(ANNUAL_USD)}</div>
                  <div className="text-[10px] text-slate-500">~{aed(ANNUAL_USD)} / year</div>
                </>, 'Save 15%')}
                {planCard('term', <>
                  <div className="text-xs font-black text-slate-900">Per Term</div>
                  <div className="text-[10px] text-slate-600">Choose the term(s)</div>
                  <div className="mt-2 text-sm font-black text-slate-900">{usd(TERM_USD)}</div>
                  <div className="text-[10px] text-slate-500">~{aed(TERM_USD)} / term</div>
                </>)}
                {planCard('voucher', <>
                  <div className="flex items-center gap-1 text-xs font-black text-slate-900">
                    <Building className="w-3.5 h-3.5 text-amber-700" />
                    <span>School Pass</span>
                  </div>
                  <div className="text-[10px] text-slate-600">Institutional Code</div>
                  <div className="mt-2 text-sm font-black text-amber-700">Free / Pass</div>
                  <div className="text-[10px] text-slate-500">Partner schools</div>
                </>)}
              </div>
            </div>

            {errorMsg && (
              <div role="alert" className="mb-4 p-2.5 bg-red-50 border-l-4 border-red-600 text-red-700 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleCheckout} className="space-y-3">
              {selectedPlan === 'voucher' ? (
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-700">School License Voucher Code (رمز قسيمة المدرسة)</label>
                  <input
                    type="text"
                    value={voucherCode}
                    onChange={(e) => setVoucherCode(e.target.value.toUpperCase())}
                    placeholder="Code from your school"
                    className="sharp-input w-full font-mono uppercase text-xs"
                    required
                  />
                  <div className="text-[11px] text-slate-500">Unlocks access paid for by your school. A receipt and tax invoice are still issued.</div>
                </div>
              ) : (
                <>
                  {selectedPlan === 'term' && (
                    <fieldset className="border border-slate-300 p-3">
                      <legend className="text-xs font-bold text-slate-700 px-1">Terms for Class {grade}</legend>
                      <div className="flex flex-wrap gap-3">
                        {[1, 2, 3].map(t => (
                          <label key={t} className="flex items-center gap-1.5 text-xs font-semibold">
                            <input type="checkbox" checked={terms.includes(t)} onChange={() => toggleTerm(t)} />
                            Term {t} · {usd(TERM_USD)}
                          </label>
                        ))}
                      </div>
                      {terms.length === 3 && <div className="text-[11px] text-emerald-800 mt-1">All three terms together get the 15% full-year discount.</div>}
                    </fieldset>
                  )}

                  <label className={`flex items-start gap-2 text-xs p-3 border ${canAutoRenew ? 'border-emerald-300 bg-emerald-50/50' : 'border-slate-200 bg-slate-50 text-slate-400'}`}>
                    <input type="checkbox" className="mt-0.5" disabled={!canAutoRenew} checked={canAutoRenew && autoRenew} onChange={e => setAutoRenew(e.target.checked)} />
                    <span>
                      <span className="font-bold flex items-center gap-1"><RefreshCw className="w-3.5 h-3.5" /> Renew automatically (تجديد تلقائي)</span>
                      {canAutoRenew
                        ? (plan === 'annual'
                          ? <>Charged {usd(ANNUAL_USD)} every 12 months for the next school year. Cancel anytime in My Subscriptions.</>
                          : <>Charged {usd(TERM_USD)} every 4 months, unlocking the next term each time. Cancel anytime in My Subscriptions.</>)
                        : <>Auto-renew is available for one term at a time or for the full year.</>}
                    </span>
                  </label>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Promo code (رمز الخصم)</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={promoCode}
                        onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                        placeholder="e.g. JISR10"
                        className="sharp-input flex-1 text-xs uppercase font-mono"
                      />
                      <button type="button" onClick={() => { setErrorMsg(''); setAppliedPromo(promoCode.trim()); }}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-[11px] font-bold flex items-center gap-1">
                        <Tag className="w-3.5 h-3.5" /> Apply
                      </button>
                    </div>
                    {promoMsg && <div className={`text-[11px] mt-1 ${appliedPromo ? 'text-emerald-800' : 'text-red-700'}`}>{promoMsg}</div>}
                  </div>

                  {quote && (
                    <div className="border border-slate-300 bg-slate-50 p-3 text-xs space-y-0.5" aria-label="Price breakdown">
                      <div className="flex justify-between"><span>{plan === 'annual' ? 'Terms 1, 2 & 3' : `Term${chosenTerms.length > 1 ? 's' : ''} ${chosenTerms.join(', ')}`}</span><span className="font-mono">{usd(quote.list_price_usd)}</span></div>
                      {quote.annual_discount_usd > 0 && <div className="flex justify-between text-emerald-800"><span>Full-year discount (15%)</span><span className="font-mono">−{usd(quote.annual_discount_usd)}</span></div>}
                      {quote.promo_discount_usd > 0 && <div className="flex justify-between text-emerald-800"><span>Promo {quote.promo_code}{quote.auto_renew ? ' (first payment)' : ''}</span><span className="font-mono">−{usd(quote.promo_discount_usd)}</span></div>}
                      <div className="flex justify-between font-black text-slate-900 border-t border-slate-300 pt-1"><span>Total today</span><span className="font-mono">{usd(quote.total_usd)}</span></div>
                      <div className="flex justify-between text-slate-500"><span>Includes 5% UAE VAT</span><span className="font-mono">{usd(quote.vat_usd)}</span></div>
                      {quote.auto_renew && quote.renewal_price_usd && <div className="text-slate-600 pt-1">Then {usd(quote.renewal_price_usd)} every {quote.renewal_months} months until you cancel.</div>}
                    </div>
                  )}
                </>
              )}

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="w-full py-3 text-sm font-bold bg-emerald-800 hover:bg-emerald-900 text-white flex items-center justify-center gap-2 border-2 border-slate-900 shadow-[2px_2px_0px_0px_#0f172a] disabled:opacity-60"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>
                    {isProcessing
                      ? 'Please wait…'
                      : selectedPlan === 'voucher'
                      ? 'Redeem School Voucher & Unlock'
                      : `Pay ${usd(total)} securely${quote?.provider === 'stripe' ? ' with card' : ''}`}
                  </span>
                </button>
                {selectedPlan !== 'voucher' && quote?.provider === 'stripe' && (
                  <div className="text-[11px] text-slate-500 mt-1 text-center">You will enter your card on Stripe's secure page and come straight back here.</div>
                )}
                {selectedPlan !== 'voucher' && quote?.provider === 'simulated' && (
                  <div className="text-[11px] text-amber-700 mt-1 text-center">Test mode: no card is charged.</div>
                )}
              </div>

              <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200">
                <span>✓ UAE TRN: 100458923100003</span>
                <span>✓ Receipt & UAE tax invoice for every payment</span>
                <span>✓ 5% VAT included</span>
              </div>
            </form>
          </>
        )}
      </div>

      {/* UAE FTA Tax Invoice Modal */}
      {showInvoiceModal && taxInvoice && (
        <div className="fixed inset-0 bg-slate-950/80 z-[60] flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border-2 border-slate-900 w-full max-w-2xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto print:border-none print:shadow-none">
            <button
              onClick={() => setShowInvoiceModal(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 p-1 print:hidden"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Printable Invoice Header */}
            <div className="border-b-2 border-slate-900 pb-4 mb-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xl font-black text-slate-900 uppercase tracking-tight">
                    FAHIM AI (فهيم للتعليم الذكي)
                  </div>
                  <div className="text-xs text-slate-600">
                    JISR Arabic Educational Technologies FZ-LLC
                  </div>
                  <div className="text-xs text-slate-600 font-mono">
                    TRN: <strong className="text-slate-900">{taxInvoice.trn}</strong>
                  </div>
                  <div className="text-xs text-slate-500">Abu Dhabi · United Arab Emirates</div>
                </div>
                <div className="text-right">
                  <div className="inline-block bg-emerald-800 text-white font-black text-xs px-2.5 py-1 uppercase tracking-wider mb-1">
                    TAX INVOICE / فاتورة ضريبية
                  </div>
                  <div className="font-mono text-xs font-bold text-slate-900">
                    {taxInvoice.invoice_number}
                  </div>
                  <div className="text-[11px] text-slate-500">{taxInvoice.issue_date}</div>
                </div>
              </div>
            </div>

            {/* Bill To Info */}
            <div className="grid grid-cols-2 gap-4 bg-slate-50 p-3 border border-slate-300 mb-4 text-xs">
              <div>
                <div className="font-bold text-slate-500 uppercase text-[10px]">Customer / العميل:</div>
                <div className="font-bold text-slate-900">{taxInvoice.parent_name}</div>
                <div className="text-slate-600">{taxInvoice.parent_email}</div>
              </div>
              <div>
                <div className="font-bold text-slate-500 uppercase text-[10px]">Student & Institution:</div>
                <div className="font-bold text-slate-900">
                  {taxInvoice.student_name} (Class {taxInvoice.grade})
                </div>
                <div className="text-slate-600">{taxInvoice.school_name}</div>
              </div>
            </div>

            {/* Itemized Line Items Table */}
            <table className="w-full text-xs border border-slate-300 mb-4">
              <thead className="bg-slate-900 text-white font-bold">
                <tr>
                  <th className="p-2 text-left">Description / البيان</th>
                  <th className="p-2 text-center">Qty</th>
                  <th className="p-2 text-right">Unit Price</th>
                  <th className="p-2 text-right">VAT (5%)</th>
                  <th className="p-2 text-right">Total (USD)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {taxInvoice.items.map((item, idx) => (
                  <tr key={idx}>
                    <td className="p-2">
                      <div className="font-bold text-slate-900">{item.description_en}</div>
                      <div className="text-slate-500 font-arabic text-[11px]" dir="rtl">
                        {item.description_ar}
                      </div>
                    </td>
                    <td className="p-2 text-center font-mono">{item.qty}</td>
                    <td className="p-2 text-right font-mono">${item.unit_price_usd.toFixed(2)}</td>
                    <td className="p-2 text-right font-mono">${item.vat_amount_usd.toFixed(2)}</td>
                    <td className="p-2 text-right font-mono font-bold text-slate-900">
                      ${item.total_usd.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Total Breakdown */}
            <div className="flex justify-end mb-4">
              <div className="w-64 space-y-1 text-xs border border-slate-300 p-3 bg-slate-50">
                <div className="flex justify-between text-slate-600">
                  <span>Taxable Subtotal (excl. VAT):</span>
                  <span className="font-mono font-bold">${taxInvoice.subtotal_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>UAE 5% VAT (ضريبة القيمة المضافة):</span>
                  <span className="font-mono font-bold">${taxInvoice.vat_amount_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm font-black text-slate-900 border-t border-slate-300 pt-1">
                  <span>Gross Total (USD):</span>
                  <span className="font-mono">${taxInvoice.total_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs font-black text-emerald-800">
                  <span>Total Payable in AED:</span>
                  <span className="font-mono">AED {taxInvoice.total_aed.toFixed(2)}</span>
                </div>
                <div className="text-[10px] text-slate-500 text-right">
                  Fixed Rate: 1 USD = 3.6725 AED
                </div>
              </div>
            </div>

            {/* Payment Method & Status Stamp */}
            <div className="flex items-center justify-between border-t border-slate-200 pt-3 text-xs">
              <div className="text-slate-600">
                Payment Method: <strong className="text-slate-900 uppercase font-mono">{taxInvoice.payment_method}</strong> · Status: <strong className="text-emerald-800 uppercase">{taxInvoice.status}</strong>
              </div>
              <div className="flex gap-2 print:hidden">
                <button
                  onClick={() => window.print()}
                  className="px-3 py-1.5 bg-slate-900 text-white font-bold text-xs flex items-center gap-1.5 hover:bg-slate-800"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Invoice</span>
                </button>
                <button
                  onClick={() => setShowInvoiceModal(false)}
                  className="px-3 py-1.5 bg-slate-200 text-slate-800 font-bold text-xs hover:bg-slate-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
