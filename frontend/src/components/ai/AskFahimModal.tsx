import React, { useState } from 'react';
import {
  X, Sparkles, Send, UserCheck, MessageSquare, Volume2,
  FileText, Upload, CheckCircle2, AlertCircle, BookOpen, ShieldCheck, Loader2
} from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from '../common/ArabEnglishToggleSwitch';

interface AskFahimModalProps {
  isOpen: boolean;
  onClose: () => void;
  contextLessonId?: string;
  childId?: string;
}

export const AskFahimModal: React.FC<AskFahimModalProps> = ({
  isOpen,
  onClose,
  contextLessonId = 'lesson_01_ball_games',
  childId
}) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'paper'>('chat');
  const [question, setQuestion] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'fahim'; text_ar: string; text_en?: string; escalated?: boolean }>>([
    {
      sender: 'fahim',
      text_ar: 'مَرْحَبًا بِكَ! أَنَا مُعَلِّمُكَ (فَهِيم). كَيْفَ أُسَاعِدُكَ فِي دَرْسِ أَلْعَابِ الكُرَةِ أَوِ القَوَاعِدِ اليَوْمَ؟',
      text_en: "Hello! I am your conversational teacher, Ask Fahim. How can I assist you with Ball Games or grammar rules today?"
    }
  ]);
  const [isSending, setIsSending] = useState<boolean>(false);

  // Question Paper Exam Assistant State
  const [paperTitle, setPaperTitle] = useState<string>('ورقة اختبار اللغة العربية - الصف الخامس');
  const [paperText, setPaperText] = useState<string>('كم عدد اللاعبين في فريق كرة القدم؟ وما هو إعراب كلمة (اللاعبُ) في جملة (سجل اللاعبُ الهدفَ)؟');
  const [paperFileBase64, setPaperFileBase64] = useState<string | null>(null);
  const [paperFileName, setPaperFileName] = useState<string | null>(null);
  const [paperMimeType, setPaperMimeType] = useState<string>('application/pdf');
  const [isSolvingPaper, setIsSolvingPaper] = useState<boolean>(false);
  const [solvedPaper, setSolvedPaper] = useState<any | null>(null);
  const [paperError, setPaperError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userText = question.trim();
    setMessages((prev) => [...prev, { sender: 'user', text_ar: userText }]);
    setQuestion('');
    setIsSending(true);

    try {
      const res = await api.askFahim(userText, contextLessonId, childId);
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
          text_en: 'Connection issue. Please review with your assigned tutor.'
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

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
        grade: 5,
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
        text_content: `Question ${qNumber} needs human tutor certification.`,
        grade: 5,
        term: 1,
        child_id: childId,
        force_escalation: true
      });
      alert('تم رفع هذا السؤال إلى قائمة المعلم الخاص للمراجعة والتصديق! (Escalated to human tutor queue)');
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
                Gemini 2.0 Flash
              </span>
            </h2>
            <p className="text-[11px] text-slate-500">
              UAE MoE Curriculum Arabic Tutor · Autonomous Exam Paper Assistant
            </p>
          </div>
        </div>

        {/* Mode Navigation Tabs */}
        <div className="flex gap-2 pt-3 pb-1 border-b border-slate-100">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors ${
              activeTab === 'chat'
                ? 'bg-purple-100 text-purple-900 border border-purple-300'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Chat Tutor (حوار مع فاهم)</span>
          </button>
          <button
            onClick={() => setActiveTab('paper')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors ${
              activeTab === 'paper'
                ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Exam Paper Assistant (مساعد أوراق الامتحانات)</span>
          </button>
        </div>

        {/* TAB 1: Chat Tutor */}
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
                      <span>Escalated to human Arabic tutor for personal guidance.</span>
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
                placeholder="Ask about ball games, words, or grammar (اسأل عن المفردات أو القواعد)..."
                className="sharp-input flex-1 text-xs rounded-xl"
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
                  📝 Sample: Term 1 MoE Exam Paper
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
                    <span>Gemini 2.0 Flash is analyzing & solving questions...</span>
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
                          <span>Model Answer · الإجابة النموذجية</span>
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
                        {q.model_answer_ar}
                      </div>
                      {q.model_answer_en && (
                        <div className="text-[11px] text-emerald-800">
                          {q.model_answer_en}
                        </div>
                      )}
                    </div>

                    {/* Explanation & Grammar Rule */}
                    <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                      <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wide">
                        Linguistic Rationale & Grammar Rule (الشرح والتعليل):
                      </div>
                      <div className="text-xs text-slate-800 text-right font-arabic leading-relaxed" dir="rtl">
                        {q.explanation_ar}
                      </div>
                      {q.explanation_en && (
                        <div className="text-[11px] text-slate-600 italic">
                          {q.explanation_en}
                        </div>
                      )}
                      {q.rule_summary_ar && (
                        <div className="mt-1 text-[11px] font-semibold text-purple-900 bg-purple-50 p-1.5 rounded border border-purple-100 text-right" dir="rtl">
                          💡 {q.rule_summary_ar}
                        </div>
                      )}
                    </div>

                    {/* Footer: Textbook Citation & Optional Escalation */}
                    <div className="flex items-center justify-between pt-1 text-[11px]">
                      <div className="flex items-center gap-1.5 text-slate-500 font-semibold">
                        <BookOpen className="w-3.5 h-3.5 text-purple-600" />
                        <span>{q.textbook_reference}</span>
                      </div>
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

