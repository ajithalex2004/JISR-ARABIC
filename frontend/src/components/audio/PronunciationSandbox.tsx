import React, { useState } from 'react';
import { Mic, MicOff, Volume2, Play, Square, RefreshCw, Check, Sparkles, Award, AlertCircle } from 'lucide-react';
import { audioManager, SpeechRecorder } from '../../services/audio';
import { api } from '../../services/api';
import { SpeechEvaluationResult } from '../../types';

export const PronunciationSandbox: React.FC = () => {
  const [customText, setCustomText] = useState<string>('كُرَةُ الْقَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ مُمْتِعَةٌ.');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  const [speechTranscript, setSpeechTranscript] = useState<string>('');
  const [recorder] = useState<SpeechRecorder>(() => new SpeechRecorder());
  const [evaluation, setEvaluation] = useState<SpeechEvaluationResult | null>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evalError, setEvalError] = useState<string>('');

  const handleListen = () => {
    if (customText.trim()) {
      audioManager.playArabic(customText.trim());
    }
  };

  const handleToggleRecord = async () => {
    if (!isRecording) {
      setSpeechTranscript('');
      setRecordedAudioUrl(null);
      setEvaluation(null);
      setEvalError('');
      const started = await recorder.startRecording((transcript) => {
        setSpeechTranscript(transcript);
      });
      if (started) setIsRecording(true);
    } else {
      const url = await recorder.stopRecording();
      setIsRecording(false);
      setRecordedAudioUrl(url);
    }
  };

  const handleEvaluate = async () => {
    if (!customText.trim()) return;
    setIsEvaluating(true);
    setEvalError('');
    try {
      const res = await api.evaluateSpeech({
        target_phrase: customText.trim(),
        spoken_text: speechTranscript.trim() || customText.trim(),
      });
      setEvaluation(res);
    } catch (e: any) {
      setEvalError(e.message || 'Failed to evaluate speech');
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="sharp-card p-4 border border-slate-300 bg-white">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3">
        <div className="flex items-center gap-2">
          <Volume2 className="w-5 h-5 text-emerald-800" />
          <h3 className="font-bold text-slate-900 text-sm">
            Pronunciation Sandbox & Microphone Lab (مختبر النطق والتسجيل)
          </h3>
        </div>
        <span className="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5">
          Section 11 Sandbox: Edits here do not affect textbook curriculum
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Input Text to vocalize */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Type or Paste Arabic Words/Sentences to Vocalize:
          </label>
          <textarea
            rows={3}
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            className="w-full sharp-input font-arabic text-lg leading-relaxed text-right p-2.5 border-slate-400"
            dir="rtl"
            placeholder="اكتب أو الصق أي كلمة أو جملة عربية هنا..."
          />
          <div className="flex items-center justify-between mt-2">
            <button
              onClick={handleListen}
              className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <Volume2 className="w-4 h-4" />
              <span>Listen to Text (استمع)</span>
            </button>
            <div className="flex gap-1 text-[11px]">
              <button
                onClick={() => setCustomText('كُرَةٌ مُسْتَدِيرَةٌ')}
                className="px-2 py-0.5 border border-slate-300 hover:bg-slate-100 font-arabic"
              >
                كُرَةٌ مُسْتَدِيرَةٌ
              </button>
              <button
                onClick={() => setCustomText('لُعْبَةٌ جَمَاعِيَّةٌ')}
                className="px-2 py-0.5 border border-slate-300 hover:bg-slate-100 font-arabic"
              >
                لُعْبَةٌ جَمَاعِيَّةٌ
              </button>
            </div>
          </div>
        </div>

        {/* Right: Microphone speech recorder & playback */}
        <div className="border-t md:border-t-0 md:border-l border-slate-200 md:pl-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Learner Speech Practice (سجل صوتك واستمع إليه):
          </label>

          <div className="bg-slate-50 p-3 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <button
                onClick={handleToggleRecord}
                className={`px-3 py-1.5 font-bold text-xs flex items-center gap-1.5 border transition-all ${
                  isRecording
                    ? 'bg-red-700 text-white border-red-800 animate-pulse'
                    : 'bg-emerald-900 text-white border-emerald-950 hover:bg-emerald-800'
                }`}
              >
                {isRecording ? (
                  <>
                    <MicOff className="w-4 h-4" />
                    <span>Stop Recording</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4" />
                    <span>Record Voice (سجل)</span>
                  </>
                )}
              </button>

              {recordedAudioUrl && (
                <audio controls src={recordedAudioUrl} className="h-8 max-w-[200px]" />
              )}
            </div>

            {isRecording && (
              <div className="text-xs text-red-700 flex items-center gap-1 font-semibold animate-pulse">
                <span className="w-2 h-2 rounded-full bg-red-600"></span>
                <span>Listening to microphone input... Speak clearly in Arabic</span>
              </div>
            )}

            {speechTranscript && (
              <div className="mt-2 text-xs border border-emerald-300 bg-emerald-50 p-2 text-right font-arabic">
                <span className="text-slate-500 text-[10px] block text-left font-sans">Recognized Speech:</span>
                <span className="text-emerald-950 font-bold">{speechTranscript}</span>
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-slate-200">
              <button
                onClick={handleEvaluate}
                disabled={isEvaluating}
                className="w-full btn-primary text-xs py-2 px-3 flex items-center justify-center gap-2 bg-[#58337E] hover:bg-[#432363] text-white disabled:opacity-50"
              >
                {isEvaluating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>جارٍ تقييم النطق وفق معايير الوزارة...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span className="font-bold">تقييم النطق وفق المعايير الوزارية (Evaluate Rubric)</span>
                  </>
                )}
              </button>

              {evalError && (
                <div className="mt-2 text-xs text-red-600 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  <span>{evalError}</span>
                </div>
              )}

              {evaluation && (
                <div className="mt-3 p-3 bg-white border border-purple-200 rounded-lg space-y-2">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-purple-600" />
                      <span className="text-xs font-bold text-slate-800">
                        {evaluation.fluency_rating} ({evaluation.accuracy_percentage.toFixed(0)}%)
                      </span>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      evaluation.is_pass ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {evaluation.is_pass ? 'مجتاز بنجاح (Passed)' : 'يحتاج تدريباً (Needs Practice)'}
                    </span>
                  </div>

                  <p className="text-xs font-arabic text-right text-slate-700 leading-relaxed" dir="rtl">
                    {evaluation.feedback_ar}
                  </p>

                  {evaluation.phoneme_scores && Object.keys(evaluation.phoneme_scores).length > 0 && (
                    <div className="pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-bold text-slate-500 block mb-1.5">
                        تحليل الفونيمات ومخارج الحروف (MoE Phoneme Accuracy):
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(evaluation.phoneme_scores).map(([ph, sc]) => {
                          const pct = Math.round(Number(sc) * 100);
                          const isHigh = pct >= 80;
                          return (
                            <span
                              key={ph}
                              className={`text-[11px] font-arabic px-2 py-0.5 rounded border font-bold ${
                                isHigh
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                  : 'bg-amber-50 text-amber-700 border-amber-200'
                              }`}
                            >
                              حرف ({ph}): {pct}%
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {evaluation.detected_mistakes && evaluation.detected_mistakes.length > 0 && (
                    <div className="text-[11px] text-amber-800 bg-amber-50 p-2 rounded border border-amber-200 font-arabic text-right" dir="rtl">
                      <span className="font-bold block mb-1">ملاحظات دقة الحروف:</span>
                      {evaluation.detected_mistakes.map((m, idx) => (
                        <div key={idx}>• {m}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <p className="text-[11px] text-slate-500 mt-2">
              Microphone recordings stay private to this browser session unless explicitly submitted for tutor review.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
