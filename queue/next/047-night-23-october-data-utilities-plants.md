# Chain of the night of 23 October 2026: sessions 867 to 879, data machine (lab-desktop), unattended: EIA-861's other files, plants and coal to plants, the siting gaps' third round

machine: data

Written by session 850, the first session of `queue/done/046-night-22-october-data-sources-gaps.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). Sessions 867 to 879 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 866 of chain 046 updates this file if its results change what it should hold. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file and terms read first and saved under `runs/license_reads/` (EIA's terms are record 1, public; ERCOT's are licenses.md #2, public; CAISO's licenses.md #3, free for public use with credit);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/c045/write_table.sh`, `runs/c045/finish_table.sh` (or `runs/c045/finish_replace.sh` for a table already in the release package), `runs/s622/resolve_ours_plus.py`, `runs/c045/keep_newest_row.py` and `runs/c045/method_cells.sh` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/046-night-22-october-data-sources-gaps.md` hold, word for word, with chain 045's lessons:

- **A reader of a table never uses pandas' `comment="#"`**: values hold "#" (session 690); skip the header by counting its leading "#" lines.
- **Saved EIA-861 zips are read, never asked for again**; a year under `/archive/` is read only from a zip already saved (EIA's robots file).
- **The whole suite takes about 10 minutes here**: redirect it to a file and read `Ran` and `FAILED` from the file; from a worktree, `test_session705` fails as a location artifact (it passes in the main checkout).
- **Session 867 begins by writing `queue/next/048-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 880), commits it alone and pushes it to main before any other work; session 879 updates it.

Read first: `docs/state/note_2026-10-26_data.md` (chain 046's note), sessions 850 to 866's reports, `docs/state/note_2026-10-25_data.md`, `docs/reviews/siting-gaps.md`.

## Session 867: each utility's regions and markets (EIA-861 Utility_Data)

Long end 1:30. Pulls: none (the saved EIA-861 zips).

- `Utility_Data_<year>.xlsx` of every saved year as an entities or series table `eia861_utility_data` (utility, state, NERC region, balancing authority, the RTO or ISO it belongs to, ownership and the activities EIA marks): the key that joins a utility to its grid for the All grids tab.
- Cross-check: each utility of `eia861_utility_sales` found; the RTO flags against `utility_service_territories`' states.

## Session 868: demand response and dynamic pricing by utility

Long end 1:30. Pulls: none.

- `Demand_Response_<year>.xlsx` and `Dynamic_Pricing_<year>.xlsx` of every saved year, by utility, state and sector, as one or two series tables (enrolled customers, energy and peak savings, the programs EIA counts), units in the vocabulary or a Decision.
- Cross-check: the states summed against EIA's own state totals where the file gives them.

## Session 869: advanced meters and net metering by utility

Long end 1:30. Pulls: none.

- `Advanced_Meters_<year>.xlsx` and `Net_Metering_<year>.xlsx` by utility, beside the state tables the ERW holds (`eia_meters_state_annual`, `eia_net_metering_state_annual`).
- Cross-check: the utilities summed by state against those state tables, every year both hold.

## Session 870: coal shipped to power plants

Long end 1:30. Pulls: EIA's API v2, route `coal/shipments`, at most 20 requests.

- Probe the route's count first; the years the ceiling allows, newest first, as `eia_coal_shipments_annual` (mine, plant, quantity in `short_ton`, transport mode, the coal's rank and quality where given).
- Cross-check: the mines against `eia_coal_mine_production_annual` (session 694), the plants against `eia923_plant_fuel_annual`.

## Session 871: CAISO's transmission access charge

Long end 1:30. Pulls: CAISO, at most 10 requests.

- CAISO's published transmission access charge rates (high voltage and the participating transmission owners' low voltage rates), a table of rates by period, from CAISO's own posting; the CAISO row of `siting-gaps.md`'s transmission column.
- Cross-check: the rates against the participating transmission owners' filed revenue requirements where CAISO's document states them.

## Session 872: ERCOT's resource lists: a node's wires utility and county

Long end 2:00. Pulls: ERCOT, at most 10 requests.

- ERCOT's public resource lists (the resource's settlement point, county and its transmission service provider) as an entities table, joined in a cross-check to session 850's `ercot_settlement_points`.
- This fills "a node's wires utility (TSP)" and "a node's county" (`siting-gaps.md`).

## Session 873: EIA-860's plants

Long end 1:30. Pulls: EIA, at most 4 requests (the page and the newest annual zip, only if not saved; never `/archive/`).

- The newest annual EIA-860 plant file as `eia860_plants_annual` (plant, county, latitude, longitude, balancing authority, utility, NERC region, sector), entities.
- Cross-check: the plants against `eia923_plant_fuel_annual` and `eia860m_operating_generators`.

## Session 874: the unsettled licenses, the second round

Long end 1:30. Pulls: at most 20 requests, two a host. As chain 046's session 859, for the publishers it did not reach.

## Sessions 875 and 876: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 877: method notes for this chain's tables

Long end 1:00. Pulls: none. A note for each table this chain wrote; coverage's Method column follows.

## Session 878: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 100 requests. This chain's and chain 046's public tables not yet in the draft, uploaded with the true replace and the proof; `--reconcile`; the release note extended. Nothing released.

## Session 879: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-27_data.md`, in session 683's form.
2. `queue/next/048-*.md` (written by session 867) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
