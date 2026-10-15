import React, { useState, useMemo, useEffect } from 'react';
import {
  GitFork, BookOpen, Sparkles, Volume2, Search,
  ChevronRight, ArrowDown, HelpCircle,
  Bookmark, GraduationCap, CheckCircle2,
  ExternalLink, Layers
} from 'lucide-react';
import { MINDMAP_CHAPTERS, CURRICULUM_RULES, MindmapChapter, getFallbackMindmapChapters } from '../../data/mindmapData';
import { audioManager } from '../../services/audio';
import { api } from '../../services/api';
import { User, ChildProfile } from '../../types';

interface MindmapsViewerProps {
  user?: User | null;
  activeChild?: ChildProfile | null;
  initialGrade?: number;
  onSelectGrade?: (grade: number) => void;
  onOpenAskFahim?: (query?: string) => void;
}

export const MindmapsViewer: React.FC<MindmapsViewerProps> = ({
  user,
  activeChild,
  initialGrade = 5,
  onSelectGrade,
  onOpenAskFahim
}) => {
  const availableGrades = useMemo(() => {
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  }, []);

  const [selectedGrade, setSelectedGrade] = useState<number>(() => {
    if (activeChild?.default_grade && user?.role !== 'admin') {
      return activeChild.default_grade;
    }
    return initialGrade || activeChild?.default_grade || 6;
  });

  const [chapters, setChapters] = useState<MindmapChapter[]>(() => getFallbackMindmapChapters(selectedGrade));
  const [activeTab, setActiveTab] = useState<'mindmap' | 'flowchart' | 'rules'>('mindmap');
  const [selectedChapterId, setSelectedChapterId] = useState<string>(() => {
    const initChapters = getFallbackMindmapChapters(selectedGrade);
    return initChapters[0]?.id || 'chapter_1';
  });
  const [langMode, setLangMode] = useState<'both' | 'ar' | 'en'>('both');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRuleKey, setSelectedRuleKey] = useState<string>('sentence_types');
  const [playingText, setPlayingText] = useState<string | null>(null);

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

  useEffect(() => {
    let isCancelled = false;
    const fetchMindmaps = async () => {
      // First immediately switch fallback chapters to prevent stale view
      const fallback = getFallbackMindmapChapters(selectedGrade);
      if (!isCancelled) {
        setChapters(fallback);
        setSelectedChapterId(fallback[0]?.id || 'chapter_1');
      }

      try {
        const res = await api.getMindmaps(selectedGrade, 1);
        if (!isCancelled && res.success && res.chapters && res.chapters.length > 0) {
          setChapters(res.chapters);
          setSelectedChapterId(res.chapters[0].id);
        }
      } catch (err) {
        if (!isCancelled) {
          setChapters(fallback);
          setSelectedChapterId(fallback[0]?.id || 'chapter_1');
        }
      }
    };
    fetchMindmaps();
    return () => { isCancelled = true; };
  }, [selectedGrade]);

  const activeChapter: MindmapChapter = useMemo(() => {
    return chapters.find(c => c.id === selectedChapterId) || chapters[0] || MINDMAP_CHAPTERS[0];
  }, [chapters, selectedChapterId]);

  const handleSpeak = (text: string) => {
    setPlayingText(text);
    audioManager.playArabic(text);
    setTimeout(() => setPlayingText(null), 2500);
  };

  // Filtered branches for search
  const filteredBranches = useMemo(() => {
    if (!searchQuery.trim()) return activeChapter.branches;
    const q = searchQuery.toLowerCase();
    return activeChapter.branches.map(branch => ({
      ...branch,
      items: branch.items.filter(item =>
        item.ar.toLowerCase().includes(q) ||
        item.en.toLowerCase().includes(q) ||
        (item.root && item.root.toLowerCase().includes(q)) ||
        (item.meaningAr && item.meaningAr.toLowerCase().includes(q)) ||
        (item.meaningEn && item.meaningEn.toLowerCase().includes(q))
      )
    })).filter(branch => branch.items.length > 0);
  }, [activeChapter, searchQuery]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6 pb-28">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#4f46e5] via-[#6366f1] to-[#8b5cf6] p-6 sm:p-8 text-white shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold text-white tracking-wide">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>دِرَاسَةٌ بَصَرِيَّةٌ تَفَاعُلِيَّةٌ • CBSE Curriculum Visual Learning</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight flex items-center gap-3">
              <GitFork className="w-8 h-8 text-amber-300 transform rotate-90" />
              <span>خرائط المفاهيم والتدفق الذهني</span>
            </h1>
            <p className="text-sm sm:text-base text-indigo-100 font-medium max-w-2xl leading-relaxed">
              Interactive concept mindmaps, syntax decision flowcharts & grammar rules tree specifically adapted for non-native Arabic learners.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 bg-black/20 backdrop-blur-md p-1.5 rounded-2xl border border-white/10 self-start md:self-auto">
            <button
              onClick={() => setLangMode('both')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                langMode === 'both' ? 'bg-white text-indigo-900 shadow' : 'text-white/80 hover:text-white'
              }`}
            >
              عربي + EN
            </button>
            <button
              onClick={() => setLangMode('ar')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                langMode === 'ar' ? 'bg-white text-indigo-900 shadow' : 'text-white/80 hover:text-white'
              }`}
            >
              عربي فقط
            </button>
            <button
              onClick={() => setLangMode('en')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                langMode === 'en' ? 'bg-white text-indigo-900 shadow' : 'text-white/80 hover:text-white'
              }`}
            >
              English Only
            </button>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Main Tabs Navigation */}
      <div className="bg-white rounded-2xl p-2 border border-slate-200/80 shadow-xs flex flex-wrap sm:flex-nowrap gap-1">
        <button
          onClick={() => setActiveTab('mindmap')}
          className={`flex-1 flex items-center justify-center gap-2.5 py-3 px-4 rounded-xl font-bold text-sm transition-all ${
            activeTab === 'mindmap'
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>خريطة مفاهيم الدرس (Lesson Mindmap)</span>
        </button>

        <button
          onClick={() => setActiveTab('flowchart')}
          className={`flex-1 flex items-center justify-center gap-2.5 py-3 px-4 rounded-xl font-bold text-sm transition-all ${
            activeTab === 'flowchart'
              ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <GitFork className="w-4 h-4 transform rotate-90" />
          <span>مخططات التدفق الإعرابي (Syntax Flowcharts)</span>
        </button>

        <button
          onClick={() => setActiveTab('rules')}
          className={`flex-1 flex items-center justify-center gap-2.5 py-3 px-4 rounded-xl font-bold text-sm transition-all ${
            activeTab === 'rules'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <Bookmark className="w-4 h-4" />
          <span>شجرة القواعد المنهجية (Curriculum Rules Tree)</span>
        </button>
      </div>

      {/* Grade Selector Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200/80 p-3 rounded-2xl shadow-xs">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
            <GraduationCap className="w-4 h-4 text-indigo-600" />
            <span>الصف الدراسي (Grade):</span>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            {availableGrades.map((g) => (
              <button
                key={g}
                onClick={() => {
                  setSelectedGrade(g);
                  onSelectGrade?.(g);
                }}
                className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                  selectedGrade === g
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                Grade {g} (الصف {g})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: LESSON CONCEPT MINDMAP                                              */}
      {/* ========================================================================= */}
      {activeTab === 'mindmap' && (
        <div className="space-y-6">
          {/* Chapter Selector Carousel / Pills */}
          <div className="bg-white rounded-3xl p-4 border border-slate-200/80 shadow-xs space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-indigo-600" />
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500">
                  فصول المنهاج (CBSE Curriculum Grade {selectedGrade} Term 1 Chapters)
                </h3>
              </div>
              {/* Search Bar */}
              <div className="relative w-48 sm:w-64">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="ابحث عن مفردة، جذر، قاعدة..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 text-slate-800"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
              {chapters.map((ch, idx) => {
                const isSelected = ch.id === selectedChapterId;
                return (
                  <button
                    key={ch.id}
                    onClick={() => setSelectedChapterId(ch.id)}
                    className={`shrink-0 flex items-center gap-2 px-3.5 py-2 rounded-2xl text-xs font-bold transition-all ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200/70'
                    }`}
                  >
                    <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px]">
                      {idx + 1}
                    </span>
                    <span>{ch.titleAr}</span>
                    <span className="text-[10px] opacity-80 hidden sm:inline">({ch.titleEn})</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Chapter Summary Banner */}
          <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-slate-50 rounded-3xl p-5 border border-indigo-100 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-extrabold">
                  {activeChapter.unitAr} • {activeChapter.unitEn}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-slate-200 text-slate-700 text-[11px] font-bold">
                  Pages {activeChapter.pages}
                </span>
              </div>
              <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
                <span>{activeChapter.titleAr}</span>
                <span className="text-slate-400 font-normal text-sm">/ {activeChapter.titleEn}</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-3xl">
                {langMode !== 'en' && <span className="font-semibold block">{activeChapter.summaryAr}</span>}
                {langMode !== 'ar' && <span className="text-slate-500 block">{activeChapter.summaryEn}</span>}
              </p>
            </div>

            <button
              onClick={() => onOpenAskFahim?.(`اشرح لي بالتفصيل درس "${activeChapter.titleAr}" وأبرز مهاراته وقواعده.`)}
              className="shrink-0 flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-2xl shadow transition-all"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>اسأل فهيم عن هذا الفصل</span>
            </button>
          </div>

          {/* Mindmap Concept Branches (Tree Grid) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredBranches.map((branch, bIdx) => (
              <div
                key={bIdx}
                className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div className="space-y-4">
                  {/* Branch Title Bar */}
                  <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
                    <div
                      className="w-10 h-10 rounded-2xl flex items-center justify-center text-white font-bold shadow-xs"
                      style={{ backgroundColor: branch.color }}
                    >
                      <Layers className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-black text-slate-900 text-base">
                        {branch.titleAr}
                      </h4>
                      <p className="text-xs text-slate-500 font-medium">
                        {branch.titleEn}
                      </p>
                    </div>
                  </div>

                  {/* Branch Items / Nodes */}
                  <div className="space-y-3">
                    {branch.items.map((item, iIdx) => (
                      <div
                        key={iIdx}
                        className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100/90 hover:bg-indigo-50/40 hover:border-indigo-200 transition-all space-y-2 group"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-0.5">
                            {langMode !== 'en' && (
                              <div className="text-sm font-black text-slate-900 flex items-center gap-2">
                                <span>{item.ar}</span>
                                <button
                                  onClick={() => handleSpeak(item.ar)}
                                  className={`p-1 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-white transition-all ${
                                    playingText === item.ar ? 'text-indigo-600 bg-indigo-100' : ''
                                  }`}
                                  title="استمع إلى النطق"
                                >
                                  <Volume2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            )}
                            {langMode !== 'ar' && (
                              <div className="text-xs font-semibold text-slate-600">
                                {item.en}
                              </div>
                            )}
                          </div>

                          {/* Root & Pattern Tags */}
                          {(item.root || item.pattern) && (
                            <div className="flex flex-col items-end gap-1">
                              {item.root && (
                                <span className="px-2 py-0.5 rounded-lg bg-blue-100 text-blue-700 text-[10px] font-extrabold">
                                  الجذر: {item.root}
                                </span>
                              )}
                              {item.pattern && (
                                <span className="px-2 py-0.5 rounded-lg bg-purple-100 text-purple-700 text-[10px] font-bold">
                                  الوزن: {item.pattern}
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Meanings / Descriptions */}
                        {(item.meaningAr || item.meaningEn) && (
                          <div className="pt-1 text-[11.5px] leading-relaxed border-t border-slate-200/60 space-y-1">
                            {langMode !== 'en' && item.meaningAr && (
                              <p className="text-slate-700 font-medium">{item.meaningAr}</p>
                            )}
                            {langMode !== 'ar' && item.meaningEn && (
                              <p className="text-slate-500 italic">{item.meaningEn}</p>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: SYNTAX DECISION FLOWCHARTS                                         */}
      {/* ========================================================================= */}
      {activeTab === 'flowchart' && (
        <div className="space-y-6">
          {/* Flowchart Header Banner */}
          <div className="bg-gradient-to-r from-purple-50 via-indigo-50 to-blue-50 rounded-3xl p-5 border border-purple-200 shadow-xs flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center shrink-0 shadow-md">
              <GitFork className="w-6 h-6 transform rotate-90" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-900">
                خوارزمية الإعراب وتحديد نوع الجملة (Syntax Parsing Decision Tree)
              </h3>
              <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
                Follow the algorithmic branches to parse any sentence accurately with complete English guidance, grammatical cases, and vowel endings.
              </p>
            </div>
          </div>

          {/* FLOWCHART 1: SENTENCE CLASSIFICATION */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-6">
            {/* Step 1 Node */}
            <div className="max-w-2xl mx-auto bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl p-4 shadow-md text-center space-y-1">
              <div className="inline-block px-2.5 py-0.5 rounded-full bg-white/20 text-[11px] font-black tracking-wide">
                الخطوة 1: فحص الكلمة الأولى (Step 1: Check 1st Word)
              </div>
              <h4 className="text-lg font-black">مَا نَوْعُ الكَلِمَةِ الَّتِي تَبْدَأُ بِهَا الجُمْلَةُ؟</h4>
              <p className="text-xs text-blue-100 max-w-lg mx-auto">
                انْظُرْ إِلَى الكَلِمَةِ الأُولَى: هَلْ تَقْبَلُ (أَلْـ) وَالتَّنْوِينَ (اسْمٌ)، أَمْ تَدُلُّ عَلَى حَدَثٍ وَزَمَنٍ (فِعْلٌ)؟
              </p>
            </div>

            {/* Split Indicator */}
            <div className="flex flex-col items-center">
              <ArrowDown className="w-5 h-5 text-indigo-400" />
              <span className="text-[11px] font-black uppercase text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200 mt-1">
                تفرع القرار (Decision Split)
              </span>
            </div>

            {/* Two Decision Branches (Nominal vs Verbal) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Branch A: Nominal Sentence */}
              <div className="bg-teal-50/60 border-2 border-teal-200 rounded-3xl p-5 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-teal-600 text-white flex items-center justify-center font-black">
                    A
                  </div>
                  <div>
                    <h5 className="font-black text-teal-950 text-base">
                      تَبْدَأُ بِاسْمٍ (الجُمْلَةُ الاسْمِيَّةُ)
                    </h5>
                    <p className="text-xs text-teal-700 font-semibold">
                      Starts with Noun (Nominal Sentence)
                    </p>
                  </div>
                </div>

                <div className="p-3 bg-white rounded-2xl border border-teal-100 text-xs text-teal-900 font-bold flex items-center justify-between">
                  <span>مِثَالٌ: الكُرَةُ مُسْتَدِيرَةٌ</span>
                  <button
                    onClick={() => handleSpeak('الكُرَةُ مُسْتَدِيرَةٌ')}
                    className="p-1 hover:text-teal-600"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Steps in Nominal */}
                <div className="space-y-3">
                  <div className="p-3 bg-white rounded-2xl border border-teal-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-black text-slate-900 text-xs">1. المُبْتَدَأُ (Subject Noun)</span>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                        مَرْفُوعٌ بِالضَّمَّةِ [ـُ]
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">الكُرَةُ: الاسْمُ الَّذِي نَبْدَأُ بِهِ الكَلامَ.</p>
                    <p className="text-slate-400 text-[11px] italic">Al-Kuratu: Starting noun introducing the subject.</p>
                  </div>

                  <div className="p-3 bg-white rounded-2xl border border-teal-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-black text-slate-900 text-xs">2. الخَبَرُ (The Predicate)</span>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                        مَرْفُوعٌ بِالضَّمَّةِ [ـٌ]
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">مُسْتَدِيرَةٌ: الكَلِمَةُ الَّتِي تُتَمِّمُ المَعْنَى مَعَ المُبْتَدَأ.</p>
                    <p className="text-slate-400 text-[11px] italic">Mustadeeratun: Tells what the subject is.</p>
                  </div>
                </div>
              </div>

              {/* Branch B: Verbal Sentence */}
              <div className="bg-orange-50/60 border-2 border-orange-200 rounded-3xl p-5 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-orange-600 text-white flex items-center justify-center font-black">
                    B
                  </div>
                  <div>
                    <h5 className="font-black text-orange-950 text-base">
                      تَبْدَأُ بِفِعْلٍ (الجُمْلَةُ الفِعْلِيَّةُ)
                    </h5>
                    <p className="text-xs text-orange-700 font-semibold">
                      Starts with Verb (Verbal Sentence)
                    </p>
                  </div>
                </div>

                <div className="p-3 bg-white rounded-2xl border border-orange-100 text-xs text-orange-900 font-bold flex items-center justify-between">
                  <span>مِثَالٌ: سَجَّلَ اللاعِبُ هَدَفًا</span>
                  <button
                    onClick={() => handleSpeak('سَجَّلَ اللاعِبُ هَدَفًا')}
                    className="p-1 hover:text-orange-600"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Steps in Verbal */}
                <div className="space-y-3">
                  <div className="p-3 bg-white rounded-2xl border border-orange-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-black text-slate-900 text-xs">1. الفِعْلُ (The Action Verb)</span>
                      <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 text-[10px] font-extrabold">
                        مَاضٍ / مُضَارِع / أَمْر
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">سَجَّلَ: فِعْلٌ مَاضٍ مَبْنِيٌّ عَلَى الفَتْحِ.</p>
                    <p className="text-slate-400 text-[11px] italic">Sajjala: Past tense verb ("scored").</p>
                  </div>

                  <div className="p-3 bg-white rounded-2xl border border-orange-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-black text-slate-900 text-xs">2. الفَاعِلُ (Subject Agent - Doer)</span>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                        مَرْفُوعٌ بِالضَّمَّةِ [ـُ]
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">اللاَّعِبُ: هُوَ مَنْ قَامَ بِتَسْجِيلِ الهَدَفِ.</p>
                    <p className="text-slate-400 text-[11px] italic">Al-La'ibu: Answers "Who did it?" (The player).</p>
                  </div>

                  <div className="p-3 bg-white rounded-2xl border border-orange-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-black text-slate-900 text-xs">3. المَفْعُولُ بِهِ (Direct Object)</span>
                      <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-extrabold">
                        مَنْصُوبٌ بِالفَتْحَةِ [ـًا]
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs">هَدَفًا: الشَّيْءُ الَّذِي وَقَعَ عَلَيْهِ الفِعْلُ.</p>
                    <p className="text-slate-400 text-[11px] italic">Hadafan: Answers "What was acted upon?" (A goal).</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* FLOWCHART 2: PREPOSITIONS & GENITIVE CASE */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-purple-600 text-white flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h4 className="font-black text-slate-900 text-base">
                  مُخَطَّطُ حُرُوفِ الجَرِّ وَالاسْمِ المَجْرُورِ (Prepositions & Genitive Case)
                </h4>
                <p className="text-xs text-slate-500">
                  إِذَا سُبِقَتِ الكَلِمَةُ بِأَحَدِ حُرُوفِ الجَرِّ: (مِنْ، إِلَى، عَنْ، عَلَى، فِي، البَاء [بـ]، الكَاف [كـ]، اللام [لـ])
                </p>
              </div>
            </div>

            <div className="bg-purple-50/70 border border-purple-200 rounded-2xl p-4 space-y-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-purple-600" />
                <span className="font-black text-purple-950 text-sm">
                  القَاعِدَةُ الحَتْمِيَّةُ: اسْمٌ مَجْرُورٌ بِالكَسْرَةِ الظَّاهِرَةِ [ـِ] (Genitive Case with Kasra)
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="bg-white p-3 rounded-xl border border-purple-100 space-y-1">
                  <div className="font-black text-slate-900 flex items-center justify-between">
                    <span>فِي المَلْعَبِ</span>
                    <button onClick={() => handleSpeak('فِي المَلْعَبِ')} className="hover:text-purple-600">
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-slate-600">فِي (حَرْفُ جَرٍّ) + المَلْعَبِ (اسْمٌ مَجْرُورٌ بِالكَسْرَةِ).</p>
                  <p className="text-slate-400 italic">"Fi" (Prep) + "Al-Mal'abi" (Genitive with Kasra) = On the pitch.</p>
                </div>

                <div className="bg-white p-3 rounded-xl border border-purple-100 space-y-1">
                  <div className="font-black text-slate-900 flex items-center justify-between">
                    <span>بِالمَضْرِبِ</span>
                    <button onClick={() => handleSpeak('بِالمَضْرِبِ')} className="hover:text-purple-600">
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-slate-600">البَاءُ (حَرْفُ جَرٍّ) + المَضْرِبِ (اسْمٌ مَجْرُورٌ بِالكَسْرَةِ).</p>
                  <p className="text-slate-400 italic">"Bi" (Prep) + "Al-Madribi" (Genitive with Kasra) = With the racket.</p>
                </div>
              </div>
            </div>
          </div>

          {/* FLOWCHART 3: THE CANCELLERS (KANA VS INNA) */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h4 className="font-black text-slate-900 text-base">
                  مُخَطَّطُ النَّوَاسِخِ: كَانَ وَأَخَوَاتُهَا مُقَابِلَ إِنَّ وَأَخَوَاتُهَا (The Modifiers / Nawasikh)
                </h4>
                <p className="text-xs text-slate-500">
                  How "Kana" (Verbs of Being) vs "Inna" (Particles of Emphasis) transform the Nominal Sentence.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Kana */}
              <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-black text-blue-900 text-sm">كَانَ وَأَخَوَاتُهَا (أَفْعَالٌ نَاسِخَةٌ)</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-200 text-blue-800 rounded-md">
                    تَرْفَعُ ثُمَّ تَنْصِبُ
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  تَرْفَعُ المُبْتَدَأَ (اسْمُ كَانَ) مَرْفُوع [ـُ]، وَتَنْصِبُ الخَبَرَ (خَبَرُ كَانَ) مَنْصُوب [ـَ].
                </p>
                <div className="p-2.5 bg-white rounded-xl border border-blue-100 text-xs font-bold text-slate-800 flex items-center justify-between">
                  <span>كَانَتِ الكُرَةُ <span className="text-amber-600 underline">سَرِيعَةً</span></span>
                  <button onClick={() => handleSpeak('كَانَتِ الكُرَةُ سَرِيعَةً')} className="hover:text-blue-600">
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Inna */}
              <div className="p-4 rounded-2xl bg-rose-50/50 border border-rose-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-black text-rose-900 text-sm">إِنَّ وَأَخَوَاتُهَا (حُرُوفٌ نَاسِخَةٌ)</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 bg-rose-200 text-rose-800 rounded-md">
                    تَنْصِبُ ثُمَّ تَرْفَعُ
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  تَنْصِبُ المُبْتَدَأَ (اسْمُ إِنَّ) مَنْصُوب [ـَ]، وَتَرْفَعُ الخَبَرَ (خَبَرُ إِنَّ) مَرْفُوع [ـُ].
                </p>
                <div className="p-2.5 bg-white rounded-xl border border-rose-100 text-xs font-bold text-slate-800 flex items-center justify-between">
                  <span>إِنَّ <span className="text-rose-600 underline">الكُرَةَ</span> سَرِيعَةٌ</span>
                  <button onClick={() => handleSpeak('إِنَّ الكُرَةَ سَرِيعَةٌ')} className="hover:text-rose-600">
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: CURRICULUM RULES TREE                                              */}
      {/* ========================================================================= */}
      {activeTab === 'rules' && (
        <div className="space-y-6">
          {/* Rules Header */}
          <div className="bg-gradient-to-r from-teal-50 via-emerald-50 to-slate-50 rounded-3xl p-5 border border-teal-200 shadow-xs flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-teal-600 text-white flex items-center justify-center font-bold">
                <Bookmark className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-black text-slate-900">
                  شجرة القواعد النحوية الشاملة (Comprehensive Grammar Rules Tree)
                </h3>
                <p className="text-xs text-slate-600">
                  Curriculum syntax formulas with parsed mathematical structures, example sentences, and English translations.
                </p>
              </div>
            </div>
          </div>

          {/* Rules Accordion / Cards List */}
          <div className="space-y-4">
            {CURRICULUM_RULES.map((rule) => {
              const isSelected = selectedRuleKey === rule.key;
              return (
                <div
                  key={rule.key}
                  className={`bg-white rounded-3xl border transition-all overflow-hidden ${
                    isSelected ? 'border-teal-400 shadow-md ring-2 ring-teal-400/20' : 'border-slate-200/80 shadow-xs'
                  }`}
                >
                  {/* Rule Header Bar */}
                  <div
                    onClick={() => setSelectedRuleKey(isSelected ? '' : rule.key)}
                    className="p-5 flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="px-2.5 py-1 rounded-xl bg-teal-100 text-teal-800 text-xs font-black">
                        {rule.badgeAr}
                      </span>
                      <div>
                        <h4 className="text-base font-black text-slate-900">
                          {rule.titleAr}
                        </h4>
                        <p className="text-xs text-slate-500 font-semibold">
                          {rule.titleEn}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <ChevronRight
                        className={`w-5 h-5 text-slate-400 transition-transform ${
                          isSelected ? 'transform rotate-90 text-teal-600' : ''
                        }`}
                      />
                    </div>
                  </div>

                  {/* Expanded Content */}
                  {isSelected && (
                    <div className="px-5 pb-5 pt-2 border-t border-slate-100 space-y-4">
                      {/* Mathematical Syntax Formula */}
                      <div className="p-3.5 rounded-2xl bg-teal-50 border border-teal-200/70 space-y-1">
                        <div className="text-[11px] font-extrabold uppercase text-teal-800">
                          المُعَادَلَةُ النَّحْوِيَّةُ (Grammar Syntax Formula)
                        </div>
                        <div className="text-sm font-black text-teal-950 font-mono">
                          {rule.formulaAr}
                        </div>
                        <div className="text-xs text-teal-700 italic">
                          {rule.formulaEn}
                        </div>
                      </div>

                      {/* Rule Explanations */}
                      <div className="space-y-1.5 text-xs sm:text-sm leading-relaxed">
                        <p className="text-slate-800 font-bold">{rule.ruleAr}</p>
                        <p className="text-slate-600">{rule.ruleEn}</p>
                      </div>

                      {/* Parsed Examples Table */}
                      <div className="space-y-2 pt-2">
                        <h5 className="text-xs font-extrabold uppercase text-slate-500 tracking-wider">
                          شَوَاهِدُ إِعْرَابِيَّةٌ مُفَصَّلَةٌ (Parsed Sentence Examples)
                        </h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {rule.examples.map((ex, eIdx) => (
                            <div
                              key={eIdx}
                              className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2"
                            >
                              <div className="flex items-center justify-between pb-1.5 border-b border-slate-200/60">
                                <div>
                                  <span className="text-sm font-black text-slate-900 block">
                                    {ex.sentenceAr}
                                  </span>
                                  <span className="text-xs text-slate-500 italic">
                                    {ex.sentenceEn}
                                  </span>
                                </div>
                                <button
                                  onClick={() => handleSpeak(ex.sentenceAr)}
                                  className="p-1.5 rounded-xl text-slate-400 hover:text-teal-600 hover:bg-white transition-all"
                                  title="استمع إلى الجملة"
                                >
                                  <Volume2 className="w-4 h-4" />
                                </button>
                              </div>

                              <div className="text-xs space-y-1">
                                <p className="text-slate-700 font-bold leading-relaxed">{ex.analysisAr}</p>
                                <p className="text-slate-500 text-[11px] leading-relaxed italic">{ex.analysisEn}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Fahim Assistant Button */}
                      <div className="pt-2 flex justify-end">
                        <button
                          onClick={() => onOpenAskFahim?.(`أريد تدريبات إضافية وشرحاً مبسطاً لقاعدة: "${rule.titleAr}" (${rule.titleEn}).`)}
                          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-teal-50 hover:text-teal-700 text-slate-700 text-xs font-bold rounded-xl transition-all"
                        >
                          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                          <span>تدرب على هذه القاعدة مع فهيم (Practice with Fahim)</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
