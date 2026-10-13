# Session 235 report: "What a generator earns" on the brand, the capture price back, scenario B as a PPA

13 October 2026, about 06:25 to 07:35 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Worktree `erw-188`, branch `wip/235-generator`, from commit a4c54722. Not pushed, not landed (the landing is the orchestrator's). Model spend USD 0. Pulls: none. No warehouse table written. No em dash in anything written.

## Read these first

- **The page is on the brand.** It wraps what it draws in `<Brand noUsage>`, as the battery page does, and writes no color, font or spacing of its own. Its revenue chart by year was the chart library's with a legend box whose colors were written in the page; it is now the brand's bar chart, a new shared component (`site/components/tool/GroupedBars.tsx`: plain SVG from the server, colors by token, the series named on the chart, an incomplete year hatched).
- **The capture price is back inside "What did it earn?", as one chart and one table.** The chart: at the hub chosen, by year and over the last twelve months, the capture price beside the hub average, the capture rate written above each pair. The table: one row a hub or zone of the grid (ERCOT 14), the last twelve months' capture price, hub average and capture rate, then the capture rate of each year. Default case: 23.27 against 32.17 USD per MWh, 72 percent; by year 177, 130, 55, 131, 146, 85, 76, and 73 percent for the nine months of 2026.
- **The page and the download agree by construction.** Both are `model.ts`'s `capView`, built with the functions `tables.csv` writes its capture tables from. Each figure of a solar or a wind plant's table carries a check key (`cap|<grid>|<hub>|<market>|<fuel>|<span>|<stat>`) that `check-values` recomputes from the capture file: 154 new keys on the default page. The two downloads are unchanged.
- **Scenario B can be a PPA in one click, and the results show the breakeven PPA price.** "Make B a PPA" sets B's contract share to 100 percent and its price to B's own breakeven, rounded up to the cent, and puts B in view. The ninth row of the results is the contract price at which NPV at the hurdle rate is zero: USD 58.36 per MWh at the defaults (the row that was there, the price that keeps coverage at 1.25, is 39.14 and stays).
- **No default and no other number moved.** The two checked numbers the page kept (coverage 0.67, debt payments USD 7,078,769) and every results cell, the sentence and the eight bars are identical before and after, at 1280 and 390 px. Both scenarios still open as merchant.
- **The battery page did not move.** One generic rule was added to `tokens.css`. On the final build the battery page's checked numbers, its visible text and its height (5,016 px) are session 211's, 0 lines of difference.
- **One check fails that is not this session's page: the route check on `/emissions`.** See "Checks" and "Not done".

## What to review

After https://erw-flame.vercel.app/internal/open (once landed):

1. https://erw-flame.vercel.app/cost-of-power/seller (the default: ERCOT, solar, the hub average)
2. https://erw-flame.vercel.app/cost-of-power/seller?iso=ercot&asset=wind&hub=HB_WEST#capture (another hub, another fuel)
3. https://erw-flame.vercel.app/cost-of-power/seller?asset=peaker#capture (a gas peaker: the model at each hub)
4. https://erw-flame.vercel.app/cost-of-power/seller?bn=100&bp=58.36&v=b#scenarios (B as a PPA at its breakeven)
5. https://erw-flame.vercel.app/cost-of-power/battery (unmoved)

Before the landing: `docs/brand/review-235/` on the branch (before and after at 1280 and 390 px, `numbers_before_after.txt`, `README.md`).

## What was done

1. **The brand** (`page.tsx`): `<Brand noUsage>` around `ToolPage`. The page's one color literal (the legend's) is gone with the legend.
2. **`GroupedBars.tsx`**, a shared component: grouped bars, one group a year, the series named on the chart's first line, a figure above each bar or one above each group. Used twice on the page: revenue by year (one series) and the capture price (two).
3. **`capView` in `model.ts`**: the chart's groups and the table's rows. Solar and wind: the capture file (`cap`, `yearRows`, `yearCell`), each hub in the market the page shows it in. A battery and a gas peaker: this page's model solved at each hub (`lib/sellerhubs.ts`), the price while selling or running against the price of every hour.
4. **`lib/capture.ts`, `stat`**, and `check-values.mjs`, the prefix `cap`: the table's figures recomputed from `site/data/seller/capture.json`.
5. **`lib/seller/finance.ts`**: `breakevenPpa` (exact: NPV is a straight line in the price), `ppaShare`, `asPpa`. `SellerScenarios.tsx`: the row `ppa` and the button, in the shared block's `foot`.
6. **`tokens.css`**: one selector added to the brand's link rule, `.brand-a th[scope="row"] a` (a link in a table's first column is underlined, as in a cell).
7. **The note** (`docs/methods/generator_earns_algorithm.md`): a session 235 lead to section 4, a new 4.19 (the chart, the table, the keys, a battery and a peaker), the breakeven PPA formula and "Make B a PPA" in 11.3, nine rows in 11.4, the checks in 11.7.
8. **The checks**: `test-seller-finance.mjs` (a session 235 block, 12 assertions), `check-seller-scenarios.mjs` (part 10b, 8 checks; the rows' list), `check-seller.mjs` (its four capture checks rewritten for the new table), `tests/test_session235.py` (14 tests, a Python mirror of the breakeven among them).

## Checks, with exit codes

None piped; outputs under `runs/session235/`, prefixed `gen_`. Three build cycles under the mutex.

| Command | Exit | Result |
|---|---|---|
| `npx tsc --noEmit`, four times | 0, 0, 0, 0 | |
| `npm run build`, five times | 0 each | builds 1 and 2: no "statement timeout" line. Builds 3, 4 and 5 (the final code): one such line each, a Supabase read of a static page at build time |
| `runs/session208/capture.mjs` on the generator page, 1280 and 390 | 0, 0 | the two kept keys identical to before; 154 new `cap` keys |
| `runs/session212/cells.mjs` | 0 | every cell, the sentence and the bars identical; two new cells, `a|ppa` and `b|ppa` |
| the same capture on `/cost-of-power/battery`, diffed with session 211's | 0 | numbers 0 lines, text 0 lines, facts identical, height 5,016 |
| `CHECK_VALUES_PAGES=/cost-of-power node scripts/check-values.mjs`, on builds 1, 2 and 4 | 0, 0, 0 | 516 of 516 values match |
| `CHECK_VALUES_PAGES=/cost-of-power/seller` (the page alone) | 0 | 179 of 179: the floor of ten is met by this page alone now |
| `node scripts/check-seller-scenarios.mjs`, on builds 1, 2 and 4 | 0, 0, 0 | 106 of 106 |
| `node scripts/test-seller-finance.mjs`, `test-battery-finance.mjs`, `test-decisions-195.mjs` | 0, 0, 0 | |
| `node scripts/check-routes.mjs` on build 2 | 0 | 0 failed |
| `node scripts/check-routes.mjs` on builds 4 and 5 | 1, 1 | one failure, `/emissions`: 2 "no data" blocks. The build log's statement timeout, cached into that static page |
| `node --import ./scripts/alias-register.mjs scripts/check-seller.mjs` | 1 | 21 ok, 12 fail. The four capture checks pass. The 12 are of sections session 212 took off the page; see "Not done" |
| `python -m unittest`, the 33 modules that read the page, the brand or the checks, before the pins moved | 1 | 555 tests, 4 failures, each a pin this session's ruling moved |
| the same 33 after | 0 | 555 tests OK, 42 skipped |
| server and Chrome after the checks | | nothing listens on 3235; no Chrome running; `EADDRINUSE` 0 in each server log |

## Tests whose pins moved (each with a "session 235" note)

- `tests/test_session107.py`: "Incomplete year" is the bar chart's own words now, not the page's.
- `tests/test_session145.py`, `tests/test_session162.py`: `<RevenueYears` is `<GroupedBars`.
- `tests/test_session186.py`: nine rows, `ppa` after `contract`.

## Decisions made without you

1. **The table's years are the capture rate, not the capture price.** Eight years of prices beside three columns did not fit the page at 1280 px; the rate is the figure that compares across hubs and years. Each year's price is in the cell's hover, on the chart for the hub chosen, and in `tables.csv`.
2. **The table shows the plant's own fuel, each hub in one market** (real time where it holds twelve months, else day-ahead; the row says which). Until session 212 it showed both fuels and both markets; those are in the download.
3. **A battery and a gas peaker get the chart and the table too, from this page's model at each hub**, not from the capture file (the file holds the solar and wind fleets). Their figures carry no check key: the model at another hub has no statistic in `check-values`. They are marked `data-model-cap`.
4. **The breakeven PPA price is on the scenario's own contract share, or on the whole plant when it holds no contract**, so a merchant scenario shows a useful number. The cell says which.
5. **"Make B a PPA" fills the breakeven, not a market price.** No published PPA price is held, and none is invented; the sentence beside the button says so. The click also puts B in view.
6. **The contract runs for the debt's years** (session 212's rule), so the breakeven is for a PPA of that length: 35 years at the defaults. A shorter term is the "Term of the debt" field.
7. **The series' names sit at the left of a chart's first line**, where the battery page's sit at the right: on a phone the chart scrolls sideways and names at the right are out of view.
8. **The "before" screenshots and numbers are session 212's captures**, not a new build: the page's code and data are identical between the two commits (an empty `git diff`).
9. **The revenue chart's hover card is gone with the chart library**; each bar keeps a plain hover title and its figure is written above it.

## For Samuel's ruling

1. The table by year: the capture rate (decision 1), or the capture price.
2. The breakeven PPA price runs for the debt's years (decision 6). A PPA term of its own would be an eleventh assumption.
3. `check-seller.mjs`, `check-seller-deeper.mjs` and `check-seller-face.mjs` still describe the page before session 212: retire them, or rewrite them for the three questions.
4. The battery page's year chart still writes its colors as literals in its own file; `GroupedBars` could draw it from the tokens. Not touched: the page is the approved reference.
5. Session 212's open items stand, but for its item 5 (the floor of ten values), which this session closes.

## Not done, not verified

- **The final build's route check fails on `/emissions`.** Three builds in a row logged one Supabase statement timeout, and `/emissions` kept two "no data" blocks. This session did not touch that page; the route check passed on build 2, whose only difference is the words of the capture table's head. A fourth rebuild was not tried.
- **`check-seller.mjs` exits 1** on 12 checks of sections session 212 removed (the months, the hybrid section, the old section ids). Only its capture checks were rewritten. `check-seller-deeper.mjs` and `check-seller-face.mjs` were not run.
- **No accessibility or design tool was run** on the new chart and table.
- **The whole suite on a clean copy was not run**: 33 modules were.
- `scripts/freeze.py status` not run: nothing was pushed.

## The landing

filled by the orchestrator
