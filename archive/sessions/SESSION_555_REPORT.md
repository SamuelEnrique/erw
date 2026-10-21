# Session 555 report: petroleum supply and disposition

21 October 2026, from 22:24 UTC (its probe; its trial ran while chain 030's landing waited for its checks), on lab-desktop (the data machine), the first session of `queue/done/031-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_petroleum_snd.py`: petroleum supply and disposition for the U.S. and the five PADDs, a month**, from EIA's API v2 (route `petroleum/sum/snd`, the Petroleum Supply Monthly), as `eia_petroleum_snd_monthly`.
  - 100,340 rows: 792 series, January 2015 to July 2026.
  - Twelve processes as words, among them field production, refinery output and input, imports, exports, net receipts, stock change, ending stocks and product supplied.
  - Both of EIA's units, `kbbl` (the month) and `kbbl/d` (with `_per_day`).
- **Narrowed, as the probe required**: the route holds about 40 products and 3,949 records a month, so 2010 on would have been about 158 pages.
  - Eight products are taken: the total, crude oil, finished motor gasoline, distillate, jet fuel, propane, residual fuel and fuel ethanol.
  - Months from 2015, about 21 pages. The others can be added by a later run.
- **Cross-check**: the U.S. crude field production per day (series MCRFPUS2, which this route shares with `petroleum/crd/crpdn`) against `eia_crude_production_state_monthly` (session 527). They are equal on all 139 months.
- **A slip of mine, put right before the commit**: the first edit of `live_set.yaml` missed because of the file's Windows line endings, so the table went into the release package as in v1. The holds were added, the package was put back, and the finish was run again; the release check passes.
- **Written under the data lock** (22:57 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`oil;products`). Tests: `tests/test_session555.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 23 of 30 | a June 2026 page (the probe); the trial (22) |

## Decisions made without you

1. Eight products and 2015 on, within the ceiling.

## Files

- New: `warehouse/connectors/eia_petroleum_snd.py`, `tests/test_session555.py`, this report. Changed: the shared metadata, holds and package.
