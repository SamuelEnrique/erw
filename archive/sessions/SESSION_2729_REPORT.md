# Session 2729 report: the CO2 intensity of the UK's electricity supplied, 1996 to 2025 (DESNZ's DUKES 5.14), public, a second source of the session's own choosing

25 October 2026, about 19:33 to 19:37 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2729.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **The ERW's carbon intensity tables were American** (EIA-930's hourly, daily and monthly). DUKES 5.14 gives the UK's, by fuel over thirty years, from the chapter of sessions 2714, 2715, 2720 and 2728.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1465). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_co2_intensity_annual`** (series, 119 rows, `carbon`), 1996 to 2025:
  - Entity `desnz_ci:<fuel>`: coal, gas, non_renewable (coal, oil, gas, other solid fuels and non-renewable waste) and all_fuels (nuclear and renewables included, net pumped storage and imports left out).
  - Variable `co2_intensity`, unit kgCO2/MWh: the sheet's tonnes of CO2 per GWh supplied, the same number.
- **DESNZ's notes, kept in the header and connector:**
  - the numerator includes an estimate for autogeneration;
  - the figures differ from the conversion factors for company reporting;
  - 2025's emissions are provisional;
  - coal has no figure from 2025, its generation having ceased in 2024;
  - only operational emissions are counted.
- **Figures:**
  - All fuels: 521.3 kg per MWh in 1996, 457.5 in 2010, 178.4 in 2020, 153.7 in 2024 and 147.2 in 2025.
  - Gas: 455.1 in 1996 and 365.4 in 2025.
  - Coal: 882.3 in 1996 and 921.2 in 2024, its last year.
- **Checks, all passing:** every value positive; all fuels' intensity never above the non-renewable fuels' in any year; the title, the years and the four rows in order.
- **Its record:** written by run `20261025T193527Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T193536Z-local`), held from the live set, and in the release package (public).

## Cross-check

No other ERW table holds the UK's carbon intensity of electricity (the OWID and Ember table holds no such variable for the UK). The checks above are internal.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.14.xlsx (the fetch) | 200 |

Read recorded: 1465.

## Decisions made without you

- **DUKES 5.14 as the second own choice; public.**
- **The `carbon` sector,** with the ERW's other emissions tables.
- **Tonnes per GWh stated as kgCO2/MWh,** a unit the validator holds (Decision 30), the number unchanged.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_co2_intensity.py`, `tests/test_session2729.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1465) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2729/`, `runs/license_reads/s2729/`, `warehouse/raw/desnz_dukes/s2729probe1/`, `warehouse/output/desnz_uk_co2_intensity_annual.csv`.
