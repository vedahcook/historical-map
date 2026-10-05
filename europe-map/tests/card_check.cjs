// Checks the city card in a headless browser: opens cities at given years (desktop 1400 x 900 and phone 390 x 844),
// moves the year a few times to make sure the card does not move, and saves screenshots to tests/shots/.
//   node tests/card_check.cjs '[["Vienna",1683,"views"],["Paris",1924,"ev"],["Prague",1109,null]]'
// Tab: views, ev, held, pop, or null to let the card choose its opening tab. Needs Playwright with Chromium
// (NODE_PATH=$(npm root -g) if installed globally). Run from europe-map/ after build_page.py. The city views'
// pictures are not in the repository: VIEWS=<folder> points at a local copy, else they come from the live site (which
// some workspaces cannot reach; the pictures then show as broken, but the layout checks still work).
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..'), shots = path.join(__dirname, 'shots'), PORT = 8790;
const LIVE = 'https://vedahcook.github.io/historical-map/', VIEWS = process.env.VIEWS || ['/home/claude/views/site/views'].find(f => fs.existsSync(f));
// topojson-client from a local copy when there is one (some workspaces cannot reach the CDN): npm install topojson-client
const TOPO = (() => { for (const d of [process.env.TOPOJSON, path.join(root, 'node_modules'), ...(process.env.NODE_PATH || '').split(':'), '/home/claude/views/node_modules']) { const f = d && (d.endsWith('.js') ? d : path.join(d, 'topojson-client/dist/topojson-client.min.js')); if (f && fs.existsSync(f)) return f; } return null; })();
const CHROME = process.env.CHROME || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(f => fs.existsSync(f));
fs.mkdirSync(shots, { recursive: true });
let src = fs.readFileSync(path.join(root, 'europe-borders.html'), 'utf8');
// a test hook inside the page's script (it is one function; the hook goes at its end)
const end = src.lastIndexOf('})();');
src = src.slice(0, end) + `window.__T = {
  open(name, y, tab) { const c = CITIES.find(c => c.n === name); fitBox([c.x - 60, c.y - 40, c.x + 60, c.y + 40]);
    setTimeout(() => { place = { x: c.x, y: c.y, city: c.i }; selCity = c.i; popClosed = false; cardPending = tab ? { tab } : null; setYear(y); drawCities(); renderPop(); }, 900); },
  year(y) { setYear(y); } };
` + src.slice(end);
fs.writeFileSync(path.join(root, '_t.html'), src);
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.json') ? 'application/json' : f.endsWith('.webp') ? 'image/webp' : 'application/octet-stream' }); r.end(b); } });
}).listen(PORT);
(async () => {
  const b = await chromium.launch(CHROME ? { executablePath: CHROME } : {});
  const errs = [];
  for (const [vw, vh, tag] of [[1400, 900, 'desk'], [390, 844, 'phone']]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh } });
    p.on('pageerror', e => errs.push(tag + ' ' + e.message));
    if (TOPO) await p.route('**/topojson-client.min.js', r => r.fulfill({ path: TOPO, contentType: 'application/javascript' }));
    await p.route(`http://localhost:${PORT}/views/**`, async r => {      // the pictures: a local copy (VIEWS=folder), else the live site, else none
      const u = decodeURIComponent(r.request().url().split('/views/')[1].split('?')[0]);
      if (VIEWS && fs.existsSync(path.join(VIEWS, u))) return r.fulfill({ path: path.join(VIEWS, u), contentType: 'image/webp' });
      try { await r.fulfill({ response: await r.fetch({ url: LIVE + 'views/' + u }) }); } catch { r.abort(); }
    });
    await p.goto(`http://localhost:${PORT}/_t.html`, { waitUntil: 'load', timeout: 180000 }); await p.waitForTimeout(2500);
    for (const [name, y, tab] of JSON.parse(process.argv[2] || '[["Vienna",1683,null],["Paris",1924,"ev"]]')) {
      await p.evaluate(([n, y, t]) => __T.open(n, y, t), [name, y, tab]); await p.waitForTimeout(3500);
      const box = () => p.evaluate(() => { const e = document.getElementById('mappop'), r = e.getBoundingClientRect(); return e.hidden ? 'hidden' : `${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)}`; });
      const seen = new Set(); for (const yy of [y, y + 1, y + 37, y - 50]) { await p.evaluate(yy => __T.year(yy), yy); await p.waitForTimeout(400); seen.add(await box()); }
      await p.evaluate(yy => __T.year(yy), y); await p.waitForTimeout(1500);
      const tabNow = await p.evaluate(() => { const t = document.querySelector('#mappop .ctabs [aria-selected=true]'); return t ? t.textContent : 'no card'; });
      console.log(tag, name, y, '| tab:', tabNow, '| card position across years:', [...seen].join(' / '), seen.size === 1 ? '(steady)' : '(MOVED)');
      await p.screenshot({ path: path.join(shots, `${tag}-${name}-${y}.png`) });
    }
    await p.close();
  }
  console.log('page errors:', errs.length ? errs.slice(0, 8) : 'none');
  await b.close(); srv.close(); fs.unlinkSync(path.join(root, '_t.html'));
})();
