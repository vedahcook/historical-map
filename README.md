# Historical Map

Work toward a more complete, better-sourced dataset of historical borders, starting with Europe in the 19th century and using [OpenHistoricalMap](https://www.openhistoricalmap.org) (OHM) as the base.

## What we know so far

- **OHM is the best open starting point.** It got 149 of 160 place-and-date checks right, ahead of CShapes-Europe (about 117 of 131; it starts in 1816) and Cliopatria (about 115 of 160).
- **Checked against the Correlates of War (COW) list of territorial transfers (1816–1900)**, OHM agrees within two months on 53 of 83 checks and within a year on 16 more. Where they differ, OHM is usually the more precise.
- **Main gaps in OHM:**
  - German states before 1810 (1826 for the Saxon duchies).
  - Bavaria 1814–16.
  - Schleswig-Holstein 1864–66, which belongs to no country.
  - Bulgaria 1885–1908.
  - Greece before 1832.
  - Crete in 1897.
- **Wrong in OHM:** Ulcinj is Montenegrin two years early, and Arta never becomes Greek.

Details: [docs/assessment.md](docs/assessment.md). Every audit check: [data/ohm-vs-cow-transfers-1816-1900.csv](data/ohm-vs-cow-transfers-1816-1900.csv).

## Balkans pilot

A working review tool on real data for the Balkans, 1815–1900. Three datasets are compared town by town and year by year, and their disagreements are grouped into 28 questions, each with suggested answers and sources. See [pilot-balkans/](pilot-balkans/).

## Europe map, 1800–1900

An interactive map of Europe's borders year by year, built on OHM with gaps filled from CShapes-Europe and Cliopatria and a short list of corrections. Where another source draws a different border, the map marks it with a dashed outline and explains the difference. See [europe-map/](europe-map/).

## Where this is going

Store individual claims ("this area belonged to this state from date A to date B, according to source S") with their sources and weights, instead of one map. When sources disagree, the system suggests an answer, and a reviewer approves it when a primary source backs every date; otherwise it goes to an expert. The [mockup](mockup/) shows the review screens.

## What's here

| Folder | Contents |
|---|---|
| `docs/` | The assessment write-up |
| `data/` | Test places, the 160 spot checks, the 60 COW transfers tested, and the audit results |
| `scripts/` | Scripts that rerun the checks against OHM, CShapes-Europe and Cliopatria |
| `mockup/` | Source for the conflict-review mockup (queue, conflict detail, rules) |
| `pilot-balkans/` | The Balkans review tool and the scripts that build it |
| `europe-map/` | The Europe 1800–1900 map and the scripts that build it |

## Rerunning the checks

The scripts need internet access. The Node scripts need Node 18 or newer and nothing else installed.

```
node scripts/ohm_checks.mjs records   # every OHM country record for 1800–1900, with date gaps flagged
node scripts/ohm_checks.mjs spot      # the 160 spot checks
node scripts/ohm_checks.mjs audit     # the COW transfer audit
node scripts/cshapes_checks.mjs       # the spot checks against CShapes-Europe
python3 scripts/cliopatria_checks.py path/to/cliopatria_polities_only.geojson   # needs: pip install shapely
```

Results are written to `out/`.

**Status:** the checks were first run on 2026-09-29 from a browser, using the same logic. The Cliopatria script has been run as-is. The OHM and CShapes scripts are tidied versions and haven't been run from the command line yet.

In the data files, `expected_holder`, `loser_pattern` and `gainer_pattern` are patterns matched against the English state names used in OHM. For example, `Sardinia|^Italy$` means "Kingdom of Sardinia" or "Italy".

## Sources and licenses

- **OpenHistoricalMap:** public domain (CC0).
- **CShapes-Europe (ETH Zurich):** non-commercial use only (CC BY-NC-SA 4.0).
- **Cliopatria:** CC BY 4.0.
- **COW Territorial Change v6:** from correlatesofwar.org. This repo includes only our own test list and results, not COW's data.
