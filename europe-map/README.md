# Europe's borders, 1000–2026

An interactive map of Europe's country borders, one year at a time (as of July 1). It shows OpenHistoricalMap (OHM) by default. Where another source draws a different border, the side panel lists it; picking one outlines the area on the map with a dashed line and says what each source claims. Nothing is outlined until one is picked.

The page is `europe-borders.html`, published as a Claude artifact. It holds the map for 1800–2026. These files sit beside it:

- `europe-borders-1500.json` (1500–1799) and `europe-borders-1000.json` (1000–1499): the earlier maps. The page loads the one next to the era on screen a moment after it opens, and any era at once when the slider reaches it. Opened straight from disk, a browser may refuse to load them; the page then says so for years before 1800.
- `flags.webp`: all the flag images in one picture, at the small size the popup shows.
- `flag-images/`: a larger copy of each flag, one file each, loaded only when a flag is tapped.

## Using the map

- **Tap a country** to highlight it and dim the rest. The map zooms so the whole country is on screen, and a popup describes it for that year: its flag (tap it to see it larger; tap anywhere to close), when the state began and ended, how, and where the border at that spot comes from. Rings mark detached parts. Tap it again, or the sea, to clear it.
- **The highlight follows the country across 1500 and 1800,** where the page switches between its three maps.
- **The timeline** shows key events, or only the highlighted country's events: when it began or ended, name changes, and gains or losses over 1,500 km². The row of events scrolls sideways.
- **Cities** appear inside the highlighted country. Tap a city for its population that year, a chart of all its figures, and who held it over the years. Tap a dot in the chart, a spot on the strip, or a line in the list to go to that year; the popup stays put.
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

`cities.txt` lists 451 of Europe's largest cities, with at most one figure per decade. Each figure is tagged with its source:

| Code | Source |
|---|---|
| W | Wikidata |
| E, G, O | Census tables in the city's English, German or other Wikipedia article |
| U | UN Statistics Division, Demographic Yearbook city table |
| C | Estimates by Chandler, de Vries and Mitchell, from Wikipedia's "Historical urban community sizes" |
| V | Jan de Vries, *European Urbanization 1500–1800* (1984), via the europop dataset (public domain, CC0) |

Before 1800 there are figures for about 250 cities, mostly de Vries's estimates every 50 years for towns of 10,000 or more (`cities/add_early.py`, then `cities/add_devries.py`). 58 of the cities, such as Leiden, Bruges and Toledo, were added because they had at least 20,000 people at some point before 1800; they have no later figures, so they appear only on the early map. There are no figures before 1500 yet, so the medieval map shows cities only in its last 25 years. The page shows the figure for the chosen year if there is one. Otherwise it estimates between the figures either side, assuming steady growth, and labels it as an estimate: within ten years of a figure, or 25 years before 1800. A hollow dot means there is no figure that close.

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
5. `python3 build_page.py`. Publish `europe-borders.html` with `europe-borders-1000.json`, `europe-borders-1500.json`, `flags.webp` and `flag-images/` beside it.

`fills.json` comes from `node fills.mjs` (candidate fill colors and their measured separation). Needs Python 3 with shapely and pyproj, and Node with topojson-server, topojson-simplify and topojson-client.

## Hosting it elsewhere

The map is plain files, so any web host can serve it.

- `python3 make_site.py` writes `../_site/`: `index.html` (the page with the standard page header, which Claude artifacts otherwise add) and the files it loads. Upload that folder to any host, or embed its `index.html` in another site with an iframe.
- `./deploy_site.sh` builds the folder and pushes it to the `gh-pages` branch, replacing what was there. GitHub Pages serves it at https://vedahcook.github.io/historical-map/ (Settings → Pages → Source: "Deploy from a branch", branch `gh-pages`). Run it after each rebuild.
- The page loads fonts from Google Fonts and the topojson-client library from jsDelivr.
- CShapes-Europe's license is non-commercial, so the map can't be hosted on a commercial site.

## Limits

- **One date per year:** July 1. Changes during a year appear the following July.
- **The map covers longitude −25.5 to 49.5 and latitude 34.4 to 71.8.** Countries stop at that edge; land beyond it is shown in plain gray (Natural Earth), so the map fills the frame.
- **The medieval map is coarser still.** Cliopatria's outlines change in steps of a few years and are simplified, and borders in the east (the steppe, Anatolia, the Caucasus) are rough.
- **The early map is coarser.** Small states of the Holy Roman Empire are often missing before about 1700, the steppe and the Caucasus are only roughly drawn, and Cliopatria's outlines are simplified.
- **City figures vary in quality.** Early figures are estimates, some for the wider city.
- **CShapes-Europe is non-commercial (CC BY-NC-SA 4.0),** so the map is too. Flag images keep their own licenses (see Flags).
