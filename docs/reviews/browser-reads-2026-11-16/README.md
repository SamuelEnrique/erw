# The old laptop's pages read in a browser, 16 November 2026

Energy Research Warehouse (ERW). Session 7600, chain 305 (part A, second bullet), the portable laptop. The rows are those of `docs/state/browser_reads_wanted.md` (on main), which the old laptop's chain 304 writes for every change it could not see: it cannot build the site. Rows 1 to 14 were read here; each row's state is written back in that file.

## How they were read

- **The build:** the four branches the rows name (`wip/7501-contracts` at `118e668fa`, `wip/7502-severance` at `c247ad4e1`, `wip/7503-shoulder` at `7820907a4`, `wip/7505-battery-awards` at `73837e331`), none landed, merged on this machine into a branch that is not pushed, built in the foreground and served here. They merge with no conflict.
- **Then again** with this branch (`wip/7600-large-load-read`) and `wip/7600-shoulder-read` merged in, to see the faults gone.
- **The browser:** the machine's own Chrome, headless, in the internal view, at 1280 by 900 and at 390 by 844 as a phone. A hover is the mouse moved onto the mark; on the phone the mark focused, as a tap does; row 12's keyboard is the Tab key pressed.
- Row 8 was read as a visitor (no token).

## The rows

| Row | Page | Seen | Fault | Pictures |
|---:|---|---|---|---|
| 1 | `/severance` | The fold is closed as the page opens, above the downloads; 14 lines; each mark's box holds "Default:" and "Source:" | At 390 px a mark right of the first 100 px ran its box past the screen (a mark at 351 px: its box from 351 to 639) and the page grew to 639 px wide while it was open. The shared mark's own fault: fixed here for every page (below) | `row-01-severance-fold-1280.png`, `row-01-before-severance-fold-tip-390.png`, `row-01-severance-fold-tip-390.png` |
| 2 | `/severance`, New Mexico | "RIO ARRIBA, district 53, suffix 3920" is kept and the ad valorem line reads 1.2395% (USD 1,265.16); "SAN JUAN, district 06, suffix 4530" is kept and reads 1.3603% (USD 1,388.46); "Reset to the defaults" goes back to the first state, and New Mexico chosen again shows "Not chosen: ad valorem left out" and 0% | none | `row-02-severance-new-mexico-1280.png` |
| 3 | `/severance?tab=lease` | "Try the sample": no request after it loads; base tax USD 114,457.19, with the rules ticked USD 114,457.19, potential savings USD 18,942.53, regulatory fees USD 73.80; the fold is the last thing of the tool | Beside the row, and on production too: at 390 px the page was 406 px wide once the sample was loaded (the table of flagged rules). Fixed here | `row-03-severance-lease-sample-390.png`, `row-03-severance-lease-fold-1280.png` |
| 4 | `/severance`, the price box | "WTI Cushing, the mean of 22 daily EIA spot prices in 2026-10, $102.07 per barrel": the latest complete month, named, with its count of days | none | `row-04-severance-price-1280.png` |
| 5 | `/contracts` | "executed from 2024-01-09 to 2223-01-01 as filed" (the load of 5 October); "Of the 18,989 rows held here, 10,956 file no number", and its mark opens on a hover and on a focus | none | `row-05-contracts-limits-tip-1280.png` |
| 6 | `/contracts?q=2026-Q2&product=power&ba=not%20stated` | 106 rows | none | `row-06-contracts-list-1280.png` |
| 7 | `/contracts?view=terms` | The fold opened: 19 lines; each box holds "Default:" and "Source:"; the tolling mark's box reads "Every row filed is counted here, a terminated contract's too. 216 of the contracts are in force ..." | At 390 px, as row 1 (a mark at 328 px: its box to 616) | `row-07-contracts-terms-fold-1280.png`, `row-07-contracts-terms-tip-390.png`, `row-07-contracts-tolling-tip-390.png` |
| 8 | `/contracts` as a visitor | The in-review page: no table, no figure | none | (no picture: the page is the in-review page) |
| 9 | `/shoulder` | The fold: 18 lines; each box opens with "Default:" and "Source:" | At 390 px, as row 1 (the case the row named: a mark at 351 px, its box to 639) | `row-09-shoulder-fold-1280.png`, `row-09-shoulder-fold-tip-390.png` |
| 10 | `/shoulder?grid=ercot&month=2024-05` | The mark stands after the label, outside its capitals; the box reads "In this month net load is lowest at 03:00, before the sun is up ..." | At 1280 px the box ran past the window (from 1031 to 1319 of 1265) and the page scrolled sideways; at 390 px it was cut by the screen's edge (to 410). Kept inside the window it stood over the figure's last characters, so a headline's mark now opens its box above itself: the figure stays whole | `row-10-before-shoulder-midday-tip-1280.png`, `row-10-shoulder-midday-tip-1280.png`, `row-10-shoulder-midday-tip-390.png` |
| 11 | `/shoulder?grid=caiso-own` | "By month since June 2025"; the third headline reads "not held" with no unit after it; the line under it holds "days (complete, of 24 hours, with a shoulder)" in three lines at 390 px | The same line ended "the batteries ran not held hours at rated power in those shoulders". Fixed on `wip/7600-shoulder-read` (the tool's faults row 17): "the hours the batteries ran at rated power in those shoulders are not held" | `row-11-shoulder-caiso-1280.png`, `row-11-shoulder-caiso-390.png` |
| 12 | `/cost-of-power/battery/awards` | "Decisions on this page (15)"; 15 lines; each box opens on a hover and on the Tab key with "Default:", "Source:" and "Made in:"; no line of the block is grey | At 390 px, as row 1 (a mark at 340 px: its box to 628) | `row-12-awards-fold-1280.png`, `row-12-awards-tab-tip-1280.png`, `row-12-awards-fold-tip-390.png` |
| 13 | `/cost-of-power/battery/awards#real-time` | "What the hub price misses: 41 real days at the batteries' own nodes"; no "one week" on the page; "Over the 41 whole days held" in the same paragraph | none | `row-13-awards-real-time-1280.png` |
| 14 | `/cost-of-power/battery/awards` at 390 px | With the fold open the page is 390 px wide | With a box open, as row 12 | `row-14-awards-fold-390.png` |

## The shared mark, for every page

Rows 1, 7, 9, 10, 12 and 14 are one fault, and it is not these four pages': the site's shared "i" mark (`site/components/tool/ToolPage.tsx`, `Tip`) opens a box 288 px wide from the mark's left edge. Measured on production on 19 pages that draw it: at 390 px, 62 of 91 marks ran past the screen and the page scrolled sideways while the box was open; at 1280 px, 4 of 87. With this branch (the placer of `site/components/largeload/TipPlace.tsx`, mounted once in the site's layout): 0 of 199 and 0 of 195 on the same pages. It is row 14 of `docs/reviews/large-load-on-site/browser-read-2026-11-16.md`; the lease tab's table is its row 15.

## Rows 15 to 31 (session 7601)

Added by the old laptop from 11:40 UTC, on four more branches (`wip/7506-impact` at `946db9195`, `wip/7507-peak-premium` at `b35e64e9a`, `wip/7508-demand-growth` at `66e294497`, `wip/7509-interconnection` at `da5dfd8cb`), none landed. They merge with the first four and with this branch with no conflict; one build, read at 1280 and 390 px. A chart's hover is the mouse moved across it at 59 places and three heights, each card's words kept.

| Row | Page | Seen | Fault | Pictures |
|---:|---|---|---|---|
| 15 | `/impact` | The A and B table at both widths: construction jobs 515; operating jobs 44.7; construction earnings USD 41 million; sales and use tax USD 19.9 million; taxes, present value USD 19.9 million; earnings, present value USD 83.6 million; property tax "not held", its hover "the local levy is not given"; the page 390 px wide at 390 px | none | `row-15-impact-1280.png`, `row-15-impact-390.png`, `row-15-impact-not-held-hover-1280.png` |
| 16 | `/impact?tech=land_based_wind&state=wy&mw=504&start=2028` | Property tax, first operating year USD 0; over the life USD 36.2 million; "Every year" opened: a column MWh, and property tax USD 0 for 2029 to 2031 and USD 1.6 million from 2032 to 2053 | none | `row-16-impact-wyoming-1280.png` |
| 17 | `/impact?tech=geothermal&state=nv&mw=26.5&start=2026` | Taxes, present value USD 0; property tax and sales and use tax "not held" | none | `row-17-impact-nevada-1280.png` |
| 18 | `/impact?tech=geothermal&state=nv&mw=36&cost=4956.83&iaval=1&own=1.0917&ownyears=60` | A, property tax, first operating year USD 876,642; "Local option by ordinance or agreement" reads Yes | none | `row-18-impact-nevada-36-1280.png` |
| 19 | `/impact?tech=land_based_wind&state=mn&mw=228&start=2026` | The mark of "Scenario A in other states" reads "Minnesota is 4 of 51"; Minnesota is the fourth bar, marked "yours" (93, 377 and 219 job-years, 689 in all); each card of the taxes chart ends "(a property tax statute is held)" or says it is not | none | `row-19-impact-states-mark-1280.png`, `row-19-impact-minnesota-card-1280.png` |
| 20 | `/explore/ercot-peak-premium` | The fold: closed as the page opens; 11 lines; each box opens on a hover and on the Tab key with "Default:" and "Source:"; no line grey | At 390 px on its own branch, the shared mark's fault of row 1 (fixed for every page here: the box stands at 94 to 382 px) | `row-20-peak-fold-1280.png`, `row-20-peak-fold-tip-390.png` |
| 21 | `/explore/ercot-peak-premium?hub=ercot:HB_BUSAVG&from=2021&to=2022` | "The thesis's figures": the median of all intervals, 2021, 25.00; the first table, peak, 2022, minimum -251.00; the thesis chart's own cards read "median 25" and "min -251" by the chart's rule | none | `row-21-peak-busavg-1280.png` |
| 22 | `/explore/ercot-peak-premium?month=12&from=2015&to=2026` | The headlines read "not held" with no unit; December 2026 reads "not held" in every cell of both tables; the chart draws four boxes, December 2015's | none | `row-22-peak-december-1280.png` |
| 23 | `/explore/ercot-peak-premium` | The three charts' cards (3, 12 and 52 of them, 202 figures) each hold only figures the page's tables show for the same hub and period, the monthly chart's against the whole monthly table (142 rows) | none | `row-23-peak-chart-card-1280.png` |
| 24 | `/explore/demand-growth` | The fold: 16 lines; each box with "Default:" and "Source:", on a hover and on the Tab key | At 390 px on its own branch, as row 20 | `row-24-demand-fold-tip-390.png` |
| 25 | `/explore/demand-growth?grid=us48&window=m07` | "+8.00 percent" in the first headline, on the Lower 48's bar and in its row of the table | none | `row-25-demand-lower-48-1280.png` |
| 26 | `/explore/demand-growth?grid=us48&window=peak` | "not held" with no unit in the headlines; the Lower 48's row reads "not held" three times and has no bar; two charts, no third; the page 390 px wide at 390 px | none | `row-26-demand-peak-1280.png`, `row-26-demand-peak-390.png` |
| 27 | `/explore/demand-growth?grid=ercot&window=ytd` | No "Stale since"; the first headline reads "+33.34 percent" for "2026 so far (January to October)" | The second chart's hover card drew no figure: every line read "percent" with no number (2026: "The year so far (January to October)  percent"), on production too. Fixed on `wip/7601-demand-growth-read` (the tool's faults row 20); read again: "+33.34 percent" | `row-27-before-demand-card-1280.png`, `row-27-demand-card-1280.png`, `row-27-demand-card-390.png` |
| 28 | `/explore/interconnection` | The fold: twelve lines; each box with "Default:" and "Source:", on a hover and on the Tab key | At 390 px on its own branch, as row 20 | `row-28-queue-fold-tip-390.png` |
| 29 | `/explore/interconnection?queue=caiso&measure=mw` | "Every entry year": 90 figures, each with two decimals ("550.00"), right-aligned; 35 cells read "not held". The stacked chart's card for 2018 reads 2,410 MW, 17,025 MW, 2,869 MW, not held, total 22,305 MW: the table's 2,410.36, 17,024.82, 2,869.40 and 22,304.58 in whole megawatts | none (the card rounds to the megawatt where the table has two decimals: the same figures in two forms) | `row-29-queue-caiso-card-1280.png` |
| 30 | `/explore/interconnection?queue=caiso&from=2020&to=2010` | First entry year 2010, Last entry year 2020; the titles read "2010 to 2020" (twice), never "2020 to 2010" | none | `row-30-queue-years-1280.png` |
| 31 | `/explore/interconnection?queue=ercot` | The line reads "... \"Entered\" counts the positions of an entry year that are still in the report, not every request made that year", wrapped, the page 390 px wide. The freshness line reads "Stale since 5 November 2026 ... last computed on 5 November 2026 (10 days ago)": more than eight days, so the mark is as the rule has it | none | `row-31-queue-ercot-390.png` |

## Rows 32 to 278 (session 7602)

Session 7602, chain 305 (part A again), 17 November 2026, the portable laptop. 130 rows the old laptop added in its chain 304 (the first run's rows 32 to 75 and the second run's 76 to 278, with gaps in the numbering). Each row's state, with what was seen, is written in `docs/state/browser_reads_wanted.md` (on main): **119 seen, 4 seen in part or in words that differ from the row's (50, 51, 138, 267), 7 with a fault** (rows 52, 55, 62, 63, 80, 82 and 179: six fixed here, one a data fault). No row was left `wanted`.

### How they were read

- **The build:** the old laptop's 27 branches named by the rows (`wip/7501-contracts` to `wip/7545-queues-read`, the heads of 17 November), merged on this machine with `wip/7600-large-load-read` into a branch that is not pushed: no conflict. Built in the foreground and served here. Most of the stacks have since landed on main (chain 301's gate j, chain 370's desk), all but `/play/battery`.
- **The browser:** the machine's own Chrome, headless, through `site/scripts/read-rows-c305.mjs` (new, on this branch), in the internal view, at 1280 by 900 and at 390 by 844 as a phone. Each row is a line of `s7602/rows-*.json` (the steps: clicks, typing, selects, every mark hovered by the mouse and focused as a tap does, the mouse moved across a chart at 25 to 60 places and three heights, the wheel turned on the map); the reader writes what it found and `s7602/show.mjs` prints it. Nothing in the reader decides a row: each state was written from its output and the pictures.
- **Two plays of the battery game** were played to their end with no move (Hard on the summer scarcity day, Normal on CAISO's steepest evening ramp; Easy on Uri at both widths), which is what rows 117, 118 and 267 needed, except row 267's "plus the fleet bonus" (drawn only when a play earns one: not seen).
- **Then again** with the four fixes merged (below), on a second build: rows 52, 62, 63, 80, 82 and 179 read once more (`row-*-after-*.png`).

### The faults

| Row | Page | Fault | Done |
|---:|---|---|---|
| 52, 62 | `/impact` (the headline "Property tax, first operating year"), `/explore/demand-growth?grid=caiso` (a decision's source of over 1,000 characters) | The shared mark's placer capped a box taller than its room (432 px at 1280) and it scrolled inside itself | Fixed in `site/components/largeload/TipPlace.tsx`: such a box is widened up to 576 px where the window allows; read again: whole at 1280 (576 by 248 px and 576 by 284 px). On a phone it still scrolls inside itself. Row 16 of `docs/reviews/large-load-on-site/browser-read-2026-11-16.md` |
| 63 | `/explore/interconnection?queue=spp&from=2018&to=2018` | A one-point chart's share axis ran 0.6 to 1.8 | Fixed in `site/components/TimeChart.tsx` (a value alone padded by a tenth of itself); read again: 0.55 to 0.75. Row 19 of `docs/reviews/interconnection-faults-2026-11-16.md` |
| 80, 82 | Every event page, the fold "Each event day's estimate" | A table 468 px wide with no frame: the page grew to 469 px at 390 once opened (on production too) | Fixed in `site/components/EventStudy.tsx`; read again: 390 px. Row 11 of `docs/reviews/events-faults-2026-11-16.md` |
| 179 | `/supply`, the burn table's links line | No place to break: the line ran to 899 px at 390 (on production too) | Fixed in `site/app/supply/page.tsx`; read again: 390 px. Row 25 of `docs/reviews/supply-read-2026-11-16.md` |
| 55 | `/cost-of-power/battery/awards` beside `/cost-of-power/battery` | The two pages give the same comparison as USD 0.37 against 2.10 (5.60 times, 8 months) and USD 0.40 against 2.24 (5.64 times, January to July): the battery page reads a snapshot written on 10 October and never again | A data fault: request row 261 of `docs/state/data_requests_done_line.md`; row 10 of `docs/reviews/battery-awards-faults-2026-11-16.md` |

### Seen differently from the row, not a fault

- Rows 69, 156, 157 and 268 were written on the month before: the figures are the live set's newer ones (USD 80.34 and 106 months on the battery page; "2,400 of 2,784" on the hub page; ERCOT's fleet 19,194.60 MW and CAISO's 17,265.50 MW in the game).
- Row 50: the impact page's charts now say "2027 build: Property 0 USD (2025), Income 0 USD (2025)", not the row's "property not held, sales none" (row 6 of that tool's read stays a ruling). Row 51: Utah is not drawn on "Taxes, present value, in other states" at the row's address, so its hover could not be read; Nevada's could.
- Row 138: the card was opened from the list's name, not by a click on the map's canvas. Row 129: the arrow keys were not tried. Row 35: the page's own count of resources was read (15 and 15), not `check-no-request.mjs`.
- Row 96: the one "license needed" on `/learn/bill` is the downloads' line (the table is held for download), not a card; a card's figure carries a check key and no hover title.

### Pictures

175 more, `row-32-*` to `row-278-*` (1280 and 390 px where the row asks both), and the after pictures of the six fixed rows.

## For the old laptop's next rows

A row is readable here when its branch can be fetched: nothing has to land first. The four branches were merged for one build; a branch that does not merge with the others is built alone.
