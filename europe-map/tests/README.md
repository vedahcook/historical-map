# Checking the map page

`card_check.cjs` opens the built page (`europe-borders.html`) in headless Chromium, opens city cards at given years on
a desktop and a phone screen, checks that the card stays put as the year moves, and saves screenshots in `tests/shots/`
(not committed). See the top of the file for how to run it. It needs Playwright, and topojson-client: from its CDN as on the live
site, or from a local copy (`npm install topojson-client`; the script looks for it) when the CDN can't be reached.

To rebuild the page first:

    python3 extract_page_data.py europe-borders.html /tmp/mapbuild      # page_data.json and topo.json, out of the page
    cd /tmp/mapbuild && python3 <repo>/europe-map/build_page.py <repo>/europe-map/europe-borders.html
