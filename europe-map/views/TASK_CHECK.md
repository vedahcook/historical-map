# Your task: check another agent's picks for a few cities

You are checking choices of period views of cities for a historical map's city popup. All material is on disk; no network access is needed.

Read /home/claude/cv3/work/PICKING.md first (the rules the picker followed). For each of your cities (slugs in your prompt):
- Picks: /home/claude/cv3/work/picks/<slug>.json (each pick has "n", the candidate number). If a city has no picks, write a review with an empty "checks" list.
- Candidates: /home/claude/cv3/work/<slug>/candidates.md, which names each candidate's preview in /home/claude/cv3/work/<slug>/previews/. Open the preview of every pick with the Read tool, and read its candidates.md entry.

For each pick decide:
1. Does it really show this city (not another city or a place with the same name, not a generic or fictitious view)?
2. Is "y"/"lab" the year the picture was made (not an upload, photo-of-a-painting or reprint date)? Braun & Hogenberg plates take the year of first publication of that volume. "lab" must read naturally after "From " ("1572", "1890s", "about 1860", "1758–61").
3. Is it a reasonable view of the city (general view or recognizable landmark), not a map, ground plan, interior, or a page mostly of text?
4. Do "trim" (fractions to keep: left, top, right, bottom) and "focal" (fractions of the trimmed picture) give a good 16:9 crop: no frames, margins, captions or book gutters inside it, tops of towers not cut off, and not zoomed in to less than about half the picture's width?
5. Do "what", "who" and "lic" agree with the candidate's record?
If a pick is wrong and a clearly better candidate exists in the same period, name it (open its preview first).

Write /home/claude/cv3/work/review/<slug>.json:
{"city": "...", "checks": [{"n": 12, "verdict": "ok" | "fix" | "drop" | "replace", "replace_with": 15, "fix": {"y": 1650, "lab": "1650", "trim": [...], "focal": [...], "what": "...", "who": "..."}, "reason": "short"}]}
Only include "fix" fields that should change, and "replace_with" only for "replace". Be strict but fair; "ok" is the expected verdict for most.

When finished, reply with one line per city listing only the non-ok verdicts (or "all ok"). No other commentary.
