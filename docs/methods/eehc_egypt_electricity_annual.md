# Egypt's installed capacity, peak load and generation by type, a fiscal year (EEHC's annual reports)

Energy Research Warehouse (ERW), method note written in session 2443 (chain 117) for a table first written on 24 October 2026 (session 2435).

Tables: `eehc_egypt_electricity_annual`

## Publisher and address

The Egyptian Electricity Holding Company (EEHC), the table "Electricity in <year>" near the start of each annual report. Four reports (PDF, no key), each giving its fiscal year and the one before:

| Report | Fiscal years | Address |
|---|---|---|
| 2015/2016 | 2014/2015, 2015/2016 | `http://www.moee.gov.eg/english_new/EEHC_Rep/2015-2016en.pdf` |
| 2017/2018 | 2016/2017, 2017/2018 | `http://www.moee.gov.eg/english_new/EEHC_Rep/2017-2018en.pdf` |
| 2020/2021 | 2019/2020, 2020/2021 | `http://www.moee.gov.eg/english_new/EEHC_Rep/REP2021-2022en.pdf` (the file's name notwithstanding) |
| 2023/2024 | 2022/2023, 2023/2024 | `https://www.eehc.gov.eg/CMSEehc/Files/AnnualReport2024En.pdf` |

Source id `eehc:annual_report`. Connector: `warehouse/connectors/eehc_egypt_electricity.py` (session 2435). www.eehc.gov.eg has no robots file (HTTP 404, read 707). www.moee.gov.eg, the ministry's host of the earlier reports, closes two pages only (read 710).

## Vintage and revision

Written by run `20261024T112507Z` (the write under the lock, offline). It read the four reports saved from 11:15 to 11:23 UTC on 24 October 2026 (`retrieved_at`, a report each). `vintage` is each report's last-modified time. A report is never asked again unless it is missing from the raw files: a past report does not change.

## Shape and variables

Series, 105 rows, ten entities, eight fiscal years: 2014/15 to 2017/18, 2019/20, 2020/21, 2022/23 and 2023/24.

- `entity`: `eehc:eg:<kind>`, the kinds below; `eehc:eg` for the peak load.
  - total, hydro, thermal (EEHC's affiliated companies and its own plants), renewable (wind and solar);
  - private_boot (the BOOT plants), ipp_purchased (energy bought from IPPs), isolated (isolated, unconnected and reserve plants);
  - fast_track (the 2015/2016 fast track plan's capacity), industrial_surplus (2022/23 and 2023/24 only).
- `variable`: `capacity` (installed, MW), `generation` (MWh, the report's GWh times 1,000), `peak_load` (MW).
- `ts_utc`: the fiscal year's first day (1 July). `x_fiscal_year` keeps EEHC's label (for example `2023/2024`). `freq` P1Y; `geo` EG.
- `node`: the report's label of the line. `x_report` the report's file.

No value is 0 or negative. Totals and parts are EEHC's: a sum takes one level. The kinds sum to the total within 0.1 TWh (2023/24: 229.37 TWh of parts against 229.28 TWh).

| | 2014/15 | 2017/18 | 2020/21 | 2023/24 |
|---|---|---|---|---|
| Installed capacity, MW | 35,220 | 55,213 | 58,818 | 59,694 |
| Peak load, MW | 28,015 | 30,800 | 31,900 | 36,800 |
| Generation, TWh | 174.9 | 196.8 | 204.8 | 229.3 |

## Reading the source

- The run stops at once, asking nothing, while `eehc_electricity`, www.eehc.gov.eg or www.moee.gov.eg is paused.
- At most four requests a run, one a report (timeout 180 seconds); `--offline` reads the saved reports only.
- The table is read from its line "Description <year> <year>" to the line of total fuel consumption.
  - A line is taken by its label (`LINES`), then its unit, MW or GWh (a footnote mark may stand before it), then its two figures.
  - A dash has no row.
  - A label whose figures stand on the next line (the 2017/2018 report's total capacity) is joined to it.
- The 2015/2016 report prints the peak load's unit as GWh; its figures (28,015 and 29,200) are megawatts, as every other report gives them, and are written as MW.
- The run stops, and no file is written, for any of these:
  - a report without its table;
  - a table without one of the lines expected of it (`REPORTS`);
  - a figure that is not a number;
  - a fiscal year and line given twice with different figures.

## License

Internal. `license_verdicts.csv` records the Egyptian Electricity Holding Company (EEHC), read 708 (session 2439): "needs written permission", sold or not. EEHC's site carries "All Rights Reserved ©2022" and grants no reuse. The table is held from the Redivis storage and the live set until EEHC consents.

## Cross-checks (session 2435)

- Total generation by fiscal year over the mean of `owid_ember_electricity_annual`'s demand for Egypt in its two calendar years: 0.993 to 1.010.

## What it does not hold

- Fiscal years 2018/2019 and 2021/2022: their reports were not found.
- EEHC's 2022/2023 and 2024/2025 reports: scanned images without text, fetched but not read.
- Fuel use, transmission and distribution, customers, prices (EGP).
