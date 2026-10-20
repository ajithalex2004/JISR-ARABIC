import React, { useEffect, useRef } from 'react';
import type { EnterIntent } from '../../entry/Root';
import { prefersReducedMotion } from './useReveal';

// Hangers of the bridge: x positions between the two feet of the arch.
const HANGERS = [120, 170, 220, 270, 330, 380, 430, 480];
// y of the cubic arch M60 280 C160 60, 440 60, 540 280 at a given x (solved numerically once).
function archY(x: number) {
  let lo = 0, hi = 1;
  for (let i = 0; i < 30; i++) {
    const t = (lo + hi) / 2;
    const bx = (1 - t) ** 3 * 60 + 3 * (1 - t) ** 2 * t * 160 + 3 * (1 - t) * t * t * 440 + t ** 3 * 540;
    if (bx < x) lo = t; else hi = t;
  }
  const t = (lo + hi) / 2;
  return (1 - t) ** 3 * 280 + 3 * (1 - t) ** 2 * t * 60 + 3 * (1 - t) * t * t * 60 + t ** 3 * 280;
}

export function BridgeArt() {
  const reduced = prefersReducedMotion();
  return (
    <figure className="jl-bridgefig">
      <svg className="jl-bridge" viewBox="0 40 600 250" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="jl-arch" x1="0" x2="1">
            <stop offset="0" stopColor="#F5EFE6" />
            <stop offset=".55" stopColor="#E0B04B" />
            <stop offset="1" stopColor="#10B981" />
          </linearGradient>
          <radialGradient id="jl-glow" cx=".5" cy=".6" r=".5">
            <stop offset="0" stopColor="#8B5CF6" stopOpacity=".5" />
            <stop offset="1" stopColor="#8B5CF6" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse className="jl-layer" data-depth="6" cx="300" cy="200" rx="290" ry="130" fill="url(#jl-glow)" />
        <g className="jl-layer" data-depth="12">
          <path id="jl-arch-path" className="jl-draw" pathLength={1} d="M60 280 C160 60, 440 60, 540 280" fill="none" stroke="url(#jl-arch)" strokeWidth="3" strokeLinecap="round" />
          <line className="jl-draw jl-draw--late" pathLength={1} x1="20" y1="280" x2="580" y2="280" stroke="#F5EFE6" strokeOpacity=".55" strokeWidth="1.5" />
          {HANGERS.map((x, i) => (
            <line key={x} className="jl-hanger" style={{ ['--i' as string]: i }} x1={x} x2={x} y1={archY(x)} y2={280} stroke="#F5EFE6" strokeOpacity=".35" strokeWidth="1" />
          ))}
          {!reduced && (
            <circle r="5" fill="#E0B04B" className="jl-traveller">
              <animateMotion dur="6s" repeatCount="indefinite" begin="1.6s" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1">
                <mpath href="#jl-arch-path" />
              </animateMotion>
            </circle>
          )}
        </g>
      </svg>
      <figcaption className="jl-bridgefig__labels jl-layer" data-depth="20">
        <span className="jl-bridgefig__en">bridge</span>
        <span className="jl-bridgefig__arrow" aria-hidden="true">→</span>
        <span className="jl-bridgefig__ar"><span lang="ar" dir="rtl">جِسر</span><small>jisr</small></span>
        <span className="jl-sr">: the English word “bridge” and the Arabic word جِسْر (jisr) mean the same thing.</span>
      </figcaption>
    </figure>
  );
}

export function Hero({ onEnter, signedIn = false }: { onEnter: (i: EnterIntent) => void; signedIn?: boolean }) {
  const ref = useRef<HTMLElement>(null);

  // Gentle pointer parallax on the art, for mouse/trackpad users who haven't asked for less motion.
  useEffect(() => {
    const el = ref.current;
    if (!el || prefersReducedMotion() || !window.matchMedia('(pointer: fine)').matches) return;
    const layers = Array.from(el.querySelectorAll<HTMLElement | SVGElement>('.jl-layer'));
    let frame = 0, x = 0, y = 0;
    const paint = () => {
      frame = 0;
      for (const l of layers) {
        const d = Number(l.dataset.depth || 0);
        l.style.transform = `translate(${(x * d).toFixed(2)}px, ${(y * d).toFixed(2)}px)`;
      }
    };
    const onMove = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      x = (e.clientX - r.left) / r.width - 0.5;
      y = (e.clientY - r.top) / r.height - 0.5;
      if (!frame) frame = requestAnimationFrame(paint);
    };
    el.addEventListener('pointermove', onMove);
    return () => { el.removeEventListener('pointermove', onMove); if (frame) cancelAnimationFrame(frame); };
  }, []);

  return (
    <section ref={ref} className="jl-hero" aria-labelledby="jl-hero-title">
      <div className="jl-wrap jl-hero__grid">
        <div className="jl-hero__copy">
          <p className="jl-eyebrow jl-rise" style={{ ['--d' as string]: 0 }}>
            <span className="jl-dot" aria-hidden="true" /> CBSE Arabic · Classes 1–10 · UAE
          </p>
          <h1 id="jl-hero-title" className="jl-display jl-rise" style={{ ['--d' as string]: 1 }}>
            JISR,<br /><em>finally</em> bridge<br /> the gap.
          </h1>
          <p className="jl-lede jl-rise" style={{ ['--d' as string]: 2 }}>
            Your child’s CBSE Arabic textbook, line by line in English, with a native voice for every word.
            Built for non-native learners in UAE schools, and for the parents helping with homework.
          </p>
          <div className="jl-actions jl-rise" style={{ ['--d' as string]: 3 }}>
            <button type="button" className="jl-btn jl-btn--primary" onClick={() => onEnter(signedIn ? 'explore' : 'signup')}>
              {signedIn ? 'Go to my dashboard' : 'Start free'} <span aria-hidden="true" className="jl-btn__arrow">→</span>
            </button>
            <a href="#curriculum" className="jl-btn jl-btn--ghost">
              Try a free lesson
            </a>
          </div>
          <ul className="jl-proof jl-rise" style={{ ['--d' as string]: 4 }} aria-label="At a glance">
            <li><strong>Chapter 1</strong> free every term</li>
            <li><strong>$10</strong> a term</li>
            <li><strong>Any</strong> phone, tablet or laptop</li>
          </ul>
        </div>
        <div className="jl-hero__art"><BridgeArt /></div>
      </div>
      <a href="#demo" className="jl-scrollcue" aria-label="Scroll to the live demo"><span /></a>
    </section>
  );
}
