# Chain of 31 October 2026: sessions 2162 to 2175, data machine (lab-desktop), unattended: Great Britain's grid beside the U.S. ones, the crude oil each company imports, natural gas by end use and state, coal and oil on the rivers, the licenses' twenty-first round

machine: data

Written by session 2148, the first session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 094 (090 to 093 taken). Chain 092 asked for sessions numbered from 2162; 2162 to 2175 were free on origin's main and in chains 079 and 090's branches when this was written (a search for "session 2162" to "session 2177" and `SESSION_2162` to `SESSION_2175` found none). Session 2161 of chain 092 updates it at chain 092's end. Model: Opus 5.5, high effort.

Chain 092 was taken at 23:21 UTC on 23 October by chain 057's agent at chain 069's end (the owner's instruction for that run: run the file the queue step prints), while chains 079 and 090 ran beside it under other agents. The sources below were chosen by session 2148 among public ones the ERW does not appear to hold and that chains 057 to 092 did not plan or take: a foreign grid that publishes its data openly, the company-level crude imports behind the refinery tables, natural gas by end use, and the barges that still move coal and oil. Each source session first confirms that the ERW does not hold its source (`coverage.csv`, `sources.csv`); a source a chain running beside this one takes first, or one the ERW holds, is replaced by the session with another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c057/write_table.sh`, which keep the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c057/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write, so its metadata patch applies; **give each write its own session label** (chain 069's session 2116: six writes under one label overwrote each other's metadata patch);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 092's list (api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, www.energyinst.org, www.fueleconomy.gov, figshare.com, www.rd.usda.gov, www.irena.org, power.larc.nasa.gov below `/api/`, apps.bea.gov's `/regional/zip/`, www.iaea.org, www.sciencebase.gov, hazards.fema.gov, data.ny.gov) and any host chains 079, 090 and 092 add to it. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches, agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is one of the standard's two words, `public` or `internal`** (chain 069's session 2116: any other word reads as public in `build_coverage.py`); a table whose license is not settled is `internal` until a ruling.
- **A connector whose documents keep their addresses between issues asks for them `fresh` whenever the run is not `--offline`.**
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** chains running beside each other agree their `license_reads.csv` numbers and their data standard decisions before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted).
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one**, and leaves room for the whole run; a reconcile's cap is 10.
- **A currency other than USD is a standing question for the owner:** a foreign grid's prices are not taken; its loads and generation (MW, MWh) are.
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2162 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2176, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2175 updates it.

Read first: chain 092's note (`docs/state/note_2026-11-14_data.md`, written by session 2161), sessions 2148 to 2161's reports, chain 090's note (`docs/state/note_2026-11-13_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2162: Great Britain's grid (NESO's open data portal)

Long end 1:30. Pulls: at most 15 requests. The National Energy System Operator's data portal (www.neso.energy's data portal and its CKAN API at api.neso.energy, robots and the NESO Open Data Licence first; if the licence forbids redistribution, the table is held internal and said so): Great Britain's historic demand data (transmission demand and embedded wind and solar, half-hourly, in MW) from 2020, summed to the hour if the files are too large to hold whole (say so); a series table, no prices; cross-check: Great Britain's yearly peak and its winter evening shape against ERCOT's and PJM's in the warehouse.

## Session 2163: the crude oil each company imports (EIA's company level imports)

Long end 1:30. Pulls: at most 15 requests. EIA's Company Level Imports (www.eia.gov/petroleum/imports/companylevel/, the monthly files; EIA's robots file and its terms, record 1): each importing company's crude oil and products by country of origin and port, in thousand barrels, a month, as many months as the ceiling allows, newest first; an events or series table (say which); cross-check: the month's crude total against `eia_petroleum_snd_monthly`'s crude imports.

## Session 2164: natural gas by end use and state (EIA's Natural Gas Annual)

Long end 1:30. Pulls: at most 15 requests. EIA's Natural Gas Annual tables of consumption by end use and state (residential, commercial, industrial, vehicle fuel, electric power, and lease, plant and pipeline fuel), in MMcf, a year (www.eia.gov/naturalgas/annual/; first confirm the ERW holds no table of them, `eia_seds_state_energy` holds natural gas consumption by sector in TBtu, a different measure); a series table; cross-check: each state's electric power use against `eia923_plant_fuel_monthly`'s natural gas burned summed to the state and year.

## Session 2165: coal and oil on the rivers (the Corps of Engineers' waterborne commerce)

Long end 1:30. Pulls: at most 15 requests. The U.S. Army Corps of Engineers' Waterborne Commerce Statistics (its Navigation and Civil Works Decision Support Center's public files, robots and the Corps' terms first): the tons of coal, crude petroleum and petroleum products moved by waterway or by state, a year; a series table in short tons (`short_ton`, Decision 50); cross-check: the coal on the inland waterways against `eia_coal_distribution_quarterly`'s river shipments summed to the year.

## Session 2166: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind (2004 to 2152) did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2167: the licenses' twenty-first round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 092 did not reach, those of sessions 2162 to 2165 and 2168 to 2169 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2168: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2169: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2168.

## Session 2170: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2171: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 092 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2172: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2173: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2174: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2168.

## Session 2175: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-15_data.md`, in session 683's form.
2. The next file (written by session 2162) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
