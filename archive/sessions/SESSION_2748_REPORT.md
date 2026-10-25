# Session 2748 report: the fuel used in UK electricity generation, 1996 to 2025 (DESNZ's DUKES 5.3), public, a third source of the session's own choosing; DUKES 5.15 set aside

25 October 2026, about 21:03 to 21:10 UTC, run before sessions 2745 to 2747, on lab-desktop (the data machine), chain 138, unattended. Precheck passed (`runs/c138/pre2748.out`). Model spend USD 0. Pulls: 3 requests of 20 (1 by the probe, 2 fetches: DUKES 5.15, set aside, and DUKES 5.3).

## Read these first

- **DUKES 5.15 (combined heat and power) was fetched and set aside:**
  - Its 2025 column repeats its 2024 column in every row, totals included. For example, the major power producers' capacity is 61,326.68 MW in both years, where DUKES 5.7 gives 61,931.21 MW for 2025.
  - Its generation totals also repeat 2017 as 2018 (the major power producers' and all generators', the rows checked).
  - DESNZ's note 5 explains carried-forward values for CHP sites without a return, not whole totals. A table with a doubtful last year would mislead, so 5.15 was not written; its workbook is saved (`warehouse/raw/desnz_dukes/s2748probe1/`).
- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1480). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_fuel_used_generation_annual`** (series, 900 rows, 30 entities, `power`), 1996 to 2025:
  - Entity `desnz_fuel:<group>:<fuel>`, groups mpp, other_transport, other_industrial, other and all.
  - Variable `fuel_used` (5.3.B, by fuel) or `fuel_used_by_plant` (5.3.C, the major power producers' CCGT and conventional steam stations).
  - **Unit MWh:** the sheet's million tonnes of oil equivalent times 11,630,000, from DESNZ's own 1 ktoe = 11.63 GWh (stated on the DUKES 5.11 workbook's cover sheet). The ERW's validator holds no MTOE, and this fixed conversion avoids a new unit.
  - Table 5.3.A (fuels in million tonnes and GWh) is not taken.
- **Figures:**
  - All companies used 925.6 TWh of fuel in 1996, 923.4 in 2010 and 545.1 in 2025.
  - Coal fell from 391.0 TWh to none; gas was 202.0 TWh in 1996 and 192.2 in 2025.
- **Checks,** within 0.02 MTOE:
  - each group's fuels add to its total;
  - the transport and industrial generators add to the other generators;
  - the major power producers and the others add to all companies.

  DESNZ's rows and totals differ by up to 0.0153 MTOE (all companies), a little beyond rounding, so the tolerance was set above that and the measured gap stated in the connector.
- **Its record:** written by run `20261025T210701Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T210706Z-local`), held from the live set, and in the release package (public).

## Cross-check

Against `desnz_uk_gas_quarterly` (Energy Trends 4.1, gas for electricity generation, four quarters summed), TWh:

| Year | Energy Trends 4.1 | DUKES 5.3 (here) |
|---|---|---|
| 2015 | 212.3 | 212.6 |
| 2020 | 232.5 | 232.5 |
| 2024 | 179.6 | 179.6 |
| 2025 | 192.2 | 192.2 |

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.15.xlsx (a fetch, set aside) | 200 |
| 3 | DUKES_5.3.xlsx (the fetch) | 200 |

Read recorded: 1480.

## Decisions made without you

- **DUKES 5.15 not written** for its repeated 2025 column.
- **MTOE stated as MWh** at DESNZ's own conversion, rather than a new unit.
- **The tolerance at 0.02 MTOE,** above DESNZ's own row and total differences.

## For Samuel's ruling

- None new. (DESNZ may be told of 5.15's 2025 column; no letter is sent.)

## Files

- New: `warehouse/connectors/desnz_dukes_fuel_used.py`, `tests/test_session2748.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1480) and `docs/licenses.md`.
- On the data machine only: `runs/c138/s2748/`, `runs/license_reads/s2748/`, `warehouse/raw/desnz_dukes/s2748probe1/` (5.15) and `s2748probe2/` (5.3), `warehouse/output/desnz_uk_fuel_used_generation_annual.csv`.
