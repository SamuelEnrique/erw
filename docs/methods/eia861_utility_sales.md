# EIA-861: each utility's retail sales, revenue and customers by state and sector, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia861_utility_sales`

Connector: `warehouse/connectors/eia861_sales.py` (session 485, the owner's instruction of 21 October 2026; its reader rebuilt in session 495).

## Publisher and report

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the workbook `Sales_Ult_Cust_<year>.xlsx` inside each year's zip, sheets States and Territories.

- Page: `https://www.eia.gov/electricity/data/eia861/`
- File: `https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip` for the newest year, and `https://www.eia.gov/electricity/data/eia861/archive/zip/f861<year>.zip` for earlier years, as the page links them.

The connector reads the page, picks the zip of the year asked (or the newest the page links), and reads the workbook from it. Its ceiling is two requests a year (the page and the zip); a zip already saved in `warehouse/raw/eia861/` is reused.

## Vintage and revision rule

The file holds the data years 2015 to 2025 (ts_utc 2015-01-01 to 2025-01-01). A run writes one data year: by default the newest the page links, or the year given with `--year <year>`. The table is merged on (entity, variable, ts_utc) by `write_csv`: a later run replaces a row with the same key and keeps every other row from earlier runs. The header's "Years held" line names only the year of the last run (2025); the rows of the earlier years are kept beside it, each with its own `source_url` (the archive zip it came from) and `retrieved_at`.

The sheet's columns are found by their headings, not by position (session 495): 2019's sheet holds a "Short Form" column the other years do not, and 2015 and 2016 spell the balancing authority heading differently. A heading the reader needs and cannot find stops the run, and so does an (entity, variable, ts_utc) given twice.

## Shape

Series (`docs/datastandard.md`), one row per utility row of EIA's sheet, measure and year.

- `entity`: `eia861:<utility number>:<state>:<part>:<balancing authority code>`, one row of EIA's sheet: a utility in one state, one part of the form (A bundled service, B energy only, C delivery only, D bundled by a power marketer) and one balancing authority (blank when EIA gives none, so the entity ends in a colon).
- `variable` and `unit`, for each sector `residential`, `commercial`, `industrial`, `transportation` and `total`:
  - `<sector>_sales`, MWh;
  - `<sector>_revenue`, USD (EIA's thousand dollars times 1,000);
  - `<sector>_customers`, count.
- `ts_utc`: the data year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>; `node` the utility's name.
- EIA's own fields: `x_utility_number`, `x_state`, `x_part`, `x_service_type` (Bundled, Energy, Delivery), `x_ownership` (EIA's ownership class, for example Investor Owned, Cooperative, Municipal, Retail Power Marketer, Behind the Meter), `x_ba_code`, `x_data_type` (always O).

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861". The connector records EIA's sentence "U.S. government publications are in the public domain", record 1 of `license_reads.csv`.

## Cross-check

None in the connector. Session 485 set the observed rows of 2025 (parts A, B and D) against EIA's monthly state retail sales (`eia_retail_sales_monthly`): 3,912.6 TWh against 4,058.0 TWh, a median state of 97.4%. Session 495 repeated it for every year: 97% to 99% (2019 99.4%, 2025 96.9%), the gap being the imputed and withheld rows left out. Sessions 511, 520 and 521 compared `eia861m_utility_sales_monthly` with this table; session 521 found that a utility with delivery-only service (parts A and C) should be compared on part A alone, which `x_part` allows.

## What it does not hold

- Imputed rows: EIA marks each row O (observed) or I (imputed, the short-form utilities it estimates). Only observed rows are taken. Session 495 notes that 2019 holds the short-form utilities as observed rows, which later years mark imputed; that is EIA's marking, kept, and it is why 2019 has more rows (55,427) than the other years.
- EIA's two aggregates, which are not utilities: 88888 ("Withheld", the retail power marketers EIA does not name) and 99999 ("Adjustment <year>", imputed).
- A cell EIA leaves as "." has no row; nothing is filled. So the five sectors do not carry the same number of rows.
- 111 rows of two entities (`eia861:19784:WA:A:BPAT` and `eia861:40355:AZ:A:AZPS`, 2015 to 2025) have `source_url` and every `x_*` field empty, although their entity names the state, part and balancing authority. Neither the header nor the connector says how they were written; a reader who needs those fields for them reads the entity.
- A state total: a sum over utilities of observed rows falls short of EIA's state totals by the imputed and withheld rows.
