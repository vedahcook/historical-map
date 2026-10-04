# City views (Europe map)

Period views of cities for the map's city popup. Decisions and plan: project doc `claude/city-views-pilot.md`.
Live test page: https://vedahcook.github.io/historical-map/staging/city-views/ (all 465 cities as of October 3, 2026: the 4 pilot cities, batch 1 (25), batch 2 (100) and batch 3 (336)).
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

Batch 2 (October 3, 2026): `batch2.txt` lists the 100 cities, chosen from the map's 465 largest by peak population, number of Wikipedia
editions and population before 1700 (`batch2-ranking.json`). `round2.py` runs the search and preview steps in rounds of under 3 minutes on
the Mac's Claude workspace (background jobs there stop when each command ends). Picks in `picks/`, checks in `review/`, processed views in
`views-batch2.json`. `build_cv2.py` builds the page for all 129 cities with a city drop-down; `check3.cjs` checks that nothing moves as the
year changes. Downloads ran on the Mac (`dl2.py` pattern: 8 threads, rounds of 2 minutes) because Wikimedia blocked the cloud workspace's
picture downloads with "429 Too Many Requests".

Batch 3 (October 3, 2026): the remaining 336 cities (`batch3.txt`). `round3.py` searched with a lighter candidate set (SMALL=1).
Picking agents followed `TASK_PICK.md` (which points to `PICKING.md`), checking agents `TASK_CHECK.md`; picks in `picks/`, checks in
`review/`, processed views in `views-batch3.json` (872 views). Downloads on the Mac with `dl3.py` (6 threads; Wikimedia allows about
70 files per 2 minutes before answering 429). `process_cv3.py` trims and crops; `build_cv2.py` now builds all 465 cities.
37 cities have no usable view, mostly smaller eastern, Russian, Turkish and North African cities with few pictures on Commons.

Second search (October 3, 2026): the 109 cities with no view or one view (`deep_targets.json` on the Mac). `gather_deep.py` searches in
the city's other languages (Russian, Ukrainian, Turkish, Persian...) with words for view, panorama, postcard and old, walks the city's
Commons category tree (history, views, postcards, decades), adds the city's Wikidata pictures, accepts old pictures from 800 px wide,
and leaves out candidates offered in the first search; `round_deep.py` runs it and `sheets_deep.py` in rounds on the Mac.
`prep_deep.py` writes the candidate lists with the views each city already has; pickers followed `TASK_PICK_deep.md` (new periods
only, or a clearly better view in the same period); picks in `picks-deep/`, checks in `review-deep/`. `process_cv4.py` crops them and
merges them with the existing views (`views-deep.json`, the full list for those 109 cities). Result: 172 new views; cities with no view
went from 37 to 6, with one view from 72 to 25.
