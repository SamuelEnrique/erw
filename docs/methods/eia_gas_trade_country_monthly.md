# Natural gas exports and imports by country and mode, volumes and prices, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_trade_country_monthly`

The table is built by `warehouse/connectors/eia_gas_trade.py` (session 625, made from session 622's `eia_padd_movements.py`). It holds EIA's monthly U.S. natural gas exports and imports by country of destination or origin and by mode (pipeline, LNG by vessel, truck, compressed, re-exports), with the volume and the price of each.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it, two routes of Natural Gas Monthly:
  - exports by country (API v2, route `natural-gas/move/expc`), source id `eia:natural-gas/move/expc`;
  - imports by country (API v2, route `natural-gas/move/impc`), source id `eia:natural-gas/move/impc`;
  - page for both: `https://www.eia.gov/naturalgas/monthly/`.
- Addresses: `https://api.eia.gov/v2/natural-gas/move/expc/data/?frequency=monthly&data[]=value&start=1973-01` and `https://api.eia.gov/v2/natural-gas/move/impc/data/?frequency=monthly&data[]=value&start=1973-01`, in pages of 5,000 rows sorted by period and series. No process facet is set: every series of each route is asked for. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 1973 to July 2026. Its header counts records of EIA's, exports 23,713 and imports 16,010, and 30,337 rows; it was written by run `20261022T035426Z` (22 October 2026, UTC) from pages an earlier run saved, 0 requests of 20.
- Volumes begin in January 1973 and prices in January 1989 in this file.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_trade/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 1973-01). The run asks one window per route, from that month to the latest. `--out-dir` writes a trial table elsewhere.
- Ceiling: 20 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per series and month.

- `entity`: `eia_gas_trade:<series>`, EIA's series id, one a mode, country and unit (for example `eia_gas_trade:N9132CN2`, pipeline exports to Canada). The mode is EIA's process code, kept in the series id and named in `node`; EIA's area is `NUS-<country>`, with `NUS-Z00` the U.S. total. An area other than `NUS-Z00`, `NUS-ZXC` or `NUS-N<two characters>` stops the run.
- `variable`, set by EIA's unit:
  - `volume`, `MMcf` (EIA's million cubic feet in the month)
  - `price`, `USD/Mcf` (dollars per thousand cubic feet)
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US` on every row. `market` is blank. `node`: EIA's series name, which names the mode and the country of destination or origin (for example "U.S. Natural Gas Pipeline Exports to Mexico (MMcf)").
- `source`: the route's source id, so a row says whether it is an export or an import. `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

In this file the export route gives 77 volume and 77 price series, the import route 27 volume and 26 price series.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: for each route the rows read must equal the total EIA's API counts, a unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice, on two pages or in both routes, stops it.

## What it does not hold

- A blank has no row; nothing is filled. The header's counts of EIA's records and of rows differ by those blanks.
- No port or terminal detail, and no trade by state: the routes are U.S. totals by country and mode.
- No heat content: volumes in MMcf and prices per Mcf, as EIA gives them.
- The countries are parts of the U.S. total (`NUS-Z00`) of the same mode: a sum must take one level.
