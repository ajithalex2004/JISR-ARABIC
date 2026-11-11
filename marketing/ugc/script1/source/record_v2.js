// Full-resolution (1080x1920) capture of the JISR app scenes for the Script 1 video.
const fs = require('fs'); const path = require('path');
const { chromium } = require('playwright');
const OUT = path.join(__dirname, 'shots2');
const DSF = 1080 / 390;
(async () => {
  const b = await chromium.launch({ args: ['--force-device-scale-factor=' + DSF] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 693 }, deviceScaleFactor: DSF, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const crypto = require('crypto');
  await ctx.route('**/api/**', async route => {
    const req = route.request(); const u = new URL(req.url());
    const key = crypto.createHash('sha1').update(req.method() + u.pathname + u.search + (req.postData() || '')).digest('hex');
    const f = path.join(__dirname, 'apicache', key);
    if (!fs.existsSync(f + '.body')) {
      const resp = await route.fetch({ url: 'https://api.jisrarabic.com' + u.pathname + u.search, headers: { 'content-type': req.headers()['content-type'] || 'application/json' } });
      fs.writeFileSync(f + '.body', await resp.body());
      fs.writeFileSync(f + '.json', JSON.stringify({ status: resp.status(), ct: resp.headers()['content-type'] || '', path: u.pathname }));
      console.log('fetched', resp.status(), u.pathname);
    }
    const m = JSON.parse(fs.readFileSync(f + '.json'));
    await route.fulfill({ status: m.status, contentType: m.ct, body: fs.readFileSync(f + '.body'), headers: { 'access-control-allow-origin': '*' } });
  });
  const events = [];
  const ev = (name) => events.push({ name, wall: Date.now() / 1000 });
  p.on('request', r => { if (/audio\/cache\/.*\.mp3/.test(r.url())) ev('audio:' + r.url().split('/').pop()); });
  await p.goto('http://127.0.0.1:5173/?grade=5', { waitUntil: 'load' });
  await p.waitForSelector('text=al-kuratu', { timeout: 60000 });
  await p.waitForTimeout(2500);
  const cosmetics = async () => p.evaluate(() => {
    const hide = (re) => document.querySelectorAll('body *').forEach(el => {
      const t = (el.textContent || '').trim();
      if (t.length < 80 && re.test(t) && ![...el.children].some(c => re.test((c.textContent || '').trim()))) el.style.visibility = 'hidden';
    });
    hide(/^Fahim v\d/); hide(/INTERACTIVE DEMO ACTIVE/i); hide(/vai-draft/i); hide(/^v\d+\.\d+\.\d+$/); hide(/TERM\s*1/i);
    if (!document.getElementById('tapstyle')) {
      const s = document.createElement('style'); s.id = 'tapstyle';
      s.textContent = `.tapdot{position:fixed;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;background:rgba(224,176,75,.45);border:3px solid #E0B04B;pointer-events:none;z-index:2147483647;animation:tapk .7s ease-out forwards}
        @keyframes tapk{0%{transform:scale(.5);opacity:1}70%{transform:scale(1.15);opacity:.9}100%{transform:scale(1.5);opacity:0}}`;
      document.head.appendChild(s);
      window.addEventListener('pointerdown', e => { const d = document.createElement('div'); d.className = 'tapdot'; d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; document.body.appendChild(d); setTimeout(() => d.remove(), 800); }, true);
    }
  });
  await cosmetics();
  const cdp = await ctx.newCDPSession(p);
  let frames = [], rec = false;
  cdp.on('Page.screencastFrame', async f => {
    if (rec) frames.push({ ts: f.metadata.timestamp, data: f.data });
    await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  const meta = {};
  async function shot(name, fn) {
    frames = []; rec = true; const evStart = events.length;
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 93, maxWidth: 1080, maxHeight: 1920 });
    await fn();
    await p.waitForTimeout(300);
    await cdp.send('Page.stopScreencast'); rec = false;
    const dir = path.join(OUT, name); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    let list = '';
    frames.forEach((fr, i) => {
      const f = `f${String(i).padStart(5, '0')}.jpg`; fs.writeFileSync(path.join(dir, f), Buffer.from(fr.data, 'base64'));
      const next = frames[i + 1] ? frames[i + 1].ts : fr.ts + 0.3;
      list += `file '${f}'\nduration ${Math.max(0.005, next - fr.ts).toFixed(4)}\n`;
    });
    list += `file 'f${String(frames.length - 1).padStart(5, '0')}.jpg'\n`;
    fs.writeFileSync(path.join(dir, 'list.txt'), list);
    const t0 = frames[0].ts;
    meta[name] = { duration: frames[frames.length - 1].ts + 0.3 - t0, frames: frames.length,
      events: events.slice(evStart).map(e => ({ name: e.name, t: +(e.wall - t0).toFixed(3) })) };
    console.log(name, JSON.stringify(meta[name]));
  }
  const smoothScroll = async (dy, ms) => { const steps = Math.round(ms / 16); for (let i = 0; i < steps; i++) { await p.mouse.wheel(0, dy / steps); await p.waitForTimeout(16); } };
  const tapAt = async (loc, label) => { const bb = await loc.boundingBox(); ev('tap:' + label); await p.mouse.click(bb.x + bb.width / 2, bb.y + bb.height / 2); };
  await p.evaluate(() => window.scrollTo(0, 0)); await p.mouse.move(380, 680); await p.waitForTimeout(500);
  await shot('A_lesson', async () => { await p.waitForTimeout(1000); await smoothScroll(330, 2200); await p.waitForTimeout(1000); });
  await shot('B_tapword', async () => { await p.waitForTimeout(500); await tapAt(p.getByText('al-kuratu', { exact: true }).first(), 'word'); await p.waitForTimeout(3200); });
  await shot('C_slow', async () => {
    await p.waitForTimeout(400); await tapAt(p.getByRole('button', { name: 'Slow 0.6x' }).first(), 'slow');
    await p.waitForTimeout(900); await tapAt(p.getByText('al-kuratu', { exact: true }).first(), 'word'); await p.waitForTimeout(3800);
  });
  await tapAt(p.getByRole('button', { name: 'Normal 1.0x' }).first(), 'normal');
  await p.getByText('(Reading & Listening)').first().click(); await p.waitForTimeout(3500);
  await cosmetics();
  await p.evaluate(() => { const el = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /Football is the number one/.test(e.textContent || '')); el.closest('div').scrollIntoView({ block: 'center' }); window.scrollBy(0, -120); });
  await p.mouse.move(380, 680); await p.waitForTimeout(1200);
  await shot('E_drill', async () => {
    await p.waitForTimeout(800);
    const pt = await p.evaluate(() => { const el = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /Football is the number one/.test(e.textContent || ''));
      let c = el; for (let i = 0; i < 8 && c; i++) { const b = c.querySelector('button'); if (b) { const r = b.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; } c = c.parentElement; } return null; });
    ev('tap:drill'); await p.mouse.click(pt.x, pt.y); await p.waitForTimeout(5800);
  });
  fs.writeFileSync(path.join(__dirname, 'meta_v2.json'), JSON.stringify(meta, null, 1));
  await b.close();
})();
