"""Step 3: for every face and every year (July 1, 1800-2026), decide who held it.

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
from units import UNITS, ohm_roles, cs_unit, clio_unit, sovereign, KIND, CLIO_OCCUPIER, OCC_PAIRS, ANNEXERS

# ERA=early runs the 1500-1799 map, ERA=medieval the 1000-1499 map, each from its own sources
# (europe-borders-sources.json in that working folder)
ERA = __import__('os').environ.get('ERA')
EARLY, MEDIEVAL = ERA == 'early', ERA == 'medieval'
Y0, Y1 = (1000, 1499) if MEDIEVAL else (1500, 1799) if EARLY else (1800, 2026)
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
        lv = int(t['l']) if t['l'].isdigit() else 5
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
# (the medieval map applies Cliopatria's names year by year: its records span several years, and a state can end inside one)
cl_u, cl_rec = fill_source(F['cl'], F['in_cl'], lambda p, y: clio_unit(p['Name'], y if MEDIEVAL else p['FromYear']), lambda p: (p['FromYear'], p['ToYear']))
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
# Cliopatria keeps a Grand Duchy of Berg after 1813, when it no longer existed
use_cl &= ~((cl_u == KI['BERG']) & (YA > 1813))
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

def fix_multi(fid, U, note, ev):
    """Like fix(), but each face-year gets its own unit (U = unit index or NONE)."""
    mask = (U != NONE) & is_land[:, None]
    FIX.append({'id': fid, 'unit': None, 'note': note, 'ev': ev, 'n': int(mask.sum())})
    k = len(SRC) + len(FIX) - 1
    def_u[mask] = U[mask]; def_src[mask] = k

if not EARLY and not MEDIEVAL:
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
    fix('bosnia-1878', 'AUT_OCC', (x > 15.6) & (x < 19.8) & (y > 42.4) & (y < 45.3) & (YA >= 1879) & (YA <= 1908) & (def_u == KI['OTT']) & ((cs_u == KI['AUT']) | (cs_u == KI['AUT_OCC'])),
        'OHM keeps Bosnia and Herzegovina plain Ottoman after 1878. Under the Treaty of Berlin Austria-Hungary occupied and ran it, while it stayed Ottoman territory until the annexation of 1908, so the map shows it as Austrian-run (hatched). The outline comes from CShapes-Europe.',
        [['Treaty of Berlin (1878)', 'https://en.wikipedia.org/wiki/Treaty_of_Berlin_(1878)'], ['Bosnian crisis (1908)', 'https://en.wikipedia.org/wiki/Bosnian_crisis']])

    # ---------- 1900-2026 ----------
    FAMS = sorted({v[2] for v in UNITS.values()}); FI = {f: i for i, f in enumerate(FAMS)}
    fam = np.array([FI[UNITS[k][2]] for k in KEYS] + [-1])          # fam[NONE] = -1
    dependent = np.array([k in KIND or UNITS[k][1] is not None for k in KEYS] + [True])
    ppts = np.column_stack(tr.transform(pts[:, 0], pts[:, 1]))


    def solid(U, min_km2=1500, erode_m=5000):
        """Drop slivers: keep only faces inside pieces that survive shrinking by erode_m and are big enough.
        Two sources drawing the same border slightly differently would otherwise leave thin strips."""
        out = np.full_like(U, NONE)
        for j in range(NY):
            col = U[:, j]
            for u in np.unique(col[col != NONE]):
                idx = np.where(col == u)[0]
                g = proj(shapely.make_valid(shapely.union_all(np.array([faces[i] for i in idx], dtype=object))))
                o = g.buffer(-erode_m).buffer(erode_m)
                if o.is_empty: continue
                o = shapely.union_all([p for p in shapely.get_parts(o) if p.area / 1e6 >= min_km2]) if not o.is_empty else o
                if o.is_empty: continue
                keep = idx[shapely.contains_xy(o.buffer(erode_m * 0.2), ppts[idx, 0], ppts[idx, 1])]
                out[keep, j] = u
        return out

    def ext_mask(key):
        i = next(n for n, p in enumerate(F['ext']) if p['k'] == key)
        m = np.zeros(NF, bool); m[F['in_ext'][i]] = True
        return m[:, None]
    isin = lambda *ks: np.isin(def_u, [KI[k] for k in ks])

    # records and dates OHM has slightly off for July 1
    fix('germany-zones-1945', 'GER_US', rec_mask([('American occupation zone in Germany', '1945-08-01')]) & (YA == 1945),
        'OHM starts its record of the American occupation zone on August 1, 1945. The four zones were set up by the Berlin Declaration of June 5, 1945, and American troops held this area by July 1, so the map shows the zone in 1945 too.',
        [['Berlin Declaration (1945)', 'https://en.wikipedia.org/wiki/Berlin_Declaration_(1945)'], ['Allied-occupied Germany', 'https://en.wikipedia.org/wiki/Allied-occupied_Germany']])
    fix('iceland-1940', 'O_GBR_ISL', isin('ISL') & (YA >= 1940) & (YA <= 1941),
        'OHM shows Iceland as independent throughout the Second World War. British forces occupied it in May 1940, against the Icelandic government’s protest, to keep Germany out; in July 1941 the United States took over by agreement with Iceland.',
        [['British invasion of Iceland', 'https://en.wikipedia.org/wiki/Invasion_of_Iceland']])
    fix('iceland-1942', 'O_USA_ISL', isin('ISL') & (YA >= 1942) & (YA <= 1945),
        'OHM shows Iceland as independent throughout the Second World War. American forces held it from July 1941 until 1946, under an agreement with the Icelandic government that replaced the British occupation of 1940. CShapes-Europe also marks Iceland as occupied.',
        [['Iceland in World War II', 'https://en.wikipedia.org/wiki/Iceland_in_World_War_II']])
    fix('faroes-1940', 'O_GBR_DEN', (x > -7.9) & (x < -6.0) & (y > 61.3) & (y < 62.5) & isin('DEN') & (YA >= 1940) & (YA <= 1945),
        'OHM keeps the Faroe Islands Danish during the Second World War. Britain occupied them from April 1940, after Germany occupied Denmark, until September 1945.',
        [['British occupation of the Faroe Islands', 'https://en.wikipedia.org/wiki/British_occupation_of_the_Faroe_Islands']])
    fix('faroes-denmark', 'DEN', (x > -7.9) & (x < -6.0) & (y > 61.3) & (y < 62.5) & (def_u == NONE) & (YA >= 1944),
        'OHM’s later records of Denmark leave out the Faroe Islands. They have been a self-governing part of the Danish realm since 1948.',
        [['Faroe Islands', 'https://en.wikipedia.org/wiki/Faroe_Islands']])
    fix('channel-islands-1940', 'O_GER_GBR', (x > -2.8) & (x < -1.9) & (y > 49.1) & (y < 49.8) & isin('GBR') & (YA >= 1940) & (YA <= 1944),
        'OHM keeps the Channel Islands British throughout the Second World War. Germany occupied them from June 30, 1940 until May 9, 1945, the only British territory it took.',
        [['German occupation of the Channel Islands', 'https://en.wikipedia.org/wiki/German_occupation_of_the_Channel_Islands']])

    fix('denmark-1940', 'O_GER_DEN', (x > 7.5) & (x < 15.5) & (y > 54.4) & (y < 58.0) & isin('DEN') & (YA >= 1940) & (YA <= 1944),
        'OHM’s record of the German occupation of Denmark starts in August 1943, when Germany took direct control. Germany occupied Denmark on April 9, 1940 and stayed until May 1945, though it let the Danish government carry on until 1943.',
        [['Occupation of Denmark', 'https://en.wikipedia.org/wiki/Occupation_of_Denmark']])
    j39 = YEARS.index(1939)
    for c in ('EST', 'LVA', 'LTU'):
        fix('baltic-1940', 'O_RUS_' + c, (YA == 1940) & isin('RUS') & (def_u[:, [j39]] == KI[c]),
            'OHM moves the Baltic states into the Soviet Union from mid-June 1940. Soviet troops occupied them on June 15-17, 1940, but they were annexed only in August, after staged elections, so on July 1 the map shows them as occupied.',
            [['Occupation of the Baltic states', 'https://en.wikipedia.org/wiki/Occupation_of_the_Baltic_states']])
    # Italy, July 1, 1944: OHM keeps the whole north-centre under the Italian Social Republic, but the Allies held Rome (from June 4)
    # and everything south of a line near Lake Trasimeno; Cliopatria's German-held area for 1944 marks it
    nazi44 = np.zeros(NF, bool)
    for p, idx in zip(F['co'], F['in_co']):
        if p['Name'] == 'Nazi Germany' and p['FromYear'] <= 1944 <= p['ToYear']: nazi44[idx] = True
    fix('italy-1944', 'ITA', (YA == 1944) & isin('RSI', 'O_GER_ITA') & ~nazi44[:, None],
        'OHM draws the Italian Social Republic and the German occupation at their full extent of September 1943. By July 1, 1944 the Allies had taken Rome and the south up to a line near Lake Trasimeno, restoring it to the Kingdom of Italy; the map uses Cliopatria’s German-held area for 1944.',
        [['Italian campaign (World War II)', 'https://en.wikipedia.org/wiki/Italian_campaign_(World_War_II)']])

    fix('eastern-thrace-1922', 'TUR', (x > 25.9) & (x < 29.3) & (y > 40.0) & (y < 42.2) & (YA >= 1923) & (YA <= 1924) & isin('GRE') & (cs_u == KI['TUR']),
        'OHM keeps Eastern Thrace Greek until 1924. Greece had to hand it back to Turkey under the Armistice of Mudanya in October 1922, and the Treaty of Lausanne (1923) confirmed the border; the map uses CShapes-Europe here.',
        [['Armistice of Mudanya', 'https://en.wikipedia.org/wiki/Armistice_of_Mudanya'], ['Treaty of Lausanne', 'https://en.wikipedia.org/wiki/Treaty_of_Lausanne']])

    # occupations: Cliopatria's areas of control in 1914-46, for pairs that are documented occupations
    occ = np.full((NF, NY), NONE, np.int16)
    for p, idx in zip(F['co'], F['in_co']):
        a = CLIO_OCCUPIER[p['Name']]
        if not len(idx): continue
        for j, yy in enumerate(YEARS):
            if not (p['FromYear'] <= yy <= p['ToYear']) or not (1914 <= yy <= 1946): continue
            h = def_u[idx, j]
            for oa, ob, y0, y1 in OCC_PAIRS:
                if oa == a and y0 <= yy <= y1:
                    m = (h == KI[ob]) & (occ[idx, j] == NONE)
                    occ[idx[m], j] = KI['O_' + oa + '_' + ob]
    # Moldavia (north of the Siret front, from Galați to the Oituz pass) stayed under the Romanian government in 1917-18;
    # Cliopatria's Austria-Hungary covers it, but only Wallachia and Dobruja were occupied
    MOLD = shapely.Polygon([(25.0, 46.25), (26.4, 46.2), (27.23, 45.88), (28.05, 45.40), (28.4, 45.3), (28.4, 48.6), (25.0, 48.6)])
    mold = shapely.contains_xy(MOLD, pts[:, 0], pts[:, 1])
    for yy in (1917, 1918):
        j = YEARS.index(yy)
        occ[mold & np.isin(occ[:, j], [KI[k] for k in ('O_GER_ROM', 'O_AUT_ROM', 'O_BUL_I_ROM')]), j] = NONE
    # occupied Wallachia was run by a German-led military administration (Mackensen), though Cliopatria gives it to Austria-Hungary
    occ[occ == KI['O_AUT_ROM']] = KI['O_GER_ROM']
    occ = solid(occ)
    fix_multi('occupation', occ,
        'OHM records most occupations of the two world wars only where an occupying power set up a named administration. Where it shows the country that held the land in law, but Cliopatria puts the area under an occupying power that year, and the occupation is documented, the map shows it as occupied (crosshatched in the occupier’s color). Cliopatria’s outlines are coarse, so the edges of these areas are approximate.',
        [['Cliopatria (Seshat)', 'https://github.com/Seshat-Global-History-Databank/cliopatria'], ['Military occupations by Germany in WWI', 'https://en.wikipedia.org/wiki/Occupation_of_Belgium_during_World_War_I'], ['German-occupied Europe (WWII)', 'https://en.wikipedia.org/wiki/German-occupied_Europe']])

    # wartime annexations: land a power held only during the Second World War (not in 1937, not in 1948)
    j37, j48 = YEARS.index(1937), YEARS.index(1948)
    ann = np.full((NF, NY), NONE, np.int16)
    for j, yy in enumerate(YEARS):
        if not 1938 <= yy <= 1945: continue
        h, h37, h48 = def_u[:, j], def_u[:, j37], def_u[:, j48]
        cand = np.isin(h, [KI[a] for a in ANNEXERS]) & (h37 != NONE) & ~dependent[h37] & (fam[h] != fam[h37]) & (fam[h] != fam[h48])
        for a_i, b_i in set(zip(h[cand].tolist(), h37[cand].tolist())):
            key = 'A_' + KEYS[a_i] + '_' + KEYS[b_i]
            if key not in KI: key = 'O_' + KEYS[a_i] + '_' + KEYS[b_i]     # OHM counts some occupied land as part of the occupier
            if key not in KI: print('  no unit for wartime holding', KEYS[a_i], KEYS[b_i]); continue
            ann[cand & (h == a_i) & (h37 == b_i), j] = KI[key]
    ann = solid(ann)
    fix_multi('annexation', ann,
        'OHM shows land annexed during the Second World War as part of the annexing country. Where a country held land only during the war (not in 1937 and not after 1947), the map shows it as annexed (crosshatched), because the annexations were not recognized and were reversed after the war: for example the Sudetenland, Alsace-Lorraine, western Poland, northern Transylvania and parts of Yugoslavia and Greece.',
        [['Territorial changes of Germany', 'https://en.wikipedia.org/wiki/Territorial_changes_of_Germany'], ['Vienna Awards', 'https://en.wikipedia.org/wiki/Vienna_Awards']])

    fix('ukraine-1944', 'RUS', isin('RKU') & (YA == 1944) & (x > 25.2),
        'OHM’s record of the Reichskommissariat Ukraine runs until November 1944 with its full extent. By July 1, 1944 the Red Army had retaken almost all of it (Kyiv in November 1943, Rivne and Lutsk in February 1944); Germany held only the area around Kovel, in the far northwest.',
        [['Reichskommissariat Ukraine', 'https://en.wikipedia.org/wiki/Reichskommissariat_Ukraine'], ['Dnieper–Carpathian offensive', 'https://en.wikipedia.org/wiki/Dnieper%E2%80%93Carpathian_offensive']])
    # the Smyrna zone: Greek-run from May 1919 under Ottoman sovereignty; retaken by Turkish forces in September 1922
    smy = (x > 26.0) & (x < 29.5) & (y > 37.0) & (y < 39.6) & np.isin(def_u[:, YEARS.index(1918)], [KI['OTT']])[:, None]
    fix('smyrna-1919', 'O_GRE_OTT', smy & (YA == 1919) & (def_u[:, YEARS.index(1920)] == KI['O_GRE_OTT'])[:, None] & isin('OTT'),
        'OHM keeps Smyrna (İzmir) Ottoman on July 1, 1919. Greek troops landed there on May 15, 1919, with Allied approval, and ran the zone around it; the map shows the zone’s 1920 extent.',
        [['Occupation of Smyrna', 'https://en.wikipedia.org/wiki/Occupation_of_Smyrna']])
    fix('smyrna-1921', 'O_GRE_OTT', smy & (YA >= 1921) & (YA <= 1922) & isin('GRE'),
        'OHM makes the Smyrna zone part of Greece from the Treaty of Sèvres (August 1920). The treaty left it under Ottoman sovereignty with Greek administration, and it was never ratified, so the map keeps showing it as occupied until Turkish forces retook it in September 1922.',
        [['Occupation of Smyrna', 'https://en.wikipedia.org/wiki/Occupation_of_Smyrna'], ['Treaty of Sèvres', 'https://en.wikipedia.org/wiki/Treaty_of_S%C3%A8vres']])
    fix('smyrna-1923', 'TUR', smy & (YA >= 1923) & (YA <= 1924) & isin('GRE'),
        'OHM keeps the Smyrna zone Greek until 1924. Turkish forces retook İzmir in September 1922, and the Treaty of Lausanne (1923) confirmed it as Turkish.',
        [['Burning of Smyrna', 'https://en.wikipedia.org/wiki/Burning_of_Smyrna'], ['Treaty of Lausanne', 'https://en.wikipedia.org/wiki/Treaty_of_Lausanne']])
    tzone = (def_u[:, YEARS.index(1930)] == KI['TNG'])[:, None]
    fix('tangier-1912', 'TNG', tzone & (YA >= 1912) & (YA <= 1924),
        'OHM has no holder for Tangier between the protectorate treaties of 1912 and the start of the international zone in 1925. The treaties left Tangier out of both protectorates for a special regime, so the map shows the later zone’s outline.',
        [['Tangier International Zone', 'https://en.wikipedia.org/wiki/Tangier_International_Zone']])
    fix('tangier-1940', 'O_ESP_TNG', tzone & (YA == 1940),
        'OHM has no holder for Tangier during the Second World War. Spain occupied the international zone on June 14, 1940, and annexed it that November.',
        [['Spanish occupation of Tangier', 'https://en.wikipedia.org/wiki/Spanish_occupation_of_Tangier']])
    fix('tangier-1941', 'A_ESP_TNG', tzone & (YA >= 1941) & (YA <= 1945),
        'OHM has no holder for Tangier during the Second World War. Spain annexed the international zone in November 1940, unrecognized, and withdrew in October 1945.',
        [['Spanish occupation of Tangier', 'https://en.wikipedia.org/wiki/Spanish_occupation_of_Tangier']])
    j19 = YEARS.index(1919)
    fix('bessarabia-1918', 'ROM', (x > 26.5) & (x < 30.5) & (y > 45.2) & (y < 48.6) & (YA == 1918) & isin('RUS') & (def_u[:, j19] == KI['ROM'])[:, None],
        'OHM has no holder for Bessarabia on July 1, 1918, and CShapes-Europe keeps it Russian. Its assembly voted to join Romania in April 1918, and Romanian troops held it from early that year; the union was recognized by the Treaty of Paris of 1920 but never by Soviet Russia.',
        [['Union of Bessarabia with Romania', 'https://en.wikipedia.org/wiki/Union_of_Bessarabia_with_Romania']])

    # breakaway regions and occupied Ukraine (Natural Earth; DeepState)
    fix('transnistria', 'TRN', ext_mask('transnistria') & (YA >= 1992) & isin('MDA', 'RUS'),
        'OHM shows Transnistria as part of Moldova. Since the war of 1992 it has been run by a breakaway government backed by Russian troops and recognized by no UN member. The outline is Natural Earth’s.',
        [['Transnistria', 'https://en.wikipedia.org/wiki/Transnistria'], ['Natural Earth disputed areas', 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/']])
    fix('abkhazia', 'ABK', ext_mask('abkhazia') & (YA >= 1994) & isin('GEO'),
        'OHM shows Abkhazia as part of Georgia. A breakaway government has held it since the war of 1992-93, with Russian backing; Russia recognized it in 2008 and keeps troops there. The outline is Natural Earth’s.',
        [['Abkhazia', 'https://en.wikipedia.org/wiki/Abkhazia'], ['Natural Earth disputed areas', 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/']])
    fix('south-ossetia', 'SOS', ext_mask('south-ossetia') & (YA >= 1992) & isin('GEO'),
        'OHM shows South Ossetia as part of Georgia. A breakaway government has held most of it since the ceasefire of June 1992, and all of it since the Russian-Georgian war of 2008; Russia recognized it that year. The outline is Natural Earth’s (the extent after 2008).',
        [['South Ossetia', 'https://en.wikipedia.org/wiki/South_Ossetia'], ['Natural Earth disputed areas', 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/']])
    fix('artsakh', 'ART', ((ext_mask('artsakh-1994') & (YA >= 1994) & (YA <= 2020)) | (ext_mask('artsakh-2020') & (YA >= 2021) & (YA <= 2023))) & isin('AZE', 'ART', 'ARM'),
        'OHM’s record of the Republic of Artsakh covers the former Nagorno-Karabakh region, and continues after 2023. Armenian forces also held the surrounding districts from the 1994 ceasefire until the war of 2020; Azerbaijan retook the rest in September 2023, and the republic dissolved. The map uses Natural Earth’s outlines for 1994-2020 and 2020-23.',
        [['Republic of Artsakh', 'https://en.wikipedia.org/wiki/Republic_of_Artsakh'], ['Natural Earth disputed areas', 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/']])
    fix('crimea-2014', 'UKR_O', ext_mask('crimea') & (YA >= 2014) & (YA <= 2021) & isin('UKR', 'RUS', 'UKR_O'),
        'OHM shows Crimea as part of Russia from 2014. Russia seized and annexed it in February-March 2014; the UN General Assembly and most countries do not recognize the annexation, so the map shows it as occupied. The outline is Natural Earth’s.',
        [['Annexation of Crimea by Russia', 'https://en.wikipedia.org/wiki/Annexation_of_Crimea_by_the_Russian_Federation'], ['UN General Assembly Resolution 68/262', 'https://en.wikipedia.org/wiki/United_Nations_General_Assembly_Resolution_68/262']])
    fix('donbas-2014', 'DLR', (ext_mask('dpr') | ext_mask('lpr')) & (YA >= 2014) & (YA <= 2021) & isin('UKR', 'RUS'),
        'OHM shows this part of the Donbas as Ukrainian. From 2014 it was held by the Russian-backed Donetsk and Luhansk "people’s republics", with Russian forces. The outline is Natural Earth’s and shows the line after February 2015; in July 2014 the fighting line was still moving.',
        [['War in Donbas', 'https://en.wikipedia.org/wiki/War_in_Donbas'], ['Natural Earth disputed areas', 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/']])
    ukr = np.zeros((NF, NY), bool)
    for yy in range(2022, 2027):
        if yy in YEARS and any(p['k'] == f'ukraine-{yy}' for p in F['ext']):
            ukr |= ext_mask(f'ukraine-{yy}') & (YA == yy)
    fix('ukraine-2022', 'UKR_O', ukr & isin('UKR', 'RUS', 'UKR_O', 'DLR'),
        'OHM does not record the areas of Ukraine occupied by Russia since the invasion of February 2022. The map uses DeepState’s map of the front line as of July 1 each year (the last update before that date). It includes Crimea and the parts of the Donbas held since 2014. Russia claims to have annexed four Ukrainian regions in September 2022; the UN General Assembly rejected this.',
        [['DeepState map', 'https://deepstatemap.live/en'], ['Russian-occupied territories of Ukraine', 'https://en.wikipedia.org/wiki/Russian-occupied_territories_of_Ukraine']])

    # specks and remnants: after 1900, a country that holds under 30 km² in a year (other than Monaco, the Vatican and
    # Fiume), or under 3% of its largest extent (and under 5,000 km²), has only slivers left where two sources draw a
    # border slightly differently, or where a source is missing a year. Each piece goes to the neighbor it touches most.
    # (Austria is left out: after 1945 its remnant is Vienna, under four-power occupation.)
    MICRO = {KI[k] for k in ('MON', 'VAT', 'O_GER_MON', 'O_ITA_MON', 'FIU')}
    tree = shapely.STRtree(faces)
    spk = np.full((NF, NY), NONE, np.int16)
    umax = np.zeros(len(KEYS))
    for j in range(NY):
        c = def_u[:, j]; m = is_land & (c != NONE)
        umax = np.maximum(umax, np.bincount(c[m], weights=farea[m], minlength=len(KEYS)))
    nspk = []
    for j, yy in enumerate(YEARS):
        if yy < 1900: continue
        col = def_u[:, j]
        lm = is_land & (col != NONE)
        tot = np.bincount(col[lm], weights=farea[lm], minlength=len(KEYS))
        tiny = {int(u) for u in np.unique(col[is_land]) if u != NONE and u not in MICRO and (u != KI['AUT'] or yy < 1945)
                and (tot[u] < 30 or (tot[u] < 5000 and tot[u] < 0.03 * umax[u]))}
        for u in tiny:
            idx = np.where((col == u) & is_land)[0]
            for part in shapely.get_parts(shapely.union_all(np.array([faces[i] for i in idx], dtype=object)).buffer(1e-4)):
                pi = idx[shapely.contains_xy(part, pts[idx, 0], pts[idx, 1])]
                if not len(pi): continue
                near = tree.query(part.buffer(0.005), predicate='intersects')
                near = near[(col[near] != u) & (col[near] != NONE) & ~np.isin(col[near], list(tiny))]
                if not len(near): continue
                touch = shapely.area(shapely.intersection(np.array([faces[i] for i in near], dtype=object), part.buffer(0.005)))
                best = max(set(col[near].tolist()), key=lambda v: touch[col[near] == v].sum())
                spk[pi, j] = best; nspk.append((KEYS[u], yy, round(float(shapely.area(part)), 3), KEYS[best]))
    fix_multi('specks', spk,
        'Where two sources draw a border slightly differently, a country can be left with a sliver of a few square kilometers in a year when it held nothing there. The map gives each such sliver to the neighbor it touches most.', [])
    print('specks', len(nspk), sorted({(u, t, min(y for uu, y, a, tt in nspk if (uu, tt) == (u, t)), max(y for uu, y, a, tt in nspk if (uu, tt) == (u, t))) for u, y, a, t in nspk}))

    print('corrections', [(f['id'], f['n']) for f in FIX])

if EARLY:
    exec(open(__file__.rsplit('/', 1)[0] + '/assign15.py').read())
if MEDIEVAL:
    exec(open(__file__.rsplit('/', 1)[0] + '/assign10.py').read())

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
