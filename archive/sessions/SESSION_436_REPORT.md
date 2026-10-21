# Session 436 report: the archive proven again

21 October 2026, from 07:30 UTC, unattended, on lab-desktop (the data machine), the sixth session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`). Model spend USD 0. Pulls: the archive bucket only. No database read, no load.

## Read these first

- **Of the 212 tables of coverage: 207 equal, 4 that differ both ways, 1 where this machine is behind, 0 where this machine is newer** ([`docs/state/archive_proof_2026-10-21.csv`](../../docs/state/archive_proof_2026-10-21.csv), one row a table, mismatches first). On 20 October session 362 counted 126 equal, 24 behind and 54 both ways, so session 373's restore and the day's runs closed nearly all of it.
- **Nothing to write to the archive**: no table holds rows here the archive lacks with none the other way ("archive behind"), so `prove.py --write` had nothing to do and was not run.
- **The five mismatches:**

  | Table | Status | Rows only here | Rows only in the archive | Why |
  |---|---|---|---|---|
  | `grid_network_links` | both differ | 15,216 | 7,680 | here to 13 October, the archive (GitHub's run of 20 October) to 17 October; the copy here is older, and `sync.py --check` calls it diverged (session 437) |
  | `price_board_spreads` | both differ | 3 | 31 | GitHub's run of 20 October revised and added rows after this copy |
  | `caiso_reliability_daily` | both differ | 2 | 2 | a revision of the same newest day (17 October) between this machine's run of 20 October and the archive's |
  | `datacenter_queue_positions` | both differ | 1 | 1 | one position revised (no time column) |
  | `policy_reads_evidence` | this machine behind | 0 | 1,781 | GitHub's run of 20 October, 01:16 UTC, archived them after this copy was written |

  All five are this machine's copies lagging or revised against the runner's, not a fault of the archive. The daily run's `dm_sync` restores the behind table, and `grid_network_links` the same way with `--refresh`.
- **The proof was stopped once for memory.** Claude Code stopped the background run at 210 of 212 tables because the machine ran low on memory while the session was idle. As the chain's rule says, it was started once more, in the foreground, where `prove.py` resumes from its results file: the last two (`eia930_all_emissions`, `noaa_station_weather_hourly`, the two largest) are equal. The five-minute probe loop of session 431 was stopped by the same check at 07:52 UTC and was not started again.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py`, `scripts/duty.py beat` | 0, 0 | |
| `warehouse/archive/prove.py --fresh` (background) | stopped | 210 tables done, stopped for low memory |
| `warehouse/archive/prove.py` (foreground, resumed) | 0 | 2 tables, equal; 212 in `runs/archive_prove/prove.jsonl` |

`warehouse/output` was not touched: each rebuilt file was compared in a scratch folder and removed.

## Decisions made without you

1. `--write` not run: no table is "archive behind".
2. The proof restarted once after the memory stop, as the chain says; the probe loop not restarted (its gate is run before each load instead).

## Files

- New: `docs/state/archive_proof_2026-10-21.csv`, this report.
