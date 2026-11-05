# Session 698 report: EIA-930's demand by sub-region, 2020, written

23 October 2026, from 00:56 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **`eia930_subba_demand_hourly_2020` is written: 719,312 rows, 82 sub-regions, every hour of 2020** (2020-01-01T00 to 2020-12-31T23 UTC), from session 697's saved pages (89 reused) and 62 new requests for August to December. Validated, archived (archive run `20261023T010236Z-local`), in coverage (sector power, public), in the release package, both holds, named by the sub-region note (`docs/methods/eia930_subba_demand.md`, which also gained 2021, session 696). 24 of the 82 sub-regions are short of 8,784 hours, 976 hours in all.
- **The cross-check against `ferc714_area_demand_2020`** (61,436 hours in common), the sub-regions summed by parent and hour, median ratio: CAISO 0.9940, ERCOT 0.9984, NYISO 0.9997, PJM 1.0002, ISO-NE 0.9830, SPP 1.0240; PNM 1.42, as in every earlier year (its sub-regions are not its whole planning area). SPP is 2.4 percent above FERC at the median in 2020, against 0.2 percent below in 2021. In 2020 CAISO agrees best with FERC's hours moved one hour (mean difference 138 MW, against 1,003 MW as stamped); 2021 did not show it.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 62 of 90 | route `electricity/rto/region-sub-ba-data`, August to December 2020 (session 697's 89 pages reused) |

## Decisions made without you

- The metadata patch conflicted with the 2021 table's adjacent line in `docs/coverage.md`; resolved with `runs/s622/resolve_ours_plus.py` (the branch's lines kept, the 2020 line added).
- The cross-check is session 684's script with the year changed (`runs/c045/s698_xcheck.py`).

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session698.py`, this report. Changed: `docs/methods/eia930_subba_demand.md`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`. On the data machine only: the saved pages, `runs/s697_*`, `runs/s698_*`, `runs/c045/s698_*`.
