# Session 2784 report: Luxembourg's power stations, net maximum power and number a year from 1960 (STATEC's LUSTAT), an own choice

26 October 2026, about 01:53 to 01:58 UTC, on lab-desktop (the data machine), chain 141, unattended. Precheck passed (`runs/c141/pre2784.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch).

## Read these first

- **Why this source:** this chain's four utilities gave no table, and STATEC's capacity table completes chain 140's Luxembourg generation and trade, under a verdict already given (CC0 1.0).
- **`statec_lu_power_capacity_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statec_power_capacity.py`, 951 rows, 14 entities, 1960 to 2024):
  - From LUSTAT dataflow DF_A4201, "Net maximum power (in MWe) and units of the power stations", every key in one request.
  - Two variables: `net_maximum_power` (MW) and `power_stations` (count), for the total; primary and secondary generation stations; hydropower, wind, solar, classic thermal and CHP stations; and six kinds below them (pumping, large and micro hydro, biomethanation, woodwaste, woodpellets).
  - The total: 1,230.3 MW in 15 stations in 1990; 2,266.9 MW in 22,861 in 2024, of which 22,610 solar. 281 observations not available have no row.
  - **The first two levels compared with their parts every year:** STATEC's totals differ in 11 cases, kept as published and listed in the header and run log. They are the power in 2009 (the total by 9.1 MW, primary by 4.0) and the number of secondary stations in 1996 to 2000, 2020, 2021 and 2024 (and the total's count in 2024). I first had the run stop on such a difference; as STATEC publishes them, they are counted instead, as in session 2771.
- **Cross-check** against `eurostat_electricity_capacity_annual` (Luxembourg, `net_capacity_total`), MW: equal in 2015 (wind 63.794, solar 116.272, hydro 1,330.266); in 2024 within 2 MW (wind 213.736 against 213.081, solar 549.797 against 547.867, hydro 1,330.009 against 1,329.994).
- **Terms:** lustat.statec.lu's robots address asked again in its own request (read 1582): no robots file. STATEC's verdict (read 1564) covers it; the license record shows the table as agreed, public.
- **Written under the data lock:** validated, archived (951 rows), in coverage. The patch applied cleanly with no marker. Coverage has 609 tables and `sources.csv` 699 sources, none twice. `finish_table.sh`: the release and license checks pass (609 tables, 0 problems).

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | lustat.statec.lu's robots address (its own request) | no file |
| 2 | DF_A4201, every key, CSV (the fetch) | 200, 232,568 bytes |

Read recorded: 1582.

## Decisions made without you

- **STATEC's totals' differences counted, not a stop,** as STATEC publishes them.
- **The third level not checked against its parents:** pumping, large and micro stations do not sum to hydropower as published.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statec_power_capacity.py`, `tests/test_session2784.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (read 1582), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c141/s2784/`, `runs/license_reads/s2784/`, `warehouse/raw/statec/s2784a4201/`.
