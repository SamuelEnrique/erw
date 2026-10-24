# Session 1173 report: the Grid pack brought current

24 October 2026 (UTC; 23 October local), on samueloldlaptop (the old laptop), session 1173 of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1173-grid`, cut from `wip/1172-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1173`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher; 23 reads of the site's own production pages through the internal view (below).

## Read these first

- **`docs/reviews/packs/grid.md` rewritten in place**, every section and history line kept, each line that no longer held corrected, with "(chain 078: was ...)" where the change matters to a reader. The opening now says the two states every figure belongs to: **on production** (landing A, sessions 1150, 1151, 1157) and **on the branch, not built** (landing B, sessions 1152 to 1172), the latter marked "from the code, to be read on landing B's build".
- **Production read at 2026-10-24 00:58 UTC** through the internal view (node's `fetch`, `unlockPost`, the token posted and never printed), 23 addresses, each 200. The script and a trimmed record are committed: `docs/brand/review-1173/walk-1173.mjs`, `walk-1173-prod.json` (panels with their keys, the first keys outside them, the sentences the pack quotes). Same interchange hour as session 1161's walk (2026-10-22 03:00 UTC), now 45 hours behind the refresh of 2026-10-24 00:06 UTC; the Mix tab's demand hour 2026-10-22 23:00 UTC, about 25 hours old.
- **What was wrong in the pack and is corrected:** "six views" opening on ERCOT's Now view (four tabs and the Ask panel since session 299, the Lower 48 by default); demand "one to two hours behind" (the sentence's hour is a day old: EIA-930 loaded by whole UTC days); the twelve months (now 2025-10 to 2026-09: CAISO 16.84, ERCOT 0.08 percent); the gravity hour of 14 October (now NYISO 21.12 and CAISO 17.45 percent); "no evaluation figure held" for the other grids (sessions 267 and 302 hold 30 questions each, 27 and 30 graded right); the replay to 2026-10-11 (now 2026-10-21); the demo's clicks.
- **A finding on production, already fixed on the branch:** four places still draw a held grid's rows on production (the Clean tab's "The seven grids, 2024" for ISO-NE, MISO, NYISO; ISO-NE's queue; ISO-NE's and NYISO's committed prices in the replay and the mix views). Session 1167's code replaces each with "license needed"; it stands on production until landing B. Said in section 6 item 6 and question 8.
- **Section 2** gains steps 25 to 34 (the server twins, stored answers, the hourly mix, scarcity, CAISO's alerts, the balance, the last keys, the Exchange blocks, a picked day, revisions); **section 3** 11 rows; **section 4** 8 rows; **section 5** 5 rows; **section 6** items 3, 4, 6, 9 and 11 updated in place and items 15 to 17 added at the end, so the blind spots' numbers the method notes and `check-revised.mjs` cite stand; **section 9** keeps its six questions (the packs' index counts them) and lists chain 078's new items in a paragraph.
- **The demo** follows the four tabs; each step is marked "walked on production" (read, not clicked: no browser) or "to be walked on landing B's build".

## What to review

1. Read `docs/reviews/packs/grid.md` on `wip/1173-grid`: the opening's two states, then sections 6 and 7, then the appendix.
2. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
3. Open `https://erw-flame.vercel.app/grid`: the Lower 48, the Mix tab; the sentence's figures as the appendix's first step quotes them (they move every hour).
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`: the seven grids' rows and "Over the last twelve months", against section 7 question 5 and section 4.
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`, "The seven grids, 2024": ISO-NE, MISO, NYISO figures drawn (the finding above).
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1173: run by the orchestrator, exit 0.
- `node docs/brand/review-1173/walk-1173.mjs` (the two runs, from the main checkout for its `.env`): exit 0, 23 addresses, each 200. `node --check` on the committed script: exit 0.
- `python -m unittest` one file at a time, each exit 0: `tests.test_session262` (12), `266` (19), `269` (6), `323` (4), `381` (8), `1170` (9, 1 skipped: no `site/node_modules` in the worktree), `1171` (7), `249` (10), `260` (12), `422` (6), and the new `tests.test_session1173` (7).
- No `tsc`: no code changed.

## The landing

- None: a document, with chain 077's landing B (waits for a person or a build).

## To finish

- At landing B's build: walk the demo's steps marked "to be walked on landing B's build" and the section 4 rows marked "from the code", put the values read in place of the marks, and run `walk-1173.mjs` again for the production rows.
- Rewrite `site/public/grid/erw_2026_grid_replication.csv` from that build (`write-grid-replication.mjs`) and section 8 with it, only if the owner wants the Stata table current (it pins the hour of 14 October and the linear pull).

## Decisions made without you

- The parts below the roadmap table are now the newer, where they differ (said in the roadmap section).
- New blind spots are numbered 15 to 17, after the old 14, so items 3, 9 and 11, which method notes and a script cite by number, keep their numbers; the ranking is the old one plus three.
- Section 9 keeps six numbered questions; chain 078's items go in a paragraph, so the packs' index (`docs/reviews/packs/README.md`, 41 questions) stays true.
- The production record is committed in a trimmed form (166 KB, no HTML), as session 1161's was, so every production figure traces to a file.
- A percent not printed on a page was not computed (CAISO's import as a share of the hour's demand): the pack quotes the page's own 17.45 percent of generation.

## For Samuel's ruling

- The held rows still on production (four places): land landing B, or accept them until it lands.

## Files

- Changed: `docs/reviews/packs/grid.md`.
- New: `docs/brand/review-1173/walk-1173.mjs`, `docs/brand/review-1173/walk-1173-prod.json`, `tests/test_session1173.py`, this report.
