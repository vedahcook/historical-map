"""Step 7: join the eras for the page.

Usage (in the later era's folder): python3 merge_eras.py EARLIER_DIR [EARLIER_DIR ...]
Reads data.json and topo.json from each earlier era's folder (1500-1799, 1000-1499) and from the current folder
(1800-2026). Writes
  page_data.json            shared lists (countries, names, descriptions, cities) and the 1800-2026 map; build_page.py
                            puts it in the page with the 1800-2026 topo.json
  europe-borders-YYYY.json  each earlier era's map (its outlines and who held each area), named by its first year,
                            which the page loads when needed
Countries, their names and their descriptions become single lists, so a country is the same entry, with the same
color, in every era."""
import json, os, sys

L = json.load(open('data.json'))
EARLY = [(json.load(open(f'{d}/data.json')), json.load(open(f'{d}/topo.json'))) for d in sys.argv[1:]]
EARLY.sort(key=lambda e: e[0]['years'][0])                 # oldest first
ALL = [e for e, t in EARLY] + [L]
for E in ALL[:-1]:
    for k in ('desc', 'fills', 'viewBox', 'home'):
        assert E[k] == L[k], k
    assert [c[0] for c in E['cities']] == [c[0] for c in L['cities']]

# ---------- countries by key ----------
units, UI = [], {}
for d in [L] + ALL[:-1][::-1]:                             # the later map's order first
    for u in d['units']:
        if u['k'] not in UI:
            UI[u['k']] = len(units); units.append({k: v for k, v in u.items() if k != 'ov'})
        else:
            assert units[UI[u['k']]]['c'] == u['c'], ('color differs between eras', u['k'])
for d in ALL:
    for u in d['units']:
        if u.get('ov') is not None:
            ov = UI[d['units'][u['ov']]['k']]
            prev = units[UI[u['k']]].get('ov')
            assert prev in (None, ov), ('overlord differs between eras', u['k'])
            units[UI[u['k']]]['ov'] = ov
for u in units: u.setdefault('ov', None)

# ---------- names ----------
names, NI = [], {}
for d in [L] + ALL[:-1][::-1]:
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

# each city: [name, x, y, [its map region in each era, oldest first], population figures]
cities = [[c[0][0], c[0][1], c[0][2], [cc[3] for cc in c], c[-1][4]] for c in zip(*[d['cities'] for d in ALL])]
page = {'years': [ALL[0]['years'][0], L['years'][1]], 'viewBox': L['viewBox'], 'home': L['home'], 'units': units,
        'fills': L['fills'], 'names': names, 'desc': L['desc'], 'cities': cities,
        'eras': [{'y0': d['years'][0], 'y1': d['years'][1], 'src': f"europe-borders-{d['years'][0]}.json"} for d in ALL[:-1]]
                + [{'y0': L['years'][0], 'y1': L['years'][1]}],
        'late': era(L)}
if os.path.exists('flags_index.json'):      # flags (flags/build_flags.py): the page shows them from flags.webp
    page['flags'] = json.load(open('flags_index.json'))
json.dump(page, open('page_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
for (E, T) in EARLY:
    json.dump({'topo': T, **era(E)}, open(f"europe-borders-{E['years'][0]}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
print('countries', len(units), '(' + ', '.join(f"{d['years'][0]}-{d['years'][1]}: {len(d['units'])}" for d in ALL) + ') names', len(names),
      'cities', len(cities))
