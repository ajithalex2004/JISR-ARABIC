import React, { useState, useRef, useEffect } from 'react';
import {
  User as UserIcon, Sparkles, Smartphone,
  Monitor, LogOut, CheckCircle, ChevronDown, Plus, Users, Compass, Menu
} from 'lucide-react';
import { User, ChildProfile } from '../../types';
import { ArabicWordSpans } from '../audio/ArabicWordSpans';
import { ArabEnglishToggleSwitch } from './ArabEnglishToggleSwitch';


const AVATAR_ICONS: Record<string, string> = {
  avatar_falcon: '🦅',
  avatar_gazelle: '🦌',
  avatar_oryx: '🦬',
  avatar_camel: '🐪',
  avatar_palm: '🌴',
};


interface HeaderProps {
  user: User | null;
  activeChild: ChildProfile | null;
  selectedGrade?: number;
  childrenList?: ChildProfile[];
  onSwitchChild?: (childId: string) => void;
  onOpenAddChild?: () => void;
  onOpenOnboarding?: () => void;
  currentView: string;
  onSelectView: (view: string) => void;
  onOpenAuth: () => void;
  onLogout: () => void;
  onOpenAskFahim: () => void;
  isMobileSimulator: boolean;
  onToggleMobileSimulator: () => void;
  onToggleMobileMenu?: () => void;
}


export const Header: React.FC<HeaderProps> = ({
  user,
  activeChild,
  selectedGrade,
  childrenList = [],
  onSwitchChild,
  onOpenAddChild,
  onOpenOnboarding,
  onSelectView,
  onOpenAuth,
  onLogout,
  onOpenAskFahim,
  isMobileSimulator,
  onToggleMobileSimulator,
  onToggleMobileMenu
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);


  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);


  const allChildren = childrenList.length > 0 ? childrenList : (user?.children || []);
  const activeAvatar = AVATAR_ICONS[activeChild?.avatar_id || 'avatar_falcon'] || '🦅';


  return (
    <header className="border-b border-purple-100 bg-white/95 backdrop-blur-md sticky top-0 z-30 shadow-xs">
      {/* Top utility banner */}
      <div className="bg-[#58337E] text-white text-xs px-4 py-1.5 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="bg-[#22C55E] text-white font-bold px-2 py-0.5 rounded-full uppercase text-[10px] tracking-wider shadow-xs">
            UAE MoE & CBSE Aligned
          </span>
          <span className="hidden sm:inline text-purple-200">
            <ArabicWordSpans text="العَرَبِيَّةُ تَجْمَعُنَا" tooltipPlacement="bottom" className="text-purple-200 font-semibold" /> · Modern Standard Arabic for Non-Native Learners
          </span>
        </div>
        <div className="flex items-center gap-3">
          <ArabEnglishToggleSwitch compact />
          <span className="text-purple-300/40">|</span>
          <button
            onClick={onToggleMobileSimulator}
            className="flex items-center gap-1.5 hover:text-white transition-colors text-purple-200 text-xs px-2 py-0.5 rounded-lg hover:bg-white/10"
            title="Toggle Mobile App Simulator"
          >
            {isMobileSimulator ? (
              <>
                <Monitor className="w-3.5 h-3.5 text-amber-300" />
                <span>Web View</span>
              </>
            ) : (
              <>
                <Smartphone className="w-3.5 h-3.5 text-emerald-300" />
                <span>Mobile App View</span>
              </>
            )}
          </button>
          <span className="text-purple-300/40">|</span>
          <span className="text-purple-200 text-[11px] font-semibold">Fahim v2.4</span>
        </div>
      </div>


      {/* Main header row */}
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex justify-between items-center gap-4">
        {/* Mobile Hamburger Menu Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 rounded-xl text-slate-700 hover:bg-purple-50 hover:text-[#6C5CE7] transition-colors"
            title="Open Menu"
          >
            <Menu className="w-5 h-5" />
          </button>


          <div className="lg:hidden flex items-center gap-2">
            <img src="/logo.svg" alt="JISR" className="w-7 h-7 rounded-lg shadow-xs object-cover" />
            <span className="font-black text-[#58337E] text-sm">JISR · <span className="text-[#10B981] font-arabic">جسر</span></span>
          </div>


          {/* Curriculum indicator for desktop */}
          <div className="hidden lg:flex items-center gap-2 text-xs">
            <span className="font-bold text-[#58337E] font-arabic text-sm">
              <ArabicWordSpans text="مِنْهَاجُ اللُّغَةِ العَرَبِيَّةِ" tooltipPlacement="bottom" />
            </span>
            <span className="text-slate-300">|</span>
            <span className="text-slate-500 font-medium">
              Class {selectedGrade || activeChild?.default_grade || 5} · {activeChild?.curriculum_stream ? activeChild.curriculum_stream.split('/')[0].trim() : 'MoE Arabic'}
            </span>
          </div>
        </div>


        {/* Action Controls & User Identity */}
        <div className="flex items-center gap-2.5">
          {/* Onboarding / Level Calibration Button */}
          {activeChild && onOpenOnboarding && (
            <button
              onClick={onOpenOnboarding}
              className={`text-xs py-1.5 px-3 rounded-full flex items-center gap-1.5 font-bold transition-all shadow-xs ${
                activeChild.diagnostic_completed
                  ? 'bg-purple-50 text-[#6C5CE7] border border-purple-200 hover:bg-purple-100'
                  : 'bg-amber-400 text-slate-950 hover:bg-amber-300 animate-pulse'
              }`}
              title="Calibrate AI Difficulty & View Personalized Learning Plan"
            >
              <Compass className="w-3.5 h-3.5 text-[#6C5CE7]" />
              <span className="hidden sm:inline">
                {activeChild.diagnostic_completed ? 'الخطة التعليمية' : 'معايرة المستوى'}
              </span>
            </button>
          )}


          {/* Arab-English Pronunciation Toggle */}
          <div className="hidden sm:flex">
            <ArabEnglishToggleSwitch />
          </div>

          {/* Ask Fahim AI Assistant Button */}
          <button
            onClick={onOpenAskFahim}
            className="text-xs py-2 px-3.5 rounded-full flex items-center gap-1.5 shadow-md bg-gradient-to-r from-[#6C5CE7] to-[#8E44AD] text-white font-bold transform hover:scale-105 active:scale-95 transition-all"
            title="Ask Fahim - Your Conversational Arabic Teacher"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>اسأل فهيم</span>
          </button>


          {/* User Session Profile & Multi-Child Switcher */}
          {user ? (
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 py-1 px-2 rounded-2xl bg-white border border-purple-100 hover:border-purple-300 hover:bg-purple-50/50 transition-all shadow-xs"
              >
                {activeChild ? (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#6C5CE7] to-[#A29BFE] text-white flex items-center justify-center text-sm shadow-xs">
                    {activeAvatar}
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-purple-100 text-[#6C5CE7] flex items-center justify-center">
                    <UserIcon className="w-4 h-4" />
                  </div>
                )}
                <div className="text-left text-xs pr-1">
                  <div className="font-bold text-slate-800 flex items-center gap-1">
                    <span>{activeChild?.name || user.email.split('@')[0]}</span>
                    <ChevronDown className="w-3 h-3 text-slate-400" />
                  </div>
                  <div className="text-[#6C5CE7] text-[10px] font-semibold">
                    {user?.role === 'admin' ? `مسؤول (الصف ${selectedGrade || 5})` : activeChild ? `الصف ${selectedGrade || activeChild.default_grade || 5} · Grade ${selectedGrade || activeChild.default_grade || 5}` : user.role}
                  </div>
                </div>
              </button>


              {/* Multi-Child Switcher Dropdown */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-3xl border border-purple-100 shadow-2xl z-50 p-3 space-y-2">
                  <div className="px-3 py-2 bg-purple-50/60 rounded-2xl mb-1">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 block">
                      الحساب الحالي
                    </span>
                    <div className="text-xs font-bold text-slate-900 truncate">{user.email}</div>
                  </div>


                  {/* Child Profiles List */}
                  {allChildren.length > 0 && (
                    <div className="mb-2">
                      <div className="text-[10px] uppercase font-bold text-slate-400 px-2 py-1 flex items-center justify-between">
                        <span>ملفات الطلاب</span>
                        <Users className="w-3 h-3 text-slate-400" />
                      </div>
                      <div className="space-y-1">
                        {allChildren.map((child) => {
                          const isCurrent = activeChild?.id === child.id;
                          const icon = AVATAR_ICONS[child.avatar_id || 'avatar_falcon'] || '🦅';
                          return (
                            <button
                              key={child.id}
                              type="button"
                              onClick={() => {
                                if (onSwitchChild) onSwitchChild(child.id);
                                setIsDropdownOpen(false);
                              }}
                              className={`w-full text-left p-2 rounded-2xl flex items-center justify-between transition-all text-xs ${
                                isCurrent
                                  ? 'bg-[#F3F0FF] text-[#6C5CE7] font-bold border border-purple-200'
                                  : 'hover:bg-slate-50 text-slate-700'
                              }`}
                            >
                              <div className="flex items-center gap-2 truncate">
                                <span className="text-base">{icon}</span>
                                <div className="truncate">
                                  <div className="font-semibold truncate">{child.name}</div>
                                  <div className="text-[10px] text-slate-400">
                                    الصف {child.default_grade} · رمز: <span className="font-mono">{child.access_pin || '1234'}</span>
                                  </div>
                                </div>
                              </div>
                              {isCurrent && <CheckCircle className="w-4 h-4 text-[#22C55E] shrink-0" />}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}


                  {/* Open Profile View */}
                  <button
                    type="button"
                    onClick={() => {
                      setIsDropdownOpen(false);
                      onSelectView('profile');
                    }}
                    className="w-full text-right p-2 text-xs text-[#58337E] hover:bg-purple-50 rounded-2xl flex items-center justify-between font-bold transition-colors"
                  >
                    <span>عرض الملف الشخصي والإعدادات</span>
                    <UserIcon className="w-4 h-4 text-[#6C5CE7]" />
                  </button>


                  {/* Add Child Profile Option */}
                  {user.role === 'parent' && (
                    <button
                      type="button"
                      onClick={() => {
                        setIsDropdownOpen(false);
                        if (onOpenAddChild) onOpenAddChild();
                      }}
                      className="w-full text-right p-2 text-xs text-[#6C5CE7] hover:bg-purple-50 rounded-2xl flex items-center justify-between font-bold transition-colors border border-dashed border-purple-200"
                    >
                      <span>+ إضافة ملف طالب جديد</span>
                      <Plus className="w-4 h-4 text-[#6C5CE7]" />
                    </button>
                  )}


                  {/* Sign Out */}
                  <div className="pt-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => {
                        setIsDropdownOpen(false);
                        onLogout();
                      }}
                      className="w-full text-right p-2 text-xs text-red-600 hover:bg-red-50 rounded-2xl flex items-center justify-between font-bold transition-colors"
                    >
                      <span>تسجيل الخروج</span>
                      <LogOut className="w-4 h-4 text-red-500" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="text-xs py-2 px-4 rounded-full flex items-center gap-1.5 shadow-md bg-[#6C5CE7] text-white font-bold hover:bg-[#58337E] transition-colors"
            >
              <UserIcon className="w-3.5 h-3.5" />
              <span>دخول / حساب جديد</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
