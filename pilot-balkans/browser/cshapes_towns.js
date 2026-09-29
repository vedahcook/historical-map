// Who CShapes-Europe says held each town, per year 1816-1900. Produces cshapes_towns.json.
// Run in a browser console on https://icr.ethz.ch/data/cshapes/ after pasting towns.json as
// window.__T = [...]; then copy the printed JSON.
// Coastal towns that fall just outside CShapes' simplified coastline take the nearest shape
// within ~22 km, marked with "~<km>".
(async () => {
  const cs = await (await fetch('/data/cshapes/CShapes-Europe.geojson')).json();
  const inRing = (r, lon, lat) => { let c = false; for (let i = 0, j = r.length - 1; i < r.length; j = i++) { const [xi, yi] = r[i], [xj, yj] = r[j]; if (((yi > lat) !== (yj > lat)) && (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)) c = !c; } return c; };
  const inGeom = (g, lon, lat) => { const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates; return polys.some(p => inRing(p[0], lon, lat) && !p.slice(1).some(h => inRing(h, lon, lat))); };
  const F = cs.features.filter(f => f.properties.To >= 1815 && f.properties.From <= 1900);
  const keys = [], idx = {}, towns = {};
  for (const [n, lat, lon] of window.__T) {
    const runs = []; let prev = null;
    for (let y = 1816; y <= 1900; y++) {
      const act = F.filter(f => f.properties.From <= y && f.properties.To >= y);
      let hit = act.filter(f => inGeom(f.geometry, lon, lat)).map(f => f.properties.Name + '|' + f.properties.Status), near = 0;
      if (!hit.length) { outer: for (const d of [0.02, 0.05, 0.1, 0.2]) { for (let a = 0; a < 16; a++) { const la = lat + d * Math.sin(a * Math.PI / 8), lo = lon + d * Math.cos(a * Math.PI / 8) / Math.cos(lat * Math.PI / 180); const h = act.filter(f => inGeom(f.geometry, lo, la)); if (h.length) { hit = h.map(f => f.properties.Name + '|' + f.properties.Status); near = Math.round(d * 111); break outer; } } } }
      const key = hit.sort().join(';') + (near ? '~' + near : '');
      if (!(key in idx)) { idx[key] = keys.length; keys.push(key); }
      if (prev && prev[2] === idx[key]) prev[1] = y; else { prev = [y, y, idx[key]]; runs.push(prev); }
    }
    towns[n] = runs;
  }
  console.log(JSON.stringify({ keys, towns }));
})();
