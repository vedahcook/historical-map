"""Runs data/spot-checks.csv against Cliopatria (Seshat Global History Databank).

    pip install shapely
    python3 scripts/cliopatria_checks.py path/to/cliopatria_polities_only.geojson

Get the GeoJSON from https://github.com/Seshat-Global-History-Databank/cliopatria
(unzip cliopatria.geojson.zip). Cliopatria records one owner per year and is coarse, so
coastal cities can fall outside every polygon; for those the nearest polygon within
~22 km is reported and marked. Results go to out/cliopatria-spot-checks.csv.
"""
import csv, json, os, re, sys
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def read_csv(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))

# Cliopatria names some states differently from OHM.
def alias(p):
    return (p.replace('Switzerland', 'Switzerland|Swiss').replace('Sweden', 'Sweden|Swedish')
             .replace('Greece', 'Greece|Hellenic').replace('Romania', 'Romania|United Principalities')
             .replace('Serbia', 'Serbia|Serbs').replace('Sardinia', 'Sardinia|Piedmont|Savoy')
             .replace('Two Sicilies', 'Two Sicilies|Naples').replace('Ottoman', 'Ottoman|Turk')
             .replace('United Kingdom', 'United Kingdom|British|Britain'))

def main(path):
    places = {r['place']: (float(r['lat']), float(r['lon'])) for r in read_csv('data/places.csv')}
    tests = read_csv('data/spot-checks.csv')
    feats = [f for f in json.load(open(path, encoding='utf-8'))['features']
             if f['geometry'] and f['properties']['ToYear'] >= 1795 and f['properties']['FromYear'] <= 1905]
    geoms = [shape(f['geometry']) for f in feats]
    tree = STRtree(geoms)
    rows, tally = [], {}
    for t in tests:
        year = int(t['date'][:4])
        lat, lon = places[t['place']]
        pt = Point(lon, lat)
        live = lambda i: feats[i]['properties']['FromYear'] <= year <= feats[i]['properties']['ToYear']
        hits = [feats[i]['properties']['Name'] for i in tree.query(pt) if live(i) and geoms[i].contains(pt)]
        note, far = '', False
        if not hits:
            near = [(geoms[i].distance(pt), feats[i]['properties']['Name']) for i in tree.query(pt.buffer(0.2)) if live(i)]
            if near:
                dist, name = min(near)
                hits, note, far = [name], f' (nearest, ~{dist * 111:.0f} km off)', dist * 111 > 22
        rx = re.compile(alias(t['expected_holder']), re.I)
        if any(rx.search(h) for h in hits):
            result = 'right'
        elif not hits or far:
            result = 'nothing there'
        elif all(h == 'German Confederation' for h in hits):
            result = 'only the German Confederation'
        else:
            result = 'wrong'
        tally[result] = tally.get(result, 0) + 1
        rows.append({'place': t['place'], 'date': t['date'], 'expected': t['expected_holder'],
                     'result': result, 'cliopatria_shows': '; '.join(hits) + note})
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    out = os.path.join(ROOT, 'out', 'cliopatria-spot-checks.csv')
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(tally)
    print('Wrote', out)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
