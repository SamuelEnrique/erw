# Session 3775 report: chain 211's note, and the stop that kept the catch-up off main

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:25 to 14:03 UTC. Opus 5.5. Model spend USD 0. Requests: none to any publisher; Supabase reads (erw_health), and the archive's bucket under the data lock.

## Read these first

- **The daily run's stop is fixed on `wip/c212-data`.**
  - The catch-up run (43212054910) pulled for almost two hours and then stopped at coverage, committing nothing: `ValueError: datacenter_tracker_rollups: sources ['erw:datacenter_projects'] are not in sources.csv; cannot set its license`.
  - The run of 7 November stopped the same way (its health summary).
  - The table (session 2236's rollups of the datacenter tracker) names a source no run ever registered.
- **What the fix holds** (commits `1153a362a` and `343a2075b`):
  - `warehouse/derived/datacenter_tracker_rollups.py` registers `erw:datacenter_projects` in `sources.csv` when it writes the table (`ip.update_sources`, as the other derived tables do), license internal like its one input `datacenter_projects`.
  - `warehouse/metadata/build_coverage.py`: a sector rule (`power;datacenters`) and a tier rule (`model_extracted`). The sector rule was the next stop: written under the lock, coverage refused with "no sector rule ... matches".
  - The license registration: `scripts/licenses.py tables` and `write`, and `package/tools/build_tables.py`. Test 378 refused the first coverage row without it, which would have made the guard refuse the bot's push.
- **Proven under the data lock** (13:55 to 13:56 UTC, in the main checkout with the branch's two files copied in and put back):
  - the rollup wrote 584 rows from 189 facilities; the validator passed;
  - `build_coverage.py --only` wrote the row (internal, `power;datacenters`, `model_extracted`);
  - the archive ran (`20261112T135617Z-local`, 584 rows).
  - The metadata moved to the branch, and main's files were put back.
- **Tests:** the 48 test files that read coverage, sources, licenses or the catalogue (972 tests; 378 failed before the registration, then passed); 237, 203, 238, 53, 67, 1008, 1001, 1009 and 207 (121, OK); `release_v1.py --check` 0 differences; `build_tables.py --check` 0.
- **Chain 211's note** (`docs/state/note_2026-11-12_data_c211.md`): its landing commit (`53d8a2f69`) and "What did not finish" (`139d6996c`); "The catch-up" by session 3777.

## Decisions made without you

- **The rollup is internal,** as its input is (license needed since 21 October 2026). The registry entry says so, and the table is in no live set, page or download.
- **The fix takes this chain's first unfinished-step session.** It stops every daily run from committing, so it comes before chain 211's Stanford draft.
- **The 14:00 UTC run was left to run.** It started on main's code before the fix and will stop the same way. Cancelling it would gain nothing, because the fix cannot land before 16:15 UTC (the landing window). The evening's scheduled fallback runs after the landing.

## For Samuel's ruling

- None. The fix is reversible, and the table stays internal.
