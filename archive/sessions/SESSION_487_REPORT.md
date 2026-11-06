# Session 487 report: the NLR (NREL) Annual Technology Baseline's costs

21 October 2026, from 17:02 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October ("NREL ATB costs"; the laboratory is now the National Laboratory of the Rockies, NLR). Model spend USD 0.

## Read these first

- **Robots and terms**:
  - The Open Energy Data Initiative's bucket (`oedi-data-lake.s3.amazonaws.com`) has no robots file (404), so the convention allows it.
  - NLR's data terms were read in session 312 and are kept in `warehouse/raw/nlr_atb/terms/`: use and copy without fee, the notice kept, DOE and NLR credited. License public, with that credit.
- **The bucket's own listing names the newest**: `ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet` (9.2 MB; the same data as a 321 MB CSV). It holds 1,161,588 rows: 20 technologies, 28 parameters, 4 cost cases, 4 scenarios and 7 cost-recovery periods, for 2023 to 2060.
- **The ATB's default view, as session 312 read its workbook**:
  - the R&D cost case (no tax credits) and a 30-year cost recovery;
  - seven parameters: CAPEX and OCC (USD/kW), fixed O&M (USD/kW-year), variable O&M, fuel and LCOE (USD/MWh), capacity factor (ratio).
  - The rows repeat for every recovery period wherever the value does not depend on it, and 30 years exists for all 20 technologies.
  - Values are in the ATB's dollars (2023 for the 2025 ATB, as its workbook says); nothing is converted or filled.
- **`warehouse/connectors/nlr_atb_costs.py`**:
  - one series table `nlr_atb_electricity_costs`: entity `nlr_atb_2025:<technology>:<detail>:<scenario>`; the ATB's fields as `x_` columns, with `x_dollar_year` and `x_atb_version`;
  - a year with no recorded dollar year stops the run, so that a 2026 ATB is not read in the wrong dollars;
  - the sector rule and `tests/test_session487.py` (4 tests); landed as `ffc3b0c0`.
- **Trial**: 95,000 rows, 547 entities, 20 technologies; the validator passes (after `USD/kW-year`, `ratio` and an ISO vintage).
- **Cross-check against session 312's reading of the 2025 workbook** (`battery_sourced_ranges`): the four-hour utility battery's 2025 CAPEX (1,291.60, 1,396.73, 1,444.91 USD/kW), OCC and fixed O&M are the same in all three scenarios, to every digit session 312 kept.

## To finish (session 489)

`python warehouse/connectors/nlr_atb_costs.py` (the file is reused; one request, the listing), the validator, `build_coverage.py --only '^nlr_atb_electricity_costs$'`, `archive.py write --tables '^nlr_atb_electricity_costs$'`, `licenses.py tables` and `write`, and land.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| oedi-data-lake.s3.amazonaws.com | 4 | robots (404), the listing twice, the parquet once |

## Decisions made without you

1. The default view only (R&D, 30 years), as session 312 chose; the tax-credit and market cases are left in the ATB.
2. The parquet, not the CSV (the same data, 35 times smaller).

## Files

- New: `warehouse/connectors/nlr_atb_costs.py`, `tests/test_session487.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
- On this machine (not in git): `warehouse/raw/nlr_atb_costs/`, `runs/s487/`.
