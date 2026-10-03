# Trim scan borders, then write a 16:9 card image (focal point) and a full-size view, both WebP.
from PIL import Image
import os
SRC = '/mnt/user-data/uploads/historical-map/europe-map/views/pilot/'
OUT = '/home/claude/views/site/views/'; os.makedirs(OUT, exist_ok=True)
# name: (trim box as fractions l, t, r, b), (focal x, focal y)
P = {
 'cologne-1493': ((0, 0, 1, 1), (0.36, 0.5)), 'cologne-1572': ((0.01, 0.01, 0.99, 0.99), (0.5, 0.5)),
 'cologne-1635': ((0.02, 0.02, 0.98, 0.98), (0.5, 0.33)), 'cologne-1845': ((0, 0, 1, 1), (0.55, 0.5)),
 'cologne-1895': ((0.02, 0.02, 0.98, 0.98), (0.5, 0.42)), 'cologne-1945': ((0, 0, 1, 1), (0.55, 0.3)),
 'cologne-2014': ((0, 0, 1, 1), (0.6, 0.5)),
 'vienna-1493': ((0, 0, 1, 1), (0.3, 0.5)), 'vienna-1572': ((0.01, 0.03, 0.99, 0.97), (0.5, 0.6)),
 'vienna-1649': ((0, 0, 1, 1), (0.5, 0.42)), 'vienna-1760': ((0, 0, 1, 1), (0.5, 0.55)),
 'vienna-1895': ((0.01, 0.01, 0.99, 0.97), (0.5, 0.4)), 'vienna-2018': ((0, 0, 1, 1), (0.5, 0.5)), 'vienna-2013': ((0, 0, 1, 1), (0.42, 0.45)),
 'paris-1572': ((0.142, 0.168, 0.854, 0.84), (0.5, 0.5)), 'paris-1615': ((0, 0, 1, 1), (0.5, 0.45)),
 'paris-1752': ((0, 0, 1, 1), (0.62, 0.5)), 'paris-1860': ((0, 0, 1, 1), (0.5, 0.35)),
 'paris-1895': ((0.035, 0.035, 0.965, 0.965), (0.5, 0.45)), 'paris-1948': ((0.03, 0.03, 0.97, 0.97), (0.5, 0.5)),
 'paris-2014': ((0, 0, 1, 1), (0.5, 0.5)),
 'istanbul-1493': ((0, 0, 1, 0.94), (0.5, 0.45)), 'istanbul-1572': ((0.01, 0.01, 0.99, 0.99), (0.5, 0.45)),
 'istanbul-1638': ((0, 0, 1, 1), (0.5, 0.55)), 'istanbul-1775': ((0, 0, 1, 1), (0.45, 0.5)),
 'istanbul-1852': ((0.245, 0.265, 0.755, 0.724), (0.5, 0.5)), 'istanbul-1895': ((0.02, 0.02, 0.98, 0.98), (0.5, 0.5)),
 'istanbul-1955': ((0, 0, 1, 1), (0.5, 0.5)), 'istanbul-2011': ((0, 0, 1, 1), (0.5, 0.5)),
}
CW, CH = 720, 405
sizes = {}
for n, (t, (fx, fy)) in P.items():
    f = SRC + n + '.jpg'
    if not os.path.exists(f): print('missing', n); continue
    im = Image.open(f).convert('RGB'); w, h = im.size
    im = im.crop((round(t[0] * w), round(t[1] * h), round(t[2] * w), round(t[3] * h))); w, h = im.size
    full = im.copy(); full.thumbnail((1280, 1280)); full.save(OUT + n + '.webp', 'WEBP', quality=80, method=6)
    # card: largest 16:9 box around the focal point
    if w / h > CW / CH: bw, bh = round(h * CW / CH), h
    else: bw, bh = w, round(w * CH / CW)
    x0 = min(max(0, round(fx * w - bw / 2)), w - bw); y0 = min(max(0, round(fy * h - bh / 2)), h - bh)
    card = im.crop((x0, y0, x0 + bw, y0 + bh)).resize((CW, CH), Image.LANCZOS)
    card.save(OUT + n + '-card.webp', 'WEBP', quality=78, method=6)
    sizes[n] = full.size
    print(n, im.size, 'card from', (bw, bh), os.path.getsize(OUT + n + '-card.webp') // 1024, 'KB', os.path.getsize(OUT + n + '.webp') // 1024, 'KB')
import json; json.dump(sizes, open('/home/claude/views/full_sizes.json', 'w'))
