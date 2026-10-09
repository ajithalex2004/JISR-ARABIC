import React, { useState, useEffect } from 'react';
import { Flame, Trophy, Award, Shield, Users, Star, Sparkles, Check, Lock } from 'lucide-react';
import { api } from '../../services/api';
import { ChildProfile, GamificationProfile, LeaderboardData, LearnerBadge } from '../../types';

interface GamificationCenterProps {
  activeChild: ChildProfile | null;
}

export const GamificationCenter: React.FC<GamificationCenterProps> = ({ activeChild }) => {
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);
  const [selectedBadge, setSelectedBadge] = useState<LearnerBadge | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (activeChild) {
      loadData();
    }
  }, [activeChild]);

  const loadData = async () => {
    if (!activeChild) return;
    setIsLoading(true);
    try {
      const [profData, lbData] = await Promise.all([
        api.getGamificationProfile(activeChild.id),
        api.getLeaderboard(activeChild.default_grade || 5, activeChild.school_name, activeChild.id)
      ]);
      setProfile(profData);
      setLeaderboard(lbData);
    } catch (e) {
      console.error('Failed to load gamification data', e);
    } finally {
      setIsLoading(false);
    }
  };

  if (!activeChild) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center space-y-3">
        <div className="text-base font-bold text-slate-800">Select a student profile to view Gamification & Leaderboard</div>
        <p className="text-xs text-slate-500">Sign in to check learning streaks, unlocked badges, and cohort rankings.</p>
      </div>
    );
  }

  if (isLoading || !profile || !leaderboard) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 text-center text-xs text-slate-500">
        Loading UAE heritage ranks, XP streaks, and cohort leaderboard...
      </div>
    );
  }

  const getAvatarEmoji = (avatarId: string) => {
    switch (avatarId) {
      case 'avatar_falcon': return '🦅';
      case 'avatar_gazelle': return '🦌';
      case 'avatar_oryx': return '🦬';
      case 'avatar_camel': return '🐪';
      case 'avatar_palm': return '🌴';
      default: return '🦅';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
      {/* Top Banner */}
      <div className="sharp-card p-6 border-l-4 border-l-emerald-800 bg-white flex flex-wrap justify-between items-center gap-4">
        <div>
          <span className="text-[11px] font-bold text-emerald-900 bg-emerald-100 px-2 py-0.5 tracking-wider uppercase">
            Gamification & Motivation · التحفيز والأوسمة
          </span>
          <h1 className="text-2xl font-black text-slate-900 mt-1">
            {profile.child_name}'s Achievement Studio
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            Celebrate daily consistency, earn experience points (XP), and climb the school cohort leaderboard.
          </p>
        </div>

        {/* Current Heritage Rank Badge */}
        <div className="flex items-center gap-3 p-3 border-2 border-slate-900 bg-amber-50/60">
          <div className="w-10 h-10 bg-emerald-900 text-amber-300 flex items-center justify-center font-bold text-lg border border-slate-900">
            <Trophy className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase block">UAE Heritage Rank</span>
            <div className="text-sm font-black text-slate-900">
              {profile.heritage_rank_en} · <span className="font-arabic text-emerald-900">{profile.heritage_rank_ar}</span>
            </div>
            <span className="text-[10px] text-amber-800 font-bold font-mono">Level {profile.level} Scholar</span>
          </div>
        </div>
      </div>

      {/* Streaks & XP Progress Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Daily Streak Card */}
        <div className="sharp-card p-5 border-2 border-amber-600 bg-gradient-to-br from-amber-50/80 to-white space-y-2">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-[11px] font-bold text-amber-900 uppercase tracking-wider block">
                Learning Streak · أيام المذاكرة
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-3xl font-black text-amber-700 font-mono">
                  {profile.current_streak_days}
                </span>
                <span className="text-xs font-bold text-slate-700">Days Active</span>
              </div>
            </div>
            <div className="w-12 h-12 bg-amber-500/20 border-2 border-amber-600 flex items-center justify-center">
              <Flame className="w-6 h-6 text-amber-600 animate-pulse" />
            </div>
          </div>
          <p className="text-[11px] text-slate-600">
            Great discipline! Studied today to protect your streak. Personal best: <span className="font-bold">{profile.longest_streak_days} days</span>.
          </p>
        </div>

        {/* Total XP & Level Gauge */}
        <div className="sharp-card p-5 border border-slate-300 bg-white space-y-2 md:col-span-2">
          <div className="flex justify-between items-baseline">
            <div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                Experience Gauge · نقاط الخبرة (XP)
              </span>
              <div className="text-2xl font-black text-slate-900 font-mono mt-0.5">
                {profile.total_xp} <span className="text-sm font-normal text-slate-500">/ {profile.xp_to_next_level} XP to Level {profile.level + 1}</span>
              </div>
            </div>
            <div className="text-right font-mono text-xs font-bold text-emerald-800">
              {profile.level_progress_pct}% Progress
            </div>
          </div>

          <div className="w-full bg-slate-200 h-3">
            <div
              className="bg-emerald-800 h-3 transition-all duration-500"
              style={{ width: `${profile.level_progress_pct}%` }}
            />
          </div>

          <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
            <span>Level {profile.level}: {profile.heritage_rank_en}</span>
            <span>Next Milestone: Level {profile.level + 1} Unlock (+{profile.xp_to_next_level - profile.total_xp} XP needed)</span>
          </div>
        </div>
      </div>

      {/* Mastery Badges Showcase (الأوسمة والجوائز) */}
      <div className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
        <div className="flex justify-between items-baseline border-b border-slate-200 pb-2">
          <div>
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight flex items-center gap-1.5">
              <Award className="w-4 h-4 text-amber-600" />
              Mastery Badges Showcase (أوسمة الإتقان اللغوي)
            </h2>
            <p className="text-xs text-slate-500">
              Unlocked upon completing linguistic milestones, diagnostic streaks, and reading chapters.
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-800 font-mono">
            {profile.unlocked_badges_count} of {profile.badges.length} Unlocked
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {profile.badges.map((badge) => (
            <div
              key={badge.badge_key}
              onClick={() => setSelectedBadge(badge)}
              className={`p-3 border-2 cursor-pointer transition-all text-center space-y-1.5 ${
                badge.is_unlocked
                  ? 'border-emerald-800 bg-emerald-50/50 hover:bg-emerald-100/60'
                  : 'border-slate-300 bg-slate-100/60 opacity-60 hover:opacity-80'
              }`}
            >
              <div className="text-2xl mb-1">{badge.icon}</div>
              <h3 className="text-xs font-bold text-slate-900 truncate">{badge.title_en}</h3>
              <span className="text-[10px] font-arabic font-bold text-emerald-900 block truncate">
                {badge.title_ar}
              </span>
              <div className="pt-1 border-t border-slate-200">
                {badge.is_unlocked ? (
                  <span className="text-[9px] font-bold text-emerald-800 uppercase flex items-center justify-center gap-0.5">
                    <Check className="w-2.5 h-2.5" /> Unlocked
                  </span>
                ) : (
                  <span className="text-[9px] font-bold text-slate-500 uppercase flex items-center justify-center gap-0.5">
                    <Lock className="w-2.5 h-2.5" /> Locked
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cohort Leaderboard (المتصدرون) */}
      <div className="sharp-card p-5 border border-slate-300 bg-white space-y-4">
        <div className="flex flex-wrap justify-between items-baseline border-b border-slate-200 pb-3 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-800" />
              <h2 className="text-sm font-black text-slate-900 uppercase tracking-tight">
                {leaderboard.cohort_title}
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {leaderboard.school_name} · Grade {leaderboard.grade} Cohort
            </p>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Your Standing</span>
            <span className="text-sm font-black text-emerald-900 font-mono">
              Rank #{leaderboard.current_child_rank} of {leaderboard.total_participants}
            </span>
          </div>
        </div>

        {/* Top 3 Podium Highlights */}
        <div className="grid grid-cols-3 gap-3 pt-2">
          {leaderboard.leaderboard.slice(0, 3).map((entry, idx) => {
            const medalColors = [
              { bg: 'bg-amber-50', border: 'border-amber-400', text: 'text-amber-800', label: '1st Gold' },
              { bg: 'bg-slate-50', border: 'border-slate-300', text: 'text-slate-700', label: '2nd Silver' },
              { bg: 'bg-amber-50/40', border: 'border-amber-700', text: 'text-amber-900', label: '3rd Bronze' }
            ][idx];
            return (
              <div
                key={entry.child_id}
                className={`p-3 border-2 ${medalColors.border} ${medalColors.bg} text-center space-y-1`}
              >
                <span className={`text-[10px] font-black uppercase tracking-wider block ${medalColors.text}`}>
                  {medalColors.label}
                </span>
                <div className="text-2xl">{getAvatarEmoji(entry.avatar_id)}</div>
                <div className="text-xs font-black text-slate-900 truncate">{entry.name}</div>
                <div className="text-xs font-mono font-bold text-emerald-800">{entry.total_xp} XP</div>
                <span className="text-[10px] text-slate-500 block">🔥 {entry.streak_days}d streak</span>
              </div>
            );
          })}
        </div>

        {/* Full Table */}
        <div className="border border-slate-200 divide-y divide-slate-200 text-xs">
          <div className="p-2.5 bg-slate-100 font-bold text-slate-600 grid grid-cols-12 uppercase text-[10px] tracking-wider">
            <span className="col-span-1 text-center">Rank</span>
            <span className="col-span-6">Student & Avatar</span>
            <span className="col-span-3 text-right">XP Points</span>
            <span className="col-span-2 text-right">Streak</span>
          </div>

          {leaderboard.leaderboard.map((entry) => (
            <div
              key={entry.child_id}
              className={`p-3 grid grid-cols-12 items-center transition-colors ${
                entry.is_current_user
                  ? 'bg-emerald-50/80 font-bold border-l-4 border-l-emerald-800 text-emerald-950'
                  : 'bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <span className="col-span-1 text-center font-mono font-bold">
                {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : `#${entry.rank}`}
              </span>
              <div className="col-span-6 flex items-center gap-2 truncate">
                <span className="text-base">{getAvatarEmoji(entry.avatar_id)}</span>
                <span className="truncate">{entry.name}</span>
                {entry.is_current_user && (
                  <span className="bg-emerald-800 text-white text-[9px] px-1.5 py-0.2 uppercase font-bold">
                    You
                  </span>
                )}
              </div>
              <span className="col-span-3 text-right font-mono font-bold text-slate-900">
                {entry.total_xp} XP
              </span>
              <span className="col-span-2 text-right font-mono text-amber-800 font-bold">
                🔥 {entry.streak_days}d
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Badge Details Modal */}
      {selectedBadge && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-sm w-full border-2 border-slate-900 p-6 text-center space-y-4">
            <div className="text-5xl">{selectedBadge.icon}</div>
            <div>
              <h3 className="text-base font-black text-slate-900">{selectedBadge.title_en}</h3>
              <span className="text-sm font-arabic font-bold text-emerald-900 block mt-0.5">
                {selectedBadge.title_ar}
              </span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {selectedBadge.description_en}
            </p>
            <p className="text-xs font-arabic text-emerald-950" dir="rtl">
              {selectedBadge.description_ar}
            </p>
            <div className="p-2 border border-slate-200 bg-slate-50 text-[11px]">
              {selectedBadge.is_unlocked ? (
                <span className="text-emerald-800 font-bold">✓ Unlocked Achievement</span>
              ) : (
                <span className="text-slate-500 font-bold">🔒 Complete linguistic tasks to unlock</span>
              )}
            </div>
            <button
              onClick={() => setSelectedBadge(null)}
              className="btn-primary w-full text-xs py-2 font-bold uppercase tracking-wider"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
