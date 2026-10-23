# Chain of the night of 24 October 2026: sessions 2042 to 2055, data machine (lab-desktop), unattended: storms, the reactors' event reports, LNG's export authorizations, the states' climate, transport's energy, the utilities' capital spending, the grid's resilience grants, the licenses' thirteenth round

machine: data

Written by session 2028, the first session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 059 (060 to 078 are the code machine's). Chain 058 asked for sessions numbered from 2042; 2042 to 2055 were free in every queue file, report, doc and branch when this was written (a search of origin's main and chain 056's branch for "session 2042" to "session 2055" and `SESSION_2042_` to `SESSION_2055_` found none). Session 2041 of chain 058 updates it at chain 058's end. Model: Opus 5.5, high effort.

Chain 058 was taken at 18:05 UTC on 23 October while chain 057 ran beside it on the same machine (the owner's instruction: each chain in its own worktrees and `wip/` branches, the data lock taken for every warehouse write and waited for with `scripts/duty.py beat`, the build lock before every build). The sources below were chosen by session 2028 among public ones the ERW does not hold (none is in `warehouse/metadata/coverage.csv`, `sources.csv` or a connector on main or on chain 056's branch): the weather that takes the grid down, the reactors' own reports, the export side of the gas market, the climate that moves demand, transport's energy as electric vehicles grow, the utilities' spending that sets rates, and the federal money for the grid. A source that chain 057's sessions 2020 and 2021 or chain 058 took first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, and data.usbr.gov's `/rise/api` and time series queries, with any host chains 057 and 058 add to the list.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in for the one run, and main's put back.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task ("ERW data machine daily") from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile. Never copy a branch's metadata into the main checkout while this machine's daily task runs there.
- **Two chains on one machine:** while another chain runs on this machine, each works only in its own worktrees and branches, takes the data lock for every warehouse write and waits for it (`scripts/duty.py beat` while it waits) rather than giving up, takes the build lock before every build, and never touches the other's branches.
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one.**
- **Session 2042 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2056, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2055 updates it.

Read first: chain 058's note (`docs/state/note_2026-11-06_data.md`, written by session 2041), sessions 2028 to 2041's reports, chain 057's note (`docs/state/note_2026-11-05_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2042: storms (NOAA's Storm Events Database)

Long end 1:30. Pulls: at most 15 requests. The National Centers for Environmental Information's Storm Events Database bulk files (www.ncei.noaa.gov's `/pub/data/swdi/stormevents/csvfiles/`, the yearly details files; robots and terms first, and the NOAA NCEI verdicts in `license_verdicts.csv` read, since ISD's non-U.S. data carry WMO restrictions that these U.S. files may not): each event's type, state, county or zone, begin and end time, and property damage, from 2015, the types that take lines down (thunderstorm wind, high wind, ice storm, winter storm, hurricane, tornado, wildfire, heat, extreme cold) first; an events table of its own, the narratives not taken; cross-check: each year's ice storms and hurricanes against chain 058's OE-417 weather events in the same states and days.

## Session 2043: the reactors' event reports (the NRC's event notification reports)

Long end 1:30. Pulls: at most 15 requests. The Nuclear Regulatory Commission's Event Notification Reports (www.nrc.gov's `/reading-rm/doc-collections/event-status/event/`, robots and terms first): each power reactor event's number, facility, unit, notification and event time, the reactor's power before and after, and the reporting rule (a scram is 50.72(b)(2)(iv)(B)), for the latest two years the pages carry; an events table, the narrative not taken; cross-check: each scram against `nrc_reactor_status`'s power for that unit on that day and the next.

## Session 2044: LNG's export authorizations (DOE's Office of Fossil Energy and Carbon Management)

Long end 1:30. Pulls: at most 15 requests. DOE's long-term LNG export authorizations (www.energy.gov's FECM pages on LNG exports and its summary of applications and authorizations, robots and terms first): each project's applicant, terminal, authorized volume in Bcf a year or billion cubic feet a day, free trade and non-free trade status, order number and date, and the term; an entities table, one row a terminal and authorization; cross-check: the operating terminals against `eia_lng_exports_monthly`'s export points and the 2025 volumes against the authorized ones.

## Session 2045: the states' climate (NOAA's Climate at a Glance)

Long end 1:30. Pulls: at most 15 requests. NCEI's Climate at a Glance statewide time series (www.ncei.noaa.gov's `/access/monitoring/climate-at-a-glance/statewide/time-series/`, the CSV each page offers; robots and terms first): each of the 48 states' monthly average temperature and precipitation, with the 20th century mean the publisher prints, from 2000, in as few requests as its paths allow (a state and variable a request may be too many: say so and take the states the cap allows, the largest power loads first); a series table; cross-check: each state's summer and winter months against `noaa_cpc_degree_days_daily`'s degree days summed to the month (warmer months, more cooling degree days).

## Session 2046: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that sessions 2004, 2018 and 2032 did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2047: the licenses' thirteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 058 did not reach, those of sessions 2042 to 2045 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2048: transport's energy (Oak Ridge's Transportation Energy Data Book)

Long end 1:30. Pulls: at most 20 requests. Oak Ridge National Laboratory's Transportation Energy Data Book (tedb.ornl.gov, the chapter workbooks of the latest edition; robots and terms first): transportation's energy use by mode and fuel, and light vehicle sales by powertrain (conventional, hybrid, plug-in hybrid, battery electric), a year a row; a series table; cross-check: transportation's total energy use against `eia_sector_energy_consumption_monthly`'s transportation sector summed to the year, and the plug-in sales against chain 058's registration counts.

## Session 2049: the utilities' capital spending (the SEC's XBRL frames)

Long end 1:30. Pulls: at most 20 requests. The Securities and Exchange Commission's XBRL frames (data.sec.gov's `/api/xbrl/frames/`, one concept and year a request; www.sec.gov's robots file and its fair access policy first: a declared reader with a contact, well under ten requests a second): the electric and gas utilities' (SIC 4911, 4931 and 4932, from each company's submissions file) yearly payments for property, plant and equipment, from 2015; a series table by company, the company's name and CIK as published; cross-check: three companies' 2024 figures against the cash flow statement of their own 10-K in EDGAR.

## Session 2050: the grid's resilience grants (DOE's Grid Deployment Office)

Long end 1:30. Pulls: at most 20 requests. The Grid Deployment Office's Grid Resilience and Innovation Partnerships (GRIP) selections and the Grid Resilience State and Tribal Formula Grants (www.energy.gov's GDO pages, robots and terms first): each selection's recipient, state, round, program, federal amount and the project's title, as DOE publishes them; an events table, one row a selection; cross-check: each round's federal total against the amount DOE's announcement of that round prints.

## Session 2051: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2052: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 058 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2053: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2054: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2055: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-07_data.md`, in session 683's form.
2. The next file (written by session 2042) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
