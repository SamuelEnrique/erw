# Chain of 28 October 2026: sessions 2120 to 2133, data machine (lab-desktop), unattended: the earthquakes the oil fields set off, the households' energy tax credits, retail electricity prices and costs, the world's renewable capacity, the world's energy by country, the licenses' eighteenth round

machine: data

Written by session 2106, the first session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 079 (060 to 069 and 070 to 078 and 080 to 088 are taken; 079 was never used). Chain 069 asked for sessions numbered from 2120; 2120 to 2133 were free in every queue file, report, doc and branch on origin's main and in chains 058, 067 and 068's worktrees when this was written (a search for "session 2120" to "session 2135" and `SESSION_2120` to `SESSION_2133` found none; 2121 appears only as a number in chain 069's own file). Session 2119 of chain 069 updates it at chain 069's end. Model: Opus 5.5, high effort.

Chain 069 was taken at 21:13 UTC on 23 October by chain 057's agent (the owner's instruction for that run: run the file the queue step prints), while chain 068 ran beside it on the same machine. The sources below were chosen by session 2106 among public ones the ERW does not hold and that chains 057 to 069 did not plan: the earthquakes that wastewater injection sets off in the oil fields, the tax credits households claim for solar and efficiency, the prices and costs behind retail electricity rates, and two world tables that set the U.S. beside other countries. A source a chain running beside this one takes first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c058/write_table.sh`, `runs/c059/write_table.sh` or `runs/c057/write_table.sh`, which keep the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c059/method_cells_locked.sh` or `runs/c057/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); when the metadata patch of a write conflicts because main lacks the branch's rows, the rows are put in by key (`runs/c057/s2021/insert_rows.py`, `runs/c066/s2066/replace_rows_many.py`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, www.energyinst.org, www.fueleconomy.gov, figshare.com, www.rd.usda.gov, and any host chain 069 adds to the list. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host (FEMA's 15 seconds and the LIHEAP hub's 60, chain 066).
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **A large file is read from disk in chunks**, and a background job the system stops may leave its Python running.
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected (only a number named as a read is shifted).
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request** (chain 066's session 2066 found nine of the day's connectors without it).
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, and leaves room for the whole run; a reconcile needs 7 requests.
- **A currency other than USD is a standing question for the owner.**
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2120 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2134, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2133 updates it.

Read first: chain 069's note (`docs/state/note_2026-11-11_data.md`, written by session 2119), sessions 2106 to 2119's reports, chain 068's note (`docs/state/note_2026-11-10_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2120: the earthquakes the oil fields set off (the USGS's earthquake catalog)

Long end 1:30. Pulls: at most 15 requests. The U.S. Geological Survey's ComCat (earthquake.usgs.gov's FDSN event service, no key; robots and the USGS's terms first): every earthquake of magnitude 2.5 and above in Oklahoma, Kansas, Texas and New Mexico from 2010, by bounding boxes and years in as few requests as the service's 20,000-event limit allows; an events table (time, latitude, longitude, depth in km, magnitude and its type, the place); cross-check: the yearly counts in Oklahoma against the state's oil and gas production (`eia_crude_production_state_monthly`), the 2015 peak and its fall after the injection limits.

## Session 2121: the households' energy tax credits (the IRS's Statistics of Income)

Long end 1:30. Pulls: at most 15 requests. The IRS's Statistics of Income tables of the residential energy credits (Form 5695: the residential clean energy credit and the energy efficient home improvement credit), by state and tax year, as www.irs.gov publishes them (robots and the IRS's terms first): the number of returns and the amount claimed; a series table; cross-check: each state's clean energy credit returns against `lbnl_tracking_the_sun`'s residential systems installed in the same year, where both hold the state.

## Session 2122: retail electricity prices and costs (Berkeley Lab)

Long end 1:30. Pulls: at most 15 requests. Berkeley Lab's Retail Electricity Price and Cost Trends data file (eta-publications.lbl.gov, the host that serves Berkeley Lab's files to the ERW's reader; robots and the file's own license first, as session 991 read the hybrid file's): each state's average retail price by sector and the cost components the file gives, by year; a series table; cross-check: the residential prices against `eia_retail_electricity_prices` for the same states and years.

## Session 2123: the world's renewable capacity (IRENA)

Long end 1:30. Pulls: at most 15 requests. The International Renewable Energy Agency's Renewable Capacity Statistics (www.irena.org's published workbook, robots and IRENA's terms of use first; if the terms forbid redistribution, the table is held internal and said so): installed capacity by country, technology and year; a series table; cross-check: the United States' solar and wind against `eia_state_capacity_annual` summed to the nation.

## Session 2124: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2125: the licenses' eighteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 069 did not reach, those of sessions 2120 to 2123 and 2126 to 2127 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2126: the world's energy by country (Our World in Data)

Long end 1:30. Pulls: at most 10 requests. Our World in Data's energy dataset (the project's CSV on its GitHub repository or its own host, robots and its CC BY license first; it compiles the Energy Institute's and Ember's figures, whose own terms the record holds: the session reads which columns are whose before taking them): primary energy and electricity by source and country, by year; a series table of the columns whose source's terms allow it, held internal otherwise; cross-check: the United States' rows against `eia_primary_energy_monthly` summed to the year.

## Session 2127: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold, chosen by the session; say why.

## Session 2128: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2129: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 960: each note's checks against the code and the table, every contradiction acted on.

## Session 2130: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. A first `--reconcile` for any table of chain 069 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2131: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2132: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2133: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-12_data.md`, in session 683's form.
2. The next file (written by session 2120) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
