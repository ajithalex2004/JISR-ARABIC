// Script 3 "Tap. Hear. Understand.": records the five app scenes for one class at 1080x1920.
// Usage: node s3/record.js <grade>
const fs = require('fs'); const path = require('path');
const { open, cosmetics } = require('./common');
const grade = Number(process.argv[2]);
const PLAN = {
  2: { lesson: 'lesson_g2_t1_ch01', challenge: 2 },
  5: { lesson: 'lesson_01_ball_games', challenge: 2 },
  8: { lesson: 'lesson_g8_t1_ch01', challenge: 2 },
}[grade];
(async () => {
  const lessonFile = fs.readdirSync(path.join(__dirname, '..', 'apicache')).filter(f => f.endsWith('.json'))
    .map(f => [f, JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'apicache', f)))]).find(([, m]) => m.path === `/api/curriculum/lesson/${PLAN.lesson}`);
  const content = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'apicache', lessonFile[0].replace('.json', '.body')))).content;
  const card = content.vocabulary_cards[0];
  const exampleWords = card.example_ar.split(/\s+/).map(w => w.replace(/[.،؟!:]/g, '')).filter(w => w && w !== card.vowelled_ar);
  const challenge = content.sentence_builder.challenges[PLAN.challenge - 1];
  const { b, ctx, p, events } = await open(grade);
  await cosmetics(p);
  const OUT = path.join(__dirname, 'shots', `g${grade}`); fs.mkdirSync(OUT, { recursive: true });
  const cdp = await ctx.newCDPSession(p);
  let frames = [], rec = false;
  cdp.on('Page.screencastFrame', async f => { if (rec) frames.push({ ts: f.metadata.timestamp, data: f.data }); await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {}); });
  const meta = { grade, card: { word: card.vowelled_ar, meaning: card.meaning_en, example: card.example_ar, example_en: card.example_en }, exampleWords, challenge };
  const ev = (name) => events.push({ name, wall: Date.now() / 1000 });
  async function shot(name, fn) {
    frames = []; rec = true; const evStart = events.length;
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 93, maxWidth: 1080, maxHeight: 1920 });
    await fn(); await p.waitForTimeout(250);
    await cdp.send('Page.stopScreencast'); rec = false;
    const dir = path.join(OUT, name); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    let list = '';
    frames.forEach((fr, i) => { const f = `f${String(i).padStart(5, '0')}.jpg`; fs.writeFileSync(path.join(dir, f), Buffer.from(fr.data, 'base64'));
      const next = frames[i + 1] ? frames[i + 1].ts : fr.ts + 0.25; list += `file '${f}'\nduration ${Math.max(0.005, next - fr.ts).toFixed(4)}\n`; });
    list += `file 'f${String(frames.length - 1).padStart(5, '0')}.jpg'\n`; fs.writeFileSync(path.join(dir, 'list.txt'), list);
    const t0 = frames[0].ts;
    meta[name] = { duration: frames[frames.length - 1].ts + 0.25 - t0, events: events.slice(evStart).map(e => ({ name: e.name, t: +(e.wall - t0).toFixed(3) })) };
    console.log(name, JSON.stringify(meta[name]));
  }
  const smoothScroll = async (dy, ms) => { const n = Math.round(ms / 16); for (let i = 0; i < n; i++) { await p.mouse.wheel(0, dy / n); await p.waitForTimeout(16); } };
  const tap = async (loc, label) => { await loc.scrollIntoViewIfNeeded(); const bb = await loc.boundingBox(); ev('tap:' + label); await p.mouse.click(bb.x + bb.width / 2, bb.y + bb.height / 2); };
  const headword = p.getByText(card.vowelled_ar, { exact: true }).first();
  // Frame the first card: its headword near the top third.
  await headword.scrollIntoViewIfNeeded();
  await p.evaluate(y => window.scrollBy(0, y), (await headword.boundingBox()).y - 230);
  await p.mouse.move(385, 400); await p.waitForTimeout(800);
  await shot('S1_word', async () => { await p.waitForTimeout(1300); await tap(headword, 'word'); await p.waitForTimeout(2300); });
  // A small scroll and back closes the headword popup, so only one popup shows at a time.
  await smoothScroll(20, 150); await smoothScroll(-20, 150); await p.waitForTimeout(400);
  await shot('S2_words', async () => {
    await p.waitForTimeout(300); await tap(p.getByText(exampleWords[0], { exact: true }).first(), 'w1');
    await p.waitForTimeout(1300); await tap(p.getByText(exampleWords[1], { exact: true }).first(), 'w2'); await p.waitForTimeout(1500);
  });
  // Scrolling closes the word popup and lifts the example's English line above the audio panel.
  await smoothScroll(100, 400); await p.waitForTimeout(500);
  await shot('S3_sentence', async () => {
    await p.mouse.move(385, 400); await p.waitForTimeout(300);
    await tap(p.getByText('listen sentence').first(), 'sentence'); await p.waitForTimeout(6000);
  });
  await smoothScroll(-100, 400); await p.waitForTimeout(500);
  await shot('S4_slow', async () => {
    await p.waitForTimeout(300); await tap(p.getByRole('button', { name: 'Slow 0.6x' }).first(), 'slow');
    await p.waitForTimeout(700); await tap(headword, 'word'); await p.waitForTimeout(3600);
  });
  await p.getByRole('button', { name: 'Normal 1.0x' }).first().click();
  await p.getByRole('button', { name: 'Close audio toolbar' }).click().catch(() => {});
  await p.getByText('(Sentence Builder)').first().click(); await p.waitForTimeout(1200);
  await cosmetics(p);
  await p.getByRole('button', { name: `Challenge ${PLAN.challenge}` }).click(); await p.waitForTimeout(800);
  const target = p.getByText(challenge.target_en, { exact: true }).first();
  await target.scrollIntoViewIfNeeded(); await p.evaluate(y => window.scrollBy(0, y), (await target.boundingBox()).y - 130);
  await p.mouse.move(385, 680); await p.waitForTimeout(800);
  await shot('S5_build', async () => {
    await p.waitForTimeout(500);
    for (const [i, tile] of challenge.tiles.entries()) { await tap(p.locator('main button', { hasText: tile }).last(), 'tile' + i); await p.waitForTimeout(550); }
    await tap(p.getByRole('button', { name: /Check Sentence/ }).first(), 'check'); await p.waitForTimeout(1800);
  });
  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify(meta, null, 1));
  await b.close();
})();
