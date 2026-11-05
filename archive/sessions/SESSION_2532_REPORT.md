# Session 2532 report: the next file first; Madagascar's electricity a month (INSTAT's Tableau de Bord de l'Economie no. 63, JIRAMA's figures), internal

24 October 2026, from about 20:33 UTC (chain 124's start) to 20:45 UTC, on lab-desktop (the data machine), the first session of `queue/done/124-day-24-november-data-madagascar-cameroon-benin-togo.md`, unattended. Precheck passed (`runs/c124/pre2532.out`). Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Chain 124 was taken at 20:33 UTC** by the agent that finished chain 123's landing (`5a7657e3`; session 2531's report), under the owner's instruction for this run.
- **The next file first:** `queue/next/125-day-25-november-data-malta-bosnia-nicaragua-brunei.md`, sessions 2546 to 2559, machine data, written by `runs/c124/write_125.py` from file 124 (its rules word for word), committed alone in the queue worktree and pushed to main as `8f4f6b73` between two snapshots (`q125-before`, `q125-after`: 25 pages, all 200, 0 differences). Number 125 and sessions 2546 to 2559 were free on main and on every branch. Its sources: Malta, Bosnia and Herzegovina, Nicaragua and Brunei; none is in `sources.csv`, the connectors or the queue on main or on the running chains' branches, except in Eurostat's international tables (Malta, Bosnia and Herzegovina).
- **The ERW held no Malagasy source** (`sources.csv`, the connectors and the queue searched for Madagascar, INSTAT and JIRAMA): only EIA's and OWID's international tables name it.
- **The hosts:** www.instat.mg's robots file allows every path, with a crawl delay of 3 seconds, which was kept (read 971); www.jirama.mg's closes `/wp-admin/` only (read 972). Neither names an AI agent.
- **INSTAT's terms:** its home page states "Copyright INSTAT 2026. Tous les droits sont reserves" and links no terms of reuse (its "Terms & Use" link is commented out of the page) (read 973). The table is **internal** until a ruling; session 2537's round reads INSTAT first.
- **The source:** INSTAT's Energie et Hydrocarbures page (read 974) lists the Tableau de Bord de l'Economie (TBE); TBE no. 63 (August 2026) links a data workbook beside its PDF (read 975). The workbook (0.67 MB, last modified 25 August 2026) was fetched once. Its sheet `SortieElec`, table 21, "Evolution mensuelle des production et consommation d'electricite" (source: JIRAMA), gives 24 months, July 2024 to June 2026.
- **A new table, `instat_madagascar_electricity_monthly`** (series, 168 rows, 6 entities, `power`): JIRAMA's production (total, hydro, thermal) and consumption (total, households, industry and services, street lighting) a month, in MWh as given. In 2025: production 2.013 TWh (hydro 0.971, thermal 1.042), consumption 1.434 TWh.
  - Each month's total equals its parts within 1 MWh, checked by the connector on every row.
  - The average price (Ar/kWh) is not taken (a price in another currency); nor are the half-year totals.
  - Written by run `20261024T204203Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T204208Z-local`), held from the live set and from Redivis (internal).

## Cross-checks

- Against `eia_world_electricity_annual`'s Madagascar for 2024: JIRAMA's hydro from July 2024 to June 2025 is 0.877 TWh against EIA's 0.900 TWh; JIRAMA's total production over the same twelve months, 1.964 TWh, is 81% of EIA's national 2.421 TWh, which also counts self-producers and grids outside JIRAMA's. `owid_ember_electricity_annual` holds only Madagascar's demand (2.43 TWh in 2024) and emissions, not its generation. JIRAMA's consumption (sales) is 71% of its production in 2025, the gap its network's losses.
- No row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` or `docs/coverage.md`.

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.instat.mg and www.jirama.mg robots files | 200, 200 |
| 3 | INSTAT's home page | 200 |
| 4 | INSTAT's Energie et Hydrocarbures page | 200 |
| 5 | TBE no. 63's page | 200 |
| 6 | TBE no. 63's data workbook (the fetch) | 200, 0.67 MB |

Reads recorded: 971 to 975 (on this branch, after chain 123's 930 to 970). Test 205's bound was raised by 40 for chain 124's reads. Two web searches found INSTAT's TBE series; they reached no publisher's host.

## Decisions made without you

- **INSTAT's TBE workbook rather than JIRAMA's site:** INSTAT republishes JIRAMA's monthly figures as a table; JIRAMA's site was not searched further.
- **Internal** under INSTAT's "all rights reserved", until a ruling.
- **One workbook, 24 months:** earlier TBEs at other addresses would reach further back; not asked within this session's ceiling.

## For Samuel's ruling

- None new (INSTAT's terms go to session 2537's round).

## Files

- New: `warehouse/connectors/instat_madagascar_electricity.py`, `tests/test_session2532.py`, this report; `queue/next/125-...md` (on main).
- Changed: the registration (`build_coverage.py`, `release_v1.py`, `live_set.yaml`); the metadata files; the license record (reads 971 to 975) and `docs/licenses.md`; `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c124/s2532/`, `runs/c124/write_125.py`, `warehouse/raw/instat_mg_tbe/`, `warehouse/output/instat_madagascar_electricity_monthly.csv`.
