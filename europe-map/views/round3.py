"""One round (under 3 minutes) for the cities in batch3.txt: for each city not finished, run the next step (search, then sheets)."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
CITIES = [l.strip() for l in open('batch3.txt') if l.strip()]
slug = lambda t: re.sub(r'[^a-z]+', '-', t.lower().replace('ó', 'o')).strip('-')
def state(c):
    p = f'cand/{slug(c)}.json'
    if not os.path.exists(p) or not os.path.exists(f'raw/{slug(c)}.json'): return 'search'
    return 'done' if 'sheets' in json.load(open(p)) else 'sheets'
env = dict(os.environ, WM_GAP='0.3', SMALL='1'); procs = []
todo = [(c, state(c)) for c in CITIES]; todo = [t for t in todo if t[1] != 'done']
for c, s in todo[:int(sys.argv[1]) if len(sys.argv) > 1 else 16]:
    cmd = ['timeout', '160', 'python3', 'gather.py' if s == 'search' else 'sheets.py', c if s == 'search' else slug(c)]
    procs.append(subprocess.Popen(cmd, env=env, stdout=open('chunk3.log', 'a'), stderr=subprocess.STDOUT))
for p in procs: p.wait()
st = {c: state(c) for c in CITIES}
print('done', sum(v == 'done' for v in st.values()), 'of', len(CITIES), '| sheets next', sum(v == 'sheets' for v in st.values()), '| search left', sum(v == 'search' for v in st.values()))
