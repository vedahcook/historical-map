"""Pack the flags into one image (flags.webp) and write flags_index.json for the page.

Inputs, in the current folder:
  flags_plan.json    description index -> [[article, first year, last year], ...]   (flags_plan.py)
  flags_claims.json  article -> {"q": Wikidata item, "flags": [{"f": Commons file, "s": start year or null,
                     "e": end year or null, "r": rank}, ...]}                       (browser/fetch_flags.js)
  flags_files.json   Commons file -> {"png": base64 thumbnail, "lic": license, "by": author, "url": file page}
Output: flags.webp (each flag 40 px high, at most 80 px wide, twice the size shown) and flags_index.json:
  {"sheet": [w, h], "items": [[x, y, w, h], ...], "desc": {index: [[item, first year, last year], ...]},
   "credits": [[file, author, license, file page, license page], ...]}   (one per item, in the same order)"""
import base64, io, json, re, sys
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from articles import BAD_FILES, BAD_WORDS, EXTRA, DATES, AUTHORS

plan = json.load(open('flags_plan.json'))
claims = json.load(open('flags_claims.json'))
files = json.load(open('flags_files.json')) if '--list' not in sys.argv else {}

def name_years(f):
    """Years in a file name such as "Flag of Albania (1920–1926).svg" or "(1918, 1991–1995)": a list of (from, to).
    A lone year, as in "(1692)", is when the flag was adopted, so it is open-ended."""
    m = re.search(r'\(([^()]*\d{4}[^()]*)\)', f)
    if not m: return []
    parts = [p.strip() for p in m.group(1).split(',')]
    spans = []
    for p in parts:
        r = re.fullmatch(r'(\d{3,4})\s*[-–]\s*(\d{3,4}|present)', p)
        if r: spans.append((int(r.group(1)), None if r.group(2) == 'present' else int(r.group(2))))
        elif re.fullmatch(r'\d{4}', p): spans.append((int(p), int(p)))
    if len(spans) == 1 and spans[0][0] == spans[0][1] and len(parts) == 1: spans = [(spans[0][0], None)]
    return spans

def candidates(article):
    """(file, from, to, preferred) for each of the article's flags: dates from Wikidata, else from the file name."""
    out = []
    for f in claims.get(article, {}).get('flags', []):
        if f['f'] in BAD_FILES or any(w in f['f'] for w in BAD_WORDS): continue
        if (article, f['f']) in DATES: out.append((f['f'], *DATES[(article, f['f'])], f['r'] == 'preferred'))
        elif f['s'] or f['e']: out.append((f['f'], f['s'], f['e'], f['r'] == 'preferred'))
        else: out += [(f['f'], a, b, f['r'] == 'preferred') for a, b in name_years(f['f'])] or [(f['f'], None, None, f['r'] == 'preferred')]
    return out + [(f, a, b, False) for f, a, b in EXTRA.get(article, [])]

def flag_for(article, year):
    """The flag in use in that year: one dated to cover it (the most recent), else an undated one (the preferred)."""
    c = [x for x in candidates(article) if not files or x[0] in files]
    dated = [x for x in c if (x[1] is not None or x[2] is not None) and (x[1] or -9999) <= year <= (x[2] or 9999)]
    # the most recently adopted; among flags adopted the same year, the preferred one, then the main design rather
    # than a variant (civil ensign, alternative color version)
    plain = lambda f: not any(w in f.lower() for w in ('variant', 'version', 'civil', 'pantone', 'digital'))
    if dated: return max(dated, key=lambda x: (x[1] or -9999, x[3], plain(x[0])))[0]
    undated = [x for x in c if x[1] is None and x[2] is None]
    if not undated: return None
    return ([x for x in undated if x[3]] or undated)[0][0]

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
if '--list' in sys.argv:        # just the files needed, for fetching their thumbnails
    json.dump(sorted(used), open('flags_needed.json', 'w'), ensure_ascii=False)
    print(len(used), 'files for', len(desc), 'of', len(plan), 'descriptions'); sys.exit()

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
LIC = {'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/', 'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/',
       'CC BY-SA 2.5': 'https://creativecommons.org/licenses/by-sa/2.5/', 'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0/',
       'CC BY 2.5': 'https://creativecommons.org/licenses/by/2.5/', 'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/',
       'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/',
       # Commons "Attribution" tag: anyone may use the file for any purpose if the author is credited
       'free to use with credit': 'https://commons.wikimedia.org/wiki/Template:Attribution'}
def author(f):
    if f in AUTHORS: return AUTHORS[f]
    a = re.sub(r'\(talk\)|User:|^Drawing created by ', '', files[f].get('by', ''))
    a = re.sub(r'^Original: (.+?) Derivative work: (.+)$', r'\1, derivative work by \2', re.sub(r'\s+', ' ', a).strip(), flags=re.I)
    return a.replace('previous version ', 'earlier version by ').replace(' ; current version ', ', current version by ')
def lic(f):
    l = files[f].get('lic', '') or 'see file page'
    return 'free to use with credit' if l == 'Attribution' else l
# for each flag: [file, author, license, file page, license page]
credits = [[f, author(f), lic(f), files[f].get('url', ''), LIC.get(lic(f), '')] for f in sorted(used, key=used.get)]
json.dump({'sheet': list(sheet.size), 'items': items, 'desc': desc, 'credits': credits},
          open('flags_index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('flags', len(items), 'descriptions with a flag', len(desc), 'of', len(plan), 'not public domain', sum(1 for c in credits if 'public domain' not in c[2].lower()),
      'sheet', sheet.size, round(len(open('flags.webp', 'rb').read()) / 1024), 'KB')
