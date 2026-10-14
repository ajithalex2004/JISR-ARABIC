import React, { useEffect, useState } from 'react';
import { RefreshCw, X } from 'lucide-react';

// A tab that is already open keeps running the build it loaded, even after a new one is
// deployed. Each production build references a uniquely hashed /assets/index-*.js from
// index.html, so comparing the script this page loaded with the one the live index.html
// references tells us a newer build is available.
const CHECK_INTERVAL_MS = 5 * 60 * 1000;
const ENTRY_SCRIPT = /\/assets\/index-[^"'\s]+\.js/;

function loadedEntryScript(): string | null {
  for (const script of Array.from(document.querySelectorAll<HTMLScriptElement>('script[src]'))) {
    const match = script.getAttribute('src')?.match(ENTRY_SCRIPT);
    if (match) return match[0];
  }
  return null;
}

async function liveEntryScript(): Promise<string | null> {
  const res = await fetch(`/index.html?v=${Date.now()}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return (await res.text()).match(ENTRY_SCRIPT)?.[0] ?? null;
}

export const UpdateAvailableBanner: React.FC = () => {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const current = loadedEntryScript();
    // Development server (no hashed bundle): nothing to compare.
    if (!current) return;

    let stopped = false;
    const check = async () => {
      if (stopped || document.visibilityState !== 'visible') return;
      try {
        const live = await liveEntryScript();
        if (live && live !== current && !stopped) {
          setUpdateAvailable(true);
          stopped = true;
        }
      } catch {
        // Offline or the request failed: try again at the next check.
      }
    };

    const timer = window.setInterval(check, CHECK_INTERVAL_MS);
    const onVisible = () => { if (document.visibilityState === 'visible') check(); };
    document.addEventListener('visibilitychange', onVisible);
    window.addEventListener('focus', check);
    return () => {
      stopped = true;
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', onVisible);
      window.removeEventListener('focus', check);
    };
  }, []);

  if (!updateAvailable || dismissed) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed top-3 left-1/2 -translate-x-1/2 z-[1000000] w-[calc(100%-2rem)] max-w-xl flex items-center gap-3 rounded-2xl bg-[#2A1548] text-white px-4 py-3 shadow-2xl border border-purple-400/40"
    >
      <RefreshCw className="w-5 h-5 text-amber-300 shrink-0" />
      <div className="flex-1 text-sm leading-snug">
        <div className="font-bold">A new version of JISR is available</div>
        <div className="text-purple-200 text-xs" dir="rtl">يتوفر إصدار جديد من جسر — حدّث الصفحة</div>
      </div>
      <button
        type="button"
        onClick={() => window.location.reload()}
        className="shrink-0 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-sm px-4 py-2"
      >
        Refresh · تحديث
      </button>
      <button
        type="button"
        aria-label="Dismiss"
        onClick={() => setDismissed(true)}
        className="shrink-0 rounded-lg p-1 text-purple-200 hover:text-white"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
