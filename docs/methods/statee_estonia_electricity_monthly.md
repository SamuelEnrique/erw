# Estonia's electricity production, imports and exports, a month (Statistics Estonia table KE21)

Energy Research Warehouse (ERW), method note written in session 2279 (chain 103) for a table first written on 24 October 2026 (session 2278).

Tables: `statee_estonia_electricity_monthly`

## Publisher and address

Statistics Estonia, table KE21, "Electricity production, imports, exports and sale (monthly)" (`https://andmed.stat.ee/en/stat/majandus__energeetika__energia-tarbimine-ja-tootmine__luhiajastatistika/KE21`). It is read through Statistics Estonia's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, both at `https://andmed.stat.ee/api/v1/en/stat/majandus/energeetika/energia-tarbimine-ja-tootmine/luhiajastatistika/KE21.PX`. Source id `statee:KE21`. Connector: `warehouse/connectors/statee_electricity.py` (session 2278).

andmed.stat.ee has no robots file (HTTP 404, read 480). www.stat.ee's robots file disallows Drupal's own folders, files and admin paths only (read 481). Elering's dashboard, the grid operator's own data, disallows every path for every reader (read 479) and was not asked.

## Vintage and revision

January 2005 to August 2026, written by run `20261024T050510Z` (24 October 2026), which read the saved metadata and answer. The query was answered at 2026-10-24T05:03:06Z (`retrieved_at` in every row). `vintage` is blank in every row: the answer's "updated" is 9999-12-31T21:59:59Z, a placeholder, which the connector writes as no vintage and the header says so. The database's listing gave KE21's last update as 2026-09-29T14:36:59 (session 2278's read of the listing).

Every run that is not `--offline` asks for the metadata and the whole table again. It saves both, with the query, over `warehouse/raw/statee_electricity/query_KE21.json` and writes the table again (`write_snapshot`).

## Shape and variables

Series, 1,344 rows: six indicators. `entity` is `statee:ee`. `variable` is the indicator's English name in snake case, its unit dropped. `node` is the name as Statistics Estonia writes it (its non-breaking spaces made plain). `x_code` is its code. `unit` is MWh (the table's GWh times 1,000). `ts_utc` is the month's first day, `freq` P1M, `geo` EE, `market` blank.

| `variable` | `x_code` | Months |
|---|---|---|
| total_electricity_production | PROD_E | 260, from 2005-01 |
| electricity_production_from_hydro_energy | PROD_E_HYDR | 260 |
| electricity_production_from_wind_energy | PROD_E_WIND | 260 |
| electricity_production_from_solar_energy | PROD_E_SOLAR | 44, from 2023-01 |
| imports_of_electricity | IMPORTS | 260 |
| exports_of_electricity | EXPORTS | 260 |

The table's two shares of sold electricity (`FCONS_C_P_PC`, `FCONS_HOUSEH_PC`, percent) are not taken. No value is 0 or negative. Totals are Statistics Estonia's, never sums made here.

TWh a year (the twelve months summed here for this note):

| Indicator | 2005 | 2015 | 2025 |
|---|---|---|---|
| total_electricity_production | 10.18 | 10.33 | 5.94 |
| electricity_production_from_hydro_energy | 0.02 | 0.03 | 0.04 |
| electricity_production_from_wind_energy | 0.06 | 0.72 | 1.32 |
| electricity_production_from_solar_energy | | | 1.13 |
| imports_of_electricity | 0.35 | 5.45 | 5.79 |
| exports_of_electricity | 1.89 | 6.38 | 2.77 |

In 2025 hydro, wind and solar were 41.9 percent of total production. January to August 2026: total production 3.93 TWh, imports 5.00, exports 2.79.

## Reading the source

- The run stops at once, asking nothing, while `statee_electricity` or the host andmed.stat.ee is paused.
- Two requests a run. The metadata GET is fetched fresh (timeout 60 seconds, 1 second's pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`).
  - The metadata must have exactly the two variables `Näitaja` and `Vaatlusperiood`, and at least one indicator whose name ends in ", GWh"; else the run stops.
  - The POST asks for every month and the indicators in GWh (timeout 180 seconds). It is tried once, and an answer other than HTTP 200 stops the run.
- `--offline` reads `query_KE21.json` and stops if it is missing.
- The run stops, and no file is written, for any of these:
  - an answer without the two dimensions;
  - a value array not the size of the dimensions;
  - an indicator not in GWh;
  - a month not of the form YYYYMmm;
  - an answer with no value;
  - an indicator and month given twice.
- A cell left empty (null) has no row (the solar indicator before 2023). Nothing is filled.

## License

Public. `license_verdicts.csv` records Statistics Estonia, read 482 (session 2278): "may be public", for public and for commercial use. The sentence, in its principles for disseminating official statistics: "Statistics Estonia's open data can be shared under Creative Common (CC) licence BY-SA 4.0." It is the record's first share-alike license: a copy or adaptation carries CC BY-SA 4.0, and the header says so. Whether version 1 on Redivis may carry it is for Samuel (chain 103's note). `sources.csv` flags `statee:KE21` public.

## Cross-checks (session 2278, full years 2016 to 2025)

- Against `eurostat_electricity_monthly` (Estonia):
  - imports and exports are 1.000 of Eurostat's in every year but 2017 (imports 1.051, exports 1.004) and 2024 (imports 0.997);
  - wind is 0.981 to 1.017 of Eurostat's;
  - total production is 1.115 to 1.176 times Eurostat's net production. The table does not say whether its production is gross or net.
- Production plus imports less exports over `owid_ember_electricity_annual`'s demand: 0.954 to 1.010.

## What it does not hold

- Months before January 2005; production from fuels by type (oil shale, gas, biomass), which KE21 does not split.
- The shares of sold electricity; prices; capacity.
