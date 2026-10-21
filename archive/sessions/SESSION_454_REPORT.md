# Session 454 report: the archive's five mismatches, closed

21 October 2026, from 08:57 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 21 October, day (`queue/done/018-day-21-october-data.md`). Model spend USD 0. Pulls: the archive bucket only (Redivis not asked). No load.

## Read these first

- **Four of session 436's five mismatches are equal now** (`prove.py --fresh --only` on the five, 09:04 UTC): `grid_network_links`, `caiso_reliability_daily`, `price_board_spreads` and `policy_reads_evidence`.
- **What each was** (`prove.py --refine` first):
  - `caiso_reliability_daily` (2 rows) and `price_board_spreads` (3 rows, 28 keys added): the archive's later runs revised and added rows, so this machine was behind.
  - `policy_reads_evidence`: 1,781 rows that GitHub's run of 20 October archived; 3,362 to 5,143 rows.
  - `grid_network_links`: a rolling window whose copy here ran to 13 October against the archive's 17 October; 26,280 to 18,744 rows, the archive's latest run.
- **The fifth, `datacenter_queue_positions`, is left as it is.** It is a tracked file and one of the daily run's uncommitted files in the main checkout, which the chain keeps as they are. Its one revised row comes with this machine's daily run.
- **A finding in `warehouse/restore_tables.py`.** For `price_board_spreads` and `policy_reads_evidence` it restored "a copy in the archive bucket": the same older version this machine held, not the archive's latest run. The proof still found them behind. `warehouse/archive/restore.py --from-bucket` rebuilt each as of the latest run, and that is what is in place. Why the stored copy was taken over a newer run is for a later session, with a test; no code was changed here.
- The four old copies are kept in `runs/s454_before/` (with `.bucketcopy.csv` for the two restored twice).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `prove.py --refine --only` (the four that differ both ways) | 0 | three behind, one rolling window older here |
| `warehouse/lock.py acquire` | 0 | 08:59 to 09:01 and 09:02 to 09:04 UTC |
| `restore_tables.py --no-redivis --out-dir runs/s454_restore` (five) | 0 | three from the archive, two from the bucket's stored copies |
| `archive/restore.py --from-bucket --out` (the two) | 0 | the latest run's rows |
| `erw_validate.py` (the restored files) | 0 | the scratch names first failed the file-name rule, so they were moved to proper names |
| `build_coverage.py --only` (the four) | 0 | `policy_reads_evidence` 5,143 rows, `price_board_spreads` 2,436 |
| `prove.py --fresh --only` (the five) | 0 | four equal; `datacenter_queue_positions` both differ (left) |

## Decisions made without you

1. `datacenter_queue_positions` left for the daily run's commit.
2. The archive's latest run taken for `grid_network_links`, although it has fewer rows: it is a rolling window, and the copy here was older.
3. No load: the chain's part says none.

## Files

- Changed: `warehouse/metadata/coverage.csv`, `docs/coverage.md` (two rows). New: this report.
- On this machine (not in git): the four tables, `runs/s454_before/`, `runs/s454_*`.

## Correction (session 460, 21 October 2026, 09:45 UTC)

Two of the four were wrong, and are undone. `policy_reads_evidence` and `price_board_spreads` held the archive's latest run's own copies: the run log's latest lines (GitHub's runs of 01:16 and 06:33 UTC on 20 October) record 3,362 and 2,408 rows with the data SHA-256 of the copies `restore_tables.py` gave, which this machine already held. `restore.py`'s replay keeps every key any run ever wrote, so its 5,143 and 2,436 rows included 1,781 and 28 keys the latest run no longer had; `prove.py` read that as "this machine behind", and this session took the replay. Session 460 put the exact copies back (coverage 3,362 and 2,408 again) and fixed `prove.py`: a copy that is the latest run's own, by its data SHA-256, is equal. The finding about `restore_tables.py` above is withdrawn: it was right. `grid_network_links` and `caiso_reliability_daily` stand (each rebuilt to the latest run's row count).
