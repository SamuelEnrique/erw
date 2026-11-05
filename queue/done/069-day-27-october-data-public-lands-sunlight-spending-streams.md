# Chain of 27 October 2026: sessions 2106 to 2119, data machine (lab-desktop), unattended: oil and gas on public lands, the sunlight solar runs on, what households spend on energy, California's total system power, the 1603 grants, the rivers behind the dams, New York's distributed solar, the licenses' seventeenth round

machine: data

Written by session 2084, the first session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 069 (060 to 068 and 070 to 088 are taken). Chain 068 asked for sessions numbered from 2098; 2100 to 2105 are taken (the laptops' chain 084, on main), so this chain starts at 2106, the first block of fourteen free numbers: 2106 to 2119 were free in every queue file, report, doc and branch on origin's main and in chains 066 and 067's branches when this was written (a search for "session 2106" to "session 2121" and `SESSION_2106_` and on found none). Session 2097 of chain 068 updates it at chain 068's end. Model: Opus 5.5, high effort.

Chain 068 was taken at 20:59 UTC on 23 October by chain 058's agent (the owner's instruction for that run: run the file the queue step prints). The sources below were chosen by session 2084 among public ones the ERW does not hold and that chains 057 to 068 did not plan: the federal lands where much of the West's oil and gas is drilled, the sunlight that sets solar output, the energy households pay for, California's own generation account, the grants that built the first wave of wind and solar, the rivers whose flow is the hydropower fleet's fuel, and the distributed solar of the state that publishes it project by project. A source a chain running beside this one takes first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`; a probe's saved copy put in the connector's raw store with `runs/c059/seed_raw.py`, so a trial does not ask twice);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c058/write_table.sh` or `runs/c059/write_table.sh`, which keep the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c058/coverage_rows.sh`; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers `runs/union_resolve.py` or `runs/c059/resolve.sh` (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, www.energyinst.org, www.fueleconomy.gov, figshare.com (chain 058's session 2029: a challenge page; its API and download hosts answer), and any host chain 068 adds to the list. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches; until the chain lands, a write, a Method-cell run or an upload of that table runs with the branch's validator copied in, kept through the coverage step, and main's put back after.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **A large file is read from disk in chunks, never held whole beside another agent's jobs** (chain 058's session 2029: a 1.2 GB file read in memory was stopped by Claude Code for low memory on this 16 GB machine); a background job the system stops may leave its Python running: look for it before putting files back or releasing the lock, and never stop a Redivis upload inside a table's replace.
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected (chain 058 did it twice, `runs/c058/s2041/renumber_refs2.py`, which shifts only a number named as a read).
- **A connector whose files keep their addresses between issues asks for them `fresh` whenever the run is not `--offline`** (chain 058's session 2038).
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` (and the reads) before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, and leaves room for the whole run; a reconcile needs 7 requests.
- **A currency other than USD is a standing question for the owner.**
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2106 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2120, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2119 updates it.

Read first: chain 068's note (`docs/state/note_2026-11-10_data.md`, written by session 2097), sessions 2084 to 2097's reports, chain 067's note (`docs/state/note_2026-11-09_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2106: oil and gas on public lands (BLM's oil and gas statistics)

Long end 1:30. Pulls: at most 15 requests. The Bureau of Land Management's oil and gas statistics (www.blm.gov's published tables: applications for permits to drill received and approved, wells spud, acres leased and producing, by state and fiscal year; robots first, the Interior's notice is read 159, may be public): a series table by state and year as BLM prints them; cross-check: the federal onshore production states against `onrr_production_annual`'s federal onshore volumes.

## Session 2107: the sunlight solar runs on (NASA's POWER project)

Long end 1:30. Pulls: at most 15 requests. NASA Langley's Prediction Of Worldwide Energy Resources (power.larc.nasa.gov's daily API, which needs no key; robots and NASA's terms first): daily all-sky surface shortwave irradiance (kWh per square meter a day, a new unit added to the standard and the validator together) at the coordinates of the grid weather stations the ERW already holds (`noaa_grid_weather_stations`, at most ten), from 2020; a series table; cross-check: CAISO's and ERCOT's monthly solar generation (`state_generation_mix_monthly` or EIA-930's) against the irradiance summed to the month, sunny months higher.

## Session 2108: what households spend on energy (BEA's personal consumption expenditures by state)

Long end 1:30. Pulls: at most 15 requests. The Bureau of Economic Analysis's personal consumption expenditures by state and function (apps.bea.gov's regional downloads, the zip files of SAPCE that need no key; robots and BEA's terms first): electricity, natural gas, gasoline and other energy goods, by state and year from 2010, in USD (the unit held); a series table; cross-check: each state's electricity spending against `eia861_utility_sales`'s residential revenue summed to the state, in the same years.

## Session 2109: California's total system power (the Energy Commission)

Long end 1:30. Pulls: at most 15 requests. The California Energy Commission's Total System Electric Generation (www.energy.ca.gov's yearly tables and workbook: in-state generation by fuel, imports from the Northwest and the Southwest, and the total; robots and the State's conditions of use first, read 10): a series table by fuel, source region and year; cross-check: in-state generation against `eia_state_generation_monthly`'s California summed to the year.

## Session 2110: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind (2004, 2018, 2032, 2046, 2060, 2074, 2088) did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2111: the licenses' seventeenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 068 did not reach, those of sessions 2106 to 2109 and 2112 to 2114 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2112: the 1603 grants (the Treasury's payments in lieu of tax credits)

Long end 1:30. Pulls: at most 15 requests. The Department of the Treasury's Section 1603 awards list (the program's published list of awardees: business name, state, technology, amount funded and date; on www.treasury.gov or the archive DOE points to, robots and terms first): an events table, one row an award; cross-check: the total funded against the program's own summary figure.

## Session 2113: the rivers behind the dams (USGS's streamflow)

Long end 1:30. Pulls: at most 15 requests. The U.S. Geological Survey's daily values service (waterservices.usgs.gov, or its successor api.waterdata.usgs.gov, robots and the USGS's terms first): daily mean discharge in cubic feet a second (a new unit, `ft3/s`, added to the standard and the validator together) at the gauges below the largest hydropower plants (the Columbia at The Dalles, the Colorado below Hoover, the Tennessee, the Missouri below Garrison; at most ten gauges), from 2015, chunked by gauge; a series table; cross-check: each gauge's yearly flow against the yearly generation of the plant at it (`usbr_hydropower_monthly` or `eia923_plant_fuel_monthly`).

## Session 2114: New York's distributed solar (NYSERDA on data.ny.gov)

Long end 1:30. Pulls: at most 15 requests. NYSERDA's Statewide Distributed Solar Projects (data.ny.gov's published dataset and its CSV export, robots and New York's open data terms first): each project's county, utility, sector, capacity and interconnection date; a series table by county, sector and year, or an entities table if the projects carry their own ids (say which); cross-check: the state's total against `eia861_distributed_generation`'s small-scale solar for New York.

## Session 2115: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2116: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 068 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2117: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2118: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2119: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-11_data.md`, in session 683's form.
2. The next file (written by session 2106) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
