# The prices pages and the price heatmap: the model audited as a hostile expert would

Session 10218, 26 November 2026, chain 710 (part D), the old laptop. Read as a power trader and as a large buyer comparing regions for a load, who would pick a market with these pages and wants to find them wrong. Platform tool 8 (the regional power-price heatmap: the Grid tool map's "Price" colors, `/grid/prices-map`) and the price pages (`/prices`, `/prices/<hub>`, `/prices/compare`). In the form of `docs/reviews/trader-model-audit-2026-11-26.md` and `docs/reviews/board-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/prices-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-prices-<n>`. Branches that change only words are for landing (the rows at the foot), and merged together as `wip/audit-prices-words`; the branch whose fix would move a figure carries the test only and is not for landing.
- **Not repeated:** the read of `/prices` of 16 November (`docs/reviews/prices-read-2026-11-16.md`, rows 1 to 21: the held grid's words of that day, the high and low with their hours, the intervals held, real time less day-ahead over the hours both hold, the variable codes, SPP's real time not named in `markets.json`, no month and no A and B), the read of `/prices/compare` (`compare-read-2026-11-16.md`, rows 1 to 22: the hold, A and B, clock against standard time, the average day's spread against each day's, ERCOT's two averaged hubs, SPP's carbon days) and its faults file (`price-compare-faults-2026-11-16.md`: the hour of zero), the ruling files of 17 November, and tonight's board and trader audits (the board's kept rows and on-peak blocks, the trader view's off-peak weighting and gas day).

## In short

- **The arithmetic is right.** An independent restatement written from the method notes with the standard library gives every figure of `/prices/compare`'s file from the warehouse's price tables (662 of 666 to the cent; the 4 others are CAISO's carbon intensity, one of whose 345 days this machine's carbon table lacks), every figure the page draws in four views (450 of 456, the 6 others the same carbon), every figure `/prices` and a hub's page draw at a fixed render time on this machine's tables (32 of 32), and the map's price file from the page's own hourly files (145 of 152 to the cent, 3 by 0.01 from hours rounded to the cent, 4 not drawn).
- **`/prices/compare` said ERCOT's eight load zones are not compared, and counted them as hubs (finding 1, Medium, words).** They have been in both periods since session 7052: 8 of the 17 rows of the twelve months. The default view names "ERCOT, Austin Energy load zone" the dearest of "the 17 hubs compared". Words fixed.
- **The comparison lacks real-time hours the site's own hourly files hold (finding 2, Medium, a figure).** SPP North's and SPP South's October real time read "not held" while the board's hourly files hold all 744 hours (34.35 and 25.30); CAISO ZP26's October real time is 45.35 on 720 hours against 44.88 on 744; SPP North's twelve months 31.66 on 8,568 hours against 31.77 on 8,760. A rebuild is the cure: data request, and a line for Samuel.
- **"Average price" is each hour once, a flat load's price, unsaid (finding 3, Medium, words).** Weighted by the grid's own hourly load the twelve months' day-ahead average is 4.0 to 7.1 percent higher (ERCOT's Hub Average 34.39 to 36.41 over the hours both hold; CAISO SP15 30.01 to 31.42). Words fixed; a load-weighted column would be a figure.
- **A held grid on `/prices` and its hub's page said its tables had no rows (finding 4, Low, words).** `latest_prices` carries NYISO's and ISO-NE's newest intervals as public (and MISO's of 4 October), so session 7539's held drawing did not apply. No held figure reached the page (`Num` holds it). Words fixed.
- **The map's legend gave no date (finding 5, Low, words).** On 26 November "Day-ahead, the newest day" is 16 November (the file built 19 November) while the site's own hourly files hold days to 20 November (ERCOT) and 25 November (CAISO, SPP); on 20 November CAISO, not ERCOT, is the dearest area. Words fixed; the rebuild is a data request.
- **Smaller:** a hub's page's day-ahead runs to tomorrow's last hour, up to 36 hours after the real time's, under words that said "the window" (finding 6, Low, words). Checked and right: the time zones and both clock changes (8,760 hours in the twelve months, 721 in the map's 30 days over 1 November), negative prices, the hold on every cell and color, the hour of zero, the 95 percent floor as stated.
- **Five branches fix words and move no figure (1, 3, 4, 5, 6), merged as `wip/audit-prices-words` with no conflict; one shows a figure (2).** Two data requests. Nothing needs the key.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/prices/page.tsx` | `/prices`, two tabs. The first (`NowView`): for each grid of `site/data/markets.json`, every hub and zone of `latest_prices` (the newest real-time interval, refreshed every 15 minutes) and the day-ahead price of the hour holding the render time (`daNow`, from the day-ahead table read since a day before); a held grid's section as its main hub named, both cells "license needed"; the decisions (`PRICES_DECISIONS`); the downloads. The ERCOT tab is the peak premium explorer (not read here) |
| `site/app/prices/[entity]/page.tsx` | `/prices/<hub>`: the newest interval; the chart of the last 30 days (real time and day-ahead read from 30 days before the render, no end); the table of intervals held, min, mean, max, from and to of each market (`stats`), the intervals due and the missing UTC days (`heldOf`), real time less day-ahead over the hours both hold (`realLessDayAhead`) |
| `site/lib/pricehub.ts` | Pure: `stepMinutes`, `heldOf`, `realLessDayAhead`, `VARIABLE_WORDS`, `whenWords` |
| `site/lib/data.ts`, `site/lib/supabase.ts` | `latestPrices` (no table named, so no license hold applies), `series` (a start, no end), `daysAgo` (floored to the hour); `restPaged` refuses a held table by grid (`licenseHold`) |
| `site/components/Num.tsx` | Draws "license needed" for a figure whose check key names a held grid (`latest_prices|nyiso:...`): no held price reaches a page |
| `site/app/prices/compare/page.tsx` | `/prices/compare`, "Where power is cheap": the sentence, three headline numbers, A and B side by side, the bars, the table (average, hours below zero, hours above USD 200, the average day's four dearest less four cheapest hours, the grid's carbon intensity, hours held), the lacking rows, "Held, not shown", "How it is computed", "What this does not tell you", the decisions (`COMPARE_DECISIONS`) |
| `site/lib/pricecompare.ts` | Pure: the choices from the address, `hold`, `pairOf`, `ordered`, `lacking`, the names (`NAMES`, `NAME_WORDS`), `two`, the period's words. No arithmetic: every figure is a row of the file |
| `site/data/price_compare.json` | The site's copy of `hub_price_comparison` (built 17 November 2026, 07:41 UTC; twelve months 1 November 2025 to 1 November 2026 and October 2026, local time): 17 and 19 public rows; 28 held by name (MISO 8, ISO-NE 9, NYISO 11) |
| `warehouse/derived/price_compare.py` | The builder: the price tables in order, an hour of real time from four 15-minute prices, the 95 and 90 percent floors, the measures, the carbon mean, `site_view` (a held grid by name only) |
| `docs/methods/hub_price_comparison.md`, `docs/methods/power_prices.md` | The notes; the replication of 16 November (578 of 578), the decisions |
| `site/app/grid/prices-map/route.ts` | Serves `site/data/regions/prices_map.json` when the reader turns the Grid tool map's color to price |
| `site/components/grid/MapPrice.tsx` | The eight price measures, `priceValue`, `priceRange` (the lowest and highest area shown), `priceLine` (the hover), `PriceControls` (the switch, the measure, the legend), the seven decisions |
| `site/app/network/Network.tsx`, `colorOf` | The color: green at the lowest area shown, fog at the middle of the range, cardinal at the highest, linear between; a blank "not held" color for an area with no figure |
| `site/data/regions/prices_map.json` | Built 19 November 2026, 22:30 UTC: 19 public hubs and zones (CAISO 3, ERCOT 14, SPP 2), each with its newest whole day (16 November; ERCOT's load zones 14 November), and `bas`: one figure set an area, by its grid's main hub (CISO SP15, ERCO Hub Average, SWPP North); ISNE and NYIS held, MISO paused, PJM held, names and reasons only |
| `warehouse/derived/prices_map.py`, `docs/methods/prices_map.md` | The builder (the compare builder's reader and hour rule, the board's on-peak rule and main hubs) and its note |
| `site/public/board/h/<hub>.json` | The board's hourly files (each hour's day-ahead and real-time price to the cent): the restatement of the map, and the second source for finding 2 |

## How every number here was computed

- **The comparison:** `restate_compare.py` (standard library, written from `hub_price_comparison.md`): the public grids' rows of `iso_hub_prices_history`, `ercot_all_hub_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices` and `ercot_zone_prices_history` of the main checkout (read only), in the note's order, each grid's local windows, the hour rules, the floors, the measures, and `carbon_intensity_daily`; `compare_compare.py` sets it against the file figure by figure. This machine's real-time tables lack the local day of 15 October 2026 for CAISO's and ERCOT's hubs (24 hours each); a second run takes those hours, and only those (inside October, for the hubs the file says held all 744), from the page's own hourly files (`fill`).
- **The page drawn:** `draw_compare.mjs` draws `/prices/compare` with its own page function on its own file in four views; `check_drawn.py` makes the page's choices (cheapest, dearest, most hours below zero, widest spread, the order, B less A) again from the restated rows and checks every marked figure.
- **`/prices` and a hub's page:** `draw_prices.mjs` draws both with the pages' own functions (`site/scripts/prices-read-page.mjs`, session 7539's stand-in for the live set) on this machine's tables at 18:00 UTC on 12 November 2026; `latest_prices` is made as each public hub's newest interval at or before that time, and each held grid is given one stand-in row (value 0) to see how the page draws it; `restate_prices.py` restates the figures from the same rows.
- **The map:** `restate_map.py` from the page's own hourly files, written from `prices_map.md`, and the scale's positions; `dump_map.py` lists the file (no held grid holds a figure).
- **One rule at a time:** `measures.py`. Copies of every script and its printout: `docs/reviews/prices-model-audit-2026-11-26/` (written to run from `runs/c10218/` of a worktree).

## The arithmetic re-done

| Figures | Compared | Agree | The gaps |
|---|---|---|---|
| `price_compare.json`, both periods, both markets: average, below zero, above 200, the average day's spread, each day's spread and its days, hours held and due, the step used, carbon days and intensity | 666 | 563 on this machine's tables; 662 with the one local day of real time this machine lacks (15 October) taken from the page's hourly files | 4: CAISO's carbon intensity of the twelve months, 117.58 against 117.72 here, on 345 days against 344 (this machine's carbon table lacks one) |
| The drawn page, four views (the default; A ERCOT West hub, B ERCOT West load zone; the month; real time): the sentence's count, cheapest, dearest and most hours below zero; the three headline numbers; every cell; the hours; the bars' order; A, B and B less A in both markets | 456 | 450 | the same CAISO carbon, 6 cells |
| `/prices`, first tab, at 18:00 UTC on 12 November: each public hub's real-time price and day-ahead price of the hour | 16 | 16 | |
| `/prices/<hub>` for ERCOT Hub Average, ERCOT West, CAISO SP15, SPP North: each market's intervals held of due, min, mean, max, from, to; real time less day-ahead's hours, min, mean, max, first and last | 16 | 16 | |
| `prices_map.json`, 19 hubs: the day's mean, on-peak, off-peak, spread; the 30 and 365 days' mean and share below zero | 152 | 145 to the cent | 3 by 0.01 (the hourly files round each hour to the cent); 4 where the file says CAISO ZP26's and SPP South's twelve months are "under 95%" (1,993 and 1,969 of 8,760 hours) while the board's hourly files hold the year: those two hubs color no area |

- **The default view, as drawn and restated:** "Over the twelve months to October 2026, CAISO, SP15 hub (south) had the lowest average day-ahead price of the 17 hubs compared, USD 30.27 per MWh, and ERCOT, Austin Energy load zone the highest, USD 39.01. CAISO, SP15 hub (south) spent the most hours below zero: 11.79 percent of them." Widest daily spread 42.31 (ERCOT West load zone). The map's default (day-ahead of 16 November): SPP 31.93 green, CAISO 45.82 at 0.63 of the scale, ERCOT 54.09 red.
- **The rules the restatement wrote again and found as the code does them:** each grid's local windows (8,760 hours in the twelve months over both clock changes, 744 in October, the map's 30 days to 16 November 721 hours over 1 November); a row held in two tables read once, from the first; an hour of real time from all four 15-minute prices, rounded to 9 places; the step holding more of the window; the 95 percent floor; the average day by local hour; each whole local day (23, 24 or 25 hours) for each day's spread; the share above USD 200 strictly above; carbon as the mean of the daily figures with the 90 percent floor; the map's on-peak (hours beginning 06:00 to 21:00, Monday to Friday, CAISO to Saturday, NERC holidays off); the hub page's intervals due from the first row to the last and the UTC days with no row; real time less day-ahead hour by hour.

## One rule changed at a time

| Choice the pages make | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Average price: each hour once | weighted by the grid's own hourly load (ERCOT's system load, CAISO's CA ISO-TAC), over the hours both hold | ERCOT's hubs and zones +1.67 to +2.73 USD/MWh (+4.5 to +7.1 percent; Hub Average 34.39 to 36.41); CAISO SP15 +1.42 (30.01 to 31.42), NP15 +1.34. SPP not sized (no year of SPP load held here) | no (finding 3) |
| The comparison's hours: the tables of 17 November | the hours the site's own hourly files hold | SPP North October real time not held to 34.35 (744 hours), SPP South to 25.30; ZP26 October real time 45.35 to 44.88 (below zero 2.08 to 2.96 percent); SPP North twelve months 31.66 to 31.77 | the hours held are on the page; that the site holds more is not (finding 2) |
| Carbon: the mean of daily intensities | the days weighted by their net generation (EIA-930), over the days both hold | October 2026: ERCOT 315.40 to 315.60 (+0.06 percent), SPP 391.82 to 391.05 (-0.20), CAISO (27 days) +1.63 percent; 26 August to early November: +0.50 to +3.09 percent | the note says "the mean of the daily carbon intensities"; small |
| Scarce hours: above USD 200 | above USD 100 | twelve months, day-ahead: CAISO 0.03 to 0.41 to 0.48 percent; ERCOT 0.65 to 0.89 against 1.79 to 3.04; SPP North 1.26 against 3.54 | yes (decision 6: one round threshold) |
| The map: an area by its grid's main hub | another hub of the grid | day-ahead of 16 November: CAISO by NP15 (56.28 for SP15's 45.82) makes CAISO the dearest area (0.63 to 1.0) and ERCOT 0.91; ERCOT by its West hub (70.03) moves CAISO to 0.36. Within ERCOT the six hubs run 45.62 to 70.03, wider than the three areas (31.93 to 54.09) | yes (decision "main-hub"; the hover names the hub) |
| The map: the newest whole day when the file was built | the newest day all three areas hold in the page's own hourly files | 16 November (the map) against 20 November: CAISO 20.54, ERCOT 16.18, SPP 6.06: CAISO from 0.63 to the dearest (1.0), ERCOT from the dearest to 0.70 | the hover names the day; the legend did not (finding 5) |
| The map's scale: lowest to highest area shown, linear through the middle | a fixed scale | with three areas the lowest is always full green and the highest full red: the twelve months' SPP 34.50 stands at 0.92, 0.36 below ERCOT and 4.21 above CAISO; on the 30-day measures two areas only (ERCOT blank: 673 of 721 hours) | yes (decision "scale"; the legend gives both ends) |
| A hub page's day-ahead: from 30 days back, no end | to the render time, as the real time | 24 of the 697 day-ahead hours read at 18:00 UTC on 12 November were the next day's | the To column shows it; the words did not (finding 6) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Day-ahead against real time | every page | `/prices`: the newest real-time interval beside the day-ahead price of the hour; the hub page: each market's own window and, over the hours both hold, real time less day-ahead; the comparison: each market a column set, A and B both; the map: day-ahead only, said | **Right as stated**; the hub page's two windows differ (finding 6) |
| Hub against zone against node | the comparison's "A hub is not a site", "What this does not tell you"; the map's decisions | hubs and ERCOT's load zones; no node | **Right** on the node; **finding 1** on ERCOT's load zones (said to be absent; counted as hubs) |
| Simple against load-weighted averages | "Average price"; the map's "Average over 30 days" | each hour once | **Finding 3** (unsaid; 4.0 to 7.1 percent) |
| The window and "latest" | the comparison's period names; `/prices`'s "newest"; the map's "the newest day" | twelve calendar months and the month, local time, said with their dates; `latest_prices` refreshed every 15 minutes with the interval's start beside it; the map's day is the file's | **Right** for the comparison and `/prices`; **finding 5** for the map's legend |
| Time zones and daylight saving days | the comparison's table note; the map's windows; the hub page ("Times in UTC") | local midnights; 8,760, 744 and 721 hours restated; the hub page's highs and lows in UTC and the grid's own clock on hover | **Right** |
| Negative prices | "Hours below zero"; the map's shares | every price enters the averages as published; an hour of real time below zero after rounding its mean to 9 places | **Right** (the hour of zero: the faults file of 16 November) |
| The heatmap's color scale and its breaks | the legend; decision "scale" | linear from the lowest to the highest area shown, through fog at the middle; no breaks; three areas | **Right as stated**; it ranks three areas, sized above |
| A region with missing hours averaged as if whole | the comparison's 95 percent floor; the map's | written at 95 percent and more, the hours held on the page ("8,568 of 8,760"); nothing filled | **Right as stated**; the hours were missing from the comparison's inputs, not from the site (finding 2) |
| Held grids reaching a cell or a color | every page | the comparison's copy carries ISO-NE, NYISO and MISO by name only (no figure in the file); the map's file the same (names, reasons); `/prices` and the hub page: a held grid's latest price drawn "license needed" by `Num`; the map's held areas blank | **Right**: no held figure in any file or page drawn; but the held grid's words on `/prices` and its hub page (finding 4) |
| Staleness | the comparison's "Built 2026-11-17"; `/prices`'s interval column; the map | the comparison names its build; `/prices` prints each interval's start; the map's hover names the day, its legend did not | **Right** but the map (finding 5); the rebuilds are data requests |
| ERCOT's Hub Average is the mean of its four hubs | the name's hover | restated by the read of 16 November; not repeated | cited |

## What a buyer's or a trader's own number would hold that this does not

| Item | Why | Size, where measurable |
|---|---|---|
| A load-weighted average, and a price for the buyer's own load shape | the pages give each hour once | +4.0 to +7.1 percent with the grid's own load shape (finding 3) |
| The price where the load settles: CAISO's load aggregation points, SPP's load zones, a node | hubs only outside ERCOT; nodes not held | not sized (no table) |
| A delivered price: transmission, capacity, ancillary services | not in a hub price; said on the page | `/cost-of-power` |
| The forward curve for next year | licensed (CME Group, ICE) | not sized |
| New York, New England, the Midcontinent, PJM | license needed, paused or licensed | `docs/licenses.md` |
| The spread inside a grid on the map | one hub an area | ERCOT's hubs 45.62 to 70.03 on 16 November, wider than the three areas' 22.16 |
| A scarcity line at each operator's own signal | one round threshold, said | above USD 100 holds 2.5 to 16 times the hours above USD 200 |
| Marginal emissions | the grid's average generation, said | not held |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | `/prices/compare` says ERCOT's eight load zones are not compared and counts them as hubs; the lead says five grids | 8 of the 17 twelve-month rows; the default sentence's dearest "hub" is a load zone | words | `wip/audit-prices-1` |
| 2 | Medium | The comparison lacks real-time hours the site's own hourly files hold | SPP North and South October real time "not held" against 34.35 and 25.30; ZP26 October 45.35 against 44.88; SPP North twelve months 31.66 against 31.77 | figure: data request, ruling line | `wip/audit-prices-2` |
| 3 | Medium | "Average price" is each hour once (a flat load's price), unsaid | load-weighted +4.0 to +7.1 percent | words | `wip/audit-prices-3` |
| 4 | Low | A held grid on `/prices` and its hub page: the section lists its zones and says its tables have no rows | words only; no held figure reaches the page | words | `wip/audit-prices-4` |
| 5 | Low | The map's legend gives no date: "the newest day" was 16 November on 26 November | the colors of 20 November rank CAISO dearest, not ERCOT | words; rebuild: data request | `wip/audit-prices-5` |
| 6 | Low | A hub page's day-ahead runs to tomorrow's last hour under "the window" | up to 36 hours past the real time's window (24 of 697 hours at the read) | words | `wip/audit-prices-6` |

- Ranked by severity, then by size. Three Medium, three Low.
- The five words branches merge together onto origin/main of 26 November with no conflict (`wip/audit-prices-words`). On it the five audit tests and every test file that reads a changed page, component or note pass (382 passed, 9 skipped), but `tests/test_session7540_compare_read.py::test_every_check_passes`, which fails on clean main the same way: `site/scripts/test-compare-read.mjs` fails 12 of its 73 checks on main (left open, below), and the same 12 on every branch. `site/scripts/test-prices-read.mjs` 26 of 26. Each branch alone was run with its importers (branch 1 and 3: 229 passed; branches 4 and 6: 47 passed and `test-prices-read` 26 of 26; branch 5: 24 and 77 passed).

## 1. ERCOT's load zones are compared, and the page said not (Medium; words)

- **Where.** `site/app/prices/compare/page.tsx`: "What this does not tell you" ("ERCOT's eight load zones. Their prices are held in the warehouse since 2015 and priced on the cost of power page; they are not in this comparison"); the input panel ("Twelve months of history are held for 17 hubs; the zones and the other hubs are held since late August 2026, so they are in the month and not in the year"); the period link ("17 hubs"); the sentence ("of the 17 hubs compared"); the A and B hover ("the zones and the hubs other than the eleven with a year of history"); the lead ("of five grids"). `hub_price_comparison.md`: "Eleven as built", "Thirty-one as built", "The zones are in the month and not in the year", the held rows "named in the table and the chart".
- **Why it is wrong.** Session 7052 added `ercot_zone_prices_history` to the builder; the copy of 17 November holds ERCOT's eight load zones in both periods (8 of the 17 rows of the twelve months, 8 of the 19 of the month). The default view names "ERCOT, Austin Energy load zone" the dearest of "the 17 hubs compared"; a buyer told the zones are absent would not look for the price its load settles at. Three grids' figures are shown, not five. And since session 7050 the held grids' rows are in "Held, not shown", not in the table.
- **The test.** `tests/test_audit_prices_1.py` on `wip/audit-prices-1`: the file holds the zones in both periods (passes on main); the drawn words (fail on main).
- **The fix on the branch, words only.** The page counts hubs and zones apart ("17 hubs and zones (9 hubs and 8 of ERCOT's load zones, held since 2015)"), names the grids shown from the file ("three grids, CAISO, ERCOT and SPP"), says the load zones are compared and that CAISO's and SPP's rows are hubs only; the note says the same; two checks of `site/scripts/test-compare-read.mjs` (row 10) follow the words. Drawn and read: pass; all 109 marked figures of the default view and 142 of A and B identical, in order.

## 2. The comparison lacks real-time hours the site holds (Medium; a figure)

- **Where.** `site/data/price_compare.json` (built 17 November 2026) against `site/public/board/h/spp-sppnorth-hub.json`, `spp-sppsouth-hub.json`, `caiso-th-zp26-gen-apnd.json` (the board's hourly files, each real-time hour the mean of its 15-minute prices, to the cent).
- **Why it matters.** The page says SPP's two hubs are "Not held for October 2026 in the real-time market (fewer than 95 percent of its hours)", while the same site's hourly files hold every one of the 744 hours. ZP26's October real time is drawn on 720 hours and SPP North's twelve months on 8,568: the rule (95 percent, nothing filled) is kept, but the missing hours were missing from the comparison's inputs, not from the warehouse.
- **How much.** SPP North October real time 34.35 (744 hours, 9.41 percent below zero) and SPP South 25.30 (19.22 percent) would be written; ZP26 October 45.35 to 44.88, below zero 2.08 to 2.96 percent; SPP North's twelve months 31.66 to 31.77, below zero 10.52 to 10.50.
- **The test.** `tests/test_audit_prices_2.py` on `wip/audit-prices-2`: the gap from the page's own files. Passes on main; not for landing.
- **For Samuel's ruling.** Default "left as it is" until the data machine's next run of the comparison. The other choice: rebuild it now (the figures above move; SPP's October real time appears).
- **Data request.** `price_compare.py --snapshot` run on the data machine, and why its real-time inputs held fewer hours than the board's hourly files for SPP and ZP26.

## 3. "Average price" is a flat load's price, unsaid (Medium; words)

- **Where.** The page's "Average price" column, sentence and headline; `hub_price_comparison.md` ("the mean of the hourly prices"); the map's averages (the same rule).
- **Why it matters.** A trader's or a utility buyer's "average" is often load-weighted; a datacenter's flat load pays the simple mean. The page said neither. The dearer hours are the busier ones, so a load shaped like the grid's pays more.
- **How much.** Over the twelve months to October 2026, the hours both held: ERCOT's hubs and zones +1.67 to +2.73 USD/MWh (+4.5 to +7.1 percent), CAISO SP15 +1.42 (+4.7), NP15 +1.34 (+4.0).
- **The test.** `tests/test_audit_prices_3.py` on `wip/audit-prices-3`: SP15's simple and load-weighted averages from the tables (passes on main; skipped where the tables are not held); the drawn words (fail on main).
- **The fix on the branch, words only.** The table's note: "The average price counts every hour held once: what a flat load, the same every hour, would pay at the hub or zone. A load shaped like the grid's own, heavier in the dearer hours, pays more than this average." "How it is computed": "not weighted by the grid's load or by any buyer's". The note's row says it with the measured size. Drawn and read: pass; every figure identical.
- **For Samuel's ruling** (a figure, not made). Default "left as it is". The other choice: a load-weighted average beside the simple one (+4.0 to +7.1 percent on the twelve months; needs each grid's hourly load in the builder; SPP's year of load is not held here).

## 4. A held grid on `/prices` and its hub page (Low; words)

- **Where.** `site/app/prices/page.tsx`: `held = !rows.ok && isLicenseReason(rows.reason) && entities.length === 0`; `site/app/prices/[entity]/page.tsx`, the latest line and the table's empty cells.
- **Why it is wrong.** `warehouse/connectors/latest_prices.py` writes NYISO's and ISO-NE's newest intervals every 15 minutes with license "public", and MISO's last row of 4 October stays; `latestPrices` names no table, so no hold applies. Then `entities` is not empty and the held drawing of session 7539 does not apply: drawn with the pages' own functions, each zone is listed, its price "license needed" (`Num` holds the figure), the held interval's start printed, and the day-ahead cell reads "no data: no nyiso_dam_zone_prices row since ...", which is not so: the rows are held. The hub page read "license needed USD/MWh, starting ..." and "no rows in nyiso_rtm_zone_prices for this entity in the last 30 days".
- **The test.** `tests/test_audit_prices_4.py` on `wip/audit-prices-4`: the connector and the reader (passes on main); the drawn pages on stand-in rows, every price 0 (fails on main).
- **The fix on the branch, words only.** A held grid's section is the held drawing whatever `latest_prices` holds; the hub page says "license needed: the rows of <table> are held, not shown" and drops the unit and start after a held price. Drawn and read: pass; the public grids' sections and hub pages identical to main's.

## 5. The map's legend gives no date (Low; words)

- **Where.** `site/components/grid/MapPrice.tsx`, `PriceControls`: "Day-ahead, the newest day" in the measure list; the legend "Green ... to red ..., each grid's main hub (the price board's)".
- **Why it matters.** "The newest day" is the newest whole day the file held when built. The file on main was built 19 November and colors by 16 November; on 26 November the site's own hourly files hold whole days to 20 November (ERCOT) and 25 November (CAISO, SPP). Each area's hover names the day; the colors, the legend and the measure's name do not. On 20 November the ranking is CAISO 20.54, ERCOT 16.18, SPP 6.06: CAISO the dearest area, not ERCOT.
- **The test.** `tests/test_audit_prices_5.py` on `wip/audit-prices-5`: the map's day against the hourly files (passes on main); the legend drawn for all eight measures (fails on main).
- **The fix on the branch, words only.** The legend names the day ("day-ahead of 2026-11-16", or "the 30 days to"), says when the areas' days differ, and names the file's build ("from the price file built 2026-11-19"); `prices_map.md` says so. Drawn and read: pass; no figure or color moves.
- **Data request.** `prices_map.py` run on the data machine with the board step (the board audit's request covers the step not run since 20 November).

## 6. A hub page's day-ahead window (Low; words)

- **Where.** `site/app/prices/[entity]/page.tsx`: "last 30 days" and "Min, mean and max of every interval in the window"; the day-ahead read from 30 days back with no end (`lib/data.ts`, `series`).
- **Why it matters.** Once the next day's day-ahead is published, the day-ahead minimum, mean and maximum run to tomorrow's last hour, up to 36 hours after the real time's window: drawn at 18:00 UTC on 12 November, 24 of ERCOT Hub Average's 697 day-ahead hours were the next day's. The To column shows it; the words said one window.
- **The test.** `tests/test_audit_prices_6.py` on `wip/audit-prices-6`: the read has a start and no end (passes on main); the drawn note (fails on main).
- **The fix on the branch, words only.** The note under the table: "The day-ahead runs to the newest hour published, which can be tomorrow's, so its window can end with tomorrow's last hour, up to 36 hours after the real time's: the From and To columns give each." Drawn and read: pass.

## What was checked and found right

- **Every figure of the comparison's file** (662 of 666 to the cent with this machine's one missing real-time day taken from the page's hourly files; the 4 others one carbon day) and **every figure the page draws** in four views, its choices made again.
- **`/prices` and four hub pages** at a fixed render time, 32 of 32, from the same rows: the intervals due and the missing UTC days (ERCOT and CAISO 6 to 8 November on this machine's tables), real time less day-ahead over the hours both hold.
- **The map's file** from the page's own hourly files, 145 of 152 to the cent, the 7 others explained; the on-peak rule with CAISO's Saturday and NERC's holidays; the 721 hours of the 30 days over 1 November.
- **No held figure** in `price_compare.json`, `prices_map.json`, or any page drawn.

## Not covered, or left open

- **`site/scripts/test-compare-read.mjs` fails 12 of 73 checks on main** (and so `tests/test_session7540_compare_read.py`): written for the copy before session 7050 cut the held rows to names and session 7052 added ERCOT's zones ("9 rows shown", the held rows in the table, the read's case figures of September). The same 12 fail on every branch here; the test is not changed by this audit beyond the two checks finding 1 makes true.
- **The live `/prices`** reads the live set; it was drawn on this machine's tables (to 13 November) at a fixed render time, with `latest_prices` made from them. The live page's own numbers were not read (no request to any service).
- **The ERCOT tab of `/prices`** (the peak premium explorer) and **`/cost-of-power`'s All grids tab**: other reads.
- **CAISO's 345th carbon day**: not on this machine.
- **The map's hubs list** (`hubs` in the file) colors no area: only each grid's main hub reaches a color; the hubs' own figures were restated, not drawn.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-prices-1` (`7c97c6134`), `wip/audit-prices-3` (`111a658f8`), `wip/audit-prices-4` (`8e23bb7cc`), `wip/audit-prices-5` (`832692976`), `wip/audit-prices-6` (`4300340c2`), or all five as `wip/audit-prices-words` (`9a4929821`, merged with no conflict). Branches 1 and 3 touch `site/app/prices/compare/page.tsx` and `docs/methods/hub_price_comparison.md`; 4 and 6 `site/app/prices/[entity]/page.tsx`; 5 `site/components/grid/MapPrice.tsx` and `docs/methods/prices_map.md`.
- **Not for landing:** `wip/audit-prices-2` (`0adc927cf`, a figure).
- **For Samuel's ruling, default "left as it is":** finding 2, rebuild the comparison now (SPP North's October real time 34.35 and SPP South's 25.30 appear; ZP26's October 45.35 to 44.88; SPP North's twelve months 31.66 to 31.77); finding 3, a load-weighted average beside the simple one (+4.0 to +7.1 percent).
- **Data requests:** the comparison rebuilt on the data machine and why its real-time inputs held fewer hours than the board's hourly files (finding 2); the map's file rebuilt with the board step (finding 5).
