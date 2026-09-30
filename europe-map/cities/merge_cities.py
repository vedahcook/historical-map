"""Extend cities.txt to 2026 and add cities that grew large after 1900.
Inputs: wd_cities.txt (Wikidata: title|QID|lon,lat|year:pop;...), enwiki_cities.txt (English Wikipedia
{{Historical populations}} tables: title|year:pop;...), and the existing cities.txt."""
import math, re, sys
CT = sys.argv[1]
OLD_TITLES = None
wd = {}; ll = {}
for l in open('wd_cities.txt').read().split('\n'):
    t, q, c, ser = l.split('|')
    wd[t] = [(int(a), int(b)) for a, b in (p.split(':') for p in ser.split(';') if p)]
    if c: ll[t] = tuple(float(v) for v in c.split(','))
ex = {}
for l in open('extras.txt').read().strip().split('\n'):
    t, src, ser = l.split('|'); ex[t] = (src, [(int(a), int(b)) for a, b in (p.split(':') for p in ser.split(';'))])
en = {}
for l in open('enwiki_cities.txt').read().split('\n'):
    t, ser = l.split('|'); en[t] = [(int(a), int(b)) for a, b in (p.split(':') for p in ser.split(';') if p)]

# cities.txt names -> the Wikipedia titles used for the lookups (same order as the browser list)
rows = [l.rstrip('\n').split('|') for l in open(CT) if l.strip() and not l.startswith('#')]
header = [l for l in open(CT) if l.startswith('#')]
titles_old = [t for t in open('titles_old.txt').read().split('\n') if t]
assert len(titles_old) == len(rows), (len(titles_old), len(rows))

def pick(points, src):
    """One figure per decade: the year closest to the decade's first census year (xx0 or xx1)."""
    by = {}
    for y, v in points:
        d = y // 10
        if d not in by or abs(y % 10 - 1) < abs(by[d][0] % 10 - 1): by[d] = (y, v, src)
    return by

WAR = lambda y: 1914 <= y <= 1922 or 1939 <= y <= 1947

def clean(ser, keep=()):
    """Drop figures far off the trend of their neighbors (likely a different city boundary in the source).
    The worst one goes first, so one bad figure does not also knock out its good neighbors. Figures from
    the two world wars and their aftermath are kept and not used as neighbors: cities really did shrink
    and grow fast then. The first and last figures are checked against the trend of the next two, but only
    when the next one is at most 10 years away. Figures in `keep` (the 1800-1905 series, checked before) stay."""
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

def fix_units(t):
    """Some English Wikipedia tables are in thousands. Compare with Wikidata for the same years."""
    e, w = dict(en.get(t, [])), dict(wd.get(t, []))
    common = [y for y in e if y in w and e[y] > 0]
    if not common: return
    r = sorted(w[y] / e[y] for y in common)[len(common) // 2]
    if 500 < r < 2000: en[t] = [(y, v * 1000) for y, v in en[t]]; print('  thousands:', t)
    elif r > 3 or r < 1 / 3: del en[t]; print('  English table disagrees with Wikidata, skipped:', t, round(r, 2))
for t in list(en): fix_units(t)

out = []
dropped = 0
for (name, lon, lat, ser), t in zip(rows, titles_old):
    old = [(1700 + int(a), int(b[:-1]), b[-1]) for a, b in (p.split(':') for p in ser.split(';'))]
    old_dec = {y // 10 for y, v, s in old}
    new_by = pick([p for p in wd.get(t, []) if p[0] >= 1906], 'W')
    if t in ex: new_by.update(pick([p for p in ex[t][1] if p[0] >= 1906], ex[t][0]))
    new_by.update(pick([p for p in en.get(t, []) if p[0] >= 1906], 'E'))     # English Wikipedia's table wins
    add = [v for d, v in new_by.items() if d not in old_dec]
    merged = clean(old + add, {(y, v) for y, v, s in old})
    dropped += len(old + add) - len(merged)
    out.append((name, lon, lat, merged))

NEW = [t for t in wd if t not in set(titles_old)]
added = []
for t in NEW:
    if t not in ll: continue
    by = pick([p for p in wd.get(t, []) if p[0] >= 1785], 'W')
    if t in ex: by.update(pick(ex[t][1], ex[t][0]))
    by.update(pick([p for p in en.get(t, []) if p[0] >= 1785], 'E'))
    ser = clean(list(by.values()))
    if len(ser) < 2: continue
    name = re.sub(r', .*$| \(.*\)$', '', t)
    name = {'Volzhsky': 'Volzhsky', 'Halle': 'Halle', 'Cork': 'Cork'}.get(name, name)
    added.append((name, f'{ll[t][0]:g}', f'{ll[t][1]:g}', ser))
# figures for a different area than the rest of the series: metro areas (Lille 2020, Thessaloniki from 2001), whole
# provinces after Turkey's 2012-14 metropolitan-municipality reform, and plain errors (Malatya 2020, Tabriz 1976)
DROP = {'Lille': {2020}, 'Thessaloniki': {2001, 2011, 2021}, 'Kayseri': {2018}, 'Mersin': {2014}, 'Samsun': {2022},
        'Trabzon': {2021}, 'Malatya': {2020}, 'Tabriz': {1976}}
out = [(n, lo, la, [p for p in ser if p[0] not in DROP.get(n, ())]) for n, lo, la, ser in out]
added = [(n, lo, la, [p for p in ser if p[0] not in DROP.get(n, ())]) for n, lo, la, ser in added]
# UN Statistics Division city-proper figures (un_cities.txt, from un_extract.py) fill decades nothing else covers;
# the figures already chosen stay, and a UN figure off their trend is dropped
UN = {}
for l in open('un_cities.txt', encoding='utf-8').read().strip().split('\n'):
    n, c, ser = l.split('|'); UN[n] = [(int(a), int(b)) for a, b in (p.split(':') for p in ser.split(';'))]
def add_un(n, ser):
    have = {y // 10 for y, v, s in ser}
    new = [p for d, p in pick(UN.get(n, []), 'U').items() if d not in have]
    return clean(ser + new, {(y, v) for y, v, s in ser}) if new else ser
out = [(n, lo, la, add_un(n, ser)) for n, lo, la, ser in out]
added = [(n, lo, la, add_un(n, ser)) for n, lo, la, ser in added]
# census tables from city articles in several Wikipedia editions (wiki_tables.txt, fetched with
# browser/fetch_city_tables.js): "fill" adds figures for decades nothing else covers; "replace" swaps in the
# whole series over its span (Paris: the official census series instead of estimates for the wider city)
WT = {}
for l in open('wiki_tables.txt', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    n, code, mode, src, ser = l.rstrip('\n').split('|')
    WT.setdefault(n, []).append((code, mode, [(int(a), int(b)) for a, b in (p.split(':') for p in ser.split(';'))]))
def add_wt(n, ser):
    for code, mode, pts in WT.get(n, []):
        if mode == 'replace':
            y0, y1 = pts[0][0], pts[-1][0]
            ser = sorted([p for p in ser if not y0 <= p[0] <= y1] + list(pick(pts, code).values()))
        else:
            have = {y // 10 for y, v, s in ser}
            new = [p for d, p in pick(pts, code).items() if d not in have]
            if new: ser = clean(ser + new, {(y, v) for y, v, s in ser})
    return ser
out = [(n, lo, la, add_wt(n, ser)) for n, lo, la, ser in out]
added = [(n, lo, la, add_wt(n, ser)) for n, lo, la, ser in added]
missing = set(WT) - {n for n, *_ in out + added}
assert not missing, missing
lines = header + [f"{n}|{lo}|{la}|" + ';'.join(f'{y - 1700}:{v}{s}' for y, v, s in ser) + '\n' for n, lo, la, ser in out + added]
open('cities_new.txt', 'w').writelines(lines)
print('cities', len(out), '+ new', len(added), 'dropped as off-trend', dropped)
from collections import Counter
dec = Counter(y // 10 * 10 for n, lo, la, ser in out + added for y, v, s in ser if y >= 1900)
print(sorted(dec.items()))
