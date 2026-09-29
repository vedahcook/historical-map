// Shared helpers for the check scripts (Node 18+, no dependencies).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
export const OVERPASS_URL = 'https://overpass-api.openhistoricalmap.org/api/interpreter';
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Minimal CSV reader/writer (quoted fields, commas and newlines inside quotes).
export function readCsv(relPath) {
  const text = readFileSync(join(ROOT, relPath), 'utf8');
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = '';
      if (row.some((v) => v !== '')) rows.push(row);
      row = [];
    } else field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  const [header, ...body] = rows;
  return body.map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ''])));
}

export function writeCsv(relPath, rows) {
  const full = join(ROOT, relPath);
  mkdirSync(dirname(full), { recursive: true });
  const cols = Object.keys(rows[0] || {});
  const esc = (v) => { const s = String(v ?? ''); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  writeFileSync(full, [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n') + '\n');
  return full;
}

export function loadPlaces() {
  const places = {};
  for (const r of readCsv('data/places.csv')) places[r.place] = [Number(r.lat), Number(r.lon)];
  return places;
}

// POST a query to OpenHistoricalMap's Overpass server, retrying on busy/timeout responses.
export async function overpass(query, tries = 4) {
  for (let t = 0; t < tries; t++) {
    const res = await fetch(OVERPASS_URL, {
      method: 'POST',
      body: 'data=' + encodeURIComponent(query),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'historical-map-checks (github.com/vedahcook/historical-map)' },
    });
    if (res.ok) return res.json();
    await sleep(5000 * (t + 1));
  }
  throw new Error('Overpass query failed after retries: ' + query.slice(0, 120));
}

// Is (lat, lon) inside a relation fetched with `out geom`? Ray casting over every member way,
// which works whether or not the rings are split across several ways.
export function relationContains(rel, lat, lon) {
  let crossings = 0;
  for (const m of rel.members || []) {
    if (m.type !== 'way' || !m.geometry) continue;
    const g = m.geometry;
    for (let i = 1; i < g.length; i++) {
      const a = g[i - 1], b = g[i];
      if ((a.lat > lat) !== (b.lat > lat)) {
        const x = a.lon + ((lat - a.lat) * (b.lon - a.lon)) / (b.lat - a.lat);
        if (x > lon) crossings++;
      }
    }
  }
  return crossings % 2 === 1;
}

// Plain polygon test for GeoJSON features (used for CShapes).
export function geojsonContains(geometry, lon, lat) {
  const inRing = (r) => {
    let c = false;
    for (let i = 0, j = r.length - 1; i < r.length; j = i++) {
      const [xi, yi] = r[i], [xj, yj] = r[j];
      if ((yi > lat) !== (yj > lat) && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) c = !c;
    }
    return c;
  };
  const polys = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
  return polys.some((p) => inRing(p[0]) && !p.slice(1).some(inRing));
}

// A record is active on `date` (YYYY-MM-DD) if start <= date < end. Plain string comparison
// works for OHM dates; a year-only date such as "1864" sorts as January 1 of that year.
export const activeOn = (r, date) => r.start && r.start <= date && (!r.end || r.end > date);
