"""Add Jan de Vries's city populations for 1500-1800 (European Urbanization, 1984, as tidied in the europop
dataset, CC0: europop_europop.csv, europop_city_coords.csv) to cities.txt, as source V.
- Cities already in the list (matched by position, within 12 km) get de Vries's figures for decades they have no
  figure for; a de Vries figure replaces an estimate from Wikipedia's table (C) in the same decade.
- Cities with at least 20,000 people at some point in 1500-1800 that are not in the list are added, with an English
  name. They have figures up to 1800 only, so the map shows them in the earlier centuries.
Figures are in thousands in the source; 0 and NA (below the book's threshold, or unknown) are left out.
Usage: python3 add_devries.py ../cities.txt"""
import csv, math, sys
from collections import defaultdict
CT = sys.argv[1]
ep = defaultdict(dict)
for r in csv.DictReader(open('europop_europop.csv', encoding='utf-8')):
    if r['population'] not in ('NA', '0'): ep[r['city']][int(r['year'])] = int(r['population']) * 1000
co = {r['city']: (float(r['lon']), float(r['lat'])) for r in csv.DictReader(open('europop_city_coords.csv', encoding='utf-8'))}
# places whose coordinates in the dataset are wrong (put in another city of the same name), and neighbors of a listed
# city that de Vries counts separately (Altona, Delft, Zaandam, Salford...): not matched to the listed city
WRONG = {'VIENNE', 'BOULOGNE', 'BRANDENBURG'}
SEPARATE = {'ALTONA', 'BARMEN', 'DELFT', 'FURTH', 'OLDHAM', 'SALFORD', 'ZAANDAM'}
NEW = {'LEIDEN': 'Leiden', 'TOLEDO': 'Toledo', 'PLYMOUTH': 'Plymouth', 'CREMONA': 'Cremona', 'MANTUA': 'Mantua',
       'BRUGGE': 'Bruges', 'VICENZA': 'Vicenza', 'JEREZ DA LA FRONTERA': 'Jerez de la Frontera', 'PIACENZA': 'Piacenza',
       'CARTAGENA': 'Cartagena', 'PORTSMOUTH': 'Portsmouth', 'LECCE': 'Lecce', 'BATH': 'Bath', 'VERSAILLES': 'Versailles',
       'MIDDELBURG': 'Middelburg', 'TOURNAI': 'Tournai', 'NANCY': 'Nancy', 'SEGOVIA': 'Segovia', 'JAEN': 'Jaén',
       'HULL': 'Hull', 'ECIJA': 'Écija', 'AIX EN PROVENCE': 'Aix-en-Provence', 'DUNDEE': 'Dundee', 'TRAPANI': 'Trapani',
       'SANTIAGO': 'Santiago de Compostela', 'SALAMANCA': 'Salamanca', 'SAINT-MALO': 'Saint-Malo', 'MECHELEN': 'Mechelen',
       'LUCCA': 'Lucca', 'CUENCA': 'Cuenca', 'BOURGES': 'Bourges', 'ARLES': 'Arles', 'SUNDERLAND': 'Sunderland',
       'PAVIA': 'Pavia', 'REGENSBURG': 'Regensburg', 'LA ROCHELLE': 'La Rochelle', 'AVIGNON': 'Avignon',
       "'S HERTOGENBOSCH": "'s-Hertogenbosch", 'ENKHUIZEN': 'Enkhuizen', 'DORDRECHT': 'Dordrecht', 'BURGOS': 'Burgos',
       'TROYES': 'Troyes', 'NICOSIA': 'Nicosia (Sicily)', 'MARSALA': 'Marsala', 'LEUVEN': 'Leuven', 'DUNKERQUE': 'Dunkirk',
       'DOUAI': 'Douai', 'BAEZA': 'Baeza', 'WATERFORD': 'Waterford', 'SAINT-OMER': 'Saint-Omer', 'POITIERS': 'Poitiers',
       'PIAZZA (ENNA)': 'Piazza Armerina', 'MODICA/POZZALLO': 'Modica', 'CALTAGIRONE': 'Caltagirone',
       'ALCAZAR DE SAN JUAN': 'Alcázar de San Juan', 'ALTONA': 'Altona', 'DELFT': 'Delft', 'ZAANDAM': 'Zaandam'}

def km(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    return 6371 * math.acos(min(1, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(a[0] - b[0]))))

header, rows = [], []
for l in open(CT, encoding='utf-8'):
    if l.startswith('#') or not l.strip(): header.append(l); continue
    n, lon, lat, ser = l.rstrip('\n').split('|')
    rows.append([n, lon, lat, [(1700 + int(a), b) for a, b in (p.split(':') for p in ser.split(';'))]])
names = {r[0] for r in rows}
added = matched = 0
for c, fig in ep.items():
    if c in WRONG: continue
    target = None
    if c not in SEPARATE:
        best = min(rows, key=lambda r: km(co[c], (float(r[1]), float(r[2]))))
        if km(co[c], (float(best[1]), float(best[2]))) < 12: target = best
    if target is None:
        if c not in NEW or max(fig.values()) < 20000 or NEW[c] in names: continue
        target = [NEW[c], f'{co[c][0]:g}', f'{co[c][1]:g}', []]; rows.append(target); names.add(NEW[c])
    else: matched += 1
    pts = target[3]
    for y, v in fig.items():
        if y == 1800 and any(1795 <= yy <= 1805 for yy, _ in pts): continue
        same = [p for p in pts if p[0] // 10 == y // 10]
        if same and not all(b.endswith('C') for _, b in same): continue
        pts[:] = [p for p in pts if p not in same] + [(y, f'{v}V')]; added += 1
    pts.sort()
out = header + [f"{n}|{lon}|{lat}|" + ';'.join(f'{y - 1700}:{b}' for y, b in pts) + '\n' for n, lon, lat, pts in rows]
open(CT, 'w', encoding='utf-8').writelines(out)
print('de Vries cities matched', matched, '; cities now', len(rows), '; figures added', added)
