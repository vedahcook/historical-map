# Paris in 1791 from the ALPAGE GIS data (https://alpage.huma-num.fr/gis-data/), for the French Revolution deep dive.
#
#   python3 deepdive/alpage_to_json.py FOLDER       (FOLDER holds Ilots_1791.gpkg, Hydro_1791.gpkg, Rues_1791.gpkg)
#
# The three GeoPackages come from the "all at once" download on that page (Donnees_SIG_ALPAGE.zip, about 440 MB):
# Tissu_urbain_ancien/Ilots_1791 (city blocks, Paul Rouet), Dynamiques_environnementales/Hydro_1791 (the Seine and
# its arms, 1785-1791, Paul Rouet) and Tissu_urbain_ancien/Rues_1791 (streets after Verniquet, Léa Hermenault).
# The zip can be read a piece at a time (HTTP range requests), so only these files need fetching.
# License: ODbL 1.0. Credit "© ALPAGE: <authors>"; maps made from the data are to be shared under CC BY-SA.
# Writes deepdive/paris1791-alpage.json: longitude/latitude, simplified to about 1.5 m, rounded to 5 decimals.
import sqlite3, sys, os, json
from shapely import wkb, transform
from pyproj import Transformer

d = sys.argv[1]
tr = Transformer.from_crs(2154, 4326, always_xy=True)
proj = lambda g: transform(g, lambda c: __import__('numpy').column_stack(tr.transform(c[:, 0], c[:, 1])))

def geoms(fn, table, cols):
    c = sqlite3.connect(os.path.join(d, fn))
    for row in c.execute(f'select geom,{",".join(cols) if cols else "fid"} from "{table}"'):
        b = row[0]; env = (b[3] >> 1) & 7; hl = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[env]     # GeoPackage header, then WKB
        yield wkb.loads(bytes(b[hl:])), row[1:]

rnd = lambda cs: [[round(x, 5), round(y, 5)] for x, y in cs]
def polys(g):
    ps = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [[rnd(p.exterior.coords)] + [rnd(r.coords) for r in p.interiors] for p in ps if not p.is_empty]

out = {'blocks': [], 'water': [], 'streets': []}
for g, _ in geoms('Ilots_1791.gpkg', 'Ilots_1791', ['SUPERFICIE']):
    g = g.simplify(1.5)
    if not g.is_empty: out['blocks'] += polys(proj(g))
for g, _ in geoms('Hydro_1791.gpkg', 'Hydro_1791', []):
    g = g.simplify(1.5)
    if g.geom_type in ('Polygon', 'MultiPolygon'): out['water'] += polys(proj(g))
for g, (tv, pa, nm) in geoms('Rues_1791.gpkg', 'Rues_1791', ['type_voie', 'particule', 'nom_voie']):
    g = proj(g.simplify(1.5)); name = ' '.join(x for x in [tv, pa, nm] if x and x.strip()).strip()
    for l in ([g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))):
        if l.geom_type == 'LineString': out['streets'].append([name, rnd(l.coords)])
json.dump(out, open('deepdive/paris1791-alpage.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(out['blocks']), 'blocks,', len(out['water']), 'water,', len(out['streets']), 'street lines')
