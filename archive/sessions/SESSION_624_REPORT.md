# Session 624 report: tanker and barge movements from 1986

22 October 2026, from 03:48 UTC, on lab-desktop (the data machine), a session of `queue/done/039-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_padd_rail_barge_movements_monthly` now runs from January 1986**: 120,742 rows (64,560 new), 689 series.
  - EIA's tanker and barge route begins in 1986-01. The rail route begins in 2010-01: EIA's metadata says so, and the early window holds no rail record.
  - 1986 to 2009 is a window of its own (`SPLIT`, `EARLY_END`), so session 622's 13 saved pages of 2010 on answered again.
- **Cross-checks**:
  - All 56,182 rows of 2010 on are unchanged.
  - For 1986 to 2009, EP00 (crude oil and products) equals crude (EPC0) plus products (EPP0) on 3,931 of 3,935 pair and month keys.
  - The four that differ are EIA's own: 390 kbbl appears in February 1989 under PADD 3 in the parts and under PADD 5 in the total (R10-R30 and R10-R50), and PADD 2 from PADD 5 (R20-R50) has parts of 445 and 73 kbbl in December 1988 and January 1989 against a total of 0. They are kept as EIA gives them.
  - All movements by tanker and barge between PADDs: 721 million barrels in 1986, 634 in 1995, 589 in 2005, 536 in 2009.
- **Written under the data lock** (03:50 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (64,560 rows archived). The table's release rows were replaced; the release check exited 0.
- Chain 038's landing (`5283179e`) deployed on Vercel at 03:47 UTC; s623-before against s623-after: 0 differences. The queue move after it (`81beb651`) was rate limited.

## Decisions made without you

- The connector's ceiling is now 20 a run (it was 17): 2010 on is answered by saved pages, and the early window is about 13 pages.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 16 of 25 | both routes' metadata, the trial (14: 13 of tanker and barge's early window, 1 empty of rail's) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_padd_movements.py`, `docs/redivis/release-v1/{tables,variables}.csv`, coverage and the archive manifest.
