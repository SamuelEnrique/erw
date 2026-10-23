# Chain of the day of 23 October 2026: sessions 951 to 964, data machine (lab-desktop), unattended: federal oil and gas production and royalties, wind turbine prices and costs, the primary energy overview, critical minerals, renewable projects on public lands, the licenses' eighth round

machine: data

Written by session 937, the first session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 054. Sessions 951 to 964 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 950 of chain 053 updates it at chain 053's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`; a session that needs one stops and says so, without signing up.
- **HydroSource's download form is not filled**; ORNL's files are taken by their public links, pending the owner's word.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead (session 923's push was refused unseen).
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, budgeted by session 892's measure (session 933: 86 Redivis requests for seven tables and the metadata in a plain upload).
- **Session 951 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 965), commits it alone and pushes it to main before any other work; session 964 updates it.

Read first: chain 053's note (written by session 950), sessions 937 to 950's reports, `docs/state/note_2026-10-31_data.md`, `docs/reviews/siting-gaps.md`.

## Session 951: federal oil and gas production and royalties (the Office of Natural Resources Revenue)

Long end 1:30. Pulls: at most 15 requests. ONRR's public data (onrr.gov): federal and Native American oil, gas and coal production by state and month, and the revenue (royalties, rents, bonuses) it collects; robots and terms first; series tables of their own; cross-check: federal offshore production against `boem_ogor_lease_production_monthly` summed by month.

## Session 952: wind turbine prices, capital and operating costs (Berkeley Lab)

Long end 1:30. Pulls: none (the 2026 wind data file session 915 saved, `warehouse/raw/lbnl_ppa_prices/`). Its sheets "Wind Turbine Prices", "CapEx Over Time", "Recent CapEx by Region", "O&M Over Time" and "Wind LCOE Over Time", as series tables of their own; cross-check: the capital costs against `nlr_atb_electricity_costs`' land-based wind for the years both hold.

## Session 953: the primary energy overview (EIA's Monthly Energy Review)

Long end 1:30. Pulls: EIA's API v2, at most 15 requests. The route `total-energy`'s Tables 1.1 to 1.3 (primary energy production, consumption, imports and exports by source, monthly), where no ERW table holds them (`eia_sector_energy_consumption_monthly` holds Tables 2.3 and 2.4); cross-check: consumption by source against `eia_seds_state_energy`'s U.S. totals for the years both hold.

## Session 954: critical minerals for storage and grids (the U.S. Geological Survey)

Long end 1:30. Pulls: at most 15 requests. USGS's Mineral Commodity Summaries data releases for lithium, cobalt, nickel, graphite, copper and the rare earths (world production by country, U.S. imports, prices), robots and terms first; a series table of its own; cross-check: the prices against `imf_commodity_prices` and `wb_commodity_prices_monthly` where they overlap.

## Session 955: renewable energy projects on public lands (the Bureau of Land Management)

Long end 1:30. Pulls: at most 15 requests. BLM's public list or map service of solar, wind and geothermal projects on public lands (status, capacity, acreage), robots and terms first; an entities table; cross-check: the projects against `uspvdb_solar_facilities` and `uswtdb_wind_turbines` by name and state.

## Session 956: the licenses' eighth round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 053 did not reach, those of sessions 951 to 955 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Sessions 957 and 958: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 959: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 960: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 932: each note's checks against the code and the table, every contradiction acted on.

## Session 961: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. First any table of chain 053 not yet in the draft or stale there (session 947's report names them); then this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 962: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 934: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 963: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 964: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-02_data.md`, in session 683's form.
2. The next file (written by session 951) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
