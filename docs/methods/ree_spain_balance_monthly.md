# Spain's electrical energy balance a month: generation by technology, storage, cross-border exchanges and demand at busbars, January 2020 to September 2026 (Red Electrica's REData)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2239 of chain 101, its report `archive/sessions/SESSION_2239_REPORT.md`).

Tables: `ree_spain_balance_monthly`

## Publisher and address

Red Electrica (REE), Spain's transmission system operator, REData API, the widget "balance/balance-electrico", page `https://www.ree.es/en/datos/balance`. One answer a year (no key):

- `https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=<year>-01-01T00:00&end_date=<year>-12-31T23:59&time_trunc=month`, 2020 to 2026.

The answer is JSON: a title "Electrical energy balance" with the description "Electrical energy balance: Allocation of production units according to primary fuel.", and four groups (Renewable, Non-renewable, Almacenamiento, Demand), each with its series of monthly values (`value`, `percentage`, `datetime`). The answers name no geography. Source id `ree:redata_balance_electrico`.

Session 2239's probe (`runs/c101/s2239/probe.csv`) made 14 requests. `apidatos.ree.es` has no robots file (read 366, HTTP 404); `www.ree.es`'s disallows search, feeds and press events only (read 367). Two requests for the generation structure over five and eleven years answered HTTP 400; REData answers at most a year a request. The seven balance answers (HTTP 200, 32,476 to 37,611 bytes) are saved in `runs/license_reads/s2239/` (08 to 14) and seeded into `warehouse/raw/ree_balance/20261024T031644Z_probe/`; the trial and the write read them offline.

Connector: `warehouse/connectors/ree_balance.py` (session 2239): `[--first 2020] [--last 2026] [--offline] [--out-dir DIR]`, one request a year. Every series is taken, its English name in snake case; `x_group` is REE's group and `x_series_id` its series id. An answer that is not the balance, a series without values, a month not in REE's form, a value that is not a number or a month given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T032244Z`, written offline from the seven answers retrieved from 2026-10-24T03:18:21Z (2025) to 03:21:03Z (2026) (`retrieved_at` is each answer's): "This run wrote 1890 rows: 1890 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `vintage` is blank in every row. Header line 4 gives each answer's "last-update" from its top level, 2021-01-12T10:19:24+01:00 (2020) to 2026-09-08T18:31:47+02:00 (2026); the groups and series carry later dates (disagreement 1).

The answers carry no provisional flag; by the groups' dates, REE last updated a year's values ten to thirteen months after it ended (2020's on 2021-11-10, 2021's on 2022-11-10, 2022's on 2023-11-28, 2023's on 2025-01-29, 2024's on 2026-01-13), and 2025's on 2026-06-04. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but a value REE later stops giving writes no row, so the earlier value would be kept.

## Shape and variables

Series, 1,890 rows, one entity `ree:ES`, `node` Spain, `geo` ES, `unit` MWh, `freq` P1M, `market` blank; 25 variables, each with one `x_series_id`. Rows a year: 269 (2020), 267, 266, 289, 292, 289 and 218 (January to September 2026).

| Group | Variable | Rows | First month | Mean | Lowest | Highest |
|---|---|---|---|---|---|---|
| Renewable | hydro | 81 | 2020-01 | 2,431,106.1 | 719,585.0 | 4,737,199.9 |
| Renewable | wind | 81 | 2020-01 | 4,950,322.1 | 3,083,405.5 | 8,295,225.2 |
| Renewable | solar_photovoltaic | 81 | 2020-01 | 3,030,934.3 | 625,344.4 | 7,730,045.3 |
| Renewable | thermal_solar | 81 | 2020-01 | 364,447.2 | 35,185.7 | 828,492.5 |
| Renewable | hydroeolian | 81 | 2020-01 | 1,814.5 | 324.1 | 3,975.8 |
| Renewable | other_renewables | 81 | 2020-01 | 344,322.8 | 221,266.5 | 436,423.9 |
| Renewable | renewable_waste | 81 | 2020-01 | 65,805.4 | 35,046.9 | 83,521.4 |
| Renewable | renewable_generation (subtotal) | 81 | 2020-01 | 11,188,752.3 | 7,472,118.4 | 14,706,099.7 |
| Non-renewable | nuclear | 81 | 2020-01 | 4,500,763.7 | 2,951,810.7 | 5,289,146.0 |
| Non-renewable | combined_cycle | 81 | 2020-01 | 3,958,162.0 | 1,544,065.8 | 8,460,442.2 |
| Non-renewable | cogeneration | 81 | 2020-01 | 1,592,550.8 | 604,123.5 | 2,440,531.5 |
| Non-renewable | coal | 81 | 2020-01 | 327,970.7 | 0 | 882,232.5 |
| Non-renewable | diesel_engines | 81 | 2020-01 | 210,789.2 | 160,418.1 | 280,041.2 |
| Non-renewable | steam_turbine | 81 | 2020-01 | 141,385.1 | 33,486.9 | 373,836.9 |
| Non-renewable | non_renewable_waste | 81 | 2020-01 | 130,531.7 | 52,279.9 | 212,202.0 |
| Non-renewable | gas_turbine | 81 | 2020-01 | 52,635.6 | 15,716.7 | 111,178.3 |
| Non-renewable | fuel_gas | 18 | 2020-03 | 0.000 | -0.001 | 0.001 |
| Non-renewable | non_renewable_generation (subtotal) | 81 | 2020-01 | 10,914,788.7 | 7,125,862.9 | 16,049,184.2 |
| Almacenamiento | pumping_turbine | 81 | 2020-01 | 381,514.4 | 105,706.3 | 714,934.5 |
| Almacenamiento | pumping_consumption | 81 | 2020-01 | -606,911.6 | -1,096,732.5 | -149,058.5 |
| Almacenamiento | battery_delivery | 45 | 2023-01 | 731.4 | 11.6 | 1,507.7 |
| Almacenamiento | battery_charging | 45 | 2023-01 | -912.2 | -1,822.9 | -26.3 |
| Almacenamiento | storage_balance (subtotal) | 81 | 2020-01 | -225,497.6 | -484,497.8 | -26,775.8 |
| Demand | cross_border_exchange_balance | 81 | 2020-01 | -800,744.0 | -2,876,662.7 | 1,482,378.8 |
| Demand | demand_at_busbars | 81 | 2020-01 | 21,077,299.4 | 17,060,912.0 | 25,259,616.6 |

MWh a month, rounded to one decimal. Every series ends in 2026-09.

- **Signs.** Pumping consumption, battery charging and the storage balance are negative in every month; the cross-border balance is negative (a net export) in 65 of 81 months, the first in July 2020. Generation plus storage plus exchanges equals demand at busbars (below).
- **Sparse and small series.** fuel_gas ("Fuel + Gas") has 18 months of 0, 0.001 or -0.001 MWh, and none in the other 61 months of its span. The batteries begin in 2023 (the 2020 to 2022 answers have 23 series, the others 25) and are a few thousand MWh a month at most. Coal is 0 in February and April 2026.
- Values keep REE's digits, with floating-point tails (demand at busbars 22,938,402.64800001 MWh in January 2025).

| Year | Demand at busbars | Wind | Solar PV | Nuclear | Combined cycle | Hydro | Cross-border balance |
|---|---|---|---|---|---|---|---|
| 2020 | 250.051 | 54.906 | 15.302 | 55.758 | 44.023 | 30.632 | 3.280 |
| 2021 | 256.546 | 60.526 | 20.981 | 54.041 | 44.500 | 29.626 | 0.852 |
| 2022 | 250.471 | 61.195 | 27.906 | 55.934 | 68.137 | 17.911 | -19.802 |
| 2023 | 246.665 | 62.672 | 37.454 | 54.647 | 46.682 | 25.765 | -13.957 |
| 2024 | 249.000 | 60.912 | 44.599 | 52.391 | 35.755 | 34.950 | -10.227 |
| 2025 | 256.257 | 58.756 | 50.273 | 51.847 | 45.734 | 33.700 | -12.795 |
| 2026, January to September | 198.272 | 42.009 | 48.991 | 39.943 | 35.780 | 24.337 | -12.212 |

TWh, the months summed.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (Decision 11), a label for the month, not an instant. Every one of REE's `datetime` values in the seven answers is a month's first midnight in Spain's time ("2026-09-01T00:00:00.000+02:00", 0 exceptions), and the connector takes its year and month. A month not ended in Europe/Madrid time when the answer was fetched is left out: the 2026 answer, fetched at 03:21:03Z on 24 October (05:21 in Madrid), held October 2026 for 24 of its 25 series (all but Fuel + Gas), and those 24 values have no row, as header line 3 states. A value REE does not give has no row; nothing is filled.

## License

Header: "License: public. REE's legal notice: users may publish the content on their website or in company or academic work, for information only and not for commercial purposes, naming REE as the source, not altering the meaning of the data, and giving the date of their latest update. Cite: Red Electrica, REData." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 369 (session 2239, REE's legal notice, `https://www.ree.es/en/legal-notice-privacy-policy`), "Notwithstanding the above, users may view and obtain a personal temporary copy of the content for their exclusive private use in their computer systems (software and hardware), publish them on their website or create company or academic content, as long as it is for information only, and not for commercial purposes.", verdict "may be public", if the ERW sells anything "needs written permission"; the table's row: flag public, "agrees", ERW verdict public. As for the ERW's other non-commercial verdicts, the table stays public while the ERW sells nothing (the report).

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/ree_spain_balance_monthly.csv`, read past its 10 header lines (counted), and from the saved answers, read only (scripts `runs/c101/s2247/ree.py` and `ree2.py`, outputs beside them).

- 1,890 rows, `ts_utc` from 2020-01-01T00:00:00Z to 2026-09-01T00:00:00Z, as header line 10 states; 25 series, as header line 3 states; no (entity, variable, ts_utc) twice; no blank value; unit MWh throughout; every `ts_utc` a month's first day.
- **Against the answers:** the 1,890 values of ended months in the seven saved answers and the table's 1,890 rows have the same keys, and the same values to within 4e-9 MWh (the CSV's floating-point rounding); the 24 October 2026 values are the only ones left out.
- The trial's table (`runs/c101/s2239/trial/ree_spain_balance_monthly.csv`) has the same rows past its header, byte for byte.
- Session 2239's cross-check (`runs/c101/s2239/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. A year's demand at busbars against Ember's Spanish demand (`owid_ember_electricity_annual`): 0.9517 (2020), 0.9446, 0.9369, 0.9303, 0.9198 and 0.9315 (2025: 256.257 against 275.1 TWh). Subtotals against their parts: 0.0 MWh for all three. Generation plus storage plus exchanges less demand: at most 0.7 MWh in 81 months. Wind and solar photovoltaic: 28.1 percent of demand in 2020, 42.5 in 2025, 45.9 in 2026 so far.
- With more digits (`ree2.py`): the subtotals equal the sum of their parts to within 3e-8 MWh in every month, and the balance closes to at most 0.742 MWh (median below 1e-7).

## Where the description and the data disagree

1. **"The date of their latest update."** REE's notice asks for it, and header line 4 gives, for each answer, the top-level "last-update". In six of the seven answers the groups carry dates weeks or months later: in the 2026 answer the top level says 2026-09-08T18:31:47+02:00, while the Non-renewable, Almacenamiento and Demand groups say 2026-10-23T07:50:18 to 07:50:21+02:00 and the latest series 07:50:22; in the 2024 answer, 2025-01-28T16:56:22 against 2026-01-13T19:24:57 (2020 2021-01-12 against 2021-11-10, 2021 2022-01-11 against 2022-11-10, 2022 2022-12-12 against 2023-11-28, 2025 2026-05-11 against 2026-06-04). Only in 2023's answer are they within a day (2025-01-28T15:08:07 against 2025-01-29T08:59:00). The header's dates understate how recent the values are.
2. **REE's own description of demand.** In every answer the Demand group's description reads "Corrected demand: After factoring in the influence of seasonal and working patterns", while its series is "Demand at busbars". The series is not corrected for season and working days: it equals generation plus storage plus exchanges to within 0.742 MWh in all 81 months, which a corrected figure would not. The table's name, demand_at_busbars, fits the numbers; REE's group text does not.
3. **The geography is not in the answers.** The docstring says `ree:ES` is "REE's default geography, the national system". The saved answers name no geography; the request names none. The cross-check's steady 0.92 to 0.95 of Ember's Spanish demand fits a national figure but does not show whether the islands are in it.

Not acted on: this note changes no file but itself.

Acted on in session 2247. The header now gives the latest update date found anywhere in REE's answers (its groups' and series' dates as well as the answer's own), as REE's notice asks; the docstring says the answers name no geography. The table was written again offline (the same 1,890 rows). REE's own word for its Demand group is recorded, not changed: the series balances generation, storage and exchanges, as the note shows.

## The session report against the table

Every figure of `SESSION_2239_REPORT.md` checked against the table, the saved answers and the rerun cross-check holds (January 2020 to September 2026, 1,890 rows, every series of the balance with REE's three subtotals, October 2026's 24 values left out, HTTP 400 for five- and eleven-year ranges, seven requests for seven years, subtotals equal to their parts, the balance within 0.7 MWh in 81 months, 0.920 to 0.952 of Ember's demand, 256.257 against 275.1 TWh, wind and solar photovoltaic 28.1 to 42.5 percent and 45.9 in 2026, 14 requests of 15), except:

- "REE's 'last-update' is in the header": the top-level date is; the groups' later dates are not (disagreement 1).

## What it does not hold

- Days, hours, regions and the peninsular, Balearic and Canary systems apart; years before 2020; REE's `percentage` field; the generation structure (fetched for 2025 and not used); October 2026 on.
