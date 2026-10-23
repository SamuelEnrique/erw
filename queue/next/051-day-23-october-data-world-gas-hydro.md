# Chain of the day of 23 October 2026: sessions 909 to 922, data machine (lab-desktop), unattended: the world's electricity, Canada's gas trade with the U.S., the hydropower fleet, charging stations, the licenses' fifth round

machine: data

Written by session 895, the first session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). Chain 049's file asked for `050-<slug>.md`; the code machine's chain already holds 050, so this file is 051. Sessions 909 to 922 were free in every queue file and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 908 of chain 049 updates this file if its results change what it should hold. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked alone and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check;
- `runs/c045/write_table.sh`, `runs/c048/write_tables.sh` (several tables of one connector under one lock), `runs/c045/finish_table.sh` (or `finish_replace.sh`), `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py`, `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/049-day-23-october-data-margins-schedules-emissions.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page (chain 048), and any a session of chain 049 names.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms (chain 048 read two publishers again that already had a verdict).
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, budgeted by session 892's measure (about 28 a run and 6 a table); an empty `erw_headers` is rebuilt in full from disk, never merged.
- **Session 909 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 923), commits it alone and pushes it to main before any other work; session 922 updates it.

Read first: chain 049's note (written by session 908), sessions 895 to 908's reports, `docs/state/note_2026-10-28_data.md`, `docs/reviews/siting-gaps.md`.

## Session 909: the world's electricity (EIA's International Energy Statistics)

Long end 1:30. Pulls: EIA's API v2, at most 20 requests. Session 886's table holds the U.S., Canada and Mexico; this takes every country's electricity generation by source, capacity, consumption and trade, annual, as a table of its own (`warehouse/connectors/eia_international_electricity.py` given a country list, or a sibling); cross-check: the three countries against session 886's table, and the world total against the countries summed.

## Session 910: Canada's natural gas trade with the U.S. (Canada Energy Regulator)

Long end 1:30. Pulls: at most 20 requests. The CER's natural gas exports and imports by port and month, where its pages give a file (robots read in session 887; its terms are recorded, read 96); cross-check: against EIA's U.S. imports from Canada (`eia_gas_trade_country_monthly`).

## Session 911: the hydropower fleet (Oak Ridge National Laboratory's HydroSource)

Long end 1:30. Pulls: at most 15 requests. ORNL's Existing Hydropower Assets (each plant's capacity, owner, river, dam), robots and terms first; an entities table; cross-check: against the hydroelectric plants of `eia860_plants_annual` by EIA plant id.

## Session 912: EV charging stations (NREL's Alternative Fuels Data Center)

Long end 1:30. Pulls: at most 15 requests. The station locator's electric stations (ports by level, network, place, opening date), robots and terms first; a key from `.env` only if one is there (`NREL_API_KEY` or `DATA_GOV_API_KEY`), else the session stops and says so, without signing up. Cross-check: stations by state against the AFDC's own state counts.

## Session 913: the Annual Energy Outlook's capacity and generation by region

Long end 1:30. Pulls: EIA's API v2, at most 20 requests. `eia_aeo_electricity` holds national series; this takes the AEO's electricity supply by EMM region (capacity additions and retirements by technology, generation by fuel), reference case, as a table of its own; cross-check: the regions summed against the national series.

## Session 914: the licenses' fifth round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 050 did not reach, those of sessions 909 to 913 first; `license_verdicts.csv` read first.

## Sessions 915 and 916: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 917: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling (not substations and lines, not ERCOT's robots-held paths), as a derived table with its method note; else the session says why none can.

## Session 918: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 891: each note's checks against the code and the table, every contradiction acted on.

## Session 919: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap (session 892's measure). Any table chains 048 and 049 left out first, then this chain's public tables; `--reconcile`; the release note extended. Nothing released.

## Session 920: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 893: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 921: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts (session 894 found the site's verdicts stale after a license change); rebuilt if stale.

## Session 922: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-10-30_data.md`, in session 683's form.
2. The next file (written by session 909) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
