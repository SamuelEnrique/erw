# Natural gas in underground storage by state: working gas, base gas, injections and withdrawals, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_storage_state_monthly`

The table is built by `warehouse/connectors/eia_gas_storage_state.py` (session 525). It holds EIA's monthly natural gas in underground storage by state and region: working gas, base gas and their total at the month's end, and the month's injections and withdrawals.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Monthly, underground storage by state (API v2, route `natural-gas/stor/sum`), source id `eia:natural-gas/stor/sum`, page `https://www.eia.gov/naturalgas/monthly/`.
- Address: `https://api.eia.gov/v2/natural-gas/stor/sum/data/?frequency=monthly&data[]=value&facets[process][]=SAO&facets[process][]=SAB&facets[process][]=SAT&facets[process][]=SAI&facets[process][]=SAW&start=2001-01`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 2001 to July 2026. Its header counts 55,015 records of EIA's, 55,015 with a value; it was written by run `20261021T211351Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 30.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_storage_state/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 2001-01). `--out-dir` writes a trial table elsewhere.
- Ceiling: 30 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area, process and month.

- `entity`: `eia_gas_storage:<process>:<area>`, EIA's process code and area code: `S<state>`, `NUS` for the U.S., or a region `R<code>`. In this file the regions are `R48`, `R83` to `R89` and `R91` (`R87` to `R89` are named in `node` as AGA regions, for example "AGA Producing Region"). Any other area stops the run.
- `variable` and EIA's process code, every one in `MMcf` (EIA's million cubic feet, kept):
  - `working_gas` (SAO), a stock at the month's end
  - `base_gas` (SAB), a stock at the month's end
  - `total_gas` (SAT), working and base gas, a stock at the month's end
  - `injections` (SAI), a flow over the month
  - `withdrawals` (SAW), a flow over the month
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US-<state>` for a state, `US` for the U.S. and every region (a region's name is in `node`). `market` is blank. `node`: EIA's series name (for example "AGA Producing Region Natural Gas in Underground Storage (Base Gas) (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 205 entities, 41 a variable.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process, unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A figure EIA withholds (a blank in the API) has no row; nothing is filled. In this file every record had a value.
- EIA's change in working gas (SAH) and net withdrawals (SAN), which follow from these, are not taken.
- No weekly storage report: this is the monthly route. No storage capacity: that is in `eia_gas_storage_capacity_monthly`.
- The states, the regions, the lower 48 and the U.S. sit side by side: a sum must take one level.
