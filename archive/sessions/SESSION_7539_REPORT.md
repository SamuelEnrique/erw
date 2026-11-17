# Session 7539 report: `/prices` read as a fund analyst (chain 304, part C, samueloldlaptop, 16 November 2026)

Branch `wip/7539-prices-read` (worktree `C:\Users\lossa\Documents\erw-7539`), from origin/main `7f19f5549`. The read file: `docs/reviews/prices-read-2026-11-16.md`.

## What was done

- The reader: a fund analyst or a merchant developer comparing hub prices, their peaks and their spread across grids and months. Five cases: ERCOT West against Houston, day-ahead, October 2026; CAISO SP15 against NP15, real time, the page's 30 days; ERCOT Hub Average, SP15 and SPP North side by side for a month; ERCOT Hub Average real time less day-ahead; New York City, ISO-NE and MISO.
- Both pages drawn whole to HTML by their own functions without a build (`site/scripts/prices-read-page.mjs`, with `prices-read-register.mjs` and `prices-read-loader.mjs`: a stand-in for `next/navigation` that carries `notFound`), on the live set's public rows at 23:20 UTC (ERCOT, CAISO, SPP; no held row saved).
- 21 rows: 9 site rows fixed with a test (`site/scripts/test-prices-read.mjs`, 26 of 26, on 7,394 committed public rows `site/scripts/prices-read-rows.csv`, with a check that no held grid's row is in them), 2 data machine, 5 browser, 4 rulings, 1 license.
- The fixes: a held grid's section names its main hub or zone with "license needed" cells instead of "license needed" followed by "no data: no NYISO rows"; a hub page's high and low say when they fell (UTC and the grid's clock); its interval count reads "2,428 of 2,812" with the days missing on hover; a new row "Real time less day-ahead, the hours both hold" (ERCOT Hub Average 0.55 over 607 hours, where the two means read -0.01); variables and hubs in words, codes on hover; the SPP page no longer says the ERW has no SPP real-time table; the lead links `/prices/compare`; the site's index line of `/prices` no longer promises Henry Hub, WTI and Brent.
- The method note `docs/methods/power_prices.md`: a section added, "A hub's page, as read by session 7539".

## Files of the other machine's stack touched (lab-desktop's chain 301 took `/prices` to the done line)

- `site/app/prices/page.tsx`, `site/app/prices/[entity]/page.tsx`, `docs/methods/power_prices.md` (a section appended). New: `site/lib/pricehub.ts`. Shared: `site/lib/pages.ts` (the `/prices` line and its tables string only). Read, not changed: `site/lib/pricecompare.ts` (its `label` is imported), `site/data/markets.json`, `replication/prices/`.

## Tests run

- `site/scripts/test-prices-read.mjs`: 26 of 26.
- Every test file that names `app/prices`, `lib/pages`, `pricecompare` or `PRICES_DECISIONS` (40 files): 536 passed, 28 skipped, 1 failed: `test_session156.py::TheNodeTests::test_the_sessions_own_tests_pass_with_no_request_and_no_switch_set` (`test-ask-ready.mjs`, 9 of 20), which fails the same way on the main copy at `18acd9b5f` (not this branch).
- The ten test files that name `power_prices`: 395 passed, 1 skipped.
- A narrow `tsc` (the site's settings, the two page files, `lib/pricehub.ts`, `lib/pages.ts`): exit 0. Not built here (memory: 1.7 GB free). `check-values` and `check-routes` not run.

## What to review

- `https://erw-flame.vercel.app/prices`: under the title, the lead's last sentence links "where power is cheap"; the ERCOT, CAISO and SPP tables' "Interval start (UTC)" column reads "(15-minute settlement point price)" or "(5-minute locational price)", the code on hover; hover a hub's code for its name ("ERCOT, West hub"); the NYISO, MISO and ISO-NE sections each show one row (New York City zone, Indiana Hub, Internal Hub) with two "license needed" cells and no "no data" box.
- `https://erw-flame.vercel.app/prices/ercot%3AHB_HUBAVG`: under the code, "ERCOT, Hub Average"; the legend in words; in the table "2,428 of 2,812" (hover: the days 6, 7 and 8 November with no row); hover "Max" 565.21 (22:00 CST, 11 November); the new row "Real time less day-ahead": 607 hours, -100.24, 0.55, 281.92.
- `https://erw-flame.vercel.app/prices/spp%3ASPPNORTH_HUB`: the note under the chart says the page draws no SPP real-time series because `site/data/markets.json` names none.

## Needs the key

- Nothing.

## Decisions made without you

- The new hub-page figures (the count due, the real time less day-ahead row, the times of the high and low) are drawn as plain cells, not through the checked-number component: they are computed on the page from rows that are themselves the table's, as the min, mean and max were.
- `site/data/markets.json` was not changed for SPP (row 14): a dozen files of the site read it.
- The read's fixture holds three hubs only (ERCOT Hub Average, SP15, SPP North) and `latest_prices`, to keep it near 600 KB.

## For Samuel's ruling

- Row 10: a month on `/prices`. Default: none; months are `/prices/compare`'s, now linked.
- Row 11: two hubs side by side on a hub's page (`?vs=`). Default: not added.
- Row 14: name SPP's real-time table in `site/data/markets.json`. Default: unchanged; naming it draws SPP's real time on its hub pages and moves `/network`'s SPP price from day-ahead to real time.
- Row 16: on-peak and off-peak on a hub's page. Default: none (the board has them).

## Rows for the coordinator

### (a) Landing request, row 37

| 37 | `wip/7539-prices-read` | `bbcc0a757` | `7539-prices-read` | 7539 | 2026-11-16 | `site/scripts/test-prices-read.mjs` (26 of 26, both pages drawn whole to HTML without a build on 7,394 committed public rows, at their render time); the 40 test files that name `app/prices`, `lib/pages`, `pricecompare` or `PRICES_DECISIONS`: 536 passed, 28 skipped, 1 failed (`test_session156`, `test-ask-ready.mjs`, which fails the same way on main at `18acd9b5f`); the ten files naming `power_prices`: 395 passed; narrow `tsc` exit 0; not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 37: what it holds (chain 304, session 7539, `/prices` read as a fund analyst)

- **Stacked on** origin/main at `7f19f5549`. Report: `archive/sessions/SESSION_7539_REPORT.md` on the branch.
- **What changes:** `/prices` (`site/app/prices/page.tsx`): one sentence in the lead with a link to `/prices/compare`; the real-time interval column says each operator's interval in words (code on hover); each hub link has its name on hover; a held grid's section (NYISO, MISO, ISO-NE) draws its main hub or zone with two "license needed" cells instead of "license needed" and a "no data" box. `/prices/<hub>` (`site/app/prices/[entity]/page.tsx`): the hub's name under its code; the legend and the latest line in words; the count "N of M" with the days missing on hover; the high and low with their times on hover; a new row "Real time less day-ahead, the hours both hold"; the SPP note's words. New: `site/lib/pricehub.ts`, `site/scripts/prices-read-page.mjs`, `prices-read-register.mjs`, `prices-read-loader.mjs`, `test-prices-read.mjs`, `prices-read-rows.csv`, `docs/reviews/prices-read-2026-11-16.md`; a section appended to `docs/methods/power_prices.md`; `site/lib/pages.ts`, the `/prices` line and tables string.
- **What does not change:** every checked number of both pages (the same keys and rows), the chart, the decisions block, `site/data/markets.json`, `site/lib/pricecompare.ts`, the ERCOT tab, `site/lib/release.ts`, every table.
- **Before landing:** a site build on the landing machine (the first build of `lib/pricehub.ts` and the two pages' changes); `check-values` on `/prices` and one hub page (the same keys); `check-methods.mjs` (no new key).
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review). With the review cookie: on `/prices` the lead's new sentence, the interval column's words, the three held grids' rows; on `/prices/<hub>` the name line, the legend words, the counts "of M", the new row, the SPP note. Any page that lists `/prices` by its index line (the page lists, the data page) reads the new line. **Tables:** none.
- **After the landing:** rows 156 to 160 of `docs/state/browser_reads_wanted.md`; data request rows 129 and 130.

### (b) Browser reads, rows 156 to 160

| 156 | 2026-11-16 | 7539 | `wip/7539-prices-read` (row 37) | `https://erw-flame.vercel.app/prices/ercot%3AHB_HUBAVG` | Hover the real-time "Max", the "Min", the count "2,428 of 2,812", and the row "Real time less day-ahead"'s name, low and high | "The highest interval starts 2026-11-12 04:00 UTC (Nov 11, 2026, 22:00 CST)" (or the newest window's own); the count's hover names the UTC days with no row; the row's hover says why the two means' difference is not it; each hover shows whole and stays inside the page | wanted |
| 157 | 2026-11-16 | 7539 | `wip/7539-prices-read` (row 37) | `https://erw-flame.vercel.app/prices/ercot%3AHB_WEST` at 390 px | The table under the chart, four rows | No sideways scroll of the page; the table scrolls inside its own frame; "of 2,812" does not wrap a number | wanted |
| 158 | 2026-11-16 | 7539 | `wip/7539-prices-read` (row 37) | `https://erw-flame.vercel.app/prices#nyiso` (and `#miso`, `#iso-ne`) | Each held grid's section; hover a "license needed" cell and the hub's code | One row: N.Y.C., INDIANA.HUB, .H.INTERNAL_HUB, each marked "main", two cells "license needed", the publisher's words on hover, the zone's name on the code's hover; no dashed "no data" box | wanted |
| 159 | 2026-11-16 | 7539 | `wip/7539-prices-read` (row 37) | `https://erw-flame.vercel.app/prices` at 390 px | The ERCOT and CAISO tables | The interval column's words ("15-minute settlement point price") do not push the page sideways; each table scrolls inside its frame | wanted |
| 160 | 2026-11-16 | 7539 | `wip/7539-prices-read` (row 37) | `https://erw-flame.vercel.app/prices` | Click "where power is cheap" in the lead | `/prices/compare` opens on its default view | wanted |

### (c) Data requests, rows 129 and 130

| 129 | 2026-11-16 | 7539 (chain 304, samueloldlaptop; branch `wip/7539-prices-read`) | `iso_hub_prices_history`, the ERCOT histories, `hub_price_comparison` (`site/data/price_compare.json`) | On 16 November 2026 `/prices/compare`'s "last whole month" is September 2026 and its twelve months end there: the history tables it is built from do not hold October 2026 whole (`docs/reviews/price-compare-faults-2026-11-16.md`, row 2), while `iso_dam_hub_prices` holds October whole for ERCOT and CAISO (744 hours a hub). Extend the histories through October 2026 and rebuild the comparison, so a reader comparing hubs over a month reads October | the operators' hub price files as each history names them; the read's row 12 | requested |
| 130 | 2026-11-16 | 7539 (chain 304, samueloldlaptop; branch `wip/7539-prices-read`) | `iso_rtm_hub_prices` (ERCOT, market `ercot_rtm`) | The live set holds no ERCOT real-time row on 6, 7 and 8 November 2026 (UTC days) at any of the six hubs: 2,428 of the 2,812 15-minute intervals from 17 October 23:00 to 16 November 05:45 UTC. Pull ERCOT's settlement point prices for those days and reload. (The day-ahead's 7 and 8 November are request 121.) | ERCOT, NP6-905-CD Settlement Point Prices at Resource Nodes, Hubs and Load Zones; the read's row 13 | requested |

### (d) The progress line, part C

| `/prices` | lab-desktop | done `bbcc0a757` on `wip/7539-prices-read` (landing row 37): the reader a fund analyst or merchant developer comparing hub prices, their peaks and their spread across grids and months; five cases (ERCOT West against Houston, day-ahead, October 2026: 36.79 against 38.09, West less Houston -1.30, from the table, not on the page; CAISO SP15 and NP15 real time, highs 149.29 and 169.88 both at 20:00 Pacific on 20 October, now on hover; ERCOT Hub Average, SP15 and SPP North for a month: September 38.80, 40.77, 36.21 on `/prices/compare`, equal to the table, October on no page; ERCOT Hub Average real time less day-ahead: 0.55 over 607 hours where the page's two means read -0.01, now a row; New York City, ISO-NE and MISO held); the hub page's high 926.42 at ERCOT West agrees with `/board`'s week table; rows: 21 (9 site fixed, 2 data machine with requests 129 and 130, 5 browser 156 to 160, 4 rulings, 1 license) | 7539 |
