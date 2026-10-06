# Step 1b: Wikidata seldom says who won a battle or siege, so the outcome comes from the English Wikipedia article's
# infobox instead: its "result" and "territory" lines, for every battle, siege, massacre or uprising in
# city-events.json and every place. Cached in review/wp_results.json (run again to fetch only what is missing).
#   cd europe-map && python3 review/fetch_results.py
import json, os, re, sys, time, urllib.request, urllib.parse

OUT = 'review/wp_results.json'
UA = {'User-Agent': 'historical-map/1.0 (https://github.com/vedahcook/historical-map)'}

def get(titles):
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'redirects': 1, 'prop': 'revisions', 'rvprop': 'content',
                                                                          'rvslots': 'main', 'titles': '|'.join(titles)})
    for k in range(30):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90))['query']
        except Exception as e: print('retry', e, file=sys.stderr); time.sleep(min(60, 5 + 4 * k))
    raise SystemExit('Wikipedia keeps refusing; try again later')

def field(text, name):
    m = re.search(r'^\s*\|\s*' + name + r'\s*=(.*?)(?=^\s*\||^\}\})', text, re.M | re.S)
    if not m: return ''
    v = m.group(1)
    v = re.sub(r'<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->', '', v, flags=re.S)
    v = re.sub(r'\{\{(?:[^{}]|\{\{[^{}]*\}\})*\}\}', lambda t: ' '.join(p for p in t.group(0)[2:-2].split('|')[1:] if '=' not in p) if re.match(r'\{\{\s*(?:plainlist|ubl|unbulleted list|hlist|flatlist)', t.group(0), re.I) else '', v)
    v = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', v)
    v = re.sub(r"'''?|<br\s*/?>|\*", ' ', v)
    return re.sub(r'\s+', ' ', v).strip()[:300]

if __name__ == '__main__':
    cache = json.load(open(OUT)) if os.path.exists(OUT) else {}
    ev = json.load(open('city-events.json')); kinds = [k[0] for k in ev['kinds']]
    want = {}
    for ci, y, md, ki, sl, n, t, end, q in ev['ev']:
        if kinds[ki] in ('war', 'violence', 'uprising') and t is not None and not re.match(r'^[a-z][a-z-]*:|^Q\d+$', t or ''):
            want[q] = t or n
    for p in json.load(open('places.json'))['p']:
        want[p['q']] = p['w'] or p['n']
    todo = [(q, t) for q, t in want.items() if q not in cache]
    print(len(want), 'articles,', len(todo), 'to fetch')
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]; d = get([t for _, t in batch])
        to = {r['from']: r['to'] for r in d.get('normalized', []) + d.get('redirects', [])}
        pages = {p['title']: p for p in d['pages'].values()}
        for q, t in batch:
            tt = to.get(to.get(t, t), to.get(t, t)); p = pages.get(tt)
            text = p['revisions'][0]['slots']['main']['*'] if p and 'revisions' in p else ''
            cache[q] = {'result': field(text, 'result'), 'territory': field(text, 'territory')}
        time.sleep(2)
        if i % 500 == 0: json.dump(cache, open(OUT, 'w'), ensure_ascii=False); print(i, file=sys.stderr)
    json.dump(cache, open(OUT, 'w'), ensure_ascii=False)
    print('done:', len(cache), 'with a result:', sum(1 for v in cache.values() if v['result']))
