import json, os, re
from pilot_views import V
from pilot_events import E, POP, DAY
from pilot_event_images import EI
cd = json.load(open('city_data.json')); sizes = json.load(open('full_sizes.json'))
NAMES = {'cologne': 'Cologne', 'vienna': 'Vienna', 'paris': 'Paris', 'istanbul': 'Istanbul'}
V = list(V)
if 'vienna-2018' not in sizes:      # the better modern view hasn't been downloaded yet: use the Kahlenberg panorama
    V = [v for v in V if not (v[0] == 'vienna' and v[1] == 2018)] + [('vienna', 2013, '2013', 'Panorama from the Kahlenberg, photograph', 'Peter Ettel', 'CC BY-SA 3.0', 'Panorama Wien, Kahlenberg.jpg')]
cities = {}
def evt(city, y, kind, n, x):
    wt, f, who, lab, what, lic = EI[(city, y)]
    e = {'y': y, 'k': kind, 'n': n, 'x': x, 'wt': wt}
    if (city, y) in DAY: e['d'] = list(DAY[(city, y)])
    vid = f'ev-{city}-{y}'
    if f and vid in sizes:
        w, h = sizes[vid]
        e['img'] = {'id': vid, 'who': who, 'lab': lab, 'what': what, 'lic': lic, 'f': f, 'w': w, 'h': h}
    return e
for k, n in NAMES.items():
    c = cd['res'][n]
    views = []
    for city, y, lab, what, who, lic, f in sorted((v for v in V if v[0] == k), key=lambda v: v[1]):
        vid = f'{city}-{y}'; w, h = sizes[vid]
        views.append({'id': vid, 'y': y, 'lab': lab, 'what': what, 'who': who, 'lic': lic, 'f': f, 'w': w, 'h': h, **({'event': True} if vid == 'cologne-1945' else {})})
    cities[k] = {'n': n, 'P': c['P'], 'runs': [{kk: r[kk] for kk in ('t', 'by', 'a', 'b', 'l', 'd')} for r in c['runs']], 'views': views, 'events': [evt(k, y, k2, n2, x2) for y, k2, n2, x2 in E[k]], 'pop': [{'a': a, 'b': b, 'j': j, 'x': x, 'pa': dict((q[0], q[1]) for q in c['P'])[a], 'pb': dict((q[0], q[1]) for q in c['P'])[b]} for a, b, j, x in POP[k]]}
fl = json.load(open('flags_data.json'))
for k, n in NAMES.items(): cities[k]['flags'] = fl['res'][n]
data = json.dumps({'Y1': cd['Y1'], 'cities': cities, 'flags': {'sheet': fl['sheet'], 'items': fl['items'], 'credits': fl['credits']}}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = open('template.html').read().replace('/*DATA*/', data).replace('/*ICONS*/', open('icons2.js').read().strip())
os.makedirs('site', exist_ok=True)
open('site/city-views.html', 'w').write(html)
used = {v['id'] for c in cities.values() for v in c['views']} | {e['img']['id'] for c in cities.values() for e in c['events'] if 'img' in e}
print(len(used), 'views;', len(html) // 1024, 'KB page')
json.dump(sorted(used), open('used.json', 'w'))
