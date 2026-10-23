# Chain of the night of 23 to 24 October 2026: sessions 2014 to 2027, data machine (lab-desktop), unattended: the wholesale hubs outside the ISOs, rooftop solar, industry's and buildings' energy, the licenses' eleventh round

machine: data

Written by session 2000, the first session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 057. Chain 056 asked for sessions numbered from 2014; 2014 to 2027 were free in every queue file, report and branch when this was written (a search for "session 2014" and the rest found none; the bare numbers 2014 to 2027 in other files are years). Session 2013 of chain 056 updates it at chain 056's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov, and any host chain 056 adds (its note says which).
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it.
- **A new unit or entity type is added to `docs/datastandard.md` and the validator together**, and until the chain lands the main checkout's validator does not know it: a write, a Method-cell run or an upload of that table runs with the branch's validator copied in for the one run, and main's put back.
- **The data lock:** the daily run holds it from about 14:10 to about 16:20 UTC; a write waits for it, and the session does its lock-free steps meanwhile.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one.**
- **Session 2014 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2028, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2027 updates it.

Read first: chain 056's note (`docs/state/note_2026-11-04_data.md`, written by session 2013), sessions 2000 to 2013's reports, `docs/state/note_2026-11-03_data.md`, `docs/reviews/siting-gaps.md`.

## Session 2014: the wholesale hubs outside the ISOs (EIA's wholesale electricity market data)

Long end 1:30. Pulls: at most 15 requests. EIA's wholesale electricity and natural gas market data (www.eia.gov/electricity/wholesale/, the yearly ICE workbooks EIA republishes): each hub's daily day-ahead on-peak price, volume and trade count, the hubs the ISO tables do not hold (Mid-Columbia, Palo Verde, the Southeast and the Rockies) first; a series table of its own; cross-check: the hubs both hold against `iso_dam_hub_prices`' daily on-peak averages.

## Session 2015: rooftop solar (Berkeley Lab's Tracking the Sun)

Long end 1:30. Pulls: at most 15 requests. Tracking the Sun's latest public data (Berkeley Lab; the files on the Open Energy Data Initiative, data.openei.org, robots and terms first; emp.lbl.gov answers 403 to the ERW's reader): installed systems' size, price, state, customer segment and year, summarised by state, segment and year as a series table if the file is too large to hold whole (say so); cross-check: the state totals against `eia861_distributed_generation`'s small-scale solar capacity.

## Session 2016: industry's energy (EIA's Manufacturing Energy Consumption Survey)

Long end 1:30. Pulls: at most 15 requests. The latest MECS tables (www.eia.gov/consumption/manufacturing/): fuel consumption by industry (NAICS) and fuel, and electricity's purchases and onsite generation; a series table; cross-check: the total against `eia_sector_energy_consumption_monthly`'s industrial sector for the survey year.

## Session 2017: buildings' energy (EIA's Commercial and Residential Energy Consumption Surveys)

Long end 1:30. Pulls: at most 15 requests. The latest CBECS and RECS summary tables (www.eia.gov/consumption/): consumption and expenditure by building type or housing type, census region and end use; one series table each, or one with a survey column; cross-check: the totals against `eia_sector_energy_consumption_monthly`'s commercial and residential sectors for each survey year.

## Session 2018: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note that session 2004 did not reach, up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2019: the licenses' eleventh round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 056 did not reach, those of sessions 2014 to 2017 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Sessions 2020 and 2021: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 2022: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can.

## Session 2023: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 960: each note's checks against the code and the table, every contradiction acted on.

## Session 2024: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. A first `--reconcile` for any table of chain 056 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2025: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2026: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2027: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-05_data.md`, in session 683's form.
2. The next file (written by session 2014) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
