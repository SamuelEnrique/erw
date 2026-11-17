# Session 7540 report: "Where power is cheap" (`/prices/compare`) read as a fund analyst (chain 304, part C)

samueloldlaptop, 16 November 2026. Branch `wip/7540-compare-read`, worktree `C:\Users\lossa\Documents\erw-7540`, from origin/main `18acd9b5f`. Model spend USD 0; no model API called.

## What was done

- The read: `docs/reviews/compare-read-2026-11-16.md`. The reader: a fund analyst setting two hubs or two grids side by side (A and B) over the same months to choose where a project earns more. Five cases (West hub against Houston hub; North hub against SPP North for a 4-hour battery; SP15 against NP15 in September 2026; New York City zone against ISO-NE Internal Hub; West hub here and on the cost of power page). 22 rows: 9 site (fixed), 5 data machine, 3 browser, 4 rulings, 1 license.
- **The page drew license-held figures.** `hub_price_comparison` is held for ISO-NE, MISO and NYISO from 21 October 2026, and the page drew every ISO-NE and NYISO figure; in the default view its "highest average price" and "widest daily spread" were held figures. Now held on the server, named, "license needed" (row 1). The builder's site copy still carries them in the public repository: data request 139 (row 2).
- **The windows are pinned at September 2026 by MISO's pause** (row 5): the end month is taken over every side of `iso_hub_prices_history`, MISO's paused Indiana hub included. Data request 140. Part A's faults row 2 called it "not a fault".
- **A and B, side by side** on the page, both markets, B less A (rows 3, 4). The words: clock time, the spread is the average day's (each day's own is 8 to 96 percent larger at the five hubs read, both markets), ERCOT's two averaged hubs, ERCOT's load zones named as not compared, no grey text of the page's own (rows 6 to 13).
- The page is drawn whole without a build: `site/scripts/font-stub-loader.mjs` (new) stands in for `next/font/google`, so `<Brand>` loads and the async page function is called and drawn.
- Tests: `site/scripts/test-compare-read.mjs` 73 of 73; `tests/test_session7540_compare_read.py` 5 passed; `test_session96`, `test_session1586`, `test_session281`, `test_session7018_compare_done`, `test_session242`, `test_session114_part2.BuiltDate`: 40 run, 35 passed, 5 skipped by their own rules (no built table on this machine, no served site). `tsc --noEmit` on the page and the lib (a narrowed config, removed after): no error. No build (memory).
- **Files of the other machine's stack touched** (lab-desktop, chain 301): `site/app/prices/compare/page.tsx`, `site/lib/pricecompare.ts` (new exports only; `href` takes optional `a` and `b`, unchanged without them), `site/scripts/check-prices-compare.mjs` (applies the same hold), `docs/methods/hub_price_comparison.md` (one dated section added). Not touched: the builder, the page file, the faults file, `replication/compare/`, `site/lib/decisions.ts`, `site/components/Num.tsx`, `site/lib/release.ts`.

## What to review

1. `https://erw-flame.vercel.app/prices/compare` (in review: unlock first). The table and the chart end with "ISO-NE, Internal Hub" and "NYISO, New York City zone", each cell "license needed"; hover one: "ISO-NE; MISO; NYISO: the publisher's own page asks for permission; none is recorded yet". The sentence's highest is "ERCOT, Houston hub, USD 35.22"; the headline's widest spread "ERCOT, West hub, 37.92".
2. Under the headline numbers, "A and B, side by side": choose A "ERCOT, West hub", B "ERCOT, Houston hub", "Set side by side". Day-ahead average 33.00 and 35.22, B less A +2.22; real time below zero 12.01 and 1.62, -10.39.
3. With A and B chosen, click "September 2026", then "Real-time", then a heading: A and B stay chosen. Choose a zone in the month, then "Twelve months": it reads "not in this period".
4. Hover "ERCOT, Hub Average" in the table; read the table's note (clock time; the spread is not the mean of each day's own spread) and "What this does not tell you" (ERCOT's eight load zones).
5. At 390 px: the two lists and the button fit; the A and B table scrolls in its own frame.

## Needs the key

Nothing.

## Decisions made without you

- Held rows stay in the table and the chart, last, every cell "license needed", rather than leaving them off (the page standard: a held value is drawn blank, nothing dropped). The sentence and headline count the rows shown.
- The hold is applied on the server from `licenseHeldRow`, as the price board does; the hold logic is unchanged.
- A and B starts empty (no pair chosen for the reader) and shows both markets and the grid's carbon.
- The spread's fault is said in words only: no figure the table does not hold is drawn (the day-by-day spread is asked of the data machine).
- The lead's "Every public hub and zone price the warehouse holds" became "The hub and zone prices of five grids", since ERCOT's load zones are held and not compared.

## For Samuel's ruling

- Row 15: ISO-NE's and NYISO's carbon intensity (EIA-930, public) is drawn "license needed" because the row is held by grid. Default: unchanged.
- Row 16: two windows only. Default: two windows; the other choice is monthly rows, the reader choosing the months.
- Row 17: clock time here, standard time on the cost of power tool. Default: each keeps its own, both said.
- Row 18: the shared input panel's note is grey on every tool. Default: unchanged.
- Row 2 (with the data machine): the figures of ISO-NE and NYISO already committed in `site/data/price_compare.json` stay in the repository's history. Default: no history rewrite; the builder stops writing them.

## Rows for the coordinator

### (a) Landing request, row 38

| 38 | `wip/7540-compare-read` | `491d75f54` | `7540-compare-read` | 7540 | 2026-11-16 | `site/scripts/test-compare-read.mjs` (73 of 73, the page drawn whole on the site's file after the day's hold, five cases); `tests/test_session7540_compare_read.py` (5 passed); `test_session96`, `1586`, `281`, `7018_compare_done`, `242`, `114_part2.BuiltDate`: 35 passed, 5 skipped by their own rules; `tsc` on the page and the lib: no error; no build made here | requested |

## Row 38: what it holds (chain 304, part C, session 7540, where power is cheap read as a fund analyst setting two hubs side by side)

- **Stacked on** origin/main `18acd9b5f`. Report: `archive/sessions/SESSION_7540_REPORT.md` on the branch (one commit on top of `491d75f54`).
- **What changes:** `site/app/prices/compare/page.tsx` (ISO-NE's and NYISO's rows held on the server, named, every cell "license needed", in the table, the chart, the sentence and the held section; "A and B, side by side" with both markets and B less A; A and B ride on every link; the Hub Average and Bus Average hovers; the table note's clock time and spread words; the lead; ERCOT's load zones in "What this does not tell you"; "not held" and the grids line in ink), `site/lib/pricecompare.ts` (new pure exports `hold`, `heldGrids`, `pairOf`, `NAME_WORDS`, type `HeldRow`; `href` takes optional `a` and `b`), `site/scripts/check-prices-compare.mjs` (checks against the same hold), `docs/methods/hub_price_comparison.md` (one dated section added). New: `site/scripts/test-compare-read.mjs`, `site/scripts/font-stub-loader.mjs`, `tests/test_session7540_compare_read.py`, `docs/reviews/compare-read-2026-11-16.md`.
- **What does not change:** `warehouse/derived/price_compare.py`, `site/data/price_compare.json`, `replication/compare/`, `docs/reviews/price-compare-faults-2026-11-16.md`, `site/lib/decisions.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, any table. No figure of a shown row changes; the `data-n` marks of held rows are gone (they were held figures); new marks `ab|...` for A and B.
- **Before landing:** a site build on the landing machine; `node --import ./scripts/alias-loader.mjs scripts/check-prices-compare.mjs <served address>` on the build (it now expects the held rows named with no number); `node --import ./scripts/tsx-register.mjs scripts/test-compare-read.mjs`.
- **Snapshot differences to expect:** none on the 25 addresses (`/prices/compare` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** rows 166 to 168 of `docs/state/browser_reads_wanted.md`; rows 139 to 143 of `docs/state/data_requests_done_line.md` are the data machine's and do not hold this row.

### (b) Browser reads, rows 166 to 168

| 166 | 2026-11-16 | 7540 | `wip/7540-compare-read` (row 38) | `https://erw-flame.vercel.app/prices/compare?a=ercot%3AHB_WEST&b=ercot%3AHB_HOUSTON` | "A and B, side by side" at 1280 and 390 px; press "Set side by side" after choosing B "SPP, North hub" | Day-ahead 33.00 and 35.22, B less A +2.22; both markets one under the other; at 390 px the two lists and the button fit and the table scrolls in its own frame, the page does not; after the press the period, market and order are as before and B reads SPP, North hub | wanted |
| 167 | 2026-11-16 | 7540 | `wip/7540-compare-read` (row 38) | `https://erw-flame.vercel.app/prices/compare` and `?period=month&market=dam&sort=avg` | ISO-NE's and NYISO's rows in the table and the chart; hover a "license needed"; view the page source | 2 held rows in the twelve months, 20 in the month, last, every cell "license needed"; the hover names ISO-NE; MISO; NYISO; no figure of theirs in the source; the sentence's highest is a CAISO, ERCOT or SPP row | wanted |
| 168 | 2026-11-16 | 7540 | `wip/7540-compare-read` (row 38) | `https://erw-flame.vercel.app/prices/compare?a=ercot%3AHB_NORTH&b=spp%3ASPPNORTH_HUB&sort=carbon` | Hover "ERCOT, Hub Average" and SPP's "not held"; click "September 2026", "Real-time" and the heading "Spread, 4 hours" | Each hover shows its words (the four hubs' average; fewer than 95 percent of hours, 90 percent of days); every click keeps A and B chosen | wanted |

### (c) Data requests, rows 139 to 143

| 139 | 2026-11-16 | 7540 (chain 304, samueloldlaptop; branch `wip/7540-compare-read`) | `site/data/price_compare.json` (`warehouse/derived/price_compare.py`, the site's view) | `hub_price_comparison` is held for ISO-NE, MISO and NYISO from 21 October 2026, and the site copy rebuilt on 16 November 2026 carries every figure of ISO-NE's 9 and NYISO's 11 rows in the public repository. The page now holds them (session 7540). Write a held grid's rows in the site copy as names only (entity, grid, node), as MISO's are written in `held_not_shown`, so no held figure is committed; the table itself unchanged | `site/data/license_status.json`; the read's row 2 | requested |
| 140 | 2026-11-16 | 7540 (chain 304, samueloldlaptop; branch `wip/7540-compare-read`) | `hub_price_comparison` (`warehouse/derived/price_compare.py`, `last_whole_month`) | The windows end with the last month every side of `iso_hub_prices_history` holds to its end, MISO's Indiana hub included; its pulls are paused since 4 October 2026 (newest day-ahead hour 2026-10-04T04:00Z, real time 2026-10-03T04:00Z on this machine's copy of 22 October), so every window stays at September 2026 while the pause lasts, though every hub shown holds October whole. Take `last_whole_month` over the sides of the grids compared (leave out the paused and held-not-shown grids), rebuild the table and the site copy; expected: windows to October 2026. Part A's faults row 2 to be read again | the read's row 5 | requested |
| 141 | 2026-11-16 | 7540 (chain 304, samueloldlaptop; branch `wip/7540-compare-read`) | `hub_price_comparison` | Add `<m>_daily_spread_mean_top4_bottom4` for both markets: the mean over the window's whole days of each day's four dearest less four cheapest hours. From the cost of power tool's year files (standard time), twelve months to September 2026, real time: ERCOT North 54.92 against 38.25 drawn, SPP North 77.95 against 39.81, ERCOT West 60.71 against 39.69. A page row follows on a laptop once the column exists | the read's rows 8 and 9 | requested |
| 142 | 2026-11-16 | 7540 (chain 304, samueloldlaptop; branch `wip/7540-compare-read`) | `hub_price_comparison` (inputs) | Add ERCOT's eight load zones (`ercot_zone_prices_history`, held from 2015) to the comparison, both windows, so a reader can set LZ_WEST beside HB_WEST; `NAMES` in `site/lib/pricecompare.ts` will need their reader's names | the read's rows 10 and 11 | requested |
| 143 | 2026-11-16 | 7540 (chain 304, samueloldlaptop; branch `wip/7540-compare-read`) | `carbon_intensity_daily` (`eia930:SWPP`) | 236 of 365 days of SPP's carbon intensity are held over October 2025 to September 2026, so the twelve months draw "not held". Find the 129 missing days and fill them from EIA-930 where the source holds them; rebuild `hub_price_comparison` | EIA-930; the read's row 14 | requested |

### (d) The progress line (part C of `docs/state/progress_c304.md`)

| `/prices/compare` | lab-desktop | done `491d75f54` on `wip/7540-compare-read` (landing row 38): the reader a fund analyst setting two hubs or two grids side by side over the same months to choose where a project earns more; five cases (ERCOT West against Houston hub; ERCOT North against SPP North for a 4-hour battery; CAISO SP15 against NP15 in September 2026; NYISO New York City against ISO-NE Internal Hub; ERCOT West here and on the cost of power page); rows: 22 (9 site fixed, 5 data machine, 3 browser, 4 rulings, 1 license); the page drew ISO-NE's and NYISO's license-held figures (now held); MISO's pause pins the windows at September 2026 (data request 140); browser reads 166 to 168, data requests 139 to 143 | 7540 |
