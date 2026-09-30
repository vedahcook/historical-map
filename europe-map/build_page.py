"""Step 8: put the map data into the page template -> europe-borders.html. Run after merge_eras.py; the page loads
the earlier maps (europe-borders-1500.json for 1500-1799, europe-borders-1000.json for 1000-1499) from beside it
when needed."""
import json, sys
here = __file__.rsplit('/', 1)[0]
tpl = open(f'{here}/page_template.html').read()
data = json.load(open('page_data.json'))
topo = open('topo.json').read()
HUES = {'light': ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'],
        'dark': ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767']}
def css(mode):
    f = ' '.join(f'--f{i}: {c};' for i, c in enumerate(data['fills'][mode]))
    h = ' '.join(f'--h{i}: {c};' for i, c in enumerate(HUES[mode]))
    return f + '\n  ' + h
page = tpl.replace('/*FILLS_LIGHT*/', css('light')).replace('/*FILLS_DARK*/', css('dark'))
page = page.replace('/*TOPO*/', topo.replace('</', '<\\/')).replace('/*DATA*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
out = sys.argv[1] if len(sys.argv) > 1 else 'europe-borders.html'
open(out, 'w').write(page)
print(out, len(page.encode()) // 1024, 'KB')
