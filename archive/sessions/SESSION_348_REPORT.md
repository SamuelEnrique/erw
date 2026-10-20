# Session 348 report: the queue statistics

20 October 2026, about 09:35 to 09:45 UTC, unattended, on portable-laptop (the third machine), the fifth session of the chain of 20 October, night. Branch `wip/348-map`, made from `wip/345-impact` so that the two branches land one after the other without conflict; not landed. Model spend USD 0. No pull from a publisher.

## Read these first

- **`iso_queue_statistics`** (the prompt's `queue_statistics`; three parts by Decision 19): 1,511 rows, six ISOs by entry year, 1989 to 2026. Entered, withdrawn, operating, still waiting and status not stated, in positions and MW; the withdrawal rate; the wait's median and mean years and the count of positions it is taken over. Every rule, each ISO's status words included, is in `docs/methods/energy_projects.md`, "Queue statistics".
- **What is not held, said in the table and the method:** ERCOT's withdrawn positions (its GIS report lists active and completed only), so no ERCOT withdrawal rate; MISO's and ISO-NE's in-service dates, so no wait for them; SPP's wait reads its Commercial Operation Date, which may be the date requested. Positions with no queue date are in no year (ERCOT's are 456 of 1,758).
- **The inputs are the data machine's copies from the ERW archive** (`restore.py --from-bucket`, into `runs/archive_restore/`, not `warehouse/output`): this machine's own copies were from 1 October. ERCOT, CAISO, SPP and ISO-NE as of 19 October; NYISO and MISO as of 4 October (their last run).
- **The LBNL cross-check** (the held copy of Queued Up through 2025, CAISO): requests of 2000 to 2020 that reached operation, 233 here and 232 in LBNL's file; the median wait of positions online 2018 to 2025, 92.35 months here and 91.39 in LBNL's; the withdrawal rate of those years 78.3 and 78.1 percent. CAISO's current report holds 148 fewer positions of those years than LBNL counted.
- **Held by grid from 21 October:** its publishers are the six ISOs, so its NYISO, MISO and ISO-NE rows are "license needed" from that day, as their queues are; 42 tables are "license needed" now (41 before).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 348"` | 0 | |
| `restore.py --from-bucket`, seven tables | 0 each | `runs/archive_restore/` (not in git) |
| `queue_statistics.py --inputs runs/archive_restore` under the data lock | 0 | 1,511 rows |
| `erw_validate.py` | 0 | PASS, 0 errors, 0 warnings (after two fixes below) |
| `build_coverage.py --only '^iso_queue_statistics$'` | 0 | derived, public, power |
| `load.py --only '^iso_queue_statistics$'` under the lock | 1 | **the table matched (1,511 and 1,511); the run failed on `sources`**: Supabase holds `erw:price_years`, which the data machine loaded tonight and this branch's `sources.csv` does not have yet. Not pruned (that would delete the data machine's row); it resolves when the branches meet main |
| `upload.py --tables iso_queue_statistics`, `archive.py write` under the lock | 0, 0 | Redivis 1,511 (draft only); archived 1,511 |
| `licenses.py write`, `check`, `status` | 0, 0, 0 | 207 tables, 0 problems; 42 "license needed" from 21 October |
| `tests.test_session348`, `test_session207` (its pins move from 41 to 42) | 0, 0 | 7 and 15 tests |

**Two faults fixed before the load:** `retrieved_at` first carried the input header's whole "Retrieved" line (the validator warned), and the rows' `source_url` carried a `#` fragment, which cuts a row for a reader that skips comment lines (pandas, the site's Python and Stata readers). Both rewritten; a test now holds that no row carries `#`.

## Decisions made without you

1. **The archive's copies, not this machine's,** for the inputs: the prompt says "as held", and the ERW holds them in its archive; this machine's files were 19 days old. `warehouse/output` of the other tables was not touched.
2. **The branch from `wip/345-impact`**, so both land in order without a conflict in the shared metadata files.
3. **Withdrawal rate by count**, as LBNL's by-count figure; MW is in the table beside it for a capacity-weighted rate.
4. **No "all years" row:** a page sums the years it shows.

## For Samuel's ruling

- None new beyond the pack's. ERCOT's withdrawn positions would need its historical GIS reports (a pull), if wanted.

## To finish

- On the data machine, after landing: `python warehouse/supabase/load.py` in its daily run settles the `sources` mismatch by itself (both rows are then in `sources.csv`).
