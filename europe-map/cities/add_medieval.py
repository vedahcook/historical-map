"""Add figures from before 1500 to cities.txt, from Wikipedia's "Historical urban community sizes": the Middle Ages
table for 1000-1350 (hucs_medieval_raw.txt, mostly Chandler 1987 and Chandler & Fox 1974) and the 1400 and 1450
columns of the Early Modern table (hucs_raw.txt). They go in as source C.
Also adds the cities in those tables that lie on the map and had 20,000 people or more at some point but are not in
cities.txt (Speyer, Worms, Amalfi, Salerno, Ani, Sarai and others); they have no later figures, so they appear only on
the medieval map.
Usage: python3 add_medieval.py ../cities.txt"""
import sys
CT = sys.argv[1]
ALIAS = {'Constantinople': 'Istanbul', 'Adrianople': 'Edirne', 'Breslau': 'Wrocław', 'Danzig': 'Gdańsk',
         'Iași (Jassy)': 'Iași', 'Antioch': 'Antakya (Antioch)', 'Edessa': 'Şanlıurfa (Edessa)'}
# cities not yet in cities.txt: longitude, latitude (Sarai: Old Sarai, at Selitrennoye; where the later capital stood
# is disputed)
NEW = {'Amalfi': (14.603, 40.634), 'Ani': (43.573, 40.507), 'Antakya (Antioch)': (36.160, 36.202), "L'Aquila": (13.400, 42.350),
       'Şanlıurfa (Edessa)': (38.795, 37.167), 'Laon': (3.620, 49.564), 'Salerno': (14.770, 40.680), 'Sarai': (47.435, 47.181),
       'Speyer': (8.433, 49.317), 'Trier': (6.637, 49.750), 'Veliky Novgorod': (31.275, 58.521), 'Worms': (8.359, 49.632),
       'York': (-1.080, 53.958), 'Ypres': (2.886, 50.851)}
# figures given as a range more than 2.5 times as wide at the top as at the bottom (Genoa 15,000-80,000 in 1000):
# too uncertain to plot
DROP = {('Genoa', 1000), ('Ypres', 1250), ('Milan', 1350), ('Thessaloniki', 1350)}

def read(path, cols):
    out = {}
    for l in open(path, encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        f = l.rstrip('\n').split('|'); n, ser = ALIAS.get(f[0], f[0]), f[cols]
        for p in ser.split(';'):
            y, v = int(p.split(':')[0]), int(p.split(':')[1][:-1])
            if y < 1500 and (f[0], y) not in DROP: out.setdefault(n, {})[y] = v
    return out
med = read('hucs_medieval_raw.txt', 2)
for n, s in read('hucs_raw.txt', 1).items():
    for y, v in s.items(): med.setdefault(n, {}).setdefault(y, v)

out, added = [], 0
for l in open(CT, encoding='utf-8'):
    if l.startswith('#') or not l.strip(): out.append(l); continue
    n, lon, lat, ser = l.rstrip('\n').split('|')
    if n in NEW: continue                                     # written again below (rerunning rebuilds them)
    pts = [(1700 + int(a), b) for a, b in (p.split(':') for p in ser.split(';'))]
    pts = [p for p in pts if p[0] >= 1500]                    # (rerunning replaces what an earlier run added)
    have = {y // 10 for y, _ in pts}
    new = [(y, f'{v}C') for y, v in med.get(n, {}).items() if y // 10 not in have]
    added += len(new)
    pts = sorted(pts + new)
    out.append(f"{n}|{lon}|{lat}|" + ';'.join(f'{y - 1700}:{b}' for y, b in pts) + '\n')
for n, (lon, lat) in NEW.items():
    s = med[n]
    assert max(s.values()) >= 20000, n
    added += len(s)
    out.append(f"{n}|{lon}|{lat}|" + ';'.join(f'{y - 1700}:{v}C' for y, v in sorted(s.items())) + '\n')
open(CT, 'w', encoding='utf-8').writelines(out)
print('added', added, 'figures;', len(NEW), 'new cities; cities with figures before 1500:',
      sum(1 for l in out if not l.startswith('#') and l.strip() and int(l.split('|')[3].split(':')[0]) < -200))
