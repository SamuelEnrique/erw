# Session 416 report: the four faults of 015's landing

21 October 2026, about 13:30 to 15:10 UTC, unattended, on portable-laptop (code role), in the worktree
`C:\Users\samen\Documents\erw-416` on `wip/416-417-charts` (from `origin/wip/461-combined` at `2289156d`). The chain
`queue/done/021-day-21-october-code.md` (written by session 415 for samueloldlaptop; run here by the owner's
instruction to run what the queue prints), session 416. Model spend USD 0; no warehouse data written; no request but
the production site for the before shots and the probe.

## Read these first

- **The four faults of session 415's note, "Faults found", each fixed with its test** (`tests/test_session416.py`, 9 tests):
  1. **"-0" on a chart's zero tick**: `ticksOf` in `site/components/svgchart.tsx` (which the peak-premium explorer's box
     chart draws through) takes `|| 0`, as session 404 did in `GroupedBars`; TimeChart's own `ticksOf` the same. The test
     runs the function as the file holds it on bounds of -0.3 to 1: before it gave a minus zero, which
     `toLocaleString` writes "-0"; now "0".
  2. **`/emissions`, "Monthly since 2018"** (the clean view of `/grid`; `/emissions` redirects there): monthly points were
     drawn on the default minute axis, whose labels over a long span are month and day ("08-01" to "09-01" over eight
     years). The chart passes `x="month"`: 2018-08 to 2026-09.
  3. **`/data` at 390 px: two faults, two causes, settled on production** (`runs/chain_021/s416/probe-data-390.mjs`):
     - the header row out of step is **the page's**: tokens.css keeps a table's first `th` in place while the figures
       scroll sideways, and `/data`'s rows began with a `td`, so the head's "Table" stayed at 16 px while its column's
       first cell went to -599 px. The table's name is now the row's header (`<th scope="row">`), and moves with its head.
     - the beige band is **the script's**: under mobile emulation, `docs/brand/review-410/shot-410.mjs` captured with a
       clip at (0, 0), which is read from the document's top, so the 351 px scrolled showed as a band. The same
       capture without the clip has none; the script now takes the viewport as `site/scripts/shot.mjs` does.
  4. **`MSYS_NO_PATHCONV=1`**: session 403's `checks.sh` is under `runs/` on samueloldlaptop, not in git, so it could not
     be edited here. `site/scripts/check-table-downloads.mjs` now reads a page Git Bash rewrote into a Windows path
     (as `check-review-pages.mjs` does since session 301), so no caller needs the variable.
- **Built and shot**: the gate opened at 14:29 UTC (2.69 s); build exit 0; the downloads check on the explorer 5 of 5;
  before and after shots in `docs/brand/review-416/`. Check-values: 900 of 901 values match Supabase; the one failure is `dcq|ercot|-|active_mw` on `/datacenters?view=grids` (the prefix `/data` also reads `/datacenters` and `/data/licenses`): session 468's key, 298,605.97 MW shown whole, the fault session 461's report lists; every value of the pages this session touched matches.

## What to review

- `docs/brand/review-416/` (its README says what to look at in each shot).
- The commit `293d45fe` (the fixes and the test).

## Checks

Every gate redirected into `runs/chain_021/s416/` or `s417/` (git ignores `runs/`), never piped; the exit read first.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 416"` | 0 | every check passed; the machine was already on duty from the main checkout's mark (not marked again) |
| `tests.test_session416` | 0 | 9 tests OK |
| The old `ticksOf` line run on the test's bounds | n/a | a minus zero (`Object.is(t, -0)` true; "-0" by `toLocaleString`): the test fails on it |
| The 21 test modules that read the changed files (118, 144_page, 161, 207, 215, 237, 282, 303, 317, 318, 328, 331, 332, 333, 351, 368, 370, 410, 412, 473, 78) | 1, then 0 | 243 tests; `test_session161` failed only on the missing generated `site/content/docs.json`; after `node scripts/build-content.mjs`, 161 passes |
| `scripts/db_probe.py` | 1, then 0 | closed at 13:36 (5.01 s) and 14:23 (3.40 s); open at 14:29 (2.69 s) |
| `npm run build` (under the build lock) | 0 | |
| `check-table-downloads.mjs` on `/explore/ercot-peak-premium` | 0 | 5 of 5 |
| check-values, restricted (`/explore/`, `/explorer/`, `/emissions`, `/data`, `/grid`) | 1 | the run passed its 15-minute limit on the slow database; nothing reported |
| check-values, restricted to the five pages touched, limit 40 minutes | 1 | 900 of 901 values match Supabase; the one failure is `dcq|ercot|-|active_mw` on `/datacenters?view=grids` (the prefix `/data` also reads `/datacenters` and `/data/licenses`): session 468's key, 298,605.97 MW shown whole, the fault session 461's report lists; every value of the pages this session touched matches |
| Shots before (production) and after (the local build), 1280 and 390 | 0 | 16 |

Impeccable is not installed on this laptop; it was not run.

## Decisions made without you

1. **The chain runs on portable-laptop** (written for samueloldlaptop) by the owner's instruction to run what the queue
   prints; its branches start from `wip/461-combined` (chain 019's prepared, unlanded combined branch) so that one
   landing takes both chains.
2. **No landing**: this machine's permission check refused an agent's landing earlier tonight; the landing's commands
   are under "To finish".
3. **Fault 4 is fixed in the check, not in the script**: `checks.sh` is not in git; the check now takes both spellings,
   so any caller is right without the variable.
4. **`/data`'s fix is the page's markup, not tokens.css**: the brand's rule (a first `th` stays in place) is right for
   tables whose rows are headed; `/data`'s rows were not. A row header is also the table's semantics.
5. **TimeChart's own y ticks took the same `|| 0`** as the shared chart's: the same fault was possible there.
6. **The explorer's default view does not show "-0"** on production at 1280 (its bounds start at -50); the fault is in
   the function, and the test runs the case.

## For Samuel's ruling

- None new.

## To finish

- Land `wip/416-417-charts` after `wip/461-combined` (or with it, as one): freeze status; merge origin/main; the suite;
  the build; check-values in full (the ten held floors aside, as the chain's rule says); snapshots before and after;
  the push to `task/`; the comparison. A person or a machine allowed to land runs it.
- On samueloldlaptop, `runs/chain_oct21/s403/checks.sh` may drop its `MSYS_NO_PATHCONV=1` need once this lands; it
  does no harm to keep it.

## Files

- `site/components/svgchart.tsx`, `site/components/TimeChart.tsx` (the zero tick), `site/components/grid/Emissions.tsx`,
  `site/app/data/page.tsx`, `docs/brand/review-410/shot-410.mjs`, `site/scripts/check-table-downloads.mjs`.
- `tests/test_session416.py`, `docs/brand/review-416/` (README and 16 shots), this report.
- Not in git: `runs/chain_021/s416/` (the probe script and its four captures, the shot script and list, outputs).
