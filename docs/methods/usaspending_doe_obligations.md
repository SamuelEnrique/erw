# The Department of Energy's budget and obligations, a fiscal year, from fiscal 2017 (USAspending.gov)

Energy Research Warehouse (ERW), method note written in session 2188 (chain 097) for a table first written on 24 October 2026 (session 2188).

Tables: `usaspending_doe_obligations`

## Publisher and address

The U.S. Department of the Treasury's Bureau of the Fiscal Service publishes USAspending.gov, the federal spending record under the DATA Act. Its public API gives each agency's figures by its toptier code; the Department of Energy is 089 (the toptier agencies list, read 379).

- `https://api.usaspending.gov/api/v2/agency/089/budgetary_resources/`: each fiscal year's budgetary resources, total obligations and total outlays, and the obligations to date at each reporting period.
- `https://api.usaspending.gov/api/v2/agency/089/obligations_by_award_category/?fiscal_year=<year>`: the year's award obligations by category, one request a year, fiscal 2017 to 2026.

api.usaspending.gov has no robots file (HTTP 404, read 377). www.usaspending.gov's disallows only addresses with a query or `.php` (read 378). The API's landing page states no terms of use (read 380).

## Vintage and revision

USAspending revises its figures at the same addresses, so each run asks all 11 again unless `--offline`. A fiscal year runs from 1 October to 30 September; a year not yet closed is marked `x_partial` yes. On 24 October 2026 fiscal 2026 is reported to its period 11 (August), and fiscal 2027 is listed with no figures and has no row.

## Shape and variables

Series, 163 rows, fiscal years 2017 to 2026, unit USD, `geo` US.

- `usaspending:doe`:
  - `budgetary_resources`, `obligated` and `outlayed`, each the fiscal year's total (`freq` P1Y, `ts_utc` the year's first day, 1 October of the year before);
  - `obligated_to_date`, the year's obligations through a fiscal period (`x_period`, 1 is October; `ts_utc` the period's month). It is monthly (P1M) from fiscal 2022 and quarterly (P3M) before; fiscal 2017 starts at period 6. The last period's figure equals the year's `obligated` in every year.
- `usaspending:doe:<category>`: `award_obligations`, the year's obligations by award category (contracts, direct_payments, grants, idvs, loans, other; P1Y). A category can be negative in a year where de-obligations exceed new awards.
- `x_fiscal_year`, `x_period` and `x_partial`.

The award categories sum to 77 to 89 percent of the year's obligations (session 2188's check). Obligations outside awards, salaries for one, are in the total only.

## Checks the connector makes

- The record must be toptier 089's.
- A fiscal year or a period given twice stops the run.
- A category not among the six read stops the run.
- A figure that does not read as a number stops the run.
- A key given twice in the table stops the run.

Nothing is filled.

## The figures, as read on 24 October 2026

- **Budgetary resources** were 49 to 61 billion USD a year in fiscal 2017 to 2021, then 130 billion in fiscal 2022, the year the infrastructure law's funds arrived, and 141 to 153 billion since.
- **Obligations** rose from 41.6 billion (fiscal 2017) to 98.5 billion (fiscal 2025).
- **Grants** rose from 3 to 4 billion a year to 9.1 billion (fiscal 2023), 14.6 billion (2024) and 28.8 billion (2025). Fiscal 2026 holds 2.6 billion to August.
- **Contracts** rose steadily, from 28.9 to 55.1 billion.

## License

Internal until a ruling. USAspending is the Treasury's, and the Treasury's terms are a standing question for the owner, as for `treasury_1603_awards` (session 2112). No verdict is recorded. The header cites USAspending.gov.

## Found while writing this note

- The by-state geography of the obligations needs a POST to USAspending's search API. The ERW's fetch helper asks by GET only, so the agency's national figures are taken.

## What it does not hold

- Any agency but DOE, any state or recipient, or a single award.
- Budget authority by DOE office, and outlays by award category.
