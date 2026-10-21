# Session 496 report: USGS's U.S. Wind Turbine Database

21 October 2026, from about 17:55 UTC, on lab-desktop (the data machine), a public source probed while the daily run held the data lock (the owner's instruction of 21 October: "if you run out of ruling-free work, probe another public source rather than idle"). Model spend USD 0.

## Read these first

- **`warehouse/connectors/uswtdb.py`: every utility-scale wind turbine in the United States**, as the entities table `uswtdb_wind_turbines`.
  - The U.S. Wind Turbine Database is published by USGS, Lawrence Berkeley National Laboratory and the American Clean Power Association, through USGS's public API (no key).
  - There are 77,839 turbines, 159,587 MW in all. Each turbine has its project, maker and model, hub height, rotor diameter, location and EIA plant id.
- **Robots and terms first.** `energy.usgs.gov` has no robots file (404), so by the convention every path is allowed. USGS's copyrights page (`www.usgs.gov/information-policies-and-instructions/copyrights-and-credits`) went through `license_read.py` into the record (record 87): "USGS-authored or produced data and information are considered to be in the U.S. Public Domain". Its verdict, "may be public", was cut by code into `license_verdicts.csv`.
- **Cross-check against `eia860m_operating_generators`** (run again on the written table by `runs/s497_crosscheck.py` on the data machine): the turbines' capacity is summed by EIA plant id and set against EIA-860M's wind nameplate.
  - 1,281 plants are in both (USWTDB names 1,348, and EIA-860M lists 1,387 wind plants).
  - The median ratio is 1.000, and 83.5% of plants are within 5%.
  - The totals are 154,420 MW against 157,493 MW.
- **A fault found in the trial**: the database's `image_date` is not an ISO date. The validator refused it, and the connector now writes it as YYYY-MM-DD.
- The database lists installed turbines and gives no status, so `status` is empty. A blank stays blank.
- Sector rule (`power`). Tests: `tests/test_session496.py`, 4. Written in session 489.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| energy.usgs.gov | 1 + 8 of 30 | robots file (404); the API's pages of 10,000 (the trial) |
| www.usgs.gov | 1 | terms page (record 87) |

## Decisions made without you

1. Built as public: USGS's own words put its data in the public domain.

## Files

- New: `warehouse/connectors/uswtdb.py`, `tests/test_session496.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `license_reads.csv`, `license_verdicts.csv`, `scripts/licenses.py`, `docs/licenses.md`.
