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
| The day's high and low, the 7 and 30 days' peak hour, complete days, hours and hours above 100, 250 and 1,000 | 33 rows, 594 figures | all (prices within 0.005) | one row's day (SPP South, real time, 22 November) is not in its hourly file (finding 1) |
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

FINDINGS_DETAIL

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

LANDING_ROWS
