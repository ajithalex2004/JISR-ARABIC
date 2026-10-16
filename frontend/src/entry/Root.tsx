import React, { lazy, Suspense, useCallback, useEffect, useState } from 'react';

// Each experience is its own chunk: visitors on the landing page don't download the app, and
// signed-in learners never download the landing page.
const App = lazy(() => import('../App'));
const Landing = lazy(() => import('../components/landing/Landing'));

export type EnterIntent = 'signup' | 'login' | 'explore';

const ENTERED_KEY = 'jisr_entered_app';

function readStorage(store: 'local' | 'session', key: string): string | null {
  try { return (store === 'local' ? window.localStorage : window.sessionStorage).getItem(key); } catch { return null; }
}

/** The landing page is for signed-out visitors arriving at the bare root (or anyone at /welcome).
 *  Deep links (?grade=, ?payment=, #admin…), sessions and returning learners go straight to the app. */
export function shouldShowLanding(loc: Pick<Location, 'pathname' | 'search' | 'hash'> = window.location): boolean {
  const path = loc.pathname.replace(/\/+$/, '') || '/';
  if (path === '/welcome') return true;
  if (path !== '/' || loc.search || loc.hash) return false;
  if (readStorage('local', 'fahim_token')) return false;
  if (readStorage('local', ENTERED_KEY)) return false;
  return true;
}

const Loading = () => (
  <div role="status" aria-live="polite" style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#140B22', color: '#E0B04B', fontFamily: 'Amiri, serif', fontSize: '2.5rem' }}>
    <span>جِسْر</span><span style={{ position: 'absolute', left: -9999 }}>Loading JISR Arabic…</span>
  </div>
);

export function Root() {
  const [landing, setLanding] = useState(shouldShowLanding);

  const enterApp = useCallback((intent: EnterIntent) => {
    try { window.localStorage.setItem(ENTERED_KEY, '1'); } catch { /* private mode: fine */ }
    const url = intent === 'explore' ? '/' : `/?auth=${intent}`;
    window.history.pushState(null, '', url);
    window.scrollTo(0, 0);
    setLanding(false);
  }, []);

  useEffect(() => {
    const onPop = () => setLanding(shouldShowLanding());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  return <Suspense fallback={<Loading />}>{landing ? <Landing onEnter={enterApp} /> : <App />}</Suspense>;
}
