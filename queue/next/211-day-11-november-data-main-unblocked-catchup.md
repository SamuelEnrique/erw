# Chain of 11 November 2026: sessions 3750 to 3773, data machine (lab-desktop), unattended, about 24 hours: main unblocked, five days caught up, the landings, the backfill, the large-load dataset resumed

machine: data

Written by the owner with Claude in chat on 11 November 2026 (Wednesday, about 01:00 Pacific) and uploaded to `queue/next` by the owner. It takes sessions 3750 to 3773; session 3750 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Opus 5.5, high effort. The desktop runs this chain in one window; the chain worker is enabled again by the owner so a dead session restarts; the other machines are off tonight.

## Why this chain (the owner's words, 11 November 2026)

The machines were paused on 6 November at 15:16 Pacific for a review that has not happened yet. Since then:

1. **Nothing from GitHub's scheduled jobs has reached main since 6 November.** Session 3713's push guard (`scripts/push_guard.py`, chain 208) now runs the whole suite before any bot push, and the suite on main has been red since 6 November 01:41 UTC (the package test `test_derived_tables_flag_license_and_inputs` on the derived tables' headers, from the health summary of 6 November). So the health summaries of 6 to 9 November and the vacuum of 8 November sit on `wip/red-health-2026-11-06` to `wip/red-health-2026-11-09` and `wip/red-vacuum-2026-11-08`, no "Daily prices" commit has landed since 01:32 UTC on 6 November, no Digest issue has been written since 6 November, and no "hourly network" or "latest prices" commit has landed either. The site's data is five days stale and the Sunday Roundup of W45 was written on it. The guard is right to refuse a red push; the fault is the red suite, and a guard without a repair path is a blockade. **This chain's first job is to make main green, re-land what the guard diverted, and run the catch-up, before anything else.**
2. The owner's rulings of 6 November are in `docs/state/rulings_2026-11-06.md` (uploaded with this file): FERC-714 forecasts may be pulled; no new ERCOT `/misapp` requests; no Google decoding endpoint; the tariff table is public row by row; any machine with memory may land the landing requests. The large-load research is in `docs/reviews/research/large-load-tariffs-2026-11-06.md` (uploaded with this file): 36 tariff rows and 10 operator rules, each with its document, page and quote, for this machine to verify and load.
3. Row 16 of `docs/state/landing_request_portable.md` (`wip/3701-sellable`'s last three changes) waits; rows 1 to 15 landed on 6 and 7 November.
4. The deals and datacenter backfill: the owner approved the run at USD 15 on 5 November; session 3500's estimate is USD 2.93 for the whole window as one run (`docs/state/backfill_estimate_2026-11-06.md`); the new extractor landed as row 8 (`886afe777`). **It runs in this chain, as one window run, under the cap.**

## Rules for every session

The rules of `queue/done/147-day-5-november-data-daily-run-landings-large-load.md` and `queue/done/157-day-6-november-data-derived-tables-landings.md` hold word for word (never stop: any wait over 20 minutes stopped and the step done directly, no sleeping until a time of day, the weekly limit the only stop; the next file first; `.venv\Scripts\python.exe`; the main checkout `C:\Users\Shared\Documents\erw` and worktrees beside it, removed once landed; landings through `scripts/land_check.py` with every printed command run as its own command and its exit read, 3 GB free, never between 14:00 and 16:15 UTC, the snapshots before and after the only touch of production; the daily run repaired never bypassed, no test skipped or marked expected-failure to make a run green; default-neutral: no page opens to visitors, nothing released on Redivis, nothing sent or posted, no page's default figure moved; no new country or foreign operator source; every warehouse write under the data lock with the locked write scripts; the report in chain 145's form, short bullets, "Decisions made without you", "For Samuel's ruling"; no em or en dash; a push to main never piped and followed by `git status -sb`). Also:

- **Session 3750 writes the next file first** (`queue/next/<first free number at or above 212>-day-12-november-data-continued.md`, `machine: data`, at least fourteen sessions: this chain's unfinished steps first, then the parked data files' live steps: `queue/parked/193` (the derived tables' second passes), `queue/parked/204` (the large-load continuation), `queue/parked/197` (the findings' landings and second pass), read and folded in, their stale steps dropped and said so), commits it alone and pushes it; session 3773 updates it.
- **The push guard stays.** No session weakens `scripts/push_guard.py` or `scripts/suite_gate.py`; a red suite is fixed in the code the failing test names. Where a test is wrong rather than the code (a test pinned to a dated figure or a wording the data machine rewrites daily), the test is changed to check the rule the figure follows, with the reason in the commit.
- **The rulings file is read first** and applied: a session that meets one of its five items acts on it without asking.
- **The research file's figures are leads, not data:** each row is loaded only after its cited document is fetched and the figure read there (robots and terms of the host first; a host the file lists as refusing is not asked by the reader; the document taken from the mirror the file names, or the row waits, said so), with the filing cited in the row. A figure the file marks secondhand goes to the row's notes.
- **Model calls** under the owner's key: the backfill USD 15 at most (one run); the scorer's catch-up as the daily run's own steps spend it (the daily cap in `.env` as it stands); the Ask weekly run USD 4; every call's cost in the report.
- **The owner reviews nothing tonight:** every "For Samuel's ruling" item goes to the note with its recommendation and the default taken; nothing waits on him.

Read first: `docs/state/rulings_2026-11-06.md`, `docs/reviews/state-of-the-erw-2026-11-06.md` (sections 2, 3, 5 and 6), `docs/state/main_red_2026-11-06.md`, `docs/state/note_2026-11-07_portable_sellable.md`, `queue/summary/2026-11-06-health.md`, `docs/state/backfill_estimate_2026-11-06.md`, `scripts/push_guard.py`, `scripts/suite_gate.py`, the three parked data files named above, `docs/reviews/research/large-load-tariffs-2026-11-06.md`, `CLAUDE.md`.

## Session 3750: the next file, the ground, the red suite named

Long end 1:00. The next file. Then: memory and disk; worktrees of landed branches removed; the chain worker's state read (not changed); `git fetch origin`; the red branches listed with their commits; **the suite run on a clean worktree of origin/main as the guard runs it** (`scripts/suite_gate.py --ref origin/main`), every failing test named with its first error line, written to `docs/state/main_red_2026-11-11.md`; the daily run's last five runs on GitHub (`gh run list --workflow daily-prices.yml -L 8` and each run's "merge tests", "package tests" and push-guard steps) with their first error lines; the hourly network's and latest prices' last runs the same way; whether the runs are failing, or passing and refused at the guard, or not starting at all (a workflow disabled by GitHub after inactivity, or by a person), said plainly in the file.

## Sessions 3751 and 3752: main green

Long end 1:30 each. Every failing test of 3750's list root-caused and fixed in the code the test names (the package test on the derived tables' header line first: the header says what the test expects, or the test is wrong and is changed to the rule, with the reason), on `wip/3751-green`, each fix with its own commit; the suite green twice on the clean worktree; landed through the gate (the gate itself runs the suite on the merged tree). If the hourly or 15-minute workflows are not starting, the reason (GitHub disables scheduled workflows on a repository with no commits for 60 days, which is not this; a workflow file error; a billing or permissions notice in the run's log) written and, where it is a fault of this repository's files, fixed; where it needs the owner (a GitHub setting), the exact setting named in the note.

## Session 3753: the diverted commits re-landed

Long end 1:30. Each `wip/red-*` branch merged with main in its own worktree, the guard run on it (`scripts/push_guard.py --dry-run`), pushed to main through the data path once green (the health summaries of 6 to 9 November, the vacuum of 8 November), the branches deleted; the daily run dispatched with the missed days (`gh workflow run daily-prices.yml -f skip=0 -f days=6`, the input session 2863 added) outside the data lock's hours, watched to its end in 20-minute checks, never a watcher left running; its steps and their status in the report; a step that fails is this session's to fix and dispatch again, once. **No past Digest issue is written** (a stored issue is a record and the owner approves backfills of periodicals): the run writes the day's issue and the missed days' data only; if the run's Digest step would write issues for the missed days, the step is run with today's date alone and the note says which days have no issue.

## Session 3754: the health summary, the stale line, the streak

Long end 1:00. The health summary rebuilt for 7 to 10 November from `erw_health` (`warehouse/health.py summary` for each day, pushed through the guard); the "Stale on main" line now covers the hourly network and latest prices jobs too (allowed 3 hours and 1 hour) and the health summary itself (allowed 1 day), with a test; `/internal/health`'s streak read: it is 0 again, the reason written.

## Session 3755: row 16 landed

Long end 1:30. `wip/3701-sellable` (row 16: session 3718's three changes, `scripts/suite_gate.py`'s traceback handling and the rest the row names) merged with origin/main, the suite, the gate (`--task 3701-3718-sellable --port 3701`), the printed commands, the snapshots; the row marked landed; the branch deleted once an ancestor; `docs/state/landing_request_portable.md` and `landing_request_oldlaptop.md` read for any other row not yet landed and the same done.

## Session 3756: the backfill

Long end 2:00. Pulls: the Claude API, cap USD 15. `docs/state/backfill_claim_2026-11-11.md` pushed to main first ("claimed by lab-desktop, session 3756"). Then `scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05` as one window run (the estimate's USD 2.93; the per-day option does not exist and is not added tonight), under the data lock, through the new extractor on main; the rows written by table and day; the cost; the two tables validated with the locked scripts, archived, coverage rebuilt for them; `check_roundup.py`'s W44 and W45 counts printed (no Roundup regenerated, nothing sent); the branch landed through the data path with snapshots. If the run passes USD 12 before its end, it stops at the next story and says where.

## Session 3757: the daily run's three failing connectors

Long end 1:30. The state report's risk: `eia930` (CAISO and PJM demand incomplete, 25 hours missing), `portwatch` (the IMF answers "Invalid URL"), `ercot_as_prices` and its rollup (the `/misapp` list, HTTP 503; ruling 2: no new `/misapp` request, so the connector is changed to stop asking and to mark the table stale with the ruling cited, not to retry). Each root-caused with its test and fixed in `wip/3757-connectors`; landed; the next run's health read by session 3771.

## Sessions 3758 and 3759: FERC-714 forecasts (ruling 1)

Long end 1:30 each. The FERC-714 Part 3, Schedule 2 planning-area forecasts pulled (FERC's eLibrary or EIA's republication, robots and terms first, the newest XBRL or CSV vintages, within a ceiling of 40 requests), written as `ferc714_planning_area_forecasts` (public), then `ferc714_forecast_growth` as chain 157's sessions 2949 and 2950 described (the revision of the same forecast year across filing years, in MW and percent; the ten largest upward revisions named in the method note), validated, archived, in coverage, method note, tracers; the cross-check against EIA-930's actual peaks where the names map.

## Sessions 3760 to 3763: the large-load tariff registry from the research file

Long end 1:30 each. The research file's rows loaded into `utility_large_load_tariffs` as the rules say (document fetched, figure read there, filing cited; public where the source is a commission docket or filed tariff book, internal where the only source is a host whose terms ask permission; secondhand figures to notes): 3760 the adopted tariffs with rate sheets read (AEP Ohio DCT and BTCR, Evergy Missouri Metro and West LLPS, Ameren LLCS, Entergy Louisiana's two, Entergy Texas LIPS, Georgia Power TOU-SC-15, SRP E-67, APS XHLF, Alabama Power LPL, Oncor and CenterPoint transmission service and TCRF); 3761 the ordered and pending ones as rows with status (Dominion GS-4 and the GS-5 order, Duke's LLT settlement, Xcel Colorado's TL, NV Energy's LGS-X and LLESA framework, PGE's Order 26-154, I&M's notice, Utah's framework, Alabama's Act 2026-610, PUCT Project 58000), each with `status` (adopted, ordered, proposed, framework) and the research file's gaps as notes; 3762 `large_load_connection_rules` from the file's operator table (ERCOT PGRR 115 and the LLIS clocks and fee, PUCT 16 TAC 25.194 as far as a primary document states it, PJM's definition, EIT and Show Cause proposal, MISO ERAS, SPP HILL, CAISO's straw proposal, FERC's six orders), each row with its document and page, a stated duration or "not stated"; 3763 the method notes `docs/methods/large_load_tariffs.md` and `large_load_connection_rules.md` (the sources, the verification rule, the status vocabulary, the row-level license, the limits), the tracers, the cross-check (a utility's demand charge against the figure EIA-861's revenue per kW implies for its largest class, as a check).

## Session 3764: the tab wired

Long end 2:00. The All grids tab's Transmission and 4CP and Time to connect columns read the two tables (every cell a figure with its filing as a hover, or "licensed source needed", or "not held"; the owner's UI rules: hover tips only, inputs left, results right, no layout change); `siting_page.py` and `gaps.json` rebuilt; `docs/reviews/siting-gaps.md` given its state section; landed through the gate with the tab read at 390 and 1280 on the local build with the internal cookie, screenshots.

## Sessions 3765 and 3766: the findings landings and the second pass (parked 197)

Long end 1:30 each. `queue/parked/197`'s live steps: the findings drafts' state (how many, where, which landed), the second read's verdicts in `docs/reviews/findings-second-read-2026-11-06.md` if it exists (the old laptop's third window wrote it) applied: every draft marked "fix first" fixed or removed, "drop" removed with the reason, "ready" left as a draft for the owner; the ranked twenty rewritten from what stands; landed. Nothing approved, nothing published.

## Sessions 3767 and 3768: the derived tables' second pass (parked 193)

Long end 1:30 each. `queue/parked/193`'s live steps: `iso_queue_snapshot_summary` loaded into the live set (the state report: 0 rows live against a built table); the weekly gas storage's refresh checked (ended 16 October; `gas_balance_weekly` rebuilt if the refresh caught up); the per-reactor outages' schedule (ended 21 October: the connector's schedule added to the daily run's monthly list if EIA publishes monthly, said so if not); CARB LCFS stale-at-source rule read (53 days: the limit raised to 60 with the reason, or the series marked discontinued); landed.

## Session 3769: the Ask weekly run

Long end 1:00. Pulls: the Claude API, cap USD 4. The thirty, the lab's twenty, the trader's twenty, the investor's twenty and the board's five through the Python loop on main as landed, graded under their named rules, recorded in `runs.json` and `ask-history.md`; a regression (a count below its last) is the first line of the note.

## Session 3770: the Stanford draft and the records

Long end 1:30. The Stanford draft takes this chain's public tables in a plain upload, `--reconcile`, the release note extended, `docs/state/redivis_v1_ready.md` rewritten as the owner's click list (nothing released); `python package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009; `scripts/build_llms.py` run so `llms.txt` carries the new tables.

## Session 3771: the daily run's week, read again

Long end 1:00. The daily run's runs since session 3753's dispatch, each step and its status, the guard's verdict on each push; the data machine's own `dm_` rows; the health summary's "Stale on main" line quoted; a fault fixed with its test; if any bot push is still refused, the failing tests named as the first line of the note.

## Session 3772: the pages checked

Long end 1:30. On a local build: `check-values`, `check-links.mjs` and AccessLint on every page this chain's tables feed (the All grids tab, the datacenter tracker, the board's gas group, `/internal/health`, `/internal/findings`, Ask), the two known floors read by hand as the state report says; faults of this chain fixed and landed.

## Session 3773: the note, the next file, the landing, the queue

Long end 1:00. `docs/state/note_2026-11-12_data_c211.md` (chain 147's note's form: what landed with commits, main's state and the guard's record since 3751, the catch-up's days and what each wrote, the backfill's rows and cost, the tariff and rules tables' rows by status and license, what did not finish and why, the decisions made without the owner, the questions for his ruling with the default taken, the model's cost); the next file updated and pushed alone; this chain's branch landed through the gate; `python scripts/chain_queue.py next`, and run the file it prints the same way.
