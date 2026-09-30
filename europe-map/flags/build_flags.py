"""Pack the flags into one image (flags.webp) and write flags_index.json for the page.

Inputs, in the current folder:
  flags_plan.json    description index -> [[article, first year, last year], ...]   (flags_plan.py)
  flags_claims.json  article -> {"q": Wikidata item, "flags": [{"f": Commons file, "s": start year or null,
                     "e": end year or null, "r": rank}, ...]}                       (browser/fetch_flags.js)
  flags_files.json   Commons file -> {"png": base64 thumbnail, "lic": license, "by": author, "url": file page}
Output: flags.webp (each flag 40 px high, at most 80 px wide, twice the size shown) and flags_index.json:
  {"sheet": [w, h], "items": [[x, y, w, h], ...], "desc": {index: [[item, first year, last year], ...]},
   "credits": [[file, author, license, url], ...]}   (credits: flags that are not in the public domain)"""
import base64, io, json
from PIL import Image

plan = json.load(open('flags_plan.json'))
claims = json.load(open('flags_claims.json'))
files = json.load(open('flags_files.json'))

def flag_for(article, year):
    """The flag Wikidata gives for the year: one dated to cover it, else the preferred one, else the first."""
    fl = [f for f in claims.get(article, {}).get('flags', []) if f['f'] in files]
    dated = [f for f in fl if (f['s'] or f['e']) and (f['s'] or -9999) <= year <= (f['e'] or 9999)]
    if dated: return max(dated, key=lambda f: f['s'] or -9999)['f']
    undated = [f for f in fl if not (f['s'] or f['e'])]
    pool = undated or fl
    if not pool: return None
    pref = [f for f in pool if f['r'] == 'preferred']
    return (pref or pool)[0]['f']

used, desc = {}, {}
for i, parts in plan.items():
    runs = []
    for article, y0, y1 in parts:
        for y in range(y0, y1 + 1):
            f = flag_for(article, y)
            if f is None: continue
            k = used.setdefault(f, len(used))
            if runs and runs[-1][0] == k and runs[-1][2] == y - 1: runs[-1][2] = y
            else: runs.append([k, y, y])
    if runs: desc[i] = runs

H, WMAX, COLS = 40, 80, 24
imgs = []
for f in sorted(used, key=used.get):
    im = Image.open(io.BytesIO(base64.b64decode(files[f]['png']))).convert('RGBA')
    w = max(1, round(im.width * H / im.height)); h = H
    if w > WMAX: w, h = WMAX, max(1, round(im.height * WMAX / im.width))
    imgs.append(im.resize((w, h), Image.LANCZOS))
rows = (len(imgs) + COLS - 1) // COLS
sheet = Image.new('RGBA', (COLS * (WMAX + 2), rows * (H + 2)), (0, 0, 0, 0))
items = []
for n, im in enumerate(imgs):
    x, y = (n % COLS) * (WMAX + 2), (n // COLS) * (H + 2)
    sheet.paste(im, (x, y)); items.append([x, y, im.width, im.height])
sheet.save('flags.webp', 'WEBP', quality=88, method=6)
PD = ('public domain', 'pd', 'cc0')
credits = sorted([f, files[f].get('by', ''), files[f].get('lic', ''), files[f].get('url', '')] for f in used
                 if not any(p in (files[f].get('lic') or '').lower() for p in PD))
json.dump({'sheet': list(sheet.size), 'items': items, 'desc': desc, 'credits': credits},
          open('flags_index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('flags', len(items), 'descriptions with a flag', len(desc), 'of', len(plan), 'credits', len(credits),
      'sheet', sheet.size, round(len(open('flags.webp', 'rb').read()) / 1024), 'KB')
