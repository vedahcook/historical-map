// Fetch census tables for cities with gaps in cities.txt, from Wikipedia articles in several languages.
// Run in the browser on any wikipedia.org page (the API allows cross-origin reads with origin=*):
// paste this, then read window.__C (city -> [{src, n, pts}]) once window.__C_done is true.
// For each page it pulls the wikitext and extracts year/population pairs from wikitables (years down a
// column, or across a row with the figures in the next row), from {{Historical populations}}-style
// templates, from chart templates with x=/y= lists, and from French Wikipedia's per-commune data pages.
window.__C = {}; window.__C_done = false;
(async () => {
  const T = window.__T;   // { city: [[lang, title], ...] }
  const strip = s => s.replace(/<ref[^>]*\/>/g, '').replace(/<ref[^>]*>[\s\S]*?<\/ref>/g, '').replace(/<!--[\s\S]*?-->/g, '')
    .replace(/\{\{formatnum:([^}|]*)[^}]*\}\}/gi, '$1').replace(/\{\{(?:0|nts|nowrap|Nts|Nowrap)\|?([^}]*)\}\}/g, '$1')
    .replace(/&nbsp;|&#160;|&thinsp;|[   ]/g, ' ').replace(/'{2,}/g, '').replace(/<[^>]+>/g, ' ');
  const YR = s => { const m = strip(s).trim().replace(/^(ca\.?|um|c\.|approx\.?|env\.?)\s*/i, '').match(/^\[?\[?(1[789]\d\d|20[0-2]\d)\]?\]?(?![\d.,])/); return m ? +m[1] : null; };
  const NUM = s => { const t = strip(s); const m = t.match(/(\d{1,3}(?:[.,  ]\d{3})+|\d{4,8})(?![\d])/); if (!m) return null; const v = +m[1].replace(/[., ]/g, ''); return v >= 1000 ? v : null; };
  const cellsOf = row => { const out = []; for (const line of row.split('\n')) { const l = line.trim(); if (!l) continue;
      if (!(l[0] === '|' || l[0] === '!')) { if (out.length) out[out.length - 1] += ' ' + l; continue; }
      for (let c of l.slice(1).split(/\|\||!!/)) { const k = c.indexOf('|'); if (k >= 0 && /=/.test(c.slice(0, k)) && !/\[\[|\{\{/.test(c.slice(0, k))) c = c.slice(k + 1); out.push(c.trim()); } }
    return out; };
  const tables = w => { const out = []; let i = 0; while ((i = w.indexOf('{|', i)) >= 0) { let d = 0, j = i; for (; j < w.length - 1; j++) { if (w[j] === '{' && w[j + 1] === '|') d++; else if (w[j] === '|' && w[j + 1] === '}') { d--; if (!d) break; } } out.push(w.slice(i + 2, j)); i = j + 2; } return out; };
  const fromTable = tb => {
    const rows = tb.split(/\n\|-[^\n]*/).map(cellsOf).filter(r => r.length);
    const v = []; for (const r of rows) for (let k = 0; k < r.length; k++) { const y = YR(r[k]); if (y == null) continue; for (let q = k + 1; q < r.length; q++) { if (YR(r[q]) != null && !NUM(r[q])) break; const n = NUM(r[q]); if (n != null && !(n >= 1700 && n <= 2030 && r[q].trim().length <= 4)) { v.push([y, n]); k = q; break; } } }
    let h = []; for (let a = 0; a + 1 < rows.length; a++) { const ys = rows[a].map(YR); if (ys.filter(x => x != null).length < 4) continue; const b = rows[a + 1]; const off = b.length - rows[a].length; ys.forEach((y, k) => { if (y == null) return; const n = NUM(b[k + off] || ''); if (n != null) h.push([y, n]); }); }
    return h.length > v.length ? h : v; };
  const fromTemplates = w => { const out = [];
    for (const m of w.matchAll(/\{\{\s*(Historical populations|Historical Populations|Population|Pop|Bevölkerungsentwicklung|Einwohnerentwicklung)[\s\S]*?\}\}/g)) { for (const p of strip(m[0]).matchAll(/\|\s*(1[789]\d\d|20[0-2]\d)\s*[|=]\s*([0-9][0-9.,  ]*)/g)) { const n = NUM(p[2]); if (n) out.push([+p[1], n]); } }
    const xs = w.match(/\|\s*x\s*=\s*([0-9,\s]+)/), ys = w.match(/\|\s*y1?\s*=\s*([0-9.,\s]+)/);
    if (xs && ys) { const X = xs[1].split(',').map(s => +s.trim()), Yv = ys[1].split(',').map(s => +s.trim().replace(/\./g, '')); if (X.length === Yv.length && X.length > 3) X.forEach((x, k) => { if (x >= 1700 && x <= 2030 && Yv[k] >= 1000) out.push([x, Yv[k]]); }); }
    return out; };
  const fromFrData = w => { const out = []; for (const m of w.matchAll(/\|an(\d+)=(\d{4})\s*\|pop\1=(\d+)/g)) out.push([+m[2], +m[3]]); return out; };
  for (const [city, pages] of Object.entries(T)) {
    const res = [];
    for (const [lang, title] of pages) {
      try {
        const j = await fetch(`https://${lang}.wikipedia.org/w/api.php?action=parse&page=${encodeURIComponent(title)}&prop=wikitext&format=json&redirects=1&origin=*`).then(r => r.json());
        const w = j.parse && j.parse.wikitext['*']; if (!w) { res.push({ src: `${lang}:${title}`, err: 'missing' }); continue; }
        const cands = [fromFrData(w), fromTemplates(w), ...tables(w).map(fromTable)];
        const best = cands.map(c => { const d = {}; for (const [y, n] of c) if (!(y in d)) d[y] = n; return Object.entries(d).map(([y, n]) => [+y, n]).sort((a, b) => a[0] - b[0]); })
          .sort((a, b) => b.filter(p => p[0] >= 1850).length - a.filter(p => p[0] >= 1850).length)[0] || [];
        res.push({ src: `${lang}:${j.parse.title}`, n: best.length, pts: best });
      } catch (e) { res.push({ src: `${lang}:${title}`, err: String(e) }); }
    }
    window.__C[city] = res;
  }
  window.__C_done = true;
})();
