"""Step 6: pick fill colors so neighbors always differ, project everything, and write the
files the page needs: geo.json (regions, alternative-border areas, lakes, rivers as
GeoJSON in map coordinates) and data.json (country histories, labels, notes).

Needs fills.json (candidate fills and their measured color separation, from the
dataviz palette validator) and the Natural Earth lakes/rivers files.
"""
import json, pickle, sys, time, re
from collections import defaultdict
import numpy as np
import shapely
from shapely.geometry import shape, mapping, box
from shapely.strtree import STRtree
from shapely.ops import polylabel
from pyproj import Transformer
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from units import UNITS

t0 = time.time()
BAL = sys.argv[1] if len(sys.argv) > 1 else '../balkans'
A = pickle.load(open('assign.pkl', 'rb')); G = pickle.load(open('regions.pkl', 'rb')); ALT = pickle.load(open('alts.pkl', 'rb'))
F = pickle.load(open('faces.pkl', 'rb'))
d = json.load(open('europe-borders-sources.json')); R = {**d['rels'], **d['rels4']}
K, YEARS = A['KEYS'], A['YEARS']; NY = len(YEARS)
regions, sigs, labels = G['regions'], G['sigs'], G['labels']
fills = json.load(open(sys.argv[2] if len(sys.argv) > 2 else '../node/fills.json'))

# ---------- neighbors ----------
geoms = [g for g, s in regions]
tree = STRtree(geoms)
fam = lambda u: UNITS[K[u]][2]
adj = defaultdict(float)
sig_u = np.array([s[0] for s in sigs])
for i, g in enumerate(geoms):
    for j in tree.query(g):
        if j <= i: continue
        inter = g.boundary.intersection(geoms[j].boundary)
        L = inter.length
        if L <= 0: continue
        ui, uj = sig_u[regions[i][1]], sig_u[regions[j][1]]
        for a, b in set(zip(ui.tolist(), uj.tolist())):
            if a >= 0 and b >= 0 and fam(a) != fam(b):
                adj[tuple(sorted((fam(a), fam(b))))] += L
print('neighbor pairs', len(adj), round(time.time() - t0), 's')

# ---------- coloring ----------
NC = len(fills['names'])
def ok(i, j, nv_min, cvd_min):
    return all(fills[m]['nv'][i][j] >= nv_min and fills[m]['cvd'][i][j] >= cvd_min for m in ('light', 'dark'))
PREF = {'FRA': 'blue-2', 'GBR': 'red-2', 'RUS': 'green-1', 'AUT': 'yellow-1', 'PRU': 'violet-1', 'OTT': 'aqua-1',
        'ESP': 'orange-1', 'SWE': 'blue-1', 'DEN': 'magenta-1', 'SAR': 'green-2', 'NAP': 'orange-2', 'PAP': 'yellow-2',
        'GRE': 'blue-1', 'NLD': 'orange-1', 'BAV': 'blue-1', 'SAX': 'green-1', 'POR': 'violet-1', 'SUI': 'red-1'}
fams = sorted({f for p in adj for f in p} | {UNITS[k][2] for k in K})
nb = defaultdict(dict)
for (a, b), L in adj.items(): nb[a][b] = L; nb[b][a] = L
names = fills['names']; NI = {n: i for i, n in enumerate(names)}

def sep(i, j):
    """Separation of two fills, 1.0 = meets the chart targets (normal-vision 15, colorblind 8) in both modes."""
    if i == j: return 0.0
    return min(min(fills[m]['nv'][i][j] / 15, fills[m]['cvd'][i][j] / 8) for m in ('light', 'dark'))

def color_all():
    """Greedy coloring, most-constrained country first. Each country takes the fill that is
    most distinct from its already-colored neighbors, weighting long shared borders more."""
    col = {}
    left = set(fams)
    while left:
        f = max(left, key=lambda f: (f in PREF, len({col[g] for g in nb[f] if g in col}), sum(nb[f].values())))
        left.discard(f)
        best, best_score = None, None
        for c in range(NC):
            worst = min([sep(c, col[g]) + (0.15 if nb[f][g] < 60 else 0) for g in nb[f] if g in col] or [9])
            score = (min(worst, 1.0), c == NI.get(PREF.get(f, ''), -1), worst, -sum(1 for v in col.values() if v == c))
            if best_score is None or score > best_score: best, best_score = c, score
        col[f] = best
    return col

col = color_all()
worst = sorted(((sep(col[a], col[b]), a, b, round(L)) for (a, b), L in adj.items()))[:15]
print('weakest neighbor pairs (1.0 = meets targets):', [(round(w, 2), a, b, L) for w, a, b, L in worst])

# ---------- projection ----------
tr = Transformer.from_crs(4326, 3035, always_xy=True)
def proj(g):
    return shapely.transform(g, lambda c: np.column_stack([v / 1000 for v in tr.transform(c[:, 0], c[:, 1])]) * [1, -1])
VIEW = box(-25.5, 34.4, 49.5, 71.8)

def feat(g, props):
    return {'type': 'Feature', 'properties': props, 'geometry': mapping(g)}

# ---------- references and histories ----------
refs, ref_i = [], {}
def ref_id(src, r):
    key = (src, int(r))
    if key in ref_i: return ref_i[key]
    if src in (0, 3):
        t = R[str(int(r))]['t']
        o = {'t': 'ohm' if src == 0 else 'bridge', 'id': int(r), 'n': t.get('n'), 's': t['s'], 'e': t['e'], 'l': t['l']}
    elif src == 1:
        p = F['cs'][int(r)]; o = {'t': 'cs', 'n': p['Name'], 's': p['From'], 'e': p['To'], 'st': p['Status']}
    elif src == 2:
        p = F['cl'][int(r)]; o = {'t': 'clio', 'n': p['Name'], 's': p['FromYear'], 'e': p['ToYear']}
    else:
        fx = A['FIX'][src - len(A['SRC'])]; o = {'t': 'fix', 'id': fx['id'], 'note': fx['note'], 'ev': fx['ev']}
    ref_i[key] = len(refs); refs.append(o)
    return ref_i[key]

used_units = sorted({int(u) for s in sigs for u in s[0] if u >= 0} | {K.index(a[k]) for a in ALT for k in ('def_u', 'alt_u')})
UI = {u: i for i, u in enumerate(used_units)}
hist = []
for u, src, r in sigs:
    runs, prev = [], None
    for j, y in enumerate(YEARS):
        cur = (UI[int(u[j])] if u[j] >= 0 else -1, ref_id(int(src[j]), r[j]) if u[j] >= 0 else -1)
        if cur != prev: runs.append([y, *cur]); prev = cur
    hist.append(runs)

# ---------- geometry ----------
gfeats = []
for g, s in regions:
    if not g.intersects(VIEW): continue
    gfeats.append(feat(proj(g.intersection(VIEW) if not g.within(VIEW) else g), {'s': s}))
afeats, alts = [], []
for a in sorted(ALT, key=lambda a: (a['y0'], -a['km2'])):
    if not a['geom'].intersects(VIEW): continue
    g = proj(a['geom'].intersection(VIEW))
    pt = polylabel(max(shapely.get_parts(shapely.make_valid(g)), key=lambda p: p.area if p.geom_type == 'Polygon' else 0), tolerance=2)
    fl = np.array(sorted(a['faces'])); j0 = YEARS.index(a['y0'])
    srcs = A['def_src'][fl, j0]; top_src = int(np.bincount(srcs).argmax())
    refv = {0: A['ohm_rec'], 1: A['cs_rec'], 2: A['cl_rec'], 3: A['ohm_rec']}.get(top_src)
    rr = int(np.bincount(refv[fl, j0][srcs == top_src]).argmax()) if refv is not None else top_src
    alts.append({'r': ref_id(top_src, rr), 'src': a['src'], 'd': UI[K.index(a['def_u'])], 'a': UI[K.index(a['alt_u'])], 'ds': a['def_sov'], 'as': a['alt_sov'],
                 'y0': a['y0'], 'y1': a['y1'], 'km2': a['km2'], 'x': round(pt.x, 1), 'y': round(pt.y, 1)})
    afeats.append(feat(g, {'i': len(alts) - 1}))
lakes = [f for f in json.load(open(f'{BAL}/ne_50m_lakes.geojson'))['features'] if (f['properties'].get('scalerank') or 0) <= 4]
lfeats = [feat(proj(shapely.make_valid(shape(f['geometry'])).intersection(VIEW)), {}) for f in lakes if shape(f['geometry']).intersects(VIEW)]
rivers = [f for f in json.load(open(f'{BAL}/ne_50m_rivers_lake_centerlines.geojson'))['features'] if (f['properties'].get('scalerank') or 9) <= 5]
rfeats = [feat(proj(shape(f['geometry']).intersection(VIEW)), {}) for f in rivers if shape(f['geometry']).intersects(VIEW)]
lfeats = [f for f in lfeats if f['geometry']['coordinates']]; rfeats = [f for f in rfeats if f['geometry']['coordinates']]
# graticule every 10 degrees, plus the edge of the mapped area
from shapely.geometry import LineString
grat = [LineString([(lon, la / 10) for la in range(344, 719)]) for lon in range(-20, 50, 10)]
grat += [LineString([(lo / 10, lat) for lo in range(-255, 496)]) for lat in range(40, 71, 10)]
gratf = [feat(proj(g), {}) for g in grat]
edgef = [feat(proj(shapely.segmentize(VIEW, 0.1).boundary), {})]
json.dump({'grat': {'type': 'FeatureCollection', 'features': gratf}, 'edge': {'type': 'FeatureCollection', 'features': edgef},
           'regions': {'type': 'FeatureCollection', 'features': gfeats}, 'alts': {'type': 'FeatureCollection', 'features': afeats},
           'lakes': {'type': 'FeatureCollection', 'features': lfeats}, 'rivers': {'type': 'FeatureCollection', 'features': rfeats}},
          open('geo.json', 'w'))
vb = proj(VIEW).bounds

# ---------- labels ----------
SHORT = {'United Kingdom of Great Britain and Ireland': 'United Kingdom', 'Kingdom of Great Britain': 'Great Britain',
         'Kingdom of the Two Sicilies': 'Two Sicilies', 'French Republic': 'France', 'French Republic (Empire)': 'French Empire',
         'Second French Empire': 'France', 'Kingdom of France': 'France', 'German Reich': 'German Empire', 'Duchy of Warsaw': 'Duchy of Warsaw',
         'United Romanian Principalities': 'Romania', 'Kingdom of Romania': 'Romania', 'Sweden–Norway': 'Sweden',
         'Denmark–Norway': 'Denmark–Norway', 'Grand Duchy of Finland': 'Finland', 'Kingdom of Poland': 'Kingdom of Poland',
         'Free and Hanseatic City of Hamburg': 'Hamburg', 'Free and Hanseatic City of Lübeck': 'Lübeck', 'Free City of Cracow': 'Kraków',
         'Prince-Bishopric of Montenegro': 'Montenegro', 'Principality of Montenegro': 'Montenegro', 'United States of the Ionian Islands': 'Ionian Islands',
         'Kingdom of Italy': 'Kingdom of Italy', 'Kingdom of Holland': 'Holland', 'Batavian Republic': 'Batavian Republic',
         'Batavian Commonwealth': 'Batavian Republic', 'Kingdom of the Netherlands': 'Netherlands', 'Holy Roman Empire': 'Holy Roman Empire',
         'Russian Empire': 'Russian Empire', 'Austrian Empire': 'Austrian Empire', 'Ottoman Empire': 'Ottoman Empire',
         'Kingdom of Portugal': 'Portugal', 'Electorate of Hesse': 'Hesse-Kassel', 'Grand Duchy of Hesse': 'Hesse-Darmstadt', 'Hesse': 'Hesse-Darmstadt',
         'Frankfur': 'Frankfurt', 'Dictatorship of Garibaldi': "Garibaldi's Sicily", 'Cyprus Protectorate': 'Cyprus',
         'French protectorate of Tunisia': 'Tunisia', 'Alawi Sultanate': 'Morocco', 'Regency of Algiers': 'Algiers', 'Qajar Iran': 'Persia',
         'Kingdom of Kartli-Kakheti': 'Kartli-Kakheti', 'North German Confederation': 'North German Confederation', 'Cretan State': 'Crete'}
def short(n, unit):
    if not n: return UNITS[unit][0]
    if n in SHORT: return SHORT[n]
    m = re.match(r'^(Kingdom|Grand Duchy|Duchy|Principality|Electorate|Margraviate|Republic|Free City|Prince-Bishopric) of (.+)$', n)
    if m and len(m.group(2)) <= 16 and m.group(1) not in ('Republic',): return m.group(2)
    return n
# countries whose smaller OHM records are provinces, not the country itself
PIECES = {'AUT', 'DEN', 'NLD', 'GER', 'PRU', 'HRE', 'SAX', 'HAN', 'HKA', 'BAD', 'HDA', 'MKS', 'MKST', 'OLD', 'BRU', 'SAL', 'SWE', 'GBR', 'FRA', 'RUS', 'OTT', 'PAP', 'NAP'}
names_l, name_i = [], {}
def nid(s):
    if s not in name_i: name_i[s] = len(names_l); names_l.append(s)
    return name_i[s]
lab = {}
for y, rows in labels.items():
    out = []
    for unit, x, yy, area, varea, (src, r) in rows:
        if unit not in [K[u] for u in used_units]: continue
        o = refs[ref_id(src, r)] if src in (0, 3) else None
        if o and (o['l'] == '2' or unit not in PIECES): name = short(o['n'], unit)
        elif unit == 'AUT': name = 'Habsburg Monarchy' if y < 1804 else 'Austrian Empire' if y < 1867 else 'Austria-Hungary'
        else: name = UNITS[unit][0]
        if unit == 'SHC': name = 'Schleswig-Holstein'
        out.append([UI[K.index(unit)], round(x / 1000, 1), round(-yy / 1000, 1), round(area), round(varea), nid(name)])
    lab[y] = out

units_out = []
for u in used_units:
    k = K[u]; name, ov, fa = UNITS[k]
    units_out.append({'k': k, 'n': name, 'ov': UI.get(K.index(ov)) if ov and K.index(ov) in UI else None, 'c': col.get(fa, 0)})
hb = proj(shapely.segmentize(box(-24.5, 35.2, 40.5, 71.3), 0.5)).bounds
data = {'years': [YEARS[0], YEARS[-1]], 'viewBox': [round(vb[0]), round(vb[1]), round(vb[2] - vb[0]), round(vb[3] - vb[1])],
        'home': [round(hb[0]), round(hb[1]), round(hb[2] - hb[0]), round(hb[3] - hb[1])],
        'units': units_out, 'fills': {m: fills[m]['P'] for m in ('light', 'dark')}, 'hist': hist, 'refs': refs,
        'labels': lab, 'names': names_l, 'alts': alts}
json.dump(data, open('data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('regions', len(gfeats), 'alts', len(alts), 'refs', len(refs), 'units', len(units_out), round(time.time() - t0), 's')
bad = [(a, b, names[col[a]], names[col[b]]) for (a, b) in adj if col[a] == col[b]]
print('same-color neighbors:', bad[:10])
