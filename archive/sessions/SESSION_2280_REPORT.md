# Session 2280 report: the next file, and Portugal's electricity balance a year (REN's Data Hub)

24 October 2026, from 04:37 UTC, on lab-desktop (the data machine), the first session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: 9 requests of 15 (below).

## Read these first

- **Chain 104 taken** at 04:36 UTC by chain 059's agent when chain 101 landed (f6b4cede). The owner's instruction for that run is to run the file the queue step prints. Chain 103, whose continuation this file is, still runs beside it under another agent, who was told; chain 102 runs too. Chain 103's agent sent its hosts, which are added to this chain's list: www.statssa.gov.za (a bot challenge), www.coordinador.cl's generation pages (HTTP 403), data.un.org's old DownloadHandler (gone), and XM (its terms).
- **The next file first,** pushed to main on its own before any other work (c446038c, with snapshots): `queue/next/105-day-8-november-data-mexico-india-peru-korea.md`, sessions 2294 to 2307, machine: data. Its sources: Mexico (CENACE), India (Grid-India), Peru (COES) and South Korea (KPX), away from chains 102 to 104's.
- **REN's terms:** datahub.ren.pt has no robots file (read 431). None of the Data Hub's pages read state terms of reuse: the monthly balance, API instructions, About and Hyperlinks pages (reads 432 to 435). The About page presents the numbers "to the scientific community, journalists and all interested parties". **So the table is `internal`** until a ruling, under the chain's rule for a license not settled, and no verdict is recorded.
- **One table written, validated, archived, in coverage (sector power), held from the live set** (internal, so not in the release package): `ren_portugal_balance_annual`, 2020 to 2025, 146 rows.
  - REN's monthly balance rows: production by source (hydro, wind, solar, waves, biomass and its parts, coal, natural gas and its parts, other thermal), storage, the commercial exchanges and consumption.
  - Each a year, in MWh (REN's GWh times 1,000).
  - **Why a year, not a month:** the Data Hub's CSV export answers one month whatever range is asked (2020 to 2026 gave January 2020). A month's file also carries the year-to-date and last year's, so December of 2021, 2023 and 2025 give the six years in three requests. 81 months would not fit the ceiling.
- **The cross-check** (`runs/c104/s2280/cross.py`, `cross.out`):
  - **REN's balance closes within REN's rounding:** every parent equals its children within 1 GWh, and production less storage use plus net imports equals consumption within 1 GWh. Net imports differ from commercial imports less exports by up to 25 GWh (2024), physical against commercial.
  - **Against Ember:** REN's consumption is 0.877 to 0.924 of Ember's Portuguese demand (2025: 53.036 against 60.44 TWh), falling each year. What Ember counts that REN's grid balance does not is not tested here.
  - Renewables made 58.3% of production in 2020 and 75.5% in 2025 (80.4% in 2024).

## The pulls

1. datahub.ren.pt/robots.txt (read 431): HTTP 404.
2. The monthly balance page (read 432).
3. The API instructions (read 433).
4. and 5. The About and Hyperlinks pages (reads 434, 435).
6. The export for 2020 to 2026: answered with January 2020 only.
7. to 9. The exports of December 2021, 2023 and 2025. They were seeded into the raw store, and the trial and the write read them offline.

## Errors

- **One request spent learning that the export ignores the range** (pull 6).

## Decisions made without you

- **A year from December's year-to-date** in place of a month, within the ceiling.
- **`internal`,** since the Data Hub states no terms.

## For Samuel's ruling

- **REN's Data Hub:** public or internal? Its pages state no terms of reuse. Undone: the table stays internal.

## Files

- New: `warehouse/connectors/ren_balance.py`, `tests/test_session2280.py`, this report; on main, `queue/next/105-day-8-november-data-mexico-india-peru-korea.md`.
- Changed:
  - `tests/test_session205.py` (its bound, +20)
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (431 to 435)
  - the coverage, sources, archive manifest and license files
- On the data machine only: `runs/c104/`, `runs/license_reads/s2280/`, `runs/s2280_*`, `warehouse/raw/ren_balance/`.
