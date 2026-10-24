# Denmark's production by technology, gross consumption and exchanges an hour, by price area, from 2025 (Energinet's settlement data)

Energy Research Warehouse (ERW), method note written in session 2218 (chain 098) for a table first written on 24 October 2026 (session 2217 of chain 098, `archive/sessions/SESSION_2217_REPORT.md`).

Tables: `energinet_dk_production_hourly`

## Publisher and address

Energinet, Denmark's transmission system operator, Energi Data Service, dataset ProductionConsumptionSettlement ("Production and consumption based on settlement data from Datahub", its metadata), page `https://www.energidataservice.dk/tso-electricity/ProductionConsumptionSettlement`. The open API (no key) answers one request with every record of the window: `https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?start=2025-01-01T00:00&end=2026-10-15T00:00&limit=0&sort=HourUTC%20ASC`, one JSON answer of 27,131,312 bytes, 31,250 records, one an hour and price area (DK1 west of the Great Belt, DK2 east). Source id `energinet:production_consumption_settlement`. The answer is saved under `warehouse/raw/energinet_production/20261024T015111Z_probe/` (session 2217's probe copy, seeded into the raw store; the trial and the write read it offline). Neither host has a robots file (reads 352 and 354); the dataset's metadata is read 353 (session 2215), saved as `runs/license_reads/s2215/02_*.bin`.

Connector: `warehouse/connectors/energinet_production.py` (session 2217): `[--start 2025-01-01] [--end 2026-10-15] [--offline] [--out-dir DIR]`, one request, reused with `--offline`. Twenty-one of the record's measures are taken, renamed in snake case; the three grid losses and power-to-heat are not. A record without the fields named, a value that is not a number, or an hour and area given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T015528Z`, written offline from the answer retrieved at 2026-10-24T01:51:11Z (`retrieved_at` on every row). `vintage` is 2026-10-24T01:51:12Z on every row: the answer's Last-Modified, the moment it was served, not the moment Energinet settled the hours.

Energinet's metadata: "Data is updated with a 9-15 day delay. Measurement data may be updated up to 2 years after the specific date, however data is normally 99% correct after 15 days ... After 3 months, data will normally be 99,9% correct." The hours after 9 October 2026 were under 15 days old when retrieved. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but an hour Energinet later sets to null writes no row, so the earlier value would be kept.

## Shape and variables

Series, 607,311 rows, two entities, `energinet:DK1` (327,093 rows) and `energinet:DK2` (280,218), `node` the price area, `unit` MWh for the hour, `freq` PT1H, `geo` DK, `market` blank, `x_hour_dk` Energinet's HourDK. Each area holds all 15,625 hours from 2024-12-31T23:00:00Z to 2026-10-13T23:00:00Z. Of the 656,250 cells (31,250 records times 21 measures), 48,939 are null and have no row: DK2's exchange_no, exchange_nl and exchange_gb in every hour (46,875: Energinet's records give null for DK2 in these three), and local_power_self_con from 2026-09-01T00:00:00Z (2,064).

| Variable | DK1 mean | DK1 lowest | DK1 highest | DK2 mean | DK2 lowest | DK2 highest |
|---|---|---|---|---|---|---|
| central_power | 329.618 | 0 | 1,469.739 | 252.528 | 0 | 845.034 |
| local_power | 169.274 | 29.257 | 684.424 | 46.290 | 1.596 | 218.275 |
| local_power_self_con | 97.839 | 13.736 | 354.432 | 23.367 | 0.213 | 100.342 |
| commercial_power | 55.276 | 20.198 | 110.534 | 132.716 | 7.476 | 281.804 |
| offshore_wind_lt100mw | 53.195 | 0 | 235.696 | 9.952 | 0 | 43.265 |
| offshore_wind_ge100mw | 709.406 | 0 | 2,025.422 | 362.964 | 0 | 958.716 |
| onshore_wind_lt50kw | 4.167 | 0 | 15.280 | 0.417 | 0 | 9.217 |
| onshore_wind_ge50kw | 959.279 | 0.052 | 3,401.134 | 171.729 | 0.005 | 632.065 |
| hydro_power | 1.432 | 0.275 | 4.361 | 0.000 | 0 | 0.000 |
| solar_power_lt10kw | 44.741 | 0 | 391.055 | 19.794 | 0.001 | 167.323 |
| solar_power_ge10lt40kw | 7.026 | 0 | 62.854 | 4.126 | 0 | 39.722 |
| solar_power_ge40kw | 364.512 | 0.009 | 3,091.377 | 118.921 | 0 | 825.260 |
| solar_power_self_con | 30.394 | 0 | 428.898 | 29.506 | 0 | 303.516 |
| unknown_prod | 3.570 | 0 | 77.328 | 10.326 | 0.098 | 116.180 |
| gross_consumption | 2,977.564 | 1,645.068 | 4,870.058 | 1,761.832 | 987.390 | 2,949.687 |
| exchange_no | 504.405 | -1,669.512 | 1,623.624 | no row | | |
| exchange_se | 323.473 | -733.589 | 748.812 | 729.711 | -1,285.364 | 1,402.052 |
| exchange_ge | -395.991 | -3,472.490 | 3,708.370 | -159.878 | -999.712 | 987.525 |
| exchange_nl | 58.435 | -704.245 | 687.678 | no row | | |
| exchange_gb | -321.221 | -1,454.788 | 1,405.719 | no row | | |
| exchange_great_belt | -14.806 | -607.900 | 600.500 | 10.908 | -611.000 | 597.100 |

Means and extremes rounded to 3 decimals. An exchange is negative for an export, positive for an import (Energinet's sign). DK2's hydro_power is zero in 15,621 hours and below 0.0005 MWh in the other four. The most frequent zeros elsewhere: solar_power_self_con (1,955 hours in DK1, 6,331 in DK2) and central_power (640 and 864).

In 2025 (Danish hours, 8,760 in each area): gross consumption 40.513 TWh (DK1 25.440, DK2 15.073), wind 19.090 TWh (47.1 percent of it), the four solar measures 4.514 TWh (11.1 percent); local_power_self_con 0.966 TWh and solar_power_self_con 0.404 TWh, so the consumption through the grid that Energinet's metadata defines (gross consumption less both self-consumption measures) is 39.143 TWh.

## Placing values in time, and what is filled

`ts_utc` is HourUTC, the hour's start; `x_hour_dk` is the same hour in Danish time. The first record is 2025-01-01T00:00 Danish time, the last 2026-10-14T01:00, so 14 October 2026 holds only its first two Danish hours. Values are MWh for the hour, as published. local_power_self_con has rows to 2026-08-31T23:00:00Z (01:00 on 1 September, Danish time) and is null from 2026-09-01T00:00:00Z, 1,032 hours in each area. A null has no row; nothing is filled.

## License

Header: "License: public, CC BY 4.0. Source: Energinet (www.energidataservice.dk). The records are reshaped from wide to long; no value is changed." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 356 (session 2215, Energi Data Service's Terms and Conditions), "Data published on Energi Data Service is subject to the conditions of Creative Commons CC-BY 4.0. Users may copy, change and distribute data freely, even for commercial purposes", verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2218)

The figures in this note were computed from the rows of `warehouse/output/energinet_dk_production_hourly.csv`, read past its 10 header lines, and from the saved metadata (read 353), read only (scripts `runs/c098/s2218/energinet.py`, `energinet2.py` and `energinet3.py`, outputs beside them).

- 607,311 rows, `ts_utc` from 2024-12-31T23:00:00Z to 2026-10-13T23:00:00Z, as the header states; 15,625 hours for each area, as the header states, and every hour of the span; no (entity, variable, ts_utc) twice; 21 variables, unit MWh throughout.
- The trial (`runs/c098/s2217/trial.out`) wrote 578,125 rows without local_power_self_con; the table holds 29,186 rows of it, and 578,125 plus 29,186 is 607,311.
- Session 2217's cross-check (`runs/c098/s2217/cross.py`), run again from the main checkout: its output is identical to the saved `cross.out`. The script reads the trial's table, `runs/c098/s2217/trial/energinet_dk_production_hourly.csv`, which lacks local_power_self_con, so its balance lines describe the hour without that measure: production plus net imports minus gross consumption, DK1 median -2.361 percent (lowest -10.321), DK2 median -0.878 percent (lowest -5.095). Its other lines do not depend on that measure, and the written table gives the same: the Great Belt flows of DK1 and DK2 cancel to a median 3.2 MWh (largest 11.0) over 15,625 hours; 2025 gross consumption 40.513 TWh against Ember's 40.670 TWh Danish demand (`owid_ember_electricity_annual`), ratio 0.9961; wind 19.090 TWh, 47.1 percent.
- The balance on the written table (`energinet.py`): the fourteen production measures, local_power_self_con among them, plus the six exchanges, minus gross consumption, is 0.0000 MWh to four decimals in all 31,250 records: in the 29,186 with local_power_self_con and in the 2,064 without it, from 2026-09-01T00:00:00Z. Where it is published, local_power_self_con is a median 2.452 percent of gross consumption in DK1 and 0.936 percent in DK2. Energinet's metadata defines gross consumption as this sum ("Calculated as sum of all production including self-consumption plus sum of exchange"), so the balance confirms that the table keeps Energinet's columns whole; it is not an independent measurement.

## Where the description and the data disagree

1. **What local_power_self_con is.** The header, the docstring and the report call it local self-consumption. Energinet's metadata names the column LocalPowerSelfConMWh "Commercial power self-consumption (terminated)": "Production from commercial power plants, that is not delivered to the grid. Named before commercial power was separated from Local power, therefor the confusing DB name. NOTE: Has gradually become less reliable, and is terminated from 1/9 2026", and "Very uncertain". Of gross consumption it says that this measure "is very uncertain, and overlaps Solar Power Self Consumption, and therefor to be excluded i the total consumption" (its emphasis marks dropped); neither the header nor the docstring says so, and a sum of the fourteen production measures counts that overlap.
2. **Grid losses inside gross consumption.** The header says "Grid losses and power-to-heat (inside gross consumption) are not taken", the docstring "the three grid losses and power-to-heat (inside gross consumption)". Energinet's metadata says of GridLossInterconnectorsMWh: "Not included in the Gross consumption." Two of the three losses, and power-to-heat, are inside it.
3. **A break in local_power at 1 September 2026, not said.** The header says only that self-consumption ends. From 2026-09-01T00:00:00Z the balance closes without it, and local_power's mean (Danish months) rises from 80.83 MWh in August 2026 to 122.84 in September in DK1, and from 20.30 to 29.85 in DK2, while the same months of 2025 went from 99.82 to 100.25 and from 35.90 to 37.87. Energinet's metadata carries a caution: "The dataset has changed as part of the transition to DataHub 3.0 ... the values will be calculated using a different method. Values in the 'Commercial power self-consumption' column will be unavailable for an extended period of time. Implemented on October 7." The table cannot say which hours the new method covers, nor whether the self-consumed production now sits in local_power; a reader comparing local_power across 1 September 2026 should not treat the two sides as one series.

Acted on in session 2218, from the saved metadata with no request: the variable is renamed `commercial_power_self_con`, after Energinet's display name, and the docstring and header quote Energinet's warnings (very uncertain, overlapping solar self-consumption, to be left out of total consumption) (disagreement 1); they now say that gross consumption is Energinet's sum of production and exchange, the interconnectors' losses outside it (disagreement 2); and they name the break at 1 September 2026 with Energinet's caution on the DataHub 3.0 method (disagreement 3). The table was written again offline from the saved answer, its file removed first under the data lock so that the old variable's rows did not stay: the same 607,311 rows. Where this note says local_power_self_con below, the table now says commercial_power_self_con.

## The session report against the table

Every figure of `SESSION_2217_REPORT.md` checked against the table, the saved answer's manifest and the rerun cross-check holds (607,311 rows, 2024-12-31T23:00Z to 2026-10-13T23:00Z, 15,625 hours each, twenty-one measures with thirteen production columns beside local self-consumption, 2,064 null records from 1 September 2026, the balance within rounding in all 31,250 records with the measure counted, DK1 short by a median 2.4 percent and up to 10.3 percent and DK2 by 0.9 percent without it, the Great Belt's 3.2 MWh, 8,760 hours each in 2025, 40.513 against 40.670 TWh and 0.9961, wind 19.090 TWh and 47.1 percent, 27 MB and 31,250 records, 1 request), except:

- "production plus net imports equals gross consumption ... but only with local self-consumption counted ... This is why the measure is taken": the balance holds by Energinet's definition of gross consumption, and in the 2,064 records from 1 September 2026 it closes without the measure. Energinet's metadata, read in session 2215, calls the measure commercial power self-consumption, very uncertain, overlapping solar self-consumption, and to be left out of total consumption (disagreement 1).
- "The three grid losses and power-to-heat are not taken: both sit inside gross consumption": the interconnector losses do not (disagreement 2).
- "1 January 2025 to 14 October 2026 in Danish time" holds, but 14 October holds only 00:00 and 01:00 Danish time; a reader counting Danish days drops it.

## What it does not hold

- The three grid losses, power-to-heat, hours before 2025 (Energinet's data runs from 2005, "not in all rows"), prices, and Energi Data Service's other datasets.
