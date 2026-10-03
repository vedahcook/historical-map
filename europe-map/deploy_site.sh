#!/bin/sh
# Publish the map with GitHub Pages. Run in europe-map/ after the page is rebuilt.
#   ./deploy_site.sh              the live map, https://vedahcook.github.io/historical-map/ (the staging copy is kept)
#   ./deploy_site.sh staging      a test copy at https://vedahcook.github.io/historical-map/staging/, marked "Staging" and
#                                 hidden from search engines (the live map is kept)
#   ... DIR SUBPATH               (either target) also publish the folder DIR at SUBPATH inside it, for example
#                                 ./deploy_site.sh staging ../_cityviews city-views  ->  .../staging/city-views/
# The gh-pages branch is replaced by a single commit each time, so it never grows. Pages update a minute or two later.
set -e
TARGET=${1:-live}; [ $# -gt 0 ] && shift
case "$TARGET" in live|staging) ;; *) echo "usage: $0 [live|staging] [DIR SUBPATH]..."; exit 1;; esac
REMOTE=$(git -C .. remote get-url origin)
ROOT=$(cd .. && pwd)
rm -rf "$ROOT/_build" "$ROOT/_old" "$ROOT/_site"
if [ "$TARGET" = staging ]; then python3 make_site.py "$ROOT/_build" --staging; else python3 make_site.py "$ROOT/_build"; fi
while [ $# -ge 2 ]; do mkdir -p "$ROOT/_build/$2"; cp -R "$1"/. "$ROOT/_build/$2/"; shift 2; done
git clone -q --depth 1 --branch gh-pages "$REMOTE" "$ROOT/_old" 2>/dev/null || mkdir -p "$ROOT/_old"
rm -rf "$ROOT/_old/.git"
mkdir -p "$ROOT/_site"
if [ "$TARGET" = live ]; then
  cp -R "$ROOT/_build"/. "$ROOT/_site/"
  [ -d "$ROOT/_old/staging" ] && cp -R "$ROOT/_old/staging" "$ROOT/_site/staging"
else
  cp -R "$ROOT/_old"/. "$ROOT/_site/"; rm -rf "$ROOT/_site/staging"
  cp -R "$ROOT/_build" "$ROOT/_site/staging"
fi
touch "$ROOT/_site/.nojekyll"
cd "$ROOT/_site"
git init -q -b gh-pages
git add -A
git -c user.name="$(git -C .. config user.name)" -c user.email="$(git -C .. config user.email)" \
  commit -q -m "Europe's borders map ($TARGET updated), built from $(git -C .. rev-parse --abbrev-ref HEAD) $(git -C .. rev-parse --short HEAD)"
git push -q -f "$REMOTE" gh-pages
rm -rf .git "$ROOT/_build" "$ROOT/_old"
echo "pushed to gh-pages ($TARGET)"
