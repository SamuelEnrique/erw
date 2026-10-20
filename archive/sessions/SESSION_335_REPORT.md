# Session 335 report: /learn/bill, finished (lighter), and the night note

20 October 2026, from about 10:00 UTC, unattended, on samueloldlaptop (the code machine), the last session of the chain of 19 to 20 October, night (`CHAIN_OCT19_PROMPT.md`). Branch `wip/335-bill-night` in the worktree `erw-296`, from session 334's branch; lands on main as `task/335-bill-night` after session 334. Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **`docs/state/review_2026-10-20_code.md`** is the note for Samuel: three things no one asked for first (three rulings a check wrote into production, a learning page that prints 0 for data it lacks, the download route's fault on the largest tables), then one line a session with its address, the screenshot folders, the decisions made without him and what waits for him, in order of value.
- **`/learn/bill` was near the standard**: every figure of a default bill is a checked number (`bill|` keys), every rate is in the site's file with its tariff passage, and the calculator has its Reset. It lacked a method note of its own and its table to download: both are there now.

## What to review

1. `docs/state/review_2026-10-20_code.md`.
2. https://erw-flame.vercel.app/learn/bill : "Method" under the bills (https://erw-flame.vercel.app/data/methods/bill); the downloads at the foot.
3. `docs/brand/review-335/`.

## What was done

- `docs/methods/bill.md` (new): the five bills and their file, how a default bill and the wholesale share are computed and checked, the calculator, the downloads; linked from the page.
- The page's table, `cost_of_power_monthly`, as CSV, Python and Stata (session 328's shared line).
- The night note.
- Tests: `tests/test_session335.py`.

## Stale tables, for the data machine

None for this page: `cost_of_power_monthly` is rebuilt with the daily run.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session335` and every test that reads a file this session changed (7 modules, 88 tests) | 0 | OK |
| `scripts/precheck.py --what "session 335"` | 0 | |
| `eslint` on the page | 0 | |
| `finish_build.sh 335` (erw-296 at `f67a2099`): build | 0 | no statement timeout |
| `check-values` on `/learn/bill` | 0 | 18 of 18 |
| `check-routes` | 0 | every page |
| `check-table-downloads` on the page, the Python reader run on `ercot_peak_premium_annual` | 0 | 6 of 6 |
| Impeccable `detect --json` on the changed files | 0 | no finding |
| The probe at 390 | 0 | 390 within 390 |
| Shots, 1280 and 390, before and after | 0 | four, `docs/brand/review-335/` |

## Landing of session 334 (recorded here: session 334's report is in that landing's own commit)

- `land_checks.sh s334land 3334 check-thesis.mjs check-table-downloads.mjs` on `task/334-thesis-severance` (origin/main merged): the suite 4,582 tests OK; build 0; `check-routes`, `check-thesis` 34 of 34, `check-table-downloads` passed; `check-values` 6,454 of 6,460, the six of `/learn/problems/know-your-grid` that production fails too.
- Main gained the data machine's sessions 360 and 361 (Research's statistics; card data files only on the site) before the push: merged.
- Freeze status exit 0. Before snapshot `s334-before` at 11:04:31 UTC; pushed at 11:04:40; run 39412389858 succeeded and merged `1b68e090` at 11:14; no new style sheet, so the after snapshot `s334-after` was taken at 11:25:09; production's `/severance?tab=lease` carries `data-downloads="1"`. The comparison: **0 differences on 25 pages**, expected. `wip/334-thesis-severance` deleted.

## Landing

## Decisions made without you

- **The night note puts first what no one asked for** (three faults found, one of them a write to production by a check), then the landings, as the chain prompt orders the rest.
- Questions skipped (Impeccable's playbooks ask them).

## For Samuel's ruling

- Session 293's question stands (the computed rows of the learning pages: kept as figures, or their inputs added to the downloads).

## Files

- New: `docs/methods/bill.md`, `docs/state/review_2026-10-20_code.md`, `tests/test_session335.py`, `docs/brand/review-335/`, this report.
- Changed: `site/app/learn/bill/page.tsx`.
