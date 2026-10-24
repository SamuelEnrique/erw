# Chain of 1 November 2026: sessions 2176 to 2189, data machine (lab-desktop), unattended: Canada's electricity by province, the offshore incidents, the reactors' inspection findings, Canada's oil and gas supply, the licenses' twenty-second round

machine: data

Written by session 2162, the first session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on the running chains' branches (`wip/2134-2147-data`, `wip/2148-2161-data`), was 097 (090 to 096 taken). Chain 094 asked for sessions numbered from 2176; 2176 to 2189 were free on origin's main and on those branches when this was written (a search for "session 2176" to "session 2189" and `SESSION_2176` to `SESSION_2189` found none). Session 2175 of chain 094 updates it at chain 094's end. Model: Opus 5.5, high effort.

Chain 094 was taken at 00:02 UTC on 24 October by chain 059's agent when chain 079 landed (the owner's instruction for that run: run the file the queue step prints), while chains 090 and 092 ran beside it under other agents. The sources below were chosen by session 2162 among public ones the ERW does not hold and that chains 057 to 094 did not plan or take (`sources.csv` on main and on chains 090 and 092's branches, and their queue files, searched): Canada's electricity and its oil and gas supply from its statistics agency (in physical units, never in CAD), the incidents on the offshore platforms, and the NRC's inspection findings at each reactor. Each source session first confirms that the ERW does not hold its source; a source a chain running beside this one takes first, or one the ERW holds, is replaced by the session with another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout **under the data lock** (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c057/write_table.sh`; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write, so its metadata patch applies; give each write its own session label; a table written again on the branch leaves its older metadata rows to be dropped by hand (keep the row with the later run time);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 094's list, www.usda.gov (HTTP 403 at its robots file, chain 092), emp.lbl.gov (Berkeley Lab's data files, HTTP 403), and any host chains 090, 092 and 094 add to it. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches, agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is `public` or `internal`**; a table whose license is not settled is `internal` until a ruling.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write, a trial or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout (trials included), waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** agreed with the chains running beside it before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted). `tests/test_session152` requires the reads numbered without a gap.
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape;** every file's em and en dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one,** and leaves room for the whole run: a reconcile needs about 7 requests (cap 10), a plain upload of one table with the metadata tables more than 50; a long upload runs as a detached process, so the foreground limit cannot stop it inside a table.
- **A currency other than USD is a standing question for the owner:** a foreign grid's or country's prices are not taken; its quantities are.
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2176 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2190, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2189 updates it.

Read first: chain 094's note (`docs/state/note_2026-11-15_data.md`, written by session 2175), sessions 2162 to 2175's reports, chain 092's note, `docs/reviews/siting-gaps.md`.

## Session 2176: Canada's electricity by province (Statistics Canada)

Long end 1:30. Pulls: at most 15 requests. Statistics Canada's monthly electric power generation by province and type of generation (table 25-10-0015-01, its full-table CSV download from www150.statcan.gc.ca; robots and the Statistics Canada Open Licence first): MWh a month by province and source, from 2016; a series table; cross-check: each province's yearly total against the CER's exports to the U.S. held in `cer_electricity_trade` and Ontario's against `ieso_ontario_demand_hourly` summed to the year.

## Session 2177: the incidents on the offshore platforms (BSEE)

Long end 1:30. Pulls: at most 15 requests. The Bureau of Safety and Environmental Enforcement's offshore incident statistics or its incident investigation data (www.bsee.gov or data.bsee.gov; robots and terms first): each reported incident with its date, area and block or platform, type (fire, injury, spill, loss of well control) and severity; an events table; cross-check: incidents by year against `boem_offshore_platforms`' platforms and `boem_ogor_lease_production_monthly`'s production, and the platforms named matched to BOEM's ids.

## Session 2178: the reactors' inspection findings (the NRC's Reactor Oversight Process)

Long end 1:30. Pulls: at most 15 requests. The NRC's inspection findings and performance indicators by plant (www.nrc.gov's Reactor Oversight Process pages; robots first, its terms are the record's): each finding with its plant, quarter, cornerstone and significance color; an events table; cross-check: the plants named against `nrc_power_reactors`, and findings by plant beside `nrc_event_notifications`' reports.

## Session 2179: Canada's oil and gas supply (Statistics Canada)

Long end 1:30. Pulls: at most 15 requests. Statistics Canada's monthly supply and disposition of crude oil and equivalent (table 25-10-0063-01) and of natural gas (25-10-0055-01), in cubic metres and as the tables give them, by province; a series table (a unit the standard lacks is added after the chains' agreed numbers); cross-check: Canada's crude exports against EIA's crude imports from Canada (`eia_crude_imports_detail_monthly`).

## Session 2180: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind (2004 to 2166) did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2181: the licenses' twenty-second round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 094 did not reach, those of sessions 2176 to 2179 and 2182 to 2183 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2182: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2183: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2182.

## Session 2184: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2185: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 094 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (from a branch merged with main first, so `erw_coverage` holds every landed chain's tables); `--reconcile`; the release note extended. Nothing released.

## Session 2186: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2187: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2188: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2182.

## Session 2189: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-16_data.md`, in session 683's form.
2. The next file (written by session 2176) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
