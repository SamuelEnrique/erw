# Chain of 5 November 2026: sessions 2252 to 2265, data machine (lab-desktop), unattended: Poland's grid (PSE), Belgium's (Elia), New Zealand's (EMI), the Columbia River's federal dams, the licenses' twenty-sixth round

machine: data

Written by session 2238, the first session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on the running chains' branches, was 102 (100 and 101 taken). Chain 101 asked for sessions numbered from 2252; 2252 to 2265 were free on origin's main when this was written. Session 2251 of chain 101 updates it at chain 101's end. Model: Opus 5.5, high effort.

Chain 101 was taken at 03:02 UTC on 24 October by chain 059's agent when chain 098 landed (the owner's instruction: run the file the queue step prints), beside chains 097 and 099 under other agents. Chain 097 takes Statistics Canada, BSEE, the NRC, the NTD and EPA's NEEDS; chain 099 the IESO's generation by fuel, Eurostat's electricity balances, the UK's gas balance, Statistics Norway, SMARD's Germany, CBS's Netherlands and SCB's Sweden; chain 101 France, Spain, Brazil and Australia. The four sources below were chosen by session 2238 among public ones the ERW does not hold (`sources.csv` on main searched for PSE, Elia, the Electricity Authority's EMI and the Corps' Northwestern Division, none found) and that chains 057 to 101 did not plan or take: the grids of three more open operators, and the federal hydropower of the Columbia, the largest in the United States. Each is a quantity, never a price in another currency. Each source session first confirms that the ERW does not hold its source; a source taken first by a chain beside this one, or held, is replaced by another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout under the data lock (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c090/write_table.sh`; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write; give each write its own session label; a table written again on the branch leaves its older metadata rows to be dropped (keep the later run's), and a table whose keys change is removed from the output folder under the data lock before it is written again (the writer merges);
- a publisher's file that can end with the day in progress keeps only the days ended at its retrieval (chain 098's `ended_days`);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/` and any path holding `archive/`** (EIA's company-level import files among them): neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 101's list and any host chains 097, 099 and 101 add to it; among them gml.noaa.gov's `/webdata/` and `/aftp/` (its robots file, session 2137), api.bls.gov (its robots file disallows `/`), www.sciencebase.gov (its robots file disallows `/` for every reader), California's DG Stats (its terms forbid robots), www.mbie.govt.nz (a bot challenge), opendata.cbs.nl's OData paths (its robots file), api.scb.se's v1 (no answer) and EirGrid's data (its disclaimer: needs written permission), the last four from chain 099. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID, FRED's API key; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host (open.canada.ca's 20 seconds).
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches, agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is `public` or `internal`**; a table whose license is not settled is `internal` until a ruling. A table registered from a source a held table already uses takes a source id of its own, so the held table's row is not overwritten.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write, a trial or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout (trials included), waits for it, puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** agreed with the chains running beside it before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted). `tests/test_session152` requires the reads numbered without a gap.
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape;** every file's em and en dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one,** and leaves room for the whole run (a plain upload of five tables with the metadata tables took 79 requests in session 2171); a long upload runs as a detached process; the branch is merged with main before the upload, so the metadata tables hold every landed chain's tables.
- **A currency other than USD is a standing question for the owner:** a foreign country's prices are not taken; its quantities are.
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2252 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2266, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2265 updates it.

Read first: chain 101's note (written by session 2251), sessions 2238 to 2251's reports, chain 098's and chain 099's notes, `docs/reviews/siting-gaps.md`.

## Session 2252: Poland's generation and demand (PSE's reports API)

Long end 1:30. Pulls: at most 15 requests. PSE, Poland's transmission system operator (its reports API at api.raporty.pse.pl or its successor; robots and PSE's terms first): the national power balance, demand and generation by type of unit, at its interval, from 2024 or as far back as the API serves, within the ceiling; the prices are not taken (PLN); a series table in MW or MWh as published; cross-check: a year's demand against `owid_ember_electricity_annual`'s Poland and Eurostat's (chain 099's `eurostat_electricity_monthly`) where both hold the year.

## Session 2253: Belgium's load and generation (Elia's Open Data)

Long end 1:30. Pulls: at most 15 requests. Elia's Open Data platform (opendata.elia.be, its export API; robots and Elia's terms first): Belgium's total load and its measured wind and solar generation, a quarter hour or an hour, from 2020, within the ceiling; a series table in MW; cross-check: a year's load against Ember's Belgium demand.

## Session 2254: New Zealand's generation by fuel (the Electricity Authority's EMI)

Long end 1:30. Pulls: at most 15 requests. The Electricity Authority's Electricity Market Information (www.emi.ea.govt.nz and its public file store; robots and the Authority's terms, CC BY 4.0 as stated, first; www.mbie.govt.nz is not asked): generation by fuel type, a month, or a half hour summed to a day, from 2015, within the ceiling; a series table in MWh; cross-check: a year's total against Ember's New Zealand demand.

## Session 2255: the Columbia River's federal dams (the Corps of Engineers' Northwestern Division)

Long end 1:30. Pulls: at most 15 requests. The Northwestern Division's water management data (www.nwd-wc.usace.army.mil, its dataquery service; robots and terms first; www.iwr.usace.army.mil, which refused the reader, is not asked): the outflow, forebay elevation and generation of the federal dams on the Columbia and the lower Snake (Grand Coulee, Chief Joseph, McNary, John Day, The Dalles, Bonneville and the four lower Snake dams, where published), a day, from 2015; a series table (ft and ft3/s as chain 098's Decisions 71 and 65, MWh for generation); cross-check: generation against `bpa_ba_load_generation`'s hydro, a year. If the host bars the reader, another public U.S. hydropower source, and the session says why.

## Session 2256: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named in a note on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2257: the licenses' twenty-sixth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 101 did not reach, those of sessions 2252 to 2255 and 2258 to 2259 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2258: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2259: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2258.

## Session 2260: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2261: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first and the branch merged with main. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2262: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2263: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2264: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2258.

## Session 2265: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2252) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
