// Cut Europe out of the elevation picture on Wikimedia Commons ("Srtm ramp2.world.21600x10800.jpg", NASA, public domain:
// heights as 8-bit gray, one pixel per minute of arc) for terrain/make_relief_dem.py. Run in the browser on an ordinary
// Wikidata or Wikipedia page (their content security policy lets a script read upload.wikimedia.org). It keeps 35°W–62°E,
// 76°N–30°N (5820 x 2760 pixels), filters each row by differences (as PNG does), gzips it and leaves it as base64 in
// DEM.b64, to be read in pieces of 240,000 characters with DEM.part(i) and joined again (undo the differences with a
// running sum per row, modulo 256). The result is saved as terrain/srtm_ramp2_eu.u8.gz.
window.DEM = { status: 'fetching' };
(async () => {
  const info = await (await fetch('https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&format=json&origin=*&titles=' + encodeURIComponent('File:Srtm ramp2.world.21600x10800.jpg'))).json();
  const url = Object.values(info.query.pages)[0].imageinfo[0].url.split('?')[0];
  const blob = await (await fetch(url)).blob(); DEM.status = 'decoding';
  const ppd = 60, x0 = (180 - 35) * ppd, y0 = (90 - 76) * ppd, w = 97 * ppd, h = 46 * ppd;
  const bmp = await createImageBitmap(blob, x0, y0, w, h);
  const cv = new OffscreenCanvas(w, h), cx = cv.getContext('2d'); cx.drawImage(bmp, 0, 0);
  const d = cx.getImageData(0, 0, w, h).data, f = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) { let p = 0; for (let x = 0; x < w; x++) { const v = d[(y * w + x) * 4]; f[y * w + x] = (v - p) & 255; p = v; } }
  const z = new Uint8Array(await new Response(new Blob([f]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
  let s = ''; for (let i = 0; i < z.length; i += 0x8000) s += String.fromCharCode.apply(null, z.subarray(i, i + 0x8000));
  DEM.b64 = btoa(s); DEM.n = Math.ceil(DEM.b64.length / 240000); DEM.status = 'ready';
  DEM.part = i => 'DEMPART ' + i + ' ' + DEM.b64.slice(i * 240000, (i + 1) * 240000) + (i === DEM.n - 1 ? ' '.repeat(150000) : '');
})();
