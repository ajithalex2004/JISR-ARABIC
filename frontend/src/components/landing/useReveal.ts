import { RefObject, useEffect, useState } from 'react';

export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/** Adds `is-in` to every [data-reveal] element inside `root` the first time it scrolls into view.
 *  Content is visible by default; hiding only starts once this runs (`jl-motion` on the root), so
 *  no-JS, print and reduced-motion visitors always see everything. */
export function useReveal(root: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const el = root.current;
    if (!el || prefersReducedMotion() || !('IntersectionObserver' in window)) return;
    el.classList.add('jl-motion');
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    el.querySelectorAll('[data-reveal]').forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, [root]);
}

/** Index of the step currently in the middle band of the viewport. */
export function useActiveStep(refs: RefObject<(HTMLElement | null)[]>, count: number) {
  const [active, setActive] = useState(0);
  useEffect(() => {
    const nodes = (refs.current || []).slice(0, count).filter(Boolean) as HTMLElement[];
    if (!nodes.length || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) setActive(Number((e.target as HTMLElement).dataset.step));
    }, { rootMargin: '-45% 0px -45% 0px' });
    nodes.forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, [refs, count]);
  return active;
}

/** True once the page has scrolled past `offset` (rAF-throttled). */
export function useScrolled(offset = 24) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    let frame = 0;
    const update = () => { frame = 0; setScrolled(window.scrollY > offset); };
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update); };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => { window.removeEventListener('scroll', onScroll); if (frame) cancelAnimationFrame(frame); };
  }, [offset]);
  return scrolled;
}
