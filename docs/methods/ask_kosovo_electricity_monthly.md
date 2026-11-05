# Kosovo's electricity a month (ASKdata, "Electricity production and consumption")

Energy Research Warehouse (ERW), method note written in session 2527 (chain 123) for a table first written on 24 October 2026 (session 2524).

Tables: `ask_kosovo_electricity_monthly`

## Publisher and address

The Kosovo Agency of Statistics (ASK), its ASKdata table "Electricity production and consumption" (tab01, Energy, Monthly indicators), read through the PxWeb API by one JSON-stat 2.0 query by POST, every value of both dimensions selected: `https://askdata.rks-gov.net/api/v1/en/ASKdata/Energy/Monthly%20indicators/tab01.px`. No key. Source id `ask:energy_tab01`. Connector: `warehouse/connectors/ask_kosovo_electricity.py` (session 2524). askdata.rks-gov.net and ask.rks-gov.net answer HTTP 404 for a robots file (reads 956, 962).

## Vintage and revision

January 2022 to July 2026, written by run `20261024T192332Z` (the write under the lock, offline), which read the answer saved at 2026-10-24T19:18:15Z. `vintage` is the answer's `updated` field, 2022-04-28T22:00:00Z, older than its newest month. Each run takes the whole table again.

## Shape and variables

Series, 715 rows, 11 entities. `ts_utc` the month's first day, 00:00 UTC; `freq` P1M; `geo` XK; `node` ASK's item label; `x_period` ASK's month label.

| ASK's item | `entity` | `variable` |
|---|---|---|
| Gross Production from Power Plants | `ask:xk:thermal` | `gross_production` |
| Gross Production from Hydropower Plants | `ask:xk:hydro` | `gross_production` |
| Gross Production from Wind and Solar | `ask:xk:wind_solar` | `gross_production` |
| Import, Export | `ask:xk:total` | `imports`, `exports` |
| Gross Electricity Available | `ask:xk:total` | `gross_available` |
| Households, Commercial, Industry, Public lighting & others, Consumers 220-110kv, Mining | `ask:xk:<sector>` | `consumption` |
| Electricity consumption | `ask:xk:total_consumption` | `consumption` |

**The unit.** ASK's dimension is named "MWH", but its figures carry three decimals (px decimals 3), and a year's gross electricity available sums to about 7.3 thousand. Read as thousands of MWh, they match `eia_world_electricity_annual`'s Kosovo for 2024: imports 3,159,876 and exports 2,622,204 MWh, equal to ASK's to the MWh, and generation 7.02 TWh against ASK's gross production 6.75 TWh. The connector multiplies each figure by 1,000; `unit` is MWh.

| TWh | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| Gross production | 6.98 | 6.33 | 6.75 | 5.86 |
| Imports | 3.4 | 3.4 | 3.2 | 4.2 |
| Consumption, total | 5.0 | 5.3 | 5.4 | 5.7 |

## Reading the source

- The run stops at once, asking nothing, while `ask_kosovo_energy` or askdata.rks-gov.net is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved answer (`warehouse/raw/ask_kosovo_energy/query_tab01.json`).
- **Months:** ASK labels most "YYYYMnn" and some "YYYYnn" (`202308`); both are read, and a month outside 1 to 12 stops the run.
- **Cells without a row:** a cell without a number.
- The run stops, and no file is written, for: dimensions other than "MWH" and "Viti/muaji", an item not in the map, a bad month, a value array not the size of the dimensions, a key given twice.

Nothing is filled.

## License

Internal, not settled. No terms of reuse were found within session 2524's ceiling. Kosovo's administrative instruction 02/2023 sets the sale of statistical data, and Eurostat's GEOSTAT usage conditions keep Kosovo's data its statistics office's, commercial use by approval. Held from the Redivis storage and the live set.

## Cross-checks (session 2524)

- `eia_world_electricity_annual`, Kosovo, 2024: imports and exports equal ASK's to the MWh (EIA's figures are evidently ASK's); ASK's gross production 0.96 of EIA's generation.

## What it does not hold

- Hourly or daily figures; capacity; prices (EUR); the quarterly and yearly energy tables of ASKdata.
