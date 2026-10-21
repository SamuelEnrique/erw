# Session 474 report: the landing checks that fail on production

21 October 2026, about 10:11 to 13:25 UTC, unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-474` on `wip/474-checks` (from `origin/main` at `440a2c8f`). The chain `queue/done/019-night-21-october-code.md`, session 474, written for samueloldlaptop and run on portable-laptop. Model spend USD 0; no warehouse data written; no request but to the production site. Nothing landed: no agent lands tonight (the parent's permission check refused a landing), so "after the night's landings" was read as production as it stands.

## Read these first

- **17 landing checks were run against production** (`https://erw-flame.vercel.app`, the internal view by the form's door, as each check unlocks it): the two `code-branch.yml` runs (`check-routes`, `check-no-request`) and the landing script's list of sessions 381 to 383 (`check-values`, `check-table-downloads`, `check-security`, `check-queues`, `check-map-v2`, `check-csp`, the battery and datacenter checks, `check-findings-grids`, `check-cross-checks`, `check-decisions-face`, `check-analysis`). **14 passed as they stand.**
- **Two were the checks' own faults, and are fixed** (`3bcf01f3`):
  - `check-analysis`: 10 of 279 failed, every one a NYISO or ISO-NE callout. From 21 October a callout whose words name a held grid is drawn as "license needed" (`components/Num.tsx`); the check now reads the hold as `lib/license.ts` does and the grid as `FindingCard.tsx` does, and expects the words and not the number in that callout. **279 of 279 on production.**
  - `check-findings-grids`: it waited 30 s for a canvas that no page draws since sessions 317 and 318 moved the cards' charts to the shared SVG set. Session 381 read the failure as "the small multiples are no longer the card's first view": they are (`data-multi-view="all"` on production); the canvas was the fault. It now waits for the SVG and counts the multiples as panels, one a grid. **161 of 163 on production.**
- **The two left are the page's, not the check's**: the 1600 x 900 render frames of `batteries_lunch_grids` and `peak_hour_grids` hold chart labels (SVG `tspan`s of a panel's direct labels) that end at 952 and 924 px, below the picture; the card's last line ends inside it (866 and 735 px). The photograph cuts them.
- **`check-values` on production ran past its own 15-minute limit** at 11:52 UTC (the probe had passed at 2.96 s, at the edge of its 3 s): the database, not the check. Its first run (10:22) stopped at once on `SUPABASE_URL is not set`, a fault of this worktree (no `site/.env.local`), not of production.

## The table

| Check | Exit on production | Failures | Done | Commit |
|---|---|---|---|---|
| check-routes | 0 | none | | |
| check-values | 1 | ran past its 15-minute limit (the database) | for the landing machine, with the gate open | |
| check-table-downloads | 0 | none | | |
| check-security | 0 | none | | |
| check-queues | 0 | none | | |
| check-map-v2 | 0 | none | | |
| check-cross-checks | 0 | none | | |
| check-analysis | 1, then 0 | 10 held callouts read as numbers | fixed: the hold read as the card reads it | `3bcf01f3` |
| check-csp | 0 | none | | |
| check-no-request | 0 | none | | |
| check-datacenter | 0 | none (the three grids that failed on 20 October pass) | | |
| check-datacenter-scenarios | 0 | none | | |
| check-datacenter-face | 0 | none | | |
| check-battery-scenarios | 0 | none (CAISO 2 hours passes) | | |
| check-battery-face | 0 | none | | |
| check-findings-grids | 1, then 1 | first: waited for a canvas; now: the two 1600 x 900 frames | fixed (the canvas); the frames for Samuel or a session with a build | `3bcf01f3` |
| check-decisions-face | 0 | none | | |

Totals: 17 run; 14 passed as they stand; 2 fixed (one passes now, one finds the page's fault); 1 waits for the database; 0 retired (none describes a page that no longer exists).

## What to review

- `https://github.com/SamuelEnrique/erw/commit/3bcf01f3` on `wip/474-checks`: `site/scripts/check-analysis.mjs`, `site/scripts/check-findings-grids.mjs`, `tests/test_session474.py`.

## Checks

Every gate redirected to a file under `runs/chain_019/s474/` in the worktree, never piped; the exit code read before the next step. The production runs went one at a time under the machine's build lock, 20 s apart, with a beat before each.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 474"` | 0 | passed (the machine's duty mark is held by the main checkout, so not marked again) |
| The 17 checks against production | see the table | `exits.txt`, one `.out` a check |
| `check-analysis.mjs` against production, after the fix | 0 | 279 of 279; the 10 held callouts read as "license needed" |
| `check-findings-grids.mjs` against production, after the fix | 1 | 161 of 163; the two render frames |
| `tests.test_session474` | 0 | 8 tests OK |
| `tests.test_session474` with a canvas planted in the check | 1 | as it should |
| `tests.test_session170`, `182_flow`, `238`, `474` (the tests that read the two scripts) | 0 | 79 tests OK, 2 skipped |
| `scripts/db_probe.py` | 1, then 0 | 3.72 s at 11:30 UTC; 2.96 s at 11:51 UTC |
| `check-values.mjs` against production, keys from `.env` | 1 | past its 15-minute limit |

Impeccable is not installed on this laptop; no page was changed, so none was owed.

## Decisions made without you

1. **The checks run are the landing gate's**: `code-branch.yml`'s two and the landing script's list of sessions 381 to 383, the checks a landing fails on. The other 45 check scripts belong to their own pages' sessions and were not run against production tonight (the database is slow).
2. **The browser checks were run against production as earlier sessions ran them**: a page view in a browser posts the site's usage count (path and event, no value), so tonight's runs are counted on `/internal/usage` as visits to pages in review.
3. **check-analysis reads the hold, it is not loosened**: a held callout must show the words, carry `data-license-held`, and not print its number; the others must print their number as before.
4. **check-findings-grids keeps every expectation but the canvas**: the render frames' rule (the whole card on the picture) is unchanged, so it now fails on a real fault.
5. **The one-grid view's figures were not changed** (below): the session's part is the checks; the page's treatment of a held grid's panel is a choice of form.
6. **check-values was run once on production, after the gate opened**, with the keys read from `.env` in the environment; when it ran past its limit it was not run again, to spare the database.

## For Samuel's ruling

- **The five-grid cards still draw the held grids' figures.** `batteries_lunch_grids` and `peak_hour_grids` draw NYISO's and ISO-NE's panels in the small multiples, and their one-grid views (`?<param>=nyiso`, `=isone`) print the chart, the callouts and the regression table with those grids' figures (`components/analysis/MultiChart.tsx`, which does not go through `Num`). Only the card's own three callouts are held. Whether a held grid's panel becomes a placeholder, as MISO's and PJM's are.
- **The render frames at 1600 x 900**: the labels of a panel run 24 to 52 px below the picture on two cards. The fix is in the shared SVG chart's direct labels (or the frame's height), a session with a build.

## To finish

- In the landing branch, with the gate open (`python scripts/db_probe.py` exit 0) and under the build lock: the build, then `node scripts/check-analysis.mjs http://localhost:<port>` and `node scripts/check-findings-grids.mjs http://localhost:<port>` against it (expected: 279 of 279, and 161 of 163 until the render frames are fixed), and the full `check-values`.
- Land `wip/474-checks` with the night's other branches (two check scripts and a test; no page changes).

## Files

- `site/scripts/check-analysis.mjs`, `site/scripts/check-findings-grids.mjs` (changed).
- `tests/test_session474.py` (new).
- This report.
- Not in git: `runs/chain_019/s474/` (each check's output, `exits.txt`, the runner, the peeks at production's markup, the shots of `check-findings-grids`).
