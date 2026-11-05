# Session 602 report: EIA-930's demand by sub-region, hourly, the last 90 days

22 October 2026, from 00:40 UTC, on lab-desktop (the data machine), a session of `queue/done/035-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia930_subba.py`: each EIA-930 sub-region's demand by hour**, from EIA's API v2 (route `electricity/rto/region-sub-ba-data`), as `eia930_subba_demand_hourly`.
  - 186,177 rows: 89 sub-regions under their parent balancing authorities (PJM's, SPP's, NYISO's, ERCOT's, CAISO's, MISO's, ISO-NE's and smaller ones), from 24 July 2026 00:00 to 21 October 2026 06:00 UTC.
  - The entity is `eia930_subba:<parent>:<subba>`.
- **The ERW's EIA-930 conventions**: demand as `demand_mw` in MW (EIA's megawatthours in the hour, the hour's mean), and the hour's start as `ts_utc`, which is EIA's hour-ending period less one hour, as `warehouse/connectors/eia930.py` does.
- **Hours missing, as EIA gives them**: every sub-region is short of the window's 2,160 hours, 6,063 hours missing in all.
  - EIA's sub-region data lag: the newest hour is 06:00 UTC on 21 October.
  - Some hours are not given.
  - Nothing is filled, and the header says how many are missing.
- **MISO's sub-regions are EIA's data**, read from EIA's servers. MISO's pause (`paused_sources.csv`) concerns requests to MISO, and no request went to MISO.
- **Cross-check**: the sub-regions summed by parent and hour (the hours where every sub-region is given) against `eia930_all_demand`'s demand.

  | Parent | Median ratio | Hours |
  |---|---|---|
  | CAISO, SPP | 1.0000 | 1,344 and 1,296 |
  | ERCOT | 1.0001 | 1,156 |
  | NYISO | 0.9997 | 1,252 |
  | MISO | 0.9932 | 1,344 |
  | PJM | 0.9912 | 1,324 |
  | ISO-NE | 0.9852 | 1,132 |

  That the sums line up hour by hour also confirms the hour convention.
- **Written under the data lock** (00:46 UTC) with `--through 2026-10-22 --offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session602.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 39 of 60 | one day (the probe); the trial (38) |

## Decisions made without you

1. The last 90 whole days only, as the chain asks. The history from 2019 would be about 900 pages, for a later run if wanted.

## Files

- New: `warehouse/connectors/eia930_subba.py`, `tests/test_session602.py`, this report. Changed: the shared metadata, holds and package.
