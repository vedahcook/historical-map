const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }); const p = await b.newPage({ viewport: { width: 1150, height: 1100 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  const html = fs.readFileSync('site/city-views.html', 'utf8');
  fs.writeFileSync('site/_preview.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + html + '</body></html>');
  await p.goto('file:///home/claude/views/site/_preview.html'); await p.waitForTimeout(500);
  const setY = y => p.evaluate(y => { const s = document.getElementById('year'); s.value = y; s.dispatchEvent(new Event('input')); }, y);
  const setC = k => p.evaluate(k => { const s = document.getElementById('citysel'); s.value = k; s.dispatchEvent(new Event('change')); }, k);
  const keys = await p.evaluate(() => [...document.querySelectorAll('#citysel option')].map(o => o.value));
  const bad = [];
  for (const m of ['desk', 'phone']) {
    await p.click(`#modes button[data-m="${m}"]`); await p.waitForTimeout(150);
    for (const k of keys) { await setC(k);
      for (const t of ['events', 'held', 'pop']) { await p.click(`.tabs button[data-tab="${t}"]:visible`); const g = new Set();
        for (const y of [1100, 1600, 1900, 2026]) { await setY(y);
          g.add(await p.evaluate(m => { const root = m === 'phone' ? document.getElementById('sbody') : document.getElementById('pop'); const r0 = root.getBoundingClientRect(); const R = s => root.querySelector(s).getBoundingClientRect();
            return `card ${Math.round(r0.height)} band ${Math.round(R('.band').top - r0.top)}+${Math.round(R('.band').height)} scroll ${Math.round(R('.scroll').top - r0.top)}`; }, m)); }
        if (g.size > 1) bad.push(`${m} ${k} ${t}: ${[...g].join(' | ')}`);
      } }
  }
  console.log('cities', keys.length, 'unstable', bad.length, bad.slice(0, 5)); console.log('errors', errs.slice(0, 5));
  await p.click('#modes button[data-m="desk"]');
  for (const [k, y] of [['bruges', 1660], ['granada', 1900], ['aleppo', 1540], ['chi-in-u', 1900]]) { await setC(k); await p.click('.tabs button[data-tab="events"]:visible'); await setY(y); await p.waitForTimeout(300); await p.locator('#pop').screenshot({ path: `s3-${k}.png` }); }
  await p.screenshot({ path: 's3-top.png', clip: { x: 0, y: 0, width: 1150, height: 220 } });
  await b.close();
})();
