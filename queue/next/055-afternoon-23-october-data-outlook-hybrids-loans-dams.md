# Chain of the afternoon of 23 October 2026: sessions 978 to 991, data machine (lab-desktop), unattended: the world's energy outlook, hybrid power plants, the federal energy loans, utilities' industrial output, the nation's dams, the licenses' ninth round

machine: data

Written by session 951, the first session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 055. Chain 054 asked for sessions numbered from 965; 970 to 977 are chain 065's (the old laptop's, `queue/done/065-late-22-october-code-allgrids-5.md`), so this chain takes the first free block of fourteen, 978 to 991, free in every queue file, report and branch when this was written (the code machine holds 700 to 749, the laptop 800 to 849, the old laptop 1000 on). Session 964 of chain 054 updates it at chain 054's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` (a table written again: the new run's metadata rows) on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **HydroSource's download form is not filled**; ORNL's files are taken by their public links, pending the owner's word.
- **Every session runs `scripts/precheck.py` first** (session 945 did not, and said so).
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one**, budgeted by session 892's measure (session 947: 90 Redivis requests for nine tables and the metadata in a plain upload).
- **Session 978 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 992, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 991 updates it.

Read first: chain 054's note (`docs/state/note_2026-11-02_data.md`, written by session 964), sessions 951 to 964's reports, `docs/state/note_2026-11-01_data.md`, `docs/reviews/siting-gaps.md`.

## Session 978: the world's energy outlook (EIA's International Energy Outlook)

Long end 1:30. Pulls: EIA's API v2, at most 15 requests. The route `ieo` (the International Energy Outlook's latest release): energy consumption, production, electricity capacity and generation and CO2 by region and fuel to 2050, the reference case first; a series table of its own; cross-check: its base year against `eia_world_energy_co2_annual` and `eia_world_electricity_annual` for the regions both hold.

## Session 979: hybrid power plants (Berkeley Lab)

Long end 1:30. Pulls: at most 10 requests. Berkeley Lab's "Hybrid Power Plants: Status of Operating and Proposed Plants" data file, the latest edition, from eta-publications.lbl.gov (emp.lbl.gov answers 403 to the ERW's reader): operating hybrid plants by type and size, and the hybrids in the interconnection queues; an entities or series table as the sheets allow; cross-check: the operating PV+storage plants against `lbnl_solar_projects`' hybrid configurations.

## Session 980: the federal energy loans (the Department of Energy's Loan Programs Office)

Long end 1:30. Pulls: at most 15 requests. The Loan Programs Office's public portfolio (energy.gov, robots and terms first): each loan or guarantee's project, borrower, technology, place, amount and date, as an events table; cross-check: the projects' places and capacities against `eia860m_operating_generators` and `eia860m_planned_generators` where an EIA plant can be named.

## Session 981: the utilities' industrial output (the Federal Reserve's G.17)

Long end 1:30. Pulls: at most 10 requests. The Federal Reserve Board's Industrial Production and Capacity Utilization (G.17) through its Data Download Program (federalreserve.gov, robots and terms first): the electric and gas utilities' output index and capacity utilization, monthly, with the total index beside them; a series table; cross-check: the electric utilities' index against `eia_retail_sales_monthly`'s U.S. sales, year on year.

## Session 982: the nation's dams (the U.S. Army Corps of Engineers' National Inventory of Dams)

Long end 1:30. Pulls: at most 15 requests. The National Inventory of Dams' public download or service (nid.sec.usace.army.mil, robots and terms first): each dam's NID id, name, place, owner type, purpose, height, storage and hydropower flag, as an entities table, the fields the public release gives; cross-check: `ornl_npd_potential`'s 597 NID ids and `ornl_eha_hydropower_plants`' dams.

## Session 983: the licenses' ninth round

Long end 1:30. Pulls: at most 20 requests, two a host. The publishers chains 046 to 054 did not reach, those of sessions 978 to 982 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Sessions 984 and 985: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 986: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can. After chain 053 the open rows were substations and lines, large-load tariffs, a 2026 sub-region table and a node's bus (chain 054's session 959 may have moved one).

## Session 987: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 946: each note's checks against the code and the table, every contradiction acted on.

## Session 988: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. A first `--reconcile` for any table of chain 054 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 989: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 948: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 990: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 991: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-03_data.md`, in session 683's form.
2. The next file (written by session 978) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
