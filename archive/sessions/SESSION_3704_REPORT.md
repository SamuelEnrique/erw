# Session 3704 report: the Grid tool's do-files

Energy Research Warehouse (ERW). Chain 208, session 5 of 20, portable laptop, 6 November 2026, about 22:24 to 22:27 UTC. Branch `wip/3701-sellable`, head `7a810c257`.

- **`replication/grid/replicate.do`:**
  - the network's hour from `snapshot_hour.csv` (written from the snapshot by `figures_of_the_page.py`, with its refresh time for the lag): each grid's net export and import, ties, largest flow, each tie, the largest net exporter;
  - the Clean tab's carbon months, rebuilt from the hours;
  - the comparison with `page_figures.csv`.
- **`replication/grid/replicate_ask.do`**, written from `page_figures.json`: 24 of the Ask panel's plain queries. The grouped queries and the compares are `replicate.py`'s.
- Neither do-file has been run: there is no Stata here.
- **Test:** `tests/test_session3703.py` gains the do-files' rules (no continuation; one empty line between commands outside a loop or program, none inside; every destring with force) and checks the Ask blocks: 13 tests, OK.

## Decisions made without you

- The tables' comment lines are dropped in Stata by reading with no names, dropping lines that begin with `#`, and naming the columns from the header row. A table's header count changes between builds, so a fixed `varnames(n)` would break.
- The weekly figures of the gravity shape's generation are not in the do-file: the tables here do not hold the hour.

## For Samuel's ruling

- None new.
