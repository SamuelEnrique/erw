# Session 549 report: nuclear outages by reactor, 2007 to 2014

21 October 2026, from 22:22 UTC, on lab-desktop (the data machine), the second session of `queue/done/030-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_nuclear_outages_generator_daily` now runs from 1 January 2007 to 21 October 2026**: 2,141,406 rows, 107 reactors at 66 plants, all 7,234 days. Session 548 held 2015 on.
  - The trial read 2007 to 2014 (300,763 records) and reused session 548's pages for 2015 on (413,039).
  - The two windows were written together as one snapshot.
- **Cross-check** (`runs/s548/crosscheck.py` on the data machine, on the whole span): the reactors summed by plant and day against `eia_nuclear_outages_facility_daily`. They are equal on all 437,624 plant-days, with the largest gap 0.0 MW.
- **Written under the data lock** (22:34 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0 (902,289 new rows archived).
- **A conflict in carrying the metadata, and a mistake of mine in resolving it, both put right before the commit.**
  - The patch replaced the row session 548 had added, and conflicted with it.
  - `git checkout --theirs` took the whole files from the patch's side, which dropped sessions 550 to 553's rows (the license check fell to 258 tables).
  - The three files were put back to the commit, and only the reactor table's line was replaced in each. The license check is back at 262 tables with 0 problems, and the release check passes.
- The release row was replaced. EIA's API answered one page with a 504, which was asked again.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 63 of 100 | 2007 to 2014 (62 pages and one 504 asked again); 2015 on reused |

## Files

- New: this report. Changed: `docs/coverage.md`, `docs/licenses.md`, `docs/redivis/release-v1/tables.csv`, `warehouse/metadata/{coverage,archive_manifest,license_tables}.csv`.
