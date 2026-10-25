# The CO2 intensity of the UK's electricity supplied, 1996 to 2025 (DESNZ's DUKES 5.14)

Energy Research Warehouse (ERW), method note written in session 2731 (chain 137) for a table first written on 25 October 2026 (session 2729).

Tables: `desnz_uk_co2_intensity_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Estimated carbon dioxide intensity of electricity supplied (DUKES 5.14)", `https://assets.publishing.service.gov.uk/media/6a6a3684bf4a7aca8f8976c4/DUKES_5.14.xlsx`, its sheet "5.14". No key. Source id `desnz:dukes_5_14_co2_intensity`. Connector: `warehouse/connectors/desnz_dukes_co2_intensity.py` (session 2729), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1465); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T193527Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T19:33:21Z (last modified 2026-07-29T17:21:08Z), DUKES 2026's edition. DESNZ's note 3: 2025's emissions are provisional.

## Shape and variables

Series, 119 rows, four entities, each year from 1996 to 2025. `entity` `desnz_ci:<fuel>`:
- `coal`, to 2024;
- `gas`;
- `non_renewable`: coal, oil, gas and other solid fuels, non-renewable waste included (note 5);
- `all_fuels`: every fuel of DUKES 5.6, nuclear and renewables included, net pumped storage and net imports left out (note 6).

`variable` co2_intensity; `unit` kgCO2/MWh, the sheet's tonnes of CO2 per GWh supplied, the same number; `ts_utc` the year's first day; `freq` P1Y; `geo` GB; `node` the sheet's row.

**Figures:**
- All fuels: 521.3 kg per MWh in 1996, 457.5 in 2010, 178.4 in 2020, 153.7 in 2024 and 147.2 in 2025.
- Gas: 455.1 in 1996, 365.4 in 2025.
- All non-renewable fuels: 719.3 in 1996, 421.7 in 2025.
- Coal: 882.3 in 1996, 921.2 in 2024.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **DESNZ's notes:**
  - The numerator is the power stations' emissions with an estimate for autogeneration, and the denominator the electricity supplied by all generators (note 1).
  - The figures differ from the government's conversion factors for company reporting, which lag two years (note 2).
  - Coal generation ceased in 2024, so coal has no figure from 2025 (note 4).
  - Only the generators' operational emissions are counted, not the fuel supply chain's (note 7).
- The table is found by its title, its year row (each year from 1996 in turn, note marks read off) and its four fuel rows in order. A blank cell has no row.
- **Checks,** all passing: every value is a positive number, and all fuels' intensity is never above the non-renewable fuels' in any year.
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

No other ERW table holds the UK's carbon intensity of electricity; the ERW's carbon intensity tables are EIA-930's American balancing authorities. The checks above are internal.
