"""Turn cand/<slug>.json into a compact list for the picking agents: work/<slug>/candidates.md (+ the sheets beside it)."""
import json, os, sys, shutil
SRC = sys.argv[1]            # folder with cand/ and sheets/ (unzipped from the Mac)
OUT = sys.argv[2]            # work folder
for f in sorted(os.listdir(os.path.join(SRC, 'cand'))):
    if not f.endswith('.json'): continue
    slug = f[:-5]; d = json.load(open(os.path.join(SRC, 'cand', f)))
    if 'sheets' not in d: print('no sheets yet', slug); continue
    od = os.path.join(OUT, slug); os.makedirs(od, exist_ok=True)
    L = [f"# {d['city']} — period-view candidates", '',
         f"Commons category: {d['commonscat']}. Periods: " + ' · '.join(f'{i} = {p}' for i, p in enumerate(d['periods'])), '',
         'Each line: #number · period · date as read (where the date came from) · series · size · license · file name · artist · date field · description · city categories', '']
    for c in d['cand']:
        L.append(f"#{c['n']} · P{c['period']} · {c['label'] or c['year']} ({c['ysrc']}) · {c['series'] or '-'} · {c['w']}×{c['h']} · {c['license']}\n"
                 f"   file: {c['title']}\n   artist: {c['artist'][:120] or '-'} · date field: {c['date_raw'][:90] or '-'}\n"
                 f"   desc: {c['desc'][:260] or '-'}\n   cats: {'; '.join(c.get('rel_cats') or c['cats'][:4])[:200]}\n   preview: previews/{c.get('preview', '')}")
    open(os.path.join(od, 'candidates.md'), 'w').write('\n'.join(L) + '\n')
    for s in d['sheets']: shutil.copy(os.path.join(SRC, 'sheets', s), od)
    pv = os.path.join(od, 'previews'); os.makedirs(pv, exist_ok=True)
    for c in d['cand']:
        p = os.path.join(SRC, 'cand', slug, c.get('preview', ''))
        if c.get('preview') and os.path.exists(p): shutil.copy(p, pv)
    json.dump(d, open(os.path.join(od, 'cand.json'), 'w'), ensure_ascii=False)
    print(slug, len(d['cand']), 'candidates', len(d['sheets']), 'sheets')
