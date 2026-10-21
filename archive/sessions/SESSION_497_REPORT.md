# Session 497 report: EIA's State Energy Data System

21 October 2026, from about 18:05 UTC, on lab-desktop (the data machine), a public source probed while the daily run held the data lock. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_seds.py`: each state's energy consumption, electricity prices and expenditures, a year**, from EIA's API v2 (route `seds`), as the series table `eia_seds_state_energy`.
  - There are 13 series in every state and the U.S. total, from 1990 to 2024: 23,660 rows, 676 series by state.
  - The series are:
    - consumption, in TBtu: total, electricity, natural gas, coal, petroleum and renewables, with nuclear;
    - electricity's price by sector and for all sectors, in USD/MMBtu;
    - the expenditures on electricity and on all energy, in USD.
- **Robots and terms**: EIA's API path is allowed, and EIA's terms are record 1 of `license_reads.csv` (public).
- **Cross-check** (run again on the written table by `runs/s497_crosscheck.py` on the data machine): each state's electricity sold to all sectors (ESTCB) against `eia_retail_sales_monthly`'s all-sector sales, summed over each whole year, at 3,412 Btu per kWh.
  - 1,248 state-years are in both, 2001 to 2024.
  - The median ratio is 1.0000, the lowest 1.0000 and the highest 1.0004.
- SEDS's figures are EIA's estimates, as its technical notes say, and are published by EIA. Nothing is filled here: a withheld value has no row. A unit not in the map stops the run, and so does a key given twice.
- Sector rule (`power;gas;oil;coal`). Tests: `tests/test_session497.py`, 3. Written in session 489.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 5 of 20 | pages of 5,000 (the trial; the write in session 489 asked again) |

## Decisions made without you

1. From 1990, not 1960, to keep the table smaller; the earlier years can be added by a later run.

## Files

- New: `warehouse/connectors/eia_seds.py`, `tests/test_session497.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
