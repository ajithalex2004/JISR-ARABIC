import React, { useEffect, useRef, useState } from 'react';
import {
  X, Sparkles, Send, UserCheck, MessageSquare, Volume2, Camera,
  FileText, Upload, CheckCircle2, AlertCircle, ShieldCheck, Loader2
} from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';
import { HomeworkHelper } from './HomeworkHelper';

// Matches the server's limit for uploaded papers (base64 of about 5 MB).
const MAX_PAPER_BYTES = 5 * 1024 * 1024;

type ModeTab = 'chat' | 'homework' | 'paper';

// Each mode keeps its own colour so the three buttons are easy to tell apart: a tinted background
// and border when not selected, and the solid colour (white text) when selected.
const MODE_TABS: Array<{ id: ModeTab; label: string; Icon: typeof MessageSquare; idle: string; active: string }> = [
  {
    id: 'chat', label: 'Chat Mentor (حوار مع فاهم)', Icon: MessageSquare,
    idle: 'bg-purple-50 text-purple-900 border-purple-300 hover:bg-purple-100 focus-visible:ring-purple-400',
    active: 'bg-purple-600 text-white border-purple-700 shadow-sm ring-2 ring-purple-200 focus-visible:ring-purple-400',
  },
  {
    id: 'homework', label: 'Homework Helper (مساعد الواجب)', Icon: Camera,
    idle: 'bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100 focus-visible:ring-amber-400',
    active: 'bg-amber-700 text-white border-amber-800 shadow-sm ring-2 ring-amber-200 focus-visible:ring-amber-400',
  },
  {
    id: 'paper', label: 'Exam Paper Assistant (مساعد أوراق الامتحانات)', Icon: FileText,
    idle: 'bg-emerald-50 text-emerald-900 border-emerald-300 hover:bg-emerald-100 focus-visible:ring-emerald-400',
    active: 'bg-emerald-700 text-white border-emerald-800 shadow-sm ring-2 ring-emerald-200 focus-visible:ring-emerald-400',
  },
];

interface AskFahimModalProps {
  isOpen: boolean;
  onClose: () => void;
  contextLessonId?: string;
  childId?: string;
  // The grade being studied; sent with questions so answers fit the student's level.
  grade?: number;
  /** Sent as the first question when the window opens (e.g. "explain this rule" from a lesson). */
  initialQuestion?: string;
}

export const AskFahimModal: React.FC<AskFahimModalProps> = ({
  isOpen,
  onClose,
  contextLessonId,
  childId,
  grade = 5,
  initialQuestion
}) => {
  const [activeTab, setActiveTab] = useState<ModeTab>('chat');
  const [question, setQuestion] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'fahim'; text_ar: string; text_en?: string; escalated?: boolean }>>([
    {
      sender: 'fahim',
      text_ar: 'مَرْحَبًا بِكَ! أَنَا مُعَلِّمُكَ (فَهِيم). كَيْفَ أُسَاعِدُكَ فِي دُرُوسِكَ أَوِ المُفْرَدَاتِ أَوِ القَوَاعِدِ اليَوْمَ؟',
      text_en: "Hello! I am your conversational teacher, Ask Fahim. How can I help you with your lessons, vocabulary or grammar today?"
    }
  ]);
  const [isSending, setIsSending] = useState<boolean>(false);

  // Question Paper Exam Assistant State
  const [paperTitle, setPaperTitle] = useState<string>('ورقة اختبار اللغة العربية');
  const [paperText, setPaperText] = useState<string>('');
  const [paperFileBase64, setPaperFileBase64] = useState<string | null>(null);
  const [paperFileName, setPaperFileName] = useState<string | null>(null);
  const [paperMimeType, setPaperMimeType] = useState<string>('application/pdf');
  const [isSolvingPaper, setIsSolvingPaper] = useState<boolean>(false);
  const [solvedPaper, setSolvedPaper] = useState<any | null>(null);
  const [paperError, setPaperError] = useState<string | null>(null);

  const sendText = async (userText: string) => {
    setMessages((prev) => [...prev, { sender: 'user', text_ar: userText }]);
    setQuestion('');
    setIsSending(true);

    try {
      const res = await api.askFahim(userText, contextLessonId, childId, grade);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'fahim',
          text_ar: res.answer_ar,
          text_en: res.answer_en,
          escalated: res.escalated_to_tutor
        }
      ]);
      audioManager.playArabic(res.answer_ar);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'fahim',
          text_ar: 'عُذْرًا، تَعَذَّرَ الِاتِّصَالُ حَالِيًّا. يُرْجَى مُرَاجَعَةِ مُعَلِّمِكَ الخُصُوصِيِّ.',
          text_en: 'Connection issue. Please review with your assigned mentor.'
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  // A ready-made question (e.g. "explain this rule") is asked once, as soon as the window opens.
  const askedRef = useRef<string>('');
  useEffect(() => {
    if (!isOpen) { askedRef.current = ''; return; }
    if (initialQuestion && askedRef.current !== initialQuestion) {
      askedRef.current = initialQuestion;
      setActiveTab('chat');
      sendText(initialQuestion);
    }
  }, [isOpen, initialQuestion]);

  if (!isOpen) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    await sendText(question.trim());
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // The server accepts papers up to about 5 MB; larger files would be rejected after uploading.
    if (file.size > MAX_PAPER_BYTES) {
      setPaperError(`This file is ${(file.size / 1024 / 1024).toFixed(1)} MB. Please upload a paper under 5 MB (a photo of each page, or a smaller PDF).`);
      e.target.value = '';
      return;
    }
    setPaperError(null);
    setPaperFileName(file.name);
    setPaperMimeType(file.type || 'application/pdf');
    setPaperTitle(file.name.replace(/\.[^/.]+$/, ""));

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setPaperFileBase64(result);
    };
    reader.readAsDataURL(file);
  };

  const handleSolveQuestionPaper = async () => {
    setIsSolvingPaper(true);
    setPaperError(null);
    try {
      const res = await api.solveQuestionPaper({
        paper_title: paperTitle,
        document_base64: paperFileBase64 || undefined,
        mime_type: paperMimeType,
        text_content: paperText,
        grade,
        term: 1,
        child_id: childId,
      });
      setSolvedPaper(res);
      if (res.questions?.[0]?.model_answer_ar) {
        audioManager.playArabic(res.questions[0].model_answer_ar);
      }
    } catch (err: any) {
      setPaperError(err.message || 'Failed to solve question paper');
    } finally {
      setIsSolvingPaper(false);
    }
  };

  const handleEscalateQuestion = async (qNumber: number) => {
    try {
      await api.solveQuestionPaper({
        paper_title: `${paperTitle} - Question ${qNumber}`,
        text_content: `Question ${qNumber} needs human mentor certification.`,
        grade,
        term: 1,
        child_id: childId,
        force_escalation: true
      });
      alert('تم رفع هذا السؤال إلى قائمة المعلم الخاص للمراجعة والتصديق! (Escalated to human mentor queue)');
    } catch (e: any) {
      alert('تعذر إرسال الطلب للمعلم حالياً');
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4">
      <div className="bg-white border-2 border-slate-900 w-full max-w-2xl shadow-2xl p-5 flex flex-col h-[620px] relative rounded-2xl">
        <div className="absolute top-4 right-12 flex items-center">
          <ArabEnglishToggleSwitch compact />
        </div>

        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 p-1"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 pb-3 border-b border-slate-200">
          <div className="w-9 h-9 bg-purple-700 text-white rounded-xl flex items-center justify-center font-bold text-sm shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
              <span>Ask Fahim · اسْأَلْ فَهِيْم</span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                Gemini AI
              </span>
            </h2>
            <p className="text-[11px] text-slate-500">
              CBSE Curriculum Arabic Mentor · Autonomous Exam Paper Assistant
            </p>
          </div>
        </div>

        {/* Mode Navigation Tabs */}
        <div className="flex flex-wrap gap-2 pt-3 pb-2 border-b border-slate-100" role="tablist" aria-label="Ask Fahim modes">
          {MODE_TABS.map(({ id, label, Icon, idle, active }) => {
            const selected = activeTab === id;
            return (
              <button
                key={id}
                type="button"
                role="tab"
                aria-selected={selected}
                onClick={() => setActiveTab(id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 ${
                  selected ? active : idle
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{label}</span>
              </button>
            );
          })}
        </div>

        {activeTab === 'homework' && <HomeworkHelper childId={childId} grade={grade} />}

        {/* TAB 1: Chat Mentor */}
        {activeTab === 'chat' && (
          <>
            <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-slate-50 border border-slate-200 my-3 rounded-xl">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`p-3 max-w-[85%] text-xs rounded-xl shadow-xs ${
                    m.sender === 'user'
                      ? 'ml-auto bg-purple-900 text-white'
                      : 'mr-auto bg-white text-slate-900 border border-slate-200'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-[10px] uppercase opacity-75">
                      {m.sender === 'user' ? 'You' : 'Teacher Fahim'}
                    </span>
                    {m.sender === 'fahim' && (
                      <button
                        onClick={() => audioManager.playArabic(m.text_ar)}
                        className="text-emerald-700 hover:text-emerald-950 p-0.5"
                        title="Listen"
                      >
                        <Volume2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <div className="text-base text-right leading-relaxed" dir="rtl">
                    <ArabicWordSpans text={m.text_ar} className="text-base font-bold text-slate-900" />
                  </div>

                  {m.text_en && (
                    <div className="text-[11px] text-slate-500 mt-1 italic border-t border-slate-100 pt-1">
                      {m.text_en}
                    </div>
                  )}

                  {m.escalated && (
                    <div className="mt-2 bg-amber-100 p-1.5 text-[10px] text-amber-950 font-bold border border-amber-300 rounded flex items-center gap-1">
                      <UserCheck className="w-3 h-3 text-amber-700" />
                      <span>Escalated to human Arabic mentor for personal guidance.</span>
                    </div>
                  )}
                </div>
              ))}
              {isSending && (
                <div className="text-xs text-slate-400 italic font-mono flex items-center gap-1.5">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-600" />
                  <span>Fahim is analyzing curriculum context...</span>
                </div>
              )}
            </div>

            <form onSubmit={handleSend} className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about your lesson, words, or grammar (اسأل عن الدرس أو المفردات أو القواعد)..."
                aria-label="Your question for Fahim"
                className="flex-1 min-w-0 text-xs px-4 py-2.5 rounded-[0.875rem] border-2 border-purple-500 bg-purple-50 text-slate-900 placeholder:text-slate-600 outline-none transition-colors hover:border-purple-600 focus:border-purple-700 focus:bg-white focus:ring-2 focus:ring-purple-200"
              />
              <button
                type="submit"
                disabled={isSending || !question.trim()}
                className="btn-accent px-4 py-2 text-xs flex items-center gap-1 rounded-xl"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Ask</span>
              </button>
            </form>
          </>
        )}

        {/* TAB 2: Question Paper Assistant */}
        {activeTab === 'paper' && (
          <div className="flex-1 overflow-y-auto p-3 space-y-4 bg-slate-50 border border-slate-200 my-3 rounded-xl">
            {/* Input / Upload Section */}
            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <Upload className="w-4 h-4 text-emerald-600" />
                  <span>Upload Question Paper or Paste Questions</span>
                </span>
                <span className="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold border border-emerald-200">
                  Autonomous Solver · Minimal Escalation
                </span>
              </div>

              {/* Sample Preset Selector */}
              <div className="flex flex-wrap gap-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    setPaperTitle('اختبار منتصف الفصل الأول - ألعاب الكرة والفروسية');
                    setPaperText('س1: كم عدد اللاعبين الأساسيين في فريق كرة القدم؟\nس2: ما هو إعراب كلمة (اللاعبُ) في جملة (سجل اللاعبُ الهدفَ)؟\nس3: ما هو مرادف كلمة (جماعية) وما ضدها؟');
                    setPaperFileBase64(null);
                    setPaperFileName(null);
                  }}
                  className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-medium"
                >
                  📝 Sample: Term 1 CBSE Curriculum Exam Paper
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPaperTitle('اختبار تشخيص القواعد والإملاء - الصف الخامس');
                    setPaperText('س1: أين يقام كأس دبي العالمي للخيول سنوياً؟\nس2: حدد نوع الجملة والفاعل في: (يركض الفارس في الميدان).\nس3: هات مثالاً على كلمة تنتهي بتاء مربوطة وأخرى بهاء.');
                    setPaperFileBase64(null);
                    setPaperFileName(null);
                  }}
                  className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-medium"
                >
                  🎯 Sample: Diagnostic & Grammar Paper
                </button>
              </div>

              {/* File Upload Input */}
              <div className="flex items-center gap-2">
                <label className="cursor-pointer inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg border border-slate-300">
                  <Upload className="w-3.5 h-3.5 text-slate-600" />
                  <span>{paperFileName ? `Attached: ${paperFileName}` : 'Attach PDF / Image Paper'}</span>
                  <input
                    type="file"
                    accept=".pdf,image/png,image/jpeg"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
                {paperFileName && (
                  <button
                    onClick={() => { setPaperFileBase64(null); setPaperFileName(null); }}
                    className="text-xs text-rose-600 hover:underline font-bold"
                  >
                    Clear
                  </button>
                )}
              </div>

              {/* Text Area for Exam Questions */}
              <div>
                <textarea
                  rows={3}
                  value={paperText}
                  onChange={(e) => setPaperText(e.target.value)}
                  placeholder="Paste question paper text here or use attached document..."
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:outline-none focus:border-purple-600 font-arabic text-right"
                  dir="rtl"
                />
              </div>

              <button
                onClick={handleSolveQuestionPaper}
                disabled={isSolvingPaper || (!paperText.trim() && !paperFileBase64)}
                className="w-full py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-xs transition-colors"
              >
                {isSolvingPaper ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Gemini is analyzing & solving questions...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Solve Exam Paper (حل ورقة الامتحان بالمنهاج الإماراتي)</span>
                  </>
                )}
              </button>
            </div>

            {/* Error Banner */}
            {paperError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{paperError}</span>
              </div>
            )}

            {/* Solved Questions Display */}
            {solvedPaper && (
              <div className="space-y-3">
                <div className="flex items-center justify-between px-1">
                  <div className="text-xs font-black text-slate-900">
                    {solvedPaper.paper_title} · {solvedPaper.total_questions} Questions Solved
                  </div>
                  <div className="text-[10px] text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded font-bold">
                    {solvedPaper.model_used} · Zero Escalation
                  </div>
                </div>

                {solvedPaper.questions?.map((q: any) => (
                  <div
                    key={q.question_number}
                    className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs space-y-2.5"
                  >
                    {/* Question Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-purple-100 text-purple-900 font-black text-xs flex items-center justify-center">
                          {q.question_number}
                        </span>
                        <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                          {q.question_type}
                        </span>
                      </div>
                      <button
                        onClick={() => audioManager.playArabic(q.question_text_ar)}
                        className="text-purple-700 hover:text-purple-950 p-1"
                        title="Listen to Question"
                      >
                        <Volume2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Question Text */}
                    <div className="text-sm font-bold text-slate-900 text-right leading-relaxed font-arabic" dir="rtl">
                      {q.question_text_ar}
                    </div>
                    {q.question_text_en && (
                      <div className="text-[11px] text-slate-500 italic">
                        {q.question_text_en}
                      </div>
                    )}

                    {/* Model Answer Box */}
                    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-[11px] font-bold text-emerald-900">
                        <span className="flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Answer · الإجابة</span>
                        </span>
                        <button
                          onClick={() => audioManager.playArabic(q.model_answer_ar)}
                          className="text-emerald-700 hover:text-emerald-950 text-[10px] underline flex items-center gap-1"
                        >
                          <Volume2 className="w-3 h-3" />
                          <span>Listen</span>
                        </button>
                      </div>
                      <div className="text-sm font-extrabold text-emerald-950 text-right font-arabic leading-relaxed" dir="rtl">
                        {q.model_answer_ar || (
                          <span className="text-amber-800 font-semibold">
                            لم تتضح هذه الإجابة من الورقة — راجعها مع المعلم · Not readable on the paper: check with a teacher
                          </span>
                        )}
                      </div>
                      {q.model_answer_en && (
                        <div className="text-[11px] text-emerald-800">
                          {q.model_answer_en}
                        </div>
                      )}
                    </div>

                    {/* Footer: optional teacher review (answers only: no explanations or textbook citations) */}
                    <div className="flex items-center justify-end pt-1 text-[11px]">
                      <button
                        onClick={() => handleEscalateQuestion(q.question_number)}
                        className="text-[10px] text-amber-800 hover:text-amber-950 hover:underline flex items-center gap-1 font-semibold"
                      >
                        <UserCheck className="w-3 h-3 text-amber-700" />
                        <span>Request Teacher Review</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

