# Session 516 report: EIA's nuclear outages by plant

21 October 2026, from 19:51 UTC, on lab-desktop (the data machine), the first session of `queue/done/027-night-22-october-sources.md` (its probe and trial run while chain 026's landing waited for its checks). Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_nuclear_outages_facility.py`: each nuclear plant's capacity, outage and outage share, a day**, from EIA's API v2 (route `nuclear-outages/facility-nuclear-outages`), as the series table `eia_nuclear_outages_facility_daily`.
  - 741,501 rows: 62 plants over 4,312 days, from 1 January 2015 to 21 October 2026, with no day missing.
  - The entity is `eia_nuclear_outages:<EIA's plant id>`, and the node is the plant's name.
- **From 2015, not 2007.** The route holds about 36,000 rows a year, so 2007 on was beyond the ceiling of 100. 2007 to 2014 is left for a later run (`--from 2007-01-01`).
- **EIA's `total` is not the number of rows the data hold.** From 2015 it says 413,039, while the pages run in order, day by day, and end at 247,167 rows on the newest day with an empty page after. For 20 and 21 October it counts 95 plants a day and returns 55.
  - My reading, not EIA's statement: the count includes plants whose figures are blank (retired plants), which the data leave out.
  - So the connector does not check against EIA's total. It reads until a short page, stops if a page leaves day order or any day has no row, and logs EIA's total beside its own.
  - The first trial stopped on the old check, with nothing written. That is the check's fault, found then.
- **Cross-check**: the plants' outage and capacity, summed by day, against `eia_nuclear_outages_daily` (session 513), EIA's own U.S. total. They are equal on all 4,312 days, with the largest gap 0.0 MW for both. So the plants are complete.
- **Written under the data lock** (20:03 UTC) with `--offline`, from the trial's saved pages (0 requests). The validator, coverage and archive exited 0 (741,501 rows archived).
- **Held** from `/data`'s catalogue and Redivis v1 until uploaded. Not in the live set.
- Sector rule (`power;uranium`). Tests: `tests/test_session516.py`, 7: the rows; reading until a short page; a missing day or pages out of order stop the run; the holds.
- New on the data machine (`runs/`, not in git): `runs/write_table.sh` and `runs/finish_table.sh`, sessions 510 to 514's write and finish steps as two scripts, each exit code read.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 53 of 100 | the probe (2); the first trial (51 pages, the last one empty); the second trial and the write reused them |

## Decisions made without you

1. 2015 on, within the ceiling.
2. Completeness checked by day order and no missing day, since EIA's total counts rows the data do not hold; the plants-to-U.S. sums confirm it.

## Files

- New: `warehouse/connectors/eia_nuclear_outages_facility.py`, `tests/test_session516.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
