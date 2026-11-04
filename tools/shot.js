// 可选：用无头 Chromium 给 docs/index.html 截图并收集报错（需要 Node 与 playwright）
// node tools/shot.js '[{"out":"a.png","eval":"...","dark":false,"w":1440,"h":900,"dpr":1}]'
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/npm-tools/node_modules/playwright')); }
const path = require('path');
(async () => {
  const page0 = 'file://' + path.resolve(process.env.PAGE || path.join(__dirname, '..', 'docs', 'index.html'));
  const jobs = JSON.parse(process.argv[2] || '[]');
  const opts = process.env.CHROME ? { executablePath: process.env.CHROME } : {};
  const browser = await chromium.launch(opts);
  for (const j of jobs) {
    const ctx = await browser.newContext({ viewport: { width: j.w || 1440, height: j.h || 900 }, colorScheme: j.dark ? 'dark' : 'light', deviceScaleFactor: j.dpr || 1 });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    await page.goto(page0);
    await page.waitForTimeout(800);
    if (j.eval) { try { const r = await page.evaluate(j.eval); if (r) console.log('eval:', JSON.stringify(r).slice(0, 2000)); } catch (e) { errs.push('eval: ' + e.message); } await page.waitForTimeout(j.wait || 700); }
    await page.screenshot({ path: j.out, fullPage: false });
    console.log(j.out, errs.length ? errs.join('\n') : 'ok');
    await ctx.close();
  }
  await browser.close();
})();
