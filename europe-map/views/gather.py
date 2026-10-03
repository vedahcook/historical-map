"""Gather period-view candidates for each city from Wikimedia Commons. Usage: python3 gather.py CITY [CITY...]
Writes cand/<slug>.json: candidates with metadata, a made-year guess, a period and a score; at most 6-8 per period."""
import sys, json, re, html, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, 'cities.json')))
EXTRA = {  # other names used in titles (local, Latin, German, French, Italian)
 'London': ['Londinum', 'Londres', 'Londra'], 'Rome': ['Roma', 'Rom'], 'Berlin': ['Berolinum'],
 'Moscow': ['Moskau', 'Moscou', 'Mosca', 'Moscovia', 'Москва'], 'Saint Petersburg': ['St. Petersburg', 'Sankt Petersburg', 'Petersburg', 'Saint-Pétersbourg', 'Petrograd', 'Leningrad'],
 'Prague': ['Praha', 'Prag', 'Praga'], 'Budapest': ['Buda', 'Pest', 'Ofen'], 'Warsaw': ['Warszawa', 'Warschau', 'Varsovie', 'Varsovia'],
 'Kraków': ['Krakow', 'Cracow', 'Krakau', 'Cracovia'], 'Madrid': [], 'Seville': ['Sevilla', 'Séville', 'Siviglia', 'Hispalis'],
 'Lisbon': ['Lisboa', 'Lissabon', 'Lisbonne', 'Olisippo'], 'Amsterdam': ['Amstelredamum', 'Amstelodamum'],
 'Brussels': ['Bruxelles', 'Brussel', 'Brüssel', 'Bruxella'], 'Venice': ['Venezia', 'Venedig', 'Venise', 'Venetia'],
 'Florence': ['Firenze', 'Florenz', 'Florentia'], 'Naples': ['Napoli', 'Neapel', 'Neapolis'], 'Milan': ['Milano', 'Mailand', 'Mediolanum'],
 'Munich': ['München', 'Monachium'], 'Nuremberg': ['Nürnberg', 'Norimberga', 'Nurnberg'], 'Dresden': ['Dresda'],
 'Copenhagen': ['København', 'Kopenhagen', 'Copenhague', 'Hafnia', 'Kiøbenhavn'], 'Stockholm': ['Holmia'],
 'Athens': ['Athen', 'Athènes', 'Atene', 'Athenae', 'Αθήνα'], 'Edinburgh': ['Edenburgum', 'Edinburgum'],
}
FRV = {'fr': 'Vue de', 'de': 'Ansicht von', 'it': 'Veduta di', 'nl': 'Gezicht op', 'pl': 'Widok', 'es': 'Vista de'}
PERIODS = [(0, 1499, 'before 1500'), (1500, 1649, '1500–1649'), (1650, 1749, '1650–1749'), (1750, 1849, '1750–1849'),
           (1850, 1913, '1850–1913'), (1914, 1969, '1914–1969'), (1970, 2026, '1970–today')]
VIEW = re.compile(r'panoram|\bview|\bvue\b|veduta|vedute|ansicht|prospe[ck]t|widok|vista|gezicht|skyline|bird|aerial|luftbild|luftaufnahme|from the |general|overview|cityscape|udsigt|utsikt|vy över|blick|photochrom|stadtbild|totale|pohled', re.I)
BAD = re.compile(r'coat of arms|wappen|\bseal\b|stamp|coin|banknote|logo|\bflag\b|portrait|interior|\bplan\b|grundriss|\bmap of\b|\bkarte\b|stadtplan|plattegrond|street map|metro|subway|diagram|signature|title page|frontispiece', re.I)
SERIES = [(re.compile(r'braun|hogenberg|civitates', re.I), 30, 'Braun & Hogenberg'), (re.compile(r'merian|topographia', re.I), 25, 'Merian'),
          (re.compile(r'schedel|nuremberg chronicle|weltchronik|liber chronicarum', re.I), 20, 'Nuremberg Chronicle'),
          (re.compile(r'photochrom|LCCN', re.I), 25, 'photochrom'), (re.compile(r'bellotto|canaletto|vanvitelli|guardi|vedut', re.I), 20, 'veduta'),
          (re.compile(r'mittelholzer', re.I), 20, 'Mittelholzer'), (re.compile(r'blaeu|toonneel', re.I), 22, 'Blaeu'),
          (re.compile(r'dahlbergh|suecia antiqua', re.I), 22, 'Dahlbergh')]
def strip(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()
def slug(t): return re.sub(r'[^a-z]+', '-', t.lower().replace('ó', 'o')).strip('-')

def year_of(meta, title, cats):
    d = strip(meta.get('DateTimeOriginal', {}).get('value', ''))
    m = re.search(r'\b(1[0-9]{3}|20[0-2][0-9])s\b', d)
    if m: return int(m.group(1)) + 5, m.group(0), 'date'
    ys = [int(y) for y in re.findall(r'(?<!\d)(1[0-9]{3}|20[0-2][0-9])(?!\d)', d) if 1000 <= int(y) <= 2026]
    if ys:
        if len(ys) >= 2 and re.search(r'between|–|-|to|and', d) and 0 < abs(ys[1] - ys[0]) <= 60:
            a, b = sorted(ys[:2]); return (a + b) // 2, f'{a}–{str(b)[-2:] if str(a)[:2] == str(b)[:2] else b}', 'date'
        return ys[0], (f'about {ys[0]}' if re.search(r'circa|ca\.|\bc\.|about|\bum\b|vers', d, re.I) else str(ys[0])), 'date'
    ys = [int(y) for y in re.findall(r'(?<!\d)(1[0-9]{3}|20[0-2][0-9])(?!\d)', title) if 1000 <= int(y) <= 2026]
    if ys: return ys[0], str(ys[0]), 'title'
    for c in cats:
        m = re.search(r'\b(1[0-9]{3})s\b', c)
        if m: return int(m.group(1)) + 5, m.group(0), 'category'
    for c in cats:
        m = re.search(r'\b(1[0-9])th[- ]century', c)
        if m: return (int(m.group(1)) - 1) * 100 + 50, f'{m.group(1)}th century', 'category'
    return None, '', ''

def period_of(y):
    for i, (a, b, _) in enumerate(PERIODS):
        if a <= y <= b: return i
    return None

def names_of(city):
    info = C[city]; base = re.sub(r'\s*\(.*\)', '', city).strip(); names = [base]
    m = re.search(r'\((.*)\)', city)
    extra = ([m.group(1)] if m else []) + info.get('native', []) + [info['labels'].get(l) for l in ('de', 'la')] + EXTRA.get(city, []) + info.get('aliases', {}).get('de', [])[:1]
    for n in extra:
        if n and n not in names and len(n) > 2: names.append(n)
    return names

def save(path, obj):
    tmp = path + '.tmp'; json.dump(obj, open(tmp, 'w'), ensure_ascii=False)
    try: os.replace(tmp, path)
    except OSError: json.dump(obj, open(path, 'w'), ensure_ascii=False)

def run(city):
    """Resumable: progress is saved to raw/<slug>.part.json after every few requests, so a run cut short continues next time."""
    os.makedirs(os.path.join(HERE, 'raw'), exist_ok=True)
    raw = os.path.join(HERE, 'raw', slug(city) + '.json'); part = os.path.join(HERE, 'raw', slug(city) + '.part.json')
    if os.path.exists(raw):
        R = json.load(open(raw)); select(city, {k: set(v) for k, v in R['found'].items()}, {k: tuple(v) for k, v in R['meta'].items()}); return
    st = json.load(open(part)) if os.path.exists(part) else {'q_done': [], 'found': {}, 'cats': None, 'cat_done': [], 'meta': {}, 'nometa': []}
    info = C[city]; cc = info['commonscat']; names = names_of(city)
    def add(t, src): st['found'].setdefault(t, [])
    def add(t, src):
        L = st['found'].setdefault(t, [])
        if src not in L: L.append(src)
    Q = []
    for n in names[:6]: Q += [f'Braun Hogenberg {n}', f'Merian {n}']
    for n in names[:4]: Q += [f'Schedel {n}']
    b = names[0]
    Q += [f'photochrom {b}', f'"{b}" panorama 19th century', f'"View of {b}"', f'"Panorama of {b}"', f'{b} veduta painting',
          f'{b} aerial photograph 1930', f'{b} from the air 1920s', f'Mittelholzer {info["labels"].get("de") or b}',
          f'{b} skyline panorama incategory:Quality_images', f'{b} panorama incategory:Featured_pictures_on_Wikimedia_Commons',
          f'{b} view lithograph', f'{b} view engraving 18th century', f'{b} early photograph view 1860']
    for lang, pre in FRV.items():
        lab = info['labels'].get(lang)
        if lab: Q.append(f'"{pre} {lab}"')
    k = 0
    for q in dict.fromkeys(Q):
        if q in st['q_done']: continue
        r = wm.commons(action='query', list='search', srsearch=q + ' filetype:bitmap', srnamespace=6, srlimit=25)
        for h in r.get('query', {}).get('search', []): add(h['title'], 'search:' + q)
        st['q_done'].append(q); k += 1
        if k % 6 == 0: save(part, st)
    save(part, st)
    if st['cats'] is None:
        tries = [f'Maps of {cc} by Braun & Hogenberg', f'Panoramics of {cc}', f'Views of {cc}', f'Old views of {cc}', f'Paintings of {cc}',
                 f'Vedute of {cc}', f'Photochrom prints of {cc}', f'Aerial photographs of {cc}', f'Skylines of {cc}', f'Cityscapes of {cc}',
                 f'Panoramas of {cc}', f'Historical images of {cc}', f'Old photographs of {cc}', f'Prints of {cc}', f'Engravings of {cc}',
                 f'Lithographs of {cc}', f'Historical views of {cc}', f"Bird's-eye views of {cc}", f'{cc} in art', f'{cc} in the Nuremberg Chronicle']
        tries += [f'{cc} in the {d}s' for d in range(1840, 1970, 10)] + [f'{cc} in the {c}th century' for c in (15, 16, 17, 18, 19)]
        tries += [f'Panoramics of {cc} in the {d}s' for d in range(1850, 1970, 10)]
        existing = []
        for i in range(0, len(tries), 50):
            r = wm.commons(action='query', titles='|'.join('Category:' + t for t in tries[i:i+50]), prop='categoryinfo')
            for p in r['query']['pages']:
                if not p.get('missing') and p.get('categoryinfo', {}).get('files', 0) > 0: existing.append(p['title'])
        st['cats'] = existing; save(part, st)
    for cat in st['cats']:
        if cat in st['cat_done']: continue
        series_cat = bool(re.search(r'Braun|Panoramic|Views|views|Vedute|Photochrom|Aerial|Skylines|Panoramas|Bird|Nuremberg|Cityscapes', cat))
        r = wm.commons(action='query', list='categorymembers', cmtitle=cat, cmtype='file', cmlimit=500)
        for m in r['query']['categorymembers']:
            if series_cat or VIEW.search(m['title']): add(m['title'], 'cat:' + cat)
        st['cat_done'].append(cat); save(part, st)
    todo = [t for t in st['found'] if t not in st['meta'] and t not in st['nometa']]
    for i in range(0, len(todo), 50):
        batch = todo[i:i+50]
        r = wm.commons(action='query', titles='|'.join(batch), prop='imageinfo|categories', iiprop='size|mime|extmetadata',
                       iiextmetadatafilter='DateTimeOriginal|Artist|LicenseShortName|ImageDescription|Credit', clshow='!hidden', cllimit='max')
        got = set()
        for p in r['query']['pages']:
            if p.get('missing') or not p.get('imageinfo'): continue
            st['meta'][p['title']] = (p['imageinfo'][0], [c['title'][9:] for c in p.get('categories', [])]); got.add(p['title'])
        for n in r['query'].get('normalized', []):
            if n['to'] in got: got.add(n['from'])
        st['nometa'] += [t for t in batch if t not in got and t not in st['meta']]
        save(part, st)
    save(raw, {'found': st['found'], 'meta': st['meta']})
    select(city, {k: set(v) for k, v in st['found'].items()}, {k: tuple(v) for k, v in st['meta'].items()})

OLD = {'Braun & Hogenberg', 'Merian', 'Nuremberg Chronicle', 'veduta', 'Blaeu', 'Dahlbergh'}
ART = re.compile(r'painting|gemälde|engraving|etching|lithograph|woodcut|drawing|kupferstich|radierung|holzschnitt|aquarell|watercolou?r|gravure|stich\b', re.I)
INST = re.compile(r'museum|gallery|galerie|galleria|collection|library|bibliothe|archive|institut|universit', re.I)

def select(city, found, meta):
    info = C[city]; cc = info['commonscat']; names = names_of(city)
    nrx = re.compile(r'(?<![A-Za-zÀ-ž])(' + '|'.join(re.escape(n) for n in names + [cc]) + r')(?![a-zà-ž])', re.I)
    out = []; seen = {}
    for t, (ii, cats) in meta.items():
        em = ii.get('extmetadata') or {}; em = em if isinstance(em, dict) else {}; lic = strip(em.get('LicenseShortName', {}).get('value', ''))
        if not re.search(r'public domain|^pd|cc0|cc[ -]by', lic, re.I) or re.search(r'\bnc\b|\bnd\b|non-?commercial', lic, re.I): continue
        if ii.get('mime') not in ('image/jpeg', 'image/png', 'image/tiff', 'image/webp'): continue
        w, h = ii.get('width', 0), ii.get('height', 0)
        if not (w >= 1000 or (h >= 1000 and w >= 800)): continue
        desc = strip(em.get('ImageDescription', {}).get('value', ''))[:400]
        rel_cats = [c for c in cats if nrx.search(c) and not INST.search(c)]
        if not (nrx.search(t) or rel_cats or any(s.startswith('cat:') and not INST.search(s) for s in found[t])): continue
        text = ' '.join([t, desc, ' '.join(cats)])
        y, lab, ysrc = year_of(em, t, cats)
        if y is None: continue
        pi = period_of(y)
        if pi is None: continue
        sname, sbonus = '', 0
        for rx, b, nm in SERIES:
            if rx.search(text) and b > sbonus: sname, sbonus = nm, b
        if BAD.search(t) and sname not in ('Braun & Hogenberg', 'Merian'): continue
        if (sname in OLD or ART.search(t + ' ' + desc)) and y > 1900 and sname != 'Mittelholzer': continue   # a photo of an old picture, dated by the photo
        stem = re.sub(r'\.(jpe?g|tiff?|png|webp)$', '', t[5:], flags=re.I).lower()
        if stem in seen and (ii['mime'] == 'image/tiff' or seen[stem] == 'image/jpeg'): continue
        seen[stem] = ii['mime']
        score = sbonus + (10 if VIEW.search(t + ' ' + desc) else 0) + min(10, w * h / 1e6)
        if any('Featured pictures' in c for c in cats): score += 15
        if any('Quality images' in c for c in cats): score += 8
        if any('Valued images' in c for c in cats): score += 10
        if any(s.startswith('search:') for s in found[t]): score += 3
        if ysrc == 'category': score -= 5
        if pi == 6 and not any('Quality images' in c or 'Featured pictures' in c for c in cats): score -= 8
        out = [o for o in out if re.sub(r'\.(jpe?g|tiff?|png|webp)$', '', o['title'], flags=re.I).lower() != stem]
        out.append({'title': t[5:], 'w': w, 'h': h, 'mime': ii['mime'], 'year': y, 'label': lab, 'ysrc': ysrc, 'period': pi,
                    'date_raw': strip(em.get('DateTimeOriginal', {}).get('value', ''))[:120], 'artist': strip(em.get('Artist', {}).get('value', ''))[:160],
                    'license': lic, 'credit': strip(em.get('Credit', {}).get('value', ''))[:160], 'desc': desc, 'cats': cats[:12],
                    'series': sname, 'score': round(score, 1), 'src': sorted(found[t])[:3], 'rel_cats': rel_cats[:4]})
    keep = []
    for pi in range(len(PERIODS)):
        xs = sorted((c for c in out if c['period'] == pi), key=lambda c: -c['score'])
        keep += xs[:8 if pi in (1, 4) else 6]
    for i, c in enumerate(keep, 1): c['n'] = i
    os.makedirs(os.path.join(HERE, 'cand'), exist_ok=True)
    json.dump({'city': city, 'qid': info['qid'], 'commonscat': cc, 'periods': [p[2] for p in PERIODS], 'n_files': len(found), 'n_ok': len(out), 'cand': keep},
              open(os.path.join(HERE, 'cand', slug(city) + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(city, 'files', len(found), 'usable', len(out), 'kept', len(keep), 'per period', [sum(1 for c in keep if c['period'] == i) for i in range(len(PERIODS))], flush=True)

if __name__ == '__main__':
    for c in sys.argv[1:]:
        try: run(c)
        except Exception as e: print('FAILED', c, repr(e), flush=True)
