import React from 'react';
import type { EnterIntent } from '../../entry/Root';
import { FAQS, FEATURES, GRADES, PLANS } from './content';

/* Small CSS/SVG illustrations for each feature tile: no image requests. */
function FeatureArt({ id }: { id: string }) {
  switch (id) {
    case 'audio':
      return <div className="jl-art jl-art--wave">{Array.from({ length: 18 }, (_, i) => <i key={i} style={{ ['--i' as string]: i, height: `${20 + ((i * 37) % 80)}%` }} />)}</div>;
    case 'fahim':
      return <div className="jl-art jl-art--chat"><span>What does <b lang="ar">صَدِيقٌ</b> mean?</span><span lang="ar" className="is-reply">صَدِيقٌ = friend 🔊</span></div>;
    case 'maps':
      return <svg className="jl-art jl-art--map" viewBox="0 0 160 90"><g stroke="currentColor" fill="none"><path d="M80 45 30 18M80 45 30 72M80 45 130 18M80 45 130 72" /></g>{[[80, 45, 9], [30, 18, 6], [30, 72, 6], [130, 18, 6], [130, 72, 6]].map(([x, y, r], i) => <circle key={i} cx={x} cy={y} r={r} />)}</svg>;
    case 'booklets':
      return <div className="jl-art jl-art--pages"><i /><i /><i /></div>;
    case 'exam':
      return <div className="jl-art jl-art--timer"><span>24:59</span><small>Paper 1 · Section B</small></div>;
    default:
      return <div className="jl-art jl-art--heat">{Array.from({ length: 28 }, (_, i) => <i key={i} style={{ opacity: [0.25, 0.5, 0.75, 1][(i * 7) % 4] }} />)}</div>;
  }
}

export function Features() {
  return (
    <section id="features" className="jl-section jl-features" aria-labelledby="jl-features-title">
      <div className="jl-wrap">
        <header className="jl-head" data-reveal>
          <p className="jl-kicker">Everything in one place</p>
          <h2 id="jl-features-title" className="jl-h2">Six ways to make Arabic <em>stick</em>.</h2>
        </header>
        <ul className="jl-bento">
          {FEATURES.map((f, i) => (
            <li key={f.id} className={`jl-tile jl-tile--${f.id}`} data-reveal style={{ ['--d' as string]: i % 3 }}>
              <span className="jl-tile__ar" lang="ar" aria-hidden="true">{f.ar}</span>
              <FeatureArt id={f.id} />
              <h3 className="jl-h3">{f.title}</h3>
              <p>{f.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export function Curriculum() {
  return (
    <section id="curriculum" className="jl-section jl-curriculum" aria-labelledby="jl-curr-title">
      <div className="jl-wrap jl-curriculum__grid">
        <div data-reveal>
          <p className="jl-kicker">Aligned with school</p>
          <h2 id="jl-curr-title" className="jl-h2">The CBSE syllabus, <em>term by term</em>.</h2>
          <p className="jl-sub">
            JISR follows the CBSE Arabic curriculum used in UAE schools, organised into the same three terms,
            so homework, revision and exams all line up with class.
          </p>
          <dl className="jl-stats">
            <div><dt>Classes</dt><dd>1–10</dd></div>
            <div><dt>Terms a year</dt><dd>3</dd></div>
            <div><dt>First chapter</dt><dd>Free</dd></div>
          </dl>
        </div>
        <nav className="jl-grades" aria-label="Open a class" data-reveal>
          <p className="jl-label">Open a class. The first chapter is free.</p>
          <ul>
            {GRADES.map((g) => (
              <li key={g}><a href={`/?grade=${g}`} className="jl-grade"><span>Class</span><strong>{g}</strong><span lang="ar" className="jl-grade__ar">الصَّفُّ {g.toLocaleString('ar-EG')}</span></a></li>
            ))}
          </ul>
        </nav>
      </div>
    </section>
  );
}

export function Pricing({ onEnter, signedIn = false }: { onEnter: (i: EnterIntent) => void; signedIn?: boolean }) {
  return (
    <section id="pricing" className="jl-section jl-pricing" aria-labelledby="jl-pricing-title">
      <div className="jl-wrap">
        <header className="jl-head jl-head--center" data-reveal>
          <p className="jl-kicker">Simple pricing</p>
          <h2 id="jl-pricing-title" className="jl-h2">Less than a single tutoring hour <em>for the whole year</em>.</h2>
        </header>
        <ul className="jl-plans">
          {PLANS.map((p, i) => (
            <li key={p.id} className={`jl-plan${p.featured ? ' jl-plan--featured' : ''}`} data-reveal style={{ ['--d' as string]: i }}>
              {p.badge && <span className="jl-plan__badge">{p.badge}</span>}
              <h3 className="jl-plan__name">{p.name}</h3>
              <p className="jl-plan__price">
                {p.was && <s aria-label={`was ${p.was}`}>{p.was}</s>}<strong>{p.price}</strong>
              </p>
              <p className="jl-plan__cadence">{p.cadence}</p>
              <ul className="jl-plan__points">{p.points.map((pt) => <li key={pt}>{pt}</li>)}</ul>
              <button type="button" className={`jl-btn ${p.featured ? 'jl-btn--primary' : 'jl-btn--line'} jl-btn--block`} onClick={() => onEnter(signedIn && p.id === 'free' ? 'explore' : p.intent)}>{p.cta}</button>
            </li>
          ))}
        </ul>
        <p className="jl-fineprint" data-reveal>
          Prices in USD and include 5% UAE VAT. Secure payment by Stripe. Every payment comes with a receipt and a UAE tax invoice.
          Auto-renew is optional and can be turned off at any time.
        </p>
      </div>
    </section>
  );
}

export function Parents() {
  const points = [
    ['One account, every child', 'Add each child with their own class and progress. Switch between them in a tap.'],
    ['A 4-digit PIN for kids', 'Children sign in with your email and their own PIN. No passwords to forget.'],
    ['Progress you can actually read', 'See which words are mastered and which chapters need another look, in English.'],
    ['Receipts that work for school', 'Every payment has a receipt number and a UAE tax invoice you can print.'],
  ];
  return (
    <section id="parents" className="jl-section jl-parents" aria-labelledby="jl-parents-title">
      <div className="jl-wrap jl-parents__grid">
        <div className="jl-parents__panel" data-reveal aria-hidden="true">
          <div className="jl-dash">
            <div className="jl-dash__head"><span className="jl-avatar">🦅</span><div><strong>Sara</strong><small>Class 5 · Term 1</small></div><span className="jl-pill">On track</span></div>
            <div className="jl-dash__bars">
              {[['Vocabulary', 0.86], ['Reading', 0.72], ['Grammar', 0.58], ['Listening', 0.91]].map(([k, v]) => (
                <div key={k as string} className="jl-bar"><span>{k}</span><i style={{ ['--v' as string]: v as number }} /><b>{Math.round((v as number) * 100)}%</b></div>
              ))}
            </div>
            <div className="jl-dash__foot"><span>This week</span><strong>+42 words</strong></div>
          </div>
        </div>
        <div>
          <header data-reveal>
            <p className="jl-kicker">For parents</p>
            <h2 id="jl-parents-title" className="jl-h2">Help with homework, <em>even if you don’t speak Arabic</em>.</h2>
          </header>
          <ul className="jl-points">
            {points.map(([t, b], i) => (
              <li key={t} data-reveal style={{ ['--d' as string]: i }}><h3 className="jl-h4">{t}</h3><p>{b}</p></li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export function Faq() {
  return (
    <section id="faq" className="jl-section jl-faq" aria-labelledby="jl-faq-title">
      <div className="jl-wrap jl-faq__grid">
        <header data-reveal>
          <p className="jl-kicker">Questions</p>
          <h2 id="jl-faq-title" className="jl-h2">Good to <em>know</em>.</h2>
        </header>
        <div className="jl-faq__list">
          {FAQS.map((f) => (
            <details key={f.q} className="jl-qa" data-reveal>
              <summary><span>{f.q}</span><i aria-hidden="true" /></summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

export function FinalCta({ onEnter, signedIn = false }: { onEnter: (i: EnterIntent) => void; signedIn?: boolean }) {
  return (
    <section className="jl-final" aria-labelledby="jl-final-title">
      <div className="jl-wrap" data-reveal>
        <p className="jl-final__ar" lang="ar" dir="rtl" aria-hidden="true">هَيَّا نَبْدَأْ</p>
        <h2 id="jl-final-title" className="jl-display jl-display--sm">Let’s begin.</h2>
        <p className="jl-lede">Create a free account in a minute. Chapter 1 of every term is on us.</p>
        <div className="jl-actions jl-actions--center">
          {signedIn ? (
            <button type="button" className="jl-btn jl-btn--primary" onClick={() => onEnter('explore')}>Go to my dashboard <span aria-hidden="true" className="jl-btn__arrow">→</span></button>
          ) : (
            <>
              <button type="button" className="jl-btn jl-btn--primary" onClick={() => onEnter('signup')}>Start free <span aria-hidden="true" className="jl-btn__arrow">→</span></button>
              <button type="button" className="jl-btn jl-btn--ghost" onClick={() => onEnter('login')}>I have an account</button>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
