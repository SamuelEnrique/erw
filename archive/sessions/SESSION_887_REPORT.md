# Session 887 report: Canada's own record of its electricity trade with the U.S. (Canada Energy Regulator)

23 October 2026, from 04:57 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: 10 requests of 20. The CER's robots file, asked alone first; the trade page; a terms address that answered with a page saying "not found"; the terms page; open.canada.ca's robots file; one search of its catalogue; a second search that timed out and was not asked again; the workbook; then the connector's page and workbook.

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `cer_electricity_trade`, 1,136 rows. It holds Canada's electricity exports to and imports from the U.S. each month, January 2010 to July 2026 (MWh), and each province's exports to each U.S. state each year, 2010 to 2025. The source is the Canada Energy Regulator's Electricity Trade Summary workbook (updated 25 September 2026).
- **Why this source (the queue file's second session on "the U.S. and its neighbors"):** session 886 needed one request for EIA's international table, which gives Canada's trade as one number a year. The CER, which authorizes every electricity export from Canada, gives the flow by month and by province and state.
- **The cross-checks:**
  - The months summed equal the workbook's own annual sheet in 17 of 17 years, for both exports and imports.
  - The provinces summed equal the annual exports in 16 of 16 complete years.
  - EIA's international exports for Canada (session 886's table) equal the CER's to the hundredth of a TWh in every year compared except 2020 (EIA 67.42, CER 67.76). EIA takes Canada's figures from the CER.
  - Exports: 68.26 TWh in 2015, 35.64 in 2024, 31.64 in 2025. The largest flows of 2025 were Ontario to New York (7.77 TWh), Manitoba to Minnesota and North Dakota (3.46), Ontario to Michigan (3.30), British Columbia to Washington (3.11) and Quebec to Vermont (3.03).
- **The license:** the CER's terms allow reproduction for non-commercial purposes with the title, the author, and a statement that the copy is not produced with the CER's endorsement. The table's header carries that statement. Commercial redistribution needs the CER's written permission. The verdict is recorded from the saved page (read 96; the robots file is read 95): "may be public" as the ERW is today, "needs written permission" if it sells anything, the same as SPP's.

## Decisions made without you

- **The CER's own workbook and terms are used.** The same agency publishes other datasets on open.canada.ca under the Open Government Licence - Canada, but this workbook was not found there in one search. The second search timed out and was not repeated.
- **Values and prices not taken.** The workbook's export and import values and its weighted average prices are in Canadian dollars, a unit the data standard does not have. No exchange rate was applied. A `CAD` unit would be a decision of its own.
- **Province rows hold complete years only.** The workbook's 2026 province rows, January to July, are left out of the province series and named in the header; the monthly rows hold 2026.
- **The CER's market destinations are kept as it names them,** as the exporters report them: Minnesota with North Dakota (`MN_ND`), ISO New England (`ISONE`) and PJM.
- **Table flagged `public`,** like SPP's tables with the same kind of terms. Nothing is released without a person.

## For Samuel's ruling

- Whether the ERW should carry Canadian dollar values (a `CAD` unit), so that the CER's trade values and export prices can be taken.

## Files

- New:
  - `warehouse/connectors/cer_electricity_trade.py`
  - `tests/test_session887.py` (5 tests)
  - this report
- Changed:
  - `warehouse/metadata/license_reads.csv` (reads 95 and 96)
  - `license_verdicts.csv` (the CER)
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
- On the data machine only:
  - `runs/c048/s887/` (the probe and record scripts)
  - `runs/license_reads/s887/` (the pages as read)
