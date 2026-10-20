import React, { useRef, useState } from 'react';
import { Camera, Upload, Loader2, Lightbulb, Volume2, CheckCircle2, AlertCircle, RotateCcw, PenLine, ShieldCheck } from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';

type Question = {
  number: string;
  question_ar: string;
  question_en: string;
  asks_en: string;
  hint_en: string;
  hint_ar: string;
  answer_format: string;
};
type Scan = { scan_id: string; is_homework: boolean; title_en: string; questions: Question[] };
type Check = { verdict: 'correct' | 'almost' | 'not_yet' | 'unreadable'; student_answer_read: string; feedback_en: string; feedback_ar: string };

const DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';

const VERDICTS: Record<Check['verdict'], { label: string; className: string }> = {
  correct: { label: 'Correct! Ready to hand in', className: 'bg-emerald-50 border-emerald-300 text-emerald-950' },
  almost: { label: 'Almost there: one small slip', className: 'bg-amber-50 border-amber-300 text-amber-950' },
  not_yet: { label: 'Not yet: have another try', className: 'bg-sky-50 border-sky-300 text-sky-950' },
  unreadable: { label: "Fahim couldn't read that clearly", className: 'bg-slate-50 border-slate-300 text-slate-800' },
};

const readAsDataUrl = (file: Blob) => new Promise<string>((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(String(reader.result));
  reader.onerror = () => reject(new Error('The file could not be read'));
  reader.readAsDataURL(file);
});

/** Photos are shrunk to at most 2000 px as JPEG: plenty to read the Arabic, quick to upload. */
async function photoPayload(file: File): Promise<{ data: string; type: string }> {
  const url = await readAsDataUrl(file);
  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
    const scale = Math.min(1, 2000 / Math.max(image.width, image.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(image.width * scale);
    canvas.height = Math.round(image.height * scale);
    canvas.getContext('2d')?.drawImage(image, 0, 0, canvas.width, canvas.height);
    return { data: canvas.toDataURL('image/jpeg', 0.85).split(',')[1], type: 'image/jpeg' };
  } catch {
    return { data: url.split(',')[1], type: file.type || 'image/jpeg' };
  }
}

function QuestionCard({ q, scanId, childId }: { q: Question; scanId: string; childId?: string }) {
  const [showHint, setShowHint] = useState(false);
  const [answer, setAnswer] = useState('');
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState<Check | null>(null);
  const [error, setError] = useState('');
  const photoInput = useRef<HTMLInputElement>(null);

  const check = async (photo?: File) => {
    setChecking(true); setError(''); setResult(null);
    try {
      const body: Parameters<typeof api.checkHomeworkAnswer>[0] = { scan_id: scanId, question_number: q.number, child_id: childId };
      if (photo) {
        const { data, type } = await photoPayload(photo);
        Object.assign(body, { answer_image_base64: data, answer_image_type: type });
      } else {
        body.answer_text = answer.trim();
      }
      setResult(await api.checkHomeworkAnswer(body));
    } catch (e: any) { setError(e.message); }
    finally { setChecking(false); }
  };

  const verdict = result ? VERDICTS[result.verdict] : null;
  return <article className="border border-slate-200 rounded-xl p-3 space-y-2 bg-white">
    <div className="flex items-start gap-2">
      <span className="shrink-0 bg-purple-700 text-white text-xs font-bold rounded-lg px-2 py-0.5">Q{q.number}</span>
      <div className="flex-1 min-w-0 space-y-1">
        <div dir="rtl" className="font-arabic text-lg leading-loose text-slate-900">
          <ArabicWordSpans text={q.question_ar} />
        </div>
        <p className="text-sm text-slate-700"><span className="font-semibold">In English:</span> {q.question_en}</p>
        <p className="text-sm text-slate-700"><span className="font-semibold">What to do:</span> {q.asks_en}</p>
      </div>
      <button type="button" aria-label="Listen to the question" onClick={() => audioManager.playArabic(q.question_ar)}
        className="shrink-0 p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50">
        <Volume2 className="w-4 h-4" />
      </button>
    </div>

    {showHint
      ? <div className="border border-amber-300 bg-amber-50 rounded-lg p-2 text-sm text-amber-950 space-y-1">
        <div className="font-semibold flex items-center gap-1"><Lightbulb className="w-4 h-4" /> Hint</div>
        <p>{q.hint_en}</p>
        <p dir="rtl" className="font-arabic">{q.hint_ar}</p>
      </div>
      : <button type="button" onClick={() => setShowHint(true)}
        className="text-sm font-semibold text-amber-800 flex items-center gap-1 hover:underline">
        <Lightbulb className="w-4 h-4" /> Stuck? Show a hint
      </button>}

    <div className="space-y-1.5">
      <label className="text-xs font-semibold text-slate-600 flex items-center gap-1" htmlFor={`answer-${q.number}`}>
        <PenLine className="w-3.5 h-3.5" /> Check my answer before I hand it in
      </label>
      <textarea id={`answer-${q.number}`} dir="rtl" rows={2} value={answer} onChange={e => setAnswer(e.target.value)}
        placeholder="اُكْتُبْ جَوَابَكَ هُنَا… (type your answer)"
        className="w-full border border-slate-300 rounded-lg p-2 font-arabic text-base" />
      <div className="flex flex-wrap gap-2">
        <button type="button" disabled={checking || !answer.trim()} onClick={() => check()}
          className="px-3 py-1.5 rounded-lg bg-purple-700 text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-1">
          {checking ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />} Check
        </button>
        <button type="button" disabled={checking} onClick={() => photoInput.current?.click()}
          className="px-3 py-1.5 rounded-lg border border-slate-300 text-sm font-semibold text-slate-700 disabled:opacity-50 flex items-center gap-1">
          <Camera className="w-4 h-4" /> Photo of my handwriting
        </button>
        <input ref={photoInput} type="file" accept="image/*" capture="environment" className="hidden"
          onChange={e => { const f = e.target.files?.[0]; e.target.value = ''; if (f) check(f); }} />
      </div>
    </div>

    {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
    {result && verdict && <div role="status" className={`border rounded-lg p-2 text-sm space-y-1 ${verdict.className}`}>
      <div className="font-bold">{verdict.label}</div>
      {result.student_answer_read && <p className="text-xs opacity-80">Fahim read: <span dir="rtl" className="font-arabic">{result.student_answer_read}</span></p>}
      <p>{result.feedback_en}</p>
      <p dir="rtl" className="font-arabic">{result.feedback_ar}</p>
    </div>}
  </article>;
}

export function HomeworkHelper({ childId, grade }: { childId?: string; grade?: number }) {
  const [scan, setScan] = useState<Scan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const cameraInput = useRef<HTMLInputElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const upload = async (file: File) => {
    setBusy(true); setError(''); setScan(null);
    try {
      const isPhoto = file.type.startsWith('image/');
      const payload = isPhoto ? await photoPayload(file)
        : { data: (await readAsDataUrl(file)).split(',')[1], type: file.type || (file.name.toLowerCase().endsWith('.docx') ? DOCX : 'application/pdf') };
      setScan(await api.scanHomework({ file_base64: payload.data, mime_type: payload.type, file_name: file.name, grade, child_id: childId }));
    } catch (e: any) { setError(e.message); }
    finally { setBusy(false); }
  };
  const picked = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (file) upload(file);
  };

  return <div className="flex-1 overflow-y-auto my-3 space-y-3">
    <div className="border border-purple-200 bg-purple-50 rounded-xl p-3 text-sm text-purple-950 space-y-2">
      <p className="font-semibold">Homework helper · مُسَاعِدُ الوَاجِبِ</p>
      <p>Snap your worksheet or upload it. Fahim explains each question in English and gives a hint, then checks your own answer before you hand it in.</p>
      <p className="text-xs flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" /> Fahim never gives the answers: the work stays yours.</p>
      <div className="flex flex-wrap gap-2">
        <button type="button" disabled={busy} onClick={() => cameraInput.current?.click()}
          className="px-3 py-2 rounded-lg bg-purple-700 text-white font-semibold flex items-center gap-1.5 disabled:opacity-50">
          <Camera className="w-4 h-4" /> Take a photo
        </button>
        <button type="button" disabled={busy} onClick={() => fileInput.current?.click()}
          className="px-3 py-2 rounded-lg border border-purple-300 bg-white text-purple-900 font-semibold flex items-center gap-1.5 disabled:opacity-50">
          <Upload className="w-4 h-4" /> Upload photo, PDF or Word
        </button>
        <input ref={cameraInput} type="file" accept="image/*" capture="environment" className="hidden" onChange={picked} />
        <input ref={fileInput} type="file" accept={`image/*,.pdf,application/pdf,.docx,${DOCX}`} className="hidden" onChange={picked} />
      </div>
    </div>

    {busy && <p role="status" className="text-sm text-slate-600 flex items-center gap-2">
      <Loader2 className="w-4 h-4 animate-spin" /> Fahim is reading your worksheet…
    </p>}
    {error && <p role="alert" className="text-sm text-red-700 flex items-center gap-1"><AlertCircle className="w-4 h-4" /> {error}</p>}

    {scan && !scan.is_homework && <p className="text-sm border border-slate-300 bg-slate-50 rounded-xl p-3">
      Fahim couldn't find any homework questions in this file. Try a clearer photo of the printed worksheet, taken straight on in good light.
    </p>}
    {scan && scan.is_homework && <>
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold text-slate-800">
          {scan.title_en ? `${scan.title_en} · ` : ''}{scan.questions.length} question{scan.questions.length === 1 ? '' : 's'}
        </p>
        <button type="button" onClick={() => setScan(null)} className="text-xs text-slate-600 flex items-center gap-1 hover:underline">
          <RotateCcw className="w-3.5 h-3.5" /> New worksheet
        </button>
      </div>
      {scan.questions.map((q, i) => <QuestionCard key={`${q.number}-${i}`} q={q} scanId={scan.scan_id} childId={childId} />)}
    </>}
  </div>;
}
