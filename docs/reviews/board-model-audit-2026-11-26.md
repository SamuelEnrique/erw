# The price board's computed columns: the model audited as a hostile expert would

Session 10206, 26 November 2026, chain 710 (part D), the old laptop. Read as a power trader who checks the board every morning and wants to find it wrong. In the form of `docs/reviews/datacenter-model-audit-2026-11-26.md` and `docs/reviews/battery-model-audit-2026-11-20.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/board-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-board-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- The board's file read here: `site/data/board.json` as origin/main holds it, built `2026-11-25T15:23:51Z` (1,319 rows: 1,208 with a value, 88 licensed, 19 paused, 4 not held; 1,208 series files and 82 hourly files under `site/public/board/`).
- Earlier reads are cited, not repeated: the data audit of 6 November (`docs/reviews/board-audit-2026-11-06.md`, rows 1 to 51), the trader's read of 16 November (`docs/reviews/board-read-2026-11-16.md`, rows 1 to 20), the ruling files of 17 November (`ruling-impact-board-2026-11-17.md`, `ruling-alternatives-board-2026-11-17.md`), the held public files (`docs/reviews/held-public-files-2026-11-13.md`). Window E is adding a group to `site/app/board/` tonight: no file of that folder, of `warehouse/derived/board_page.py` or of `site/lib/board.ts` is edited by this audit's branches.

## In short

- **The arithmetic is right.** An independent restatement written from the method notes, not from the builder or the replication, gives every computed figure the board holds from the page's own files: 23,547 row figures on 1,208 rows (latest, five moves with their base dates and percents, the 7-day, 30-day and 12-month means and counts, the 30-day low and high, the one-year range and position, the trend's points), 266,809 figures of the power rows from the hours, 166,601 spread figures (hub spreads, spark, implied heat rate, dark, cracks, Brent less WTI, day-ahead less real time) and the week table's measures. Every public figure agrees to the fourth decimal within the rounding of its inputs (largest 0.0001), and every daily power mean to the fourth decimal at full precision from the warehouse's own tables (1,566 days, four differ by 0.0001: rounding). The on-peak flag of 1,145,008 hours agrees with the rule written again.
- **The board shows old rows where it holds new prices (finding 1, High).** The page keeper keeps a row from an earlier build when the new build's history is shorter. On the board of 25 November ERCOT Hub average's day-ahead tile reads USD 16.18 on 20 November, marked stale, while the week table on the same page reads 46.31 on 25 November as "Day-ahead, latest". 98 public rows are marked stale that the new build held current (power 28, battery 27, ancillary 14, day-ahead less real time 11, hub spreads 11, on-peak 6, plant fuel 1), up to 12 days behind for power and 53 for reserves. A figure: for Samuel's ruling, and a data request (the data machine's board step last ran on 20 November).
- **Held grids' figures written after the hold sit in the public file (finding 2, Medium).** `site/data/board.json`, committed to the public repository, holds 20 week lines of NYISO's and ISO-NE's hubs and zones with day-ahead means to 25 November and 20 of their real-time spikes of 17 to 20 November, a month after the hold of 21 October. The page drops them on the server (`holdRows`), so no reader sees one. The fix is the builder's: a data request.
- **The week table's on-peak is not the on-peak group's (finding 3, Medium).** For CAISO the week's "On-peak DA" and "Off-peak DA" take the five-day block (Saturday off-peak), while the group "Power, on-peak and off-peak" takes CAISO's six-day block; the week's on-peak mean is of the latest 7 weekdays, over 9 calendar days, while its hover says "the 7 days to". SP15's off-peak week: 42.72 as drawn, 45.36 under the group's rule (6.2 percent). Fixed in words.
- **Smaller.** The strip's lowest and highest grid compare a day five days before the build with no stale mark (finding 4, words); "Battery spread" is the trader's convention of the day's highest hour less its lowest in either order, not what a battery earns, and says neither (finding 5, words): ordered, it is 5.0 to 9.7 percent lower, at an 85 percent round trip 10.6 to 14.0 percent lower.
- **Three branches fix words and move no figure (3, 4, 5); one shows a figure for ruling (1); one shows a builder fix for the data machine (2).**

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/board/page.tsx` | The page: the hold of the day on the server (`holdRows` with `licenseHeldGrids()`), the license line, the rows' CSV links, "Ask the board", the decisions block, the downloads |
| `site/components/board/BoardView.tsx` | The page's face: the twelve tiles, the headline strip (lowest and highest grid, four closes, the two range cells), the groups' tables (latest, moves, percents by `PERCENT`, 7-day, 30-day and 12-month means, 30-day low to high, trend, one-year range, the day's high and low), the week table and its spikes |
| `site/components/board/Workbench.tsx` | A row opened: its series or its hours, overlays, spreads and ratios, prior years, the distribution, 30-day volatility |
| `site/lib/board.ts` | Every rule of the page, pure: `holdRows`, `closeAge` (stale past 3 days for a power market's daily row, 10 another daily, 17 weekly, 132 monthly, 135 quarterly), `shownMove`, `gridExtremes`, `rangeExtremes`, `headDate`, `weekStale`, `rowsCsv`, `volatility`, `distribution` |
| `site/data/board.json` | Every row's figures as the builder wrote them, the week table (`week`) and the spikes (`spikes`) |
| `site/public/board/s/<id>.json`, `h/<id>.json` | A row's whole series (4 decimals); a hub's or reserve's hours (each hour to the cent) with the on-peak flag of each hour |
| `warehouse/derived/board_page.py` | The builder: daily means of complete local days, on-peak and off-peak, battery spread, day-ahead less real time, the spreads, the moves, the means, the range, the trend, the week table from `iso_trader_daily` and the spikes from `iso_rt_top_intervals` |
| `warehouse/derived/page_keep.py` | Takes a built row only where it is no older and no shorter than the held one; keeps Henry Hub and every spark and heat row as one set |
| `warehouse/derived/trader_view.py` and `docs/methods/trader_view.md` | The week table's daily measures (`iso_trader_daily`) |
| `docs/methods/price_board.md` | The note: "The columns of every row", the groups, the assumptions, the spreads, the week, the workbench; `price_board_carbon.md` and `price_board_v4.md` for the older tables |
| `replication/board/replicate.py` | The published replication (30,587 of 30,587 on the file of 15 November) |

## How every number here was computed

- **The independent restatement:** `restate_board.py` (standard library), written from the note's table "The columns of every row", its spreads table and `trader_view.md`'s measures: each row's figures from its series file; each power row's daily means, on-peak and off-peak means (the rule written again, NERC holidays by their own dates), battery spread and day's extremes from its hours; each spread from its input rows' series files; the week table from the hours. It never prints a held grid's value.
- **At full precision:** `restate_precision.py` reads `iso_dam_hub_prices` and `iso_rtm_hub_prices` of the main checkout (26 August to 12 November 2026, read only) and makes each complete local day's mean again.
- **One rule at a time:** `measures_board.py` (reuses the restatement's rules). **The kept rows:** `kept_rows.py`. **The held grids in the file:** `held_check.py` (ids, counts and dates only).
- Copies of every script and its printout: `docs/reviews/board-model-audit-2026-11-26/` (written to run from `runs/c10206/` of a worktree).

## The arithmetic re-done

| Figures | Compared | Agree | The gaps |
|---|---|---|---|
| Each row from its series file: latest; day, week, month, year and YTD moves (change, base date, percent where the page shows one); 7-day and 30-day means and counts; 30-day low and high; 12-month mean, count, latest less it; one-year range, count, position; trend points | 23,547 on 1,208 rows | all public figures but 17 | 14 at the fourth decimal (largest 0.00007: the means are made from the series' rounded values); 3 on one row kept from a build before the YTD move and the 12-month mean existed (Montana's gas to power plants: no YTD, no 12-month mean, a trend of seven years). The 158 other gaps are all on held grids' rows, which the page never draws |
| Daily means from the hours, to the cent | 80,617 days | 80,617 | the hourly files round each hour to the cent, so to the fourth decimal the largest gap is 0.0024 |
| Daily means at full precision, from the warehouse's tables | 1,566 days, 22 rows | 1,562 | 4 by 0.0001 (rounding half up against half even) |
| On-peak, off-peak, on-peak less off-peak, by day | 24,361 | all, to the cent | |
| Battery spread, by day | 80,617 | all within 0.01 | 7,249 by 0.01: the hours are rounded to the cent in the file |
| The on-peak flag of each hour | 1,145,008 hours | all | |
| The day's high and low, the 7 and 30 days' peak hour, complete days, hours and hours above 100, 250 and 1,000 | 33 rows, 529 figures | all (prices within 0.005) | one row's day (SPP South, real time, 22 November) is not in its hourly file (finding 1) |
| Hub spreads; spark; implied heat rate; dark; the eight cracks; Brent less WTI; day-ahead less real time | 24,697; 24,675; 4,922; 154; 59,474; 9,854; 32,913 | all, within 0.0001 | SPP South's day-ahead less real time holds 21 and 22 November, whose day-ahead means are not on the board's day-ahead row; CAISO's and SPP's spark and heat rows lack 21 November, which their inputs allow (finding 1) |
| The week table: day-ahead, real time less day-ahead, heat rate, their changes; largest real-time premium; hours 50 over; 30-day volatility | CAISO SP15 and NP15, SPP North | all to the cent | on-peak and off-peak only under the five-day block (finding 3). ERCOT's six hubs, CAISO ZP26 and SPP South not restated: their hourly files end 20 November and the week ends 25 November (finding 1) |

- **Nothing is filled.** No restated daily mean needed a day the hours do not hold whole; every day in a row's file is complete in its hours, and no complete day of the hours' span is missing from a row's file (34 hubs and zones).
- **The rules the restatement wrote again and found as the code does them:** a move's base is the newest value at least 1, 7, 30 or 365 days back and no more than 6 days older (a weekly year: 364 days back, within 3); a monthly move is the month before and the same month a year before; YTD against the year before's last value within its slack; the percent only on a price that cannot be negative; the 12-month mean and range on 180, 26, 9 or 4 values; the trend 90 days, a year or three years; a real-time hour the mean of every one of its intervals; a complete local day of 24, 23 or 25 hours; on-peak hours ending 7 to 22, Monday to Friday (CAISO to Saturday), NERC holidays off; the gas price the day's or the newest trading day's up to 4 days before.

## One rule changed at a time

Each line changes one choice and keeps every other. Measured on the page's own files, main hubs, the last 365 complete days or the 30 days to the row's latest.

| Choice the board makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Battery spread: the day's highest hour less its lowest, either order (day-ahead) | the best spread charging before discharging | ERCOT Hub average 55.22 to 50.89 (-7.8 percent); ERCOT West -9.6; CAISO SP15 -5.0; SPP North -9.7. The lowest hour came after the highest on 16, 21, 46 and 37 percent of days | the formula, not the order (finding 5) |
| The same, 100 percent round trip | ordered, 85 percent round trip | -13.9, -13.5, -10.6, -14.0 percent | no (finding 5) |
| The same, one hour a side | the two highest less the two lowest | ERCOT Hub average 55.22 to 52.44 (-5.0 percent) | the formula names one hour |
| Spark spread over all 24 hours | over the on-peak hours, weekdays | ERCOT Hub average's 30-day mean 14.92 to 15.80 (+0.88) | yes, the formula ("day-ahead daily mean") |
| Heat rate 7.0 MMBtu/MWh | EIA's 2025 fleet average, 7.781 (`heat_ref`, on hover) | 30-day mean 14.92 to 12.70 (-2.22); 20 November -5.52 to -7.94 | yes, both on hover |
| Gas at Henry Hub | a regional hub (Waha for ERCOT) | not sized: no regional daily gas price is held (licensed) | yes ("indicative") |
| The week's on-peak in CAISO, Monday to Friday | Monday to Saturday, as the on-peak group | SP15 on-peak 29.34 to 29.45; off-peak 42.72 to 45.36 (+6.2 percent); NP15 58.90 to 60.60 and 57.22 to 56.93 | no (finding 3) |
| A kept row when the new build is shorter | the new build's newest values | ERCOT Hub average day-ahead 16.18 on 20 November (stale) to 46.31 on 25 November; 98 public rows current | no (finding 1) |
| The 30-day mean over the days held | a mean that waits for 30 days | 114 of 249 power-group rows have fewer than 30 (51 have 28: ERCOT's 7 and 8 November are missing; on-peak rows hold weekdays only) | the count on hover (cited: the impact file of 17 November, line 6) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "Latest" and its date | every row, the tiles, the strip | the newest value held; a day-ahead price may be tomorrow's, said on hover ("a day-ahead price for a coming day") | **Right as stated**, but a row kept from an earlier build is older than the prices the same file holds (finding 1) |
| "Day-ahead, latest" in the week table | the week table | the week's own build (`iso_trader_daily`), not the row's | **Finding 1**: for ERCOT 25 November against the row's 20 November |
| Stale | every row, tile and head | past 3 days a power market's daily row, 10 another daily, 17 weekly, 132 monthly, 135 quarterly; moves and the 12-month mean blank | **Right**; the strip's grid cells are the one figure dated without the rule (finding 4) |
| Time zones and the day | the hovers | each grid's local operating day (America/Chicago, America/Los_Angeles); cross-grid spreads on the same date, each on its own local day, said in the formula | **Right as stated** |
| Day-ahead against real time | the groups, the week | each market's own daily mean; day-ahead less real time in the group, real time less day-ahead in the week, each said | **Right as stated** (the read of 16 November, row 8) |
| A real-time hour | the name's hover ("Interval") | the mean of the hour's 4 15-minute prices (ERCOT), of 4 15-minute means of 5-minute prices (CAISO), as each interval says; restated at full precision | **Right** |
| Hub definitions | the name's hover ("Code") | the operator's settlement point names; the load zones and the node basis by class | **Right as stated** |
| Units | every row | USD/MWh, USD/MW-hour for reserves, USD/MMBtu, USD/bbl, USD/gal; the cracks in USD/bbl (gallons times 42) | **Right** |
| On-peak | the on-peak group; the week table | hours ending 7 to 22 local, Monday to Friday (CAISO Monday to Saturday), NERC holidays off; the week's measure from `trader_view.md` takes Monday to Friday everywhere | **Finding 3** |
| "the 7 days to" | the week table's hover | the latest 7 days holding the measure; for on-peak, 7 weekdays over 9 calendar days | **Finding 3** |
| Spark spread, implied heat rate, dark spread | the formula on hover | as stated, the gas the day's or up to 4 days before; "indicative" | **Right as stated**; restated |
| Battery spread | the formula on hover | the day's highest hour less its lowest, on complete days | **Finding 5**: in either order, not said |
| Percent beside a move | the moves | 100 x the move over the base, only on a row that is not power, reserves, a yield or a formula, and a base above zero | **Right** (1,983 percents restated) |
| Held grids (ISO-NE, NYISO; MISO paused; PJM licensed) | every cell | `holdRows` on the server drops every figure of a held grid's row, its week lines and spikes; drawn with the page's own components, no held figure reaches the HTML (`site/scripts/test-board-read.mjs`, 31 of 31 on this file) | **Right on the page**; in the public file, finding 2 |
| "30-day avg" | the column | the mean of the values held in the 30 days, its count on hover | **Right as stated**; the missing ERCOT days are the impact file's line 6 |
| The strip's "Lowest of 3 grids" and "Highest" | the headline strip | the newest day every priced main hub holds | **Finding 4**: 20 November on the file of 25 November, no stale mark |

## What a trader's own board would hold that this does not

| Item | Why | From |
|---|---|---|
| Regional gas (Waha, Houston Ship Channel, SoCal Citygate) in the spark spread | licensed indices | the note's publisher table |
| Forward curves (NYMEX, ICE) | licensed | CME Group, ICE |
| New York, New England, PJM, MISO | license needed or paused | `docs/licenses.md` |
| Real-time 15-minute or 5-minute extremes on the wall | the board keeps hours; the spikes table holds intervals | the note, session 1611 |
| An on-peak spark spread and a battery spread with order and losses | not built; sized above | this audit |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | High | Rows kept from an earlier build are shown though the same file holds newer prices; two "latest" day-ahead prices for one hub on one page | ERCOT Hub average day-ahead 16.18 (20 Nov, stale) against 46.31 (25 Nov); 98 public rows stale that the new build held current | figure: ruling; data request | `wip/audit-board-1` |
| 2 | Medium | NYISO's and ISO-NE's week lines and spikes written after the hold are in the public `board.json` | 20 week lines to 25 Nov, 20 spikes of 17 to 20 Nov; none drawn | builder: data request | `wip/audit-board-2` |
| 3 | Medium | The week table's on-peak and off-peak in CAISO take Monday to Friday, the on-peak group Monday to Saturday; the on-peak week is 7 weekdays, not "the 7 days" | SP15 off-peak week 42.72 against 45.36 (6.2 percent) | words | `wip/audit-board-3` |
| 4 | Low | The strip's lowest and highest grid are dated 5 days before the build with no stale mark | the strip's day 20 Nov on the file of 25 Nov | words (a mark) | `wip/audit-board-4` |
| 5 | Low | "Battery spread" is the highest hour less the lowest in either order, no losses, one hour: not what a battery earns, and not said | ordered -5.0 to -9.7 percent; at 85 percent round trip -10.6 to -14.0 | words (the note) | `wip/audit-board-5` |

- Ranked by severity, then by size. One High, two Medium, two Low. Finding 1 moves printed figures if its rule is changed and is Samuel's ruling; finding 2 is the builder's, run on the data machine.
- The three words branches (3, 4, 5) were merged together onto origin/main of 26 November in a trial: no conflict, their tests pass (5 of 5). Each branch's test run with every test file that reads the changed component or note: 227, 207 and 80 passed; `site/scripts/test-board-read.mjs` 31 of 31 and `test-board-1116`, `1137`, `1193`, `1311` pass on branches 3 and 4.

## 1. Rows kept from an earlier build are older than the file's own prices (High; a figure)

- **Where.** `warehouse/derived/page_keep.py`, `choose`: a built row is taken only where it is no older and no shorter (98 percent of the held points) than the held one; else the held row stays, with `held = {since, newest, why}`. The board's tiles, groups, strip and workbench read the kept row; the week table and the spikes come from the new build.
- **Why it is wrong.** On the board built 25 November 2026 the daily runner's build held ERCOT's prices to 25 November with 90 days of history; the held rows hold 2,879 days to 20 November, so the keeper kept them. ERCOT Hub average's day-ahead tile reads USD 16.18 on 20 November, marked stale; the week table on the same page reads 46.31 on 25 November as "Day-ahead, latest". The page marks every kept row stale, so no stale figure reads as current; but a trader sees two "latest" prices for one hub, and the newest is not on the tile. The same keep leaves inputs and outputs out of step: SPP South's day-ahead less real time (new build) holds 21 and 22 November, whose day-ahead means are not on the board's day-ahead row (kept); SPP South's real-time "Day's high / low" is of 22 November, a day its hourly file (kept) does not hold; the spark set (Henry Hub with every spark and heat row, kept together) ends on 20 November though 21 November's spread can be made from the rows drawn; the workbench's hourly files for ERCOT's six hubs, CAISO ZP26 and SPP South end on 20 November.
- **How much.** 245 rows are kept (151 public). 98 public rows are marked stale that the new build's newest would have kept current: power 28, battery 27, ancillary 14 (up to 53 days behind), day-ahead less real time 11, hub spreads 11, on-peak 6, plant fuel 1. The other kept rows (45 gas by state, 3 heating, 4 metals, 1 spark) would be no more current with the new build. One kept row is from a build before the YTD move and the 12-month mean (Montana's gas to power plants): no YTD, no 12-month mean, a trend of seven years under a header that says three.
- **Why now.** The data machine's page files last ran on 20 November (`3b1ad41e8`); its run rebuilds every row with its whole history, and the keep then takes it. So the first cure is a run, not code.
- **The test.** `tests/test_audit_board_1.py` on `wip/audit-board-1`: the rule (a newer, shorter build loses), and on the file of 25 November the tile older than the week table and the 98 rows. Passes on main; not for landing.
- **For Samuel's ruling.** Default "left as it is". The other choice: the keeper appends the new build's newer points to the held row's history and recomputes the row (the tile would read 46.31 on 25 November; 98 rows current). That moves figures.
- **Data request.** The data machine's board step (`dm_board_page`) run, and the reason it has not run since 20 November said.

## 2. Held grids' week lines and spikes in the public file (Medium; the builder)

- **Where.** `warehouse/derived/board_page.py`, `build_week`: the week table from `iso_trader_daily` and the spikes from `iso_rt_top_intervals` for every grid but MISO. Every other builder of the board asks `ls.held_grids()` (power, reserves, spark, battery, day-ahead less real time); this one does not. `site/lib/board.ts`, `holdRows`, drops the held grids' week lines and spikes on the server.
- **Why it is wrong.** `site/data/board.json` is committed to the public repository. On the file of 25 November it holds 20 week lines of NYISO's and ISO-NE's hubs and zones (day-ahead means to 25 November) and 20 of their real-time spikes (17 to 20 November), a month after the hold of 21 October. No reader of the page sees one; anyone reading the repository does. The held public files of 13 November (`docs/reviews/held-public-files-2026-11-13.md`) named the series and hourly files, not these, and the request of 13 November (data request 28 of `docs/state/data_requests_licenses.md`) stopped new writes for the spark, heat and dark rows only.
- **The test.** `tests/test_audit_board_2.py` on `wip/audit-board-2`: counts and dates only (no value read out), that the page drops them, and that `build_week` names no held grid. Passes on main; not for landing.
- **The fix, for the data machine** (window A; `board_page.py` may be touched by window E tonight, so no edit here): `build_week` skips an `iso` whose grid is in `ls.held_grids()` for both the week and the spikes, as `build_power` does. A tightening that moves no figure a reader sees. Removing the lines already committed is the owner's ruling, as for the held public files.

## 3. The week table's on-peak is not the on-peak group's (Medium; words)

- **Where.** `site/components/board/BoardView.tsx`, `WeekTable` (the heads "On-peak DA, week" and "Off-peak DA, week" had no hover; each cell's hover "the 7 days to ..."); `Workbench.tsx`, the same five figures; `warehouse/derived/trader_view.py` (on-peak: weekdays that are not NERC holidays, every grid) against `board_page.py`'s on-peak group (CAISO Monday to Saturday).
- **Why it is wrong.** One page carries two on-peaks for CAISO and says neither. A CAISO Saturday is on-peak in the group and off-peak in the week. And the on-peak week is the latest 7 weekdays that hold an on-peak mean (17 to 25 November on the file), where the hover says "the 7 days to 25 Nov 2026".
- **How much.** SP15's week on the file of 25 November: off-peak 42.72 as drawn, 45.36 under the group's rule (+2.64, 6.2 percent); on-peak 29.34 and 29.45. NP15: off-peak 57.22 and 56.93, on-peak 58.90 and 60.60. Restated from the page's hourly file, each to the cent under the five-day block.
- **The test.** `tests/test_audit_board_3.py` on `wip/audit-board-3`: the measured gap from the hourly file (passes on main) and the words drawn with the page's own component (fails on main).
- **The fix on the branch, words only.** The two heads say on hover which hours and days (Monday to Friday in every grid, CAISO included, where the group takes Monday to Saturday; the 7 weekdays can run over 9 calendar days); the on-peak cell says "the latest 7 weekdays with an on-peak mean, to ..."; the workbench says the same; `price_board.md` and `trader_view.md` say so. It touches `BoardView.tsx` and `Workbench.tsx`, not `site/app/board/`; if window E edits the same lines tonight, the landing desk merges after window E's landing. No figure moves. Taking one block for both is Samuel's ruling and would move figures.

## 4. The strip's lowest and highest grid carry no stale mark (Low; words)

- **Where.** `BoardView.tsx`, `Headline`: the two cells' note is the row's label and `dateWords(ex.day)`; `gridExtremes` takes the newest day every priced main hub holds.
- **Why it is wrong.** The rule of the read of 16 November (row 1: a stale number is never shown as current) was applied to the strip's closes and range cells, not to these two. On the file of 25 November ERCOT's day-ahead row ends on 20 November (finding 1), so the strip compares 20 November, five days before the build, and dates it with no mark beside closes that carry one.
- **The test.** `tests/test_audit_board_4.py` on `wip/audit-board-4`: drawn with the page's own component, the two cells read "(stale)" with the age on hover past a market's 3 days, and none on a copy whose build day is the strip's day. Fails on main.
- **The fix on the branch, words only.** The day reads "(stale)" past 3 days (`weekStale`, the week table's rule, already imported), with the age on hover and `data-head-stale`; `price_board.md` says so. No figure moves.

## 5. "Battery spread" is the top-bottom convention, unsaid (Low; words)

- **Where.** `board_page.py`, `FORMULAS["battery"]` ("the day's highest hourly price - its lowest hourly price at the hub, on complete operating days"), drawn in the name's hover; `price_board.md`, the spreads table.
- **Why it matters.** A trader knows the top-bottom spread; a reader from a fund reads "battery spread" as what a battery takes. It is in either order (on 16 to 46 percent of days the lowest hour comes after the highest), one hour each way and before losses.
- **How much.** Day-ahead, the 365 days to 20 or 25 November: charging first, the mean spread is 7.8 (ERCOT Hub average, 55.22 to 50.89), 9.6 (ERCOT West), 5.0 (CAISO SP15) and 9.7 percent (SPP North) lower; at an 85 percent round trip 13.9, 13.5, 10.6 and 14.0 percent lower.
- **The test.** `tests/test_audit_board_5.py` on `wip/audit-board-5`: from the page's hourly file, order and losses make it smaller (passes on main); the note's words (fail on main).
- **The fix on the branch, words only: the note.** The row's own formula is the builder's words, in a file window E may touch tonight; the ready text for after window E lands, for window A: `"the day's highest hourly price - its lowest hourly price at the hub, on complete operating days, in either order, one hour each way and before losses: the top-bottom spread, not what a battery earns"`. It reaches the page at the data machine's next build.

## What was checked and found right

- **Every row's figures** from its own series file (23,547), and the power rows' daily means at full precision (1,566 days).
- **The spreads**: hub spreads within and across grids, the spark spread and implied heat rate with the gas rule of up to 4 days, the dark spread on whole months, the 3-2-1 cracks and the six product cracks with their yields, Brent less WTI, day-ahead less real time.
- **The on-peak calendar**: NERC's six holidays and a Sunday holiday on the Monday, CAISO's Saturdays, the daylight saving days' 23 and 25 hours.
- **The week table's** day-ahead, real time less day-ahead, heat rate, their changes, the largest real-time premium, the hours 50 over and the 30-day volatility (a sample standard deviation of 30 daily changes), where the hours are on the page.
- **No held figure on the page**: drawn with the page's own components after `holdRows`, `site/scripts/test-board-read.mjs` 31 of 31.

## Not covered, or left open

- **The workbench's own arithmetic** (overlays, ratios, prior years' band, distribution): read in `lib/board.ts`, not restated; it computes on the files restated here.
- **The spikes** (`iso_rt_top_intervals`): a table's top intervals, printed, not computed by the page; not restated.
- **The ERCOT week lines, CAISO ZP26's and SPP South's**: their hourly files end 20 November; a data request below.
- **Ancillary services' hours**: 43 rows' daily means restated from their series only (Part 1), not from their hourly files.
- **The pages drawn to HTML for the words branches**: each branch's test draws the changed component with the site's own code.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-board-3` (`b7307258e`), `wip/audit-board-4` (`2990df68e`), `wip/audit-board-5` (`8fb73f0a3`). They merge together cleanly onto origin/main of 26 November. Branches 3 and 4 touch `site/components/board/BoardView.tsx` (3 also `Workbench.tsx`): land after window E's board group if both are waiting.
- **Not for landing:** `wip/audit-board-1` (`947f9f9de`, a figure), `wip/audit-board-2` (`b438aa45f`, the builder's fix).
- **For Samuel's ruling, default "left as it is":** finding 1, the keeper's rule (append a shorter build's newer points to the held history: ERCOT Hub average's day-ahead tile 16.18 on 20 November to 46.31 on 25 November; 98 public rows current).
- **Data requests:** the data machine's board step run and why it has not run since 20 November (finding 1); `build_week` to skip held grids (finding 2); the battery formula's words in the builder after window E lands (finding 5); ERCOT's six hubs', CAISO ZP26's and SPP South's week lines restated from `iso_trader_daily` of 19 to 25 November, which this machine does not hold.

## The words branches of the datacenter audit, drawn (part D, second bullet)

`/cost-of-power` drawn to HTML with the site's own page and drawer (`site/scripts/cost-of-power-read.mjs`, its reads answered from table files cut to a year) for four cases (the default, 1,000 MW at `LZ_NORTH`, the All grids tab at 100 and 1,000 MW), on origin/main and on each branch, and compared line by line (`draw_dc.mjs`, `compare_draw.py`, `pair_diff.py`, `numbers_same.py`; `task1_summary.out`).

| Branch | Head | What changed in the drawing | Verdict |
|---|---|---|---|
| `wip/audit-datacenter-1` | `8c85398c8` | the row "Levelized power per GPU-hour, over the years counted" and its note; "all-in" to "levelized" in the sensitivity chart's sentence, caption and nine hovers; no "all-in" left on the view; every number the same, in order | pass |
| `wip/audit-datacenter-2` | `e6ed957b4` | the All grids "All-in" column's tip gains its sentence; ", loss" in the 14 cells' hovers; nothing else | pass |
| `wip/audit-datacenter-3` | `70b141e1a` | the income note gains the price-taker clause (one number added: "1 MW"); nothing else | pass |
| `wip/audit-datacenter-5` | `886f65045` | the contract share's hover gains its two sentences; nothing else | pass |
| `wip/audit-datacenter-6` | `763efd9c8` | the note under "How clean?" gains its sentence; nothing else | pass |

No em dash in any drawing.
