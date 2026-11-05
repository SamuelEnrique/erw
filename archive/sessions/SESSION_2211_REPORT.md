# Session 2211 report: the reservoirs behind Hoover and Glen Canyon (Reclamation's hydrodata)

24 October 2026, from 01:32 UTC, on lab-desktop (the data machine), the second session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: 15 requests of 15 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `usbr_mead_powell_daily`, Lake Powell's and Lake Mead's pool elevation, storage, total release and (Lake Powell only) inflow, a day, over each reservoir's whole period of record: 192,509 rows, Lake Mead's release from 1934 and its elevation from 1935, Lake Powell's from 1963, to 22 October 2026. The files are Reclamation's Upper Colorado region's hydrodata (`www.usbr.gov/uc/water/hydrodata/reservoir_data/<site>/csv/<data type>.csv`, site 919 Lake Powell, 921 Lake Mead), not data.usbr.gov's RISE API, which is not asked. Reclamation marks them provisional.
- **The units are Reclamation's own words,** since the files state none: the Lower Colorado levels page's note ("ft=feet above mean sea level, cfs=cubic feet per second, kaf=1000 acre-feet", read 346) and the Glen Canyon Dam page (elevation in feet, storage in acre-feet, read 347). **Two new units:** `ft` (Decision 71) and `acre-ft` (Decision 72); release and inflow use `ft3/s` (Decision 65). Chain 097 holds Decision 70, as its agent and this session agreed.
- **Lake Mead has no inflow file** (its dashboard lists none and the address answers HTTP 404); Lake Powell's inflow is taken.
- **The cross-check** (`runs/c098/s2211/cross.py`):
  - Lake Powell on 30 September 2026 is 3,518.08 feet and 5.16 million acre-feet in the table, the figures the Glen Canyon Dam page gives for the end of September.
  - Each dam's total release against the USGS gauge below it (`usgs_streamflow_daily`), 2020 to 2025: Hoover against the gauge below it, median 1.000 and within 10% on every one of 2,192 days; Glen Canyon against Lees Ferry, median 0.988 and within 10% on 99.7% (the Paria joins below the dam, above the gauge).
  - Hoover's monthly net generation (`usbr_hydropower_monthly`) against Lake Mead's mean elevation, 130 months of 2015 to 2025: correlation 0.262. Hoover's output follows the delivery schedule's releases more than the lake's head; the weak tie is a fact of the plant, not a fault of either table.

## The pulls

1. `www.usbr.gov/robots.txt` (read 345, read again; read 172 is session 2003's).
2. Lake Powell's hydrodata dashboard, for the files and data type codes.
3 and 4. Both lakes' pool elevation files.
5. Lake Powell's storage as JSON, for units (it states none).
6. The Lower Colorado levels page (read 346).
7. The Glen Canyon Dam status page (read 347).
8 to 15. The connector's trial: the four data types for both lakes (Lake Mead's inflow answering HTTP 404), saved and reused by the write (`--offline`).

Reclamation's terms are the record's (read 173, may be public).

## Errors

- **The connector first named a page not read** (`site_map.html`) as its source page; corrected to Lake Powell's dashboard, which was.
- **The trial stopped on Lake Mead's missing inflow file** with the ceiling spent; inflow is now Lake Powell's only and the write read the saved files.
- **The first Hoover comparison mixed gross and net generation rows;** recomputed on net generation (the same correlation).
- **`tests/test_session205.py`'s bound raised once more** for this chain's reads (323 to 326 on its branch).

## Decisions made without you

- **The whole period of record taken,** not from 2015 as the file suggested: the files hold it and nothing is lost by keeping it.
- **`ft` and `acre-ft` as Decisions 71 and 72,** Reclamation's units, never converted.
- **`geo` US-AZ for both dams** (each on Arizona's border).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usbr_colorado_reservoirs.py`, `tests/test_session2211.py`, this report.
- Changed: `docs/datastandard.md` (Decisions 71 and 72), `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (324 to 326), `tests/test_session205.py`, the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c098/s2211/`, `runs/license_reads/s2211/`, `runs/s2211_*`, `warehouse/raw/usbr_colorado_reservoirs/`.
