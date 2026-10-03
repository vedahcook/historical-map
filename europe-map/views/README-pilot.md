# City views mockup: build files

Source for the city popup mockup (https://claude.ai/artifact/PvaAhNL4Zb1cYzmjF97fC6, version 15).
Decisions and open items: project doc `claude/city-views-pilot.md`.

To rebuild in a new Claude session: copy this folder to /home/claude/views, put flags.webp in site/,
stage the original pictures from ../pilot/ (they land in /mnt/user-data/uploads/historical-map/europe-map/views/pilot/),
then:
  python3 process.py && python3 process_ev.py   # crop and convert pictures to site/views/*.webp (needs Pillow)
  python3 build.py                              # writes site/city-views.html (template.html + data + icons2.js)
  NODE_PATH=$(npm root -g) node check8.cjs      # Playwright: checks nothing moves as the year changes; screenshots
Publish site/city-views.html with site/flags.webp and site/views/ as supporting files (or update the artifact by URL;
its published files can also be read back from the artifact).

Files
- template.html: the page (CSS, layout, all behavior). /*DATA*/ and /*ICONS*/ are filled in by build.py.
- icons2.js: the nine thin-line event icons.
- pilot_views.py: the 28 city views (year, label, what, who, license, Commons file).
- pilot_events.py: sample events (E), population changes and their causes (POP), and verified days for one-day events (DAY).
- pilot_event_images.py: each event's Wikipedia article and Commons picture (EI).
- process.py / process_ev.py: crop to 16:9 cards and full-size WebP; full_sizes.json records sizes.
- make_fetch_script.py: writes the Terminal download script from pilot_views.py (only needed while Wikimedia is blocked).
- city_data.json, flags_data.json: per city, the map's population figures, who held it each year (with colors) and flags.
  Made by extract.cjs / extract_flags.cjs, which run a copy of europe-map/europe-borders.html (saved as _x.html, served
  locally) with `window.__X = { ERAS, loadEra, CITIES, cityUnit, heldBy, flagOf, D, Y1, CSRC }` added inside its main
  function. Re-run these with more city names to scale up.
