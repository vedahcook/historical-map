"""Terrain for the Europe map: shaded relief, rivers with names, lakes and the names of mountain ranges.

Usage (in europe-map/): python3 terrain/make_terrain.py <folder with the sources>
Writes relief.webp (the shading, as an image to lay over the map) and terrain.json (rivers, lakes, mountain names and
where the image sits), both loaded by the page only when it needs them.

Sources (all Natural Earth, public domain):
- shadedrelief.jpg: Natural Earth's 1:50m shaded relief with hypsometric tints, 10800 x 5400 pixels for the world, as
  shipped in the basemap-data Python package (mpl_toolkits/basemap_data/shadedrelief.jpg).
- ne_10m_rivers_lake_centerlines.geojson, ne_10m_rivers_europe.geojson (more of Europe's smaller rivers),
  ne_10m_lakes.geojson, ne_10m_lakes_europe.geojson, ne_10m_geography_regions_polys.geojson (mountain ranges and
  plains), ne_50m_land.geojson: from github.com/nvkelso/natural-earth-vector (geojson folder).

Shading: the image's brightness divided by its local average (over about 6 pixels, land only) keeps the light and
shadow of the slopes and drops the colors for height, which change slowly. It is then drawn in the map's projection
(ETRS89-LAEA, in km, y pointing south, as export.py), 2.5 km to the pixel, as black (shade) or white (light) with
transparency, so the page lays it over the country colors without blending tricks."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import shapely
from shapely.geometry import shape, box, mapping
from shapely.ops import linemerge, unary_union
from pyproj import Transformer

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
tr = Transformer.from_crs(4326, 3035, always_xy=True)
inv = Transformer.from_crs(3035, 4326, always_xy=True)
def proj(g):
    return shapely.transform(g, lambda c: np.column_stack([v / 1000 for v in tr.transform(c[:, 0], c[:, 1])]) * [1, -1])
VIEW = box(-25.5, 34.4, 49.5, 71.8)
WIDE = box(-40, 28, 70, 80)                           # what the relief covers (beyond the mapped area, so it fills the screen)

# ---------- the area the relief image covers, in map km ----------
KM = 2.5
vb = proj(shapely.segmentize(VIEW, 0.1)).bounds        # the map's own area
x0, y0, x1, y1 = vb[0] - 600, vb[1] - 500, vb[2] + 600, vb[3] + 400
NX, NY = int((x1 - x0) / KM), int((y1 - y0) / KM)
print('relief grid', NX, 'x', NY)

# ---------- shading from the shaded-relief picture ----------
im = Image.open(f'{SRC}/shadedrelief.jpg').convert('RGB')
A = np.asarray(im).astype(np.float32); W, H = im.size; ppd = W / 360
L = 0.299 * A[..., 0] + 0.587 * A[..., 1] + 0.114 * A[..., 2]
L = ndimage.gaussian_filter(L, 0.9)                      # soften the picture's grain (JPEG and texture)
# land in the picture: anything not water-blue (the picture's sea and lakes)
water = (A[..., 2] - A[..., 0] > 22) & (A[..., 2] > 140)
land = ndimage.binary_opening(~water, iterations=1).astype(np.float32)
SIG = 9
avg = ndimage.gaussian_filter(L * land, SIG) / np.maximum(ndimage.gaussian_filter(land, SIG), 1e-3)   # local average over land only
ratio = np.where(land > 0, L / np.maximum(avg, 1), 1.0)
# the picture's own coastlines carry a thin dark rim; ease the shading off within two pixels of the water
dist = ndimage.distance_transform_edt(land)
ratio = 1 + (ratio - 1) * np.clip((dist - 1) / 2.5, 0, 1)

# sample it at each pixel of the map grid (bilinear)
gx = x0 + (np.arange(NX) + 0.5) * KM; gy = y0 + (np.arange(NY) + 0.5) * KM
GX, GY = np.meshgrid(gx, gy)
lon, lat = inv.transform(GX.ravel() * 1000, -GY.ravel() * 1000)
px = (np.asarray(lon) + 180) * ppd - 0.5; py = (90 - np.asarray(lat)) * ppd - 0.5
r = ndimage.map_coordinates(ratio, [py, px], order=1, mode='nearest').reshape(NY, NX)

# land in the map: Natural Earth 50m land, without the larger lakes
mask = Image.new('L', (NX, NY), 0); dr = ImageDraw.Draw(mask)
def fill(g, v):
    for p in shapely.get_parts(g):
        if p.geom_type != 'Polygon' or p.is_empty: continue
        dr.polygon([((x - x0) / KM, (y - y0) / KM) for x, y in p.exterior.coords], fill=v)
        for h in p.interiors: dr.polygon([((x - x0) / KM, (y - y0) / KM) for x, y in h.coords], fill=255 - v)
area = box(x0, y0, x1, y1)
for f in json.load(open(f'{SRC}/ne_50m_land.geojson'))['features']:
    g = shapely.make_valid(shape(f['geometry'])).intersection(WIDE)
    if not g.is_empty: fill(shapely.make_valid(proj(g)).intersection(area), 255)
lakes_all = [f for f in json.load(open(f'{SRC}/ne_10m_lakes.geojson'))['features']] + json.load(open(f'{SRC}/ne_10m_lakes_europe.geojson'))['features']
for f in lakes_all:
    g = shapely.make_valid(shape(f['geometry']))
    if g.intersects(WIDE) and g.area > 0.02: fill(shapely.make_valid(proj(g.intersection(WIDE))).intersection(area), 0)
M = np.asarray(mask).astype(np.float32) / 255

# shade below 1, light above; strength chosen so the Alps read clearly and the plains stay clean
s = (r - 1)
s = np.sign(s) * np.minimum(np.abs(s), 0.4)
a_shade = np.clip(-s * 1.7, 0, 0.5); a_light = np.clip(s * 0.8, 0, 0.16)
alpha = (np.where(s < 0, a_shade, a_light) * M)
gray = np.where(s < 0, 0, 255).astype(np.uint8)
alpha8 = np.clip(alpha * 255, 0, 255).astype(np.uint8)
alpha8[alpha8 < 9] = 0                                   # no faint haze over the plains
rgba = np.dstack([gray, gray, gray, alpha8])
Image.fromarray(rgba, 'RGBA').save('relief.webp', 'WEBP', quality=72, alpha_quality=60, method=6)
import os
print('relief.webp', os.path.getsize('relief.webp') // 1024, 'KB')

# ---------- rivers ----------
# Natural Earth's rivers, each tagged with the zoom (web map levels) from which it should show; the page converts that
# to its own scale. Pieces of one river are merged; its name goes along it when there is room.
NAME_FIX = {'Rhein': 'Rhine', 'Glma': 'Glomma', 'Truma': 'Struma', 'Zapadnaya Dvina': 'Daugava', 'Júcar-Xúquer': 'Júcar', 'Strimonas': 'Struma'}
def rivers(path, extra):
    out = []
    for f in json.load(open(f'{SRC}/{path}'))['features']:
        p = f['properties']
        if p.get('featurecla', '').startswith('Lake') and 'Centerline' not in p.get('featurecla', ''): continue
        g = shape(f['geometry'])
        if not g.intersects(WIDE): continue
        name = p.get('name_en') or p.get('name') or ''
        if name == 'Aragón' and p.get('name') == 'Alagón': name = 'Alagón'     # a slip in Natural Earth's English names
        name = NAME_FIX.get(name, name)
        out.append({'g': g.intersection(WIDE), 'n': name, 'z': float(p.get('min_zoom') or 7), 'r': float(p.get('scalerank') or 9), 'lz': float(p.get('min_label') or 8), 'id': (path, p.get('rivernum'), name)})
    return out
R = rivers('ne_10m_rivers_lake_centerlines.geojson', False) + rivers('ne_10m_rivers_europe.geojson', True)
# merge each river's pieces (same file, river number and name)
groups = {}
for x in R: groups.setdefault(x['id'], []).append(x)
riv = []
for (path, num, name), xs in groups.items():
    u = unary_union([x['g'] for x in xs])
    g = linemerge(u) if u.geom_type == 'MultiLineString' else u
    g = proj(g)
    z = min(x['z'] for x in xs); rk = min(x['r'] for x in xs); lz = min(x['lz'] for x in xs)
    # coarser outlines for rivers that show from far out; each tier keeps the detail its zoom needs
    tol = 0.6 if z >= 6 else 1.2 if z >= 5 else 2.0
    g = g.simplify(tol)
    parts = [p for p in shapely.get_parts(g) if p.length > 3]
    if not parts: continue
    coords = [[round(c, 1) for xy in p.coords for c in xy] for p in parts]
    riv.append({'n': name if name and name.lower() not in ('', 'unnamed') else '', 'z': z, 'r': rk, 'lz': lz, 'c': coords})
print('rivers', len(riv), sum(len(c) for x in riv for c in x['c']) // 2, 'points')

# ---------- lakes: Natural Earth 10m, the larger ones (the page's own 50m lakes cover the rest from far out) ----------
lk = []
for f in lakes_all:
    p = f['properties']; g = shapely.make_valid(shape(f['geometry']))
    if not g.intersects(WIDE): continue
    g = shapely.make_valid(proj(g.intersection(WIDE))).simplify(0.8)
    if g.area < 25: continue
    z = float(p.get('min_zoom') or 6)
    for q in shapely.get_parts(g):
        if q.geom_type != 'Polygon' or q.area < 25: continue
        lk.append({'z': z, 'c': [[round(c, 1) for xy in ring.coords for c in xy] for ring in [q.exterior, *q.interiors]]})
print('lakes', len(lk))

# ---------- names of mountain ranges, uplands and plains ----------
from shapely.ops import polylabel
KEEP = {'Range/mtn', 'Plateau', 'Plain', 'Lowland', 'Delta', 'Tundra'}
SKIP = {'Cruach nam Miseag', 'Calabria', 'Mount Lebanon Range', 'Zagros Mountains', 'Elburz Mountains', 'Iberian Peninsula',
        'Vychegda Lowland', 'Bolshezemelskaya Tundra', 'North-Estonian Coastal Plain', 'Caspian Depression', 'Rif', 'Tell Atlas', 'Saharan Atlas'}
RENAME = {'Appennino Ligure': 'Apennines', 'Taurus mountains': 'Taurus Mountains', 'Böhmerwald': 'Bohemian Forest', 'Pontic-Caspian steppe': 'Pontic–Caspian steppe'}
mt = []
for f in json.load(open(f'{SRC}/ne_10m_geography_regions_polys.geojson'))['features']:
    p = f['properties']
    if p['FEATURECLA'] not in KEEP: continue
    g = shapely.make_valid(shape(f['geometry']))
    if not g.intersects(VIEW): continue
    name = p.get('NAME_EN') or p['NAME']
    if name in SKIP: continue
    name = RENAME.get(name, name)
    g = shapely.make_valid(proj(g.intersection(WIDE))); big = max(shapely.get_parts(g), key=lambda q: q.area)
    c = polylabel(big, tolerance=5)
    bb = big.bounds
    mt.append({'n': name, 'k': 'r' if p['FEATURECLA'] == 'Range/mtn' else 'p', 'z': float(p['MIN_LABEL']), 'x': round(c.x, 1), 'y': round(c.y, 1),
               'w': round(bb[2] - bb[0]), 'h': round(bb[3] - bb[1])})
print('region names', len(mt))

json.dump({'relief': {'src': 'relief.webp', 'box': [round(x0, 1), round(y0, 1), round(NX * KM, 1), round(NY * KM, 1)]},
           'rivers': riv, 'lakes': lk, 'names': mt}, open('terrain.json', 'w'), separators=(',', ':'))
print('terrain.json', os.path.getsize('terrain.json') // 1024, 'KB')
