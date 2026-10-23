# Chain of the evening of 23 October 2026: sessions 2000 to 2013, data machine (lab-desktop), unattended: energy jobs by state, new reactor applications, ERCOT's large loads, Reclamation's hydropower, the licenses' tenth round

machine: data

Written by session 978, the first session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, under chain 045's rule ("the next file is written and pushed to `queue/next` at the START of the chain"), at the owner's instruction for chain 045 ("at least twelve sessions, machine: data, ... the sources and gaps ... in chain 040's form"). The next free number in `queue/next` and `queue/done` was 056. Chain 055 asked for sessions numbered from 992; only 992 to 999 are free below 1000 (the old laptop holds 1000 on, and its files claim 1108 upward for its next), and 965 to 969 are a block of five, so this chain takes 2000 to 2013, free in every queue file, report and branch when this was written and claimed by no machine. Session 991 of chain 055 updates it at chain 055's end. Model: Opus 5.5, high effort.

Each source session follows chain 040's form:

- the publisher's robots file asked in a call of its own and read before any other path of its host, and its terms (EIA's are record 1, public);
- a probe, and a trial with `--out-dir` from the main checkout, whose saved pages the write reuses (`--offline`);
- a cross-check, reading every ERW table past its header lines, never with pandas' `comment="#"`;
- `runs/c045/write_table.sh` (connectors), `runs/c051/write_derived.sh` (derived builders), `runs/c045/finish_table.sh`, `runs/c045/method_cells.sh`, and the resolvers `runs/union_resolve.py` (then a look for a source row twice in `sources.csv`, merged by hand), `runs/c046/take_theirs.py`, `runs/c048/ours_with_theirs_table.py` and `runs/c053/s946/theirs.py` on the data machine, each given the chain's worktree (`WT=`, `WTN=`); stage the branch (`git add`) before a write, so its metadata patch applies;
- a sector rule, both holds, tests and a report.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md` hold, word for word, among them:

- **ERCOT's robots file disallows `/misapp` and `/misdownload`**, and **EIA's disallows `/archive/`**: neither is asked.
- **Hosts that refused the ERW's reader, or whose robots file disallows its paths, are not asked again without a ruling:** api.census.gov, www.phmsa.dot.gov, FERC's policy page, EPA's bulk file API without a key, apps.cer-rec.gc.ca, files.ember-energy.org, www.bls.gov.
- **Keys not held:** `EPA_CAMD_API_KEY`, `NREL_API_KEY` or `DATA_GOV_API_KEY`, `OPENEI_API_KEY`; a session that needs one stops and says so, without signing up.
- **Every session runs `scripts/precheck.py` first.**
- **A redirect to a new host is a new host:** its robots file is asked before the next request to it (session 951's error).
- **A new unit is added to `docs/datastandard.md` and the validator together** (session 954's Decision 56), and until the chain lands the main checkout's validator does not know it: a write or an upload of that table runs with the branch's validator copied in for the one run, and main's put back.
- **No character typed as an escape:** a dash or quote the code must match is written by code point (`chr(0x2014)`), and every file's em dashes are counted before a commit.
- **A push to main is never piped, and is followed by `git status -sb`** showing nothing ahead.
- **A new read of a publisher already in `license_reads.csv` gets a label of its own**; a session checks `license_verdicts.csv` before reading a publisher's terms.
- **A table that a page reads is never rewritten to add rows from another file.**
- **A request cap on the Redivis uploader stops between tables, never inside one** (session 961: 93 Redivis requests for ten tables and the metadata in a plain upload, 37 for one table by `--tables`).
- **Session 2000 begins by writing `queue/next/<next free number>-<slug>.md`** for this machine (at least twelve sessions, machine: data, numbered from 2014, a number found taken skipped upward and said so), commits it alone and pushes it to main before any other work; session 2013 updates it.

Read first: chain 055's note (`docs/state/note_2026-11-03_data.md`, written by session 991), sessions 978 to 991's reports, `docs/state/note_2026-11-02_data.md`, `docs/reviews/siting-gaps.md`.

## Session 2000: energy jobs by state and technology (the Department of Energy's U.S. Energy and Employment Report)

Long end 1:30. Pulls: at most 15 requests. The latest USEER's public data (energy.gov, robots and terms first): employment by technology (generation by fuel, transmission and storage, fuels, energy efficiency, motor vehicles) nationally and by state; a series table of its own; cross-check: the national totals against the report's own summary figures.

## Session 2001: new reactor applications (the Nuclear Regulatory Commission)

Long end 1:30. Pulls: at most 15 requests. The NRC's public lists of new reactor licensing (combined licenses, early site permits, construction permits, design certifications) and advanced reactor pre-application activities (nrc.gov, robots first; the NRC's terms as session 925 read them): an events or entities table, each application with its applicant, site, design, docket and dates; cross-check: the sites against `nrc_power_reactors` (an operating site with a new application).

## Session 2002: ERCOT's large loads (the interconnection status ERCOT publishes)

Long end 1:30. Pulls: at most 15 requests, none to `/misapp` or `/misdownload`. ERCOT's public large load interconnection status (the monthly update ERCOT posts under its files, not its MIS): the megawatts requested and approved by status and by month, as a series table; if ERCOT serves it only under the robots-held paths, the session says so and takes nothing. Cross-check: the totals against ERCOT's own slides of the same month, and `ercot_cdr_reserve_margins`' large load figures where they meet.

## Session 2003: Reclamation's hydropower (the Bureau of Reclamation's RISE)

Long end 1:30. Pulls: at most 15 requests. The Bureau of Reclamation's Reclamation Information Sharing Environment (data.usbr.gov, robots and terms first): its hydropower plants' monthly generation where RISE gives it as a catalogued item; a series table; cross-check: the plants against `ornl_eha_hydropower_plants` and their generation against `eia923_plant_fuel_monthly` by EIA plant id.

## Session 2004: a gap of the platform's held-but-undescribed tables

Long end 1:30. Pulls: none. The tables in `warehouse/metadata/coverage.csv` with no method note (`eia_sector_energy_consumption_monthly` among them, session 960), up to six, each a note written from its connector and table, checked as session 960 checked its notes.

## Session 2005: the licenses' tenth round

Long end 1:30. Pulls: at most 20 requests, two pages a host beside its robots file. The publishers chains 046 to 055 did not reach, those of sessions 2000 to 2003 first; `license_verdicts.csv` read first; `tests/test_session205.py`'s bound raised if the round needs it.

## Sessions 2006 and 2007: two more sources

Long end 1:30 each. Pulls: at most 20 requests each. A public source the ERW does not hold, chosen by each session; say why.

## Session 2008: a gap of the siting review

Long end 1:30. Pulls: at most 10 requests. One open row of `docs/reviews/siting-gaps.md` that a public table can close without a ruling, read after the code machine's latest state section; else the session says why none can. After chain 054 none could without a ruling or a key (session 959).

## Session 2009: method notes for this chain's tables

Long end 1:00. Pulls: none. As session 960: each note's checks against the code and the table, every contradiction acted on.

## Session 2010: the Stanford draft

Long end 1:30. Pulls: Redivis's API only, at most 150 requests, in whole runs under the cap. A first `--reconcile` for any table of chain 055 not yet in the draft or stale there; then those and this chain's public tables, in a plain upload that refreshes the metadata tables; `--reconcile`; the release note extended. Nothing released.

## Session 2011: seven days of the data jobs

Long end 1:00. Pulls: GitHub's API, at most 30 requests (with this machine's token for reads). As session 962: each data job's last seven days, each failure with its step and first error line; a fault of this repository's code fixed with its test.

## Session 2012: the package's and the site's records

Long end 1:00. Pulls: none. `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables and verdicts; rebuilt if stale.

## Session 2013: the note, the next file updated, the landing and the queue

Long end 1:00.

1. `docs/state/note_2026-11-04_data.md`, in session 683's form.
2. The next file (written by session 2000) updated if this chain's results change what it should hold, pushed to main on its own with snapshots.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC. If the check run's merge step fails because main moved, merge origin/main again and push the branch again.
4. Then `python scripts/chain_queue.py next`.
