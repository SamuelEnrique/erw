# Session 621 report: EIA-930's demand by sub-region, 2024, written

22 October 2026, from 03:10 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia930_subba_demand_hourly_2024`: 726,716 rows, 83 sub-regions, every hour of 2024** (8,784 hours, a leap year), demand in MW.
  - Built from session 620's saved pages (January to June and part of July) and this session's 65 requests (the rest).
  - Each month's records equal the rows read (from 57,360 in February to 61,752 in December).
  - 64 sub-regions miss some hours: 2,356 hours in all, the shortest 8,337 of 8,784. They are counted in the header and never filled.
- **Cross-check against FERC Form 714's 2024 planning-area demand**, as session 613 did (60,858 hours in common):

  | Parent | Hours | Median ratio | Min | Max |
  |---|---|---|---|---|
  | CISO | 8,722 | 0.998 | 0.842 | 1.119 |
  | ERCO | 8,754 | 1.006 | 0.865 | 1.249 |
  | ISNE | 8,784 | 0.981 | 0.874 | 1.138 |
  | NYIS | 8,781 | 1.000 | 0.837 | 1.109 |
  | PJM | 8,735 | 1.006 | 0.921 | 1.107 |
  | PNM | 8,322 | 1.378 | 1.123 | 1.700 |
  | SWPP | 8,760 | 0.999 | 0.496 | FERC 0 MW in some hours |

  - Six parents agree at the median within 2%. PNM's sub-regions again sum to about 1.38 times PNM's planning area.
  - SPP's ratio is 0.999 in 2024 against 0.932 in 2025 (session 613): a change in SPP's sub-regions or its FERC filing between the years, not looked into.
  - The hours again fit FERC one hour earlier for ERCO, ISNE, NYIS, PJM and SWPP, and one hour later for CISO: the same pattern as 2025.
- **Written under the data lock** (03:15 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (726,716 rows archived). Release rows added; `licenses.py check` 0 problems (282 tables). **Held** from `/data` and Redivis v1.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 65 of 90 | 2024, July to December (620's pages reused) |

## Files

- New: this report. Changed: the release package, the license record, coverage and the archive manifest.
