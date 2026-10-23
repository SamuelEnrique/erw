# Session 2020 report: a source of its own choosing: the rest of Tracking the Sun, and its table

23 October 2026, from 18:50 UTC, on lab-desktop (the data machine), the first of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`'s two sessions of a source of its own choosing. Model spend USD 0. Pulls: 19 requests of 20 (the 2024 edition's other nineteen state files on the OEDI data lake, through the connector; its listing was reused from session 2015's saved copy). The write reused every saved file (`--offline`).

## Read these first

- **Why this source:** session 2015 found Berkeley Lab's Tracking the Sun as 27 state files, past its ceiling of 15, and fetched eight. The ERW held distributed solar only as EIA-861's capacity by state and utility, with no size, price, segment, battery or year of installation. Taking the other nineteen under this session's ceiling finishes the one table the chain asked for, rather than starting a second source and leaving the first half-held.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `lbnl_tracking_the_sun`, 8,762 rows: 3,426,466 systems in 27 states (AR, AZ, CA, CO, CT, DC, DE, FL, IL, MA, MD, ME, MN, NH, NJ, NM, NY, OH, OR, PA, RI, TX, UT, VA, VT, WA, WI), summarised by state, customer segment and year of installation, 1983 to 2024: systems, systems priced, systems with a battery (count), DC capacity (MW) and the median installed price per kW (USD/kW, unscreened). 19,162 systems have no year (no date, a date after their file's own, or one before 1980) and no row. The 2024 edition holds systems installed to 2023; its 2024 rows are few (a partial year).
- **Its license:** its own verdict, "Berkeley Lab, Tracking the Sun on OEDI" (session 2019, read 176): may be public, CC BY 4.0; `scripts/licenses.py` maps the table to it by hand.

## The cross-check

Tracking the Sun's DC capacity installed to the end of 2019, by state, against EIA-861's net-metered photovoltaic capacity at the end of 2019 (`eia_net_metering_state_annual`; its rows by technology end with 2019) and its non-net-metered distributed PV (`eia861_distributed_generation`), `runs/c057/s2020/cross.py`:

- **The 27 states:** 25,297 MW DC against 20,609 MW net metered and 945 MW not: 117 percent; residential 13,732 against 12,381, 111 percent. The states' figures correlate at 0.98.
- **California:** 10,259 against 9,128 and 169: 110 percent, the usual ratio of DC to AC capacity.
- **Above EIA's:** Minnesota (11.9 times), Utah (5.0) and Vermont (4.6). My reading, not checked against a source: Tracking the Sun's providers there report community and other systems that are not net metered.
- **Below EIA's:** Maryland (13 percent), Florida (15), Pennsylvania (37), Arkansas (2). My reading, not checked: its data providers there cover only a part of the state's systems. Berkeley Lab's report, which would say, was not read (emp.lbl.gov answers 403).

## Errors

- **Dates before 1980:** eight systems are dated 1899 to 1905 and 1971 (Illinois, Maryland, Ohio, Rhode Island, Utah). No grid-connected solar system is that old: a date before 1980 now counts as no date (the floor, `FLOOR` in the connector; Oregon's systems from 1983 are kept). Session 2015's test holds the case.
- **The first cross-check matched no EIA row:** the net-metering table's rows by technology end with 2019; the check is made at the end of 2019.

## Decisions made without you

- **This session's source is the rest of session 2015's,** said above.
- **The 1980 floor** (eight systems out of 3.4 million); reversible.
- **The cross-check at 2019,** the last year EIA's state rows give photovoltaics apart.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session2020.py` (2 tests), this report.
- Changed: `warehouse/connectors/lbnl_tracking_the_sun.py` (the floor), `tests/test_session2015.py`, `scripts/licenses.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c057/s2020/`, `runs/s2020*`, `warehouse/raw/lbnl_tracking_the_sun/` (all 27 states).
