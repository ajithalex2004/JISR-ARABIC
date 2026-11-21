/**
 * Card colours for groups of cards that sit side by side (stage, class, term, lesson/chapter and KPI
 * cards): each card in a group gets a different soft background and matching border, in a fixed
 * order (blue, amber, green, rose, violet), so neighbouring cards are easy to tell apart.
 *
 * - tone(n).idle / .active: a selectable card (button): light when not selected, dark when selected.
 * - tone(n).card: a plain card (KPI, chapter card). Uses ! (important) because the shared card
 *   classes (sharp-card, faheem-card in index.css) would otherwise keep their white background.
 * - LOCKED: a card that can't be opened (stays grey, whatever its position).
 * Class names are written out in full so Tailwind keeps them.
 */
export interface Tone {
  idle: string;
  active: string;
  sub: string;
  card: string;
  accent: string;
}

const TONES: Tone[] = [
  {
    idle: 'bg-blue-50 border-blue-300 hover:border-blue-600 text-slate-900',
    active: 'bg-blue-800 border-blue-950 text-white',
    sub: 'text-blue-100',
    card: '!bg-blue-50 !border-blue-300',
    accent: 'text-blue-900',
  },
  {
    idle: 'bg-amber-50 border-amber-300 hover:border-amber-600 text-slate-900',
    active: 'bg-amber-700 border-amber-900 text-white',
    sub: 'text-amber-100',
    card: '!bg-amber-50 !border-amber-300',
    accent: 'text-amber-900',
  },
  {
    idle: 'bg-emerald-50 border-emerald-300 hover:border-emerald-600 text-slate-900',
    active: 'bg-emerald-800 border-emerald-950 text-white',
    sub: 'text-emerald-100',
    card: '!bg-emerald-50 !border-emerald-300',
    accent: 'text-emerald-900',
  },
  {
    idle: 'bg-rose-50 border-rose-300 hover:border-rose-600 text-slate-900',
    active: 'bg-rose-700 border-rose-900 text-white',
    sub: 'text-rose-100',
    card: '!bg-rose-50 !border-rose-300',
    accent: 'text-rose-900',
  },
  {
    idle: 'bg-violet-50 border-violet-300 hover:border-violet-600 text-slate-900',
    active: 'bg-violet-700 border-violet-900 text-white',
    sub: 'text-violet-100',
    card: '!bg-violet-50 !border-violet-300',
    accent: 'text-violet-900',
  },
];

export const TONE_COUNT = TONES.length;

/** The colour for card number n (0-based) in a group; it wraps after five. */
export function tone(n: number): Tone {
  return TONES[((Math.floor(n) % TONES.length) + TONES.length) % TONES.length];
}

export const LOCKED = 'bg-slate-100 border-slate-300 text-slate-400 cursor-not-allowed';
