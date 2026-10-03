"""City views page for the pilot cities plus batch 1: views from work/views.json, events from the map's Wikidata list
(for the new cities), the pilot's sample events, population changes and pictures for the four pilot cities."""
import json, os, re, sys
sys.path.insert(0, '/home/claude/views')
from pilot_views import V
from pilot_events import E, POP, DAY
from pilot_event_images import EI
cd = json.load(open('city_data.json')); fl = json.load(open('flags_data.json')); sizes = json.load(open('full_sizes.json'))
NEW = json.load(open('/home/claude/cv/work/views.json'))
PILOT = {'cologne': 'Cologne', 'vienna': 'Vienna', 'paris': 'Paris', 'istanbul': 'Istanbul'}
MAPNAME = {'saint-petersburg': 'St. Petersburg', 'krakow': 'Kraków'}
ORDER = ['london', 'paris', 'vienna', 'berlin', 'saint-petersburg', 'moscow', 'istanbul', 'budapest', 'warsaw', 'prague', 'naples', 'madrid',
         'munich', 'amsterdam', 'dresden', 'milan', 'cologne', 'copenhagen', 'rome', 'lisbon', 'stockholm', 'nuremberg', 'brussels', 'edinburgh',
         'florence', 'venice', 'seville', 'krakow', 'athens']
# the map's events (Wikidata): row = [city index, year, MMDD, kind, sitelinks, label, enwiki title or '' (same as label) or a QID, end year]
names = [l.split('|')[0] for l in open('/home/claude/historical-map/europe-map/cities.txt') if not l.startswith('#') and l.strip()]
EV = json.load(open('/home/claude/historical-map/europe-map/city-events.json'))['ev']
EPI = re.compile(r'plague|cholera|epidemic|pandemic|influenza|typhus|smallpox|black death|outbreak', re.I)
def kind(k, label):
    return ['war', 'war', 'revolt', 'politics', 'faith', 'politics', 'fire', 'epidemic' if EPI.search(label) else 'quake', 'building', 'politics'][k]
Y0, Y1 = 1000, cd['Y1']; GAP = 21 / 350 * (Y1 - Y0)
def fits(evs):
    rowEnd = []
    for e in sorted(evs, key=lambda e: e['y']):
        r = next((i for i, y in enumerate(rowEnd) if e['y'] - y >= GAP), -1)
        if r < 0:
            if len(rowEnd) >= 4: return False
            rowEnd.append(e['y'])
        else: rowEnd[r] = e['y']
    return True
def wd_events(name):
    i = names.index(name); rows = sorted((r for r in EV if r[0] == i and Y0 <= r[1] <= Y1 and not re.match(r'^Q\d+$', r[6] or '')), key=lambda r: -r[4])
    out = []
    for r in rows:
        e = {'y': r[1], 'k': kind(r[3], r[5]), 'n': r[5], 'x': '', 'wt': r[6] or r[5]}
        if r[2] and not r[7]: e['d'] = [r[2] // 100, str(r[2] % 100)]
        if fits(out + [e]): out.append(e)
        if len(out) >= 16: break
    return sorted(out, key=lambda e: e['y'])
def pilot_evt(city, y, k, n, x):
    wt, f, who, lab, what, lic = EI[(city, y)]
    e = {'y': y, 'k': k, 'n': n, 'x': x, 'wt': wt}
    if (city, y) in DAY: e['d'] = list(DAY[(city, y)])
    vid = f'ev-{city}-{y}'
    if f and vid in sizes: w, h = sizes[vid]; e['img'] = {'id': vid, 'who': who, 'lab': lab, 'what': what, 'lic': lic, 'f': f, 'w': w, 'h': h}
    return e
cities = {}
for key in ORDER:
    n = PILOT.get(key) or MAPNAME.get(key) or key.capitalize()
    c = cd['res'][n]
    runs = [{kk: r[kk] for kk in ('t', 'by', 'a', 'b', 'l', 'd')} for r in c['runs']]
    if key in PILOT:
        views = []
        for city, y, lab, what, who, lic, f in sorted((v for v in V if v[0] == key), key=lambda v: v[1]):
            vid = f'{city}-{y}'
            if vid not in sizes: continue
            w, h = sizes[vid]; views.append({'id': vid, 'y': y, 'lab': lab, 'what': what, 'who': who, 'lic': lic, 'f': f, 'w': w, 'h': h, **({'event': True} if vid == 'cologne-1945' else {})})
        evs = [pilot_evt(key, y, k2, n2, x2) for y, k2, n2, x2 in E[key]]
        P = dict((q[0], q[1]) for q in c['P'])
        pop = [{'a': a, 'b': b, 'j': j, 'x': x, 'pa': P[a], 'pb': P[b]} for a, b, j, x in POP[key]]
    else:
        views, evs, pop = NEW[key], wd_events(n), []
    cities[key] = {'n': n, 'P': c['P'], 'runs': runs, 'views': views, 'events': evs, 'pop': pop, 'flags': fl['res'][n]}
data = json.dumps({'Y1': cd['Y1'], 'cities': cities, 'flags': {'sheet': fl['sheet'], 'items': fl['items'], 'credits': fl['credits']}},
                  ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = open('template.html').read().replace('/*DATA*/', data).replace('/*ICONS*/', open('icons2.js').read().strip())
html = html.replace('Four cities and <span id="nviews"></span> views from Wikimedia Commons.', f'{len(cities)} cities and <span id="nviews"></span> views from Wikimedia Commons.')
html = html.replace('The events, 13 to 17 per city, are a sample written for this mockup.',
                    'Events: for Cologne, Vienna, Paris and Istanbul, a sample written for this mockup, with pictures; for the other cities, the map’s own events from Wikidata, not yet checked and without pictures.')
os.makedirs('site', exist_ok=True); open('site/city-views.html', 'w').write(html)
used = {v['id'] for c in cities.values() for v in c['views']} | {e['img']['id'] for c in cities.values() for e in c['events'] if 'img' in e}
json.dump(sorted(used), open('used.json', 'w'))
print(len(cities), 'cities;', len(used), 'pictures;', sum(len(c['events']) for c in cities.values()), 'events;', len(html) // 1024, 'KB page')
for k in ORDER: print(k, len(cities[k]['views']), 'views', len(cities[k]['events']), 'events', end=' | ')
