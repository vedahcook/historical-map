"""Get page_data.json and topo.json back out of the built page (europe-borders.html), for build_page.py. They are not
kept in the repository (they come out of merge_eras.py, whose inputs are not kept either), but the page holds both:
  python3 extract_page_data.py [europe-borders.html] [output folder]      (writes page_data.json and topo.json)
Then: cd <output folder> && python3 <repo>/europe-map/build_page.py <repo>/europe-map/europe-borders.html"""
import json, os, re, sys
src = sys.argv[1] if len(sys.argv) > 1 else 'europe-borders.html'
out = sys.argv[2] if len(sys.argv) > 2 else '.'
page = open(src).read()
def block(i):
    m = re.search(rf'<script type="application/json" id="{i}">(.*?)</script>', page, re.S)
    return m.group(1).replace('<\\/', '</')
os.makedirs(out, exist_ok=True)
topo = block('topo'); json.loads(topo)
open(f'{out}/topo.json', 'w').write(topo)
data = json.loads(block('data'))
json.dump(data, open(f'{out}/page_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('wrote', f'{out}/page_data.json', f'{out}/topo.json')
