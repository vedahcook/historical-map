"""Download each picked view (1280 px wide, 1920 for wide panoramas, the original if smaller) into full/<id>.<ext>.
Usage: python3 fetch_picks.py work   (reads work/picks/<slug>.json and work/<slug>/cand.json; writes work/picked.json)"""
import json, os, sys, glob, hashlib, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
W = sys.argv[1]; os.makedirs(os.path.join(W, 'full'), exist_ok=True)
out = json.load(open(os.path.join(W, 'picked.json'))) if os.path.exists(os.path.join(W, 'picked.json')) else {}
for pf in sorted(glob.glob(os.path.join(W, 'picks', '*.json'))):
    slug = os.path.basename(pf)[:-5]; P = json.load(open(pf)); cand = json.load(open(os.path.join(W, slug, 'cand.json')))['cand']
    size = {c['title']: (c['w'], c['h'], c['mime']) for c in cand}
    ids = []
    for p in P['picks']:
        if p['file'] not in size: print('NOT A CANDIDATE', slug, p['file']); continue
        w, h, mime = size[p['file']]
        vid = f"{slug}-{p['y']}"
        while vid in ids: vid += 'b'
        ids.append(vid); p['id'] = vid
        want = 1920 if w / h > 2.0 else 1280
        n = p['file'].replace(' ', '_'); hh = hashlib.md5(n.encode('utf-8')).hexdigest()
        if w > want: url, ext = wm.thumb_url(p['file'], want), ('.png' if mime == 'image/png' else '.jpg')
        else: url, ext = f"https://upload.wikimedia.org/wikipedia/commons/{hh[0]}/{hh[:2]}/{urllib.parse.quote(n)}", ('.png' if mime == 'image/png' else '.jpg')
        path = os.path.join(W, 'full', vid + ext); p['path'] = path
        if not os.path.exists(path):
            st = wm.download(url, path)
            if st != 200: print('FAILED', vid, st, url); p['path'] = None; continue
        print('ok', vid, flush=True)
    out[slug] = P
    json.dump(out, open(os.path.join(W, 'picked.json'), 'w'), ensure_ascii=False, indent=1)
print('cities', len(out))
