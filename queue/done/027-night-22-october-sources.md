# Chain of 21 to 22 October 2026, night: sessions 516 to 522, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 515, the last session of `queue/done/026-night-21-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Sessions 516 to 522 were free in every queue file and in every `wip/` and `task/` branch when this was written (the code machine's chains hold 497 to 506, the old laptop's 531 to 542).

Each source session goes through the erw-add-connector skill (`.claude/skills/erw-add-connector/SKILL.md`):

- its robots file and its terms are read first;
- a probe;
- a trial with `--out-dir`, whose saved responses the real write reuses (sessions 510, 511 and 513: a write after a trial asks nothing);
- a cross-check against a table the ERW already holds;
- then the real run under the data lock, the validator, `build_coverage.py --only`, the archive and a sector rule, with tests;
- a new public table held from `/data` and Redivis v1 (`catalogue_hold` in `live_set.yaml`, `STORAGE_HELD` in `release_v1.py`, its rows added to `docs/redivis/release-v1/` with `runs/release_rows.py` on the data machine).

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/026-night-21-october-sources.md` hold, word for word, with its lessons. Two are added from chain 026:

- **A host whose certificate chain fails Python's check is read through Windows' own trust store** (`truststore`, installed), and verification is never turned off (session 512).
- **A whole-number column with blanks is read as text before it is written**, or it comes out as "200.0" (session 514).

Read `docs/state/note_2026-10-22_night_sources_data.md` and sessions 510 to 514's reports first.

## Session 516: EIA's nuclear outages by plant

Long end 1:30. Pulls: EIA's API v2, route `nuclear-outages/facility-nuclear-outages`, daily from 2007, at most 100 requests, 3 seconds apart (about 80 pages of 5,000).

- Each plant's capacity, outage and outage share, as `eia_nuclear_outages_facility_daily`, with the entity `eia_nuclear_outages:<facility>`.
- Cross-check: the plants' outage MW summed by day against `eia_nuclear_outages_daily`, and the plants against `nrc_reactor_status`.

## Session 517: natural gas prices by state

Long end 1:30. Pulls: EIA's API v2, route `natural-gas/pri/sum`, monthly, at most 30 requests.

- The citygate, residential, commercial, industrial and electric power prices by state (USD/MMBtu, with EIA's dollars per thousand cubic feet converted only if EIA states the heat content; otherwise kept in a unit the vocabulary holds, or the unit's addition put under "For Samuel's ruling" and that series not taken).
- One table, `eia_gas_prices_state_monthly`.
- Cross-check: the electric power price against `eia_power_plant_fuel_costs`' natural gas cost by state.

## Session 518: natural gas consumption by state and sector

Long end 1:30. Pulls: EIA's API v2, route `natural-gas/cons/sum`, monthly, at most 30 requests.

- Deliveries by state and sector, as `eia_gas_consumption_state_monthly`, in a unit the vocabulary holds (the same rule as 517).
- Cross-check: the U.S. total against `eia_sector_energy_consumption_monthly`, or against SEDS' natural gas consumption (`eia_seds_state_energy`, NGTCB) by state and year.

## Session 519: EIA's coal production by mine

Long end 1:30. Pulls: EIA's API v2, route `coal/mine-production` (or the closest route its metadata names), annual, at most 20 requests.

- Each mine's production by year, as `eia_coal_mine_production_annual`, in short tons only if the vocabulary has the unit by then; otherwise the probe and the trial only, with the unit under "For Samuel's ruling".
- Cross-check: the U.S. total against SEDS' coal (`CLTCB`) at EIA's average heat content, as an order of magnitude only.

## Session 520: EIA-861M's back years

Long end 1:00. Pulls: EIA's EIA-861M page and its files `retail_sales_2017.xlsx` to `sales_ult_cust_2024.xlsx`, at most 10 requests.

- `eia861m_sales.py --years 2017 ... 2026`. The 2017 to 2020 files are named `retail_sales_<year>`: extend `file_urls` to them only if their sheets have the same headings; read each one's headings first.
- Cross-check each whole year against `eia861_utility_sales` (2017 to 2024).

## Session 521: the 861M gaps, read

Long end 1:00. Pulls: none.

- Session 511 found that 13% of the utility-states differ by over 10% between their twelve months of EIA-861M and the annual EIA-861 for 2025 (utility 60025, for one, from 4.3 to 7.3 times).
- Read the annual form's parts (A to D), service types and data types for those utilities in `eia861_utility_sales`, and say, with counts, what explains each group. Change no table.
- Report only; if a reader's fault is found, fix it with a test.

## Session 522: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-23_sources_data.md`, in session 364's form.
2. The next file, before the queue step: at least six sessions of public sources the ERW does not yet hold, each with its robots file and terms first, numbered from the next free numbers (checked across `queue/` and every branch). Commit and push it to main on its own, with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
