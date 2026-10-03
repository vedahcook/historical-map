# Event pictures: a 16:9 card (wide pictures cropped to the middle; tall ones shown whole over a blurred, darkened
# copy of themselves) and a full-size copy, both WebP. Adds their sizes to full_sizes.json.
from PIL import Image, ImageFilter, ImageEnhance
import os, json, glob
SRC = '/mnt/user-data/uploads/historical-map/europe-map/views/pilot/'
OUT = '/home/claude/views/site/views/'; os.makedirs(OUT, exist_ok=True)
sizes = json.load(open('full_sizes.json'))
CW, CH = 720, 405
for f in sorted(glob.glob(SRC + 'ev-*.jpg') + glob.glob(SRC + 'ev-*.png')):
    n = os.path.splitext(os.path.basename(f))[0]
    im = Image.open(f); im = im.convert('RGBA').convert('RGB') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
    w, h = im.size
    full = im.copy(); full.thumbnail((1280, 1280)); full.save(OUT + n + '.webp', 'WEBP', quality=80, method=6); sizes[n] = full.size
    if w / h >= 1.25:          # wide enough: crop the middle to 16:9
        bw, bh = (round(h * CW / CH), h) if w / h > CW / CH else (w, round(w * CH / CW))
        x0, y0 = (w - bw) // 2, max(0, round(h * 0.45 - bh / 2)); y0 = min(y0, h - bh)
        card = im.crop((x0, y0, x0 + bw, y0 + bh)).resize((CW, CH), Image.LANCZOS)
    else:                      # tall or square: the whole picture over a blurred copy
        bg = im.copy(); s = max(CW / w, CH / h); bg = bg.resize((round(w * s) + 1, round(h * s) + 1)); 
        bx, by = (bg.width - CW) // 2, (bg.height - CH) // 2; bg = bg.crop((bx, by, bx + CW, by + CH))
        bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(18))).enhance(0.55)
        fg = im.copy(); fg.thumbnail((CW, CH), Image.LANCZOS)
        bg.paste(fg, ((CW - fg.width) // 2, (CH - fg.height) // 2)); card = bg
    card.save(OUT + n + '-card.webp', 'WEBP', quality=78, method=6)
    print(n, (w, h))
json.dump(sizes, open('full_sizes.json', 'w'))
