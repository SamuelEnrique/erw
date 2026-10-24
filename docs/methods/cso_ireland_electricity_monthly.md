# Ireland's gross and net electricity output, a month (CSO PxStat table MSM01)

Energy Research Warehouse (ERW), method note written in session 2321 (chain 106) for a table first written on 24 October 2026 (session 2320).

Tables: `cso_ireland_electricity_monthly`

## Publisher and address

The Central Statistics Office, Ireland (CSO), PxStat table MSM01, "Electricity Output" (`https://data.cso.ie/table/MSM01`, product "Industrial Production Volume and Turnover Indices - Electricity"). It is read through PxStat's RESTful API (no key), one GET of the whole table as JSON-stat 2.0: `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/MSM01/JSON-stat/2.0/en`. Source id `cso:MSM01`. Connector: `warehouse/connectors/cso_ireland_electricity.py` (session 2320). ws.cso.ie and www.cso.ie have no robots file (HTTP 404, reads 526 and 527).

## Vintage and revision

January 1975 to August 2026, written by run `20261024T065859Z` (the write under the lock), which read the answer saved at 2026-10-24T06:48:25Z (`retrieved_at`). `vintage` is the answer's "updated", 2026-10-09T11:00:00Z, in every row. CSO's note says data for 2024 were updated by respondents on 10 September 2025. Every run that is not `--offline` asks for the table again and writes it again (`write_snapshot`).

## Shape and variables

Series, 644 rows.

- `entity`: `cso:ie`.
- `variable`: one of two series.
  - `gross_electricity_output` (`x_code` MSM01C1): January 1975 to December 2008, 408 months. CSO discontinued it from January 2009.
  - `net_electricity_output` (MSM01C2): January 2007 to August 2026, 236 months.
- `node`: the statistic as CSO names it.
- `unit`: MWh (the table's "Gigawatt Hours" times 1,000).
- `ts_utc`: the month's first day. `freq` P1M, `geo` IE.

CSO's definitions (the answer's note):
- Gross output "represents the amount of electricity that passes through the National Grid (excluding imports). It also includes electricity that is manufactured and consumed by manufacturers of electricity."
- Net output is the same, without that manufacture and use.

No value is 0 or negative. Net output, TWh a full year: 2015 26.29, 2020 29.50, 2022 32.29, 2025 29.58.

## Reading the source

- The run stops at once, asking nothing, while `cso_electricity` or the host ws.cso.ie is paused.
- One request a run, fetched fresh (timeout 60 seconds, 1 second's pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). `--offline` reads the saved answer.
- The run stops, and no file is written, for any of these:
  - an answer without the three dimensions `STATISTIC`, `TLIST(M1)` and `C02196V02652` (the State);
  - a statistic whose unit is not "Gigawatt Hours";
  - a month not of the form YYYYMM;
  - a value array not the size of the dimensions;
  - an answer with no value;
  - a statistic and month given twice.
- A cell left empty has no row. Nothing is filled.

## License

Public. `license_verdicts.csv` records the Central Statistics Office, Ireland (CSO), read 528 (session 2320): "may be public", for public and for commercial use. The sentence is in CSO's Copyright and Re-use Policy: "Statistical information on this website is accessible free of charge and licensed under Creative Commons Attribution (CC BY 4.0)." The CSO logo may not be used for commercial purposes. The header names the source.

## Cross-checks (session 2320, full years 2016 to 2025)

- Net output over `eurostat_electricity_monthly`'s net production TOTAL for Ireland: 0.967 to 1.006.
- Over `owid_ember_electricity_annual`'s demand: 0.959 in 2016, falling to 0.786 in 2025. Net output excludes imports, and the gap widens as demand outgrows the island's own output.

## What it does not hold

- Output by source; imports and exports; Northern Ireland (the State only); EirGrid's own data (written permission, chain 099).
