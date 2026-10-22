# Session 634 report: EIA-930's demand by sub-region, 2022, written

22 October 2026, from 05:50 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia930_subba_demand_hourly_2022`: 712,831 rows, 82 sub-regions, every hour of 2022**, demand in MW.
  - Built from session 633's saved pages (January to July and part of August) and this session's 63 requests (the rest).
  - 38 sub-regions miss some hours: 5,489 hours in all. They are counted in the header and never filled.
  - The shortest is PNM's CYGA, which EIA gives from 07:00 UTC on 30 June 2022 (4,409 hours). PNM's other sub-regions have 8,736 hours each.
- **Cross-check against FERC Form 714's 2022 planning-area demand**, as sessions 613, 621 and 628 did (56,918 hours in common; PNM's only from 30 June, where all its sub-regions are given):

  | Parent | Hours | Median ratio | Min | Max |
  |---|---|---|---|---|
  | CISO | 8,757 | 1.000 | 0.881 | 1.103 |
  | ERCO | 8,759 | 1.001 | 0.918 | 1.105 |
  | ISNE | 8,760 | 0.984 | 0.882 | 1.130 |
  | NYIS | 8,760 | 1.000 | 0.903 | 1.217 |
  | PJM | 8,713 | 1.003 | 0.488 | 1.111 |
  | PNM | 4,409 | 1.377 | 1.000 | 1.586 |
  | SWPP | 8,760 | 0.998 | 0.498 | FERC 0 MW in some hours |

  - Six parents agree at the median within 2%; PNM's sub-regions again sum to about 1.38 times PNM's planning area.
  - The hours fit FERC one hour earlier for ERCO, ISNE, NYIS, PJM and SWPP. For CISO, one hour later is again the closest (471 MW against 613 as stamped), less clearly than in the later years.
- **Written under the data lock** (05:59 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (712,831 rows archived). Release rows added; `licenses.py check` 0 problems (289 tables). **Held** from `/data` and Redivis v1.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 63 of 90 | 2022, August to December (633's pages reused) |

## Files

- New: this report. Changed: the release package, the license record, coverage and the archive manifest.
