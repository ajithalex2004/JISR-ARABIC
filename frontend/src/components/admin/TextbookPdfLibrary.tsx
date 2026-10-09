import React, { useState, useEffect } from 'react';
import {
  BookOpen, Layers, CheckCircle2, ChevronRight, ChevronLeft,
  Search, Eye, FileText, Volume2, Maximize2, RefreshCw, ZoomIn
} from 'lucide-react';
import { audioManager } from '../../services/audio';
import { API_BASE } from '../../services/api';

interface TextbookBook {
  id: string;
  title: string;
  grade: number;
  term: number;
  academic_year: string;
  total_pages: number;
  scanned_pages_count: number;
  rendered_images_count: number;
  is_complete: boolean;
  pdf_filename: string;
}

interface PageData {
  pdf_page: number;
  printed_page: number;
  ocr_text_ar: string;
  translation_en?: string;
  confidence: number;
  review_status: string;
  image_url: string;
}

export const TextbookPdfLibrary: React.FC = () => {
  const [selectedGrade, setSelectedGrade] = useState<number>(1);
  const [selectedTerm, setSelectedTerm] = useState<number>(1);
  const [books, setBooks] = useState<TextbookBook[]>([]);
  const [pages, setPages] = useState<PageData[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
  const [viewMode, setViewMode] = useState<'inspector' | 'gallery'>('inspector');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [isZoomed, setIsZoomed] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const currentEditionId = `moe_gr${selectedGrade}_vol${selectedTerm}_2023`;

  // 1. Fetch full library catalog
  useEffect(() => {
    const fetchLibrary = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/admin/textbook-library`);
        if (res.ok) {
          const data = await res.json();
          setBooks(data || []);
        }
      } catch (err) {
        console.error('Failed to load textbook library:', err);
      }
    };
    fetchLibrary();
  }, []);

  // 2. Fetch pages for selected edition
  useEffect(() => {
    const fetchPages = async () => {
      setIsLoading(true);
      setErrorMsg('');
      try {
        const res = await fetch(`${API_BASE}/api/admin/textbook-pages/${currentEditionId}`);
        if (res.ok) {
          const data: PageData[] = await res.json();
          setPages(data || []);
          setCurrentPageIndex(0);
        } else {
          setPages([]);
          setErrorMsg('No indexed pages found for this book edition.');
        }
      } catch (err: any) {
        setErrorMsg('Error loading textbook pages: ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPages();
  }, [currentEditionId]);

  const activeBook = books.find((b) => b.grade === selectedGrade && b.term === selectedTerm) || {
    id: currentEditionId,
    title: `اللغة العربية - الصف ${selectedGrade} - الجزء ${selectedTerm}`,
    grade: selectedGrade,
    term: selectedTerm,
    academic_year: '2023–2024',
    total_pages: pages.length || 100,
    scanned_pages_count: pages.length,
    rendered_images_count: pages.length,
    is_complete: true,
    pdf_filename: `Grade${selectedGrade}_Vol${selectedTerm}.pdf`
  };

  const currentPage = pages[currentPageIndex] || {
    pdf_page: 1,
    printed_page: 1,
    ocr_text_ar: 'قيد التحميل...',
    confidence: 0.95,
    review_status: 'verified',
    image_url: `/api/admin/page-image/1?edition_id=${currentEditionId}`
  };

  const [activeTranslation, setActiveTranslation] = useState<string>('');

  useEffect(() => {
    if (!currentPage) return;
    if (currentPage.translation_en) {
      setActiveTranslation(currentPage.translation_en);
      return;
    }
    fetch(`${API_BASE}/api/admin/ocr-page/${currentPage.pdf_page}?edition_id=${currentEditionId}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.paragraphs_en && data.paragraphs_en.length > 0) {
          setActiveTranslation(data.paragraphs_en.join('\n\n'));
        } else {
          setActiveTranslation('English translation under editorial review.');
        }
      })
      .catch(() => {
        setActiveTranslation('English translation under editorial review.');
      });
  }, [currentPage?.pdf_page, currentEditionId]);

  const filteredPages = searchQuery.trim()
    ? pages.filter((p) =>
        p.ocr_text_ar.toLowerCase().includes(searchQuery.trim().toLowerCase()) ||
        String(p.pdf_page) === searchQuery.trim() ||
        String(p.printed_page) === searchQuery.trim()
      )
    : pages;

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="sharp-card p-5 border-2 border-slate-900 bg-white space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <h2 className="text-base font-black text-slate-900 uppercase tracking-wider">
                مكتبة كتب الوزارة وصفحات الـ PDF التفاعلية (Textbook PDF Library)
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              تصفح وفحص كافة صفحات كتب وزارة التربية والتعليم الرسمية لجميع الصفوف (1 إلى 10) والفصول الثلاثة، بدقة 2x مع نصوص الـ OCR المقابلة.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <button
              onClick={() => setViewMode('inspector')}
              className={`px-3 py-1.5 text-xs font-bold border transition-all ${
                viewMode === 'inspector'
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
              }`}
            >
              الفاحص المزدوج (Inspector)
            </button>
            <button
              onClick={() => setViewMode('gallery')}
              className={`px-3 py-1.5 text-xs font-bold border transition-all ${
                viewMode === 'gallery'
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
              }`}
            >
              معرض الصفحات (Thumbnails)
            </button>
          </div>
        </div>

        {/* 1. Grade Selector Pills (Grades 1 to 10) */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block">
            المرحلة الدراسية (Select Grade Level):
          </label>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((g) => {
              const isSelected = selectedGrade === g;
              return (
                <button
                  key={g}
                  onClick={() => setSelectedGrade(g)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all border shrink-0 flex items-center gap-1.5 cursor-pointer ${
                    isSelected
                      ? 'bg-purple-900 text-white border-purple-900 shadow-xs'
                      : 'bg-white text-slate-700 border-slate-200 hover:border-slate-400 hover:bg-slate-50'
                  }`}
                >
                  <span>Grade {g}</span>
                  <span className="font-arabic text-[11px] opacity-80">(الصف {g})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. Term Selector Tabs */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block">
            الفصل الدراسي (Select Term / Volume):
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { t: 1, labelEn: 'Term 1 / Vol 1', labelAr: 'الفصل الدراسي الأول' },
              { t: 2, labelEn: 'Term 2 / Vol 2', labelAr: 'الفصل الدراسي الثاني' },
              { t: 3, labelEn: 'Term 3 / Vol 3', labelAr: 'الفصل الدراسي الثالث' }
            ].map((item) => {
              const isSelected = selectedTerm === item.t;
              return (
                <button
                  key={item.t}
                  onClick={() => setSelectedTerm(item.t)}
                  className={`py-2 px-3 text-xs font-bold transition-all border text-center rounded-xl cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                      : 'bg-white text-slate-700 border-slate-200 hover:border-slate-400 hover:bg-slate-50'
                  }`}
                >
                  <div className="font-bold">{item.labelEn}</div>
                  <div className="text-[11px] font-arabic opacity-80 mt-0.5">{item.labelAr}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. Active Book Telemetry Ribbon */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 border border-slate-200 rounded-xl text-xs font-mono">
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Edition ID</span>
            <span className="font-bold text-slate-800">{activeBook.id}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Total Book Pages</span>
            <span className="font-bold text-slate-800">{pages.length || activeBook.total_pages} Pages</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">OCR Indexed</span>
            <span className="font-bold text-emerald-700 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{pages.length} Pages (100%)</span>
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">2x PNG Images</span>
            <span className="font-bold text-purple-700 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" />
              <span>{pages.length} Ready</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <div className="sharp-card p-12 bg-white border border-slate-300 flex flex-col items-center justify-center space-y-3 text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin text-purple-700" />
          <span className="text-sm font-bold">جاري تحميل صفحات كتاب الصف {selectedGrade} (الفصل {selectedTerm})...</span>
        </div>
      ) : errorMsg ? (
        <div className="sharp-card p-8 bg-amber-50 border border-amber-300 text-amber-900 text-center space-y-2">
          <p className="text-sm font-bold">{errorMsg}</p>
          <p className="text-xs text-amber-700">تأكد من فهرسة الكتاب أو تشغيل خادم الواجهة الخلفية.</p>
        </div>
      ) : viewMode === 'gallery' ? (
        /* THUMBNAIL GALLERY VIEW */
        <div className="sharp-card p-5 bg-white border border-slate-300 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black text-slate-900 uppercase">
                جميع صفحات الكتاب ({pages.length} صفحة)
              </h3>
            </div>
            <div className="relative max-w-xs w-full">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="بحث برقم الصفحة أو النص العربي..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="sharp-input w-full pl-8 text-xs font-arabic"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3 max-h-[650px] overflow-y-auto p-1">
            {filteredPages.map((p, idx) => {
              const actualIdx = pages.findIndex((x) => x.pdf_page === p.pdf_page);
              return (
                <div
                  key={p.pdf_page}
                  onClick={() => {
                    setCurrentPageIndex(actualIdx >= 0 ? actualIdx : 0);
                    setViewMode('inspector');
                  }}
                  className="group border border-slate-200 hover:border-purple-600 bg-white rounded-lg p-2 space-y-1.5 cursor-pointer transition-all shadow-2xs hover:shadow-md"
                >
                  <div className="aspect-[3/4] bg-slate-100 rounded-sm overflow-hidden flex items-center justify-center relative">
                    <img
                      src={p.image_url?.startsWith('http') ? p.image_url : `${API_BASE}${p.image_url}`}
                      alt={`Page ${p.pdf_page}`}
                      loading="lazy"
                      className="w-full h-full object-contain group-hover:scale-105 transition-transform"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.onerror = null;
                        target.src = `${API_BASE}/api/admin/page-image/${p.pdf_page}?edition_id=${currentEditionId}`;
                      }}
                    />
                    <span className="absolute bottom-1 right-1 bg-slate-900/80 text-white text-[9px] font-mono font-bold px-1.5 py-0.5 rounded">
                      p. {p.pdf_page}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-600 font-arabic truncate text-right" dir="rtl">
                    {p.ocr_text_ar.slice(0, 30) || 'صفحة كتاب الوزارة'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* SPLIT PAGE INSPECTOR VIEW */
        <div className="grid lg:grid-cols-12 gap-6">
          {/* Left Column: High-Res Scanned Page Image (7 cols) */}
          <div className="lg:col-span-7 sharp-card bg-white p-5 border-2 border-slate-900 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-700" />
                <h3 className="text-sm font-black text-slate-900">
                  الصفحة الأصلية المصورة (High-Res 2x PNG)
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-purple-900 bg-purple-50 px-2.5 py-1 border border-purple-200 rounded">
                  Page {currentPage.pdf_page} of {pages.length}
                </span>
                <button
                  onClick={() => setIsZoomed(!isZoomed)}
                  className="p-1.5 border border-slate-300 rounded hover:bg-slate-100 text-slate-600"
                  title="Toggle Full Zoom"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Page Image Display */}
            <div className="bg-slate-100 border border-slate-200 rounded-lg p-2 flex items-center justify-center min-h-[580px] max-h-[750px] overflow-auto">
              <img
                src={currentPage.image_url?.startsWith('http') ? currentPage.image_url : `${API_BASE}${currentPage.image_url}`}
                alt={`Grade ${selectedGrade} Term ${selectedTerm} Page ${currentPage.pdf_page}`}
                className={`max-w-full h-auto object-contain transition-all shadow-md rounded ${
                  isZoomed ? 'scale-125 origin-top' : ''
                }`}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.onerror = null;
                  target.src = `${API_BASE}/api/admin/page-image/${currentPage.pdf_page}?edition_id=${currentEditionId}`;
                }}
              />
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-200">
              <button
                onClick={() => setCurrentPageIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentPageIndex <= 0}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1 cursor-pointer"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>الصفحة السابقة (Previous)</span>
              </button>

              <div className="flex items-center gap-1.5 text-xs font-mono">
                <span>انتقال إلى صفحة:</span>
                <input
                  type="number"
                  min={1}
                  max={pages.length}
                  value={currentPage.pdf_page}
                  onChange={(e) => {
                    const pageNum = parseInt(e.target.value, 10);
                    if (pageNum >= 1 && pageNum <= pages.length) {
                      const idx = pages.findIndex((p) => p.pdf_page === pageNum);
                      if (idx >= 0) setCurrentPageIndex(idx);
                    }
                  }}
                  className="w-14 px-2 py-1 border border-slate-300 rounded text-center text-xs font-bold"
                />
                <span className="text-slate-400">/ {pages.length}</span>
              </div>

              <button
                onClick={() => setCurrentPageIndex((prev) => Math.min(pages.length - 1, prev + 1))}
                disabled={currentPageIndex >= pages.length - 1}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1 cursor-pointer"
              >
                <span>الصفحة التالية (Next)</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Right Column: OCR Text & Transcription Analysis (5 cols) */}
          <div className="lg:col-span-5 sharp-card bg-white p-5 border-2 border-slate-900 space-y-4 flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-emerald-700" />
                <h3 className="text-sm font-black text-slate-900">
                  النص العربي المفهرس (Extracted OCR Text)
                </h3>
              </div>
              <button
                onClick={() => audioManager.playArabic(currentPage.ocr_text_ar)}
                className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-300 rounded text-[11px] font-bold flex items-center gap-1 hover:bg-emerald-100 cursor-pointer"
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>استمع للنص (Listen)</span>
              </button>
            </div>

            {/* OCR Text Box */}
            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-lg p-4 overflow-y-auto max-h-[320px] space-y-3">
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono border-b border-slate-200 pb-1.5">
                <span>Printed Page: {currentPage.printed_page}</span>
                <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">
                  دقة النص: {(currentPage.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div
                dir="rtl"
                className="font-arabic text-sm text-slate-800 leading-loose whitespace-pre-wrap text-right select-text"
              >
                {currentPage.ocr_text_ar || 'لا يوجد نص مستخرج لهذه الصفحة (صفحة غلاف أو رسوم بيانية).'}
              </div>
            </div>

            {/* English Translation Box */}
            <div className="bg-emerald-50/60 border border-emerald-200 rounded-lg p-3.5 overflow-y-auto max-h-[240px] space-y-2">
              <div className="flex items-center justify-between text-[11px] font-bold text-emerald-900 border-b border-emerald-200 pb-1">
                <span>الترجمة الإنجليزية المعتمدة (English Translation)</span>
                <span className="text-[10px] font-mono text-emerald-700">Page {currentPage.printed_page}</span>
              </div>
              <div
                dir="ltr"
                className="text-xs text-slate-700 font-sans leading-relaxed whitespace-pre-wrap text-left select-text"
              >
                {activeTranslation || currentPage.translation_en || 'English translation under editorial review.'}
              </div>
            </div>

            {/* Quick Actions Footer */}
            <div className="pt-3 border-t border-slate-200 flex items-center justify-between text-xs">
              <span className="text-slate-500">
                {currentPage.ocr_text_ar.split(/\s+/).filter(Boolean).length} كلمة عربية
              </span>
              <div className="flex items-center gap-2">
                {(activeTranslation || currentPage.translation_en) && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(activeTranslation || currentPage.translation_en || '');
                      alert('تم نسخ الترجمة الإنجليزية إلى الحافظة.');
                    }}
                    className="text-emerald-800 hover:underline font-bold text-[11px]"
                  >
                    نسخ الترجمة (Copy English)
                  </button>
                )}
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(currentPage.ocr_text_ar);
                    alert('تم نسخ النص العربي إلى الحافظة.');
                  }}
                  className="text-purple-700 hover:underline font-bold text-[11px]"
                >
                  نسخ العربي (Copy Arabic)
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
