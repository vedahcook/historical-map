"""Second, deeper search for cities with few views (deep_targets.json). Usage: python3 gather_deep.py CITY [CITY...]
Differences from gather.py: names in more languages (Russian, Ukrainian, Turkish, Persian...), searches with words for
"view", "panorama", "postcard", "old" in the name's language, a walk through the city's Commons category tree (history,
views, postcards, decades), the city's Wikidata pictures, old pictures from 800 px wide, and candidates already offered
in the first search left out. Periods the city already has get at most 3 candidates. Writes cand_deep/<slug>.json."""
import sys, json, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm, gather as G
HERE = os.path.dirname(os.path.abspath(__file__))
T = {t['name']: t for t in json.load(open(os.path.join(HERE, 'deep_targets.json')))}
LANGS = ['ru', 'uk', 'be', 'pl', 'tr', 'ro', 'bg', 'sr', 'el', 'hu', 'cs', 'sk', 'lt', 'lv', 'fa', 'ar', 'ka', 'hy', 'az', 'fr', 'it', 'es', 'nl', 'de']
TERMS = {'ru': ['панорама', 'вид', 'открытка', 'старый'], 'uk': ['панорама', 'вид', 'листівка', 'старий'], 'be': ['панарама', 'від', 'паштоўка'],
         'pl': ['widok', 'panorama', 'pocztówka'], 'tr': ['manzara', 'panorama', 'kartpostal', 'eski'], 'ro': ['vedere', 'panorama', 'carte poștală'],
         'bg': ['изглед', 'панорама', 'картичка'], 'sr': ['поглед', 'панорама', 'разгледница'], 'el': ['άποψη', 'πανόραμα'], 'hu': ['látkép', 'panoráma'],
         'cs': ['pohled', 'panorama', 'pohlednice'], 'sk': ['pohľad', 'panoráma'], 'lt': ['panorama', 'vaizdas'], 'lv': ['panorāma', 'skats'],
         'fa': ['نمای'], 'ar': ['منظر'], 'ka': ['ხედი'], 'hy': ['տեսարան'], 'az': ['panorama', 'mənzərə'],
         'fr': ['vue', 'carte postale'], 'it': ['veduta', 'cartolina'], 'es': ['vista', 'postal'], 'nl': ['gezicht', 'ansichtkaart'], 'de': ['Ansicht', 'Postkarte'],
         'en': ['panorama', 'view', 'postcard', 'old photograph', 'skyline', 'aerial']}
HIST = re.compile(r'histor|\bold\b|panoram|\bviews?\b|skyline|aerial|from above|from the air|bird|postcard|in the \d{3,4}s|in the \d{1,2}(st|nd|rd|th) century|'
                  r'\b1[5-9]\d\d\b|\bart\b|painting|engraving|\bprints?\b|lithograph|drawing|photochrom|prokudin|mittelholzer|fortepan|cityscape|townscape|'
                  r'general view|before|pre-|истор|панорам|вид |открыт|старый|архив|eski|kartpostal|tarih', re.I)
SKIP = re.compile(r'people|portrait|interior|sport|football|transport|\bbus|tram|trolley|vehicle|car\b|cars\b|demonstrat|protest|\bmaps?\b|logo|'
                  r'coats? of arms|flags?\b|signs?\b|stamps?\b|graves?|cemeter|church interiors|museum exhibits|objects|plaques|monuments? to|statues|'
                  r'by photographer|uploaded|quality images|videos|audio|sound|plants|animals|birds of|insects', re.I)
def names_deep(city):
    info = G.C[city]; out = [('en', n) for n in G.names_of(city)]
    for l in LANGS:
        n = info['labels'].get(l)
        if n and len(n) > 2 and n not in [x for _, x in out]: out.append((l, n))
    for l, al in (info.get('aliases') or {}).items():
        for n in al[:2]:
            if len(n) > 2 and ',' not in n and n not in [x for _, x in out]: out.append((l, n))
    return out[:12]
def run(city):
    os.makedirs(os.path.join(HERE, 'raw_deep'), exist_ok=True)
    s = G.slug(city); raw = os.path.join(HERE, 'raw_deep', s + '.json'); part = os.path.join(HERE, 'raw_deep', s + '.part.json')
    if os.path.exists(raw):
        R = json.load(open(raw)); select(city, R['found'], R['meta']); return
    st = json.load(open(part)) if os.path.exists(part) else {'q_done': [], 'found': {}, 'cats': None, 'cat_done': [], 'meta': {}, 'nometa': [], 'wd': False}
    info = G.C[city]; cc = info['commonscat']; names = names_deep(city)
    def add(t, src):
        L = st['found'].setdefault(t, [])
        if src not in L and len(L) < 4: L.append(src)
    Q = []
    for l, n in names[:7]:
        Q += [f'"{n}" {w}' for w in (TERMS['en'] if l == 'en' else TERMS.get(l, [])[:3])]
        Q.append(f'"{n}"')
    k = 0
    for q in dict.fromkeys(Q):
        if q in st['q_done']: continue
        r = wm.commons(action='query', list='search', srsearch=q + ' filetype:bitmap', srnamespace=6, srlimit=50)
        for h in r.get('query', {}).get('search', []): add(h['title'], 'search:' + q)
        st['q_done'].append(q); k += 1
        if k % 8 == 0: G.save(part, st)
    G.save(part, st)
    if not st['wd']:
        e = wm.api('www.wikidata.org', action='wbgetentities', ids=info['qid'], props='claims')
        cl = (e.get('entities', {}).get(info['qid']) or {}).get('claims', {})
        for p in ('P18', 'P8592', 'P3451', 'P5252'):
            for c in cl.get(p, []):
                v = (c.get('mainsnak', {}).get('datavalue') or {}).get('value')
                if isinstance(v, str): add('File:' + v, 'wikidata:' + p)
        st['wd'] = True; G.save(part, st)
    if st['cats'] is None:
        seen, frontier, keep = {'Category:' + cc}, ['Category:' + cc], ['Category:' + cc]
        for depth in range(3):
            nxt = []
            for cat in frontier:
                r = wm.commons(action='query', list='categorymembers', cmtitle=cat, cmtype='subcat', cmlimit=500)
                for m in r.get('query', {}).get('categorymembers', []):
                    t = m['title']
                    if t in seen or SKIP.search(t) or not HIST.search(t): continue
                    seen.add(t); nxt.append(t); keep.append(t)
                if len(keep) > 80: break
            frontier = nxt[:60]
            if len(keep) > 80: break
        st['cats'] = keep[:90]; G.save(part, st)
    for cat in st['cats']:
        if cat in st['cat_done']: continue
        top = cat == 'Category:' + cc
        r = wm.commons(action='query', list='categorymembers', cmtitle=cat, cmtype='file', cmlimit=500)
        for m in r.get('query', {}).get('categorymembers', []):
            if not top or G.VIEW.search(m['title']): add(m['title'], 'cat:' + cat[9:])
        st['cat_done'].append(cat); G.save(part, st)
    todo = [t for t in st['found'] if t not in st['meta'] and t not in st['nometa']]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        r = wm.commons(action='query', titles='|'.join(batch), prop='imageinfo|categories', iiprop='size|mime|extmetadata',
                       iiextmetadatafilter='DateTimeOriginal|Artist|LicenseShortName|ImageDescription|Credit', clshow='!hidden', cllimit='max')
        got = set()
        for p in r['query']['pages']:
            if p.get('missing') or not p.get('imageinfo'): continue
            st['meta'][p['title']] = (p['imageinfo'][0], [c['title'][9:] for c in p.get('categories', [])]); got.add(p['title'])
        for n in r['query'].get('normalized', []):
            if n['to'] in got: got.add(n['from'])
        st['nometa'] += [t for t in batch if t not in got and t not in st['meta']]
        if i % 500 == 0: G.save(part, st)
    G.save(raw, {'found': st['found'], 'meta': st['meta']})
    select(city, st['found'], st['meta'])

def select(city, found, meta):
    info = G.C[city]; cc = info['commonscat']; s = G.slug(city)
    names = [n for _, n in names_deep(city)]
    nrx = re.compile(r'(?<![A-Za-zÀ-ž])(' + '|'.join(re.escape(n) for n in names + [cc]) + r')(?![a-zà-ž])', re.I)
    old = os.path.join(HERE, 'cand', s + '.json')
    offered = {c['title'] for c in json.load(open(old))['cand']} if os.path.exists(old) else set()
    covered = set(T[city]['covered'])
    out, seen = [], {}
    for t, (ii, cats) in meta.items():
        if t[5:] in offered: continue
        em = ii.get('extmetadata') or {}; em = em if isinstance(em, dict) else {}; lic = G.strip(em.get('LicenseShortName', {}).get('value', ''))
        if not re.search(r'public domain|^pd|cc0|cc[ -]by', lic, re.I) or re.search(r'\bnc\b|\bnd\b|non-?commercial', lic, re.I): continue
        if ii.get('mime') not in ('image/jpeg', 'image/png', 'image/tiff', 'image/webp'): continue
        w, h = ii.get('width', 0), ii.get('height', 0)
        desc = G.strip(em.get('ImageDescription', {}).get('value', ''))[:400]
        rel_cats = [c for c in cats if nrx.search(c) and not G.INST.search(c)]
        srcs = found.get(t, [])
        if not (nrx.search(t) or nrx.search(desc) or rel_cats or any(x.startswith(('cat:', 'wikidata:')) and not G.INST.search(x) for x in srcs)): continue
        if srcs and all(re.fullmatch(r'search:"[^"]+"', x) for x in srcs) and not (G.VIEW.search(t + ' ' + desc) or HIST.search(t + ' ' + desc) or rel_cats): continue
        if re.search(r'genus|species|lepidoptera|insect|entomolog|butterfl|moth\b|beetle|botan|herbarium|fossil', ' '.join(cats) + ' ' + t, re.I): continue
        text = ' '.join([t, desc, ' '.join(cats)])
        y, lab, ysrc = G.year_of(em, t, cats)
        if y is None: continue
        pi = G.period_of(y)
        if pi is None: continue
        if pi == 6 and not (w >= 1200 or (h >= 1200 and w >= 900)): continue
        if pi < 6 and not (w >= 800 or (h >= 800 and w >= 640)): continue
        sname, sbonus = '', 0
        for rx, b, nm in G.SERIES:
            if rx.search(text) and b > sbonus: sname, sbonus = nm, b
        if G.BAD.search(t) and sname not in ('Braun & Hogenberg', 'Merian'): continue
        if (sname in G.OLD or G.ART.search(t + ' ' + desc)) and y > 1900 and sname != 'Mittelholzer': continue
        stem = re.sub(r'\.(jpe?g|tiff?|png|webp)$', '', t[5:], flags=re.I).lower()
        if stem in seen and (ii['mime'] == 'image/tiff' or seen[stem] == 'image/jpeg'): continue
        seen[stem] = ii['mime']
        score = sbonus + (10 if G.VIEW.search(t + ' ' + desc) else 0) + min(10, w * h / 1e6)
        if any('Featured pictures' in c for c in cats): score += 15
        if any('Quality images' in c for c in cats): score += 8
        if any('Valued images' in c for c in cats): score += 10
        if any(x.startswith('wikidata:') for x in srcs): score += 12
        if any(re.search(r'postcard|открыт|листів|kartpostal|pocztów|pohlednic|carte post', c, re.I) for c in cats + [t]): score += 4
        if ysrc == 'category': score -= 5
        if pi == 6 and not any('Quality images' in c or 'Featured pictures' in c for c in cats): score -= 8
        out = [o for o in out if re.sub(r'\.(jpe?g|tiff?|png|webp)$', '', o['title'], flags=re.I).lower() != stem]
        out.append({'title': t[5:], 'w': w, 'h': h, 'mime': ii['mime'], 'year': y, 'label': lab, 'ysrc': ysrc, 'period': pi,
                    'date_raw': G.strip(em.get('DateTimeOriginal', {}).get('value', ''))[:120], 'artist': G.strip(em.get('Artist', {}).get('value', ''))[:160],
                    'license': lic, 'credit': G.strip(em.get('Credit', {}).get('value', ''))[:160], 'desc': desc, 'cats': cats[:12],
                    'series': sname, 'score': round(score, 1), 'src': sorted(srcs)[:3], 'rel_cats': rel_cats[:4]})
    keep = []
    for pi in range(len(G.PERIODS)):
        xs = sorted((c for c in out if c['period'] == pi), key=lambda c: -c['score'])
        keep += xs[:2 if pi in covered else (5 if pi in (1, 4, 5) else 4)]
    for i, c in enumerate(keep, 1): c['n'] = i
    os.makedirs(os.path.join(HERE, 'cand_deep'), exist_ok=True)
    json.dump({'city': city, 'qid': info['qid'], 'commonscat': cc, 'periods': [p[2] for p in G.PERIODS], 'covered': sorted(covered),
               'n_files': len(found), 'n_ok': len(out), 'cand': keep}, open(os.path.join(HERE, 'cand_deep', s + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(city, 'files', len(found), 'usable', len(out), 'kept', len(keep), 'per period', [sum(1 for c in keep if c['period'] == i) for i in range(len(G.PERIODS))], flush=True)

if __name__ == '__main__':
    for c in sys.argv[1:]:
        try: run(c)
        except Exception as e: print('FAILED', c, repr(e), flush=True)
