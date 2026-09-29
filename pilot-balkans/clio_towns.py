"""Who Cliopatria says held each town, per year 1815-1900 (writes clio_towns.json).

Needs cliopatria_polities_only.geojson from
https://github.com/Seshat-Global-History-Databank/cliopatria (unzip cliopatria.geojson.zip), and shapely.
Coastal towns that fall just outside Cliopatria's coarse shapes take the nearest shape
within 22 km, marked with "~<km>".
"""
import json, sys
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

towns = json.load(open('towns.json'))
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'cliopatria_polities_only.geojson'))
feats = [f for f in d['features'] if f['geometry'] and f['properties']['ToYear'] >= 1810 and f['properties']['FromYear'] <= 1905]
geoms = [shape(f['geometry']) for f in feats]
tree = STRtree(geoms)
out = {}
for n, lat, lon in towns:
    pt = Point(lon, lat); cand = list(tree.query(pt.buffer(0.2)))
    runs, prev = [], None
    for y in range(1815, 1901):
        live = [i for i in cand if feats[i]['properties']['FromYear'] <= y <= feats[i]['properties']['ToYear']]
        hits = sorted({feats[i]['properties']['Name'] for i in live if geoms[i].contains(pt)})
        key = ';'.join(hits)
        if not hits:
            near = [(geoms[i].distance(pt), feats[i]['properties']['Name']) for i in live]
            if near:
                dist, nm = min(near)
                if dist * 111 <= 22: key = nm + '~' + str(round(dist * 111))
        if prev and prev[2] == key: prev[1] = y
        else: prev = [y, y, key]; runs.append(prev)
    out[n] = runs
json.dump(out, open('clio_towns.json', 'w'), ensure_ascii=False)
print(len(out), 'towns')
