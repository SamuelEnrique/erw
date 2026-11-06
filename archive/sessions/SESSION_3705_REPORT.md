# Session 3705 report: the Grid tool's decisions block and note

Energy Research Warehouse (ERW). Chain 208, session 6 of 20, portable laptop, 6 November 2026, about 22:27 to 22:30 UTC. Branch `wip/3701-sellable`, head `5d555561f`.

- **`replication/grid/assumptions.json`**: 25 assumptions, each with its default, unit, source and how to change it. It covers:
  - the snapshot, its window, the pair rule, the hour shown, the sign and the lag's rounding;
  - the gravity shape's source, pull and full-pull share (the owner's rulings 1a, 2c, 4b and 6a of 18 October);
  - carbon intensity, its daily and monthly weighting and the months left out;
  - the Mix tab's latest hour, California's join and the sources;
  - the Clean tab's carbon-free sources and levels;
  - the Ask panel's examples and scope;
  - the license hold and the tolerance.
- **`docs/methods/grid_network.md`** gains:
  - a Replication section: the package, what it found and the test;
  - a line in Cross-checks pointing to `docs/methods/crosschecks/grid.md` (sessions 3708 to 3710);
  - the decisions block, the assumptions file word for word.
- **Tests:** `tests/test_session3705.py`: the note's table equals the assumptions file cell by cell. With 3702's: 6 tests, OK. `check-cross-checks.mjs --files`: 70 of 70 passed.
- No page changed. The page's own block of rulings (`data-decisions="299"`) is as it was.

## Decisions made without you

- The decisions block is in the method note and the package, not on the page: the prompt forbids page changes.

## For Samuel's ruling

- None new.
