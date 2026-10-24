# Session 2440 report: a source of the session's own choosing (Canada's annual generation by class of producer, Statistics Canada 25-10-0020-01), public; Statistics Poland's BDL first, closed by its quota

24 October 2026, from 11:36 UTC to 11:43 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2440.out`). Model spend USD 0. Pulls: 7 requests of 20 (6 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **First choice, Statistics Poland's Local Data Bank (BDL), not taken.**
  - The ERW held no GUS source.
  - bdl.stat.gov.pl has no robots file: the request was answered by the bank's start page (read 780).
  - Its API names subject P1674, "Production of electricity by sources", 2000 to 2025, by voivodeship (reads 781 and 783).
  - After three API requests it answered HTTP 429, "API calls quota exceeded! Maximum admitted 1000 per 12 h." (reads 782 and 784). The quota is counted for the machine's address, not for this session, so it was spent before this session began. Waiting twelve hours is past the session's span.
- **Instead, Statistics Canada's table 25-10-0020-01, "Electric power, annual generation by class of producer".**
  - Why: the ERW holds StatCan's monthly generation by type (25-10-0015-01) and five other energy tables, but not the split between electric utilities and industrial producers. No chain has taken this table (main and chains 114's and 115's branches searched).
  - www150.statcan.gc.ca's robots file disallows paths ending in `.csv` for every agent and names no AI agent (read 785). The table's download is a `.zip`, as chain 112's connector uses.
- **A new table, `statcan_generation_class_annual`** (series, 5,937 rows, 42 series, `power`): generation in MWh by province and territory, class of producer (all, utilities and industries) and type of generation, 2005 to 2025.
  - StatCan's ".." (1,316) and "x" (10, suppressed for confidentiality) have no row and are counted in the header.
  - Its revisions ("r") are kept in `x_revised`.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set like the chain's other tables.
- **Public.** The Statistics Canada Open Licence; StatCan's verdict is on record.

## Cross-checks

- Utilities plus industries equal all classes exactly in every year, for Canada.
- Canada's total over the twelve-month sums of `statcan_electricity_generation_monthly`'s total: 0.992 to 1.023 from 2016, and 1.028 to 1.080 from 2008 to 2015. StatCan's monthly survey covered fewer producers before 2016.
- Over `owid_ember_electricity_annual`'s demand for Canada: 0.990 to 1.072. Canada is a net exporter, so generation exceeds demand in most years.
- Canada's generation, TWh: 2005 604.4, 2015 640.3, 2020 636.6, 2025 639.5.

## Requests (7 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | bdl.stat.gov.pl/robots.txt | the bank's start page |
| 2 | BDL's variables search for electricity | 200: 541 variables |
| 3 | the variables of subject P1674 | 429 |
| 4 | subject P1674 | 200: years 2000 to 2025 |
| 5 | the variables of P1674 at another page size | 429: the quota of 1,000 per 12 hours |
| 6 | www150.statcan.gc.ca/robots.txt | 200: `.csv` closed, `.zip` open |
| 7 | 25100020-eng.zip (the fetch) | 200, 100,577 bytes, last modified 16 October 2026 |

Reads recorded: 780 to 785 (on this branch). `tests/test_session205.py`'s bound was raised by 40 for this chain's reads (684 later reads against 682).

## Decisions made without you

- **Public** under StatCan's open licence.
- **A Canadian table close to U.S. markets** in place of Poland's, closed for the day by its quota.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/statcan_generation_class.py`, `tests/test_session2440.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 780 to 785), `docs/redivis/release-v1/` (the table's rows), and `tests/test_session205.py` (the bound).
- On the data machine only: `runs/c117/s2440/`, `warehouse/raw/statcan_generation_class/`, `warehouse/output/statcan_generation_class_annual.csv`.
