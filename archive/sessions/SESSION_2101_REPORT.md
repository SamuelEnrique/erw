# Session 2101 report: the shown rows follow the table

23 October 2026, about 18:30 to 18:40 UTC, unattended, on portable-laptop (the code machine), in `erw-828` (`wip/833-deals`) and the main checkout. Chain `queue/done/084-day-23-october-portable-deals-4.md`, session 2101. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request but GitHub and the ERW's own database. Rulings item 3's "until then" line: a code session regenerates the two committed files by hand.

## Read these first

- **The tables had moved.** The committed `site/data/deals_public.json` was as of the extraction of 22 October 15:02 UTC (505 deals); this machine's `warehouse/output/energy_deals.csv` is the extraction of 23 October 15:01 UTC (514 deals, 568 evidence rows), restored by `scripts/sync.py` at 18:09 UTC. The same for the datacenter tables (150 to 154 projects, 172 evidence rows).
- **Both files regenerated** with `warehouse/deals/public_rows.py` from the restored tables, on `wip/833-deals` (commit after `d78ef087`, pushed). **The 16 shown deals are the same 16** by event id; no deal moved into or out of the shown sort. The 9 new deals are 8 held and 1 unsettled:

| Tracker | Before (22 Oct) | After (23 Oct) |
|---|---|---|
| deals: shown, held, unsettled | 16, 486, 3 | 16, 494, 4 |
| datacenter projects: shown, held, unsettled | 0, 150, 0 | 0, 154, 0 |

- **The new unsettled deal**: `deal:871a7181a2ef97f3` (23 October, Solar Energy Corporation of India and ACME Solar), one evidence row from Energy-Storage.news, whose terms are not read (rulings item 2: the sweep that reads Energy-Storage.news and Electrek settles 4 deals now, not 3).
- **The new held deals** (8, dated 22 and 23 October): ChronoScale, Soluna and Applied Digital (Data Center Dynamics); QatarEnergy and Cheniere (Hart Energy, LNG Prime); Liberty (Hart Energy); Welspun (Reuters); QatarEnergy and Venture Global (Reuters); Google and Voltus (Heatmap News, Utility Dive); Nebius, Humain and DataVolt (Data Center Dynamics); Shell and ExxonMobil (Rigzone); Citi and Nebius; Neysa and STTGDC (Data Center Dynamics). The one new deal with a public source, SGE, Origin Nuclear and Ontario Power Generation (World Nuclear News, 22 October 12:02 UTC), was already in the 22 October file.
- The held publishers' top five for the datacenter projects: Data Center Dynamics 84 of 85 rows, Reuters 39 of 41, Bloomberg 16 of 17, WSJ 10, Financial Times 3.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2101"` | 0 | on duty |
| `public_rows.py --deals ... --evidence ... --json site/data/deals_public.json` | 0 | 16 shown, 494 held, 4 unsettled |
| `public_rows.py ... --datacenters site/data/datacenters_public.json` | 0 | 0 shown, 154 held |
| `pytest tests/test_session822.py test_session823.py test_session825.py test_session827.py` (`runs/s2101_tests.out`) | 0 | 30 passed |
| `git push origin wip/833-deals` | 0 | |

No build (free memory under the chain's line; the files are data, not components).

## Decisions made without you

1. The reader was run from `erw-828` with the main checkout's interpreter and explicit paths to the main checkout's `warehouse/output` (the worktree holds no output folder); the registry and the verdicts are the worktree's, merged with main in session 2100.
2. `scripts/sync.py --check` did not answer within two minutes and was left running in the background; the restored files' headers (23 October 15:01 UTC, today's run) were taken as current instead.

## For Samuel's ruling

- Item 3 of `docs/reviews/deals-rulings-2026-10-23.md` stands: the daily run writing the two files after the extraction would make this session unnecessary each day.

## Files

- Changed on `wip/833-deals`: `site/data/deals_public.json`, `site/data/datacenters_public.json`.
- New: this report, `runs/s2101_tests.out` (not in git).
