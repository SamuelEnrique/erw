# Chain of the day of 23 October 2026: sessions 923 to 936, data machine (lab-desktop), unattended: the world's oil and gas, Ember's yearly electricity, the reactor fleet, the World Bank's commodity prices, power plants' fuel stocks, the licenses' sixth round

machine: data

Written by session 909, the first session of `queue/done/051-day-23-october-data-world-gas-hydro.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 052. Sessions 923 to 936 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 922 of chain 051 updated it at chain 051's end (23 October, about 09:00 UTC): session 923 reads the bulk file chain 051 saved, session 928 begins with the Texas Comptroller's policies, session 933 refreshes the draft's two metadata tables, and the rules name the keys and the reader fault chain 051 found. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked alone and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/c045/write_table.sh`, `runs/c048/write_tables.sh` (several tables of one connector under one lock), `runs/c045/finish_table.sh` (or `finish_replace.sh`), `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py`, `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/051-day-23-october-data-world-gas-hydro.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page (chain 048), and EPA's bulk file API without a key (session 898: `EPA_CAMD_API_KEY` is not set).
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **No cross-check reads an ERW table with pandas' `comment="#"`:** it cuts a row at a '#' inside a value (session 917). Skip the header lines instead (`runs/c051/readt.py` on the data machine).
- **Keys not held:** `EPA_CAMD_API_KEY` (session 898) and `NREL_API_KEY` or `DATA_GOV_API_KEY` (session 912); a session that needs one stops and says so, without signing up.
- **HydroSource's download form is not filled** (sessions 911 and 916): ORNL's files are taken by their public links, pending the owner's word.
- **A request cap on the Redivis uploader stops between tables, never inside one**, budgeted by session 892's measure (about 28 a run and 6 a table); an empty `erw_headers` is rebuilt in full from disk, never merged.
- **Session 923 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 937), commits it alone and pushes it to main before any other work; session 936 updates it.

Read first: chain 051's note (`docs/state/note_2026-10-30_data.md`, written by session 922), sessions 909 to 922's reports, `docs/state/note_2026-10-29_data.md`, `docs/reviews/siting-gaps.md`.

## Session 923: the world's oil and natural gas (EIA's International Energy Statistics)

Long end 1:30. Pulls: none if the bulk file session 909 saved is used (`warehouse/raw/eia_intl_bulk/`, `INTL.zip`, last modified 19 October 2026), at most 20 otherwise. Session 909 took every country's electricity from it (`eia_world_electricity_annual`, `warehouse/connectors/eia_intl_bulk.py`); this takes every country's petroleum and natural gas production, consumption, reserves and trade, annual, from the same file, as a table of its own (a second table of `eia_intl_bulk.py`; the units are EIA's thousand barrels a day, billion cubic feet and the rest, mapped to the standard's or left out and named); cross-check: the U.S. rows against `eia_crude_reserves_annual` and `eia_gas_balance_annual`, and the world total against the countries summed.

## Session 924: Ember's yearly electricity data

Long end 1:30. Pulls: at most 15 requests. Ember's yearly electricity data by country (generation by source, capacity, demand, emissions intensity), robots and terms first (its license is read, not assumed); a series table of its own; cross-check: against session 909's EIA table for the same countries and years, the differences counted and named.

## Session 925: the reactor fleet (NRC)

Long end 1:30. Pulls: at most 15 requests. The NRC's list of operating power reactors (each unit's docket, licensee, location, reactor type, licensed thermal power, license dates and renewals), robots and terms first; an entities table beside `nrc_reactor_status`; cross-check: every unit of `nrc_reactor_status` found in it, and its capacity against the nuclear generators of `eia860m_operating_generators`.

## Session 926: the World Bank's commodity prices (the Pink Sheet)

Long end 1:30. Pulls: at most 10 requests. The World Bank's monthly commodity price data (energy: crude, coal, natural gas in the U.S., Europe and Japan), robots and terms first; a series table of its own; cross-check: the series both hold against `imf_commodity_prices`.

## Session 927: fuel stocks at power plants (EIA)

Long end 1:30. Pulls: EIA's API v2, at most 20 requests. Coal and petroleum stocks at power plants, monthly, by state and sector (electric power operational data), where no ERW table holds them; cross-check: the coal stocks against the Electric Power Monthly's national figure for the same months.

## Session 928: the licenses' sixth round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 051 did not reach, those of sessions 923 to 927 first; `license_verdicts.csv` read first. Then the Texas Comptroller's site policies (`https://comptroller.texas.gov/about/policies/`, linked from its home page, read 125; its robots file allows `/about/`).

## Sessions 929 and 930: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 931: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling (not substations and lines, not ERCOT's robots-held paths), as a derived table with its method note; else the session says why none can.

## Session 932: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 891: each note's checks against the code and the table, every contradiction acted on.

## Session 933: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap (session 892's measure). Session 919 put every public table of chains 048, 049 and 051 in the draft; first a plain upload of `erw_coverage` and `erw_sources` (346 and 439 rows here, 316 and 416 in the draft), then this chain's public tables; `--reconcile`; the release note extended. Nothing released.

## Session 934: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 893: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 935: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 936: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-31_data.md`, in session 683's form.
2. The next file (written by session 923) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
