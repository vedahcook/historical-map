# Triage: is the map wrong, or the event?

You are checking questions where a historical map of Europe (who held every place, year by year, 1000–2026) seems to
disagree with an event or place from Wikidata. Each question is one JSON object in your batch file:

- `test`: what kind of disagreement (see below); `where`: the city or place; `y`: the event's year; `q`: the event's
  Wikidata id (null for `flip`)
- `text`: the question in plain words
- `map`: what the map shows around then, as [year, ruler] pairs (each ruler holds from that year until the next pair)
- `winner` / `sides`: what Wikidata gives as the winner or the sides

Tests: **capture** (an event that took the city, whose winner the map does not show holding it right after; *date*:
the map shows the change at another date; *never*: not at all), **held** (the defender won but the map changes ruler),
**ruler** (the sides of a fight in the city do not include the map's ruler), **flip** (the map shows the city changing
ruler and back within 10 years with no event recorded), **placed** (the event is filed under a city but happened far
away).

For each question, read the event's English Wikipedia article (WebFetch https://en.wikipedia.org/wiki/Special:Search?search=<Wikidata id or name>,
or the Wikidata item https://www.wikidata.org/wiki/<q> for its article link) and, when needed, the city's history
article. Then decide one verdict:

- `map` — the map's ruler or dates are wrong. Give `fix`: who really held the place and from when to when.
- `event` — the event's record is wrong (wrong winner, wrong year, filed under the wrong city). Give `fix`.
- `naming` — no real disagreement: the names differ (e.g. "Habsburg Monarchy" vs "Holy Roman Empire"), the ruler was
  an ally, overlord or vassal of a side, a short raid or sack that did not change who held the city, or similar.
- `expert` — historians disagree, or the sources do not settle it. Say what is disputed.

Be strict: say `map` or `event` only when a source says so plainly; never guess. Keep `why` to one or two plain
sentences. Cite one to three source URLs. Write American English.

Write your answers as a JSON array to the output file named in your instructions, one object per question, in the
same order: `{"i": <the question's index>, "verdict": "map"|"event"|"naming"|"expert", "fix": "...", "why": "...",
"sources": ["..."], "confidence": "high"|"medium"|"low"}`. Use the Write tool for the file. Reply with only a one-line
count of verdicts when done.
