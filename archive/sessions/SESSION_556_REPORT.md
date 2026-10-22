# Session 556 report: petroleum products supplied

21 October 2026, from 22:55 UTC, on lab-desktop (the data machine), the second session of `queue/done/031-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_product_supplied.py`: product supplied (EIA's measure of consumption) for every product, the U.S. and the five PADDs, a month**, from EIA's API v2 (route `petroleum/cons/psup`), as `eia_product_supplied_monthly`.
  - 71,938 rows: 702 series, January 2017 to July 2026.
  - About 60 products, EIA's totals and their parts, in `kbbl` and `kbbl/d`. The header says a sum takes one level.
  - From 2017, within the ceiling.
- **EIA's API answered one page with a 502, twice**, and the first run stopped with nothing written. The second run reused the four pages already saved.
- **Cross-check**: the 96 series this route shares with session 555's table (`eia_petroleum_snd_monthly`, product supplied) are equal on all 11,040 rows they both hold.
- **Written under the data lock** (23:04 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`oil;products`). Tests: `tests/test_session556.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 19 of 20 | a June 2026 page (the probe); the first trial (4, two of them 502s); the second (14) |

## Files

- New: `warehouse/connectors/eia_product_supplied.py`, `tests/test_session556.py`, this report. Changed: the shared metadata, holds and package.
