# Energy equities: the page files and their rules

Energy Research Warehouse (ERW), method note written in session 10000 (chain 701, part D) on 26 November 2026. Contract: `docs/state/page_files_equities.md`. Sources and verdicts: `docs/reviews/equities-sources-2026-11-26.md`.

## What the files hold today

Builder: `warehouse/derived/equity_pages.py` (no request; warehouse tables only), a daily step of the data machine. It writes `site/data/equities/index.json`, `board.json` and `energy_prices.json`.

- **The equity side is held.** SEC EDGAR, the one public source of each company's industry code (SIC), share count and statements, refuses the ERW's contact string (HTTP 403, "Undeclared Automated Tool"); and no free source of daily share prices or index levels lets the ERW keep them (Stooq's robots file refuses every reader, Nasdaq forbids storing, Tiingo and Alpha Vantage need keys and are internal). So `index.json` lists the fifteen segments with the reason their rule cannot be applied and no company or index; every row of `board.json` is held (`not_held`) with that reason; no company, index or segment file is written. A page draws each blank with its reason.
- **The energy prices are the warehouse's own** (`energy_prices.json`): WTI, Brent and Henry Hub spot (`eia_fuel_spot_prices`, daily), ERCOT's hub average day-ahead daily mean (`ercot_hub_prices_daily`, `da_mean`), CAISO's SP15 and NP15 day-ahead daily means (`iso_hub_prices_history`, the mean of each complete Pacific day: 24 hours, 23 or 25 on the clock-change days; a day short of an hour is not written), uranium (`imf_commodity_prices`, PURAN, monthly, on its own dates), and California's carbon allowance at its quarterly auctions (`carb_auction_allowance_prices`, current vintage, on its own dates). PJM, NYISO and ISO-NE (held by their terms, `docs/licenses.md`) and MISO (paused) are series with a status and no rows.
- **Span.** Each daily series from 2016-01-01: the contract's span is that of the longest shown equity series, and none is shown yet (a dated line of the contract).

## Moves

Each series' `moves`, as the board computes its own rows': `d` the previous day held; `w` the last day held on or before 7 calendar days back; `m` one calendar month back; `ytd` the last day held of the previous year; `y` one calendar year back. `ch` is the last value less the value then, `pct` that over the value then times 100. No score, no signal, no view.

## The rules that wait for the SEC

When EDGAR can be read, the universe is every company whose SEC industry code is an energy code, one segment by the code (integrated oil and gas 2911 with exploration; exploration and production 1311 and 1381; midstream 4922 to 4924 and 4610; refining 2911 without upstream; oilfield services 1389 and 3533; coal 1220 and 1221; regulated utilities 4911, 4931, 4932, 4939 with a rate base; independent power 4911 without; nuclear and uranium 1094 and the owners of reactors; solar 3674 makers of cells; wind 3511; storage, hydrogen and grid equipment by code 3690, 2810 and 3612 to 3613), a company that fits two codes in both and named in `segments_note`. This list is the draft of the written rule, to be fixed in this note before any company is placed; matched to `company_directory` by SEC number or exact legal name only.
