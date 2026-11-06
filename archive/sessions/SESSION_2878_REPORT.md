# Session 2878 report: reserve margins beyond ERCOT

5 November 2026, about 21:47 to 21:48 UTC, on lab-desktop (the data machine), chain 147, unattended, done while session 2863's landing gate ran. Model spend USD 0. Pulls: www.eia.gov 3 of 15.

## Read these first

- **Held, and not wired, by a ruling already made.**
  - `eia411_capacity_margins_annual` is in coverage (chain 049, session 895: EIA-411's peak load, resources and margins by NERC area, 1990 to 2027, public).
  - Decision 30 of `docs/methods/siting.md` (session 1047) rules that it is not drawn as a grid's planning reserve margin. EIA-411's last release is of November 2016, so its summer 2027 figures are 2016 projections: ERCOT's reads 38.07% against 11.43% in ERCOT's own CDR.
  - Wiring the table would reverse that decision, so the tab is left as it is.
- **EIA publishes no current reserve margins by assessment area.**
  - The Electric Power Annual's index (read 21:48 UTC) lists no table of peak demand, capacity resources or margins by NERC area. Chapter 4 is capacity by source, producer type, state, and fuel switching.
  - `epa_04_01_a.html`, the old address of such a table, redirects to `/electricity/`.
  - `eia_reserve_margins_annual` is therefore not written.
- **The siting gaps row "reserve margins by zone"** stays filled for ERCOT only (`ercot_cdr_reserve_margins`) and open for the other grids.

## Decisions made without you

- **NERC's long-term reliability assessment was not read.** NERC's terms could not be read (session 666), and the chain names EIA.

## For Samuel's ruling

- **A source for other grids' margins:** each ISO's own resource adequacy report (CAISO, NYISO, ISO-NE, SPP, PJM, MISO; each with its own license), or NERC's LTRA once its terms are read.

## Files

- New: this report.
- On the data machine only: `runs/s2878/`, `runs/license_reads/s2878/`.
