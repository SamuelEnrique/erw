# Weekly heating oil and propane prices, residential and wholesale, by state and PADD

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_heating_fuel_prices_weekly`

Connector: `warehouse/connectors/eia_heating_fuel_prices.py` (session 605).

## Publisher and report

U.S. Energy Information Administration (EIA), Heating Oil and Propane Update (the State Heating Oil and Propane Program, weekly in the heating season, October to March), read through EIA's API v2, route `petroleum/pri/wfr`. The report's page is `https://www.eia.gov/petroleum/heatingoilpropane/`. The connector asks:

`https://api.eia.gov/v2/petroleum/pri/wfr/data/?frequency=weekly&data[]=value&facets[process][]=PRS&facets[process][]=PWR&start=2012-01-01`

in pages of 5,000 records sorted by period and series, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

The header gives weeks 2012-01-02 to 2026-10-19: 48,726 records of EIA's, 48,534 rows. Residential prices begin on 2012-01-02 and wholesale prices on 2013-10-07. `--from YYYY-MM-DD` sets the first week (default `2012-01-01`).

The table is written with `ip.write_snapshot`: each run replaces the whole table. A page an earlier run saved in `warehouse/raw/eia_heating_fuel_prices/` is reused unless `--fresh`; `--offline` asks nothing. A new week or a revised price reaches the table only through a page asked again. Ceiling: 13 requests a run. A read shorter than EIA's count stops the run.

## Shape

Series. One row per EIA series and week.

- `entity`: `eia_heating_price:<series>`, EIA's series id (one a product, process and area), for example `eia_heating_price:W_EPD2F_PRS_NUS_DPG`. Products: `EPD2F` (No. 2 heating oil) and `EPLLPA` (propane). Areas: `NUS` the U.S., `R10`, `R1X`, `R1Y`, `R1Z`, `R20`, `R30`, `R40`, `R50` (PADDs and PADD 1's subdistricts), and `S<state>`. 140 entities: heating oil residential 28, heating oil wholesale 32, propane residential 46, propane wholesale 34.
- `variable`: `residential_price` (process PRS, 27,174 rows) or `wholesale_price` (process PWR, wholesale/resale, 21,360 rows), unit `USD/gal` (EIA's dollars per gallon, factor 1).
- `ts_utc`: EIA's week date at 00:00:00Z; `freq` `P1W`; `geo` `US-<state>` for a state, `US` for the U.S. and the PADDs; `market` empty.
- `node`: EIA's series name, which names heating oil or propane.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Heating Oil and Propane Update").

## Cross-check

None in the connector. It stops on a unit, process or area not in its map, on a key given twice, and on a read shorter than EIA's count.

## What it does not hold

- Weeks outside the heating season have no rows, as EIA publishes none.
- A blank has no row; nothing is filled (48,726 records against 48,534 rows).
- Wholesale prices before 2013-10-07.
- Other products or processes of the route: only PRS and PWR are asked.
