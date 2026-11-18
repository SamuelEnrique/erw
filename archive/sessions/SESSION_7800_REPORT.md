# Session 7800 report: chain 401, the ground, part A and part B (the screenshots of the ruling alternatives)

Energy Research Warehouse (ERW). Chain 401 of 17 November 2026 (`queue/done/401-day-17-november-desktop-screenshots-regions-tariffs.md`), lab-desktop, data machine. Model spend USD 0: no script called a model. 17 November 21:33 UTC to 18 November 00:20 UTC.

## What Samuel can now see that he could not before

- 91 rows of `docs/state/browser_reads_wanted.md` marked: the 87 `wanted` rows of 13:20 PST and 4 rows (373 to 376) that chain 402 added during the afternoon. 68 seen, 6 faults, 17 not seen. Each seen or faulted row has the branch's picture at the name the row gives and production's beside it as `<name>-default-1280.png` in `docs/reviews/ruling-alternatives/` (12 MB of production pictures; about the same for the branches), and the row's state gives the figure read on the branch and on production.
- The faults, each also one line under "Browser reads of chain 401" in its tool's ruling-alternatives record:
  - row 345 (`wip/alt-events-2`): with `wip/alt-events-1` beside it the Elliott page's whole "What the estimates say" reads "license needed", so the numbers cannot be seen; `wip/alt-events-1` alone does the same (row 340, seen otherwise).
  - rows 341 (`wip/alt-impact-26`), 362 (`wip/alt-prices-3`), 366 (`wip/alt-supply-2`): at 390 px the page is 409, 504 and 490 px wide (production 390).
  - row 363 (`wip/alt-storage-1`): the new column reads "no whole month" for every grid.
  - row 357 (`wip/alt-prices-2`): only the day-ahead October row is drawn, not the real-time one.
- Not seen: 13 rows need a branch builder's table loaded to the live set (279, 282, 286, 294, 299, 302, 311, 317, 324, 329, 336, 350, 365), each with the figure its test pins; 3 need a model call (308, 314, 319: about USD 0.05, 0.03 and 0.03); 1 needs a stale row on the board (358).
- Seen with figures other than the row's, because today's tables are newer: 293, 298 (August 2026 now held), 303, 364, 369, 371, 375, 376; seen with a scale or a rounding unlike the row's: 288, 290, 295, 309, 316, 323, 335. Each says so in its state.
- Seen with something else worth a look: row 367 (`wip/alt-grid-2`): the lead sentence takes the snapshot's hour (Nov 17, 50,367 MW) while the Demand card under it keeps Nov 15, 54,008 MW; row 356 (`wip/alt-map-1`): its source line reads "the datacenter tracker, ." with the date empty.

## How

- One worktree, `C:\Users\Shared\Documents\erw-alt` (packages by `npm ci`), each branch checked out in turn and served by `next dev` (`runs/c401/serve.ps1`, port 3401, a `site/.env.local` with the Supabase anon key and the internal token only), read with the internal view in a fresh headless Chrome (`runs/c401/shot.mjs`, one JSON spec a row in `runs/c401/specs/`, the runner `runs/c401/run_rows.sh`). Production read the same way at erw-flame.vercel.app. Every read sends Do-Not-Track and, after row 344, `x-erw-check: 1`.
- Builders run into the worktree only: `project_map.py --in-dir` (rows 356 and 359) and `price_compare.py --snapshot` through `runs/c401/pc_wrap.py` (rows 371 and 372: main's tables read, the table to a scratch folder, only the worktree's `site/data/price_compare.json` written). Nothing was loaded to the live set, Supabase, the Redivis draft or main's page files; no `wip/alt-*` branch was merged, landed or requested.
- Row order: largest change first (`runs/c401/wanted_rows.py`), rows of one tool together.

## Commits

- `aa081f1d5` the chain file as pasted; the rest appended when Samuel sent it; the resume file `queue/next/410-resume-chain-401.md`; `docs/state/progress_c401.md`.
- One commit a row, "Session 7800: browser row N ...", 91 in all, each with its pictures, the row's state and its progress line; fault rows also carry their record line.

## Part A

- No row of `docs/state/landing_request_*.md` is requested.
- `data_requests_five_tools` row 2 waits on Samuel's ruling (default: the generator steps stay off); row 5 is done on main (`scripts/price_years_rebuild.py`, `price_years_by_window` rebuilt 14 November); `data_requests_forecast` row 5 is stopped by comptroller.texas.gov's robots file. Nothing new to do.

## Errors and what was done

- Turbopack's dev server kept modules from the branch before (`periodMeans is not a function`, `wholesaleMonth is not a function`) on rows 285 and 342. From then on every row got a fresh server on an emptied `.next`, and the six faults and row 309 were read again on fresh servers: each held.
- For a few minutes two runs shared the worktree (a background run of rows 325 and 361 beside rows 347, 353 and 344); rows 325, 347 and 361 were read again alone. 353 and 344 ran after the background run stopped touching the worktree.
- A heredoc slipped into one command against the chain's rule; it was stopped at once and ran nothing.

## Needs the key

- Rows 308, 314 and 319: the Ask chat's answers on a build of the branch, about USD 0.11 for the three. Until then Samuel rules on them from the tests' pinned figures.

## Decisions made without you

- The pasted chain first arrived without its resume block; the resume file was written in chain 370's form and matched, word for word, the block that came later.
- Rows 373 to 376, added by chain 402 after this chain was written, were read too: the chain's purpose is that Samuel sees every alternative he rules on tonight.
- A row whose figures follow a table that changed since the row was written is `seen`, with both figures, not a fault; a fault is a branch that does not show what it was built to show.
- Pictures beyond the one the row names (a second state, a hover) are named `<tool>-<n>-<what>-1280.png`, each with its production twin.

## For Samuel's ruling

- Two plays of the home battery game reached `game_plays` from the local dev server through the page's own route, before the reads sent `x-erw-check: 1`: Winter Storm Uri (level 2021-02-15), Normal, no moves, about 23:49 and 23:55 UTC on 17 November. Default: left as they are; delete them by those times if they should not be in the research table. The production plays of rows 344 and 346 carried the scripted-check header.
- Row 367 (`wip/alt-grid-2`): the lead sentence and the Demand card name different hours on the branch; if this alternative is chosen, the card would want the same rule. Default: none, it stays a ruling alternative.
