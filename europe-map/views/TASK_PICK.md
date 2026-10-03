# Your task: pick period views for a few cities

You are choosing period views (old engravings, paintings, early photographs, a modern photo) of cities for a historical map's city popup. All material is already on disk; you need no network access.

1. Read /home/claude/cv3/work/PICKING.md and follow it exactly.
2. For each of your cities (folder slug and name are given in your prompt), the folder /home/claude/cv3/work/<slug>/ holds candidates.md, contact sheets <slug>-1.jpg, -2.jpg…, and previews/.
3. For each city: read candidates.md, look at every contact sheet with the Read tool, open the 500 px previews of the candidates you're seriously considering (always for the ones you pick, to set trim and focal point), then write /home/claude/cv3/work/picks/<slug>.json in the format given in PICKING.md. Check each file parses as JSON (python3 -m json.tool). Use only file names that appear in that city's candidates.md, copied exactly.
4. These are mostly smaller cities: picking only 1–4 views is normal, and an empty "picks" list is fine when nothing is good.
5. Be strict about the picture really showing that city (watch for places with the same name elsewhere — many of these names are shared) and about the date being when the picture was made. Prefer general views where the city's landmarks are recognizable. Skip a period rather than use a doubtful picture. Don't use a two-page spread with the gutter through the view, and trim away frames, margins and captions.

When finished, reply with one short line per city: periods covered (with years) and gaps. No other commentary.
