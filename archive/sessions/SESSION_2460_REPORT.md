# Session 2460 report: Statistics Canada's annual supply and disposition of electricity by province, 2005 to 2025 (the third own choice)

24 October 2026, from 13:05 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. It ran before sessions 2456 to 2459, so that the daily run's lock (from about 14:10 UTC) would not hold up its write and the Stanford draft. Precheck passed (`runs/c118/pre2460.out`). Model spend USD 0. Pulls: 2 of 20 (below).

## Read these first

- **The record read first** (session 2455's lesson): Statistics Canada's verdict is public (the Open Licence, read 361), and nothing of StatCan's is in `warehouse/output/retired/`.
- **The choice:** table 25-10-0021-01, electric power, electric utilities and industry, annual supply and disposition. The ERW holds StatCan's monthly generation and trade and, since chain 114, its capacity. It does not hold sales to ultimate customers by sector, producers' own use, unallocated electricity or interprovincial flows.
- **One public table:** `statcan_electricity_disposition_annual`, 3,909 rows, 14 areas (Canada and the provinces and territories), 2005 to 2025. It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables:
  - generation, trade with the United States and its parts, interprovincial receipts and deliveries, electricity available, producers' use, sales to ultimate customers in four sectors, and unallocated electricity;
  - in MWh.
  - StatCan's values in Canadian dollars (2,153 rows) are not taken, a currency other than USD being the owner's question.
  - 867 figures marked .. have no row.
- **The checks:**
  - the four sales sectors add to total sales within 1 MWh in all 294 area years (the run stops otherwise);
  - supply (generation, imports, exports, receipts, deliveries) does not equal the electricity available in 6 of 294 area years;
  - use (producers', sales, unallocated) does not equal it in 107. Both are counted in the header and kept as published.
- **License: public** (the Statistics Canada Open Licence). The robots file is unchanged since session 2418 (read 804).
- **Test 205's bound raised by 40 again,** for this chain's reads, which reach 805 on this branch.

## The cross-check (`runs/c118/s2460/cross.py`, `cross.out`; tables read past their header lines)

- **Canada's annual generation against the year's sum of `statcan_electricity_generation_monthly`:**
  - within 0.8 per cent from 2016 to 2022 (2017: 649.5 against 649.4 TWh);
  - 2.8 to 8.0 per cent above from 2008 to 2015;
  - 1.3 to 2.3 per cent above from 2023 to 2025.
  - The monthly survey's coverage differs from the annual's; StatCan's notes were not read here (session 2457's note will).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www150.statcan.gc.ca | 2 of 20 | robots, the table's zip (105,168 bytes); 2 s or more apart |

## Errors

- **The test's sales check first used a 1 MWh change,** within the tolerance. It now uses 5.

## Decisions made without you

- **StatCan's supply and disposition** as the third own choice, the record read first.
- **The values in Canadian dollars left out.**

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/statcan_electricity_disposition.py`
  - `tests/test_session2460.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (804 and 805), `license_tables.csv`, `docs/licenses.md`
  - `tests/test_session205.py` (the bound)
  - the coverage, sources and archive manifest files, and the release lists
- On the data machine only: `runs/c118/s2460/`, `runs/license_reads/s2460/`.
