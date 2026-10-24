# Session 2162 report: the next file, and Great Britain's grid (Elexon's BMRS, in place of NESO's portal)

24 October 2026, from 00:02 UTC, on lab-desktop (the data machine), the first session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 12 requests of 15 (below).

## Read these first

- **Chain 094 taken** at 00:02 UTC by chain 059's agent when chain 079 landed (the owner's instruction for that run: run the file the queue step prints). Chain 092, whose continuation this file is, still runs beside it (another agent), with chain 090 (a third). Chain 092's agent was told and sent what its session 2161 would have written: www.usda.gov joins the hosts not asked again; its five tables (BPA's balancing authority, SNOTEL, the World Bank's electricity access, building permits, EV charging) are not taken again; its last decision is 68, so this chain's start at 69; two working rules (one session label a write; a trial waits for the data lock).
- **The next file first,** pushed to main on its own before any other work: `queue/next/097-day-1-november-data-canada-offshore-inspections-supply.md` (sessions 2176 to 2189, machine: data): Statistics Canada's electricity and oil and gas supply, BSEE's offshore incidents, the NRC's inspection findings and the rest. 097 was the next free number (090 to 096 taken). Snapshots `s2162-q-before`/`-after`: 0 differences.
- **NESO's data portal is closed to the ERW's reader:** www.neso.energy's robots file allows the portal's pages (read 290), but api.neso.energy, which serves every dataset's files, disallows `/` for every reader (read 291). Not asked further.
- **Elexon's BMRS publishes Great Britain's demand openly,** under a licence that allows copying, publishing and commercial use with an attribution (read 294, a new verdict, may be public). **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `elexon_gb_demand_daily`, the Initial National Demand Outturn per day (INDOD: the half-hourly national demand summed to MWh, excluding station transformer, pumping and interconnector export demand), 27 April 2021 to 23 October 2026, 1,932 days.
  - **The endpoint's daily series begins on 27 April 2021** (the window asked from 1 January 2020 answers from then), and **74 days have no figure,** most of May and June 2021 and 17 days to the end of 2022; they have no row, nothing is filled, and the header counts them.
  - Half-hourly figures were not taken: that endpoint answers 28 days a request, and five years would have needed about 70 requests against this session's 15. The daily endpoint answers two years a request.
  - The day is written at 00:00:00Z (Decision 11, as EIA-930's daily tables), Great Britain's own settlement day kept in `x_settlement_date`.
- **The cross-check** (`runs/c094/s2162/cross.py`):
  - INDO a year is 227.9 to 230.6 TWh in 2023 to 2025, 0.712 to 0.727 of Ember's UK demand (`owid_ember_electricity_annual`): INDO leaves out the embedded generation the transmission system does not see and Northern Ireland, which Ember counts.
  - The shape of the year: Great Britain's January days run 1.21 of the year's mean and its June days 0.85; its largest day falls in November to January every year from 2021 to 2025. ERCOT's August days run 1.24 and PJM's July 1.18 (`eia930_daily_demand`): Britain peaks in winter, the two U.S. grids in summer (ERCOT's largest day fell in a winter month in three of the five years, in the cold snaps).

## The pulls

1. `www.neso.energy/robots.txt` (read 290).
2. `api.neso.energy/robots.txt` (read 291): disallows `/`.
3. `data.elexon.co.uk/robots.txt` (read 292): HTTP 404, no robots file.
4. `www.elexon.co.uk/robots.txt` (read 293).
5. Elexon's licence to use BMRS open data (read 294).
6. A year of the half-hourly outturn: HTTP 400, the 28-day limit.
7. A year of the daily outturn (2024), to see the answer.
8. The API's description (`swagger.json`), for the endpoint's definition.
9 to 12. The connector's trial: the four windows, saved and reused by the write (`--offline`).

## Errors

- **The first two writes were blocked by the validator:** the day was written at its start in Great Britain's clock (23:00Z in summer), and a daily table's `ts_utc` must be 00:00:00Z. The connector was corrected; the second write merged into the first's blocked file, which was then removed under the data lock and the table written a third time (validated). Nothing was archived or put in coverage before the valid write.
- **Chain 079's trials ran without the data lock** (sessions 2120 to 2127 copied each connector into the main checkout for its trial without taking it), against the rule for several chains on one machine; this chain's trials take it (`runs/c092/trial.sh`). No other chain's write was found disturbed.

## Decisions made without you

- **Elexon's BMRS in place of NESO's portal** for Great Britain's demand: the same national demand figure, from a host that allows the reader.
- **Daily figures only,** within the ceiling; the half-hourly series is left to a session with about 70 requests.
- **The day at 00:00:00Z** with Great Britain's own day beside it.

## For Samuel's ruling

- **api.neso.energy** disallows every reader: NESO's data (embedded wind and solar, the transmission demand by half hour) waits on a request to NESO or a person's download.

## Files

- New: `warehouse/connectors/elexon_demand.py`, `tests/test_session2162.py`, this report; on main, `queue/next/097-day-1-november-data-canada-offshore-inspections-supply.md`.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (290 to 294), `license_verdicts.csv` (Elexon), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c094/`, `runs/license_reads/s2162/`, `runs/s2162*`, `warehouse/raw/elexon_demand/`.
