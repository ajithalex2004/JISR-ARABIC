import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, RefreshCw, BookOpen, Layers, Check } from 'lucide-react';
import { api } from '../../services/api';

interface TextbookPdfUploaderProps {
  onUploadComplete?: (editionId: string) => void;
}

export const TextbookPdfUploader: React.FC<TextbookPdfUploaderProps> = ({ onUploadComplete }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [grade, setGrade] = useState<number>(1);
  const [term, setTerm] = useState<number>(1);
  const [startPage, setStartPage] = useState<number>(1);
  const [pageCount, setPageCount] = useState<string>(''); // empty = all
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [uploadResult, setUploadResult] = useState<any>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Only PDF documents are supported (.pdf)');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setErrorMessage('');
      setUploadResult(null);

      // Auto-detect grade and term from filename if present
      const name = file.name.toLowerCase();
      const gMatch = name.match(/(?:grade|gr|g|class|cls)[\s_-]?(\d+)/i);
      if (gMatch && parseInt(gMatch[1], 10) >= 1 && parseInt(gMatch[1], 10) <= 12) {
        setGrade(parseInt(gMatch[1], 10));
      }
      const tMatch = name.match(/(?:term|vol|t)[\s_-]?(\d+)/i);
      if (tMatch && parseInt(tMatch[1], 10) >= 1 && parseInt(tMatch[1], 10) <= 3) {
        setTerm(parseInt(tMatch[1], 10));
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Only PDF documents are supported (.pdf)');
        return;
      }
      setSelectedFile(file);
      setErrorMessage('');
      setUploadResult(null);

      const name = file.name.toLowerCase();
      const gMatch = name.match(/(?:grade|gr|g|class|cls)[\s_-]?(\d+)/i);
      if (gMatch && parseInt(gMatch[1], 10) >= 1 && parseInt(gMatch[1], 10) <= 12) {
        setGrade(parseInt(gMatch[1], 10));
      }
      const tMatch = name.match(/(?:term|vol|t)[\s_-]?(\d+)/i);
      if (tMatch && parseInt(tMatch[1], 10) >= 1 && parseInt(tMatch[1], 10) <= 3) {
        setTerm(parseInt(tMatch[1], 10));
      }
    }
  };

  const pollTask = async (taskId: string) => {
    try {
      const task = await api.getTask(taskId);
      if (task.status === 'completed' || task.status === 'succeeded') {
        setIsUploading(false);
        setUploadProgress(100);
        setStatusMessage('Textbook successfully processed and indexed into PostgreSQL!');
        setUploadResult(task.result || { status: 'completed' });
        if (onUploadComplete) {
          onUploadComplete(task.result?.book_edition_id || `moe_gr${grade}_vol${term}_2023`);
        }
      } else if (task.status === 'failed') {
        setIsUploading(false);
        setErrorMessage(`Task failed: ${task.error || 'Unknown indexing error'}`);
      } else {
        // still processing
        setUploadProgress(task.progress || 50);
        setStatusMessage(`Processing textbook OCR & rendering pages (${task.progress || 50}%)...`);
        setTimeout(() => pollTask(taskId), 1500);
      }
    } catch (err: any) {
      setIsUploading(false);
      setErrorMessage(`Error polling indexing task: ${err.message}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage('Please select a textbook PDF file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(15);
    setStatusMessage('Uploading PDF file to server...');
    setErrorMessage('');
    setUploadResult(null);

    try {
      const pCount = pageCount.trim() ? parseInt(pageCount.trim(), 10) : undefined;
      const res = await api.uploadCurriculumPdf(selectedFile, grade, term, startPage, pCount);

      if (res.task_id) {
        setStatusMessage('PDF staged. Background OCR and page rendering in progress...');
        setUploadProgress(30);
        pollTask(res.task_id);
      } else {
        setIsUploading(false);
        setUploadProgress(100);
        setUploadResult(res);
        setStatusMessage('Upload and indexing finished successfully.');
        if (onUploadComplete) {
          onUploadComplete(res.book_edition_id);
        }
      }
    } catch (err: any) {
      setIsUploading(false);
      setErrorMessage(err.message || 'Failed to upload textbook PDF.');
    }
  };

  return (
    <div className="sharp-card p-6 border-2 border-slate-900 bg-white space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <h2 className="text-base font-black text-slate-900 uppercase tracking-wider">
              UAE Ministry Textbook PDF Uploader & OCR Pipeline
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Upload official UAE MoE Arabic student textbooks (Volumes 1, 2, 3) for automated page slicing, OCR Arabic transcription, and Reader integration.
          </p>
        </div>
        <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-3 py-1 border border-slate-300 self-start sm:self-auto">
          moe_gr{grade}_vol{term}_2023
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Grade Selector */}
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            1. Select Grade Level (المرحلة الدراسية):
          </label>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
              <button
                type="button"
                key={g}
                onClick={() => setGrade(g)}
                className={`px-3 py-1.5 text-xs font-bold transition-all border shrink-0 ${
                  grade === g
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                }`}
              >
                Grade {g} (الصف {g})
              </button>
            ))}
          </div>
        </div>

        {/* Term Selector */}
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            2. Select Term / Volume (الفصل الدراسي):
          </label>
          <div className="flex items-center gap-2">
            {[
              { t: 1, labelEn: 'Term 1 / Vol 1', labelAr: 'الفصل الأول' },
              { t: 2, labelEn: 'Term 2 / Vol 2', labelAr: 'الفصل الثاني' },
              { t: 3, labelEn: 'Term 3 / Vol 3', labelAr: 'الفصل الثالث' }
            ].map((item) => (
              <button
                type="button"
                key={item.t}
                onClick={() => setTerm(item.t)}
                className={`flex-1 py-2 px-3 text-xs font-bold transition-all border text-center ${
                  term === item.t
                    ? 'bg-purple-900 text-white border-purple-900'
                    : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div>{item.labelEn}</div>
                <div className="text-[11px] font-arabic opacity-80">{item.labelAr}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            3. Choose or Drag Textbook PDF:
          </label>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed p-6 text-center cursor-pointer transition-all ${
              selectedFile
                ? 'border-emerald-500 bg-emerald-50/20'
                : 'border-slate-300 hover:border-slate-500 bg-slate-50/50'
            }`}
          >
            <div className="flex flex-col items-center justify-center gap-2">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                selectedFile ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'
              }`}>
                {selectedFile ? <FileText className="w-6 h-6" /> : <Upload className="w-6 h-6" />}
              </div>

              {selectedFile ? (
                <div>
                  <div className="text-sm font-black text-slate-900">{selectedFile.name}</div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · Ready to upload for Grade {grade} (Term {term})
                  </div>
                  <div className="text-xs text-emerald-700 font-bold mt-2">
                    Click to choose a different PDF
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-sm font-bold text-slate-800">
                    Click to select PDF or drag & drop here
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Accepts official UAE Ministry Student Textbooks (up to 200 MB)
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Page Range Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 p-4 border border-slate-200">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Start PDF Page Index (Default: 1)
            </label>
            <input
              type="number"
              min={1}
              value={startPage}
              onChange={(e) => setStartPage(Math.max(1, parseInt(e.target.value, 10) || 1))}
              className="sharp-input w-full text-xs"
            />
            <span className="text-[10px] text-slate-500">First page to process (usually 1 for front cover).</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Page Count Limit (Optional)
            </label>
            <input
              type="number"
              min={1}
              placeholder="Leave empty to index all pages"
              value={pageCount}
              onChange={(e) => setPageCount(e.target.value)}
              className="sharp-input w-full text-xs"
            />
            <span className="text-[10px] text-slate-500">Leave blank to automatically index the entire book.</span>
          </div>
        </div>

        {/* Status Messages */}
        {errorMessage && (
          <div className="p-3 bg-rose-50 border border-rose-300 text-rose-800 text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {statusMessage && (
          <div className="p-3 bg-blue-50 border border-blue-300 text-blue-900 text-xs font-semibold space-y-2">
            <div className="flex items-center gap-2">
              <RefreshCw className={`w-3.5 h-3.5 ${isUploading ? 'animate-spin' : ''}`} />
              <span>{statusMessage}</span>
            </div>
            {isUploading && (
              <div className="w-full bg-blue-200 h-1.5 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            )}
          </div>
        )}

        {/* Upload Result Card */}
        {uploadResult && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-900 space-y-3 text-xs">
            <div className="flex items-center gap-2 font-bold text-sm text-emerald-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Textbook Ingestion Complete!</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] bg-white p-2.5 border border-emerald-200">
              <div>
                <span className="text-slate-500 block">Edition ID:</span>
                <span className="font-bold text-slate-900">{uploadResult.book_edition_id || `moe_gr${grade}_vol{term}_2023`}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Pages Processed:</span>
                <span className="font-bold text-slate-900">{uploadResult.pages_processed || 'All'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Status:</span>
                <span className="font-bold text-emerald-700">Indexed & Verified</span>
              </div>
            </div>
            <p className="text-slate-600">
              Scanned pages are now available in the interactive reader and linked to the curriculum chapters for Grade {grade}, Term {term}.
            </p>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={isUploading || !selectedFile}
            className={`btn-primary py-2.5 px-6 text-xs font-bold flex items-center gap-2 ${
              isUploading || !selectedFile ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isUploading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Processing OCR & Indexing Pages...</span>
              </>
            ) : (
              <>
                <Upload className="w-3.5 h-3.5" />
                <span>Upload & Process Grade {grade} (Term {term}) PDF</span>
              </>
            )}
          </button>

          {selectedFile && !isUploading && (
            <button
              type="button"
              onClick={() => {
                setSelectedFile(null);
                setUploadResult(null);
                setStatusMessage('');
              }}
              className="text-xs text-slate-500 hover:text-slate-800 underline"
            >
              Clear
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
