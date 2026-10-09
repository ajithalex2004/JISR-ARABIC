import React, { useState, useEffect, useMemo } from 'react';
import {
  BookOpen, Clock, FileText, CheckCircle2,
  Volume2, ArrowRight, Sparkles, Layers, Bookmark, GraduationCap
} from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';
import { User, ChildProfile } from '../../types';

interface MalazimViewerProps {
  user?: User | null;
  activeChild?: ChildProfile | null;
  initialGrade?: number;
  lessonId?: string;
  onSelectGrade?: (grade: number) => void;
}

export const MalazimViewer: React.FC<MalazimViewerProps> = ({
  user,
  activeChild,
  initialGrade = 5,
  lessonId,
  onSelectGrade
}) => {
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

  const [bookletData, setBookletData] = useState<any | null>(null);
  const [activeMode, setActiveMode] = useState<'study' | 'quick_review'>('study');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [submittedExercises, setSubmittedExercises] = useState<Record<string, boolean>>({});

  const [feedback, setFeedback] = useState<Record<string, any>>({});
  const [error, setError] = useState('');

  const targetLessonId = lessonId || (selectedGrade === 7 ? 'lesson_g7_t1_ch01' : selectedGrade === 6 ? 'lesson_g6_t1_ch01' : 'lesson_01_ball_games');

  useEffect(() => {
    const fetchBooklet = async () => {
      setLoading(true);
      try {
        const res = await api.getMalazim(targetLessonId, activeChild?.id, selectedGrade);
        if (res.success && res.booklet) {
          setBookletData(res.booklet);
        }
      } catch (err) {
        console.error('Failed to load malazim:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBooklet();
  }, [targetLessonId, selectedGrade, activeChild?.id]);

  const handleSelectOption = (sectionId: string, optionIdx: number) => {
    if (submittedExercises[sectionId]) return;
    setSelectedAnswers((prev) => ({ ...prev, [sectionId]: optionIdx }));
  };

  const handleSubmitExercise = async (sectionId: string) => {
    try {
      setError('');
      const result = await api.checkBookletAnswer(targetLessonId, sectionId, selectedAnswers[sectionId], activeChild?.id);
      setFeedback(prev => ({ ...prev, [sectionId]: result }));
      setSubmittedExercises(prev => ({ ...prev, [sectionId]: true }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to check answer');
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-slate-600">
        <BookOpen className="w-8 h-8 text-emerald-800 animate-pulse mx-auto mb-2" />
        <p className="font-bold text-sm">جَارٍ تَحْمِيلُ المَلْزَمَةِ الذَّكِيَّةِ...</p>
      </div>
    );
  }

  const studyMode = bookletData?.study_mode;
  const quickReview = bookletData?.quick_review_mode;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {error && <p role="alert" className="text-red-700 mb-4">{error}</p>}

      {/* Grade Selector Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 bg-white border border-slate-200 p-3 rounded-sm shadow-2xs">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
            <GraduationCap className="w-4 h-4 text-emerald-800" />
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
                    ? 'bg-emerald-800 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                الصف {g} (Grade {g})
              </button>
            ))}
          </div>
        </div>
        <div className="text-xs text-slate-500 font-sans flex items-center gap-2">
          <span>{bookletData?.curriculum_alignment || 'UAE MoE & CBSE Aligned'}</span>
          <span className="text-slate-300">|</span>
          <span className="font-semibold text-emerald-800">{bookletData?.pages_reference || `Grade ${selectedGrade}`}</span>
        </div>
      </div>

      {/* Header Banner */}
      <div className="bg-emerald-950 text-white border-2 border-slate-900 p-6 mb-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="bg-amber-400 text-slate-950 text-[10px] font-bold px-2 py-0.5 rounded-2xs uppercase tracking-wider">
              الصف {selectedGrade} · Grade {selectedGrade}
            </span>
            <span className="text-xs text-emerald-300 font-sans">
              {bookletData?.title_en}
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight font-arabic">
            {bookletData?.title_ar || `ملزمة الصف ${selectedGrade} الذكية`}
          </h1>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          <ArabEnglishToggleSwitch />
          {/* Dual Mode Switcher Tabs */}
          <div className="flex border-2 border-amber-400 bg-slate-900 p-1 rounded-sm">
          <button
            onClick={() => setActiveMode('study')}
            className={`px-4 py-2 text-xs font-bold transition-all flex flex-col items-center justify-center gap-0.5 ${
              activeMode === 'study'
                ? 'bg-amber-400 text-slate-950'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-1.5">
              <BookOpen className="w-4 h-4" />
              <span className="font-arabic font-bold text-xs">وضع المذاكرة الشامل</span>
            </div>
            <span className="text-[10px] font-sans font-normal opacity-90">Comprehensive Study Mode</span>
          </button>
          <button
            onClick={() => setActiveMode('quick_review')}
            className={`px-4 py-2 text-xs font-bold transition-all flex flex-col items-center justify-center gap-0.5 ${
              activeMode === 'quick_review'
                ? 'bg-amber-400 text-slate-950'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              <span className="font-arabic font-bold text-xs">مراجعة الـ 15 دقيقة</span>
            </div>
            <span className="text-[10px] font-sans font-normal opacity-90">15-Minute Quick Notes</span>
          </button>
        </div>
      </div>
    </div>

      {/* MODE 1: STUDY MODE */}
      {activeMode === 'study' && studyMode && (
        <div className="space-y-6">
          {studyMode.sections.map((sec: any) => {
            const isSubmitted = submittedExercises[sec.section_id];
            const selectedIdx = selectedAnswers[sec.section_id];
            const isCorrect = feedback[sec.section_id]?.is_correct === true;

            return (
              <div key={sec.section_id} className="bg-white border-2 border-slate-900 p-5 shadow-sm">
                <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-black text-slate-900 font-arabic">
                      <ArabicWordSpans text={sec.title_ar} className="text-base font-black text-slate-900" />
                    </h2>
                    <span className="text-xs text-slate-500 font-sans">({sec.title_en})</span>
                  </div>
                  <button
                    onClick={() => audioManager.playArabic(sec.content_ar)}
                    className="text-emerald-800 hover:text-emerald-950 p-1.5 flex items-center gap-1.5 text-xs font-bold border border-slate-300 hover:border-slate-800 bg-white"
                    title="استمع إلى الشرح / Listen"
                  >
                    <Volume2 className="w-4 h-4 text-emerald-800" />
                    <span>استمع (Listen)</span>
                  </button>
                </div>

                <div className="text-sm text-slate-800 leading-relaxed text-right mb-3" dir="rtl">
                  <ArabicWordSpans text={sec.content_ar} className="text-sm leading-relaxed" />
                </div>
                <p className="text-xs text-slate-500 italic mb-4">
                  {sec.content_en}
                </p>

                {/* Key Takeaways */}
                <div className="bg-slate-50 border border-slate-200 p-3.5 mb-4">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block font-arabic">
                    النقاط الجوهرية:
                  </span>
                  <span className="text-[10px] text-slate-500 font-sans block mb-2">
                    Key Takeaways & Core Concepts
                  </span>
                  <ul className="space-y-2 text-xs text-slate-800 list-disc list-inside font-arabic" dir="rtl">
                    {sec.key_takeaways_ar.map((point: string, idx: number) => (
                      <li key={idx}>
                        <ArabicWordSpans text={point} className="text-xs font-semibold" />
                        {sec.key_takeaways_en?.[idx] && (
                          <div className="text-[11px] text-slate-500 font-sans italic text-left mr-4 mt-0.5" dir="ltr">
                            {sec.key_takeaways_en[idx]}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Inline Mini-Exercise */}
                <div className="bg-emerald-50/70 border border-emerald-300 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-emerald-800" />
                    <div>
                      <span className="text-xs font-black uppercase tracking-wider text-emerald-950 block font-arabic">
                        تطبيق فوري مباشر:
                      </span>
                      <span className="text-[10px] text-emerald-700 font-sans block">
                        Inline Concept Check
                      </span>
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-sm font-bold text-slate-900 text-right" dir="rtl">
                      <ArabicWordSpans text={sec.inline_exercise.question_ar} className="text-sm font-bold text-slate-900" />
                    </div>
                    {sec.inline_exercise.question_en && (
                      <div className="text-xs text-slate-600 font-sans italic mt-1 text-left" dir="ltr">
                        {sec.inline_exercise.question_en}
                      </div>
                    )}
                  </div>

                  <div className="space-y-2 mb-3">
                    {sec.inline_exercise.options.map((opt: string, oIdx: number) => {
                      const isSelected = selectedIdx === oIdx;
                      let optionClasses = "bg-white border-slate-300 text-slate-800 hover:border-slate-600";
                      if (isSelected && !isSubmitted) {
                        optionClasses = "bg-emerald-900 text-white border-emerald-950";
                      } else if (isSubmitted) {
                        if (oIdx === feedback[sec.section_id]?.correct_index) {
                          optionClasses = "bg-emerald-100 border-emerald-600 text-emerald-950 font-bold";
                        } else if (isSelected && !isCorrect) {
                          optionClasses = "bg-rose-100 border-rose-600 text-rose-950";
                        }
                      }

                      return (
                        <div
                          key={oIdx}
                          onClick={() => handleSelectOption(sec.section_id, oIdx)}
                          className={`p-2.5 text-xs border cursor-pointer transition-all flex items-center justify-between ${optionClasses}`}
                        >
                          <div className="flex flex-col text-right flex-1" dir="rtl">
                            <ArabicWordSpans
                              text={opt}
                              className={`text-xs ${isSelected && !isSubmitted ? 'text-white font-bold' : 'text-slate-900 font-semibold'}`}
                            />
                            {sec.inline_exercise.options_en?.[oIdx] && (
                              <span
                                className={`text-[11px] font-sans italic mt-0.5 text-left ${
                                  isSelected && !isSubmitted ? 'text-emerald-200' : 'text-slate-500'
                                }`}
                                dir="ltr"
                              >
                                {sec.inline_exercise.options_en[oIdx]}
                              </span>
                            )}
                          </div>
                          <span className="w-4 h-4 border border-current flex items-center justify-center text-[10px] ml-2 flex-shrink-0">
                            {isSelected ? '✓' : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  {!isSubmitted ? (
                    <button
                      onClick={() => handleSubmitExercise(sec.section_id)}
                      disabled={selectedIdx === undefined}
                      className="bg-emerald-900 text-white text-xs font-bold px-4 py-2 border border-emerald-950 uppercase tracking-wider disabled:opacity-50 flex flex-col items-center"
                    >
                      <span>تحقق من الإجابة</span>
                      <span className="text-[10px] font-normal font-sans opacity-90">Check Answer</span>
                    </button>
                  ) : (
                    <div className={`p-2.5 text-xs font-arabic text-right border ${isCorrect ? 'bg-emerald-100 border-emerald-400 text-emerald-950' : 'bg-amber-100 border-amber-400 text-amber-950'}`} dir="rtl">
                      <div className="font-bold mb-0.5">{isCorrect ? '🌟 ممتاز! ' : '💡 انتبه: '}</div>
                      <ArabicWordSpans text={feedback[sec.section_id]?.explanation_ar || ''} />
                      {feedback[sec.section_id]?.explanation_en && (
                        <div className="text-[11px] text-slate-700 font-sans italic mt-1.5 pt-1.5 border-t border-emerald-200/50 text-left" dir="ltr">
                          {feedback[sec.section_id]?.explanation_en || ''}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* MODE 2: QUICK REVIEW / 15-MIN CHEAT SHEET */}
      {activeMode === 'quick_review' && quickReview && (
        <div className="space-y-6">
          {/* Bulleted Rules Card */}
          <div className="bg-white border-2 border-slate-900 p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-emerald-800" />
              <div>
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider font-arabic">
                  الخلاصة المركزة لأهم الحقائق
                </h3>
                <span className="text-[11px] text-slate-500 font-sans block">
                  Essential Facts & Rules Summary
                </span>
              </div>
            </div>
            <div className="divide-y divide-slate-200">
              {quickReview.bullet_rules.map((item: any, idx: number) => (
                <div key={idx} className="py-3">
                  <div className="font-arabic text-sm text-slate-900 font-semibold text-right" dir="rtl">
                    • {item.rule_ar}
                  </div>
                  {item.rule_en && (
                    <div className="text-xs text-slate-600 font-sans italic mt-1 text-left pl-4" dir="ltr">
                      {item.rule_en}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Vocabulary Flashcards Grid */}
          <div className="bg-white border-2 border-slate-900 p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-800" />
              <div>
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider font-arabic">
                  بطاقات المفردات والأضداد
                </h3>
                <span className="text-[11px] text-slate-500 font-sans block">
                  Vocabulary & Antonyms Flashcards
                </span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {quickReview.vocabulary_flashcards.map((card: any, idx: number) => (
                <div key={idx} className="p-3.5 bg-slate-50 border border-slate-300 flex flex-col justify-between">
                  <div className="flex justify-between items-center mb-1.5">
                    <div>
                      <span className="text-base font-black text-emerald-950 font-arabic">{card.word_ar}</span>
                      {card.word_en && <span className="text-xs text-slate-600 font-sans block font-semibold">{card.word_en}</span>}
                    </div>
                    <button
                      onClick={() => audioManager.playArabic(card.word_ar)}
                      className="text-emerald-800 hover:text-emerald-950 p-1"
                      title="استمع للكلمة / Pronounce"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="text-xs text-slate-700 text-right mb-1.5" dir="rtl">
                    <span className="text-slate-500 font-sans font-bold">المعنى: </span>{card.meaning_ar}
                    {card.meaning_en && (
                      <span className="text-[11px] text-slate-600 font-sans italic block text-left mt-0.5" dir="ltr">
                        Meaning: {card.meaning_en}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-700 text-right" dir="rtl">
                    <span className="text-slate-500 font-sans font-bold">الضد: </span>
                    <span className="text-amber-800 font-bold">{card.opposite_ar}</span>
                    {card.opposite_en && card.opposite_en !== '—' && (
                      <span className="text-[11px] text-slate-600 font-sans italic block text-left mt-0.5" dir="ltr">
                        Antonym: {card.opposite_en}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Grammar Formulas */}
          <div className="bg-white border-2 border-slate-900 p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-800" />
              <div>
                <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider font-arabic">
                  معادلات القواعد النحوية
                </h3>
                <span className="text-[11px] text-slate-500 font-sans block">
                  Grammar Rules & Synthesis Formulas
                </span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quickReview.grammar_formulas.map((form: any, idx: number) => (
                <div key={idx} className="p-3.5 bg-amber-50/60 border border-amber-300">
                  <span className="text-xs font-bold text-amber-950 block mb-0.5 font-arabic">{form.title_ar}</span>
                  {form.title_en && <span className="text-[11px] text-slate-600 block mb-1 font-sans">{form.title_en}</span>}
                  <div className="font-mono text-xs font-bold text-slate-900 bg-white p-2.5 border border-slate-200 mb-2 text-center">
                    <div>{form.formula_ar}</div>
                    {form.formula_en && <div className="text-[10px] text-slate-500 font-normal mt-0.5">{form.formula_en}</div>}
                  </div>
                  <div className="text-xs text-slate-700 text-right" dir="rtl">
                    <div><span className="text-slate-500 font-sans font-bold">مثال: </span>{form.example_ar}</div>
                    {form.example_en && (
                      <div className="text-[11px] text-slate-600 font-sans italic text-left mt-0.5" dir="ltr">
                        Example: {form.example_en}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}
    </div>
  );
};
