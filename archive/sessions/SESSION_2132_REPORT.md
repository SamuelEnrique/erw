# Session 2132 report: the package's and the site's records

23 October 2026, from 23:23 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`. Model spend USD 0. Pulls: none.

## Read these first

- **The records were stale:** `package/tools/build_tables.py --check` found 413 tables shipped and 418 in the license record, the 5 that differ being this chain's (`epa_lmop_landfill_projects`, `epa_tri_energy_releases_annual`, `eurostat_renewable_capacity_annual`, `owid_ember_electricity_annual`, `usgs_comcat_earthquakes_south_central`), and the site's two files lacking them.
- **Rebuilt:** `package/src/erw/data/tables.csv` (418 tables: public 310, internal 57, unsettled 51), `site/data/table_verdicts.json` and `site/data/table_citations.json`. The check passes after, and the tests of sessions 1001, 1008 and 1009 pass (22 tests). All five of this chain's tables are public, each crediting its publishers (Ember and Our World in Data together for the electricity table).

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
