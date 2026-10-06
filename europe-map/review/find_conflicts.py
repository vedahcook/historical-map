# Step 2 of the check of events and places against the map's borders (see review/README.md): compares what each
# event or place says (Wikidata, cached by review/fetch_wd.py) with who the map says held the spot, year by year,
# and writes every disagreement as a question for review to review/candidates.json.
#   cd europe-map && python3 review/find_conflicts.py          (needs page_data.json and topo.json: see tests/README.md)
# Tests:
#   capture   an event that took a city ("Siege of", "Capture of", "Fall of"...) whose winner the map does not show
#             holding the city right after it: either later or earlier (a date question) or not at all
#   held      a defended city: the winner already held it, but the map hands the city to someone else right then
#   ruler     a battle, siege or massacre in a city whose participants do not include whoever the map says held it
#   flip      a city that changes ruler and changes back within 10 years with no event recorded in those years
#   placed    an event filed under a city but whose own coordinates are more than 25 km away
# Ruler names are compared loosely (by country: "Kingdom of Hungary" and "Hungarian" match; a ruler's overlord counts),
# so a question can still be only a naming difference; the next step (review/triage) sorts that out.
import json, math, re, sys, os, unicodedata, collections
sys.path.insert(0, 'cities')

WD = json.load(open('review/wd_facts.json'))
D = json.load(open('/tmp/mapbuild/page_data.json'))
U, NM, DS = D['units'], D['names'], D['desc']
ERAS = [dict(e, data=json.load(open(e['src'])) if e.get('src') else D['late']) for e in D['eras']]
LABELS = {}
for e in ERAS: LABELS.update({int(y): rows for y, rows in e['data']['labels'].items()})
CITY = D['cities']; N465 = 465
EV = json.load(open('city-events.json')); KINDS = [k[0] for k in EV['kinds']]
PLACES = json.load(open('places.json'))['p']
rows = [l.rstrip('\n').split('|') for l in open('cities.txt') if l.strip() and not l.startswith('#')]
LONLAT = [(float(r[1]), float(r[2])) for r in rows]

def era(y): return next(i for i, e in enumerate(ERAS) if e['y0'] <= y <= e['y1'])
HIST = {}
def holder(ss, y):
    if y < 1000 or y > 2026: return None
    i = era(y); s = ss[i]
    if s < 0: return None
    runs = ERAS[i]['data']['hist'][s]; u = None
    for yy, uu, r in runs:
        if yy <= y: u = uu
        else: break
    return u if u is not None and u >= 0 else None
def uname(u, y):
    if u is None: return 'no country'
    for r in LABELS.get(y, []):
        if r[0] == u: return DS[r[6]]['t'] if r[6] >= 0 else NM[r[5]]
    return U[u]['n']

# loose names: each name becomes the set of countries it points to
GROUPS = {
    'france': 'france french vichy gaul capetian valois bourbon armagnac orleanist', 'england': 'england english britain british united kingdom great gb plantagenet',
    'scotland': 'scotland scottish scots', 'ireland': 'ireland irish', 'germany': 'germany german nazi reich wehrmacht weimar',
    'prussia': 'prussia prussian brandenburg', 'hre': 'holy roman imperial emperor', 'austria': 'austria austrian habsburg hapsburg habsburgs',
    'russia': 'russia russian soviet ussr muscovy moscow rsfsr bolshevik bolsheviks red tsardom', 'ukraine': 'ukraine ukrainian cossack cossacks zaporozhian hetmanate',
    'ottoman': 'ottoman ottomans turkey turkish turks', 'spain': 'spain spanish castile castilian aragon aragonese leon francoist nationalist',
    'portugal': 'portugal portuguese', 'poland': 'poland polish commonwealth piast jagiellonian', 'lithuania': 'lithuania lithuanian',
    'sweden': 'sweden swedish swedes', 'denmark': 'denmark danish danes', 'norway': 'norway norwegian', 'netherlands': 'netherlands dutch holland provinces batavian',
    'belgium': 'belgium belgian', 'hungary': 'hungary hungarian hungarians magyar', 'bohemia': 'bohemia bohemian czech czechoslovakia czechoslovak hussite hussites moravia',
    'venice': 'venice venetian', 'genoa': 'genoa genoese', 'milan': 'milan milanese sforza visconti', 'florence': 'florence florentine tuscany tuscan medici',
    'papal': 'papal pope holy see papacy', 'naples': 'naples neapolitan sicilies', 'sicily': 'sicily sicilian', 'savoy': 'savoy sardinia piedmont sardinian',
    'italy': 'italy italian', 'byzantine': 'byzantine byzantium nicaea nicaean epirus trebizond', 'serbia': 'serbia serbian serbs yugoslavia yugoslav',
    'bulgaria': 'bulgaria bulgarian bulgarians', 'greece': 'greece greek hellenic', 'romania': 'romania romanian wallachia moldavia', 'croatia': 'croatia croatian',
    'bosnia': 'bosnia bosnian', 'montenegro': 'montenegro montenegrin', 'albania': 'albania albanian', 'teutonic': 'teutonic order knights livonian',
    'burgundy': 'burgundy burgundian', 'bavaria': 'bavaria bavarian', 'saxony': 'saxony saxon', 'switzerland': 'switzerland swiss confederacy',
    'crimea': 'crimea crimean', 'tatar': 'tatar tatars horde mongol mongols', 'persia': 'persia persian iran iranian safavid qajar', 'arab': 'arab arabs caliphate umayyad abbasid',
    'georgia': 'georgia georgian', 'armenia': 'armenia armenian', 'finland': 'finland finnish', 'estonia': 'estonia estonian', 'latvia': 'latvia latvian',
    'morocco': 'morocco moroccan', 'algeria': 'algeria algerian algiers', 'tunisia': 'tunisia tunisian tunis', 'navarre': 'navarre navarrese', 'granada': 'granada nasrid',
    'normandy': 'normandy norman normans', 'brittany': 'brittany breton', 'flanders': 'flanders flemish', 'aquitaine': 'aquitaine gascony gascon',
    'transylvania': 'transylvania transylvanian', 'seljuk': 'seljuk seljuks seljuq seljuqs zengid zengids artuqid artuqids atabeg danishmend danishmendids',
    'mamluk': 'mamluk mamluks', 'ayyubid': 'ayyubid ayyubids', 'timurid': 'timurid timurids timur', 'kievan': 'kievan rus kyivan', 'novgorod': 'novgorod novgorodian',
    'galicia': 'galicia halych galicia volhynia volhynian', 'kazan': 'kazan', 'crusader': 'crusader crusaders antioch edessa jerusalem tripoli templar templars hospitaller hospitallers',
}
TOK_EXTRA = {'hispanic': 'spain', 'castilian': 'spain', 'bourbon': 'france', 'confederate': None}
TOK = {w: g for g, ws in GROUPS.items() for w in ws.split()}
TOK.update({w: g for w, g in TOK_EXTRA.items() if g})
# countries that count as the same side for this purpose (an empire and its crown lands, a kingdom and its fiefs)
RELATED = [('austria', 'hre'), ('bohemia', 'hre'), ('bavaria', 'hre'), ('saxony', 'hre'), ('prussia', 'germany'), ('prussia', 'hre'),
           ('spain', 'naples'), ('spain', 'sicily'), ('spain', 'milan'),
           ('france', 'normandy'), ('france', 'brittany'), ('france', 'aquitaine'), ('france', 'burgundy'), ('france', 'flanders'),
           ('england', 'normandy'), ('england', 'aquitaine'), ('england', 'scotland'), ('england', 'ireland'), ('poland', 'lithuania'),
           ('russia', 'ukraine'), ('russia', 'kievan'), ('russia', 'novgorod'), ('ottoman', 'crimea'), ('ottoman', 'tatar'), ('seljuk', 'ottoman'),
           ('denmark', 'norway'), ('sweden', 'finland'), ('savoy', 'italy'), ('naples', 'sicily'), ('hungary', 'croatia'), ('hungary', 'transylvania')]
REL = collections.defaultdict(set)
for a, b in RELATED: REL[a].add(b); REL[b].add(a)
def keys(name):
    if not name: return set()
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    k = {TOK[w] for w in re.findall(r'[a-z]+', s) if w in TOK}
    return k | {r for x in k for r in REL[x]}
def ukeys(u, y):
    if u is None: return set()
    k = keys(uname(u, y)) | keys(U[u]['n'])
    if U[u].get('ov') is not None: k |= keys(U[U[u]['ov']]['n'])
    return k
def lab(q): return WD['labels'].get(q) or WD['items'].get(q, {}).get('n') or q
RES = json.load(open('review/wp_results.json')) if os.path.exists('review/wp_results.json') else {}
VICTORY = re.compile(r"([^.;,()]{2,60}?)\s+victory", re.I)
def winner(q):
    # who won, as (keys, words): Wikidata's winner, else the Wikipedia infobox's "X victory"
    f = WD['items'].get(q, {}); w = [lab(v) for v in f.get('P1346', []) if isinstance(v, str)]
    if w: return set().union(*(keys(x) for x in w)), ', '.join(w)
    r = RES.get(q, {}).get('result', '')
    if not r or re.search(r'inconclusive|indecisive|stalemate|disputed|unclear|status quo', r, re.I): return set(), ''
    m = VICTORY.search(r)
    if not m: return set(), ''
    return keys(m.group(1)), m.group(0).strip()
def km(a, b):
    R = 6371; la1, la2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0]); dp = la2 - la1
    return 2 * R * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dl / 2) ** 2))

CAPTURE = re.compile(r'^(siege|capture|fall|conquest|recapture|liberation|occupation|surrender|storming|reconquest|annexation|taking)\b', re.I)      # (not a sack: the sackers seldom stayed)
WARLIKE = {'war', 'violence', 'uprising'}
out = []
def add(test, where, y, q, text, **kw):
    out.append(dict(test=test, where=where, y=y, q=q, text=text, **kw))
def around(ss, y, a=-3, b=3):
    seq, last = [], object()
    for yy in range(y + a, y + b + 1):
        u = holder(ss, yy)
        if u != last: seq.append([yy, uname(u, yy)]); last = u
    return seq

def check_event(ss, where, ci, y, name, q, kind):
    f = WD['items'].get(q, {})
    part = [v for v in f.get('P710', []) if isinstance(v, str)]
    if kind not in WARLIKE or y < 1000: return
    h0, h1 = holder(ss, y - 1), holder(ss, y)
    wk, wtxt = winner(q); win = [wtxt] if wtxt else []
    if CAPTURE.match(name) and wk:
        k0 = ukeys(h0, y - 1)
        if not (wk & k0):      # the winner did not hold it before: the map (July 1 of each year) should show the winner from then on
            d = (f.get('P582') or f.get('P585') or [''])[0]
            first = y if re.match(r'\d{4}-0[1-6]', d or '') else y + 1 if re.match(r'\d{4}-(0[7-9]|1[0-2])', d or '') else None
            after = [yy for yy in ([first] if first else [y, y + 1]) if wk & ukeys(holder(ss, yy), yy)]
            if not after:
                near = [yy for yy in range(y - 15, y + 16) if wk & ukeys(holder(ss, yy), yy)]
                if near:
                    add('capture', where, y, q, f"{name} ({y}). Result: {wtxt}. The map shows the winners holding {where} from {near[0]}, not from {first or y}." if near[0] > y
                        else f"{name} ({y}). Result: {wtxt}. The map already shows the winners holding {where} in {near[0]}, before the event.",
                        ci=ci, map=around(ss, y, -16, 16), winner=wtxt, kind='date')
                else:
                    add('capture', where, y, q, f"{name} ({y}). Result: {wtxt}. The map never shows the winners holding {where} in the 15 years around it (it shows {uname(h1, y)}).",
                        ci=ci, map=around(ss, y, -4, 6), winner=wtxt, kind='never')
            return
        else:      # the holder won (a defense): the map should not hand the city to someone else then
            for yy in range(y, y + 2):
                h = holder(ss, yy)
                if h != h0 and not (wk & ukeys(h, yy)):
                    add('held', where, y, q, f"{name} ({y}). Result: {wtxt}, so the defenders kept {where}; but the map hands it to {uname(h, yy)} in {yy}.", ci=ci, map=around(ss, y, -3, 5), winner=wtxt)
                    return
            return
    sides = set().union(*(keys(lab(p)) for p in part)) if part else set()
    if len(part) >= 2 and sides:
        hk = ukeys(h1, y) | ukeys(h0, y - 1) | ukeys(holder(ss, y + 1), y + 1)      # (an event late in the year: the next year's ruler too)
        if hk and not (hk & sides):
            add('ruler', where, y, q, f"{name} ({y}): the sides were {', '.join(dict.fromkeys(lab(p) for p in part))}; the map says {uname(h1, y)} held {where}.",
                ci=ci, map=around(ss, y, -2, 2), sides=list(dict.fromkeys(lab(p) for p in part)))

evs_by_city = collections.defaultdict(list)
for ci, y, md, ki, sl, n, t, end, q in EV['ev']:
    evs_by_city[ci].append((y, end or y, KINDS[ki], n))
    c = CITY[ci]; f = WD['items'].get(q, {})
    xy = f.get('P625', [None])[0] if f.get('P625') else None
    if xy and km(xy, LONLAT[ci]) > 25:
        add('placed', c[0], y, q, f"{n} ({y}) is filed under {c[0]}, but Wikidata places it {round(km(xy, LONLAT[ci]))} km away ({xy[1]:.3f}, {xy[0]:.3f}).", ci=ci, at=xy, km=round(km(xy, LONLAT[ci])))
        continue      # (its ruler is that of another spot: not compared with the city's)
    check_event(c[3], c[0], ci, y, n, q, KINDS[ki])
for p in PLACES:
    k = {'war': 'war', 'memorial': 'violence'}.get(p['k'], 'other')
    check_event(p['ss'], p['n'], None, p['y'] if not re.match(r'\d', p['when'] or '') else int(re.match(r'\d+', p['when']).group()), p['n'], p['q'], k)
# the wider events (wider-events.json) that struck each city: (name, first year, last year)
WIDE = collections.defaultdict(list)
for n, t, q, a, b, cs in json.load(open('wider-events.json'))['ev']:
    ids = range(len(CITY)) if cs == 'all' else [i for i in range(len(CITY)) if i not in set(cs['not'])] if isinstance(cs, dict) else cs
    for i in ids: WIDE[i].append((n, a, b))
# brief flips in the large cities: A, then B for 10 years or less, then A again, with no event in the city then
for ci in range(N465):
    ss = CITY[ci][3]; seq = []
    for y in range(1000, 2027):
        u = holder(ss, y)
        if not seq or seq[-1][1] != u: seq.append([y, u])
    for i in range(1, len(seq) - 1):
        a, b, c2 = seq[i - 1], seq[i], seq[i + 1]
        dur = c2[0] - b[0]
        if a[1] == c2[1] and dur <= 10 and a[1] is not None and not (b[1] is not None and U[b[1]].get('o')):
            evs = [e for e in evs_by_city[ci] if e[0] <= c2[0] + 2 and e[1] >= b[0] - 2]
            wars = [w for w in WIDE.get(ci, []) if w[1] <= c2[0] + 1 and w[2] >= b[0] - 1]
            if not evs and not wars:
                add('flip', CITY[ci][0], b[0], None, f"The map shows {CITY[ci][0]} held by {uname(b[1], b[0])} for {dur} year{'s' if dur > 1 else ''} ({b[0]}–{c2[0] - 1}), between years of {uname(a[1], b[0] - 1)}, with no event recorded in the city then.",
                    ci=ci, map=around(ss, b[0], -3, dur + 2))
json.dump(out, open('review/candidates.json', 'w'), ensure_ascii=False, indent=0)
print(len(out), 'questions:', dict(collections.Counter(o['test'] + ('/' + o['kind'] if o.get('kind') else '') for o in out)))
print('in the 465 large cities:', sum(1 for o in out if o.get('ci') is not None and o['ci'] < N465))
