# Europe's borders, 1500–2026

An interactive map of Europe's country borders, one year at a time (as of July 1). It shows OpenHistoricalMap (OHM) by default. Where another source draws a different border, the side panel lists it; picking one outlines the area on the map with a dashed line and says what each source claims. Nothing is outlined until one is picked.

The page is `europe-borders.html`, published as a Claude artifact. It holds the map for 1800–2026. Two files sit beside it:

- `europe-borders-1500.json`: the map for 1500–1799, which the page loads a moment after it opens (or at once if it opens on an earlier year). Opened straight from disk, a browser may refuse to load it; the page then says so for years before 1800.
- `flags.webp`: all the flag images in one picture.

## Using the map

- **Tap a country** to highlight it and dim the rest. The map zooms so the whole country is on screen, and a popup describes it for that year: its flag, when the state began and ended, how, and where the border at that spot comes from. Rings mark detached parts. Tap it again, or the sea, to clear it.
- **The highlight follows the country across 1800,** where the page switches between its two maps.
- **The timeline** shows key events, or only the highlighted country's events: when it began or ended, name changes, and gains or losses over 1,500 km². The row of events scrolls sideways.
- **Cities** appear inside the highlighted country. Tap a city for its population that year, a chart of all its figures, and who held it over the years. Tap a dot in the chart, a spot on the strip, or a line in the list to go to that year; the popup stays put.
- **One popup at a time,** placed to cover as little as possible of what it describes.

## How the map decides

- **Default: OHM.** It matched the historical record in 149 of 160 spot checks for the 1800s, more than the other sources.
- **Gaps in OHM are filled** from CShapes-Europe (1816 onward), then Cliopatria. A gap of a year or two with the same country on both sides is bridged.
- **Before 1800 OHM has fewer records.** It often has the Holy Roman Empire without its member states, so many small German states show as the Empire, and Cliopatria fills more of the map. Where OHM has only a large realm, the map shows the states within it that Cliopatria has: Ottoman vassals (Moldavia, Wallachia, Transylvania, the Crimean Khanate, Ragusa), the Habsburg, Spanish and Austrian Netherlands, Franche-Comté, and Lithuania before 1569.
- **Corrections** where our checks found the sources wrong or missing. Each one is explained on the page. For 1500–1799 they include Hungary after Mohács, Menorca, Oran, Ceuta, Calais, Ferrara, Savoy and Nice in 1792–99, Serbia and Oltenia in 1718–39, the English Commonwealth, and a few states the sources keep a year or two too long (Bohemia, Milan, Lorraine, Luxembourg, the Aq Qoyunlu).
- **Self-governing territories** are shown in their own color with stripes in the overlord's color; **occupied land** has a crosshatch in the occupier's color.
- **Colors:** each country keeps one color throughout, on both sides of 1800. The early map takes the later map's colors and colors its own countries around them. A few neighbors that touch for only a few kilometers share a color before 1800.

## Alternative borders

OHM is compared with CShapes-Europe from 1816 and with Cliopatria before that.

- **What counts:** an area of at least 400 km² (5,000 km² for the coarser Cliopatria), at least 6 km wide, that a source puts in a different country for more than a year.
- **Compared at the level of sovereignty,** so a self-governing territory and its overlord count as the same. Before 1807, a member state of the Holy Roman Empire and the Empire count as the same.

## Descriptions

`descriptions.py` (1800–1899), `descriptions20.py` (1900–2026) and `descriptions15.py` (1500–1799) give each state a title, dates and two sentences on how it began and ended. Early entries for countries that also exist after 1799 end by 1799, so they never apply to the later map. They were checked against the introductions of the Wikipedia articles on each state.

## Flags

The popup shows the flag the state used that year, from Wikimedia Commons, with its license.

- **Which flag:** the flag images Wikidata lists for the state's Wikipedia article, with the years each was in use (from Wikidata, or else from the file name). Where the dates overlap, the most recently adopted flag wins. `flags/articles.py` names the article for each state and fixes wrong or missing entries; `flags/flags_plan.py` and `flags/build_flags.py` pick the flag for each year and pack the images.
- **No flag** for occupied land, and for about 75 states Wikidata has no flag for (mostly short-lived or early ones).
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

Before 1800 there are figures for about 250 cities, mostly de Vries's estimates every 50 years for towns of 10,000 or more (`cities/add_early.py`, then `cities/add_devries.py`). 58 of the cities, such as Leiden, Bruges and Toledo, were added because they had at least 20,000 people at some point before 1800; they have no later figures, so they appear only on the early map. The page shows the figure for the chosen year if there is one. Otherwise it estimates between the figures either side, assuming steady growth, and labels it as an estimate: within ten years of a figure, or 25 years before 1800. A hollow dot means there is no figure that close.

## Checks

- `spot_checks.py` tests the 1800–2026 map against 123 well-documented place-and-year facts. 121 pass; the two that fail are Heligoland, which is too small to appear in the coastline data.
- `spot_checks15.py` tests the 1500–1799 map against 169 facts. 165 pass; the four that fail are German states that neither OHM nor Cliopatria has around 1600 (the Palatinate, Trier, Hesse-Kassel, Pomerania), which show as the Holy Roman Empire.

## Rebuilding

Each era is built in its own working folder with the same scripts. Setting `ERA=early` switches the scripts to 1500–1799 (`units15.py`, `assign15.py`, `descriptions15.py`).

1. **Get the source data.**
   - 1800–2026: run `browser/fetch_borders.js`; 1500–1799: `browser/fetch_borders_1500.js`. Each runs in a browser console on https://overpass-api.openhistoricalmap.org/api/status. Save the result as `europe-borders-sources.json` in that era's folder.
   - `clio.pkl`: the Cliopatria polities active in the era that fall inside the map, as a list of (properties, shape) pairs. `land.pkl`: Natural Earth 50m land, clipped to longitude −26 to 50 and latitude 34 to 72.
2. **In each era's folder, run in order:**
   - `python3 rel_polys.py`, `python3 faces.py`, `python3 assign.py`, `python3 alts.py`, `python3 regions.py`
   - `python3 export.py <folder with Natural Earth lakes and rivers> fills.json`. Run the later era first; for the early era set `KEEP_COLORS=<later era's folder>/data.json` so countries keep their colors.
   - `node topo.mjs geo.json topo.json 0.3 1e5`
3. **In the later era's folder:** `python3 merge_eras.py <early era's folder>`.
4. **Flags, same folder:** `python3 flags/flags_plan.py` (which article each description's flag comes from), then run `browser/fetch_flags.js` in a browser console to get `flags_claims.json` (each article's flags and dates from Wikidata) and `flags_files.json` (thumbnails, authors and licenses from Commons), then `python3 flags/build_flags.py`, which writes `flags.webp` and `flags_index.json`. Run `merge_eras.py` again so the page data includes them. The saved `flags/flags_claims.json` can be reused; `flags_files.json` is not kept because of its size.
5. `python3 build_page.py`. Publish `europe-borders.html` with `europe-borders-1500.json` and `flags.webp` beside it.

`fills.json` comes from `node fills.mjs` (candidate fill colors and their measured separation). Needs Python 3 with shapely and pyproj, and Node with topojson-server, topojson-simplify and topojson-client.

## Limits

- **One date per year:** July 1. Changes during a year appear the following July.
- **The map covers longitude −25.5 to 49.5 and latitude 34.4 to 71.8.** Countries stop at that edge; land beyond it is shown in plain gray (Natural Earth), so the map fills the frame.
- **The early map is coarser.** Small states of the Holy Roman Empire are often missing before about 1700, the steppe and the Caucasus are only roughly drawn, and Cliopatria's outlines are simplified.
- **City figures vary in quality.** Early figures are estimates, some for the wider city.
- **CShapes-Europe is non-commercial (CC BY-NC-SA 4.0),** so the map is too. Flag images keep their own licenses (see Flags).
