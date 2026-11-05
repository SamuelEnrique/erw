# Natural gas consumption by state and sector, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_consumption_state_monthly`

The table is built by `warehouse/connectors/eia_gas_consumption_state.py` (session 518). It holds EIA's monthly natural gas consumption by state for the residential, commercial, industrial and electric power sectors, and the U.S. total.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Monthly, consumption by state (API v2, route `natural-gas/cons/sum`), source id `eia:natural-gas/cons/sum`, page `https://www.eia.gov/naturalgas/monthly/`.
- Address: `https://api.eia.gov/v2/natural-gas/cons/sum/data/?frequency=monthly&data[]=value&facets[process][]=VRS&facets[process][]=VCS&facets[process][]=VIN&facets[process][]=VEU&facets[process][]=VC0&start=2001-01`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 2001 to July 2026. Its header counts 63,855 records of EIA's, 63,420 with a value; it was written by run `20261021T202219Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 30.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_consumption_state/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 2001-01). `--out-dir` writes a trial table elsewhere.
- Ceiling: 30 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area, process and month.

- `entity`: `eia_gas_consumption:<process>:<area>`, EIA's process code and area code: `S<state>` (for example `SAK`), or `NUS` for the U.S. Any other area stops the run.
- `variable` and EIA's process code, every one in `MMcf` (EIA's million cubic feet, kept):
  - `consumption_residential` (VRS)
  - `consumption_commercial` (VCS)
  - `consumption_industrial` (VIN)
  - `consumption_electric_power` (VEU)
  - `consumption_total` (VC0): the four sectors plus vehicle fuel, lease and plant fuel and pipeline fuel. A sum over the variables must leave it out.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US-<state>` or `US`. `market` is blank. `node`: EIA's series name (for example "Alaska Natural Gas Residential Consumption (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

In this file the four sectors have 51 or 52 entities each (the state areas and the U.S., as EIA gives them); `consumption_total` has one, the U.S. (`NUS`).

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process, unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A figure EIA withholds (a blank in the API) has no row; nothing is filled. The header's two counts differ by those blanks.
- EIA's vehicle fuel, lease and plant fuel, pipeline fuel and its deliveries total are not taken; each is inside `consumption_total`.
- No state total in this file: `consumption_total` is the U.S. only, and a state's four sectors do not make its total (the total holds the fuels above as well).
- No heat content: volumes only.
