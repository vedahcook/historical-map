const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1150, height: 1100 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  const html = fs.readFileSync('site/city-views.html', 'utf8');
  fs.writeFileSync('site/_preview.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + html + '</body></html>');
  await p.goto('file:///home/claude/views/site/_preview.html'); await p.waitForTimeout(400);
  const setY = y => p.evaluate(y => { const s = document.getElementById('year'); s.value = y; s.dispatchEvent(new Event('input')); }, y);
  const bad = [], out = [];
  for (const m of ['desk', 'phone']) {
    await p.click(`#modes button[data-m="${m}"]`); await p.waitForTimeout(200);
    for (const ci of [1, 2, 3, 4]) { await p.click(`#cities button:nth-child(${ci})`);
      for (const t of ['events', 'held', 'pop']) { await p.click(`.tabs button[data-tab="${t}"]:visible`);
        const g = new Set();
        for (const y of [1000, 1349, 1572, 1740, 1871, 1945, 2026]) { await setY(y);
          g.add(await p.evaluate(m => { const root = m === 'phone' ? document.getElementById('sbody') : document.getElementById('pop'); const r0 = root.getBoundingClientRect(); const R = s => root.querySelector(s).getBoundingClientRect();
            const sc = root.querySelector('.scroll'), cr = R('.credit');
            return `card ${Math.round(r0.height)} band ${Math.round(R('.band').top - r0.top)}+${Math.round(R('.band').height)} scroll ${Math.round(R('.scroll').top - r0.top)}-${Math.round(R('.scroll').bottom - r0.top)} creditBottomGap ${sc.scrollHeight <= sc.clientHeight ? Math.round(R('.scroll').bottom - cr.bottom) : 'scrolls'}`; }, m));
        }
        const k = `${m} c${ci} ${t}`; out.push(k + ': ' + [...g].join(' | ')); if ([...g].map(s => s.replace(/ creditBottomGap.*/, '')).filter((v, i, a) => a.indexOf(v) === i).length > 1) bad.push(k);
      } }
  }
  console.log(out.join('\n')); console.log('unstable:', bad);
  await p.click('#modes button[data-m="desk"]'); await p.click('#cities button:nth-child(1)'); await p.click('.tabs button[data-tab="events"]:visible'); await setY(1740); await p.waitForTimeout(200);
  await p.locator('#pop').screenshot({ path: 'd-ev.png' });
  await p.click('.tabs button[data-tab="held"]:visible'); await setY(1845); await p.waitForTimeout(200);
  await p.locator('#pop').screenshot({ path: 'd-held.png' });
  await p.click('#cities button:nth-child(4)'); await p.click('.tabs button[data-tab="pop"]:visible'); await setY(1453); await p.waitForTimeout(200);
  await p.locator('#pop').screenshot({ path: 'd-pop.png' });
  await p.click('#modes button[data-m="phone"]'); await p.click('#cities button:nth-child(2)'); await p.click('.tabs button[data-tab="events"]:visible'); await setY(1683); await p.waitForTimeout(300);
  await p.locator('#phone').screenshot({ path: 'p-ev.png' });
  await p.click('.tabs button[data-tab="pop"]:visible'); await setY(1857); await p.waitForTimeout(300);
  await p.locator('#phone').screenshot({ path: 'p-pop.png' });
  console.log('errors', errs); await b.close();
})();
