# Session 363 report: the Redivis draft current

20 October 2026, from 11:00 UTC, unattended, on lab-desktop (the data machine), the seventh session of the chain of 20 October, night (run beside session 362, whose archive comparison was still running). Model spend USD 0. Pulls: Redivis uploads only.

## Read these first

- **No draft was truly behind this machine except the new `node_basis_daily`, which the storage cap refused, and the item stopped there, as the prompt says.** `scripts/sync.py --check` (11:00 UTC, Redivis's own counts and newest timestamps, no export): 209 tables in coverage; 156 current, 49 behind (the runner's uploads are newer than this machine's copies), 2 diverged (`grid_network_links`, `price_board_latest`: newer here by one measure and older by the other), **1 ahead**, **1 not on Redivis**.
- **`eia930_generation_latest` was not ahead, and the draft holds the runner's version again.** `sync.py` called it ahead (2,410 rows here against the draft's 1,906 at the same newest hour, 19 October 05:00), and it was uploaded at 11:03 UTC. Session 362's comparison then showed the opposite: this copy is an older snapshot (504 keys a later run dropped, 1,906 values the runner's later run revised). At 11:33 UTC the table rebuilt from the archive (the runner's run, 1,906 rows) was uploaded to the draft in its place (count(*) 1,906). For a snapshot table `sync.py` judges ahead by rows at an equal newest hour, which is wrong when the snapshot's keys move: a ruling below.
- **`node_basis_daily`** (session 358's table, 949,995 rows, not on Redivis): **refused by the cap**, "This import would cause your account to exceed its free storage allotment of 10GB.", the second refusal of the day (10:25 and 11:03 UTC). Nothing was deleted from the draft to make room.
- The runbook (`docs/redivis/release-v1-runbook.md`) now has a section "The draft on 20 October 2026" with these counts, the cap, and what the click needs first; its counts read 135 tables and 3 metadata tables (138 with them), 41 held.

## What to review

1. `docs/redivis/release-v1-runbook.md`, the new section and the two counts.

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| Redivis uploads | the tables behind | 2 asked: 1 uploaded, 1 refused by the storage cap; with them the uploader's own `erw_coverage` and `erw_sources` (`erw_headers` skipped by the export cap, as every day since 15 October) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/sync.py --check --no-git` | 0 | read only, the counts above |
| `upload.py eia930_generation_latest node_basis_daily` (data lock) | 1 | the refusal of `node_basis_daily`; the other uploads count(*) equal |
| the archive's rebuild of `eia930_generation_latest` uploaded in place of this machine's (data lock, `runs/s363_revert.py`, not in git) | 0 | count(*) 1,906 |

## Decisions made without you

1. **The 49 "behind" tables were left alone**: the draft is newer than this machine for them, which is the draft current; restoring this machine from it is what the export cap forbids since 15 October.
2. **The two "diverged" tables were not uploaded**: the draft is newer by its timestamps, and an upload would put an older table over it.

## For Samuel's ruling

- **`scripts/sync.py`'s "ahead" for a snapshot table**: judged by row count at an equal newest timestamp, it called an older snapshot ahead. Compare by the archive's row hashes instead (as `warehouse/archive/prove.py` does), or never call a snapshot table ahead by rows alone?
- **Redivis storage, 10 GB free, full** (with session 358's report): a paid tier, or tables to take out of the draft, before `node_basis_daily` can be drafted and before release v1 can hold every table `tables.csv` lists.

## Files

- Changed: `docs/redivis/release-v1-runbook.md`, `warehouse/metadata/redivis_uploads.csv`.
