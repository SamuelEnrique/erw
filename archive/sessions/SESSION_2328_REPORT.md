# Session 2328 report: Canada's electricity trade with the U.S. and between provinces (Statistics Canada, table 25-10-0016-01), the session's own choice

24 October 2026, from 07:20 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Precheck passed (`runs/c108/pre2328.out`). Model spend USD 0. Pulls: 5 of 20 (below).

## Read these first

- **Two sources tried first and left:**
  - **New Zealand's MBIE:** its robots file allows the reader (read 531), but its electricity statistics page answers with an Incapsula challenge (read 532), which is not answered. Not asked again.
  - **Chile's INE:** it has no robots file (a 404 page under status 200, read 533). Its data pages are not known without guessing addresses, so nothing more was asked.
- **One public table, the session's choice:** `statcan_electricity_trade_monthly`, from Statistics Canada's table 25-10-0016-01 (the Monthly Electricity Supply and Disposition Survey). It is written, validated, archived, in coverage (sector power), and held from the live set and the release. 25,215 rows, January 2008 to July 2026:
  - for Canada and each province and territory, a month's generation, receipts from other provinces and from the United States, deliveries to other provinces and to the United States (firm, non-firm and other), and the electricity available for use;
  - in MWh, as StatCan publishes them.
  - 12,503 cells StatCan marks ".." (not available) have no row.
- **Why this one:** the ERW holds StatCan's generation table (25-10-0015-01, chain 097) but not its trade table. Canada's sales to and purchases from the U.S. grids (New England, New York, the Midwest and the Pacific Northwest) bear directly on U.S. markets.
- **License:** Statistics Canada's Open Licence, already on record (public). The robots file asks a crawl delay of 2 seconds (kept) and names no AI agent (read 534).

## The cross-check (`runs/c108/s2328/cross.py`, `cross.out`)

- **StatCan's identities, in every area and month where all parts are given:**
  - Receipts equal receipts from other provinces plus the two U.S. receipts (239 area-months, no gap).
  - Deliveries equal deliveries to other provinces plus to the U.S. (1,846, no gap).
  - Deliveries equal firm plus non-firm plus other in 314 of 315 area-months; Canada in February 2013 differs by 125,051 MWh.
  - Availability equals generation plus receipts minus deliveries in 2,388 of 2,390; British Columbia in February 2019, and Canada with it, differ by 70,931 MWh.
  - Both gaps are StatCan's as published, recorded, not adjusted.
- **Against `statcan_electricity_generation_monthly`:** Canada's total generation is the same in all 223 months.
- **Against `eia_international_electricity_annual` (the U.S.):**
  - Canada's deliveries to the U.S. are 2.5 to 8.1 TWh a year above EIA's U.S. imports (2024: 35.78 against 33.25 TWh; 2017: 72.04 against 65.68).
  - Canada's purchased receipts from the U.S. are 0.6 to 6.7 TWh from EIA's U.S. exports (2024: 23.28 against 19.44 TWh).
  - The two agencies measure at different points and in different ways; recorded, not reconciled.
  - The fall in deliveries to the U.S., from 65.4 TWh (2022) to 35.8 TWh (2024), and the rise in purchases from it (14.1 to 23.3 TWh) match the drought years of Quebec's and British Columbia's hydro.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.mbie.govt.nz | 2 | robots, the statistics page (a challenge) |
| www.ine.gob.cl | 1 | robots (none) |
| www150.statcan.gc.ca | 2 | robots, the table's zip (267 kB); 2 s or more apart |

## Errors

- **A first cross-check summed StatCan's several "total" generation types;** the comparison now takes the total of all types alone.

## Decisions made without you

- **StatCan's table chosen** after MBIE's challenge and INE Chile's unknown addresses.
- **Every component kept,** with StatCan's totals marked `x_total`, as the generation table does.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/statcan_electricity_trade.py`
  - `tests/test_session2328.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (531 to 534), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2328/`, `runs/license_reads/s2328/`, `runs/s2328*`.
