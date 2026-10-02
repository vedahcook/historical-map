"""Put the cities in cities.txt into the built page (europe-borders.html) without rebuilding the maps.

Usage (in europe-map/): python3 cities/patch_page.py
The page keeps every city it already has, in the same order (with the map regions export.py found for them, and
their figures as cities.txt now has them); cities added to cities.txt since (cities/towns_merge.py) are appended, placed in each era's map regions by place_cities.py.
A full rebuild (export.py, merge_eras.py, build_page.py) gives the same list, since export.py reads cities.txt."""
import json, re, sys
sys.path.insert(0, 'cities')
from place_cities import Placer, page_data

PAGE = 'europe-borders.html'
CSRC = 'WGECOUV'      # as in export.py
D, topo = page_data(PAGE)
P = Placer(D, topo)
have = {c[0] for c in D['cities']}
rows = [l.rstrip('\n').split('|') for l in open('cities.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
names = [r[0] for r in rows]
assert names[:len(D['cities'])] == [c[0] for c in D['cities']], 'cities.txt no longer starts with the cities in the page'
pts_of = lambda ser: sorted([1700 + int(a), int(b[:-1]), CSRC.index(b[-1])] for a, b in (p.split(':') for p in ser.split(';')))
for c, r in zip(D['cities'], rows): c[4] = pts_of(r[3])        # figures added to cities already in the page
added, off = [], []
for n, lon, lat, ser in rows[len(D['cities']):]:
    x, y, ss = P.place(float(lon), float(lat))
    if all(s < 0 for s in ss): off.append(n); continue
    added.append([n, x, y, ss, pts_of(ser)])
D['cities'] = D['cities'] + added
h = open(PAGE, encoding='utf-8').read()
m = re.search(r'(<script[^>]*id="data"[^>]*>)(.*?)(</script>)', h, re.S)
data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
open(PAGE, 'w', encoding='utf-8').write(h[:m.start(2)] + data + h[m.end(2):])
print('cities in the page:', len(D['cities']), f'(+{len(added)}); off the map:', off[:20], len(off))
