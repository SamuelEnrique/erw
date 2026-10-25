# Session 2642 report: Anguilla's electricity generation a month, 1995 to 2025 (the Anguilla Statistics Department's Table 2.4.2-1, ANGLEC's figures), internal, a source of the session's own choosing

25 October 2026, about 08:05 to 08:12 UTC, on lab-desktop (the data machine), chain 131, unattended. Run before session 2641. Precheck passed (`runs/c131/pre2642.out`). Model spend USD 0. Pulls: 3 requests of 20 (2 by the probe, 1 fetch the connector reads offline).

## Why this source

- **The ERW held Anguilla in no table,** EIA's world table included, and no chain or queue file had taken it (the record, the queue and the unlanded chains' branches searched). Its statistics office publishes the utility's monthly generation since 1995.

## Read these first

- **The host:** statistics.gov.ai has no robots file (HTTP 404, read 1294). Its Energy page (read 1295) links the Energy Statistics workbook (published 26 May 2026, last modified 8 June 2026), fetched once.
- **The terms** (read 1295): the page's footer reads, after a copyright sign and 2026, "Anguilla Statistics Department, GOA . All rights reserved.", with no terms of reuse linked. **Verdict: needs written permission** (ZIMSTAT's precedent). The table is **internal**.
- **A new table, `statai_anguilla_electricity_monthly`** (series, 372 rows, 1 entity, `power`): Table 2.4.2-1, ANGLEC's electricity generation each month of 1995 to 2025, in MWh (the table's kWh divided by 1,000).
  - 23,205.5 MWh in 1995 and 110,181.8 MWh in 2025. Each year's months add to its Total within 1 kWh.
  - Written by run `20261025T080827Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T080831Z-local`), held from the live set and from Redivis (internal).
  - **Its method note** (`docs/methods/statai_anguilla_electricity_monthly.md`) is written in this session, as the chain's notes session (2639) ran before the table existed; it was checked against the table and given its Method cell.
- **Two oddities, kept as printed or left out:**
  - **2026 left out:** its three months are not a whole year, and February's and March's figures repeat 2025's exactly (the table's % change 0), so they cannot be told from placeholders.
  - **January 2022 and January 2023** carry the same figure, 8,363,036 kWh; both are written as printed.
- **Not taken:** the annual % change; the workbook's other sheets (revenue in XCD, petroleum imports; one sheet's years do not match its title in the contents list).

## Cross-checks

- EIA's world table holds no Anguilla. Within the workbook, each year's Total equals its months.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | statistics.gov.ai's robots file | 404 |
| 2 | the Energy page | 200 |
| 3 | the Energy Statistics workbook (the fetch) | 200, 80.0 kB |

Reads recorded: 1294 and 1295.

## Decisions made without you

- **Anguilla as the own choice.**
- **Whole years only; 2026's repeated months left out.**
- **Internal** under the Department's copyright line.

## For Samuel's ruling

- **Whether to ask the Department** whether 2026's February and March figures are placeholders, and for permission to publish the table.

## Files

- New: `warehouse/connectors/statai_anguilla_electricity.py`, `tests/test_session2642.py`, `docs/methods/statai_anguilla_electricity_monthly.md`, this report.
- Changed: the registration; the metadata files and `docs/coverage.md` (its Method cell); the license record (reads 1294 and 1295, the Department's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c131/s2642/`, `runs/license_reads/s2642/`, `warehouse/raw/statai_ai/`, `warehouse/output/statai_anguilla_electricity_monthly.csv`.
