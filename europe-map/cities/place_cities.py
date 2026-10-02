"""Find the map region that holds each city in each era, from the maps already in the page (europe-borders.html
for 1800-2026, europe-borders-1500.json, europe-borders-1000.json). The same rule as export.py: the region that
covers the city, or else the nearest within about 20 km (a port just off the simplified coastline).
Used by add_towns.py, so towns can be added without rebuilding the maps."""
import json, re
import shapely
from shapely.strtree import STRtree
from pyproj import Transformer

tr = Transformer.from_crs(4326, 3035, always_xy=True)

def page_data(path='europe-borders.html'):
    h = open(path, encoding='utf-8').read()
    get = lambda i: json.loads(re.search(rf'<script[^>]*id="{i}"[^>]*>(.*?)</script>', h, re.S).group(1).replace('<\\/', '</'))
    return get('data'), get('topo')

def decode(topo):
    """TopoJSON regions -> [(hist index s, shapely geometry in map km)]"""
    t = topo.get('transform'); arcs = []
    for a in topo['arcs']:
        x = y = 0; pts = []
        for p in a:
            if t: x += p[0]; y += p[1]; pts.append((x * t['scale'][0] + t['translate'][0], y * t['scale'][1] + t['translate'][1]))
            else: pts.append(tuple(p[:2]))
        arcs.append(pts)
    def ring(ix):
        out = []
        for i in ix:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out
    def poly(p):
        rs = [ring(r) for r in p]; rs = [r for r in rs if len(r) >= 4]      # simplification can leave a ring too small to keep
        return shapely.Polygon(rs[0], rs[1:]) if rs and len(ring(p[0])) >= 4 else None
    def geom(g):
        ps = [g['arcs']] if g['type'] == 'Polygon' else g['arcs'] if g['type'] == 'MultiPolygon' else []
        ps = [q for q in map(poly, ps) if q is not None]
        return shapely.MultiPolygon(ps) if ps else None
    out = []
    for g in topo['objects']['regions']['geometries']:
        G = geom(g)
        if G is not None: out.append((g['properties']['s'], shapely.make_valid(G)))
    return out

class Placer:
    def __init__(self, D, late_topo, here='.'):
        self.eras = []
        for e in D['eras']:
            topo = json.load(open(f"{here}/{e['src']}"))['topo'] if e.get('src') else late_topo
            regs = decode(topo)
            self.eras.append((regs, STRtree([g for _, g in regs])))
    def xy(self, lon, lat):
        cx, cy = tr.transform(lon, lat); return round(cx / 1000, 1), round(-cy / 1000, 1)
    def place(self, lon, lat):
        """map position (x, y in km) and region index in each era (-1: off the map)"""
        x, y = self.xy(lon, lat); pt = shapely.Point(x, y); ss = []
        for regs, tree in self.eras:
            hit = [j for j in tree.query(pt) if regs[j][1].covers(pt)]
            if not hit:
                near = tree.query_nearest(pt, max_distance=20)
                hit = list(near[:1])
            ss.append(int(regs[hit[0]][0]) if hit else -1)
        return x, y, ss

if __name__ == '__main__':      # check: the existing cities come out where export.py put them
    D, topo = page_data()
    P = Placer(D, topo)
    bad = 0
    # positions are stored in map km; invert to lon/lat for the check
    inv = Transformer.from_crs(3035, 4326, always_xy=True)
    for c in D['cities']:
        lon, lat = inv.transform(c[1] * 1000, -c[2] * 1000)
        x, y, ss = P.place(lon, lat)
        if ss != c[3]: bad += 1; print(c[0], c[3], ss)
    print(len(D['cities']), 'cities,', bad, 'placed differently')
