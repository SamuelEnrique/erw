# Session 735 report: the replication, extended

22 October 2026, from 15:38 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-735` on `wip/735-allgrids` (cut from `wip/734-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 735. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the live set with the anon key, the warehouse's CSVs in `runs/archive_restore/`, and a local build.

## Read these first

- **`warehouse/replication/siting.py` computes the chain's new figures a second time.** It still uses the standard library only, run in its clean environment.
  - **With `--tables <folder>`**, the warehouse's own CSVs:
    - the node list's basis spread (724), for the three nodes, from `node_basis_daily`'s daily rows (its own linear quantile, as pandas computes it);
    - three zones' demand growth (728: N.Y.C., NORTH, .Z.SEMASS), from `eia930_subba_demand_hourly_2024` and `_2025`.
  - **The second card (734)**: its HB_HUBAVG figures, flat and flexible, set beside the replication's own all-in figures.
- **Against a build of this branch: 89 figures computed, 77 beside the page, 0 differ.** Every new figure equals the page's: the spreads 7.8679 and 9.8042, the zones 1.0759, -6.6983 and 0.3406, the card's 42.1271 and 32.2486.
- **Against production** (without 724, 728 and 734 served yet): 83 figures, 71 beside the page, 0 differ. The new figures read "not on the page" there.
- **Not replicated**: 726's kinds (words, not figures), and 729's and 730's work (none there; 730's functions are tested on their fixture).
- **The method note's "The replication"** gains the `--tables` line.

## What to review

1. `runs/chain_062/repl735c.out` on this machine: one line a figure.
2. `docs/methods/siting.md`, "The replication".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the replication against production, without and with `--tables` | 0 | 83 / 71 / 0 differ; 89 / 71 / 0 differ |
| `db_probe.py` | 1, then 0 | the first probe at 16:30 answered 1 and the build ran anyway (my command did not stop on it); the build's log holds no statement timeout. The probe at 16:31 answered 0 (1.49 s) |
| `npm ci`, `npm run build` (lock `s735`, beat) | 0 | |
| the replication against the build, `--tables runs/archive_restore` | 0 | 89 / 77 / 0 differ |

## The landing

With the next landing (735 onward).

## Decisions made without you

1. **Three zones, not nineteen**: one of each kind of figure (a gain, a fall, ISO-NE). The other sixteen use the same code path.
2. **The tables stay optional**: a reader without the warehouse's CSVs still runs the replication from the live set and the repository.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/replication/siting.py` (`table_rows`, `quantile`, `table_figures`, `--tables`, the card's figures), `docs/methods/siting.md`.
- New: this report.
