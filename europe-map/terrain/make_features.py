"""Names of physical features for the Europe map: seas and straits, mountain ranges, plains and uplands, passes and
peaks. Writes them into terrain.json ('feat'), which the page draws as its own layer of names.

Usage (in europe-map/): python3 terrain/make_features.py <folder with the Natural Earth sources> [terrain.json]

Sources: Natural Earth 10m marine areas (seas, gulfs, straits) and geography regions (ranges, plains, uplands, deltas),
public domain; terrain/features_extra.json, a short list of passes, gorges, gaps, straits, peaks, marshes and forests
that mattered in Europe's history, placed from Wikidata.

Each area (a sea, a range) gets a 'spine': the longest line through the middle of its shape (the shape drawn on a grid,
thinned to its skeleton, and the longest path through that taken and smoothed). The page sets the name along the part
of the spine on screen, spaced out to stretch across it, the way names of ranges and seas run on older atlases."""
import json, sys, collections
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.morphology import skeletonize
import shapely
from shapely.geometry import shape, box, LineString
from pyproj import Transformer

SRC = sys.argv[1]; TJ = sys.argv[2] if len(sys.argv) > 2 else 'terrain.json'
tr = Transformer.from_crs(4326, 3035, always_xy=True)
def proj(g): return shapely.transform(g, lambda c: np.column_stack([v / 1000 for v in tr.transform(c[:, 0], c[:, 1])]) * [1, -1])
def pt(lon, lat): x, y = tr.transform(lon, lat); return round(x / 1000, 1), round(-y / 1000, 1)
VIEW = box(-25.5, 34.4, 49.5, 71.8); WIDE = box(-35, 30, 62, 76)

def spine(poly):
    """the longest path through the middle of a shape, in map km, smoothed"""
    minx, miny, maxx, maxy = poly.bounds
    res = max(maxx - minx, maxy - miny) / 220
    W, H = int((maxx - minx) / res) + 5, int((maxy - miny) / res) + 5
    im = Image.new('1', (W, H), 0); dr = ImageDraw.Draw(im)
    for p in shapely.get_parts(poly):
        if p.geom_type != 'Polygon': continue
        dr.polygon([((x - minx) / res + 2, (y - miny) / res + 2) for x, y in p.exterior.coords], fill=1)
    m = ndimage.binary_closing(np.asarray(im), iterations=2)
    m = ndimage.binary_opening(m, iterations=1) if m.sum() > 400 else m
    sk = skeletonize(m)
    ys, xs = np.nonzero(sk)
    if len(xs) < 3: c = poly.representative_point(); return [(c.x - 1, c.y), (c.x + 1, c.y)]
    idx = {(y, x): i for i, (y, x) in enumerate(zip(ys, xs))}
    nb = [[] for _ in xs]
    for i, (y, x) in enumerate(zip(ys, xs)):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                j = idx.get((y + dy, x + dx))
                if j is not None and j != i: nb[i].append(j)
    def bfs(s):
        d = {s: 0}; prev = {s: None}; q = collections.deque([s])
        while q:
            u = q.popleft()
            for v in nb[u]:
                if v not in d: d[v] = d[u] + 1; prev[v] = u; q.append(v)
        far = max(d, key=d.get); return far, prev
    a, _ = bfs(0); b, prev = bfs(a)
    path = []; u = b
    while u is not None: path.append(u); u = prev[u]
    xy = np.array([(xs[i], ys[i]) for i in path], float)
    k = max(3, len(xy) // 12) | 1                         # smooth: a running mean over about a twelfth of the length
    pad = np.pad(xy, ((k // 2, k // 2), (0, 0)), mode='edge')
    sm = np.array([pad[i:i + k].mean(0) for i in range(len(xy))])
    sm = sm[len(sm) // 12: len(sm) - len(sm) // 12] if len(sm) > 12 else sm   # the skeleton's ends run into corners: drop a twelfth at each
    line = LineString([((x - 2) * res + minx, (y - 2) * res + miny) for x, y in sm]).simplify(res * 1.5)
    return [(round(x, 1), round(y, 1)) for x, y in line.coords]

feats = []
def add(name, kind, z, rank, geom=None, at=None, wiki=''):
    f = {'n': name, 'k': kind, 'z': round(z, 2), 'r': rank}
    if geom is not None:
        big = max(shapely.get_parts(geom), key=lambda p: p.area)
        s = spine(big); f['c'] = [c for xy in s for c in xy]
        f['len'] = round(LineString(s).length); f['w'] = round(2 * big.area / max(1, LineString(s).length))   # mean width, km
    else: f['p'] = list(at)
    if wiki: f['wk'] = wiki
    feats.append(f)

# ---------- seas, gulfs and straits ----------
MARINE = {'sea': 'sea', 'ocean': 'sea', 'bay': 'gulf', 'gulf': 'gulf', 'channel': 'gulf', 'sound': 'strait', 'strait': 'strait', 'fjord': 'gulf'}
SKIP = {'Greenland Sea', 'Scoresby Sound', 'Denmark Strait', 'Boknafjord', 'Vestfjorden', 'Sognefjord', 'Trondheimsfjord', 'Gulf of Gabès', 'Sea of the Hebrides', 'Atlantic Ocean', 'Barents Sea', 'White Sea', 'Caspian Sea'}
for f in json.load(open(f'{SRC}/ne_10m_geography_marine_polys.geojson'))['features']:
    p = f['properties']; name = p.get('name_en') or p.get('name'); fc = (p.get('featurecla') or '').lower()
    kind = MARINE.get(fc)
    if not name or not kind or name in SKIP: continue
    g = shapely.make_valid(shape(f['geometry']))
    if not g.intersects(VIEW): continue
    g = shapely.make_valid(proj(g.intersection(WIDE)))
    if g.is_empty: continue
    add(name, kind, float(p.get('min_label') or 6), int(p.get('scalerank') or 5), geom=g)

# ---------- mountain ranges, plains and uplands ----------
KEEP = {'Range/mtn': 'range', 'Plateau': 'lowland', 'Plain': 'lowland', 'Lowland': 'lowland', 'Delta': 'lowland', 'Tundra': 'lowland'}
SKIPR = {'Cruach nam Miseag', 'Calabria', 'Mount Lebanon Range', 'Zagros Mountains', 'Elburz Mountains', 'Iberian Peninsula', 'Vychegda Lowland',
         'North-Estonian Coastal Plain', 'Caspian Depression', 'Rif', 'Tell Atlas', 'Saharan Atlas', 'Volga Delta', 'Bolshezemelskaya Tundra'}
RENAME = {'Appennino Ligure': 'Apennines', 'Taurus mountains': 'Taurus Mountains', 'Böhmerwald': 'Bohemian Forest', 'Pontic-Caspian steppe': 'Pontic–Caspian Steppe',
          'Vatnajökull': 'Vatnajökull', 'Hardangervidda': 'Hardangervidda'}
for f in json.load(open(f'{SRC}/ne_10m_geography_regions_polys.geojson'))['features']:
    p = f['properties']; kind = KEEP.get(p['FEATURECLA'])
    if not kind: continue
    g = shapely.make_valid(shape(f['geometry']))
    if not g.intersects(VIEW): continue
    name = p.get('NAME_EN') or p['NAME']
    if name in SKIPR: continue
    name = RENAME.get(name, name)
    add(name, kind, float(p['MIN_LABEL']), int(p['SCALERANK']), geom=shapely.make_valid(proj(g.intersection(WIDE))))

# ---------- passes, gorges, peaks and the rest, from the hand-made list ----------
X = json.load(open(__file__.rsplit('/', 1)[0] + '/features_extra.json'))
STYLE = {'pass': 'pass', 'gorge': 'pass', 'gap': 'pass', 'strait': 'strait', 'peak': 'peak', 'plain': 'lowland', 'forest': 'lowland', 'marsh': 'lowland', 'field': 'lowland'}
for name, kind, lon, lat, rank, wiki in X['features']:
    add(name, STYLE[kind], {1: 4.8, 2: 5.5, 3: 6.2}[rank], rank + 3, at=pt(lon, lat), wiki=wiki)
    feats[-1]['t'] = kind

T = json.load(open(TJ)); T.pop('names', None); T['feat'] = feats
json.dump(T, open(TJ, 'w'), separators=(',', ':'))
print(len(feats), 'features:', collections.Counter(f['k'] for f in feats))
