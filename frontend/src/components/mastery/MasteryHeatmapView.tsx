import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle2, RotateCcw, Sparkles, BookOpen, Layers, Target, ChevronRight, Award } from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, MasteryHeatmapData, ConceptMasteryItem, GapReviewSession } from '../../types';

interface MasteryHeatmapViewProps {
  activeChild: ChildProfile | null;
  onNavigateToCapsule?: (capsuleId: string) => void;
}

export const MasteryHeatmapView: React.FC<MasteryHeatmapViewProps> = ({
  activeChild,
  onNavigateToCapsule
}) => {
  const [heatmapData, setHeatmapData] = useState<MasteryHeatmapData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [drillSession, setDrillSession] = useState<GapReviewSession | null>(null);
  const [isDrillOpen, setIsDrillOpen] = useState<boolean>(false);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState<number>(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [drillResult, setDrillResult] = useState<any>(null);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState<boolean>(false);

  useEffect(() => {
    if (activeChild) {
      loadHeatmap();
    }
  }, [activeChild]);

  const loadHeatmap = async () => {
    if (!activeChild) return;
    setIsLoading(true);
    try {
      const data = await api.getMasteryHeatmap(activeChild.id);
      setHeatmapData(data);
    } catch (e) {
      console.error('Failed to load mastery heatmap', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartDrill = async () => {
    if (!activeChild) return;
    try {
      const session = await api.getGapReviewSession(activeChild.id);
      setDrillSession(session);
      setCurrentQuestionIdx(0);
      setSelectedOption(null);
      setDrillResult(null);
      setIsDrillOpen(true);
    } catch (e) {
      console.error('Failed to start gap drill', e);
    }
  };

  const handleSubmitDrillAnswer = async () => {
    if (!drillSession || selectedOption === null || !activeChild) return;
    const q = drillSession.questions[currentQuestionIdx];
    const isCorrect = selectedOption === q.correct_index;
    setIsSubmittingAnswer(true);
    try {
      const res = await api.recordDrillAnswer({
        child_id: activeChild.id,
        concept_key: q.concept_key,
        question_id: q.id,
        selected_index: selectedOption,
        is_correct: isCorrect
      });
      setDrillResult({
        isCorrect,
        explanation_ar: q.explanation_ar,
        explanation_en: q.explanation_en,
        feedback_ar: res.feedback_ar,
        feedback_en: res.feedback_en,
        xp_awarded: res.xp_awarded,
        new_mastery_pct: res.new_mastery_pct
      });
      // Refresh heatmap in background
      loadHeatmap();
    } catch (e) {
      console.error('Failed to record answer', e);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleNextQuestion = () => {
    if (!drillSession) return;
    if (currentQuestionIdx + 1 < drillSession.questions.length) {
      setCurrentQuestionIdx(prev => prev + 1);
      setSelectedOption(null);
      setDrillResult(null);
    } else {
      // Completed drill
      setIsDrillOpen(false);
      setDrillSession(null);
    }
  };

  if (!activeChild) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center space-y-3">
        <div className="text-base font-bold text-slate-800">Select a student profile to view Concept Mastery</div>
        <p className="text-xs text-slate-500">Sign in to track granular linguistic progress and knowledge gap detection.</p>
      </div>
    );
  }

  if (isLoading || !heatmapData) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 text-center text-xs text-slate-500">
        Calibrating real-time concept mastery and isolating linguistic gaps...
      </div>
    );
  }

  const categoryLabels: Record<string, { ar: string; en: string }> = {
    grammar: { ar: 'القواعد والتراكيب النحوية', en: 'Grammar & Syntax' },
    vocabulary: { ar: 'المفردات والمعجم اللغوي', en: 'Vocabulary & Glossary' },
    reading: { ar: 'الطلاقة وفهم المقروء', en: 'Reading Fluency & Comprehension' },
    orthography: { ar: 'الإملاء ورسم الحروف', en: 'Orthography & Spelling' },
    speaking: { ar: 'الطلاقة الشفهية والنطق', en: 'Oral Phonics & Speaking' }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      {/* Header Banner */}
      <div className="sharp-card p-6 border-l-4 border-l-emerald-800 bg-white flex flex-wrap justify-between items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-bold text-emerald-900 bg-emerald-100 px-2 py-0.5 tracking-wider uppercase">
              Real-Time Diagnostic Analytics · سجل الإتقان
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900">
            {heatmapData.child_name}'s Knowledge Gap Heatmap
          </h1>
          <p className="text-xs text-slate-600 mt-1 max-w-2xl">
            Fine-grained concept proficiency tracker aligned with the UAE Ministry of Education (MoE) and CBSE standards.
            Sub-70% competencies are automatically isolated and scheduled into spaced-repetition recovery drills.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <span className="text-[10px] font-bold uppercase text-slate-500 block">Overall Mastery</span>
            <span className="text-3xl font-black text-emerald-900 font-mono">
              {heatmapData.overall_mastery_pct}%
            </span>
          </div>
          <div className="w-12 h-12 bg-emerald-900 text-amber-300 flex items-center justify-center font-bold text-lg border-2 border-slate-900">
            <Target className="w-6 h-6 text-amber-300" />
          </div>
        </div>
      </div>

      {/* Active Knowledge Gaps Isolation Banner */}
      {heatmapData.active_gaps_count > 0 ? (
        <div className="sharp-card p-5 border-2 border-red-600 bg-red-50/70 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-red-200 pb-3">
            <div className="flex items-center gap-2 text-red-950 font-black text-sm">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span>{heatmapData.active_gaps_count} Persistent Knowledge Gap(s) Detected (فجوات لغوية تحتاج معالجة)</span>
            </div>
            <button
              onClick={handleStartDrill}
              className="btn-accent text-xs py-2 px-4 flex items-center gap-1.5 font-bold uppercase tracking-wider"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Launch Gap Recovery Drill (+25 XP)</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {heatmapData.knowledge_gaps.map((gap) => (
              <div key={gap.concept_key} className="p-3 border border-red-300 bg-white flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">{gap.concept_name_en}</span>
                    <span className="text-xs font-arabic font-bold text-red-800">· {gap.concept_name_ar}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {gap.persistent_mistake_count} repeated error(s) in active lessons
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-base font-black text-red-600 font-mono">{gap.mastery_percentage}%</span>
                  <span className="text-[10px] text-red-700 bg-red-100 px-1.5 py-0.5 block mt-0.5 font-bold uppercase">
                    Needs Review
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="sharp-card p-4 border border-emerald-300 bg-emerald-50/60 flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-950 text-xs font-bold">
            <CheckCircle2 className="w-5 h-5 text-emerald-700" />
            <span>Zero critical gaps detected! All monitored language competencies are above the 70% threshold.</span>
          </div>
          <button
            onClick={handleStartDrill}
            className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1"
          >
            <span>Run Maintenance Refresher</span>
          </button>
        </div>
      )}

      {/* Heatmap Legend */}
      <div className="sharp-card p-3 border border-slate-200 bg-white flex flex-wrap items-center justify-between text-xs gap-3">
        <span className="font-bold text-slate-700 uppercase tracking-tight text-[11px]">Mastery Scale:</span>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-[#064e3b]" />
            <span className="text-slate-600">Mastered (85–100%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-[#059669]" />
            <span className="text-slate-600">Proficient (70–84%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-[#d97706]" />
            <span className="text-slate-600">Developing (50–69%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-[#dc2626]" />
            <span className="text-slate-600">Critical Gap (&lt;50% or persistent)</span>
          </div>
        </div>
      </div>

      {/* Concept Matrix by Category */}
      <div className="space-y-6">
        {Object.entries(heatmapData.concepts_by_category).map(([catKey, items]) => {
          const catInfo = categoryLabels[catKey] || { ar: catKey, en: catKey.toUpperCase() };
          return (
            <div key={catKey} className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-800" />
                  <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider">
                    {catInfo.en}
                  </h3>
                  <span className="text-xs font-arabic font-bold text-emerald-900">
                    · {catInfo.ar}
                  </span>
                </div>
                <span className="text-xs text-slate-500 font-mono font-bold">
                  {items.length} Concepts Tracked
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {items.map((item) => (
                  <div
                    key={item.concept_key}
                    className={`p-4 border ${item.is_gap ? 'border-red-300 bg-red-50/30' : 'border-slate-200 bg-slate-50/60'} space-y-2.5`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-xs font-bold text-slate-900">{item.concept_name_en}</h4>
                        <span className="text-xs font-arabic font-bold text-emerald-900 block mt-0.5">
                          {item.concept_name_ar}
                        </span>
                      </div>
                      <div className="text-right">
                        <span
                          className="text-base font-black font-mono"
                          style={{ color: item.color_hex }}
                        >
                          {item.mastery_percentage}%
                        </span>
                        <span
                          className="text-[10px] font-bold block uppercase"
                          style={{ color: item.color_hex }}
                        >
                          {item.status_label_en}
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-200 h-2">
                      <div
                        className="h-2 transition-all duration-300"
                        style={{
                          width: `${item.mastery_percentage}%`,
                          backgroundColor: item.color_hex
                        }}
                      />
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-200">
                      <span>{item.correct_attempts} of {item.total_attempts} verified answers</span>
                      <span className="font-arabic">{item.status_label_ar}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Gap Recovery Drill Modal */}
      {isDrillOpen && drillSession && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-2xl w-full border-2 border-slate-900 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-slate-200 pb-3">
              <div>
                <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 uppercase tracking-wider">
                  Adaptive Spaced Repetition Drill · تدريب سد الفجوات
                </span>
                <h3 className="text-base font-black text-slate-900 mt-1">
                  Question {currentQuestionIdx + 1} of {drillSession.questions.length}: {drillSession.questions[currentQuestionIdx].concept_name_en}
                </h3>
              </div>
              <button
                onClick={() => setIsDrillOpen(false)}
                className="text-slate-500 hover:text-slate-900 text-xs font-bold px-2 py-1 border border-slate-300"
              >
                ✕ Close
              </button>
            </div>

            {/* Question Card */}
            <div className="p-4 border border-slate-200 bg-slate-50 space-y-3">
              <div className="text-right">
                <span className="font-arabic font-black text-lg text-slate-900 leading-relaxed block" dir="rtl">
                  {drillSession.questions[currentQuestionIdx].prompt_ar}
                </span>
              </div>
              <div className="text-xs text-slate-600 font-medium">
                {drillSession.questions[currentQuestionIdx].prompt_en}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-2">
              {drillSession.questions[currentQuestionIdx].options.map((opt, idx) => (
                <button
                  key={idx}
                  disabled={drillResult !== null}
                  onClick={() => setSelectedOption(idx)}
                  className={`w-full p-3.5 text-right font-arabic font-bold text-sm border-2 transition-all flex items-center justify-between ${
                    selectedOption === idx
                      ? 'border-emerald-800 bg-emerald-50 text-emerald-950'
                      : 'border-slate-300 hover:border-slate-500 bg-white text-slate-800'
                  }`}
                  dir="rtl"
                >
                  <span className="flex-1">{opt}</span>
                  <span className="w-5 h-5 border border-slate-400 flex items-center justify-center text-[10px] ml-3 font-mono">
                    {selectedOption === idx ? '✓' : idx + 1}
                  </span>
                </button>
              ))}
            </div>

            {/* Result / Explanation */}
            {drillResult && (
              <div className={`p-4 border-2 ${drillResult.isCorrect ? 'border-emerald-700 bg-emerald-50' : 'border-red-600 bg-red-50'} space-y-2`}>
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-black uppercase ${drillResult.isCorrect ? 'text-emerald-900' : 'text-red-900'}`}>
                    {drillResult.isCorrect ? '✓ Correct! إجابة صحيحة' : '✗ Incorrect! إجابة غير دقيقة'}
                  </span>
                  <span className="text-xs font-bold text-emerald-800 font-mono">
                    +{drillResult.xp_awarded} XP Awarded
                  </span>
                </div>
                <p className="text-xs text-slate-700 font-arabic text-right" dir="rtl">
                  {drillResult.explanation_ar}
                </p>
                <p className="text-[11px] text-slate-500">
                  {drillResult.explanation_en}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-3 border-t border-slate-200">
              {!drillResult ? (
                <button
                  disabled={selectedOption === null || isSubmittingAnswer}
                  onClick={handleSubmitDrillAnswer}
                  className="btn-primary text-xs py-2.5 px-6 font-bold uppercase tracking-wider"
                >
                  {isSubmittingAnswer ? 'Verifying...' : 'Check Answer (تحقق من الإجابة)'}
                </button>
              ) : (
                <button
                  onClick={handleNextQuestion}
                  className="btn-accent text-xs py-2.5 px-6 font-bold uppercase tracking-wider flex items-center gap-1.5"
                >
                  <span>{currentQuestionIdx + 1 < drillSession.questions.length ? 'Next Question →' : 'Finish Drill & Update Mastery'}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
