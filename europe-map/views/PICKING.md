# Picking period views for the Europe map's city popup

The popup shows a picture of the city made close to the year on the map: the closest view within 100 years, otherwise a blank plate. So each city needs a spread of views across the centuries, each one clearly of that city.

For each city folder you are given:
- `candidates.md`: numbered candidates (#1, #2, …) from Wikimedia Commons, with period, date as read, series, size, license, file name, artist, date field, description and city categories.
- `<slug>-1.jpg`, `-2.jpg`, …: contact sheets showing the candidates by number.
- `previews/`: a 500 px copy of each candidate (file named in `candidates.md`). Open these for any candidate you're seriously considering, and always for the ones you pick (you need them for the crop).

## What to pick
- At most one view per period: P0 before 1500 · P1 1500–1649 · P2 1650–1749 · P3 1750–1849 · P4 1850–1913 · P5 1914–1969 · P6 1970–today. Exception: P3 and P4 may have two if they are at least 40 years apart and both are strong. So 5–8 views per city.
- Skip a period rather than use a weak, doubtful or wrong picture. A blank plate is better than a wrong one.
- Best: a general view of the whole city (panorama, bird's-eye view, view across the river or from a height) where its main landmarks are recognizable. Then: a famous landmark scene that says "this city". Color beats black and white when both are good. Higher resolution beats lower.
- Avoid: maps and ground plans (a Braun & Hogenberg bird's-eye view with buildings drawn is fine; a flat street plan is not), single buildings or interiors when a general view exists, pages dominated by text, duplicates of the same plate, pictures of other cities (check the title, description and categories — some search hits are paintings of other cities held in this city's museums).
- Nuremberg Chronicle (1493): use only a woodcut labeled with this city that is a true view. Many town woodcuts in the book are generic stock blocks reused for several towns; if the description says so, or you can't tell, skip it.
- A view of a specific event (a siege, a fire, a city in ruins) is allowed but must be marked `"event": true`; it will never be shown for years before it. Prefer ordinary views.
- Modern period (P6): a good, recent photograph of the city's skyline or historic center, ideally a Commons Quality or Featured image.

## Dates
- `y` is the year the picture was made (an integer used for matching); `lab` is how the label shows it: "1572", "1890s", "about 1860", "1758–61".
- Prints from books take the year the plate was first published, even for later colored copies: Braun & Hogenberg vol. 1 1572, vol. 2 1575, vol. 3 1581, vol. 4 1588, vol. 5 1598, vol. 6 1617. Merian's Topographia: the year of that volume (for example Topographia Bohemiae 1650, Topographia Germaniae volumes 1642–1654, Topographia Italiae 1688). If you know the plate's year from the description, use it.
- Commons sometimes gives the date a painting was photographed or a book was reprinted; correct it from the description, or skip the picture if the true date is unclear.
- Photochrom prints: "1890s", `y` 1895, unless the record gives a specific year.

## Fields to write (one JSON file per city: `picks/<slug>.json`)
```json
{"city": "Prague", "picks": [
  {"n": 2, "file": "Nuremberg chronicles - praha.png", "y": 1493, "lab": "1493",
   "what": "Woodcut in Hartmann Schedel’s Nuremberg Chronicle", "who": "Michael Wolgemut and Wilhelm Pleydenwurff",
   "lic": "PD", "event": false, "trim": [0, 0, 1, 1], "focal": [0.5, 0.5], "why": "colored true view; castle and bridge recognizable"}
], "gaps": "P2: nothing usable", "notes": "anything the reviewer should know"}
```
- `file`: the exact Commons file name from `candidates.md` (without "File:").
- `what`: short plain description in this style: "Engraving in Braun and Hogenberg, Civitates Orbis Terrarum, vol. 1" · "Bird’s-eye view, etching" · "The Charles Bridge and the castle, painting (National Gallery Prague)" · "Photochrom print (Library of Congress)" · "Aerial photograph (ETH Library, Zurich)" · "Photograph". Name what is shown when it isn't the whole city ("The Opernring, photochrom print").
- `who`: the maker(s) as usually credited: "Georg Braun and Frans Hogenberg" · "Matthäus Merian" · "Detroit Publishing Co." (or "Photoglob Zürich", per the record) · "Walter Mittelholzer" · the photographer's name for modern photos (from the artist field, cleaned of usernames in brackets). Use "unknown artist" or "unknown photographer" if none.
- `lic`: "PD" for public domain (including "PDM-owner"), "CC0", or the exact Creative Commons short name ("CC BY-SA 4.0").
- `trim`: fractions [left, top, right, bottom] of the picture to keep, cutting book margins, page gutters, text blocks, color bars and frames. A plate with two cities (Prague above Eger) is trimmed to this city's half.
- `focal`: the point [x, y] (fractions of the trimmed picture) that a 16:9 crop should center on: the most recognizable part (cathedral, castle, river front).
- `why`: a few words for the reviewer.
- Use typographic apostrophes (’), American spelling, plain words.

Work city by city. When done, reply with one line per city: views picked by period, and any gaps.
