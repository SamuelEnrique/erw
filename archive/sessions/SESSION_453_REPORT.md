# Session 453 report: the NOAA weather tables, refreshed

21 October 2026, from 08:45 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 21 October, day (`queue/done/018-day-21-october-data.md`). Model spend USD 0. Pulls: NOAA, 35 requests through `noaa_grid_weather.py --refresh` (388 files reused). 17,165 rows were counted against the year's ceiling: **2,829,911 of 6,000,000 in 2026** (2,812,746 before).

## Read these first

| Table | Newest before | Newest after | Rows before, after |
|---|---|---|---|
| `noaa_station_weather_hourly` | 11 Oct 03:00 UTC | **18 Oct 03:00 UTC** | 4,735,433, 4,747,179 |
| `noaa_grid_weather_hourly` | 11 Oct 03:00 UTC | **18 Oct 03:00 UTC** | 1,902,921, 1,907,625 |
| `noaa_grid_weather_daily` | 10 Oct | **17 Oct** | 118,336, 118,630 |
| `noaa_grid_weather_stations` | (static, 2019) | the same | 245, 245 |

- Validated, archived (16,989 rows new or changed across the four) and coverage rebuilt with `--only`. NOAA's data reach 18 October: the newest hours lag a few days at the source.
- **No load**: no NOAA table is in the live set (`load.py --only '^noaa_' --dry-run`: "no live-set table matches"; the three grid tables are under `catalogue_hold`).
- Memory first: 8.52 GB free.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py`, `scripts/duty.py beat` | 0, 0 | |
| `warehouse/lock.py acquire` | 0 | 08:45 UTC; released 08:56 UTC |
| `noaa_grid_weather.py --refresh` | 0 | 35 requests |
| `erw_validate.py` (the four) | 0 | |
| `archive.py write`, `build_coverage.py --only` | 0, 0 | |
| `load.py --only '^noaa_' --dry-run` | 1 | no live-set table matches; nothing loaded |

## Decisions made without you

1. No load: the tables are not in the live set.

## Files

- Changed: `warehouse/metadata/coverage.csv`, `docs/coverage.md`, `warehouse/metadata/archive_manifest.csv`, `warehouse/metadata/sources.csv` (the four tables' rows). New: this report.
