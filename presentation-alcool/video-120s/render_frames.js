// Rendu image par image : node render_frames.js <sortie> [workers] [t1,t2,...]
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const out = process.argv[2]; const W = +(process.argv[3] || 4); const list = process.argv[4];
const FPS = 30, DUR = 120;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const url = 'file://' + path.join(__dirname, 'video.html');
  const times = list ? list.split(',').map(Number) : [...Array(FPS * DUR).keys()].map(i => i / FPS);
  let next = 0;
  const work = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
    page.on('pageerror', e => console.error('pageerror:', e.message));
    await page.goto(url); await page.evaluate(() => document.fonts.ready);
    if (next === 0) {
      const info = await page.evaluate(() => ({ err: window.ERR, sfx: window.SFX }));
      fs.writeFileSync(path.join(out, 'sfx.json'), JSON.stringify(info.sfx));
      if (info.err.length) console.error(info.err.join('\n'));
    }
    while (next < times.length) {
      const i = next++; const t = times[i];
      await page.evaluate(t => window.render(t), t);
      const name = list ? `k_${String(t).replace('.', '_')}.png` : `f${String(i).padStart(4, '0')}.png`;
      await page.screenshot({ path: path.join(out, name) });
      if (!list && i % 300 === 0) console.log('frame', i);
    }
    await page.close();
  };
  await Promise.all([...Array(W)].map(work));
  await browser.close();
})();
