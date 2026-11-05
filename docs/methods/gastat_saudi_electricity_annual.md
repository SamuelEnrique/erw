# Saudi Arabia's electricity a year (GASTAT's Electrical Energy Statistics 2024, the Ministry of Energy's figures)

Energy Research Warehouse (ERW), method note written in session 2555 (chain 125) for a table first written on 24 October 2026 (session 2552).

Tables: `gastat_saudi_electricity_annual`

## Publisher and address

The General Authority for Statistics (GASTAT), Saudi Arabia, its workbook "Electrical Energy Statistics 2024" (Arabic edition), each of whose tables names the Ministry of Energy as its source: `https://www.stats.gov.sa/documents/20117/2435281/Electrical_Energy_Statistics_2024_AR.xlsx_fixed_9794353/b763f431-ab03-cf1d-4a14-eec2fe2f6ef4`, listed on GASTAT's "Electrical energy statistics" tab. One GET, no key. Source id `gastat:electrical_energy_statistics_2024`, publisher "Ministry of Energy, Saudi Arabia, as published by GASTAT". Connector: `warehouse/connectors/gastat_saudi_electricity.py` (session 2552). www.stats.gov.sa's robots file closes `/api/`, `/c/portal/` and `/o/` (read 1034).

## Vintage and revision

2010 to 2024, written by run `20261024T231634Z` (the write under the lock, offline), which read the workbook saved at 2026-10-24T23:12:59Z. `vintage` is its last-modified time, 2025-12-07T06:06:04Z. Each year's edition has its own address.

## Shape and variables

Series, 177 rows, 28 entities. `entity` `gastat:sa:<item>`; `ts_utc` the year's first day; `freq` P1Y; `geo` SA; `node` GASTAT's Arabic label; `x_approx` true on the 11 rows GASTAT marks with an approximation sign.

| Sheet | `variable` | Items | Unit | Years | 2024 |
|---|---|---|---|---|---|
| 1 | `licensed_capacity` | total | MW (GW times 1,000) | 2019 to 2024 | 92,500 (approximate) |
| 2 | `licensed_capacity` | steam, gas, combined_cycle, diesel, renewable | MW | 2019 to 2024 | renewable 6,550 |
| 3 | `peak_load` | total | MW | 2019 to 2024 | 74,800 (approximate) |
| 4 | `peak_load` | central, eastern, western, southern (the Saudi Electricity Company's business areas) | MW | 2020 to 2024 | central 24,700 |
| 5 | `energy_sent_out` | total | MWh (GWh times 1,000) | 2010 to 2024 | 402.628 TWh |
| 6 | `energy_consumed` | total (sales: no internal loads, no energy passed through the grid) | MWh | 2010 to 2024 | 340.430 TWh |
| 8 | `consumption` | residential, commercial, government, industrial, other (the transmission company's interconnected system) | MWh | 2021 to 2024 | residential 161.207 TWh |
| 7 | `sales_<category>` | the 13 administrative regions | MWh | 2024 | Riyadh residential 45.213 TWh |

Sheet 2's types sum to 94.95 GW in 2024 against sheet 1's approximate 92.5 GW: the two sheets are taken as published, not made to agree.

## Reading the source

- The run stops at once, asking nothing, while `gastat_sa` or www.stats.gov.sa is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved workbook (its address carries no file extension, so it is opened from memory).
- **Sheets** by name ("1 " with its trailing space, "2" to "8"), each checked by words of its title in Arabic; **columns** by words of their headers; **rows** by their year (a number or text), or in sheet 7 by the region's name; sheet 7's year from its title.
- **Figures:** numbers, or text with commas and an approximation sign; the sign is kept in `x_approx`.
- **Sums:** each year's consumption by category (sheet 8) within 1 GWh of the energy consumed (sheet 6): 340,430 GWh both in 2024.
- The run stops, and no file is written, for: a sheet or a column not found, a sheet with no year, a figure that is not a number, a key given twice, a region not in the map or missing, sheet 7 with no year in its title, a sum missed.

Nothing is filled. The loss rate (sheet 10), the counts of consumers (9) and the later sheets are not taken.

## License

Internal, not settled. GASTAT's use policy (read 1037), 1.2.2, allows reuse "for any purpose, including commercial use", GASTAT acknowledged and changes indicated, "Except for trademarks, logos, and any clearly identified third-party material"; each table names the Ministry of Energy as its source. GASTAT's own verdict (session 2552) is may be public; whether it covers the Ministry's figures is with the owner. Held from the live set and from Redivis.

## Cross-checks (session 2552)

- The regions' sales in 2024 sum to 340.376 TWh against the energy consumed, 340.430 TWh.
- `eia_world_electricity_annual`, Saudi Arabia, 2024: EIA's generation 445.757 TWh against GASTAT's energy sent out 402.628 TWh (90%); EIA's consumption 405.978 TWh against GASTAT's sales-based 340.430.

## What it does not hold

- Generation by fuel or plant (only capacity by type); months; trade (the GCC interconnection); prices (SAR).
