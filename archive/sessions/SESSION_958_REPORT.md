# Session 958 report: uranium mined and milled in the U.S. (EIA's Domestic Uranium Production Report)

23 October 2026, from 12:51 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`, the second of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: 8 requests of 20 (www.eia.gov's robots file, asked in a call of its own and read first; the weekly coal production page and its workbook; the uranium report's page; its four workbooks).

## Read these first

- **First looked at, not taken: EIA's weekly coal production.** Its workbook holds only the latest three weeks, the year to date and the 52 weeks; the history sits under EIA's archive, which its robots file disallows.
- **Why this source instead:** the ERW holds the uranium utilities buy (`eia_uranium_marketing_annual`) and the reactors that burn it (`nrc_power_reactors`), not the domestic supply. EIA's Domestic Uranium Production Report gives each U.S. facility's quarterly production and the state of every mill and in-situ recovery plant.
- **Two tables written, validated, archived, in coverage (sector uranium, public), in the release package, both holds:**
  - `eia_uranium_production_quarterly` (series, 171 rows): pounds of U3O8 produced at each of 8 facilities and in all, Q2 2025 to Q2 2026 (1.09 million pounds in Q2 2026, against 0.48 a year before); and the number of mills and plants producing, by kind, at the end of each year from 2000 and of Q2 2026.
  - `eia_uranium_facilities` (entities, 24): 4 mills and heap leach facilities (capacity in short tons of ore a day) and 20 in-situ recovery plants (pounds of U3O8 a year), each with owner, county and state, and EIA's operating status at the end of 2025 and of each 2026 quarter (operating, standby, developing, permitted and licensed, restoration, reclamation and the rest).
- **The checks:** the total row equals the facilities summed in all five quarters; the six facilities producing in Q2 2026 (White Mesa, Alta Mesa, Lost Creek, Ross, Smith Ranch-Highland, Willow Creek) are the six Table 2 counts (one conventional mill, five in-situ plants), and each has the status "operating"; Burke Hollow and Hobson, also "operating", produce through Hobson's plant, as EIA's note says.

## Decisions made without you

- **`status` empty, EIA's statuses in `x_status_<period>`:** EIA's words ("standby", "restoration", "partially permitted and licensed") are not the vocabulary's.
- **A count at a year's end dated that year's 1 January,** `freq` P1Y, as the ERW dates a year; the latest quarter's at that quarter's first day.
- **EIA's marks have no row:** 8 "-" (no production) and 1 "." (withheld or not available).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_uranium_production.py`, `tests/test_session958.py` (5 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv` (one row for the two tables, merged by hand after the resolver), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s958/`, `runs/license_reads/s958/`, `runs/s958*`, `warehouse/raw/eia_coal_weekly/`, `warehouse/raw/eia_uranium_production/`.
