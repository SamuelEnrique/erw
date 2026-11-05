# Published low and high cases of the battery's assumptions

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 19 October 2026.

Tables: `battery_sourced_ranges`

## Publisher and address

National Laboratory of the Rockies (NLR, formerly NREL), 2025 Electricity Annual Technology Baseline (ATB), workbook
`2025_v1_Workbook_08-27-2026.xlsx`, sheet "Utility-Scale Battery - R&D" (battery costs from Cole, Ramasamy and Olmez
Turan, Cost Projections for Utility-Scale Battery Storage: 2025 Update, NREL/TP-6A40-93281). Address:
`https://data.openei.org/files/8759/2025_v1_Workbook_08-27-2026.xlsx`. Page: `https://atb.nlr.gov/electricity/2025/data`.

Builder: `warehouse/connectors/sourced_ranges.py` (session 306). The header's "Retrieved" line names
`warehouse/connectors/battery_sourced_ranges.py`: the connector builds that name from the table's, and no file of that
name exists. It also writes `site/data/sourced_ranges.json`, the same rows for the battery page.

Where each figure comes from: every value is read from the workbook kept in `warehouse/raw/nlr_atb/` (SHA-256
`fa0a2b95efb85ba448467d34054db6770d274db0076ae42eda87d69827155c44`), never typed. Each row names its document in
`x_document` and its place in `x_page`: the sheet, the row and the column 2025 (for example "sheet Utility-Scale Battery
- R&D, row 19, column 2025"). The technical life comes from row 68, the line "For 15-year technical life". Coverage.csv
marks the table `derived` no, tier `source`: it computes nothing from other ERW tables.

## Vintage and revision

One year, 2025 (`ts_utc` 2025-01-01, `freq` `P1Y`). Held from coverage.csv: 2025-01-01, last run 2026-10-19T12:40:18Z.
`vintage` is the workbook's date, 2026-08-27 (2025 v1); `retrieved_at` 2026-10-19T06:12:19Z, when the workbook was kept.

A snapshot: each run reads the kept workbook and replaces the table whole (the last run: 90 rows, the previous file 90).
No scheduled job runs it. `--pull` asks NLR's data host for the workbook first, one request; without it no request is
made. Session 306 used 3 requests of its ceiling of 3 (the data page, the disclaimer agreement and the workbook,
8,509,204 bytes).

## Shape and variables

Series. `entity` `nlr_atb_2025:utility_battery[_<d>h]:<case>`, where `<d>` is the duration in hours and `<case>` the
ATB's case in lower case. Key (`entity`, `variable`, `ts_utc`). `geo` `US`; `source` `nlr:atb-2025-v1`.

| Variable | Unit | Durations | The workbook's label |
|---|---|---|---|
| `capex` | `USD/kW` | 2, 4, 6, 8, 10 h | CAPEX ($/kW) |
| `overnight_capital_cost` | `USD/kW` | 2, 4, 6, 8, 10 h | Overnight Capital Cost ($/kW) |
| `fixed_om` | `USD/kW-year` | 2, 4, 6, 8, 10 h | Fixed Operation and Maintenance Expenses ($/kW-yr) |
| `grid_connection_cost` | `USD/kW` | 2, 4, 6, 8, 10 h | Grid Connection Costs (GCC) ($/kW) |
| `round_trip_efficiency` | `ratio` | 2, 4, 6, 8, 10 h | Round-Trip Efficiency |
| `energy_capital_cost` | `USD/kWh` | none | Battery Energy Capital Cost ($/kWh) |
| `power_capital_cost` | `USD/kW` | none | Battery Power Capital Cost ($/kW) |
| `interest_rate_nominal` | `ratio` | none | Interest Rate Nominal |
| `return_on_equity_nominal` | `ratio` | none | Rate of Return on Equity Nominal |
| `technical_life` | `year` | none | "For 15-year technical life" |

| x_* field | Holds |
|---|---|
| `x_case` | `low`, `mid` or `high` on the cost scale |
| `x_published_case` | the ATB's own case: Advanced (low), Moderate (mid), Conservative (high) |
| `x_duration_h` | the hours, empty where the assumption has no duration |
| `x_document` | the document, as above |
| `x_page` | the sheet, row and column |
| `x_dollar_year` | 2023 for a dollar value, empty otherwise |

Where the workbook gives one value for all three cases (efficiency, the rates, the life), each case has its row with
that value.

As of 23 October 2026: 90 rows, 18 entities, 10 variables, 30 rows a case. `x_dollar_year` 2023 on 66 rows, empty on
24.

| Assumption (2025, 2023 dollars) | Low (Advanced) | Mid (Moderate) | High (Conservative) |
|---|---|---|---|
| `capex`, 4 h, USD/kW | 1,291.60 | 1,396.73 | 1,444.91 |
| `fixed_om`, 4 h, USD/kW-year | 45.81 | 49.87 | 51.74 |
| `energy_capital_cost`, USD/kWh | 199.76 | 222.63 | 233.12 |
| `power_capital_cost`, USD/kW | 346.12 | 356.28 | 360.95 |
| `grid_connection_cost`, every duration, USD/kW | 104.12 | 104.12 | 104.12 |
| `round_trip_efficiency`, every duration | 0.85 | 0.85 | 0.85 |
| `interest_rate_nominal` | 0.065 | 0.065 | 0.065 |
| `return_on_equity_nominal` | 0.085 | 0.085 | 0.085 |
| `technical_life`, years | 15 | 15 | 15 |

The values are rounded here; the file keeps six decimals.

## License

ERW verdict (docs/licenses.md, "Every table"): verdict today "may be public"; flag in coverage.csv "public"; flag and
verdict "agrees"; if the ERW sells anything "may be public"; ERW verdict "public". NLR's notice (read 65): "The user is
granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all
copies of the Data." Credit DOE/NLR and keep the notice. Cite "National Laboratory of the Rockies (NLR), 2025 Electricity
Annual Technology Baseline (ATB), workbook 2025_v1_Workbook_08-27-2026.xlsx", with the sheet and row in `x_page`.

## Cross-check (session 487)

Session 487 read the ATB's 2025 parquet file for `nlr_atb_electricity_costs` and compared it with this table: the
four-hour utility battery's 2025 CAPEX (1,291.60, 1,396.73, 1,444.91 USD/kW), overnight capital cost and fixed O&M are
the same in all three cases, to every digit kept. The connector itself compares nothing; it refuses a key given twice.

## What it does not hold

- One source. Lazard's LCOE+ (June 2025) is read only from a copy held in `warehouse/raw`; none is held, so none of its
  cases is written and no request was made.
- What the ATB does not state, so not written: cycles a year or a day; degradation; capacity fade; augmentation cost;
  the debt share of a utility-scale battery (the WACC sheet gives none for it).
- One year (2025) of a workbook that runs to later years; one sheet (the R&D cost drivers without tax credits, the ATB's
  default).
- No conversion of dollars: the values are the workbook's 2023 dollars. Session 306 noted that `site/lib/battery/finance.ts`
  called the ATB figures "2024 dollars".
