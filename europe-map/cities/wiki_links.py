"""Check every event's and person's Wikipedia link against Wikidata, and keep each one's Wikidata id.
Run in europe-map/ after cities/make_extras.py (which writes city-events.json and city-people.json):
  python3 cities/wiki_links.py list     -> wiki_lookup.json: the English titles and Wikidata ids to look up
  python3 cities/wiki_links.py fetch    -> wiki_links_out.json (resumable, stops after 150 s: run again until it says DONE;
                                           run it where Wikimedia doesn't throttle, e.g. the Mac's Claude workspace)
  python3 cities/wiki_links.py apply    -> rewrites the two files and writes wiki-titles.json
After `apply` each row ends with its Wikidata id, and its link column holds: '' (English article titled like the name),
'Title' (English article), 'xx:Title' (no English article: the article in language xx, shown as "Spanish Wikipedia" and
so on), or null (no article in any language; the map links the Wikidata entry). The other language is the city's own if
it is French, German, Spanish or Italian, else the first of those four that exists, else another of the city's languages,
else any. wiki-titles.json keeps each entry's titles in English, French, German, Spanish and Italian, for pages in those
languages later. cities/city_country.json (each city's present-day country, read from the map for 2026) gives the city's
languages."""
import json, os, re, sys, time, requests
LOOKUP, OUT = 'wiki_lookup.json', 'wiki_links_out.json'
def do_list():
    titles, qids = set(), set()
    for f, k, ti in (('city-events.json', 'ev', 6), ('city-people.json', 'pp', 7)):
        for r in json.load(open(f))[k]:
            q0 = r[8] if len(r) > 8 else ''
            if q0: qids.add(q0)
            elif re.match(r'^Q\d+$', r[ti] or ''): qids.add(r[ti])
            else: titles.add(r[ti] or r[5])
    json.dump({'titles': sorted(titles), 'qids': sorted(qids)}, open(LOOKUP, 'w'), ensure_ascii=False)
    print(len(titles), 'titles,', len(qids), 'Wikidata ids ->', LOOKUP)

def do_fetch():
    L = json.load(open(LOOKUP))
    S = json.load(open(OUT)) if os.path.exists(OUT) else {'t2q': {}, 'sl': {}, 'redir': {}, 'missing': [], 'search': {}, 'stage': 1, 'i': 0, 'q2': []}
    t0 = time.time(); S.setdefault('q2', [])
    def save(): json.dump(S, open(OUT + '.tmp', 'w'), ensure_ascii=False); os.replace(OUT + '.tmp', OUT)
    def api(url, params):
        params = dict(params, format='json', maxlag=5)
        for i in range(6):
            try:
                r = requests.post(url, data=params, headers=UA, timeout=60)
                if r.status_code == 200:
                    j = r.json()
                    if 'error' in j and j['error'].get('code') == 'maxlag': time.sleep(5); continue
                    return j
                time.sleep(4 * (i + 1))
            except Exception: time.sleep(4)
        raise RuntimeError('api failed')
    def wp_sitelinks(ent):
        return {k[:-4]: v['title'] for k, v in (ent.get('sitelinks') or {}).items() if k.endswith('wiki') and k not in NOTWP}
    WD = 'https://www.wikidata.org/w/api.php'
    def out_of_time(): return time.time() - t0 > 150
    # stage 1: enwiki titles -> entries (with all their Wikipedia articles)
    T = L['titles']
    while S['stage'] == 1 and not out_of_time():
        b = T[S['i']:S['i'] + 50]
        if not b: S['stage'] = 2; S['i'] = 0; break
        j = api(WD, {'action': 'wbgetentities', 'sites': 'enwiki', 'titles': '|'.join(b), 'props': 'sitelinks'})
        got = set()
        for qid, ent in j.get('entities', {}).items():
            if 'missing' in ent: continue
            sl = wp_sitelinks(ent); S['sl'][qid] = sl
            if 'en' in sl: S['t2q'][sl['en']] = qid; got.add(sl['en'])
        S['missing'] += [t for t in b if t not in got]
        S['i'] += 50; save()
    # stage 2: titles not found (moved or deleted pages): ask English Wikipedia, following redirects
    M = S['missing']
    while S['stage'] == 2 and not out_of_time():
        b = M[S['i']:S['i'] + 50]
        if not b: S['stage'] = 3; S['i'] = 0; break
        j = api('https://en.wikipedia.org/w/api.php', {'action': 'query', 'titles': '|'.join(b), 'redirects': 1, 'prop': 'pageprops', 'ppprop': 'wikibase_item'})
        q = j.get('query', {}); fwd = {}
        for n in q.get('normalized', []): fwd[n['from']] = n['to']
        rd = {r['from']: r['to'] for r in q.get('redirects', [])}
        byt = {p['title']: p for p in q.get('pages', {}).values()}
        for t in b:
            t1 = fwd.get(t, t); t2 = rd.get(t1, t1); p = byt.get(t2)
            if p and 'missing' not in p and p.get('pageprops', {}).get('wikibase_item'):
                S['t2q'][t] = p['pageprops']['wikibase_item']; S['redir'][t] = t2; S['q2'].append(p['pageprops']['wikibase_item'])
        S['i'] += 50; save()
    # stage 3: entries by id (the data's own Q-ids and those found in stage 2)
    Q = sorted(set(L['qids']) | set(S['q2']))
    while S['stage'] == 3 and not out_of_time():
        b = Q[S['i']:S['i'] + 50]
        if not b: S['stage'] = 4; S['i'] = 0; break
        j = api(WD, {'action': 'wbgetentities', 'ids': '|'.join(b), 'props': 'sitelinks'})
        for qid, ent in j.get('entities', {}).items():
            if 'missing' in ent: S['sl'][qid] = None; continue
            S['sl'][ent.get('id', qid)] = wp_sitelinks(ent)
            if ent.get('id') and ent['id'] != qid: S['redir'][qid] = ent['id']
        S['i'] += 50; save()
    # stage 4: pages deleted from English Wikipedia: search Wikidata by the title; keep the top hits with their dates
    gone = [t for t in M if t not in S['t2q']]
    while S['stage'] == 4 and not out_of_time():
        b = gone[S['i']:S['i'] + 10]
        if not b: S['stage'] = 5; break
        for t in b:
            j = api(WD, {'action': 'query', 'list': 'search', 'srsearch': t, 'srlimit': 5})
            ids = [h['title'] for h in j.get('query', {}).get('search', []) if re.match(r'^Q\d+$', h['title'])]
            cands = []
            if ids:
                e = api(WD, {'action': 'wbgetentities', 'ids': '|'.join(ids), 'props': 'labels|descriptions|claims|sitelinks', 'languages': 'en'})
                for qid in ids:
                    ent = e.get('entities', {}).get(qid, {})
                    yrs = {}
                    for pr in ('P585', 'P580', 'P582', 'P569', 'P570', 'P571', 'P577'):
                        for c in (ent.get('claims') or {}).get(pr, []):
                            v = (c.get('mainsnak', {}).get('datavalue') or {}).get('value')
                            if isinstance(v, dict) and 'time' in v:
                                m = re.match(r'([+-]\d+)-', v['time'])
                                if m: yrs.setdefault(pr, []).append(int(m.group(1)))
                    cands.append({'q': qid, 'label': (ent.get('labels') or {}).get('en', {}).get('value'), 'desc': (ent.get('descriptions') or {}).get('en', {}).get('value'),
                                  'years': yrs, 'sl': wp_sitelinks(ent)})
            S['search'][t] = cands
        S['i'] += 10; save()
    print('DONE' if S['stage'] == 5 else f"stage {S['stage']} at {S['i']}", 'entries', len(S['sl']), 'missing', len(M), 'gone', len(gone), round(time.time() - t0), 's')


def do_apply():

    S = json.load(open(OUT))
    CC = {i: c for i, (n, c) in enumerate(json.load(open('cities/city_country.json')))}
    FIVE = ['en', 'fr', 'de', 'es', 'it']
    LOCAL = {'United Kingdom': ['en', 'cy', 'gd'], 'French Fifth Republic': ['fr', 'br', 'oc', 'co', 'eu', 'ca'], 'Republic of Austria': ['de'],
      'Germany (Federal Republic)': ['de'], 'Russian Federation': ['ru'], 'Republic of Turkey': ['tr'], 'Republic of Hungary': ['hu'],
      'Republic of Poland': ['pl'], 'Czech Republic (Czechia)': ['cs'], 'Italian Republic': ['it', 'scn', 'nap', 'vec', 'sc'],
      'Kingdom of Spain': ['es', 'ca', 'eu', 'gl', 'ast'], 'Kingdom of the Netherlands': ['nl', 'fy'], 'Ukraine': ['uk'], 'Kingdom of Denmark': ['da'],
      'Portuguese Republic': ['pt'], 'Kingdom of Sweden': ['sv'], 'Kingdom of Belgium': ['nl', 'fr', 'de'], 'Ireland': ['en', 'ga'], 'Romania': ['ro'],
      'Republic of Latvia': ['lv'], 'Republic of Lithuania': ['lt'], 'Switzerland': ['de', 'fr', 'it', 'rm'], 'Georgia': ['ka'],
      'Kingdom of Norway': ['no', 'nn'], 'Algeria': ['ar', 'fr'], 'Hellenic Republic': ['el'], 'Republic of Finland': ['fi', 'sv'],
      'Republic of Moldova': ['ro'], 'Syria': ['ar'], 'Republic of Bulgaria': ['bg'], 'Republic of Belarus': ['be', 'ru'], 'Republic of Serbia': ['sr'],
      'Slovak Republic': ['sk'], 'Republic of Croatia': ['hr'], 'Russian-occupied Ukraine': ['uk', 'ru'], 'Bosnia and Herzegovina': ['bs', 'sr', 'hr'],
      'Grand Duchy of Luxembourg': ['lb', 'fr', 'de'], 'Republic of Estonia': ['et'], 'Republic of Slovenia': ['sl'], 'North Macedonia': ['mk'],
      'Montenegro': ['sr', 'sh'], 'Republic of Kosovo': ['sq', 'sr'], 'Republic of Albania': ['sq'], 'Iraq': ['ar'], 'Iran': ['fa'],
      'Republic of Armenia': ['hy'], 'Republic of Azerbaijan': ['az'], 'Republic of Tunisia': ['ar', 'fr'], 'Kingdom of Morocco': ['ar', 'fr'],
      'Republic of Iceland': ['is'], 'Republic of Cyprus': ['el', 'tr'], 'Lebanon': ['ar', 'fr'], 'Transnistria': ['ro', 'ru'], 'Abkhazia': ['ab', 'ru'],
      'South Ossetia': ['os', 'ru'], 'Malta': ['mt', 'en'], 'Principality of Andorra': ['ca']}
    GENERAL = ['ru', 'pl', 'nl', 'pt', 'sv', 'uk', 'cs', 'hu', 'ro', 'tr', 'el', 'ca', 'da', 'no', 'fi', 'bg', 'sr', 'hr', 'sk', 'sl', 'lt', 'lv', 'et']
    redir = S['redir']
    def ent(q):
        while q in redir and redir[q] != q and re.match(r'^Q\d+$', redir[q]): q = redir[q]
        return q, S['sl'].get(q)
    def pick(sl, ci, name):
        """link for the English page"""
        if not sl: return None
        if 'en' in sl: return '' if sl['en'] == name else sl['en']
        loc = LOCAL.get(CC.get(ci), [])
        order = [l for l in loc if l in FIVE[1:]] + [l for l in FIVE[1:] if l not in loc] + [l for l in loc if l not in FIVE] + GENERAL
        for l in order:
            if l in sl: return f'{l}:{sl[l]}'
        if sl:
            l = sorted(sl)[0]; return f'{l}:{sl[l]}'
        return None
    def find_gone(title, years):
        """an English article deleted since the data was gathered: the Wikidata entry with that label and a matching year"""
        best = None
        for c in S['search'].get(title, []):
            if (c.get('label') or '').lower() != title.lower(): continue
            ys = [y for v in c['years'].values() for y in v]
            if any(abs(y - yy) <= 1 for y in ys for yy in years if yy is not None):
                if best: return None                       # two matches: leave it
                best = c
        if best: S['sl'].setdefault(best['q'], best['sl'])
        return best['q'] if best else None
    for cs in S['search'].values():                    # entries found by searching (for English articles since deleted)
        for c in cs: S['sl'].setdefault(c['q'], c['sl'])
    TITLES = {}
    MISSING = set(S['missing'])
    stats = {'en': 0, 'other': 0, 'none': 0, 'noqid': 0, 'renamed': 0, 'gone_found': 0}
    def resolve(ci, name, t, years, q0=''):
        old = t
        if q0: q = q0
        elif re.match(r'^Q\d+$', t or ''): q = t
        else:
            title = t or name; q = S['t2q'].get(title)
            if not q: q = find_gone(title, years); stats['gone_found'] += bool(q)
        if not q:
            stats['noqid'] += 1
            if not re.match(r'^Q\d+$', t or '') and (t or name) in MISSING: return None, ''   # English article gone, entry not found: no link
            return (old if old is not None else ''), ''
        q, sl = ent(q)
        link = pick(sl, ci, name)
        if sl: TITLES[q] = [sl.get(l, '') for l in FIVE]
        if link is None: stats['none'] += 1
        elif re.match(r'^[a-z][a-z-]*:', link): stats['other'] += 1
        else:
            stats['en'] += 1
            if (link or name) != (old or name) and not re.match(r'^Q\d+$', old or ''): stats['renamed'] += 1
        return link, q
    E = json.load(open('city-events.json'))
    changed = []
    for r in E['ev']:
        ci, y, md, ki, sl, n, t, end = r[:8]
        link, q = resolve(ci, n, t, [y, end], r[8] if len(r) > 8 else '')
        if link != t and not (link == '' and t == ''): changed.append((n, t, link))
        r[:] = [ci, y, md, ki, sl, n, link, end, q]
    E['source'] = E['source'].split(';')[0] + '; links checked against Wikidata ' + time.strftime('%B %-d, %Y')
    json.dump(E, open('city-events.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('events', stats, 'changed', len(changed)); [print('  ', c) for c in changed[:25]]
    ev_stats = dict(stats); stats.update({k: 0 for k in stats})
    P = json.load(open('city-people.json'))
    for r in P['pp']:
        ci, w, b, d, sl, n, role, t = r[:8]
        link, q = resolve(ci, n, t, [b, d], r[8] if len(r) > 8 else '')
        r[:] = [ci, w, b, d, sl, n, role, link, q]
    P['source'] = P['source'].split(';')[0] + '; links checked against Wikidata ' + time.strftime('%B %-d, %Y')
    json.dump(P, open('city-people.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('people', stats)
    json.dump({'source': 'Wikidata (CC0), ' + time.strftime('%B %-d, %Y'), 'langs': FIVE, 't': TITLES}, open('wiki-titles.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('titles for', len(TITLES), 'entries;', {l: sum(1 for v in TITLES.values() if v[i]) for i, l in enumerate(FIVE)})
    json.dump({'events': ev_stats, 'people': stats}, open(OUT + '.stats.json', 'w'))


{"list": do_list, "fetch": do_fetch, "apply": do_apply}[sys.argv[1]]()
