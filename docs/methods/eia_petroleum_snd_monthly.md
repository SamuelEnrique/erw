# Petroleum supply and disposition: crude oil and every product of the route, the U.S. and the five PADDs, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_petroleum_snd_monthly`

Connector: `warehouse/connectors/eia_petroleum_snd.py` (session 555; products added in sessions 574, 600, 601 and 610).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, supply and disposition, read through EIA's API v2, route `petroleum/sum/snd` (source id `eia:petroleum/sum/snd`). Report page: `https://www.eia.gov/petroleum/supply/monthly/`. The connector asks, once for each group of products:

`https://api.eia.gov/v2/petroleum/sum/snd/data/?frequency=monthly&data[]=value&facets[product][]=<each product of the group>&start=2015-01`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 14 requests a run.

The products are asked in five groups, each its own request, so a group's saved pages answer it again: session 555's eight (EP00 the total, EPC0 crude oil, EPM0F finished motor gasoline, EPD0 distillate, EPJK jet fuel, EPLLPA propane, EPPR residual fuel, EPOOXE fuel ethanol), session 574's twelve (kerosene, aviation gasoline, asphalt, petroleum coke, lubricants, natural gas plant liquids, ethane, normal butane, isobutane, unfinished oils, biodiesel and renewable diesel), and sessions 600, 601 and 610's ten, seventeen and eleven. The docstring says the table now holds every product of the route. The header lists all 58 product codes; EP00, the total, holds the others. The header's access line still says `<each of eight>`, from session 555's single group.

## Vintage and revision rule

The header gives months 2015-01 to 2026-07: 533,519 records of EIA's, 523,835 rows (the rest were blanks). The run of 22 October 2026 (`20261022T023332Z`) asked 0 requests: every page came from `warehouse/raw/eia_petroleum_snd/`. The previous file held 475,869 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run. `--from YYYY-MM` sets the first month (default 2015-01); there is no separate early window. The docstring gives the reason for 2015: the route holds about 40 products and 3,949 records a month, beyond a run's ceiling.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_petroleum_snd:<series>`, EIA's series id, one a process, product and area in one unit (for example `eia_petroleum_snd:MCREXP11`). The table holds 4,459 entities.
- `variable`: EIA's process as a word, with `_per_day` added for EIA's thousand barrels a day:
  - `field_production` (FPF), `refinery_net_production` (YPR), `refinery_net_input` (YIR), `imports` (IM0), `exports` (EEX), `net_receipts` (VNR), `stock_change` (SCG), `product_supplied` (VPP), `supply_adjustment` (VUA), `renewable_plant_production` (YNP), `transfers_to_crude_supply` (TVP): each in `kbbl` (thousand barrels in the month) and as `<variable>_per_day` in `kbbl/d`;
  - `ending_stocks` (SAE): `kbbl` only in this table.
- `unit`: `kbbl` or `kbbl/d`; EIA's `mbbl` and `mbbl/d` are kept at a factor of 1.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name (for example "East Coast (PADD 1) Exports of Crude Oil (Thousand Barrels)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Areas the connector accepts: the U.S. (NUS, NUS-Z00) and the five PADDs (R10 to R50, each also with the suffixes Z00 and Z0P). The PADDs are parts of the U.S.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process, unit or area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless each group's rows read equal the total EIA counts. Several narrower ERW tables repeat parts of this one: `eia_ngl_production_monthly` (`field_production`), `eia_refinery_inputs_monthly` (`refinery_net_input`) and `eia_refinery_production_monthly` (`refinery_net_production`) say in their connectors that their U.S. and PADD series are also here.

## What it does not hold

- No month before 2015-01.
- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No refining districts or states: only the U.S. and the five PADDs.
- No product outside the five groups: a product EIA adds to the route later is not asked until a group names it.
