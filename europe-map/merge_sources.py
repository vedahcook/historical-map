"""Step 0: combine the two border downloads into europe-borders-sources.json.

  europe-borders-sources-1795-1905.json   OHM 1795-1905 + CShapes-Europe (browser/fetch_borders.js)
  europe-borders-sources-1900-2026.json   OHM 1900-2026, a few non-country OHM records (Northern
                                          Cyprus, wartime occupation zones), and DeepState's map of
                                          Russian-occupied Ukraine for July 1, 2022-2026
                                          (browser/fetch_borders_1900.js)
Also reads Natural Earth's disputed areas (ne_10m_admin_0_disputed_areas.geojson and
ne_50m_admin_0_breakaway_disputed_areas.geojson) for breakaway regions OHM does not record.
"""
import json

a = json.load(open('europe-borders-sources-1795-1905.json'))
b = json.load(open('europe-borders-sources-1900-2026.json'))
out = {'meta': {'1795-1905': a['meta'], '1900-2026': b['meta']},
       'rels': {**a['rels'], **b['rels']}, 'rels4': {**a['rels4'], **b['extra']},
       'ways': {**a['ways'], **b['ways']}, 'cshapes': a['cshapes'], 'deepstate': b['deepstate']}

# breakaway regions from Natural Earth: key -> (file, NAME/BRK_NAME)
NE = {'crimea': ('ne_10m_admin_0_disputed_areas.geojson', 'Crimea'),
      'dpr': ('ne_10m_admin_0_disputed_areas.geojson', "Donetsk People's Republic"),
      'lpr': ('ne_10m_admin_0_disputed_areas.geojson', "Luhansk People's Republic"),
      'transnistria': ('ne_10m_admin_0_disputed_areas.geojson', 'Transnistria'),
      'abkhazia': ('ne_10m_admin_0_disputed_areas.geojson', 'Abkhazia'),
      'south-ossetia': ('ne_10m_admin_0_disputed_areas.geojson', 'South Ossetia'),
      'artsakh-1994': ('ne_50m_admin_0_breakaway_disputed_areas.geojson', 'Artsakh'),
      'artsakh-2020': ('ne_10m_admin_0_disputed_areas.geojson', 'Artsakh')}
ne = {}
for k, (fn, name) in NE.items():
    feats = [f for f in json.load(open(fn))['features'] if f['properties'].get('BRK_NAME') == name]
    assert len(feats) == 1, (k, len(feats))
    ne[k] = feats[0]['geometry']
out['naturalearth'] = ne
json.dump(out, open('europe-borders-sources.json', 'w'), separators=(',', ':'))
print('rels', len(out['rels']), 'rels4', len(out['rels4']), 'ways', len(out['ways']), 'deepstate years', sorted(out['deepstate']), 'ne', sorted(ne))
