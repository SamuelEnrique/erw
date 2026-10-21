# Session 460 report: restore_tables.py was right; prove.py judged against the replay

21 October 2026, from 09:36 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 21 October, day and evening (`queue/done/020-day-21-october-data-2.md`). Model spend USD 0. Pulls: the archive bucket only.

## Read these first

- **The part's premise was wrong, and so was session 454's swap of two tables. Both are corrected.** The part asked why `restore_tables.py` took a stored copy over a newer run. The run log says it did not.
  - For `policy_reads_evidence` the latest run is GitHub's of 01:16 UTC on 20 October, with 3,362 rows. For `price_board_spreads` it is GitHub's of 06:33 UTC, with 2,408 rows.
  - Their data SHA-256 are those of the stored copies `restore_tables.py` restored, which this machine already held.
  - What `prove.py` compares against is `restore.py`'s replay, which keeps every key any run ever wrote. For a table whose keys leave (policy evidence a later read drops, spreads a later build leaves out), the replay holds rows the latest run no longer had: 1,781 and 28 here.
  - `prove.py` read that as "this machine behind", and session 454 put the replay's 5,143 and 2,436 rows in place.
- **Undone**: the two exact copies are back in `warehouse/output` (their hashes are the latest run's), validated, with coverage at 3,362 and 2,408 rows again. The replays are kept in `runs/s460_replay/`. Neither table was loaded in between: 454 made no load, so the live set never held the replay.
- **Fixed in `warehouse/archive/prove.py`**, with `tests/test_session460.py` (4 tests; the first fails without the fix):
  - `last_run()` returns the run's `data_sha256`.
  - A copy whose data SHA-256 is the latest run's own is "equal", and the cause gives how many rows the replay holds beyond it.
  - An older copy is still "this machine behind", and a run with no recorded SHA is judged as before.
  - Run on the two tables: both "equal (this copy is the latest run's own ...)".
- **Session 454's report has a correction appended**, and its finding about `restore_tables.py` is withdrawn. `grid_network_links` and `caiso_reliability_daily` stand: each was rebuilt to its latest run's row count. Session 436's CSV is left as the record of what the proof said then; this report says what it missed.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| the run log's lines for the two tables | 0 | `runs/s460_runs.out` |
| the copies' data SHA-256 against the latest run's | 0 | the set-aside copies match; the replays do not |
| `warehouse/lock.py acquire`, the swap back, `erw_validate.py`, `build_coverage.py --only` | 0 | about 09:38 UTC |
| `tests.test_session460` with and without the fix | 0, 1 | |
| `prove.py --fresh --only` the two (fixed; the main checkout's copy restored after) | 0 | both equal |

## Decisions made without you

1. The two tables put back to the latest run's exact copies, and the earlier report corrected, not rewritten.
2. A copy that is the latest run's own counts as "equal", and the replay's extra keys are named in the cause instead of a new status, so earlier counts read the same way.

## Files

- Changed: `warehouse/archive/prove.py`, `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `archive/sessions/SESSION_454_REPORT.md` (the correction). New: `tests/test_session460.py`, this report.
