# British Columbia's balancing authority load an hour, January 2024 to September 2026 (BC Hydro)

Energy Research Warehouse (ERW), method note written in session 2681 (chain 134) for a table first written on 25 October 2026 (session 2679).

Tables: `bchydro_ba_load_hourly`

## Publisher and address

BC Hydro (British Columbia Hydro and Power Authority) publishes an Hourly Control Area Load Report a year for its balancing authority (BCHA), listed on its historical transmission data page. The table reads the workbooks of 2024, 2025 and the year in progress, 2026, under `https://www.bchydro.com/content/dam/BCHydro/customer-portal/documents/corporate/suppliers/transmission-system/balancing_authority_load_data/`, no key. Source id `bchydro:hourly_control_area_load_report`. Connector: `warehouse/connectors/bchydro_ba_load.py` (session 2679), whose raw store is `warehouse/raw/bchydro/`. www.bchydro.com's robots file closes extranet, media library and account paths, not these documents (read 1396).

## Vintage and revision

Written by run `20261025T115752Z` (the write under the lock, offline), which read the workbooks retrieved from 11:54 to 11:56 UTC on 25 October 2026. The 2025 workbook was last modified on 15 January 2026. The 2026 workbook runs to 30 September 2026 and grows as the year goes on.

## Shape and variables

Series, 24,095 rows, 1 entity: `bchydro:bcha:load`, variable `load`. `unit` MW (the hour's control area load as published); `ts_utc` the hour's start; `freq` PT1H; `geo` CA-BC; `node` BCHA.

The hours run from 08:00 UTC on 1 January 2024 to 06:00 UTC on 1 October 2026. By UTC year:
- 2024: 8,776 hours, 66.4 TWh, peak 12,334 MW;
- 2025: 8,760 hours, 67.3 TWh, peak 11,359 MW;
- 2026: 6,559 hours, 49.6 TWh, peak 10,823 MW.

## Reading the source

- The run stops at once, asking nothing, while `bchydro` or www.bchydro.com is paused.
- Three requests a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The time base:** the reports are in Pacific local time with daylight saving, by hour ending (HE 1 to 24).
  - The spring day has 23 hours (no HE 2).
  - The autumn day has 25, its repeated hour marked "2*". The 2025 sheet lists "2*" before HE 2 and the 2024 sheet after; it is placed after HE 2 in time either way.
  - Each day's hours are put in that order and counted from the day's local midnight in UTC (America/Vancouver).
  - A day whose hours are not the ones its date has stops the run. The five change days in these files check.
- **Each sheet is checked for:** its title ("Hourly Control Area Load Report"), its area group (BCHA), its year, and its header ("Date", "HE", "Control Area Load"). The 2024 sheet's "Date" carries a stray mark, compared by its letters.
- Only whole days that ended before the workbook's retrieval are kept. Nothing is filled.
- The run stops for a load not positive, a date of another year, a day given twice or a gap.

## License

Internal. BC Hydro's Legal page (read 1398): "All editorial content and graphics on this site are protected by Canadian copyright and international treaties and may not be copied without the express permission of British Columbia Hydro and Power Authority (BC Hydro), which reserves all rights". Verdict: needs written permission. BC Hydro grants permission case by case. Held from the release package and the live set.

## Cross-check

Against `statcan_electricity_generation_monthly`'s British Columbia (all types of generation), in TWh:
- 2024: generation 59.0 against the load's 66.4;
- 2025: generation 64.5 against 67.3.

The load exceeds generation by BC's net imports.
