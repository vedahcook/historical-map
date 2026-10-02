"""Shaded relief for the Europe map from elevation data (replaces the relief in make_terrain.py when run after it).

Usage (in europe-map/): python3 terrain/make_relief_dem.py terrain/srtm_ramp2_eu.u8.gz <folder with ne_50m_land and the lakes> [terrain.json]
Writes relief.webp and sets the image's position in terrain.json.

Elevation: "Srtm ramp2.world.21600x10800.jpg" on Wikimedia Commons (NASA, public domain): the Earth's heights as 8-bit
gray, one pixel per minute of arc (about 1.9 km north–south, 1.2 km east–west at 50°N), sea level at gray 12. Checked
against known peaks (Mont Blanc, Elbrus, Mulhacén, Etna, Musala): about 37 m per gray level. terrain/srtm_ramp2_eu.u8.gz
is the part from 35°W to 62°E and 76°N to 30°N (2760 rows of 5820 bytes, gzipped), as browser/fetch_dem.js cuts it out.

Shading: heights smoothed a little (the picture is a JPEG, and 37 m steps would show as terraces), resampled to the
map's projection at KM km to the pixel, then lit from four directions around the northwest (the usual way to keep
relief soft and even) and drawn, as before, as black (shade) or white (light) with transparency over the country
colors."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import shapely
from shapely.geometry import shape, box
from pyproj import Transformer

DEM, SRC = sys.argv[1], sys.argv[2]
TJ = sys.argv[3] if len(sys.argv) > 3 else 'terrain.json'
KM = float(os.environ.get('KM', '1.6'))
tr = Transformer.from_crs(4326, 3035, always_xy=True); inv = Transformer.from_crs(3035, 4326, always_xy=True)
def proj(g): return shapely.transform(g, lambda c: np.column_stack([v / 1000 for v in tr.transform(c[:, 0], c[:, 1])]) * [1, -1])
VIEW = box(-25.5, 34.4, 49.5, 71.8); WIDE = box(-35, 30, 62, 76)

# the same area as make_terrain.py: the map's own area and some way beyond
vb = proj(shapely.segmentize(VIEW, 0.1)).bounds
x0, y0, x1, y1 = vb[0] - 600, vb[1] - 500, vb[2] + 600, vb[3] + 400
NX, NY = int((x1 - x0) / KM), int((y1 - y0) / KM)

import gzip
g = (np.frombuffer(gzip.open(DEM).read(), np.uint8).reshape(2760, 5820) if DEM.endswith('.gz') else np.load(DEM)).astype(np.float32)
elev = np.clip(g - 12, 0, None) * 37.2                       # meters
elev = ndimage.gaussian_filter(elev, float(os.environ.get('SMOOTH', '1.3')))
sea = ndimage.gaussian_filter((g <= 12).astype(np.float32), 0.8) > 0.5
gx = x0 + (np.arange(NX) + 0.5) * KM; gy = y0 + (np.arange(NY) + 0.5) * KM
GX, GY = np.meshgrid(gx, gy)
lon, lat = inv.transform(GX.ravel() * 1000, -GY.ravel() * 1000)
px = (np.asarray(lon) + 35) * 60 - 0.5; py = (76 - np.asarray(lat)) * 60 - 0.5
E = ndimage.map_coordinates(elev, [py, px], order=1, mode='nearest').reshape(NY, NX)

# hillshade: rows run south, columns east; slopes in m per m
dzdy, dzdx = np.gradient(E, KM * 1000)
dzdy = -dzdy                                                   # northward
Z = float(os.environ.get('ZF', '4'))                           # vertical exaggeration: 1.6 km cells flatten the slopes
p, q = dzdx * Z, dzdy * Z
alt = np.radians(42)
def lit(az):
    a = np.radians(az)
    lx, ly, lz = np.cos(alt) * np.sin(a), np.cos(alt) * np.cos(a), np.sin(alt)   # light from azimuth a (clockwise from north)
    return (lz - p * lx - q * ly) / np.sqrt(1 + p * p + q * q)
hs = 0.15 * lit(225) + 0.25 * lit(270) + 0.40 * lit(315) + 0.20 * lit(360)
rel = hs / np.sin(alt) - 1                                     # 0 on flat ground, below 0 in shade

# land: Natural Earth 50m land without the larger lakes, and not the elevation picture's sea
mask = Image.new('L', (NX, NY), 0); dr = ImageDraw.Draw(mask)
def fill(geom, v):
    for pg in shapely.get_parts(geom):
        if pg.geom_type != 'Polygon' or pg.is_empty: continue
        dr.polygon([((x - x0) / KM, (y - y0) / KM) for x, y in pg.exterior.coords], fill=v)
        for h in pg.interiors: dr.polygon([((x - x0) / KM, (y - y0) / KM) for x, y in h.coords], fill=255 - v)
area = box(x0, y0, x1, y1)
for f in json.load(open(f'{SRC}/ne_50m_land.geojson'))['features']:
    geom = shapely.make_valid(shape(f['geometry'])).intersection(WIDE)
    if not geom.is_empty: fill(shapely.make_valid(proj(geom)).intersection(area), 255)
for name in ('ne_10m_lakes.geojson', 'ne_10m_lakes_europe.geojson'):
    for f in json.load(open(f'{SRC}/{name}'))['features']:
        geom = shapely.make_valid(shape(f['geometry']))
        if geom.intersects(WIDE) and geom.area > 0.02: fill(shapely.make_valid(proj(geom.intersection(WIDE))).intersection(area), 0)
M = np.asarray(mask).astype(np.float32) / 255
M *= 1 - ndimage.map_coordinates(sea.astype(np.float32), [py, px], order=1, mode='nearest').reshape(NY, NX)

A, B = float(os.environ.get('SHADE', '1.35')), float(os.environ.get('LIGHT', '0.6'))
alpha = np.where(rel < 0, np.clip(-rel * A, 0, 0.55), np.clip(rel * B, 0, 0.18)) * M
gray = np.where(rel < 0, 0, 255).astype(np.uint8)
a8 = np.clip(alpha * 255, 0, 255).astype(np.uint8); a8[a8 < 5] = 0
Image.fromarray(np.dstack([gray, gray, gray, a8]), 'RGBA').save('relief.webp', 'WEBP', quality=70, alpha_quality=55, method=6)
print('relief.webp', NX, 'x', NY, os.path.getsize('relief.webp') // 1024, 'KB')
if os.path.exists(TJ):
    T = json.load(open(TJ)); T['relief'] = {'src': 'relief.webp', 'box': [round(x0, 1), round(y0, 1), round(NX * KM, 1), round(NY * KM, 1)]}
    json.dump(T, open(TJ, 'w'), separators=(',', ':'))
