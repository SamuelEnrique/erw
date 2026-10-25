# Chain of 30 October 2026: sessions 2148 to 2161, data machine (lab-desktop), unattended: the Northwest's federal grid, the snow behind the West's dams, the world's electricity access, the next season's outlook, the new homes that add load, the licenses' twentieth round

machine: data

Written by session 2134, the first session of `queue/done/090-day-29-october-data-wildfires-geomagnetic-inventory-carbon.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 092 (090 and 091 taken). Chain 090 asked for sessions numbered from 2148; 2148 to 2161 were free on origin's main and in chains 069 and 079's branches when this was written. Session 2147 of chain 090 updates it at chain 090's end. Model: Opus 5.5, high effort.

Chain 090 was taken at 23:01 UTC on 23 October by chain 058's agent (the owner's instruction: run the file the queue step prints), beside chains 069 and 079 under other agents. The three agreed their numbers that hour: data standard decisions 63 to 65 are chain 069's (acre, MJ/m2-day, ft3/s), 66 chain 079's (g), 67 on chain 090's; each chain numbers its reads after main's last and renumbers after whatever has landed when it merges. The sources below were chosen by session 2134 among public ones the ERW does not hold and that chains 057 to 090 did not plan or take (not EPA's TRI, USGS's ComCat, Eurostat's renewable capacity, Our World in Data, USGS's thermoelectric water use or FEMA's National Risk Index): the federal power marketing grid of the Northwest, the snowpack that fills the West's reservoirs, the world's electricity access, the season's temperature outlook that drives demand, and the building permits that add homes to the grid. A source a chain running beside this one takes first is replaced by the session with another public one, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c057/write_table.sh`, which keep the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/090-day-29-october-data-wildfires-geomagnetic-inventory-carbon.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, www.energyinst.org, www.fueleconomy.gov, figshare.com, www.rd.usda.gov, www.irena.org (HTTP 403, chain 068), power.larc.nasa.gov below `/api/` and apps.bea.gov's `/regional/zip/` (chain 069), www.iaea.org (HTTP 403, chain 068), www.sciencebase.gov (its robots file disallows / for every reader), hazards.fema.gov (the connection reset), data.ny.gov (its terms forbid automated access, chain 069), and any host chains 079 and 090 add to the list. JODI (jodidata.org) is not pulled.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`, BEA's UserID; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first, from the main checkout.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A robots file's crawl delay is kept** between requests to its host.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, numbered after the last decision on main and on the running chains' branches.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task from 17:00 UTC for up to two hours; a write or an upload waits for it.
- **Several chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits), puts main's files back before releasing it, and never touches the others' branches; no commit and no pull in the main checkout while another chain holds the lock; queue commits are made in a detached worktree of their own and pushed with `HEAD:main`.
- **Two chains' reads and decisions:** chains running beside each other agree their `license_reads.csv` numbers and their data standard decisions before writing them; the one that lands second renumbers at its merge and corrects its reports (only a number named as a read is shifted).
- **Every connector asks `iso_prices.paused()` and `paused_host()` before its first request.**
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A request cap on the Redivis uploader stops between tables, never inside one**, and leaves room for the whole run; a reconcile needs 7 requests or more, so its cap is 10.
- **A currency other than USD is a standing question for the owner.**
- **Merging main into a chain's branch:** a generated line is merged as the union of both sides with its true count, never by taking one side.
- **Session 2148 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2162, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2161 updates it.

Read first: chain 090's note (`docs/state/note_2026-11-13_data.md`, written by session 2147), sessions 2134 to 2147's reports, chain 079's note (`docs/state/note_2026-11-12_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2148: the Northwest's federal grid (BPA's balancing authority data)

Long end 1:30. Pulls: at most 15 requests. The Bonneville Power Administration's balancing authority load, wind, hydro, thermal and net interchange at five-minute intervals, as its transmission site publishes them (transmission.bpa.gov's yearly or monthly workbooks, robots and BPA's terms first; BPA has read 48 and no verdict): a series table, the five-minute values summed to the hour if the files are too large to hold whole (say so), from 2020; cross-check: the hourly load against `eia930_all_demand`'s BPAT in the same hours.

## Session 2149: the snow behind the West's dams (NRCS SNOTEL)

Long end 1:30. Pulls: at most 15 requests. The Natural Resources Conservation Service's SNOTEL snow water equivalent, a day, at the stations above the Columbia, the Colorado and California's reservoirs (wcc.sc.egov.usda.gov's report generator, robots and USDA's terms first; www.rd.usda.gov refused the reader, a different host), at most twenty stations, from 2015; a series table in inches (`in`, Decision 60); cross-check: each spring's peak against the following summer's generation of the hydro plants downstream (`usbr_hydropower_monthly` or `eia923_plant_fuel_monthly`).

## Session 2150: the world's electricity access (the World Bank's indicators)

Long end 1:30. Pulls: at most 15 requests. The World Bank's World Development Indicators for electricity (api.worldbank.org's v2 API, which needs no key: access to electricity, percent of population; electric power consumption per capita; renewable electricity output, percent; robots and the World Bank's terms first, `wb_commodity_prices_monthly` has its verdict): each country's yearly value from 2000; a series table; cross-check: the United States' consumption per capita against `eia_retail_sales_monthly` summed to the year over the population the World Bank gives.

## Session 2151: the next season's outlook (NOAA CPC's three-month temperature outlook)

Long end 1:30. Pulls: at most 10 requests. The Climate Prediction Center's official 90-day temperature outlook by climate division (www.cpc.ncep.noaa.gov, which has no robots file, its outlook data files; NWS's verdict, read 8): each issue's probabilities of above, near and below normal for the next thirteen leads, as many issues as the archive serves within the ceiling; a series table (percent, `pct`); cross-check: the winter outlooks issued in strong El Nino and La Nina seasons against `noaa_cpc_oni_monthly` (chain 068).

## Session 2152: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind (2004, 2018, 2032, 2046, 2060, 2074, 2088, 2110, 2124, 2138) did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2153: the licenses' twentieth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 090 did not reach, those of sessions 2148 to 2151 and 2154 first (BPA, which has a read and no verdict, among them); `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2154: the new homes that add load (the Census Bureau's building permits)

Long end 1:30. Pulls: at most 15 requests. The Census Bureau's Building Permits Survey by state, a month, as its files are published (www2.census.gov's `/econ/bps/` text files; api.census.gov refused the reader and is not asked; robots and the Census Bureau's terms first): units authorized by structure type, each state and month from 2015; a series table (count); cross-check: each state's yearly units against the growth of `eia861_utility_sales`'s residential customers in the same state the following year.

## Session 2155: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold and no chain has taken, chosen by the session; say why.

## Session 2156: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2157: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 090 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2158: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2159: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2160: a second source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. As session 2155.

## Session 2161: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-14_data.md`, in session 683's form.
2. The next file (written by session 2148) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
