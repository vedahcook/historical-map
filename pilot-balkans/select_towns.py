"""Pick Balkan towns from Natural Earth populated places (writes towns_ne.json).

Download first:
  curl -O https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson
"""
import json

d = json.load(open('ne_10m_populated_places_simple.geojson'))
KEEP = {'GR', 'AL', 'MK', 'BG', 'RS', 'XK', 'ME', 'BA', 'HR', 'RO', 'MD'}
out = []
for f in d['features']:
    p = f['properties']; lat, lon = p['latitude'], p['longitude']
    ok = p['iso_a2'] in KEEP or p['adm0_a3'] in ('KOS', 'SRB')
    if p['adm0_a3'] == 'TUR' and lon < 29.3 and lat > 40.3: ok = True              # East Thrace
    if p['adm0_a3'] == 'UKR' and 28.0 <= lon <= 30.5 and 45.0 <= lat <= 46.6: ok = True  # Budjak
    if ok:
        out.append((p['name'], p['adm0_a3'], round(lat, 4), round(lon, 4), p['pop_max']))
json.dump(out, open('towns_ne.json', 'w'))
print(len(out), 'towns')
