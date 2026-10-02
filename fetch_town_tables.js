// Fetch population histories for the towns in cities/towns_input.json (written by cities/towns_select.py) from
// Wikipedia articles in several languages. Run in the browser console on any wikipedia.org page (the API allows
// cross-origin reads with origin=*), with INPUT_URL set to where towns_input.json can be fetched. Poll
// window.__TT.status until 'done'; the result is saved as hm-town-tables.json (Downloads):
//   { QID: [[source, [[year, population], ...]], ...] }   up to three candidate series per article
// cities/towns_merge.py checks each series against Wikidata and picks what to keep.
// What it reads, by language:
//   every article: wikitables (years down a column, or across a row with the figures in the next row) and
//     {{Historical populations}}-style templates (year|figure pairs)
//   fr: the commune's data page, Modèle:Données/<commune>/évolution population (INSEE and Cassini/EHESS series)
//   it: Template:Demografia/<comune> (ISTAT censuses from 1861)
//   es: {{Gráfica de evolución}} (INE censuses from 1842)
//   pl: <timeline> bar charts
//   ru: the {{Население}} table, expanded (it draws on ruwiki's own data pages)
(async () => {
  const G = window.__TT = { status: 'input', pages: 0, errors: [], out: {} };
  const SAVE = (name, text) => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); };
  const towns = await fetch(INPUT_URL).then(r => r.json());          // [[QID, {lang: title}], ...]
  const api = async (lang, params) => {
    for (let t = 0; t < 4; t++) {
      try { const r = await fetch(`https://${lang}.wikipedia.org/w/api.php?format=json&formatversion=2&origin=*&` + new URLSearchParams(params)); if (r.ok) return await r.json(); }
      catch (e) { G.errors.push(lang + ' ' + String(e)); }
      await new Promise(s => setTimeout(s, 3000 * (t + 1)));
    }
    return null;
  };
  const strip = s => s.replace(/<ref[^>]*\/>/g, '').replace(/<ref[^>]*>[\s\S]*?<\/ref>/g, '').replace(/<!--[\s\S]*?-->/g, '')
    .replace(/\{\{(?:FN|Fn|efn|sfn|Anm\.?|note|nota|Nota)[^{}]*\}\}/g, '')
    .replace(/\{\{formatnum:([^}|]*)[^}]*\}\}/gi, '$1').replace(/\{\{(?:0|nts|nowrap|Nts|Nowrap|NNS|Zahl|FormatZahl|nobr)\|([^}|]*)[^}]*\}\}/g, '$1')
    .replace(/\[\[[^\]|]*\|([^\]]*)\]\]/g, '$1').replace(/\[\[|\]\]/g, '')
    .replace(/&nbsp;|&#160;|&thinsp;|&#8201;|&#8239;|[   ]/g, ' ').replace(/'{2,}/g, '').replace(/<[^>]+>/g, ' ');
  // a year cell: short, with exactly one four-digit year in it ("1871", "1. Dez. 1834", "31.12.1990", "um 1500")
  const YR = s => {
    const t = strip(s).trim(); if (!t || t.length > 32) return null;
    const nums = t.match(/\d+/g) || []; const ys = nums.filter(n => n.length === 4 && +n >= 1000 && +n <= 2029);
    if (ys.length !== 1 || nums.some(n => n.length > 4)) return null;
    if (/\d[,\s]\d{3}(?!\d)/.test(t)) return null;                     // a number with thousands separators, not a date
    return +ys[0];
  };
  const NUM = s => {
    const t = strip(s); const m = t.match(/(?<![\d.,])(\d{1,3}(?:[.,\s]\d{3})+|\d{4,8})(?![\d,.]?\d)/);
    if (!m) return null; const v = +m[1].replace(/\D/g, ''); return v >= 1000 ? v : null;
  };
  const cellsOf = row => { const out = []; for (const line of row.split('\n')) { const l = line.trim(); if (!l) continue;
      if (!(l[0] === '|' || l[0] === '!')) { if (out.length) out[out.length - 1] += ' ' + l; continue; }
      for (let c of l.slice(1).split(/\|\||!!/)) { const k = c.indexOf('|'); if (k >= 0 && /=/.test(c.slice(0, k)) && !/\[\[|\{\{/.test(c.slice(0, k))) c = c.slice(k + 1); out.push(c.trim()); } }
    return out; };
  const tables = w => { const out = []; let i = 0; while ((i = w.indexOf('{|', i)) >= 0) { let d = 0, j = i; for (; j < w.length - 1; j++) { if (w[j] === '{' && w[j + 1] === '|') d++; else if (w[j] === '|' && w[j + 1] === '}') { d--; if (!d) break; } } out.push(w.slice(i + 2, j)); i = j + 2; } return out; };
  const fromTable = tb => {
    tb = tb.replace(/\{\|[\s\S]*?\|\}/g, '');                           // nested tables are read on their own
    const rows = tb.split(/\n\|-[^\n]*/).map(cellsOf).filter(r => r.length);
    const v = []; for (const r of rows) for (let k = 0; k < r.length; k++) { const y = YR(r[k]); if (y == null) continue; for (let q = k + 1; q < r.length; q++) { if (YR(r[q]) != null && !NUM(r[q])) break; const n = NUM(r[q]); if (n != null && !(n >= 1000 && n <= 2029 && strip(r[q]).trim().length <= 4)) { v.push([y, n]); k = q; break; } } }
    const h = []; for (let a = 0; a + 1 < rows.length; a++) { const ys = rows[a].map(YR); if (ys.filter(x => x != null).length < 3) continue; const b = rows[a + 1]; const off = b.length - rows[a].length; ys.forEach((y, k) => { if (y == null) return; const n = NUM(b[k + off] || ''); if (n != null) h.push([y, n]); }); }
    return h.length > v.length ? h : v; };
  const fromTemplates = w => { const out = [];
    for (const m of w.matchAll(/\{\{\s*(Historical populations|Historical Populations|Historical population|Population|Pop|Bevölkerungsentwicklung|Einwohnerentwicklung|Demografia|Censo)\s*[|\n]/g))
      for (const p of strip(tplAt(w, m.index)).matchAll(/\|\s*(1\d\d\d|20[0-2]\d)\s*[|=]\s*([0-9][0-9., ]*)/g)) { const n = NUM(p[2]); if (n) out.push([+p[1], n]); }
    return out; };
  const fromFrData = w => [...w.matchAll(/\|an(\d+)=\s*(\d{4})\s*\|pop\1=\s*(\d+)/g)].map(m => [+m[2], +m[3]]);
  const fromItDemo = w => { const a = {}, p = {}; for (const m of w.matchAll(/\|\s*a(\d+)\s*=\s*(\d{4})/g)) a[m[1]] = +m[2]; for (const m of w.matchAll(/\|\s*p(\d+)\s*=\s*([\d.]+)/g)) p[m[1]] = +m[2].replace(/\./g, ''); return Object.keys(a).filter(k => p[k] >= 1000).map(k => [a[k], p[k]]); };
  // {{Gráfica de evolución|...|1842|5153|1857|8745|...}}: the unnamed parameters are year, figure, year, figure...
  const tplAt = (w, i) => { let d = 0, j = i; for (; j < w.length - 1; j++) { if (w[j] === '{' && w[j + 1] === '{') { d++; j++; } else if (w[j] === '}' && w[j + 1] === '}') { d--; j++; if (!d) break; } } return w.slice(i, j + 1); };
  const fromEsGraph = w => { const out = []; for (const m of w.matchAll(/\{\{\s*Gráfica de evoluci[oó]n/g)) { const body = tplAt(w, m.index).slice(2, -2).replace(/\{\{[\s\S]*?\}\}/g, ''); const toks = strip(body).split('|').map(s => s.trim()).filter(s => /^\d[\d.]*$/.test(s)).map(s => +s.replace(/\./g, '')); let i = toks.findIndex(t => t >= 1000 && t <= 2029); if (i < 0) continue; for (; i + 1 < toks.length; i += 2) { if (!(toks[i] >= 1000 && toks[i] <= 2029)) break; if (toks[i + 1] >= 1000) out.push([toks[i], toks[i + 1]]); } } return out; };
  const fromPl = w => [...w.matchAll(/bar:\s*(\d{4})\s+from:\s*0\s+till:\s*(\d+)/g)].map(m => [+m[1], +m[2]]).filter(p => p[1] >= 1000);
  const norm = c => { const d = {}; for (const [y, n] of c) if (!(y in d)) d[y] = n; return Object.entries(d).map(([y, n]) => [+y, n]).sort((a, b) => a[0] - b[0]); };
  const keep = (q, src, cands) => {
    const best = cands.map(norm).filter(c => c.length >= 3).sort((a, b) => b.filter(p => p[0] >= 1780).length - a.filter(p => p[0] >= 1780).length).slice(0, 3);
    if (best.length) (G.out[q] = G.out[q] || []).push(...best.map(c => [src, c]));
  };
  // ---------- pages, 20 at a time per language ----------
  const jobs = {}, ruArg = {};
  const add = (lang, title, q) => (jobs[lang] = jobs[lang] || []).push([title, q]);
  for (const [q, w] of towns) for (const [lang, title] of Object.entries(w)) {
    add(lang, title, q);
    if (lang === 'fr') add('fr', `Modèle:Données/${title}/évolution population`, q);
    if (lang === 'it') add('it', `Template:Demografia/${title}`, q);
  }
  G.status = 'pages'; G.total = Object.values(jobs).reduce((t, j) => t + j.length, 0);
  for (const [lang, list] of Object.entries(jobs)) {
    for (let i = 0; i < list.length; i += 20) {
      const part = list.slice(i, i + 20), byTitle = {}; part.forEach(([t, q]) => byTitle[t] = q);
      let cont = {}, pages = [], back = {};
      do {
        const j = await api(lang, { action: 'query', prop: 'revisions', rvprop: 'content', rvslots: 'main', redirects: 1, titles: part.map(p => p[0]).join('|'), ...cont });
        if (!j) { G.errors.push(`${lang} batch ${i} failed`); break; }
        for (const r of [...(j.query.normalized || []), ...(j.query.redirects || [])]) back[r.to] = r.from;
        pages.push(...(j.query.pages || []).filter(p => p.revisions)); cont = j.continue || null;
      } while (cont);
      for (const p of pages) {
        let t = p.title; for (let k = 0; k < 4 && back[t]; k++) t = back[t];
        const q = byTitle[t]; if (!q) continue;
        const w = p.revisions[0].slots.main.content || '';
        const src = `${lang}:${p.title}`;
        if (p.ns === 10 && lang === 'fr') keep(q, src, [fromFrData(w)]);
        else if (p.ns === 10 && lang === 'it') keep(q, src, [fromItDemo(w)]);
        else {
          const c = [fromTemplates(w), ...tables(w).map(fromTable)];
          if (lang === 'es') c.push(fromEsGraph(w));
          if (lang === 'pl') c.push(fromPl(w));
          if (lang === 'fr') c.push(fromFrData(w));
          keep(q, src, c);
          if (lang === 'ru') { const m = w.match(/\{\{\s*[Нн]аселение\s*\|\s*([^|}\n]+)/); if (m) ruArg[q] = m[1].trim(); }
        }
      }
      G.pages += part.length;
    }
  }
  // ---------- ruwiki: expand {{Население|...}}, ten at a time ----------
  G.status = 'ru';
  const rq = Object.keys(ruArg);
  for (let i = 0; i < rq.length; i += 10) {
    const part = rq.slice(i, i + 10);
    const j = await api('ru', { action: 'expandtemplates', prop: 'wikitext', title: 'Москва', text: part.map(q => `{{Население|${ruArg[q]}}}`).join('\nQQSEPQQ\n') });
    if (!j || !j.expandtemplates) { G.errors.push('ru expand ' + i); continue; }
    j.expandtemplates.wikitext.split('QQSEPQQ').forEach((html, k) => {
      const rows = html.split(/<tr[^>]*>/).slice(1), pts = [];
      for (let a = 0; a + 1 < rows.length; a++) {
        const ths = [...rows[a].matchAll(/<th[^>]*>([\s\S]*?)<\/th>/g)].map(m => YR(m[1]));
        if (ths.filter(x => x != null).length < 2) continue;
        const tds = [...rows[a + 1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(m => NUM(m[1]));
        ths.forEach((y, n) => { if (y != null && tds[n] != null) pts.push([y, tds[n]]); });
      }
      if (part[k]) keep(part[k], `ru:{{Население|${ruArg[part[k]]}}}`, [pts]);
    });
  }
  SAVE('hm-town-tables.json', JSON.stringify(G.out));
  G.status = 'done';
})();
