// Who OpenHistoricalMap says held each town (all dates). Produces the data in ohm_towns.json.
// Run in a browser console on https://overpass-api.openhistoricalmap.org/api/status
// (same site as the data server). First paste the contents of towns.json as: window.__T = [...];
// Then poll window.__B.status until it reads 'done' and copy window.__B.
//
// Records missing from OHM's lookup index are tested directly. Very large ones (the Russian
// Empire) can time out; for those, fetch geometry clipped to the region with
// `out geom(34,5,49,40)` and cast the ray WEST, so only boundary pieces inside the clip matter.
window.__B = { done: 0, found: {}, status: 'running' };
(async () => {
  const run = async q => { for (let t = 0; t < 5; t++) { try { const r = await fetch('/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }); if (r.ok) return r.json(); } catch (e) {} await new Promise(s => setTimeout(s, 5000 * (t + 1))); } return { elements: null }; };
  const pip = (rel, lat, lon) => { let c = 0; for (const m of rel.members || []) { if (m.type !== 'way' || !m.geometry) continue; const g = m.geometry; for (let i = 1; i < g.length; i++) { const a = g[i - 1], b = g[i]; if (!a || !b) continue; if ((a.lat > lat) !== (b.lat > lat)) { const x = a.lon + (lat - a.lat) * (b.lon - a.lon) / (b.lat - a.lat); if (x > lon) c++; } } } return c % 2 === 1; };
  const B = window.__B;
  for (const [n, lat, lon] of window.__T) {
    const j = await run(`[out:json][timeout:60];is_in(${lat},${lon})->.a;area.a["boundary"="administrative"]["admin_level"~"^[234]$"];out ids;`);
    B.found[n] = new Set((j.elements || []).map(e => e.id - 3600000000));
    B.done++;
  }
  B.status = 'unindexed';
  const cands = (await run(`[out:json][timeout:180];relation["boundary"="administrative"]["admin_level"~"^[234]$"](34,13,49,31)(if: t["start_date"] < "1906" && (t["end_date"] >= "1805" || !is_tag("end_date")));out tags bb;`)).elements;
  const indexed = new Set();
  for (let i = 0; i < cands.length; i += 300) { const a = await run(`[out:json][timeout:120];area(id:${cands.slice(i, i + 300).map(c => c.id + 3600000000).join(',')});out ids;`); (a.elements || []).forEach(x => indexed.add(x.id - 3600000000)); }
  B.unindexed = cands.filter(c => !indexed.has(c.id)).map(c => c.id);
  for (const c of cands.filter(c => !indexed.has(c.id))) {
    const inBox = window.__T.filter(([n, lat, lon]) => c.bounds && lat >= c.bounds.minlat && lat <= c.bounds.maxlat && lon >= c.bounds.minlon && lon <= c.bounds.maxlon);
    if (!inBox.length) continue;
    const g = ((await run(`[out:json][timeout:180];rel(${c.id});out geom;`)).elements || [])[0];
    if (g) inBox.forEach(([n, lat, lon]) => { if (pip(g, lat, lon)) B.found[n].add(c.id); });
    else (B.failed = B.failed || []).push(c.id);   // retry these with the clipped, west-ray method
  }
  B.status = 'tags';
  const ids = [...new Set(Object.values(B.found).flatMap(s => [...s]))];
  B.tags = {};
  for (let i = 0; i < ids.length; i += 300) { const t = await run(`[out:json][timeout:120];rel(id:${ids.slice(i, i + 300).join(',')});out tags;`); (t.elements || []).forEach(e => B.tags[e.id] = e.tags); }
  B.status = 'done';
})();
