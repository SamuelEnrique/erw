# Session 2481 report: the licenses' forty-first round (EEP needs written permission)

24 October 2026, about 13:45 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2481.out`). Model spend USD 0. Pulls: none of 20. The verdict rests on a page this chain's source sessions already read.

## Read these first

- **One verdict: Ethiopian Electric Power (EEP)** (read 812): its home page's footer, "© 2026 Ethiopian Electric Power | Powered by Ethiopian Electric Power." The page writes the sign as `&copy;`. No reuse statement is on the page. Verdict: **needs written permission**, sold or not, as EEHC's and POWER Magazine's notices are read. The ERW holds no table of it.
- **Not given a verdict:**
  - **MIREME (Mozambique):** its home page states no terms (read 816). The "Copyright" heading of its report's technical sheet is not a page in the record, so `mireme_mozambique_electricity_annual` stays internal, its license unsettled.
  - **RIC (Trinidad and Tobago), the National Statistics Bureau of Bhutan and EDM:** no terms page was read.
  - **The Ethiopian Statistics Service:** its host does not resolve.
  - **Statistics Canada:** has its verdict already; this chain's three StatCan tables rest on it.
- **The record:** `licenses.py tables`, `write` and `check` give 540 tables, 159 publishers with a verdict, and 0 problems. Tests 205, 207 and 887 pass.

## Decisions made without you

- **A copyright line with no reuse statement read as needs written permission,** as the record reads EEHC's.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (one row), `warehouse/metadata/license_tables.csv`, `docs/licenses.md`. New: this report.
