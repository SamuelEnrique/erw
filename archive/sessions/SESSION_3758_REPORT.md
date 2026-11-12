# Session 3758 report: FERC-714 forecasts (ruling 1), with 3759

Energy Research Warehouse (ERW). Chain 211, sessions 9 and 10 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0. Requests: 2 to PUDL's bucket (one HEAD, one GET of a 250 KB file), within the ceiling of 40.

- **`ferc714_planning_area_forecasts`** (`warehouse/connectors/ferc714_forecasts.py`, `603054e94`):
  - Source: PUDL's `core_ferc714__yearly_planning_area_demand_forecast` (FERC Form 714, Part 3, Schedule 2; FERC's own site refuses automated readers, session 484).
  - Contents: summer peak, winter peak and net energy by planning area, forecast year and filing; 67,215 rows, 190 planning areas, report years 2006 to 2025.
  - Public (ruling 1). Written under the data lock with `runs/c147/write_table.sh`, archived (`20261112T112715Z-local`).
- **`ferc714_forecast_growth`** (`warehouse/derived/ferc714_forecast_growth.py`):
  - Each filing's change of the same forecast year against the filing one and two years before, in MW, MWh and percent.
  - 198,354 rows, 168 planning areas, filings 2007 to 2025; derived, public; archived (`20261112T112909Z-local`).
- **Decision 77** (`docs/datastandard.md`, `warehouse/validate/erw_validate.py`): a series table whose header says "Revisions: kept, one row per vintage" is keyed by vintage too, and a blank vintage is refused. Both tables use it.
- **The method note** `docs/methods/ferc714_forecast_growth.md`:
  - The ten largest upward revisions of 2030's summer peak, 2025 filing against 2024: SPP +7,235 MW, MISO +5,485, Sierra Pacific +2,736, Duke Energy Carolinas +1,848, FPL +1,487, APS +1,330, Nevada Power +1,118, TVA +957, PNM +769, El Paso Electric +760. The 88 areas' upward revisions sum to 28,963 MW, net +6,861.
  - The cross-check (3759): each ISO's forecast filed a year ahead against EIA-930's actual peak. Six of seven are within about 9 percent; MISO runs 8 to 9 percent above every year; PJM's 2025 actual peak passed its forecast by 4 percent.
- `tests/test_session3758.py` (8 tests). A sector rule in `build_coverage.py`.

## Decisions made without you

- **`vintage` is the filing's due date** (1 June after the report year), because PUDL gives no submission time. `x_report_year` carries the report year itself.
- **The validator was extended (decision 77)** rather than the filing year being encoded in a variable or entity name. The standard already allowed vintage in the key, and the validator had not caught up.
- **Coverage of the derived table** was built together with its input in one run (`runs/s3759/write_growth.sh`), since main's coverage did not yet hold the input.
- **A claim was checked before it was kept.** One sentence about PJM in the note's first draft was checked against the table and corrected before commit: the 2024 filing raised the outer years; the 2025 filing trimmed 2026 to 2032.

## For Samuel's ruling

- None new.
