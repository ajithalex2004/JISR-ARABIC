import React, { useState, useEffect } from 'react';
import {
  BookOpen, Lock, Unlock, Play, CheckCircle2, Clock, Sparkles,
  ChevronRight, FlaskConical, BookText, Mic, Volume2, ArrowRight,
  Award, FileText, CheckCircle, GraduationCap, Calendar
} from 'lucide-react';
import { LessonSummary, TermSummary, ChildProfile, User } from '../../types';
import { api } from '../../services/api';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';

interface CatalogueViewProps {
  user?: User | null;
  activeChild: ChildProfile | null;
  onSelectLesson: (lessonId: string) => void;
  onOpenPaywall: (grade: number, term: number, chapterName?: string) => void;
  onOpenOnboarding?: () => void;
  onSelectView?: (view: string) => void;
  onOpenAskFahim?: () => void;
}

export const CatalogueView: React.FC<CatalogueViewProps> = ({
  user,
  activeChild,
  onSelectLesson,
  onOpenPaywall,
  onOpenOnboarding,
  onSelectView,
  onOpenAskFahim
}) => {
  const availableGrades = React.useMemo(() => {
    if (user?.role === 'admin') {
      return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
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
    return [5];
  }, [user, activeChild]);

  const [selectedGrade, setSelectedGrade] = useState<number>(() => {
    return activeChild?.default_grade || 5;
  });
  const [selectedTerm, setSelectedTerm] = useState<number>(1);
  const [terms, setTerms] = useState<TermSummary[]>([]);
  const [lessons, setLessons] = useState<LessonSummary[]>([]);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    if (availableGrades.length > 0 && !availableGrades.includes(selectedGrade)) {
      setSelectedGrade(availableGrades[0]);
    }
  }, [availableGrades, selectedGrade]);

  useEffect(() => {
    if (activeChild?.default_grade && availableGrades.includes(activeChild.default_grade)) {
      setSelectedGrade(activeChild.default_grade);
    }
  }, [activeChild, availableGrades]);

  const loadData = async () => {
    setLoadError('');
    try {
      const tList = await api.getTerms(selectedGrade, activeChild?.id);
      setTerms(tList || []);
      const lList = await api.getLessons(selectedGrade, selectedTerm, activeChild?.id);
      setLessons(lList || []);
    } catch (err) {
      setTerms([]);
      setLessons([]);
      setLoadError('Curriculum data is unavailable. Please try again when the curriculum service is online.');
      console.warn('Curriculum API unavailable; stale fallback data was not displayed.', err);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedGrade, selectedTerm, activeChild]);

  const currentTermInfo = terms.find((t) => t.term === selectedTerm);
  const isTermUnlocked = currentTermInfo?.is_unlocked ?? true;

  // Group lessons dynamically by Unit
  const unitsMap = lessons.reduce((acc, lesson) => {
    const key = lesson.unit_id || `unit_${Math.ceil(lesson.lesson_order / 5)}`;
    if (!acc[key]) {
      acc[key] = {
        id: key,
        title_ar: lesson.unit_title_ar || (lesson.lesson_order <= 5 ? 'الوحدة الأولى' : 'الوحدة الثانية'),
        title_en: lesson.unit_title_en || (lesson.lesson_order <= 5 ? 'Unit 1' : 'Unit 2'),
        lessons: [] as typeof lessons
      };
    }
    acc[key].lessons.push(lesson);
    return acc;
  }, {} as Record<string, { id: string; title_ar: string; title_en: string; lessons: typeof lessons }>);

  const unitsList = Object.values(unitsMap);
  const firstLesson = lessons[0];
  const isBallGames = firstLesson?.title_ar === 'أَلْعَابُ الكُرَةِ';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-8 pb-28">
      {loadError && <div role="alert" className="p-4 border border-amber-400 bg-amber-50 text-amber-900 text-sm font-semibold">{loadError}</div>}

      {/* Grade Selector Card */}
      <div className="bg-white rounded-3xl p-4 sm:p-5 border border-purple-100 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-purple-100 text-[#58337e] flex items-center justify-center font-bold">
              <GraduationCap className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-black text-slate-800">
                {availableGrades.length === 1 ? 'المرحلة الدراسية المعتمدة (Enrolled Grade Level)' : 'المرحلة الدراسية (Select Grade Level)'}
              </h2>
              <p className="text-[11px] text-slate-500 font-medium">
                {availableGrades.length === 1
                  ? `Official UAE Ministry of Education (MoE) Arabic Curriculum · Grade ${availableGrades[0]} Enrolled Track`
                  : user?.role === 'admin'
                  ? 'Official UAE Ministry of Education (MoE) Arabic Curriculum · Grades 1 to 10'
                  : `Official UAE Ministry of Education (MoE) Arabic Curriculum · Enrolled Grades (${availableGrades.map((g) => `Class ${g}`).join(', ')})`}
              </p>
            </div>
          </div>
          <span className="text-xs font-bold text-[#58337e] bg-purple-50 px-3 py-1 rounded-full border border-purple-200 self-start sm:self-auto">
            الصف {selectedGrade} (Grade {selectedGrade})
          </span>
        </div>

        {/* Grade Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
          {availableGrades.map((g) => {
            const isSelected = selectedGrade === g;
            return (
              <button
                key={g}
                onClick={() => {
                  setSelectedGrade(g);
                }}
                className={`px-4 py-2 rounded-2xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 shrink-0 ${
                  isSelected
                    ? 'bg-gradient-to-r from-[#58337e] to-[#6c5ce7] text-white shadow-md shadow-purple-500/20 scale-[1.03]'
                    : 'bg-slate-100 hover:bg-purple-50 text-slate-700 hover:text-[#58337e]'
                }`}
              >
                <span>الصف {g}</span>
                <span className={`text-[10px] font-normal ${isSelected ? 'text-purple-200' : 'text-slate-400'}`}>G{g}</span>
                {availableGrades.length === 1 && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-normal ${isSelected ? 'bg-white/20 text-white' : 'bg-purple-100 text-[#58337e]'}`}>
                    المسار المسجل
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Term Selector Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-2.5 rounded-2xl border border-slate-200 shadow-2xs">
        <div className="flex items-center gap-2 p-1 bg-slate-100/90 rounded-xl w-full sm:w-auto">
          {[
            { term: 1, labelAr: 'الفصل الأول', labelEn: 'Term 1' },
            { term: 2, labelAr: 'الفصل الثاني', labelEn: 'Term 2' },
            { term: 3, labelAr: 'الفصل الثالث', labelEn: 'Term 3' }
          ].map((t) => {
            const isSelected = selectedTerm === t.term;
            const termData = terms.find((item) => item.term === t.term);
            const isLocked = termData && !termData.is_unlocked;
            return (
              <button
                key={t.term}
                onClick={() => setSelectedTerm(t.term)}
                className={`flex-1 sm:flex-initial px-5 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                  isSelected
                    ? 'bg-white text-[#58337e] shadow-xs font-black'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Calendar className="w-3.5 h-3.5 opacity-70" />
                <span>{t.labelAr}</span>
                <span className="text-[10px] opacity-75 font-normal">({t.labelEn})</span>
                {isLocked && <Lock className="w-3 h-3 text-amber-500 ml-0.5" />}
              </button>
            );
          })}
        </div>

        <div className="text-xs text-slate-500 font-medium px-2 flex items-center gap-2">
          <span>{lessons.length} فصول معتمدة في هذا الفصل</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="text-emerald-700 font-bold">{isTermUnlocked ? 'متاح بالكامل' : 'يحتاج اشتراك'}</span>
        </div>
      </div>

      {/* 1. Header Banner: Strictly Arabic Curriculum Only */}
      <div className="bg-gradient-to-r from-[#58337e] via-[#6c5ce7] to-[#4a154b] rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        {/* Subtle decorative circles */}
        <div className="absolute -top-16 -right-16 w-56 h-56 bg-white/10 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute -bottom-20 -left-12 w-48 h-48 bg-emerald-500/15 rounded-full blur-xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="bg-[#22c55e] text-white font-bold px-3 py-1 rounded-full text-xs uppercase tracking-wider shadow-sm">
                UAE MoE Curriculum
              </span>
              <span className="bg-white/20 text-purple-100 font-semibold px-3 py-1 rounded-full text-xs backdrop-blur-xs">
                Grade {selectedGrade} · Term {selectedTerm}
              </span>
              <span className="bg-purple-900/40 text-purple-200 font-medium px-3 py-1 rounded-full text-xs">
                {lessons.length || 0} Chapters
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-black font-arabic tracking-tight text-white pt-1">
              <ArabicWordSpans
                text="مِنْهَاجُ اللُّغَةِ العَرَبِيَّةِ (العَرَبِيَّةُ تَجْمَعُنَا)"
                tooltipPlacement="bottom"
                className="text-white"
              />
            </h1>

            <p className="text-purple-100 text-sm max-w-2xl font-medium leading-relaxed">
              Modern Standard Arabic for Non-Native & Native Learners. Interactive textbook, word-level audio translations, smart study booklets, and adaptive quizzes.
            </p>
          </div>

          {/* Progress / Diagnostic Badge */}
          <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md px-5 py-4 rounded-2xl border border-white/15 shrink-0 self-start md:self-auto">
            <div className="relative w-14 h-14 flex items-center justify-center">
              <svg className="w-14 h-14 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-white/20"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-[#22c55e]"
                  strokeDasharray={`${activeChild?.diagnostic_score || 85}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <span className="absolute text-xs font-black text-white">
                {activeChild?.diagnostic_score ? `${activeChild.diagnostic_score}%` : '85%'}
              </span>
            </div>
            <div>
              <div className="text-xs text-purple-200 font-semibold uppercase tracking-wider">Curriculum Mastery</div>
              <div className="text-sm font-bold text-white">
                {activeChild?.diagnostic_level ? activeChild.diagnostic_level.toUpperCase() : 'INTERMEDIATE'}
              </div>
              <div className="text-[11px] text-emerald-300 font-medium">Chapter 1 Active</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. FEATURED SHOWCASE: COMPLETE CHAPTER 1 */}
      {firstLesson && (
        <div className="bg-white rounded-3xl border-2 border-purple-200/80 p-6 sm:p-8 shadow-lg shadow-purple-500/5 space-y-6 relative overflow-hidden">
          {/* Accent Top Border */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#6c5ce7] via-[#22c55e] to-[#58337e]" />

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="bg-emerald-100 text-emerald-800 font-bold px-3 py-1 rounded-full text-xs flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                  <span>الفصل الأول · نشط الآن (Active Chapter)</span>
                </span>
                <span className="bg-purple-100 text-[#6c5ce7] font-semibold px-3 py-1 rounded-full text-xs">
                  {firstLesson.unit_title_ar || 'الوحدة الأولى'}: {firstLesson.unit_title_en || 'Unit 1'} · ص {firstLesson.start_page}
                </span>
                {firstLesson.is_first_chapter_demo && (
                  <span className="bg-amber-100 text-amber-800 font-bold px-2.5 py-1 rounded-full text-xs">
                    تجربة كاملة مجانية (Free Full Access)
                  </span>
                )}
              </div>

              <div className="pt-2">
                <h2 className="text-2xl sm:text-3xl font-black text-slate-900 flex items-baseline gap-3 flex-wrap">
                  <span className="text-[#58337e] font-arabic text-3xl sm:text-4xl">
                    <ArabicWordSpans text={firstLesson.title_ar} tooltipPlacement="top" className="text-[#58337e] font-black" />
                  </span>
                  <span className="text-slate-500 text-lg font-bold font-sans">Chapter 1: {firstLesson.title_en}</span>
                </h2>
                <p className="text-xs sm:text-sm text-slate-600 font-medium mt-1">
                  الصف {selectedGrade} · الفصل الدراسي {selectedTerm} · {firstLesson.unit_title_ar || 'الوحدة الأولى'}
                </p>
              </div>
            </div>

            {/* Quick Stats Pill */}
            <div className="grid grid-cols-3 gap-2 sm:gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100 text-center shrink-0">
              <div className="px-2">
                <div className="text-lg font-black text-[#58337e]">8</div>
                <div className="text-[10px] font-bold text-slate-500 uppercase">مفردات (Vocab)</div>
              </div>
              <div className="px-2 border-x border-slate-200">
                <div className="text-lg font-black text-[#6c5ce7]">2</div>
                <div className="text-[10px] font-bold text-slate-500 uppercase">قواعد (Grammar)</div>
              </div>
              <div className="px-2">
                <div className="text-lg font-black text-[#22c55e]">10</div>
                <div className="text-[10px] font-bold text-slate-500 uppercase">أسئلة (Quiz)</div>
              </div>
            </div>
          </div>

          {/* Reading Passage Preview with Instant Tooltip Translation */}
          <div className="bg-[#fcfaff] rounded-2xl p-4 sm:p-5 border border-purple-100/80 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#6c5ce7]" />
                <span className="text-xs font-bold text-[#58337e] uppercase tracking-wider">
                  معاينة النص القرائي (Interactive Passage Preview)
                </span>
              </div>
              <span className="text-[11px] text-[#6c5ce7] font-semibold flex items-center gap-1">
                <Volume2 className="w-3.5 h-3.5" />
                <span>Point to any word to see translation & listen</span>
              </span>
            </div>

            <div className="p-4 bg-white rounded-xl border border-purple-100 text-right leading-loose font-arabic text-lg sm:text-xl text-slate-800 shadow-2xs">
              <ArabicWordSpans
                text={
                  isBallGames
                    ? "كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الأَكْثَرُ شَعْبِيَّةً فِي العَالَمِ. يُحِبُّهَا الكِبَارُ وَالصِّغَارُ، حَيْثُ يَتَنَافَسُ فِي المَلْعَبِ فَرِيقَانِ كَبِيرَانِ لِتَسْجِيلِ الهَدَفِ فِي شِبَاكِ حَارِسِ المَرْمَى."
                    : `نَصُّ الدَّرْسِ الأَوَّلِ: ${firstLesson.title_ar}. يَتَعَلَّمُ الطَّالِبُ فِي هَذَا الفَصْلِ المَفَاهِيمَ اللُّغَوِيَّةَ وَالمُفْرَدَاتِ الأَسَاسِيَّةَ وَفْقَ مِنْهَاجِ وِزَارَةِ التَّرْبِيَةِ وَالتَّعْلِيمِ فِي دَوْلَةِ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ.`
                }
                tooltipPlacement="top"
                className="font-arabic text-lg sm:text-xl text-slate-800"
              />
            </div>
            <p className="text-xs text-slate-500 italic text-left">
              {isBallGames
                ? '"Football is the most popular game in the world. Both young and old love it, where two large teams compete on the pitch to score goals into the goalkeeper\'s net."'
                : `"Interactive reading passage for Grade ${selectedGrade} (Term ${selectedTerm}): ${firstLesson.title_en}. Students explore authentic vocabulary, language structures, and reading comprehension aligned with UAE MoE standards."`}
            </p>
          </div>

          {/* 4 Interactive Curriculum Pillars for Chapter 1 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {/* Pillar 1: Full Interactive Reading */}
            <div
              onClick={() => onSelectLesson(firstLesson.id)}
              className="p-4 rounded-2xl border border-blue-100 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-300 transition-all cursor-pointer group shadow-2xs"
            >
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <BookOpen className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                1. قراءة الدرس والنص (Interactive Reading)
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                Full interactive reading text with word-level tooltips and native audio.
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs font-bold text-blue-600">
                <span>ابدأ القراءة (Start Reading)</span>
                <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
              </div>
            </div>

            {/* Pillar 2: Smart Study Booklet */}
            <div
              onClick={() => onSelectView && onSelectView('malazim')}
              className="p-4 rounded-2xl border border-emerald-100 bg-emerald-50/50 hover:bg-emerald-50 hover:border-emerald-300 transition-all cursor-pointer group shadow-2xs"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <BookText className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
                2. الملزمة الذكية للدرس (Smart Study Notes)
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                15-minute quick study notes covering vocabulary and grammar rules.
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs font-bold text-emerald-600">
                <span>عرض الملزمة (View Notes)</span>
                <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
              </div>
            </div>

            {/* Pillar 3: Fast 3-Minute Capsule */}
            <div
              onClick={() => onSelectView && onSelectView('capsules')}
              className="p-4 rounded-2xl border border-purple-100 bg-purple-50/50 hover:bg-purple-50 hover:border-purple-300 transition-all cursor-pointer group shadow-2xs"
            >
              <div className="w-10 h-10 rounded-xl bg-purple-100 text-[#6c5ce7] flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <Clock className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-[#6c5ce7] transition-colors">
                3. الكبسولة السريعة (3-Min Capsule)
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                3–5 minute bite-sized audio capsule for busy parents and quick review.
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs font-bold text-[#6c5ce7]">
                <span>فتح الكبسولة (Open Capsule)</span>
                <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
              </div>
            </div>

            {/* Pillar 4: MoE Model Exam */}
            <div
              onClick={() => onSelectView && onSelectView('tests')}
              className="p-4 rounded-2xl border border-amber-100 bg-amber-50/50 hover:bg-amber-50 hover:border-amber-300 transition-all cursor-pointer group shadow-2xs"
            >
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <FlaskConical className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-slate-900 group-hover:text-amber-700 transition-colors">
                4. اختبار محاكاة الوزارة (Ministry Mock Exam)
              </h4>
              <p className="text-xs text-slate-500 mt-1">
                10-question adaptive quiz aligned with UAE MoE exam standards.
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs font-bold text-amber-600">
                <span>بدء الاختبار (Start Exam)</span>
                <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
              </div>
            </div>
          </div>

          {/* Big Action Bar for Chapter 1 */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
            <button
              onClick={() => onSelectLesson(firstLesson.id)}
              className="w-full sm:w-auto flex-1 btn-faheem-primary py-3.5 px-6 text-sm font-bold rounded-2xl flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>قراءة الدرس الأول كاملاً (Open Chapter 1: {firstLesson.title_en})</span>
            </button>
            <button
              onClick={() => onSelectView && onSelectView('malazim')}
              className="w-full sm:w-auto btn-faheem-secondary py-3.5 px-6 text-sm font-bold rounded-2xl flex items-center justify-center gap-2 hover:bg-slate-50 transition-all"
            >
              <BookText className="w-4 h-4 text-emerald-600" />
              <span>ملزمة الفصل الأول الذكية (Chapter 1 Smart Study Booklet)</span>
            </button>
          </div>
        </div>
      )}

      {/* 3. FULL SYLLABUS: ALL 10 TERM 1 LESSONS */}
      <div className="space-y-6 pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-xl font-black text-slate-900">
              فهرس فصول المنهاج (Grade {selectedGrade} · {currentTermInfo?.title_en || `Term ${selectedTerm}`} Chapters)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {lessons.length} Complete Curriculum Lessons from the Official UAE Student Textbook: <span className="font-bold text-[#58337e]">العَرَبِيَّةُ تَجْمَعُنَا</span>
            </p>
          </div>
          {!isTermUnlocked && (
            <button
              onClick={() => onOpenPaywall(selectedGrade, selectedTerm, currentTermInfo?.demo_chapter_name)}
              className="text-xs font-bold text-[#6c5ce7] hover:text-[#5b47fb] flex items-center gap-1.5 bg-purple-50 px-3.5 py-2 rounded-xl transition-colors border border-purple-200 self-start sm:self-auto"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Unlock All Chapters (from USD {currentTermInfo?.price_usd ?? 20})</span>
            </button>
          )}
        </div>

        {/* DYNAMIC UNITS */}
        {unitsList.map((unitGroup, uIdx) => (
          <div key={unitGroup.id} className="space-y-3 pt-2">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${uIdx % 2 === 0 ? 'bg-[#6c5ce7]' : 'bg-emerald-500'}`} />
              <h4 className="text-sm font-bold text-slate-800">
                {unitGroup.title_ar} ({unitGroup.title_en}) · {unitGroup.lessons.length} {unitGroup.lessons.length === 1 ? 'درس' : 'دروس'}
              </h4>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {unitGroup.lessons.map((lesson) => {
                const isDemo = lesson.is_first_chapter_demo;
                const canPlay = isDemo || isTermUnlocked;

                return (
                  <div
                    key={lesson.id}
                    className={`faheem-card p-4 flex flex-col justify-between hover:border-purple-400 transition-all group ${
                      isDemo ? 'ring-2 ring-emerald-500/30 bg-emerald-50/10' : ''
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className="text-[11px] font-bold text-slate-500">
                          الدرس {lesson.lesson_order} (L{lesson.lesson_order}) · ص {lesson.start_page} (p.{lesson.start_page})
                        </span>
                        {isDemo ? (
                          <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                            متاح مجاناً (Free Access)
                          </span>
                        ) : canPlay ? (
                          <span className="bg-purple-100 text-[#6c5ce7] text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Unlock className="w-2.5 h-2.5" /> متاح (Available)
                          </span>
                        ) : (
                          <span className="bg-slate-100 text-slate-500 text-[10px] font-medium px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Lock className="w-2.5 h-2.5" /> مغلق (Locked)
                          </span>
                        )}
                      </div>

                      <div className="text-lg font-black font-arabic text-[#58337e] group-hover:text-[#6c5ce7] transition-colors">
                        <ArabicWordSpans
                          text={lesson.title_ar}
                          tooltipPlacement="top"
                          className="text-[#58337e] font-black"
                        />
                      </div>
                      <div className="text-xs font-bold text-slate-600 mt-0.5">
                        {lesson.title_en}
                      </div>
                    </div>

                    <div className="pt-3 mt-3 border-t border-slate-100">
                      {canPlay ? (
                        <button
                          onClick={() => onSelectLesson(lesson.id)}
                          className={`w-full py-2 px-3 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-all ${
                            isDemo
                              ? 'bg-[#22c55e] hover:bg-[#16a34a] text-white shadow-xs'
                              : 'btn-faheem-primary'
                          }`}
                        >
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>{isDemo ? 'قراءة الدرس كاملاً (Read Full Chapter)' : 'فتح الدرس (Open Lesson)'}</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => onOpenPaywall(selectedGrade, selectedTerm, currentTermInfo?.demo_chapter_name)}
                          className="w-full bg-slate-100 hover:bg-purple-50 hover:text-[#6c5ce7] text-slate-600 font-bold py-2 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <Lock className="w-3.5 h-3.5" />
                          <span>فتح الدرس (Unlock Chapter)</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
