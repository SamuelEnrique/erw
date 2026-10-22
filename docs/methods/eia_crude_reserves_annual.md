# U.S. crude oil proved reserves and their changes by state and area, a year

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_crude_reserves_annual`

Connector: `warehouse/connectors/eia_crude_reserves.py` (session 551).

## Publisher and report

U.S. Energy Information Administration (EIA), U.S. Crude Oil and Natural Gas Proved Reserves, crude oil, read through EIA's API v2, route `petroleum/crd/pres`. The report's page is `https://www.eia.gov/naturalgas/crudeoilreserves/`. The connector asks:

`https://api.eia.gov/v2/petroleum/crd/pres/data/?frequency=annual&data[]=value&facets[process][]=<each>&start=1977`

with the eight processes below as facets, in pages of 5,000 records sorted by period and series, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

The header gives years 1977 to 2021: 13,987 records of EIA's, 13,931 rows. `--from YYYY` sets the first year (default `1977`).

The table is written with `ip.write_snapshot`: each run replaces the whole table. A page an earlier run saved in `warehouse/raw/eia_crude_reserves/` is reused unless `--fresh`; `--offline` asks nothing. A revised figure at EIA reaches the table only through a page asked again. Ceiling: 9 requests a run. A read shorter than EIA's count stops the run.

A row EIA gives twice with the same value is kept once and counted in the run log; the same key with two values stops the run.

## Shape

Series. One row per process, area and year.

- `entity`: `eia_crude_reserves:<process>:<area>`, EIA's codes, for example `eia_crude_reserves:R01:NUS`. Areas (52 in the table): `S<state>`, `NUS` the U.S., `R48` the Lower 48, and EIA's parts of states and offshore areas: `RTX01` to `RTX10` Texas's districts, `RLAN` and `RLASO` Louisiana's north and south, `RCAC`, `RCAJ` and `RCAL` California's coastal, San Joaquin and Los Angeles basins, `RNMEAST` and `RNMWEST` New Mexico's, `RUSF`, `R5F`, `R44F`, `R1901F`, `RCASF`, `RLASF` and `RTXSF` federal and state offshore.
- `variable`, each in `kbbl` (EIA's million barrels times 1,000): `proved_reserves` (R01), `adjustments` (R02), `revision_increases` (R03), `revision_decreases` (R04), `sales` (R05), `acquisitions` (R06), `extensions_and_discoveries` (R07A), `production` (R10).
- `ts_utc`: the year's 1 January at 00:00:00Z, holding reserves at the year's end; `freq` `P1Y`; `geo` `US-<state>` for a state, `US` otherwise; `market` empty.
- `node`: EIA's series name.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

Parts of states and the Lower 48 repeat what states and the U.S. hold: a sum takes one level.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves").

## Cross-check

None in the connector. It stops on a unit or process not in its map, on a key given twice with two values, and on a read shorter than EIA's count.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled. `sales` and `acquisitions` have fewer rows than the other changes (1,131 against 2,274), and `extensions_and_discoveries` 299.
- Years after 2021: the header's span ends there.
- Natural gas reserves: only crude oil's processes are asked.
