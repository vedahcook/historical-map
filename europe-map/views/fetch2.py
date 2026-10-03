"""Download every picked view for work/picks/*.json into full/. Originals up to 25 MB come straight from upload.wikimedia.org
(no thumbnail rendering, which Wikimedia throttles here); bigger files use the 1280 px (1920 for wide panoramas) thumbnail.
Resumable; writes full/index.json mapping Commons file name -> local file."""
import json, glob, os, sys, hashlib, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import wm
W = 'work'; os.makedirs('full', exist_ok=True)
idx = json.load(open('full/index.json')) if os.path.exists('full/index.json') else {}
files = {}
for pf in sorted(glob.glob(f'{W}/picks/*.json')):
    slug = os.path.basename(pf)[:-5]; cand = {c['title']: c for c in json.load(open(f'{W}/{slug}/cand.json'))['cand']}
    for p in json.load(open(pf))['picks']:
        c = cand.get(p['file'])
        if c and p['file'] not in idx: files[p['file']] = c
titles = list(files); info = {}
for k in range(0, len(titles), 50):
    r = wm.commons(action='query', titles='|'.join('File:' + t for t in titles[k:k+50]), prop='imageinfo', iiprop='size|url|mime')
    norm = {n['to']: n['from'] for n in r['query'].get('normalized', [])}
    for pg in r['query']['pages']:
        if pg.get('imageinfo'): info[norm.get(pg['title'], pg['title'])[5:]] = pg['imageinfo'][0]
print('to fetch', len(titles), 'with info', len(info), flush=True)
for i, t in enumerate(titles):
    ii = info.get(t); c = files[t]
    if not ii: print('no info', t); continue
    ext = {'image/png': '.png', 'image/tiff': '.tif', 'image/webp': '.webp'}.get(ii['mime'], '.jpg')
    name = hashlib.md5(t.encode()).hexdigest()[:16]
    if ii['size'] <= 25e6: url, path = ii['url'], f'full/{name}{ext}'
    else:
        want = 1920 if c['w'] / c['h'] > 2 else 1280
        url, path = wm.thumb_url(t, want), f"full/{name}{'.png' if ii['mime'] == 'image/png' else '.jpg'}"
    try:
        st = wm.download(url, path)
    except Exception as e:
        print('FAILED', t, e, flush=True); continue
    if st == 200: idx[t] = path
    else: print('FAILED', st, t, flush=True)
    if i % 10 == 0: json.dump(idx, open('full/index.json', 'w'), ensure_ascii=False); print(i, 'done', flush=True)
json.dump(idx, open('full/index.json', 'w'), ensure_ascii=False)
print('finished', len(idx), flush=True)
