# Chain of 29 October 2026: sessions 2134 to 2147, data machine (lab-desktop), unattended: the wildfires near the grid, the geomagnetic storms, the national greenhouse gas inventory, the atmosphere's carbon dioxide, households' energy burden, the licenses' nineteenth round

machine: data

Written by session 2120, the first session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on origin's main and on chains 068 and 069's branches, was 090 (078 to 089 are taken). Chain 079 asked for sessions numbered from 2134; 2134 to 2147 were free in every queue file, report and branch on origin's main and in chains 068 and 069's worktrees when this was written (a search for `SESSION_2134` to `SESSION_2147` and "session 2134" to "session 2147" found none; 2134 appears only as the number chain 079's file asks for). Session 2133 of chain 079 updates it at chain 079's end. Model: Opus 5.5, high effort.

Chain 079 was taken at 22:22 UTC on 23 October by chain 059's agent (the owner's instruction for that run: run the file the queue step prints), while chains 068 and 069 ran beside it on the same machine. The sources below were chosen by session 2120 among public ones the ERW does not hold and that chains 057 to 079 did not plan (a search of `sources.csv` on main and on chains 068 and 069's branches, and of their queue files, found none of them): the wildfires that burn near lines and plants, the geomagnetic storms that load transformers, the national inventory the power sector's emissions sit in, the atmosphere's carbon dioxide, and the energy burden of households, the gap chain 069 found too large for one session. A source a chain running beside this one takes first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms;
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or `runs/c057/write_table.sh`, which keep the data lock until main's metadata files are put back and the branch's validator through the coverage step; `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers (then a look for a row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, www.energyinst.org, www.fueleconomy.gov, figshare.com, www.rd.usda.gov, www.irena.org (HTTP 403, chain 068), power.larc.nasa.gov below `/api/` and apps.bea.gov's `/regional/zip/` (chain 069), and any host chain 079 adds to the list. JODI (jodidata.org) is not pulled.
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
- **Session 2134 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2148, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2147 updates it.

Read first: chain 079's note (`docs/state/note_2026-11-12_data.md`, written by session 2133), sessions 2120 to 2133's reports, chain 069's note (`docs/state/note_2026-11-11_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2134: the wildfires near the grid (the wildland fire perimeters)

Long end 1:30. Pulls: at most 15 requests. The National Interagency Fire Center's Wildland Fire Interagency Geospatial Services (WFIGS) incident locations or perimeters, as its open data host publishes them (robots and the terms first): every fire of 2015 on, with its discovery date, its location, its final size and its cause where given; an events table; if the size needs a unit the data standard lacks, it is added under the decision chain 069 numbered for `acre`, never a second one. Cross-check: the yearly acres burned against NIFC's own national statistics page, and the large fires near `uswtdb_wind_turbines` or `eia860_plants_annual` locations counted.

## Session 2135: the geomagnetic storms (NOAA's Space Weather Prediction Center)

Long end 1:30. Pulls: at most 15 requests. The planetary K index and its storm levels (NOAA SWPC's products, or the GFZ Potsdam Kp record if SWPC holds only recent days; robots and terms first): every three-hour value from as far back as the public file goes; a series table; cross-check: the storms of G4 and above against the dates NOAA's own alerts or the May 2024 storm name, and any `nrc_event_notifications` or OE-417 row on those days counted.

## Session 2136: the national greenhouse gas inventory (EPA)

Long end 1:30. Pulls: at most 15 requests. EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks by economic sector and gas, by year from 1990, as EPA's data explorer or its published tables give it (robots and terms first): a series table in the units of `epa_ghgrp_facility_emissions` (tCO2e, Decision 61, scaled from the inventory's MMT); cross-check: the electric power sector's CO2 against `eia_power_co2_state_annual` summed to the nation, and against `epa_ghgrp_facility_emissions`' power plants summed.

## Session 2137: the atmosphere's carbon dioxide (NOAA's Global Monitoring Laboratory)

Long end 1:00. Pulls: at most 10 requests. Mauna Loa's monthly mean carbon dioxide and the global marine surface mean (gml.noaa.gov's text files, robots and its use policy first): a series table; a unit in ppm if the data standard lacks it (numbered after the last decision); cross-check: the yearly growth against the yearly growth GML's own annual file prints.

## Session 2138: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2139: the licenses' nineteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 079 did not reach, those of sessions 2134 to 2137 and 2140 first; IRENA's terms from an address other than www.irena.org if one serves them (chain 068 could not read them); `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2140: households' energy burden (DOE's LEAD Tool)

Long end 2:00. Pulls: at most 70 requests. DOE's Low-Income Energy Affordability Data (data.openei.org submission 6219, CC BY 4.0; chain 069 found it 52 state archives, California's alone 913 MB): each state's archive read from disk in chunks, never whole, and reduced to the tract or county by income bracket rows the session chooses (energy burden, the average energy cost and income, the households); a series table; cross-check: the state averages against `eia_seds_residential_annual` (chain 069) where both hold the year. If the archives cannot be taken within the ceiling, the states done are written and the rest said so.

## Session 2141: a source of the session's own choosing

Long end 1:30. Pulls: at most 20 requests. A public source the ERW does not hold, chosen by the session; say why.

## Session 2142: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2143: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 960: each note's checks against the code and the table, every contradiction acted on.

## Session 2144: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. A first `--reconcile` for any table of chain 079 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2145: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2146: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2147: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-13_data.md`, in session 683's form.
2. The next file (written by session 2134) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
