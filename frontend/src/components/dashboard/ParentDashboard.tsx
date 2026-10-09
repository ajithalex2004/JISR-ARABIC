import React, { useState, useEffect } from 'react';
import {
  UserCheck, Award, Printer, AlertCircle, FileCheck, DollarSign, Clock,
  CheckCircle2, Compass, Sparkles, Calendar, Mail, Bell, Send, HeartHandshake,
  HelpCircle, Volume2, Receipt, X, Building
} from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, WeeklyDigestData, ActionableGuidanceData, TaxInvoiceData } from '../../types';

interface ParentDashboardProps {
  activeChild: ChildProfile | null;
  onOpenPaywall: () => void;
  onOpenOnboarding?: () => void;
}

export const ParentDashboard: React.FC<ParentDashboardProps> = ({ activeChild, onOpenPaywall, onOpenOnboarding }) => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [receipts, setReceipts] = useState<any[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<TaxInvoiceData | null>(null);
  const [weeklyDigest, setWeeklyDigest] = useState<WeeklyDigestData | null>(null);
  const [actionableGuidance, setActionableGuidance] = useState<ActionableGuidanceData | null>(null);
  const [dispatchStatus, setDispatchStatus] = useState<string | null>(null);
  const [isDispatching, setIsDispatching] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (activeChild) {
      loadData();
    }
  }, [activeChild]);

  const loadData = async () => {
    if (!activeChild) return;
    setIsLoading(true);
    try {
      const [data, recs, digest, guidance] = await Promise.all([
        api.getParentDashboard(activeChild.id),
        api.getReceipts(activeChild.id),
        api.getWeeklyDigest(activeChild.id).catch(() => null),
        api.getActionableGuidance(activeChild.id).catch(() => null)
      ]);
      setDashboardData(data);
      setReceipts(recs);
      setWeeklyDigest(digest);
      setActionableGuidance(guidance);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendDigest = async (channel: 'in_app_notification' | 'email') => {
    if (!activeChild) return;
    setIsDispatching(true);
    try {
      const res = await api.sendWeeklyDigest(activeChild.id, { channel });
      setDispatchStatus(res.message_summary_en);
      setTimeout(() => setDispatchStatus(null), 6000);
    } catch (e) {
      console.error('Failed to dispatch digest', e);
    } finally {
      setIsDispatching(false);
    }
  };


  const handlePrint = () => {
    window.print();
  };

  if (!activeChild) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center space-y-3">
        <div className="text-base font-bold text-slate-800">Sign in to view Parent Dashboard</div>
        <p className="text-xs text-slate-500">Track your child's evidence-based progress and purchase receipts.</p>
      </div>
    );
  }

  if (isLoading || !dashboardData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center text-xs text-slate-500">
        Loading parent analytics and honest coverage report...
      </div>
    );
  }

  const { child, overall_stats, skills, missing_coverage, companion_card } = dashboardData;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      {/* Top Banner */}
      <div className="sharp-card p-5 border-l-4 border-l-emerald-800 bg-white flex flex-wrap justify-between items-center gap-4">
        <div>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Parent Oversight & Evidence Portal
          </span>
          <h1 className="text-xl font-black text-slate-900">
            {child.name}'s Learning Record · <span className="font-arabic font-bold text-emerald-900">سجل الطالب</span>
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            {child.school_name} · Class {child.default_grade} · {child.gender} (Age {child.age})
          </p>
        </div>

        <button
          onClick={handlePrint}
          className="btn-secondary text-xs flex items-center gap-1.5"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Print Companion Report</span>
        </button>
      </div>

      {/* Fahim AI Intelligent Calibration & Roadmap Card */}
      <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-900 text-amber-300 flex items-center justify-center font-bold text-lg border-2 border-slate-900">
              <Compass className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-black uppercase tracking-tight text-slate-900">
                  Fahim AI Baseline Calibration & Learning Roadmap
                </h2>
                <span className="font-arabic font-bold text-xs text-emerald-900">· المسار التعليمي المخصص</span>
              </div>
              <p className="text-xs text-slate-600">
                Calibrates AI content difficulty according to UAE MoE & CBSE baseline diagnostic benchmarks.
              </p>
            </div>
          </div>

          {onOpenOnboarding && (
            <button
              onClick={onOpenOnboarding}
              className="btn-accent text-xs py-2 px-4 flex items-center gap-1.5 font-bold uppercase tracking-wider shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              <span>{child.diagnostic_completed ? 'Review / Recalibrate 4-Week Plan' : 'Start 4-Step Onboarding'}</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-3 border border-slate-200 bg-slate-50">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Diagnostic Status
            </span>
            <div className="mt-1 flex items-center gap-1.5">
              {child.diagnostic_completed ? (
                <span className="text-sm font-bold text-emerald-800 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700" /> Calibrated (مكتمل)
                </span>
              ) : (
                <span className="text-sm font-bold text-amber-800 flex items-center gap-1">
                  <Clock className="w-4 h-4 text-amber-700" /> Pending Calibration
                </span>
              )}
            </div>
            <span className="text-[10px] text-slate-400">
              {child.diagnostic_completed ? `Score: ${child.diagnostic_score || 0}%` : '8-question adaptive assessment'}
            </span>
          </div>

          <div className="p-3 border border-slate-200 bg-slate-50">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Calibrated Stream / Level
            </span>
            <div className="text-sm font-bold text-slate-900 mt-1 uppercase">
              {child.diagnostic_level === 'independent' ? 'Independent (متمكن)' : child.diagnostic_level === 'guided' ? 'Guided (متوسط)' : 'Foundation (مبتدئ)'}
            </div>
            <span className="text-[10px] text-slate-500 font-arabic truncate block">
              {child.curriculum_stream || 'MoE / CBSE Arabic (Non-Arabs)'}
            </span>
          </div>

          <div className="p-3 border border-slate-200 bg-slate-50">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Student Quick PIN
            </span>
            <div className="text-sm font-mono font-black text-slate-900 mt-1">
              {child.access_pin || '1234'}
            </div>
            <span className="text-[10px] text-slate-400">Direct student login code</span>
          </div>
        </div>
      </div>

      {/* Honest Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="sharp-card p-4 border border-slate-300 bg-white">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Completed Activities
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {overall_stats.total_attempts}
          </div>
          <span className="text-[10px] text-slate-400">Authentic submitted attempts</span>
        </div>

        <div className="sharp-card p-4 border border-slate-300 bg-white">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Accuracy Rate
          </span>
          <div className="text-2xl font-black text-emerald-800 mt-1">
            {overall_stats.accuracy_pct}%
          </div>
          <span className="text-[10px] text-slate-400">Objective first attempts</span>
        </div>

        <div className="sharp-card p-4 border border-slate-300 bg-white">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Mistakes to Review
          </span>
          <div className="text-2xl font-black text-amber-800 mt-1">
            {overall_stats.unresolved_mistakes_count}
          </div>
          <span className="text-[10px] text-slate-400">Pending in Mistake Notebook</span>
        </div>

        <div className="sharp-card p-4 border border-slate-300 bg-white">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Current Practice Streak
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {overall_stats.study_streak_days} Days
          </div>
          <span className="text-[10px] text-slate-400">Consecutive learning days</span>
        </div>
      </div>

      {/* Skill Breakdown (Honest Evidence-Based Assessment) */}
      <div className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
        <div className="border-b border-slate-200 pb-2 flex justify-between items-baseline">
          <div>
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight">
              Skill-by-Skill Evidence Breakdown
            </h2>
            <p className="text-xs text-slate-500">
              Evaluated strictly on verified student answers. Unobserved items are not fabricated.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(skills).map(([key, skill]: [string, any]) => (
            <div key={key} className="p-3 border border-slate-200 bg-slate-50/70 space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="font-bold text-xs text-slate-900">{skill.name_en}</span>
                <span className="font-arabic text-xs font-bold text-emerald-900">{skill.name_ar}</span>
              </div>

              {skill.assessed ? (
                <div>
                  <div className="flex justify-between text-[11px] font-semibold text-slate-600 mb-1">
                    <span>Performance: {skill.score_pct}%</span>
                    <span>{skill.evidence_count} evidence records</span>
                  </div>
                  <div className="w-full bg-slate-200 h-2">
                    <div
                      className="bg-emerald-800 h-2 transition-all"
                      style={{ width: `${skill.score_pct}%` }}
                    />
                  </div>
                </div>
              ) : (
                <div className="text-[11px] text-amber-800 bg-amber-50 p-2 border border-amber-200">
                  <span className="font-bold">Pending Evaluation: </span>
                  {skill.status_note}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Missing Coverage Report (Section 9 Anti-Inflation Rule) */}
      <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-3">
        <div className="flex items-center gap-2 text-slate-900">
          <AlertCircle className="w-5 h-5 text-amber-700" />
          <h2 className="text-sm font-black uppercase tracking-tight">
            Curriculum Coverage & Incomplete Chapter Tracking
          </h2>
        </div>
        <p className="text-xs text-slate-600">
          {missing_coverage.honest_progress_note}
        </p>

        <div className="border border-slate-200 divide-y divide-slate-200 text-xs">
          <div className="p-3 bg-emerald-50/60 flex justify-between items-center font-bold">
            <span className="text-emerald-950">Lesson 1: Ball Games (ألعاب الكرة)</span>
            <span className="bg-emerald-700 text-white px-2 py-0.5 text-[10px] uppercase">
              Completed & Assessed ✓
            </span>
          </div>

          {missing_coverage.pending_lessons.map((pl: any) => (
            <div key={pl.order} className="p-2.5 bg-white flex justify-between items-center">
              <span className="text-slate-700">
                Lesson {pl.order}: {pl.title_en} · <span className="font-arabic">{pl.title_ar}</span>
              </span>
              <span className="text-slate-400 italic text-[11px]">
                {pl.reason}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 4.2 Weekly Digest & Notification Dispatch (الملخص الأسبوعي) */}
      {weeklyDigest && (
        <div className="sharp-card p-5 border-2 border-emerald-900 bg-white space-y-4">
          <div className="flex flex-wrap justify-between items-center gap-3 border-b border-slate-200 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-emerald-900 bg-emerald-100 px-2 py-0.5 uppercase tracking-wider">
                  Weekly Digest · الملخص الأسبوعي
                </span>
                <span className="text-xs text-slate-500 font-bold">{weeklyDigest.week_label}</span>
              </div>
              <h2 className="text-base font-black text-slate-900 mt-1">
                Study Time, Capsule Mastery & Quiz Summary
              </h2>
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={isDispatching}
                onClick={() => handleSendDigest('in_app_notification')}
                className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
              >
                <Bell className="w-3.5 h-3.5 text-emerald-800" />
                <span>In-App Alert</span>
              </button>
              <button
                disabled={isDispatching}
                onClick={() => handleSendDigest('email')}
                className="btn-accent text-xs py-1.5 px-3 flex items-center gap-1.5 font-bold"
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Email Summary</span>
              </button>
            </div>
          </div>

          {dispatchStatus && (
            <div className="p-3 border border-emerald-400 bg-emerald-50 text-xs text-emerald-950 font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-700 flex-shrink-0" />
              <span>{dispatchStatus}</span>
            </div>
          )}

          {/* Digest KPI cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 border border-slate-200 bg-slate-50">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Study Time</span>
              <div className="text-xl font-black text-slate-900 font-mono mt-0.5">
                {weeklyDigest.study_minutes} mins
              </div>
              <span className="text-[10px] text-emerald-700 font-bold">
                +{weeklyDigest.study_minutes_vs_last_week_pct}% vs. last week
              </span>
            </div>

            <div className="p-3 border border-slate-200 bg-slate-50">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Completed Capsules</span>
              <div className="text-xl font-black text-emerald-900 font-mono mt-0.5">
                {weeklyDigest.completed_capsules_count} Units
              </div>
              <span className="text-[10px] text-slate-500">3-min bite-sized lessons</span>
            </div>

            <div className="p-3 border border-slate-200 bg-slate-50">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Avg Quiz Score</span>
              <div className="text-xl font-black text-emerald-800 font-mono mt-0.5">
                {weeklyDigest.avg_quiz_score}%
              </div>
              <span className="text-[10px] text-slate-500">{weeklyDigest.quizzes_taken} quizzes evaluated</span>
            </div>

            <div className="p-3 border border-slate-200 bg-slate-50">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Active Streak</span>
              <div className="text-xl font-black text-amber-700 font-mono mt-0.5">
                🔥 {weeklyDigest.streak_days} Days
              </div>
              <span className="text-[10px] text-slate-500">Consecutive practice days</span>
            </div>
          </div>

          {/* Tutor feedback & parent tips */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div className="p-3.5 border border-slate-200 bg-slate-50 space-y-2">
              <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                Tutor Pedagogical Observation
              </span>
              <p className="text-xs text-slate-700 leading-relaxed italic">
                "{weeklyDigest.tutor_feedback_summary_en}"
              </p>
            </div>

            <div className="p-3.5 border border-slate-200 bg-slate-50 space-y-2">
              <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                Weekly Parent Action Tips
              </span>
              <ul className="space-y-1 text-xs text-slate-600 list-disc list-inside">
                {weeklyDigest.parent_tips.map((tip, idx) => (
                  <li key={idx}>{tip}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 4.2 Actionable Guidance for Non-Arabic Speaking Parents */}
      {actionableGuidance && (
        <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-4">
          <div className="flex items-center gap-3 border-b border-slate-200 pb-3">
            <div className="w-10 h-10 bg-amber-600 text-white flex items-center justify-center font-bold text-lg">
              <HeartHandshake className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight">
                  Non-Arabic Speaking Parent Guide (دليل ولي الأمر)
                </h2>
                <span className="bg-amber-100 text-amber-900 text-[10px] px-2 py-0.5 font-bold uppercase">
                  No Arabic Needed
                </span>
              </div>
              <p className="text-xs text-slate-600">
                {actionableGuidance.welcome_message_en}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {actionableGuidance.guidance_items.map((item, idx) => (
              <div key={idx} className="p-4 border border-slate-200 bg-slate-50/70 space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-slate-900">{item.topic_en}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 uppercase ${
                      item.status === 'mastering'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.status === 'needs_reinforcement'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-slate-200 text-slate-700'
                    }`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-xs font-arabic font-bold text-emerald-900 block" dir="rtl">
                    {item.topic_ar}
                  </span>

                  <div className="space-y-1.5 pt-1 border-t border-slate-200 text-xs">
                    <div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase block">💬 What to ask at home:</span>
                      <p className="text-slate-800 italic mt-0.5">{item.parent_prompt_en}</p>
                    </div>

                    <div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase block">🌟 How to praise them:</span>
                      <p className="text-slate-700 mt-0.5">{item.praise_suggestion_en}</p>
                    </div>

                    <div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase block">🏡 Quick Household Activity:</span>
                      <p className="text-slate-600 mt-0.5">{item.household_activity_en}</p>
                    </div>
                  </div>
                </div>

                {item.phonetic_help_en && (
                  <div className="p-2 border border-slate-300 bg-white text-[11px] font-mono text-slate-700 flex items-center gap-1.5">
                    <Volume2 className="w-3.5 h-3.5 text-emerald-800 flex-shrink-0" />
                    <span className="truncate">{item.phonetic_help_en}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Monetization, Packages & FTA Tax Invoices */}
      <div className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
        <div className="flex flex-wrap justify-between items-baseline border-b border-slate-200 pb-2 gap-2">
          <div>
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight flex items-center gap-1.5">
              <Receipt className="w-4 h-4 text-emerald-800" />
              <span>Subscriptions, Bundles & Invoicing (الفواتير والاشتراكات)</span>
            </h2>
            <p className="text-[11px] text-slate-500">
              UAE VAT-compliant tax invoices (TRN: 100458923100003) and verified curriculum authorizations
            </p>
          </div>
          <button
            onClick={onOpenPaywall}
            className="text-xs bg-emerald-800 hover:bg-emerald-900 text-white font-bold px-3 py-1.5 border border-slate-900 shadow-[2px_2px_0px_0px_#0f172a]"
          >
            + Upgrade / Redeem Voucher
          </button>
        </div>

        {/* Current Active Entitlement Status */}
        <div className="p-3 bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-100 border border-emerald-400 text-emerald-900 flex items-center justify-center font-black">
              {receipts.some(r => r.package_type === 'annual') ? '★' : '✓'}
            </div>
            <div>
              <div className="font-bold text-slate-900">
                {receipts.some(r => r.package_type === 'annual')
                  ? 'Active Plan: Full Academic Year Pass (Terms 1, 2, & 3)'
                  : receipts.length > 0
                  ? 'Active Plan: Single Term License'
                  : 'Active Plan: Freemium Free Demo (Chapter 1 Ball Games)'}
              </div>
              <div className="text-[11px] text-slate-500">
                Enrolled: {child.name} · {child.school_name} · Class {child.default_grade}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block bg-emerald-100 text-emerald-900 border border-emerald-300 px-2 py-0.5 text-[10px] font-bold">
              {receipts.length > 0 ? 'LICENSED' : 'FREEMIUM PREVIEW'}
            </span>
          </div>
        </div>

        {receipts.length === 0 ? (
          <div className="text-xs text-slate-500 py-3 text-center border border-dashed border-slate-300">
            Chapter 1 (Ball Games) is active on the Free Demo tier. To unlock Chapters 2–10, exam preparation, and study booklets, select a Term or Annual pass.
          </div>
        ) : (
          <div className="space-y-2">
            {receipts.map((r) => {
              const isAnnual = r.package_type === 'annual' || r.term === 0;
              const isVoucher = r.payment_method === 'school_voucher';
              return (
                <div key={r.id} className="p-3 border border-slate-300 bg-white hover:bg-slate-50/80 transition-colors flex flex-wrap justify-between items-center gap-3 text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-1.5 py-0.5 text-[10px] font-black uppercase ${
                        isAnnual
                          ? 'bg-amber-600 text-white'
                          : isVoucher
                          ? 'bg-blue-700 text-white'
                          : 'bg-slate-800 text-white'
                      }`}>
                        {isAnnual ? 'Annual Pass (Terms 1, 2, 3)' : `Term ${r.term} License`}
                      </span>
                      <span className="font-mono font-bold text-slate-900">{r.receipt_number}</span>
                      {r.voucher_code && (
                        <span className="text-[10px] font-mono bg-amber-100 text-amber-900 border border-amber-300 px-1">
                          Voucher: {r.voucher_code}
                        </span>
                      )}
                    </div>
                    <div className="text-slate-500 text-[11px] flex flex-wrap gap-x-3">
                      <span>Class {r.grade}</span>
                      <span>Method: <strong className="uppercase">{r.payment_method}</strong></span>
                      <span>Subtotal: ${Number(r.subtotal_usd || 0).toFixed(2)}</span>
                      <span>VAT (5%): ${Number(r.vat_amount_usd || 0).toFixed(2)}</span>
                      <span>TRN: {r.trn || '100458923100003'}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-right">
                    <div>
                      <div className="font-black text-slate-900 text-sm">
                        USD {Number(r.amount_usd).toFixed(2)}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        AED {Number(r.amount_aed || (r.amount_usd * 3.6725)).toFixed(2)}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const inv = await api.getTaxInvoice(r.receipt_number);
                          setSelectedInvoice(inv);
                        } catch (err: any) {
                          alert('Failed to load invoice: ' + err.message);
                        }
                      }}
                      className="px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-[11px] flex items-center gap-1 border border-slate-900 shadow-[1px_1px_0px_0px_#0f172a]"
                    >
                      <Receipt className="w-3 h-3 text-amber-400" />
                      <span>View Tax Invoice</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Tax Invoice Modal */}
      {selectedInvoice && (
        <div className="fixed inset-0 bg-slate-950/80 z-[70] flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border-2 border-slate-900 w-full max-w-2xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto print:border-none print:shadow-none">
            <button
              onClick={() => setSelectedInvoice(null)}
              className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 p-1 print:hidden"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Printable Invoice Header */}
            <div className="border-b-2 border-slate-900 pb-4 mb-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xl font-black text-slate-900 uppercase tracking-tight">
                    FAHEEM AI (فهيم للتعليم الذكي)
                  </div>
                  <div className="text-xs text-slate-600">
                    JISR Arabic Educational Technologies FZ-LLC
                  </div>
                  <div className="text-xs text-slate-600 font-mono">
                    TRN: <strong className="text-slate-900">{selectedInvoice.trn}</strong>
                  </div>
                  <div className="text-xs text-slate-500">Abu Dhabi · United Arab Emirates</div>
                </div>
                <div className="text-right">
                  <div className="inline-block bg-emerald-800 text-white font-black text-xs px-2.5 py-1 uppercase tracking-wider mb-1">
                    TAX INVOICE / فاتورة ضريبية
                  </div>
                  <div className="font-mono text-xs font-bold text-slate-900">
                    {selectedInvoice.invoice_number}
                  </div>
                  <div className="text-[11px] text-slate-500">{selectedInvoice.issue_date}</div>
                </div>
              </div>
            </div>

            {/* Bill To Info */}
            <div className="grid grid-cols-2 gap-4 bg-slate-50 p-3 border border-slate-300 mb-4 text-xs">
              <div>
                <div className="font-bold text-slate-500 uppercase text-[10px]">Customer / العميل:</div>
                <div className="font-bold text-slate-900">{selectedInvoice.parent_name}</div>
                <div className="text-slate-600">{selectedInvoice.parent_email}</div>
              </div>
              <div>
                <div className="font-bold text-slate-500 uppercase text-[10px]">Student & School:</div>
                <div className="font-bold text-slate-900">
                  {selectedInvoice.student_name} (Class {selectedInvoice.grade})
                </div>
                <div className="text-slate-600">{selectedInvoice.school_name}</div>
              </div>
            </div>

            {/* Line Items */}
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
                {selectedInvoice.items.map((item, idx) => (
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

            {/* Totals */}
            <div className="flex justify-end mb-4">
              <div className="w-64 space-y-1 text-xs border border-slate-300 p-3 bg-slate-50">
                <div className="flex justify-between text-slate-600">
                  <span>Subtotal (excl. VAT):</span>
                  <span className="font-mono font-bold">${selectedInvoice.subtotal_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>UAE 5% VAT:</span>
                  <span className="font-mono font-bold">${selectedInvoice.vat_amount_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm font-black text-slate-900 border-t border-slate-300 pt-1">
                  <span>Gross Total (USD):</span>
                  <span className="font-mono">${selectedInvoice.total_usd.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs font-black text-emerald-800">
                  <span>Total Payable (AED):</span>
                  <span className="font-mono">AED {selectedInvoice.total_aed.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-slate-200 pt-3 text-xs">
              <div className="text-slate-600">
                Payment Method: <strong className="text-slate-900 uppercase font-mono">{selectedInvoice.payment_method}</strong> · Status: <strong className="text-emerald-800 uppercase">{selectedInvoice.status}</strong>
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
                  onClick={() => setSelectedInvoice(null)}
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
