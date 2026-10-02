"""Pick the towns to add to cities.txt, so the map can show ten cities on screen however far in the viewer zooms.

Step 1 (python3 towns_select.py classes hm-candidates.json): from every Wikidata item in the map's area with a
population figure of 20,000 or more (browser query, saved as hm-candidates.json), keep the towns and cities: items
that are a kind of human settlement, or a municipality in a country where the municipality is the town (France,
Italy, Spain, Portugal, the Netherlands, Belgium, Algeria, Tunisia). Parts of cities (boroughs, quarters, districts) are left
out. Writes towns_qids.json.

Step 2 (python3 towns_select.py dedupe hm-series.json, the towns' Wikidata figures, labels and Wikipedia
articles, fetched in the browser): drop the towns already in cities.txt (within 3 km, or within 15 km
with a similar name) and duplicates among the new ones (a town and its municipality),
then write towns_input.json, the list of Wikipedia articles browser/fetch_town_tables.js reads."""
import json, math, re, sys, unicodedata

# classes whose items are the town itself although Wikidata doesn't file them under "human settlement"
MUNI = {'Q484170': 'commune of France', 'Q747074': 'comune of Italy', 'Q2074737': 'municipality of Spain',
        'Q33146843': 'municipality of Catalonia', 'Q123754112': 'municipality of the Valencian Community',
        'Q2039348': 'municipality of the Netherlands', 'Q493522': 'municipality of Belgium',
        'Q2989398': 'commune of Algeria', 'Q41067667': 'municipality of Tunisia', 'Q13217644': 'municipality of Portugal'}
# parts of a city, groups of cities, and places that no longer exist: left out even when filed as settlements
PART = re.compile(r'neighbo|suburb|quarter|mahalle|area of London|municipal part|constituent locality|metropolitan (area|region|county|borough|city of Italy|association)|'
                  r'agglomeration|conurbation|city district|district of (Moscow|Budapest|Vienna|Madrid|Barcelona|Valencia|'
                  r'Palermo|The Hague|Cartagena|Prague)|districts of|microdistrict|raion of city|locality of|Ortsteil|'
                  r'Stadtbezirk|okrug of Saint|borough of (Munich|Berlin|Hamburg|Bologna)|zone of Rome|quartiere|'
                  r'municipio of Rome|Municipi of|urban zone|sector of|subdivisions of|dzielnica|intracity|arrondissement|'
                  r'municipality of (Naples|Bari)|first-level unit|housing estate|central business|financial cent|'
                  r'Gemarkung|frazione|hamlet|pedanía|self-governing city (district|part)|administrative district of|'
                  r'municipal district of|core municipal part|inhabited area|former settlement|'
                  r'abandoned|deserted|ruins|archaeological|ghost town|borough of London|London borough', re.I)
BOX = (-25.5, 34.4, 49.5, 71.8)
CANDIDATES = 'hm-candidates.json'
MARK = '# Towns added by cities/towns_merge.py'          # cities.txt: the lines after it are towns_merge.py's      # step 1's input, also read in step 2 for the class names

def classes(path):
    d = json.load(open(path))
    settle, lab = set(d['settle']), d['clab']
    part = {k for k, v in lab.items() if PART.search(v)}
    keep, why = [], {}
    for it in d['all']:
        cl = set(it['cl'])
        if cl & part: continue
        if cl & settle or cl & set(MUNI): keep.append(it)
    print(len(d['all']), 'items;', len(keep), 'towns')
    print('classes left out as parts of cities:', '; '.join(sorted(lab[k] for k in part)))
    json.dump(keep, open('towns_qids.json', 'w'))

def fold(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\(.*?\)|,.*$|[^a-z ]', '', s).strip()

def similar(a, b):
    a, b = fold(a), fold(b)
    return bool(a and b) and (a in b or b in a or a[:5] == b[:5])

def km(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    return 6371 * math.acos(min(1, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(a[0] - b[0]))))

# the language of each country's own Wikipedia (Russian for the former Soviet states, whose town articles in
# Russian carry population tables), read along with German and English
LANG = {'Q183': ['de'], 'Q142': ['fr'], 'Q38': ['it'], 'Q29': ['es'], 'Q159': ['ru'], 'Q212': ['ru', 'uk'], 'Q145': [],
        'Q43': ['tr'], 'Q36': ['pl'], 'Q55': ['nl'], 'Q31': ['nl', 'fr'], 'Q213': ['cs'], 'Q40': [], 'Q39': ['fr', 'it'],
        'Q41': ['el'], 'Q45': ['pt'], 'Q218': ['ro'], 'Q28': ['hu'], 'Q219': ['bg'], 'Q403': ['sr'], 'Q224': ['hr'],
        'Q214': ['sk'], 'Q215': ['sl'], 'Q35': ['da'], 'Q20': ['no'], 'Q34': ['sv'], 'Q33': ['fi'], 'Q184': ['ru'],
        'Q217': ['ru', 'ro'], 'Q37': ['lt'], 'Q211': ['lv'], 'Q191': ['et'], 'Q230': ['ru'], 'Q399': ['ru'], 'Q227': ['ru'],
        'Q232': ['ru'], 'Q222': ['sq'], 'Q221': ['mk'], 'Q225': ['bs', 'sr'], 'Q236': ['sr'], 'Q1246': ['sq'], 'Q229': ['el'],
        'Q189': ['is'], 'Q27': [], 'Q32': ['fr'], 'Q262': ['fr'], 'Q1028': ['fr'], 'Q948': ['fr'], 'Q822': ['fr']}

def existing():
    """the cities already listed: name, lon, lat, latest population; and their Wikidata items"""
    rows = []
    for l in open('../cities.txt', encoding='utf-8'):
        if l.startswith(MARK): break                    # the towns this script added last time
        if l.strip() and not l.startswith('#'): rows.append(l.rstrip('\n').split('|'))
    qids = {l.split('|')[1] for l in open('wd_cities.txt', encoding='utf-8') if l.strip()}
    last = lambda ser: int(ser.split(';')[-1].split(':')[1][:-1])
    lasty = lambda ser: 1700 + int(ser.split(';')[-1].split(':')[0])
    return [(r[0], float(r[1]), float(r[2]), last(r[3]), lasty(r[3])) for r in rows], qids

# districts of a city filed as towns: a district of Antwerp, Wuppertal, Bremen..., or a county or island
CITY_PART = re.compile(r'^district of (Antwerp|Wuppertal|Klagenfurt|Bremen)|^District of Wuppertal|Bremerhaven district|'
                       r'subdistrict|ceremonial county|urban district of the Netherlands|^island$|city region', re.I)
TURKISH_DISTRICT = {'district of Turkey', 'municipality of Turkey', 'town'}

# listed cities whose figure takes in the towns around them (Greater London, the Brussels-Capital Region, the City
# of Belgrade, the cities of Birmingham and Leeds), and how far out (km)
METRO_FIGURE = {'London': 20, 'Brussels': 9, 'Belgrade': 10, 'Birmingham': 8, 'Leeds': 6}

def inside_big_city(t, old, lab):
    """A district of a large city: within 4 km of the center of a listed city of 500,000 or more; inside a city
    whose figure already counts its surroundings (METRO_FIGURE); or, in Turkey, a district of a large city (Turkey's
    large cities count their districts in their own figure): within 30 km of a listed Turkish city of a million or
    more, or 15 km of one of 300,000 or more."""
    here = (t['lon'], t['lat'])
    for n, lo, la, pop, _ in old:
        d = km(here, (lo, la))
        if pop >= 5e5 and d < 4 or d < METRO_FIGURE.get(n, 0): return n
        if t['c'] == 'Q43' and {lab.get(k) for k in t['cl']} & TURKISH_DISTRICT and (pop >= 1e6 and d < 30 or pop >= 3e5 and d < 15): return n
    return None

def dedupe(path):
    S = json.load(open(path))          # QID -> {label, wiki: {lang: title}, pop: [[date, figure, method], ...]}
    T = [{**t, **S[t['q']]} for t in json.load(open('towns_qids.json')) if t['q'] in S]
    T = [t for t in T if BOX[0] <= t['lon'] <= BOX[2] and BOX[1] <= t['lat'] <= BOX[3]]
    old, oldq = existing()
    lab = json.load(open(CANDIDATES))['clab']
    early = lambda t: sum(1 for p in t['pop'] if int(p[0][:4]) < 1950)
    new, gone, parts, extend = [], [], [], []
    for t in sorted(T, key=lambda t: -t['p']):
        name = t['label'] or t['wiki'].get('en') or next(iter(t['wiki'].values()), t['q'])
        name = re.sub(r' district$', '', name)
        if re.search(r'Province$|Métropole$|^Metropolis of|^Metropolitan ', name): parts.append(name); continue
        if any(CITY_PART.search(lab.get(k, '')) for k in t['cl']): parts.append(name); continue
        here = (t['lon'], t['lat'])
        o = [c for c in old if km(here, c[1:3]) < 3 or (km(here, c[1:3]) < 15 and similar(name, c[0]))]
        if o:
            gone.append((name, o[0][0]))
            # a city listed only for the earlier centuries (de Vries's and Chandler's towns, such as Regensburg or
            # Leiden): its later figures come from this town
            if o[0][4] < 1850 and o[0][0] not in {e['extend'] for e in extend}: extend.append({**t, 'name': name, 'extend': o[0][0]})
            continue
        big = inside_big_city(t, old, lab)
        if big: parts.append(f'{name} ({big})'); continue
        twin = [n for n in new if km(here, (n['lon'], n['lat'])) < 3 and similar(name, n['name'])]
        if twin:                      # a town and its municipality: keep the one with more figures before 1950
            n = twin[0]
            if early(t) > early(n): new[new.index(n)] = {**t, 'name': name}
            continue
        new.append({**t, 'name': name})
    # Turkey split its large cities into districts in 2008; a Turkish "town" whose figures begin then and that lies
    # within 15 km of a Turkish city (or a larger town) is one of those districts (Selçuklu and Meram in Konya,
    # Odunpazarı in Eskişehir)
    first = lambda t: min((int(p[0][:4]) for p in t['pop']), default=9999)
    city = lambda t: bool({lab.get(k) for k in t['cl']} & {'city', 'big city'})
    for t in [t for t in new if t['c'] == 'Q43' and first(t) >= 2007 and not city(t)]:
        here = (t['lon'], t['lat'])
        big = [n['name'] for n in new if n is not t and n['c'] == 'Q43' and (city(n) or n['p'] > t['p']) and km(here, (n['lon'], n['lat'])) < 15]
        if big: new.remove(t); parts.append(f"{t['name']} ({big[0]})")
    print(len(T), 'towns;', len(gone), 'already listed;', len(parts), 'parts of a city;', len(new), 'new')
    print('parts of a city:', '; '.join(parts))
    print('early cities to carry forward:', ', '.join(f"{e['extend']} ({e['name']})" for e in extend))
    # what towns_merge.py needs, compactly (kept in the repository, so the merge can be re-run)
    slim = lambda t: {'q': t['q'], 'name': t['name'], 'label': t['label'], 'lon': t['lon'], 'lat': t['lat'], 'p': t['p'], 'c': t['c'],
                      'cls': [lab.get(k, k) for k in t['cl']], 'wiki': {l: t['wiki'][l] for l in ('en', 'de') if l in t['wiki']},
                      'pop': [[d[:10], v, m] for d, v, m in t['pop']], **({'extend': t['extend']} if 'extend' in t else {})}
    json.dump([slim(t) for t in new], open('towns_new.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump([slim(t) for t in extend], open('towns_extend.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    inp = []
    for t in new + extend:
        langs = LANG.get(t['c'], []) + ['de', 'en']
        inp.append([t['q'], {l: t['wiki'][l] for l in dict.fromkeys(langs) if l in t['wiki']}])
    json.dump(inp, open('towns_input.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('articles to read:', sum(len(w) for _, w in inp))

if __name__ == '__main__':
    {'classes': classes, 'dedupe': dedupe}[sys.argv[1]](sys.argv[2])
