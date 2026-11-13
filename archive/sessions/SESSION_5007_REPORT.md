# Session 5007 report: the cross-check tables against the page's figures

Energy Research Warehouse (ERW). Chain 233, portable laptop window P1, 13 November 2026, about 10:50 to 11:00 UTC. Opus 5.5. Model spend USD 0.

- Each cross-check table's "ours" column was set against its tool's `page_figures.json`, row by row where the row names its field.
  - Battery and generator: every row agrees.
  - Research and Grid: no row names a field the comparison can read; unchanged.
- Datacenter: five rows had moved since 6 November (the cost for 100 MW, the carbon, the tonnes, the hourly window), because the daily files' hours held changed. Updated to the figures of 12 November, the old ones kept beside them.
  - None of the five has a published counterpart, so no gap moved.
  - The table now says its figures move with the daily files and how a reader sets them beside today's.
- No test holds the table to the daily figures: one would turn main red each time the data machine rewrites them (the red-main causes of 30 October and 6 November).
- Tests: `tests/test_session3707.py`, 7 passed (exit 0).

## Decisions made without you

- The table dated, not tested against the daily figures.
