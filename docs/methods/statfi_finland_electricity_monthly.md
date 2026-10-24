# Finland's electricity supply and consumption, a month (Statistics Finland table 12su)

Energy Research Warehouse (ERW), method note written in session 2275 (chain 103) for a table first written on 24 October 2026 (session 2273).

Tables: `statfi_finland_electricity_monthly`

## Publisher and address

Statistics Finland, StatFin table 12su, "Supplies and total consumption of electricity by Month, Electricity production/supply and Information" (`https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__ehk/statfin_ehk_pxt_12su.px/`). It is read through Statistics Finland's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, both at `https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12su.px`. Source id `statfi:12su`. Connector: `warehouse/connectors/statfi_electricity.py` (session 2273). pxdata.stat.fi has no robots file (HTTP 404). stat.fi's robots file disallows a few paths, none of them used here (session 2273, reads 443 and 444).

## Vintage and revision

January 1992 to June 2026, written by run `20261024T041229Z` (24 October 2026), which read the saved metadata and answer (its log). The query was answered at 2026-10-24T04:09:36Z (`retrieved_at` in every row). `vintage` is the answer's "updated", 2026-09-23T05:00:00Z, in every row. The header's "Retrieved: 20261024T041229Z" is the write's run id; it also states the answer's time.

Every run that is not `--offline` asks for the metadata and the whole table again. It saves both, with the query, over `warehouse/raw/statfi_electricity/query_12su.json` and writes the table again (`write_snapshot`), so Statistics Finland's revisions replace the rows held.

## Shape and variables

Series, 6,350 rows: 16 lines over 414 months. `entity` is `statfi:fi`. `variable` is the line's English name in snake case, its leading code dropped. `node` is the name as Statistics Finland writes it, code included. `x_code` is the line's code. `unit` is MWh (the table's GWh times 1,000). `ts_utc` is the month's first day, `freq` P1M, `geo` FI, `market` blank.

| `variable` | `x_code` | `node` | From |
|---|---|---|---|
| total_electricity_generation | 1 | 1 TOTAL ELECTRICITY GENERATION | 1992-01 |
| hydro_power | 1.1 | 1.1 Hydro power | 1992-01 |
| wind_power | 1.2 | 1.2 Wind power | 1992-01 |
| solar_power | 1.3 | 1.3 Solar power | 1992-01 |
| nuclear_power | 1.4 | 1.4 Nuclear power | 1992-01 |
| combined_heat_and_power_chp | 1.5 | 1.5 Combined heat and power (CHP) | 1992-01 |
| chp_district_heating | 1.5.1 | 1.5.1 CHP, district heating | 1992-01 |
| chp_industri | 1.5.2 | 1.5.2 CHP, industri | 1992-01 |
| micro_chp | 1.5.3 | 1.5.3 Micro-CHP | 2000-01 (318 months) |
| conventional_condensing_power | 1.6 | 1.6 Conventional condensing power | 1992-01 |
| net_imports_of_electricity | 2 | 2 NET IMPORTS OF ELECTRICITY | 1992-01 |
| norway | 2.1 | 2.1 Norway | 1992-01 |
| sweden | 2.2 | 2.2 Sweden | 1992-01 |
| russia | 2.3 | 2.3 Russia | 1992-01 |
| estonia | 2.4 | 2.4 Estonia | 2006-11 (236 months) |
| total_electricity_consumption | SSS | SSS TOTAL ELECTRICITY CONSUMPTION | 1992-01 |

The variable `chp_industri` keeps Statistics Finland's own spelling of the English label ("CHP, industri"). The net imports and their countries are signed as Statistics Finland gives them: a negative month is a net export (Norway 173 months, Estonia 169, Sweden 80, the total 13, Russia 1). The Russian line is zero from June 2022; its last month above zero is May 2022. Totals are Statistics Finland's lines, never sums made here.

TWh a year (the twelve months summed here for this note):

| Line (`x_code`) | 1992 | 2010 | 2025 |
|---|---|---|---|
| total_electricity_generation (1) | 54.96 | 77.23 | 78.91 |
| hydro_power (1.1) | 14.96 | 12.74 | 12.32 |
| wind_power (1.2) | 0.00 | 0.29 | 22.16 |
| solar_power (1.3) | 0.00 | 0.00 | 0.98 |
| nuclear_power (1.4) | 18.17 | 21.89 | 31.33 |
| combined_heat_and_power_chp (1.5) | 17.27 | 28.12 | 10.69 |
| conventional_condensing_power (1.6) | 4.57 | 14.18 | 1.44 |
| net_imports_of_electricity (2) | 8.23 | 10.50 | 5.56 |
| sweden (2.2) | 3.76 | -2.82 | 10.00 |
| estonia (2.4) | | 1.72 | -4.67 |
| total_electricity_consumption (SSS) | 63.19 | 87.72 | 84.47 |

January to June 2026: total generation 42.40 TWh, total consumption 46.20 TWh.

## Reading the source

- The run stops at once, asking nothing, while `statfi_electricity` or the host pxdata.stat.fi is paused.
- Two requests a run. The metadata GET is fetched fresh (timeout 60 seconds, 1 second's pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). The metadata must have exactly the three variables `timeperiod_m`, `energia_30_20200915` and `contentscode`, with `maara_gwh` among the contents, else the run stops. The POST asks for every month and line and the quantity in GWh only (timeout 180 seconds). It is tried once, and an answer other than HTTP 200 stops the run.
- `--offline` reads `query_12su.json` (the metadata, the query, the answer and its time) and stops if it is missing.
- The run stops, and no file is written, for any of these: an answer without the three dimensions; a value array not the size of the dimensions; a content other than `maara_gwh`; a month not of the form YYYYMmm; an answer with no value; a line and month given twice. A cell Statistics Finland leaves empty (null) has no row; a 0 it gives is kept (353 rows). Nothing is filled.
- The table's changes, cumulative sums and shares are not asked.

## License

Public. `license_verdicts.csv` records Statistics Finland, read 445 (session 2271, from session 2273's read of its terms of use): "may be public", for public and for commercial use. The sentence: "Statistics Finland's open data materials and public content of the web service are covered by the Creative Commons Attribution 4.0 International licence." The page asks for "Source: Statistics Finland", which the header gives. `sources.csv` flags `statfi:12su` public; `license_tables.csv` lists the table under Statistics Finland.

## Cross-checks (session 2275)

- The written table and session 2273's trial copy hold the same 6,350 keys with every value equal. Session 2273's results (`runs/c103/s2273/cross.out`, full years 2016 to 2025) therefore hold for the written rows:
  - total generation over `eurostat_electricity_monthly`'s net production TOTAL for Finland: 0.998 to 1.014;
  - net imports over Eurostat's imports less exports: 0.979 to 1.031 (1.000 to 1.001 in seven of the ten years);
  - total consumption over `owid_ember_electricity_annual`'s demand: 0.961 to 0.972.
- Computed from the rows here, in all 414 months:
  - the six sources (hydro, wind, solar, nuclear, CHP and condensing power) sum to total generation within 2,000 MWh;
  - CHP's three kinds sum to CHP within 1,000 MWh;
  - the four countries sum to net imports within 1,000 MWh;
  - total generation plus net imports equals total consumption within 1,000 MWh.
  
  The table's figures are whole GWh, so these gaps are its rounding.

## What it does not hold

- Months before January 1992 or after June 2026.
- Prices, capacity, and Finland's bidding zone or regions: the table is national.
- Statistics Finland's other electricity tables (annual production by fuel, consumption by sector).
