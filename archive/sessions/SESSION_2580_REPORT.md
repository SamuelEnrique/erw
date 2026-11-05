# Session 2580 report: Hawaii's electricity by island, and Hawaiian Electric on Oahu since 1994 (DBEDT's State of Hawaii Data Book 2025), internal, a source of the session's own choosing

25 October 2026, about 02:37 to 02:44 UTC, on lab-desktop (the data machine), chain 127, unattended. Precheck passed (`runs/c127/pre2580.out`). Model spend USD 0. Pulls: 8 requests of 20 (7 by the probe, 1 by the fetch the connector reads offline).

## Why this source

- **US first, and a gap:** the ERW held Hawaii only as a state in EIA's tables. DBEDT's Data Book splits it by island (Oahu, Hawaii, Maui, Kauai, Lanai, Molokai), gives the utilities' customers and sales by island, and Hawaiian Electric's service on Oahu since 1994. No chain had taken DBEDT, and none of its hosts is closed (`license_verdicts.csv`, `license_reads.csv`, the retired tables and the queue files read first).

## Read these first

- **The hosts:** files.hawaii.gov has no robots file (read 1123); dbedt.hawaii.gov's sets no rule and asks a crawl delay of 10 seconds (read 1124), kept with a wait in each command (its requests 19 to 22 seconds apart). The Data Book 2024's page answers 404 (read 1125); the Data Book's page (read 1126) links the 2025 edition, whose page (read 1127) links section 17 as one workbook.
- **The terms:** DBEDT's pages read "Copyright (c) 2026, State of Hawaii. All rights reserved." (read 1127); the State's Terms of Use page on portal.ehawaii.gov (no robots file, read 1128) is drawn by script, with no terms in its bytes (read 1129). **Verdict: needs written permission** (ZIMSTAT's precedent). The table is **internal**. Its table 17.07 rests on EIA's Form EIA-923, which the ERW holds under EIA's own terms.
- **The source:** the State of Hawaii Data Book 2025, section 17 (one workbook, 217.6 kB, last modified 30 September 2026), tables 17.07 (electricity production by source and island, 2024, million kWh), 17.10 (electric utilities by island, 2025: customers and sales) and 17.13 (Hawaiian Electric's service on Oahu, 1994 to 2025).
- **A new table, `dbedt_hawaii_electricity_annual`** (series, 268 rows, 88 entities, `power`): 2024 generation 9,160.9 GWh for the state (petroleum 7,054.0, solar 704.9, wind 663.3; Oahu 6,513.7); 2025 sales 2,561 GWh residential and 6,355 GWh other use; Hawaiian Electric's sales on Oahu 6,797 GWh in 1994 and 6,258 GWh in 2025, its generating capability 1,516 MW. Each island's sources checked against its total and the islands against the state within 0.5 million kWh; the utilities' islands against the state total. Written by run `20261025T024218Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T024223Z-local`), held from the live set and from Redivis (internal). The trial ran from the main checkout under the data lock.
- **Not taken:** 17.10's and 17.13's rates and revenues (USD) and average use per customer; the section's other tables (fuel, gas utilities, research).

## Cross-checks

- Against `eia_state_source_disposition_annual`'s Hawaii for 2024, read past its header lines: EIA's total net generation 9,160,979 MWh, DBEDT's 9,160.9 GWh; EIA's sales of full-service providers 8,881.8 GWh for 2024 against DBEDT's 8,916 GWh for 2025.

## Requests (8 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | files.hawaii.gov's and dbedt.hawaii.gov's robots files | 404, 200 |
| 3 to 5 | the Data Book 2024 page, the Data Book's page, the 2025 page | 404, 200, 200 |
| 6, 7 | portal.ehawaii.gov's robots file and Terms of Use page | 404, 200 (script) |
| 8 | section 17's workbook (the fetch) | 200, 217.6 kB |

Reads recorded: 1123 to 1129.

## Decisions made without you

- **Hawaii as the own choice,** US first.
- **Quantities only** (customers, MWh, MW), no rates or revenues.
- **Internal** under the State's copyright line.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/dbedt_hawaii_electricity.py`, `tests/test_session2580.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1123 to 1129, DBEDT's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c127/s2580/`, `warehouse/raw/dbedt_hi/`, `warehouse/output/dbedt_hawaii_electricity_annual.csv`.
