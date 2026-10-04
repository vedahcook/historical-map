"""Candidate lists for the deeper search: like prep_md.py, plus the views each city already has."""
import json, os, sys, shutil
SRC, OUT = sys.argv[1], sys.argv[2]
V = {}
for f in ('/home/claude/cv/work/views.json', '/home/claude/cv2/work/views.json', '/home/claude/cv3/work/views.json'): V.update(json.load(open(f)))
P = [(0, 1499), (1500, 1649), (1650, 1749), (1750, 1849), (1850, 1913), (1914, 1969), (1970, 2100)]
per = lambda y: next(i for i, (a, b) in enumerate(P) if a <= y <= b)
done = []
for f in sorted(os.listdir(os.path.join(SRC, 'cand_deep'))):
    if not f.endswith('.json'): continue
    slug = f[:-5]; d = json.load(open(os.path.join(SRC, 'cand_deep', f)))
    if 'sheets' not in d: continue
    od = os.path.join(OUT, slug)
    if os.path.exists(os.path.join(od, 'candidates.md')): continue
    os.makedirs(od, exist_ok=True)
    have = V.get(slug, [])
    L = [f"# {d['city']} — more period-view candidates (second search)", '',
         f"Commons category: {d['commonscat']}. Periods: " + ' · '.join(f'{i} = {p}' for i, p in enumerate(d['periods'])), '',
         'Views this city already has (keep them unless a candidate in the same period is clearly better):']
    L += [f"- P{per(v['y'])} · {v['lab']} · {v['what']} · {v['who']}" for v in have] or ['- none']
    L += ['', 'Each line: #number · period · date as read (where the date came from) · series · size · license · file name · artist · date field · description · city categories', '']
    for c in d['cand']:
        L.append(f"#{c['n']} · P{c['period']} · {c['label'] or c['year']} ({c['ysrc']}) · {c['series'] or '-'} · {c['w']}×{c['h']} · {c['license']}\n"
                 f"   file: {c['title']}\n   artist: {c['artist'][:120] or '-'} · date field: {c['date_raw'][:90] or '-'}\n"
                 f"   desc: {c['desc'][:260] or '-'}\n   cats: {'; '.join(c.get('rel_cats') or c['cats'][:4])[:200]}\n   preview: previews/{c.get('preview', '')}")
    open(os.path.join(od, 'candidates.md'), 'w').write('\n'.join(L) + '\n')
    for s in d['sheets']: shutil.copy(os.path.join(SRC, 'sheets_deep', s), od)
    pv = os.path.join(od, 'previews'); os.makedirs(pv, exist_ok=True)
    for c in d['cand']:
        p = os.path.join(SRC, 'cand_deep', slug, c.get('preview', ''))
        if c.get('preview') and os.path.exists(p): shutil.copy(p, pv)
    json.dump(d, open(os.path.join(od, 'cand.json'), 'w'), ensure_ascii=False)
    done.append(slug)
print(len(done), 'cities prepared:', ' '.join(done))
