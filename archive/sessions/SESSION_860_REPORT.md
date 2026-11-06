# Session 860 report: U.S. petroleum exports by destination

23 October 2026, from 02:13 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`eia_petroleum_exports_by_destination` is written: 45,058 rows, 281 series, January 2015 to July 2026**: U.S. exports of crude oil and of total petroleum products to each destination EIA names (201 countries and the U.S. total), in kbbl and kbbl/d (route `petroleum/move/expc`, the Petroleum Supply Monthly). Validated, archived, in coverage (sector oil;products, public), in the release package, both holds.
- **Why this source:** the ERW holds crude imports by country of origin (`eia_crude_imports_by_country`, `eia_crude_imports_detail_monthly`) but not where U.S. crude and products go, now the larger flow. It is outside chain 047's list, so no later session repeats it.
- **The window:** the route's 42 products since 2015 are 407,028 records (82 pages), more than the session's 20 requests; crude oil and total products from 2015 took 9 pages.
- **The cross-checks:** the U.S. crude total equals `eia_petroleum_snd_monthly`'s U.S. crude exports in every one of the 139 months (difference 0); the destinations sum to the U.S. total at a median of 1.0000 (0.993 to 1.063 by month and product).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 18 of 20 | two route listings, the route's metadata, three counts, the product facet, the trial's nine pages and one more that ended the read (the write reused all) |

## Decisions made without you

- Crude oil and total products only, from 2015, within the ceiling; the other 40 products and the years before are left for a later session.
- The daily rate named `exports_per_day`, as `eia_petroleum_snd_monthly` names it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_petroleum_exports.py`, `tests/test_session860.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s860/`, `runs/s860_*`.
