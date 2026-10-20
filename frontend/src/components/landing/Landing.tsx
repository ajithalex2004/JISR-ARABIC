import React, { useEffect, useRef, useState } from 'react';
import type { EnterIntent } from '../../entry/Root';
import { Hero } from './Hero';
import { Marquee, WordDemo } from './WordDemo';
import { ScrollStory } from './ScrollStory';
import { Curriculum, Faq, Features, FinalCta, Parents, Pricing } from './Sections';
import { useReveal, useScrolled } from './useReveal';
import './landing.css';

const NAV = [['#how', 'How it works'], ['#features', 'Features'], ['#pricing', 'Pricing'], ['#faq', 'FAQ']];

function Nav({ onEnter, signedIn }: { onEnter: (i: EnterIntent) => void; signedIn: boolean }) {
  const scrolled = useScrolled();
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);
  return (
    <header className={`jl-nav${scrolled ? ' is-scrolled' : ''}${open ? ' is-open' : ''}`}>
      <div className="jl-wrap jl-nav__inner">
        <a href="/welcome" className="jl-logo" aria-label="JISR Arabic home">
          <img src="/logo-icon.svg" alt="" width="36" height="36" />
          <span className="jl-logo__en">JISR</span><span className="jl-logo__ar" lang="ar">جِسْر</span>
        </a>
        <nav aria-label="Main" className="jl-nav__links" id="jl-menu">
          <ul>{NAV.map(([href, label]) => <li key={href}><a href={href} onClick={() => setOpen(false)}>{label}</a></li>)}</ul>
          <div className="jl-nav__cta">
            <button type="button" className="jl-btn jl-btn--text jl-nav__signin" onClick={() => onEnter('login')}>Sign in</button>
            {signedIn ? (
              <button type="button" className="jl-btn jl-btn--primary jl-btn--sm" onClick={() => onEnter('explore')}>My dashboard</button>
            ) : (
              <button type="button" className="jl-btn jl-btn--primary jl-btn--sm" onClick={() => onEnter('signup')}>Start free</button>
            )}
          </div>
        </nav>
        {/* Phones: Sign in stays on screen next to the menu button instead of hiding inside the menu. */}
        <button type="button" className="jl-btn jl-btn--line-light jl-btn--sm jl-nav__signin-m" onClick={() => onEnter('login')}>Sign in</button>
        <button type="button" className="jl-burger" aria-expanded={open} aria-controls="jl-menu" onClick={() => setOpen((o) => !o)}>
          <span className="jl-sr">{open ? 'Close menu' : 'Open menu'}</span><i aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}

function Footer({ onEnter }: { onEnter: (i: EnterIntent) => void }) {
  return (
    <footer className="jl-footer">
      <div className="jl-wrap jl-footer__grid">
        <div>
          <a href="/welcome" className="jl-logo"><img src="/logo-icon.svg" alt="" width="32" height="32" /><span className="jl-logo__en">JISR</span><span className="jl-logo__ar" lang="ar">جِسْر</span></a>
          <p className="jl-footer__tag">The bridge to Arabic for non-native learners in UAE schools.</p>
        </div>
        <nav aria-label="Footer">
          <ul>
            {NAV.map(([href, label]) => <li key={href}><a href={href}>{label}</a></li>)}
            <li><button type="button" className="jl-linkbtn" onClick={() => onEnter('explore')}>Open the app</button></li>
          </ul>
        </nav>
      </div>
      <div className="jl-wrap jl-footer__base">
        <span>© {new Date().getFullYear()} JISR Arabic Educational Technologies FZ-LLC</span>
        <span lang="ar">مِنْهَاجُ اللُّغَةِ العَرَبِيَّةِ</span>
      </div>
    </footer>
  );
}

export default function Landing({ onEnter, signedIn = false }: { onEnter: (i: EnterIntent) => void; signedIn?: boolean }) {
  const root = useRef<HTMLDivElement>(null);
  useReveal(root);
  useEffect(() => {
    // The landing is dark; match the mobile browser chrome while it's on screen.
    const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
    const prevColor = meta?.content;
    if (meta) meta.content = '#140B22';
    return () => { if (meta && prevColor) meta.content = prevColor; };
  }, []);
  return (
    <div ref={root} className="jl">
      <a href="#jl-main" className="jl-skip">Skip to content</a>
      <Nav onEnter={onEnter} signedIn={signedIn} />
      <main id="jl-main" tabIndex={-1}>
        <Hero onEnter={onEnter} signedIn={signedIn} />
        <Marquee />
        <WordDemo />
        <ScrollStory />
        <Features />
        <Curriculum />
        <Parents />
        <Pricing onEnter={onEnter} signedIn={signedIn} />
        <Faq />
        <FinalCta onEnter={onEnter} signedIn={signedIn} />
      </main>
      <Footer onEnter={onEnter} />
    </div>
  );
}
