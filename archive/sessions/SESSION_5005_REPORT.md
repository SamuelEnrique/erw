# Session 5005 report: the Grid tool

Energy Research Warehouse (ERW). Chain 233, portable laptop window P1, 13 November 2026, about 11:30 to 11:50 UTC. Opus 5.5. Model spend USD 0.

- Branch `wip/5000-grid`, cut from `wip/5000-analysis`.
- Read on the builds of sessions 5001 and 5004: six views at 1280 and 390, no error, no sideways scroll. `/network` and `/ask` resolve into `/grid`: the one page has stood since session 299.
- Faults file `docs/reviews/grid-faults-2026-11-13.md`: 3 rows (1 fixed, 1 data machine, 1 not a fault).
- Fixed: `replication/grid/replicate.py` ran with no argument only on the day its figures were written.
  - The snapshot the figures are of is now kept beside them (`snapshot.json`) and read by default.
  - The network group meets 85 of 85.
  - The figures script keeps that copy each time it writes.
- For the data machine: the carbon and Ask groups of `page_figures.json` are rewritten where the tables are held.
- Tests: the 15 files that touch the Grid note or its replication: 184 passed, 12 skipped (exit 0). New: `tests/test_session5005.py`.

## Decisions made without you

- The Grid's decisions block left in the page (it is your rulings, word for word, held by test 299), not moved into `decisions.ts`.
- No further page composition: the Grid is one page, and its design waits for the brand mockups.

## For Samuel's ruling

- None new. The Grid note is ready for your signature.
