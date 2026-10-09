import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles, Mic, MicOff, Send, Volume2, Lightbulb, CheckCircle2,
  RefreshCw, GraduationCap, Award, HelpCircle
} from 'lucide-react';
import { api } from '../../services/api';
import { audioManager } from '../../services/audio';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ChildProfile } from '../../types';

interface SocraticLearnStudioProps {
  activeChild: ChildProfile | null;
}

interface SocraticMessage {
  id: string;
  sender: 'student' | 'fahim';
  text_ar: string;
  text_en?: string;
  guiding_hint_ar?: string;
  guiding_hint_en?: string;
  is_mastered?: boolean;
  tone?: string;
}

const SAMPLE_TOPICS = [
  { id: 'taa_marbutah', title_ar: 'التاء المربوطة والهاء', title_en: 'Taa Marbutah vs. Haa' },
  { id: 'verb_subject', title_ar: 'مطابقة الفعل للفاعل', title_en: 'Subject-Verb Agreement' },
  { id: 'ball_games', title_ar: 'قوانين ألعاب الكرة', title_en: 'Ball Games Rules & Pitch' },
  { id: 'nominal_sentence', title_ar: 'الجملة الاسمية والخبر', title_en: 'Nominal Sentence & Predicate' }
];

export const SocraticLearnStudio: React.FC<SocraticLearnStudioProps> = ({ activeChild }) => {
  const availableGrades = React.useMemo(() => {
    if (activeChild?.default_grade) {
      return [activeChild.default_grade];
    }
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  }, [activeChild]);

  const [selectedTopic, setSelectedTopic] = useState<string>('التاء المربوطة والهاء');
  const [grade, setGrade] = useState<number>(activeChild?.default_grade || 5);

  useEffect(() => {
    if (activeChild?.default_grade) {
      setGrade(activeChild.default_grade);
    }
  }, [activeChild]);
  const [inputText, setInputText] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showHint, setShowHint] = useState<boolean>(false);
  const [speechSupported, setSpeechSupported] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<SocraticMessage[]>([
    {
      id: 'init_1',
      sender: 'fahim',
      text_ar: 'مَرْحَبًا بِكَ فِي جَلْسَةِ التَّعَلُّمِ السُّقْرَاطِيِّ (تَعَلَّمْ مَعَ فَاهِم)! لَنْ أُعْطِيَكَ الحَلَّ مُبَاشَرَةً، بَلْ سَنَفْكُرُ مَعًا خَطْوَةً بِخَطْوَةٍ. عَمَّ تُرِيدُ أَنْ نَتَحَاوَرَ اليَوْمَ؟',
      text_en: "Welcome to Socratic Learn! I won't simply give you answers; we'll reason step-by-step together. What shall we explore today?",
      tone: grade <= 5 ? 'primary_gamified' : 'middle_academic'
    }
  ]);

  // Check Web Speech Recognition support
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        setSpeechSupported(true);
        const recog = new SpeechRecognition();
        recog.continuous = false;
        recog.interimResults = false;
        recog.lang = 'ar-SA';

        recog.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInputText(transcript);
          setIsListening(false);
        };

        recog.onerror = () => setIsListening(false);
        recog.onend = () => setIsListening(false);
        recognitionRef.current = recog;
      }
    }
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const toggleMic = () => {
    if (!speechSupported || !recognitionRef.current) {
      alert('خاصية التعرف الصوتي غير مدعومة في هذا المتصفح. استخدم Chrome أو Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setInputText('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = inputText.trim();
    if (!query || isLoading) return;

    const userMsg: SocraticMessage = {
      id: `user_${Date.now()}`,
      sender: 'student',
      text_ar: query
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);
    setShowHint(false);

    try {
      const res = await api.socraticLearn({
        topic: selectedTopic,
        student_input: query,
        grade: grade,
        child_id: activeChild?.id
      });

      const fahimMsg: SocraticMessage = {
        id: `fahim_${Date.now()}`,
        sender: 'fahim',
        text_ar: res.response_ar,
        text_en: res.response_en,
        guiding_hint_ar: res.guiding_hint_ar,
        guiding_hint_en: res.guiding_hint_en,
        is_mastered: res.is_step_mastered,
        tone: res.tone
      };

      setMessages((prev) => [...prev, fahimMsg]);
      // Play speech audio automatically
      audioManager.playArabic(res.response_ar);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'fahim',
          text_ar: 'عُذْرًا، وَاجَهْنَا خَلَلًا فِي الِاتِّصَالِ بِمُعَلِّمِكَ السُّقْرَاطِيِّ. حَاوِلْ مَرَّةً أُخْرَى.',
          text_en: 'Connection issue. Please retry your inquiry.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const latestFahimMessage = [...messages].reverse().find(m => m.sender === 'fahim');

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Module Title Banner */}
      <div className="bg-slate-900 text-white border-2 border-slate-900 p-6 mb-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-amber-500 text-slate-950 text-[11px] font-black uppercase px-2 py-0.5 tracking-wider">
              Module 3.1 · ركيزة التعلّم الذكي
            </span>
            <span className="text-slate-400 text-xs">
              Socratic Guidance & Dual Audio Modality
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight">
            Learn with Fahim · تَعَلَّمْ مَعَ فَاهِم (الحوار السقراطي)
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
            المعلم الذكي لا يلقنك الإجابة الجاهزة، بل يطرح عليك أسئلة موجهة ويقدم لك تلميحات متدرجة لتبني استنتاجك بنفسك.
          </p>
          <p className="text-xs text-slate-400 mt-1 italic font-sans">
            Ustadh Fahim doesn't hand out direct answers, but guides you with step-by-step Socratic hints to reach understanding.
          </p>
        </div>

        {/* Tone & Grade Switcher */}
        <div className="bg-slate-800 border border-slate-700 p-3 flex flex-col gap-2 min-w-[200px]">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">نبرة الحوار (Tone):</span>
            <span className="font-bold text-amber-400 flex items-center gap-1">
              {grade <= 5 ? (
                <>
                  <Award className="w-3.5 h-3.5" />
                  <span>تأسيسي تفاعلي (Primary)</span>
                </>
              ) : (
                <>
                  <GraduationCap className="w-3.5 h-3.5" />
                  <span>أكاديمي تحليلي (Academic)</span>
                </>
              )}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <label className="text-slate-400 text-[11px]">الصف الدراسي (Grade):</label>
            <select
              value={grade}
              onChange={(e) => setGrade(Number(e.target.value))}
              className="bg-slate-900 text-white text-xs px-2 py-1 border border-slate-600 focus:outline-none focus:border-emerald-500"
            >
              {availableGrades.map((g) => (
                <option key={g} value={g}>
                  الصف {g} (Grade {g})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Topics Selector Pills */}
      <div className="mb-4">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
          اختر موضوع الحوار السقراطي (Select Socratic Topic):
        </label>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_TOPICS.map((topic) => (
            <button
              key={topic.id}
              onClick={() => setSelectedTopic(topic.title_ar)}
              className={`px-3 py-1.5 text-xs font-bold border-2 transition-all ${
                selectedTopic === topic.title_ar
                  ? 'bg-emerald-900 text-white border-emerald-950'
                  : 'bg-white text-slate-800 border-slate-300 hover:border-slate-800'
              }`}
            >
              <span>{topic.title_ar}</span>
              <span className="text-[10px] opacity-70 ml-1.5 font-normal">({topic.title_en})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Dialogue Panel */}
      <div className="bg-white border-2 border-slate-900 shadow-sm flex flex-col h-[520px]">
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 border-b border-slate-200">
          {messages.map((m) => {
            const isUser = m.sender === 'student';
            return (
              <div
                key={m.id}
                className={`flex flex-col max-w-[85%] ${isUser ? 'ml-auto items-end' : 'mr-auto items-start'}`}
              >
                <div className="flex items-center gap-2 mb-1 px-1">
                  <span className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                    {isUser ? `${activeChild?.name || 'Student'} (أَنْتَ)` : 'Ustadh Fahim (الأُسْتَاذُ فَاهِم)'}
                  </span>
                  {!isUser && (
                    <button
                      onClick={() => audioManager.playArabic(m.text_ar)}
                      className="text-emerald-800 hover:text-emerald-950 p-0.5"
                      title="استمع إلى النطق الصوتي"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div
                  className={`p-3.5 text-sm border ${
                    isUser
                      ? 'bg-emerald-900 text-white border-emerald-950'
                      : 'bg-white text-slate-900 border-slate-300 shadow-sm'
                  }`}
                >
                  <div className="text-base text-right leading-relaxed" dir="rtl">
                    <ArabicWordSpans text={m.text_ar} className={`text-base font-bold ${isUser ? 'text-white' : 'text-slate-900'}`} />
                  </div>
                  {m.text_en && (
                    <div className="text-[11px] text-slate-500 mt-1.5 pt-1.5 border-t border-slate-100 italic">
                      {m.text_en}
                    </div>
                  )}

                  {m.is_mastered && (
                    <div className="mt-2.5 bg-emerald-50 border border-emerald-300 p-2 flex items-center gap-2 text-emerald-900 text-xs font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-700 flex-shrink-0" />
                      <span>أحسنت! تم إتقان هذه الخطوة المنطقية بنجاح 🌟</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex items-center gap-2 p-3 bg-white border border-slate-200 text-xs text-slate-600 w-fit">
              <RefreshCw className="w-3.5 h-3.5 text-emerald-800 animate-spin" />
              <span>المعلم فاهم يحلل إجابتك ويصيغ سؤالاً توجيهياً... (Ustadh Fahim is analyzing...)</span>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Guiding Hint Strip (Socratic Scaffolding) */}
        {latestFahimMessage?.guiding_hint_ar && (
          <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-amber-950 font-bold">
              <Lightbulb className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>تلميح إرشادي (Guiding Hint):</span>
              {showHint ? (
                <div className="flex flex-col">
                  <span className="font-normal text-slate-800"><ArabicWordSpans text={latestFahimMessage.guiding_hint_ar} /></span>
                  {latestFahimMessage.guiding_hint_en && (
                    <span className="text-[11px] text-slate-500 font-sans italic" dir="ltr">{latestFahimMessage.guiding_hint_en}</span>
                  )}
                </div>
              ) : (
                <span className="text-slate-500 italic">هل أنت محتار؟ اضغط لإظهار التلميح الإرشادي (Need help? Click to show hint)</span>
              )}
            </div>
            <button
              onClick={() => setShowHint(!showHint)}
              className="text-amber-800 hover:text-amber-950 underline font-bold text-[11px]"
            >
              {showHint ? 'إخفاء التلميح (Hide Hint)' : 'إظهار التلميح (Show Hint)'}
            </button>
          </div>
        )}

        {/* Input Bar with Voice Recognition & Text Submission */}
        <form onSubmit={handleSend} className="p-3 bg-slate-100 flex items-center gap-2">
          {speechSupported && (
            <button
              type="button"
              onClick={toggleMic}
              className={`p-2.5 border-2 transition-all flex items-center justify-center ${
                isListening
                  ? 'bg-rose-600 text-white border-rose-800 animate-pulse'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-slate-800'
              }`}
              title={isListening ? 'جاري الاستماع... اضغط للإيقاف' : 'تحدث باللغة العربية (Voice Input)'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-emerald-800" />}
            </button>
          )}

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isListening ? 'تحدث الآن، جارٍ تحويل صوتك إلى نص... (Listening...)' : 'اكتب استنتاجك أو فكرتك هنا (Type your response or use mic)...'}
            className="flex-1 bg-white border border-slate-300 px-3.5 py-2 text-sm text-slate-900 focus:outline-none focus:border-emerald-800"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="bg-emerald-900 text-white border-2 border-slate-900 px-4 py-2 text-xs font-bold uppercase tracking-wider hover:bg-emerald-800 transition-colors disabled:opacity-50 flex items-center gap-1.5"
          >
            <span>إرسال (Send)</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
