# The desktop's second window, chain 228: the landing desk (13 November 2026)

Energy Research Warehouse (ERW), sessions 4000 onward, for Samuel. Chain 228 (`queue/done/228-day-13-november-desktop-window2-landings.md`), lab-desktop's second Claude Code window, unattended from 09:25 UTC. Opus 5.5. Model spend: USD 0.

(Kept current as the chain goes; session 4049 finishes it.)

## Read these first

- **An 8 GB laptop can run the landing gate again** once `wip/w2-4000` lands.
  - numpy's OpenBLAS committed about 610 MB in every Python process, a buffer for each of the desktop's 20 threads. The suite now runs its maths on one thread.
  - Below 12 GB, `land_check.py` runs the suite in batches of 40 modules (`scripts/suite_batches.py`).
  - Whole suite batched: 8,648 tests OK; the heaviest process 652 MB.
- **The curtain's hole is closed on production** (row 18, `b1ea7427a`): `check-curtain.mjs` exit 0 after the deploy.
- **Every morning gate failed `/digest`'s floor by the clock**, because the page has no issue before 14:00 UTC. check-values now notes the floor in that case instead of failing it.
- **A revised figure's note on a stored Digest was silently removed whenever the issue's story sections were held** (since 21 October).
  - digest.ts spliced the notes in before the news index's hold rewrote the sections by their original line places.
  - EIA revised 12 November's US48 demand peak (488,034 to 488,341 MW), and every gate failed on it from that afternoon.
  - Fixed in land-f: demand is read as a revision too, the notes go in after the hold, and once a key.

## Every landing, with its commit

| Row | Branch | Commit on main | Snapshots |
|---|---|---|---|
| old laptop 9 | `wip/1905-revert` | `3a82aebe4` | 0 differences |
| portable 16 | `wip/3701-sellable` | already landed at `5a2193a1e` (12 November) | none needed |
| portable 18 (urgent) | `wip/5100-security` | `b1ea7427a` | 0 differences; curtain exit 0 |
| portable 17, 19 to 22 | `wip/5000-grid` (P1's stack) | `5fe21d6de` | 0 differences |
| old laptop 10, in part | `wip/1973-periodicals` to `5f5aea071` | `5fe21d6de` | 0 differences |
| this window's own | `wip/w2-4000` (the 8 GB gate, the root causes, the `/digest` floor) | `5fe21d6de` | 0 differences |
| desktop w3 4 (licenses, rows 1 to 3 within it) | `wip/4150-licenses`, with the desk's fix of a held count | `71f8442ed` | the menu's rename on 25 pages, expected |
| desktop w4 1 (the forecast, `/impact`) | `wip/4200-forecast` | `71f8442ed` | the same |
| old laptop 10, in part | `wip/1973-periodicals` to `88893595d` | `71f8442ed` | the same |
| desktop w3 6 (licenses, rows 1 to 5 within it) | `wip/4166-licenses` | `f06f7f3d2` (pushed at 16:15) | 0 differences |
| desktop w4 2 and 3, and 4 to `a544dbc19` | `wip/4250-forecast` | `f06f7f3d2` | 0 differences |
| old laptop 10, the rest (to `a898be5be`) | `wip/1973-periodicals` | `f06f7f3d2` | 0 differences |
| desktop w4 4, the rest (to `ea34a1ea8`) | `wip/4250-forecast` | `8f7995482` | 0 differences |
| desktop w4 5 (to `279dd3121`), with the desk's fix of a Digest's revision notes | `wip/4250-forecast`, `wip/w2-4000` | `b5e925530` | 0 differences |
| old laptop 11, in part (to `e547f598f`) | `wip/3457-periodicals` | `f71fda27e` | 0 differences |
| desktop w4 6 (Virginia) | `wip/4270-forecast` | `ad7f16ca6` | 0 differences |
| portable 23, in part (to `5411fef7d`, the security list) | `wip/5150-security` | `ad7f16ca6` | 0 differences |
| old laptop 11, in part (to `91cc7525c`) | `wip/3457-periodicals` | `ad7f16ca6` | 0 differences |

## Rows that wait, and why

- **Window 4's branch past `ea34a1ea8`** (`93a66d4ee`, code): waits for a new row.

## The fallback's results

- **(a) The 8 GB gate:** above.
- **(b) Root causes:** every failed scheduled run of 30 October to 12 November is written in `queue/summary/`. Two are open:
  - the board's spark spread (window A's session 3873);
  - in part, the 8 November ledger refusal.
- **(c) Main green:**
  - the gates' suites passed on main merged: 8,633 tests at 09:34 and 8,640 at 10:19;
  - the `/digest` floor fixed;
  - test 1116 passes on main.

## Decisions made without you

- **One gate for several requesters' stacks** (sessions 4003, 4005 and 4007).
  - The build lock is shared with window A and window 4's builds, and one gate takes about 35 minutes.
  - Conflicts were resolved by rule:
    - a generated file by its generator (`package/llms.txt`'s catalogue by `scripts/build_llms.py`);
    - a request file by main's rows.
- **A branch its owner keeps committing to is gated as a `wip/w2-*` copy**, never pushed onto. A row is landed at its requested head, and later commits are taken only when the row allows them (reports and notes).
- **Row 18 (the curtain's hole) went before row 17**, which had been requested a few minutes earlier.
- **A held table's row count is held** (session 4005, landed with window 3's row 4). This is the small, plainly correct fix the gate found.
- **The batched suite is the gate's default only below 12 GB.** The desktop and GitHub keep one process. The maths libraries run on one thread everywhere in the suite.
- **No push between 14:00 and 16:15.** The blackout's gate (land-c) was run before 16:15 and pushed at 16:15.

## For Samuel's ruling (each with the default taken)

- **`/policy`'s floor (10)**: since `policy_actions` and `policy_reads` are held, the page carries 0 checked numbers and its "license needed" marks.
  - Default: `/policy` is in `land_check.py`'s `HELD_FLOOR_PAGES` beside session 408's ten, a pass only when the page shows "license needed".
  - The other way: lower the floor in `site/scripts/check-values-floor.json`.
- **The forecast's menu name "Local impact"** (window 4's row): it landed with that default, and the menu reads "Local impact in review" on every page.
