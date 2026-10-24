# Chain of 2 November 2026: sessions 2210 to 2223, data machine (lab-desktop), unattended: the price indexes of power and fuel, the reservoirs behind Hoover and Glen Canyon, California's rooftop solar, two sources of the sessions' choosing, the licenses' twenty-third round

machine: data

Written by session 2176, the first session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on the running chains' branches, was 098 (090 to 097 taken). Chain 097 asked for sessions numbered from 2190; 2200 to 2209 are taken (the code chains' sessions on main), so this chain starts at 2210, the first block of fourteen free numbers on origin's main and every pushed branch (a search of `SESSION_*` reports and the queue files' session ranges found none from 2210 to 2223). Session 2189 of chain 097 updates it at chain 097's end. Model: Opus 5.5, high effort.

Chain 097 was taken at 00:45 UTC on 24 October by chain 057's agent at chain 092's end (the owner's instruction for that run: run the file the queue step prints), with chain 094's agent told; chains 090 and 094 ran beside it under other agents. The sources below were chosen by session 2176 among public ones the ERW does not appear to hold and that chains 057 to 097 did not plan or take: the price indexes that put power and fuel prices in the economy's terms, the two reservoirs whose levels set the Southwest's hydropower, and California's interconnected rooftop solar. Each source session first confirms that the ERW does not hold its source (`coverage.csv`, `sources.csv` on main and on the running chains' branches, and their queue files); a source taken first by a chain beside this one, or held, is replaced by another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout **under the data lock** (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c057/write_table.sh`; `runs/c057/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (`runs/union_resolve.py` where each side only adds its own row; then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write, so its metadata patch applies; give each write its own session label;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 097's list (among them www.usda.gov, emp.lbl.gov, api.neso.energy, donnees.hydroquebec.com, www.iwr.usace.army.mil, data.ny.gov) and any host chains 090, 094 and 097 add to it. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID, FRED's API key; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches, agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is `public` or `internal`**; a table whose license is not settled is `internal` until a ruling.
- **A connector whose documents keep their addresses between issues asks for them `fresh` whenever the run is not `--offline`** (past years' files included where the publisher rewrites them).
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write, a trial or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout (trials included), waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** agreed with the chains running beside it before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted). `tests/test_session152` requires the reads numbered without a gap.
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape;** every file's em and en dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one,** and leaves room for the whole run.
- **A currency other than USD is a standing question for the owner.**
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2210 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2224, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2223 updates it.

Read first: chain 097's note (written by session 2189), sessions 2176 to 2189's reports, chain 094's and chain 092's notes, `docs/reviews/siting-gaps.md`.

## Session 2210: the price indexes of power and fuel (FRED's published series)

Long end 1:30. Pulls: at most 15 requests. The Federal Reserve Bank of St. Louis's FRED, its keyless CSV downloads (`fred.stlouisfed.org/graph/fredgraph.csv?id=<series>`; robots and FRED's terms first, and each series' own source and its terms, since FRED republishes BLS's and others' series): the producer price indexes for electric power and for natural gas, and the consumer price indexes for electricity and for utility gas service, monthly from 2000; a series table (`index`, Decision 53); cross-check: the residential electricity index's yearly change against `eia_retail_electricity_prices`' residential price for the nation.

## Session 2211: the reservoirs behind Hoover and Glen Canyon (Reclamation's Lower Colorado data)

Long end 1:30. Pulls: at most 15 requests. The Bureau of Reclamation's published reservoir data for Lake Mead and Lake Powell (www.usbr.gov's Lower Colorado and Upper Colorado pages and their data files, not data.usbr.gov's `/rise/api`, which is not asked; robots and the Interior's terms first, Reclamation's verdict is read 173): daily or monthly elevation, storage and release from 2015; a series table (a unit the standard lacks, feet of elevation or acre-feet, added after the chains' agreed numbers); cross-check: each reservoir's release against `usgs_streamflow_daily`'s gauges below Hoover and at Lees Ferry, and its elevation against `usbr_hydropower_monthly`'s generation at the dam.

## Session 2212: California's rooftop solar (California DG Stats)

Long end 1:30. Pulls: at most 15 requests. California Distributed Generation Statistics' interconnected project data (californiadgstats.ca.gov's downloads, robots and terms first; if a file is past what a session can read from disk in chunks, its monthly summaries instead, and say so): interconnected systems and capacity by utility, county, sector and month; a series table; cross-check: the state's total against `eia861_distributed_generation`'s small-scale solar for California and `lbnl_tracking_the_sun`'s California systems.

## Session 2213: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2214: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named in a note on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2215: the licenses' twenty-third round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 097 did not reach, those of sessions 2210 to 2213 and 2217 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2216: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2217: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2213.

## Session 2218: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2219: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2220: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2221: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2213.

## Session 2222: a second gap of held-but-undescribed tables

Long end 1:30. Pulls: none. As session 2214, the next six.

## Session 2223: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2210) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
