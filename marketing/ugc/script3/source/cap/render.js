const path = require('path'); const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 's3.html')); await p.evaluate(() => document.fonts.ready);
  await p.locator('#bg').screenshot({ path: path.join(__dirname, 'bg.png') });
  await p.locator('#mask').screenshot({ path: path.join(__dirname, 'mask.png') });
  for (const id of await p.$$eval('#caps section', s => s.map(x => x.id)))
    await p.locator('#' + id).screenshot({ path: path.join(__dirname, id + '.png'), omitBackground: true });
  await b.close();
})();
