# Session 3978 report: chain 278's unfinished steps; the two Derived from lines closed

Energy Research Warehouse (ERW). Chain 279, data machine (lab-desktop), 14 November 2026, 23:54 to 23:59 UTC. Opus 5.5. Model spend USD 0. No request.

Chain 278's unfinished steps, from file 279's list:

- **Waiting, skipped:** the daily run of 15 November (14:00 UTC, the first with the four fixes); the Roundup of 15 November; the Digest of 16 November and check-values on `/digest`; the data machine's run of 15 November (17:00 UTC, the first with the new replication group; `noaa_grid_weather`'s weekly step; `dm_live_set`); `wip/red-dm-2026-11-14` (deleted once that run commits); the hunt once the tables move; the CAISO's FERC compliance filing (due 16 November); the Ask weekly run (from 19 November); whether the owner's API key's limit refused the runs' model steps.
- **Done: the two `Derived from:` lines that parse as one name.** `datacenter_facilities` and `ercot_node_transmission` are entities tables, and `build_coverage.py` reads a `Derived from:` line only for series tables (`table_row` sends entities to `entities_row`, which never calls `derived_from`; the two calls are in the series builders). So the lines can never stop coverage; both tables' coverage rows read `derived: no`, as built. Nothing changed. (The data machine's own copy of `datacenter_tracker_rollups` predates session 3888's header line, so locally it parses as not derived; the runner writes it fresh.)

## Decisions made without you

- **The two headers left as their builders write them:** no reader parses them, and rewriting them would rewrite two tables for no reader.

## For Samuel's ruling

- None.
