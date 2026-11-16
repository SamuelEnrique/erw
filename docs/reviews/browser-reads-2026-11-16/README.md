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

## For the old laptop's next rows

A row is readable here when its branch can be fetched: nothing has to land first. The four branches were merged for one build; a branch that does not merge with the others is built alone.
