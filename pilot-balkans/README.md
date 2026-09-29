# Balkans pilot, 1815–1900

A working review tool built on real data. For 218 towns across the Balkans, Romania and Bessarabia, three datasets were asked who held the town on July 1 of every year from 1815 to 1900:

- OpenHistoricalMap (OHM)
- CShapes-Europe
- Cliopatria

Wherever they disagree, the disagreement becomes a question to review.

## Results

- **127 disagreements in all.**
  - **31 are settled automatically:** the sources agree on who held the town and differ by a year on when.
  - **The other 96 group by cause into 28 questions**, plus one small leftover (a two-year gap at Tulcea):
    - 14 are ready for anyone to review.
    - 4 need an expert.
    - 10 are settled by a rule, such as whether self-governing states show as their own.
- **New problems found in OHM:**
  - Bulgaria after 1885 is missing.
  - Tyrnavos and Arta are never Greek.
  - There is no Ottoman record for 1897.
  - Ulcinj is Montenegrin two years early.
- **New problems found in CShapes and Cliopatria:**
  - CShapes: Kotor is shown as Ottoman, then Montenegrin; Zemun as Serbian.
  - Cliopatria: Turnu Severin is placed in Serbia, and Ruse and Silistra north of the Danube.

The review page is `balkan-borders-review.html`, published as a Claude artifact. Decisions are saved in each reviewer's browser and downloaded as a JSON file.

## Rebuilding

Run everything from this folder.

1. **Pick the towns.**
   - Download `ne_10m_populated_places_simple.geojson` from Natural Earth, then run `python3 select_towns.py`.
   - Run `python3 towns.py`, which adds historically important towns and writes `towns.json`.
2. **Get each source's answer per town.**
   - **OHM:** run `browser/ohm_towns.js` in a browser console on the OHM data server. Then pack `window.__B` into `ohm_towns.json` as `{recs: [[id, name, level, start, end]…], combos: ["i,j,…"], towns: {name: comboIndex}}`, keeping level 2–4 records that overlap 1810–1905. Check `window.__B.failed`: four Russian Empire records timed out on the first run and were added afterward.
   - **CShapes:** run `browser/cshapes_towns.js` on the CShapes page and save the output as `cshapes_towns.json`.
   - **Cliopatria:** run `python3 clio_towns.py path/to/cliopatria_polities_only.geojson`, which writes `clio_towns.json`.
3. **Find and group the conflicts.**
   - `python3 find_conflicts.py` writes `conflicts_raw.json`.
   - `python3 questions.py` holds the 28 hand-written questions, suggested answers and sources, and writes `questions.json`.
4. **Build the page.**
   - Download `ne_50m_land`, `ne_50m_lakes` and `ne_50m_rivers_lake_centerlines` (Natural Earth GeoJSON).
   - Run `python3 bundle.py`.
   - Insert `bundle.json` into `page_template.html` in place of `/*BUNDLE*/`, replacing every `</` with `<\/`.

Needs Python 3 with shapely.

## Limits

- **Towns, not borders:** checking towns shows who held which area and when. It does not check exactly where a border line ran between towns.
- **Suggested answers need checking:** they were drafted from treaties and well-documented events, and link to pages about them rather than to the treaty texts themselves. Answers marked medium confidence need an expert.
