# Session 3807 report: the landings, the daily run's next stop, the next file, the queue

Energy Research Warehouse (ERW). Chain 215, session 16 of 16, data machine (lab-desktop), 12 November 2026 17:10 to 20:10 UTC. Opus 5.5. Model spend USD 0.

## The landings

- **First, `4e8cda2c6`** (task/c215-data at `7625c45b3`, run 43272669045, 18:03 UTC): the outages' daily step and tables, the FERC-714 map, the reserve registry and table with its records, the tab's reserve line, the reports to 3802.
  - The gate: suite passed (8,383); check-values on the 3 known floors only (`cv_diff` 0 new); check-routes 0 failed, cross-checks 92 of 92, check-csp 97 pages and 0 violations.
  - The reserve line read on the gate's build at 1280 and 390 px: 3 CAISO rows with 30.8 percent, 14 ERCOT rows with their CDR, 23 "not held".
  - Snapshots `c215-land-before` and `c215-land-after`: 0 differences.
- **Second, `c59df9262`** (task/c215-data2 at `9b6c124a9`, run 43292880091, 20:01 UTC): the data machine's two fixes (the catalogue conflict, `dm_analysis_figures` with test 3701), the later reports, the note.
  - The gate: suite passed (8,385); the 3 known floors only; the three hand checks passed.
  - Snapshots `c215-land2-before` and `c215-land2-after`: 0 differences.
- **Between them, the data machine's page files** (`72e8958c7`, `3dab64a49`, 19:04 UTC) went to main through the push guard (session 3793). Snapshots: 0 differences.

## The daily run's next stop, fixed

- The dispatched run (43276079255) passed the rollup's stop (chain 212's fix) and stopped at 19:53 UTC on the next first-written table: "deal_counterparties: no sector rule in build_coverage.SECTOR_RULES matches".
- **Fixed on `wip/c215-data`** (`8be148dd5`):
  - the sector (`deals`) and tier (`model_extracted`) rules;
  - written, validated, in coverage and archived under the lock (510 rows, `20261112T200434Z-local`), with no further stop;
  - the license record (public, "the ERW's own work", as `energy_companies` built from the same deals);
  - held from v1 and the live catalogue as the late tables are; the package's record and the catalogue rebuilt.
- Tests 275, 378, 410, 505, 237, 203, 238, 53, 67, 469, 1008, 1001, 1009, 3298 and 207: 171, OK.
- **It lands through the gate next** (the third of the day). The evening's scheduled fallback, if it starts before, runs on the old code and stops the same way; the 14:00 UTC run of 13 November has the fix.

## The next file and the queue

- `queue/next/216-day-14-november-data-continued.md` gets its "Sessions 3809 to 3813" from this chain's note, pushed alone after this landing:
  - read the next daily run, which should commit now that both stops are fixed;
  - the Stanford upload of `iso_reserve_margin_reports`;
  - the data machine's run of 13 November with the two fixes;
  - NYISO's incomplete day;
  - the waiting rows;
  - the hunt.
- Then `chain_queue.py next`.

## Decisions made without you

- **The counterparties fix went in this chain,** not the next: it is the only stop between main and its daily commit.
- **Pushed with the floors failing,** as the established rule allows (known floors only, hand checks on the same build).

## For Samuel's ruling

- None new (chain 215's note).
