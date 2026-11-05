# Bulgaria's electricity a month (NSI's "Production and deliveries of electricity")

Energy Research Warehouse (ERW), method note written in session 2541 (chain 124) for a table first written on 24 October 2026 (session 2539).

Tables: `nsi_bulgaria_electricity_monthly`

## Publisher and address

The National Statistical Institute, Bulgaria (NSI), its time-series workbook "Production and deliveries of electricity": `https://www.nsi.bg/sites/default/files/files/data/timeseries/Energy-1.4.Electricity_en.xlsx`, listed on its electricity statistics page (`https://www.nsi.bg/en/statistical-data/81/293`). One GET, no key. Source id `nsi_bg:energy_1_4_electricity`. Connector: `warehouse/connectors/nsi_bulgaria_electricity.py` (session 2539). www.nsi.bg's robots file closes `/admin/` only (read 1006).

## Vintage and revision

The workbook's sheets as NSI publishes them: on 24 October 2026, "2019" (twelve months) and "2026" (January to July). Written by run `20261024T214340Z` (the write under the lock, offline), which read the workbook saved at 2026-10-24T21:40:18Z. `vintage` is its last-modified time, 2026-08-24T08:24:00Z. The workbook holds no other year, so 2020 to 2025 are not here; a later run takes whatever sheets it then holds.

## Shape and variables

Series, 157 rows, 10 entities. `entity` `nsi:bg:<item>`; `unit` MWh (NSI's GWh, whole, times 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` BG; `node` NSI's row label; `x_period` the month.

| `variable` | Items | Figures |
|---|---|---|
| `gross_production`, `net_production` | total | 2019: 44.161 and 40.296 TWh; January to July 2026: 25.111 and 23.101 TWh |
| `net_production` (2026 only) | nuclear, coal, petroleum_products, natural_gas, combustible_renewables, hydro, wind, solar, other | July 2026: nuclear 1,398, solar 1,021 GWh |
| `imports`, `exports` | total | 2019: 3.043 and 8.854 TWh |
| `net_consumption` | total | 2019: 33.826 TWh |

The sources hold net production: a sum over entities takes one level.

## Reading the source

- The run stops at once, asking nothing, while `nsi_bg_energy` or www.nsi.bg is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved workbook.
- **Months:** a sheet's header row is either "months of 2019" over a row of I to XII, or "I.2026" and the like; either gives the columns.
- **Figures:** held as text, whole GWh. "-" (no case registered) has no row; ".", "x" or any other mark stops the run. The legend rows at the foot are passed over; a label's trailing space is dropped ("of which Coal ").
- **Sums:** each 2026 month's nine sources to its net production within 5 GWh (nine figures each rounded to a whole GWh; May 2026's differ by 3).
- The run stops, and no file is written, for: a row not in the map, a month header of another form, a key given twice, a sum missed, a workbook with no figure.

Nothing is filled.

## License

Internal. NSI's licence (read 1008), section 2.1.1, allows reproduction, dissemination and use, commercial included, with the author named, but "You may not disseminate derivative or collective works". Verdict (session 2539): needs written permission, a reshaped table in a warehouse being possibly both; the question is with the owner. Held from the live set and from Redivis.

## Cross-checks (session 2539)

- `eia_world_electricity_annual`, Bulgaria, 2019: NSI's exports 8.854 TWh against EIA's 8.855, imports 3.043 against 3.045; EIA's generation, 42.809 TWh, lies between NSI's net and gross production.

## What it does not hold

- 2020 to 2025 (not in the workbook; NSI's monthly releases and yearbooks hold them as PDFs); 2019 by source; prices (BGN).
