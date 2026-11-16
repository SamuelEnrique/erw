# Session 7517 (chain 304, part B): the demand growth explorer read as its reader

Energy Research Warehouse (ERW). samueloldlaptop (code role), unattended, 16 November 2026. Tool: `/explore/demand-growth`. Branch `wip/7508-demand-growth`, worktree `erw-7508`, on top of session 7508's done line. Model spend USD 0. Nothing pushed, nothing landed, no table written, no shared explore file edited, no other page's code edited, nothing asked of any publisher.

## At the top

- **California's growth here is the batteries' charging.** EIA's California demand counts the power the grid's batteries take to charge. Where the charging is held (CAISO's own data, from June 2025): June to December 2025, demand +2.81 percent on the same months of 2019, the charging 1,690 MW on average, demand less the charging -3.60 percent, beside -2.28 percent for California's retail sales. January to August 2026: +10.75 percent, 2,114 MW, +2.05 percent, sales -2.90. So the charging closes the gap to sales for 2025 (same sign, 1.3 points apart) and four fifths of 2026's growth, with 5 points left in 2026. The page's figure (+4.45 percent) is unchanged; its decisions now say this in place of "not established here".
- **A second thing in California's base, not established:** EIA's March 2019 is 19,536 MW, 11 percent under the months beside it; March reads +14.05 percent where February reads +4.95. A data request.
- **A figure the page lacked and the table held:** the highest hour of 2026 so far (PJM's record of 162,648 MW, 2 July 2026). The peak window now draws it.
- **The done line is kept** (the coordinator's rule, received mid-session): the note and the replication carry the new figure. As printed: "/explore/demand-growth: 35943 of 35943 slots of text on 315 views equal the replication's (3296 distinct checked figures; 777 of 777 growth figures recomputed from the MW rows)".
- **Not meant:** nothing. Part A's faults row 12 still reads "not established" in its own file (its rows are not reopened); this session's row 5 and the note's new section carry the finding.

## The reader and the five cases

- **The reader:** an AI lab's energy lead sizing a 300 MW site that runs every hour, choosing among ERCOT, PJM and California. Why: the page answers the first question of that shortlist (how fast, and in which hours, each grid has grown), and that reader tests it hardest (the growth in MW, the newest peak, the forecast next). A fund analyst's "load growth is back" is cases 1, 2 and 4 as they stand.
- **1. ERCOT since 2019 and its evening:** +27.22 percent; 17:00 to 21:00 grew 12,096 to 13,354 MW, like every hour of the day (10,314 to 13,428 MW). Answered; one address an hour.
- **2. PJM, the year so far and the summer peak:** +8.34 percent for January to October 2026; peak 160,560 MW in 2025 (+5.41), and since this session 162,648 MW in 2026 (+6.78).
- **3. A 300 MW site:** 2.52 percent of ERCOT's growth of six years, 6.12 of PJM's, 0.93 of the Lower 48's, by the reader's own arithmetic: the page gives no change in MW for the year and takes no input.
- **4. California:** above.
- **5. MISO and SPP:** drawn in full (MISO +2.20 percent, SPP +11.14); every row is EIA's, nothing is MISO's own and nothing is asked of MISO. No row.

## The rows by kind (`docs/reviews/demand-growth-read-2026-11-16.md`, 12 rows)

- `site`, fixed with a test: 5 (rows 3, 4, 5, 9, 10).
- `data machine`: 3 (rows 1, 7, 8).
- `ruling`: 3 (rows 2, 6, 11).
- `browser`: 1 (row 12, four ready rows below).

## What was fixed

- Row 3: the peak window draws one line under its headlines, three rows of the table: "The highest hour of 2026 so far (January to October): 162,648 MW, +6.78 percent on the highest hour of the same months of 2019 (152,315 MW)." Seven grids; none for the Lower 48. `site/lib/explore/demandgrowth.ts` reads the two variables in that window only.
- Row 4: in the year-so-far window, "2019, January to October: 91,744 MW" under the second headline (it read "2019: 91,744 MW"), and the column "2019, January to October, MW" in "Every grid".
- Row 5: the decision "Demand at the grid is not sales to customers" states California's charging with the figures above; the decision on the demand series says California's counts the charging. `replication/demand_growth/california_charging.py` recomputes them from `california_rows.csv` (850 public rows copied unchanged from three tables).
- Rows 9 and 10: a line at the foot says the table holds no forecast and links the All grids tab; its tip says what that tab holds and that its demand growth is the last twelve months over the twelve before (ERCOT +5.21 there, +5.57 here for 2025 on 2024).
- The method note: a new section, "Read as its reader (session 7517, 16 November 2026)": figure 3a, the two pages' growth side by side for seven grids, California's rule and table, the replication's line.
- The replication: `replicate.py` writes the new line and the two changed labels from the note's words; `demand-growth-figures.mjs` reads them from the drawn page; `page_figures.json` and `.csv` written again.

## Tests

Each file in its own process, one at a time, `ERW_SPEND_CAP_USD=0`, output in `runs/s7517/tests/`, exit code read.

- `tests/test_session7517_demand_growth_read.py`: 11, pass (the page drawn on 120 views; each fix on the drawn HTML; the decisions' words against the California recomputation; the replication beside the page; the note and the committed figures; the shared files untouched; no dash).
- `tests/test_session7508_demand_growth.py`: 13, pass.
- `test_session404` 12 (1 skipped), `test_session152` 17, `test_session2201` 6, `test_session2203` 6, `test_session2204` 5, `test_session1496` 6, `test_session281` 6, `test_session2877` 6, `test_session331` 8, `test_session472` 4, `test_session538` 14, `test_session97` 12 (4 skipped), `test_session2200` 8, `test_session706` 4 (1 skipped): all pass. (`test_session404` failed once on a year written in a comment of mine; the comment was changed.)
- Type check of the changed page files alone (`tsc`, a scratch config, removed): exit 0.
- Not run: `check-values.mjs`, `check-routes.mjs`, `check-methods.mjs` (they need a running site). The new keys are on the peak views of the seven grids; the peak view the checker reads is the Lower 48's, which draws none.

## What to review

1. `https://erw-flame.vercel.app/explore/demand-growth?grid=pjm&window=peak` (in review): under the three headlines, "The highest hour of 2026 so far (January to October): 162,648 MW, +6.78 percent on the highest hour of the same months of 2019 (152,315 MW)."
2. `https://erw-flame.vercel.app/explore/demand-growth?grid=pjm&window=ytd`: under the second headline, "2019, January to October: 91,744 MW"; the table "Every grid" headed "2019, January to October, MW".
3. `https://erw-flame.vercel.app/explore/demand-growth?grid=caiso`: at the foot, open "Decisions on this page"; rest the mouse on the "i" of "Demand at the grid is not sales to customers": the two windows of California's charging. Then `&window=h09` (+13.91 percent) and `&window=h17` (-1.46): the morning's growth is the charging.
4. Any view, the foot: "The table holds no forecast. What the grid operators forecast, as the ERW holds it, is under Headroom on All grids", the link opening `https://erw-flame.vercel.app/cost-of-power?view=allgrids`.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 13:05 | 7517 | `eia930_demand_growth` (`warehouse/derived/demand_growth.py`) | Write the change in MW since 2019 for the three whole-year windows, as the builder does for a month and an hour: the whole year's average and the peak on the last whole year's row, the year so far on the newest year's (three rows an area, MW to one decimal, from the means as the table rounds them). The explorer then draws its column "Change, MW" in those windows (ERCOT: 55,717.2 less 43,797.6) | EIA Form EIA-930, the table's own rows | requested |
| 2026-11-16 13:05 | 7517 | `eia930_demand_growth`, `eia930:CISO`, `avg_demand_mw_m03` of 2019 | EIA's hours of March 2019 for California set beside CAISO's own load for the month. The table holds 19,536.4 MW, where February and April of 2019 are 22,125.0 and 22,030.8, every later March is 21,614 MW or more, and California's retail sales of March 2019 (19,565 GWh) were above February's and April's. Say whether EIA's hours are low (the faulty hours of February to May 2019 that the screen leaves out only when a quarter from their neighbours) and, if so, what 2019's mean would be | CAISO's own load (OASIS or its annual report); EIA Form EIA-930 | requested |
| 2026-11-16 13:05 | 7517 | `shoulder_hours_monthly` (or a table of its own); `eia930_demand_growth` | The batteries' charging by month in California from 2019, as MW on average (the hours below zero of the fleet's output), so that the year 2025 and each earlier year can be split as June to December 2025 is in `replication/demand_growth/california_charging.py`: it is held from June 2025 only. And the same check for ERCOT: whether EIA's `ERCO` demand counts ERCOT's batteries' charging (EIA's demand beside ERCOT's own load on an average day of 2025). This goes with session 7508's request on EIA's California series and session 7512's row 1 | CAISO, supply by fuel (history) or EIA-930's own battery series for CISO; ERCOT's fuel mix report | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 13:05 | 7517 | wip/7508-demand-growth | /explore/demand-growth?grid=pjm&window=peak | The line under the three headlines, at 1280 and 390 px; each of its three figures under the mouse | "The highest hour of 2026 so far (January to October): 162,648 MW, +6.78 percent on the highest hour of the same months of 2019 (152,315 MW)."; each figure's hover names its row and EIA-930; no sideways scroll. With `grid=us48`: no such line | wanted |
| 2026-11-16 13:05 | 7517 | wip/7508-demand-growth | /explore/demand-growth?grid=pjm&window=ytd | The second headline's line; the head of the table "Every grid" at 390 px | "2019, January to October: 91,744 MW"; the column headed "2019, January to October, MW"; the table scrolls inside its own frame, not the page | wanted |
| 2026-11-16 13:05 | 7517 | wip/7508-demand-growth | /explore/demand-growth | The foot: the line that begins "The table holds no forecast", its link and its "i", under the mouse and the keyboard, at 390 px | The link opens /cost-of-power?view=allgrids; the tip opens, is not cut by the frame and names ERCOT's report, CAISO's assessment and FERC Form 714 | wanted |
| 2026-11-16 13:05 | 7517 | wip/7508-demand-growth | /explore/demand-growth?grid=caiso | "Decisions on this page" opened; the "i" of "Demand at the grid is not sales to customers", at 1280 and 390 px | The tip (over 1,000 characters) is whole and readable: it ends "it does not close 2026's gap to sales." and its source line; it is not cut off at the bottom of the page or the side of the screen | wanted |

## Landing request

- Head: the commit that holds this report on `wip/7508-demand-growth` (the reply names it); it lands with session 7508's stack, of which it is the top.
- Tests: `tests/test_session7517_demand_growth_read.py` (11), `tests/test_session7508_demand_growth.py` (13) and the fourteen older files above (114 tests, 6 skipped), all pass.
- Changes: `/explore/demand-growth` (in review): one line in the peak window (three new checked figures a grid), two labels of the year-so-far window, one line and tip at the foot, the words of two decisions. New: `docs/reviews/demand-growth-read-2026-11-16.md`, `replication/demand_growth/california_charging.py` and `california_rows.csv`, the test, the note's section.
- Does not change: any table, any shared explore file, `release.ts`, any other page. A snapshot of the live pages differs on none (the page is in review). `check-values` reads 21 more keys on the seven grids' peak views; none on the five views it reads today.

## Needs the key

None.

## Decisions made without you

- The reader is the lab's energy lead (the chain file's), not the analyst: the lead's cases include the analyst's.
- The peak window gained a line, not a fourth headline or a changed third one: nothing the page had is dropped, and no slot part A replicated changes but the two labels of row 4.
- California's figures are stated for the two windows the charging is held for, not scaled to the year 2025: no figure is made for months without rows. The charging is the sum of the average day's hours below zero, as session 7512 counted it (August 2025: 42,433 MWh a day in both sessions).
- "Demand less the charging" takes nothing off 2019: its charging is not held, and the fleet was 186 MW.
- `california_rows.csv` is committed: the three tables are public (EIA, public domain; CAISO's supply by fuel, license public in the table's header).
- The All grids tab was not edited (row 10 is fixed on this page's side; row 11 is a ruling naming its file and lines).
- Two long commands (a drawing of the 315 views, the older tests) ran in this session's background; no agent or helper was started.
- The rows are the tables as this machine holds them (restored copies, the builds of 4 October and 6 November 2026), not the live set.

## For Samuel's ruling

1. Whether the explorer should take a site's MW and state its share of a grid's growth. Default: no; the page draws rows and computes nothing.
2. Which demand California's growth should stand on: EIA's, which counts the batteries' charging (+4.45 percent), or demand less the charging (negative in the months held of 2025). Default: EIA's stays, and the decisions state the charging beside it.
3. A forecast beside an outcome: CAISO's forecast peak for summer 2026 (46,844 MW) is under the highest hour metered (49,959 MW), and neither page says the two are different measures. Default: nothing drawn here; one sentence in the All grids tab's hover on your word.
4. Part A's row 12 ("cause not established") is now answered in part by row 5 of this read. Default: part A's file is left as written; the pack's cross-check line for California can cite this report.

## A fault seen in another tool

- None new. Session 7512's rows 5, 7 and 13 on `/shoulder` and this read's rows 5, 6 and 8 are one finding; the data machine's answer to one serves both.
