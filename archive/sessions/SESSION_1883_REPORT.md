# Session 1883: the price board read on the real board.json of 12 November, and its fixes (12 November 2026)

Energy Research Warehouse (ERW). Session 1883, samueloldlaptop, unattended, Opus 5.5. The read was committed to main (`330158fde`); the fixes are on `wip/1883-board`, from `wip/1882-periodicals` at `67ba19a4f`. No freeze checked or needed: nothing was pushed to main or a `task/` branch.

## What it did

- Read `/board` on a build served at `localhost:3883` holding `site/data/board.json` as the data machine's run of 12 November 2026 built it (`2026-11-12T17:48:19Z`, commit `72e8958c7`), in the internal view at 1280 and 390, under four filter addresses that between them show every row (1,313 of 1,313). Scripts and outputs in `runs/s1883/` (`agent.md`).
- `node --import ./scripts/alias-register.mjs scripts/check-board.mjs http://localhost:3883`: exit 0, 48 of 48 checks.
- Every figure of every row against the file by the page's own functions (`fmt`, `signed`, `shownMove`, `closeAge`): 19,454 marked cells, no difference. Chain 165's 96 rows: every row with a value names its interval or formula and its source on hover; 74 trend lines' tooltips read at both ends, none wrong; the 22 placeholders print their status words with no digit.
- The keyboard at 1280 and 390, every group open: 468 stops a pass, each with the 2 px focus ring; all 25 scrolling tables reachable.
- **The rows added to `docs/reviews/board-audit-2026-11-06.md`, section 10:** 41 to 51: 5 `open` (site code), 5 `data machine`, 1 `not a fault`.
  - 41: at 390 px the page scrolls sideways (521 px; 711 with every filter at "all"): the held line's `sr-only` words are placed outside their table's scrolling box.
  - 42: a closed group's head shows its first row's figure with no stale mark (12 of 23 heads).
  - 43: the 30-day low to high cell is empty on every weekly, monthly and quarterly row; the column collapses and its header wraps to five lines in 13 groups.
  - 44: under a filter leaving the power table with placeholders only, its region is named "Power, by hub and zone, 2 of 2".
  - 45: `check-board.mjs`'s usage line names `alias-loader.mjs`, which stops at once.
  - 46 to 50, for the data machine: every public power row stale on the day of the build (hubs to 6 November, real time to 4 November, SPP to 31 October); gas in storage to 16 October and the US trade rows to July; no 2026 4CP interval held; four ERCOT load zones not held in real time; heating oil and propane, the low-carbon fuel credit and gas by sector behind.
  - 51: MISO's capacity placeholder carries the pause's date in its hover: not a fault.
- Rows 24 and 25 (CFTC positions, the STEO): no ruling in `docs/state/rulings_*.md`; they stay for a ruling.

## Decisions made without you

- Row 42: the head keeps its first row and prints "stale" beside the date, the first of the audit's two answers. Taking the first row that is not stale would still leave power's head stale on this build, and it would change the row `check-board.mjs`'s fold check reads.
- Row 44: the region inside its namesake is named "Power, by hub and zone, table", not the bare group name. Two regions with the same name, one inside the other, are what AccessLint's landmark-unique rule flags.

## Fixes

On `wip/1883-board`, commit `ebdb3fcd` (code and tests), then the audit's states and this report.

| Row | Fix | File |
|---:|---|---|
| 41 | The table's scrolling box is `relative overflow-x-auto`: the box is now the containing block of the absolutely placed `sr-only` span, so the box clips it and the page stays its own width. No visible change | `site/components/board/BoardView.tsx` |
| 42 | The head prints a "stale" badge beside its date, with the close's age on hover (`closeAge(leadRow(...))`, `data-lead-stale`), in the row's own style | `site/components/board/BoardView.tsx` |
| 43 | A row with no `lo30` says its step ("weekly", "monthly", "quarterly", hover "A monthly series has no 30-day low and high.", `data-lo30-step`); a daily one says "not held yet" | `site/components/board/BoardView.tsx` |
| 44 | `uniqueNames` sets apart a region it named that sits inside a container of the same name: it is named "<name>, table" ("code" for a `pre`) and not counted with the container; two inside one container are "<name>, table, 1 of 2". Regions side by side, and elements without `contains()`, count as before | `site/components/ScrollRegions.tsx` (shared) |
| 45 | The usage line names `node --import ./scripts/alias-register.mjs scripts/check-board.mjs [base-url]` | `site/scripts/check-board.mjs` |

Tests:

- `tests/test_board_1883.py`, new, 11 tests (one class a row; the node parts run `lib/board.ts` and a transpiled `ScrollRegions.tsx` on stand-in elements): exit 0, 11 passed, none skipped.
- Every `tests/test_board_*.py` with the tests that read the touched files (`test_session583`, `412`, `1715`, `428`, `1193`, `132`, `240`, `1116`, `1118`, `168_board`, `281`, `319`, `328`, `473`, `502`): exit 1, 218 passed, 1 failed. The failure is `test_session1116.py::test_the_node_tests`: `scripts/test-board-1116.mjs` check 5 reads the committed `site/data/board.json` and finds the top twelve's `ercot-hb-hubavg-da` stale. That is audit row 46's data, not this change; the script imports only `lib/board.ts` and `lib/license.ts`, which this session did not touch.
- `npx tsc --noEmit` in `site/` (build lock held as `s1883`, then released): exit 2. All 15 errors are about the generated `PageProps`, `LayoutProps` and `@/content/*.json` of a tree that has not been built; none in the files changed here.

Not done in this session: no build was run, so the 390 width (row 41) and the height of the 30-day header (row 43) were not measured again in a browser. A session that builds the branch should read `runs/s1883/wide2.mjs` and `costs.mjs` again on it.

## To finish

- Build `wip/1883-board` and run `runs/s1883/wide2.mjs` and `runs/s1883/costs.mjs` on it: the page should be 390 wide with the groups open, and no group's header 84 px tall.
- Land the branch through a `task/` branch with rule 8's before and after snapshot.
