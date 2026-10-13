# Session 212 report: "What a generator earns" on the battery page's three questions

13 October 2026, from 01:55 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `wip/212-generator-layout`, from `wip/203-brand-battery` (decision 1), pushed, **not landed** (the chain prompt: "Do NOT land"). Model spend USD 0. Pulls: none. No data lock, no warehouse table written. No em dash in anything written.

## Read these first

- **The page asks the battery page's three questions, in its order, with its components.** "What did it earn?": the summary sentence, the three headline numbers, the revenue chart by year, the income table (the last twelve months beside the long-run averages), one sentence of what the model cannot see, the two CSV lines, and the reader's own year of output. "Is it worth building?": scenarios A and B on the shared block, ten assumptions now (the contract's share and price last, 0 by default), and the results table with its eight rows as before. "What matters most": the NPV sensitivity chart with one line on how to read it, the contract rows drawn only when the scenario holds a contract. Screenshots before and after, 1280 and 390 px: `docs/brand/review-212/`.
- **Every number at the default is unchanged except the ones the hurdle rate moves.** The two checked numbers that stay (the headline's coverage, 0.67 times, and its debt payments, USD 7,078,769) are identical before and after at both widths; `check-values` 345 of 345 across the three cost-of-power pages. The hurdle rate (12 since session 208, Lazard's cost of equity; 9.6 until then) moves NPV, the sentence under the table and the chart's bars, and nothing else: at the default case NPV is USD -74.16 million (USD -741.60 per kW) at 12 where it was USD -78.43 million (USD -784.25 per kW) at 9.6; IRR, coverage, the worst month, the capture price and the breakeven contract price do not read it. The full list, bar by bar: `docs/brand/review-212/numbers_before_after.txt`.
- **What left the page is in two CSV downloads, computed by the page's own code.** `months.csv` (every month: revenue, energy, the capture price and rate, each month's coverage at scenario A's costs) and `tables.csv` (long form, a row a cell: the capture price at every hub and zone over the last twelve months, by year at the hub in both markets, every public hub of every grid by year, the plant with a battery beside it in both rows, the stress days, the fleet's hours as EIA reports them). What the page computes moved out of `page.tsx` into `model.ts`, unchanged line for line, so a download is the same read and arithmetic as the page; in review a visitor is answered 404, as the page is. 425 check keys left the page, every one a monthly row, a stress day, or a statistic of a section the downloads hold.
- **Gone outright, for your ruling:** the premium chart by year (its figures are in the download and in the second headline number), the "Debt coverage" section (the headline's coverage and the results row stay), the standalone contract panel and "With your contract" (`SellerContract.tsx` on disk, undrawn), and the three capture tables as tables. Kept on the page where the ruling named no place: the reader's own year of output ("Your plant's profile", a tool, not a table), under the first question (decision 3).
- **Not restyled on the brand.** `docs/brand.md` says no page but the battery's takes the brand until Samuel approves it; the generator page keeps the site's style (cardinal bands, Georgia). The layout is the battery's; the sheet is not (decision 2).

## What to review

1. The screenshots: https://github.com/SamuelEnrique/erw/tree/wip/212-generator-layout/docs/brand/review-212 (`generator_before_1280.png` against `generator_after_1280.png`, then the two at 390 px; `README.md` says what to look at).
2. The numbers: `docs/brand/review-212/numbers_before_after.txt` on the same branch.
3. To see it live on the old laptop: `git switch wip/212-generator-layout`, `cd site`, `npm run build`, `npx next start -p 3212`, open http://localhost:3212/internal/open, then http://localhost:3212/cost-of-power/seller . The downloads: `/cost-of-power/seller/months.csv` and `/cost-of-power/seller/tables.csv`.

## What was done

1. **The contract as two scenario assumptions** (`lib/seller/finance.ts`): `cshare` (letter `n`, percent, 0 to 100, step 10 points) and `cprice` (letter `p`, USD, 0 to 1,000, step USD 1); `Contract` says the asset's form, a share of the energy at a price per MWh (solar, wind) or a toll on a share of the capacity in USD per kW-month (a battery, a peaker), and `contractYear`, `merchantShare`, `incomeInYear`, `flows`, `coverage`, `resultOf` and `sensitivity` read it, with `FINANCE_KEYS` the eight of session 186. A missing key is read as 0, so every older address is a merchant case. The sensitivity chart draws the contract's rows only when the scenario holds a contract (session 211's rule). The breakeven contract price row does not read the contract: it is the price for the whole of the energy.
2. **The block and the chart** (`SellerScenarios.tsx`): the block is handed `chart: null`; `SellerSensitivity` draws the shared `Sensitivity` in the third section; `useBlock` holds what both read. The headline's coverage (`CoverHeadline`) reads A's contract, unkeyed when contracted (the table holds no contract), with the contract named in its note. `MonthsOfA`, `CoverageOfA` and `DscrOfA` stay on disk for a page that draws the months.
3. **The page** (`page.tsx`): three `ToolSection`s inside `data-question` wrappers; `model.ts` holds what the page computed before (every line moved, none changed); `csv.ts` the three lines the two routes share; `months.csv/route.ts` and `tables.csv/route.ts` the downloads, each gated on the page's status. The sentence of what the model cannot see is the asset's (solar and wind: the fleet's shape, the hub's price, nothing curtailed, no capacity or ancillary payment; a peaker: no start cost, no minimum run; a battery: energy alone), with a link to the note's new "cannot-see" anchor.
4. **The checks.** `test-seller-finance.mjs`: the session 212 block (twelve assertions on the contract's arithmetic, the address and the chart's rows). `check-seller-scenarios.mjs`: the chart read from the document, the worst month and the pair read from the two downloads (fetched by the browser with the internal cookie, parsed), the three questions' order, the how-to-read line, section 9 rewritten as the contract as assumptions (as session 208's battery check), a visitor's 404 for the download, the hurdle rate's stale pins of 9.6 moved to 12. Nine test modules' pins moved (decision 5).
5. **The note** (`docs/methods/generator_earns_algorithm.md`): a session 212 lead to section 4 (what the page draws now, what each download holds, what is gone), the "What the model cannot see" list with its anchor, 4.10 marked gone, 11.1's two new rows and the contract's formulas.

## Checks, with exit codes

None piped; outputs under `runs/session212/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py` (session 211's, 01:15 UTC; the same duty holds) | 0 | on duty until 13 October 17:15 UTC |
| `node scripts/test-seller-finance.mjs` (after the pins moved and the session 212 block added) | 0 | all passed |
| `npx tsc --noEmit`, twice | 2, 0 | the first: one import from the wrong module, fixed |
| `npm run build`, twice (the restructure; the final route) | 0, 0 | no "statement timeout" line |
| `runs/session208/capture.mjs` before and after, 1280 and 390, and at `?ah=9.6` | 0 ×6 | 430 keys before, 2 after; the 2 identical; 425 gone to the downloads |
| `runs/session212/cells.mjs` at 12 and at 9.6 | 0, 0 | NPV, the sentence and the bars move; every other cell identical |
| `python -m unittest` on the 16 modules that read the seller page, before the pins moved (`tests1.out`) | 1 | 270 tests, 13 failures and 1 error: every one a pin of a section or a line that moved (listed in decision 5) |
| the same 16 after the pins moved (`tests2.out`, `tests3.out`) | 0 | 270 tests OK |
| `node scripts/check-seller-scenarios.mjs http://localhost:3212`, twice | 1, 0 | the first: two rounding comparisons against the CSV (whole dollars there), fixed in the check; the second 98 of 98 |
| `CHECK_VALUES_PAGES=/cost-of-power/seller node scripts/check-values.mjs` (`MSYS_NO_PATHCONV=1`) | 1 | 8 of 8 values match; the exit is the script's own floor of ten values a run, which a restricted run of this page alone no longer reaches (the page keeps two keys; the seller tab's other addresses the rest) |
| `CHECK_VALUES_PAGES=/cost-of-power node scripts/check-values.mjs` (the three cost-of-power pages) | 0 | 345 of 345 values match Supabase |
| `CHECK_VALUES_PAGES=/cost-of-power/battery` | 0 | 254 of 254 (the shared block's change of session 211 is on this branch too) |
| `node scripts/test-battery-finance.mjs`, `test-decisions-195.mjs` | 0, 0 | |
| `curl` of `months.csv` as a visitor | | 404 "in review" |
| `scripts/freeze.py status` | not run | nothing deployed |
| Whole suite in a clean copy | not run | not landed; the chain prompt says not to. Run it before the landing |

## Decisions made without you

1. **The branch comes from `wip/203-brand-battery`, not `main`.** The three-question layout, the exported `Sensitivity`, the Reset names and the seller library's hurdle rate of 12 live only there; a branch from `main` would have had to repeat them. The landing order is therefore the battery first, then this. Reversible: a rebase.
2. **No brand sheet on the generator page.** `docs/brand.md`: "Samuel approves the battery, Grid and price board mockups before any other page changes." The layout is the battery's; the type, colors and table bands are the site's. When the brand is approved the battery's `brand.css` is one sheet to share (it is scoped to `.brand-a`).
3. **"Your plant's profile" stays, under the first question, as "Your plant's own year".** The ruling lists folds, contract sections and "cannot see" lists to remove and sends extra tables to the CSV; the profile is a tool (a year of the reader's own output, priced in the browser), not a table, and belongs to "What did it earn?". Removing it is one block.
4. **The premium chart and the "Debt coverage" section are gone, not kept.** Neither is one of the three questions' components; the premium figures are in `tables.csv` and in the second headline number, the coverage statistics follow from `months.csv`. Both are one block each to restore.
5. **Nine test modules' pins moved**, each with a session 212 note: 107 (no Fold), 145 (the pieces and parts as the page holds them now; the one "cannot see" sentence allowed on the face), 153 and 196 (a page line now in `model.ts`), 162 (the three blocks as the download and the model hold them), 183 (the page read with `model.ts`; the hybrid's "whatever hub is chosen" line in the download's header), 186 (ten assumptions; the block in the second question, the chart in the third), 195 (the months' components gone from the page).
6. **The two downloads' names** are `erw_generator_months_<grid>_<asset>_<hub>.csv` and `erw_generator_tables_...csv`, the battery's pattern. `tables.csv` is long form (table, row, column, value, note) so that six tables of different shapes are one file; a value not held is blank with its reason in the note.
7. **The capture tables are not drawn in any form**, as the ruling's "extra tables go into the CSV download" reads. The hub picker in the panel still opens every hub, so the second headline number is the capture price at any hub.
8. **The contract's bounds are 0 to 1,000 for the price** (a battery's toll and an energy price share one field), and the chart's step is USD 1 with the asset's unit written beside it.
9. **The note's 11.1 table still names the hurdle rate's old default** (9.6) in its old row; session 208 added its paragraph and did not move the row. Not changed here, listed for a note session.

## For Samuel's ruling

1. The page, from the screenshots: the three questions on the generator, and the three removals of decision 4 (the premium chart, "Debt coverage", the capture tables) against keeping any of them.
2. "Your plant's own year" under the first question (decision 3), or off the page.
3. The brand sheet for this page (decision 2), when the battery's is approved.
4. The landing order: the battery (`wip/203-brand-battery`) first, then this branch.
5. `check-values`' floor of ten values a run, which a restricted run of this one page no longer reaches: raise the page's keys (the results table's cells could carry them) or lower the floor for a restricted run.
6. Session 208's and 211's open items stand.

## To finish

- The landing, after the battery's: `git switch -c task/212-generator-layout wip/212-generator-layout`, `git merge origin/main`, the whole suite in a clean worktree, `npm run build`, the before snapshot as its own command, `git push`, the after snapshot and the comparison (the seller page is in review: 0 differences expected on the 25 pages).

## The prompt

Chain of 12 October, evening, sessions 210 to 213, code machine, unattended. Session 212: "'What a generator earns' (site/app/cost-of-power/seller), the battery page's layout. Branch wip/212-generator-layout. Do NOT land. 1. The same three questions as the battery page, in the same order and the same components: 'What did it earn?' (headline, three numbers, revenue chart, income table), 'Is it worth building?' (Scenarios A and B with a contract share and price defaulting to 0, and the results table), 'What matters most' (the NPV sensitivity chart with its one-line how-to-read; contract rows only when a contract is entered). 2. Defaults: hurdle 12 percent (Lazard cost of equity), every default grey with source, editable, Reset. Remove folds, standalone contract sections and 'what this model cannot see' lists the same way session 208 did; one sentence of the key limits under the income table; extra tables go into the CSV download. 3. Every number at the default is unchanged except those the hurdle rate moves (list them, old and new). check-values passes. Screenshots at 1280 and 390 to docs/brand/review-212/."
