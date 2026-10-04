# Europe's borders, 1000–2026

An interactive map of Europe's country borders, one year at a time (as of July 1). It shows OpenHistoricalMap (OHM) by default. Where another source draws a different border, the side panel lists it; picking one outlines the area on the map with a dashed line and says what each source claims. Nothing is outlined until one is picked.

The page is `europe-borders.html`, published as a Claude artifact. It holds the map for 1800–2026. These files sit beside it:

- `europe-borders-1500.json` (1500–1799) and `europe-borders-1000.json` (1000–1499): the earlier maps. The page loads the one next to the era on screen a moment after it opens, and any era at once when the slider reaches it. Opened straight from disk, a browser may refuse to load them; the page then says so for years before 1800.
- `flags.webp`: all the flag images in one picture, at the small size the popup shows.
- `flag-images/`: a larger copy of each flag, one file each, loaded only when a flag is tapped.
- `terrain.json` also holds the names of physical features and the spines they are set along.
- `city-events.json` and `city-people.json`: events in each city and people born or died there (from Wikidata), loaded a moment after the page opens. Each row ends with its Wikidata id; its link goes to the English Wikipedia article, or, where there is none, to the article in another language (marked "Spanish Wikipedia" and so on), or to the Wikidata entry.
- `city-views.json`: for each city, its period views (engravings, paintings, early photographs, a modern photo) from Wikimedia Commons, shown in the city's popup: the one made closest to the map's year. The pictures themselves (a 720 × 405 card and a larger copy of each) are on the published site in `views/`, not in the repository; `views/README.md` says how they are chosen and made.
- `wiki-titles.json` (not published yet): for each of those Wikidata ids, the article titles in English, French, German, Spanish and Italian, for pages in those languages later.
- `terrain.json` and `relief.webp`: rivers, lakes and the names of mountain ranges in more detail, and the shaded relief (from Natural Earth), loaded a moment after the page opens.

## Using the map

- **Tap a country** to highlight it and dim the rest. It keeps its color and gets an outline in a deeper shade of it, and its name goes level inside its borders, as near the middle of the main part on screen as it fits (on two lines or smaller if need be; mostly inside if it can't fit at all); the rest of the map is washed out and grayed, and any dimmed country that would still come close to the highlighted country's color is made lighter or darker until it is clearly different (otherwise a country in the stronger shade of a color could fade into exactly the paler shade, as the Ottoman Empire did next to Hungary). The map zooms so the whole country is on screen, and a popup describes it for that year: its flag (tap it to see it larger; tap anywhere to close), when the state began and ended, how, and where the border at that spot comes from. Rings mark detached parts. Tap it again, or the sea, to clear it.
- **The highlight follows the country across 1500 and 1800,** where the page switches between its three maps.
- **The timeline** shows key events, or only the highlighted country's events: when it began or ended, name changes, and gains or losses over 1,500 km². The row of events scrolls sideways.
- **Cities** appear inside the highlighted country: the ten largest of its cities on screen that year. Zooming in or panning brings in smaller towns, so a view about 200 km across still shows ten in most of Europe from the 1800s on. Tap a city for its population that year, a chart of all its figures, and who held it over the years. The list of holders uses each state's full name, as in its own popup, and for a dependent territory names the power that controlled it ("under the Ottoman Empire", "occupied by Germany") unless the name already says so; a renamed state (Russian Empire, Soviet Union, Russia) gets a line for each name. Tap a dot in the chart, a spot on the strip, or a line in the list to go to that year; the popup stays put.
- **City popups have tabs:** *Population* (the figure and chart), *Held by*, *Events* (what happened there, with links to Wikipedia; tap a row to go to that year) and *People* (who was born or died there; those alive in the year shown are in bold). The tab chosen stays chosen from city to city.
- **Event icons (switched off for now, `EVENT_ICONS` in `page_template.html`; to be redesigned):** in the year of an event, its city shows an icon for the kind of event (battle or siege, massacre or attack, uprising, treaty or congress, church council, coronation, great fire, other disaster, world's fair or Olympic Games, trial, crisis or scandal), with the city's name. Up to seven at a time, the most written-about first (the highlighted country's before the rest), so zooming in brings in others. Tapping one highlights whoever held the city and opens its popup on the Events tab.
- **Terrain:** shaded relief from elevation data, faint under the country colors; more rivers and lakes as you zoom in; and a layer of names of physical features (seas, ranges, plains, rivers, passes, peaks), set along each feature in a serif italic. The mountain button beside the zoom buttons turns the relief and these names on and off (remembered in the browser).
- **Timeline:** one even scale from 1000 to 2026 under the map (the zoomed timeline and the play, previous and next buttons were removed on October 4, 2026; the arrow keys still step one year). Above the slider, bars show how much the borders changed each year; below it, the biggest changes (or the highlighted country's) as buttons that go to their year.
- **One popup at a time,** placed to cover as little as possible of what it describes.

## How the map decides

- **Default: OHM.** It matched the historical record in 149 of 160 spot checks for the 1800s, more than the other sources.
- **Gaps in OHM are filled** from CShapes-Europe (1816 onward), then Cliopatria. A gap of a year or two with the same country on both sides is bridged.
- **Before 1800 OHM has fewer records.** It often has the Holy Roman Empire without its member states, so many small German states show as the Empire, and Cliopatria fills more of the map. Where OHM has only a large realm, the map shows the states within it that Cliopatria has: Ottoman vassals (Moldavia, Wallachia, Transylvania, the Crimean Khanate, Ragusa), the Habsburg, Spanish and Austrian Netherlands, Franche-Comté, and Lithuania before 1569.
- **Before 1500 Cliopatria draws most of the map.** OHM has records for only part of Europe, and some (France after 1050, the Empire after 1201, Hungary, Serbia, Milan) are only a name with no outline. OHM's large eastern realms (Byzantium, the Ottomans, the Mongol hordes) are drawn roughly, so where Cliopatria has a state there, it wins. The great fiefs of France (Normandy, Aquitaine, Burgundy, Flanders and others) are striped in France's color; English-held lands in France are in England's color family with French stripes until 1337.
- **Corrections** where our checks found the sources wrong or missing. Each one is explained on the page. For 1000–1499 they include Gaelic Ireland and the Lordship of Ireland, Gascony, Lorraine, Bavaria and Austria where neither source draws them, the Kingdom of Arles, Naples from 1282, Norman Apulia, Ragusa, and thin strips of coast that Cliopatria's rough coastlines leave out. For 1500–1799 they include Hungary after Mohács, Menorca, Oran, Ceuta, Calais, Ferrara, Savoy and Nice in 1792–99, Serbia and Oltenia in 1718–39, the English Commonwealth, and a few states the sources keep a year or two too long (Bohemia, Milan, Lorraine, Luxembourg, the Aq Qoyunlu).
- **Self-governing territories** are shown in their own color with stripes in the overlord's color; **occupied land** has a crosshatch in the occupier's color.
- **Colors:** each country keeps one color throughout all three maps, and neighbors in any of them never share a color. The 1800–2026 map is colored first, keeping clear of each country's neighbors in the earlier maps too; each earlier map takes the later maps' colors and colors its own countries around them. `colors.json` keeps every country's color from one build to the next.

## Alternative borders

OHM is compared with CShapes-Europe from 1816 and with Cliopatria before that. Where the map follows another source instead of OHM, OHM's own border is listed as the alternative.

- **What counts:** an area of at least 400 km² (5,000 km² for the coarser Cliopatria), at least 6 km wide, that a source puts in a different country for more than a year.
- **Compared at the level of sovereignty,** so a self-governing territory and its overlord count as the same. Before 1807, a member state of the Holy Roman Empire and the Empire count as the same, and so do the Kingdom of Arles and its members.

## Descriptions

`descriptions.py` (1800–1899), `descriptions20.py` (1900–2026), `descriptions15.py` (1500–1799) and `descriptions10.py` (1000–1499) give each state a title, dates and two sentences on how it began and ended. Entries for earlier eras end where the next era begins, so they never apply to a later map. The 1500–2026 entries were checked against the introductions of the Wikipedia articles on each state.

## Flags

The popup shows the flag the state used that year, from Wikimedia Commons, with its license.

- **Which flag:** the flag images Wikidata lists for the state's Wikipedia article, with the years each was in use (from Wikidata, or else from the file name). Where the dates overlap, the most recently adopted flag wins. `flags/articles.py` names the article for each state and fixes wrong or missing entries; `flags/flags_plan.py` and `flags/build_flags.py` pick the flag for each year and pack the images.
- **No flag** for occupied land, for about 75 states Wikidata has no flag for (mostly short-lived or early ones), and before 1500.
- **Licenses:** 316 images; about 250 are in the public domain. The rest are under Creative Commons or similar licenses, so the popup names the author and links the license, and the page's "Flag credits" list gives all of them. `flags/flags_files_meta.json` has the author and license of each file as Commons gives them; `AUTHORS` in `flags/articles.py` fixes the ones that are not a plain name.

## City populations

`cities.txt` lists about 4,900 cities and towns, with at most one figure per decade: 465 of Europe's largest cities, then (after the line `# Towns added by cities/towns_merge.py`) about 4,400 towns that reached 20,000 people. Each figure is tagged with its source:

| Code | Source |
|---|---|
| W | Wikidata |
| E, G, O | Census tables in the city's English, German or other Wikipedia article |
| U | UN Statistics Division, Demographic Yearbook city table |
| C | Estimates by Chandler, de Vries, Mitchell and others, from Wikipedia's "Historical urban community sizes" |
| V | Jan de Vries, *European Urbanization 1500–1800* (1984), via the europop dataset (public domain, CC0) |

Before 1800 there are figures for about 250 cities, mostly de Vries's estimates every 50 years for towns of 10,000 or more (`cities/add_early.py`, then `cities/add_devries.py`). 58 of the cities, such as Leiden, Bruges and Toledo, were added because they had at least 20,000 people at some point before 1800; their later figures now come from the towns step below.

Before 1500 there are figures for 59 cities, from the same Wikipedia page's tables for 1000–1350, 1400 and 1450 (mostly Tertius Chandler's estimates; `cities/hucs_medieval_raw.txt`, added by `cities/add_medieval.py`). 14 of them, such as Speyer, Amalfi and Sarai, had 20,000 people or more then but are not among the later cities, so they appear only on the medieval map. A figure given as a range more than 2.5 times as wide at the top as at the bottom is left out. Before 1500 the map estimates within 50 years of a figure. The page shows the figure for the chosen year if there is one. Otherwise it estimates between the figures either side, assuming steady growth, and labels it as an estimate: within ten years of a figure, or 25 years before 1800. A hollow dot means there is no figure that close.

### Smaller towns (October 2026)

So the map keeps ten cities on screen as the viewer zooms in, the list adds every town in the map's area that Wikidata gives 20,000 people or more at some point:

1. **Candidates** (browser query on query.wikidata.org, saved as `cities/hm-candidates.json`, not kept in the repository): every item with a population figure of 20,000 or more and coordinates in the map's area, with its classes. `python3 towns_select.py classes hm-candidates.json` keeps the towns: kinds of human settlement, and municipalities where the municipality is the town (France, Italy, Spain, Portugal, the Netherlands, Belgium, Algeria, Tunisia), leaving out parts of cities (boroughs, quarters, districts).
2. **Wikidata figures** for those towns (browser, `cities/hm-series.json`, not kept), then `python3 towns_select.py dedupe hm-series.json`: drops towns already listed (within 3 km, or 15 km with a similar name), districts of large cities (within 4 km of a city of 500,000 or more; inside Greater London, the Brussels-Capital Region, Belgrade, Birmingham or Leeds, whose figures already count them; the districts Turkey made of its large cities in 2008), and a town's duplicate municipality. Writes `towns_new.json` and `towns_extend.json` (cities listed only before 1800 that match a town).
3. **Wikipedia tables:** `browser/fetch_town_tables.js` reads each town's article in its country's language, German and English (tables, census templates, the French and Italian data pages, the Spanish census chart, Russian Wikipedia's population table), saved as `cities/hm-town-tables.json`.
4. `python3 towns_merge.py hm-town-tables.json ../cities.txt` checks each Wikipedia series against Wikidata (they must agree within a factor of 3/2 where both have a figure), fills the decades Wikidata lacks, adds de Vries's figures within 12 km, drops figures off the trend, and keeps towns with at least two figures, one of them 20,000 or more. Wikipedia figures before 1800 are kept only from German Wikipedia. It also carries the early-only cities forward (`extend_tables.txt`). Re-running it replaces the towns it added before.
5. `python3 cities/patch_page.py` (in `europe-map/`) puts the new cities into the built page without rebuilding the maps (each placed in each era's map regions by `cities/place_cities.py`); a full rebuild gives the same result, since `export.py` reads `cities.txt`.

Coverage is uneven: Wikidata and Wikipedia have long series for France, Italy, Spain, Germany, the Netherlands, Czechia and much of Russia, but British towns often have only recent figures (sometimes for the whole borough), Portuguese municipalities mostly one figure, and Turkish cities' recent figures cover their whole province (from 2013 these are left out for its large cities). Before the mid-1800s most smaller towns have no figure, so zoomed-in views show fewer than ten.

## Events and people in cities (October 2026)

From Wikidata, gathered by `browser/fetch_city_extras.js` (run in the browser on an ordinary Wikidata page; see its header) and assembled by `cities/make_extras.py`:

1. **The cities' Wikidata items** (`cities` step): the ids already known for the 465 large cities and the towns, checked against each city's position (within 30 km); the rest found by searching their names and taking the most written-about item within 8 km. Three early cities have none (Ani, Sarai, Gorodishche).
2. **Events** (`events`): items located in the city (P276 location, P131 in the administrative area, or P276 a place within the city), dated (P585, else P580) from 1000 to 2026, with Wikipedia articles in at least three languages.
3. **Kinds** (`classes`, `roots`): each event's classes are traced up the class tree (P279) to the root classes in `cities/event_kinds.py`, which sets ten kinds (each with an icon) and the classes to leave out (sports, festivals, awards, accidents, buildings and so on). Events of no kind are left out.
4. **People** (`people`): those born (P19) or died (P20) in the city with articles in at least 30 languages; for places with fewer than 8 such people, at least 10 languages, in the place itself and then in places within it (P131). People who lived before 1000 are left out.
5. `python3 cities/make_extras.py select WD` picks each city's events (the most written-about, up to 30 for the large cities and 12 for towns, no more than about a third from any century) and people (up to 14 and 6, spread the same way) and lists the items whose names it needs; the `details` step fetches their English labels, descriptions and English Wikipedia titles; `python3 cities/make_extras.py build WD` writes `city-events.json` and `city-people.json`.

6. `python3 cities/wiki_links.py list`, then `fetch` (on a machine Wikimedia doesn't throttle; run again until it says DONE), then `apply`: checks every link against Wikidata as it is now (articles renamed, deleted or added since), keeps the Wikidata id, picks another language's article where there is no English one (the city's own language if it is French, German, Spanish or Italian, else the first of those, else another of the city's languages, using `cities/city_country.json`), and writes `wiki-titles.json`. First run October 3, 2026: of 4,321 events, 1 English article had been deleted (the Concord of Segovia, now linked to the Spanish article) and 360 events with no English article now link to another language instead of Wikidata; of 23,418 people, 1 article had been renamed and 62 now link to another language.

The browser tool returns large results in pieces of 230,000 characters (`HM.prep`, `HM.part`), joined again in order.

Limits: Wikidata sometimes places an event or a birth in a district or region rather than the city, or not at all, so lists can be incomplete. Wars and battles are the best-recorded kind of event. Counts of Wikipedia languages favor recent events and people.

## Terrain (October 2026)

Three steps, in `europe-map/`, with the Natural Earth files in a folder SRC (from github.com/nvkelso/natural-earth-vector, geojson folder: the 10m rivers with the Europe supplement, the 10m lakes and Europe lakes, the 10m geography regions and marine areas, the 50m land; and `shadedrelief.jpg` from the basemap-data Python package):

1. `python3 terrain/make_terrain.py SRC`: rivers and lakes (with Natural Earth's zoom levels, which the page converts to its own scale) into `terrain.json`. Man-made reservoirs carry the years they held water, from `terrain/reservoirs.json` (about 90 in the map's area, each found by a point inside it, with the year it was first filled; the Kakhovka Reservoir ends in 2022, the Dnieper Reservoir has a gap for 1942–46), and the page shows them only in those years. Natural lakes that dams only raised (Ilmen, Mjøsa, Oulujärvi and others Natural Earth calls reservoirs) are not listed, so they always show. `export.py` leaves the reservoirs out of the page's own coarse lakes, which show only until `terrain.json` loads. It also draws a relief from Natural Earth's shaded-relief picture, which step 2 replaces.
2. `python3 terrain/make_relief_dem.py terrain/srtm_ramp2_eu.u8.gz SRC terrain.json`: the shaded relief from elevation data. The heights are NASA's, as the 8-bit picture "Srtm ramp2.world.21600x10800.jpg" on Wikimedia Commons (public domain, one pixel per minute of arc, about 37 m per gray level, checked against known peaks), cut to Europe by `browser/fetch_dem.js` and kept in `terrain/srtm_ramp2_eu.u8.gz`. Smoothed a little, resampled to the map's projection at 1.6 km to the pixel, lit from four directions around the northwest, and drawn as black or white with transparency, so the page lays it over the country colors (`relief.webp`).
3. `python3 terrain/make_features.py SRC terrain.json`: the names of physical features (below).

### Names of physical features

One layer of names, apart from the political ones: seas, gulfs and straits, lakes and lagoons, mountain ranges, plains and uplands, rivers, passes, gorges and peaks. They are set in a serif italic (plains upright), water in blue and land in browns, and each shows from the zoom its rank allows.

- **Seas and ranges** (Natural Earth's marine areas and geography regions) carry a spine, the longest line through the middle of their shape (the shape drawn on a grid, thinned to a skeleton, the longest path taken and smoothed). The page sets the name along the part of the spine on screen, spaced out to stretch across it, as older atlases do; where other names are in the way it tightens the spacing, moves along the line, or moves a little to one side of it.
- **Rivers** are named along their course.
- **Lakes and lagoons**: 45 chosen in `terrain/features_extra.json` for their size or their place in history (Ladoga, Peipus, Geneva, Constance, Ohrid, Lough Neagh, the Vistula Lagoon…), with their outlines found in Natural Earth's lakes by name or by a point inside them, plus the Curonian and Szczecin lagoons from the marine areas. A lake's name goes along it when the lake is long and wide enough on screen, and just beside it otherwise. Reservoirs are left out. A name can change with the year: the IJsselmeer is the Zuiderzee before 1932.
- **The Atlantic and the Mediterranean** follow hand-drawn lines in `terrain/features_extra.json` ('spines'), since Natural Earth's shapes put them badly (the Atlantic is the whole ocean; the Mediterranean's middle line runs off the bottom of the map). A feature can have other lines to try ('alt'): the Atlantic's runs down the coast of Portugal for views of Iberia.
- **Passes, gorges, gaps, straits, peaks, marshes and forests** that mattered in Europe's history but are not in Natural Earth come from `terrain/features_extra.json` (positions from Wikidata): passes and peaks get a small mark.
- **Order** when names compete for room: countries, cities and events, then seas, ranges, rivers, lakes, gulfs and straits, plains, peaks, passes.
- The mountain button turns the relief and this layer off (the rivers themselves stay).

## Checks

- `spot_checks.py` tests the 1800–2026 map against 123 well-documented place-and-year facts. 121 pass; the two that fail are Heligoland, which is too small to appear in the coastline data.
- `spot_checks10.py` tests the 1000–1499 map against 324 facts, and all pass. In 17 either of two answers is accepted, where the facts allow both or no source draws the smaller state (listed in the file).
- `spot_checks15.py` tests the 1500–1799 map against 169 facts. 165 pass; the four that fail are German states that neither OHM nor Cliopatria has around 1600 (the Palatinate, Trier, Hesse-Kassel, Pomerania), which show as the Holy Roman Empire.

## Rebuilding

Each era is built in its own working folder with the same scripts. Setting `ERA=early` switches the scripts to 1500–1799 (`units15.py`, `assign15.py`, `descriptions15.py`), and `ERA=medieval` to 1000–1499 (`units10.py`, `assign10.py`, `descriptions10.py`).

1. **Get the source data.**
   - 1800–2026: run `browser/fetch_borders.js`; 1500–1799: `browser/fetch_borders_1500.js`; 1000–1499: `browser/fetch_borders_1000.js`. Each runs in a browser console on https://overpass-api.openhistoricalmap.org/api/status. Save the result as `europe-borders-sources.json` in that era's folder.
   - `clio.pkl`: the Cliopatria polities active in the era that fall inside the map, as a list of (properties, shape) pairs. `land.pkl`: Natural Earth 50m land, clipped to longitude −26 to 50 and latitude 34 to 72.
2. **In each era's folder, run in order:**
   - `python3 rel_polys.py`, `python3 faces.py`, `python3 assign.py`, `python3 alts.py`, `python3 regions.py`
   - `python3 export.py <folder with Natural Earth lakes and rivers> fills.json`. Run the latest era first, then 1500–1799, then 1000–1499 (all three again after any change, since each takes colors from the ones before). Set these so colors agree across eras (paths are the other eras' folders):
     - 1800–2026: `EXTRA_ADJ=<early>/adj.json:<medieval>/adj.json` (keep clear of neighbors in the earlier maps; `adj.json` is written by each export, so the first build of all needs a second pass)
     - 1500–1799: `KEEP_COLORS=<late>/data.json EXTRA_ADJ=<medieval>/adj.json`
     - 1000–1499: `KEEP_COLORS=<late>/data.json:<early>/data.json`
   - `node topo.mjs geo.json topo.json 0.3 1e5`
3. **In the latest era's folder:** `python3 merge_eras.py <1500–1799 folder> <1000–1499 folder>`.
4. **Flags, same folder:** `python3 flags/flags_plan.py` (which article each description's flag comes from), then run `browser/fetch_flags.js` in a browser console to get `flags_claims.json` (each article's flags and dates from Wikidata) and `flags_files.json` (thumbnails, authors and licenses from Commons), then (for the larger copies) `browser/fetch_flags_large.js`, saved as `flags_large.json`, then `python3 flags/build_flags.py`, which writes `flags.webp`, `flag-images/` and `flags_index.json`. Run `merge_eras.py` again so the page data includes them. The saved `flags/flags_claims.json` can be reused; `flags_files.json` is not kept because of its size.
5. `python3 build_page.py`. Publish `europe-borders.html` with `europe-borders-1000.json`, `europe-borders-1500.json`, `flags.webp`, `flag-images/`, `city-events.json`, `city-people.json`, `terrain.json` and `relief.webp` beside it.

To change only the page's code (`page_template.html`), the map data can be taken from the built page instead of rebuilding: extract the `topo` and `data` scripts of `europe-borders.html` into `topo.json` and `page_data.json` (as `cities/place_cities.py` reads them) and run `build_page.py`.

`fills.json` comes from `node fills.mjs` (candidate fill colors and their measured separation). Needs Python 3 with shapely and pyproj, and Node with topojson-server, topojson-simplify and topojson-client.

## Hosting it elsewhere

The map is plain files, so any web host can serve it.

- `python3 make_site.py` writes `../_site/`: `index.html` (the page with the standard page header, which Claude artifacts otherwise add) and the files it loads. Upload that folder to any host, or embed its `index.html` in another site with an iframe.
- `./deploy_site.sh` builds the folder and pushes it to the `gh-pages` branch as a single commit, replacing what was there. GitHub Pages serves it at https://vedahcook.github.io/historical-map/ (Settings → Pages → Source: "Deploy from a branch", branch `gh-pages`).
- **Test copy first:** `./deploy_site.sh test` publishes the rebuilt page at https://vedahcook.github.io/historical-map/test/ (marked "Test version", kept out of search engines) and leaves the live map alone; once it looks right, `./deploy_site.sh` puts it live (the test copy stays until the next test). Only changed files are uploaded.
- The page loads fonts from Google Fonts and the topojson-client library from jsDelivr.
- CShapes-Europe's license is non-commercial, so the map can't be hosted on a commercial site.

## Limits

- **One date per year:** July 1. Changes during a year appear the following July.
- **The map covers longitude −25.5 to 49.5 and latitude 34.4 to 71.8.** Countries stop at that edge; land beyond it is shown in plain gray (Natural Earth), so the map fills the frame.
- **The medieval map is coarser still.** Cliopatria's outlines change in steps of a few years and are simplified, and borders in the east (the steppe, Anatolia, the Caucasus) are rough.
- **The early map is coarser.** Small states of the Holy Roman Empire are often missing before about 1700, the steppe and the Caucasus are only roughly drawn, and Cliopatria's outlines are simplified.
- **City figures vary in quality.** Early figures are estimates, some for the wider city.
- **The relief is coarse up close:** the elevation data has about 2 km to the pixel, so it softens and fades somewhat when zoomed in far.
- **CShapes-Europe is non-commercial (CC BY-NC-SA 4.0),** so the map is too. Flag images keep their own licenses (see Flags).
