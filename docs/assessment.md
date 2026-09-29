# OpenHistoricalMap: 19th-century Europe borders — assessment

Checked 2026-09-29 against OHM's live data (Overpass API at overpass-api.openhistoricalmap.org).

## What OHM has
- 353 country-level border records (`admin_level=2`) active in Europe between 1800 and 1900. A new record is created each time a border changes, so one country is a chain of records (e.g., Russian Empire ≈ 30 records for 1800–1900).
- Autonomous and vassal states are stored one level down (`admin_level=3`): Norway 1814–1905, Finland 1809–1917, Moldavia 1812–1859, Wallachia 1829–1859, United Principalities 1859–1878, Serbia 1833–1867, Bulgaria 1878–1885, Monaco 1815–1861, Luxembourg 1831–1840. Any query must include both levels.
- Dates are day-level for most records; 56 start dates and 47 end dates are year-only.
- 348 of 353 records link to Wikidata; only 69 cite a source map or document.
- Geometry detail varies a lot: Belgium 1839 and German Reich 1871 have ~20–35 m between points (likely reused from modern borders where unchanged); Kingdom of Greece 1881 ~0.5 km median, 1.5 km at the 90th percentile.
- License: CC0 (public domain).

## Spot-check method
160 checks: 92 places × dates on either side of well-documented transfers (e.g., Nice 1860, Strasbourg 1871, Niš 1878, Arta 1881, Heligoland 1890) plus capital-city controls. For each, which country-level (or level-3) record contains the point on that date. The test set targets known changes, so it measures relative quality, not an absolute error rate.

## OHM results: 149 of 160 correct
Four initial "misses" (Nice 1861, Chambéry 1861, Lisbon 1850, Kraków 1830) were caused by OHM's lookup index lagging recent edits; checking the current geometry directly showed them correct. Anyone using OHM's `is_in` lookups should expect this lag.

Real problems (11):
- **Missing German states 1806–1810/1826:** no Bavaria, Württemberg, or Baden before 1810; no Grand Duchy of Würzburg (1806–1814) or Grand Duchy of Frankfurt (1810–1813); no Duchy of Nassau before 1815; no Saxon duchies (Saxe-Weimar, Saxe-Gotha-Altenburg, Saxe-Coburg-Saalfeld, Saxe-Hildburghausen, Saxe-Meiningen) before 1826. (Munich 1808, Stuttgart 1808, Karlsruhe 1808, Würzburg 1808, Gotha 1820, Weimar 1820 all return nothing.)
- **Bavaria gap:** no record from 1814-06-03 to 1816-05-01 (Munich 1815 returns nothing).
- **Bulgaria 1885–1908 missing:** after the 1885 unification with Eastern Rumelia, Sofia and Plovdiv show as plain Ottoman territory. Only 1878–1885 (level 3) and 1908+ exist.
- **Greece before 1832 missing:** Nafplio 1829 shows as Ottoman. The Greek state (1822 onward; independence recognized 1830) is absent until 1832-05-07.
- **Arta 1881 border wrong:** the 1881 Greece record does not contain Arta, which was ceded to Greece in 1881; the Ottoman record does.

Smaller issues found in the date chains:
- Ottoman Empire: no record for 1897 → 1898 (year-only dates around the 1897 war settlement).
- Prussia: 11-day gap, 1866-09-20 → 1866-10-01.
- France: 6-week gap 1814-04-13 → 1814-05-30; one record (relation 2913630) has start and end dates reversed (1808-05-24 → 1807-12-10), leaving mid-1808 uncovered.
- Kingdom of Sardinia and Second French Empire: overlapping records (1859 and 1862).
- Several one-day gaps from inconsistent end-date conventions (Baden 1819, Two Sicilies 1843 and 1860, Switzerland 1816 and 1874).
- Name typo: Free City of Frankfurt's English name is "Frankfur".
- Also absent: Moldavia before 1812, Wallachia before 1829, Ionian Islands 1807–1815, Serbia 1815–1833.

Modeling choices to be aware of (defensible, but inconsistent):
- Netherlands 1815–1839 still includes Belgium while Belgium 1830–1839 also exists (overlapping claim and actual control).
- Serbia 1867–1878 is country-level while Bulgaria 1878–1885 is level 3, though both were Ottoman vassals.
- Bosnia 1878–1908 is shown as Ottoman, not Austria-Hungary.
- Neuchâtel 1815–1848 sits in both Switzerland and Prussia (historically accurate dual status).

## Audit against COW Territorial Change (1816–1900)
Checked 2026-09-29. From COW Territorial Change v6, 60 transfers inside Europe for 1816–1900 were tested; its other rows are colonial or in Asia, and a few 1–2 km² adjustments were left out. Each was tested at 1–4 places (83 checks) by sampling OHM month by month and finding when the place moves from the losing to the gaining state. Full table: [`data/ohm-vs-cow-transfers-1816-1900.csv`](../data/ohm-vs-cow-transfers-1816-1900.csv).

| Verdict | Checks | What it means |
|---|---|---|
| Agrees (within 2 months) | 53 | Includes all 13 North German Confederation entries, Italian unification, Berlin 1878 transfers, Ionian Islands, Heligoland |
| Within a year | 16 | OHM uses the formal treaty/annexation date; COW often uses the conquest or armistice. OHM is usually the more precise (e.g., Alsace-Lorraine May 1871 vs COW Dec 1871; Romagna Mar 1860 vs COW Dec 1860) |
| Coding difference | 6 | Legal vs. actual control: OHM keeps Bosnia and Cyprus Ottoman, has Luxembourg separate throughout, shows the Cretan State. On Hesse-Darmstadt 1867 OHM is right and COW is wrong |
| OHM gap or error | 8 | See below |

New problems found by the audit:
- **Schleswig, Holstein and Lauenburg belong to no country from Jan 1864 to Oct 1866** (Lauenburg until July 1867). Denmark's record ends on a year-only date, and the Austro-Prussian joint rule (1864–66) is missing entirely.
- **Ulcinj is in Montenegro from July 1878**; it was handed over in Nov 1880.
- **Crete has no country in 1897** (part of the Ottoman 1897 gap).
- **German Empire starts 4 May 1871** (imperial constitution in force); most references use 1 or 18 Jan 1871. Defensible but unusual.
- Minor: France's 1860 record includes Menton 10 months before its Feb 1861 purchase.
- Confirmed from the earlier checks: Greece missing before 1832; Arta never becomes Greek.

Limits: COW only covers transfers involving states it recognizes, so it does not test Bulgaria 1885, the pre-1816 German states, or vassal-state internal changes.

## Head-to-head on the same checks
| Dataset | Result | Notes |
|---|---|---|
| OHM | 149/160 (125/131 for 1816+) | Day-level dates, detailed geometry, public domain |
| CShapes-Europe (ETH Zurich) | ~117/131 (starts 1816, so 29 checks not applicable) | Yearly, independent states only, simplified coastlines (coastal cities fall 2–11 km outside polygons). Errors: Tuscany shown as Austria in 1850; Milan still Austrian in 1860; Frankfurt 1860 shown as Nassau; Hamburg, Lübeck, Cyprus, Heligoland absent. Has Bulgaria 1879–1912 and the Saxon duchies 1816–1826, which OHM lacks. CC BY-NC-SA 4.0 |
| Cliopatria (Seshat) | ~115/160 | Coarse (~40 km² resolution). Errors include Dresden 1850 and Wittenberg 1812 as Duchy of Warsaw, Budapest 1850 as "Hungarian Nationalists", Prussia often missing (only the German Confederation umbrella), Florence 1850 as Austria, Arta/Larissa 1882 Ottoman. Has 1806–1815 German states OHM lacks, but needs checking. CC BY 4.0 |

## Other sources
- **COW Territorial Change v6** (1816–2018): tables of every territorial transfer with dates, gainer and loser. No maps. Best checklist for systematically auditing OHM's change dates.
- **Euratlas** (commercial, ~€150+): 1800 and 1900 snapshots only; separates sovereign vs. holder states and marks uncertain borders.
- **Centennia** (commercial): Europe and Middle East 1000–present at about tenth-of-a-year resolution; GIS research edition by institutional license; free viewer for 1789–1939.
- **HistoGIS** (Austrian Academy of Sciences): dated administrative units, Central Europe focus; includes Europe state borders 1815 digitized from an 1816 map; has an API.
- **Census Mosaic historical GIS files:** German Confederation 1815–1870 and German Empire 1871+ at regional level, Serbia 1865–1895 districts, Poland 1897, Europe 1900. Non-commercial, registration required.
- **historical-basemaps** (aourednik, GPL-3.0): world snapshots for 1800, 1815, 1878, 1880, 1900; self-described work in progress; each polygon has a border-precision rating.
- **Georeferenced historical maps** (e.g., MAPIRE for Habsburg surveys) to settle specific disputes.

## Reproducing
Overpass query used (POST to /api/interpreter):
```
[out:json][timeout:120];
relation["boundary"="administrative"]["admin_level"="2"](34,-25,72,45)
  (if: t["start_date"] < "1901" && (t["end_date"] >= "1800" || !is_tag("end_date")));
out tags;
```
Point checks used `is_in(lat,lon)` plus a direct point-in-polygon test on `rel(ID); out geom;` where the index looked stale.
