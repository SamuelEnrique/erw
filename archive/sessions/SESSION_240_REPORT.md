# Session 240 report: top blocks on /board and /datacenters, on the brand

13 October 2026, unattended, one session of the overnight chain of 12 to 13 October, on the old laptop (`samueloldlaptop`, a code machine). Worktree `erw-190`, branch `wip/240-top-blocks`, from `bba5d091`. No table was written, no model was called, nothing was pushed.

## Read these first

- **/board has a top block of twelve numbers**, above everything else: for each, its value, unit and date, its move over a day and over a week (signed, with an arrow, in the tokens' up and down colors) and its last 30 points. Each tile is a row of the wall, read from the same file (`site/data/board.json`) by the same code (`fmt`, `signed`, `sparkOf`), so the tile and the row cannot disagree; `check-board.mjs` now compares each tile with the file and with its own row.
- **The twelve are one list in one place**: `TOP_TWELVE` in `site/lib/board.ts`. Change a line there and the block follows. The table below says which and why.
- **None of the twelve goes dark on 20 October, and none is stale or paused.** No row of ISO-NE, NYISO, MISO or PJM is in the list, and a test holds the list to that (`TOP_NEVER`, `scripts/test-board.mjs`, `tests/test_session240.py`). All twelve are daily and dated within a week of the file's build.
- **The wall is folded by group, the first open.** 18 groups (the 17 of the file and "The week, by hub"). "Power, by hub and zone" is open as the page opens; each closed group keeps its title, its row count and its first number in view. Every row is still in the page, open or closed (211 rows in the HTML as the page opens; `check-board.mjs` holds every group's row count and every row to the file), the workbench is as it was, and "Open every group" opens all at once.
- **/datacenters has a top block of three numbers**: facilities held (380), megawatts stated (18,347 MW, with what the sum counts and its split by status as the table has it), and facilities first reported this week (10, for 7 to 13 October). Each carries its check key.
- **What changed this week is only partly held, and the page says so.** The table is rebuilt whole each day: `status_date` is empty on all 380 rows, `vintage` is the build day on all of them, and no earlier status or MW is kept. So a change of status or of megawatts is "not held". The one date a facility carries is its first story's (103 of 380, the ones found in the news); the page lists the facilities whose first story is dated in the seven days to today.
- **The list is grouped by operator**, in one table so the columns line up: 52 groups, each head with the operator, its facilities and the megawatts the page's sums count for it, largest first. The first group is open; a filter opens every group that has a row left. All 380 rows are in the page, the six filters and the map link stay.
- **Both pages are on the brand** (`<Brand>`, the shared components, the tokens). Two generic rules were added to `site/app/tokens.css` and four shared components to `site/components/tool/ToolPage.tsx` (below). **The battery page did not move**: its 47 checked numbers are identical to session 211's (`diff` 0 lines) and its height at 1280 px is 5016.
- **Not met in full: "no spacing in the pages' own files".** No color literal and no font is left in the two pages' files (the board's two `#fff` became `var(--color-surface)`, its 9, 10 and 11 px type became the brand's 12). The Tailwind spacing classes of the wall's dense table, of the workbench and of the datacenter rows are as they were: the task keeps the wall "as it is", and rewriting 760 lines of table markup onto shared components was not done. `Workbench.tsx` still holds five grey literals for the prior-years chart (line 96).
- **`check-board-v4.mjs` does not pass (4 of 10).** It reads `/board/v4`, which has redirected to `/board` since session 132; its keys (`ercot:HB_HUBAVG|da|last`) are not on `/board`, before or after this session. It was not run on a build of the base commit, so "it failed the same way before" is read from the script and the redirect, not measured.
- **Two things are not done: the "before" screenshots, and a build of the last commit** (one sort line). Both under "To finish".
- **One test of the branch is red on a file this session did not touch**: `tests/test_session215.py`, `test_the_check_prefixes_num_knows_are_the_ones_the_pages_write`, "check prefixes Num does not know: ['cap']". The prefix is written by `site/app/cost-of-power/seller/page.tsx` (session 235).

## The twelve

| # | Series (the row's id) | What it is | Table | Why |
|---|---|---|---|---|
| 1 | `ercot-hb-hubavg-da` | ERCOT Hub average, day-ahead, USD/MWh | `ercot_all_hub_prices_history`, `iso_hub_prices_history` and the rolling hub tables | The most traded hub of the grid where AI load is growing fastest; public after 20 October |
| 2 | `ercot-hb-hubavg-rt` | ERCOT Hub average, real time, USD/MWh | the same | Real time against day-ahead is the first spread a power trader reads |
| 3 | `caiso-th-sp15-gen-apnd-da` | CAISO SP15, day-ahead, USD/MWh | `iso_hub_prices_history` (CAISO's rows) | The West's benchmark, the solar-heavy shape; public after 20 October |
| 4 | `spp-sppnorth-hub-da` | SPP North hub, day-ahead, USD/MWh | `iso_hub_prices_history` (SPP's rows) | The wind belt, the third grid whose own prices stay public |
| 5 | `eia-henry-hub-spot` | Henry Hub natural gas, spot, USD/MMBtu | EIA's daily spot prices | Gas sets the power price most hours |
| 6 | `ercot-hb-hubavg-spark` | ERCOT spark spread, indicative, USD/MWh | row 1 less 7 MMBtu/MWh times row 5 (the board's formula) | Power against gas in one number: a gas plant's margin |
| 7 | `eia-wti-cushing-spot` | WTI crude, Cushing, spot, USD/bbl | EIA's daily spot prices | The US crude benchmark |
| 8 | `eia-brent-spot` | Brent crude, spot, USD/bbl | EIA's daily spot prices | The world's crude benchmark |
| 9 | `eia-eer-epmru-pf4-y35ny-dpg-spot` | Gasoline, New York Harbor, spot, USD/gal | EIA's daily spot prices | The largest product |
| 10 | `eia-eer-epd2dxl0-pf4-y35ny-dpg-spot` | Diesel (ULSD), New York Harbor, spot, USD/gal | EIA's daily spot prices | The distillate benchmark |
| 11 | `erw-crack-321-gulf-coast` | 3-2-1 crack spread, Gulf Coast, USD/bbl | the board's formula over EIA's Gulf Coast gasoline and diesel and WTI | Products against crude in one number: a refiner's margin |
| 12 | `fred-dgs10` | US Treasury yield, 10-year, percent | `fred_treasury_yields` (release H.15) | The one macro line: the rate every project is financed against |

Left out on purpose: NYISO New York City and ISO-NE Internal hub (their own prices show "license needed" from 20 October), MISO (paused) and PJM (licensed); every monthly and weekly series (no move over a day). Close calls, one line each to swap: the 2-year yield (`fred-dgs2`), ERCOT's implied heat rate (`ercot-hb-hubavg-heat`), Brent minus WTI (`erw-brent-minus-wti`).

## What was built

- `site/lib/board.ts`: `TOP_TWELVE`, `TOP_NEVER`, `topRows`, `leadRow` (a group's first row with a value, for a closed group's head).
- `site/components/board/BoardView.tsx`: `TopTwelve` above the strip the page had (the strip of eight stays, under it); each group and the week's table inside a fold; a "Jump to" link opens the group it goes to, and so does an address with a group's id (`/board#gas`); "Open every group". The filters of a group moved from its title line into its body (a button inside a fold's title would toggle the fold). `site/app/board/page.tsx`: `<Brand>`.
- `site/app/datacenters/page.tsx`, `Body.tsx`, `DatacentersTable.tsx`: `<Brand>`, `ToolPage`, `ToolHeader`, a `HeadlineRow` of three `HeadlineNumber`s, a section "What changed this week" (a `ToolTable` of the facilities first reported this week and the "not held" sentence), the two bars as they were, then the scope and method paragraphs (they stood above the numbers), then the list by operator.
- Shared, additive, in `site/components/tool/ToolPage.tsx`: `NumberTile` and `NumberTileGrid` (a number with its unit, time, moves and trend), `GroupFold` (a section that opens and closes, its title and one line in view when closed), `FoldRows` (a group of rows inside one table that opens and closes). No existing component was changed.
- `site/app/tokens.css`, additive, two generic rules at the end, scoped to `.brand-a`: the plus and minus before a `GroupFold`'s title, and a dense table (`table[data-dense]`: figures at 12 px, the row's first figure at 14). Neither names a page; neither matches the battery page.
- `site/scripts/check-values.mjs`, additive, in the `datacenters` block: four keys (`status_mw`, `first_week`, `n_first_story`, `operator_count`) and `status_mw` in the whole-MW rule.
- `site/scripts/check-board.mjs`: five checks added (the top block against the file and the wall, its place above the wall, the folds, the brand's wrapper, a tile's words) and one step moved: Henry Hub's row is now in a closed group, so the check opens "Natural gas" by its title before it hovers the trend line. `site/scripts/test-board.mjs`: one test of the list.
- `tests/test_session240.py`: 14 tests.

## What to review

1. The screenshots: `docs/brand/review-240/` (`README.md` says what to look at).
2. After the landing, in the internal view (https://erw-flame.vercel.app/internal/open first):
   - https://erw-flame.vercel.app/board : the twelve tiles; click a tile's name (the workbench opens on that row); click "Natural gas" (the group opens); "Open every group".
   - https://erw-flame.vercel.app/board#crude : the address opens the crude group.
   - https://erw-flame.vercel.app/datacenters : the three numbers, "What changed this week", then the list; choose a State in the filter (every group with a row opens).

## Checks, with exit codes

Run under the build mutex on the branch at `929b5917` with the board check as it is committed (cycle 1, 08:39 to 08:46 UTC). Outputs: `runs/session240/` in the main copy.

| Check | Exit | Result |
|---|---|---|
| `npx tsc --noEmit` | 0 | clean |
| `npm run build` | 0 | built twice; the log holds a `statement timeout` on a read of `series` (2 the first time, 1 the second): not a read of these two pages (/board reads the site file, /datacenters reads `entities`) |
| `check-values` on /board and /datacenters, run 1 | 0 | 82 of 82 values match Supabase |
| `check-values`, run 2 | 0 | 82 of 82. All 82 are /datacenters: /board carries no `data-check`, its numbers are marked `data-n` and compared with `data/board.json` by `check-board.mjs` |
| `check-board.mjs` | 0 | 36 of 36 (the first run, 35 of 36: the new fold check measured a height where the browser keeps one for a closed fold; it now asks `checkVisibility()`) |
| `check-datacenters.mjs` | 0 | all 11 passed, unchanged script |
| `check-routes.mjs` | 0 | 0 failed |
| `check-board-v4.mjs` | 1 | 4 of 10: it reads `/board/v4`, a redirect to `/board` since session 132, so none of its keys is on the page it reads. Not run on the base commit (see "To finish") |
| `scripts/test-board.mjs` | 0 | 11 tests, one new |
| The battery page (`runs/session208/capture.mjs`, 1280) | 0 | `diff` of its numbers with session 211: 0 lines; height 5016 |
| `tests/test_session240.py` | 0 | 14 tests |
| The modules that read a changed file, three at a time: 132, 168_board, 203; 235, 236, 67; 115_page, 138, 149_checks; 178, 179, 186; 194, 44, 54; 55, 58, 90; 104, 106, 166_datacenters | 0 each | no pin moved |
| 177, 215, 114_part2 | 1 | one failure, `test_session215` on the seller page's `cap` prefix (not this session's file) |
| Port 3241 after the checks | | free; `EADDRINUSE` 0 in the server log |
| Em dash in the changed files | | none (`tests/test_session240.py` holds it) |

**Not built: the last commit, `f7ccf7f5`.** It changes one line of `DatacentersTable.tsx` (the sort that puts the rows with no operator stated last) and the board check's two `checkVisibility()` calls. The check was run as committed (36 of 36); the sort line was not type-checked or built: the mutex was held by the orchestrator (08:17 to 08:39 and 08:46 to 09:04), then by sessions 239 and 241b, and this session stopped waiting at 09:19 UTC, past its hour.

## Decisions made without you

- **The first group open, the others closed** (the task allowed either). A reader who scrolls past the twelve meets rows at once; each closed group still shows its first number.
- **The strip of eight the page had stays**, under the twelve (lowest and highest grid, the two range extremes are not among the twelve; nothing the board shows is dropped). Four of its cells repeat a tile.
- **The board's small type went from 9, 10 and 11 px to 12** (`text-xs`), in `BoardView.tsx` and `Workbench.tsx`: the brand has six sizes and 12 is its smallest. The wall is a little wider for it and scrolls inside its frame as it did.
- **"This week" is the seven UTC days that end on the day the page is drawn** (the page is redrawn hourly). The first day is in the number's check key (`datacenters|first_week|2026-10-07`), so the check counts the same days whenever it runs.
- **The megawatts by status are the table's own words**: planned, operating, under construction, and "status not stated" where the status is blank (8,799 of the 18,347 MW). Nothing is assigned a status.
- **The rows with no operator stated are the last group**, whatever their megawatts (27 rows, 13,400 MW, which would otherwise be first): they are not an operator.
- **One table for the list, not one a group**, so the columns line up down the page; a closed group's rows are hidden, not removed.
- **A group head's megawatts follow the page's rule for sums** (a named US state, not cancelled, MW stated), and its count is every row of the operator, as the list shows them. With a filter on, the heads count the rows shown and carry no check key.
- **The scope and method paragraphs moved below the top block**; their words are unchanged.

## For Samuel's ruling

1. The twelve: the list above, and the three close calls.
2. From 20 October `datacenter_facilities` is "license needed" as a whole (its publishers include news outlets and operators, `site/data/license_status.json`), so /datacenters, top block included, will show those words that day unless a permission is recorded.
3. The words this session put on the pages: "Facilities held", "Megawatts stated", "First reported this week", "What changed this week", the "Not held" sentence, "Operator not stated", "Open every group", "Open every operator", and the line under the board's "Jump to".
4. Whether the strip of eight should go now that the twelve stand above it.
5. Whether the board should keep a visitor's open groups in the address, as it keeps a row and the filters (today a reload returns to the first group open).

## Not done, not verified

- The whole python suite was not run (the orchestrator runs it on a clean copy); the modules that read a file this session changed were, three at a time: see the checks.
- No accessibility or design tool was run on the two pages (time). The fold is a native `details`; the list's group head is a `button` with `aria-expanded`.
- The spacing classes and the five greys named under "Read these first".
- `check-values` was a restricted run on the two pages, not the gate of a landing.

## To finish

Under the build mutex, from the main copy, one command (about eight minutes; it refuses to start on a worktree that is not clean):

```bash
bash /c/Users/lossa/Documents/erw/runs/session240/cycle2.sh
```

It checks out the base commit `bba5d091` in the worktree `erw-190`, builds it, takes the four "before" screenshots into `runs/session240/shots/` and runs `check-board-v4.mjs` on it; then checks out `wip/240-top-blocks`, builds it and runs `check-values` twice, `check-datacenters`, `check-board`, `check-board-v4`, `check-routes` and the eight "after" screenshots, each with its exit code, and stops the server on port 3241. Then copy `runs/session240/shots/*.png` to `docs/brand/review-240/` and commit. If only the build matters: `cd site && npx tsc --noEmit; echo "exit=$?"` on the branch is enough to cover the one unbuilt line.

The four "after" screenshots of /datacenters in the folder were taken before the last commit: in them "Operator not stated" (27 rows, 13,400 MW) is the first group; on the branch it is the last and the largest named operator's group is first.

## The landing

filled by the orchestrator
