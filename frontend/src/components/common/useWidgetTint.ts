import { RefObject, useEffect } from 'react';

/**
 * Alternating widget colours. Inside the given container, every top-level plain white card/panel
 * (a div, section, article, nav or header with a white background and a border) gets a soft background and
 * matching border from a repeating palette, in page order, so neighbouring widgets look different.
 *
 * - Boxes nested inside a tinted widget stay white, so tiles and options stand out on the card.
 * - Widgets that already have a colour (dark banners, gradients, tinted panels) are left alone.
 * - Add data-no-tint to an element to keep it (and everything inside it) as it is.
 * The palette itself is in index.css ([data-widget-tint]).
 */
export const WIDGET_TINTS = 5;

function isPlainWhiteCard(el: Element): boolean {
  const cls = el.getAttribute('class');
  if (!cls) return false;
  const tokens = cls.split(/\s+/);
  if (!tokens.includes('bg-white')) return false;
  // A box with a border all round (border, border-2…); a row with only a divider (border-b) is not a card.
  return tokens.some((t) => t === 'border' || /^border-\d$/.test(t));
}

export function applyWidgetTints(root: Element): void {
  const candidates = Array.from(root.querySelectorAll('div, section, article, nav, header'));
  const widgets: Element[] = [];
  for (const el of candidates) {
    if (!isPlainWhiteCard(el) || el.closest('[data-no-tint]')) continue;
    // Only the outermost white card: one inside another widget stays white.
    let parent = el.parentElement;
    let nested = false;
    while (parent && parent !== root) {
      if (parent.hasAttribute('data-widget-tint') || isPlainWhiteCard(parent)) { nested = true; break; }
      parent = parent.parentElement;
    }
    if (!nested) widgets.push(el);
  }
  const keep = new Set(widgets);
  root.querySelectorAll('[data-widget-tint]').forEach((el) => { if (!keep.has(el)) el.removeAttribute('data-widget-tint'); });
  widgets.forEach((el, i) => {
    const tint = String(i % WIDGET_TINTS);
    if (el.getAttribute('data-widget-tint') !== tint) el.setAttribute('data-widget-tint', tint);
  });
}

export function useWidgetTint(ref: RefObject<HTMLElement | null>, enabled: boolean): void {
  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    if (!enabled) {
      root.querySelectorAll('[data-widget-tint]').forEach((el) => el.removeAttribute('data-widget-tint'));
      return;
    }
    let frame = 0;
    const schedule = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => { frame = 0; applyWidgetTints(root); });
    };
    applyWidgetTints(root);
    // Re-apply as screens change; only class and child changes matter (our own data attribute doesn't
    // retrigger the observer).
    const observer = new MutationObserver(schedule);
    observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => {
      observer.disconnect();
      if (frame) cancelAnimationFrame(frame);
    };
  }, [ref, enabled]);
}
