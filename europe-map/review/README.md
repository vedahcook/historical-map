# Checking events and places against the map's borders

The map says who held every spot in every year. The city events (`city-events.json`, from Wikidata) and the
landmark places (`places.json`) say things too: who besieged a city and won, who fought there, when. Where the two
disagree, one of them is wrong, and someone has to decide which. This folder finds those disagreements and keeps them
as a queue of questions for later adjudication (Veda, October 5, 2026).

## Steps

1. `python3 review/fetch_wd.py` — what Wikidata says about each event and place: participants (P710), winner (P1346),
   location and coordinates, dates, and the names of everything those point to. Cached in `wd_facts.json` (run it
   again to fetch only what is missing). Wikidata throttles this workspace; a full fetch takes 20–30 minutes.
2. `python3 review/find_conflicts.py` — compares those facts with the map, year by year (needs `page_data.json` and
   `topo.json` in `/tmp/mapbuild`, see `tests/README.md`). Writes `candidates.json`. The tests:
   - **capture**: an event that took a city (siege, capture, fall, conquest, liberation…) whose winner the map does
     not show holding the city right after it: either at another date (a *date* question, like Vienna 1485 vs the
     map's 1487) or not at all (*never*)
   - **held**: the defender won, but the map hands the city to someone else right then
   - **ruler**: a battle, siege or massacre in a city whose sides do not include whoever the map says held it
   - **flip**: one of the 465 large cities changes ruler and changes back within 10 years, with no event recorded
     in the city then (like Istanbul shown Ottoman in 1402–1406)
   - **placed**: an event filed under a city but whose own coordinates are more than 25 km away (the Battle of the
     Boyne under Drogheda); its ruler is not compared with the city's
   Rulers are compared loosely, by country ("Kingdom of Hungary" matches "Hungarian"; an overlord counts), so some
   questions are only naming differences.
3. Triage (`triage/`): separate helpers read the sources for each question and sort it: the map is wrong (with the
   right ruler and years), the event is wrong or misplaced (with the fix), only a naming difference, or a question
   for an expert. Each answer cites its sources.
4. Adjudication: a person accepts or overrules each suggested answer. Decisions go to `decisions.json`; accepted map
   fixes are applied to the border data, accepted event fixes to `city-events.json` or `places.json`.

New events, places or border changes go through the same steps; questions already decided are not asked again.

## First run (October 5, 2026)

- Wikidata facts for 4,235 events and places; Wikipedia infobox results for 2,945 battles, sieges and the like (2,152
  give a result). Wikidata rarely records who won (`P1346` is empty for all of them), so winners come from the
  infobox's "X victory".
- 498 questions: capture 195 (72 about dates, 123 never shown), held 5, ruler 56, flip 109, placed 133; 316 of them in
  the 465 large cities.
- Pilot triage of 40 (two Sonnet helpers, about 320,000 tokens): 16 map wrong, 1 event wrong, 22 only naming, 1 for
  an expert. By test: capture 10 map / 6 naming; held 2 / 1; flip 4 map, 3 naming, 1 expert; ruler 0 of 8 (all
  naming: outside armies fighting over someone else's city); placed 1 event, 4 naming. Results in
  `triage/verdicts.json`.
- Map errors confirmed in the pilot include Vienna (Hungarian from June 1485, not 1487), Istanbul (Byzantine until
  1453, not Ottoman 1402–1406), Maastricht (Dutch 1831–1838, not Belgian; Dutch from 1632), Kamianets-Podilskyi
  (Ottoman 1672–1699), Tabriz (Ottoman from 1585), Edessa (Zengid from 1144), Drogheda (Commonwealth from 1649),
  Brussels (French 1746–1748), Tripoli in Greece (Greek from 1821), Évora (Portuguese from 1165).
- Recommended for the full triage: capture, held and flip (309 questions). The ruler test is mostly noise and the
  placed test mostly harmless; run them later, more cheaply, or drop them.
