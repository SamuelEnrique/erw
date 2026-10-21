# Session 489 report: the tables of sessions 484 to 497, written under the data lock

21 October 2026, from 18:29 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/022-evening-21-october-sources.md`, run once the daily run released the data lock. Model spend USD 0.

## Read these first

- **Ten connectors' tables written into `warehouse/output`**, all under the data lock (taken 18:29:44, released 18:36), by `runs/s489_write.sh`. Every connector reused its raw files where it held them.

  | Table | Rows | What |
  |---|---|---|
  | `ferc714_area_demand_2023` to `_2025` | 779,627; 781,703; 770,886 | 89 respondents a year (session 484) |
  | `eia861_utility_sales` | 2015 to 2025, 34,207 to 55,427 a year | 1,521 to 3,179 utilities (sessions 485 and 495) |
  | `egrid_power_plants` | 12,612 plants | eGRID2023, 1,303,569 MW (session 486) |
  | `nlr_atb_electricity_costs` | 95,000 | ATB 2025 v1.0.0, 547 entities, 20 technologies (session 487) |
  | `eia_aeo_electricity` | 34,034 | AEO2026, 11 cases (session 490) |
  | `eia_steo_forecasts` | 5,088 | the STEO of 6 October 2026, 53 series (session 491) |
  | `epa_ghgrp_power_co2` | 17,035 | 1,443 facilities, 2010 to 2023 (session 492) |
  | `boem_renewable_leases` | 52 | leases and grants (session 493) |
  | `uswtdb_wind_turbines` | 77,839 | 159,587 MW (session 496) |
  | `eia_seds_state_energy` | 23,660 | 676 series by state, 1990 to 2024 (session 497) |

- **The gates**: the validator exited 0. `archive.py write` exited 0: 12 tables archived, 3,030,651 rows. `build_coverage.py --only` failed first (exit 1): `eia_seds_state_energy` had no sector rule. Session 497's rule was only on the `wip/` branch. The coverage was run again with the branch's `build_coverage.py`, copied in for that one run and then restored: it exited 0.
- **The metadata moved to the branch**: `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv` and `sources.csv` were copied as a patch of added lines only. `licenses.py tables --headers` (the data machine's `warehouse/output`), `write` and `check` were run in the worktree: 224 tables, 0 problems. The main checkout was put back to main's files.
- **No table of this chain is in the live set.** Nothing was loaded and nothing was uploaded to Redivis.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 33 | AEO 24 (of 60), STEO 4, SEDS 5 (of 20) |
| energy.usgs.gov | 8 of 30 | USWTDB's pages |
| others | 0 | raw files reused (PUDL, EIA-861, eGRID, ATB, GHGRP, BOEM) |

## Decisions made without you

1. Coverage was run with the branch's sector rules, not main's, rather than landing the rule first and writing a second time.

## Files

- Changed: `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`. New: this report. `runs/s489_write.sh` stays on the data machine (`runs/` is not in git).
