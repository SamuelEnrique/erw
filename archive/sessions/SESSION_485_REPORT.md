# Session 485 report: EIA-861 utility sales

21 October 2026, from 16:59 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October. Model spend USD 0.

## Read these first

- **Robots and terms**: `www.eia.gov/robots.txt` allows the EIA-861 page and its zips. EIA's terms are in the record (record 1, 12 October 2026: "U.S. government publications are in the public domain"). License public.
- **The newest year is 2025, final data** (`zip/f8612025.zip`, 4.8 MB, posted 7 October 2026). The table is from `Sales_Ult_Cust_2025.xlsx`, sheets States and Territories.
- **Real data only.** Each row of EIA's sheet is marked O (observed) or I (imputed: the short-form utilities EIA estimates). Only observed rows are taken: 2,697 of 2,880.
  - Two aggregates are not utilities and are left out: 88888 ("Withheld", the retail power marketers EIA does not name) and 99999 ("Adjustment 2025", imputed).
  - A "." cell has no row.
  - After that the key is unique: utility, state, part (A bundled, B energy only, C delivery only, D a power marketer's bundled) and balancing authority.
- **`warehouse/connectors/eia861_sales.py`**:
  - one series table `eia861_utility_sales`: entity `eia861:<utility>:<state>:<part>:<BA>`; variables `<sector>_sales` (MWh), `_revenue` (USD, EIA's thousand dollars times 1,000) and `_customers` (count) for five sectors; ts_utc the year's 1 January; geo `US-<state>`; EIA's own fields as `x_` columns;
  - the sector rule and `tests/test_session485.py` (5 tests); landed as `ffc3b0c0`.
- **Trial**: 34,484 rows, 2,612 sheet rows, 1,532 utilities; the validator passes.
- **Cross-check against EIA's monthly state retail sales** (`eia_retail_sales_monthly`, 2025, parts A, B and D, which EIA's own state totals count):
  - the observed rows come to 3,912.6 TWh against 4,058.0 TWh, a median state of 97.4% (Texas 98.8%, Florida 99.2%, Wyoming 92.9%);
  - the gap is the imputed and withheld rows left out, as expected.

## To finish (session 489)

`python warehouse/connectors/eia861_sales.py` (the zip is reused; one request, the page), the validator, `build_coverage.py --only '^eia861_utility_sales$'`, `archive.py write --tables '^eia861_utility_sales$'`, `licenses.py tables` and `write`, and land. Earlier years: session 495.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 4 | robots file, the page twice (probe and trial), the zip once (reused by the trial) |

## Decisions made without you

1. Observed rows only; the two aggregates out.
2. Revenue in USD, not EIA's thousands, so it joins the ERW's other money.
3. 2025 first; earlier years in session 495.

## Files

- New: `warehouse/connectors/eia861_sales.py`, `tests/test_session485.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
- On this machine (not in git): `warehouse/raw/eia861/`, `runs/s485/`.
