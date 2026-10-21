# Session 437 report: the Redivis draft, what fits

21 October 2026, from 07:38 UTC, unattended, on lab-desktop (the data machine), the seventh session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`), run while session 436's archive proof runs in the background. Model spend USD 0. Pulls: Redivis's metadata through `scripts/sync.py --check` (table counts and newest times, no export); **no upload** (below).

## Read these first

- **No upload was made: this machine's permission settings refused it.** The command (`warehouse/lock.py acquire ...` then `warehouse/redivis/upload.py ercot_node_prices_hourly`) was refused before it ran, as an outward-facing write to a shared service. It was not retried and not worked around. The lock was never taken (`lock.py status`: free). The exact commands are under "To finish".
- **What is behind on Redivis**, from `sync.py --check` at 07:40 UTC: 212 tables, 206 current.
  - Two tables this machine holds newer, and so behind on Redivis, both of which fit:
    - `ercot_node_prices_hourly`: 720 rows more here, through 21 October 04:00 UTC; 101 MB in the internal draft.
    - `eia930_all_storage`: 24 rows more; 38 MB.
  - `grid_network_links` has diverged and is not uploaded from here: its copy here is older, so an upload would roll Redivis back.
  - `api_cost_ledger` is behind here.
  - The two tables held for storage stay held, as the chain says.
- **The bytes**: 9.306 GB in the drafts by Redivis's sizes; about 9.4 GB in use by the account's own count (its refusal of 20 October: 10.1 GB with a 0.7 GB import); **about 0.6 GB free**. The two held tables need more than that together. The 41 license-held tables (0.94 GB) leave the draft before the click anyway, and removing them first makes room for both. Written into `docs/redivis/release-v1-runbook.md` as "The draft on 21 October 2026 (session 437)".

## To finish

```
.venv\Scripts\python.exe warehouse\lock.py acquire --task "Redivis uploads that fit" --minutes 45
.venv\Scripts\python.exe warehouse\redivis\upload.py ercot_node_prices_hourly
.venv\Scripts\python.exe warehouse\redivis\upload.py eia930_all_storage
.venv\Scripts\python.exe warehouse\lock.py release
```

Each replaces its table in the draft (a delete, then the upload). A refusal for storage would leave the table out of the draft (session 385), but 0.6 GB free is far above the few hundred kilobytes each one grows. This machine's daily run uploads each table that moved, so they may go up at 17:00 UTC without a person.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `scripts/sync.py --check --no-git` | 0 | 206 current, 1 behind, 2 ahead, 1 diverged, 2 not on Redivis |
| `warehouse/redivis/upload.py ercot_node_prices_hourly` | not run | refused by the permission settings |

## Decisions made without you

1. `grid_network_links` not uploaded: the copy here is the older one.
2. The refused upload left to a person rather than tried another way.

## For Samuel's ruling

- The storage, with the bytes the two held tables need: more than the 0.6 GB free. Removing the 41 license-held tables from the draft now (0.94 GB) makes room.
- Whether an unattended session may upload to the Redivis draft (this machine's permission settings say no; the chain's part said yes).

## Files

- Changed: `docs/redivis/release-v1-runbook.md`. New: this report.
