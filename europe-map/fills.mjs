import { validate, contrast } from './vp.mjs';
import fs from 'fs';
const hexToRgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const rgbToHex = c => '#' + c.map(v => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, '0')).join('');
const mix = (a, b, t) => rgbToHex(hexToRgb(a).map((v, i) => v * t + hexToRgb(b)[i] * (1 - t)));
const names = ['blue', 'orange', 'aqua', 'yellow', 'magenta', 'green', 'violet', 'red'];
const light = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'];
const dark = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767'];
const levels = { light: [0.38, 0.62], dark: [0.52, 0.74] };
const out = {};
for (const mode of ['light', 'dark']) {
  const surf = mode === 'light' ? '#fcfcfb' : '#1a1a19';
  const P = [];
  for (const t of levels[mode]) for (let i = 0; i < 8; i++) P.push(mix((mode === 'light' ? light : dark)[i], surf, t));
  const cvd = [], nv = [];
  for (let i = 0; i < P.length; i++) { cvd.push([]); nv.push([]); for (let j = 0; j < P.length; j++) {
    if (i === j) { cvd[i].push(0); nv[i].push(0); continue; }
    const r = validate([P[i], P[j]], { mode, surface: surf, pairs: 'all' }).report;
    cvd[i].push(+(/ΔE ([\d.]+)/.exec(r[2][2]) || [0, 99])[1]); nv[i].push(+(/ΔE ([\d.]+)/.exec(r[3][2]) || [0, 99])[1]);
  } }
  const ink = mode === 'light' ? '#0b0b0b' : '#ffffff';
  out[mode] = { P, cvd, nv, inkContrast: P.map(p => +contrast(p, ink).toFixed(2)) };
}
out.names = [...names.map(n => n + '-1'), ...names.map(n => n + '-2')];
fs.writeFileSync('fills.json', JSON.stringify(out));
console.log(out.light.P.join(' '), '\n', out.dark.P.join(' '));
console.log('ink contrast light', out.light.inkContrast.join(' '), '\n dark', out.dark.inkContrast.join(' '));
