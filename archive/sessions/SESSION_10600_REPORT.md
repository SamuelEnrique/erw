# Session 10600 report (chain 730, lab-desktop second window): the start, parts A to E

26 November 2026, 10:52 to about 12:10 UTC. Folder `C:\Users\Shared\Documents\erw-w2` (documents, pushed to main) and a code worktree `C:\Users\Shared\Documents\erw-w2-predict` (branch `wip/c730-predict-v2`). Model spend: USD 0, no model API called. No warehouse table written, no data lock taken.

## What a reader will see that was not there before

- Nothing on a page yet: the files land through row 5 of `docs/state/landing_request_window2.md`, and window E builds `/forecast` on them. Once both land, a reader sees, for 29 places, the ERW's own forecast of tomorrow's demand by hour with a band, the last 35 days of the forecast beside what happened and beside the operator's forecast, and a report card in which the ERW loses to the operator in 21 of 29 places; for six places (TEX, ERCO, CENT, SWPP, CAL, CISO), the same for the day-ahead hub price.

## Commits

- `b0fd13f24` queue file taken by hand; `c586d9356` resume file 731; `f5a61df9c` the page-file contract and its three examples (part A); `8a5eac43d` resume file 631 removed (chain 630 closed, part B); `03398ea2d` the ground (part C); `eae871921` the demand method note; `435f03a9e` the data requests; `9222ebea0` the price method note; `ec52f7cd5` the correction (ISO-NE and NYISO held); `2ca26b52e` landing row 5; progress lines between.
- Branch `wip/c730-predict-v2` at `0cdfd65ad`: the code, the files, the tests, the replication (one commit).

## Rows and their state

- Part A: done. Part B: done (chain 630's landing and Redivis rows were done; 51 second looks on 45 tables left for part F). Part C: done. Part D: done; landing requested (row 5). Part E: done for ERCOT, SPP and CAISO; landing requested with D. Data requests 1 to 5: requested.

## The scores (last two years, mean absolute percent error)

- Demand, the ERW's regression against the operator: the operator wins in 21 places (worst for the ERW: CPLE 9.94 against 4.03, the Southeast 6.81 against 1.27, New England 7.99 against 2.80, Texas 5.22 against 2.08); the ERW wins in 8 (FPC 7.78 against 23.77, PSCO 6.67 against 13.64, CISO 4.27 against 8.50, CAL, CENT, SWPP, NW, PACE). In six of the eight the operator's own error over these two years is well above its error over the whole backtest, so those wins may reflect what the operator files rather than the ERW's skill. The regression beats yesterday's and last week's hour in every place.
- Price, mean absolute error in USD/MWh: ERCOT yesterday's price 13.07 (chosen; the regression 16.23), SPP regression 14.52 (yesterday 16.54), CAISO regression 5.91 (yesterday 6.20). On spike hours every method misses by hundreds or thousands of dollars.

## Errors and how they were caught

- **ISO-NE's and NYISO's prices were forecast at first.** The ground read the `license` column of `coverage.csv` (public) and not the per-publisher record (`license_verdicts.csv`: written permission needed; `license_status.csv`: `iso_hub_prices_history` license needed since 21 October). The whole suite's warnings named it. Fixed before anything landed: their price is held, the 96 ledger rows written for them removed, the documents corrected with a dated note, and the branch whose pushed history carried their prices replaced and deleted on GitHub (`wip/c730-predict`, last `1f006a073`). Its commits may still be reachable on GitHub by their hash for a while.
- **Module names collided.** `demand.py` and `run.py` in `warehouse/predict/` shadowed other tools' modules of the same names in the whole suite (4 failures, all this branch's). Renamed `predict_*`; the path is appended, not prepended; the test loads `run.py` under its own name.
- A stray command with an empty heredoc (which this chain forbids) hung on standard input; stopped at once, nothing changed, no process left.
- The first ledger rows (27 November) were made before the one-gap rule was tightened to match the note (a lone missing hour only); the rebuilt scores are equal to two decimals, and the ledger keeps the rows as made.

## Decisions made without you

- **Large authority:** mean demand of at least 5,000 MW over the last 365 days (16 authorities). The six that are whole regions appear under both names, as on `/demand`.
- **The hour the forecast is made:** demand at 20:00 UTC on the day before, from demand through two days before (the warehouse's EIA-930 copy lands at about 18:30 UTC); price at 14:00 UTC the day before, before the grids' day-ahead results.
- **"The same hour yesterday"** means the same hour of the latest whole day held when the forecast is made: two days before the target day for demand, the day before for price. Using the day before for demand would use a day not yet held.
- **No weather in the headline:** no dated weather forecast is held (the NWS table keeps only the latest). Asked of window A (request 4).
- **No wind or solar forecasts in the price:** neither table says when its forecast was published. Asked (request 5).
- **The flexible method (d)** is not built: without weather it has nothing to add; part F returns to it.
- **Price hubs:** ERCOT HB_NORTH, SPP SPPNORTH_HUB, CAISO SP15.
- **The page-file examples** sit in `docs/state/page_files_predict_examples/`, outside `site/`, so pushing them changed no page.
- **Precheck** run with `--dry-run --no-duty`: from a worktree `daily_cap` always fails (no cost ledger), and a recorded failure would send the machine's alert email for nothing.

## For Samuel's ruling

- None needed for the forecast to run. One plain question when you look: the ERW forecast loses to the operators in most places, and the page will say so in its first table. That is the chain's own rule ("nothing is hidden"), kept.

## Needs the key

- Nothing.
