# Europe's borders, 1800–1900

An interactive map of Europe's country borders, one year at a time (as of July 1). It shows OpenHistoricalMap (OHM) by default. Where another source draws a different border, the map outlines that area with a dashed line and a numbered marker, and says what each source claims.

The page is `europe-borders.html`, published as a Claude artifact.

## Using the map

- **Tap a country** to highlight it and dim the rest. The map zooms so the whole country is on screen, and a popup describes it for that year. Tap it again, or the sea, to clear it; tap another country to switch.
- **The side panel** then shows a short history of that country for the chosen year (`descriptions.py`: when it began, how, and when it ended), which source the border comes from, and who held the place over the century.
- **The timeline** shows only that country's events while it is highlighted: when it began or ended, name changes, and gains or losses over 1,500 km².
- **Cities** appear inside the highlighted country. Tap a city's dot or name for its population that year.
- **One popup at a time,** placed to cover as little as possible of what it describes (never a tapped city's dot or name). Nothing pops up on hover.
- **Map font:** Source Sans 3.

## How the map decides

- **Default: OHM.** It matched the historical record in 149 of 160 spot checks, more than the other sources.
- **Gaps in OHM are filled** from CShapes-Europe (1816 onward), then Cliopatria. A gap of a year or two with the same country on both sides is bridged.
- **Corrections** where our checks found OHM wrong or missing:
  - Bulgaria after 1885
  - Ulcinj, 1878–80
  - Arta and Tyrnavos after 1881
  - Greece, 1830–31
  - Schleswig-Holstein, 1865–66
  - Moldavia before 1812
  - The Ionian Islands, 1807–15
  - Bosnia under Austrian rule, 1878 onward
  - Russia's gains in the Caucasus, 1801–13

  Each correction is explained on the page.
- **Self-governing territories** (Serbia before 1878, Finland, Congress Poland and others) are shown in their own color with stripes in the overlord's color.

## Alternative borders

OHM is compared with CShapes-Europe from 1816 and with Cliopatria before that.

- **What counts:** an area of at least 400 km² (5,000 km² for the coarser Cliopatria), at least 6 km wide, that a source puts in a different country for more than a year.
- **Compared at the level of sovereignty,** so a self-governing territory and its overlord count as the same.
- **Two source conventions are not flagged:**
  - CShapes treats the North German Confederation's members as independent until 1871.
  - CShapes folds Hanover into the UK while the two shared a king.
- **Result:** 114 alternative borders across the century.

## City populations

`cities.txt` lists about 250 of Europe's largest cities by 1900, with population figures from 1785 to 1910 (at most one per decade). Each figure is tagged with its source:

| Code | Source | What it is |
|---|---|---|
| W | Wikidata | Census counts with a date |
| E, G | English and German Wikipedia | The city's census table |
| C | Chandler, de Vries and Mitchell, via Wikipedia's "Historical urban community sizes" | Estimates, often for the wider city |

The page shows the figure for the chosen year if there is one. Otherwise it estimates between the figures either side, assuming steady growth, and labels it as an estimate. A hollow dot means there is no figure within ten years. `export.py` places each city in its map region, so it moves with border changes.

## Checks

`spot_checks.py` tests the finished map against 123 well-documented place-and-year facts. Examples: Nice becomes French in 1860, Venice becomes Italian in 1866, and Tbilisi is Russian after 1801. 121 pass. The two that fail are Heligoland, which is too small to appear in the coastline data.

## Rebuilding

Run everything from one working folder.

1. **Get the source data.**
   - Run `browser/fetch_borders.js` in a browser console on https://overpass-api.openhistoricalmap.org/api/status.
   - Save the result as `europe-borders-sources.json` (about 11 MB).
2. **Prepare the Cliopatria and land files.**
   - `clio.pkl`: the Cliopatria polities active 1795–1905 that fall inside the map, as a list of (properties, shape) pairs. See `../pilot-balkans/clio_towns.py` for how to read Cliopatria.
   - `land.pkl`: Natural Earth 50m land, clipped to longitude −26 to 50 and latitude 34 to 72.
3. **Run the steps in order:**
   - `python3 rel_polys.py`: one polygon per OHM record, bridging small gaps in broken records.
   - `python3 faces.py`: cut the map into pieces using every source's borders.
   - `python3 assign.py`: who held each piece each year, including the corrections.
   - `python3 alts.py`: the alternative borders.
   - `python3 regions.py`: merge pieces with the same history, and place the labels.
   - `node fills.mjs`: candidate fill colors and their measured separation. It needs `validate_palette.js` from the dataviz skill, saved as `vp.mjs`.
   - `python3 export.py <folder with Natural Earth lakes and rivers> fills.json`
   - `node topo.mjs geo.json topo.json 0.3 1e5`: needs `topojson-server`, `topojson-simplify` and `topojson-client`.
   - `python3 build_page.py`

Needs Python 3 with shapely and pyproj.

## Limits

- **One date per year:** July 1. Changes during a year appear the following July.
- **Year-only end dates in OHM** (such as "1864") are read as the end of that year.
- **The map covers longitude −25.5 to 49.5 and latitude 34.4 to 71.8.** Places outside it, such as most of Russia and North Africa, are cut off at the edge.
- **City figures vary in quality.** Paris, Glasgow, Liverpool, Dublin, Bristol and Antwerp have only wider-city estimates, and a few cities (Brussels, Athens, Belgrade, Bradford among them) have only one or two figures.
- **CShapes-Europe is non-commercial (CC BY-NC-SA 4.0),** so the map is too.
