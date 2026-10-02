"""Events in each city, and people born or died there, for the city popups and the event icons on the map.

Usage (in europe-map/), with the files saved from browser/fetch_city_extras.js in a folder WD:
  python3 cities/make_extras.py select WD    -> WD/want.json: the Wikidata items whose names are needed (run the
                                                 browser step 'details' with HM.want set to it, save as WD/details.json)
  python3 cities/make_extras.py build WD     -> city-events.json and city-people.json beside the page
Input files in WD: ev.json ({qid: city items in cities.txt order, ev: events}), under.json (each event class's root
classes, from the 'roots' step with cities/event_kinds.py's ROOTS), pp.json (people), details.json (names).

Choice:
- An event's kind comes from its classes (cities/event_kinds.py). Sports, festivals, awards, accidents and other
  kinds the map does not show are left out.
- An event recorded in more than three cities (a massacre that spread across France) is kept for the largest.
- Each city keeps its most written-about events (most Wikipedia articles), at most 30 for the 465 large cities and 12
  for the towns: first no more than a fifth of them from any one century, so the early centuries keep some, then the
  best of the rest.
- People: those Wikidata records as born or died in the city (or in a place within it), with at least 10 Wikipedia
  articles, who lived after 1000; each city keeps its most written-about, at most 14 (large cities) or 6, again
  spread over the centuries."""
import json, sys, re, collections
sys.path.insert(0, 'cities')
from event_kinds import KINDS, DROP

mode, WD = sys.argv[1], sys.argv[2]
E = json.load(open(f'{WD}/ev.json')); qid = E['qid']; ev = E['ev']
BIG = 465                                       # the first cities in cities.txt: Europe's largest
idx = collections.defaultdict(list)
for i, q in enumerate(qid):
    if q: idx[q].append(i)

def kind_of(e, under):
    roots = set()
    for c in e['cls']: roots |= set(under.get(c, []))
    for ki, (k, _, qs) in enumerate(KINDS):
        if roots & set(qs): return ki
    return None

def spread(items, cap, year):
    """the cap highest-scoring items, spread over the centuries: first at most a fifth of the cap (at least 2) from any
    one century, then the best of the rest"""
    per = max(2, round(cap * 0.2)); out, n = [], collections.Counter()
    ranked = sorted(items, key=lambda x: -x['sl'])
    for it in ranked:
        y = year(it); c = (y // 100) if y is not None else 99
        if n[c] >= per: continue
        out.append(it); n[c] += 1
        if len(out) >= cap: return out
    for it in ranked:
        if len(out) >= cap: break
        if not any(o is it for o in out): out.append(it)
    return out

def choose_events():
    under = json.load(open(f'{WD}/under.json'))
    per_city = collections.defaultdict(list)
    for q, e in ev.items():
        ki = kind_of(e, under)
        if ki is None: continue
        y = int(e['t'][:4])
        if not (1000 <= y <= 2026): continue
        if 'Q114342413' in e['cls']: continue       # a cancelled event (the 1940 and 1944 Olympic Games)
        cities = sorted({i for c in e['c'] for i in idx.get(c, [])})
        if len(cities) > 3: cities = cities[:1]     # spread over many places (a massacre across France): the largest city
        for i in cities: per_city[i].append({'q': q, 'y': y, 'ki': ki, 'sl': e['sl'], 't': e['t'], 'p': e['p'], 'end': e['end']})
    return {i: spread(xs, 30 if i < BIG else 12, lambda x: x['y']) for i, xs in per_city.items()}

def choose_people():
    pp = json.load(open(f'{WD}/pp.json'))
    per_city = collections.defaultdict(list)
    for q, p in pp.items():
        for c, w in p['at'].items():
            for i in idx.get(c, []): per_city[i].append({'q': q, 'w': ''.join(sorted(set(w))), 'b': p['b'], 'd': p['d'], 'sl': p['sl']})
    return {i: spread(xs, 14 if i < BIG else 6, lambda x: x['b'] if x['b'] is not None else x['d']) for i, xs in per_city.items()}

if mode == 'select':
    evs, pps = choose_events(), choose_people()
    want = sorted({x['q'] for xs in evs.values() for x in xs} | {x['q'] for xs in pps.values() for x in xs})
    json.dump(want, open(f'{WD}/want.json', 'w'))
    print('events', sum(map(len, evs.values())), 'in', len(evs), 'cities; people', sum(map(len, pps.values())), 'in', len(pps), 'cities; names needed', len(want))
    print('by kind', collections.Counter(KINDS[x['ki']][0] for xs in evs.values() for x in xs))
    sys.exit()

# ---------- build ----------
L = json.load(open(f'{WD}/details.json'))          # q -> [label, description, enwiki title]
def title(q):
    l, _, t = L.get(q, [q, '', ''])
    return '' if t == l else t if t else q          # '' = the article's title is the name; Q… = no English article
def name(q):
    l = L.get(q, [q])[0]
    return l[0].upper() + l[1:] if l and l[0].islower() and not l.startswith('de ') else l
def role(q):
    d = L.get(q, ['', '', ''])[1] or ''
    d = re.sub(r'\s*\([^()]*\d[^()]*\)?\s*$', '', d).strip()        # dates at the end: "(1756–1791)", "(*1872 – †1934)", "(born 1954)
    if len(d) > 58: d = d[:56].rsplit(' ', 1)[0].rstrip(',;:') + '…'
    return d

evs, pps = choose_events(), choose_people()
CANCELLED = {'1916 Summer Olympics', '1940 Summer Olympics', '1944 Summer Olympics', '1940 Winter Olympics', '1944 Winter Olympics'}   # never held
kinds = [[k, t] for k, t, _ in KINDS]
rows = []
for i in sorted(evs):
    for x in sorted(evs[i], key=lambda x: (x['t'], x['q'])):
        md = int(x['t'][5:7]) * 100 + (int(x['t'][8:10]) if x['p'] >= 11 else 0) if x['p'] >= 10 else 0
        # an end year only for what lasts (a siege, an uprising, an epidemic, a council), not a treaty's expiry
        end = x['end'] if x['end'] and x['end'] > x['y'] and x['end'] - x['y'] <= 60 and KINDS[x['ki']][0] in ('war', 'uprising', 'disaster', 'religion', 'violence') else 0
        if name(x['q']) in CANCELLED or re.fullmatch(r'Q\d+', name(x['q'])): continue      # never held, or no name in any language
        rows.append([i, x['y'], md, x['ki'], x['sl'], name(x['q']), title(x['q']), end])
json.dump({'source': 'Wikidata (CC0), gathered October 2, 2026', 'kinds': kinds, 'ev': rows}, open('city-events.json', 'w'), ensure_ascii=False, separators=(',', ':'))
prow = []
for i in sorted(pps):
    for x in sorted(pps[i], key=lambda x: (x['b'] if x['b'] is not None else x['d'] or 0, x['q'])):
        prow.append([i, x['w'], x['b'], x['d'], x['sl'], name(x['q']), role(x['q']), title(x['q'])])
json.dump({'source': 'Wikidata (CC0), gathered October 2, 2026', 'pp': prow}, open('city-people.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import os
print('city-events.json', len(rows), os.path.getsize('city-events.json') // 1024, 'KB; city-people.json', len(prow), os.path.getsize('city-people.json') // 1024, 'KB')
