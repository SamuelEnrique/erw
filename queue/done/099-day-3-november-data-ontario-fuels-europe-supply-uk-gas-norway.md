# Chain of 3 November 2026: sessions 2224 to 2237, data machine (lab-desktop), unattended: Ontario's generation by fuel, Europe's monthly electricity supply, the UK's gas balance, Norway's electricity, the licenses' twenty-fourth round

machine: data

Written by session 2210, the first session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on the running chains' branches, was 099 (090 to 098 taken). Chain 098 asked for sessions numbered from 2224; 2224 to 2237 were free on origin's main and every pushed branch when this was written (a search for `SESSION_2224` to `SESSION_2237` and "session 2224" to "session 2237" found none). Session 2223 of chain 098 updates it at chain 098's end. Model: Opus 5.5, high effort.

Chain 098 was taken at 01:29 UTC on 24 October by chain 059's agent when chain 094 landed (the owner's instruction for that run: run the file the queue step prints), while chain 097 ran beside it under another agent (chain 090 under a third). The sources below were chosen by session 2210 among public ones the ERW does not hold and that chains 057 to 098 did not plan or take (`sources.csv` on main and on the running chains' branches, and their queue files, searched): the fuels behind Ontario's demand (the IESO, whose terms are on record), the European countries' monthly electricity balances (Eurostat, whose terms are on record and which publishes quantities, not prices), the UK's gas supply and demand (GOV.UK, the Open Government Licence) and Norway's hydro-led electricity (Statistics Norway). Each source session first confirms that the ERW does not hold its source; a source taken first by a chain beside this one, or held, is replaced by another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout under the data lock (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c057/write_table.sh`; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write; give each write its own session label; a table written again on the branch leaves its older metadata rows to be dropped (keep the later run's), and a table whose keys change is removed from the output folder under the data lock before it is written again (the writer merges);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/` and any path holding `archive/`** (EIA's company-level import files among them): neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 098's list and any host chains 097 and 098 add to it. JODI (jodidata.org) is not pulled.
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
- **Session 2224 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2238, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2237 updates it.

Read first: chain 098's note (written by session 2223), sessions 2210 to 2223's reports, chain 097's note, `docs/reviews/siting-gaps.md`.

## Session 2224: Ontario's generation by fuel (the IESO)

Long end 1:30. Pulls: at most 15 requests. The IESO's hourly generator output by fuel type (its public reports site, the yearly `GenOutputbyFuelHourly` files or their successor; robots first, the IESO's verdict is on record: may be public, its notice carried in the header): Ontario's generation by fuel, an hour, from 2020; a series table; cross-check: the hourly total against `ieso_ontario_demand_hourly`'s demand plus net exports, and the nuclear share against the reactors in `nrc_power_reactors`' Canadian neighbours as the IESO names them.

## Session 2225: Europe's monthly electricity supply (Eurostat)

Long end 1:30. Pulls: at most 15 requests. Eurostat's monthly supply, transformation and consumption of electricity (`nrg_cb_em`, through the SDMX API as session 2123 took `nrg_inf_epcrw`; its terms are the record's, the countries outside the EU, EFTA and the candidates left out): each country's net production by fuel, imports, exports and supply, in GWh, monthly from 2016; a series table in MWh; cross-check: a year's net production against `owid_ember_electricity_annual`'s demand for the same countries, and the EU's sum against Eurostat's own EU27_2020 total.

## Session 2226: the UK's gas balance (DESNZ, Energy Trends section 4)

Long end 1:30. Pulls: at most 15 requests. The Department for Energy Security and Net Zero's Energy Trends section 4 (natural gas: supply, imports by route, exports and demand by sector, quarterly; GOV.UK, the Open Government Licence, as session 2167 read it): a series table in the units the tables give (GWh written as MWh; a unit the standard lacks added after the chains' agreed numbers); cross-check: the gas used for electricity against `desnz_uk_electricity_quarterly`'s gas-fired generation, and the LNG imports against EIA's U.S. LNG exports to the UK where the warehouse holds them.

## Session 2227: Norway's electricity (Statistics Norway)

Long end 1:30. Pulls: at most 15 requests. Statistics Norway's monthly electricity statistics (table 08307 or its successor through the SSB API, robots and SSB's terms, CC BY 4.0 as stated, first): production by type, consumption, imports and exports, in MWh or GWh, monthly from 2010; a series table; cross-check: the yearly totals against `owid_ember_electricity_annual`'s Norway demand and Eurostat's figures for Norway (session 2225).

## Session 2228: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named in a note on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes; `desnz_uk_renewables_quarterly` (chain 094's session 2174, written after its notes session) among them.

## Session 2229: the licenses' twenty-fourth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 098 did not reach, those of sessions 2224 to 2227 and 2230 to 2231 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2230: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2231: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2230.

## Session 2232: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2233: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first and the branch merged with main. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2234: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2235: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2236: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2230.

## Session 2237: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2224) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
