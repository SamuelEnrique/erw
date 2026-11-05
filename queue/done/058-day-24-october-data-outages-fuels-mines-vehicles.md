# Chain of 24 October 2026: sessions 2028 to 2041, data machine (lab-desktop), unattended: the grid's disturbances and outages, the renewable fuels' credits, ethanol's plants, the mines, motor fuel, electric vehicles, the licenses' twelfth round

machine: data

Written by session 2014, the first session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 058. Chain 057 asked for sessions numbered from 2028; 2028 to 2041 were free in every queue file, report, doc and branch when this was written (a search for "session 2028" to "session 2041" and `SESSION_2028` to `SESSION_2041` found none). Session 2027 of chain 057 updates it at chain 057's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, and data.usbr.gov's `/rise/api` and time series queries, with any host chain 057 adds to the list.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in for the one run, and main's put back.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task ("ERW data machine daily") from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile. Never copy a branch's metadata into the main checkout while this machine's daily task runs there.
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one.**
- **Session 2028 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2042, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2041 updates it.

Read first: chain 057's note (`docs/state/note_2026-11-05_data.md`, written by session 2027), sessions 2014 to 2027's reports, `docs/state/note_2026-11-04_data.md`, `docs/reviews/siting-gaps.md`.

## Session 2028: the grid's disturbances (DOE's OE-417 electric emergency incident reports)

Long end 1:30. Pulls: at most 15 requests. The Department of Energy's Electric Disturbance Events (Form OE-417) yearly summaries (the Office of Cybersecurity, Energy Security, and Emergency Response's annual files, robots and terms first): each event's start and restoration time, area, NERC region, event type, demand lost in MW and customers affected; an events table of its own; cross-check: each year's count and largest events against the summary the publisher prints beside the files.

## Session 2029: outages by county (Oak Ridge's EAGLE-I)

Long end 1:30. Pulls: at most 15 requests. Oak Ridge National Laboratory's EAGLE-I customer outage records as published for reuse (the dataset's public release and its license, robots and terms first): customers out by county, summarised to a day (the county's peak) as a series table if the 15-minute file is too large to hold whole (say so); cross-check: the largest days against session 2028's OE-417 events in the same states.

## Session 2030: the renewable fuels' credits (EPA's RIN generation)

Long end 1:30. Pulls: at most 15 requests. EPA's Renewable Fuel Standard data (the EPA Moderated Transaction System's public tables on www.epa.gov, robots and terms first; EPA's bulk file API is not asked without a key): RINs generated a month by D code and fuel, and the volumes; a series table; cross-check: the yearly D6 total against `eia_oxygenate_production_monthly`'s or EIA's fuel ethanol production for the same years, in gallons.

## Session 2031: ethanol's and biodiesel's plants (EIA's biofuels capacity reports)

Long end 1:30. Pulls: at most 15 requests. EIA's U.S. Fuel Ethanol Plant Production Capacity and Biodiesel and Renewable Diesel capacity files (www.eia.gov/petroleum/): each plant's nameplate and operating capacity by state and PADD, a year a row; an entities table, or a series table by state if the plant list is not published (say so); cross-check: the state totals against the publisher's own summary table.

## Session 2032: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that sessions 2004 and 2018 did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2033: the licenses' twelfth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 057 did not reach, those of sessions 2028 to 2031 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2034: the mines (MSHA's open government data)

Long end 1:30. Pulls: at most 20 requests. The Mine Safety and Health Administration's mines and quarterly employment and production files (arlweb.msha.gov or www.msha.gov's open data page, robots and terms first): coal mines' status, state, operator and quarterly coal production and hours; a series table, and the mines as entities if their identifiers are published; cross-check: each year's coal production against `eia_coal_mine_production_annual`.

## Session 2035: motor fuel (FHWA's monthly motor fuel reported by the states)

Long end 1:30. Pulls: at most 20 requests. The Federal Highway Administration's Monthly Motor Fuel Reported by States (www.fhwa.dot.gov/policyinformation/, robots and terms first): gasoline and special fuels gallons a month by state; a series table; cross-check: the national gasoline total against `eia_product_supplied_monthly`'s motor gasoline for the same months.

## Session 2036: electric vehicles by state (the Alternative Fuels Data Center's registration counts)

Long end 1:30. Pulls: at most 20 requests. The Department of Energy's vehicle registration counts by state (afdc.energy.gov's published data file, not its key-gated API; robots and terms first): electric, plug-in hybrid and hybrid vehicles registered by state and year; a series table; if the file is reached only through the API, stop and say so (the key is not held).

## Session 2037: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2038: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 057 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2039: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2040: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2041: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-06_data.md`, in session 683's form.
2. The next file (written by session 2028) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
