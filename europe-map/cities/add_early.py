"""Add figures from 1500 to 1780 to cities.txt from Wikipedia's "Historical urban community sizes" tables
(hucs_raw.txt: mostly de Vries 1984 and Chandler). They go in as source C, for decades the city has no figure yet.
Usage: python3 add_early.py ../cities.txt"""
import sys
CT = sys.argv[1]
ALIAS = {'Adrianople': 'Edirne', 'Constantinople': 'Istanbul', 'Breslau': 'Wrocław', 'Danzig': 'Gdańsk',
         'Iași (Jassy)': 'Iași', 'Saint Petersburg': 'St. Petersburg'}
early = {}
for l in open('hucs_raw.txt', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    n, ser = l.rstrip('\n').split('|')
    n = ALIAS.get(n, n)
    for p in ser.split(';'):
        y, v = int(p.split(':')[0]), int(p.split(':')[1][:-1])
        if 1500 <= y <= 1780: early.setdefault(n, {})[y] = v
out, added = [], 0
for l in open(CT, encoding='utf-8'):
    if l.startswith('#') or not l.strip(): out.append(l); continue
    n, lon, lat, ser = l.rstrip('\n').split('|')
    pts = [(1700 + int(a), b) for a, b in (p.split(':') for p in ser.split(';'))]
    have = {y // 10 for y, _ in pts}
    new = [(y, f'{v}C') for y, v in early.get(n, {}).items() if y // 10 not in have and y < pts[0][0]]
    added += len(new)
    pts = sorted(pts + new)
    out.append(f"{n}|{lon}|{lat}|" + ';'.join(f'{y - 1700}:{b}' for y, b in pts) + '\n')
open(CT, 'w', encoding='utf-8').writelines(out)
print('added', added, 'figures for', sum(1 for n in early if any(l.startswith(n + '|') for l in out)), 'cities')
