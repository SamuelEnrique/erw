# Natural gas prices by state: citygate and the four consuming sectors, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_prices_state_monthly`

The table is built by `warehouse/connectors/eia_gas_prices_state.py` (session 517). It holds EIA's monthly natural gas prices by state: the citygate price and the price delivered to residential, commercial, industrial and electric power consumers.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Monthly, prices by state (API v2, route `natural-gas/pri/sum`), source id `eia:natural-gas/pri/sum`, page `https://www.eia.gov/naturalgas/monthly/`.
- Address: `https://api.eia.gov/v2/natural-gas/pri/sum/data/?frequency=monthly&data[]=value&facets[process][]=PG1&facets[process][]=PRS&facets[process][]=PCS&facets[process][]=PIN&facets[process][]=PEU&start=2001-01`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 2001 to July 2026. Its header counts 78,606 records of EIA's, 72,550 with a value; it was written by run `20261021T201723Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 30.
- `price_electric_power` begins in January 2002 in this file; the other four begin in January 2001.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_prices_state/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 2001-01). `--out-dir` writes a trial table elsewhere.
- Ceiling: 30 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area, process and month.

- `entity`: `eia_gas_price:<process>:<area>`, EIA's process code and area code: `S<state>` (for example `SAL`), or `NUS` for the U.S. Any other area stops the run.
- `variable` and EIA's process code, every one in `USD/Mcf` (EIA's dollars per thousand cubic feet, kept: no heat content is stated beside them):
  - `price_citygate` (PG1)
  - `price_residential` (PRS)
  - `price_commercial` (PCS)
  - `price_industrial` (PIN)
  - `price_electric_power` (PEU)
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US-<state>` or `US`. `market` is blank. `node`: EIA's series name (for example "Alabama Price of Natural Gas Delivered to Residential Consumers (Dollars per Thousand Cubic Feet)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 257 entities: 50 to 52 a variable.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process, unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A figure EIA withholds (a blank in the API) has no row; nothing is filled. The header's two counts differ by those blanks.
- EIA's own shares of sales (VFA, VFC, VRX) are not taken.
- No price per MMBtu: the unit is EIA's dollars per thousand cubic feet, and the ERW does not convert it.
- No import or export prices: EIA's prices by country and mode are in `eia_gas_trade_country_monthly`.
