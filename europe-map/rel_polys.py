"""Build one polygon per OHM record (relation), limited to the map box.
Method: node the record's border lines together with the box edge, split into faces,
and keep faces whose sample point is inside by counting border crossings to the west
(ray parity). Works even though ways wholly outside lat 34-72 were not fetched."""
import json, pickle, numpy as np, time
from shapely.geometry import LineString, box, Polygon
from shapely.ops import unary_union, polygonize, linemerge
from shapely import get_coordinates

B = (-26.0, 34.0, 50.0, 72.0)
BOX = box(*B)
d = json.load(open('europe-borders-sources.json'))
ways = d['ways']
rels = {**{k: v for k, v in d['rels'].items()}, **{k: v for k, v in d['rels4'].items()}}
# some early records are made of other records (a kingdom of its provinces): their members are in 'sub',
# and their polygon is the union of the members'
subs, sub = d.get('subs', {}), d.get('sub', {})
todo = {**sub, **rels}

def segs_of(wids):
    out = []
    for w in wids:
        p = ways.get(str(w))
        if p and len(p) >= 2:
            a = np.array(p, float); out.append(np.hstack([a[:-1], a[1:]]))
    return np.vstack(out) if out else np.zeros((0, 4))

def parity(S, xs, ys):
    # S: (n,4) x1 y1 x2 y2; for each point count crossings of the westward ray
    x1, y1, x2, y2 = S[:, 0][None], S[:, 1][None], S[:, 2][None], S[:, 3][None]
    Y = ys[:, None]; X = xs[:, None]
    straddle = (y1 > Y) != (y2 > Y)
    with np.errstate(divide='ignore', invalid='ignore'):
        xi = x1 + (Y - y1) * (x2 - x1) / (y2 - y1)
    return ((straddle & (xi < X)).sum(1) % 2) == 1

out = {}; t0 = time.time(); bad = []; gaps = []; connectors = []
for rid, r in todo.items():
    if not r['m'] and subs.get(rid): continue
    wids = [m[0] for m in r['m']]
    lines = [LineString(ways[str(w)]) for w in wids if str(w) in ways and len(ways[str(w)]) >= 2]
    if not lines: bad.append((rid, r['t'].get('n'), 'no lines')); continue
    L = unary_union(lines)
    if not L.intersects(BOX): continue
    # close small gaps in broken records: pair up loose ends that lie inside the box
    mg = linemerge(L) if L.geom_type == 'MultiLineString' else L; parts = list(getattr(mg, 'geoms', [mg]))
    deg = {}
    for g in parts:
        for c in (g.coords[0], g.coords[-1]): deg[c] = deg.get(c, 0) + 1
    ends = [c for c, k in deg.items() if k % 2 == 1 and B[0] + 0.05 < c[0] < B[2] - 0.05 and B[1] + 0.05 < c[1] < B[3] - 0.05]
    extra = []
    while len(ends) >= 2:
        a = ends.pop(0)
        j = min(range(len(ends)), key=lambda k: (ends[k][0]-a[0])**2 + (ends[k][1]-a[1])**2)
        dd = ((ends[j][0]-a[0])**2 + (ends[j][1]-a[1])**2) ** 0.5
        b = ends.pop(j)
        if dd < 0.25: extra.append(LineString([a, b])); connectors.append([a, b]); gaps.append((rid, r['t'].get('n'), round(dd, 4)))
    if extra: L = unary_union([L] + extra); lines = lines + extra
    L = unary_union([L.intersection(BOX), BOX.boundary])
    faces = [f for f in polygonize(L)]
    if not faces: bad.append((rid, r['t'].get('n'), 'no faces')); continue
    pts = np.array([f.representative_point().coords[0] for f in faces])
    S = segs_of(wids)
    if extra: S = np.vstack([S] + [np.array([[*e.coords[0], *e.coords[1]]]) for e in extra])
    inside = np.zeros(len(faces), bool)
    for i in range(0, len(faces), 400):
        inside[i:i+400] = parity(S, pts[i:i+400, 0], pts[i:i+400, 1])
    keep = [f for f, k in zip(faces, inside) if k]
    if not keep: bad.append((rid, r['t'].get('n'), 'empty')); continue
    poly = unary_union(keep)
    out[rid] = poly
def build(rid, seen=()):
    if rid in out: return out[rid]
    kids = [build(str(c), seen + (rid,)) for c in subs.get(rid, []) if str(c) not in seen]
    kids = [k for k in kids if k is not None and not k.is_empty]
    if kids: out[rid] = unary_union(kids)
    return out.get(rid)
for rid, r in rels.items():
    if not r['m'] and subs.get(rid): build(rid)
out = {k: v for k, v in out.items() if k in rels}
print('gaps closed:', len(gaps), sorted(gaps, key=lambda g: -g[2])[:25]); print(len(out), 'polygons', round(time.time() - t0), 's'); print('problems:', bad[:30], len(bad))
pickle.dump(out, open('rel_polys.pkl', 'wb')); pickle.dump(gaps, open('gaps.pkl','wb')); pickle.dump(connectors, open('connectors.pkl','wb'))
