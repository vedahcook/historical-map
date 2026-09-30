// Fetch OpenHistoricalMap border records for Europe 1495-1806 and save them as
// europe-borders-sources-1495-1806.json. Run in a browser on https://overpass-api.openhistoricalmap.org/api/status,
// poll window.__H.status until 'done', then read window.__H out in chunks (see the end).
//  - country and self-governing records (admin_level 2-3) and all level-4 records (member states of the
//    Holy Roman Empire, Italian and Iberian states and others) touching lat 34-72, lon -25..50
//  - member ways fetched whole where they touch lat 34-72, rounded to 1e-4 degrees and simplified with
//    Douglas-Peucker at 0.002 degrees
window.__H = { status: 'relations', ways: {}, rels: {}, extra: {}, errors: [], done: 0 };
(async () => {
  const G = window.__H;
  const run = async q => { for (let t = 0; t < 6; t++) { try { const r = await fetch('/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }); if (r.ok) return await r.json(); G.errors.push(r.status); } catch (e) { G.errors.push(String(e)); } await new Promise(s => setTimeout(s, 6000 * (t + 1))); } return null; };
  const dp = (pts, tol) => { if (pts.length < 3) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1; const st = [[0, pts.length - 1]]; while (st.length) { const [a, b] = st.pop(); const [ax, ay] = pts[a], [bx, by] = pts[b]; const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy; let md = -1, mi = -1; for (let i = a + 1; i < b; i++) { const [px, py] = pts[i]; let d; if (L === 0) d = (px - ax) ** 2 + (py - ay) ** 2; else { let t = ((px - ax) * dx + (py - ay) * dy) / L; t = Math.max(0, Math.min(1, t)); d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2; } if (d > md) { md = d; mi = i; } } if (md > tol * tol) { keep[mi] = 1; st.push([a, mi], [mi, b]); } } return pts.filter((_, i) => keep[i]); };
  const rec = r => ({ t: { n: r.tags['name:en'] || r.tags.name, nl: r.tags.name, l: r.tags.admin_level || '', b: r.tags.boundary || r.tags.type || '', s: r.tags.start_date || '', e: r.tags.end_date || '', wd: r.tags.wikidata || '' }, m: r.members.filter(m => m.type === 'way').map(m => [m.ref, m.role === 'inner' ? 1 : 0]) });
  const period = '(if: t["start_date"] < "1806" && (t["end_date"] >= "1495" || !is_tag("end_date")))';
  const rl = await run(`[out:json][timeout:300];relation["boundary"="administrative"]["admin_level"~"^[23]$"](34,-25,72,50)${period};out body;`);
  for (const r of rl.elements) G.rels[r.id] = rec(r);
  const l4 = await run(`[out:json][timeout:300];relation["boundary"="administrative"]["admin_level"="4"](34,-25,72,50)${period};out body;`);
  for (const r of l4.elements) G.extra[r.id] = rec(r);
  const all = [...new Set([...Object.values(G.rels), ...Object.values(G.extra)].flatMap(r => r.m.map(x => x[0])))];
  G.nways = all.length; G.status = 'ways';
  for (let i = 0; i < all.length; i += 1000) {
    const j = await run(`[out:json][timeout:300];way(id:${all.slice(i, i + 1000).join(',')})(34,-180,72,50);out geom;`);
    for (const w of (j ? j.elements : [])) G.ways[w.id] = dp(w.geometry.filter(Boolean).map(p => [Math.round(p.lon * 1e4) / 1e4, Math.round(p.lat * 1e4) / 1e4]), 0.002);
    G.done = i + 1000;
  }
  G.status = 'done';
})();
// Read out: JSON.stringify({ meta: { fetched: new Date().toISOString() }, rels: __H.rels, rels4: __H.extra, ways: __H.ways }), in slices
