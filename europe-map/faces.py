"""Step 2: cut the map into small pieces ("faces") using every border line from every
source, then record which records of each source contain each face.

Inputs (in the working folder): europe-borders-sources.json, rel_polys.pkl, land.pkl, clio.pkl
Output: faces.pkl
"""
import json, pickle, time, sys
import numpy as np
import shapely
from shapely.geometry import shape, box
from shapely.ops import unary_union, polygonize
from shapely.strtree import STRtree
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from units import ohm_roles, cs_unit, clio_unit

B = (-26.0, 34.0, 50.0, 72.0)
BOX = box(*B)
t0 = time.time()
d = json.load(open('europe-borders-sources.json'))
R = {**d['rels'], **d['rels4']}
P = pickle.load(open('rel_polys.pkl', 'rb'))
land = pickle.load(open('land.pkl', 'rb'))
clio = pickle.load(open('clio.pkl', 'rb'))

# records that matter: OHM records with a role; CShapes 1816-1900; Cliopatria 1795-1815 (+ all years for gap filling)
ohm = {rid: g for rid, g in P.items() if ohm_roles(R[rid]['t'].get('n'), R[rid]['t']['l'])}
cs = []
for f in d['cshapes']['features']:
    p = f['properties']
    if p['To'] >= 1816 and p['From'] <= 1900 and cs_unit(p['Name'], p['Status'], p['From']):
        g = shapely.make_valid(shape(f['geometry'])).intersection(BOX)
        if not g.is_empty: cs.append((p, g.simplify(0.002)))
cl = [(p, shapely.make_valid(g)) for p, g in clio if clio_unit(p['Name']) and p['FromYear'] <= 1900]
print('records: ohm', len(ohm), 'cshapes', len(cs), 'clio', len(cl), round(time.time() - t0), 's')

# Collect every border line as unique 2-point segments (many records repeat the same lines).
def segs(g, out, nd=4):
    for part in shapely.get_parts(shapely.boundary(g) if g.geom_type in ('Polygon', 'MultiPolygon') else g):
        c = np.round(shapely.get_coordinates(part), nd)
        for a, b in zip(map(tuple, c[:-1]), map(tuple, c[1:])):
            if a != b: out.add((a, b) if a < b else (b, a))

S = set()
ways = d['ways']
used = {m[0] for rid in ohm for m in R[rid]['m']}
for w in used:
    p = ways.get(str(w))
    if p and len(p) >= 2:
        c = [tuple(x) for x in np.round(np.array(p), 4)]
        for a, b in zip(c[:-1], c[1:]):
            if a != b: S.add((a, b) if a < b else (b, a))
for a, b in pickle.load(open('connectors.pkl', 'rb')):
    a, b = tuple(np.round(a, 4)), tuple(np.round(b, 4))
    if a != b: S.add((a, b) if a < b else (b, a))
n_ohm = len(S)
segs(land, S); segs(BOX, S)
for p, g in cs: segs(g, S)
for p, g in cl:
    if p['FromYear'] <= 1815: segs(g.simplify(0.003), S)
print('segments: ohm', n_ohm, 'all', len(S), round(time.time() - t0), 's')
L = unary_union(shapely.linestrings(np.array([[a, b] for a, b in S])))
print('noded', round(time.time() - t0), 's')
faces = [f for f in polygonize(L) if f.within(BOX.buffer(1e-9))]
print('faces', len(faces), round(time.time() - t0), 's')
pts = np.array([f.representative_point().coords[0] for f in faces])
xs, ys = pts[:, 0], pts[:, 1]
is_land = shapely.contains_xy(land, xs, ys)
tree = STRtree([shapely.Point(p) for p in pts])

def members(g):
    idx = tree.query(g)
    if len(idx) == 0: return np.zeros(0, int)
    return idx[shapely.contains_xy(g, xs[idx], ys[idx])]

in_ohm = {rid: members(g) for rid, g in ohm.items()}
in_cs = [members(g) for p, g in cs]
in_cl = [members(g) for p, g in cl]
print('membership done', round(time.time() - t0), 's')
pickle.dump({'faces': faces, 'pts': pts, 'land': is_land, 'in_ohm': in_ohm, 'cs': [p for p, g in cs], 'in_cs': in_cs,
             'cl': [p for p, g in cl], 'in_cl': in_cl}, open('faces.pkl', 'wb'))
print('saved', round(time.time() - t0), 's')
