// Checks the places layer: highlights a country at a year (as if tapping a point inside it), takes a screenshot, then
// opens a place's popup and takes another (desktop 1400 x 900 and phone 390 x 844). Screenshots go to tests/shots/.
//   NODE_PATH=$(npm root -g) node tests/places_check.cjs '[["France",2.35,48.85,1450,"agincourt"],["Poland",21.0,52.2,1990,"grunwald"]]'
// Each row: a label, a longitude and latitude inside the country, the year, and a place id to open (or null).
// Same setup as card_check.cjs (Playwright with Chromium; topojson-client from TOPOJSON or NODE_PATH).
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..'), shots = path.join(__dirname, 'shots'), PORT = 8791;
const TOPO = (() => { for (const d of [process.env.TOPOJSON, path.join(root, 'node_modules'), ...(process.env.NODE_PATH || '').split(':')]) { const f = d && (d.endsWith('.js') ? d : path.join(d, 'topojson-client/dist/topojson-client.min.js')); if (f && fs.existsSync(f)) return f; } return null; })();
const CHROME = process.env.CHROME || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(f => fs.existsSync(f));
fs.mkdirSync(shots, { recursive: true });
let src = fs.readFileSync(path.join(root, 'europe-borders.html'), 'utf8');
const end = src.lastIndexOf('})();');
src = src.slice(0, end) + `window.__P = {
  focus(y, x, yk) { setYear(y); fitBox([x - 450, yk - 450, x + 450, yk + 450]);
    const go = () => { if (!eraOf(y).ready || animating) return setTimeout(go, 200); const f = regionAt(x, yk); place = { x, y: yk, s: f ? f.properties.s : -1, E: curEra() }; popClosed = false;
      drawPin(); drawDim(); drawLabels(); drawBadges(); drawCities(); renderTimeline(); renderPop(); }; setTimeout(go, 900); },
  open(id) { openPlace(id, true); },
  marks() { return plDots.map(m => m.p.id); },
  dbg() { return { sel: selPlace, on: [...document.querySelectorAll('#places .plm.on')].length, all: document.querySelectorAll('#places .plm').length }; } };
` + src.slice(end);
fs.writeFileSync(path.join(root, '_p.html'), src);
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.json') ? 'application/json' : 'application/octet-stream' }); r.end(b); } });
}).listen(PORT);
// map position in km from longitude and latitude: Lambert equal-area for Europe (EPSG:3035), as the cities are placed
function laea(lon, lat) {
  const a = 6378137, e2 = 0.00669438002290, e = Math.sqrt(e2), rad = Math.PI / 180, lat0 = 52 * rad, lon0 = 10 * rad;
  const q = p => (1 - e2) * (Math.sin(p) / (1 - e2 * Math.sin(p) ** 2) - Math.log((1 - e * Math.sin(p)) / (1 + e * Math.sin(p))) / (2 * e));
  const qp = q(Math.PI / 2), b = p => Math.asin(q(p) / qp), Rq = a * Math.sqrt(qp / 2);
  const D = a * Math.cos(lat0) / Math.sqrt(1 - e2 * Math.sin(lat0) ** 2) / (Rq * Math.cos(b(lat0)));
  const be = b(lat * rad), b1 = b(lat0), L = lon * rad - lon0;
  const B = Rq * Math.sqrt(2 / (1 + Math.sin(b1) * Math.sin(be) + Math.cos(b1) * Math.cos(be) * Math.cos(L)));
  const E = 4321000 + B * D * Math.cos(be) * Math.sin(L), N = 3210000 + B / D * (Math.cos(b1) * Math.sin(be) - Math.sin(b1) * Math.cos(be) * Math.cos(L));
  return [E / 1000, -N / 1000];
}
(async () => {
  const b = await chromium.launch(CHROME ? { executablePath: CHROME } : {});
  const errs = [];
  for (const [vw, vh, tag] of [[1400, 900, 'desk'], [390, 844, 'phone']]) {
    const p = await b.newPage({ viewport: { width: vw, height: vh } });
    p.on('pageerror', e => errs.push(tag + ' ' + e.message));
    if (TOPO) await p.route('**/topojson-client.min.js', r => r.fulfill({ path: TOPO, contentType: 'application/javascript' }));
    await p.goto(`http://localhost:${PORT}/_p.html`, { waitUntil: 'load', timeout: 180000 }); await p.waitForTimeout(2500);
    for (const [label, lon, lat, y, id] of JSON.parse(process.argv[2])) {
      const [x, yk] = laea(lon, lat);
      await p.evaluate(([y, x, yk]) => __P.focus(y, x, yk), [y, x, yk]); await p.waitForTimeout(3500);
      console.log(tag, label, y, '| places shown:', (await p.evaluate(() => __P.marks())).join(', '));
      await p.screenshot({ path: path.join(shots, `${tag}-${label}-${y}-map.png`) });
      if (id) { await p.evaluate(id => __P.open(id), id); await p.waitForTimeout(1800); console.log(tag, 'after open', JSON.stringify(await p.evaluate(() => __P.dbg()))); await p.screenshot({ path: path.join(shots, `${tag}-${label}-${y}-${id}.png`) }); }
    }
    await p.close();
  }
  console.log('page errors:', errs.length ? errs.slice(0, 8) : 'none');
  await b.close(); srv.close(); fs.unlinkSync(path.join(root, '_p.html'));
})();
