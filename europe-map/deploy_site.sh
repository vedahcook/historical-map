#!/bin/sh
# Publish the map with GitHub Pages (the gh-pages branch). Run in europe-map/ after the page is rebuilt.
#   sh deploy_site.sh test   a test copy at https://vedahcook.github.io/historical-map/test/ (the live map stays as it is)
#   sh deploy_site.sh        the live map at https://vedahcook.github.io/historical-map/ (a test copy there is kept)
# The branch holds a single commit, replaced each time, so it never grows; files that are already published (the
# earlier eras' maps, flags, terrain) are not uploaded again. The pages change a minute or two later.
set -e
REMOTE=$(git remote get-url origin)
NAME=$(git config user.name); EMAIL=$(git config user.email); REV=$(git rev-parse --short HEAD)
rm -rf ../_site ../_site_test ../_site_git
git clone -q --depth 1 --branch gh-pages "$REMOTE" ../_site        # what is published now
if [ "$1" = test ]; then
  python3 make_site.py ../_site/test --test
  MSG="Test copy of Europe's borders map, built from main $REV"
else
  if [ -d ../_site/test ]; then mv ../_site/test ../_site_test; fi
  mv ../_site/.git ../_site_git
  python3 make_site.py ../_site
  mv ../_site_git ../_site/.git
  if [ -d ../_site_test ]; then mv ../_site_test ../_site/test; fi
  MSG="Europe's borders map, built from main $REV"
fi
cd ../_site
git checkout -q --orphan next
git add -A
git -c user.name="$NAME" -c user.email="$EMAIL" commit -q -m "$MSG"
git push -q -f origin next:gh-pages
cd .. && rm -rf _site
echo "pushed to gh-pages"
