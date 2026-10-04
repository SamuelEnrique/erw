# Session 104 report: the price board, version 3

**Built and on the live site, in review at `/board/v3`.** The prices that matter in three groups, power by grid, natural gas and oil, in the battery page's layout: each with its last value and the day it is for, its move on the day and on the week, and its last thirty days held. MISO is shown as paused and PJM as licensed, in words, with no number. One summary sentence. The older board, `/board`, is untouched. One deploy, with the 25-page snapshot before and after.

## Read these first

1. **Two numbers moved on the home page across this deploy, and neither is this session's.** They are session 103's load reaching the page: a deploy makes the home page read the catalogue again. The row total went from 13,849,497 to 13,849,370 (the 127 rows session 103's report said would move). And **"Last refresh" went from 2026-10-04 14:45 UTC to 19:34 UTC**, which session 103's report did not foresee: the home page shows the newest run among the public tables, and the shoulder table was rebuilt at 19:34. It is true, and it reads as if the daily run had run again at 19:34. It will read 14:4x again after tomorrow's daily run only if no session loads a public table after it. This session changed no table and loaded nothing.
2. **`/shoulder` on production still shows the table as it was before session 103's load, and it is not the page's own hour of cache as I wrote there, or not only.** I checked again after this deploy: 99 of 3,482 of its checks still differ. The database holds the new figures (read with a visitor's key: California, July 2025, days held 30; the page says 31). The page's reads are kept by Vercel across deploys, each for an hour from when it was last refreshed, and a first request after the hour is answered from the old copy while the new one is fetched. I will check it once more in session 105 and say what I find. If it still differs then, it is a fault and I will look for it.
3. **The summary sentence compares the grids on the newest day they all hold,** not on the newest day any holds. New York's day-ahead prices run a day ahead of the others'; my first version of the sentence spoke for New York alone ("Day-ahead power for 5 October 2026 averaged USD 43.84 per MWh in NYISO"). Now: "Day-ahead power for 4 October 2026 averaged from USD 36.05 per MWh in SPP to USD 56.22 in CAISO, across the 5 grids with that day held; Henry Hub gas was USD 3.18 per MMBtu on 29 September 2026 and WTI crude USD 96.16 a barrel." The table still gives each grid its own newest day.
4. **Gas and oil are five days older than power,** and the page says so: EIA's daily spot prices in the warehouse end on 29 September 2026.

## The page

`/board/v3`, in review (`site/lib/release.ts`). Layout: the battery page's (the header, a panel of choices on the left, a summary sentence, three headline numbers, sections with tables, one fold, the source line). Nothing decorative: the only drawing is a small line of the last thirty days in each row.

| Group | What a row is | From |
|---|---|---|
| Power, by grid | The mean of a day's prices at the grid's main hub, USD per MWh: ERCOT's hub average, CAISO's SP15, New York City, SPP's North hub, New England's Internal hub. Day-ahead or real-time, by the one choice in the panel | `price_board_latest` |
| | MISO: "Paused since 4 October 2026: MISO's terms forbid automated access to its site, so the ERW has stopped asking for its prices until a person has reviewed the terms. The prices already held stay in the warehouse and are not shown here." | no number |
| | PJM: "Licensed: PJM's prices are published under a license and an account the ERW does not hold, so no PJM hub price is in the warehouse and none is shown." | no number |
| Natural gas | Henry Hub, EIA's daily spot price, USD per MMBtu | `eia_fuel_spot_prices` |
| Oil | WTI at Cushing and Brent, EIA's daily spot prices, USD per barrel | `eia_fuel_spot_prices` |

Each row: the last value; the day it is for; the move on the day (against the day held before it, whatever the gap: a fuel has no weekend, and the earlier day is in the cell's title); the move on the week (against the newest day held seven to ten days earlier); the last thirty days held. **A move whose earlier day is not in the table says "not held". Nothing is filled.** If a table cannot be read, its section says so and shows no number, and the sentence is not written.

**MISO's prices are in the table the page reads and are not shown.** That is session 96's reading of your pause carried here: MISO's terms forbid derivative works as well as automated access, so the page gives the reason and no figure.

The arithmetic is in `site/lib/board3.ts`, apart from the page, so it is tested without a browser.

## Every difference, the 25 live pages

`before-104` (20:12 UTC) against `after-104` (20:19 UTC): 44 differences.

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 38 | 32: the five latest real-time prices and their lines (the 15-minute feed). 6: the row total, 13,849,497 to 13,849,370, and "Last refresh", 14:45 to 19:34 UTC (each as a checked number and twice as text) | The feed: yes. The two catalogue numbers: **session 103's load, first point above** |
| `/network` | 6 | the hourly refresh's stamps | Yes |
| The other 23 | 0 | | |

Between session 103's last snapshot and this session's first, nine minutes apart: 0 differences.

## Tests and checks

- `tests/test_session104.py`, 8 tests: the last value, the day's and the week's move on days made for the test; a move whose earlier day is not held is null (a day a month back is not a week's move); a fuel skips the weekend; thirty days of history at most; the summary sentence, with and without a grid a day ahead; **the board's figures against the warehouse's own table** (each grid's last value and its day's move equal `price_board_latest`'s, and the table's own day change); the page in the battery page's layout and in review; the older board not touched by this session.
- The workflow (run 37231203900) passed and merged (`527774f`); Vercel accepted the deployment.
- On production in the internal view: `/board/v3` and `/board/v3?market=rt` render with data (164 figures each) and are closed to a visitor; `/board` renders as before (1,159 figures; its file is not in this session's commit).
- The route check on this machine's build: 0 failed.

## Errors and decisions

1. **One hub a grid**, the site's main hub for each (`site/data/markets.json`). CAISO's NP15 and ZP26, ERCOT's other hubs and the zones are on the older board and on `/prices/compare`.
2. **The week's move wants a day seven to ten days back.** A day further back is not called a week's move.
3. **No model call, no pull, no table, no load.** Model spend USD 0.00. MISO stays paused; this page asks no publisher for anything.
4. **A test passes a long table to Node on standard input:** a Windows command line could not hold it.

## For Samuel

1. **"Last refresh" on the home page** (first point). If it should mean the daily run and nothing else, it wants its own source (the daily run's stamp in `run_status`) instead of the newest table run. A small change to a live page: after you say so.
2. **Whether MISO's held prices may be shown** is the pause's open question, not this page's. One line in `site/lib/board3.ts` shows them.
3. **When it replaces `/board`:** version 3 leaves out what the older board has and this one was not asked for (peak and off-peak, spreads and heat rates, carbon, the ERCOT premium). They could be a second page, or folds under this one.

Energy Research Warehouse (ERW), session 104, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 20:10 to 20:30 UTC, unattended.
