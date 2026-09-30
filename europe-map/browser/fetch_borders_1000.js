// Fetch OpenHistoricalMap border records for Europe 995-1505 (the medieval era, 1000-1499) and save them as
// europe-borders-sources.json in that era's working folder. Run in a browser on
// https://overpass-api.openhistoricalmap.org/api/status, poll window.__M.status until 'done', then read
// JSON.stringify(window.__M.out) in slices.
//  - country and self-governing records (admin_level 2-3) and level-4 records touching lat 34-72, lon -25..50
//  - records made of other records (a kingdom of its provinces): the member records, in 'sub' and 'subs'
//  - member ways fetched whole where they touch lat 34-72, rounded to 1e-4 degrees and simplified with
//    Douglas-Peucker at 0.002 degrees
window.__M = { status: 'relations', ways: {}, rels: {}, extra: {}, sub: {}, subs: {}, errors: [], done: 0 };
(async () => {
  const G = window.__M;
  const run = async q => { for (let t = 0; t < 6; t++) { try { const r = await fetch('/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }); if (r.ok) return await r.json(); G.errors.push(r.status); } catch (e) { G.errors.push(String(e)); } await new Promise(s => setTimeout(s, 6000 * (t + 1))); } return null; };
  const dp = (pts, tol) => { if (pts.length < 3) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1; const st = [[0, pts.length - 1]]; while (st.length) { const [a, b] = st.pop(); const [ax, ay] = pts[a], [bx, by] = pts[b]; const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy; let md = -1, mi = -1; for (let i = a + 1; i < b; i++) { const [px, py] = pts[i]; let d; if (L === 0) d = (px - ax) ** 2 + (py - ay) ** 2; else { let t = ((px - ax) * dx + (py - ay) * dy) / L; t = Math.max(0, Math.min(1, t)); d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2; } if (d > md) { md = d; mi = i; } } if (md > tol * tol) { keep[mi] = 1; st.push([a, mi], [mi, b]); } } return pts.filter((_, i) => keep[i]); };
  const rec = r => ({ t: { n: r.tags['name:en'] || r.tags.name, nl: r.tags.name, l: r.tags.admin_level || '', b: r.tags.boundary || r.tags.type || '', s: r.tags.start_date || '', e: r.tags.end_date || '', wd: r.tags.wikidata || '' }, m: r.members.filter(m => m.type === 'way').map(m => [m.ref, m.role === 'inner' ? 1 : 0]) });
  // start dates are text: medieval ones sort as "0995" ... "1505"; a record with no start date is left out
  const period = '(if: is_tag("start_date") && t["start_date"] < "1506" && t["start_date"] >= "0" && (t["end_date"] >= "0995" || !is_tag("end_date")))';
  const rl = await run(`[out:json][timeout:300];relation["boundary"="administrative"]["admin_level"~"^[123]$"](34,-25,72,50)${period};out body;`);
  for (const r of rl.elements) G.rels[r.id] = rec(r);
  const l4 = await run(`[out:json][timeout:300];relation["boundary"="administrative"]["admin_level"="4"](34,-25,72,50)${period};out body;`);
  for (const r of l4.elements) G.extra[r.id] = rec(r);
  // member records
  const parents = [...rl.elements, ...l4.elements].filter(r => r.members.some(m => m.type === 'relation'));
  for (const r of parents) G.subs[r.id] = r.members.filter(m => m.type === 'relation').map(m => m.ref);
  const kids = [...new Set(Object.values(G.subs).flat())];
  G.status = 'members';
  for (let i = 0; i < kids.length; i += 500) {
    const j = await run(`[out:json][timeout:300];relation(id:${kids.slice(i, i + 500).join(',')});out body;`);
    for (const r of (j ? j.elements : [])) G.sub[r.id] = rec(r);
  }
  const all = [...new Set([...Object.values(G.rels), ...Object.values(G.extra), ...Object.values(G.sub)].flatMap(r => r.m.map(x => x[0])))];
  G.nways = all.length; G.status = 'ways';
  for (let i = 0; i < all.length; i += 1000) {
    const j = await run(`[out:json][timeout:300];way(id:${all.slice(i, i + 1000).join(',')})(34,-180,72,50);out geom;`);
    for (const w of (j ? j.elements : [])) G.ways[w.id] = dp(w.geometry.filter(Boolean).map(p => [Math.round(p.lon * 1e4) / 1e4, Math.round(p.lat * 1e4) / 1e4]), 0.002);
    G.done = i + 1000;
  }
  G.out = JSON.stringify({ meta: { fetched: new Date().toISOString(), period: '995-1505' }, rels: G.rels, rels4: G.extra, sub: G.sub, subs: G.subs, ways: G.ways, cshapes: { type: 'FeatureCollection', features: [] }, naturalearth: {}, deepstate: {} });
  G.status = 'done';
})();
