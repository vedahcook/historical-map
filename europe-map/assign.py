"""Step 3: for every face and every year (July 1, 1800-1900), decide who held it.

The map shows OpenHistoricalMap (OHM) by default. It falls back to CShapes-Europe (from
1816) or Cliopatria where OHM has no record, and applies a short list of corrections
where our checks found OHM wrong. Every other source's answer is kept, so places where
a source disagrees can be flagged as alternative borders.

Output: assign.pkl
"""
import json, pickle, sys, time
import numpy as np
import shapely
from pyproj import Transformer
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from units import UNITS, ohm_roles, cs_unit, clio_unit, sovereign

Y0, Y1 = 1800, 1900
YEARS = list(range(Y0, Y1 + 1)); NY = len(YEARS)
t0 = time.time()
d = json.load(open('europe-borders-sources.json'))
R = {**d['rels'], **d['rels4']}
P = pickle.load(open('rel_polys.pkl', 'rb'))
F = pickle.load(open('faces.pkl', 'rb'))
faces, pts, is_land = F['faces'], F['pts'], F['land']
NF = len(faces)
tr = Transformer.from_crs(4326, 3035, always_xy=True)
proj = lambda g: shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))
farea = shapely.area(proj(np.array(faces, dtype=object))) / 1e6          # km²

KEYS = sorted(UNITS); KI = {k: i for i, k in enumerate(KEYS)}; NONE = -1

def active(s, e, y):
    """Is a record in force on July 1 of year y? A year-only or month-only end date
    ("1864", "1860-10") is read as the end of that year or month, so that records ending
    and starting within the same year don't leave a gap."""
    t = f'{y}-07-01'
    e = e or '9999'
    if len(e) == 4: e += '-12-31'
    elif len(e) == 7: e += '-31'
    return (s or '0000') <= t <= e

# ---------- OHM: best record per face and year ----------
ohm_u = np.full((NF, NY), NONE, np.int16); ohm_pri = np.zeros((NF, NY), np.int8)
ohm_area = np.full((NF, NY), np.inf); ohm_rec = np.zeros((NF, NY), np.int64); ohm_lvl = np.full((NF, NY), 9, np.int8)
for rid, idx in F['in_ohm'].items():
    if not len(idx): continue
    t = R[rid]['t']; roles = ohm_roles(t.get('n'), t['l'])
    area = shapely.area(proj(P[rid])) / 1e6
    for j, y in enumerate(YEARS):
        if not active(t['s'], t['e'], y): continue
        role = next(((u, p) for u, p, a, b in roles if a <= y <= b), None)
        if not role or role[0] is None: continue
        u, p = role
        # higher priority wins; then the country-level record over its provinces; then the smaller record
        lv = int(t['l'])
        better = (p > ohm_pri[idx, j]) | ((p == ohm_pri[idx, j]) & ((lv < ohm_lvl[idx, j]) | ((lv == ohm_lvl[idx, j]) & (area < ohm_area[idx, j]))))
        k = idx[better]
        ohm_u[k, j] = KI[u]; ohm_pri[k, j] = p; ohm_area[k, j] = area; ohm_rec[k, j] = int(rid); ohm_lvl[k, j] = lv
print('ohm done', round(time.time() - t0), 's')

# ---------- CShapes and Cliopatria ----------
def fill_source(props, members, unit_of, yr):
    u = np.full((NF, NY), NONE, np.int16); ar = np.full((NF, NY), np.inf); rec = np.full((NF, NY), -1, np.int32)
    for i, (p, idx) in enumerate(zip(props, members)):
        if not len(idx): continue
        a0, a1 = yr(p)
        for j, y in enumerate(YEARS):
            if not (a0 <= y <= a1): continue
            k = unit_of(p, y)
            if k is None: continue
            area = p.get('Area') or 0
            better = area < ar[idx, j]; kk = idx[better]
            u[kk, j] = KI[k]; ar[kk, j] = area; rec[kk, j] = i
    return u, rec

cs_u, cs_rec = fill_source(F['cs'], F['in_cs'], lambda p, y: cs_unit(p['Name'], p['Status'], y) if y >= 1816 else None,
                           lambda p: (p['From'], p['To']))
cl_u, cl_rec = fill_source(F['cl'], F['in_cl'], lambda p, y: clio_unit(p['Name']), lambda p: (p['FromYear'], p['ToYear']))
print('cshapes/clio done', round(time.time() - t0), 's')

# ---------- the map's answer ----------
SRC = ['ohm', 'cshapes', 'cliopatria', 'ohm-bridged']            # + corrections, indexed from 4
def_u = ohm_u.copy(); def_src = np.zeros((NF, NY), np.int8)
YA = np.array(YEARS)[None, :]
# A gap of one or two years in OHM with the same country on both sides is bridged.
bridged = np.zeros((NF, NY), bool)
for j in range(1, NY - 1):
    for w in (1, 2):
        if j + w >= NY: continue
        before, after = def_u[:, j - 1], def_u[:, j + w]
        hole = (before != NONE) & (before == after) & np.all(def_u[:, j:j + w] == NONE, axis=1)
        for k in range(j, j + w): def_u[hole, k] = before[hole]; bridged[hole, k] = True
ohm_pri[bridged] = 2
def_src[bridged] = 3
# Where OHM has no country, or only the Holy Roman Empire umbrella, use CShapes (1816+) then Cliopatria.
gap = (def_u == NONE) | (ohm_pri == 1)
use_cs = gap & (cs_u != NONE) & (YA >= 1816)
def_u[use_cs] = cs_u[use_cs]; def_src[use_cs] = 1
use_cl = gap & ~use_cs & (cl_u != NONE) & ((ohm_pri == 0) | (cl_u != KI['HRE']))
def_u[use_cl] = cl_u[use_cl]; def_src[use_cl] = 2

# ---------- corrections ----------
# Each: id, note shown on the map, sources, and a function returning a boolean mask (NF x NY) and the unit.
x, y = pts[:, 0][:, None], pts[:, 1][:, None]
def rec_mask(names_dates):
    m = np.zeros(NF, bool)
    for rid, r in R.items():
        if rid in P and any((r['t'].get('n') == n and r['t']['s'].startswith(s)) for n, s in names_dates):
            m |= shapely.contains_xy(P[rid], pts[:, 0], pts[:, 1])
    return m[:, None]

FIX = []
def fix(fid, unit, mask, note, ev):
    mask = mask & is_land[:, None]
    FIX.append({'id': fid, 'unit': unit, 'note': note, 'ev': ev, 'n': int(mask.sum())})
    k = len(SRC) + len(FIX) - 1
    def_u[mask] = KI[unit]; def_src[mask] = k

fix('caucasus-1801', 'RUS', (x > 38) & (x < 50) & (y > 38.5) & (y < 44.5) & (YA >= 1802) & (YA <= 1813) & (def_u == KI['PER']) & (cl_u == KI['RUS']),
    'OHM keeps eastern Georgia and the khanates north of the Aras River under Persia until the Treaty of Gulistan (1813). Russia annexed Kartli-Kakheti in 1801 and took most of the khanates in 1804-06; the treaty confirmed this. For these years the map uses Cliopatria\u2019s outline.',
    [['Russian annexation of Georgia', 'https://en.wikipedia.org/wiki/Annexation_of_the_Kingdom_of_Kartli-Kakheti_by_the_Russian_Empire'], ['Treaty of Gulistan (1813)', 'https://en.wikipedia.org/wiki/Treaty_of_Gulistan']])
fix('bulgaria-1885', 'BUL', rec_mask([('Bulgaria', '1878'), ('Eastern Rumelia', '1878')]) & (YA >= 1886) & (def_u == KI['OTT']),
    'OHM has no record of Bulgaria after it united with Eastern Rumelia in September 1885, so this area shows as plain Ottoman there. The map shows the united, self-governing principality, which stayed under Ottoman overlordship until 1908.',
    [['Unification of Bulgaria (1885)', 'https://en.wikipedia.org/wiki/Bulgarian_unification']])
fix('ulcinj-1880', 'OTT', (x > 19.05) & (x < 19.45) & (y > 41.75) & (y < 42.05) & (YA >= 1878) & (YA <= 1880) & (def_u == KI['MNE']),
    'OHM makes Ulcinj Montenegrin from the Treaty of Berlin (1878). It was handed over only in November 1880, after a naval demonstration by the powers.',
    [['Ulcinj: transfer to Montenegro (1880)', 'https://en.wikipedia.org/wiki/Ulcinj#History']])
fix('thessaly-1881', 'GRE', (x > 20.6) & (x < 23.3) & (y > 38.8) & (y < 40.1) & (YA >= 1882) & (def_u == KI['OTT']) & (cs_u == KI['GRE']),
    'OHM leaves Arta and the Tyrnavos area Ottoman after 1881. Under the Convention of Constantinople (1881) they went to Greece with Thessaly; the map uses CShapes-Europe for this border.',
    [['Convention of Constantinople (1881)', 'https://en.wikipedia.org/wiki/Convention_of_Constantinople_(1881)']])
fix('greece-1830', 'GRE', (x > 19.5) & (x < 27) & (y > 35.8) & (y < 39.6) & (YA >= 1830) & (YA <= 1831) & (def_u == KI['OTT']) & (cs_u == KI['GRE']),
    'OHM starts Greece in 1832, when its borders were fixed. Greek independence was recognized in February 1830 (London Protocol); for 1830-31 the map uses CShapes-Europe’s border.',
    [['London Protocol (1830)', 'https://en.wikipedia.org/wiki/London_Protocol_(1830)']])
shc = rec_mask([('Duchy of Schleswig', '1773'), ('Duchy of Holstein', '1843'), ('Duchy of Saxe-Lauenburg', '1814')])
fix('schleswig-holstein', 'SHC', shc & (YA >= 1865) & (YA <= 1866) & (ohm_u == NONE),
    'OHM has no country here between Denmark’s surrender of the duchies (October 1864) and their annexation by Prussia (1866-67). They were under joint Austrian and Prussian rule.',
    [['Treaty of Vienna (1864)', 'https://en.wikipedia.org/wiki/Treaty_of_Vienna_(1864)'], ['Gastein Convention (1865)', 'https://en.wikipedia.org/wiki/Gastein_Convention']])
fix('moldavia-early', 'MOL', (YA <= 1811) & (def_u == KI['OTT']) & (cl_u[:, [0]] == KI['MOL']),
    'OHM’s records for self-governing Moldavia start in 1812. Before that the map uses Cliopatria’s outline of the principality as of 1800. Moldavia was under Ottoman overlordship and included Bessarabia until 1812; Russia occupied it during the war of 1806-12.',
    [['Principality of Moldavia', 'https://en.wikipedia.org/wiki/Moldavia']])
ion = (x > 19.3) & (x < 23.3) & (y > 35.9) & (y < 39.95) & (YA >= 1807) & (YA <= 1815) & (ohm_u == NONE)
ion_fr = ion & ((YA <= 1808) | ((y > 39.1) & (YA <= 1813)))
fix('ionian-french', 'FRA', ion_fr,
    'OHM has no record for the Ionian Islands between the end of the Septinsular Republic (1807) and the British protectorate (1815). France held them from 1807; Britain took most of the islands in 1809-10, but Corfu stayed French until 1814.',
    [['Ionian Islands under French rule', 'https://en.wikipedia.org/wiki/French_rule_in_the_Ionian_Islands_(1807%E2%80%931814)']])
fix('ionian-british', 'GBR', ion & ~ion_fr,
    'OHM has no record for the Ionian Islands between the end of the Septinsular Republic (1807) and the British protectorate (1815). Britain took most of the islands in 1809-10 and Corfu in 1814.',
    [['Ionian Islands under French rule', 'https://en.wikipedia.org/wiki/French_rule_in_the_Ionian_Islands_(1807%E2%80%931814)']])
fix('bosnia-1878', 'AUT_OCC', (x > 15.6) & (x < 19.8) & (y > 42.4) & (y < 45.3) & (YA >= 1879) & (def_u == KI['OTT']) & ((cs_u == KI['AUT']) | (cs_u == KI['AUT_OCC'])),
    'OHM keeps Bosnia and Herzegovina plain Ottoman after 1878. Under the Treaty of Berlin Austria-Hungary occupied and ran it, while it stayed Ottoman territory until the annexation of 1908, so the map shows it as Austrian-run (hatched). The outline comes from CShapes-Europe.',
    [['Treaty of Berlin (1878)', 'https://en.wikipedia.org/wiki/Treaty_of_Berlin_(1878)'], ['Bosnian crisis (1908)', 'https://en.wikipedia.org/wiki/Bosnian_crisis']])
print('corrections', [(f['id'], f['n']) for f in FIX])

# ---------- report gaps ----------
nodef = is_land[:, None] & (def_u == NONE)
print('land face-years with no holder:', int(nodef.sum()), 'area-years km2:', int((farea[:, None] * nodef).sum()))
big = np.argsort(-(farea * nodef.sum(1)))[:15]
for i in big:
    if nodef[i].any():
        ys = [YEARS[j] for j in np.where(nodef[i])[0]]
        print(f'  face {i} {farea[i]:.0f} km2 at {pts[i][0]:.2f},{pts[i][1]:.2f} years {ys[0]}-{ys[-1]} ({len(ys)})')

pickle.dump({'KEYS': KEYS, 'YEARS': YEARS, 'farea': farea, 'ohm_u': ohm_u, 'ohm_pri': ohm_pri, 'ohm_rec': ohm_rec,
             'cs_u': cs_u, 'cs_rec': cs_rec, 'cl_u': cl_u, 'cl_rec': cl_rec, 'def_u': def_u, 'def_src': def_src,
             'SRC': SRC, 'FIX': FIX}, open('assign.pkl', 'wb'))
print('saved', round(time.time() - t0), 's')
