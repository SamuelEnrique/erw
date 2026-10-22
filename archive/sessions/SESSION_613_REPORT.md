# Session 613 report: EIA-930's demand by sub-region, 2025, written

22 October 2026, from 01:51 UTC, on lab-desktop (the data machine), a session of `queue/done/037-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia930_subba_demand_hourly_2025`: 723,617 rows, 83 sub-regions, every hour of 2025** (00:00 UTC on 1 January to 23:00 on 31 December), demand in MW.
  - Built from session 612's saved pages (January to July and part of August) and this session's 62 requests (the rest), in twelve monthly windows of EIA's hour-ending periods.
  - Each month's records equal the rows read (from 55,770 in February to 61,740 in October).
  - The sub-regions are under eight parents: CISO, ERCO, ISNE, MISO, NYIS, PJM, PNM and SWPP.
  - 75 sub-regions miss some hours: 3,463 hours in all, the shortest 8,568 of 8,760. They are counted in the header and never filled.
- **Cross-check, against FERC Form 714's 2025 planning-area demand** (`ferc714_area_demand_2025`). The ERW holds no 2025 EIA-930 demand by balancing authority on this machine: `eia930_all_demand` starts on 26 August 2026, and the history table here covers early 2018 only. The sub-regions were summed by parent and hour, only where every sub-region of the parent is given (60,905 hours in common).

  | Parent | FERC 714 respondent | Hours | Median ratio | Min | Max |
  |---|---|---|---|---|---|
  | CISO | 24 | 8,711 | 0.993 | 0.824 | 1.094 |
  | ERCO | 58 | 8,686 | 1.008 | 0.933 | 1.190 |
  | ISNE | 76 | 8,760 | 0.981 | 0.874 | 1.139 |
  | NYIS | 100 | 8,758 | 1.000 | 0.815 | 1.118 |
  | PJM | 119 | 8,734 | 1.005 | 0.923 | FERC 0 MW in some hours |
  | PNM | 125 | 8,568 | 1.373 | 1.109 | 1.620 |
  | SWPP | 146 | 8,688 | 0.932 | 0.465 | FERC 0 MW in some hours |

  - Five parents agree at the median within 2%.
  - PNM's sub-regions sum to 1.37 times PNM's FERC planning area, and SPP's to 0.93 of SPP's. The sub-regions and the planning areas are not the same territory; I did not look further.
  - **The hours do not line up the same way for every parent.**
    - With FERC's hours moved one hour earlier, the mean difference falls for ERCO (1,552 to 974 MW), ISNE (439 to 326), NYIS (339 to 171) and PJM (1,900 to 1,023).
    - CISO's falls with FERC's hours moved one hour later (935 to 367).
    - The sub-regions follow EIA-930's convention, the same as `eia930_all_demand`, which session 602 checked. The difference is between EIA-930 and FERC 714 as PUDL gives it, not settled here.
- **Written under the data lock** (01:59 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (723,617 rows archived). Release rows added; `licenses.py check` 0 problems (278 tables). **Held** from `/data` and Redivis v1. MISO is a parent here as EIA publishes it: nothing was asked of MISO's servers.

## For Samuel's ruling

- Whether EIA-930's 2025 demand by balancing authority should come onto the data machine (from the archive's members of the history table) so a year table like this one can be checked against EIA's own parents.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 62 of 90 | 2025, August to December (612's pages reused) |

## Files

- New: this report. Changed: the release package, coverage and the archive manifest.
