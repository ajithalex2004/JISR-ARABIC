// Renders each template section to a 1080x1920 PNG in ../export (overlays keep a transparent background).
// Run: node marketing/ugc/source/render.js
const path = require('path');
const { chromium } = require('playwright');
const ids = ['endcard', 'hook', 'subtitle', 'wordcard', 'chip-emerald', 'chip-gold', 'tag', 'guide'];
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'templates.html'));
  await page.evaluate(() => document.fonts.ready);
  for (const id of ids) {
    const transparent = !['endcard', 'guide'].includes(id);
    await page.locator('#' + id).screenshot({ path: path.join(__dirname, '..', 'export', `jisr-${id}-1080x1920.png`), omitBackground: transparent });
  }
  await browser.close();
})();
