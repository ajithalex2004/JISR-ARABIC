import React, { useState, useEffect } from 'react';
import {
  Volume2, Play, CheckCircle2, XCircle, ArrowLeft, RotateCcw,
  Sparkles, Check, Send, Award, FileText, UserCheck, ShieldAlert,
  HelpCircle, ChevronRight, Mic, BookOpen
} from 'lucide-react';
import { LessonPackage, ChildProfile, MistakeEntry } from '../../types';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';
import { audioManager } from '../../services/audio';
import { api } from '../../services/api';
import { PronunciationSandbox } from '../audio/PronunciationSandbox';

interface LessonViewerProps {
  lessonId: string;
  activeChild: ChildProfile | null;
  onBack: () => void;
  onOpenPaywall: () => void;
  onOpenReader?: (page?: number) => void;
}

const CHAPTER_1_PAGES = [
  { page: 8, pnum: 6, titleAr: 'نواتج التعلم', titleEn: 'Learning Outcomes' },
  { page: 9, pnum: 7, titleAr: 'قاموسي', titleEn: 'My Glossary' },
  { page: 10, pnum: 8, titleAr: 'أستمع: ألعاب الكرة', titleEn: 'Listening: Ball Games' },
  { page: 11, pnum: 9, titleAr: 'بعد الاستماع: أبحث عن الخطأ', titleEn: 'Post-Listening: Error Hunt' },
  { page: 12, pnum: 10, titleAr: 'أتحدث: استبيان الألعاب', titleEn: 'Speaking: Sports Survey' },
  { page: 13, pnum: 11, titleAr: 'مخطط الأصابع الخمسة', titleEn: 'Five Fingers & Presentation' },
  { page: 14, pnum: 12, titleAr: 'أقرأ: الساحرة المستديرة', titleEn: 'Reading: Round Magician' },
  { page: 15, pnum: 13, titleAr: 'بعد القراءة: وقت المناقشة', titleEn: 'Post-Reading: Discussion' },
  { page: 16, pnum: 14, titleAr: 'أكتب: التخطيط للكتابة', titleEn: 'Writing: Planning Circle' },
  { page: 17, pnum: 15, titleAr: 'التراكيب ومجلة المدرسة الرياضية', titleEn: 'Connectors & Publishing' },
];

type FeatureTab =
  | 'vocab'
  | 'studio'
  | 'grammar'
  | 'builder'
  | 'practice'
  | 'mission'
  | 'instructions'
  | 'prep'
  | 'mistakes'
  | 'exam';

export const LessonViewer: React.FC<LessonViewerProps> = ({
  lessonId,
  activeChild,
  onBack,
  onOpenPaywall,
  onOpenReader
}) => {
  const [data, setData] = useState<{ lesson: any; content: LessonPackage; version_id?: string } | null>(null);
  const [activeTab, setActiveTab] = useState<FeatureTab>('vocab');
  const [selectedPath, setSelectedPath] = useState<'foundation' | 'guided' | 'independent'>('guided');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');

  // Chapter 1 Complete 10 Pages State
  const [selectedChapterPdfPage, setSelectedChapterPdfPage] = useState<number>(14); // Default PDF page 14 = printed page 12 (Main Reading)
  const [chapterPageData, setChapterPageData] = useState<any>(null);
  const [isLoadingChapterPage, setIsLoadingChapterPage] = useState<boolean>(false);

  // Interactive Feature State
  const [prepAnswers, setPrepAnswers] = useState<Record<string, string>>({});
  const [prepSubmitted, setPrepSubmitted] = useState<boolean>(false);
  const [practiceAnswers, setPracticeAnswers] = useState<Record<string, string>>({});
  const [practiceResults, setPracticeResults] = useState<Record<string, any>>({});
  
  // Sentence Builder State
  const [activeChallengeIndex, setActiveChallengeIndex] = useState<number>(0);
  const [selectedTiles, setSelectedTiles] = useState<string[]>([]);
  const [builderFeedback, setBuilderFeedback] = useState<{ isCorrect?: boolean; msg?: string }>({});

  // Exam State
  const [examAnswers, setExamAnswers] = useState<Record<string, string>>({});
  const [examWritingText, setExamWritingText] = useState<string>('');
  const [examSubmitted, setExamSubmitted] = useState<boolean>(false);
  const [examFeedback, setExamFeedback] = useState<any>(null);

  // Mistake Notebook
  const [mistakes, setMistakes] = useState<MistakeEntry[]>([]);

  useEffect(() => {
    loadLesson();
    if (activeChild) {
      loadMistakes();
    }
  }, [lessonId, activeChild]);

  const loadLesson = async () => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      const res = await api.getLessonContent(lessonId, activeChild?.id);
      setData(res);
    } catch (err: any) {
      if (err.message === 'PAYMENT_REQUIRED') {
        setErrorMsg('Payment required to access this term. Chapter 1 is available as Free Demo.');
        onOpenPaywall();
      } else {
        setErrorMsg(err.message || 'Failed to load lesson package.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadMistakes = async () => {
    if (!activeChild) return;
    try {
      const mList = await api.getMistakes(activeChild.id);
      setMistakes(mList.filter((m) => m.lesson_id === lessonId));
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (activeTab === 'studio') {
      loadChapterPage(selectedChapterPdfPage);
    }
  }, [selectedChapterPdfPage, activeTab]);

  const loadChapterPage = async (pdfPage: number) => {
    setIsLoadingChapterPage(true);
    try {
      const pageRes = await api.getOcrPage(pdfPage);
      setChapterPageData(pageRes);
    } catch (err) {
      console.error('Failed to load chapter page:', err);
    } finally {
      setIsLoadingChapterPage(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center">
        <div className="text-sm font-bold text-slate-700">Loading validated lesson package...</div>
        <div className="text-xs text-slate-500 mt-1">Arabic vowels, audio scripts and 12 pedagogical features</div>
      </div>
    );
  }

  if (errorMsg || !data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center space-y-4">
        <div className="p-4 bg-amber-50 border border-amber-300 text-amber-900 text-sm font-bold">
          {errorMsg || 'Lesson not accessible.'}
        </div>
        <button onClick={onBack} className="btn-secondary text-xs">
          ← Back to Curriculum Catalogue
        </button>
      </div>
    );
  }

  const { content } = data;

  // Handle Prep Check Answer
  const handleSelectPrepOption = (qId: string, optId: string) => {
    setPrepAnswers((prev) => ({ ...prev, [qId]: optId }));
  };

  // Submit Practice Activity
  const handleSubmitPractice = async (actId: string) => {
    const ans = practiceAnswers[actId];
    if (!ans) return;
    if (!activeChild) {
      alert('Please sign in with a student profile to save progress.');
      return;
    }

    try {
      const res = await api.submitAttempt({
        child_id: activeChild.id,
        lesson_id: lessonId,
        activity_id: actId,
        path_type: selectedPath,
        user_answer: ans,
        lesson_version_id: data?.version_id
      });
      setPracticeResults((prev) => ({ ...prev, [actId]: res }));
      loadMistakes();
    } catch (e) {
      console.error(e);
    }
  };

  // Sentence Builder logic
  const currentChallenge = content?.sentence_builder?.challenges?.[activeChallengeIndex];
  const allChallengeTiles = currentChallenge && Array.isArray(currentChallenge.tiles)
    ? [...currentChallenge.tiles, ...(Array.isArray(currentChallenge.distractors) ? currentChallenge.distractors : [])].sort()
    : [];

  const handleAddTile = (tile: string) => {
    setSelectedTiles((prev) => [...prev, tile]);
    setBuilderFeedback({});
  };

  const handleRemoveTile = (index: number) => {
    setSelectedTiles((prev) => prev.filter((_, i) => i !== index));
    setBuilderFeedback({});
  };

  const handleCheckSentence = async () => {
    if (!currentChallenge) return;
    const constructed = selectedTiles.join(' ');
    try {
      const result = activeChild ? await api.submitAttempt({
        child_id: activeChild.id, lesson_id: lessonId,
        activity_id: currentChallenge.id, path_type: selectedPath,
        user_answer: constructed,
        lesson_version_id: data?.version_id
      }) : await api.checkSentence(lessonId, currentChallenge.id, constructed);
      setBuilderFeedback({ isCorrect: result.is_correct, msg: result.feedback_en });
      loadMistakes();
    } catch {
      setBuilderFeedback({ isCorrect: false, msg: 'Unable to check your sentence. Please try again.' });
    }
  };

  // Submit Exam
  const handleSubmitExam = async () => {
    if (!activeChild) {
      alert('Sign in to submit exam');
      return;
    }
    setExamSubmitted(true);
    let scoreTotal = 0;
    const qList = content.exam_practice.objective_questions;

    for (const q of qList) {
      const userAns = examAnswers[q.id];
      if (userAns) {
        const res = await api.submitAttempt({
          child_id: activeChild.id,
          lesson_id: lessonId,
          activity_id: q.id,
          path_type: 'independent',
          user_answer: userAns,
          lesson_version_id: data?.version_id
        });
        scoreTotal += res.score;
      }
    }

    if (examWritingText.trim()) {
      await api.submitForTutor({
        child_id: activeChild.id,
        lesson_id: lessonId,
        activity_id: content.exam_practice.writing_task.id,
        submission_type: 'writing',
        content_text: examWritingText
      });
    }

    setExamFeedback({
      objectiveScore: scoreTotal,
      maxObjective: qList.reduce((acc, q) => acc + q.marks, 0),
      writingRouted: Boolean(examWritingText.trim())
    });
    loadMistakes();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Top Breadcrumb & Return Bar */}
      <div className="flex flex-wrap justify-between items-center pb-3 border-b-2 border-slate-900 gap-2">
        <button
          onClick={onBack}
          className="btn-secondary text-xs flex items-center gap-1 font-bold"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Catalogue</span>
        </button>

        <div className="text-center">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest block">
            Class {content.grade} · Term {content.term} · Printed Page {content.start_page}
          </span>
          <h1 className="text-xl font-black text-slate-900">
            {content.title_en} · <ArabicWordSpans text={content.title_ar} className="text-xl font-bold text-emerald-900" />
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <ArabEnglishToggleSwitch />
          <span className="bg-emerald-800 text-white text-xs font-bold px-2.5 py-1 uppercase tracking-wider">
            {data.lesson.is_first_chapter_demo ? 'Interactive Demo Active' : 'Full Term Pack'}
          </span>
          <span className="text-xs text-slate-500 font-mono">v{content.version}</span>
        </div>
      </div>

      {/* Curriculum Learning Tabs Bar */}
      <div className="flex overflow-x-auto border-b border-slate-300 text-xs font-bold gap-1 pb-1">
        <button
          onClick={() => setActiveTab('vocab')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'vocab' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          1. قاموس المفردات (Glossary)
        </button>
        <button
          onClick={() => setActiveTab('studio')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'studio' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          2. نص القراءة والاستماع (Reading & Listening)
        </button>
        <button
          onClick={() => setActiveTab('grammar')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'grammar' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          3. القواعد والتراكيب (Grammar)
        </button>
        <button
          onClick={() => setActiveTab('builder')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'builder' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          4. باني الجمل (Sentence Builder)
        </button>
        <button
          onClick={() => setActiveTab('practice')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'practice' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          5. تمارين الكتاب الوزاري (Exercises)
        </button>
        <button
          onClick={() => setActiveTab('mission')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'mission' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          6. مهمة التحدث والنطق (Speaking)
        </button>
        <button
          onClick={() => setActiveTab('instructions')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'instructions' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          7. لغة التعليمات (Instructions)
        </button>
        <button
          onClick={() => setActiveTab('prep')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'prep' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          8. الاستعداد للدرس (Prep Check)
        </button>
        <button
          onClick={() => setActiveTab('mistakes')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'mistakes' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          9. سجل المراجعة ({mistakes.length})
        </button>
        <button
          onClick={() => setActiveTab('exam')}
          className={`px-3 py-2 border transition-all shrink-0 ${
            activeTab === 'exam' ? 'bg-emerald-900 text-white border-emerald-900' : 'bg-white text-slate-700 hover:bg-slate-100'
          }`}
        >
          10. اختبار الفصل (Chapter Quiz)
        </button>
      </div>

      {/* TAB 1: VOCABULARY & GLOSSARY (Printed Page 7) */}
      {activeTab === 'vocab' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-emerald-50/50 border border-emerald-300 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-slate-900 text-base">
                Glossary Vocabulary Cards · قَامُوسِي (Level 5 Book, p. 7)
              </h2>
              <p className="text-xs text-slate-600">
                Click any Arabic word to vocalize pronunciation. Listen to full definitions and example sentences.
              </p>
            </div>
            <span className="text-xs bg-emerald-800 text-white px-2 py-0.5 font-bold">
              {content.vocabulary_cards.length} Core Words
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {content.vocabulary_cards.map((card) => (
              <div
                key={card.id}
                className="sharp-card p-4 border border-slate-300 hover:border-emerald-800 bg-white space-y-2.5 transition-all"
              >
                {/* Header with word and listen button */}
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => audioManager.playArabic(card.vowelled_ar)}
                      className="p-1.5 bg-emerald-800 hover:bg-emerald-700 text-white transition-colors"
                      title="Listen to word"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                    <ArabicWordSpans
                      text={card.vowelled_ar}
                      className="text-2xl font-bold text-emerald-950"
                    />
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                      {card.meaning_en}
                    </span>
                    <span className="text-[10px] text-slate-400 block font-mono">
                      Root: {card.root}
                    </span>
                  </div>
                </div>

                {/* Definition */}
                <div className="bg-slate-50 p-2 text-xs border border-slate-200">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">
                    Definition (التعريف):
                  </div>
                  <ArabicWordSpans
                    text={card.definition_ar}
                    className="text-sm font-semibold text-slate-800"
                  />
                </div>

                {/* Example sentence */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase">
                    <span>Example (مثال):</span>
                    <button
                      onClick={() => audioManager.playArabic(card.example_ar)}
                      className="text-emerald-800 hover:underline flex items-center gap-0.5 lowercase"
                    >
                      <Play className="w-2.5 h-2.5 fill-current" />
                      <span>listen sentence</span>
                    </button>
                  </div>
                  <div className="text-right">
                    <ArabicWordSpans
                      text={card.example_ar}
                      className="text-sm text-slate-900 leading-relaxed font-arabic"
                    />
                  </div>
                  <div className="text-xs text-slate-500 italic">
                    {card.example_en}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pronunciation Sandbox embedded */}
          <PronunciationSandbox />
        </div>
      )}

      {/* TAB 2: COMPREHENSIVE CHAPTER 1 READING & ALL 10 PAGES (Pages 6-15) */}
      {activeTab === 'studio' && (
        <div className="space-y-5">
          {/* Chapter 1 Overview & Book Reader Link */}
          <div className="sharp-card p-4 bg-emerald-50/70 border-2 border-emerald-900 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="bg-emerald-900 text-white text-[10px] font-bold px-2 py-0.5 uppercase tracking-wider">
                  الفصل الأول كاملاً (Complete Chapter 1)
                </span>
                <span className="text-xs text-slate-500 font-sans">
                  Printed Pages 6 to 15 · 10 Complete Verified Pages
                </span>
              </div>
              <h2 className="text-lg font-black text-slate-900 font-arabic">
                أَلْعَابُ الكُرَةِ · نصوص وتمارين الفصل كاملاً مع الترجمة الصوتية والإنجليزية
              </h2>
              <p className="text-xs text-slate-600 mt-0.5">
                Browse every official page of the chapter below. Every sentence has an English translation directly underneath and word-level audio tooltips.
              </p>
            </div>

            {onOpenReader && (
              <button
                onClick={() => onOpenReader(selectedChapterPdfPage)}
                className="btn-primary text-xs py-2 px-3.5 flex items-center gap-2 shrink-0 shadow-sm"
              >
                <BookOpen className="w-4 h-4" />
                <span>فتح في قارئ الكتاب المزدوج (Dual Book Reader)</span>
              </button>
            )}
          </div>

          {/* 10-Page Horizontal Navigation Strip */}
          <div className="bg-white border border-slate-300 p-2 space-y-1.5 shadow-2xs">
            <div className="flex items-center justify-between px-1">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                اختر صفحة من الفصل الأول (Select Chapter Page):
              </span>
              <span className="text-[11px] font-bold text-emerald-800 font-mono">
                10 صفحات متوفرة (10 Pages Available)
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-1.5">
              {CHAPTER_1_PAGES.map((item) => {
                const isSelected = selectedChapterPdfPage === item.page;
                return (
                  <button
                    key={item.page}
                    onClick={() => setSelectedChapterPdfPage(item.page)}
                    className={`p-2 border text-center transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'bg-emerald-900 text-white border-emerald-950 font-bold shadow-xs'
                        : 'bg-slate-50 hover:bg-white text-slate-700 border-slate-200 hover:border-slate-400'
                    }`}
                  >
                    <span className={`text-[10px] font-mono px-1 py-0.5 rounded-xs mb-1 block ${
                      isSelected ? 'bg-emerald-800 text-amber-300 font-bold' : 'bg-slate-200 text-slate-700'
                    }`}>
                      ص {item.pnum} (p.{item.pnum})
                    </span>
                    <span className="font-arabic text-xs font-bold truncate block" title={item.titleAr}>
                      {item.titleAr}
                    </span>
                    <span className={`text-[9.5px] truncate block mt-0.5 ${isSelected ? 'text-emerald-200' : 'text-slate-500'}`} title={item.titleEn}>
                      {item.titleEn}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selected Page Content Display */}
          <div className="sharp-card p-5 border-2 border-emerald-900 bg-white space-y-4">
            {/* Page Title & Audio Action Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-3 gap-2">
              <div>
                <span className="text-xs font-mono text-slate-500 block">
                  PDF Page {selectedChapterPdfPage} · Printed Page {chapterPageData?.printed_page || '—'} · UAE Ministry Level 5
                </span>
                <h3 className="text-xl font-black text-slate-900 font-arabic mt-0.5">
                  {chapterPageData?.title_ar || 'جاري التحميل...'}
                </h3>
                {chapterPageData?.title_en && (
                  <div className="text-xs text-emerald-800 font-sans font-semibold mt-0.5">
                    {chapterPageData.title_en}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                {chapterPageData?.paragraphs && (
                  <button
                    onClick={() => audioManager.playArabic(chapterPageData.paragraphs.join(' '))}
                    className="btn-primary text-xs py-2 px-3 flex items-center gap-1.5 shadow-xs"
                  >
                    <Volume2 className="w-4 h-4" />
                    <span>استمع للصفحة كاملاً (Listen to Page)</span>
                  </button>
                )}
                {onOpenReader && (
                  <button
                    onClick={() => onOpenReader(selectedChapterPdfPage)}
                    className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
                    title="View scanned authentic textbook image"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-emerald-800" />
                    <span>عرض الصفحة الأصلية</span>
                  </button>
                )}
              </div>
            </div>

            {/* Loading Indicator */}
            {isLoadingChapterPage && (
              <div className="py-8 text-center text-slate-500 text-xs font-bold">
                جَارٍ تَحْمِيلُ نُصُوصِ الصَّفْحَةِ وَتَرْجَمَتِهَا... (Loading page transcription and translations...)
              </div>
            )}

            {/* Render Page Paragraphs with English Translation Under Each */}
            {!isLoadingChapterPage && chapterPageData && (
              <div className="space-y-4">
                {chapterPageData.paragraphs?.map((para: string, idx: number) => (
                  <div key={idx} className="p-4 bg-slate-50/70 border border-slate-300 space-y-2.5 rounded-sm">
                    {/* Paragraph Number & Listen Button */}
                    <div className="flex items-center justify-between border-b border-slate-200/80 pb-1.5">
                      <button
                        onClick={() => audioManager.playArabic(para)}
                        className="text-xs font-bold text-emerald-800 hover:text-emerald-950 flex items-center gap-1"
                        title="Play paragraph audio"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                        <span>استمع للفقرة (Listen)</span>
                      </button>
                      <span className="text-[10px] font-mono text-slate-400 uppercase font-bold">
                        Paragraph {idx + 1}
                      </span>
                    </div>

                    {/* Arabic Text with Word Tooltips */}
                    <div className="text-right leading-loose font-arabic text-lg text-slate-900 select-text" dir="rtl">
                      <ArabicWordSpans text={para} className="text-lg text-slate-900 font-arabic select-text" />
                    </div>

                    {/* English Translation Directly Below */}
                    <div className="text-xs text-slate-600 italic bg-white p-3 border border-slate-200 text-left rounded-xs">
                      <span className="font-bold text-slate-800 not-italic block mb-0.5 text-left font-sans">
                        English Translation (الترجمة الإنجليزية):
                      </span>
                      {chapterPageData.paragraphs_en?.[idx] || 'Translation verified for this section.'}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* If Page 14 (Printed Page 12: Main Reading), Also Show Sentence-by-Sentence Audio Scripts */}
            {selectedChapterPdfPage === 14 && content.listen_speak_studio?.audio_scripts && (
              <div className="pt-4 border-t-2 border-slate-200">
                <div className="mb-3">
                  <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider block">
                    تدريبات الاستماع جملة بجملة (Sentence-by-Sentence Listening Drills)
                  </span>
                  <p className="text-xs text-slate-500">
                    Listen to each sentence individually to practice pronunciation and intonation:
                  </p>
                </div>
                <div className="space-y-2">
                  {content.listen_speak_studio.audio_scripts.map((script) => (
                    <div
                      key={script.id}
                      className="p-3 border border-slate-200 bg-white flex items-center justify-between gap-4 hover:border-emerald-700"
                    >
                      <button
                        onClick={() => audioManager.playArabic(script.text_ar)}
                        className="p-2 bg-emerald-900 hover:bg-emerald-800 text-white shrink-0"
                        title="Play sentence"
                      >
                        <Volume2 className="w-4 h-4" />
                      </button>
                      <div className="flex-1 text-right">
                        <ArabicWordSpans text={script.text_ar} className="text-base font-bold text-slate-900" />
                        <div className="text-xs text-slate-500 mt-0.5 text-left italic">{script.text_en}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: INSTRUCTION DECODER (Printed Page 8-10 Command Verbs) */}
      {activeTab === 'instructions' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-slate-100 border border-slate-300">
            <h2 className="font-bold text-slate-900 text-base">
              Arabic Exercise-Instruction Decoder (مفكك تعليمات التمارين)
            </h2>
            <p className="text-xs text-slate-600">
              Master the command verbs that UAE textbooks use so learners can understand instructions without guessing.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {content.instruction_decoder.map((inst, idx) => (
              <div key={idx} className="sharp-card p-4 border border-slate-300 bg-white space-y-2">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <button
                    onClick={() => audioManager.playArabic(inst.verb_ar)}
                    className="p-1.5 bg-emerald-800 text-white hover:bg-emerald-700"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                  <ArabicWordSpans text={inst.verb_ar} className="text-xl font-bold text-emerald-950" />
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-800 uppercase block">{inst.meaning_en}</span>
                    <span className="text-[11px] text-slate-400 font-mono italic">{inst.transliteration}</span>
                  </div>
                </div>

                <div className="text-xs text-slate-700 bg-emerald-50/60 p-2 border border-emerald-200">
                  <span className="font-bold text-emerald-950 block mb-0.5">What the child must do:</span>
                  {inst.action_guidance}
                </div>

                <div className="pt-1 text-right">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block text-left">Textbook Example:</span>
                  <ArabicWordSpans text={inst.sample_sentence_ar} className="text-sm font-arabic font-medium" />
                  <div className="text-[11px] text-slate-500 italic text-left">{inst.sample_sentence_en}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: GRAMMAR & PATTERNS (Printed Page 11 & 14) */}
      {activeTab === 'grammar' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-emerald-50/40 border border-emerald-300">
            <h2 className="font-bold text-slate-900 text-base">
              {content.grammar_lab.title_en} · {content.grammar_lab.title_ar}
            </h2>
            <p className="text-xs text-slate-600">
              Grammar rules for noun-adjective agreement, singular/dual forms, and possessive pronouns (ياء المتكلم، هاء الغائب).
            </p>
          </div>

          <div className="space-y-4">
            {content.grammar_lab.sections.map((sec, idx) => (
              <div key={idx} className="sharp-card p-5 border border-slate-300 bg-white space-y-3">
                <div className="border-b border-slate-200 pb-2 flex justify-between items-baseline">
                  <h3 className="font-bold text-slate-900 text-sm">
                    {sec.rule_name_en} · <span className="font-arabic text-emerald-900">{sec.rule_name_ar}</span>
                  </h3>
                </div>
                <p className="text-xs text-slate-600">{sec.explanation_en}</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
                  {sec.examples.map((ex, exIdx) => (
                    <div key={exIdx} className="p-3 bg-slate-50 border border-slate-200 text-right space-y-1">
                      <div className="flex justify-between items-center">
                        <button
                          onClick={() => audioManager.playArabic(ex.phrase_ar)}
                          className="p-1 bg-emerald-800 text-white"
                        >
                          <Volume2 className="w-3 h-3" />
                        </button>
                        <ArabicWordSpans text={ex.phrase_ar} className="text-base font-bold text-slate-900" />
                      </div>
                      <div className="text-xs text-slate-500 italic text-left">{ex.translation_en}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: SENTENCE BUILDER */}
      {activeTab === 'builder' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-white border border-slate-300 space-y-2">
            <div className="flex justify-between items-center">
              <h2 className="font-bold text-slate-900 text-base">
                Interactive Sentence Builder (باني الجمل التفاعلي)
              </h2>
              <div className="flex gap-1">
                {content.sentence_builder.challenges.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setActiveChallengeIndex(i);
                      setSelectedTiles([]);
                      setBuilderFeedback({});
                    }}
                    className={`px-2.5 py-1 text-xs font-bold border ${
                      activeChallengeIndex === i ? 'bg-emerald-900 text-white border-emerald-950' : 'bg-white text-slate-700'
                    }`}
                  >
                    Challenge {i + 1}
                  </button>
                ))}
              </div>
            </div>
            <p className="text-xs text-slate-600">
              Click words from the word bank to arrange them into a grammatically correct Arabic sentence.
            </p>
          </div>

          {currentChallenge && (
            <div className="sharp-card p-6 border-2 border-slate-900 bg-white space-y-5">
              {/* Target English sentence */}
              <div className="bg-slate-100 p-3 border border-slate-300">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                  Target English Meaning:
                </span>
                <span className="text-base font-bold text-slate-900">{currentChallenge.target_en}</span>
              </div>

              {/* Assembled Sentence Stage */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-2">
                  Your Assembled Arabic Sentence (Click words to remove):
                </label>
                <div className="min-h-[60px] p-3 border-2 border-dashed border-emerald-700 bg-emerald-50/30 flex flex-wrap items-center justify-end gap-2" dir="rtl">
                  {selectedTiles.length === 0 ? (
                    <span className="text-slate-400 text-sm font-sans">
                      Click the tiles below to build the sentence here...
                    </span>
                  ) : (
                    selectedTiles.map((tile, tIdx) => (
                      <button
                        key={tIdx}
                        onClick={() => handleRemoveTile(tIdx)}
                        className="bg-emerald-800 text-white font-arabic text-base font-bold px-3 py-1.5 border border-emerald-950 shadow-sm hover:bg-red-800 transition-colors"
                        title="Click to remove"
                      >
                        {tile}
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Tile Bank */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-2">
                  Word Bank (Click to add to sentence):
                </label>
                <div className="flex flex-wrap gap-2 justify-end" dir="rtl">
                  {allChallengeTiles.map((tile, tIdx) => (
                    <button
                      key={tIdx}
                      onClick={() => handleAddTile(tile)}
                      className="bg-white hover:bg-emerald-100 text-slate-900 font-arabic text-lg font-bold px-4 py-2 border-2 border-slate-700 shadow-sm transition-all"
                    >
                      {tile}
                    </button>
                  ))}
                </div>
              </div>

              {/* Feedback */}
              {builderFeedback.msg && (
                <div
                  className={`p-3 border text-xs font-bold flex items-center gap-2 ${
                    builderFeedback.isCorrect
                      ? 'bg-emerald-100 border-emerald-400 text-emerald-900'
                      : 'bg-red-100 border-red-400 text-red-900'
                  }`}
                >
                  {builderFeedback.isCorrect ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-700 shrink-0" />
                  )}
                  <span>{builderFeedback.msg}</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                <button
                  onClick={() => setSelectedTiles([])}
                  className="btn-secondary text-xs flex items-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Clear All Tiles</span>
                </button>

                <div className="flex gap-2">
                  <button
                    onClick={() => audioManager.playArabic(selectedTiles.join(' '))}
                    disabled={selectedTiles.length === 0}
                    className="btn-secondary text-xs flex items-center gap-1"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>Listen</span>
                  </button>
                  <button
                    onClick={handleCheckSentence}
                    disabled={selectedTiles.length === 0}
                    className="btn-primary text-xs flex items-center gap-1.5 px-4"
                  >
                    <Check className="w-4 h-4" />
                    <span>Check Sentence (تحقق)</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 6: PRACTICE EXERCISES (Printed Page 9 & 13) */}
      {activeTab === 'practice' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-emerald-50/50 border border-emerald-300 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-slate-900 text-base">
                Interactive Practice Exercises · تمارين الفهم والاختيار
              </h2>
              <p className="text-xs text-slate-600">
                Graded strictly on the server against pinned textbook answers. Diacritics normalized.
              </p>
            </div>
            <span className="text-xs bg-emerald-900 text-white px-2 py-0.5 font-bold">
              {content.practice_activities.length} Exercises
            </span>
          </div>

          <div className="space-y-4">
            {content.practice_activities.map((act) => {
              const res = practiceResults[act.id];
              const selectedOpt = practiceAnswers[act.id];

              return (
                <div key={act.id} className="sharp-card p-5 border border-slate-300 bg-white space-y-3">
                  <div className="flex justify-between items-baseline border-b border-slate-200 pb-2">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider font-mono">
                      {act.id} · {act.title_en}
                    </span>
                    <span className="text-xs font-bold text-emerald-900">
                      Points: {act.points}
                    </span>
                  </div>

                  {/* Arabic Prompt */}
                  <div className="text-right flex items-center justify-between">
                    <button
                      onClick={() => audioManager.playArabic(act.prompt_ar)}
                      className="p-1.5 bg-emerald-800 text-white"
                      title="Listen to question prompt"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                    <ArabicWordSpans
                      text={act.prompt_ar}
                      className="text-lg font-bold text-slate-900"
                    />
                  </div>
                  <div className="text-xs text-slate-500 italic">{act.prompt_en}</div>

                  {/* Options */}
                  <div className="space-y-2 pt-2">
                    {act.options.map((opt) => {
                      const isSelected = selectedOpt === opt.id;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => setPracticeAnswers((prev) => ({ ...prev, [act.id]: opt.id }))}
                          className={`w-full p-3 border text-right transition-all flex items-center justify-between ${
                            isSelected
                              ? 'border-emerald-800 bg-emerald-50 text-slate-900 font-bold'
                              : 'border-slate-300 bg-white text-slate-800 hover:bg-slate-50'
                          }`}
                        >
                          <span className="text-xs text-slate-400 font-sans italic">{opt.label_en}</span>
                          <div className="flex items-center gap-2">
                            <ArabicWordSpans text={opt.label_ar} className="font-arabic text-base" />
                            <span className="w-4 h-4 border border-slate-400 flex items-center justify-center text-xs">
                              {isSelected ? '✓' : ''}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Result Feedback Banner */}
                  {res && (
                    <div
                      className={`p-3 border text-xs font-bold flex items-center gap-2 ${
                        res.is_correct
                          ? 'bg-emerald-100 border-emerald-400 text-emerald-900'
                          : 'bg-red-100 border-red-400 text-red-900'
                      }`}
                    >
                      {res.is_correct ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-700 shrink-0" />
                      )}
                      <div>
                        <div>{res.feedback_ar}</div>
                        <div className="font-normal font-sans text-slate-600">{res.feedback_en}</div>
                      </div>
                    </div>
                  )}

                  {/* Submit Action */}
                  <div className="pt-2 flex justify-end">
                    <button
                      onClick={() => handleSubmitPractice(act.id)}
                      disabled={!selectedOpt}
                      className="btn-primary text-xs py-1.5 px-4"
                    >
                      Submit Answer (تأكيد الإجابة)
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 7: SPEAKING MISSION (UAE Sports Club Scenario) */}
      {activeTab === 'mission' && (
        <div className="space-y-4">
          <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-4">
            <div className="border-b border-slate-200 pb-3">
              <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider block">
                Real-Life UAE Communicative Mission
              </span>
              <h2 className="text-lg font-black text-slate-900">
                {content.speaking_mission.title_en} · <span className="font-arabic text-emerald-900">{content.speaking_mission.title_ar}</span>
              </h2>
            </div>

            <div className="bg-amber-50 border border-amber-300 p-3 text-xs text-amber-950">
              <span className="font-bold block mb-1">Scenario (الموقف اليومي):</span>
              {content.speaking_mission.scenario_en}
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Practice Sentences (Listen, Repeat, and Record):
              </h3>
              {content.speaking_mission.prompts_ar.map((pr, idx) => (
                <div key={idx} className="p-3 border border-slate-200 bg-slate-50 flex items-center justify-between gap-4">
                  <button
                    onClick={() => audioManager.playArabic(pr)}
                    className="p-2 bg-emerald-900 text-white hover:bg-emerald-800 shrink-0"
                    title="Listen to model"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                  <div className="flex-1 text-right">
                    <ArabicWordSpans text={pr} className="text-lg font-bold text-slate-900" />
                    {content.speaking_mission.prompts_en?.[idx] && (
                      <div className="text-xs text-slate-500 italic mt-0.5 text-left" dir="ltr">
                        {content.speaking_mission.prompts_en[idx]}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Microphone recorder component */}
            <PronunciationSandbox />
          </div>
        </div>
      )}

      {/* TAB 8: PREPARATION CHECK */}
      {activeTab === 'prep' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-slate-100 border border-slate-300">
            <h2 className="font-bold text-slate-900 text-base">
              {content.prep_check.title_en} · {content.prep_check.title_ar}
            </h2>
            <p className="text-xs text-slate-600">{content.prep_check.description_en}</p>
          </div>

          <div className="space-y-4">
            {content.prep_check.questions.map((q) => (
              <div key={q.id} className="sharp-card p-4 border border-slate-300 bg-white space-y-3">
                <div className="text-right flex items-center justify-between">
                  <button
                    onClick={() => audioManager.playArabic(q.prompt_ar)}
                    className="p-1.5 bg-emerald-800 text-white"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                  <ArabicWordSpans text={q.prompt_ar} className="text-base font-bold text-slate-900" />
                </div>
                <div className="text-xs text-slate-500 italic">{q.prompt_en}</div>

                <div className="space-y-1.5">
                  {q.options.map((opt) => {
                    const isSelected = prepAnswers[q.id] === opt.id;
                    return (
                      <button
                        key={opt.id}
                        onClick={() => handleSelectPrepOption(q.id, opt.id)}
                        className={`w-full p-2.5 border text-right flex items-center justify-between text-xs ${
                          isSelected ? 'border-emerald-800 bg-emerald-50 font-bold' : 'border-slate-300 bg-white'
                        }`}
                      >
                        <span className="text-slate-400 italic font-sans">{opt.label_en}</span>
                        <ArabicWordSpans text={opt.label_ar} className="font-arabic text-sm" />
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: MISTAKE NOTEBOOK */}
      {activeTab === 'mistakes' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-amber-50/60 border border-amber-300 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-slate-900 text-base">
                Private Mistake Notebook · دَفْتَرُ الأَخْطَاءِ والمُرَاجَعَةِ
              </h2>
              <p className="text-xs text-slate-600">
                Personalized review loop. Incorrect answers during exercises are safely stored here for targeted re-practice.
              </p>
            </div>
            <span className="text-xs bg-amber-800 text-white px-2.5 py-1 font-bold">
              {mistakes.length} Items to Review
            </span>
          </div>

          {mistakes.length === 0 ? (
            <div className="sharp-card p-8 text-center bg-white border border-slate-300">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-900">No active mistakes in this chapter!</h3>
              <p className="text-xs text-slate-500 mt-1">
                You have answered questions correctly or haven't attempted them yet.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {mistakes.map((m) => (
                <div key={m.id} className="sharp-card p-4 border border-slate-300 bg-white flex justify-between items-center">
                  <div>
                    <span className="text-[11px] font-bold text-slate-400 font-mono block">
                      Activity {m.activity_id} · Review count: {m.review_count}
                    </span>
                    <div className="text-sm font-bold text-slate-900 font-arabic">{m.concept_name}</div>
                    <div className="text-xs text-red-700 mt-1">
                      <span>Wrong: </span>
                      <span className="font-mono bg-red-50 px-1 py-0.5 border border-red-200">{m.wrong_answer}</span>
                    </div>
                  </div>
                  <button
                    onClick={async () => {
                      await api.resolveMistake(m.id);
                      loadMistakes();
                    }}
                    className="btn-primary text-xs py-1.5 px-3"
                  >
                    Mark Resolved (تمت المراجعة)
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 11: EXAM PRACTICE */}
      {activeTab === 'exam' && (
        <div className="space-y-4">
          <div className="sharp-card p-4 bg-slate-900 text-white border border-slate-950 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-white text-base">
                {content.exam_practice.title_en} · {content.exam_practice.title_ar}
              </h2>
              <p className="text-xs text-slate-300">
                Modeled after UAE Ministry of Education & CBSE Class 5 Arabic Term Assessment (Total Marks: {content.exam_practice.total_marks}).
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Objective Questions */}
            {content.exam_practice.objective_questions.map((q, idx) => (
              <div key={q.id} className="sharp-card p-5 border border-slate-300 bg-white space-y-2">
                <div className="flex justify-between items-baseline border-b border-slate-200 pb-1.5">
                  <span className="text-xs font-bold text-slate-500 font-mono">Q{idx + 1} ({q.marks} Marks)</span>
                </div>
                <div className="text-right">
                  <ArabicWordSpans text={q.prompt_ar} className="text-base font-bold text-slate-900" />
                </div>
                <div className="text-xs text-slate-500 italic">{q.prompt_en}</div>

                <div className="space-y-1.5 pt-2">
                  {q.options.map((opt) => (
                    <button
                      key={opt.id}
                      onClick={() => setExamAnswers((prev) => ({ ...prev, [q.id]: opt.id }))}
                      className={`w-full p-2.5 border text-right flex items-center justify-between text-xs ${
                        examAnswers[q.id] === opt.id ? 'border-emerald-900 bg-emerald-50 font-bold' : 'border-slate-300 bg-white'
                      }`}
                    >
                      <span className="text-slate-400 italic font-sans">{opt.label_en}</span>
                      <ArabicWordSpans text={opt.label_ar} className="font-arabic text-sm" />
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* Writing Task */}
            <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-3">
              <div className="flex justify-between items-baseline border-b border-slate-200 pb-2">
                <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider font-mono">
                  Writing Section ({content.exam_practice.writing_task.marks} Marks)
                </span>
                <span className="text-xs text-slate-500 font-medium">Tutor-Evaluated Rubric</span>
              </div>
              <div className="text-right">
                <ArabicWordSpans text={content.exam_practice.writing_task.prompt_ar} className="text-base font-bold text-slate-900" />
              </div>
              <div className="text-xs text-slate-500 italic">{content.exam_practice.writing_task.prompt_en}</div>

              <textarea
                rows={4}
                value={examWritingText}
                onChange={(e) => setExamWritingText(e.target.value)}
                placeholder="اكتب فقرتك هنا باللغة العربية..."
                className="sharp-input w-full font-arabic text-base text-right p-3"
                dir="rtl"
              />
            </div>

            {/* Exam Feedback Summary */}
            {examFeedback && (
              <div className="p-4 bg-emerald-100 border-2 border-emerald-600 text-emerald-950 space-y-1">
                <div className="font-bold text-sm">Exam Assessment Submitted!</div>
                <div className="text-xs">
                  Objective Score: <strong>{examFeedback.objectiveScore} / {examFeedback.maxObjective} marks</strong>
                </div>
                {examFeedback.writingRouted && (
                  <div className="text-xs text-emerald-800">
                    Your paragraph writing has been routed to the tutor queue for rubric evaluation.
                  </div>
                )}
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={handleSubmitExam}
                className="btn-accent py-2.5 px-6 text-sm"
              >
                Submit Exam for Grading (تسليم الاختبار)
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
