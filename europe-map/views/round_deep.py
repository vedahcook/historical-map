"""One round (under 3 minutes) of the deeper search for deep_targets.json: for each city not finished, the next step (search, then sheets)."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
CITIES = [t['name'] for t in json.load(open('deep_targets.json'))]
slug = lambda t: re.sub(r'[^a-z]+', '-', t.lower().replace('ó', 'o')).strip('-')
def state(c):
    p = f'cand_deep/{slug(c)}.json'
    if not os.path.exists(p) or not os.path.exists(f'raw_deep/{slug(c)}.json'): return 'search'
    return 'done' if 'sheets' in json.load(open(p)) else 'sheets'
env = dict(os.environ, WM_GAP='0.3'); procs = []
todo = [(c, state(c)) for c in CITIES]; todo = [t for t in todo if t[1] != 'done']
ns, nh = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (10, 8)
todo = [t for t in todo if t[1] == 'search'][:ns] + [t for t in todo if t[1] == 'sheets'][:nh]
for c, s in todo:
    cmd = ['timeout', '160', 'python3', 'gather_deep.py' if s == 'search' else 'sheets_deep.py', c if s == 'search' else slug(c)]
    procs.append(subprocess.Popen(cmd, env=env, stdout=open('deep.log', 'a'), stderr=subprocess.STDOUT))
for p in procs: p.wait()
st = {c: state(c) for c in CITIES}
print('done', sum(v == 'done' for v in st.values()), 'of', len(CITIES), '| sheets next', sum(v == 'sheets' for v in st.values()), '| search left', sum(v == 'search' for v in st.values()))
