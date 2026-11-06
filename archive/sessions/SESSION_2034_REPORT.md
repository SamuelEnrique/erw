# Session 2034 report: the mines (MSHA's open government data)

23 October 2026, from 19:28 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 8 requests of 20 (below).

## Read these first

- **Two tables written, validated, archived, in coverage (sector coal, public), in the release package, both holds:**
  - `msha_coal_mines`, entities: all 35,736 coal mines MSHA lists (active 705, suspended 592 and retired 34,439 by the ERW's words; MSHA's own, Active, New Mine, Temporarily Idled, NonProducing, Abandoned and Abandoned and Sealed, kept in `x_mine_status`), each with its operator, controller, state and county, type (surface, underground, facility), status date and, where MSHA gives both, its latitude and longitude. The mine id keeps MSHA's seven digits; EIA's coal tables drop the leading zero.
  - `msha_coal_production_quarterly`, series: each coal mine's quarter from 2010 to the second quarter of 2026, its subunits summed: `coal_production` (short tons), `employee_hours` and `average_employees` (counts), 294,323 rows for 3,378 mines. A quarter whose production every subunit leaves empty has no production row; where only some do, the others are summed and the empty ones counted in `x_production_blank`.
- **The cross-check against `eia_coal_mine_production_annual`:** MSHA's production summed to the year is within 0.21 percent of EIA's every year from 2010 to 2024 (1,086.4 against 1,084.4 million short tons in 2010; 512.548 against 512.540 in 2024). In 2024 all 773 mines in EIA's table are in MSHA's; 772 are within 5 percent of EIA's figure, and all 76 mines over a million tons. MSHA lists 1,150 mines that year: the rest report hours or employees with little or no production.
- **The source:** MSHA's Open Government Data page (`arlweb.msha.gov`), the pipe-delimited `Mines.zip` and `MinesProdQuarterly.zip`, refreshed weekly (both last modified 23 October 2026, 11:58 UTC), with their definition files. arlweb.msha.gov has no robots file.
- **MSHA's verdict: "U.S. Department of Labor, Mine Safety and Health Administration (MSHA)", may be public** (read 211, the Department of Labor's Copyright page): "Materials created by the federal government are generally part of the public domain and may be used, reproduced and distributed without permission."

## The pulls

1. `arlweb.msha.gov/robots.txt` (read 209): HTTP 404, no robots file. 2. The Open Government Data page. 3. `www.dol.gov/robots.txt` (read 210). 4. The Department of Labor's Copyright page (read 211). 5 to 8. `Mines.zip` (7.3 MB), `MinesProdQuarterly.zip` (54.7 MB) and the two definition files, saved in `warehouse/raw/msha_mines/` and reused by the write (`--offline`).

## Decisions made without you

- **Coal mines only** (MSHA's coal indicator C); metal and non-metal mines are not taken.
- **Quarters from 2010,** not from 2000, to keep the table near 300,000 rows; `--from-year` takes earlier years.
- **Employee hours in `count`:** the unit vocabulary's `hour` is an hour of the day (Decision 29), so hours worked are a count of hours, said in the header. No new unit.
- **MSHA's statuses mapped to the data standard's words,** MSHA's own kept beside them: New Mine as active, NonProducing as suspended.
- **A mine with only one of its two coordinates has neither** (six mines), so the validator's pair rule holds; a zero coordinate is left empty too.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/msha_mines.py`, `tests/test_session2034.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (209 to 211), `license_verdicts.csv` (MSHA), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/s2034/`, `runs/license_reads/s2034/`, `runs/s2034*`, `warehouse/raw/msha_mines/`.
