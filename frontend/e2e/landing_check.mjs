// Landing page verification: viewports, accessibility (axe WCAG 2.1 AA), entry-gate routing,
// CTA flows into the app, the word demo, keyboard, mobile menu, reduced motion and SEO assets.
//
// Run from frontend/:
//   npm run build && npx vite preview --port 4173 &
//   npm i --no-save playwright@1 axe-core@4 && node e2e/landing_check.mjs
// Options: BASE_URL=https://app.jisrarabic.com (test the live site), CHROMIUM_PATH=/path/to/chromium
import { chromium } from 'playwright';
import fs from 'fs';
import { createRequire } from 'module';
const BASE = process.env.BASE_URL || 'http://localhost:4173';
const axe = fs.readFileSync(createRequire(import.meta.url).resolve('axe-core/axe.min.js'), 'utf8');
const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };
async function page(opts = {}) {
  const ctx = await b.newContext({ viewport: opts.viewport || { width: 1440, height: 900 }, reducedMotion: opts.reduced ? 'reduce' : 'no-preference' });
  if (opts.token) await ctx.addInitScript(() => localStorage.setItem('fahim_token', 'x'));
  const p = await ctx.newPage(); p.errs = [];
  p.on('pageerror', e => p.errs.push(e.message)); p.on('console', m => m.type() === 'error' && !/Failed to load resource/.test(m.text()) && p.errs.push(m.text()));
  await p.route('**/api/**', r => r.fulfill({ status: 401, contentType: 'application/json', body: '{"detail":"no"}' }));
  return p;
}
const isLanding = p => p.locator('.jl').count().then(n => n > 0);

// 1. Viewports: renders, no overflow, no errors
for (const [w, h] of [[375, 812], [768, 1024], [1440, 900]]) {
  const p = await page({ viewport: { width: w, height: h } });
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  ok(await isLanding(p), `${w}px: landing shown at /`);
  const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  ok(ov <= 0, `${w}px: no horizontal overflow (${ov}px)`);
  ok(p.errs.length === 0, `${w}px: no console errors ${JSON.stringify(p.errs)}`);
  await p.context().close();
}

// 2. Accessibility audit (axe, WCAG 2 A/AA) + structure
{
  const p = await page();
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  await p.addScriptTag({ content: axe });
  // reveal everything so contrast is measured on final colours
  await p.evaluate(() => document.querySelectorAll('[data-reveal]').forEach(n => n.classList.add('is-in')));
  await p.waitForTimeout(1500);
  const res = await p.evaluate(async () => (await window.axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'] })).violations.map(v => `${v.id}(${v.impact}) x${v.nodes.length}: ${v.nodes.slice(0, 2).map(n => n.target.join(' ')).join(' | ')}`));
  ok(res.length === 0, 'axe: no violations' + (res.length ? '\n   ' + res.join('\n   ') : ''));
  ok(await p.locator('h1').count() === 1, 'exactly one h1');
  const levels = await p.$$eval('h1,h2,h3,h4', hs => hs.map(h => +h.tagName[1]));
  ok(levels.every((l, i) => i === 0 || l - levels[i - 1] <= 1), 'heading levels never skip');
  await p.keyboard.press('Tab');
  ok(await p.evaluate(() => document.activeElement?.textContent) === 'Skip to content', 'first Tab reaches the skip link');
  await p.context().close();
}

// 3. Word demo
{
  const p = await page();
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  const w = p.locator('.jl-word').nth(1);
  await w.scrollIntoViewIfNeeded(); await w.click();
  ok(await w.getAttribute('aria-pressed') === 'true', 'tapping a word selects it');
  ok((await p.locator('.jl-demo__card-en').innerText()) === 'the language', 'card shows the meaning');
  await p.getByRole('tab', { name: 'Sentence 2' }).click();
  ok((await p.locator('.jl-demo__translation').innerText()).includes('I went to school'), 'sentence tabs switch');
  ok(p.errs.length === 0, 'demo: no errors ' + JSON.stringify(p.errs));
  await p.context().close();
}

// 4. Mobile menu
{
  const p = await page({ viewport: { width: 375, height: 812 } });
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  const burger = p.getByRole('button', { name: 'Open menu' });
  await burger.click();
  ok(await p.getByRole('link', { name: 'Pricing' }).first().isVisible(), 'menu opens and shows links');
  await p.keyboard.press('Escape');
  ok(await burger.getAttribute('aria-expanded') === 'false', 'Escape closes the menu');
  await p.context().close();
}

// 5. CTA flows into the app
{
  const p = await page();
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  await p.locator('.jl-hero').getByRole('button', { name: /Start free/ }).click();
  await p.waitForTimeout(1500);
  ok(!(await isLanding(p)), 'Start free opens the app');
  ok(await p.getByText(/create account|sign up/i).first().isVisible().catch(() => false), 'sign-up modal is open');
  ok(!(new URL(p.url()).search.includes('auth')), 'auth intent stripped from URL: ' + p.url());
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  ok(!(await isLanding(p)), 'returning visitor goes straight to the app');
  await p.goto(BASE + '/welcome', { waitUntil: 'networkidle' });
  ok(await isLanding(p), '/welcome always shows the landing');
  ok(p.errs.length === 0, 'flows: no errors ' + JSON.stringify(p.errs));
  await p.context().close();
}

// 6. Gate rules
for (const [path, opts, want, label] of [['/?grade=7', {}, false, 'deep link ?grade= goes to app'], ['/?payment=success', {}, false, 'payment return goes to app'], ['/#admin', {}, false, '#admin goes to app'], ['/', { token: true }, false, 'signed-in visitor goes to app']]) {
  const p = await page(opts);
  await p.goto(BASE + path, { waitUntil: 'networkidle' });
  ok((await isLanding(p)) === want, label);
  await p.context().close();
}

// 7. Reduced motion: no hidden content, no marquee animation
{
  const p = await page({ reduced: true });
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  ok(!(await p.locator('.jl-motion').count()), 'reduced motion: reveal never arms');
  const op = await p.locator('#pricing [data-reveal]').first().evaluate(n => getComputedStyle(n).opacity);
  ok(op === '1', 'reduced motion: below-fold content visible without scrolling');
  await p.context().close();
}

// 8. SEO assets
{
  const p = await page();
  for (const f of ['/robots.txt', '/sitemap.xml', '/og-image.png']) { const r = await p.request.get(BASE + f); ok(r.ok(), `${f} served`); }
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  ok(!!(await p.locator('meta[property="og:image"]').getAttribute('content')), 'og:image present');
  await p.context().close();
}
await b.close();
console.log(fails ? `\n${fails} FAILED` : '\nALL PASSED');
process.exit(fails ? 1 : 0);
