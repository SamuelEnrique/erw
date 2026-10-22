# EIA State Energy Data System: each state's consumption, prices and expenditures, a year

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_seds_state_energy`

Connector: `warehouse/connectors/eia_seds.py` (session 507; more series and the saved-page rule since session 546).

## Publisher and report

U.S. Energy Information Administration (EIA), State Energy Data System (SEDS), read through EIA's API v2, route `seds`. Source code `eia:seds`; the report's page is `https://www.eia.gov/state/seds/`. The connector asks for its 27 series in one paged query:

`https://api.eia.gov/v2/seds/data/?frequency=annual&data[]=value&facets[seriesId][]=<id>...&start=1990`

in pages of 5,000 records, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and redacted in every `source_url`.

## Vintage and revision rule

- Years 1990 to 2024 (SEDS itself starts in 1960; this table from 1990). Retrieved 2026-10-21. `vintage` is empty.
- Written with `ip.write_snapshot`: a run replaces the whole table, so EIA's revisions replace the earlier figures. The run of 21 October 2026 wrote 49,140 rows; the previous file held 23,660, before session 546's series were added.
- Ceiling: 20 requests a run. A page an earlier run saved in `warehouse/raw/eia_seds/` is reused unless `--fresh`; `--offline` asks nothing.

## Shape and columns

Series shape: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`.

- `entity`: `eia_seds:<seriesId>:<state>`, for example `eia_seds:CLTCB:AK`. States: the 50 states, DC and `US` (52 codes).
- `variable`: `value` for every row; the series id in the entity says what it is, and `node` gives EIA's series name.
- `ts_utc`: the year's 1 January; `freq` `P1Y`; `geo` `US-<state>`, or `US` for the U.S.; `market` empty.
- Units: billion Btu as `TBtu` (times 0.001); dollars per million Btu as `USD/MMBtu`; million dollars as `USD` (times 1,000,000).

The series (each 1,820 rows: 52 codes over 35 years):

- Consumption, `TBtu`: `TETCB` total energy; `ESTCB` electricity (sales to ultimate customers); `NGTCB` natural gas; `CLTCB` coal; `PATCB` all petroleum products; `RETCB` renewable energy; `NUETB` nuclear energy consumed for electricity generation.
- Electricity consumed by sector, `TBtu`: `ESRCB` residential, `ESCCB` commercial, `ESICB` industrial, `ESACB` transportation.
- Natural gas consumed by sector, `TBtu`: `NGRCB` residential, `NGCCB` commercial, `NGICB` industrial, `NGEIB` electric power, `NGACB` transportation.
- Electricity price, `USD/MMBtu`: `ESRCD` residential, `ESCCD` commercial, `ESICD` industrial, `ESTCD` all sectors.
- Natural gas price, `USD/MMBtu`: `NGRCD` residential, `NGCCD` commercial, `NGICD` industrial, `NGEID` electric power, `NGTCD` all sectors.
- Expenditures, `USD`: `ESTCV` electricity, `TETCV` total energy.

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy Data System")."

## Cross-check

None in the connector. A unit outside its map stops the run, and so does an (entity, variable, ts_utc) given twice.

## What it does not hold

- SEDS's figures are EIA's estimates, as its technical notes describe them. Nothing is filled here, and a withheld or missing value has no row.
- No year before 1990 and none after 2024.
- Only the 27 series above, chosen by the connector; no other SEDS series.
- Prices are in dollars per million Btu, not cents per kWh; no conversion is made.
