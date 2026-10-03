// Per city: the map's population figures, who held it each year (with light and dark swatches) and its flags.
// Usage: NODE_PATH=$(npm root -g) node extract_all.cjs "Name1" "Name2" ...  -> city_data.json, flags_data.json
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const NAMES = process.argv.slice(2);
(async () => {
const root = '/home/claude/historical-map/europe-map';
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.json') ? 'application/json' : 'application/octet-stream' }); r.end(b); } }); }).listen(8765);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }); const p = await b.newPage({ viewport: { width: 1300, height: 850 } });
await p.route('**/topojson-client.min.js', r => r.fulfill({ path: '/home/claude/views/node_modules/topojson-client/dist/topojson-client.min.js', contentType: 'application/javascript' }));
await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
p.on('pageerror', e => console.error('PAGEERR', e.message));
await p.goto('http://localhost:8765/_x.html', { waitUntil: 'load', timeout: 180000 });
await p.waitForFunction(() => window.__X, null, { timeout: 180000 });
await p.evaluate(() => __X.ERAS.forEach(E => __X.loadEra(E)));
await p.waitForFunction(() => __X.ERAS.every(E => E.ready), null, { timeout: 240000 });
const out = await p.evaluate(names => {
  const tmp = document.createElement('div'); document.body.appendChild(tmp);
  const resolve = bg => { tmp.style.background = bg; const cs = getComputedStyle(tmp); return cs.backgroundImage !== 'none' ? cs.backgroundImage + ', ' + cs.backgroundColor : cs.backgroundColor; };
  const { CITIES, cityUnit, heldBy, flagOf, D, Y1, CSRC } = __X, F = D.flags, used = new Set(); const res = {}, fres = {}, missing = [];
  for (const n of names) {
    const c = CITIES.find(c => c.n === n); if (!c) { missing.push(n); continue; }
    const runs = [], fr = [];
    for (let y = 1000; y <= Y1; y++) {
      const u = cityUnit(c, y), last = runs[runs.length - 1], h = heldBy(u, y);
      if (last && last.b === y - 1 && last.t === h.t && last.by === h.by && last.bg === h.bg) last.b = y; else runs.push({ ...h, a: y, b: y });
      const fi = u >= 0 ? flagOf(u, y) : -1, fl = fr[fr.length - 1];
      if (fl && fl[2] === fi && fl[1] === y - 1) fl[1] = y; else fr.push([y, y, fi]); if (fi >= 0) used.add(fi);
    }
    document.documentElement.setAttribute('data-theme', 'light'); const light = runs.map(r => resolve(r.bg));
    document.documentElement.setAttribute('data-theme', 'dark'); const dark = runs.map(r => resolve(r.bg));
    document.documentElement.removeAttribute('data-theme');
    res[n] = { P: c.P, runs: runs.map((r, i) => ({ t: r.t, by: r.by, a: r.a, b: r.b, l: light[i], d: dark[i] })) };
    fres[n] = fr.filter(r => r[2] >= 0);
  }
  const items = {}, credits = {};
  for (const i of used) { items[i] = F.items[i]; credits[i] = F.credits[i]; }
  return { data: { res, Y1, CSRC }, flags: { res: fres, items, credits, sheet: F.sheet }, missing };
}, NAMES);
fs.writeFileSync('city_data.json', JSON.stringify(out.data)); fs.writeFileSync('flags_data.json', JSON.stringify(out.flags));
console.log('cities', Object.keys(out.data.res).length, 'missing', out.missing, 'flags used', Object.keys(out.flags.items).length);
await b.close(); srv.close();
})();
