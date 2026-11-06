# Session 2742 report: the UK's installed capacity by connection, 2011 to 2025 (DESNZ's DUKES 5.12), public, a source of the session's own choosing

25 October 2026, about 20:53 to 20:58 UTC, on lab-desktop (the data machine), chain 138, unattended. Precheck passed (`runs/c138/pre2742.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **This chain's four planned territories gave no table** (Puerto Rico, the US Virgin Islands, American Samoa, the Northern Mariana Islands).
- **The ERW held no split of the UK's capacity between transmission and distribution.** DUKES 5.12 gives it by fuel, the companion of chains 136 and 137's DUKES tables, from the same chapter, host and licence.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1478). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_capacity_by_connection_annual`** (series, 1,245 rows, 83 entities, `power`), 2011 to 2025:
  - Entity `desnz_conn:<gb|ni|uk>:<transmission|distribution|all>:<fuel>`; the UK table alone has `all`.
  - Variable `installed_capacity`, MW, at 31 December (DESNZ's note 2). This is installed capacity, not the de-rated capacity of `desnz_uk_derated_capacity_annual` (note 1).
  - The UK table's wave and tidal row has no network label; it carries "All" from the row above.
- **Figures:**
  - The UK's transmission-connected capacity fell from 80,890 MW in 2011 to 68,667 in 2025, while distribution-connected capacity rose from 15,041 to 42,437 MW.
  - Distribution held 21,331 of the UK's 21,915 MW of solar in 2025.
  - The total rose from 95,931 to 111,103 MW.
- **Checks, all passing,** within 0.5 MW:
  - each area's and network's fuels add to its total;
  - Great Britain and Northern Ireland add to the UK, network by network and fuel by fuel;
  - the UK's transmission and distribution add to its all.
- **Its record:** written by run `20261025T205604Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T205608Z-local`), held from the live set, and in the release package (public). The patch applied cleanly.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1, the end of 2025), the UK's installed capacity, MW:

| | DUKES 5.12 (here) | Energy Trends 6.1 |
|---|---|---|
| Solar | 21,914.94 | 21,914.97 |
| Onshore wind | 16,430.23 | 16,430.69 |
| Offshore wind | 16,649.88 | 16,649.68 |

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.12.xlsx (the fetch) | 200 |

Read recorded: 1478.

## Decisions made without you

- **DUKES 5.12 as the own choice; public.**
- **A blank network label read as the row above's,** the one blank in the sheet.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_connection.py`, `tests/test_session2742.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1478) and `docs/licenses.md`.
- On the data machine only: `runs/c138/s2742/`, `runs/license_reads/s2742/`, `warehouse/raw/desnz_dukes/s2742probe1/`, `warehouse/output/desnz_uk_capacity_by_connection_annual.csv`.
