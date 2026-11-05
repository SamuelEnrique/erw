# EIA energy-related CO2 emissions by state, sector and fuel, a year

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_co2_state_annual`

Connector: `warehouse/connectors/eia_co2_state.py` (session 530).

## Publisher and report

U.S. Energy Information Administration (EIA), State Energy-Related Carbon Dioxide Emissions, read through EIA's API v2, route `co2-emissions/co2-emissions-aggregates`. Source code `eia:co2-emissions/co2-emissions-aggregates`; the report's page is `https://www.eia.gov/environment/emissions/state/`. The connector asks

`https://api.eia.gov/v2/co2-emissions/co2-emissions-aggregates/data/?frequency=annual&data[]=value&start=1970`

in pages of 5,000 records, sorted by year, state, sector and fuel, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and redacted in every `source_url`.

## Vintage and revision rule

- Years 1970 to 2022, retrieved 2026-10-21. `vintage` is empty.
- Written with `ip.write_snapshot`: a run replaces the whole table, so a year EIA revises is replaced at the next run.
- Ceiling: 17 requests a run (about 14 pages from 1970). A page an earlier run saved in `warehouse/raw/eia_co2_state/` is reused unless `--fresh`; `--offline` asks nothing.

## Shape and columns

Series shape: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`.

- `entity`: `eia_co2:<state>:<sectorId>:<fuelId>`, EIA's codes, for example `eia_co2:AK:EC:CO`.
  - Sectors: `CC` commercial, `EC` electric power, `IC` industrial, `RC` residential, `TC` transportation, and `TT` all sectors.
  - Fuels: `CO` coal, `NG` natural gas, `PE` petroleum, and `TO` all fuels.
  - States: the 50 states, DC and `US` (52 codes); 1,248 entities.
- `variable`: `co2` only, unit `tCO2`: EIA's million metric tons of CO2 times 1,000,000.
- `ts_utc`: the year's 1 January; `freq` `P1Y`; `geo` `US-<state>`, or `US` for the U.S.; `market` empty.
- `node`: EIA's names joined, for example "Alaska, Electric Power carbon dioxide emissions, Coal".

From the header: 66,144 records of EIA's, 66,144 with a value.

## Using the levels

`TT` and `TO` are EIA's own totals. A sum takes one level and leaves `TT` and `TO` out; adding the totals to the parts counts the same emissions twice.

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy-Related Carbon Dioxide Emissions")."

## Cross-check

None in the connector. It checks its own reading: the rows read must equal EIA's `total`; a unit other than million metric tons of CO2 stops the run; a record without a state, sector or fuel stops it; an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A blank has no row; nothing is filled (none was blank in this run).
- No year after 2022, the latest the API gave.
- No other gas and no emissions outside energy use: energy-related CO2 only.
- No fuel finer than coal, natural gas and petroleum, and no plant or utility figures.
