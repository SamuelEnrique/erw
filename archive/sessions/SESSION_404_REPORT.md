# Session 404 report: the demand growth explorer

21 October 2026, from about 05:20 to 06:15 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-404` on `wip/404-s` (cut from `wip/403-s`). The chain `queue/done/015-day-20-october-code-pm.md`, "Session 404": platform tool 5, the second signature explorer. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **The page is `/explore/demand-growth`**, in review and not in the menu (`site/lib/release.ts`; no line in `site/lib/pages.ts`). Growth since 2019 by grid and by window of the year, from `eia930_demand_growth` as it stands in the live set. Filters in the address: `grid` (the slugs of `/demand`: `ercot`, `caiso`, `pjm`, `miso`, `spp`, `nyiso`, `isone`, `us48`) and `window` (`avg` the whole year's average hour, the default; `peak` its highest hour; `ytd` the year so far; `m01` to `m12` a month; `h00` to `h23` a local hour of the day). A value the table does not hold falls back to the default (ERCOT, `avg`) with one line saying so.
- **"The thesis chart"**: no document of the ERW names one for demand growth (the thesis charts named in `docs/platform-tools.md` and `docs/OVERVIEW.md` are the ERCOT peak premium's; `docs/methods/thesis.md` is the Thesis Builder; the method note of `eia930_demand_growth` names no chart). As the chain allowed, the page draws the table's own headline figure: growth since 2019 for every grid in the window chosen, largest first, with the site's bar chart (`components/tool/GroupedBars.tsx`). The chart is titled "The headline chart", not "the thesis chart".
- **The production build worked tonight** (six builds, 05:40 to 05:59 UTC, each exit 0: the database answered), so the page was checked on `next start`: **check-values 202 of 202** on its five views, twice; the floor was computed and is **not committed** (below); shots at 1280 and 390 committed in `docs/brand/review-404/`.
- **The table is held for review in the live set** (`warehouse/supabase/live_set.yaml`, `review_hold`), so the site's public catalogue does not list it and session 403's `Freshness` would have said "not in the site's catalogue". A reader of the catalogue's own row, `site/lib/explore/heldfresh.ts`, and a component, `site/components/explore/HeldFreshness.tsx`, were **added beside** the shared parts; `Explore.tsx`, `lib/explore/index.ts` and `fresh.ts` are unchanged (a test checks it), so session 405's branch merges cleanly. `iso_queue_statistics`, session 405's table, is held for review too: 405 may use the same two files.
- **Stale since 5 October 2026, stated on the page from the data**: the freshness line reads the catalogue's `last_run` (5 October 2026 02:07 UTC) and `ts_max` (the newest period, 2026), and the end of the year-to-date window (September 2026) from the table's header. No date is written by hand (a test checks the sources).

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first), once landed:

1. https://erw-flame.vercel.app/explore/demand-growth : ERCOT, the whole year's average hour. Growth since 2019 +27.22 percent (43,798 MW in 2019, 55,717 MW in 2025); the year so far +33.10 percent (2026, January to September). The headline chart: ERCOT +27.22, SPP +11.14, Lower 48 +7.03, PJM +5.37, CAISO +4.45, MISO +2.20, ISO-NE -2.54, NYISO -2.73. Seen on `next start`, 21 October about 05:55 UTC.
2. https://erw-flame.vercel.app/explore/demand-growth?grid=us48&window=peak : the Lower 48 has no peak; one line says why (the method note's reason) and the other grids' peaks are drawn (ERCOT +12.16 first).
3. https://erw-flame.vercel.app/explore/demand-growth?grid=pjm&window=ytd : the year so far, PJM +8.25 percent (93,181 MW to 100,868 MW, January to September).
4. https://erw-flame.vercel.app/explore/demand-growth?grid=caiso&window=m08 : August, CAISO +2.66 percent, +803 MW; the change is a row of the last whole year only.
5. https://erw-flame.vercel.app/explore/demand-growth?grid=ercot&window=h17 : 17:00 local, ERCOT +26.67 percent, +13,354 MW.
6. https://erw-flame.vercel.app/explore/demand-growth?grid=bogus&window=x : the default, with the line "The address asked for a grid and a window the table does not hold".

## What was done

- `site/app/explore/demand-growth/page.tsx` (new): one read of the table (the window's variables for every area, a few hundred rows) and the header. It draws three headline numbers, the headline chart (growth by grid), every grid's 2019 and latest demand and growth (and the change in MW for a month or an hour), the grid's growth by window year by year and its demand in the window by year (both `GroupedBars`), the grid's rows year by year (with the year on the year before and the hours used, for the whole-year window), a line relating it to `/demand`, the method link, the downloads line and the source line, in session 403's `ExploreFrame` and `FilterForm`. Every figure is one row with key `series|eia930_demand_growth|<entity>|<variable>|<year>`; the page computes none; a sign is written outside the number.
- `site/lib/explore/demandgrowth.ts` (new): the explorer's constants (grids, the 39 windows, the variables read) and helpers (the years a view reads at, the end of the year-to-date window from the header).
- `site/lib/explore/heldfresh.ts`, `site/components/explore/HeldFreshness.tsx` (new): the freshness of a table held for review, in the shared `Freshness`'s form.
- `site/components/tool/GroupedBars.tsx`: a tick at minus zero is written "0" (it read "-0" on the headline chart). No figure moves; `/cost-of-power/seller`, the other page drawing it, was shot after the change and its revenue chart is as before.
- `site/lib/release.ts`: `/explore/demand-growth` in review (its line beside `/demand`'s, not after 403's, so 405's line does not touch it). `site/scripts/check-values.mjs`: five views in the list (beside `/demand?view=consumption`) and the table's MW keys read as whole numbers (one alternative added to the `whole` pattern). `site/scripts/check-routes.mjs`: three views (beside `/demand`).
- `docs/methods/demand_growth.md`: a section "The explorer (session 404, 21 October 2026)": the filters and the rows each reads, the headline chart and why it is not called the thesis chart, where the dates come from, and the downloads line.
- `tests/test_session404.py` (new, 12 tests).

## Checks

Every gate redirected to a file under `runs/chain_oct21/s404/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `duty.py beat` before each build | 0 (six times) | |
| `npm ci` in the worktree | 0 | |
| `npm run build`, six builds (05:40 to 05:59 UTC) | 0 each | no statement timeout tonight in these builds |
| `npx tsc --noEmit` after each build | 0 each | |
| `npx eslint app/explore/demand-growth components/explore lib/explore` | 1, then 0 | the first run found the figure writer declared as a component inside the render (`react-hooks/static-components`, 8 errors); it is a plain function now; 0 on the five later runs, and on `GroupedBars.tsx` |
| `check-values`, `CHECK_VALUES_PAGES=/explore/demand-growth`, on `next start` at 3404, twice after the last build | 0, 0 | 202 of 202 values match Supabase on the five views (also 0, 0 after builds 3 and 4) |
| `check-values` with `CHECK_VALUES_WRITE_FLOOR=1`, restricted | 0 | 202 of 202; floors of 10 for the five views; the file was restored, not committed (below) |
| `check-table-downloads.mjs /explore/demand-growth` | 0 once, 127 twice | "1 of 1 checks pass" every time (the line says the table is not in the live set); the 127 is node's own crash at exit on Windows (`Assertion failed: !(handle->flags & UV_HANDLE_CLOSING)`), after the result |
| `check-routes.mjs` (whole list), first run | 0 | the three views 200, in review as a visitor; `?grid=us48&window=peak` carried one "no data" (the empty peak chart), replaced by a line before the last build |
| `check-routes.mjs`, second run | 1 | the three views 200, 0 "no data"; the one failure is `/grid` with 3 "no data" blocks (the database's statement timeouts on that page's reads; it passed in the first run); not this session's page |
| The page through the internal door, six addresses | 0 | 200 each; 63, 22, 61, 46, 45 and 63 keys; no "undefined" or "NaN"; the visitor sees the in-review page with no figure |
| `tests.test_session404` | 0 | 12 tests, 1 skipped in the worktree (the table's CSV is not there); the skipped one passed against the main copy's `warehouse/output/eia930_demand_growth.csv` (every window a row of every grid) |
| Tests near the change: 403, 97, 107, 145, 152, 162, 235, 268, 331 | 0 | 125 tests OK, 6 skipped |
| Whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 4,807 tests, 254 skipped, one failure: `test_session156` (the ask fixtures), foreseen by the chain's rules |

Shots, looked at before described: `docs/brand/review-404/01` to `05` (the five views, 1280 and 390) and `06_seller` (1280 and 390). At 1280 the page reads top to bottom as in "What to review". At 390 the bar charts keep their width and scroll inside their frames (the brand's rule for a chart whose svg is the figure's child), and the every-grid table scrolls its last column, as the site's tables do.

## Decisions made without you

- **The headline chart stands for the thesis chart**, since no document names one for demand growth: growth since 2019 by grid, in the window chosen. If a thesis chart is named later, the page's first chart is the place to change.
- **Windows**: the whole year's average and highest hour, the year so far, a month, a local hour: every growth figure the table holds by area. The month-and-hour cells (`_mMM_hHH`) are not offered; `/demand` draws them as its map.
- **Bars, not lines, for the years**: the shared line chart's year axis labels ticks between years with the year (it read "2020, 2020, 2021, 2023, 2024, 2024, 2026"), so the two charts along the years use the bar chart, whose groups are the years. The line chart is not changed (other pages read it).
- **Freshness beside the shared parts**, in two new files, so that 403's exports are untouched and 405 merges cleanly.
- **The floor of check-values is not committed**: the five lines sort between `/events/uri-2021` and `/grid`, where session 403's and 405's floors also go, so three branches would conflict on adjacent lines. The run that writes them is under "To finish"; the file it wrote is kept at `runs/chain_oct21/s404/check-values-floor.with404.json`.
- **The downloads line says the table is not in the live set**, as `/demand`'s does: the download route serves only `in_live_set` "yes".
- **`GroupedBars`' minus-zero tick** fixed in the shared component (one expression), since the headline chart is the first place it showed.

## For Samuel's ruling

- `eia930_demand_growth` is held for review in the live set, so its two pages offer no CSV: (a) keep it held until `/demand` opens; (b) take it off `review_hold` now (the home page's counts of public tables and rows would move by one table and its rows).
- `eia930_demand_growth` has not been rebuilt since 5 October 2026 (the page says so): the data machine's run of `warehouse/derived/demand_growth.py`.
- Demand growth is drawn at two addresses now, `/demand` (with the month-and-hour map, the ranking, the weather view and consumption) and `/explore/demand-growth`: (a) keep both; (b) link `/demand` to the explorer; (c) fold one into the other.
- The shared line chart (`components/TimeChart.tsx`, `x="year"`) repeats a year on its axis when it holds few years (seen on this page before it moved to bars; 403's charts along the years use it): a fix there touches every page that draws years.

## To finish

At the landing, after merging 403, 404 and 405, in the copy that is built (under the build mutex, `scripts/duty.py beat` first):

```bash
cd site && npm run build > ../runs/landing_build.out 2>&1; echo "build exit=$?"
npx next start -p 3404        # in the background
MSYS_NO_PATHCONV=1 CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/explore/ node scripts/check-values.mjs http://localhost:3404; echo "exit=$?"   # the floors of every explorer's views at once
git add scripts/check-values-floor.json && git commit -m "The explorers' check-values floors"
# then stop the process listening on the port, remove owner.txt and rmdir the lock
```

The landing's full `check-values` and `check-routes` then read the page with the rest.

## Files

- `site/app/explore/demand-growth/page.tsx`, `site/lib/explore/demandgrowth.ts`, `site/lib/explore/heldfresh.ts`, `site/components/explore/HeldFreshness.tsx` (new)
- `site/components/tool/GroupedBars.tsx`, `site/lib/release.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-routes.mjs`, `docs/methods/demand_growth.md`
- `tests/test_session404.py` (new), `docs/brand/review-404/` (12 shots), this report
- Run outputs (not in git): `C:\Users\lossa\Documents\erw\runs\chain_oct21\s404\`

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The floors of every explorer's views:** the same restricted run as session 403's (`CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/explore/`, exit 0, 867 of 867) wrote the five demand-growth views' floors, each 10 (`/explore/demand-growth` and `?grid=caiso&window=m08`, `?grid=ercot&window=h17`, `?grid=pjm&window=ytd`, `?grid=us48&window=peak`). Commit `16261335`.
- The shots were already committed by this session (`docs/brand/review-404/`); none taken again.
- The demand-growth note's figures of a month or an hour were named by no note when session 409's script read the site (six MISSING); `docs/methods/demand_growth.md` gained the section "The figures on the page and their keys" (commit `fc1496c4`, session 409's section below says how).
- `tests.test_session404`: exit 0 within the ten sessions' modules.
