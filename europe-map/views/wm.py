"""Polite Wikimedia client: one request per second, waits out 429s, standard thumbnail widths only."""
import time, json, requests, urllib.parse, hashlib, os
UA = 'HistoricalMapPilot/1.0 (https://github.com/vedahcook/historical-map)'
S = requests.Session(); S.headers['User-Agent'] = UA
_last = [0.0]
GAP = float(os.environ.get("WM_GAP", "1.05"))
def _pace(gap=None):
    gap = GAP if gap is None else gap
    d = time.time() - _last[0]
    if d < gap: time.sleep(gap - d)
    _last[0] = time.time()
def get(url, params=None, stream=False, tries=14, post=False):
    for i in range(tries):
        _pace()
        try:
            r = S.post(url, data=params, timeout=60) if post else S.get(url, params=params, timeout=60, stream=stream)
        except requests.RequestException as e:
            time.sleep(5 * (i + 1)); continue
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get('retry-after'); time.sleep(min(90, max(int(ra) + 1 if ra and ra.isdigit() else 0, 8 * (i + 1)))); continue
        return r
    raise RuntimeError(f'gave up on {url} {params}')
def api(site, **p):
    p.setdefault('format', 'json'); p.setdefault('formatversion', 2)
    for i in range(5):
        r = get(f'https://{site}/w/api.php', params=p, post=len(str(p)) > 1500)
        try: return r.json()
        except ValueError: time.sleep(5 * (i + 1))
    raise RuntimeError('no JSON from ' + site)
def commons(**p): return api('commons.wikimedia.org', **p)
def thumb_url(fname, width):
    """upload.wikimedia.org thumbnail URL (thumb.wikimedia.org is not on the allowed list)"""
    n = fname.replace(' ', '_'); h = hashlib.md5(n.encode('utf-8')).hexdigest()
    q = urllib.parse.quote(n)
    ext = n.rsplit('.', 1)[-1].lower()
    suffix = q + ('.jpg' if ext in ('tif', 'tiff', 'pdf', 'djvu') else '.png' if ext in ('svg',) else '')
    pre = 'page1-' if ext in ('pdf', 'djvu', 'tif', 'tiff') and False else ''
    return f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{pre}{width}px-{suffix}'
def download(url, path):
    r = get(url)
    if r.status_code != 200: return r.status_code
    open(path, 'wb').write(r.content); return 200
