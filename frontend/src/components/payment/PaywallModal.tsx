import React, { useState } from 'react';
import {
  X, CreditCard, Lock, CheckCircle2, ShieldCheck, Tag, Sparkles,
  School, Receipt, Printer, ArrowRight, Building, AlertCircle
} from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, TaxInvoiceData } from '../../types';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
  grade: number;
  term: number;
  chapterName?: string;
  activeChild: ChildProfile | null;
  onPaymentSuccess: () => void;
}

export const PaywallModal: React.FC<PaywallModalProps> = ({
  isOpen,
  onClose,
  grade,
  term,
  chapterName = 'Ball Games / ألعاب الكرة',
  activeChild,
  onPaymentSuccess
}) => {
  const [selectedPlan, setSelectedPlan] = useState<'term' | 'annual' | 'voucher'>('annual');
  const [cardNumber, setCardNumber] = useState('4242 •••• •••• 4242');
  const [expDate, setExpDate] = useState('12/28');
  const [cvc, setCvc] = useState('123');
  const [promoCode, setPromoCode] = useState('');
  const [voucherCode, setVoucherCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successReceipt, setSuccessReceipt] = useState<string | null>(null);
  const [taxInvoice, setTaxInvoice] = useState<TaxInvoiceData | null>(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);

  if (!isOpen) return null;

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
          setIsProcessing(false);
          return;
        }
        const res = await api.redeemVoucher({
          child_id: activeChild.id,
          grade,
          code: voucherCode.trim()
        });
        setSuccessReceipt(res.receipt_number);
        // Load invoice
        try {
          const inv = await api.getTaxInvoice(res.receipt_number);
          setTaxInvoice(inv);
        } catch {
          // fallback
        }
        onPaymentSuccess();
      } else if (selectedPlan === 'annual') {
        const res = await api.checkoutAnnual({
          child_id: activeChild.id,
          grade,
          card_number: cardNumber.replace(/\D/g, '') || '4242424242424242',
          promo_code: promoCode.trim()
        });
        setSuccessReceipt(res.receipt_number);
        try {
          const inv = await api.getTaxInvoice(res.receipt_number);
          setTaxInvoice(inv);
        } catch {
          // fallback
        }
        onPaymentSuccess();
      } else {
        // Single term
        const res = await api.checkoutTerm({
          child_id: activeChild.id,
          grade,
          term,
          package_type: 'term',
          card_number: cardNumber.replace(/\D/g, '') || '4242424242424242',
          promo_code: promoCode.trim()
        });
        setSuccessReceipt(res.receipt_number);
        try {
          const inv = await api.getTaxInvoice(res.receipt_number);
          setTaxInvoice(inv);
        } catch {
          // fallback
        }
        onPaymentSuccess();
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Payment processing failed. Please verify card or voucher.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleViewInvoice = async () => {
    if (taxInvoice) {
      setShowInvoiceModal(true);
    } else if (successReceipt) {
      try {
        const inv = await api.getTaxInvoice(successReceipt);
        setTaxInvoice(inv);
        setShowInvoiceModal(true);
      } catch (err: any) {
        setErrorMsg('Failed to load tax invoice: ' + err.message);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/75 z-50 flex items-center justify-center p-4 overflow-y-auto">
      {/* Main Checkout Modal */}
      <div className="bg-white border-2 border-slate-900 w-full max-w-xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 p-1 border border-transparent hover:border-slate-300"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 pb-3 border-b-2 border-slate-900 mb-4">
          <div className="w-10 h-10 bg-amber-600 text-white flex items-center justify-center shrink-0">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
              Fahim AI · الباقات والاشتراكات
            </div>
            <h2 className="text-base font-black text-slate-900 uppercase tracking-tight">
              Unlock Curriculum & Exam Bank · Class {grade}
            </h2>
          </div>
        </div>

        {/* Freemium Explainer Banner */}
        <div className="bg-emerald-50 border-l-4 border-emerald-700 p-3 mb-4 text-xs text-emerald-950">
          <div className="font-bold flex items-center gap-1.5 mb-1 text-emerald-900">
            <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
            <span>Freemium Preview Active (النسخة التجريبية المجانية):</span>
          </div>
          <p className="leading-relaxed">
            Chapter 1 (<strong>{chapterName}</strong>) is 100% free with vocabulary cards, socratic tutor, and diagnostic checks. 
            Upgrade to a Term, Annual Pass, or School Voucher to unlock Chapters 2–10, all 5 Microlearning Capsules, Study Booklets (الملازم), and MoE practice exam models.
          </p>
        </div>

        {/* Success Confirmation & Invoice Trigger */}
        {successReceipt ? (
          <div className="space-y-4 py-4">
            <div className="p-4 bg-emerald-100 border-2 border-emerald-600 text-emerald-950">
              <div className="flex items-center gap-2 font-black text-sm mb-1">
                <CheckCircle2 className="w-5 h-5 text-emerald-700" />
                <span>Subscription Activated Successfully! (تم تفعيل الاشتراك بنجاح)</span>
              </div>
              <p className="text-xs mb-2">
                All curriculum materials, adaptive quizzes, and study booklets are now unlocked for {activeChild?.name || 'your student'}.
              </p>
              <div className="font-mono text-xs bg-white p-2 border border-emerald-400 inline-block font-bold">
                Receipt Number: {successReceipt}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <button
                type="button"
                onClick={handleViewInvoice}
                className="flex-1 py-3 px-4 bg-slate-900 text-white font-bold text-xs flex items-center justify-center gap-2 hover:bg-slate-800"
              >
                <Receipt className="w-4 h-4 text-amber-400" />
                <span>View UAE FTA Tax Invoice (الفاتورة الضريبية)</span>
              </button>
              <button
                type="button"
                onClick={onClose}
                className="py-3 px-6 bg-emerald-700 text-white font-bold text-xs hover:bg-emerald-800"
              >
                Start Learning Now
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Package Selection Tabs */}
            <div className="mb-4">
              <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Select Package or Institutional License (اختر الباقة المناسبة):
              </div>
              <div className="grid grid-cols-3 gap-2">
                {/* Annual Pass Card */}
                <button
                  type="button"
                  onClick={() => setSelectedPlan('annual')}
                  className={`p-3 text-left border-2 transition-all relative ${
                    selectedPlan === 'annual'
                      ? 'border-emerald-800 bg-emerald-50/70 shadow-sm'
                      : 'border-slate-300 hover:border-slate-500 bg-white'
                  }`}
                >
                  <div className="absolute top-0 right-0 bg-amber-600 text-white text-[9px] font-black px-1.5 py-0.5 uppercase tracking-wider">
                    SAVE 15%
                  </div>
                  <div className="text-xs font-black text-slate-900">Annual Pass</div>
                  <div className="text-[10px] text-slate-600">Terms 1, 2, & 3</div>
                  <div className="mt-2 text-sm font-black text-emerald-800">
                    USD 50
                  </div>
                  <div className="text-[10px] text-slate-500">~AED 183.62 / Year</div>
                </button>

                {/* Single Term Card */}
                <button
                  type="button"
                  onClick={() => setSelectedPlan('term')}
                  className={`p-3 text-left border-2 transition-all ${
                    selectedPlan === 'term'
                      ? 'border-emerald-800 bg-emerald-50/70 shadow-sm'
                      : 'border-slate-300 hover:border-slate-500 bg-white'
                  }`}
                >
                  <div className="text-xs font-black text-slate-900">Single Term</div>
                  <div className="text-[10px] text-slate-600">Each Term</div>
                  <div className="mt-2 text-sm font-black text-slate-900">
                    USD 20
                  </div>
                  <div className="text-[10px] text-slate-500">~AED 73.45 / Term</div>
                </button>

                {/* School Voucher Card */}
                <button
                  type="button"
                  onClick={() => setSelectedPlan('voucher')}
                  className={`p-3 text-left border-2 transition-all ${
                    selectedPlan === 'voucher'
                      ? 'border-emerald-800 bg-emerald-50/70 shadow-sm'
                      : 'border-slate-300 hover:border-slate-500 bg-white'
                  }`}
                >
                  <div className="flex items-center gap-1 text-xs font-black text-slate-900">
                    <Building className="w-3.5 h-3.5 text-amber-700" />
                    <span>School Pass</span>
                  </div>
                  <div className="text-[10px] text-slate-600">Institutional Code</div>
                  <div className="mt-2 text-sm font-black text-amber-700">
                    Free / Pass
                  </div>
                  <div className="text-[10px] text-slate-500">ADEK & Partner Schools</div>
                </button>
              </div>
            </div>

            {/* Plan Details Callout */}
            <div className="bg-slate-100 p-3 border border-slate-300 mb-4 text-xs">
              {selectedPlan === 'annual' && (
                <div className="space-y-1">
                  <div className="font-bold text-slate-900 flex items-center justify-between">
                    <span>Full Academic Year Comprehensive Pass (Class {grade})</span>
                    <span className="font-black text-emerald-800">USD 50.00 (Incl. 5% UAE VAT)</span>
                  </div>
                  <ul className="text-slate-600 text-[11px] list-disc list-inside space-y-0.5">
                    <li>Unlimited access to all 30 lessons across Terms 1, 2, and 3</li>
                    <li>Full interactive Study Booklets (الملازم الذكية) with study & review modes</li>
                    <li>All 5 Microlearning Capsules with interactive checkpoint quizzes</li>
                  </ul>
                </div>
              )}
              {selectedPlan === 'term' && (
                <div className="space-y-1">
                  <div className="font-bold text-slate-900 flex items-center justify-between">
                    <span>Single Term Access (Class {grade} · Term {term})</span>
                    <span className="font-black text-slate-900">USD 20.00 (Incl. 5% UAE VAT)</span>
                  </div>
                  <p className="text-slate-600 text-[11px]">
                    Unlocks all 10 chapters in Term {term}, grammar lab exercises, and teacher feedback queue for {activeChild?.name || 'learner'}.
                  </p>
                </div>
              )}
              {selectedPlan === 'voucher' && (
                <div className="space-y-1">
                  <div className="font-bold text-slate-900 flex items-center justify-between">
                    <span>School-Sponsored License Redemption (قسيمة المدرسة)</span>
                    <span className="font-black text-amber-700">100% Institutionally Sponsored</span>
                  </div>
                  <p className="text-slate-600 text-[11px]">
                    Enter the license code provided by your school (e.g. <strong>SUNRISE2026</strong> or <strong>ADEK-ARABIC-100</strong>) to unlock immediate full access.
                  </p>
                </div>
              )}
            </div>

            {errorMsg && (
              <div className="mb-4 p-2.5 bg-red-50 border-l-4 border-red-600 text-red-700 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Form Fields */}
            <form onSubmit={handleCheckout} className="space-y-3">
              {selectedPlan === 'voucher' ? (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    School License Voucher Code (رمز قسيمة المدرسة)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={voucherCode}
                      onChange={(e) => setVoucherCode(e.target.value.toUpperCase())}
                      placeholder="e.g. SUNRISE2026 or ADEK-ARABIC-100"
                      className="sharp-input flex-1 font-mono uppercase text-xs"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setVoucherCode('SUNRISE2026')}
                      className="px-2.5 py-1.5 bg-slate-200 hover:bg-slate-300 border border-slate-400 text-[11px] font-bold"
                    >
                      Use SUNRISE2026
                    </button>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Direct institutional authorization from partner schools and educational authorities.
                  </div>
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Card Number (UAE Central Bank / Simulation Enabled)
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={cardNumber}
                        onChange={(e) => setCardNumber(e.target.value)}
                        className="sharp-input w-full pl-8 font-mono text-xs"
                        placeholder="4242 4242 4242 4242"
                      />
                      <CreditCard className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Expiry Date</label>
                      <input
                        type="text"
                        value={expDate}
                        onChange={(e) => setExpDate(e.target.value)}
                        className="sharp-input w-full text-xs font-mono"
                        placeholder="MM/YY"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">CVC / CVV</label>
                      <input
                        type="password"
                        maxLength={4}
                        value={cvc}
                        onChange={(e) => setCvc(e.target.value)}
                        className="sharp-input w-full text-xs font-mono"
                        placeholder="123"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Promotional Code (رمز الخصم)
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={promoCode}
                        onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                        placeholder="Enter promo code"
                        className="sharp-input flex-1 text-xs uppercase font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setPromoCode((value) => value.trim())}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-[11px] font-bold"
                      >
                        Apply Promo
                      </button>
                    </div>
                  </div>
                </>
              )}

              {/* Action Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="w-full py-3 text-sm font-bold bg-emerald-800 hover:bg-emerald-900 text-white flex items-center justify-center gap-2 border-2 border-slate-900 shadow-[2px_2px_0px_0px_#0f172a] active:translate-x-[1px] active:translate-y-[1px]"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>
                    {isProcessing
                      ? 'Validating & Activating...'
                      : selectedPlan === 'voucher'
                      ? 'Redeem School Voucher & Unlock'
                      : selectedPlan === 'annual'
                      ? 'Pay USD 50 & Unlock Full Academic Year'
                      : `Pay USD 20 & Unlock Term ${term}`}
                  </span>
                </button>
              </div>

              {/* UAE FTA Invoicing Guarantee */}
              <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200">
                <span>✓ UAE TRN: 100458923100003</span>
                <span>✓ 5% FTA VAT Itemized</span>
                <span>✓ Instant curriculum activation</span>
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
