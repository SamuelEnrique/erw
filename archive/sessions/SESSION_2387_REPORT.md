# Session 2387 report: Costa Rica's generation by plant (CENCE's web services), internal

24 October 2026, from 09:16 UTC to 09:22 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: 14 requests of 15 (7 by the probe, 1 by the fetch, 6 by the trial; the write ran offline).

## Read these first

- **CENCE publishes its data through web services, listed by a service of its own.** apps.grupoice.com has no robots file (read 639).
  - The chart pages read JSON by GET.
  - The file downloads sit behind JSF forms, and the generation chart's service answers one day a request, too narrow for a history.
  - The service list (38 services) names `EnergiaMensualOficial`: "generación mensual de energía en MWh de las plantas del SEN", "solamente datos ya oficializados", a year a request.
- **A new table, `cence_costarica_generation_monthly`** (series, 7,731 rows, `power`): Costa Rica's official monthly generation by plant, January 2020 to August 2026.
  - It covers 117 plants, with CENCE's source and the operating company kept as `x_source` and `x_company`, in MWh as CENCE gives them.
  - CENCE's source "Intercambio" (two rows a month, the exchanges with the regional market) is written as `interchange`, signed as CENCE gives it, not as generation.
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license is not settled.** The services' answers end "© 2025 ICE Todos los Derechos Reservados" (read 640) and grant no reuse, so the table is `internal`.
- **Cross-checks:**
  - generation by source, 2020 to August 2026: hydro 60.1 TWh, geothermal 10.3, wind 10.0, thermal 2.6, bagasse 0.4, solar 0.1; interchange -2.0;
  - generation over `owid_ember_electricity_annual`'s demand: 0.989 to 1.120, 2020 to 2025; with interchange added, 0.982 to 1.140.
  - Every month of 2025 is present; 2026 runs to August.

## Requests (14 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | apps.grupoice.com/robots.txt | 404 |
| 2 | a guessed download page | 404, the site's menu |
| 3 | the generation chart page | 200: a day a request |
| 4 | the web services' guide | 200 |
| 5 | the web services' page | 200: the service list's address |
| 6 | the service list | 200: 38 services |
| 7 | EnergiaMensualOficial's parameters | 200: a year (and a plant) |
| 8 | 2025 (the fetch) | 200 |
| 9 to 14 | 2020 to 2024 and 2026 (the trial) | 200 |

Reads recorded: 639 and 640.

## Decisions made without you

- **Interchange kept as a variable of its own,** not summed into generation.
- **`internal`** under ICE's all-rights-reserved notice.

## For Samuel's ruling

- **ICE's consent** for Costa Rica's generation data, if it is wanted public.

## Files

- New: `warehouse/connectors/cence_costarica_electricity.py`, `tests/test_session2387.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record (reads 639 and 640).
- On the data machine only: `runs/c113/s2387/`, `warehouse/raw/cence_electricity/`, `warehouse/output/cence_costarica_generation_monthly.csv`.
