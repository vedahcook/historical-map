"""Add the towns picked by towns_select.py to cities.txt, with their population figures.

Usage (in cities/): python3 towns_merge.py hm-town-tables.json ../cities.txt
Inputs: towns_new.json (towns_select.py: each town with its Wikidata figures) and hm-town-tables.json
(browser/fetch_town_tables.js: series from Wikipedia articles), plus de Vries's figures for 1500-1800
(europop_europop.csv, as in add_devries.py).

For each town:
- Wikidata's figures come first (source W), at most one per decade (the year closest to the decade's census year).
- A Wikipedia series is used only if it agrees with Wikidata where both have a figure (within two years): the
  middle ratio between them must be between 2/3 and 3/2. A series about 1,000 times too small is taken as given in
  thousands. With no year in common, its latest figure must be within a factor of two of Wikidata's nearest one
  (at most 15 years apart). A series that passes joins the figures later series are checked against, so the early
  part of a series split over several tables is checked against the later part. Series that pass fill decades
  Wikidata has no figure for (German Wikipedia G, English E, other editions O), best-agreeing first.
- Turkey: see turkey() below.
- de Vries's estimates (V) fill 1500-1800 for towns within 12 km of one of his cities.
- Figures far off the trend of their neighbors are dropped (clean() from merge_cities.py), and a town needs at
  least two figures, one of them 20,000 or more.
Then the towns are appended to cities.txt (the 465 cities already there are left as they are), and the remaining
de Vries cities (10,000 people or more at some point in 1500-1800, not near any listed city) are added with his
figures only, so the early map has its smaller towns too."""
import csv, json, math, re, statistics, sys
from collections import defaultdict

TABLES, CT = sys.argv[1], sys.argv[2]
new = json.load(open('towns_new.json'))
tab = json.load(open(TABLES))

def pick(points, src):
    """One figure per decade: the year closest to the decade's first census year (xx0 or xx1)."""
    by = {}
    for y, v in points:
        d = y // 10
        if d not in by or abs(y % 10 - 1) < abs(by[d][0] % 10 - 1): by[d] = (y, v, src)
    return by

WAR = lambda y: 1914 <= y <= 1922 or 1939 <= y <= 1947
def clean(ser, keep=()):
    """As in merge_cities.py: drop figures far off the trend of their neighbors, worst first."""
    ser = sorted(ser)
    while len(ser) > 2:
        worst, wi = 2.2, None
        for i, (y, v, _) in enumerate(ser):
            if WAR(y) or (y, v) in keep: continue
            others = [(yy, vv) for k, (yy, vv, _) in enumerate(ser) if k != i and not WAR(yy)]
            lo = [p for p in others if p[0] < y]; hi = [p for p in others if p[0] > y]
            if lo and hi: (y0, v0), (y1, v1) = lo[-1], hi[0]
            elif len(hi) >= 2 and hi[0][0] - y <= min(10, hi[1][0] - hi[0][0]): (y0, v0), (y1, v1) = hi[0], hi[1]
            elif len(lo) >= 2 and y - lo[-1][0] <= min(10, lo[-1][0] - lo[-2][0]): (y0, v0), (y1, v1) = lo[-2], lo[-1]
            else: continue
            exp = v0 * (v1 / v0) ** ((y - y0) / (y1 - y0))
            r = max(v / exp, exp / v)
            if r > worst: worst, wi = r, i
        if wi is None: break
        del ser[wi]
    return ser

def km(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    return 6371 * math.acos(min(1, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(a[0] - b[0]))))

def wd_points(t):
    """Wikidata figures by year: a census figure (P459 = census) wins over an estimate; else the middle one."""
    by = defaultdict(list)
    for d, v, det in t['pop']:
        if v >= 1000: by[int(d[:4])].append((det == 'Q39825', v))
    return sorted((y, max(vs)[1] if any(c for c, _ in vs) else int(statistics.median(v for _, v in vs))) for y, vs in by.items())

def agree(series, wd):
    """How far a Wikipedia series is from Wikidata (1 = the same), and the factor to apply (1, or 1000 for
    thousands); None if it disagrees or can't be checked."""
    if not wd: return None
    W = dict(wd)
    # a table read with its columns out of step: its figures turn up in Wikidata, but for other years
    if sum(1 for y, v in series if any(v == wv and abs(y - wy) > 2 for wy, wv in wd)) >= 2: return None
    rs =[v / next(W[y + d] for d in (0, 1, -1, 2, -2) if y + d in W) for y, v in series if any(y + d in W for d in (0, 1, -1, 2, -2))]
    if rs:
        r = statistics.median(rs)
        if 2 / 3 <= r <= 1.5: return abs(math.log(r)), 1
        if 2 / 3 <= r * 1000 <= 1.5: return abs(math.log(r * 1000)), 1000
        return None
    y, v = series[-1]
    yy, vv = min(wd, key=lambda p: abs(p[0] - y))
    if abs(yy - y) <= 15 and 0.5 <= v / vv <= 2: return 0.5 + abs(math.log(v / vv)), 1
    return None

CODE = lambda src: 'G' if src.startswith('de:') else 'E' if src.startswith('en:') else 'O'

# de Vries 1500-1800 (europop), as in add_devries.py
ep = defaultdict(dict)
for r in csv.DictReader(open('europop_europop.csv', encoding='utf-8')):
    if r['population'] not in ('NA', '0'): ep[r['city']][int(r['year'])] = int(r['population']) * 1000
co = {r['city']: (float(r['lon']), float(r['lat'])) for r in csv.DictReader(open('europop_city_coords.csv', encoding='utf-8'))}
WRONG = {'VIENNE', 'BOULOGNE', 'BRANDENBURG'}
MARK = '# Towns added by cities/towns_merge.py'      # the lines after it are this script's; a re-run replaces them
lines_all = open(CT, encoding='utf-8').readlines()
base = lines_all[:next((i for i, l in enumerate(lines_all) if l.startswith(MARK)), len(lines_all))]
old = [l.rstrip('\n').split('|') for l in base if l.strip() and not l.startswith('#')]
old_pos = [(float(r[1]), float(r[2])) for r in old]
dv_used = {c for c in ep if c not in WRONG and any(km(co[c], p) < 12 for p in old_pos)}

# Turkey's 2012-14 reform made its large cities' figures cover their whole province, so from 2013 on Wikidata's
# figures for a "metropolitan municipality" are left out (the city's own figures come from Turkish Wikipedia), and
# for other Turkish towns a figure from 2013 on more than 1.4 times the last earlier one is left out
METRO_TR = lambda t: t['c'] == 'Q43' and any('metropolitan municipality' in c for c in t['cls'])
def turkey(t, wd):
    if t['c'] != 'Q43': return wd
    if METRO_TR(t): return [p for p in wd if p[0] <= 2012]
    before = [v for y, v in wd if y <= 2012]
    return [p for p in wd if p[0] <= 2012 or not before or p[1] <= 1.4 * before[-1]]

def name_of(t):
    """The English name, without a qualifier ("Mysłowice, Silesian Voivodeship", "Van (Turkey)", "Zugdidi Municipality");
    with no English name, the English or German article's title"""
    n = t['label'] or t['wiki'].get('en') or t['wiki'].get('de')
    return re.sub(r',.*$| \(.*\)$| [Mm]unicipality$', '', n) if n else None

out, used_tables, skipped = [], defaultdict(int), defaultdict(int)
for t in new:
    if not name_of(t): continue
    wd = turkey(t, wd_points(t))
    by = pick(wd, 'W')
    # Wikipedia series: first those that agree with Wikidata, then those that agree with what is accepted so far
    # (a German article's series split over tables side by side: the early part is checked against the later)
    # With no Wikidata figure to check against: the largest figure Wikidata has, undated; for a large Turkish city
    # that is its province, of which the city itself is roughly 60% (Konya, Diyarbakır, Eskişehir, Erzurum in 2012)
    ref = list(wd) or ([(2012, 0.6 * t['p'])] if METRO_TR(t) else [(2020, t['p'])] if t['p'] else [])
    pending = [(src, [(y, v) for y, v in pts if 1000 <= y <= 2026]) for src, pts in tab.get(t['q'], [])]
    accepted = []
    while pending:
        scored = [(agree(pts, sorted(ref)), i) for i, (src, pts) in enumerate(pending)]
        ok = [(a, i) for a, i in scored if a]
        if not ok: break
        a, i = min(ok, key=lambda x: x[0][0])
        src, pts = pending.pop(i)
        pts = [(y, v * a[1]) for y, v in pts]
        accepted.append((src, pts))
        have = {y for y, v in ref}; ref += [p for p in pts if p[0] not in have]
    for src, pts in pending: skipped[src.split(':')[0]] += 1
    for src, pts in accepted:
        used_tables[src.split(':')[0]] += 1
        # before 1800 only German Wikipedia's figures (other editions' tables that far back proved unreliable), and
        # none above 1.2 times the town's first figure of 1800-1900: towns grew in the 19th century
        later = [v for y, v in sorted(pts + wd) if 1800 <= y <= 1900][:1]
        pts = [(y, v) for y, v in pts if y >= 1800 or (y >= 1500 and CODE(src) == 'G' and later and v <= 1.2 * later[0])]
        for d, p in pick(pts, CODE(src)).items():
            if d not in by: by[d] = p
    here = (t['lon'], t['lat'])
    near = [c for c in ep if c not in WRONG and c not in dv_used and km(co[c], here) < 12]
    if near:
        c = min(near, key=lambda c: km(co[c], here)); dv_used.add(c)
        for y, v in ep[c].items():
            if y // 10 not in by: by[y // 10] = (y, v, 'V')
    ser = clean([p for p in by.values() if p[1] >= 1000])
    # a figure followed within 15 years by one six times larger is for something else (a village of the same name)
    ser = [p for i, p in enumerate(ser) if not (i + 1 < len(ser) and ser[i + 1][0] - p[0] <= 15 and ser[i + 1][1] >= 6 * p[1])]
    if len(ser) < 2 or max(v for y, v, s in ser) < 20000: continue          # a town needs to have reached 20,000
    out.append((name_of(t), f"{t['lon']:.3f}", f"{t['lat']:.3f}", ser))

# de Vries cities near no listed town: his figures only (title case: the dataset has no accents)
added_dv = 0
for c, fig in ep.items():
    if c in WRONG or c in dv_used or max(fig.values()) < 10000: continue
    if any(km(co[c], (float(lo), float(la))) < 12 for _, lo, la, _ in out): continue
    name = ' '.join(w.capitalize() if w not in ('DE', 'LA', 'EN', 'DA', 'DEL') else w.lower() for w in c.replace("'S ", "'s-").split())
    ser = sorted((y, v, 'V') for y, v in fig.items())
    if len(ser) >= 1: out.append((name, f'{co[c][0]:g}', f'{co[c][1]:g}', ser)); added_dv += 1

# cities listed only for the earlier centuries (Regensburg, Leiden, Toledo...): their later figures come from the
# matching town's Wikidata figures and the series in extend_tables.txt (one per city, checked by eye)
ext = {e['extend']: e for e in json.load(open('towns_extend.json'))}
ET = {}
for l in open('extend_tables.txt', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    q, lang, ser = l.rstrip('\n').split('|'); ET[q] = ('G' if lang == 'de' else 'E' if lang == 'en' else 'O', [tuple(map(int, p.split(':'))) for p in ser.split(';')])
extended = 0
for i, l in enumerate(base):
    if l.startswith('#') or '|' not in l: continue
    n, lo, la, ser = l.rstrip('\n').split('|')
    if n not in ext: continue
    have = sorted((1700 + int(a), int(b[:-1]), b[-1]) for a, b in (p.split(':') for p in ser.split(';')))
    last = have[-1][0]
    t = ext[n]
    by = {}
    if t['q'] in ET: by.update({d: p for d, p in pick(ET[t['q']][1], ET[t['q']][0]).items()})
    for d, p in pick(turkey(t, wd_points(t)), 'W').items():
        if d not in by: by[d] = p
    add = [p for p in by.values() if p[0] > last + 5]
    if not add: continue
    merged = clean(have + add, {(y, v) for y, v, s in have})
    base[i] = f"{n}|{lo}|{la}|" + ';'.join(f'{y - 1700}:{v}{s}' for y, v, s in merged) + '\n'; extended += 1

lines = [f"{n}|{lo}|{la}|" + ';'.join(f'{y - 1700}:{v}{s}' for y, v, s in ser) + '\n' for n, lo, la, ser in out]
open(CT, 'w', encoding='utf-8').writelines(base + [MARK + ' (Wikidata, Wikipedia and de Vries; see that script)\n'] + lines)
print('early cities carried forward', extended)
print('towns added', len(out), f'(of them de Vries only: {added_dv})')
print('Wikipedia series used', dict(used_tables), 'set aside (disagree with Wikidata or unchecked)', dict(skipped))
from collections import Counter
first = Counter(min(y for y, v, s in ser) // 50 * 50 for n, lo, la, ser in out)
print('earliest figure, by half-century:', sorted(first.items()))
