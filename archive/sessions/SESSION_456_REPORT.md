# Session 456 report: the live set's two largest tables, sized for a ruling

21 October 2026, from 09:08 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 21 October, day (`queue/done/018-day-21-october-data.md`). Model spend USD 0. Pulls: none. Reads only, behind the gate. No change to `live_set.yaml`.

## Read these first

- **The note: [`docs/state/live_set_size_2026-10-21.md`](../../docs/state/live_set_size_2026-10-21.md).**
- **`node_basis_daily` has no reader in Supabase.** The pages read `node_basis_summary` (1,260 rows). No line of the site, the `erw` package or Ask names `node_basis_daily`. Its 957,969 live rows are 27% of `series`, about 600 MB, and taking it out of the live set loses nothing a visitor sees. Windows of 365, 90 and 35 days would keep 909,579, 216,771 and 140,874 rows.
- **`ercot_rtm_price_adders`** has one reader, the datacenter answers, which read one variable of eight (`rtorpa_mean`, bounded in time). Keeping only that variable frees about 310 MB; keeping only the page's rows (from August 2024, 11,786) about 370 MB.
- Together the two tables are 43% of `series` (about 970 MB). The rest is about 1.2 GB, still over the 512 MB of shared buffers, so the compute tier remains a question.
- Three pages' reads timed now: 0.03 to 0.08 s each (a quiet database).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py`, `scripts/db_probe.py` | 0, 0 | 0.54 s |
| the two tables' rows by window and variable (from `warehouse/output`) | 0 | `runs/s456_sizes.out` |
| the three reads and the index sizes | 0 | `runs/s456_reads.out` |
| the site, package and Ask searched for the two tables' readers | | `site/lib/nodebasisread.ts`, `site/lib/datacenter/answers.ts` |

## Decisions made without you

1. The sizes are estimated from `series`' average of 623 bytes a row, said so in the note.

## For Samuel's ruling

- `node_basis_daily` out of the live set (about 600 MB, no reader).
- `ercot_rtm_price_adders` cut to `rtorpa_mean` (310 MB) or to the page's rows (370 MB).

## Files

- New: `docs/state/live_set_size_2026-10-21.md`, this report.
