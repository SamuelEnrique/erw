# EIA Short-Term Energy Outlook: retail electricity prices, Henry Hub and the generation mix, monthly, each release kept

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_steo_forecasts`

Connector: `warehouse/connectors/eia_steo.py` (session 491).

## Publisher and report

U.S. Energy Information Administration (EIA), Short-Term Energy Outlook (STEO), read through EIA's API v2, route `steo`. Source code `eia:steo`; the report's page is `https://www.eia.gov/outlooks/steo/`. The connector asks:

- `https://api.eia.gov/v2/steo/facet/seriesId/` for the series list, and keeps the series it wants (below);
- `https://www.eia.gov/outlooks/steo/` for the release's date ("Release Date: <Month> <day>, <year>");
- `https://api.eia.gov/v2/steo/data/?frequency=monthly&data[]=value&facets[seriesId][]=<id>...&start=2020-01` in pages of 5,000.

Requests are 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and redacted in every `source_url`.

## Vintage and revision rule

- The API holds the current release only. The table holds the release of 2026-10-06, months 2020-01 to 2027-12, retrieved 2026-10-21.
- `vintage` is the release's date (2026-10-06T00:00:00Z). This is the one table of this batch written with `ip.write_csv` and the key (entity, variable, ts_utc, vintage), as docs/datastandard.md rule 5 allows when a table says so: each release is kept. A later release adds its rows beside the earlier ones; a run of the same release replaces the rows with the same key and keeps every other row.
- `--start` sets the first month (default 2020-01).
- Ceiling: 20 requests a run (the run of 21 October 2026 used 4).

## Shape and columns

Series shape, with two extra columns: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_kind, x_units_published`.

- `entity`: `eia_steo:<seriesId>`, for example `eia_steo:CLEPSHR_US`.
- `variable`: `value` for every row; `node` EIA's series description, for example "Coal share of U.S. electricity generation".
- `ts_utc`: the month's first day; `freq` `P1M`; `geo` `US`; `market` empty.
- `x_kind`: `forecast` for a month from the release's month on (2026-10 here), `history` for EIA's own figure for an earlier month. 795 forecast rows and 4,293 history rows.
- `x_units_published`: EIA's unit as published.

The 53 series and their units:

- Retail electricity price, `USD/kWh` (cents per kWh times 0.01, nominal dollars, as the STEO gives them): `ESRCU` residential, `ESCMU` commercial, `ESICU` industrial and `ESTCU` all sectors, each for the U.S. (`_US`) and the regions `ENC`, `ESC`, `HAK`, `MAC`, `MTN`, `NEC`, `PAC`, `SAC`, `WNC` and `WSC` (EIA's census divisions, with Alaska and Hawaii as `HAK`; for example "Retail Price of Electricity in Commercial Sector, East North Central"): 44 series.
- Henry Hub spot price, `NGHHUUS`, `USD/MMBtu`.
- U.S. generation shares, `ratio` (EIA's percentage divided by 100): `CLEPSHR_US` coal, `HVEPSHR_US` conventional hydropower, `NGEPSHR_US` natural gas, `NUEPSHR_US` nuclear, `RTEPSHR_US` renewables, `SOEPSHR_US` utility-scale solar, `WNEPSHR_US` wind and `XXEPSHR_US` other energy sources: 8 series.

5,088 rows from this release.

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Short-Term Energy Outlook, October 2026")."

## Cross-check

None in the connector. A unit outside its map stops the run; a page naming no release date stops it; an (entity, variable, ts_utc, vintage) given twice stops it.

## What it does not hold

- Forecasts are EIA's; nothing is filled or interpolated. A blank has no row.
- No release before 2026-10-06: the API keeps no earlier release, so the table begins with the first one the ERW read.
- No month before 2020-01.
- Only the series above: no STEO series for oil, coal or natural gas volumes, and no electricity demand or generation in energy units.
