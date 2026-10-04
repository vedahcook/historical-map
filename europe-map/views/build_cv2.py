"""City views page for the pilot cities plus batch 1: views from work/views.json, events from the map's Wikidata list
(for the new cities), the pilot's sample events, population changes and pictures for the four pilot cities."""
import json, os, re, sys
sys.path.insert(0, '/home/claude/views')
from pilot_views import V
from pilot_events import E, POP, DAY
from pilot_event_images import EI
cd = json.load(open('city_data.json')); fl = json.load(open('flags_data.json')); sizes = json.load(open('full_sizes.json'))
NEW = {}
for vf in ['/home/claude/cv/work/views.json', '/home/claude/cv2/work/views.json', '/home/claude/cv3/work/views.json', '/home/claude/cv4/work/views.json']:
    if os.path.exists(vf): NEW.update(json.load(open(vf)))
B2 = [l.strip() for l in open('/home/claude/cv/batch2.txt') if l.strip()]
B3 = [l.strip() for l in open('/home/claude/cv/batch3.txt') if l.strip()]
slug = lambda t: re.sub(r'[^a-z]+', '-', t.lower().replace('ó', 'o')).strip('-')
PILOT = {'cologne': 'Cologne', 'vienna': 'Vienna', 'paris': 'Paris', 'istanbul': 'Istanbul'}
MAPNAME = {'saint-petersburg': 'St. Petersburg', 'krakow': 'Kraków'}
ORDER = ['london', 'paris', 'vienna', 'berlin', 'saint-petersburg', 'moscow', 'istanbul', 'budapest', 'warsaw', 'prague', 'naples', 'madrid',
         'munich', 'amsterdam', 'dresden', 'milan', 'cologne', 'copenhagen', 'rome', 'lisbon', 'stockholm', 'nuremberg', 'brussels', 'edinburgh',
         'florence', 'venice', 'seville', 'krakow', 'athens']
# the map's events (Wikidata): row = [city index, year, MMDD, kind, sitelinks, label, enwiki title or '' (same as label) or a QID, end year]
names = [l.split('|')[0] for l in open('/home/claude/historical-map/europe-map/cities.txt') if not l.startswith('#') and l.strip()]
EV = json.load(open('/home/claude/historical-map/europe-map/city-events.json'))['ev']
EPI = re.compile(r'plague|cholera|epidemic|pandemic|influenza|typhus|smallpox|black death|outbreak', re.I)
WIKI_LANG = {'fr': 'French', 'de': 'German', 'es': 'Spanish', 'it': 'Italian', 'ru': 'Russian', 'uk': 'Ukrainian', 'be': 'Belarusian', 'pl': 'Polish',
             'cs': 'Czech', 'sk': 'Slovak', 'sr': 'Serbian', 'hr': 'Croatian', 'bs': 'Bosnian', 'sl': 'Slovene', 'bg': 'Bulgarian', 'mk': 'Macedonian',
             'ro': 'Romanian', 'hu': 'Hungarian', 'el': 'Greek', 'tr': 'Turkish', 'nl': 'Dutch', 'pt': 'Portuguese', 'ca': 'Catalan', 'eu': 'Basque',
             'gl': 'Galician', 'sv': 'Swedish', 'da': 'Danish', 'no': 'Norwegian', 'nn': 'Norwegian', 'fi': 'Finnish', 'et': 'Estonian', 'lv': 'Latvian',
             'lt': 'Lithuanian', 'ka': 'Georgian', 'hy': 'Armenian', 'az': 'Azerbaijani', 'ar': 'Arabic', 'fa': 'Persian', 'he': 'Hebrew', 'sq': 'Albanian',
             'is': 'Icelandic', 'ga': 'Irish', 'cy': 'Welsh', 'lb': 'Luxembourgish', 'mt': 'Maltese', 'eo': 'Esperanto', 'la': 'Latin'}
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
    i = names.index(name); rows = sorted((r for r in EV if r[0] == i and Y0 <= r[1] <= Y1), key=lambda r: -r[4])
    out = []
    for r in rows:
        e = {'y': r[1], 'k': kind(r[3], r[5]), 'n': r[5], 'x': ''}
        link = r[6]                                  # '' / 'Title' (English), 'xx:Title' (another edition), None (no article)
        m = re.match(r'^([a-z][a-z-]*):(.+)$', link or '')
        if m: e['wt'], e['wl'], e['wn'] = m.group(2), m.group(1), WIKI_LANG.get(m.group(1), m.group(1))
        elif link is not None and not re.match(r'^Q\d+$', link): e['wt'] = link or r[5]
        if len(r) > 8 and r[8]: e['q'] = r[8]
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
KEYS = ORDER + [slug(n) for n in B2 + B3 if slug(n) in NEW]
for n in B2 + B3: MAPNAME[slug(n)] = n
for key in KEYS:
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
old = html[html.index("const cb = $('cities');"):html.index("$('year').addEventListener")]
new = '''const cb = $('cities');
const sel = document.createElement('select'); sel.id = 'citysel'; sel.setAttribute('aria-label', 'City');
for (const [k, c] of Object.entries(D.cities).sort((a, b) => a[1].n.localeCompare(b[1].n))) {
  const o = document.createElement('option'); o.value = k; o.textContent = `${c.n} (${c.views.length})`; o.selected = k === city; sel.appendChild(o);
}
sel.onchange = () => { city = sel.value; selEv = null; for (const t in scrolls) delete scrolls[t]; render(); };
cb.appendChild(sel);
'''
html = html.replace(old, new)
html = html.replace('.cities button[aria-pressed="true"]', '.cities select { font: inherit; font-weight: 500; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; min-width: 240px; max-width: 100%; }\n.cities button[aria-pressed="true"]')
html = html.replace('No events listed before ${c.events[0].y}.', "${c.events.length ? 'No events listed before ' + c.events[0].y + '.' : 'No events listed for this city yet.'}")
html = html.replace('Pick a city and move the year', 'Pick a city (the number is how many views it has) and move the year')
os.makedirs('site', exist_ok=True); open('site/city-views.html', 'w').write(html)
used = {v['id'] for c in cities.values() for v in c['views']} | {e['img']['id'] for c in cities.values() for e in c['events'] if 'img' in e}
json.dump(sorted(used), open('used.json', 'w'))
print(len(cities), 'cities;', len(used), 'pictures;', sum(len(c['events']) for c in cities.values()), 'events;', len(html) // 1024, 'KB page')
print('views per city:', sorted((len(c['views']) for c in cities.values())))
