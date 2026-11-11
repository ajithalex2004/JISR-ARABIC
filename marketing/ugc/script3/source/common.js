// Shared: local app with /api answered from production (cached on disk), cosmetics, tap marker.
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const { chromium } = require('playwright');
const CACHE = path.join(__dirname, '..', 'apicache');
const DSF = 1080 / 390;
async function open(grade, { scale = true } = {}) {
  const b = await chromium.launch(scale ? { args: ['--force-device-scale-factor=' + DSF] } : {});
  const ctx = await b.newContext({ viewport: { width: 390, height: 693 }, deviceScaleFactor: scale ? DSF : 1, isMobile: true, hasTouch: true });
  const events = [];
  await ctx.route('**/api/**', async route => {
    const req = route.request(); const u = new URL(req.url());
    const key = crypto.createHash('sha1').update(req.method() + u.pathname + u.search + (req.postData() || '')).digest('hex');
    const f = path.join(CACHE, key);
    if (/audio\/cache\/.*\.mp3/.test(u.pathname)) events.push({ name: 'audio:' + u.pathname.split('/').pop(), wall: Date.now() / 1000 });
    if (!fs.existsSync(f + '.body')) {
      const resp = await route.fetch({ url: 'https://api.jisrarabic.com' + u.pathname + u.search, headers: { 'content-type': req.headers()['content-type'] || 'application/json' } });
      fs.writeFileSync(f + '.body', await resp.body());
      fs.writeFileSync(f + '.json', JSON.stringify({ status: resp.status(), ct: resp.headers()['content-type'] || '', path: u.pathname + u.search }));
    }
    const m = JSON.parse(fs.readFileSync(f + '.json'));
    await route.fulfill({ status: m.status, contentType: m.ct, body: fs.readFileSync(f + '.body'), headers: { 'access-control-allow-origin': '*' } });
  });
  const p = await ctx.newPage();
  await p.goto(`http://127.0.0.1:5173/?grade=${grade}`, { waitUntil: 'load' });
  await p.waitForSelector('text=Glossary', { timeout: 60000 });
  await p.waitForTimeout(2500);
  return { b, ctx, p, events };
}
async function cosmetics(p) {
  await p.evaluate(() => {
    document.querySelectorAll('body *').forEach(el => {
      const t = (el.textContent || '').trim();
      if (t.length < 80 && /TERM\s*1/i.test(t) && ![...el.children].some(c => /TERM\s*1/i.test((c.textContent || '').trim()))) el.style.visibility = 'hidden';
    });
    if (!document.getElementById('tapstyle')) {
      const s = document.createElement('style'); s.id = 'tapstyle';
      s.textContent = `.tapdot{position:fixed;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;background:rgba(224,176,75,.45);border:3px solid #E0B04B;pointer-events:none;z-index:2147483647;animation:tapk .7s ease-out forwards}
        @keyframes tapk{0%{transform:scale(.5);opacity:1}70%{transform:scale(1.15);opacity:.9}100%{transform:scale(1.5);opacity:0}}`;
      document.head.appendChild(s);
      window.addEventListener('pointerdown', e => { const d = document.createElement('div'); d.className = 'tapdot'; d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; document.body.appendChild(d); setTimeout(() => d.remove(), 800); }, true);
    }
  });
}
module.exports = { open, cosmetics, DSF };
