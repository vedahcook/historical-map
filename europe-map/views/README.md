# City views (Europe map)

Period views of cities for the map's city popup. Decisions and plan: project doc `claude/city-views-pilot.md`.
Live test page: https://vedahcook.github.io/historical-map/staging/city-views/ (29 cities, October 2, 2026).
Pictures are not stored here: the processed ones are on the gh-pages branch (`staging/city-views/views/`), the originals on
Veda's Mac (`europe-map/views/pilot/` for the pilot, `europe-map/views/citywork/full/` for batch 1) and on Wikimedia Commons.

Steps (batch 1 ran these; paths in the scripts point at the Claude workspace, /home/claude/views and /home/claude/cv):
1. `gather.py CITY...` lists candidates from Commons per city (searches for Braun & Hogenberg, Merian, the Nuremberg Chronicle,
   photochroms, vedute, aerial photos; the city's period categories), filters by license, size, city name and date, and keeps
   6-8 per period (`cand/<slug>.json`). Resumable: progress is saved in `raw/`. `cities.json` holds each city's Wikidata item,
   Commons category and names. Run it from a machine Wikimedia doesn't throttle (Veda's Mac); `wm.py` paces requests.
2. `sheets.py SLUG...` downloads 500 px previews and lays out numbered contact sheets.
3. `prep_md.py` writes a candidate list per city; picking agents follow `PICKING.md` and write `picks/<slug>.json`;
   checking agents write `review/<slug>.json` (applied to the picks).
4. `fetch_picks.py` (or the Mac) downloads the picked pictures; `process_cv.py` trims and crops them (card 720x405, full size).
5. `extract_all.cjs` takes population, holders and flags per city from the built map page (`city_data.json`, `flags_data.json`).
6. `build_cv.py` builds the page from `template.html`: batch-1 views, the map's Wikidata events for the new cities (unchecked,
   no pictures), and the pilot's sample events, pictures and population changes for Cologne, Vienna, Paris and Istanbul.
7. Publish: `../deploy_site.sh staging DIR city-views` with DIR holding index.html, flags.webp and views/.
