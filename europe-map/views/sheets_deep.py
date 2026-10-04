"""Download a 500 px preview of each candidate and lay them out as numbered contact sheets.
Usage: python3 sheets.py SLUG [SLUG...]   (reads cand/<slug>.json; writes cand/<slug>/<n>.jpg and sheets/<slug>-<k>.jpg)"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
TW, TH, CAP, COLS, ROWS = 360, 240, 38, 4, 3
try:
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
except Exception:
    F = FB = ImageFont.load_default()
def run(slug):
    d = json.load(open(os.path.join(HERE, 'cand_deep', slug + '.json'))); os.makedirs(os.path.join(HERE, 'cand_deep', slug), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'sheets_deep'), exist_ok=True)
    tiles = []
    for c in d['cand']:
        p = os.path.join(HERE, 'cand_deep', slug, hashlib.md5(c['title'].encode()).hexdigest()[:12] + '.jpg'); c['preview'] = os.path.basename(p)
        if not os.path.exists(p):
            st = wm.download(wm.thumb_url(c['title'], 500), p)
            if st != 200: print(slug, c['n'], 'preview failed', st); continue
        try: im = Image.open(p).convert('RGB')
        except Exception: continue
        tiles.append((c, im))
    json.dump(d, open(os.path.join(HERE, 'cand_deep', slug + '.json'), 'w'), ensure_ascii=False, indent=1)
    per = COLS * ROWS
    for k in range(0, len(tiles), per):
        sheet = Image.new('RGB', (COLS * TW, ROWS * (TH + CAP)), (40, 40, 40)); dr = ImageDraw.Draw(sheet)
        for i, (c, im) in enumerate(tiles[k:k + per]):
            x, y = (i % COLS) * TW, (i // COLS) * (TH + CAP)
            t = im.copy(); t.thumbnail((TW - 6, TH - 6)); sheet.paste(t, (x + (TW - t.width) // 2, y + (TH - t.height) // 2))
            dr.rectangle([x, y + TH, x + TW, y + TH + CAP], fill=(250, 250, 245))
            dr.text((x + 6, y + TH + 2), f"#{c['n']}", fill=(180, 30, 20), font=FB)
            dr.text((x + 52, y + TH + 3), f"{c['label'] or c['year']}  {c['series']}"[:34], fill=(20, 20, 20), font=F)
            dr.text((x + 52, y + TH + 20), f"{c['w']}×{c['h']}  {c['license'][:18]}", fill=(90, 90, 90), font=F)
        sheet.save(os.path.join(HERE, 'sheets_deep', f'{slug}-{k // per + 1}.jpg'), quality=82)
    d['sheets'] = [f'{slug}-{k // per + 1}.jpg' for k in range(0, len(tiles), per)]
    json.dump(d, open(os.path.join(HERE, 'cand_deep', slug + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(slug, len(tiles), 'previews,', len(d['sheets']), 'sheets', flush=True)
if __name__ == '__main__':
    for s in sys.argv[1:]:
        try: run(s)
        except Exception as e: print('FAILED', s, repr(e), flush=True)
