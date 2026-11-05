# Session 2776 report: Luxembourg's electricity imports and exports by country a year from 1933 (STATEC's LUSTAT), the third own choice

26 October 2026, about 00:16 to 00:22 UTC, on lab-desktop (the data machine), chain 140, unattended. Run before session 2773, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c140/pre2776.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch).

## Read these first

- **Why this source:** the companion of session 2771's DF_A4203. The same publisher and verdict (STATEC, CC0 1.0), and a cheap one to take: Luxembourg imports most of its electricity, so its trade by country is half of its balance.
- **`statec_lu_electricity_trade_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statec_electricity_trade.py`, 584 rows, 10 entities, 1933 to 2024):
  - From LUSTAT dataflow DF_A4208, "Electricity imports and exports by country", every key in one request (CSV with labels). The GWh rows only.
  - Imports (l01) from Belgium, France and Germany, Germany's split into the Société électrique de l'Our (SEO) and others; exports (l02) to Belgium, France and Germany's RWE grid. Variables `electricity_imports` and `electricity_exports`, in MWh.
  - Imports and exports: 4,665,464 and 754,921 MWh in 1990; 6,571,238 and 1,321,776 in 2024. 336 observations not available have no row.
  - **Checked every year:** imports equal their three countries and exports theirs, within 0.5 GWh (a miss stops the run). Germany's split differs in 1963 (623.6 GWh) and 1969 (45.0 GWh); these are counted and kept as published.
- **Cross-check** against `eurostat_electricity_trade_annual` (Luxembourg's partners): **equal to the 0.1 GWh** in 2010, 2020 and 2024, totals and countries (2024: imports 6,571.2, of which Germany 4,469.7, Belgium 1,209.2 and France 892.3; exports 1,321.8).
- **Terms:** lustat.statec.lu's robots address asked again in its own request (read 1565): no robots file, as in session 2771. STATEC's verdict (read 1564, session 2771) covers it. The license record shows the table as agreed, public.
- **The write's patch conflicted** in all four metadata files: this table's rows sit beside session 2771's, which main does not yet hold. Each block was the two new rows, so they were resolved as unions (`runs/c124/resolve_union.py`). No marker is left, and each table appears once in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md` (608 tables, 698 sources). `finish_table.sh`: the release and license checks pass (608 tables, 0 problems).
- **A heredoc with backslashes broke the test file** as I first wrote it (the memory's warning). It was rewritten with the editor before any run.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | lustat.statec.lu's robots address (its own request) | no file, as before |
| 2 | DF_A4208, every key, CSV (the fetch) | 200, 506,207 bytes |

Read recorded: 1565.

## Decisions made without you

- **A second table from the same publisher** as the third own choice, as chain 138 took several DUKES tables: it completes Luxembourg's balance at the cost of two requests.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statec_electricity_trade.py`, `tests/test_session2776.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (read 1565), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c140/s2776/`, `runs/license_reads/s2776/`, `warehouse/raw/statec/s2776a4208/`.
