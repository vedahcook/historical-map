"""Bundle everything the review page needs into one JSON file (bundle.json)."""
import json, math, re
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

YEARS = list(range(1815, 1901))
towns = [t for t in json.load(open('towns.json')) if not t[0].endswith(' (2)')]
TL = json.load(open('timelines.json'))
REC_IDS = json.load(open('ohm_record_ids.json'))
ohm = json.load(open('ohm_towns.json'))
RECS = {r[0]: r for r in ohm['recs']}
raw = {c['id']: c for c in json.load(open('conflicts_raw.json'))}
QS = json.load(open('questions.json'))

# ---- projection: equirectangular scaled at 42.5N --------------------------------
W, LON0, LON1, LAT0, LAT1 = 900, 13.0, 31.0, 34.6, 48.8
K = math.cos(math.radians(42.5))
SX = W / ((LON1 - LON0) * K)
H = round((LAT1 - LAT0) * SX)
def xy(lon, lat):
    return (round((lon - LON0) * K * SX, 1), round((LAT1 - lat) * SX, 1))

def path_of(geom, tol):
    geom = geom.simplify(tol, preserve_topology=True)
    parts = []
    def ring(coords, close):
        pts = [xy(x, y) for x, y in coords]
        if len(pts) < 2: return
        parts.append('M' + 'L'.join(f'{p[0]},{p[1]}' for p in pts) + ('Z' if close else ''))
    t = geom.geom_type
    if t == 'Polygon':
        ring(geom.exterior.coords, True); [ring(i.coords, True) for i in geom.interiors]
    elif t == 'MultiPolygon':
        for g in geom.geoms:
            ring(g.exterior.coords, True); [ring(i.coords, True) for i in g.interiors]
    elif t == 'LineString':
        ring(geom.coords, False)
    elif t == 'MultiLineString':
        for g in geom.geoms: ring(g.coords, False)
    elif t == 'GeometryCollection':
        for g in geom.geoms: parts.append(path_of(g, 0))
    return ''.join(parts)

BOX = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
land = unary_union([shape(f['geometry']).intersection(BOX) for f in json.load(open('ne_50m_land.geojson'))['features'] if shape(f['geometry']).intersects(BOX)])
lakes = unary_union([shape(f['geometry']).intersection(BOX) for f in json.load(open('ne_50m_lakes.geojson'))['features'] if shape(f['geometry']).intersects(BOX)])
rivers = [shape(f['geometry']).intersection(BOX) for f in json.load(open('ne_50m_rivers_lake_centerlines.geojson'))['features']
          if shape(f['geometry']).intersects(BOX) and (f['properties'].get('scalerank') or 9) <= 6]
basemap = {'w': W, 'h': H, 'land': path_of(land, 0.02), 'lakes': path_of(lakes, 0.02), 'rivers': path_of(unary_union(rivers), 0.02)}

# ---- holders --------------------------------------------------------------------
LABEL = {'OTT': 'Ottoman Empire', 'RUS': 'Russian Empire', 'AUT': 'Austria', 'GRE': 'Greece', 'SRB': 'Serbia',
         'MNE': 'Montenegro', 'WAL': 'Wallachia', 'MOL': 'Moldavia', 'ROM': 'Romania (United Principalities)',
         'BUL': 'Bulgaria', 'ERU': 'Eastern Rumelia', 'EGY': 'Egypt', 'CRT': 'Cretan State', 'ION': 'Ionian Islands',
         'UK': 'United Kingdom', 'AUTOCC': 'Austria-Hungary (occupation)', 'HUNREV': 'Hungarian revolutionaries',
         'FRA': 'France', 'NONE': 'No country'}

def label(code):
    if code is None: return None
    if '+' in code: return ' and '.join(LABEL.get(c, c) for c in code.split('+'))
    return LABEL.get(code, code.replace('OTHER:', ''))

# per town, per source: runs [start, end, code]
def runs(vals):
    out = []
    for y, v in zip(YEARS, vals):
        if out and out[-1][2] == v: out[-1][1] = y
        else: out.append([y, y, v])
    return out

town_data = {}
for n, lat, lon in towns:
    x, y = xy(lon, lat)
    town_data[n] = {'x': x, 'y': y, 'src': {s: runs(TL[n][s]) for s in ('OHM', 'CShapes', 'Cliopatria')}}

def to_year(s):
    s = str(s)
    m = re.match(r'(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?', s)
    y, mo, d = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)
    return round(y + (mo - 1) / 12 + (d - 1) / 365, 3)

questions = []
for q in QS['questions']:
    rc = [raw[r] for r in q['raw']]
    qtowns = q.get('towns') or sorted({t for c in rc for t in c['towns']})
    qtowns = [t for t in qtowns if t in town_data]
    start = min(c['start'] for c in rc); end = max(c['end'] for c in rc)
    # focus town: the one with most conflicting years
    weight = {}
    for c in rc:
        for t, a, b in c['town_ranges']:
            if t in qtowns: weight[t] = weight.get(t, 0) + b - a + 1
    focus = max(qtowns, key=lambda t: (weight.get(t, 0), t)) if qtowns else None
    FOCUS = {'danube': 'Bucharest', 'occupations': 'Bucharest', 'serbia': 'Belgrade', 'serbia-early': 'Belgrade', 'nis': 'Niš',
             'bulgaria-1885': 'Plovdiv', 'rumelia': 'Plovdiv', 'kardzhali': 'Kyustendil', 'ionian': 'Kerkira', 'bosnia': 'Sarajevo',
             'montenegro': 'Cetinje', 'montenegro-towns': 'Ulcinj', 'greece-start': 'Nafplio', 'crete-egypt': 'Iraklio',
             'cretan-state': 'Iraklio', 'thessaly': 'Arta', 'elassona': 'Elassona', 'gap1897': 'Thessaloniki', 'bessarabia': 'Izmayil',
             'hungary': 'Cluj-Napoca', 'bulgaria-1877': 'Sofia'}
    if FOCUS.get(q['id']) in qtowns: focus = FOCUS[q['id']]
    window = [max(1815, start - 4), min(1900, end + 4)]
    # OHM records touching the question's towns within the window
    rec_ids = set()
    for t in qtowns:
        for y in range(window[0], window[1] + 1):
            rec_ids.update(REC_IDS[t][y - 1815])
    ohm_records = sorted(({'id': i, 'name': RECS[i][1], 'level': RECS[i][2], 'start': RECS[i][3], 'end': RECS[i][4]} for i in rec_ids if i in RECS and RECS[i][2] in (2, 3)), key=lambda r: r['start'])
    qq = dict(q)
    qq.update({'towns': qtowns, 'focus': focus, 'start': start, 'end': end,
               'window': window,
               'town_years': sum(c['town_years'] for c in rc), 'ohm_records': ohm_records})
    for k in ('legal', 'actual'):
        if qq.get(k):
            qq[k] = [dict(s, x0=to_year(s['from']), x1=to_year(s['to']) if str(s['to']) != '1900' else 1901) for s in qq[k]]
    questions.append(qq)

timing = [c for c in raw.values() if c['category'] == 'timing']
timing_list = [{'towns': c['towns'], 'start': c['start'], 'end': c['end'], 'claims': [{'source': x['source'], 'holder': x['holder']} for x in c['claims']]} for c in timing]
other = [c for c in raw.values() if c['category'] != 'timing' and not any(c['id'] in q['raw'] for q in QS['questions'])]
other_list = [{'towns': c['towns'], 'start': c['start'], 'end': c['end'], 'claims': [{'source': x['source'], 'holder': x['holder']} for x in c['claims']]} for c in other]

bundle = {'years': [YEARS[0], YEARS[-1]], 'basemap': basemap, 'labels': LABEL, 'towns': town_data,
          'questions': questions, 'evidence': QS['evidence'], 'rules': QS['rules'],
          'timing': timing_list, 'other': other_list,
          'track': {'OHM': '149 of 160 spot checks right', 'CShapes': 'about 117 of 131 right (from 1816)', 'Cliopatria': 'about 115 of 160 right'},
          'built': '2026-09-29'}
s = json.dumps(bundle, ensure_ascii=False, separators=(',', ':'))
open('bundle.json', 'w').write(s)
print('bundle bytes', len(s), 'basemap bytes', len(json.dumps(basemap)), 'H', H, 'towns', len(town_data), 'questions', len(questions), 'timing', len(timing_list), 'other', len(other_list))
print({q['id']: (q['focus'], len(q['towns']), q['start'], q['end'], len(q['ohm_records'])) for q in questions})
