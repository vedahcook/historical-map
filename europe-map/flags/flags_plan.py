"""Which article (and so which Wikidata flag) each description shown on the map uses, for which years.
Usage (in the later era's folder, after merge_eras.py): python3 flags_plan.py
Writes flags_plan.json (description index -> [[article, first year, last year], ...]) and flags_articles.json."""
import json, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from articles import ARTICLE, NO_FLAG

P = json.load(open('page_data.json')); E = json.load(open('europe-borders-1500.json'))
U, desc = P['units'], P['desc']
occ = {u['k'] for u in U if u.get('o')}
used = {}
for lab in (P['late']['labels'], E['labels']):
    for y, rows in lab.items():
        for r in rows:
            if r[6] < 0: continue
            d = used.setdefault(r[6], {'units': set(), 'y0': 9999, 'y1': 0})
            d['units'].add(U[r[0]]['k']); d['y0'] = min(d['y0'], int(y)); d['y1'] = max(d['y1'], int(y))
plan = {}
for i, d in sorted(used.items()):
    t = desc[i]['t']
    if t in NO_FLAG or all(k in occ for k in d['units']): continue      # occupied or annexed land: no flag
    u = sorted(d['units'])[0]
    a = ARTICLE.get((u, t, d['y0'])) or ARTICLE.get((u, t)) or ARTICLE.get(t) or re.sub(r'\s*\(.*?\)\s*$', '', t).strip().replace('’', "'")
    plan[i] = a if isinstance(a, list) else [(a, d['y0'], d['y1'])]
json.dump(plan, open('flags_plan.json', 'w'), ensure_ascii=False)
arts = sorted({a for v in plan.values() for a, _, _ in v})
json.dump(arts, open('flags_articles.json', 'w'), ensure_ascii=False)
print(len(plan), 'descriptions,', len(arts), 'articles')
