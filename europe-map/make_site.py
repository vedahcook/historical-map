"""Make a copy of the map that any website can host: a folder with index.html and the files it loads.

Usage (in europe-map/): python3 make_site.py [OUT]      (OUT defaults to ../_site)
europe-borders.html is written for Claude artifacts, which add the page's header (document type, character set,
phone-screen setting) when it is published. index.html is the same page with that header, so it works on its own.
Upload the whole folder to any web host, or run deploy_site.sh to publish it with GitHub Pages."""
import glob, os, shutil, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '../_site'
src = open('europe-borders.html', encoding='utf-8').read()
cut = src.index('</style>') + len('</style>')          # the title, font link and styles go in the head
head, body = src[:cut], src[cut:]
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Europe's country borders on July 1 of every year from 1000 to 2026, from OpenHistoricalMap checked against other datasets.">
<style>[hidden] {{ display: none !important; }}</style>
{head}
</head>
<body>{body}</body>
</html>
'''
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(page)
for f in sorted(glob.glob('europe-borders-[0-9]*.json')) + ['flags.webp', 'relief.webp', 'terrain.json', 'city-events.json', 'city-people.json']: shutil.copy(f, OUT)   # the earlier eras' maps, terrain, events, people
shutil.copytree('flag-images', f'{OUT}/flag-images')
open(f'{OUT}/.nojekyll', 'w').close()                  # GitHub Pages: serve the files as they are
n = sum(len(fs) for _, _, fs in os.walk(OUT)); size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
print(f'{OUT}: {n} files, {size / 1e6:.1f} MB')
