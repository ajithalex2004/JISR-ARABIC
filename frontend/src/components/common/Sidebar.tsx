import React from 'react';
import {
  BookOpen, BookText, Clock, FlaskConical, Sparkles,
  Target, Trophy, User as UserIcon, LogOut,
  Smartphone, Monitor, ChevronRight, CheckCircle, ShieldCheck, Settings
} from 'lucide-react';
import { User, ChildProfile } from '../../types';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';

interface SidebarProps {
  user: User | null;
  activeChild: ChildProfile | null;
  currentView: string;
  onSelectView: (view: string) => void;
  onOpenAuth: () => void;
  onLogout: () => void;
  onOpenAskFahim: () => void;
  isMobileSimulator: boolean;
  onToggleMobileSimulator: () => void;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

const AVATAR_ICONS: Record<string, string> = {
  avatar_falcon: '🦅',
  avatar_gazelle: '🦌',
  avatar_camel: '🐪',
  avatar_oryx: '🦄',
  avatar_horse: '🐎',
};

export const Sidebar: React.FC<SidebarProps> = ({
  user,
  activeChild,
  currentView,
  onSelectView,
  onOpenAuth,
  onLogout,
  onOpenAskFahim,
  isMobileSimulator,
  onToggleMobileSimulator,
  isOpenMobile = false,
  onCloseMobile
}) => {
  const activeAvatar = AVATAR_ICONS[activeChild?.avatar_id || 'avatar_falcon'] || '🦅';

  const menuItems = [
    {
      id: 'catalogue',
      titleEn: 'Curriculum & Lessons',
      titleAr: 'المنهاج والدروس',
      icon: BookOpen,
      badge: 'Ch. 1 Active',
      isView: (v: string) => v === 'catalogue' || v === 'lesson'
    },
    {
      id: 'reader',
      titleEn: 'Scanned Textbook (108 p.)',
      titleAr: 'الكتاب المدرسي الممسوح',
      icon: BookOpen,
      badge: 'Ch. 1 Full (p. 6–15)',
      isView: (v: string) => v === 'reader'
    },
    {
      id: 'malazim',
      titleEn: 'Smart Study Booklets',
      titleAr: 'الملازم الذكية',
      icon: BookText,
      badge: '15-Min Notes',
      isView: (v: string) => v === 'malazim'
    },
    {
      id: 'capsules',
      titleEn: 'Learning Capsules',
      titleAr: 'الكبسولات التعليمية',
      icon: Clock,
      badge: '3–5 Min',
      isView: (v: string) => v === 'capsules'
    },
    {
      id: 'tests',
      titleEn: 'MoE Exam Simulation',
      titleAr: 'محاكاة الامتحانات',
      icon: FlaskConical,
      badge: 'MoE Model',
      isView: (v: string) => v === 'tests'
    },
    ...(user?.role === 'learner' ? [] : [{
      id: 'ask_fahim',
      titleEn: 'Ask Fahim (AI Tutor)',
      titleAr: 'اسأل فهيم',
      icon: Sparkles,
      action: onOpenAskFahim,
      highlight: true
    }, {
      id: 'mastery',
      titleEn: 'Mastery Heatmap',
      titleAr: 'لوحة الإتقان',
      icon: Target,
      isView: (v: string) => v === 'mastery'
    }, {
      id: 'ranks',
      titleEn: 'Ranks & Badges',
      titleAr: 'الأوسمة والإنجازات',
      icon: Trophy,
      isView: (v: string) => v === 'ranks'
    }]),
    {
      id: 'profile',
      titleEn: 'Student Profile',
      titleAr: 'الملف الشخصي',
      icon: UserIcon,
      isView: (v: string) => v === 'profile'
    },
    {
      id: 'admin',
      titleEn: 'Admin & PDF Library',
      titleAr: 'لوحة الإدارة ومكتبة الكتب',
      icon: Settings,
      badge: 'MoE 30 Books',
      isView: (v: string) => v === 'admin'
    }
  ];

  const handleNav = (item: any) => {
    if (item.action) {
      item.action();
    } else {
      onSelectView(item.id);
    }
    if (onCloseMobile) onCloseMobile();
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-72 bg-white border-r border-purple-100 flex flex-col justify-between transition-transform duration-300 ease-in-out shadow-xl lg:shadow-none lg:translate-x-0 ${
        isOpenMobile ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* 1. Brand Logo & Identity */}
      <div>
        <div className="p-5 border-b border-purple-100 bg-gradient-to-b from-purple-50/50 to-transparent">
          <div
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => handleNav({ id: 'catalogue' })}
          >
            <img
              src="/logo.svg"
              alt="JISR Logo"
              className="w-11 h-11 rounded-2xl shadow-md transform hover:scale-105 transition-transform object-cover"
            />
            <div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black tracking-tight text-[#58337E] font-sans">JISR</span>
                <span className="text-xl font-bold font-arabic text-[#10B981]">جِــسْـــر</span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium tracking-wide">
                UAE Arabic Platform · <ArabicWordSpans text="مِنْهَاجُ اللُّغَةِ العَرَبِيَّةِ" tooltipPlacement="bottom" className="text-slate-600 font-semibold" />
              </p>
            </div>
          </div>

          {/* Active Student Status Box */}
          <div className="mt-4 p-3 rounded-2xl bg-[#F8F6FF] border border-purple-100 flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-2.5 truncate">
              <div className="w-9 h-9 rounded-xl bg-white border border-purple-200 text-lg flex items-center justify-center shadow-xs shrink-0">
                {activeAvatar}
              </div>
              <div className="truncate">
                <div className="text-xs font-bold text-slate-900 truncate">
                  {activeChild?.name || user?.email?.split('@')[0] || 'Guest Student'}
                </div>
                <div className="text-[10px] text-[#6C5CE7] font-semibold flex items-center gap-1">
                  <span>الصف {activeChild?.default_grade || 5}</span>
                  <span className="text-slate-300">•</span>
                  <span>Grade {activeChild?.default_grade || 5} {activeChild?.curriculum_stream ? (activeChild.curriculum_stream.includes('Non-Arabs') || activeChild.curriculum_stream.includes('B') ? 'Arabic B' : activeChild.curriculum_stream) : 'Arabic B'}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center text-[#22C55E]" title="Verified UAE MoE Curriculum">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* 2. Navigation Menu */}
        <nav className="p-3 space-y-1.5 overflow-y-auto max-h-[calc(100vh-280px)] scrollbar-thin">
          <div className="px-3 pt-1 pb-1 text-[10px] uppercase font-extrabold tracking-wider text-slate-400">
            Navigation Menu (القائمة الرئيسية)
          </div>

          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.isView ? item.isView(currentView) : false;
            const isHighlighted = item.highlight;

            return (
              <button
                key={item.id}
                onClick={() => handleNav(item)}
                className={`w-full text-left px-3.5 py-2.5 rounded-2xl flex items-center justify-between transition-all group ${
                  isActive
                    ? 'bg-[#6C5CE7] text-white font-bold shadow-md shadow-purple-500/20'
                    : isHighlighted
                    ? 'bg-gradient-to-r from-purple-50 to-amber-50 text-[#58337E] font-bold border border-purple-200/80 hover:border-purple-300 hover:shadow-xs'
                    : 'text-slate-700 hover:bg-purple-50 hover:text-[#58337E] font-semibold'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : isHighlighted
                        ? 'bg-purple-100 text-[#6C5CE7]'
                        : 'bg-slate-100 text-slate-500 group-hover:bg-purple-100 group-hover:text-[#6C5CE7]'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs leading-tight flex items-center gap-1.5">
                      <span>{item.titleEn}</span>
                    </div>
                    <div
                      className={`text-[11px] font-arabic font-bold ${
                        isActive ? 'text-purple-100' : 'text-slate-500 group-hover:text-purple-700'
                      }`}
                      dir="rtl"
                    >
                      {item.titleAr}
                    </div>
                  </div>
                </div>

                {isHighlighted ? (
                  <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
                ) : (
                  <ChevronRight
                    className={`w-4 h-4 transition-transform group-hover:translate-x-0.5 ${
                      isActive ? 'text-white/80' : 'text-slate-300 group-hover:text-purple-400'
                    }`}
                  />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* 3. Footer Controls */}
      <div className="p-4 border-t border-purple-100 space-y-2.5 bg-slate-50/70">
        {/* Toggle Mobile App Simulator */}
        <button
          onClick={onToggleMobileSimulator}
          className="w-full px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-white border border-slate-200/80 flex items-center justify-between transition-colors shadow-2xs"
          title="Toggle Mobile Simulator"
        >
          <div className="flex items-center gap-2">
            {isMobileSimulator ? (
              <Monitor className="w-3.5 h-3.5 text-purple-600" />
            ) : (
              <Smartphone className="w-3.5 h-3.5 text-emerald-600" />
            )}
            <span>{isMobileSimulator ? 'Switch to Desktop View' : 'Mobile App Simulator'}</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">Sim</span>
        </button>

        {/* User Session: Login or Logout */}
        {user ? (
          <button
            onClick={onLogout}
            className="w-full px-3 py-2 rounded-xl text-xs font-bold text-red-600 hover:bg-red-50 flex items-center justify-center gap-2 transition-colors border border-red-100"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>تسجيل الخروج (Sign Out)</span>
          </button>
        ) : (
          <button
            onClick={() => {
              onOpenAuth();
              if (onCloseMobile) onCloseMobile();
            }}
            className="w-full py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-[#6C5CE7] to-[#8E44AD] hover:opacity-95 shadow-md shadow-purple-500/20 flex items-center justify-center gap-2 transition-transform transform active:scale-95"
          >
            <UserIcon className="w-3.5 h-3.5 text-purple-200" />
            <span>تسجيل الدخول / حساب جديد</span>
          </button>
        )}
      </div>
    </aside>
  );
};
