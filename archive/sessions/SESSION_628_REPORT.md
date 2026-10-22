# Session 628 report: EIA-930's demand by sub-region, 2023, written

22 October 2026, from 04:18 UTC, on lab-desktop (the data machine), a session of `queue/done/039-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia930_subba_demand_hourly_2023`: 717,332 rows, 82 sub-regions, every hour of 2023**, demand in MW.
  - Built from session 627's saved pages (January to July and part of August) and this session's 65 requests (the rest, with one HTTP 502 and one 504 asked again).
  - 24 sub-regions miss some hours: 988 hours in all, the shortest 8,711 of 8,760. They are counted in the header and never filled.
- **Cross-check against FERC Form 714's 2023 planning-area demand**, as sessions 613 and 621 did (61,268 hours in common):

  | Parent | Hours | Median ratio | Min | Max |
  |---|---|---|---|---|
  | CISO | 8,758 | 1.013 | 0.874 | 1.130 |
  | ERCO | 8,759 | 1.005 | 0.925 | 1.097 |
  | ISNE | 8,760 | 0.982 | 0.876 | 1.129 |
  | NYIS | 8,760 | 1.000 | 0.918 | 1.123 |
  | PJM | 8,711 | 1.006 | 0.918 | 1.324 |
  | PNM | 8,760 | 1.390 | 0.703 | 1.619 |
  | SWPP | 8,760 | 0.998 | 0.497 | 109.5 (an hour FERC gives near 0 MW) |

  - Six parents agree at the median within 2%; PNM's sub-regions again sum to about 1.39 times PNM's planning area.
  - The hours fit FERC one hour earlier for ERCO, ISNE, NYIS, PJM and SWPP, and one hour later for CISO, as in 2024 and 2025.
- **Written under the data lock** (04:39 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (717,332 rows archived). Release rows added; `licenses.py check` 0 problems (286 tables). **Held** from `/data` and Redivis v1.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 65 of 90 | 2023, August to December (627's pages reused), with two retries |

## Files

- New: this report. Changed: the release package, the license record, coverage and the archive manifest.
