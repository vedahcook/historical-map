"""Crop each picked view: trim, then a 16:9 card (720x405) centered on the focal point and a full-size copy, both WebP.
Writes /home/claude/views/site/views/<id>.webp and <id>-card.webp, and work/views.json (the views per city with their ids and sizes)."""
import json, glob, os
from PIL import Image
W = '/home/claude/cv2/work'; OUT = '/home/claude/views/site/views/'; os.makedirs(OUT, exist_ok=True)
urls = json.load(open('/home/claude/cv2/full/urls2.json')); path_of = {}
for x in urls: path_of.setdefault(x['file'], f"/home/claude/cv2/full/full2/{x['id']}{x['ext']}")
CW, CH = 720, 405; res = {}; missing = []
for pf in sorted(glob.glob(f'{W}/picks/*.json')):
    slug = os.path.basename(pf)[:-5]; P = json.load(open(pf)); ids = []; views = []
    for p in sorted(P['picks'], key=lambda p: p['y']):
        src = path_of.get(p['file'])
        if not src or not os.path.exists(src): missing.append((slug, p['file'])); continue
        vid = f"{slug}-{p['y']}"
        while vid in ids: vid += 'b'
        ids.append(vid)
        im = Image.open(src); im = im.convert('RGBA').convert('RGB') if im.mode in ('P', 'LA', 'RGBA', 'I;16', 'I') else im.convert('RGB')
        w, h = im.size; t = p.get('trim') or [0, 0, 1, 1]
        im = im.crop((round(t[0] * w), round(t[1] * h), round(t[2] * w), round(t[3] * h))); w, h = im.size
        full = im.copy(); full.thumbnail((1600, 1280) if w / h > 2 else (1280, 1280), Image.LANCZOS); full.save(OUT + vid + '.webp', 'WEBP', quality=80, method=6)
        fx, fy = p.get('focal') or [0.5, 0.5]
        bw, bh = (round(h * CW / CH), h) if w / h > CW / CH else (w, round(w * CH / CW))
        x0 = min(max(0, round(fx * w - bw / 2)), w - bw); y0 = min(max(0, round(fy * h - bh / 2)), h - bh)
        im.crop((x0, y0, x0 + bw, y0 + bh)).resize((CW, CH), Image.LANCZOS).save(OUT + vid + '-card.webp', 'WEBP', quality=78, method=6)
        v = {'id': vid, 'y': p['y'], 'lab': p['lab'], 'what': p['what'], 'who': p['who'], 'lic': p['lic'], 'f': p['file'], 'w': full.size[0], 'h': full.size[1]}
        if p.get('event'): v['event'] = True
        views.append(v)
        if bw < 560: print('soft card', vid, (bw, bh))
    res[slug] = views
json.dump(res, open(f'{W}/views.json', 'w'), ensure_ascii=False, indent=1)
print(sum(map(len, res.values())), 'views in', len(res), 'cities; missing', missing)
