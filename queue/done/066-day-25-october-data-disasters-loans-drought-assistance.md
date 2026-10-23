# Chain of 25 October 2026: sessions 2056 to 2069, data machine (lab-desktop), unattended: the disasters declared, the federal energy loans, drought, the hurricanes' tracks, energy assistance, the vehicles' efficiency, the reactors' licenses and uprates, the licenses' fourteenth round

machine: data

Written by session 2042, the first session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 066 (060 to 065 and 070 to 078 are the code machine's, 080 to 084 the portable laptop's; 066 to 069 were never used). Chain 059 asked for sessions numbered from 2056; 2056 to 2069 were free in every queue file, report, doc and branch when this was written (a search of origin's main, chains 056 and 057's branches and chains 057 and 058's worktrees for "session 2056" to "session 2069" and `SESSION_2056_` to `SESSION_2069_` found none). Session 2055 of chain 059 updates it at chain 059's end. Model: Opus 5.5, high effort.

(Updated by session 2055 at chain 059's end: the hosts the SEC and the Texas Comptroller refused, LPO's map, and the order of the validator in the write script.) Chain 059 was taken at 18:19 UTC on 23 October while chains 057 and 058 ran beside it on the same machine (the owner's instruction: each chain in its own worktrees and `wip/` branches, the data lock taken for every warehouse write and waited for with `scripts/duty.py beat`, the build lock before every build). The sources below were chosen by session 2042 among public ones the ERW does not hold (none is in `warehouse/metadata/coverage.csv`, `sources.csv` or a connector on main or on chains 056 and 057's branches, nor among chains 057 to 059's planned sources): the disasters that follow the storms, the federal loans that finance new plants, the drought that takes hydropower and cooling water, the hurricanes that cross the Gulf's refineries and terminals, the money that helps households pay for energy, the efficiency of the vehicles that will draw on the grid, and the licenses that keep the reactors running. A source that chains 057 to 059 took first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, and data.usbr.gov's `/rise/api` and time series queries, with www.sec.gov and data.sec.gov (session 2049: HTTP 403 to a reader that declares no contact email, the SEC's fair access rule), comptroller.texas.gov below its root (session 2047: its robots file disallows `/*/`) and any host chains 057 and 058 add to the list.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in for the one run, and main's put back.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task ("ERW data machine daily") from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile. Never copy a branch's metadata into the main checkout while this machine's daily task runs there.
- **Two chains on one machine:** while another chain runs on this machine, each works only in its own worktrees and branches, takes the data lock for every warehouse write and waits for it (`scripts/duty.py beat` while it waits) rather than giving up, takes the build lock before every build, and never touches the other's branches. Every step that copies a branch's files into the main checkout runs under the data lock and puts main's files back before releasing it (`runs/c059/write_table.sh`, `runs/c059/method_cells_locked.sh`, `runs/c059/coverage_row.sh`); with `VALIDATOR=branch` the branch's validator stays in through the coverage step, or a table with a new unit gets a "blocked" coverage row (session 2053).
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one.**
- **Session 2056 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2070, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2069 updates it.

Read first: chain 059's note (`docs/state/note_2026-11-07_data.md`, written by session 2055), sessions 2042 to 2055's reports, chain 058's note (`docs/state/note_2026-11-06_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2056: the disasters declared (FEMA's OpenFEMA disaster declarations)

Long end 1:30. Pulls: at most 15 requests. The Federal Emergency Management Agency's Disaster Declarations Summaries (OpenFEMA, www.fema.gov's `/api/open/` data sets, no key; robots and OpenFEMA's terms first): each declaration's number, type (major disaster, emergency, fire management), incident type, state, county or tribal area, incident begin and end, and declaration date, from 2015; an events table, one row a declaration and area; cross-check: each year's hurricane and severe storm declarations against session 2042's storm events and chain 058's OE-417 weather events in the same states and months.

## Session 2057: the federal energy loans (DOE's Loan Programs Office)

Long end 1:30. Pulls: at most 15 requests. Sessions 512 and 513 found LPO's portfolio (the office is now the Office of Energy Dominance Financing) published only as a map application; if it still is, this session takes another public source the ERW does not hold and says why. The Loan Programs Office's portfolio of closed loans and loan guarantees and its conditional commitments (www.energy.gov's LPO portfolio pages, robots and terms first): each project's borrower, program (Title 17, ATVM, Tribal Energy, Energy Infrastructure Reinvestment), technology, state, amount, status and date of close or commitment, as LPO publishes them; an events table, one row a loan or commitment; cross-check: the portfolio's total against the figure LPO's portfolio page prints, and each generating project against `eia860` by plant name and state.

## Session 2058: drought (the U.S. Drought Monitor)

Long end 1:30. Pulls: at most 15 requests. The U.S. Drought Monitor's comprehensive statistics by state (droughtmonitor.unl.edu's data services, the weekly percent of area in each category D0 to D4; robots and its terms of use first, the Monitor asks for credit to the National Drought Mitigation Center, USDA and NOAA): each of the 48 states' weekly percent of area by category, from 2015, in as few requests as its services allow; a series table; cross-check: the West's worst weeks against `eia923`'s or EIA's monthly hydroelectric generation in Washington, Oregon and California for the same months (more drought, less hydro).

## Session 2059: the hurricanes' tracks (the National Hurricane Center's HURDAT2)

Long end 1:30. Pulls: at most 10 requests. The National Hurricane Center's best track data for the Atlantic and the Northeast and North Central Pacific (www.nhc.noaa.gov's `/data/hurdat/`, the text files; robots and NOAA's terms first): each storm's identifier and name, and each six-hourly fix's time, latitude, longitude, maximum wind in knots, minimum pressure in millibars and status, from 2000, with the landfall records the files mark; a series table, or an events table of the landfalls with the fixes in a series table (say which); cross-check: each U.S. landfall since 2015 against session 2042's hurricane events and session 2056's declarations in the same states.

## Session 2060: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that sessions 2004, 2018, 2032 and 2046 did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2061: the licenses' fourteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 059 did not reach, those of sessions 2056 to 2059 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2062: energy assistance (HHS's LIHEAP)

Long end 1:30. Pulls: at most 20 requests. The Department of Health and Human Services' Low Income Home Energy Assistance Program data (the Administration for Children and Families' LIHEAP pages and the LIHEAP Performance Management and Data Warehouse's published state tables; robots and terms first): each state's yearly allocation in dollars and, where published, households served for heating, cooling and crisis assistance, from 2015; a series table; cross-check: each year's national total against the appropriation ACF's own funding release prints.

## Session 2063: the vehicles' efficiency (EPA and DOE's fueleconomy.gov)

Long end 1:30. Pulls: at most 10 requests. The fuel economy data file of www.fueleconomy.gov (the vehicles file of its downloads page, robots and terms first): each model year, make, model, powertrain (gasoline, hybrid, plug-in hybrid, battery electric, fuel cell), combined miles per gallon or its equivalent, and electricity use in kWh per 100 miles for the electric ones, from model year 2015; an entities table, one row a vehicle configuration; cross-check: the battery electric models' median kWh per 100 miles by model year, and the count of electric models a year against chain 058's registrations.

## Session 2064: the reactors' licenses and uprates (the NRC's lists)

Long end 1:30. Pulls: at most 15 requests. The Nuclear Regulatory Commission's status of license renewal applications and its lists of approved and expected power uprates (www.nrc.gov's `/reactors/operating/licensing/` pages, robots and terms first, read after session 2043's verdict): each unit's application date, the renewed license's expiry, and each uprate's type (measurement uncertainty recapture, stretch, extended), megawatts thermal and approval date; an events table; cross-check: each unit against `nrc_power_reactors`' units by docket number, and the uprates' total against the figure the NRC's page prints.

## Session 2065: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2066: method notes for this chain's tables, and the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. First as session 960: each note's checks against the code and the table, every contradiction acted on. Then a first `--reconcile` for any table of chain 059 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2067: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2068: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2069: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-08_data.md`, in session 683's form.
2. The next file (written by session 2056) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
