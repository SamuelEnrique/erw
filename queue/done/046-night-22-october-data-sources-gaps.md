# Chain of the night of 22 October 2026: sessions 850 to 866, data machine (lab-desktop), unattended: the siting gaps a public source can fill, EIA-930's early sub-regions, the licenses a read can settle

machine: data

Written by session 688, the first session of `queue/done/045-evening-22-october-data-resumed.md`, under that file's added rule ("the next file is written and pushed to `queue/next` at the START of the chain, not at its end"), at the owner's instruction for it ("at least twelve sessions, machine: data, numbered from 850, the sources and gaps chain 044's reports leave open, in chain 040's form"). Sessions 850 to 866 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 699 of chain 045 updated it at chain 045's end (23 October, about 01:15 UTC): sessions 864 and 865 added, the note and the landing moved to 866, session 858's leads and session 863's uploads named. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file and terms read first and saved under `runs/license_reads/` (EIA's terms are record 1, public; ERCOT's are licenses.md #2, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/write_table.sh`, `runs/finish_table.sh`, `runs/union_resolve.py`, `runs/s622/resolve_ours_plus.py` and `runs/release_replace.py` on the data machine;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/045-evening-22-october-data-resumed.md` hold, word for word, with chain 043's and 044's lessons and chain 045's added rule: **session 850 begins by writing `queue/next/047-<slug>.md` for this machine (at least twelve sessions, machine: data, numbered from the next free numbers above 866, from 867 on, below 1000), commits it alone and pushes it to main before any other work**; session 866 updates that file instead of writing one from nothing.

Read first: `docs/state/note_2026-10-25_data.md` (chain 045's note), sessions 684 to 699's reports, `docs/reviews/siting-gaps.md` and `docs/reviews/siting-open-2026-10-23.md` (the code machine's open items), `docs/reviews/siting-sources-2026-10-24.md` (session 691's findings) and `docs/state/unsettled_licenses_2026-10-19.md`.

## Session 850: ERCOT's settlement point mapping

Long end 1:30. Pulls: ERCOT's public reports, at most 10 requests.

- ERCOT's Settlement Points List and Electrical Buses (report NP4-160), the latest posting, as an entities table `ercot_settlement_points` (settlement point, its kind, load zone, hub, the electrical buses it holds, the posting's date), from a connector made from `ercot_rt_spp.py`'s report reader.
- Cross-check: every node of `node_basis_daily` and `ercot_rt_spp` found in the mapping, the missing named; every hub and load zone of the ERCOT price tables found.
- This fills the siting gap "a node's load zone and settlement hub" (`siting-open-2026-10-23.md`, item 11).

## Session 851: ERCOT's capacity, demand and reserves report

Long end 1:30. Pulls: ERCOT, at most 6 requests.

- The latest Capacity, Demand and Reserves (CDR) report's summary: the planning reserve margin by year, the firm peak load forecast and the resources counted, as a series table `ercot_cdr_reserve_margins` (`MW`, `percent`), each row naming the report and its date.
- Cross-check: the CDR's peak forecast for the current year against `grid_peak_vs_capacity`'s ERCOT peak; the resources against `eia_state_capacity_annual`'s Texas total.
- This fills reserve margins for ERCOT (item 20), whatever NERC's terms hold.

## Session 852: ERCOT's transmission projects

Long end 2:00. Pulls: ERCOT, at most 8 requests.

- ERCOT's Transmission Project and Information Tracking report (TPIT), the latest posting, as an events table `ercot_transmission_projects` (project, the transmission service provider, county, voltage, kind, the in-service date, its status).
- Cross-check: the counties against `utility_service_territories`' Texas counties; the TSPs against `texas_delivery_charges`' utilities.
- This fills "transmission projects by county" for ERCOT's nodes (item 12).

## Session 853: EIA-861's delivery-only service

Long end 1:30. Pulls: none (the saved EIA-861 zips).

- The Delivery_Only_Service sheet of every saved EIA-861 year, as `eia861_delivery_only` (utility, state, balancing authority, customers, MWh delivered, by sector), from `eia861_sales.py`'s reader and its `years_held` (session 690); its rows read whole, never with `comment="#"` (two utilities' names hold a "#").
- Cross-check: CenterPoint, Oncor and AEP Texas present for Texas; the delivery-only MWh by state against `eia861_utility_sales`' energy-only rows for the same state and year.
- This fills "a Texas wires utility's own revenue" (the ERCOT row of `siting-gaps.md`).

## Session 854: generation with a signed interconnection agreement, derived

Long end 1:30. Pulls: none.

- A derived table `interconnection_agreements_by_grid` from `lbnl_interconnection_queue` (held): projects with an `ia_date` and no operation date, by grid, state, fuel and year of agreement, MW summed, with its method in `docs/methods/interconnection_agreements_by_grid.md`.
- Cross-check: each grid's total against the same file's active MW; the sum against Berkeley Lab's own headline where its report states one.
- This fills the headroom row "generation with a signed interconnection agreement".

## Sessions 855 and 856: EIA-930's demand by sub-region, 2019

Long end 1:30 each. Pulls: at most 90 requests each.

- `python warehouse/connectors/eia930_subba.py --year 2019`: 855 saves pages to its ceiling, 856 writes `eia930_subba_demand_hourly_2019` from both sessions' pages. The two holds.
- Cross-check: against `ferc714_area_demand_2019`, the same seven parents.

## Session 857: EIA-930's demand by sub-region, its first months

Long end 1:30. Pulls: at most 60 requests.

- The months before 2019 that EIA holds for the sub-regions (probe the first period first), as `eia930_subba_demand_hourly_2018`, or as the months it holds, said in the header.
- Cross-check: against `ferc714_area_demand_2018` where both hold an hour.

## Session 858: substations and transmission lines, the second try

Long end 2:00. Pulls: at most 12 requests, two a host, only if session 691 to 693 did not write both tables.

- The leads session 691 left unread (`docs/reviews/siting-sources-2026-10-24.md`): the federal GeoPlatform (`geoplatform.gov`, which holds FGDC's National Geospatial Data Asset lists; its Utilities theme may name the lines' lead agency) and data.gov's new catalogue interface (the old CKAN API answers 404), their robots file and terms first. Esri's archive of the lines is under Esri's license and is not a public source; a layer whose license line says public is written as `hifld_substations` or `hifld_transmission_lines` (the names the code machine reads).
- A refusal or no public layer: the session writes what it found in `docs/reviews/siting-sources-2026-10-24.md` and probes nothing else.

## Session 859: the unsettled licenses a read can settle

Long end 1:30. Pulls: at most 20 requests, two a host.

- From `docs/state/unsettled_licenses_2026-10-19.md` and `docs/licenses.md`'s "unsettled" rows, the publishers whose terms page is public and readable without a browser: each read and saved, its verdict in `license_reads.csv` and `license_verdicts.csv` in the words of `docs/licenses.md`, then `python scripts/licenses.py write` in a worktree.
- A verdict that would change a table's flag is listed for the owner, not applied.

## Sessions 860 and 861: two more sources

Long end 1:30 each. Pulls: at most 20 requests each.

- A public source the ERW does not hold, chosen by each session (EIA's route list, ERCOT's public reports, or a federal publisher whose robots file and terms allow it), first from the gaps of `siting-gaps.md` a public source fills. Say why it was chosen.

## Session 862: method notes for this chain's tables

Long end 1:00. Pulls: none. A note for each table this chain wrote, in the form of sessions 674 to 678, with the `Tables:` line; coverage's Method column follows.

## Session 863: the live set and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 100 requests.

- No new table enters the live set unless a ruling names it.
- Up to the Stanford draft with the true replace and the proof (`upload.py --target stanford --prove-by-listing`), about 5 requests a table: chain 045's new public tables (`eia_coal_mine_production_annual`, `eia861_utility_reliability`, `eia930_subba_demand_hourly_2020`), `eia861m_utility_sales_monthly` (rewritten by session 689 without EIA's aggregates), chain 041's two never uploaded there (`eia930_subba_demand_hourly_2021`, `eia_coal_production_annual`), then this chain's public tables; then `--reconcile`; the release note extended. The 45 tables that only grew since their upload (session 688's reconcile) wait for the owner's answer on the click. Nothing released.

## Session 864: the package's remote test, the rest

Long end 1:30. Pulls: Redivis's API only, at most 100 requests.

- `ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote -k "eia_fuel_spot_prices or eia_drilling_monthly or cite or coverage"`: the eight tests session 688's ceiling left (`same_as_local` holds a table a daily run rewrote after its upload). Count the requests (`runs/c045/s688/counted_pytest.py`, `ERW_CAP`). A failure is fixed in the package with its test, or written down with its cause.

## Session 865: the headers that say less than their files

Long end 1:30. Pulls: none (each table written again from its saved pages, `--offline`, under the lock, where its connector allows).

- Session 696's notes found: `eia_series.py`'s tables say a run "replaces all of it" while the connector merges; `rrc_lease_production_monthly`'s first header line says "internal" (public, noncommercial, since session 324); `battery_sourced_ranges`' header names a builder that does not exist (`sourced_ranges.py` builds it); `news_scores_shadow`'s header counts 4,348 rows of a file holding 4,748. Each connector's header text made true, with a test.
- `nyiso_interconnection_queue`'s header says public while its ERW verdict is "license needed": listed for the owner, not changed.

## Session 866: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-26_data.md`, in session 683's form.
2. `queue/next/047-*.md` (written by session 850) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
