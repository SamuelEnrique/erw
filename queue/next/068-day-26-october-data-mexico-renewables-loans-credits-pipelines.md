# Chain of 26 October 2026: sessions 2084 to 2097, data machine (lab-desktop), unattended: Mexico's grid beside ERCOT, the world's renewable capacity, the rural utilities' loans, the energy tax credits, the gas pipelines between states, the world's reactors, ENSO, the licenses' sixteenth round

machine: data

Written by session 2070, the first session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 068 (066 and 067 are the data machine's, 070 to 078 the code machine's, 080 to 085 the laptops'). Chain 067 asked for sessions numbered from 2084; 2084 to 2097 were free in every queue file, report, doc and branch on origin's main and in chains 057 and 058's worktrees when this was written (a search for "session 2084" to "session 2097" and `SESSION_2084_` to `SESSION_2097_` found none). Session 2083 of chain 067 updates it at chain 067's end. Model: Opus 5.5, high effort.

Chain 067 was taken at 20:00 UTC on 23 October by chain 059's agent (the owner's instruction for that run: run the file the queue step prints) while chain 066 ran beside it under another agent, and chain 058 under a third. The sources below were chosen by session 2070 among public ones the ERW does not hold and that chains 057 to 067 did not plan: the Mexican grid that trades with ERCOT, the world's renewable capacity beside the U.S. fleets, the federal loans to rural utilities, the tax credits that pay for clean energy, the pipelines that carry gas between states, the world's reactors, and the Pacific's winter signal. A source a chain running beside this one takes first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`; a probe's saved copy put in the connector's raw store with `runs/c059/seed_raw.py`, so a trial does not ask twice);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh`, which keeps the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c059/method_cells_locked.sh`; `runs/c059/coverage_row.sh`), `runs/c045/finish_table.sh`, and the resolvers `runs/c059/resolve.sh` (then, for a table written again, the older of its two metadata rows dropped by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, and any host chains 058 to 067 add to the list.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout** (from a worktree it finds no ledger file and may fail).
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in, kept through the coverage step, and main's put back after.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task ("ERW data machine daily") from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits) rather than giving up, puts main's files back before releasing it, and never touches the others' branches. **No commit and no pull in the main checkout while another chain holds the lock** (its files are copied in, and a local commit breaks its fast-forward pull): queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **A background job the system stops for low memory may leave its Python running:** look for it before putting files back or releasing the lock, and never stop a Redivis upload inside a table's replace.
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` (and the reads, for a page already read) before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, and leaves room for the whole run.
- **Session 2084 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2098, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2097 updates it.

Read first: chain 067's note (`docs/state/note_2026-11-09_data.md`, written by session 2083), sessions 2070 to 2083's reports, chain 066's note (`docs/state/note_2026-11-08_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2084: Mexico's grid beside ERCOT (CENACE's prices and demand)

Long end 1:30. Pulls: at most 15 requests. The Centro Nacional de Control de Energia's public market data (www.cenace.gob.mx, robots and its terms of use first; its pages are in Spanish): the day-ahead local marginal prices of the Baja California and national systems' zones or nodes nearest the U.S. border, or the system demand by region, a day or an hour, for the latest full year and this year, in as few files as its reports allow; a series table (MXN, a new unit, added to the standard and the validator together, or the session says why not); if the terms forbid reuse or the files are reached only through a form, the session stops and says so. Cross-check: the border days of ERCOT's and CAISO's highest prices against Mexico's.

## Session 2085: the world's renewable capacity (IRENA's statistics)

Long end 1:30. Pulls: at most 15 requests. The International Renewable Energy Agency's Renewable Capacity Statistics (www.irena.org's publication and its data file, or IRENASTAT's downloadable tables; robots and IRENA's terms of use first): each country's installed capacity by technology (solar, wind onshore and offshore, hydropower, bioenergy, geothermal, storage where given), a year a row, from 2015; a series table; cross-check: the United States' rows against `eia_state_capacity` or EIA's net summer capacity summed to the nation for the same years (IRENA counts AC or DC as it says).

## Session 2086: the rural utilities' loans (USDA's Rural Utilities Service)

Long end 1:30. Pulls: at most 15 requests. USDA Rural Development's Electric Infrastructure Loan and loan guarantee program and its Powering Affordable Clean Energy and New ERA selections (www.rd.usda.gov's published lists, robots and terms first): each loan's or award's borrower (cooperative), state, program, amount and date as published; an events table; cross-check: the New ERA awards' total against the amount USDA's announcement prints.

## Session 2087: the energy tax credits (the IRS's Statistics of Income)

Long end 1:30. Pulls: at most 15 requests. The Internal Revenue Service's Statistics of Income tables on energy credits (www.irs.gov's SOI tax stats, the residential energy credits of Form 5695 by state and year, and the business credits of Form 3800 where SOI tabulates them; robots and terms first): number of returns and amount claimed, a year a row, from 2015; a series table; cross-check: the national totals against the total SOI's own summary table prints.

## Session 2088: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind (2004, 2018, 2032, 2046, 2060, 2074) did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2089: the licenses' sixteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 067 did not reach, those of sessions 2084 to 2087 and 2090 to 2092 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2090: the gas pipelines between states (EIA's state-to-state capacity)

Long end 1:30. Pulls: at most 15 requests. EIA's U.S. State-to-State Capacity of natural gas pipelines (www.eia.gov's natural gas pipeline data page, the workbook it links; not `/archive/`): each pair of states' inflow and outflow capacity in MMcf a day, a year a row, as EIA gives them; a series table (the pipeline projects are already held, `eia_gas_pipeline_projects`); cross-check: the capacity added between states in recent years against the projects held there, completed in the same years.

## Session 2091: the world's reactors (the IAEA's PRIS)

Long end 1:30. Pulls: at most 15 requests. The International Atomic Energy Agency's Power Reactor Information System (pris.iaea.org's public country and reactor pages, robots and the IAEA's terms of use first; if the terms forbid reuse or automated reading, the session stops and says so): each operating, under construction and shut down reactor's country, name, type, net and gross capacity, construction start, grid connection and shutdown dates; an entities table; cross-check: the United States' reactors against `nrc_power_reactors` by name and capacity.

## Session 2092: the Pacific's winter signal (NOAA CPC's ENSO index)

Long end 1:30. Pulls: at most 10 requests. The Climate Prediction Center's Oceanic Nino Index and its ENSO outlook (www.cpc.ncep.noaa.gov's ONI table and the probabilistic outlook's data, robots and NOAA's terms first; ftp.cpc.ncep.noaa.gov, which chain 056 read, may serve the same): the three-month running ONI from 1950 and the outlook's probabilities of La Nina, neutral and El Nino by season; a series table; cross-check: the winters of strong La Nina and El Nino against `noaa_climdiv_state_monthly`'s winter temperatures in the South and the North (chain 059).

## Session 2093: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2094: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 067 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2095: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2096: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2097: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-10_data.md`, in session 683's form.
2. The next file (written by session 2084) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
