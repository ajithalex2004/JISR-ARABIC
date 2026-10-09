import React, { useState, useEffect } from 'react';
import {
  Award, Clock, CheckCircle2, XCircle, AlertCircle, BarChart3,
  Layers, ArrowRight, ArrowLeft, RefreshCw, Sparkles, BookOpen
} from 'lucide-react';
import { api } from '../../services/api';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ChildProfile } from '../../types';

interface AdaptiveAssessmentStudioProps {
  activeChild: ChildProfile | null;
}

export const AdaptiveAssessmentStudio: React.FC<AdaptiveAssessmentStudioProps> = ({ activeChild }) => {
  const [activeTab, setActiveTab] = useState<'simulation' | 'adaptive'>('simulation');

  // Exam Simulation State
  const [examData, setExamData] = useState<any | null>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState<number>(0);
  const [examAnswers, setExamAnswers] = useState<Record<string, number>>({});
  const [secondsRemaining, setSecondsRemaining] = useState<number>(1200);
  const [isExamActive, setIsExamActive] = useState<boolean>(false);
  const [isExamSubmitted, setIsExamSubmitted] = useState<boolean>(false);
  const [examResult, setExamResult] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Fetch Exam Data
  useEffect(() => {
    const fetchExam = async () => {
      setLoading(true);
      try {
        const grade = activeChild?.default_grade || 5;
        const term = activeChild?.selected_term || 1;
        const res = await api.getExamSimulation(grade, term, activeChild?.id);
        if (res.success && res.exam) {
          setExamData(res.exam);
          setSessionId(res.session_id || null);
          setSecondsRemaining(res.exam.time_limit_seconds || 1200);
        }
      } catch (err) {
        console.error('Failed to load exam:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchExam();
  }, [activeChild?.id]);

  // Timer countdown
  useEffect(() => {
    if (!isExamActive || isExamSubmitted || secondsRemaining <= 0) return;
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isExamActive, isExamSubmitted, secondsRemaining]);

  const handleSelectExamOption = (questionId: string, optionIdx: number) => {
    if (isExamSubmitted) return;
    setExamAnswers((prev) => ({ ...prev, [questionId]: optionIdx }));
  };

  const handleSubmitExam = async () => {
    if (isExamSubmitted) return;
    setLoading(true);
    const timeSpent = (examData?.time_limit_seconds || 1200) - secondsRemaining;
    try {
      const res = await api.submitExamSimulation({
        child_id: activeChild?.id || 'guest_child',
        grade: activeChild?.default_grade || 5,
        term: activeChild?.selected_term || 1,
        answers: examAnswers,
        time_taken_seconds: Math.max(timeSpent, 30)
        ,session_id: sessionId || undefined
      });
      if (res.success) {
        setExamResult(res.evaluation);
        setIsExamSubmitted(true);
        setIsExamActive(false);
      }
    } catch (err) {
      console.error('Failed to submit exam simulation:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const questions = examData?.questions || [];
  const activeQ = questions[currentQuestionIdx];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Module Title Banner */}
      <div className="bg-slate-900 text-white border-2 border-slate-900 p-6 mb-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight font-arabic">
            الاختبارات التكيفية ومحاكاة الاختبار
          </h1>
          <p className="text-base text-amber-300 mt-1 font-semibold">
            Adaptive Assessment &amp; Exam Simulation
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-2 border-amber-400 bg-slate-800 p-1">
          <button
            onClick={() => setActiveTab('simulation')}
            className={`px-4 py-2 text-xs font-bold transition-all ${
              activeTab === 'simulation' ? 'bg-amber-400 text-slate-950' : 'text-slate-300 hover:text-white'
            }`}
          >
            محاكاة الاختبار (Exam Simulation)
          </button>
          <button
            onClick={() => setActiveTab('adaptive')}
            className={`px-4 py-2 text-xs font-bold transition-all ${
              activeTab === 'adaptive' ? 'bg-amber-400 text-slate-950' : 'text-slate-300 hover:text-white'
            }`}
          >
            تدفق الصعوبة التكيفي (Flow State)
          </button>
        </div>
      </div>

      {/* TAB 1: OFFICIAL EXAM SIMULATION */}
      {activeTab === 'simulation' && (
        <div>
          {!isExamActive && !isExamSubmitted ? (
            /* Exam Start Screen */
            <div className="bg-white border-2 border-slate-900 p-8 text-center max-w-2xl mx-auto shadow-sm">
              <div className="w-16 h-16 bg-emerald-900 text-amber-400 flex items-center justify-center font-bold text-2xl mx-auto mb-4 border-2 border-slate-900">
                <Award className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-black text-slate-900 mb-2 font-arabic">
                {examData?.exam_title_ar || 'محاكاة الاختبار'}
              </h2>
              <p className="text-xs text-slate-500 mb-6 font-mono">
                {examData?.curriculum} · الصف 5 الفصل 1
              </p>

              <div className="grid grid-cols-3 gap-3 bg-slate-50 p-4 border border-slate-200 mb-6 text-xs">
                <div>
                  <span className="text-slate-500 block">المدة الزمنية (Time Limit)</span>
                  <span className="font-bold text-slate-900 text-sm">20 دقيقة (20 Mins)</span>
                </div>
                <div>
                  <span className="text-slate-500 block">عدد الأسئلة (Total Questions)</span>
                  <span className="font-bold text-slate-900 text-sm">{examData?.total_questions || 10} أسئلة (10 Qs)</span>
                </div>
                <div>
                  <span className="text-slate-500 block">مستويات بلوم (Bloom Levels)</span>
                  <span className="font-bold text-slate-900 text-sm">4 مستويات (4 Levels)</span>
                </div>
              </div>

              <button
                onClick={() => setIsExamActive(true)}
                className="bg-emerald-900 text-white text-sm font-bold px-8 py-3 border-2 border-slate-900 uppercase tracking-wider hover:bg-emerald-800 transition-colors shadow-sm"
              >
                ابدأ الاختبار الآن (Start Exam Now)
              </button>
            </div>
          ) : isExamActive && !isExamSubmitted ? (
            /* Live Exam Player */
            <div className="bg-white border-2 border-slate-900 shadow-sm p-6">
              {/* Exam Top Bar with Timer */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-6">
                <div>
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                    السؤال {currentQuestionIdx + 1} من {questions.length} (Question {currentQuestionIdx + 1} of {questions.length})
                  </span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="bg-emerald-100 text-emerald-950 text-[10px] font-black px-2 py-0.5 border border-emerald-300 uppercase">
                      {activeQ?.bloom_name_ar} ({activeQ?.bloom_name_en})
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      {activeQ?.points} درجات ({activeQ?.points} Pts)
                    </span>
                  </div>
                </div>

                {/* Countdown Timer */}
                <div className={`flex items-center gap-2 px-3.5 py-1.5 border-2 font-mono text-sm font-bold ${
                  secondsRemaining < 300
                    ? 'bg-rose-100 text-rose-950 border-rose-600 animate-pulse'
                    : 'bg-slate-900 text-amber-400 border-slate-900'
                }`}>
                  <Clock className="w-4 h-4" />
                  <span>{formatTimer(secondsRemaining)}</span>
                </div>
              </div>

              {/* Question Navigation Palette */}
              <div className="flex flex-wrap gap-1.5 mb-6 bg-slate-50 p-2.5 border border-slate-200">
                {questions.map((q: any, idx: number) => {
                  const isAnswered = examAnswers[q.id] !== undefined;
                  const isCurrent = idx === currentQuestionIdx;
                  return (
                    <button
                      key={q.id}
                      onClick={() => setCurrentQuestionIdx(idx)}
                      className={`w-7 h-7 text-xs font-bold border transition-all ${
                        isCurrent
                          ? 'border-emerald-950 bg-emerald-900 text-white'
                          : isAnswered
                          ? 'border-emerald-600 bg-emerald-100 text-emerald-950'
                          : 'border-slate-300 bg-white text-slate-700 hover:border-slate-500'
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>

              {/* Active Question Body */}
              {activeQ && (
                <div className="mb-8">
                  <div className="p-4 bg-slate-50 border border-slate-200 mb-4 rounded-sm">
                    <div className="text-base font-black text-slate-900 font-arabic text-right leading-relaxed" dir="rtl">
                      <ArabicWordSpans text={activeQ.question_ar} className="text-base font-black text-slate-900 font-arabic" />
                    </div>
                    {activeQ.question_en && (
                      <div className="text-xs text-slate-600 font-sans italic mt-2 pt-2 border-t border-slate-200 text-left" dir="ltr">
                        {activeQ.question_en}
                      </div>
                    )}
                  </div>

                  <div className="space-y-2.5">
                    {activeQ.options.map((opt: string, oIdx: number) => {
                      const isSelected = examAnswers[activeQ.id] === oIdx;
                      return (
                        <div
                          key={oIdx}
                          onClick={() => handleSelectExamOption(activeQ.id, oIdx)}
                          className={`p-3 text-xs border-2 cursor-pointer transition-all flex items-center justify-between ${
                            isSelected
                              ? 'bg-emerald-900 text-white border-emerald-950 font-bold'
                              : 'bg-white text-slate-800 border-slate-300 hover:border-slate-800'
                          }`}
                        >
                          <div className="flex flex-col text-right flex-1" dir="rtl">
                            <ArabicWordSpans
                              text={opt}
                              className={`font-arabic text-sm ${isSelected ? 'text-white font-bold' : 'text-slate-900 font-semibold'}`}
                            />
                            {activeQ.options_en?.[oIdx] && (
                              <span
                                className={`text-xs font-sans mt-0.5 text-left italic ${
                                  isSelected ? 'text-emerald-200' : 'text-slate-500'
                                }`}
                                dir="ltr"
                              >
                                {activeQ.options_en[oIdx]}
                              </span>
                            )}
                          </div>
                          <span className="w-4 h-4 border border-current flex items-center justify-center text-[10px] ml-3 flex-shrink-0">
                            {isSelected ? '✓' : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Bottom Nav Controls */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                <button
                  onClick={() => setCurrentQuestionIdx((prev) => Math.max(0, prev - 1))}
                  disabled={currentQuestionIdx === 0}
                  className="px-4 py-2 border border-slate-300 text-xs font-bold disabled:opacity-30 flex items-center gap-1"
                >
                  <ArrowRight className="w-3.5 h-3.5" />
                  <span>السابق (Previous)</span>
                </button>

                {currentQuestionIdx < questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentQuestionIdx((prev) => Math.min(questions.length - 1, prev + 1))}
                    className="px-4 py-2 bg-slate-900 text-white text-xs font-bold flex items-center gap-1"
                  >
                    <span>التالي (Next)</span>
                    <ArrowLeft className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmitExam}
                    disabled={loading}
                    className="px-6 py-2 bg-emerald-900 text-white border-2 border-slate-900 text-xs font-bold uppercase tracking-wider hover:bg-emerald-800"
                  >
                    {loading ? 'جارٍ التصحيح... (Grading...)' : 'إنهاء وتصحيح الاختبار (Submit & Grade Exam)'}
                  </button>
                )}
              </div>
            </div>
          ) : (
            /* Post-Exam Report & Solution Walkthroughs */
            <div className="space-y-6">
              {/* Scorecard Hero */}
              <div className="bg-white border-2 border-slate-900 p-6 shadow-sm flex flex-wrap items-center justify-between gap-6">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="bg-emerald-800 text-white text-[10px] font-bold px-2 py-0.5 uppercase">
                      تقرير النتيجة الرسمية (Official Score Report)
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      تم تصحيح الإجابات آلياً بدقة (Automatically & accurately graded)
                    </span>
                  </div>
                  <h2 className="text-2xl font-black text-slate-900 font-arabic">
                    نتيجة محاكاة الاختبار (Exam Simulation Result)
                  </h2>
                  <p className="text-xs text-slate-700 mt-1 font-arabic font-bold" dir="rtl">
                    {examResult?.feedback_ar}
                  </p>
                  {examResult?.feedback_en && (
                    <p className="text-xs text-slate-500 mt-1 italic font-sans" dir="ltr">
                      {examResult.feedback_en}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-4 bg-slate-50 p-4 border border-slate-200">
                  <div className="text-center">
                    <span className="text-3xl font-black text-emerald-950 font-mono">
                      {examResult?.percentage}%
                    </span>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">النسبة المئوية (Score)</span>
                  </div>
                  <div className="w-px h-10 bg-slate-300" />
                  <div className="text-center">
                    <span className="text-3xl font-black text-amber-600 font-mono">
                      {examResult?.grade_letter}
                    </span>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">التقدير (Grade)</span>
                  </div>
                  <div className="w-px h-10 bg-slate-300" />
                  <div className="text-center">
                    <span className="text-xl font-black text-slate-900 font-mono">
                      {examResult?.correct_count} / {examResult?.total_questions}
                    </span>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">الإجابات الصحيحة (Correct)</span>
                  </div>
                </div>
              </div>

              {/* Bloom's Taxonomy Breakdown */}
              <div className="bg-white border-2 border-slate-900 p-6 shadow-sm">
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-emerald-800" />
                  <span>تحليل الأداء حسب هرم بلوم المعرفي (Bloom's Taxonomy)</span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                  {examResult?.bloom_breakdown && Object.entries(examResult.bloom_breakdown).map(([key, b]: any) => (
                    <div key={key} className="p-3.5 bg-slate-50 border border-slate-300">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="font-bold text-xs text-slate-900 font-arabic">{b.name_ar}</span>
                        <span className="text-[10px] text-slate-500 font-mono">{b.percentage}%</span>
                      </div>
                      <div className="w-full bg-slate-200 h-2 mb-2">
                        <div
                          className="bg-emerald-800 h-2 transition-all duration-500"
                          style={{ width: `${b.percentage}%` }}
                        />
                      </div>
                      <span className="text-[11px] text-slate-600">
                        {b.correct} من أصل {b.total} أسئلة صحيحة
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Detailed Solution Walkthroughs */}
              <div className="bg-white border-2 border-slate-900 p-6 shadow-sm">
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-emerald-800" />
                  <span>دليل الحلول النموذجية وتفسير الأخطاء (Solution Walkthroughs)</span>
                </h3>

                <div className="space-y-4">
                  {examResult?.solution_walkthrough?.map((item: any, idx: number) => {
                    const isCorrect = item.is_correct;
                    return (
                      <div
                        key={item.question_id}
                        className={`p-4 border-2 text-right ${
                          isCorrect ? 'border-emerald-300 bg-emerald-50/30' : 'border-rose-300 bg-rose-50/30'
                        }`}
                        dir="rtl"
                      >
                        <div className="flex justify-between items-center mb-2" dir="ltr">
                          <span className={`text-xs font-bold px-2 py-0.5 border ${
                            isCorrect ? 'bg-emerald-100 text-emerald-950 border-emerald-400' : 'bg-rose-100 text-rose-950 border-rose-400'
                          }`}>
                            {isCorrect ? '✓ إجابة صحيحة' : '✗ إجابة غير صحيحة'}
                          </span>
                          <span className="text-xs font-bold text-slate-500">
                            السؤال {idx + 1}
                          </span>
                        </div>

                        <div className="mb-2">
                          <p className="font-arabic text-sm font-bold text-slate-900">
                            <ArabicWordSpans text={item.question_ar} className="font-arabic text-sm font-bold text-slate-900" />
                          </p>
                          {item.question_en && (
                            <p className="text-xs text-slate-500 font-sans italic mt-1 text-left" dir="ltr">
                              {item.question_en}
                            </p>
                          )}
                        </div>

                        <div className="text-xs text-slate-700 space-y-1.5 mb-3">
                          <div>
                            <span className="font-bold text-slate-500">إجابتك (Your Answer): </span>
                            <span className={isCorrect ? 'text-emerald-900 font-bold' : 'text-rose-700 font-bold'}>
                              {item.selected_option !== undefined ? (
                                <span className="inline-flex flex-col align-top ml-1">
                                  <ArabicWordSpans text={item.options[item.selected_option]} />
                                  {item.options_en?.[item.selected_option] && (
                                    <span className="text-[11px] text-slate-500 font-sans italic" dir="ltr">
                                      {item.options_en[item.selected_option]}
                                    </span>
                                  )}
                                </span>
                              ) : (
                                'لم تجب (Not answered)'
                              )}
                            </span>
                          </div>
                          {!isCorrect && (
                            <div>
                              <span className="font-bold text-slate-500">الإجابة النموذجية (Correct Answer): </span>
                              <span className="text-emerald-950 font-bold inline-flex flex-col align-top ml-1">
                                <ArabicWordSpans text={item.options[item.correct_option]} />
                                {item.options_en?.[item.correct_option] && (
                                  <span className="text-[11px] text-slate-500 font-sans italic" dir="ltr">
                                    {item.options_en[item.correct_option]}
                                  </span>
                                )}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Detailed Rationale */}
                        <div className="bg-white p-3 border border-slate-200 text-xs text-slate-800 leading-relaxed font-arabic">
                          <span className="font-bold text-emerald-950 block mb-1">
                            💡 تفسير الحل النموذجي (Model Solution Explanation):
                          </span>
                          <ArabicWordSpans text={item.solution_walkthrough_ar} className="text-xs leading-relaxed" />
                          {item.solution_walkthrough_en && (
                            <div className="text-xs text-slate-600 font-sans italic mt-2 pt-2 border-t border-slate-100 text-left" dir="ltr">
                              {item.solution_walkthrough_en}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-6 text-center">
                  <button
                    onClick={() => {
                      setIsExamSubmitted(false);
                      setIsExamActive(false);
                      setExamAnswers({});
                      setCurrentQuestionIdx(0);
                      setSecondsRemaining(examData?.time_limit_seconds || 1200);
                    }}
                    className="bg-emerald-900 text-white text-xs font-bold px-6 py-2.5 border-2 border-slate-900 uppercase tracking-wider hover:bg-emerald-800"
                  >
                    إعادة محاكاة الاختبار (Retake Exam Simulation)
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ADAPTIVE FLOW STATE (تدفق الصعوبة التكيفي) */}
      {activeTab === 'adaptive' && (
        <div className="bg-white border-2 border-slate-900 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <h2 className="text-lg font-black text-slate-900 font-arabic">
              نظام الصعوبة التكيفية (Flow State Adaptive Assessment)
            </h2>
          </div>
          <p className="text-xs text-slate-600 mb-1 leading-relaxed">
            محرك الاختبارات يضبط مستوى الصعوبة تلقائياً: عند حل الأسئلة بنجاح يرتقي النظام من المستوى السهل إلى المتوسط ثم المتقدم والتحدي، بينما يقدم تلميحات داعمة عند مواجهة صعوبة لضمان تدفق التركيز ومنع الإحباط.
          </p>
          <p className="text-xs text-slate-500 mb-6 italic font-sans">
            The adaptive exam engine dynamically scales question difficulty from Easy to Medium, Hard, and Challenge tiers while offering targeted hints when struggles occur to sustain deep focus.
          </p>

          <div className="grid grid-cols-4 gap-2 text-center text-xs font-bold mb-6">
            <div className="p-3 bg-emerald-50 border border-emerald-300 text-emerald-950">
              ١. التأسيس (Easy)
            </div>
            <div className="p-3 bg-amber-50 border border-amber-300 text-amber-950">
              ٢. التوجيه (Medium)
            </div>
            <div className="p-3 bg-blue-50 border border-blue-300 text-blue-950">
              ٣. التمكن (Hard)
            </div>
            <div className="p-3 bg-purple-50 border border-purple-300 text-purple-950">
              ٤. التحدي (Challenge)
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 p-4 text-xs text-slate-700 leading-relaxed font-arabic text-right" dir="rtl">
            <span className="font-bold text-slate-900 block mb-1">
              ميزة اختبار التدفق التكيفي نشطة في كافة الوحدات الدراسية (Adaptive Flow Active Across All Units).
            </span>
            يمكن للطلاب خوض التدريب التكيفي المباشر أثناء حل تمارين الفصول، حيث تظهر التلميحات الذكية تلقائياً عند أول خطأ، وتُسجل نقاط القوة في دفتر الملاحظات الخاص بالطالب.
            <div className="text-[11px] text-slate-500 font-sans italic mt-2 pt-2 border-t border-slate-200 text-left" dir="ltr">
              Students experience real-time adaptive flow during chapter exercises: intelligent hints surface automatically on the first slip, and strengths are saved to the student review notebook.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
