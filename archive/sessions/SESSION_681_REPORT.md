# Session 681 report: cross-checks against the new tables

22 October 2026, from about 10:14 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **The code machine's stand-in for "which utility serves a site" is wrong in 4 of the 7 hub counties.** The largest industrial seller of the state (`eia861_utility_sales`, 2025) against the utilities `utility_service_territories` lists for a county each grid's main hub points to:
  - **Texas (Harris, ERCOT's Houston hub):** TXU Energy Retail, a retailer with no franchise territory; the county's wires are CenterPoint's, Entergy Texas's and a co-op's.
  - **California (Los Angeles, SP15):** PG&E, which serves 50 California counties but not Los Angeles.
  - **New York (New York County, Zone J):** Niagara Mohawk; Manhattan is Consolidated Edison's.
  - **Massachusetts (Suffolk, the Mass Hub):** Direct Energy Business, a retailer.
  - **Pennsylvania, Indiana, Kansas** (PJM, MISO, SPP): the state's largest seller does serve the county, among others.
  The territory table answers the question the stand-in was standing in for; the code machine should read it.
- **Request to operation against `iso_queue_statistics`' median wait:** CAISO within weeks for 2015 and 2017 entries (8.48 against 8.62 years; 4.93 against 4.93), SPP for 2015 (4.40 against 4.47). ERCOT, NYISO and SPP 2017 differ by 0.7 to 2.5 years (different sets of projects: Berkeley Lab's completed requests against the ISO file's positions with a wait). PJM and MISO cannot be compared: `iso_queue_statistics` holds no wait for them.
- **Each grid's 2025 peak in `grid_peak_vs_capacity` equals the peak the site's demand pages draw** (`site/data/demand_growth.json`, built 5 October), MW for MW and hour for hour, for all seven grids.
- **The three checks are in `check-cross-checks`:** each note (`utility_service_territories.md`, `interconnection_durations.md`, `grid_peak_vs_capacity.md`) has a section "Cross-checks" at its anchor, in the five columns, and `site/scripts/check-cross-checks.mjs` reads them (floors 7, 12 and 7 rows). `--files`: all 70 checks pass. No figure was moved.

## Decisions made without you

- A hub's county was chosen here, one per grid (Harris, Los Angeles, New York, Suffolk, Allegheny, Marion, Sedgwick); the note names the choice. A hub is a set of buses, not a county.
- The "published" side of the durations check is the warehouse's own table from the ISOs' files, not a publisher's figure: the source cell names its method note, which the script accepts and lists as a note.
- The peak check compares the table with the site's own copy, not with an ISO's published peak: no request was allowed, and EIA-930 is the source of both.
- `tests/test_session538.py` copies the six notes the script now reads, so its planted-fault copy still runs whole.

## For Samuel's ruling

- None new; the stand-in's four misses are for the code machine (its session 718 reads `utility_service_territories`).

## Files

- Changed: `docs/methods/utility_service_territories.md`, `docs/methods/interconnection_durations.md`, `docs/methods/grid_peak_vs_capacity.md`, `site/scripts/check-cross-checks.mjs`, `tests/test_session538.py`. New: this report. On the data machine only: `runs/c043/crosschecks_681.py` and its output.
