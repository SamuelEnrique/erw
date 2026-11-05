# Session 2502 report: the Faroe Islands' electricity production by source, 1990 to 2025, and sales by consumer group, 1997 to 2025 (Statistics Faroe Islands), the third own choice, public

24 October 2026, from about 15:19 UTC to 15:24 UTC for the reads and the connector; the table written under the data lock at 16:30 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2502.out`). Model spend USD 0. Pulls: 14 requests of 20 (11 by the probe, 3 by the connector's queries).

## Read these first

- **First choice not reachable:** IT.NRW's electricity fed in by source for North Rhine-Westphalia (Germany's largest industrial state, an open-licensed table on the state's portal). ckan.open.nrw reset the connection at its robots file (read 856); nothing more was asked.
- **Why the Faroe Islands:** a grid the ERW did not hold, published under CC BY 4.0 through a PxWeb API.
- **Statistics Faroe Islands (Hagstova Føroya):** statbank.hagstova.fo answers HTTP 404 for a robots file (read 858); hagstova.fo's closes system paths only (read 857). The API's listings (reads 859 to 862) lead to two tables of SEV's figures (SEV is the islands' public power company): UO03020, production by hydro, wind, thermal, solar, biogas and tidal, 1990 to 2025; UO03030, sales by consumer group, 1997 to 2025 (reads 863, 864).
- **A new table, `hagstova_faroe_electricity_annual`** (series, 421 rows, 16 entities, `power`): `generation` by source and `sales` by consumer group, in MWh as given.
  - Written by run `20261024T163010Z`, validated (0 errors, 0 warnings), archived, held from the live set. Public: its rows are added to the release package, and it goes in the next Stanford draft.
- **Public.** The terms of use (read 866): "Statistical data, tables, texts, charts and infographics from Statistics Faroe Islands are available under Creative Commons Attribution 4.0 International (CC BY 4.0), unless otherwise stated", the statbank and its API included, commercial use included, with Statistics Faroe Islands credited. Verdict: may be public. The header carries the credit.

## Cross-checks

- The sources sum to the total each year (2025: 506,249 MWh).
- Production over `owid_ember_electricity_annual`'s demand for the Faroe Islands: 0.96 to 1.04 (2000 to 2021), 0.90 in 2022 and 0.93 in 2023.
- Produced, GWh: 211.0 in 1990, 280.4 in 2010, 406.8 in 2020, 506.2 in 2025; wind 147.5 GWh in 2025. Sales to fisheries and aquaculture grew from 25.9 GWh in 2010 to 133.8 GWh in 2025.

## Requests (14 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | ckan.open.nrw/robots.txt | the connection was reset |
| 2 | hagstova.fo/robots.txt | 200: system paths closed |
| 3 | statbank.hagstova.fo/robots.txt | 404 |
| 4 to 7 | the API's listings down to the energy tables | 200 |
| 8, 9 | the two tables' metadata | 200 |
| 10 | hagstova.fo/en | 200: the terms of use linked |
| 11 | the terms of use | 200 |
| 12 | UO03020 by POST, an empty query | 200: the total only |
| 13, 14 | UO03020 and UO03030 by POST, every category selected | 200 |

Reads recorded: 856 to 866 (on this branch). Four web searches (Statistik Austria, INE Portugal, Macao, Hagstova's terms) reached no publisher's host.

## Errors

- **The first query was empty,** as Statistics Iceland's connector sends it; this statbank then eliminates the category dimension and returns the total only. The connector selects every category and year; one request was spent.

## Decisions made without you

- **The Faroe Islands as the third own choice,** after North Rhine-Westphalia's host reset the connection.
- **`vintage` left empty:** the answers' `updated` field reads 2000-01-01, a placeholder; the statbank's listing gives 3 June 2026.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/hagstova_faroe_electricity.py`, `tests/test_session2502.py`, this report.
- Changed: the registration; the metadata files; `docs/redivis/release-v1/` (the table's rows); the license record (reads 856 to 866, one verdict).
- On the data machine only: `runs/c121/s2502/`, `warehouse/raw/hagstova_faroe_energy/`, `warehouse/output/hagstova_faroe_electricity_annual.csv`.
