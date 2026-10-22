# Session 617 report: petroleum supply and disposition, the fifth group, pulled

22 October 2026, from 02:29 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_petroleum_snd_monthly` now holds all 58 products of EIA's route**: 523,835 rows, 4,459 series, January 2015 to July 2026.
  - 47,966 new rows in 429 series, from the eleven small products session 610 named (`GROUPS[4]`).
  - The trial ran from the main checkout, as chain 038's rule says: the first four groups' 100 saved pages were reused, and 10 requests were made.
- **Cross-checks**:
  - All 475,869 earlier rows are unchanged.
  - The 78 new series also in `eia_product_supplied_monthly` are equal on all 8,112 rows.
- **Written under the data lock** (02:33 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (47,966 rows archived). The table's release rows were replaced (`runs/release_replace.py`); the release check exited 0.
- **The connector's ceiling is now 14 a run** (it was 29). Every group's pages are saved, so a run asks only for pages it lacks. A ceiling under the session's 15 means a run from the wrong place stops before it breaks the session's ceiling.
- **Chain 037's landing deployed** (`95224f02`, Vercel success at 02:30:45 UTC, the first deploy since the rate limit began at 19:29 UTC on 21 October). s616-before against s616-after2 (taken after the deploy): 0 differences, as every page is in review. The queue move's push after it (`1319ee1f`) was rate limited again.

## Decisions made without you

- The ceiling lowered to 14, as above.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 10 of 15 | the fifth group (the trial) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_petroleum_snd.py` (the ceiling), `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `warehouse/metadata/{coverage,archive_manifest}.csv`.
