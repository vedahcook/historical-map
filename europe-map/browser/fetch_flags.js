// Fetch the flags for the map's states: article -> Wikidata item -> flag images (P41, with their start and end
// dates) -> a small PNG of each from Wikimedia Commons, with its license and author.
// Run in a browser console on any page (the APIs allow cross-origin reads), with ARTICLES set to the contents of
// flags_articles.json (from flags/flags_plan.py). Poll window.__FL.status until 'done', then read window.__FL.gz
// (gzip + base64 of {claims, files}) in slices and save it as flags_claims.json and flags_files.json.
window.__FL = { status: 'items', claims: {}, files: {}, errors: [] };
(async () => {
  const G = window.__FL;
  const get = async u => { for (let t = 0; t < 4; t++) { try { const r = await fetch(u); if (r.ok) return await r.json(); } catch (e) { G.errors.push(String(e)); } await new Promise(s => setTimeout(s, 2000 * (t + 1))); } return null; };
  // 1. article -> Wikidata item
  const q = {};
  for (let i = 0; i < ARTICLES.length; i += 50) {
    const j = await get('https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&format=json&origin=*&titles=' + encodeURIComponent(ARTICLES.slice(i, i + 50).join('|')));
    if (!j) continue;
    const back = {}; for (const r of [...(j.query.redirects || []), ...(j.query.normalized || [])]) back[r.to] = r.from;
    for (const p of Object.values(j.query.pages)) { let t = p.title; while (back[t]) t = back[t]; if (p.pageprops && p.pageprops.wikibase_item) q[t] = p.pageprops.wikibase_item; }
  }
  // 2. item -> flags (P41), with start (P580) and end (P582) years
  G.status = 'claims';
  const ids = [...new Set(Object.values(q))], year = v => v && v[0].datavalue ? +v[0].datavalue.value.time.slice(1, 5) * (v[0].datavalue.value.time[0] === '-' ? -1 : 1) : null;
  const flagsOf = {};
  for (let i = 0; i < ids.length; i += 50) {
    const j = await get('https://www.wikidata.org/w/api.php?action=wbgetentities&props=claims&format=json&origin=*&ids=' + ids.slice(i, i + 50).join('|'));
    if (!j) continue;
    for (const [id, e] of Object.entries(j.entities)) flagsOf[id] = ((e.claims || {}).P41 || []).filter(c => c.mainsnak.datavalue && c.rank !== 'deprecated')
      .map(c => ({ f: c.mainsnak.datavalue.value, s: year((c.qualifiers || {}).P580), e: year((c.qualifiers || {}).P582), r: c.rank }));
  }
  for (const [a, id] of Object.entries(q)) G.claims[a] = { q: id, flags: flagsOf[id] || [] };
  // 3. each flag file -> a thumbnail (fits 120 x 60 px), its license and author
  G.status = 'files';
  const names = [...new Set(Object.values(G.claims).flatMap(c => c.flags.map(f => f.f)))];
  const strip = h => (h || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
  for (let i = 0; i < names.length; i += 50) {
    const j = await get('https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=120&iiurlheight=60&format=json&origin=*&titles=' + encodeURIComponent(names.slice(i, i + 50).map(n => 'File:' + n).join('|')));
    if (!j) continue;
    const back = {}; for (const r of (j.query.normalized || [])) back[r.to] = r.from;
    for (const p of Object.values(j.query.pages)) {
      const ii = (p.imageinfo || [])[0]; if (!ii) continue;
      const m = ii.extmetadata || {}, name = (back[p.title] || p.title).replace(/^File:/, '');
      G.files[name] = { thumb: ii.thumburl, url: ii.descriptionurl, lic: strip((m.LicenseShortName || {}).value), by: strip((m.Artist || {}).value).slice(0, 200) };
    }
  }
  // 4. the thumbnails themselves
  G.status = 'images'; G.done = 0;
  for (const [name, f] of Object.entries(G.files)) {
    try { const b = await fetch(f.thumb).then(r => r.blob()); f.png = await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(b); }); }
    catch (e) { G.errors.push(name + ': ' + e); }
    G.done++;
  }
  const s = new Blob([JSON.stringify({ claims: G.claims, files: G.files })]).stream().pipeThrough(new CompressionStream('gzip'));
  const buf = new Uint8Array(await new Response(s).arrayBuffer()); let bin = ''; for (let i = 0; i < buf.length; i += 32768) bin += String.fromCharCode(...buf.subarray(i, i + 32768));
  G.gz = btoa(bin); G.status = 'done';
})();
