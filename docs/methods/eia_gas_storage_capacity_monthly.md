# Underground natural gas storage capacity and fields by state and region, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_storage_capacity_monthly`

The table is built by `warehouse/connectors/eia_gas_storage_capacity.py` (session 626). It holds EIA's underground natural gas storage capacity, total and working gas, and the number of storage fields, by state, storage region, the lower 48 and the U.S., a month (Form EIA-191, as the docstring names it).

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Monthly, underground storage capacity (API v2, route `natural-gas/stor/cap`), source id `eia:natural-gas/stor/cap`, page `https://www.eia.gov/dnav/ng/ng_stor_cap_dcu_nus_m.htm`.
- Address: `https://api.eia.gov/v2/natural-gas/stor/cap/data/?frequency=monthly&data[]=value&facets[process][]=SAC&facets[process][]=SACW0&facets[process][]=SAD&start=1989-01`, in pages of 5,000 rows. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 1989 to July 2026. Its header counts 24,006 records of EIA's and 23,980 rows; it was written by run `20261022T035930Z` (22 October 2026, UTC) from pages an earlier run saved, 0 requests of 13.
- The variables begin at different months in this file: `total_capacity` in January 1989, `working_capacity` in January 2012 and `storage_fields` in January 2013.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_storage_capacity/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 1989-01). `--out-dir` writes a trial table elsewhere.
- Ceiling: 13 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per series and month.

- `entity`: `eia_gas_storage_capacity:<series>`, EIA's series id, one a process and area (for example `eia_gas_storage_capacity:N5290US2`, the U.S. total capacity, and `NA1394_SAL_8`).
- Areas taken: any state (`S<state>`), `NUS` the U.S., `R48` the lower 48, EIA's storage regions `R83` to `R86` and `R91`, and `R87` to `R89`, the AGA regions of the early years. Any other area stops the run.
- `variable`, EIA's process code and unit (a process in another unit stops the run):
  - `total_capacity` (SAC), `MMcf`
  - `working_capacity` (SACW0), `MMcf`
  - `storage_fields` (SAD), `count`
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US-<state>` for a state, `US` for the U.S., the lower 48 and the regions. `market` is blank. `node`: EIA's series name (for example "U.S. Total Natural Gas Underground Storage Capacity (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 123 entities, 41 a variable.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process, unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A blank has no row; nothing is filled. The header's two counts differ by those blanks.
- No gas in storage, injections or withdrawals: those are in `eia_gas_storage_state_monthly`.
- No field or company detail: the figures are EIA's sums by area.
- The states are parts of the lower 48 and the U.S., and so are EIA's regions: a sum must take one level.
