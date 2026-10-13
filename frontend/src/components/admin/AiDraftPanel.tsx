import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { CheckCircle2, Eye, Loader2, Sparkles, Upload } from 'lucide-react';

interface Props {
  grade: number;
  term: number;
  lesson: any | null;
  onChanged: () => void;
}

const statusStyle: Record<string, string> = {
  content_pending: 'bg-amber-100 text-amber-800',
  approved: 'bg-sky-100 text-sky-800',
  published: 'bg-emerald-100 text-emerald-800',
  superseded: 'bg-slate-100 text-slate-500',
};

/** Queue Gemini drafts from the textbook scans, then review, approve and publish them. */
export const AiDraftPanel: React.FC<Props> = ({ grade, term, lesson, onChanged }) => {
  const [versions, setVersions] = useState<any[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadVersions = async () => {
    if (!lesson) return setVersions([]);
    try {
      setVersions(await api.getLessonVersions(lesson.id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    setPreview(null);
    setError('');
    loadVersions();
  }, [lesson?.id]);

  const pollTask = async (taskId: string) => {
    try {
      const task = await api.getTask(taskId);
      if (task.status === 'completed' || task.status === 'succeeded') {
        const s = task.result?.summary || {};
        setBusy(false);
        setMessage(`AI drafting finished: ${s.drafted ?? 0} drafted, ${s.skipped ?? 0} already waiting for review, ${s.failed ?? 0} failed.`);
        const failed = (task.result?.lessons || []).filter((l: any) => l.status === 'failed');
        if (failed.length) setError(failed.map((l: any) => `${l.lesson_id}: ${l.detail}`).join('\n'));
        await loadVersions();
        onChanged();
      } else if (task.status === 'failed') {
        setBusy(false);
        setError(`Drafting failed: ${task.error || 'unknown error'}`);
      } else {
        setMessage(`Drafting lessons with AI from the textbook pages (${task.progress || 0}%)… this takes about a minute per lesson.`);
        setTimeout(() => pollTask(taskId), 3000);
      }
    } catch (err: any) {
      setBusy(false);
      setError(err.message);
    }
  };

  const startDrafts = async (lessonIds?: string[], overwrite = false) => {
    setBusy(true);
    setError('');
    setMessage('Queuing AI drafting…');
    try {
      const { task_id } = await api.startContentDrafts(grade, term, lessonIds, overwrite);
      pollTask(task_id);
    } catch (err: any) {
      setBusy(false);
      setMessage('');
      setError(err.message);
    }
  };

  const review = async (versionId: string, action: 'approve' | 'publish') => {
    setError('');
    try {
      await api.reviewLessonVersion(lesson.id, versionId, action);
      setMessage(action === 'approve' ? 'Draft approved. Publish it to make it live for learners.' : 'Lesson published to learners.');
      await loadVersions();
      onChanged();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const openPreview = async (versionId: string) => {
    try {
      setPreview(await api.getLessonVersion(lesson.id, versionId));
    } catch (err: any) {
      setError(err.message);
    }
  };

  const content = preview?.content || {};

  return (
    <div className="space-y-4 border border-purple-200 bg-purple-50/30 p-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-black text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> AI lesson drafts
          </h3>
          <p className="text-[11px] text-slate-600">
            Gemini reads the scanned textbook pages and drafts the full lesson. Nothing reaches learners until a reviewer approves and publishes it.
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          {lesson && (
            <button
              disabled={busy}
              onClick={() => startDrafts([lesson.id], true)}
              className="px-3 py-2 text-xs font-bold border border-purple-300 text-purple-900 hover:bg-purple-100 disabled:opacity-50"
            >
              Redraft this lesson
            </button>
          )}
          <button
            disabled={busy}
            onClick={() => startDrafts()}
            className="px-3 py-2 text-xs font-bold bg-purple-800 hover:bg-purple-900 text-white disabled:opacity-50 flex items-center gap-1.5"
          >
            {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            Draft Grade {grade} Term {term}
          </button>
        </div>
      </div>

      {message && <div className="text-xs text-purple-900 bg-white border border-purple-200 p-2">{message}</div>}
      {error && <div className="text-xs text-red-800 bg-red-50 border border-red-200 p-2 whitespace-pre-wrap">{error}</div>}

      {lesson && (
        <div className="space-y-2">
          {versions.length === 0 && <div className="text-[11px] text-slate-500 italic">No content versions for this lesson yet.</div>}
          {versions.map((v) => (
            <div key={v.id} className="flex flex-wrap items-center justify-between gap-2 bg-white border border-slate-200 p-2 text-xs">
              <div className="flex items-center gap-2">
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${statusStyle[v.status] || 'bg-slate-100 text-slate-700'}`}>{v.status}</span>
                <span className="font-mono text-slate-700">{v.version_tag}</span>
                {v.ai_draft && <span className="text-[9px] font-bold text-purple-800">AI draft · pages {v.provenance?.source_pdf_pages?.[0]}–{v.provenance?.source_pdf_pages?.slice(-1)[0]}</span>}
                {v.is_active && <span className="text-[9px] font-bold text-emerald-700">LIVE</span>}
              </div>
              <div className="flex gap-1.5">
                <button onClick={() => openPreview(v.id)} className="px-2 py-1 border border-slate-300 hover:bg-slate-50 flex items-center gap-1">
                  <Eye className="w-3 h-3" /> Preview
                </button>
                {v.status === 'content_pending' && (
                  <button onClick={() => review(v.id, 'approve')} className="px-2 py-1 bg-sky-700 hover:bg-sky-800 text-white flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Approve
                  </button>
                )}
                {v.status === 'approved' && (
                  <button onClick={() => review(v.id, 'publish')} className="px-2 py-1 bg-emerald-700 hover:bg-emerald-800 text-white flex items-center gap-1">
                    <Upload className="w-3 h-3" /> Publish
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {preview && (
        <div className="bg-white border border-slate-200 p-3 space-y-3 text-xs max-h-[480px] overflow-y-auto">
          <div className="flex justify-between items-center">
            <span className="font-bold text-slate-800">Preview · {preview.version_tag}</span>
            <button onClick={() => setPreview(null)} className="text-slate-500 hover:underline">Close</button>
          </div>
          <section>
            <h4 className="font-bold text-slate-700 mb-1">Vocabulary ({content.vocabulary_cards?.length || 0})</h4>
            <div className="flex flex-wrap gap-1.5" dir="rtl">
              {(content.vocabulary_cards || []).map((c: any) => (
                <span key={c.id} className="font-arabic border border-slate-200 px-2 py-0.5" title={c.meaning_en || c.english || ''}>
                  {c.word_ar || c.arabic || c.word}
                </span>
              ))}
            </div>
          </section>
          <section>
            <h4 className="font-bold text-slate-700 mb-1">Exam practice ({content.exam_practice?.objective_questions?.length || 0} questions)</h4>
            <ol className="list-decimal pr-5 space-y-1 font-arabic" dir="rtl">
              {(content.exam_practice?.objective_questions || []).map((q: any) => (
                <li key={q.id}>{q.question_ar || q.prompt_ar || q.question}</li>
              ))}
            </ol>
          </section>
          <details>
            <summary className="cursor-pointer font-bold text-slate-700">Full lesson package (JSON)</summary>
            <pre className="text-[10px] bg-slate-50 p-2 overflow-x-auto whitespace-pre-wrap" dir="auto">{JSON.stringify(content, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
};
