# Your task: add period views for a few cities (second search)

You are choosing period views (old engravings, paintings, early photographs, a modern photo) of cities for a historical map's city popup. A first search found few or no usable pictures for these cities; a second, deeper search found the candidates on disk. You need no network access.

1. Read /home/claude/cv4/work/PICKING.md and follow it exactly.
2. For each of your cities (slug and name in your prompt), /home/claude/cv4/work/<slug>/ holds candidates.md, contact sheets <slug>-1.jpg, -2.jpg…, and previews/. The top of candidates.md lists the views the city ALREADY has.
3. Pick new views only for periods the city doesn't have yet. You may replace an existing view only when a candidate in the same period is clearly better (a general view instead of a weak street scene, much sharper, clearly the city's landmarks); then add `"replaces": <year of the existing view>` to that pick and say why.
4. For each city: read candidates.md, look at every contact sheet with the Read tool, open the 500 px previews of the candidates you're seriously considering (always for the ones you pick, to set trim and focal point), then write /home/claude/cv4/work/picks/<slug>.json in the format in PICKING.md. Check it parses (python3 -m json.tool). Use only file names from that city's candidates.md, copied exactly. An empty "picks" list is fine when nothing new is good.
5. Be strict: the picture must really show this city (many names are shared with other places, and searches in other languages bring in unrelated files), the date must be when the picture was made, and it should be a general view or a recognizable landmark scene, not a single house, a street sign, a group of people or an interior. Old postcards are welcome. Skip a period rather than use a doubtful picture. Trim away frames, margins, captions and postcard borders.

When finished, reply with one short line per city: new periods covered (with years), any replacements, and gaps. No other commentary.
