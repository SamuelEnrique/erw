# Session 2720 report: the UK's electricity storage a year, 1996 to 2025 (DESNZ's DUKES 5.16), public, a third source of the session's own choosing

25 October 2026, about 17:17 to 17:19 UTC, run before sessions 2717 to 2719 while the data lock was held, with the write at 18:26 UTC, on lab-desktop (the data machine), chain 136, unattended. Precheck passed (`runs/c136/pre2720.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **The ERW's storage tables were all American** (EIA-860, EIA-930, ERCOT and CAISO). DUKES 5.16 gives the UK's storage by type over thirty years, from the chapter of sessions 2714 and 2715.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1449). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_storage_annual`** (series, 360 rows, `power`), 1996 to 2025:
  - Entity `desnz_st:<type>`: pumped_storage, battery_grid_scale (DESNZ's note 2 leaves out batteries behind the meter), other_storage, total.
  - Variables: `output` and `input` in MWh (tables 5.16.A and B, GWh times 1,000), and `power_capacity` in MW (5.16.C, the rate at which the sites may supply their stored energy, DESNZ's note 1).
  - Each table is found by its title, its year row (each year from 1996 in turn) and its four type rows in order. A zero is kept, as DESNZ writes it.
- **Figures:**
  - Grid-scale battery power capacity was 1,097 MW in 2020, 3,820 in 2023, 5,210 in 2024 and 7,512 in 2025. It passed pumped storage's 2,744 MW in 2023.
  - Batteries discharged 2,274 GWh in 2025 against 2,688 GWh charged, a round trip of about 85 per cent.
  - Pumped storage's was 81 per cent (1,437 GWh out against 1,767 GWh in).
- **Checks, all passing:** the three types add to the total in each table and year, within 0.01.
- **Its record:** written by run `20261025T182559Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T182603Z-local`), held from the live set, and in the release package (public).
- **The write's patch conflicted in `sources.csv`** again, beside session 2715's row. It was resolved as a union, with no marker and no row twice, and committed before the finish.

## Cross-check

Against session 2714's `desnz_uk_power_stations`: pumped hydro is 2,900 MW there (the four stations at the end of May 2026), against 2,744 MW of power capacity here (the end of 2025). DESNZ gives storage's power capacity on another basis than installed capacity. The same 2,744 MW stands in every year since 2007.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.16.xlsx (the fetch) | 200 |

Read recorded: 1449.

## Decisions made without you

- **DUKES 5.16 as the third own choice; public.**
- **The `power` sector:** the ERW has no storage sector.
- **Run before sessions 2717 to 2719,** so that its table is described and uploaded with the chain's others.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_storage.py`, `tests/test_session2720.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1449) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2720/`, `runs/license_reads/s2720/`, `warehouse/raw/desnz_dukes/s2720probe1/`, `warehouse/output/desnz_uk_storage_annual.csv`.
