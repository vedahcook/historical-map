"""Find where OHM, CShapes-Europe and Cliopatria disagree about who held each Balkan town, 1815-1900.

Inputs (same folder): towns.json, ohm_towns.json, cshapes_towns.json, clio_towns.json
Output: conflicts.json (grouped conflicts) and timelines.json (per town, per source, per year).
"""
import json, re
from collections import defaultdict

YEARS = list(range(1815, 1901))
towns = json.load(open('towns.json'))
ohm = json.load(open('ohm_towns.json'))
cs = json.load(open('cshapes_towns.json'))
clio = json.load(open('clio_towns.json'))

# Drop near-duplicate towns created by merging lists.
towns = [t for t in towns if not t[0].endswith(' (2)')]
TOWN = {t[0]: (t[1], t[2]) for t in towns}

# ---- canonical holders -------------------------------------------------------
LABEL = {
    'OTT': 'Ottoman Empire', 'RUS': 'Russian Empire', 'AUT': 'Austria', 'GRE': 'Greece',
    'SRB': 'Serbia', 'MNE': 'Montenegro', 'WAL': 'Wallachia', 'MOL': 'Moldavia',
    'ROM': 'Romania (United Principalities)', 'BUL': 'Bulgaria', 'ERU': 'Eastern Rumelia',
    'EGY': 'Egypt', 'CRT': 'Cretan State', 'ION': 'Ionian Islands', 'UK': 'United Kingdom',
    'AUTOCC': 'Austria-Hungary (occupation)', 'HUNREV': 'Hungarian revolutionaries',
    'FRA': 'France', 'NONE': 'No country',
}
# Which holders are self-governing units under an overlord (vassal or protectorate).
OVERLORD = {'SRB': 'OTT', 'WAL': 'OTT', 'MOL': 'OTT', 'ROM': 'OTT', 'BUL': 'OTT', 'ERU': 'OTT',
            'EGY': 'OTT', 'CRT': 'OTT', 'ION': 'UK', 'AUTOCC': 'OTT', 'HUNREV': 'AUT'}

def canon(name):
    n = name.lower()
    rules = [
        ('ottoman|turkey', 'OTT'), ('russia', 'RUS'), ('austria-hungary|austrian empire|cisleithania|transleithania|habsburg', 'AUT'),
        ('greece|hellenic', 'GRE'), ('serbia|serbs', 'SRB'), ('montenegro', 'MNE'),
        ('united romanian|united principalities|romania|rumania', 'ROM'), ('wallachia', 'WAL'), ('moldavia', 'MOL'),
        ('eastern rumelia', 'ERU'), ('bulgaria', 'BUL'), ('egypt', 'EGY'), ('cretan state', 'CRT'),
        ('ionian|septinsular', 'ION'), ('united kingdom|british|great britain', 'UK'),
        ('bosnia|herzegovina', 'AUTOCC'), ('hungarian nationalists', 'HUNREV'), ('france|french', 'FRA'),
    ]
    for pat, key in rules:
        if re.search(pat, n):
            return key
    return 'OTHER:' + name

# ---- OHM: effective holder per year ------------------------------------------
recs = ohm['recs']            # [osm_id, name, level, start, end]
combos = [[int(x) for x in c.split(',')] if c else [] for c in ohm['combos']]
VASSAL_L3 = {'Principality of Serbia', 'Principality of Wallachia', 'Principality of Moldavia',
             'United Romanian Principalities', 'Bulgaria'}
L4_AUTONOMY = {'Eastern Rumelia': 'ERU', 'Eyalet of Egypt': 'EGY'}

def active(r, date):
    return r[3] <= date and (not r[4] or r[4] > date)

def ohm_holder(town, year):
    date = f'{year}-07-01'
    act = [recs[i] for i in combos[ohm['towns'][town]] if active(recs[i], date)]
    l2 = [r for r in act if r[2] == 2]
    l3 = [r for r in act if r[2] == 3 and r[1] in VASSAL_L3]
    l4 = [r for r in act if r[2] == 4 and r[1] in L4_AUTONOMY]
    ids = [r[0] for r in act]
    if l3:
        return canon(l3[0][1]), ids
    if l4:
        return L4_AUTONOMY[l4[0][1]], ids
    keys = sorted({canon(r[1]) for r in l2})
    if not keys:
        return 'NONE', ids
    if len(keys) > 1:
        vassals = [k for k in keys if k in OVERLORD]
        if len(vassals) == 1 and all(k == vassals[0] or k == OVERLORD[vassals[0]] for k in keys):
            return vassals[0], ids
        return '+'.join(keys), ids
    return keys[0], ids

def from_runs(runs, year, parse):
    for a, b, k in runs:
        if a <= year <= b:
            return parse(k)
    return None

def cs_parse_key(i):
    k = cs['keys'][i]
    if not k:
        return None
    parts = [p.split('~')[0] for p in k.split(';')]
    keys = sorted({('AUTOCC' if p.split('|')[0] in ('Bosnia', 'Herzegovina') else canon(p.split('|')[0])) for p in parts})
    return '+'.join(keys)

def clio_parse(k):
    if not k:
        return None
    names = [p.split('~')[0] for p in k.split(';')]
    keys = sorted({canon(n) for n in names})
    if len(keys) > 1:
        vassals = [x for x in keys if x in OVERLORD]
        if len(vassals) == 1 and all(x == vassals[0] or x == OVERLORD[vassals[0]] for x in keys):
            return vassals[0]
    return '+'.join(keys)

timelines = {}
for t in TOWN:
    tl = {'OHM': {}, 'CShapes': {}, 'Cliopatria': {}, 'OHM_records': {}}
    for y in YEARS:
        h, ids = ohm_holder(t, y)
        tl['OHM'][y] = h
        tl['OHM_records'][y] = ids
        tl['CShapes'][y] = from_runs(cs['towns'][t], y, cs_parse_key) if y >= 1816 else None
        tl['Cliopatria'][y] = from_runs(clio[t], y, clio_parse)
    timelines[t] = tl

# ---- classify each town-year ------------------------------------------------
SOURCES = ['OHM', 'CShapes', 'Cliopatria']

def related(a, b):
    """True if a and b differ only as a self-governing unit vs. its overlord (or two names for one line)."""
    fam = {'WAL', 'MOL', 'ROM'}
    if a in fam and b in fam:
        return True
    return OVERLORD.get(a) == b or OVERLORD.get(b) == a

def classify(vals):
    speaking = {s: v for s, v in vals.items() if v is not None}
    distinct = set(speaking.values())
    if len(distinct) <= 1:
        return 'agree'
    if speaking.get('OHM') == 'NONE':
        return 'gap'
    others = distinct - {'NONE'}
    if all(related(a, b) for a in others for b in others if a != b) and 'NONE' not in distinct:
        return 'rule'
    return 'holder'

cells = defaultdict(dict)   # town -> year -> (category, signature)
for t, tl in timelines.items():
    for y in YEARS:
        vals = {s: tl[s][y] for s in SOURCES}
        cat = classify(vals)
        sig = tuple((s, vals[s]) for s in SOURCES if vals[s] is not None)
        cells[t][y] = (cat, sig)

# Timing: a disagreement lasting a single year, whose values all appear the year before or after,
# is just sources picking different years for the same change.
def values_at(t, y):
    if y not in cells[t]:
        return set()
    return {v for _, v in cells[t][y][1]}

runs = []   # (town, category, signature, start, end)
for t in cells:
    y = YEARS[0]
    while y <= YEARS[-1]:
        cat, sig = cells[t][y]
        e = y
        while e + 1 <= YEARS[-1] and cells[t][e + 1] == (cat, sig):
            e += 1
        if cat != 'agree':
            if e - y + 1 <= 1 and {v for _, v in sig} <= (values_at(t, y - 1) | values_at(t, e + 1)):
                cat = 'timing'
            runs.append((t, cat, sig, y, e))
        y = e + 1

# ---- group runs into conflicts -------------------------------------------------
groups = defaultdict(list)
for t, cat, sig, a, b in runs:
    groups[(cat, sig)].append((t, a, b))

conflicts = []
for (cat, sig), items in groups.items():
    # split into clusters of overlapping or touching year ranges
    items.sort(key=lambda x: x[1])
    clusters = []
    for it in items:
        for c in clusters:
            if it[1] <= c['end'] + 1 and it[2] >= c['start'] - 1:
                c['towns'].append(it); c['start'] = min(c['start'], it[1]); c['end'] = max(c['end'], it[2]); break
        else:
            clusters.append({'towns': [it], 'start': it[1], 'end': it[2]})
    for c in clusters:
        conflicts.append({
            'category': cat,
            'claims': [{'source': s, 'holder': v, 'label': LABEL.get(v, v)} for s, v in sig],
            'start': c['start'], 'end': c['end'],
            'towns': sorted({x[0] for x in c['towns']}),
            'town_ranges': sorted([[x[0], x[1], x[2]] for x in c['towns']]),
            'town_years': sum(x[2] - x[1] + 1 for x in c['towns']),
        })

conflicts.sort(key=lambda c: (-c['town_years']))
for i, c in enumerate(conflicts):
    c['id'] = f'c{i + 1:03d}'
json.dump(conflicts, open('conflicts_raw.json', 'w'), ensure_ascii=False, indent=1)
json.dump({t: {s: [tl[s][y] for y in YEARS] for s in SOURCES} for t, tl in timelines.items()},
          open('timelines.json', 'w'), ensure_ascii=False)
json.dump({t: [tl['OHM_records'][y] for y in YEARS] for t, tl in timelines.items()}, open('ohm_record_ids.json', 'w'))

from collections import Counter
print('towns', len(TOWN), 'runs', len(runs), 'conflicts', len(conflicts))
print(Counter(c['category'] for c in conflicts))
print('town-years by category', {k: sum(c['town_years'] for c in conflicts if c['category'] == k) for k in ['holder', 'gap', 'rule', 'timing']})
for c in conflicts[:70]:
    if c['category'] == 'timing':
        continue
    print(c['id'], c['category'], c['start'], c['end'], c['town_years'], '|', '; '.join(f"{x['source']}={x['holder']}" for x in c['claims']), '|', ', '.join(c['towns'][:8]) + (' …' if len(c['towns']) > 8 else ''))
