import React, { useState, useEffect } from 'react';
import { UserCheck, CheckCircle2, Clock, Send, MessageSquare, Volume2 } from 'lucide-react';
import { api } from '../../services/api';

export const TutorDashboard: React.FC = () => {
  const [queue, setQueue] = useState<any[]>([]);
  const [selectedSub, setSelectedSub] = useState<any | null>(null);
  const [score, setScore] = useState<number>(8.5);
  const [feedback, setFeedback] = useState<string>('');
  const [filter, setFilter] = useState<'pending' | 'reviewed' | 'all'>('pending');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    loadQueue();
  }, [filter]);

  const loadQueue = async () => {
    setIsLoading(true);
    try {
      const data = await api.getTutorQueue(filter);
      setQueue(data);
      if (data.length > 0 && !selectedSub) {
        setSelectedSub(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReview = async () => {
    if (!selectedSub) return;
    setIsSubmitting(true);
    try {
      await api.reviewTutorSubmission({
        submission_id: selectedSub.id,
        tutor_score: score,
        tutor_feedback: feedback || 'أحسنت في الصياغة وترتيب الأفكار. انتبه لتطابق المذكر والمؤنث في الصفات.'
      });
      loadQueue();
      setSelectedSub(null);
      setFeedback('');
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      {/* Top Banner */}
      <div className="sharp-card p-5 border-l-4 border-l-emerald-900 bg-white flex justify-between items-center">
        <div>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Assigned Arabic Tutor Queue (بوابة المعلم الخصوصي)
          </span>
          <h1 className="text-xl font-black text-slate-900">
            Student Submissions Review & Rubric Evaluation
          </h1>
        </div>

        {/* Filter */}
        <div className="flex gap-1 border border-slate-300 p-1 bg-slate-50">
          {(['pending', 'reviewed', 'all'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 text-xs font-bold capitalize transition-all ${
                filter === f ? 'bg-emerald-900 text-white' : 'bg-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Submissions Queue List (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Submissions Queue ({queue.length}):
          </h2>

          {queue.length === 0 ? (
            <div className="sharp-card p-8 text-center bg-white border border-slate-300 text-xs text-slate-500">
              No submissions found for filter '{filter}'.
            </div>
          ) : (
            queue.map((sub) => {
              const isSelected = selectedSub?.id === sub.id;
              return (
                <div
                  key={sub.id}
                  onClick={() => setSelectedSub(sub)}
                  className={`sharp-card p-4 border-2 cursor-pointer transition-all ${
                    isSelected ? 'border-emerald-900 bg-emerald-50/40 shadow-sm' : 'border-slate-300 bg-white hover:border-slate-400'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-slate-900 text-sm">{sub.child_name}</span>
                    <span className={`px-2 py-0.5 text-[10px] font-bold uppercase ${
                      sub.status === 'pending' ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                    }`}>
                      {sub.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-600">
                    {sub.school_name} · Grade {sub.grade}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono mt-1">
                    Type: {sub.submission_type} · Activity: {sub.activity_id}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Rubric Grading & Detailed Evaluation Workspace (7 cols) */}
        <div className="lg:col-span-7">
          {selectedSub ? (
            <div className="sharp-card p-6 border-2 border-slate-900 bg-white space-y-4">
              <div className="border-b border-slate-200 pb-3 flex justify-between items-baseline">
                <div>
                  <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider block">
                    Evaluating Student Submission
                  </span>
                  <h3 className="text-base font-black text-slate-900">
                    {selectedSub.child_name} · Class {selectedSub.grade}
                  </h3>
                </div>
                <span className="text-xs text-slate-500 font-mono">
                  {selectedSub.created_at.split('T')[0]}
                </span>
              </div>

              {/* Submitted Content Display */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Student's Written Work (عمل الطالب):
                </label>
                <div className="p-4 bg-slate-50 border border-slate-300 font-arabic text-lg text-right text-slate-900 min-h-[100px]" dir="rtl">
                  {selectedSub.content_text || 'No text submitted.'}
                </div>
              </div>

              {/* Submitted Audio if available */}
              {selectedSub.audio_url && (
                <div className="p-3 bg-emerald-50 border border-emerald-300 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-emerald-950">
                    <Volume2 className="w-4 h-4 text-emerald-700" />
                    <span>Student Voice Recording:</span>
                  </div>
                  <audio controls src={selectedSub.audio_url} className="h-8" />
                </div>
              )}

              {/* Rubric Score Slider/Input */}
              <div className="space-y-1 pt-2 border-t border-slate-200">
                <div className="flex justify-between text-xs font-bold text-slate-800">
                  <span>Rubric Score:</span>
                  <span className="font-mono text-emerald-900 text-sm">{score} / 10 Marks</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={10}
                  step={0.5}
                  value={score}
                  onChange={(e) => setScore(parseFloat(e.target.value))}
                  className="w-full accent-emerald-800 cursor-pointer"
                />
              </div>

              {/* Feedback Textarea */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-700 block">
                  Constructive Feedback (ملاحظات المعلم وتوجيهاته):
                </label>
                <textarea
                  rows={3}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="اكتب ملاحظاتك وتوجيهاتك للطالب هنا..."
                  className="sharp-input w-full text-xs font-arabic text-right p-2.5"
                  dir="rtl"
                />
              </div>

              <button
                onClick={handleReview}
                disabled={isSubmitting}
                className="btn-primary w-full py-2.5 text-xs flex items-center justify-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{isSubmitting ? 'Saving Review...' : 'Save Feedback & Finalize Grade'}</span>
              </button>
            </div>
          ) : (
            <div className="sharp-card p-12 text-center bg-white border border-slate-300 text-slate-500 text-xs">
              Select a submission from the queue on the left to grade and review.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
