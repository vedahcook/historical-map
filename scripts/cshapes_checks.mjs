#!/usr/bin/env node
// Runs data/spot-checks.csv against CShapes-Europe (ETH Zurich; yearly, from 1816).
//   node scripts/cshapes_checks.mjs
// Downloads the GeoJSON (~5 MB) each run. CShapes coastlines are simplified, so a coastal
// city can fall just outside every polygon; for those the nearest polygon within ~22 km is
// reported and marked as such. Results go to out/cshapes-spot-checks.csv.
import { readCsv, writeCsv, loadPlaces, geojsonContains } from './lib.mjs';

const URL = 'https://icr.ethz.ch/data/cshapes/CShapes-Europe.geojson';
// CShapes names some states differently from OHM.
const alias = (p) => p
  .replace('Sardinia', 'Sardinia|Piedmont')
  .replace('Two Sicilies', 'Two Sicilies|Naples')
  .replace(/Prussia/g, 'Prussia|^Germany')
  .replace('Ottoman', 'Ottoman|Turkey')
  .replace('Romania', 'Romania|Rumania');

const features = (await (await fetch(URL)).json()).features;
const places = loadPlaces();
const rows = [];
for (const t of readCsv('data/spot-checks.csv')) {
  const year = Number(t.date.slice(0, 4));
  if (year < 1816) { rows.push({ place: t.place, date: t.date, expected: t.expected_holder, result: 'before 1816 (not covered)', cshapes_shows: '' }); continue; }
  const [lat, lon] = places[t.place];
  const active = features.filter((f) => f.properties.From <= year && f.properties.To >= year);
  let hits = active.filter((f) => geojsonContains(f.geometry, lon, lat)).map((f) => f.properties.Name);
  let note = '';
  if (!hits.length) {
    search: for (const d of [0.02, 0.05, 0.1, 0.2]) {
      for (let a = 0; a < 16; a++) {
        const la = lat + d * Math.sin((a * Math.PI) / 8), lo = lon + (d * Math.cos((a * Math.PI) / 8)) / Math.cos((lat * Math.PI) / 180);
        const h = active.filter((f) => geojsonContains(f.geometry, lo, la)).map((f) => f.properties.Name);
        if (h.length) { hits = h; note = ` (nearest, ~${Math.round(d * 111)} km off)`; break search; }
      }
    }
  }
  const rx = new RegExp(alias(t.expected_holder), 'i');
  const result = hits.some((h) => rx.test(h)) ? 'right' : hits.length ? 'wrong' : 'nothing there';
  rows.push({ place: t.place, date: t.date, expected: t.expected_holder, result, cshapes_shows: hits.join('; ') + note });
}
const tally = {};
rows.forEach((r) => (tally[r.result] = (tally[r.result] || 0) + 1));
console.log(tally);
console.log('Wrote', writeCsv('out/cshapes-spot-checks.csv', rows));
