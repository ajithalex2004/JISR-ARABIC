import React, { createContext, useContext } from 'react';
import { CheckCircle2, Lock, Sparkles } from 'lucide-react';
import { ANNUAL_USD, TERM_USD, aed, usd } from './pricing';

/** Why the learner is being asked to upgrade: shapes the headline and what the plan opens. */
export type UpgradeReason = 'chapter' | 'term' | 'ask_fahim' | 'foundation';

export interface UpgradeRequest {
  reason: UpgradeReason;
  grade?: number;
  term?: number;
  chapterName?: string;
}

interface UpgradeContextValue {
  /** guest: not signed in; student: PIN login (can't pay); parent: can buy; staff: never prompted. */
  viewer: 'guest' | 'student' | 'parent' | 'staff';
  /** The learner already has a paid plan (any term): no Ask Fahim or Foundation prompts then. */
  hasPlan: boolean;
  /** Opens the plans screen (or sign-up for a guest). */
  open: (request: UpgradeRequest) => void;
}

const UpgradeContext = createContext<UpgradeContextValue>({ viewer: 'staff', hasPlan: false, open: () => undefined });
export const UpgradeProvider = UpgradeContext.Provider;
export const useUpgrade = () => useContext(UpgradeContext);

const COPY: Record<UpgradeReason, { title: (r: UpgradeRequest) => string; lead: (r: UpgradeRequest) => string; benefits: string[] }> = {
  chapter: {
    title: (r) => (r.chapterName ? `“${r.chapterName}” is part of the paid plan` : 'This chapter is part of the paid plan'),
    lead: (r) => `Chapter 1 is free. Unlock ${r.term ? `Term ${r.term}` : 'the term'} to open every chapter${r.grade ? ` of Class ${r.grade}` : ''}.`,
    benefits: ['Every chapter of the term, with audio and word meanings', 'Smart study booklets and mindmaps', 'CBSE exam practice and Ask Fahim, the AI mentor'],
  },
  term: {
    title: (r) => `Unlock ${r.term ? `Term ${r.term}` : 'this term'}${r.grade ? ` of Class ${r.grade}` : ''}`,
    lead: () => 'Open all its chapters, booklets, mindmaps and exam practice.',
    benefits: ['All chapters of the term, with audio and word meanings', 'Smart study booklets, mindmaps and capsules', 'CBSE exam simulation and Ask Fahim, the AI mentor'],
  },
  ask_fahim: {
    title: () => 'Ask Fahim, the AI mentor, is part of the paid plan',
    lead: () => 'Homework help, “explain this rule”, and exam-paper practice, in English or Arabic, any time.',
    benefits: ['Unlimited questions to Fahim, the AI mentor', 'Step-by-step explanations of grammar rules', 'Plus every chapter, booklet and exam of the term'],
  },
  foundation: {
    title: (r) => `Ready for the${r.grade ? ` Class ${r.grade}` : ''} CBSE curriculum?`,
    lead: () => 'Great work finishing this stage! Put what you have learned to work on the official textbook chapters.',
    benefits: ['Every textbook chapter, with audio and word meanings', 'Booklets, mindmaps and CBSE exam practice', 'Ask Fahim to explain any rule'],
  },
};

interface UpgradeCardProps extends UpgradeRequest {
  className?: string;
  /** A one-line strip instead of the full card (e.g. under a term bar). */
  compact?: boolean;
}

/**
 * A clear upgrade prompt with the price, shown at the moment a free learner meets something paid
 * (a locked chapter or term, Ask Fahim, the end of a Foundation stage). Never shown to staff.
 */
export const UpgradeCard: React.FC<UpgradeCardProps> = ({ className = '', compact = false, ...request }) => {
  const { viewer, hasPlan, open } = useUpgrade();
  if (viewer === 'staff') return null;
  // A locked chapter or term is shown whatever else is paid; Ask Fahim and Foundation prompts only to free learners.
  if (hasPlan && (request.reason === 'ask_fahim' || request.reason === 'foundation')) return null;
  const copy = COPY[request.reason];
  const priceLine = `${usd(TERM_USD)} per term (~${aed(TERM_USD)}) · Full year ${usd(ANNUAL_USD)} (save 15%)`;
  const cta = viewer === 'guest' ? 'Create a free account' : viewer === 'student' ? 'How to unlock' : 'See plans & unlock';

  if (compact) {
    return (
      <div role="note" className={`flex flex-wrap items-center gap-x-3 gap-y-1.5 p-2.5 border-2 border-amber-400 bg-amber-50 text-xs ${className}`}>
        <Lock className="w-4 h-4 text-amber-700 shrink-0" aria-hidden />
        <span className="font-bold text-amber-950">{copy.title(request)}</span>
        <span className="text-amber-900">From {usd(TERM_USD)} per term · Full year {usd(ANNUAL_USD)}</span>
        <button type="button" onClick={() => open(request)}
          className="ml-auto px-3 py-1 bg-emerald-800 hover:bg-emerald-900 text-white font-bold">
          {cta}
        </button>
      </div>
    );
  }

  return (
    <section aria-label="Upgrade" className={`border-2 border-amber-400 bg-gradient-to-br from-amber-50 to-white p-4 sm:p-5 ${className}`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-amber-500 text-white flex items-center justify-center shrink-0">
          {request.reason === 'foundation' ? <Sparkles className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
        </div>
        <div className="flex-1 min-w-0 space-y-2">
          <div>
            <h3 className="text-base font-black text-slate-900">{copy.title(request)}</h3>
            <p className="text-sm text-slate-700">{copy.lead(request)}</p>
          </div>
          <ul className="space-y-1">
            {copy.benefits.map((b) => (
              <li key={b} className="flex items-start gap-1.5 text-xs text-slate-800">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700 mt-0.5 shrink-0" /> {b}
              </li>
            ))}
          </ul>
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <button type="button" onClick={() => open(request)}
              className="px-5 py-2.5 bg-emerald-800 hover:bg-emerald-900 text-white text-sm font-black">
              {cta}
            </button>
            <span className="text-xs font-bold text-slate-800">{priceLine}</span>
          </div>
          {viewer === 'student' && (
            <p className="text-[11px] text-slate-600">Plans are bought from a parent account. Ask your parent to log in and unlock it for you.</p>
          )}
        </div>
      </div>
    </section>
  );
};
