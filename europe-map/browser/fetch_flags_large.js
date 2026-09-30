// Fetch a larger copy of each flag the map uses, for the enlarged view shown when a flag is tapped.
// Run in a browser console on any page (the APIs allow cross-origin reads). It reads the list of flags from
// flags/flags_index.json in the GitHub repository, asks Wikimedia Commons for a thumbnail of each that fits in
// 480 x 320 px, and re-encodes it as WebP in the browser. Poll window.__FB.status until 'done', then read
// window.__FB.out (JSON {file: [width, height, base64 WebP]}) in slices and save it as flags_large.json.
window.__FB = { status: 'list', files: {}, errors: [], done: 0 };
(async () => {
  const G = window.__FB;
  const get = async u => { for (let t = 0; t < 4; t++) { try { const r = await fetch(u); if (r.ok) return r; } catch (e) { G.errors.push(String(e)); } await new Promise(s => setTimeout(s, 2000 * (t + 1))); } return null; };
  const idx = await (await get('https://raw.githubusercontent.com/vedahcook/historical-map/main/europe-map/flags/flags_index.json')).json();
  const names = idx.credits.map(c => c[0]);
  G.total = names.length; G.status = 'urls';
  const thumb = {};
  for (let i = 0; i < names.length; i += 50) {
    const r = await get('https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&iiurlwidth=480&iiurlheight=320&format=json&origin=*&titles=' + encodeURIComponent(names.slice(i, i + 50).map(n => 'File:' + n).join('|')));
    if (!r) continue;
    const j = await r.json();
    const back = {}; for (const x of (j.query.normalized || [])) back[x.to] = x.from;
    for (const p of Object.values(j.query.pages)) { const ii = (p.imageinfo || [])[0]; if (ii) thumb[(back[p.title] || p.title).replace(/^File:/, '')] = ii.thumburl; }
  }
  G.status = 'images';
  for (const n of names) {
    try {
      const b = await (await get(thumb[n])).blob();
      const im = await createImageBitmap(b);
      const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
      c.getContext('2d').drawImage(im, 0, 0);
      const w = await new Promise(res => c.toBlob(res, 'image/webp', 0.86));
      const s = await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(w); });
      G.files[n] = [im.width, im.height, s];
    } catch (e) { G.errors.push(n + ': ' + e); }
    G.done++;
  }
  G.out = JSON.stringify(G.files); G.status = 'done';
})();
