"""Step 4: find alternative borders - places where another source puts an area in a
different country than the map does, for longer than a year and over a real area
(not a sliver from two sources drawing the same border slightly differently).

Compared at the level of who held sovereignty, so a self-governing territory and its
overlord count as the same (sources differ on whether such territories are shown).

Output: alts.pkl  (list of alternative regions with years, sources and geometry)
"""
import pickle, sys, time
import numpy as np
import shapely
from shapely.ops import unary_union
from pyproj import Transformer
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from units import UNITS, sovereign, KIND

MIN_KM2 = 400        # smallest alternative region shown
ERODE_M = 3000       # must still exist after shrinking by 3 km (so at least ~6 km wide)
t0 = time.time()
A = pickle.load(open('assign.pkl', 'rb')); F = pickle.load(open('faces.pkl', 'rb'))
K, YEARS = A['KEYS'], A['YEARS']; NY = len(YEARS); KI = {k: i for i, k in enumerate(K)}
faces, land, farea = F['faces'], F['land'], A['farea']
NONE = -1
SOV = np.full((len(K) + 1, NY), NONE, np.int16)          # last row = no holder
for i, k in enumerate(K):
    for j, y in enumerate(YEARS): SOV[i, j] = KI[sovereign(k, y)]
sov = lambda U: SOV[U, np.arange(NY)[None, :]]
d_s = sov(A['def_u'])
IS_OCC = np.array([k in KIND for k in K] + [False])
OCC_SOV = np.full((len(K) + 1, NY), NONE, np.int16)
for k in KIND:
    for j, y in enumerate(YEARS): OCC_SOV[KI[k], j] = KI[sovereign(UNITS[k][1], y)]
EDGE = ['GEO', 'AZE', 'ARM', 'MRNC', 'UKR', 'BLR', 'GEO_S', 'AZE_S', 'ARM_S', 'UKR_S', 'BLR_S', 'TSF', 'WHT', 'EST', 'LVA', 'LTU']
GERMAN = {KI[k] for k in ['SAX', 'MKS', 'MKST', 'OLD', 'BRU', 'HKA', 'HDA', 'NAS', 'HAN', 'ANH', 'LIP', 'SCH', 'WALD', 'REU', 'SWB',
                          'SXW', 'SXA', 'SXC', 'SXM', 'HAM', 'BRE', 'LUB', 'FRK', 'HHO', 'BAV', 'WUR', 'BAD']}
YA = np.array(YEARS)[None, :]

def conflicts(alt_u, yr_ok):
    a_s = sov(alt_u)
    c = land[:, None] & yr_ok & (alt_u != NONE) & (A['def_u'] != NONE) & (a_s != d_s)
    # the German states in 1867-70 (COW counts them independent until 1871; OHM has the North German Confederation)
    c &= ~((YA >= 1867) & (YA <= 1870) & (d_s == KI['PRU']) & np.isin(alt_u, list(GERMAN)))
    # CShapes folds Hanover into the UK while they shared a king (to 1837)
    c &= ~((YA <= 1837) & (A['def_u'] == KI['HAN']) & (a_s == KI['GBR']))
    # occupations: the crosshatch already shows both the occupier and the country that held the land in law, so a source
    # that shows the occupier, or (during the world wars) a different prewar owner, is not a further alternative
    du = A['def_u']
    c &= ~(IS_OCC[du] & (((YA >= 1914) & (YA <= 1945)) | (a_s == OCC_SOV[du, np.arange(NY)[None, :]])))
    # CShapes follows the Correlates of War list, which leaves out the states of 1918-21 on Russia's edges and counts
    # Iceland as Danish until 1944; and it shows the Habsburg successor states for all of 1918
    c &= ~((YA >= 1918) & (YA <= 1921) & np.isin(du, [KI[k] for k in EDGE]) & (a_s == KI['RUS']))
    c &= ~((d_s == KI['ISL']) & (a_s == KI['DEN']))
    c &= ~((YA == 1918) & (d_s == KI['AUT']))
    # timing: a one-year disagreement where the other source matches the map a year earlier or later
    sh = lambda M, k: np.concatenate([M[:, :1]] * k + [M[:, :-k]], 1) if k > 0 else np.concatenate([M[:, -k:]] + [M[:, -1:]] * -k, 1)
    cp = np.concatenate([np.zeros_like(c[:, :1]), c[:, :-1]], 1); cn = np.concatenate([c[:, 1:], np.zeros_like(c[:, :1])], 1)
    single = c & ~cp & ~cn
    timing = single & ((a_s == sh(d_s, 1)) | (a_s == sh(d_s, -1)) | (d_s == sh(a_s, 1)) | (d_s == sh(a_s, -1)))
    return c & ~timing, a_s

yr = YA + 0 * A['def_u']
cs_c, cs_s = conflicts(A['cs_u'], yr >= 1816)
cl_c, cl_s = conflicts(A['cl_u'], yr <= 1815)
# Cliopatria is coarse and groups states into umbrellas; only compare against real states
cl_c &= ~np.isin(A['cl_u'], [KI['RHC'], KI['HRE']]) & (A['def_u'] != KI['HRE'])
# where the map overrode OHM with a correction, OHM itself is the alternative
ohm_c, ohm_s = conflicts(np.where(A['ohm_pri'] >= 2, A['ohm_u'], NONE), (A['def_src'] >= 4))
print('conflict face-years: cshapes', int(cs_c.sum()), 'cliopatria', int(cl_c.sum()), 'ohm', int(ohm_c.sum()))

tr = Transformer.from_crs(4326, 3035, always_xy=True)
proj = lambda g: shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))
cache = {}
cl_mode = False
def regions(idx):
    """Connected pieces of a set of faces that are big and wide enough."""
    key = (cl_mode, idx.tobytes())
    if key in cache: return cache[key]
    g = unary_union([faces[i] for i in idx])
    out = []
    for part in shapely.get_parts(g):
        pp = proj(part)
        if pp.area / 1e6 < MIN_KM2 * (12 if cl_mode else 1) or pp.buffer(-ERODE_M * (2 if cl_mode else 1)).is_empty: continue
        pidx = idx[shapely.contains_xy(part.buffer(1e-7), F['pts'][idx, 0], F['pts'][idx, 1])]
        out.append((part, pidx, pp.area / 1e6))
    cache[key] = out
    return out

found = {}        # (src, def_sov, alt_sov, alt_unit, frozenset faces) -> years
for src, C, S, U in [('cshapes', cs_c, cs_s, A['cs_u']), ('cliopatria', cl_c, cl_s, A['cl_u']), ('ohm', ohm_c, ohm_s, A['ohm_u'])]:
    cl_mode = src == 'cliopatria'
    for j, y in enumerate(YEARS):
        f = np.where(C[:, j])[0]
        if not len(f): continue
        pairs = np.stack([d_s[f, j], S[f, j]], 1)
        for ds, as_ in np.unique(pairs, axis=0):
            idx = f[(pairs[:, 0] == ds) & (pairs[:, 1] == as_)]
            for part, pidx, km2 in regions(idx):
                au = np.bincount(U[pidx, j], minlength=len(K)).argmax()
                du = np.bincount(A['def_u'][pidx, j], minlength=len(K)).argmax()
                key = (src, int(ds), int(as_), frozenset(pidx.tolist()))
                found.setdefault(key, {'years': [], 'geom': part, 'km2': km2, 'alt_u': int(au), 'def_u': int(du)})['years'].append(y)
print('alternative regions', len(found), round(time.time() - t0), 's')

# merge entries that are the same pair and overlap heavily in consecutive years
alts = []
for (src, ds, as_, fs), v in sorted(found.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[1]['years'][0])):
    ys = v['years']
    # split into runs of consecutive years
    runs = [[ys[0], ys[0]]]
    for y in ys[1:]:
        if y == runs[-1][1] + 1: runs[-1][1] = y
        else: runs.append([y, y])
    for a, b in runs:
        alts.append({'src': src, 'def_sov': K[ds], 'alt_sov': K[as_], 'def_u': K[v['def_u']], 'alt_u': K[v['alt_u']],
                     'y0': a, 'y1': b, 'km2': round(v['km2']), 'geom': v['geom'], 'faces': fs})
# join runs of the same pair that follow each other and cover nearly the same area (80% of the larger)
alts.sort(key=lambda a: (a['src'], a['def_sov'], a['alt_sov'], a['y0']))
merged = []
for a in alts:
    for m in merged:
        if (m['src'], m['def_sov'], m['alt_sov']) == (a['src'], a['def_sov'], a['alt_sov']) and a['y0'] == m['y1'] + 1:
            inter = len(m['faces'] & a['faces'])
            if inter >= 0.8 * max(len(m['faces']), len(a['faces'])):
                m['y1'] = a['y1']; m['faces'] = m['faces'] | a['faces']; m['geom'] = unary_union([m['geom'], a['geom']])
                m['km2'] = max(m['km2'], a['km2']); break
    else:
        merged.append(dict(a))
print('after merging', len(merged))
from collections import Counter
print(Counter((m['src'], m['def_sov'], m['alt_sov']) for m in merged).most_common(40))
pickle.dump(merged, open('alts.pkl', 'wb'))
