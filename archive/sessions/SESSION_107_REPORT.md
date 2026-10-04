# Session 107 report: the seller tab, version 2

**Built and on the live site, in review at `/cost-of-power/seller/v2`.** The seller tab's solar, wind and gas peaker in the battery page's layout and its framing: the last twelve months first, the long-run averages beside them and labeled as long-run averages. The live seller tab, its model and its snapshot are untouched: the snapshot comparison shows 0 differences on the live tab and its two California views. One deploy, after one push that failed its tests and merged nothing.

## Read these first

1. **Only Texas has a long-run average.** ERCOT holds seven full years (2019 to 2025); the other grids are held from September 2024 and hold one full year, 2025. For them the page gives the last twelve months and the year 2025, and says "There is no long-run average yet." Where a span is not whole, its cell says "not held" and why. Nothing is filled.
2. **The last twelve months read very differently from the long-run averages in Texas, which is the point of labeling them.** Per kW of nameplate:

   | ERCOT, hub average | Last twelve months (Oct 2025 to Sep 2026) | Long-run average, 2023 to 2025 | Long-run average, 2019 to 2025 |
   |---|---|---|---|
   | Solar | USD 59.85 | USD 102.24 a year | USD 130.80 a year |
   | Wind | USD 83.57 | USD 81.17 a year | USD 111.23 a year |
   | Gas peaker, margin over fuel | USD 48.15 | USD 120.28 a year | USD 246.94 a year |

   The seven-year average holds 2021 (Winter Storm Uri). The page's chart shows each year, so a reader sees where an average comes from.
3. **New England has no twelve months in a row, for any asset.** Six of its 26 months are not held (September 2024, February and September 2025, July, September and October 2026): its real-time price files miss intervals, which is in the register of known faults. So New England shows its years and no last twelve months, and says so.
4. **New York has no solar.** EIA-930 itemizes no solar generation for New York; the view says so and shows no number.
5. **MISO is on the live tab and not on this page.** Its pulls are paused since 4 October and its terms forbid derivative works, so a new page shows no figure of its prices (session 96's reading, as on `/prices/compare` and `/board/v3`). The page says why. The live tab keeps MISO as it was.
6. **The page needed its own line in the release list.** `/cost-of-power/seller` is live, and a path takes the status of its nearest parent: without `"/cost-of-power/seller/v2": "review"` the new page would have opened to visitors. It has the line; a test asks the release gate itself; and on production a visitor gets the in-review page.

## The page

`/cost-of-power/seller/v2`, in review. Layout: the battery page's. A panel of two choices (grid, asset); a summary sentence that leads with the last twelve months; three headline numbers (revenue over the last twelve months, the capture price against the price of every hour, the long-run average or why it is not held); a chart of revenue by calendar year, a year short of twelve held months hatched; a table of the three spans (revenue per kW, energy sold, capture price, the price of every hour, capture rate); two folds; the source line.

- **Every figure is the live tab's own model's.** `site/lib/seller2.ts` calls `lib/merchant.ts` on `data/merchant_snapshot.json`, month by month, per MW at the model's defaults, and only adds the months up over a span.
- **The spans, by the battery page's rules:** the last twelve months are the newest held month with its eleven before it all held; a year is full when its twelve months are held; a long-run average is the sum over its full years divided by their number.
- **The peaker's figure is its margin over fuel and variable cost,** and the page calls it that everywhere, not revenue.
- **Per kW, before any cost but the peaker's fuel.** The costs, the debt coverage and the stress days stay on the live tab; this page was asked for the framing.

## Every difference, the 25 live pages

`before-107` (21:16 UTC) against `after-107b` (21:30 UTC): 26 differences, all on the home page, all the latest real-time prices. The live seller tab, its California solar and wind views, and the other 21 pages: 0.

## Tests and checks

- `tests/test_session107.py`, 8 tests. **Every view recomputed from the snapshot by hand** (15 views: revenue over the last twelve months and its first and last month, both long-run averages, the full years) and set against the page's module: equal to six decimals. The rules on months made for the test: a missing month breaks the twelve and the year; a long-run average is a year, not a sum. Only Texas has a long-run average today; New York's solar says so; MISO is not a choice. The release gate answers "review" for the page and "live" for the live tab.
- **The first push failed on GitHub and merged nothing** (run 37235411635): the page wrote the date of EIA's California change in words, and session 78's rule keeps that date in one file. The page now reads it from there. I had run only this session's tests before that push; before the second I ran all of them (766; the one failure is the interchange ceiling, which is not this session's and does not run on GitHub).
- The second push (run 37235900913) passed and merged (`5a71554`); Vercel accepted the deployment.
- On production, internal view: the page renders with data for three views and is closed to a visitor. Its sentence there: "Over the last twelve months, Oct 2025 to Sep 2026, a merchant solar plant in ERCOT priced at the hub average earned USD 59.85 per kW. The long-run average of 2023 to 2025 was USD 102.24 a year, and of the 7 full years held (2019 to 2025) USD 130.80."

## Errors and decisions

1. **A snapshot named `after-107` was taken of the old site,** in the same command as the failed push, before I had read the push's result. It is not used; the comparison above is against `after-107b`, taken after the real deploy. From here a deploy's steps stop at the first failure.
2. **The price of every hour over a span is the mean of the months' all-hours prices,** not weighted by the months' lengths. It is a reference beside the capture price and is labeled.
3. **No model call, no pull, no table, no load. Model spend USD 0.00.**

## For Samuel

1. **When it replaces the live tab:** version 2 leaves out the batteries (they have their own page), the costs and debt coverage, the stress days and MISO. The first three could come over as folds; MISO waits on the pause.
2. **The hourly weighting** (second decision), if the price of every hour should be exact over a span.

Energy Research Warehouse (ERW), session 107, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 21:12 to 21:35 UTC, unattended.
