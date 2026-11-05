# Session 684 report: chain 041's session 641, EIA-930's demand by sub-region for 2021

22 October 2026, from 10:44 UTC, on lab-desktop (the data machine), the first session of `queue/done/044-night-24-october-data.md`, done on chain 041's branch `wip/638-644-sources`. Model spend USD 0.

## Read these first

- **`eia930_subba_demand_hourly_2021` is written: 710,831 rows, 82 sub-regions, every hour of 2021** (2021-01-01T00 to 2021-12-31T23 UTC). Validated, archived, in coverage, in the release package (public), with session 640's two holds.
- **No request was made.** Every page of 2021 was saved: January to July by session 640, August to December by a run that started at 07:12 UTC (`warehouse/raw/eia930_subba/20261022T071223Z`, last written about 07:48 UTC): chain 041's session 641, which left no report and wrote no table before that chain stopped. Its requests were within that session's ceiling; their count is not recorded.
- **The cross-check against `ferc714_area_demand_2021`** (55,026 hours in common): six parents within 2% at the median: CAISO 0.9985, ERCOT 0.9992, NYISO 0.9997, PJM 1.0032, SPP 0.9977, ISO-NE 0.9839. PNM's sub-regions hold only 2,479 hours of the year (1.42 at the median, as earlier years). FERC's PJM series holds a few broken hours (a maximum ratio of 19,096), so its mean difference is not a measure.
- **Chain 041's branch is brought up to main** (chain 043 landed): `release_v1.py`'s held list joined both sides; `docs/coverage.md` and `coverage.csv` taken from main and chain 041's four tables' rows rebuilt in one `--only` build (`eia_refinery_production_monthly` from 2005, 326,819 rows; `eia_crude_imports_detail_monthly` from 2009, 183,393; `eia_ngl_production_monthly` from 1973, 110,896; and the 2021 table).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 0 of 90 | every page was saved |

## Decisions made without you

- The work of chain 041's session 641 is done here on its own branch, so chain 041 lands whole (session 686).
- The archive manifest kept the newest run's lines for chain 041's three tables (the same data, archived again by the combined run).

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `archive_manifest.csv`, `sources.csv`, `docs/licenses.md`, `license_tables.csv`, `docs/redivis/release-v1/`, `warehouse/redivis/release_v1.py` (the merge). On the data machine only: `runs/c044/`, `runs/c043/s684_*`.
