// Gather what happened in each city of the Europe map, and who was born or died there, from Wikidata.
// Run in the browser on an ordinary Wikidata page (https://www.wikidata.org/wiki/Q1741: its content security policy
// lets a script read GitHub and the query service; query.wikidata.org's own page does not allow GitHub). Load with
//   const SRC = 'https://raw.githubusercontent.com/vedahcook/historical-map/<branch>/';
//   (0, eval)(await (await fetch(SRC + 'fetch_city_extras.js')).text());
// then HM.run('cities'), HM.run('events'), HM.run('classes'), HM.run('roots') (with HM.ROOTS set), HM.run('people'),
// HM.run('battles'), HM.run('details') (with HM.want set); poll HM.status.
// Each step keeps its result in HM (HM.qid, HM.ev, HM.cls, HM.pp, HM.lab). HM.dump(name) gives a step's result as text.
// Input: cities_in.json (written by cities/extras_input.py): [index, name, lon, lat, Wikidata id or null] per city.
(() => {
  const HM = window.HM = window.HM || { status: 'idle', log: [], errors: [] };
  const SRC = HM.SRC || 'https://raw.githubusercontent.com/vedahcook/historical-map/towns-scratch/';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const note = s => { HM.log.push(new Date().toISOString().slice(11, 19) + ' ' + s); if (HM.log.length > 400) HM.log.shift(); };
  const QS = 'https://query.wikidata.org/sparql?format=json&query=';
  // a SPARQL query, retried; null after a timeout or repeated failure (the caller splits the batch)
  async function sparql(q, tries = 3) {
    for (let t = 0; t < tries; t++) {
      try {
        const r = await fetch(QS + encodeURIComponent(q), { headers: { Accept: 'application/sparql-results+json' } });
        if (r.ok) return (await r.json()).results.bindings;
        if (r.status === 500 || r.status === 400) { HM.errors.push('sparql ' + r.status); return null; }   // timeout or bad query
        await sleep(r.status === 429 ? 30000 : 4000 * (t + 1));
      } catch (e) { HM.errors.push(String(e)); await sleep(4000 * (t + 1)); }
    }
    return null;
  }
  async function api(params) {
    for (let t = 0; t < 4; t++) {
      try { const r = await fetch('https://www.wikidata.org/w/api.php?format=json&origin=*&' + new URLSearchParams(params)); if (r.ok) return await r.json(); }
      catch (e) { HM.errors.push(String(e)); }
      await sleep(3000 * (t + 1));
    }
    return null;
  }
  const id = u => u.replace('http://www.wikidata.org/entity/', '');
  const V = qs => qs.map(q => 'wd:' + q).join(' ');
  const km = (a, b, c, d) => { const R = 6371, r = Math.PI / 180, x = (c - a) * r * Math.cos((b + d) / 2 * r), y = (d - b) * r; return R * Math.hypot(x, y); };
  const pt = s => { const m = /Point\(([-\d.]+) ([-\d.]+)\)/.exec(s || ''); return m ? [+m[1], +m[2]] : null; };
  // run a query over items in batches; a batch that times out is split in half, down to one item
  async function batched(items, size, make, onRows, label) {
    const queue = []; for (let i = 0; i < items.length; i += size) queue.push(items.slice(i, i + size));
    let done = 0;
    while (queue.length) {
      const b = queue.shift(); const rows = await sparql(make(b));
      if (rows) { onRows(rows, b); done += b.length; HM.status = `${label}: ${done} of ${items.length}`; }
      else if (b.length > 1) { queue.unshift(b.slice(0, b.length >> 1), b.slice(b.length >> 1)); }
      else { HM.errors.push(label + ' failed for ' + b[0]); onRows(null, b); done++; }
      await sleep(300);
    }
  }

  const steps = {};
  // 1. each city's Wikidata item: the id we have, checked against the city's position (within 30 km), or found by
  // searching its names near its position
  steps.cities = async () => {
    const C = HM.cities = await (await fetch(SRC + 'cities_in.json')).json();
    const qid = HM.qid = C.map(c => c[4]);
    const known = [...new Set(qid.filter(Boolean))], at = {};
    await batched(known, 300, b => `SELECT ?c ?p WHERE { VALUES ?c { ${V(b)} } ?c wdt:P625 ?p }`, rows => { for (const r of rows || []) at[id(r.c.value)] = at[id(r.c.value)] || pt(r.p.value); }, 'checking');
    const todo = C.filter(c => !c[4] || !at[c[4]] || km(c[2], c[3], ...at[c[4]]) > 30).map(c => c[0]);
    note('to search: ' + todo.length);
    let n = 0;
    for (const i of todo) {
      const [, name, lon, lat] = C[i];
      const names = [...new Set([name, name.replace(/\s*\(.*\)$/, ''), (/\(([^)]+)\)/.exec(name) || [])[1], name.replace(/,.*$/, '')].filter(Boolean))];
      const cands = new Set();
      for (const s of names) for (const lang of ['en', 'de']) {
        const j = await api({ action: 'wbsearchentities', search: s, language: lang, type: 'item', limit: 12 });
        (j && j.search || []).forEach(x => cands.add(x.id));
      }
      let best = null;
      if (cands.size) {
        const rows = await sparql(`SELECT ?c ?p WHERE { VALUES ?c { ${V([...cands])} } ?c wdt:P625 ?p }`) || [];
        for (const r of rows) { const p = pt(r.p.value); if (!p) continue; const d = km(lon, lat, ...p); if (d < 25 && (!best || d < best[1])) best = [id(r.c.value), d]; }
      }
      qid[i] = best ? best[0] : null; n++;
      HM.status = `searching: ${n} of ${todo.length}`;
    }
    HM.status = 'cities done'; note('cities without an item: ' + qid.filter(q => !q).length);
  };

  // 2. events located in each city (P276 location, P131 in the city, or P276 a place in the city), dated (P585 point in
  // time, else P580 start) from 1000 on, with at least 3 Wikipedia articles. Kept: item, date and precision, end year,
  // number of articles, classes (P31).
  steps.events = async () => {
    const cities = HM.only || [...new Set(HM.qid.filter(Boolean))]; const ev = HM.ev = HM.ev || {};   // HM.only: just these cities, added to what is there
    const make = (b, hop) => `SELECT ?city ?e ?d ?pr ?d2 ?pr2 ?end ?sl (GROUP_CONCAT(DISTINCT ?c; separator=" ") AS ?cls) WHERE {
      VALUES ?city { ${V(b)} }
      { ?e wdt:P276 ?city } UNION { ?e wdt:P131 ?city } ${hop ? 'UNION { ?e wdt:P276 ?l . ?l wdt:P131 ?city }' : ''}
      ?e wikibase:sitelinks ?sl . FILTER(?sl >= 3)
      OPTIONAL { ?e p:P585/psv:P585 [ wikibase:timeValue ?d ; wikibase:timePrecision ?pr ] }
      OPTIONAL { ?e p:P580/psv:P580 [ wikibase:timeValue ?d2 ; wikibase:timePrecision ?pr2 ] }
      OPTIONAL { ?e wdt:P582 ?end }
      FILTER(BOUND(?d) || BOUND(?d2))
      OPTIONAL { ?e wdt:P31 ?c }
    } GROUP BY ?city ?e ?d ?pr ?d2 ?pr2 ?end ?sl`;
    const add = rows => {
      for (const r of rows || []) {
        const e = id(r.e.value), c = id(r.city.value), d = r.d || r.d2, pr = r.pr || r.pr2;
        const y = parseInt(d.value, 10); if (!(y >= 1000 && y <= 2026)) continue;     // the map's years ('-0410-...' parses negative)
        const x = ev[e] = ev[e] || { c: [], t: d.value.slice(0, 10), p: +pr.value, sl: +r.sl.value, cls: r.cls.value.split(' ').filter(Boolean).map(id), end: r.end ? parseInt(r.end.value, 10) : null };
        if (!x.c.includes(c)) x.c.push(c);
      }
    };
    HM.retry = [];
    await batched(cities, 40, b => make(b, true), (rows, b) => { if (rows) add(rows); else HM.retry = HM.retry.concat(b); }, 'events');
    // a city whose query timed out with the extra hop: once more without it
    for (const c of HM.retry || []) add(await sparql(make([c], false)));
    HM.status = 'events done'; note('events: ' + Object.keys(ev).length);
  };

  // 3. the classes of those events, with labels and how many events of each, for choosing which kinds to keep
  steps.classes = async () => {
    const n = {}; for (const e of Object.values(HM.ev)) for (const c of e.cls) n[c] = (n[c] || 0) + 1;
    const cs = Object.keys(n); const lab = HM.clsLab = HM.clsLab || {};
    await batched(cs, 300, b => `SELECT ?c ?l WHERE { VALUES ?c { ${V(b)} } ?c rdfs:label ?l FILTER(LANG(?l) = "en") }`, rows => { for (const r of rows || []) lab[id(r.c.value)] = r.l.value; }, 'class labels');
    HM.clsN = n; HM.status = 'classes done';
  };
  // which of the classes descend (P279*) from each of the given root classes
  steps.roots = async () => {
    const cs = Object.keys(HM.clsN), R = HM.ROOTS, under = HM.under = {};
    await batched(cs, 150, b => `SELECT ?c ?r WHERE { VALUES ?c { ${V(b)} } VALUES ?r { ${V(R)} } ?c wdt:P279* ?r }`, rows => { for (const r of rows || []) (under[id(r.c.value)] = under[id(r.c.value)] || []).push(id(r.r.value)); }, 'roots');
    HM.status = 'roots done';
  };

  // 4. people born (P19) or died (P20) in each city, or in a place in it (P131): everyone with at least 30 Wikipedia
  // articles; then, for places with fewer than 8 such people, everyone with at least 10, in the place itself and then
  // in places within it
  steps.people = async () => {
    const all = HM.only || [...new Set(HM.qid.filter(Boolean))]; const pp = HM.pp = HM.pp || {};
    // one query for births and one for deaths (a UNION of the two is far slower on the query service)
    const make = (b, min, hop, prop) => `SELECT ?city ?p ?sl ?b ?d WHERE {
      VALUES ?city { ${V(b)} }
      ${hop ? `?p wdt:${prop} ?l . ?l wdt:P131 ?city .` : `?p wdt:${prop} ?city .`}
      ?p wikibase:sitelinks ?sl . FILTER(?sl >= ${min})
      OPTIONAL { ?p wdt:P569 ?b } OPTIONAL { ?p wdt:P570 ?d }
    }`;
    const n = {};
    const add = (rows, k) => {
      for (const r of rows || []) {
        const p = id(r.p.value), c = id(r.city.value), b = r.b ? parseInt(r.b.value, 10) : null, d = r.d ? parseInt(r.d.value, 10) : null;
        const x = pp[p] = pp[p] || { sl: +r.sl.value, b, d, at: {} };
        if (b != null && (x.b == null || b < x.b)) x.b = b; if (d != null && (x.d == null || d > x.d)) x.d = d;
        if (!(x.at[c] || '').includes(k)) { x.at[c] = (x.at[c] || '') + k; n[c] = (n[c] || 0) + 1; }
      }
    };
    // passes: 30+ articles in the city itself (the largest cities have thousands of people born there); then, for
    // places with fewer than 8 people so far, 10+ in the place itself, then 10+ in places within it
    for (const [min, size, pick, hop] of [[30, 60, all, false], [10, 60, null, false], [10, 40, null, true]]) {
      const list = pick || all.filter(c => (n[c] || 0) < 8);
      for (const [prop, k] of [['P19', 'b'], ['P20', 'd']]) {
        HM.retry = [];
        await batched(list, size, b => make(b, min, hop, prop), (rows, b) => { if (rows) add(rows, k); else HM.retry = HM.retry.concat(b); }, `people (${k}, ${min}+${hop ? ', within' : ''})`);
      }
    }
    // people who lived before the map begins
    for (const [p, x] of Object.entries(pp)) if ((x.d != null && x.d < 1000) || (x.d == null && x.b != null && x.b < 950)) delete pp[p];
    HM.status = 'people done'; note('people: ' + Object.keys(pp).length);
  };

  // battles and sieges anywhere on the map (P625 position), dated from 1000 on, with at least 8 Wikipedia articles: for a
  // later layer of events outside cities
  steps.battles = async () => {
    const out = HM.bt = {};
    for (const root of ['Q178561', 'Q188055']) {
      const rows = await sparql(`SELECT ?e ?p ?d ?pr ?d2 ?pr2 ?sl WHERE {
        ?c wdt:P279* wd:${root} . ?e wdt:P31 ?c . ?e wdt:P625 ?p . ?e wikibase:sitelinks ?sl . FILTER(?sl >= 8)
        OPTIONAL { ?e p:P585/psv:P585 [ wikibase:timeValue ?d ; wikibase:timePrecision ?pr ] }
        OPTIONAL { ?e p:P580/psv:P580 [ wikibase:timeValue ?d2 ; wikibase:timePrecision ?pr2 ] }
      }`, 2) || [];
      for (const r of rows) {
        const d = r.d || r.d2, pr = r.pr || r.pr2; if (!d) continue; const y = parseInt(d.value, 10); if (!(y >= 1000 && y <= 2026)) continue;
        const q = pt(r.p.value); if (!q || q[0] < -26 || q[0] > 50 || q[1] < 34 || q[1] > 72) continue;
        out[id(r.e.value)] = { t: d.value.slice(0, 10), p: +pr.value, sl: +r.sl.value, x: q, k: root === 'Q178561' ? 'b' : 's' };
      }
      HM.status = 'battles: ' + Object.keys(out).length;
    }
    HM.status = 'battles done';
  };

  // 5. labels, short descriptions and English Wikipedia titles for the items chosen (HM.want), 50 at a time
  steps.details = async () => {
    const want = HM.want, lab = HM.lab = HM.lab || {}; let n = 0;
    for (let i = 0; i < want.length; i += 50) {
      const ids = want.slice(i, i + 50).filter(q => !lab[q]); if (!ids.length) continue;
      const j = await api({ action: 'wbgetentities', ids: ids.join('|'), props: 'labels|descriptions|sitelinks', languages: 'en|de|fr|it|es|ru|pl', languagefallback: 1, sitefilter: 'enwiki' });
      for (const [q, e] of Object.entries((j && j.entities) || {})) {
        const L = e.labels || {}, D = e.descriptions || {};
        const l = (L.en || L.de || L.fr || L.it || L.es || L.pl || L.ru || Object.values(L)[0] || {}).value || q;
        lab[q] = [l, (D.en || {}).value || '', ((e.sitelinks || {}).enwiki || {}).title || ''];
      }
      n += ids.length; HM.status = `details: ${Math.min(i + 50, want.length)} of ${want.length}`;
      await sleep(150);
    }
    HM.status = 'details done';
  };

  HM.run = name => { HM.status = name + ': starting'; steps[name]().catch(e => { HM.status = name + ' failed: ' + e; HM.errors.push(String(e && e.stack || e)); }); return HM.status; };
  // a step's result as text. Short results are padded, so the tool that reads them saves them to a file
  HM.dump = (obj, pad = 150000) => { const s = 'HMDATA ' + JSON.stringify(obj); return s.length < pad ? s + ' '.repeat(pad - s.length) : s; };
  // a large result in pieces small enough for the browser tool (it cuts results at about 260,000 characters):
  // HM.prep(obj) gives the number of pieces, HM.part(i) each piece (joined again by join.py)
  HM.prep = obj => { HM._s = JSON.stringify(obj); return Math.ceil(HM._s.length / 230000); };
  HM.part = i => { const s = 'HMPART ' + i + ' ' + HM._s.slice(i * 230000, (i + 1) * 230000); return s.length < 150000 ? s + ' '.repeat(150000 - s.length) : s; };
})();
