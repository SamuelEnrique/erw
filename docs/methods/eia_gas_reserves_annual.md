# Dry natural gas proved reserves and their changes by state and area, a year (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_reserves_annual`

The table is built by `warehouse/connectors/eia_gas_reserves.py` (session 552). It holds EIA's dry natural gas proved reserves at each year's end, and the changes that take one year's reserves to the next (adjustments, revisions, sales, acquisitions, extensions and discoveries, production), by state, part of a state and offshore area.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: U.S. Crude Oil and Natural Gas Proved Reserves (API v2, route `natural-gas/enr/dry`), source id `eia:natural-gas/enr/dry`, page `https://www.eia.gov/naturalgas/crudeoilreserves/`.
- Address: `https://api.eia.gov/v2/natural-gas/enr/dry/data/?frequency=annual&data[]=value&facets[process][]=<each>&start=1977`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers the years 1977 to 2021. Its header counts 20,174 records of EIA's and 19,232 rows; it was written by run `20261021T221659Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 9.
- The changes follow EIA's own breaks: `extensions`, `new_field_discoveries` and `new_reservoir_discoveries` run 1977 to 2015, and `extensions_and_discoveries` 2016 to 2021; `sales` and `acquisitions` begin in 2000.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a figure EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_reserves/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new years only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY` sets the first year (default 1977). `--out-dir` writes a trial table elsewhere.
- Ceiling: 9 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area, process and year.

- `entity`: `eia_gas_reserves:<process>:<area>`, EIA's process and area codes. Areas: `S<state>`, `NUS` for the U.S., `R48` the Lower 48, and EIA's parts of states and offshore areas: `RTX01` to `RTX10` Texas's districts (the file also holds `RTX07B`, `RTX07C` and `RTX08A`), `RLAN` and `RLASO` Louisiana's north and south, `RCAC`, `RCAJ` and `RCAL` California's coastal, San Joaquin and Los Angeles basins, `RNMEAST` and `RNMWEST` New Mexico's, and `RUSF`, `R5F`, `R44F`, `R1901F`, `RCASF`, `RLASF` and `RTXSF` federal and state offshore.
- `variable` and EIA's process code, every one in `bcf` (EIA's billion cubic feet):
  - `proved_reserves` (R11)
  - `adjustments` (R12)
  - `revision_increases` (R13) and `revision_decreases` (R14)
  - `sales` (R15) and `acquisitions` (R16)
  - `extensions` (R17), `extensions_and_discoveries` (R17A)
  - `new_field_discoveries` (R18) and `new_reservoir_discoveries` (R19)
  - `production` (R20)
- `ts_utc`: the year's 1 January at 00:00:00Z, standing for reserves at that year's end; `freq` `P1Y`.
- `geo`: `US-<state>` for a state, `US` otherwise. `market` is blank. `node`: EIA's series name. For R11, EIA's name reads "Dry Natural Gas Expected Future Production" (for example "U.S. Dry Natural Gas Expected Future Production (Billion Cubic Feet)"); the connector calls it `proved_reserves`.
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 561 entities, 51 a variable.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process or unit not in the map stops it, and a key given twice with two values stops it; a row EIA gives twice with the same value is kept once.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled. The header's two counts differ by those figures and by any row EIA gave twice with the same value (this header does not count those apart).
- Dry gas only: the route is `natural-gas/enr/dry`; wet gas, associated gas and crude oil reserves are not taken.
- No year after 2021 in this file.
- Parts of states and the Lower 48 repeat what the states and the U.S. hold: a sum must take one level.
