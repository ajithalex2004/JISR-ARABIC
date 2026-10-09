import React, { useState } from 'react';
import {
  User, MessageSquare, TrendingUp, ShoppingBag, Globe, GraduationCap,
  MessageCircle, LogOut, Trash2, ChevronLeft, Plus, Sparkles, Award, Wallet
} from 'lucide-react';
import { User as UserType, ChildProfile } from '../../types';
import { api } from '../../services/api';

interface ProfileViewProps {
  user: UserType | null;
  activeChild: ChildProfile | null;
  onOpenPaywall: () => void;
  onOpenOnboarding?: () => void;
  onSelectView: (view: string) => void;
  onLogout: () => void;
  onOpenAskFahim: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({
  user,
  activeChild,
  onOpenPaywall,
  onOpenOnboarding,
  onSelectView,
  onLogout,
  onOpenAskFahim
}) => {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');

  const displayName = activeChild?.name || user?.email?.split('@')[0] || 'طالب فاهم';
  const gradeText = activeChild?.default_grade
    ? `الصف ${activeChild.default_grade}`
    : (user?.children?.[0]?.default_grade ? `الصف ${user.children[0].default_grade}` : 'الصف الدراسي');

  const handleSendFeedback = () => {
    if (!feedbackText.trim()) return;
    setFeedbackSent(true);
    setTimeout(() => {
      setShowFeedbackModal(false);
      setFeedbackSent(false);
      setFeedbackText('');
    }, 1500);
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-5" dir="rtl">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-black text-[#58337E] font-arabic">حسابي</h1>
        <div className="text-xs text-slate-500 font-sans">Fahim Account</div>
      </div>

      {/* Student Profile Identity Card */}
      <div className="bg-white rounded-3xl p-5 border border-purple-100 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-[#6C5CE7] to-[#A29BFE] p-0.5 shadow-md">
              <div className="w-full h-full rounded-full bg-white flex items-center justify-center overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop&q=80"
                  alt="Student Avatar"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback to stylized icon
                    (e.currentTarget as HTMLElement).style.display = 'none';
                  }}
                />
                <div className="text-2xl font-bold text-[#6C5CE7]">
                  {displayName.charAt(0)}
                </div>
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-[#22C55E] rounded-full border-2 border-white flex items-center justify-center text-[10px] text-white">
              ✓
            </div>
          </div>

          <div>
            <h2 className="text-lg font-black text-slate-800 font-arabic">{displayName}</h2>
            <div className="mt-1 flex items-center gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#F3F0FF] text-[#6C5CE7] border border-purple-200">
                {gradeText}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                · {activeChild?.curriculum_stream || 'منهاج وزارة التربية والتعليم'}
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* General Settings Group ("عام") */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">عام (General)</h3>
        <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden divide-y divide-slate-100">
          {/* My Progress */}
          <button
            onClick={() => onSelectView('mastery')}
            className="w-full p-4 flex items-center justify-between hover:bg-purple-50/50 transition-colors text-right group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-[#22C55E] flex items-center justify-center shrink-0">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800 font-arabic group-hover:text-[#6C5CE7] transition-colors">
                  تقدمي (My Progress)
                </div>
                <div className="text-xs text-slate-400">سجل الإتقان ونقاط الضعف والقوة (Mastery & knowledge heatmap)</div>
              </div>
            </div>
            <ChevronLeft className="w-5 h-5 text-slate-400 group-hover:text-[#6C5CE7] transition-transform group-hover:-translate-x-1" />
          </button>

          {/* My Orders / Subscriptions */}
          <button
            onClick={() => onSelectView('subscriptions')}
            className="w-full p-4 flex items-center justify-between hover:bg-purple-50/50 transition-colors text-right group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800 font-arabic group-hover:text-[#6C5CE7] transition-colors">
                  طلباتي (My Subscriptions & Invoices)
                </div>
                <div className="text-xs text-slate-400">الباقات المفعلة وفواتير الاشتراك (Active packages & receipts)</div>
              </div>
            </div>
            <ChevronLeft className="w-5 h-5 text-slate-400 group-hover:text-[#6C5CE7] transition-transform group-hover:-translate-x-1" />
          </button>

          {/* Language */}
          <div className="w-full p-4 flex items-center justify-between text-right">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800 font-arabic">اللغة (Language)</div>
                <div className="text-xs text-slate-400">لغة واجهة التطبيق (App Interface Language)</div>
              </div>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
              العربية (AR)
            </span>
          </div>

          {/* Feedback & Complaints */}
          <button
            onClick={() => setShowFeedbackModal(true)}
            className="w-full p-4 flex items-center justify-between hover:bg-purple-50/50 transition-colors text-right group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-teal-100 text-teal-600 flex items-center justify-center shrink-0">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800 font-arabic group-hover:text-[#6C5CE7] transition-colors">
                  إرسال مقترحات وشكاوى (Send Feedback)
                </div>
                <div className="text-xs text-slate-400">ساعدنا في تحسين تجربة فاهم (Help us improve Fahim)</div>
              </div>
            </div>
            <ChevronLeft className="w-5 h-5 text-slate-400 group-hover:text-[#6C5CE7] transition-transform group-hover:-translate-x-1" />
          </button>
        </div>
      </div>

      {/* Account Section ("الحساب") */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">الحساب (Account)</h3>
        <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden divide-y divide-slate-100">
          {/* Logout */}
          <button
            onClick={onLogout}
            className="w-full p-4 flex items-center justify-between hover:bg-red-50/50 transition-colors text-right group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center shrink-0">
                <LogOut className="w-5 h-5" />
              </div>
              <span className="text-sm font-bold text-red-600 font-arabic">تسجيل الخروج (Log Out)</span>
            </div>
            <ChevronLeft className="w-5 h-5 text-red-300 group-hover:text-red-500 transition-transform group-hover:-translate-x-1" />
          </button>

          {/* Delete Account */}
          <button
            onClick={async () => {
              if (window.confirm('هل أنت متأكد من رغبتك في حذف الحساب نهائياً؟ سيتم محو جميع بيانات التعلم والحساب وفق معايير الخصوصية.')) {
                try {
                  await api.deleteAccount();
                  alert('تم حذف الحساب وجميع البيانات بنجاح.');
                  onLogout();
                } catch (e: any) {
                  alert(e.message || 'حدث خطأ أثناء محاولة حذف الحساب');
                }
              }
            }}
            className="w-full p-4 flex items-center justify-between hover:bg-red-50/50 transition-colors text-right group"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center shrink-0">
                <Trash2 className="w-5 h-5" />
              </div>
              <span className="text-sm font-bold text-red-600 font-arabic">حذف الحساب (Delete Account)</span>
            </div>
            <ChevronLeft className="w-5 h-5 text-red-300 group-hover:text-red-500 transition-transform group-hover:-translate-x-1" />
          </button>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4 border border-purple-100">
            <h3 className="text-base font-black text-[#58337E] font-arabic">إرسال مقترحات وملاحظات</h3>
            <p className="text-xs text-slate-500">
              يسعد فريق فهيم بتلقي رأيك لتطوير الدروس والمحادثة الذكية.
            </p>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="اكتب رسالتك أو اقتراحك هنا..."
              rows={4}
              className="w-full p-3 rounded-2xl border border-slate-200 focus:outline-none focus:border-[#6C5CE7] text-sm"
            />
            {feedbackSent ? (
              <div className="p-3 bg-emerald-50 text-[#22C55E] rounded-2xl text-center text-xs font-bold">
                تم إرسال اقتراحك بنجاح، شكراً لك!
              </div>
            ) : (
              <div className="flex items-center gap-2 justify-end">
                <button
                  onClick={() => setShowFeedbackModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-100"
                >
                  إلغاء
                </button>
                <button
                  onClick={handleSendFeedback}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-[#6C5CE7] text-white hover:bg-[#5E35B1]"
                >
                  إرسال
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
