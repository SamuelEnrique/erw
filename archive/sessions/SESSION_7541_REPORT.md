# Session 7541 report: `/supply` read as a utility planner or a fund analyst (chain 304, part C, samueloldlaptop, 16 November 2026)

- Branch `wip/7541-supply-read`, worktree `C:\Users\lossa\Documents\erw-7541`, stacked on origin/main at `7363f1a81`.
- A first session (7541) stalled at 15:46; its page and lib changes were committed by the coordinator as `53624d72c`. This session (7541 continued) worked out its rows from its changes and four scratch scripts, finished the read, the fixes and the test.
- The read: `docs/reviews/supply-read-2026-11-16.md`, five cases, 27 rows: 9 site fixed, 6 data machine, 5 browser, 6 rulings, 1 license.
- The page drawn whole by its own function (`site/scripts/supply-read-page.mjs`, new); test `site/scripts/test-supply-read.mjs`, 10 of 10.
- **One held figure reached the remote branch and was taken out:** commit `dde2f1d30` (the read file's head) wrote ISO-NE's cleared weekly figure in case 2; `b7d535b7c` removed it, and the test now fails if any held cleared figure is in the read file, this report or the two scripts. The same figure is already on main in `site/data/supply.json` (row 17, request 154), so nothing new was made public; squash the branch at landing to drop it from history.

## What changed

- `site/app/supply/page.tsx` and `site/lib/supply.ts` (another machine's stack, lab-desktop's chain 301): the hold of a held grid's cleared row (`holdRows`), the year and Last 52 column hovers, unit words on hover (`unitTitle`), the Grid page links under the burn table (first session); the burn week hover (`burnWeekWords`), the monthly gas volume and net export hovers (`latestTitle`), state names in full (`placeWords`, `withPlaceWords`) (this session).
- `site/scripts/test-supply.mjs`: the placeholder list now holds "license needed". `site/scripts/check-supply.mjs`: reads the file after the day's hold and the place words; a held grid's cleared row must read "license needed".
- Not touched: `site/data/supply.json`, `warehouse/derived/supply_page.py`, `site/lib/release.ts`, `site/components/Num.tsx`, the method note, the replication, any table.

## Tests

- `site/scripts/test-supply-read.mjs`: 10 of 10. `site/scripts/test-supply.mjs`: 9 of 9 (after its one line). `node --check scripts/check-supply.mjs`: exit 0 (it needs a built site; not run).
- `tests/test_session134.py`, `136`, `241a`, `247`, `281`, `333` (every python test naming the page, the lib or the file): 91 passed, 199 subtests.
- `tsc --strict` on `site/lib/supply.ts` alone: exit 0. No build (memory).

## What to review

- `https://erw-flame.vercel.app/supply` (in review: the review cookie). 1) "Day-ahead energy cleared, by grid": NYISO and ISO-NE read "license needed", hover each. 2) Hover the heads "On last year" and "Last 52". 3) "Fuel burned for power": the links line under the heading; open ERCOT "neighbours". 4) Hover "30 Oct 2026" on "the seven grids together" and on PJM. 5) Hover any unit ("Bcf/d"). 6) "Natural gas trade": hover 16.60 (LNG exports, all terminals); read "Sabine Pass, Louisiana". 7) "Crude and product trade": hover −6,382 (product net imports).

## Needs the key

- Nothing.

## Decisions made without you

- A held grid's cleared row is held on the page, by grid, as the price board holds a held grid's rows: NYISO (its table is in `license_status.json`) and ISO-NE (its table is internal by the note's own reading, and ISO-NE is a held grid).
- The page's fixes are hovers and words only; no figure moved, no row added or dropped.

## For Samuel's ruling

- Read rows 15, 18, 19, 20, 21 and 27, each with its default taken: CAISO's five-year columns unnamed in the note (default: unchanged); "tighter" on coal and oil burn (default: unchanged); an A and B of two grids (default: none added); a grid's net imports drawn here (default: linked, not drawn); a near-zero series leading the surprise list (default: unchanged); the ask panel reading the unheld file (default: not changed here).

## Rows for the coordinator

### (a) Landing request, row 39

| 39 | `wip/7541-supply-read` | `<head>` | `7541-supply-read` | 7541 | 2026-11-16 | `site/scripts/test-supply-read.mjs` (10 of 10, the page drawn whole without a build on the site's file after the day's hold); `site/scripts/test-supply.mjs` (9 of 9); `tests/test_session134`, `136`, `241a`, `247`, `281`, `333`: 91 passed; `tsc` on `lib/supply.ts`: exit 0; not built here (memory); `check-supply` and `check-routes` not run | requested |

## Row 39: what it holds (chain 304, part C, session 7541, `/supply` read as a utility planner or a fund analyst)

- **Stacked on** origin/main at `7363f1a81`. Report: `archive/sessions/SESSION_7541_REPORT.md` on the branch. Squash at landing (one held figure in `dde2f1d30`, removed in `b7d535b7c`).
- **What changes:** `/supply` (`site/app/supply/page.tsx`, `site/lib/supply.ts`): NYISO's and ISO-NE's day-ahead cleared rows read "license needed" with no figure; hovers on the heads "On last year" and "Last 52", on every unit, on the date of a burn row older than another grid's, on each monthly gas trade figure (the month's volume) and on a net import below zero; a links line under the burn table to each grid's Mix and Network views on the Grid page; state names in full in the LNG places. `site/scripts/check-supply.mjs` and `test-supply.mjs` follow the hold. New: `site/scripts/supply-read-page.mjs`, `site/scripts/test-supply-read.mjs`, `docs/reviews/supply-read-2026-11-16.md`.
- **What does not change:** every other checked number of the page (the same keys and rows), the charts, the decisions block, `site/data/supply.json`, the builder, the method note, the replication, `site/lib/release.ts`, every table.
- **Before landing:** a site build on the landing machine; `check-supply.mjs` on the built site (its cleared check now expects "license needed" for each held grid); `check-values` on `/supply` (two fewer `data-n` keys: `cleared-nyiso|last` and `cleared-iso-ne|last`, held).
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review). With the review cookie: on `/supply` the two held rows, the links line, the state names, the new hovers. **Tables:** none.
- **After the landing:** rows 176 to 180 of `docs/state/browser_reads_wanted.md`; data request rows 149 to 154.

### (b) Browser reads, rows 176 to 180

| 176 | 2026-11-16 | 7541 | `wip/7541-supply-read` (row 39) | `https://erw-flame.vercel.app/supply`, at 1280 px | Hover the heads "On last year" and "Last 52"; a unit ("Bcf/d"); "30 Oct 2026" on the seven grids' gas burn; 16.60 on LNG exports, all terminals; −6,382 on product net imports | Each tip shows on its cell and inside the page: the 52-week base and the price board's 365 days; "the last 52 values held"; "billion cubic feet a day"; "The newest week all seven grids hold whole ... not yet for CAISO, ISO-NE, PJM"; "514.6 Bcf in the month, about 514,600 MMcf"; "Below zero ... (net exports)" | wanted |
| 177 | 2026-11-16 | 7541 | `wip/7541-supply-read` (row 39) | `https://erw-flame.vercel.app/supply?g=burn` | The line under "Fuel burned for power in the seven grids": click ERCOT "mix", back, ERCOT "neighbours" | The Grid page opens on ERCOT's Mix view, then on its Network view with what ERCOT takes from and sends to each neighbour by month | wanted |
| 178 | 2026-11-16 | 7541 | `wip/7541-supply-read` (row 39) | `https://erw-flame.vercel.app/supply?g=cleared` | The NYISO and ISO-NE rows | "license needed" across each row, "NYISO: the publisher's own page asks for permission; none is recorded yet" on hover, no figure and no trend line; ERCOT, CAISO, SPP and SPP West keep their figures | wanted |
| 179 | 2026-11-16 | 7541 | `wip/7541-supply-read` (row 39) | `https://erw-flame.vercel.app/supply`, at 390 px | The burn table's links line and every table | The links line wraps inside the page; each table scrolls in its own frame; no sideways scroll of the page | wanted |
| 180 | 2026-11-16 | 7541 | `wip/7541-supply-read` (row 39) | `https://erw-flame.vercel.app/supply?g=gastrade` | The LNG rows' places | "Sabine Pass, Louisiana", "Corpus Christi, Texas", "Cove Point, Maryland", "Elba Island, Georgia"; no "LA" or "TX" | wanted |

### (c) Data requests, rows 149 to 154

| 149 | 2026-11-16 | 7541 (chain 304, samueloldlaptop; branch `wip/7541-supply-read`) | `site/data/board.json` (`warehouse/derived/board_page.py`), the "y" move of a weekly series | The year base of a weekly series is the newest value at least 365 days back: for EIA's storage week ending 2026-11-06 it is 2025-10-31 (Lower 48 −43 Bcf), while EIA's report and `/supply` set the week beside the same week a year before, 2025-11-07 (−88). Take a weekly series' year base as the value 364 days back, or the nearest within 3 days, as `warehouse/derived/supply_page.py` does | EIA, Weekly Natural Gas Storage Report (its "year ago" column); `docs/methods/supply_and_trade.md`, "The three comparisons" | requested |
| 150 | 2026-11-16 | 7541 (same) | `site/data/supply.json`, the burn rows (`warehouse/derived/supply_page.py` over `generation_mix_hourly`) | No whole week ending 2026-11-06 for CAISO's and ISO-NE's gas burn and PJM's gas, coal and oil, in the file built 2026-11-16 12:00 UTC, while ERCOT, MISO, NYISO and SPP hold it. Find which hours of 31 Oct to 6 Nov (local) are not held for the three grids, pull them if EIA-930 (or CAISO's own supply by fuel) has them, and rebuild | EIA-930 hourly generation by source; CAISO, Today's Outlook supply by fuel | requested |
| 151 | 2026-11-16 | 7541 (same) | the same rows | Weeks missing inside the last year: 17 of 52 from 2025-11-07 to 2026-10-30 for "the seven grids together" (7 Nov; 5, 12, 19 Dec; 20, 27 Feb; 13 Mar; 8, 22, 29 May; 5 Jun; 24 Jul; 21 Aug; 11, 18, 25 Sep; 16 Oct); SPP 20 and 27 Feb, 8, 22, 29 May, 5 Jun, 24 Jul, 18 Sep; CAISO 5 Dec, 13 Mar, 21 Aug, 25 Sep, 16 Oct; PJM 7 Nov 2025, 5 Jun 2026. For each, name the hours missing from `generation_mix_hourly` and fill those EIA-930 holds | EIA-930 hourly generation by source | requested |
| 152 | 2026-11-16 | 7541 (same) | `caiso_dam_cleared_energy`, `spp_dam_cleared_energy` (and the `site/data/supply.json` cleared rows) | The weeks ending 2026-10-30 and 2026-11-06 are not whole for CAISO, SPP and SPP West (the rows jump from 23 Oct to 13 Nov), so no cleared row has a week's change. Find the missing days and pull them from the operators' own reports | CAISO OASIS ENE_SLRS; SPP Marketplace DA-MC | requested |
| 153 | 2026-11-16 | 7541 (same) | `ercot_dam_cleared_energy` | The newest whole week is the one ending 2026-10-23 (and 16 Oct is missing): the weeks ending 30 Oct, 6 Nov and 13 Nov are not whole in the file built 2026-11-16. ERCOT lists 31 days of NP4-192-CD; pull the days still listed before they fall off | ERCOT, NP4-192-CD, DAM Total Energy Purchased | requested |
| 154 | 2026-11-16 | 7541 (same) | `site/data/supply.json` (`warehouse/derived/supply_page.py`) | The committed page file holds NYISO's cleared row (its table held for a license since 2026-10-21) and ISO-NE's (internal by the note) with their figures; the page now holds both before it draws, but the repository is public. Write a held grid's cleared row with status and note only (no last, prev, year, avg5, change, spark, season), by `site/data/license_status.json` and the grid prefixes of `site/lib/license.ts` | `site/data/license_status.json`; `docs/methods/supply_and_trade.md`, "The operators' terms" | requested |

### (d) Progress, part C

done `<head>` on `wip/7541-supply-read` (landing row 39): the reader a utility planner or a fund analyst reading what fuels a grid's supply, the country's imports and exports, and how each moved over named weeks and months; five cases (ERCOT's burn, week ending 6 Nov 2026; ISO-NE going into winter; PJM against MISO; gas exports, August 2026; crude and product trade, week ending 6 Nov 2026); rows: 27 (9 site fixed, 6 data machine, 5 browser, 6 rulings, 1 license); test-supply-read 10 of 10
