# Session 362 report: the archive proven

20 October 2026, from 10:52 UTC, unattended, on lab-desktop (the data machine), the sixth session of the chain of 20 October, night. Model spend USD 0. Pulls: none (the erw-archive bucket read, and written under the data lock; Redivis not read).

## Read these first

- **Seven tables of coverage could not be rebuilt whole from the archive, and now can.**
  - **The five tables of this chain** (`price_years_by_window`, `node_basis_daily`, `node_basis_summary`, `ercot_node_prices_hourly`, `ercot_4cp_intervals`) had nothing archived: they were written today and no archive step had run. Archived from this machine's copies (run `20261020T112045Z-local`, 1,452,397 rows, 0 deleted) and proved again: each rebuilds equal, rows, newest timestamp and the hash of its sorted rows.
  - **`api_cost_ledger` and `eia930_all_storage`** (both rolling-window tables, whose keys the archive never deletes) held rows only this machine had: four model calls of 15 October 2026 at 16:22 UTC (their request ids are in the CSV) and ERCOT's battery output for every hour of 15 October 2026 (24 rows). Neither the archive, the runner's tables nor the live set held them. **Only those 28 rows were archived**: archiving this machine's copies whole would have put 1,056 older storage values back over the archive's newer ones, so the archive's own rebuild plus the missing keys went through the archive's own writer (`warehouse/archive/prove.py --fill`). Checked after: the archive holds every key this machine holds, and its newer values stand.
- **Of the 209 tables: 126 equal, 24 where this machine is behind the archive, 54 that differ both ways, 5 not archived (above).** Every mismatch is listed with its cause in [`docs/state/archive_proof_2026-10-20.csv`](../../docs/state/archive_proof_2026-10-20.csv) (one row a table: the archive's rows and newest timestamp, this machine's, the rows on each side alone, and for the 54 the keys on each side alone and the keys revised).
- **The cause of nearly every mismatch is this machine, not the archive.** 110 tables' latest archived run is the GitHub runner's; this machine cannot restore the runner's newer copies since Redivis refused exports on 15 October (the daily `dm_sync` reads Redivis). Of the 54 that differ both ways, 47 hold no key the archive lacks: the archive's later runs revised values (EIA's revisions above all: `eia930_all_emissions` 337,383 rows revised, `carbon_intensity_hourly` 9,499) and added keys. The other seven: the two filled above, and five snapshot tables that can lose rows (`iso_rt_top_intervals`, `grid_network_nodes`, `grid_network_links`, `price_board_latest`, `eia930_generation_latest`), whose keys move each run, so a key only here is an older snapshot's, not a gap.
- **This machine's copies are stale for about 78 tables.** Session 357 met it (CAISO's battery stack) and session 363 too (below). A ruling: restore this machine from the archive, which `warehouse/restore_tables.py` can do (session 305), before its own builds read those tables.

## What to review

1. [`docs/state/archive_proof_2026-10-20.csv`](../../docs/state/archive_proof_2026-10-20.csv).
2. `warehouse/archive/prove.py`: the comparison, `--refine` (keys alone and revised), `--fill` (the missing keys alone, through `archive.archive_table`).

## Checks

| What | Exit | Notes |
|---|---|---|
| `prove.py` over the 209 tables | 0 | 10:52 to 11:20 UTC; the rebuilt files in a scratch folder, each removed after its comparison; `warehouse/output` untouched |
| `prove.py --refine` (the 54) | 0 | 11:20 to 11:27 UTC |
| `archive.py write --tables` the five new tables (data lock) | 0 | 5 tables, 1,452,397 rows, 0 deleted |
| `prove.py --fill api_cost_ledger eia930_all_storage` (data lock) | 0 | 4 and 24 rows archived, 0 deleted |
| the seven proved again | 0 | the five equal; the two with no key the archive lacks |

## Decisions made without you

1. **The comparison's hash is over the archive's own row hashes** (every column but `retrieved_at`, values as the archive normalizes them), sorted, so order and a run's retrieval time do not count.
2. **A snapshot table's keys found only here are not archived**: they belong to an older snapshot that a later run replaced, and archiving them would bring them back.
3. **The missing rows alone are written**, never this machine's copy whole, where the archive holds newer values (above).
4. **Nothing on this machine was replaced**, as the prompt says, though 78 tables here are older than the archive.

## For Samuel's ruling

- **Restore this machine from the archive** (`warehouse/restore_tables.py`, or `restore.py --out` table by table): 24 tables are behind and 47 more differ only by the archive's later revisions. Until then a data-machine build reads older inputs than the runner's.
- The four ledger calls of 15 October 16:22 UTC are in the archive now but not in the live ledger: whether to load them there too.

## Files

- New: `warehouse/archive/prove.py`, `docs/state/archive_proof_2026-10-20.csv`, this report.
- Changed: `warehouse/metadata/archive_manifest.csv`.
- Outside git: the archive's parts in the bucket (two runs: `20261020T112045Z-local` and the fill's), `warehouse/archive/` month files, `runs/archive_prove/prove.jsonl`.
