# Step 1 of the check of events and places against the map's borders (see review/README.md):
# what Wikidata says about each city event (city-events.json) and each place (places.json): its participants (P710),
# winner (P1346), location (P276), coordinates (P625), dates (P585, P580, P582) and what it is (P31), plus the English
# names of every item those point to. Cached in review/wd_facts.json; run again to fetch only what is missing.
#   cd europe-map && python3 review/fetch_wd.py
import json, os, sys, time, urllib.request, urllib.parse

OUT = 'review/wd_facts.json'
UA = {'User-Agent': 'historical-map/1.0 (https://github.com/vedahcook/historical-map)'}
PROPS = ['P710', 'P1346', 'P276', 'P625', 'P585', 'P580', 'P582', 'P31', 'P17', 'P361']

def get(ids, props):
    url = 'https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode({'action': 'wbgetentities', 'format': 'json', 'ids': '|'.join(ids), 'props': props, 'languages': 'en'})
    for k in range(30):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))['entities']
        except Exception as e: print('retry', e, file=sys.stderr); time.sleep(min(60, 5 + 4 * k))
    raise SystemExit('Wikidata keeps refusing; try again later')

def val(snak):
    dv = snak.get('datavalue', {}).get('value')
    if isinstance(dv, dict) and 'id' in dv: return dv['id']
    if isinstance(dv, dict) and 'time' in dv: return dv['time'][:11].lstrip('+')
    if isinstance(dv, dict) and 'latitude' in dv: return [round(dv['longitude'], 5), round(dv['latitude'], 5)]
    return None

if __name__ == '__main__':
    cache = json.load(open(OUT)) if os.path.exists(OUT) else {'items': {}, 'labels': {}}
    ev = json.load(open('city-events.json'))['ev']
    qs = sorted({e[8] for e in ev if e[8]} | {p['q'] for p in json.load(open('places.json'))['p']})
    todo = [q for q in qs if q not in cache['items']]
    print(len(qs), 'items,', len(todo), 'to fetch')
    for i in range(0, len(todo), 50):
        for q, ent in get(todo[i:i + 50], 'claims|labels').items():
            c = ent.get('claims', {})
            cache['items'][q] = {'n': ent.get('labels', {}).get('en', {}).get('value'),
                                 **{p: [v for v in (val(s['mainsnak']) for s in c.get(p, [])) if v is not None] for p in PROPS if p in c}}
        time.sleep(1)
        if i % 500 == 0: json.dump(cache, open(OUT, 'w'), ensure_ascii=False); print(i, file=sys.stderr)
    refs = sorted({v for it in cache['items'].values() for p in ('P710', 'P1346') for v in it.get(p, []) if isinstance(v, str) and v.startswith('Q')} - set(cache['labels']))      # (the sides' names: all the check needs)
    print(len(refs), 'names to fetch')
    for i in range(0, len(refs), 50):
        for q, ent in get(refs[i:i + 50], 'labels').items():
            cache['labels'][q] = ent.get('labels', {}).get('en', {}).get('value')
        time.sleep(2)
        if i % 500 == 0: json.dump(cache, open(OUT, 'w'), ensure_ascii=False); print('names', i, file=sys.stderr)
    json.dump(cache, open(OUT, 'w'), ensure_ascii=False)
    print('done:', len(cache['items']), 'items,', len(cache['labels']), 'names')
