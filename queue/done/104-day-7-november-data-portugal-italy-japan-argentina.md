# Chain of 7 November 2026: sessions 2280 to 2293, data machine (lab-desktop), unattended: Portugal's grid, Italy's, Japan's areas' demand, Argentina's, the licenses' twenty-eighth round

machine: data

Written by session 2266, the first session of `queue/done/103-day-6-november-data-south-africa-chile-colombia-taiwan.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on the running chains' branches, was 104 (100 to 103 taken). Sessions 2280 to 2293 were free on origin's main when this was written. Session 2279 of chain 103 updates it at chain 103's end. Model: Opus 5.5, high effort.

Chain 103 was taken at 03:56 UTC on 24 October by chain 090's agent when chain 099 landed (the owner's instruction: run the file the queue step prints), beside chains 101 and 102 under other agents. The four sources below were chosen by session 2266 among public ones the ERW does not hold (`sources.csv` on main searched for REN, Terna, OCCTO and CAMMESA, none found) and that chains 057 to 103 did not plan or take: Portugal's and Italy's grids beside the European ones chains 099, 101 and 102 hold, Japan's ten areas' demand, and Argentina's wholesale market quantities. Each is a quantity, never a price in another currency. Each source session first confirms that the ERW does not hold its source; a source taken first by a chain beside this one, or held, or whose host or terms bar the reader, is replaced by another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout under the data lock (`runs/c092/trial.sh`), whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c057/write_table.sh`, with `VALIDATOR=branch` for a new unit; `runs/c057/method_cells_locked.sh`, whose run validates with main's validator, so a table with a new unit is set back to pass by hand), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); give each write its own session label; a table written again on the branch leaves its older metadata rows to be replaced by key (`runs/c066/s2066/replace_rows_many.py`);
- a publisher's file that can end with the day in progress keeps only the days ended at its retrieval (chain 098's `ended_days`); a file in local time is checked for its time base (chain 101: ONS's Brasilia time stated nowhere) and its daylight-saving days (chain 101: RTE's fixed 96 quarter hours a day);
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/103-day-6-november-data-south-africa-chile-colombia-taiwan.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/` and any path holding `archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file or terms bar it, are not asked again without a ruling:** every host of chain 103's list and any host chains 101, 102 and 103 add to it; among them www.sciencebase.gov (its robots file disallows `/` for every reader), www.phmsa.dot.gov (HTTP 403), odre.opendatasoft.com (its robots file closes `/api/` and every download to all but Google), nemweb.com.au and www.aemo.com.au (a Cloudflare challenge), www.energy.gov.au and www.aer.gov.au (the connection reset at robots.txt), www.mbie.govt.nz (a bot challenge), opendata.cbs.nl's OData paths, api.scb.se's v1, EirGrid's data (written permission), Eskom's Data Portal (its disclaimer: "may not be exploited by the User for any purposes"), data.gov.tw (HTTP 500 at its robots file), opendata.elia.be (its robots file closes `/api/` and downloads to all but Google) and transparency.apg.at (no answer). JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID, FRED's API key; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches (72 on main when this was written), agreed with the agents of the chains running beside it.
- **`sources.csv`'s license is `public` or `internal`**; a table whose license is not settled is `internal` until a ruling. A table registered from a source a held table already uses takes a source id of its own.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write, a trial or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout (trials included), waits for it, puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** agreed with the chains running beside it before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted). `tests/test_session152` requires the reads numbered without a gap.
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape;** every file's em and en dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one,** and leaves room for the whole run (a plain upload of seven tables with the metadata tables took 90 requests in session 2185); a long upload runs as a detached process; the branch is merged with main before the upload.
- **A currency other than USD is a standing question for the owner:** a foreign country's prices are not taken; its quantities are.
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **The live site:** from 24 October 2026 (about 02:00 UTC) every page answered HTTP 402 (the Vercel deployment disabled, a question for the owner); the snapshots are still taken on both sides of a push, and a comparison that cannot run is said so in the report.
- **Session 2280 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2294, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2293 updates it.

Read first: chain 103's note (written by session 2279), sessions 2266 to 2279's reports, chain 102's note, `docs/reviews/siting-gaps.md`.

## Session 2280: Portugal's generation and consumption (REN's Data Hub)

Long end 1:30. Pulls: at most 15 requests. Redes Energeticas Nacionais' Data Hub (datahub.ren.pt; robots and REN's terms first): Portugal's daily or monthly electricity production by source and consumption, from 2015, within the ceiling; a series table in MWh; cross-check: the yearly totals against `eurostat_electricity_monthly`'s Portugal.

## Session 2281: Italy's generation and demand (Terna)

Long end 1:30. Pulls: at most 15 requests. Terna's public data (www.terna.it's statistics and its download centre or Transparency report; robots and Terna's terms first), or Energy-Charts' Italy (api.energy-charts.info, CC BY 4.0, as chain 102 read it) if Terna's host or terms bar the reader: Italy's generation by source and demand, monthly or daily, from 2015; a series table in MWh; cross-check: against Eurostat's Italy.

## Session 2282: Japan's areas' demand (OCCTO or the ten utilities' area data)

Long end 1:30. Pulls: at most 15 requests. The Organization for Cross-regional Coordination of Transmission Operators' public data (www.occto.or.jp), or the general transmission utilities' own area supply-demand files (robots and terms first): each of the ten areas' hourly demand, as far back as published within the ceiling; a series table in MW; cross-check: a year's sum against Ember's Japan.

## Session 2283: Argentina's generation and demand (CAMMESA)

Long end 1:30. Pulls: at most 15 requests. CAMMESA, the wholesale market administrator (cammesaweb.cammesa.com and its published reports or API; robots and terms first): Argentina's monthly generation by type and demand, from 2015, within the ceiling; prices not taken (ARS); a series table in MWh; cross-check: a year's total against Ember's Argentina.

## Session 2284: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach (none named on a note's `Tables:` line or by a note's file name on main or on the running chains' branches), up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2285: the licenses' twenty-eighth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 103 did not reach, those of sessions 2280 to 2283 and 2286 to 2287 first; `license_verdicts.csv` read first; a verdict's read recorded with the outcome exactly `read`; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2286: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2287: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2286.

## Session 2288: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2289: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first and the branch merged with main. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile`; then this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2290: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2291: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2292: a third source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2286.

## Session 2293: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_<the next free date>_data.md`, in session 683's form.
2. The next file (written by session 2280) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
