// Fetch OpenHistoricalMap border records for Europe 1900-2026, plus DeepState's map of
// Russian-occupied Ukraine on July 1 of 2022-2026, and save them as
// europe-borders-sources-1900-2026.json. Run in a browser console on
// https://overpass-api.openhistoricalmap.org/api/status, poll window.__H.status until 'done',
// then run the save step at the bottom.
//  - country and self-governing records (admin_level 2-3) touching lat 34-72, lon -25..50
//  - a few other records: Northern Cyprus, the German occupation zone in Denmark (1943-45),
//    the Italian occupation of Corsica, the German operational zones in Italy, the Soviet
//    military administration in Germany, the Republic of Crimea (2014-)
//  - member ways fetched whole where they touch lat 34-72, rounded to 1e-4 degrees and simplified
//    with Douglas-Peucker at 0.002 degrees
window.__H = { status: 'relations', ways: {}, rels: {}, extra: {}, errors: [], done: 0 };
(async () => {
  const G = window.__H;
  const run = async q => { for (let t = 0; t < 6; t++) { try { const r = await fetch('/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }); if (r.ok) return await r.json(); G.errors.push(r.status); } catch (e) { G.errors.push(String(e)); } await new Promise(s => setTimeout(s, 6000 * (t + 1))); } return null; };
  const dp = (pts, tol) => { if (pts.length < 3) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1; const st = [[0, pts.length - 1]]; while (st.length) { const [a, b] = st.pop(); const [ax, ay] = pts[a], [bx, by] = pts[b]; const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy; let md = -1, mi = -1; for (let i = a + 1; i < b; i++) { const [px, py] = pts[i]; let d; if (L === 0) d = (px - ax) ** 2 + (py - ay) ** 2; else { let t = ((px - ax) * dx + (py - ay) * dy) / L; t = Math.max(0, Math.min(1, t)); d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2; } if (d > md) { md = d; mi = i; } } if (md > tol * tol) { keep[mi] = 1; st.push([a, mi], [mi, b]); } } return pts.filter((_, i) => keep[i]); };
  const rec = r => ({ t: { n: r.tags['name:en'] || r.tags.name, nl: r.tags.name, l: r.tags.admin_level || '', b: r.tags.boundary || r.tags.type || '', s: r.tags.start_date || '', e: r.tags.end_date || '', wd: r.tags.wikidata || '' }, m: r.members.filter(m => m.type === 'way').map(m => [m.ref, m.role === 'inner' ? 1 : 0]) });
  const period = '(if: t["start_date"] < "2027" && (t["end_date"] >= "1900" || !is_tag("end_date")))';
  const rl = await run(`[out:json][timeout:300];relation["boundary"="administrative"]["admin_level"~"^[23]$"](34,-25,72,50)${period};out body;`);
  for (const r of rl.elements) G.rels[r.id] = rec(r);
  const ex = await run(`[out:json][timeout:300];relation(id:2801348,2748851,2839233,2839234,2956709,2956736,2879989,2961565,2693415,2855399,2957460,2748559,2859007,2854266,2960491,2958257,2696479);out body;`);
  for (const r of ex.elements) G.extra[r.id] = rec(r);
  const all = [...new Set([...Object.values(G.rels), ...Object.values(G.extra)].flatMap(r => r.m.map(x => x[0])))];
  G.nways = all.length; G.status = 'ways';
  for (let i = 0; i < all.length; i += 1000) {
    const j = await run(`[out:json][timeout:300];way(id:${all.slice(i, i + 1000).join(',')})(34,-180,72,50);out geom;`);
    for (const w of (j ? j.elements : [])) G.ways[w.id] = dp(w.geometry.filter(Boolean).map(p => [Math.round(p.lon * 1e4) / 1e4, Math.round(p.lat * 1e4) / 1e4]), 0.002);
    G.done = i + 1000;
  }
  // DeepState: the snapshot nearest before July 1 of each year; keep the areas marked occupied
  const ids = { 2022: 1656655372, 2023: 1688077565, 2024: 1719745832, 2025: 1751314076, 2026: 1782827647 };
  const rnd = c => typeof c[0] === 'number' ? [Math.round(c[0] * 1e4) / 1e4, Math.round(c[1] * 1e4) / 1e4] : c.map(rnd);
  const flat = g => g.type === 'GeometryCollection' ? g.geometries.flatMap(flat) : (g.type === 'Polygon' || g.type === 'MultiPolygon') ? [{ type: g.type, coordinates: rnd(g.coordinates) }] : [];
  G.deepstate = {};
  for (const [y, id] of Object.entries(ids)) {
    const j = await (await fetch(`https://deepstatemap.live/api/history/${id}/geojson`)).json();
    G.deepstate[y] = j.features.filter(f => /Occupied/.test((f.properties && f.properties.name) || '')).flatMap(f => flat(f.geometry));
  }
  G.status = 'done';
})();
// Save step (after status is 'done'):
// const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ meta: { fetched: new Date().toISOString() }, rels: __H.rels, extra: __H.extra, ways: __H.ways, deepstate: __H.deepstate })], { type: 'application/json' })); a.download = 'europe-borders-sources-1900-2026.json'; a.click();
