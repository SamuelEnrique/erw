# Session 2325 report: Kenya's generation capacity and electricity consumption (EPRA's statistics reports)

24 October 2026, from 07:09 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Precheck passed (`runs/c108/pre2325.out`). Model spend USD 0. Pulls: 6 of 15 (below).

## Read these first

- **One public table:** `epra_kenya_electricity_annual`, from the Energy and Petroleum Regulatory Authority's Energy and Petroleum Statistics Reports for the fiscal years 2023/24, 2024/25 and 2025/26 (July to June). It is written, validated, archived, in coverage (sector power), and held from the live set and the release. 129 rows, 43 variables:
  - **Table 2.1:** capacity by technology as at each 30 June: interconnected installed and effective, captive, offgrid and total installed (MW).
  - **Table 2.2:** consumption by customer category: industrial, domestic, small commercial, street lighting, e-mobility, total (MWh, EPRA's GWh times 1,000).
- **How the PDFs are read:** EPRA publishes its statistics as PDF reports only. The tables are read with pdfplumber's table extraction, already a requirement of the repository, which keeps blank cells in place (pdftotext lost them).
  - Every part's technologies must add to its total, and every technology's interconnected, captive and offgrid capacity to its total installed, within 0.15 MW.
  - The customer categories must add to their total within 0.15 GWh.
  - All three reports pass. A failed check stops the run.
- **License:** each report says "Unless otherwise stated, material in this publication may be freely used, shared, copied, reproduced, printed and/or stored, provided that appropriate acknowledgment is given of EPRA as the source and copyright holder" (read 528; the same in reads 529 and 530). A new verdict, may be public in both columns.
  - EPRA's robots file keeps the default Drupal rules and names no AI agent (read 525).
- **Kenya Power (KPLC) was not needed:** EPRA's reports carry the figures the plan asked for, except monthly generation and peak demand, which the reports give only as charts.

## The cross-check (`runs/c108/s2325/cross.py`, `cross.out`)

- **Against `irena_capacity_annual`'s Kenya** (IRENA counts at each December):
  - Wind: 436.1 MW in both, every year.
  - Geothermal: 943.7 MW (June 2024 and 2025) against IRENA's 939.7 (end 2024).
  - Hydro: 872.4 to 872.6 against 892.0 to 892.7 (2.3 per cent below).
  - Solar: 514.1 MW (June 2025) against 551.1 (end 2024). The two differ in timing and in what captive solar they count.
- **Against `owid_ember_electricity_annual`'s demand:** EPRA's 2024/25 consumption (11.33 TWh) is about 23 per cent below Ember's calendar 2024 and 2025 demand (14.75 and 15.58 TWh). Consumption is sales; demand includes losses, which EPRA's reports put at about 20 per cent and more.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.epra.go.ke | 6 of 15 | robots, the home page, the statistics page, three reports (4.4, 1.9 and 2.5 MB); 3 s or more apart |

## Errors

- **The first trial missed the 2026 report's table 2.2:** its title's year falls on a later line among the other column's text. The title match now takes the first year pair within 400 characters.
- **A test's made-up table had no offgrid total,** which the connector rightly refused; the test was corrected.

## Decisions made without you

- **Three fiscal-year reports, not the calendar-year ones** (2020 to 2023) or the half-year reports, which give other periods.
- **A dash read as no row,** like a blank, since EPRA does not say whether a dash means zero.
- **Capacity dated by its fiscal year's 1 July,** "as at" its 30 June, as `irena_capacity_annual` dates a year-end figure.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/epra_kenya_electricity.py`
  - `tests/test_session2325.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (525 to 530), `license_verdicts.csv` (EPRA), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2325/`, `runs/license_reads/s2325/`, `runs/s2325*`.
