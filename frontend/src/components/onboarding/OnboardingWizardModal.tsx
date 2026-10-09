import React, { useState, useEffect } from 'react';
import {
  X, CheckCircle2, ChevronRight, ChevronLeft, Award, Sparkles, BookOpen,
  Calendar, School, User, Lock, Compass, BrainCircuit, ArrowRight, RefreshCw, BarChart2
} from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, DiagnosticQuestion, DiagnosticResult, LearningPlan } from '../../types';
import { UAE_AVATARS } from '../auth/AuthModal';

export const CURRICULUM_STREAMS_LIST = [
  {
    id: 'MoE / CBSE Arabic (Non-Arabs)',
    titleAr: 'منهاج وزارة التربية والتعليم / CBSE (للناطقين بغير العربية)',
    titleEn: 'MoE / CBSE Arabic B (Non-Arabs)',
    descAr: 'المنهاج المعتمد لمدارس CBSE والمدارس الخاصة في دولة الإمارات.'
  },
  {
    id: 'MoE General Stream',
    titleAr: 'المسار العام (وزارة التربية والتعليم)',
    titleEn: 'General Stream (MoE Curriculum)',
    descAr: 'يركز على الكفاءات اللغوية والتواصلية الأساسية وفق المعايير الوطنية.'
  },
  {
    id: 'MoE Advanced Stream',
    titleAr: 'المسار المتقدم (وزارة التربية والتعليم)',
    titleEn: 'Advanced Stream (MoE Curriculum)',
    descAr: 'نصوص أدبية متقدمة، تحليل نحوي وبلاغي، وتطبيقات كتابية معمقة.'
  },
  {
    id: 'MoE Elite Stream',
    titleAr: 'مسار النخبة (وزارة التربية والتعليم)',
    titleEn: 'Elite Stream (MoE Curriculum)',
    descAr: 'أعلى مستويات التحصيل اللغوي مع نصوص تراثية وتفكير نقدي.'
  },
  {
    id: 'International IB / British / American',
    titleAr: 'المدارس الدولية (IB / البريطاني / الأمريكي)',
    titleEn: 'International Stream (IB / British / American B)',
    descAr: 'مخصص لمتعلمي اللغة العربية كلغة إضافية مع معايير KHDA / ADEK.'
  }
];

interface OnboardingWizardModalProps {
  isOpen: boolean;
  child: ChildProfile | null;
  onClose: () => void;
  onComplete: (updatedChild: ChildProfile, plan: LearningPlan) => void;
}

export const OnboardingWizardModal: React.FC<OnboardingWizardModalProps> = ({
  isOpen,
  child,
  onClose,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);

  // Step 1: Demographics
  const [name, setName] = useState(child?.name || 'Zayed Al-Nuaimi');
  const [avatarId, setAvatarId] = useState(child?.avatar_id || 'avatar_falcon');
  const [gender, setGender] = useState(child?.gender || 'Boy');
  const [age, setAge] = useState(child?.age || 10);
  const [schoolName, setSchoolName] = useState(child?.school_name || 'Sunrise International School, Abu Dhabi');
  const [grade, setGrade] = useState(child?.default_grade || 5);

  // Step 2: Stream & Term
  const [stream, setStream] = useState(child?.curriculum_stream || 'MoE / CBSE Arabic (Non-Arabs)');
  const [selectedTerm, setSelectedTerm] = useState<number>(child?.selected_term || 1);
  const [accessPin, setAccessPin] = useState(child?.access_pin || '1234');

  // Step 3: Diagnostic Assessment
  const [questions, setQuestions] = useState<DiagnosticQuestion[]>([]);
  const [currentQIndex, setCurrentQIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);
  const [isSubmittingDiagnostic, setIsSubmittingDiagnostic] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState<DiagnosticResult | null>(null);

  // General Status
  const [errorMsg, setErrorMsg] = useState('');
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  // Reset and sync with incoming child
  useEffect(() => {
    if (isOpen && child) {
      setName(child.name || '');
      setAvatarId(child.avatar_id || 'avatar_falcon');
      setGender(child.gender || 'Boy');
      setAge(child.age || 10);
      setSchoolName(child.school_name || 'Sunrise International School, Abu Dhabi');
      setGrade(child.default_grade || 5);
      setStream(child.curriculum_stream || 'MoE / CBSE Arabic (Non-Arabs)');
      setSelectedTerm(child.selected_term || 1);
      setAccessPin(child.access_pin || '1234');
      setCurrentStep(1);
      setErrorMsg('');
      setAnswers({});
      setCurrentQIndex(0);
      setDiagnosticResult(null);
    }
  }, [isOpen, child]);

  // Fetch diagnostic questions when entering Step 3
  useEffect(() => {
    if (isOpen && currentStep === 3 && questions.length === 0) {
      fetchQuestions();
    }
  }, [isOpen, currentStep]);

  const fetchQuestions = async () => {
    setIsLoadingQuestions(true);
    setErrorMsg('');
    try {
      const res = await api.getDiagnosticQuestions(grade, stream);
      setQuestions(res.questions);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load diagnostic questions.');
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  if (!isOpen || !child) return null;

  // Save Step 1 & Step 2 Profile updates to backend
  const handleSaveProfileSteps = async () => {
    if (!name.trim()) {
      setErrorMsg('Please enter student full name.');
      return false;
    }
    if (accessPin.length !== 4) {
      setErrorMsg('Student PIN must be exactly 4 digits.');
      return false;
    }

    setIsSavingProfile(true);
    setErrorMsg('');
    try {
      await api.updateOnboardingProfile({
        child_id: child.id,
        name,
        avatar_id: avatarId,
        gender,
        age,
        school_name: schoolName,
        default_grade: grade,
        selected_term: selectedTerm,
        curriculum_stream: stream,
        access_pin: accessPin
      });
      return true;
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save student profile.');
      return false;
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleNextFromStep1 = () => {
    if (!name.trim()) {
      setErrorMsg('يرجى كتابة اسم الطالب الكامل (Please enter student name)');
      return;
    }
    setErrorMsg('');
    setCurrentStep(2);
  };

  const handleNextFromStep2 = async () => {
    const success = await handleSaveProfileSteps();
    if (success) {
      setCurrentStep(3);
    }
  };

  const handleSelectOption = (questionId: string, optionId: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmitDiagnostic = async () => {
    if (Object.keys(answers).length < questions.length) {
      setErrorMsg('يرجى الإجابة عن جميع الأسئلة لمعايرة المستوى بدقة (Please answer all questions)');
      return;
    }

    setIsSubmittingDiagnostic(true);
    setErrorMsg('');
    try {
      const result = await api.submitDiagnostic(child.id, answers);
      setDiagnosticResult(result);
      setCurrentStep(4);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to grade diagnostic assessment.');
    } finally {
      setIsSubmittingDiagnostic(false);
    }
  };

  const handleFinishOnboarding = () => {
    if (diagnosticResult) {
      const updatedChild: ChildProfile = {
        ...child,
        name,
        avatar_id: avatarId,
        gender,
        age,
        school_name: schoolName,
        default_grade: grade,
        selected_term: selectedTerm,
        curriculum_stream: stream,
        access_pin: accessPin,
        diagnostic_completed: true,
        diagnostic_level: diagnosticResult.calibrated_level,
        diagnostic_score: diagnosticResult.score,
        learning_plan: JSON.stringify(diagnosticResult.learning_plan)
      };
      onComplete(updatedChild, diagnosticResult.learning_plan);
    }
    onClose();
  };

  const currentQ = questions[currentQIndex];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white border-2 border-slate-900 shadow-2xl w-full max-w-4xl my-8 overflow-hidden rounded-none flex flex-col max-h-[92vh]">
        {/* Header Bar */}
        <div className="bg-emerald-900 text-white px-6 py-4 border-b-2 border-slate-900 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-500 text-slate-900 flex items-center justify-center font-bold text-xl border-2 border-slate-900">
              <Compass className="w-6 h-6 text-slate-900" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black uppercase tracking-tight">FAHIM AI ONBOARDING</h2>
                <span className="font-arabic text-amber-300 font-bold text-lg">· رحلة التهيئة والتسجيل الذكية</span>
              </div>
              <p className="text-xs text-emerald-200">
                UAE Curriculum Calibration & 4-Week Personalized Mastery Roadmap
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 hover:bg-emerald-800 transition-colors border border-transparent hover:border-emerald-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* 4-Step Progress Ribbon */}
        <div className="bg-slate-100 border-b border-slate-300 px-6 py-3">
          <div className="grid grid-cols-4 gap-2 text-center text-xs font-bold">
            <div
              className={`py-2 px-2 border-b-4 transition-colors ${
                currentStep === 1
                  ? 'border-emerald-800 text-emerald-900 bg-white shadow-sm'
                  : currentStep > 1
                  ? 'border-emerald-600 text-emerald-700'
                  : 'border-slate-300 text-slate-400'
              }`}
            >
              <span className="block text-[10px] uppercase tracking-wider text-slate-500">Step 1</span>
              <span>1. بيانات الطالب (Profile)</span>
            </div>
            <div
              className={`py-2 px-2 border-b-4 transition-colors ${
                currentStep === 2
                  ? 'border-emerald-800 text-emerald-900 bg-white shadow-sm'
                  : currentStep > 2
                  ? 'border-emerald-600 text-emerald-700'
                  : 'border-slate-300 text-slate-400'
              }`}
            >
              <span className="block text-[10px] uppercase tracking-wider text-slate-500">Step 2</span>
              <span>2. المنهاج والفصل (Curriculum)</span>
            </div>
            <div
              className={`py-2 px-2 border-b-4 transition-colors ${
                currentStep === 3
                  ? 'border-emerald-800 text-emerald-900 bg-white shadow-sm'
                  : currentStep > 3
                  ? 'border-emerald-600 text-emerald-700'
                  : 'border-slate-300 text-slate-400'
              }`}
            >
              <span className="block text-[10px] uppercase tracking-wider text-slate-500">Step 3</span>
              <span>3. تقييم المستوى (Diagnostic)</span>
            </div>
            <div
              className={`py-2 px-2 border-b-4 transition-colors ${
                currentStep === 4
                  ? 'border-emerald-800 text-emerald-900 bg-white shadow-sm'
                  : 'border-slate-300 text-slate-400'
              }`}
            >
              <span className="block text-[10px] uppercase tracking-wider text-slate-500">Step 4</span>
              <span>4. الخطة المخصصة (Learning Plan)</span>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {errorMsg && (
          <div className="bg-rose-50 border-b border-rose-300 p-3 text-rose-800 text-xs font-semibold flex items-center justify-between px-6">
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg('')} className="text-rose-600 hover:text-rose-900 font-bold">✕</button>
          </div>
        )}

        {/* Wizard Body (Scrollable) */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#fbfbfa]">
          {/* ================= STEP 1: Student Profile & Demographics ================= */}
          {currentStep === 1 && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="border-l-4 border-emerald-800 pl-4 py-1">
                <h3 className="text-lg font-black text-slate-900">الخطوة الأولى: الملف التعريفي والرمز التراثي</h3>
                <p className="text-xs text-slate-600">
                  Step 1: Student Profile, Heritage Avatar & Grade Level Demographics.
                </p>
              </div>

              {/* Student Name */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  اسم الطالب الكامل (Student Full Name) <span className="text-rose-600">*</span>
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="e.g. Zayed Al-Nuaimi / زايد النعيمي"
                    className="w-full pl-9 pr-4 py-2.5 bg-white border-2 border-slate-300 text-slate-900 font-medium focus:border-emerald-800 focus:outline-none rounded-none text-sm"
                  />
                </div>
              </div>

              {/* Heritage Avatar Selection */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  اختر الرمز التراثي الإماراتي (Select Student Heritage Avatar)
                </label>
                <div className="grid grid-cols-5 gap-2.5">
                  {UAE_AVATARS.map(av => (
                    <button
                      key={av.id}
                      type="button"
                      onClick={() => setAvatarId(av.id)}
                      className={`p-3 border-2 flex flex-col items-center justify-center text-center transition-all ${
                        avatarId === av.id
                          ? 'border-emerald-800 bg-emerald-50 text-emerald-950 shadow-md ring-1 ring-emerald-800'
                          : 'border-slate-300 bg-white text-slate-700 hover:border-slate-400'
                      }`}
                    >
                      <span className="text-3xl mb-1">{av.icon}</span>
                      <span className="text-xs font-bold font-arabic">{av.nameAr}</span>
                      <span className="text-[10px] text-slate-500 font-medium">{av.nameEn}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Age, Gender & Grade */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Age */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    العمر (Age)
                  </label>
                  <input
                    type="number"
                    min={5}
                    max={18}
                    value={age}
                    onChange={e => setAge(parseInt(e.target.value) || 10)}
                    className="w-full px-3 py-2 bg-white border-2 border-slate-300 text-slate-900 font-semibold focus:border-emerald-800 focus:outline-none rounded-none text-sm"
                  />
                </div>

                {/* Gender */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    الجنس (Gender)
                  </label>
                  <select
                    value={gender}
                    onChange={e => setGender(e.target.value)}
                    className="w-full px-3 py-2 bg-white border-2 border-slate-300 text-slate-900 font-semibold focus:border-emerald-800 focus:outline-none rounded-none text-sm"
                  >
                    <option value="Boy">Boy (ولد)</option>
                    <option value="Girl">Girl (بنت)</option>
                  </select>
                </div>

                {/* Grade */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    الصف الدراسي (Grade)
                  </label>
                  <select
                    value={grade}
                    onChange={e => setGrade(parseInt(e.target.value) || 5)}
                    className="w-full px-3 py-2 bg-white border-2 border-slate-300 text-slate-900 font-semibold focus:border-emerald-800 focus:outline-none rounded-none text-sm"
                  >
                    {[...Array(12)].map((_, i) => (
                      <option key={i + 1} value={i + 1}>
                        Class {i + 1} (الصف {i + 1}) {i + 1 === 5 ? '⭐ Aligned' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* School Name */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  اسم المدرسة في الإمارات (School Name)
                </label>
                <div className="relative">
                  <School className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    value={schoolName}
                    onChange={e => setSchoolName(e.target.value)}
                    placeholder="e.g. Sunrise International School, Abu Dhabi"
                    className="w-full pl-9 pr-4 py-2.5 bg-white border-2 border-slate-300 text-slate-900 font-medium focus:border-emerald-800 focus:outline-none rounded-none text-sm"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Supported: Abu Dhabi (ADEK), Dubai (KHDA), Sharjah (SPEA) and Northern Emirates schools.
                </p>
              </div>

              {/* Next Button */}
              <div className="pt-4 flex justify-end">
                <button
                  type="button"
                  onClick={handleNextFromStep1}
                  className="btn-primary flex items-center gap-2 px-6 py-2.5 text-sm uppercase tracking-wider font-bold"
                >
                  <span>التالي: اختيار المنهاج والفصل (Next: Stream & Term)</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* ================= STEP 2: Curriculum & Stream Selection ================= */}
          {currentStep === 2 && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="border-l-4 border-emerald-800 pl-4 py-1">
                <h3 className="text-lg font-black text-slate-900">الخطوة الثانية: المسار التعليمي والفصل الدراسي</h3>
                <p className="text-xs text-slate-600">
                  Step 2: Ministry Curriculum Alignment, Term Selection & Student Access PIN.
                </p>
              </div>

              {/* Curriculum Stream Selection */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  اختر المسار التعليمي المعتمد (Curriculum & Stream Alignment)
                </label>
                <div className="space-y-2">
                  {CURRICULUM_STREAMS_LIST.map(st => (
                    <label
                      key={st.id}
                      onClick={() => setStream(st.id)}
                      className={`block p-3.5 border-2 cursor-pointer transition-all ${
                        stream === st.id
                          ? 'border-emerald-800 bg-emerald-50/70 shadow-sm'
                          : 'border-slate-300 bg-white hover:border-slate-400'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <input
                          type="radio"
                          name="curriculum_stream"
                          checked={stream === st.id}
                          onChange={() => setStream(st.id)}
                          className="mt-1 text-emerald-800 focus:ring-0"
                        />
                        <div className="flex-1">
                          <div className="font-bold text-sm text-slate-900 font-arabic">{st.titleAr}</div>
                          <div className="text-xs font-semibold text-emerald-900">{st.titleEn}</div>
                          <div className="text-[11px] text-slate-600 mt-0.5">{st.descAr}</div>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Term / Semester Selection */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  اختر الفصل الدراسي للبدء (Select Academic Term)
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setSelectedTerm(1)}
                    className={`p-3.5 border-2 text-left transition-all ${
                      selectedTerm === 1
                        ? 'border-emerald-800 bg-emerald-50 text-emerald-950 shadow-md ring-1 ring-emerald-800'
                        : 'border-slate-300 bg-white text-slate-700 hover:border-slate-400'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-black uppercase tracking-wider bg-emerald-200 text-emerald-900 px-1.5 py-0.5">
                        Free Demo Included
                      </span>
                      {selectedTerm === 1 && <CheckCircle2 className="w-4 h-4 text-emerald-800" />}
                    </div>
                    <div className="font-bold text-sm text-slate-900 font-arabic">الفصل الأول (Term 1)</div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      ألعاب الكرة (Ball Games) - First Chapter 100% Free
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedTerm(2)}
                    className={`p-3.5 border-2 text-left transition-all ${
                      selectedTerm === 2
                        ? 'border-emerald-800 bg-emerald-50 text-emerald-950 shadow-md ring-1 ring-emerald-800'
                        : 'border-slate-300 bg-white text-slate-700 hover:border-slate-400'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-bold text-slate-500">$20 Term Unlock</span>
                      {selectedTerm === 2 && <CheckCircle2 className="w-4 h-4 text-emerald-800" />}
                    </div>
                    <div className="font-bold text-sm text-slate-900 font-arabic">الفصل الثاني (Term 2)</div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      النصوص القرائية والقواعد المتوسطة
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedTerm(3)}
                    className={`p-3.5 border-2 text-left transition-all ${
                      selectedTerm === 3
                        ? 'border-emerald-800 bg-emerald-50 text-emerald-950 shadow-md ring-1 ring-emerald-800'
                        : 'border-slate-300 bg-white text-slate-700 hover:border-slate-400'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-bold text-slate-500">$20 Term Unlock</span>
                      {selectedTerm === 3 && <CheckCircle2 className="w-4 h-4 text-emerald-800" />}
                    </div>
                    <div className="font-bold text-sm text-slate-900 font-arabic">الفصل الثالث (Term 3)</div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      التعبير الكتابي والاستعداد للاختبار الختامي
                    </div>
                  </button>
                </div>
              </div>

              {/* 4-Digit Student Access PIN */}
              <div className="bg-amber-50/70 border border-amber-300 p-4">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-amber-700 mt-0.5" />
                  <div className="flex-1">
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">
                      رمز دخول الطالب المباشر (4-Digit Child Quick PIN)
                    </label>
                    <p className="text-xs text-slate-600 mb-2">
                      Allows your child to log in quickly from school or tablet without needing your parent password.
                    </p>
                    <input
                      type="text"
                      maxLength={4}
                      value={accessPin}
                      onChange={e => setAccessPin(e.target.value.replace(/\D/g, ''))}
                      className="w-32 px-3 py-2 bg-white border-2 border-slate-400 text-center font-mono text-lg font-bold tracking-widest text-slate-900 focus:border-emerald-800 focus:outline-none rounded-none"
                    />
                  </div>
                </div>
              </div>

              {/* Navigation Buttons */}
              <div className="pt-4 flex justify-between items-center">
                <button
                  type="button"
                  onClick={() => setCurrentStep(1)}
                  className="btn-secondary flex items-center gap-1.5 px-4 py-2 text-xs font-bold uppercase tracking-wider"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>السابق (Back)</span>
                </button>

                <button
                  type="button"
                  onClick={handleNextFromStep2}
                  disabled={isSavingProfile}
                  className="btn-primary flex items-center gap-2 px-6 py-2.5 text-sm uppercase tracking-wider font-bold"
                >
                  {isSavingProfile ? (
                    <span>جاري الحفظ والمعايرة...</span>
                  ) : (
                    <>
                      <span>بدء تقييم تحديد المستوى (Start Diagnostic Quiz)</span>
                      <ChevronRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* ================= STEP 3: Baseline Diagnostic Assessment ================= */}
          {currentStep === 3 && (
            <div className="max-w-3xl mx-auto space-y-6">
              <div className="flex justify-between items-start border-l-4 border-emerald-800 pl-4 py-1">
                <div>
                  <h3 className="text-lg font-black text-slate-900 flex items-center gap-2">
                    <span>اختبار تحديد المستوى الذكي</span>
                    <span className="text-xs bg-emerald-100 text-emerald-900 font-bold px-2 py-0.5">
                      Baseline Diagnostic Assessment
                    </span>
                  </h3>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Adaptive 8-question check to calibrate Fahim AI difficulty and prevent frustration.
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">السؤال (Question)</span>
                  <div className="text-lg font-black text-emerald-900">
                    {currentQIndex + 1} / {questions.length || 8}
                  </div>
                </div>
              </div>

              {isLoadingQuestions ? (
                <div className="py-16 text-center space-y-3">
                  <RefreshCw className="w-8 h-8 text-emerald-700 animate-spin mx-auto" />
                  <p className="text-sm font-bold text-slate-700">جاري تحميل أسئلة المعايرة الذكية...</p>
                  <p className="text-xs text-slate-500">Retrieving calibrated grade {grade} questions</p>
                </div>
              ) : currentQ ? (
                <div className="space-y-5 bg-white border-2 border-slate-300 p-6 shadow-sm">
                  {/* Competency Badge */}
                  <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                    <span className="text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-800 px-2 py-1 border border-slate-300">
                      {currentQ.competency_ar} · {currentQ.competency_en}
                    </span>
                    <span className={`text-[11px] font-bold uppercase px-2 py-0.5 ${
                      currentQ.difficulty === 'easy' ? 'bg-emerald-100 text-emerald-800' :
                      currentQ.difficulty === 'hard' ? 'bg-amber-100 text-amber-900' :
                      'bg-sky-100 text-sky-800'
                    }`}>
                      Level: {currentQ.difficulty}
                    </span>
                  </div>

                  {/* Reading Passage (if applicable) */}
                  {currentQ.passage_ar && (
                    <div className="bg-amber-50/50 border-r-4 border-amber-600 p-4">
                      <span className="text-[11px] font-bold text-amber-900 uppercase tracking-wider block mb-1">
                        اقرأ الفقرة التالية ثم أجب: (Read the passage)
                      </span>
                      <p className="font-arabic text-base sm:text-lg leading-relaxed text-slate-900 text-right" dir="rtl">
                        {currentQ.passage_ar}
                      </p>
                    </div>
                  )}

                  {/* Question Stem */}
                  <div className="space-y-1">
                    <h4 className="font-arabic text-lg sm:text-xl font-bold text-slate-900 text-right" dir="rtl">
                      {currentQ.question_ar}
                    </h4>
                    <p className="text-xs text-slate-600">{currentQ.question_en}</p>
                  </div>

                  {/* Multiple Choice Options */}
                  <div className="space-y-2.5 pt-2">
                    {currentQ.options.map((opt) => {
                      const isSelected = answers[currentQ.id] === opt.id;
                      return (
                        <button
                          key={opt.id}
                          type="button"
                          onClick={() => handleSelectOption(currentQ.id, opt.id)}
                          className={`w-full p-3.5 border-2 text-right transition-all flex items-center justify-between ${
                            isSelected
                              ? 'border-emerald-800 bg-emerald-50 text-emerald-950 font-bold ring-1 ring-emerald-800'
                              : 'border-slate-300 bg-white text-slate-800 hover:border-slate-400'
                          }`}
                        >
                          <div className="w-6 h-6 border-2 border-slate-400 flex items-center justify-center font-mono text-xs font-bold mr-3 text-slate-700">
                            {String.fromCharCode(65 + opt.id)}
                          </div>
                          <div className="flex-1 text-right" dir="rtl">
                            <span className="font-arabic text-base block">{opt.text_ar}</span>
                            <span className="text-[11px] text-slate-500 font-normal block" dir="ltr">
                              {opt.text_en}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Pagination / Action Bar */}
                  <div className="pt-4 border-t border-slate-200 flex justify-between items-center">
                    <button
                      type="button"
                      disabled={currentQIndex === 0}
                      onClick={() => setCurrentQIndex(prev => Math.max(0, prev - 1))}
                      className="btn-secondary flex items-center gap-1 px-4 py-2 text-xs font-bold uppercase tracking-wider disabled:opacity-40"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>السابق (Previous)</span>
                    </button>

                    {currentQIndex < questions.length - 1 ? (
                      <button
                        type="button"
                        onClick={() => setCurrentQIndex(prev => prev + 1)}
                        className="btn-primary flex items-center gap-1 px-5 py-2 text-xs font-bold uppercase tracking-wider"
                      >
                        <span>التالي (Next)</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    ) : (
                      <button
                        type="button"
                        disabled={isSubmittingDiagnostic}
                        onClick={handleSubmitDiagnostic}
                        className="btn-accent flex items-center gap-2 px-6 py-2.5 text-xs font-black uppercase tracking-wider"
                      >
                        {isSubmittingDiagnostic ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span>جاري المعايرة الذكية...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4" />
                            <span>إنهاء التقييم وتوليد الخطة (Submit & Calibrate)</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          )}

          {/* ================= STEP 4: Personalized Learning Plan Generation ================= */}
          {currentStep === 4 && diagnosticResult && (
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Calibrated Level Banner */}
              <div className="bg-emerald-950 text-white p-6 border-2 border-slate-900 shadow-lg relative overflow-hidden">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative z-10">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Award className="w-5 h-5 text-amber-400" />
                      <span className="text-xs uppercase tracking-widest text-amber-400 font-bold">
                        AI Difficulty Calibrated · المسار المعتمد
                      </span>
                    </div>
                    <h3 className="text-2xl font-black font-arabic text-white">
                      {diagnosticResult.learning_plan.level_title_ar}
                    </h3>
                    <p className="text-xs text-emerald-200 font-semibold">
                      {diagnosticResult.learning_plan.level_title_en}
                    </p>
                  </div>

                  <div className="bg-emerald-900/90 border-2 border-amber-400 px-5 py-3 text-center">
                    <span className="text-[10px] text-amber-300 font-bold uppercase tracking-wider block">
                      Diagnostic Score
                    </span>
                    <span className="text-3xl font-black text-amber-400 font-mono">
                      {diagnosticResult.score}%
                    </span>
                    <span className="text-[10px] text-emerald-200 block">
                      {diagnosticResult.correct_count} / {diagnosticResult.total_questions} Correct
                    </span>
                  </div>
                </div>

                <p className="mt-4 text-xs text-slate-200 font-arabic leading-relaxed border-t border-emerald-800/80 pt-3" dir="rtl">
                  {diagnosticResult.learning_plan.level_summary_ar}
                </p>
              </div>

              {/* Competency Breakdown & Skills Radar */}
              <div className="bg-white border-2 border-slate-300 p-5 space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-200 pb-2.5">
                  <BarChart2 className="w-4 h-4 text-emerald-800" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                    تحليل الكفاءات والمهارات (Competency Skill Breakdown)
                  </h4>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {Object.entries(diagnosticResult.learning_plan.competency_breakdown).map(([key, stat]) => (
                    <div key={key} className="bg-slate-50 border border-slate-200 p-3.5 space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-slate-900 font-arabic">{stat.name_ar}</span>
                        <span className="font-mono font-bold text-emerald-900">{stat.percentage}%</span>
                      </div>
                      <div className="w-full bg-slate-200 h-2">
                        <div
                          className={`h-2 transition-all duration-500 ${
                            stat.percentage >= 75 ? 'bg-emerald-700' :
                            stat.percentage >= 50 ? 'bg-amber-600' : 'bg-rose-600'
                          }`}
                          style={{ width: `${stat.percentage}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-slate-500 flex justify-between">
                        <span>{stat.name_en}</span>
                        <span>{stat.correct} / {stat.total}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Strengths & Growth Areas */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="bg-emerald-50 border border-emerald-200 p-3">
                    <span className="text-[11px] font-bold text-emerald-900 uppercase tracking-wider block mb-1.5">
                      ✓ نقاط القوة المعززة (Target Strengths)
                    </span>
                    <ul className="text-xs text-emerald-950 space-y-1 list-disc list-inside">
                      {diagnosticResult.learning_plan.strengths.map((str, idx) => (
                        <li key={idx}>{str}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-amber-50 border border-amber-200 p-3">
                    <span className="text-[11px] font-bold text-amber-900 uppercase tracking-wider block mb-1.5">
                      ⚡ مجالات التمكين والتأسيس (Growth Priorities)
                    </span>
                    <ul className="text-xs text-amber-950 space-y-1 list-disc list-inside">
                      {diagnosticResult.learning_plan.growth_areas.map((ga, idx) => (
                        <li key={idx}>{ga}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* 4-Week Milestone Roadmap */}
              <div className="bg-white border-2 border-slate-300 p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-emerald-800" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      جدول الإنجاز الأسبوعي المخصص (4-Week Milestone Schedule)
                    </h4>
                  </div>
                  <span className="text-[11px] bg-slate-100 text-slate-700 font-bold px-2 py-0.5">
                    Class {grade} · Term {selectedTerm}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {diagnosticResult.learning_plan.milestones.map((m) => (
                    <div key={m.week} className="border-2 border-slate-200 p-3.5 bg-slate-50/50 hover:border-emerald-700 transition-colors">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="text-[10px] font-black uppercase tracking-wider bg-emerald-800 text-white px-1.5 py-0.5">
                          Week {m.week}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono font-semibold">
                          ~{m.estimated_hours} Hours/wk
                        </span>
                      </div>
                      <h5 className="font-bold text-xs text-slate-900 font-arabic">{m.title_ar}</h5>
                      <p className="text-[11px] text-slate-600 mt-0.5">{m.focus_en}</p>
                      <div className="mt-2 pt-2 border-t border-slate-200 flex flex-wrap gap-1">
                        {m.target_activities.map((act, i) => (
                          <span key={i} className="text-[10px] bg-white border border-slate-300 text-slate-700 px-1.5 py-0.5">
                            {act}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Complete & Launch CTA */}
              <div className="pt-2 flex justify-between items-center">
                <div className="text-xs text-slate-600">
                  <span>Starting Chapter: </span>
                  <strong className="text-emerald-900">{diagnosticResult.learning_plan.recommended_first_chapter}</strong>
                </div>

                <button
                  type="button"
                  onClick={handleFinishOnboarding}
                  className="btn-primary flex items-center gap-2 px-8 py-3 text-sm uppercase tracking-wider font-black shadow-lg"
                >
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>ابدأ التعلم الآن (Start Learning with Fahim AI)</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
