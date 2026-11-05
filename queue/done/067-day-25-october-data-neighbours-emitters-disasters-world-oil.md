# Chain of 25 October 2026: sessions 2070 to 2083, data machine (lab-desktop), unattended: Ontario's and Alberta's power markets, every sector's greenhouse gas emitters, the billion-dollar disasters, the world's oil balances, the Statistical Review, the licenses' fifteenth round

machine: data

Written by session 2056, the first session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next`, `queue/todo` and `queue/done`, on this machine and on origin's main, was 067 (066 is chain 066's; 067 to 069 were never used). Chain 066 asked for sessions numbered from 2070; 2070 to 2083 were free in every queue file, report and doc on origin's main and in chains 058 and 059's worktrees when this was written (a search for "session 2070" to "session 2083" and `SESSION_2070` to `SESSION_2083` found none). Session 2069 of chain 066 updates it at chain 066's end. Model: Opus 5.5, high effort.

The sources were chosen by session 2056 among public ones the ERW does not hold and that chains 057 to 066 did not plan: the two Canadian markets beside the U.S. grids, the emitters outside the power sector, the disasters' costs, and the world's oil and energy balances. A source a chain running beside this one takes first is replaced by the session with another public one the ERW does not hold, and the session says why.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- the locked write scripts (`runs/c059/write_table.sh` or a copy that keeps the data lock until main's metadata files are put back and the branch's validator through the coverage step, `runs/c059/method_cells_locked.sh`), `runs/c045/finish_table.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, data.usbr.gov's `/rise/api` and time series queries, www.sec.gov and data.sec.gov, comptroller.texas.gov below its root, and any host chains 058 to 066 add to the list.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in for the one run, and main's put back after the coverage step.
- **The data lock:** GitHub's daily run holds it from about 14:10 to about 16:20 UTC, and this machine's own daily task ("ERW data machine daily") from 17:00 UTC for up to two hours; a write or an upload waits for it, and the session does its lock-free steps meanwhile. Never copy a branch's metadata into the main checkout while this machine's daily task runs there.
- **Two chains on one machine:** each works only in its own worktrees and branches, takes the data lock for every warehouse write and every step that copies a branch's files into the main checkout, waits for it (`scripts/duty.py beat` while it waits) rather than giving up, puts main's files back before releasing it, and never touches the other's branches. Before a Redivis or other upload, the main checkout is pulled to origin's main (session 2024: a validator 33 commits behind refused a table).
- **Two chains' reads:** a chain whose branch is cut from another unlanded chain's numbers its `license_reads.csv` rows after that chain's last; if both add the same number, the later chain's rows are renumbered at the merge and its reports corrected.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one:** a run's cap leaves room for the whole run (a single table with the three metadata tables cost more than 40 requests, session 2024).
- **Session 2070 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2084, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2083 updates it.

Read first: chain 066's note (`docs/state/note_2026-11-08_data.md`, written by session 2069), sessions 2056 to 2069's reports, chain 057's note (`docs/state/note_2026-11-05_data.md`), `docs/reviews/siting-gaps.md`.

## Session 2070: Ontario's market (the IESO's public reports)

Long end 1:30. Pulls: at most 15 requests. The Independent Electricity System Operator's public reports (reports-public.ieso.ca or the host its reports page names, robots and the IESO's terms of use first): the hourly Ontario energy price (HOEP, or its successor under the market renewal of May 2025) and Ontario demand, for the latest full year and this year, in as few files as the reports allow; a series table in the price and demand form of the ISO tables (CAD, a new unit, added to the standard and the validator together, or the session says why not); cross-check: Ontario's demand against EIA-930's interchange with the IESO at the NYISO and MISO borders, where the ERW holds it.

## Session 2071: Alberta's market (the AESO's pool price)

Long end 1:30. Pulls: at most 15 requests. The Alberta Electric System Operator's pool price and Alberta internal load (its public reports or data files, robots and terms first; the AESO's API needs a key and is not asked without one): the hourly pool price and load, for the latest full year and this year; a series table; cross-check: the year's average against the AESO's own annual market statistics where it prints one.

## Session 2072: every sector's emitters (EPA's Greenhouse Gas Reporting Program)

Long end 1:30. Pulls: at most 20 requests. EPA's GHGRP facility-level data for all sectors (the program's published data summary spreadsheets on www.epa.gov, robots and terms first; EPA's bulk file API is not asked without a key): each reporting facility's id, name, state, industry sector and subpart, and its total reported CO2e by year, from 2015; an entities table of the facilities and a series table of their emissions, or one of them (say which); cross-check: the power plants' totals against `epa_ghgrp_power_co2`.

## Session 2073: the billion-dollar disasters (NOAA's archived record)

Long end 1:30. Pulls: at most 10 requests. NOAA NCEI's U.S. Billion-Dollar Weather and Climate Disasters (retired in 2025; its archived data files on www.ncei.noaa.gov, robots and NOAA's terms first): each event's name, type, begin and end dates, CPI-adjusted cost in USD and deaths, and the states affected, from 1980 to the record's last year; an events table; cross-check: the events since 2015 against chain 066's FEMA declarations in the same states and months.

## Session 2074: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that the earlier sessions of this kind did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2075: the licenses' fifteenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 066 did not reach, those of sessions 2070 to 2073 and 2076 to 2077 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Session 2076: the world's oil balances (the JODI Oil World Database)

Long end 1:30. Pulls: at most 20 requests. The Joint Organisations Data Initiative's oil database (www.jodidata.org's downloadable files, robots and its terms of use first): each country's monthly crude oil production, refinery intake, demand and closing stocks, in thousand barrels a day or thousand barrels as JODI gives them, from 2015, for the countries that report; a series table; cross-check: the United States' rows against `eia_petroleum_snd_monthly` or `eia_world_oil_monthly` for the same months.

## Session 2077: the Statistical Review of World Energy (the Energy Institute)

Long end 1:30. Pulls: at most 15 requests. The Energy Institute's Statistical Review of World Energy, its consolidated dataset (www.energyinst.org's Statistical Review downloads, robots and its terms of use first; the download may ask for a form, in which case the session stops and says so): each country's yearly primary energy consumption by fuel and its electricity generation by source; a series table, if its terms allow it to be held (else held internal and said so); cross-check: the United States' rows against `eia_primary_energy_monthly` summed by year.

## Session 2078: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2079: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 960: each note's checks against the code and the table, every contradiction acted on.

## Session 2080: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap, the main checkout pulled first. A first `--reconcile` for any table of chain 066 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables (`erw_coverage` with them); `--reconcile`; the release note extended. Nothing released.

## Session 2081: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2082: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2083: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-09_data.md`, in session 683's form.
2. The next file (written by session 2070) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
