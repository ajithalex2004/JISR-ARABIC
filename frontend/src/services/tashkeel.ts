/**
 * Tashkeel (vowel mark) display mode.
 * "full" shows the textbook's vowelled Arabic; "plain" hides the marks so a child practises
 * reading Arabic as it is usually written. Audio, dictionary lookups and tooltips always use
 * the original vowelled text, so a tap in plain mode reveals the marks.
 */

import { useState, useEffect } from 'react';

export type TashkeelMode = 'full' | 'plain';

const STORAGE_KEY = 'jisr_tashkeel_mode';

// Harakat, tanween, shadda, sukun, extra combining vowels, superscript alef and Quranic
// annotation marks. Hamza/madda combining marks (U+0653–U+0655) are spelling, so they stay.
const TASHKEEL_RE = /[ً-ْٖ-ٰٟۖ-ۜ۟-۪ۤۧۨ-ۭ]/g;

/** Removes vowel marks for display; letters, hamza, punctuation and spacing are untouched. */
export function stripTashkeel(text: string): string {
  return text ? text.replace(TASHKEEL_RE, '') : '';
}

type Listener = (mode: TashkeelMode) => void;

class TashkeelStateManager {
  private _mode: TashkeelMode = 'full';
  private _listeners: Set<Listener> = new Set();

  constructor() {
    try {
      if (window.localStorage.getItem(STORAGE_KEY) === 'plain') this._mode = 'plain';
    } catch {
      // Storage unavailable (private mode, SSR): keep the default.
    }
  }

  get mode(): TashkeelMode {
    return this._mode;
  }

  set(mode: TashkeelMode): void {
    this._mode = mode;
    try {
      window.localStorage.setItem(STORAGE_KEY, mode);
    } catch {
      // Not persisted; the choice still applies for this visit.
    }
    this._listeners.forEach((fn) => fn(mode));
  }

  toggle(): void {
    this.set(this._mode === 'full' ? 'plain' : 'full');
  }

  subscribe(listener: Listener): () => void {
    this._listeners.add(listener);
    return () => {
      this._listeners.delete(listener);
    };
  }
}

export const TashkeelState = new TashkeelStateManager();

/** React hook: [mode, toggle]. */
export function useTashkeel(): [TashkeelMode, () => void] {
  const [mode, setMode] = useState<TashkeelMode>(() => TashkeelState.mode);
  useEffect(() => TashkeelState.subscribe(setMode), []);
  return [mode, () => TashkeelState.toggle()];
}
