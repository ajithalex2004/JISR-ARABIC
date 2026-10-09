import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { TextbookPdfUploader } from './TextbookPdfUploader';
import { BookOpen, CheckCircle2, Clock, Layers, Sparkles } from 'lucide-react';

export const CurriculumReview: React.FC = () => {
  const [lessons, setLessons] = useState<any[]>([]);
  const [grade, setGrade] = useState<number>(5);
  const [term, setTerm] = useState<number>(1);
  const [selected, setSelected] = useState<any>(null);

  const load = async () => {
    try {
      const data = await api.getCurriculumReview(term, grade);
      setLessons(data || []);
      if (data && data.length > 0) {
        setSelected(data[0]);
      } else {
        setSelected(null);
      }
    } catch (err) {
      console.error('Failed to load curriculum review:', err);
    }
  };

  useEffect(() => {
    load();
  }, [grade, term]);

  return (
    <div className="space-y-6">
      {/* 1. Integrated Textbook PDF Uploader Card */}
      <TextbookPdfUploader onUploadComplete={() => load()} />

      {/* 2. Review and Inspection Grid */}
      <div className="grid lg:grid-cols-[340px_1fr] gap-6">
        {/* Left Column: Chapters by Term */}
        <section className="sharp-card bg-white p-5 border border-slate-300 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-200 pb-3 gap-2">
            <div>
              <h2 className="font-black text-sm text-slate-900 uppercase tracking-wider">Curriculum Review</h2>
              <p className="text-[11px] text-slate-500">Chapters & OCR Pages</p>
            </div>
            <div className="flex items-center gap-1.5">
              <select
                value={grade}
                onChange={(e) => setGrade(Number(e.target.value))}
                className="sharp-input text-xs font-bold"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
                  <option key={g} value={g}>Grade {g}</option>
                ))}
              </select>
              <select
                value={term}
                onChange={(e) => setTerm(Number(e.target.value))}
                className="sharp-input text-xs font-bold"
              >
                <option value={1}>Term 1</option>
                <option value={2}>Term 2</option>
                <option value={3}>Term 3</option>
              </select>
            </div>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {lessons.map((l) => {
              const isSelected = selected?.id === l.id;
              const isPublished = l.status === 'published';
              return (
                <button
                  key={l.id}
                  onClick={() => setSelected(l)}
                  className={`w-full text-left p-3.5 border transition-all text-xs ${
                    isSelected
                      ? 'border-purple-800 bg-purple-50/50 shadow-xs'
                      : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-slate-500">Page {l.start_page}</span>
                    <span
                      className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                        isPublished ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {l.status}
                    </span>
                  </div>
                  <div className="font-bold text-sm text-slate-900 font-arabic text-right" dir="rtl">
                    {l.title_ar}
                  </div>
                  <div className="text-[11px] text-slate-600 mt-0.5">{l.title_en}</div>
                </button>
              );
            })}
          </div>
        </section>

        {/* Right Column: OCR Text & Page Inspection */}
        <section className="sharp-card bg-white p-6 border border-slate-300 min-h-[500px]">
          {selected ? (
            <div className="space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
                <div>
                  <div className="text-xl font-black text-slate-900 font-arabic" dir="rtl">
                    {selected.title_ar}
                  </div>
                  <div className="text-xs text-slate-600 font-medium mt-0.5">
                    {selected.title_en} · Start Page: {selected.start_page} · Status: <span className="font-bold uppercase text-purple-900">{selected.status}</span>
                  </div>
                </div>

                <button
                  onClick={async () => {
                    const newStatus = selected.status === 'published' ? 'content_pending' : 'published';
                    await api.updateCurriculumStatus(selected.id, newStatus);
                    await load();
                    setSelected({ ...selected, status: newStatus });
                  }}
                  className={`px-4 py-2 text-xs font-bold transition-all ${
                    selected.status === 'published'
                      ? 'bg-amber-100 text-amber-900 hover:bg-amber-200 border border-amber-300'
                      : 'bg-emerald-700 hover:bg-emerald-800 text-white'
                  }`}
                >
                  {selected.status === 'published' ? 'Unpublish (Return to Review)' : 'Approve & Publish Lesson'}
                </button>
              </div>

              {/* Scanned Pages List */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Textbook Pages & Transcribed Content ({selected.pages?.length || 0} pages)
                  </h3>
                  <a
                    href={`/api/admin/page-image/${selected.start_page}?edition_id=moe_gr${selected.grade || grade}_vol${selected.term || term}_2023`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-purple-700 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>View Scanned Page {selected.start_page}</span>
                  </a>
                </div>

                <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                  {selected.pages && selected.pages.length > 0 ? (
                    selected.pages.map((p: any) => (
                      <article key={p.pdf_page} className="p-4 border border-slate-200 bg-slate-50/50 space-y-2">
                        <div className="flex items-center justify-between text-xs border-b border-slate-200 pb-1.5">
                          <span className="font-mono font-bold text-slate-700">PDF Page {p.pdf_page}</span>
                          <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                            {p.review_status || 'indexed'}
                          </span>
                        </div>
                        <p dir="rtl" className="font-arabic text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
                          {p.ocr_text_ar || 'No OCR text extracted for this page.'}
                        </p>
                      </article>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 italic p-6 text-center border border-dashed border-slate-200">
                      No scanned pages indexed yet for this chapter range. Upload the textbook PDF above to generate page images and OCR.
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500 flex flex-col items-center justify-center py-20">
              <Layers className="w-10 h-10 text-slate-300 mb-2" />
              <span>Select a lesson from the left column to inspect its OCR pages and publication status.</span>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
