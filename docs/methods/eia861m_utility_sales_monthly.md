# EIA-861M: each sampled utility's retail sales, revenue and customers by state and sector, a month

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia861m_utility_sales_monthly`

Connector: `warehouse/connectors/eia861m_sales.py` (session 511; extended back to 2017 in session 520).

## Publisher and report

U.S. Energy Information Administration (EIA), Form EIA-861M, sales to ultimate customers: one workbook a year, sheets for the states and the territories.

- Page: `https://www.eia.gov/electricity/data/eia861m/`
- Files: `https://www.eia.gov/electricity/data/eia861m/xls/sales_ult_cust_<year>.xlsx` for the current years, and under `archive/xls/` for earlier ones. EIA names its 2017 to 2020 files `retail_sales_<year>.xlsx` and later ones `sales_ult_cust_<year>.xlsx`; the connector finds both on the page. A year the page does not link stops the run.

Ceiling: the page and ten years, 11 requests a run (the module docstring still says six; the code's `CEILING` is 11, session 520). A file already saved in `warehouse/raw/eia861m/` is reused, and `--offline` asks nothing.

## Vintage and revision rule

Months January 2017 to July 2026. The header records each file's Last-Modified (for example 2025: Tue, 24 Feb 2026; 2026: Thu, 24 Sep 2026). EIA's `x_data_status` is Final for 2017 to 2024 and Preliminary for 2025 and 2026.

By default a run reads 2025 and the current year; `--years <y> ...` reads the years asked. The table is written by `write_snapshot`: each run replaces the whole table with what it read. A run that asks for fewer years than the table holds therefore leaves a smaller table; the run that wrote the present file asked for 2017 to 2026.

Every column is found by its heading (session 495's lesson). A heading the reader needs and cannot find stops the run, and so does an (entity, variable, ts_utc) given twice or a row in two sheets.

## Shape

Series (`docs/datastandard.md`), one row per utility, state, month and measure.

- `entity`: `eia861m:<utility number>:<state>`, a utility of EIA's monthly sample in one state.
- `variable` and `unit`, for each sector `residential`, `commercial`, `industrial`, `transportation` and `total`:
  - `<sector>_sales`, MWh;
  - `<sector>_revenue`, USD (EIA's thousand dollars times 1,000);
  - `<sector>_customers`, count.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` P1M; `geo` US-<state>; `node` the utility's name.
- EIA's own fields: `x_utility_number`, `x_state`, `x_ownership`, `x_data_status` (Preliminary or Final).

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861M". The connector cites EIA's "U.S. government publications are in the public domain", record 1 of `license_reads.csv`.

## Cross-check

None in the connector. Session 511 (2025) and session 520 (every year) compared each utility-state's twelve months, summed, with the annual form's total sales in `eia861_utility_sales`: a median ratio of 1.0000 in every year the report lists, 77.3% to 85.8% of utility-states within 2%, and (session 521's summary) 11% to 18% over 10% apart. Session 521 read the gaps: a utility that also delivers energy others sell (annual parts A and C) reports in EIA-861M only what it bundles, and against part A alone those agree at a median of 1.0000; behind-the-meter owners make most of the rest, and 13 utility-states were left unexplained.

## What it does not hold

- The utilities outside EIA's monthly sample. EIA estimates them as one row a state; the connector leaves out rows whose name begins "State Adjustment", "State Total" or "US Total", none of them a utility, and since session 689 (23 October 2026) every row numbered 0, 88888 or 99999, whatever its name. The 2017 to 2021 files name the same aggregates "Adjustment <year>" (utility number 0) and "Total EPM" (88888); until session 689 the table held them, 9,360 rows of each a year (93,600 in all), and session 689's write took them out (1,145,088 rows to 1,051,488; the archive records the 93,600 keys deleted). The saved files 2017 to 2026 number every aggregate 0 or 88888; 99999 is in none of them.
- Session 689's cross-check of the rewritten table: in every month from January 2017 to July 2026, the sampled utilities of the 50 states and the District of Columbia plus EIA's adjustment rows equal EIA's own U.S. total row for total sales, revenue and customers (to the rounding of the file).
- A cell EIA leaves blank or "." has no row; nothing is filled.
- A state or national total: a sum over sampled utilities is not EIA's state total, which includes its estimate.
- The annual form's parts (bundled, energy only, delivery only): the monthly form has none, so this table cannot separate them.
