# Session 2015 report: rooftop solar (Berkeley Lab's Tracking the Sun), its first eight states; chain 056 landed

23 October 2026, from 18:19 UTC, on lab-desktop (the data machine), the second session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`. Model spend USD 0. Pulls: 15 requests of 15 (data.openei.org's robots file, asked in a call of its own: none, HTTP 404; OEDI's search for "tracking the sun"; the Tracking the Sun submission page; the data lake's robots file, a new host, in a call of its own: none, HTTP 404 NoSuchKey; the lake's folder listing; the 2024 edition's listing, read by the probe; then the connector's own listing and eight state files).

## Read these first

- **No table yet, on purpose:** the latest public data on OEDI are the 2024 edition (files dated 28 February 2025; systems installed to 2023, a few in 2024), as **27 Parquet files, one a state**, 118 MB: 27 file requests and a listing, past this session's 15. This session fetched eight states (AR, AZ, CA, CO, CT, DC, DE, FL; 102 MB, California 81 MB) through the connector (`--fetch-only --states`), and **session 2020 takes the other nineteen under its own ceiling of 20 and writes the table** (the chain file lets sessions 2020 and 2021 choose their sources; this one is said there with why). A write before then stops at the first state not saved (the offline trial stopped at Illinois): no table of some states only.
- **The connector is built and tested:** `warehouse/connectors/lbnl_tracking_the_sun.py`, one series table, `lbnl_tracking_the_sun`, the file's systems summarised by state, customer segment and year of installation: systems, systems priced, systems with a battery (count), DC capacity (MW) and the median installed price per kW (USD/kW, unscreened). The file holds one row a system (California's file alone 1,921,220): too large to hold whole, so a summary, as the chain file allowed, said in its header.
- **License: CC BY 4.0,** as the OEDI submission states (its record's "license": https://creativecommons.org/licenses/by/4.0/, and OEDI's footer); emp.lbl.gov was not asked (it answers 403 to the ERW's reader). Public.
- **The eight states' figures, as a first check** (`runs/c057/s2015/partial.py`): California 1,920,989 systems dated, 18,004 MW DC; Arizona 288,733 and 3,128 MW; Colorado 108,882 and 1,101 MW. California's residential median rises from about USD 4,045 a kW in 2018 to 4,150 in 2023 (Berkeley Lab's report, screened, gives lower medians; this table says it is unscreened). The cross-check against `eia861_distributed_generation` waits for the whole table (session 2020).
- **Chain 056 landed:** check run 40001414007 completed success and merged `task/2000-2013-data` (`bdf7367a`, "Merge task/2000-2013-data: checks passed") at about 18:22 UTC. Vercel's status for `bdf7367a`: "Deployment rate limited", so nothing deployed. The snapshot after (`c056-land-after`, 18:26:40 UTC) against `c056-land-before`: **0 differences in all** (25 pages; every page reads as the in-review page). Expected: the chain changes no page.

## Errors

- **One Arizona system is dated 29 March 2038,** after its file was published: a system dated after its file's own Last-Modified day now counts as one with no date, and has no row (the header counts them).
- **A heredoc patch broke** on apostrophes (my notes warned of it): the connector was written whole with the Write tool instead.

## Decisions made without you

- **The table's write moved to session 2020,** whose source is the rest of this one, under its own ceiling: two sessions' ceilings for one source of 28 requests, none exceeded.
- **The 2024 edition only:** OEDI's lake holds 2018 to 2024; the latest is the one asked for. Earlier editions are not taken.
- **A summary, not the systems:** five figures a state, segment and year; zip codes, installers, equipment and the rest not taken.
- **The price unscreened,** the median of price over size for systems with both above zero; Berkeley Lab's screens are not reproduced.
- **A date after the file's date is no date** (one system).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/lbnl_tracking_the_sun.py`, `tests/test_session2015.py` (3 tests), this report.
- On the data machine only: `runs/c057/s2015/`, `runs/license_reads/s2015/`, `warehouse/raw/lbnl_tracking_the_sun/` (eight states and the listing), `runs/c057/c056_*`.
