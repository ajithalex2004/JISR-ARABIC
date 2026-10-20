import React, { lazy, Suspense, useCallback, useEffect, useState } from 'react';

// Each experience is its own chunk: visitors on the landing page don't download the app, and
// signed-in learners never download the landing page.
const App = lazy(() => import('../App'));
const Landing = lazy(() => import('../components/landing/Landing'));

export type EnterIntent = 'signup' | 'login' | 'explore';

// Set when a visitor goes from the welcome page into the app ("Sign in", "My dashboard"…).
// Session-scoped on purpose: every new visit starts on the welcome page.
const IN_APP_KEY = 'jisr_in_app';
export const WELCOME_PATH = '/welcome';

function readStorage(store: 'local' | 'session', key: string): string | null {
  try { return (store === 'local' ? window.localStorage : window.sessionStorage).getItem(key); } catch { return null; }
}

/** Every visit to the site starts on the welcome page (/welcome), signed in or not. Deep links
 *  (?grade=, ?payment=, #admin…) and anyone who already went into the app during this browser
 *  session (so a refresh doesn't bounce them out of a lesson) go to the app. */
export function shouldShowLanding(loc: Pick<Location, 'pathname' | 'search' | 'hash'> = window.location): boolean {
  const path = loc.pathname.replace(/\/+$/, '') || '/';
  if (path === WELCOME_PATH) return true;
  if (path !== '/' || loc.search || loc.hash) return false;
  if (readStorage('session', IN_APP_KEY)) return false;
  return true;
}

/** Leave the app for the welcome page (used on sign-out). */
export function goToWelcome() {
  try { window.sessionStorage.removeItem(IN_APP_KEY); } catch { /* ignore */ }
  window.location.assign(WELCOME_PATH);
}

const Loading = () => (
  <div role="status" aria-live="polite" style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#140B22', color: '#E0B04B', fontFamily: 'Amiri, serif', fontSize: '2.5rem' }}>
    <span>جِسْر</span><span style={{ position: 'absolute', left: -9999 }}>Loading JISR Arabic…</span>
  </div>
);

export function Root() {
  const [landing, setLanding] = useState(() => {
    const show = shouldShowLanding();
    // Keep the address bar on /welcome so the welcome page is always the page people see and share.
    if (show && window.location.pathname !== WELCOME_PATH) window.history.replaceState(null, '', WELCOME_PATH);
    return show;
  });

  useEffect(() => {
    try { window.localStorage.removeItem('jisr_entered_app'); } catch { /* old "skip the landing" flag */ }
  }, []);

  const enterApp = useCallback((intent: EnterIntent) => {
    try { window.sessionStorage.setItem(IN_APP_KEY, '1'); } catch { /* private mode: fine */ }
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
