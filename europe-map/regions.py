"""Step 5: merge neighboring faces that have the same history into regions, and work out
country labels for each year.

Output: regions.pkl
"""
import pickle, sys, time
import numpy as np
import shapely
from shapely.ops import unary_union, polylabel
from pyproj import Transformer
sys.path.insert(0, __file__.rsplit('/', 1)[0])

t0 = time.time()
A = pickle.load(open('assign.pkl', 'rb')); F = pickle.load(open('faces.pkl', 'rb'))
K, YEARS = A['KEYS'], A['YEARS']; NY = len(YEARS)
faces, land = F['faces'], F['land']
def_u, def_src = A['def_u'], A['def_src']
# which record backs each answer: OHM relation id, CShapes/Cliopatria feature index, or correction number
ref = np.where(def_src == 0, A['ohm_rec'], np.where(def_src == 1, A['cs_rec'], np.where(def_src == 2, A['cl_rec'],
               np.where(def_src == 3, A['ohm_rec'], def_src))))
# bridged years: point at the OHM record just before the gap (or, failing that, just after)
last = np.zeros(len(faces), np.int64); nxt = np.zeros(len(faces), np.int64); back = np.zeros_like(ref)
for j in range(NY - 1, -1, -1):
    o = def_src[:, j] == 0; nxt[o] = A['ohm_rec'][o, j]; back[:, j] = nxt
for j in range(NY):
    o = def_src[:, j] == 0; last[o] = A['ohm_rec'][o, j]
    b = def_src[:, j] == 3
    ref[b, j] = np.where(last[b] > 0, last[b], back[b, j])

sig_of = {}; sigs = []; face_sig = np.full(len(faces), -1)
for i in np.where(land)[0]:
    key = (def_u[i].tobytes(), def_src[i].tobytes(), ref[i].tobytes())
    if key not in sig_of:
        sig_of[key] = len(sigs); sigs.append((def_u[i].copy(), def_src[i].copy(), ref[i].copy()))
    face_sig[i] = sig_of[key]
print('signatures', len(sigs), round(time.time() - t0), 's')

regions = []                     # (polygon lon/lat, sig)
for s in range(len(sigs)):
    idx = np.where(face_sig == s)[0]
    g = unary_union([faces[i] for i in idx]) if len(idx) > 1 else faces[idx[0]]
    for part in shapely.get_parts(g):
        regions.append((part, s))
print('regions', len(regions), round(time.time() - t0), 's')

# labels: for each year and country, the largest piece inside the view, and a point well inside it
tr = Transformer.from_crs(4326, 3035, always_xy=True)
proj = lambda g: shapely.transform(g, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))
VIEW = shapely.box(-25.5, 34.4, 49.5, 71.8)   # same as the page's map area
rp = [proj(g) for g, s in regions]
rarea = np.array([g.area / 1e6 for g in rp])
rsig = np.array([s for g, s in regions])
sig_u = np.array([sg[0] for sg in sigs])            # sig x year -> unit
sig_ref = np.array([sg[2] for sg in sigs]); sig_src = np.array([sg[1] for sg in sigs])
in_view = np.array([g.intersects(VIEW) for g, s in regions])
labels = {}
cache = {}
for j, y in enumerate(YEARS):
    u = sig_u[rsig, j]
    for k in np.unique(u):
        if k < 0: continue
        idx = np.where((u == k) & in_view)[0]
        if not len(idx): continue
        key = tuple(idx)
        if key not in cache:
            g = shapely.make_valid(proj(unary_union([regions[i][0] for i in idx])))
            parts = sorted(shapely.get_parts(g), key=lambda p: -p.area)
            main = parts[0]
            vg = proj(shapely.segmentize(VIEW, 0.25))   # densify so the edges follow parallels and meridians
            main_v = shapely.make_valid(main).intersection(vg)
            if main_v.is_empty: cache[key] = None; continue
            mv = max([p for p in shapely.get_parts(main_v) if p.geom_type == 'Polygon'], key=lambda p: p.area)
            pt = polylabel(mv, tolerance=2000)
            cache[key] = (pt.x, pt.y, g.area / 1e6, mv.area / 1e6)
        if cache[key] is None: continue
        # name: the record name covering most of this country's area this year
        refs = {}
        for i in idx:
            refs.setdefault((int(sig_src[rsig[i], j]), int(sig_ref[rsig[i], j])), 0)
            refs[(int(sig_src[rsig[i], j]), int(sig_ref[rsig[i], j]))] += rarea[i]
        best = max(refs, key=refs.get)
        labels.setdefault(y, []).append((K[k], *cache[key], best))
print('labels', sum(len(v) for v in labels.values()), round(time.time() - t0), 's')
pickle.dump({'regions': regions, 'sigs': sigs, 'labels': labels}, open('regions.pkl', 'wb'))
