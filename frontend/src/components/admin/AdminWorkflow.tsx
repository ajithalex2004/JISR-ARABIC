import React, { useState, useEffect } from 'react';
import { Settings, Plus, Upload, CheckCircle2, AlertTriangle, FileCode, Layers } from 'lucide-react';
import { api } from '../../services/api';
import { TutorAssignments } from './TutorAssignments';
import { CurriculumReview } from './CurriculumReview';
import { TextbookPdfUploader } from './TextbookPdfUploader';
import { TextbookPdfLibrary } from './TextbookPdfLibrary';

type AdminMode = 'PDF_LIBRARY' | 'UPLOAD_PDF' | 'CURRICULUM_REVIEW' | 'ADD_TERM' | 'ADD_CLASS' | 'ADD_LESSON' | 'UPDATE_EDITION' | 'COVERAGE' | 'QUALITY';

export const AdminWorkflow: React.FC = () => {
  const [activeMode, setActiveMode] = useState<AdminMode>('PDF_LIBRARY');
  const [coverage, setCoverage] = useState<any>(null);
  const [quality, setQuality] = useState<any>(null);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [successMsg, setSuccessMsg] = useState<string>('');

  // ADD_TERM form
  const [termGrade, setTermGrade] = useState<number>(5);
  const [termNumber, setTermNumber] = useState<number>(2);
  const [termTitleAr, setTermTitleAr] = useState<string>('الفصل الدراسي الثاني');
  const [termTitleEn, setTermTitleEn] = useState<string>('Term 2');
  const [termPrice, setTermPrice] = useState<number>(33.0);

  // ADD_CLASS form
  const [classNumber, setClassNumber] = useState<number>(6);
  const [classNameAr, setClassNameAr] = useState<string>('الصف السادس');
  const [classNameEn, setClassNameEn] = useState<string>('Class 6');

  // ADD_LESSON form
  const [lessonPackageJson, setLessonPackageJson] = useState<string>(
    JSON.stringify(
      {
        lesson_id: 'lesson_02_horse_riding',
        version: '0.1.0',
        title_ar: 'ركوب الخيل',
        title_en: 'Horse Riding',
        unit_id: 'unit_01_sports',
        grade: 5,
        term: 1,
        start_page: 16,
        is_first_chapter_demo: false,
        prep_check: {
          title_ar: 'اختبار الاستعداد',
          title_en: 'Preparation Check',
          description_en: 'Horse riding prerequisites',
          questions: []
        },
        learning_paths: {
          foundation: { title_ar: 'المسار التأسيسي', title_en: 'Foundation', pacing: 'Step-by-step', target: 'Basic vocabulary' },
          guided: { title_ar: 'المسار الموجه', title_en: 'Guided', pacing: 'Guided', target: 'Sentence construction' },
          independent: { title_ar: 'المسار المستقل', title_en: 'Independent', pacing: 'Full immersion', target: 'Fluency' }
        },
        instruction_decoder: [],
        vocabulary_cards: [],
        grammar_lab: { title_ar: 'القواعد', title_en: 'Grammar', sections: [] },
        sentence_builder: { title_ar: 'باني الجمل', title_en: 'Sentence Builder', challenges: [] },
        listen_speak_studio: { title_ar: 'أستمع وأتحدث', title_en: 'Studio', passage_ar: '', passage_en: '', audio_scripts: [] },
        practice_activities: [],
        speaking_mission: { title_ar: 'المهمة', title_en: 'Mission', scenario_en: '', prompts_ar: [], recording_task_en: '' },
        parent_companion: { title_ar: 'بطاقة ولي الأمر', title_en: 'Parent Card', summary_en: '', dinner_table_prompts: [], home_practice_checklist: [] },
        tutor_handover: { title_ar: 'بطاقة المعلم', title_en: 'Tutor Card', learner_focus: 'CBSE 5', unobserved_fields_note: '', rubric_categories: [] },
        exam_practice: { title_ar: 'الاختبار', title_en: 'Exam', total_marks: 10, objective_questions: [], writing_task: { id: 'w1', prompt_ar: '', prompt_en: '', marks: 4 } },
        spaced_recall: { title_ar: 'التذكر', title_en: 'Spaced Recall', linked_concepts: [] }
      },
      null,
      2
    )
  );

  // UPDATE_EDITION form
  const [editionId, setEditionId] = useState<string>('moe_gr5_vol1_2024');
  const [editionTitle, setEditionTitle] = useState<string>('العربية تجمعنا - المستوى الخامس - طبعة 2024–2025');
  const [academicYear, setAcademicYear] = useState<string>('2024–2025');
  const [pubYear, setPubYear] = useState<string>('2024–2025');

  useEffect(() => {
    loadCoverage();
  }, []);

  const loadCoverage = async () => {
    try {
      const res = await api.getCoverageReport();
      setCoverage(res);
    } catch (e) {
      console.error(e);
    }
  };
  const loadQuality = async () => {
    try { setQuality(await api.getQualityReport()); } catch (e: any) { setActionLog(prev => [...prev, e.message]); }
  };

  const handleAddTerm = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.adminAddTerm({
        grade: termGrade,
        term: termNumber,
        title_ar: termTitleAr,
        title_en: termTitleEn,
        price_usd: termPrice
      });
      setSuccessMsg(res.message);
      setActionLog((prev) => [`[${new Date().toLocaleTimeString()}] ADD_TERM: ${res.message}`, ...prev]);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleAddClass = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.adminAddClass({
        grade_number: classNumber,
        name_ar: classNameAr,
        name_en: classNameEn
      });
      setSuccessMsg(res.message);
      setActionLog((prev) => [`[${new Date().toLocaleTimeString()}] ADD_CLASS: ${res.message}`, ...prev]);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleAddLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(lessonPackageJson);
      const res = await api.adminAddLesson({
        unit_id: parsed.unit_id || 'unit_01_sports',
        grade: parsed.grade || 5,
        term: parsed.term || 1,
        lesson_order: 2,
        title_ar: parsed.title_ar,
        title_en: parsed.title_en,
        start_page: parsed.start_page || 16,
        content_json: parsed
      });
      setSuccessMsg(res.message);
      setActionLog((prev) => [`[${new Date().toLocaleTimeString()}] ADD_LESSON: ${res.message}`, ...prev]);
    } catch (err: any) {
      alert('Invalid JSON schema: ' + err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <TutorAssignments />
      {/* Top Banner */}
      <div className="sharp-card p-5 border-l-4 border-l-slate-900 bg-white flex justify-between items-center">
        <div>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Curriculum Scaling & Edition Ingestion Engine
          </span>
          <h1 className="text-xl font-black text-slate-900">
            Fahim Content & Expansion Administration
          </h1>
        </div>
      </div>

      {/* Mode Tabs */}
      <div className="flex border-b-2 border-slate-900 overflow-x-auto text-xs font-bold">
        {[
          { id: 'PDF_LIBRARY' as const, label: '📚 Textbook Library (مكتبة الكتب)' },
          { id: 'UPLOAD_PDF' as const, label: '📤 Upload & OCR (رفع الكتب)' },
          { id: 'CURRICULUM_REVIEW' as const, label: '🔍 Curriculum Review (مراجعة المنهاج)' },
          { id: 'ADD_TERM' as const, label: '➕ Add Term' },
          { id: 'ADD_CLASS' as const, label: '🏫 Add Class' },
          { id: 'ADD_LESSON' as const, label: '📝 Add Lesson' },
          { id: 'UPDATE_EDITION' as const, label: '🔄 Update Edition' },
          { id: 'COVERAGE' as const, label: '📊 Coverage' },
          { id: 'QUALITY' as const, label: '🛡️ Quality' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveMode(tab.id);
              setSuccessMsg('');
              if (tab.id === 'QUALITY') loadQuality();
            }}
            className={`px-4 py-3 border-t-2 border-r-2 border-l-2 transition-all shrink-0 cursor-pointer ${
              activeMode === tab.id
                ? 'bg-white text-purple-950 font-black border-slate-900 -mb-0.5 pb-3.5 z-10 shadow-xs'
                : 'bg-slate-100 text-slate-500 border-transparent hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {successMsg && (
        <div className="p-3 bg-emerald-100 border border-emerald-400 text-emerald-900 text-xs font-bold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-700" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* MODE 0: TEXTBOOK PDF LIBRARY */}
      {activeMode === 'PDF_LIBRARY' && <TextbookPdfLibrary />}

      {activeMode === 'UPLOAD_PDF' && (
        <TextbookPdfUploader
          onUploadComplete={() => {
            setSuccessMsg('Textbook indexed! Switched to Curriculum Review.');
            setActiveMode('CURRICULUM_REVIEW');
          }}
        />
      )}

      {activeMode === 'CURRICULUM_REVIEW' && <CurriculumReview />}

      {/* MODE 1: ADD_TERM */}
      {activeMode === 'ADD_TERM' && (
        <div className="sharp-card p-6 border border-slate-300 bg-white space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider">
              Add / Configure Term Container
            </h2>
            <p className="text-xs text-slate-600">
              Registers Term 2, Term 3, or other terms with custom pricing (default USD 33 per term).
            </p>
          </div>

          <form onSubmit={handleAddTerm} className="space-y-3 max-w-md">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Target Class</label>
                <select
                  value={termGrade}
                  onChange={(e) => setTermGrade(parseInt(e.target.value, 10))}
                  className="sharp-input w-full text-xs"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                    <option key={g} value={g}>Class {g}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Term Number</label>
                <select
                  value={termNumber}
                  onChange={(e) => setTermNumber(parseInt(e.target.value, 10))}
                  className="sharp-input w-full text-xs"
                >
                  <option value={1}>Term 1</option>
                  <option value={2}>Term 2</option>
                  <option value={3}>Term 3</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Title (English)</label>
              <input
                type="text"
                value={termTitleEn}
                onChange={(e) => setTermTitleEn(e.target.value)}
                className="sharp-input w-full text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Title (Arabic)</label>
              <input
                type="text"
                value={termTitleAr}
                onChange={(e) => setTermTitleAr(e.target.value)}
                className="sharp-input w-full text-xs font-arabic text-right"
                dir="rtl"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Term Price in USD (Crack Term Fee)
              </label>
              <input
                type="number"
                step="0.01"
                value={termPrice}
                onChange={(e) => setTermPrice(parseFloat(e.target.value))}
                className="sharp-input w-full text-xs font-mono font-bold"
              />
            </div>

            <button type="submit" className="btn-primary py-2 px-4 text-xs">
              Commit Term Registration
            </button>
          </form>
        </div>
      )}

      {/* MODE 2: ADD_CLASS */}
      {activeMode === 'ADD_CLASS' && (
        <div className="sharp-card p-6 border border-slate-300 bg-white space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider">
              Add Class / Grade Container
            </h2>
            <p className="text-xs text-slate-600">
              Registers a new school grade (e.g. Class 6) without modifying frontend source code.
            </p>
          </div>

          <form onSubmit={handleAddClass} className="space-y-3 max-w-md">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Grade Number</label>
              <input
                type="number"
                min={1}
                max={12}
                value={classNumber}
                onChange={(e) => setClassNumber(parseInt(e.target.value, 10))}
                className="sharp-input w-full text-xs"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Class Name (English)</label>
              <input
                type="text"
                value={classNameEn}
                onChange={(e) => setClassNameEn(e.target.value)}
                className="sharp-input w-full text-xs"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Class Name (Arabic)</label>
              <input
                type="text"
                value={classNameAr}
                onChange={(e) => setClassNameAr(e.target.value)}
                className="sharp-input w-full text-xs font-arabic text-right"
                dir="rtl"
              />
            </div>

            <button type="submit" className="btn-primary py-2 px-4 text-xs">
              Create Class Container
            </button>
          </form>
        </div>
      )}

      {/* MODE 3: ADD_LESSON */}
      {activeMode === 'ADD_LESSON' && (
        <div className="sharp-card p-6 border border-slate-300 bg-white space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider">
              Import Validated 12-Feature Lesson JSON Package
            </h2>
            <p className="text-xs text-slate-600">
              Paste the complete authoring package. Reimporting identical SHA256 hashes safely updates without duplicating.
            </p>
          </div>

          <form onSubmit={handleAddLesson} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 font-mono">
                Lesson Authoring JSON Package (content.schema.json compliant):
              </label>
              <textarea
                rows={12}
                value={lessonPackageJson}
                onChange={(e) => setLessonPackageJson(e.target.value)}
                className="sharp-input w-full font-mono text-xs p-3"
              />
            </div>

            <button type="submit" className="btn-primary py-2 px-4 text-xs flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5" />
              <span>Validate & Ingest Lesson Package</span>
            </button>
          </form>
        </div>
      )}

      {/* MODE 4: UPDATE_EDITION */}
      {activeMode === 'UPDATE_EDITION' && (
        <div className="sharp-card p-6 border border-slate-300 bg-white space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider">
              Update Book Edition (Section 8 Ingestion)
            </h2>
            <p className="text-xs text-slate-600">
              Preserves historical attempts and existing student assessments. A new edition becomes a distinct version.
            </p>
          </div>

          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const res = await api.adminAddTerm({ grade: 5, term: 1, title_ar: 'طبعة حديثة', title_en: 'New Edition', price_usd: 33 });
              setSuccessMsg(`Edition ${academicYear} registered safely.`);
            }}
            className="space-y-3 max-w-md"
          >
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Edition Identifier</label>
              <input
                type="text"
                value={editionId}
                onChange={(e) => setEditionId(e.target.value)}
                className="sharp-input w-full text-xs font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Book Title</label>
              <input
                type="text"
                value={editionTitle}
                onChange={(e) => setEditionTitle(e.target.value)}
                className="sharp-input w-full text-xs"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Academic Year</label>
                <input
                  type="text"
                  value={academicYear}
                  onChange={(e) => setAcademicYear(e.target.value)}
                  className="sharp-input w-full text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Publication Year</label>
                <input
                  type="text"
                  value={pubYear}
                  onChange={(e) => setPubYear(e.target.value)}
                  className="sharp-input w-full text-xs"
                />
              </div>
            </div>

            <button type="submit" className="btn-primary py-2 px-4 text-xs">
              Register Edition
            </button>
          </form>
        </div>
      )}

      {/* MODE 5: COVERAGE REPORT */}
      {activeMode === 'COVERAGE' && coverage && (
        <div className="sharp-card p-6 border border-slate-300 bg-white space-y-4">
          <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
            Textbook Extraction & Pronunciation Coverage Report
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">Total Pages:</span>
              <span className="text-xl font-black text-slate-900">{coverage.total_source_pages}</span>
            </div>
            <div className="p-3 bg-emerald-50 border border-emerald-300">
              <span className="text-emerald-900 block">Reviewed Pages:</span>
              <span className="text-xl font-black text-emerald-900">{coverage.reviewed_pages_count}</span>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">Reviewed Words:</span>
              <span className="text-xl font-black text-slate-900">{coverage.reviewed_word_occurrences}</span>
            </div>
            <div className="p-3 bg-emerald-50 border border-emerald-300">
              <span className="text-emerald-900 block">Playable Audio Targets:</span>
              <span className="text-xl font-black text-emerald-900">{coverage.playable_audio_targets_count}</span>
            </div>
          </div>

          <div className="text-xs text-slate-600 bg-slate-50 p-3 border border-slate-200">
            <strong>Source File:</strong> {coverage.pdf_source}
          </div>
        </div>
      )}
      {activeMode === 'QUALITY' && quality && (
        <div className="space-y-4">
          <div className={`p-4 border-2 ${quality.ok ? 'border-emerald-600 bg-emerald-50' : 'border-amber-500 bg-amber-50'}`}>
            <div className="font-black text-slate-900">OCR &amp; Content Quality Checks</div>
            <div className="text-sm mt-1">{quality.ok ? 'Ready for publication' : `${quality.issue_count} issue(s) require review`}</div>
            <div className="text-xs text-slate-600 mt-2">Pages checked: {quality.pages_checked} · Lessons checked: {quality.lessons_checked}</div>
          </div>
          {quality.issues?.length > 0 && <div className="border border-slate-200 divide-y divide-slate-200 text-xs">{quality.issues.map((issue: any, i: number) => <div key={i} className="p-2.5"><strong>{issue.type}</strong> · {issue.edition_id || issue.lesson_id || `page ${issue.pdf_page}`}</div>)}</div>}
        </div>
      )}

      {/* Action Logs Box */}
      {actionLog.length > 0 && (
        <div className="sharp-card p-4 border border-slate-300 bg-slate-900 text-slate-200 font-mono text-xs space-y-1">
          <div className="text-amber-400 font-bold mb-1">Administrative Audit Trail:</div>
          {actionLog.map((log, i) => (
            <div key={i}>{log}</div>
          ))}
        </div>
      )}
    </div>
  );
};
