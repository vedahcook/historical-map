"""Step 7: join the two eras for the page.

Usage (in the later era's folder): python3 merge_eras.py EARLY_DIR
Reads data.json and topo.json from EARLY_DIR (1500-1799) and from the current folder (1800-2026). Writes
  page_data.json            shared lists (countries, names, descriptions, cities) and the 1800-2026 map; build_page.py
                            puts it in the page with the 1800-2026 topo.json
  europe-borders-1500.json  the 1500-1799 map (its outlines and who held each area), which the page loads when needed
Countries, their names and their descriptions become single lists, so a country is the same entry, with the same
color, on both sides of 1800."""
import json, sys

ED = sys.argv[1]
E = json.load(open(f'{ED}/data.json'))
L = json.load(open('data.json'))
ET = json.load(open(f'{ED}/topo.json'))
for k in ('desc', 'fills', 'viewBox', 'home'):
    assert E[k] == L[k], k
assert [c[0] for c in E['cities']] == [c[0] for c in L['cities']]

# ---------- countries by key ----------
units, UI = [], {}
for d in (L, E):
    for u in d['units']:
        if u['k'] not in UI:
            UI[u['k']] = len(units); units.append({k: v for k, v in u.items() if k != 'ov'})
        else:
            assert units[UI[u['k']]]['c'] == u['c'], ('color differs between eras', u['k'])
for d in (L, E):
    for u in d['units']:
        if u.get('ov') is not None:
            ov = UI[d['units'][u['ov']]['k']]
            prev = units[UI[u['k']]].get('ov')
            assert prev in (None, ov), ('overlord differs between eras', u['k'])
            units[UI[u['k']]]['ov'] = ov
for u in units: u.setdefault('ov', None)

# ---------- names ----------
names, NI = [], {}
for d in (L, E):
    for n in d['names']:
        if n not in NI: NI[n] = len(names); names.append(n)

def era(d):
    um = [UI[u['k']] for u in d['units']]
    nm = [NI[n] for n in d['names']]
    U = lambda u: um[u] if u is not None and u >= 0 else u
    return {
        'hist': [[[y, U(u), r] for y, u, r in runs] for runs in d['hist']],
        'refs': d['refs'],
        'labels': {y: [[U(r[0]), *r[1:5], nm[r[5]], r[6]] for r in rows] for y, rows in d['labels'].items()},
        'alts': [{**a, 'd': U(a['d']), 'a': U(a['a'])} for a in d['alts']],
    }

cities = [[n, x, y, [se, sl], P] for (n, x, y, se, _), (_, _, _, sl, P) in zip(E['cities'], L['cities'])]
page = {'years': [E['years'][0], L['years'][1]], 'viewBox': L['viewBox'], 'home': L['home'], 'units': units,
        'fills': L['fills'], 'names': names, 'desc': L['desc'], 'cities': cities,
        'eras': [{'y0': E['years'][0], 'y1': E['years'][1], 'src': 'europe-borders-1500.json'},
                 {'y0': L['years'][0], 'y1': L['years'][1]}],
        'late': era(L)}
json.dump(page, open('page_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump({'topo': ET, **era(E)}, open('europe-borders-1500.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('countries', len(units), '(later', len(L['units']), 'early', len(E['units']), ') names', len(names),
      'cities', len(cities))
