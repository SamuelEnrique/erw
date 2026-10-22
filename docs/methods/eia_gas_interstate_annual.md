# Interstate and international natural gas movements by state, a year (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_interstate_annual`

The table is built by `warehouse/connectors/eia_gas_interstate.py` (session 550). It holds EIA's annual natural gas movements between pairs of areas: state to state, state to the federal Gulf of America, and state to Canada, Mexico and other countries, with each area's totals and net figures.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Annual, interstate movements (API v2, route `natural-gas/move/ist`), source id `eia:natural-gas/move/ist`, page `https://www.eia.gov/naturalgas/annual/`.
- Address: `https://api.eia.gov/v2/natural-gas/move/ist/data/?frequency=annual&data[]=value&facets[process][]=<each of nine>&start=1997`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers the years 1997 to 2024. Its header counts 29,475 records of EIA's and 29,470 rows; it was written by run `20261021T221643Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 19.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a figure EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_interstate/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new years only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY` sets the first year (default 1997). `--out-dir` writes a trial table elsewhere.
- Ceiling: 19 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per pair, process and year.

- `entity`: `eia_gas_interstate:<process>:<pair>`, EIA's process code and its area pair, from and to: `SAL-SFL` is Alabama to Florida. A second part `Z00` is the first area's total, `Z0R` and `Z0S` its parts as EIA names them. `R3FM` is the federal Gulf of America; `NCA` and `NMX` are Canada and Mexico (other `N` codes, such as `SAK-NJA`, are other countries as EIA gives them). `NUS` is the U.S.
- `variable` and EIA's process code, every one in `MMcf` (million cubic feet in the year):
  - `net_receipts` (MIN)
  - `receipts` (MIR) and `deliveries` (MID)
  - `net_across_borders` (IMB)
  - `imports_intransit` (IMI) and `exports_intransit` (EEI)
  - `net_receipts_imports` (MIE), `receipts_imports` (MIT) and `deliveries_exports` (MIF)
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` `P1Y`.
- `geo`: `US-<state>` of the pair's first area, `US` otherwise. `market` is blank. `node`: EIA's series name, which names both areas (for example "Alabama Natural Gas Interstate Receipts From Florida (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 1,903 entities.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process or unit not in the map stops it, and a key given twice with two values stops it. A row EIA gives twice with the same value, under two series ids, is kept once (the docstring's example: Louisiana's 2016 net receipts from the United Arab Emirates, `NA1290_SLA-NTC_2` and `NGM_EPG0_IMB_SLA-NTC_MMCF`); the header counts 3 such rows in this file.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled.
- Only the nine processes above are asked for.
- No monthly movements: this is the annual route only, and the file's last year is 2024.
- Totals (`Z00`), net figures and their parts are all EIA's and sit side by side: a sum must take one level.
