import React, { useState, useEffect, useMemo } from 'react';
import {
  Zap, Clock, CheckCircle, Play, Volume2, Award, ArrowRight,
  BookOpen, Check, X, Sparkles, GraduationCap
} from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';
import { User, ChildProfile } from '../../types';

interface CapsulesGridProps {
  user?: User | null;
  activeChild: ChildProfile | null;
  initialGrade?: number;
  onSelectGrade?: (grade: number) => void;
}

export const CapsulesGrid: React.FC<CapsulesGridProps> = ({ user, activeChild, initialGrade = 5, onSelectGrade }) => {
  const availableGrades = useMemo(() => {
    if (user?.role === 'admin') {
      return [5, 6, 7];
    }
    if (user?.role === 'learner' && activeChild?.default_grade) {
      return [activeChild.default_grade];
    }
    if (user?.role === 'parent' && user.children && user.children.length > 0) {
      const grades = Array.from(new Set(user.children.map((c) => c.default_grade).filter(Boolean))).sort((a, b) => a - b);
      if (grades.length > 0) return grades;
    }
    if (activeChild?.default_grade) {
      return [activeChild.default_grade];
    }
    return [initialGrade || 5];
  }, [user, activeChild, initialGrade]);

  const [selectedGrade, setSelectedGrade] = useState<number>(() => {
    if (initialGrade && (user?.role === 'admin' || !activeChild?.default_grade)) {
      return initialGrade;
    }
    return activeChild?.default_grade || initialGrade || 5;
  });

  useEffect(() => {
    if (initialGrade && initialGrade !== selectedGrade) {
      setSelectedGrade(initialGrade);
    }
  }, [initialGrade]);

  useEffect(() => {
    if (user?.role !== 'admin' && activeChild?.default_grade) {
      setSelectedGrade(activeChild.default_grade);
    }
  }, [activeChild?.default_grade, user?.role]);

  const [capsules, setCapsules] = useState<any[]>([]);
  const [completedCount, setCompletedCount] = useState<number>(0);
  const [selectedCapsule, setSelectedCapsule] = useState<any | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState<boolean>(false);
  const [isCompletedState, setIsCompletedState] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchCapsules = async () => {
    setLoading(true);
    try {
      const res = await api.listCapsules(activeChild?.id, selectedGrade);
      if (res.success) {
        setCapsules(res.capsules);
        setCompletedCount(res.completed_count || 0);
      }
    } catch (err) {
      console.error('Failed to load capsules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCapsules();
  }, [activeChild?.id, selectedGrade]);

  const openCapsule = (cap: any) => {
    setSelectedCapsule(cap);
    setQuizAnswers({});
    setQuizSubmitted(false);
    setIsCompletedState(cap.is_completed);
  };

  const handleSelectQuizOption = (qIdx: number, oIdx: number) => {
    if (quizSubmitted) return;
    setQuizAnswers((prev) => ({ ...prev, [qIdx]: oIdx }));
  };

  const handleFinishCapsule = async () => {
    setQuizSubmitted(true);
    const totalQ = selectedCapsule.quiz.length;
    let correct = 0;
    selectedCapsule.quiz.forEach((q: any, idx: number) => {
      if (quizAnswers[idx] === q.correct_index) correct++;
    });

    const scorePct = totalQ > 0 ? (correct / totalQ) * 100.0 : 100.0;

    if (activeChild?.id) {
      try {
        await api.completeCapsule(selectedCapsule.id, {
          child_id: activeChild.id,
          score: scorePct,
          time_spent_seconds: selectedCapsule.duration_minutes * 60
        });
        setIsCompletedState(true);
        fetchCapsules();
      } catch (err) {
        console.error('Failed to complete capsule:', err);
      }
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Grade Selector Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 bg-white border border-slate-200 p-3 rounded-sm shadow-2xs">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
            <GraduationCap className="w-4 h-4 text-purple-700" />
            <span>الصف الدراسي (Grade):</span>
          </div>
          <div className="flex items-center gap-1.5">
            {availableGrades.map((g) => (
              <button
                key={g}
                onClick={() => {
                  setSelectedGrade(g);
                  onSelectGrade?.(g);
                }}
                className={`px-3 py-1 rounded-sm text-xs font-bold transition-all ${
                  selectedGrade === g
                    ? 'bg-purple-700 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                الصف {g} (Grade {g})
              </button>
            ))}
          </div>
        </div>
        <div className="text-xs text-slate-500 font-sans flex items-center gap-2">
          <span>UAE MoE & CBSE Aligned</span>
          <span className="text-slate-300">|</span>
          <span className="font-semibold text-purple-700">كبسولات الصف {selectedGrade} (Grade {selectedGrade})</span>
        </div>
      </div>

      {/* Header Banner */}
      <div className="bg-slate-900 text-white border-2 border-slate-900 p-6 mb-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="bg-amber-400 text-slate-950 text-[10px] font-bold px-2 py-0.5 rounded-2xs uppercase tracking-wider">
              الصف {selectedGrade} · Grade {selectedGrade}
            </span>
            <span className="text-xs text-purple-300 font-sans">
              3–5 Minute Focused Grammar & Vocabulary Units
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight font-arabic">
            الكبسولات اللغوية السريعة — الصف {selectedGrade}
          </h1>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          <ArabEnglishToggleSwitch />
          {/* Progress Badge Counter */}
          <div className="bg-slate-800 border border-slate-700 p-3 flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-400 text-slate-950 flex items-center justify-center font-bold">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block">الإنجاز الكلي (Total Progress):</span>
            <span className="text-sm font-bold text-white">
              {completedCount} من أصل {capsules.length} كبسولات منجزة ({completedCount}/{capsules.length} Done)
            </span>
          </div>
        </div>
      </div>
    </div>

      {/* Grid of Capsules */}
      {loading ? (
        <div className="py-12 text-center text-slate-600 font-bold">
          جَارٍ تَحْمِيلُ الكَبْسُولَاتِ التَّعْلِيمِيَّةِ... (Loading Microlearning Capsules...)
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {capsules.map((cap) => (
            <div
              key={cap.id}
              className={`bg-white border-2 transition-all p-5 flex flex-col justify-between ${
                cap.is_completed ? 'border-emerald-800' : 'border-slate-900 hover:border-emerald-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 uppercase tracking-wider">
                    {cap.topic}
                  </span>
                  <div className="flex items-center gap-1 text-slate-500 text-xs font-mono">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{cap.duration_minutes} دقائق ({cap.duration_minutes}m)</span>
                  </div>
                </div>

                <h3 className="text-base font-black text-slate-900 mb-1 font-arabic text-right" dir="rtl">
                  {cap.title_ar}
                </h3>
                <p className="text-xs text-slate-500 mb-3 font-sans">
                  {cap.title_en}
                </p>

                <p className="text-xs text-slate-700 font-arabic text-right mb-4 line-clamp-2" dir="rtl">
                  {cap.summary_ar}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                {cap.is_completed ? (
                  <span className="text-xs font-bold text-emerald-800 flex items-center gap-1">
                    <CheckCircle className="w-4 h-4 text-emerald-700" />
                    <span>تم الإتقان (Mastered)</span>
                  </span>
                ) : (
                  <span className="text-xs text-slate-500 font-medium">غير مكتملة بعد (Pending)</span>
                )}

                <button
                  onClick={() => openCapsule(cap)}
                  className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition-colors ${
                    cap.is_completed
                      ? 'bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-300'
                      : 'bg-emerald-900 text-white hover:bg-emerald-800 border-2 border-slate-900'
                  }`}
                >
                  <Play className="w-3 h-3" />
                  <span>{cap.is_completed ? 'مراجعة (Review)' : 'ابدأ الكبسولة (Start)'}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CAPSULE MODAL VIEWER */}
      {selectedCapsule && (
        <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white border-2 border-slate-900 w-full max-w-2xl shadow-2xl p-6 flex flex-col max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
              <div>
                <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">
                  {selectedCapsule.topic} · مدة الكبسولة {selectedCapsule.duration_minutes} دقائق
                </span>
                <h2 className="text-lg font-black text-slate-900 font-arabic text-right" dir="rtl">
                  {selectedCapsule.title_ar}
                </h2>
              </div>
              <button
                onClick={() => setSelectedCapsule(null)}
                className="text-slate-500 hover:text-slate-900 p-1 font-bold"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Audio Script Banner */}
            <div className="bg-emerald-950 text-white p-4 mb-4 flex items-start justify-between gap-3">
              <div className="flex-1">
                <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider block mb-1">
                  الشرح الصوتي للكبسولة (Audio Explanation):
                </span>
                <div className="text-xs leading-relaxed text-right text-emerald-100" dir="rtl">
                  <ArabicWordSpans text={selectedCapsule.audio_script_ar} className="text-xs leading-relaxed text-emerald-100" />
                </div>
                {selectedCapsule.audio_script_en && (
                  <div className="text-[11px] text-emerald-300 font-sans italic mt-2 pt-2 border-t border-emerald-900 text-left" dir="ltr">
                    {selectedCapsule.audio_script_en}
                  </div>
                )}
              </div>
              <button
                onClick={() => audioManager.playArabic(selectedCapsule.audio_script_ar)}
                className="bg-amber-400 text-slate-950 px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 hover:bg-amber-300 transition-colors flex-shrink-0"
              >
                <Volume2 className="w-4 h-4" />
                <span>استمع</span>
              </button>
            </div>

            {/* Rule Steps */}
            <div className="space-y-3 mb-5">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                خطوات القاعدة الأساسية (Rule Breakdown):
              </h4>
              {selectedCapsule.rule_steps.map((step: any) => (
                <div key={step.step_number} className="p-3 bg-slate-50 border border-slate-200 text-right" dir="rtl">
                  <div className="text-xs font-black text-emerald-950 block mb-1 font-arabic">
                    <ArabicWordSpans text={step.title_ar} className="text-xs font-black text-emerald-950" />
                    {step.title_en && <span className="text-[11px] text-slate-500 font-sans block mt-0.5 text-left" dir="ltr">{step.title_en}</span>}
                  </div>
                  <div className="text-xs text-slate-700 leading-relaxed">
                    <ArabicWordSpans text={step.explanation_ar} className="text-xs leading-relaxed" />
                  </div>
                  {step.explanation_en && (
                    <div className="text-[11px] text-slate-500 font-sans italic mt-1 pt-1 border-t border-slate-200 text-left" dir="ltr">
                      {step.explanation_en}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Examples Grid */}
            <div className="mb-5">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                أمثلة تطبيقية سريعة (Worked Examples):
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {selectedCapsule.examples.map((ex: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-amber-50/50 border border-amber-200 text-right" dir="rtl">
                    <div className="text-sm font-black text-slate-900 font-arabic">
                      <ArabicWordSpans text={ex.word_ar || ex.sentence_ar} className="text-sm font-black text-slate-900" />
                    </div>
                    {ex.translation_en && (
                      <div className="text-[11px] text-slate-600 font-sans italic text-left" dir="ltr">
                        {ex.translation_en}
                      </div>
                    )}
                    <div className="text-[11px] text-amber-900 font-medium mt-1">
                      {ex.type || ex.gender || ex.test_ar}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 2-Question Checkpoint Quiz */}
            <div className="bg-slate-100 p-4 border border-slate-300 mb-4">
              <div className="flex items-center gap-1.5 mb-3">
                <Sparkles className="w-4 h-4 text-emerald-800" />
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-900">
                  اختبار التحقق الفوري (Checkpoint Quiz):
                </h4>
              </div>

              {selectedCapsule.quiz.map((q: any, qIdx: number) => {
                const chosen = quizAnswers[qIdx];
                const isCorrect = chosen === q.correct_index;

                return (
                  <div key={qIdx} className="mb-4 last:mb-0">
                    <div className="mb-2">
                      <p className="text-xs font-bold text-slate-900 font-arabic text-right" dir="rtl">
                        {qIdx + 1}. <ArabicWordSpans text={q.question_ar} />
                      </p>
                      {q.question_en && (
                        <p className="text-[11px] text-slate-500 font-sans italic mt-0.5 text-left" dir="ltr">
                          {q.question_en}
                        </p>
                      )}
                    </div>

                    <div className="space-y-1.5">
                      {q.options.map((opt: string, oIdx: number) => {
                        const isSelected = chosen === oIdx;
                        let btnStyle = "bg-white border-slate-300 text-slate-800";
                        if (isSelected && !quizSubmitted) {
                          btnStyle = "bg-emerald-900 text-white border-emerald-950";
                        } else if (quizSubmitted) {
                          if (oIdx === q.correct_index) {
                            btnStyle = "bg-emerald-100 border-emerald-600 text-emerald-950 font-bold";
                          } else if (isSelected && !isCorrect) {
                            btnStyle = "bg-rose-100 border-rose-600 text-rose-950";
                          }
                        }

                        return (
                          <button
                            key={oIdx}
                            type="button"
                            onClick={() => handleSelectQuizOption(qIdx, oIdx)}
                            className={`w-full text-right p-2 text-xs border font-arabic transition-all flex items-center justify-between ${btnStyle}`}
                            dir="rtl"
                          >
                            <div className="flex flex-col text-right flex-1" dir="rtl">
                              <span className={isSelected && !quizSubmitted ? 'text-white font-bold' : 'text-slate-900'}>{opt}</span>
                              {q.options_en?.[oIdx] && (
                                <span
                                  className={`text-[10.5px] font-sans italic mt-0.5 text-left ${
                                    isSelected && !quizSubmitted ? 'text-emerald-200' : 'text-slate-500'
                                  }`}
                                  dir="ltr"
                                >
                                  {q.options_en[oIdx]}
                                </span>
                              )}
                            </div>
                            <span className="w-3.5 h-3.5 border border-current flex items-center justify-center text-[9px] mr-2 flex-shrink-0">
                              {isSelected ? '✓' : ''}
                            </span>
                          </button>
                        );
                      })}
                    </div>

                    {quizSubmitted && q.explanation_ar && (
                      <div className={`mt-2 p-2 text-xs font-arabic text-right border ${isCorrect ? 'bg-emerald-50 border-emerald-300 text-emerald-950' : 'bg-amber-50 border-amber-300 text-amber-950'}`} dir="rtl">
                        <div className="font-bold">{isCorrect ? '🌟 ممتاز! ' : '💡 توضيح: '}</div>
                        <div><ArabicWordSpans text={q.explanation_ar} /></div>
                        {q.explanation_en && (
                          <div className="text-[10.5px] font-sans italic mt-1 pt-1 border-t border-slate-200 text-left" dir="ltr">
                            {q.explanation_en}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-200">
              <button
                onClick={() => setSelectedCapsule(null)}
                className="text-xs text-slate-600 hover:text-slate-900 font-bold"
              >
                إغلاق (Close)
              </button>

              {!quizSubmitted ? (
                <button
                  onClick={handleFinishCapsule}
                  disabled={Object.keys(quizAnswers).length < selectedCapsule.quiz.length}
                  className="bg-emerald-900 text-white text-xs font-bold px-5 py-2 border-2 border-slate-900 uppercase tracking-wider hover:bg-emerald-800 disabled:opacity-50"
                >
                  إتمام الكبسولة والتحقق (Complete & Check)
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-800 flex items-center gap-1">
                    <CheckCircle className="w-4 h-4" />
                    <span>تم الإنجاز ونيل وسام الكبسولة 🏅 (Capsule Badge Earned)</span>
                  </span>
                  <button
                    onClick={() => setSelectedCapsule(null)}
                    className="bg-emerald-900 text-white text-xs font-bold px-4 py-2 border-2 border-slate-900"
                  >
                    تم (Done)
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
