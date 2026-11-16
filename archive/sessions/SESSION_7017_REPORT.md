# Session 7017 report: done-line requests 4, 13, 14, 15 and 34; 32 waiting for the lock

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The data lock

- The GitHub daily run (run 43881234167) took the data lock at 14:10 UTC (expiry 19:30). No write was attempted under it; the session took the steps that need none.

## The data requests

- **32, waiting for the lock.** This machine's `energy_projects` was the archive's copy of 26 October; the archive holds the build of 5 November (39,917 rows), restored to `runs/c301/rq_energy_projects.csv`. Its rebuild into place and the map's file follow when the lock is free. `scripts/sync.py` compares tables with Redivis by their newest timestamp and row count, which says little about a snapshot table like this one; noted, not changed.
- **34, left as it is** (the row's default): the map keeps a queue position's megawatts to one decimal; 0.8 MW in 761,478.2.
- **13, done.** Run from `wip/7507-peak-premium` against the tables rebuilt in session 7015: `from_hourly.py` 26,040 of 26,040 rows; `replicate.py` 25,110 of 25,110 figures, 674 of 674 views, 6,266 of 6,266 two-hub figures, 12,172 of 12,172 periods. `--write` is left to the branch's machine.
- **14, answered.** The workbooks of run `20261105T230347Z` are not on this machine (the table was built on the runner); the nearest held are of 2 and 9 November, on which this chain's own replication gives 24,241 of 24,245.
- **15, done.** CAISO's own system load beside EIA-930's California demand, January to October: EIA's figure 99.50 to 99.61 percent of CAISO's from 2021 to 2025 and 100.02 percent in 2026; 2026 over 2025, CAISO 5.57 percent and EIA 6.03 percent.
- **4, code done.** A party's place by contracts in `ferc_eqr_party_mw` is its `x_rank` in `ferc_eqr_party_totals`, the place the contracts page names (708 of 812 rows held another; a trial run found every party a place); the loader's summary takes a blank place as none; test 7016_eqr_place. The rebuild and load wait for the lock.

## Goal 3

- 16 November 15:08 UTC: CAISO's large-loads process page (its robots file answering 404 first, in a call of its own) has the same bytes (sha256 `578c69995d9a0388...`): "Nov 16, 2026 FERC filing" still to come. Not filed; checked again at a later session's start.

## For Samuel's ruling

- None new.
