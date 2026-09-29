#!/usr/bin/env node
// Checks OpenHistoricalMap's country borders for Europe, 1800–1900, against known facts.
//
//   node scripts/ohm_checks.mjs records  – every country record, with date gaps and overlaps flagged
//   node scripts/ohm_checks.mjs spot     – data/spot-checks.csv: who held each place on each date
//   node scripts/ohm_checks.mjs audit    – data/cow-audit-events.csv: when OHM moves each place
//                                          from the losing to the gaining state, vs. COW's date
//
// Results go to out/. Needs Node 18+ and internet access; no packages to install.
// "Level 2" records are countries; "level 3" are vassal or self-governing states under them.
import { readCsv, writeCsv, loadPlaces, overpass, relationContains, activeOn, sleep } from './lib.mjs';

const EUROPE_BBOX = '(34,-25,72,45)';

async function records() {
  const j = await overpass(`[out:json][timeout:180];
relation["boundary"="administrative"]["admin_level"="2"]${EUROPE_BBOX}
  (if: t["start_date"] < "1901" && (t["end_date"] >= "1800" || !is_tag("end_date")));
out tags;`);
  const rows = j.elements.map((e) => ({
    id: e.id, name: e.tags['name:en'] || e.tags.name, name_local: e.tags.name,
    start: e.tags.start_date || '', end: e.tags.end_date || '',
    wikidata: e.tags.wikidata || '', source: e.tags.source || '',
  }));
  // Gaps and overlaps between consecutive records with the same English name.
  const byName = {};
  rows.forEach((r) => (byName[r.name] = byName[r.name] || []).push(r));
  const issues = [];
  for (const [name, list] of Object.entries(byName)) {
    list.sort((a, b) => a.start.localeCompare(b.start));
    for (let i = 1; i < list.length; i++) {
      const prevEnd = (list[i - 1].end || '9999').slice(0, 10), next = list[i].start.slice(0, 10);
      if (prevEnd < next && prevEnd >= '1800' && next <= '1900-12-31') issues.push({ name, kind: 'gap', from: prevEnd, to: next });
      if (prevEnd > next) issues.push({ name, kind: 'overlap', from: next, to: prevEnd });
    }
  }
  rows.filter((r) => r.end && r.start > r.end).forEach((r) => issues.push({ name: r.name, kind: 'start after end', from: r.start, to: r.end }));
  console.log(`${rows.length} country records; ${rows.filter((r) => r.wikidata).length} link to Wikidata; ${rows.filter((r) => r.source).length} cite a source`);
  console.log(`${issues.length} date issues (one-day gaps usually mean inconsistent end-date conventions)`);
  console.log('Wrote', writeCsv('out/ohm-country-records.csv', rows));
  console.log('Wrote', writeCsv('out/ohm-date-issues.csv', issues));
}

// Every level-2/3 record containing each place, across all dates.
// OHM's lookup index lags recent edits, so records missing from it are tested directly.
async function holdersByPlace(places) {
  const names = Object.keys(places);
  const found = Object.fromEntries(names.map((n) => [n, new Set()]));
  for (const n of names) {
    const [lat, lon] = places[n];
    const j = await overpass(`[out:json][timeout:60];is_in(${lat},${lon})->.a;area.a["boundary"="administrative"]["admin_level"~"^[23]$"];out ids;`);
    j.elements.forEach((e) => found[n].add(e.id - 3600000000));
    await sleep(500);
  }
  const cands = (await overpass(`[out:json][timeout:180];relation["boundary"="administrative"]["admin_level"~"^[23]$"]${EUROPE_BBOX}
  (if: t["start_date"] < "1911" && (t["end_date"] >= "1795" || !is_tag("end_date")));out tags bb;`)).elements;
  const indexed = new Set();
  for (let i = 0; i < cands.length; i += 300) {
    const ids = cands.slice(i, i + 300).map((c) => c.id + 3600000000).join(',');
    (await overpass(`[out:json][timeout:120];area(id:${ids});out ids;`)).elements.forEach((a) => indexed.add(a.id - 3600000000));
  }
  const unindexed = cands.filter((c) => !indexed.has(c.id));
  console.log(`${unindexed.length} records missing from OHM's lookup index; testing them directly`);
  for (const c of unindexed) {
    const inBox = names.filter((n) => { const [lat, lon] = places[n]; const b = c.bounds; return b && lat >= b.minlat && lat <= b.maxlat && lon >= b.minlon && lon <= b.maxlon; });
    if (!inBox.length) continue;
    const geom = (await overpass(`[out:json][timeout:180];rel(${c.id});out geom;`)).elements[0];
    if (geom) inBox.forEach((n) => { if (relationContains(geom, ...places[n])) found[n].add(c.id); });
  }
  const allIds = [...new Set(names.flatMap((n) => [...found[n]]))];
  const tags = {};
  for (let i = 0; i < allIds.length; i += 300) {
    (await overpass(`[out:json][timeout:120];rel(id:${allIds.slice(i, i + 300).join(',')});out tags;`)).elements.forEach((e) => (tags[e.id] = e.tags));
  }
  const out = {};
  for (const n of names) {
    out[n] = [...found[n]].filter((id) => tags[id] && ['2', '3'].includes(tags[id].admin_level)).map((id) => ({
      id, name: tags[id]['name:en'] || tags[id].name, level: tags[id].admin_level, start: tags[id].start_date || '', end: tags[id].end_date || '',
    }));
  }
  return out;
}

async function spot() {
  const allPlaces = loadPlaces();
  const tests = readCsv('data/spot-checks.csv');
  const places = Object.fromEntries([...new Set(tests.map((t) => t.place))].map((p) => [p, allPlaces[p]]));
  const holders = await holdersByPlace(places);
  const rows = tests.map((t) => {
    const rx = new RegExp(t.expected_holder, 'i');
    const hits = holders[t.place].filter((r) => activeOn(r, t.date));
    const l2 = hits.filter((h) => h.level === '2'), l3 = hits.filter((h) => h.level === '3');
    const result = l2.some((h) => rx.test(h.name)) ? 'right' : l3.some((h) => rx.test(h.name)) ? 'right (vassal level)' : hits.length ? 'wrong' : 'nothing there';
    return { place: t.place, date: t.date, expected: t.expected_holder, result, ohm_shows: hits.map((h) => `${h.name} (L${h.level})`).join('; ') };
  });
  const tally = {};
  rows.forEach((r) => (tally[r.result] = (tally[r.result] || 0) + 1));
  console.log(tally);
  console.log('Wrote', writeCsv('out/ohm-spot-checks.csv', rows));
}

// Month-by-month: find the first month after which the place sits only in the gaining state for a year.
async function audit() {
  const allPlaces = loadPlaces();
  const events = readCsv('data/cow-audit-events.csv');
  const needed = [...new Set(events.flatMap((e) => e.test_places.split(';')))];
  const holders = await holdersByPlace(Object.fromEntries(needed.map((p) => [p, allPlaces[p]])));
  const ym = (i) => `${Math.floor(i / 12)}-${String((i % 12) + 1).padStart(2, '0')}`;
  const rows = [];
  for (const e of events) {
    const [cy, cm] = e.cow_date.split('-').map(Number);
    const cowIdx = cy * 12 + (cm ? cm - 1 : 6);
    const L = new RegExp(e.loser_pattern, 'i'), G = new RegExp(e.gainer_pattern, 'i');
    for (const place of e.test_places.split(';')) {
      const recs = holders[place], status = [], label = [];
      for (let i = cowIdx - 144; i <= cowIdx + 144; i++) {
        const act = recs.filter((r) => activeOn(r, ym(i) + '-15'));
        const inL = act.some((r) => L.test(r.name)), inG = act.some((r) => G.test(r.name));
        status.push(inG && !inL ? 'G' : inL && !inG ? 'L' : inG && inL ? 'B' : act.length ? 'O' : 'N');
        label.push(act.map((r) => r.name + (r.level === '3' ? ' (vassal level)' : '')).sort().join(' + ') || 'no country');
      }
      const timeline = [];
      label.forEach((l, k) => { if (k === 0 || l !== label[k - 1]) { const m = cowIdx - 144 + k; if (Math.abs(m - cowIdx) <= 72) timeline.push(`${ym(m)} ${l}`); } });
      let lastLoser = -1;
      status.forEach((s, k) => { if (s === 'L' || s === 'B') lastLoser = k; });
      let result, ohmDate = '', diff = '';
      if (lastLoser < 0) result = status.every((s) => s === 'G') ? 'gainer throughout' : status.includes('G') ? 'loser never shown' : 'neither shown';
      else {
        let t = -1;
        for (let k = lastLoser + 1; k < status.length - 11; k++) if (status.slice(k, k + 12).every((s) => s === 'G')) { t = k; break; }
        if (t < 0) result = 'no handover to gainer';
        else {
          const m = cowIdx - 144 + t;
          ohmDate = ym(m); diff = m - cowIdx;
          result = (cm ? Math.abs(diff) <= 2 : Math.floor(m / 12) === cy) ? 'agrees' : Math.abs(diff) <= 12 ? 'within a year' : 'differs';
        }
      }
      rows.push({ cow_number: e.cow_number, transfer: e.transfer, place, cow_date: e.cow_date, ohm_date: ohmDate, difference_months: diff, result, ohm_shows: timeline.join(' → ') });
    }
  }
  const tally = {};
  rows.forEach((r) => (tally[r.result] = (tally[r.result] || 0) + 1));
  console.log(tally);
  console.log('Wrote', writeCsv('out/ohm-cow-audit.csv', rows));
}

const cmd = process.argv[2];
const commands = { records, spot, audit };
if (!commands[cmd]) {
  console.log('Usage: node scripts/ohm_checks.mjs records|spot|audit');
  process.exit(1);
}
await commands[cmd]();
