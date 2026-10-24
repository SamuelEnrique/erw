# Session 2477 report: Mozambique's electricity balance, 2020 to 2024 (MIREME's energy statistics report), internal

24 October 2026, from 13:20 UTC to 13:27 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2477.out`). Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no Mozambican source** (`sources.csv` and the connectors on main searched for EDM, INE, MIREME and Mozambique).
- **EDM** (www.edm.co.mz): its robots file closes `/novo/` only (read 814). A web search found its figures only in the press. The ministry's yearly report gathers EDM's and the other producers' figures.
- **The Ministry of Mineral Resources and Energy (MIREME):** mireme.gov.mz's robots file disallows nothing (read 815). Its home page states no terms (read 816). Its "Relatório Estatístico de Energia 2023 - 2024" (5th edition, 89 pages, last modified 4 February 2026) was fetched once.
- **A new table, `mireme_mozambique_electricity_annual`** (series, 107 rows, 12 entities, `power`). It is read from the report's table 3.2.2, the electricity balance in MWh, 2020 to 2024, and holds:
  - generation by source (hydro, natural gas, diesel, bagasse, solar);
  - imports, exports and primary supply;
  - own use by source;
  - losses (transport, distribution);
  - final consumption by sector (industry, residential, commerce and public services, agriculture and forest).
  - The table's figures write thousands with spaces. They are read by their position under the year headings, so a figure is never split or merged by its spaces.
  - Not written: cells marked "..." (no row), and one cell out of the form of thousands (2022's solar, printed "69 7017"), counted.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set.
- **Internal.** The report's technical sheet is headed "Copyright" and grants no reuse, and the site states no terms. No verdict is written: the report's sheet is not a read in the record. The licences' round (session 2481) can read a page of terms.

## Cross-checks

- Within the table, generation's sources sum to the total: 0.9999 to 1.000, and 0.9964 in 2022, the year whose solar figure is not written.
- Primary supply over `owid_ember_electricity_annual`'s demand for Mozambique: 0.989 to 0.997 in 2020 to 2022, 1.069 in 2023 and 1.099 in 2024.
- Generation, TWh: 18.94 in 2020, 19.63 in 2023, 19.46 in 2024. Exports, mostly Cahora Bassa's sales to South Africa, are 10.7 to 11.5 TWh a year, against imports of 7.6 to 8.2 TWh.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.edm.co.mz/robots.txt | 200: `/novo/` closed |
| 2 | mireme.gov.mz/robots.txt | 200: nothing closed |
| 3 | MIREME's home page | 200: no terms |
| 4 | the 2023-2024 statistics report (the fetch) | 200, 15.9 MB, 89 pages |

Reads recorded: 814 to 816 (on this branch). One web search found the ministry's reports; it reached no publisher's host.

## Decisions made without you

- **`internal`** under the report's "Copyright" heading.
- **The malformed 2022 solar cell left out** and counted, not guessed.
- **Quantities written positive,** the table's parentheses marking a subtraction in the balance.

## For Samuel's ruling

- **MIREME's consent,** if Mozambique's balance is wanted public.

## Files

- New: `warehouse/connectors/mireme_mozambique_electricity.py`, `tests/test_session2477.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 814 to 816).
- On the data machine only: `runs/c120/s2477/`, `warehouse/raw/mireme_mozambique_energy/`, `warehouse/output/mireme_mozambique_electricity_annual.csv`.
