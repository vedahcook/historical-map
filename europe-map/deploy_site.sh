#!/bin/sh
# Publish the map with GitHub Pages: build the site folder (make_site.py) and push it as the only commit on the
# gh-pages branch, replacing what was there, so the branch never grows. Run in europe-map/ after the page is rebuilt.
# The map then appears at https://vedahcook.github.io/historical-map/ a minute or two later.
set -e
python3 make_site.py ../_site
cd ../_site
rm -rf .git
git init -q -b gh-pages
git add -A
git -c user.name="$(git -C .. config user.name)" -c user.email="$(git -C .. config user.email)" \
  commit -q -m "Europe's borders map, built from main $(git -C .. rev-parse --short HEAD)"
git push -q -f "$(git -C .. remote get-url origin)" gh-pages
rm -rf .git
echo "pushed to gh-pages"
