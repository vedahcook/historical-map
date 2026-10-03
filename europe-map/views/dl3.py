import json, os, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
UA = 'HistoricalMapPilot/1.0 (https://github.com/vedahcook/historical-map)'
L = json.load(open('urls3.json')); os.makedirs('full3', exist_ok=True); t0 = time.time()
def one(x):
    p = f"full3/{x['id']}{x['ext']}"
    if os.path.exists(p) and os.path.getsize(p) > 1000: return 'have'
    if time.time() - t0 > 105: return 'later'
    for i in range(4):
        try:
            r = requests.get(x['url'], headers={'User-Agent': UA}, timeout=40)
            if r.status_code == 200: open(p, 'wb').write(r.content); return 'ok'
            if r.status_code in (429, 503): time.sleep(5 * (i + 1)); continue
            return f'http {r.status_code}'
        except Exception as e: time.sleep(3)
    return 'failed'
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, L))
from collections import Counter; c = Counter(res)
print(dict(c), [(L[i]['file'][:50], r) for i, r in enumerate(res) if r.startswith('http') or r == 'failed'][:8], round(time.time() - t0), 's')
