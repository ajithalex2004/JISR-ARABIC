import React, { useState, useEffect, useMemo } from 'react';
import { BookOpen, Volume2, FileText, Sparkles, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';
import { User, ChildProfile } from '../../types';

interface TextbookReaderProps {
  user?: User | null;
  activeChild?: ChildProfile | null;
  initialGrade?: number;
  initialTerm?: number;
  initialPage?: number;
  onSelectGrade?: (grade: number) => void;
}

export const TextbookReader: React.FC<TextbookReaderProps> = ({
  user,
  activeChild,
  initialGrade = 5,
  initialTerm = 1,
  initialPage,
  onSelectGrade
}) => {
  const availableGrades = useMemo(() => {
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
    return [initialGrade || 5];
  }, [user, activeChild, initialGrade]);

  const [grade, setGrade] = useState<number>(() => {
    if (initialGrade && (user?.role === 'admin' || !activeChild?.default_grade)) {
      return initialGrade;
    }
    return activeChild?.default_grade || initialGrade || 5;
  });
  const [term, setTerm] = useState<number>(initialTerm);
  const defaultPageForGrade = grade === 6 ? 8 : 7;
  const [currentPage, setCurrentPage] = useState<number>(initialPage || defaultPageForGrade);
  const [totalPages, setTotalPages] = useState<number>(112);

  useEffect(() => {
    if (initialGrade && initialGrade !== grade) {
      setGrade(initialGrade);
      setCurrentPage(initialGrade === 6 ? 8 : 7);
    }
  }, [initialGrade]);

  useEffect(() => {
    if (availableGrades.length > 0 && !availableGrades.includes(grade)) {
      setGrade(availableGrades[0]);
    }
  }, [availableGrades, grade]);

  useEffect(() => {
    if (user?.role !== 'admin' && activeChild?.default_grade && availableGrades.includes(activeChild.default_grade)) {
      setGrade(activeChild.default_grade);
    }
  }, [activeChild, availableGrades, user?.role]);

  const currentEditionId = `moe_gr${grade}_vol${term}_2023`;

  useEffect(() => {
    fetch(`/api/admin/textbook-pages/${currentEditionId}`)
      .then((res) => (res.ok ? res.json() : []))
      .then((pages: any[]) => {
        if (pages && pages.length > 0) {
          setTotalPages(pages.length);
        }
      })
      .catch(() => undefined);
  }, [currentEditionId]);

  const [pageData, setPageData] = useState<any>(null);
  const [coverageReport, setCoverageReport] = useState<any>(null);
  const [showCoverageModal, setShowCoverageModal] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'split' | 'text' | 'image'>('split');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [chapters, setChapters] = useState<Array<{ page: number; title: string }>>([]);
  const [expandedAnswers, setExpandedAnswers] = useState<Record<number, boolean>>({});
  const [loadingAnswers, setLoadingAnswers] = useState<Record<number, boolean>>({});
  const [dynamicAnswers, setDynamicAnswers] = useState<Record<number, any>>({});

  useEffect(() => {
    setExpandedAnswers({});
    setLoadingAnswers({});
    setDynamicAnswers({});
  }, [currentPage, currentEditionId]);

  const toggleAnswer = async (pIdx: number, questionText: string) => {
    if (expandedAnswers[pIdx]) {
      setExpandedAnswers((prev) => ({ ...prev, [pIdx]: false }));
      return;
    }

    const existing =
      pageData?.model_answers?.[pIdx] ||
      pageData?.model_answers?.[String(pIdx)] ||
      dynamicAnswers[pIdx];

    if (existing) {
      setExpandedAnswers((prev) => ({ ...prev, [pIdx]: true }));
      return;
    }

    setLoadingAnswers((prev) => ({ ...prev, [pIdx]: true }));
    try {
      const solution = await api.solveQuestion(
        questionText,
        pageData?.unit || pageData?.lesson_title || '',
        grade
      );
      if (solution) {
        setDynamicAnswers((prev) => ({ ...prev, [pIdx]: solution }));
        setExpandedAnswers((prev) => ({ ...prev, [pIdx]: true }));
      }
    } catch (err) {
      console.error('Failed to solve question:', err);
    } finally {
      setLoadingAnswers((prev) => ({ ...prev, [pIdx]: false }));
    }
  };

  useEffect(() => {
    api
      .getLessons(grade, term)
      .then((lessons: any[]) => {
        setChapters(
          (lessons || []).map((lesson) => ({
            page: Number(lesson.start_page || 1),
            title: `${lesson.title_en || 'Chapter'} (${lesson.title_ar || ''})`
          }))
        );
      })
      .catch(() => setChapters([]));
  }, [grade, term]);

  useEffect(() => {
    if (initialPage) {
      setCurrentPage(initialPage);
    }
  }, [initialPage]);

  useEffect(() => {
    loadPage(currentPage);
    loadCoverage();
  }, [currentPage, currentEditionId]);

  const loadPage = async (page: number) => {
    setIsLoading(true);
    try {
      const data = await api.getOcrPage(page, currentEditionId);
      setPageData(data);
    } catch (e) {
      console.error('Failed to load page:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCoverage = async () => {
    try {
      const report = await api.getCoverageReport();
      setCoverageReport(report);
    } catch (e) {
      console.error(e);
    }
  };

  const GR5_CHAPTER_1_PAGES = [
    { page: 7, pnum: 6, titleAr: 'نواتج التعلم', titleEn: 'Learning Outcomes' },
    { page: 8, pnum: 7, titleAr: 'قاموسي', titleEn: 'My Glossary' },
    { page: 9, pnum: 8, titleAr: 'أستمع: ألعاب الكرة', titleEn: 'Listening: Ball Games' },
    { page: 10, pnum: 9, titleAr: 'بعد الاستماع: أبحث عن الخطأ', titleEn: 'Post-Listening: Error Hunt' },
    { page: 11, pnum: 10, titleAr: 'أتحدث: استبيان ألعاب الكرة', titleEn: 'Speaking: Sports Survey' },
    { page: 12, pnum: 11, titleAr: 'مخطط الأصابع الخمسة', titleEn: 'Five Fingers Framework' },
    { page: 13, pnum: 12, titleAr: 'أقرأ: الساحرة المستديرة', titleEn: 'Reading: Round Magician' },
    { page: 14, pnum: 13, titleAr: 'بعد القراءة: وقت المناقشة', titleEn: 'Post-Reading: Discussion' },
    { page: 15, pnum: 14, titleAr: 'أكتب: التخطيط للكتابة', titleEn: 'Writing: Planning Circle' },
    { page: 16, pnum: 15, titleAr: 'التراكيب والمجلة الرياضية', titleEn: 'Connectors & Publishing' },
  ];

  const GR6_CHAPTER_1_PAGES = [
    { page: 8, pnum: 8, titleAr: 'نواتج التعلم', titleEn: 'Learning Outcomes' },
    { page: 9, pnum: 9, titleAr: 'قاموسي', titleEn: 'My Dictionary' },
    { page: 10, pnum: 10, titleAr: 'أستمع: احتياجاتي ورغباتي', titleEn: 'Listening: Needs & Desires' },
    { page: 11, pnum: 11, titleAr: 'بعد الاستماع: أبحث عن الكلمة', titleEn: 'Post-Listening: Missing Word' },
    { page: 12, pnum: 12, titleAr: 'أتحدث: احتياجات ورغبات', titleEn: 'Speaking: Needs & Desires' },
    { page: 13, pnum: 13, titleAr: 'أتخيل وأخطط: تقسيم المال', titleEn: 'Imagining: Budgeting' },
    { page: 14, pnum: 14, titleAr: 'أقرأ: احتياجاتي ورغباتي', titleEn: 'Reading: Needs & Desires' },
    { page: 15, pnum: 15, titleAr: 'بعد القراءة: عجلة الأسئلة', titleEn: 'Post-Reading: Question Wheel' },
    { page: 16, pnum: 16, titleAr: 'أكتب: التخطيط للكتابة', titleEn: 'Writing: Planning' },
    { page: 17, pnum: 17, titleAr: 'أكتب: نص الاحتياجات والرغبات', titleEn: 'Writing: Needs & Desires' },
  ];

  const GR7_CHAPTER_1_PAGES = [
    { page: 7, pnum: 6, titleAr: 'نواتج التعلم: كيف قضيت إجازتي؟', titleEn: 'Learning Outcomes: Vacation' },
    { page: 8, pnum: 7, titleAr: 'قاموسي الخاص', titleEn: 'My Dictionary: Vacation Lexicon' },
    { page: 9, pnum: 8, titleAr: 'أستمع: كيف قضيت إجازتي؟', titleEn: 'Listening: How I Spent My Vacation' },
    { page: 10, pnum: 9, titleAr: 'بعد الاستماع: مخطط الحوار', titleEn: 'Post-Listening: Dialogue Analysis' },
    { page: 11, pnum: 10, titleAr: 'أتحدث: كلمة وموضوع', titleEn: 'Speaking: Word & Theme' },
    { page: 12, pnum: 11, titleAr: 'بعد المحادثة: أختار وأتحدث', titleEn: 'Post-Speaking: Choose & Present' },
    { page: 13, pnum: 12, titleAr: 'أقرأ: كيف قضيت إجازتي؟', titleEn: 'Reading: How I Spent My Vacation' },
    { page: 14, pnum: 13, titleAr: 'بعد القراءة: أدوات الجزم', titleEn: 'Post-Reading: Jazam Particles' },
    { page: 15, pnum: 14, titleAr: 'أكتب: قبل الكتابة (التخطيط)', titleEn: 'Writing: Vacation Planning' },
    { page: 16, pnum: 15, titleAr: 'أثناء وبعد الكتابة: نص الإجازة', titleEn: 'Drafting & Vacation Text' },
  ];

  const CHAPTER_1_PAGES = grade === 7 ? GR7_CHAPTER_1_PAGES : grade === 6 ? GR6_CHAPTER_1_PAGES : GR5_CHAPTER_1_PAGES;

  const OTHER_CHAPTERS = [
    { page: 18, title: 'Horse Riding (ركوب الخيل)', pnum: 16 },
    { page: 28, title: 'Running (الجري)', pnum: 26 },
    { page: 38, title: 'Arts (الفنون)', pnum: 36 },
    { page: 48, title: 'Reading (القراءة)', pnum: 46 },
    { page: 58, title: 'At My School (في مدرستي)', pnum: 56 },
    { page: 68, title: 'At My Home (في بيتي)', pnum: 66 },
    { page: 78, title: 'My Food (طعامي)', pnum: 76 },
    { page: 88, title: 'My Clothes (ملابسي)', pnum: 86 },
    { page: 98, title: 'Fun Time (وقت المرح)', pnum: 96 }
  ];
  const defaultChapter1Page = (grade === 6 ? 8 : 7);
  const chapterOptions = chapters.length ? chapters : [
    {
      page: defaultChapter1Page,
      title: grade === 7
        ? 'Chapter 1 · How I Spent My Vacation (كَيْفَ قَضَيْتُ إِجَازَتِي؟)'
        : grade === 6
        ? 'Chapter 1 · Needs & Desires (احْتِيَاجَاتِي وَرَغَبَاتِي)'
        : 'Chapter 1 · Ball Games (أَلْعَابُ الكُرَةِ)'
    },
    ...OTHER_CHAPTERS.map((chapter, index) => ({ page: chapter.page, title: `Chapter ${index + 2} · ${chapter.title}` }))
  ];
  const selectedChapter = [...chapterOptions].reverse().find((chapter) => currentPage >= chapter.page) || chapterOptions[0];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Top Header & Pagination */}
      <div className="sharp-card p-4 border-b-2 border-slate-900 bg-white flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-xl font-black text-slate-900 font-arabic">
            العَرَبِيَّةُ تَجْمَعُنَا (Arabic Brings Us Together)
          </h1>
        </div>

        {/* View Mode Toggle & Page Navigators */}
        <div className="flex items-center flex-wrap gap-2">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            Grade
            <select
              value={grade}
              onChange={(e) => {
                const nextGrade = Number(e.target.value);
                setGrade(nextGrade);
                setCurrentPage(nextGrade === 6 ? 8 : 7);
                onSelectGrade?.(nextGrade);
              }}
              className="border border-slate-400 bg-white px-2 py-1 text-xs font-semibold"
            >
              {availableGrades.map((g) => (
                <option key={g} value={g}>Grade {g}</option>
              ))}
            </select>
          </label>
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            Term
            <select
              value={term}
              onChange={(e) => {
                setTerm(Number(e.target.value));
                setCurrentPage(grade === 6 ? 8 : 7);
              }}
              className="border border-slate-400 bg-white px-2 py-1 text-xs font-semibold"
            >
              <option value={1}>Term 1</option>
              <option value={2}>Term 2</option>
              <option value={3}>Term 3</option>
            </select>
          </label>
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            Chapter
            <select value={selectedChapter.page} onChange={(e) => setCurrentPage(Number(e.target.value))} className="border border-slate-400 bg-white px-2 py-1 text-xs font-semibold">
              {chapterOptions.map((chapter) => <option key={chapter.page} value={chapter.page}>{chapter.title}</option>)}
            </select>
          </label>
          {/* View Mode Switcher */}
          <div className="flex border border-slate-300 bg-slate-100 p-0.5 text-xs font-bold mr-2">
            <button
              onClick={() => setViewMode('split')}
              className={`px-2.5 py-1 transition-all ${
                viewMode === 'split' ? 'bg-emerald-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              عرض مزدوج (Split)
            </button>
            <button
              onClick={() => setViewMode('text')}
              className={`px-2.5 py-1 transition-all ${
                viewMode === 'text' ? 'bg-emerald-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              النص والترجمة (Text)
            </button>
            <button
              onClick={() => setViewMode('image')}
              className={`px-2.5 py-1 transition-all ${
                viewMode === 'image' ? 'bg-emerald-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              الكتاب المصور (Image)
            </button>
          </div>

          <ArabEnglishToggleSwitch />
        </div>
      </div>

      {/* Reader Body */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Chapter index removed; navigation is provided by the top Chapter selector. */}
        <div className="hidden">
          {/* Chapter 1 Pages Card */}
          <div className="sharp-card p-3.5 border-2 border-emerald-900 bg-white space-y-2.5">
            <div className="border-b border-emerald-100 pb-2">
              <span className="text-[10px] font-black uppercase tracking-wider text-emerald-800 block">
                Chapter 1 · Complete
              </span>
              <h3 className="text-sm font-bold text-slate-900 font-arabic">
                {grade === 6 ? 'احْتِيَاجَاتِي وَرَغَبَاتِي (My Needs & Desires)' : 'أَلْعَابُ الكُرَةِ (Ball Games)'}
              </h3>
              <span className="text-[11px] text-slate-500 font-sans">
                {grade === 6 ? 'Printed Pages 8 to 17 (10 Pages)' : 'Printed Pages 6 to 15 (10 Pages)'}
              </span>
            </div>

            <div className="space-y-1 text-xs">
              {CHAPTER_1_PAGES.map((item) => {
                const isActive = currentPage === item.page;
                return (
                  <button
                    key={item.page}
                    onClick={() => setCurrentPage(item.page)}
                    className={`w-full text-left p-2 border transition-all flex flex-col justify-between ${
                      isActive
                        ? 'border-emerald-800 bg-emerald-100/70 font-bold text-emerald-950 shadow-xs'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-arabic font-semibold">{item.titleAr}</span>
                      <span className="text-[10px] font-mono bg-white px-1.5 py-0.5 border border-slate-300 rounded-xs">
                        ص {item.pnum}
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-sans mt-0.5">{item.titleEn}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Other Chapters Jump */}
          <div className="sharp-card p-3 border border-slate-300 bg-white space-y-2 text-xs">
            <h4 className="text-[11px] font-bold text-slate-600 uppercase tracking-wider border-b border-slate-200 pb-1">
              Other Chapters (فصول المنهاج الأخرى):
            </h4>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {OTHER_CHAPTERS.map((item) => (
                <button
                  key={item.page}
                  onClick={() => setCurrentPage(item.page)}
                  className={`w-full text-left p-1.5 text-[11px] border transition-all flex items-center justify-between ${
                    currentPage === item.page
                      ? 'border-emerald-800 bg-emerald-50 font-bold'
                      : 'border-slate-100 hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <span className="truncate">{item.title}</span>
                  <span className="text-[10px] font-mono text-slate-400">p.{item.pnum}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main reader content */}
        <div className="lg:col-span-12 space-y-4">
          {/* Main Card */}
          <div className="sharp-card p-6 border-2 border-slate-900 bg-white min-h-[600px] space-y-5">
            {/* Page Title & Audio Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-4 gap-3">
              <div>
                <span className="text-xs font-mono text-slate-500 block">
                  PDF Page {currentPage} · Printed Page {pageData?.printed_page || '—'} · {pageData?.unit || 'الرياضات والهوايات'}
                </span>
                <h2 className="text-xl font-black text-slate-900 font-arabic mt-1 text-right sm:text-left" dir="rtl">
                  {pageData?.title_ar}
                </h2>
                {pageData?.title_en && (
                  <div className="text-xs text-emerald-800 font-sans font-semibold mt-0.5">
                    {pageData.title_en}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                  disabled={currentPage <= 1}
                  className="px-3 py-2 text-xs font-bold border border-slate-400 bg-white text-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  ← Previous
                </button>
                <button
                  onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                  disabled={currentPage >= totalPages}
                  className="px-3 py-2 text-xs font-bold border border-slate-900 bg-slate-900 text-white disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next →
                </button>
                <button
                  onClick={() => {
                    if (pageData?.paragraphs) {
                      audioManager.playArabic(pageData.paragraphs.join(' '));
                    }
                  }}
                  className="btn-primary text-xs py-2 px-3 flex items-center gap-1.5 shadow-xs"
                >
                  <Volume2 className="w-4 h-4" />
                  <span>Read Full Page (استمع للصفحة كاملة)</span>
                </button>
              </div>
            </div>

            {/* Split View Grid or Single View */}
            <div className={`grid gap-6 ${viewMode === 'split' ? 'grid-cols-1 xl:grid-cols-2' : 'grid-cols-1'}`}>
              {/* 1. Scanned Original Page Image (visible in split or image mode) */}
              {(viewMode === 'split' || viewMode === 'image') && (
                <div className="space-y-2 order-1">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 bg-slate-100 p-2 border border-slate-300">
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-emerald-800" />
                      <span>الكتاب المدرسي الأصلي (Original Scanned Page)</span>
                    </span>
                    <span className="font-mono text-[11px] text-slate-500">Printed Page {pageData?.printed_page}</span>
                  </div>
                  <div className="border-2 border-slate-300 bg-slate-100 p-2 rounded-sm max-h-[750px] overflow-auto flex items-center justify-center">
                    <img
                      src={`/api/admin/page-image/${currentPage}?edition_id=${currentEditionId}`}
                      alt={`Textbook Page ${currentPage}`}
                      className="max-w-full h-auto object-contain shadow-md rounded-xs"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.onerror = null;
                        target.src = `/api/admin/page-image/${currentPage}`;
                      }}
                    />
                  </div>
                </div>
              )}

              {/* 2. Interactive Arabic Text with Word Audio & English Translations (visible in split or text mode) */}
              {(viewMode === 'split' || viewMode === 'text') && (
                <div className="space-y-4 order-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 bg-emerald-50 p-2 border border-emerald-300">
                    <span className="flex items-center gap-1.5 text-emerald-950">
                      <Volume2 className="w-3.5 h-3.5 text-emerald-800" />
                      <span>النص التفاعلي والترجمة الإنجليزية (Interactive Text & Translation)</span>
                    </span>
                    <span className="text-[10px] text-emerald-800 font-sans">Click any word for audio</span>
                  </div>

                  <div className="space-y-3.5 max-h-[750px] overflow-y-auto pr-1">
                    {pageData?.paragraphs?.map((p: string, pIdx: number) => {
                      const modelAnswer =
                        pageData?.model_answers?.[pIdx] ||
                        pageData?.model_answers?.[String(pIdx)] ||
                        dynamicAnswers[pIdx];
                      const isQuestion =
                        p.includes('؟') ||
                        p.includes('?') ||
                        !!(pageData?.model_answers?.[pIdx] || pageData?.model_answers?.[String(pIdx)]);

                      return (
                        <div
                          key={pIdx}
                          className="p-4 bg-slate-50/80 border border-slate-300 hover:border-emerald-700 transition-colors shadow-2xs space-y-2"
                        >
                          <div className="flex justify-between items-center text-[11px] text-slate-500 border-b border-slate-200 pb-1.5">
                            <button
                              onClick={() => audioManager.playArabic(p)}
                              className="text-emerald-800 hover:text-emerald-950 font-bold flex items-center gap-1 hover:underline"
                              title="Listen to this paragraph"
                            >
                              <Volume2 className="w-3.5 h-3.5" />
                              <span>Listen (استمع للفقرة)</span>
                            </button>
                            <span className="font-mono text-[10px] text-slate-400">Paragraph {pIdx + 1}</span>
                          </div>

                          {/* Interactive Arabic Sentence */}
                          <div className="text-right leading-loose pt-1 font-arabic" dir="rtl">
                            <ArabicWordSpans
                              text={p}
                              className="text-lg font-medium leading-loose text-slate-900"
                            />
                          </div>

                          {/* English Translation Directly Below */}
                          {pageData?.paragraphs_en?.[pIdx] && (
                            <div className="pt-2 border-t border-slate-200 text-xs text-slate-600 font-sans italic text-left leading-relaxed" dir="ltr">
                              <span className="font-semibold text-slate-400 not-italic mr-1">EN:</span>
                              {pageData.paragraphs_en[pIdx]}
                            </div>
                          )}

                          {/* Model Answer Button & Accordion (For Questions & Exercises) */}
                          {isQuestion && (
                            <div className="pt-2 border-t border-slate-200 space-y-2">
                              <button
                                onClick={() => toggleAnswer(pIdx, p)}
                                disabled={loadingAnswers[pIdx]}
                                className={`w-full py-1.5 px-3 rounded-sm text-xs font-bold flex items-center justify-between transition-all ${
                                  expandedAnswers[pIdx]
                                    ? 'bg-amber-100 text-amber-900 border border-amber-300'
                                    : 'bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 hover:border-amber-300'
                                }`}
                              >
                                <span className="flex items-center gap-1.5">
                                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                                  <span>
                                    {expandedAnswers[pIdx]
                                      ? 'إخفاء الإجابة النموذجية (Hide Model Answer)'
                                      : '💡 عرض الإجابة النموذجية (Show Model Answer)'}
                                  </span>
                                </span>
                                {loadingAnswers[pIdx] ? (
                                  <span className="flex items-center gap-1 text-[11px] text-amber-700">
                                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                    <span>جاري التفكير... (Solving...)</span>
                                  </span>
                                ) : expandedAnswers[pIdx] ? (
                                  <ChevronUp className="w-3.5 h-3.5 text-amber-700" />
                                ) : (
                                  <ChevronDown className="w-3.5 h-3.5 text-amber-700" />
                                )}
                              </button>

                              {/* Expanded Model Answer Card */}
                              {expandedAnswers[pIdx] && modelAnswer && (
                                <div className="p-3 bg-amber-50/80 rounded-sm border border-amber-300 shadow-2xs space-y-2.5">
                                  {/* Answer header with pronunciation button */}
                                  <div className="flex justify-between items-center text-[11px] pb-1.5 border-b border-amber-200">
                                    <span className="font-bold text-amber-900 flex items-center gap-1">
                                      <span>الإجابة النموذجية</span>
                                      <span className="text-[10px] text-amber-700 font-sans font-normal">(Model Answer)</span>
                                    </span>
                                    <button
                                      onClick={() => audioManager.playArabic(modelAnswer.text_ar)}
                                      className="text-amber-800 hover:text-amber-950 font-bold flex items-center gap-1 hover:underline text-[11px]"
                                      title="Listen to model answer"
                                    >
                                      <Volume2 className="w-3 h-3 text-amber-700" />
                                      <span>استمع للإجابة (Listen)</span>
                                    </button>
                                  </div>

                                  {/* Arabic Answer (Interactive audio words) */}
                                  <div className="text-right leading-loose font-arabic" dir="rtl">
                                    <ArabicWordSpans
                                      text={modelAnswer.text_ar}
                                      className="text-base font-bold text-amber-950 leading-loose"
                                    />
                                  </div>

                                  {/* Arabzi Phonetics Badge */}
                                  {modelAnswer.arabzi && (
                                    <div className="flex items-center gap-1.5 text-xs text-amber-900 bg-amber-100/90 px-2 py-1 rounded-xs border border-amber-200">
                                      <span className="font-bold font-sans text-[11px] text-amber-800">🗣️ Arabzi:</span>
                                      <span className="font-mono text-[11px] tracking-wide text-amber-950">{modelAnswer.arabzi}</span>
                                    </div>
                                  )}

                                  {/* English Translation */}
                                  {modelAnswer.text_en && (
                                    <div className="text-xs text-slate-700 font-sans leading-relaxed">
                                      <span className="font-semibold text-amber-900 mr-1">Meaning:</span>
                                      <span>{modelAnswer.text_en}</span>
                                    </div>
                                  )}

                                  {/* Pedagogical Explanation / Grammar Rule */}
                                  {modelAnswer.explanation_en && (
                                    <div className="text-[11px] text-amber-800 bg-white/70 p-2 rounded-xs border border-amber-200 font-sans leading-relaxed">
                                      <span className="font-semibold text-amber-950 block mb-0.5">Rule / Context:</span>
                                      <span>{modelAnswer.explanation_en}</span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>
      </div>

      {/* Coverage Report Modal */}
      {showCoverageModal && coverageReport && (
        <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white border-2 border-slate-900 w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-200 pb-2">
              <h3 className="font-bold text-slate-900 text-base">
                Whole-Book Coverage Report (Section 11)
              </h3>
              <button onClick={() => setShowCoverageModal(false)} className="text-slate-500 font-bold">
                ✕
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Source Book Title:</span>
                <span className="font-bold text-slate-900">{coverageReport.book_title}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Total Source PDF Pages:</span>
                <span className="font-bold text-slate-900">{coverageReport.total_source_pages}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Reviewed Chapter Pages:</span>
                <span className="font-bold text-emerald-800">{coverageReport.reviewed_pages_count}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Reviewed Sentences:</span>
                <span className="font-bold text-slate-900">{coverageReport.reviewed_sentences_count}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Reviewed Word Occurrences:</span>
                <span className="font-bold text-slate-900">{coverageReport.reviewed_word_occurrences}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-600">Playable Audio Targets:</span>
                <span className="font-bold text-emerald-800">{coverageReport.playable_audio_targets_count}</span>
              </div>
            </div>

            <div className="p-3 bg-slate-100 text-xs text-slate-600 space-y-1">
              <div className="font-bold text-slate-800">Review Integrity:</div>
              <div>{coverageReport.content_review_status}</div>
            </div>

            <button
              onClick={() => setShowCoverageModal(false)}
              className="btn-primary w-full py-2 text-xs font-bold"
            >
              Close Report
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
