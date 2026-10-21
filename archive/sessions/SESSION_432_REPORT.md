# Session 432 report: iso_queue_statistics rebuilt whole

21 October 2026, from 07:12 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`). Model spend USD 0. Pulls: none (the six queue tables held here).

## Read these first

- **The reader's fix was already on main**: `005b590d` (session 367, "queue_statistics reads its inputs by the header's count of lines, not comment="#""), which is an ancestor of `origin/main`. Nothing was cherry-picked. `task/367-372` holds no commit main lacks.
- **868 positions regained their queue date**: ERCOT 455, CAISO 169, NYISO 104, ISO-NE 94, MISO 30, SPP 16.

  | ISO | Positions entered (before, after) | Undated (before, after) |
  |---|---|---|
  | ERCOT | 1,302, 1,757 | 456, 1 |
  | CAISO | 2,109, 2,278 | 169, 0 |
  | NYISO | 1,710, 1,814 | 104, 0 |
  | ISO-NE | 1,657, 1,751 | 94, 0 |
  | MISO | 3,845, 3,875 | 36, 6 |
  | SPP | 3,014, 3,030 | 64, 48 |

  ERCOT's MW entered went from 306,952 to 438,194; its operating positions from 449 to 589 and its waiting ones from 853 to 1,168.
- **The table keeps its 1,511 rows**, with the same keys (no row only before or only after); 474 values changed. The live set took the 474 (`written 474, deleted 0`).
- **Through the gate**: `scripts/db_probe.py` open before the comparison read (0.53 s), before the load (0.45 s) and after it (0.45 s).
- **The loader vacuums `series` whole after every load**, even this one of 474 rows (`VACUUM (ANALYZE)`, `load.py` since session 45). On a 2.1 GB table that is disk work on every load, which matters for `docs/state/database_2026-10-21.md`'s first cause. Recorded there for Samuel; not changed.

## Steps

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | (session 431's, the same hour) |
| `warehouse/lock.py acquire --task "session 432: ..." --minutes 60` | 0 | 07:14 UTC; released 07:21 UTC |
| `warehouse/derived/queue_statistics.py` | 0 | 1,511 rows, 6 ISOs, entry years 1989 to 2026; this machine held no copy before |
| `erw_validate.py warehouse/output/iso_queue_statistics.csv` | 0 | 139 entities, 14 variables |
| `warehouse/archive/archive.py write --tables '^iso_queue_statistics$'` | 0 | 1,511 rows new or changed (the first copy from this machine), to the bucket |
| `build_coverage.py --only '^iso_queue_statistics$'` | 0 | its row: the retrieved time only |
| `load.py --only '^iso_queue_statistics$' --dry-run`, then for real | 0, 0 | 1,511 selected; 474 written, 0 deleted; the database 2,318.1 MB before and after |
| `runs/s375_splice.py write iso_queue_statistics`, `release_v1.py --check` | 0, 0 | the package row's description is now the table's own first header line (it was the restore's note); 138 in v1 with the metadata tables, 2 held, 42 out; 0 differences |

Rule 8 for the load: `s432-load-before` and `s432-load-after`, 0 differences on 25 pages, expected (every page is in review, and no page in the snapshot reads the table).

## The method note

`docs/methods/energy_projects.md`, "Queue statistics": the line "A fault in the first build (session 367)" is replaced by "Rebuilt whole on 21 October 2026 (session 432)", with the positions regained counted, and the undated counts of "The entry year" are the rebuild's.

## Decisions made without you

1. No cherry-pick: the fix was on main.
2. The comparison read of the live copy (1,511 rows) made behind the gate, to count what the rebuild changed.
3. The release package's row spliced, which also replaces its description (the restore's note) with the table's own.

## Files

- Changed: `docs/methods/energy_projects.md`, `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `docs/redivis/release-v1/tables.csv`.
- On this machine (not in git): `warehouse/output/iso_queue_statistics.csv`, `runs/s432_*.out`.
