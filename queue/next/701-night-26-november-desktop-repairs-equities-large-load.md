# Chain of 26 November 2026, night: sessions 10000 to 10199, data machine (lab-desktop), first window, unattended, until the weekly limit: the landing desk for five other windows, the week's broken jobs repaired, energy stocks and indices brought into the warehouse, and the large-load dataset brought current

machine: data

Written by Claude in chat with Samuel on 26 November 2026 at about 03:15 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Samuel could not review this week and has the weekend for it. The weekly Claude allowance resets on Friday 27 November at 14:00 PST (22:00 UTC) with most of it unspent, and he wants it spent on builds that push the ERW forward, not on fixes for their own sake. Since 20 November no machine has built anything on the ERW itself. This window does three things: it lands for five other windows, it repairs what broke this week because everything built tonight stands on it, and it builds two things a reader cannot get from the ERW today: the listed energy companies and indices beside the energy prices the warehouse already holds (Samuel's ask of 24 November, approved for this run on 26 November), and the large-load dataset brought current and deepened (his "next tier" list names it, and no one else publishes it). Nothing here waits on a ruling.

## The six windows of this run (who owns what)

| Window | Chain | Folder | Owns tonight |
|---|---|---|---|
| A, desktop first window (this one) | 701 | `C:\Users\Shared\Documents\erw` | every landing; the data lock and every warehouse table; the daily run; `warehouse/connectors/equity_*`, `warehouse/derived/equity_*`, `site/data/equities/`, `docs/state/page_files_equities.md`; the large-load tables and `docs/research/large_load/` |
| B, desktop second window | 730 | `C:\Users\Shared\Documents\erw-w2` | the codebook's last steps; the ERW forecast: `warehouse/predict/`, `site/data/predict/`, `docs/state/page_files_predict.md`, `docs/state/data_requests_predict.md`, `replication/predict/` |
| C, desktop third window | 740 | `C:\Users\Shared\Documents\erw-w3` | datacenters in the Economic impact tool: `site/app/impact/`, `warehouse/forecast/`, `site/data/forecast/`, `docs/methods/forecast.md`, `docs/state/data_requests_forecast.md` |
| D, old laptop | 710 | `C:\Users\lossa\Documents\erw` | `docs/reviews/weekend-2026-11-28.md`; the datacenter model audit and the Automated Analysis audit (branches `wip/audit-datacenter-*`, `wip/audit-analysis-*`) |
| E, personal laptop first window | 720 | `$HOME\Documents\erw` | the pages: `site/app/forecast/`, `site/app/equities/`, the new group in `site/app/board/` |
| F, personal laptop second window | 750 | `$HOME\Documents\erw-w2` | the browser read of everything landed; its fixes on branches `wip/c750-*` |

A window edits only what it owns. A fault found in another window's files is a row for that window, never an edit. Branch names carry the chain's number (`wip/c701-*` here).

## Rules

- **The rules of chain 601 hold word for word** (`queue/done/601-night-20-november-desktop-grid-conditions.md`, and through it chains 581, 505 and 501 and the owner's rules of 16 November as `queue/done/301-day-16-november-desktop-open-faults.md` has them), with these changes:
- **Session numbers** 10000 to 10199, each checked free on origin/main and every branch first. The four-digit numbers are nearly all taken (the highest used is 9901), so this run's are five digits.
- **This window is the only one that lands and the only one that writes a warehouse table.** The desk reads every `docs/state/landing_request_*.md` (window2, desktop_w3, oldlaptop, portable and the new portable_w2) and every `docs/state/data_requests_*.md` (the new `data_requests_predict.md` and window C's rows in `data_requests_forecast.md` among them) at the start of every session and after each numbered step. This window never kills a process it did not start, never works in another window's folder, and every site build goes through `scripts/buildlock.py`.
- **Samuel's ruling of 26 November for this run:** a fix goes in only if it is important, and it is never the plan. Part C is in this chain because the pages and tables are going stale; it is done once, at the cause, and the chain moves on. A session whose only output is a repair that no reader and no later build needs is a fault of this chain.
- **The health gate and this run.** `PRIORITIES.md` holds new sources and tools while the daily run fails outside the known-gap list, and says a direct request wins. Samuel asked for parts D and E directly on 26 November, so they do not wait on the gate. Part C still comes first.
- **No waiting, anywhere.** A step that needs a publisher's answer, a long pull, a lock another process holds or a file another window has not written yet is marked waiting in the progress file and the next step is taken at once. No sleep, no timer, no "waiting" commit.
- **What exists is read before anything is built** (rule 4): each part starts by listing in the progress file what the warehouse and the site already hold of it. What exists is extended, never built twice.
- **Licenses first.** For each source: the robots file and the terms are read before any pull, and the verdict is written with the license codes of `docs/price-sources.md`. A source whose terms forbid automated readers is not pulled (Yahoo is already ruled out there). A source that may be read and not redistributed gives an internal table, and the page draws its cells blank with the hover "license needed". No hold is lifted or worked around. No paid service is called and nothing is bought.
- **Add, never change. No default moves. No ruling is taken for Samuel.** No `wip/alt-*`, `wip/switch-*` or `wip/audit-*` branch is landed unless its row in a landing request file is marked requested by the window that owns it. Every new page stays in review, in no menu, listed on `/in-review`.
- **No model of the ERW's own in this chain, no advice, no view.** The equities tables say what the companies and the exchanges published.
- **Sound before landed.** Each new table: validated by `erw_validate.py`, registered (coverage, sources, license record), archived, with a method note and a test. Each page file: traced to its rows by `check-values`. Each landing: through `scripts/land_check.py` with the whole suite, a build and a snapshot before and after.
- **Disk and memory.** At the start of every session and before every gate: the free space of drive C and the free memory, written in the progress file. Under 20 GB free: the worktrees of this machine whose branch is already in main are removed, their ignored files listed first; no other worktree is touched (the older gate worktrees wait for Samuel's ruling, as session 9001's report says). No background render and no second build while one runs.
- **Never end idle.** After part E, part F, until the weekly limit.

## The start (session 10000, long end 0:45)

1. `git fetch origin`. If this folder's `main` cannot fast-forward to `origin/main` (the data machine's daily run has been refused its push since 21 November and may hold commits of its own): the local commits are pushed first as `wip/c701-local-main-2026-11-26`, untracked and ignored files are listed in the progress file and left where they are, and `main` is then set to `origin/main`. Nothing is discarded.
2. Precheck. Free disk and memory. This chain's file taken (`queue/next/701-...` to `queue/done/`), if the command that started the session has not already done it.
3. The resume file `queue/next/702-resume-chain-701.md`, committed alone and pushed, its text the lines between BEGIN and END below without those two words. A session that takes a resume file first writes the same text under the next number up (to 709). The chain's last session removes it.
4. `docs/state/progress_c701.md`: one line a landing, request, repair, source, table, file or view, its state and session, pushed after each.
5. Part A, then part B, in this same session.

BEGIN
# Resume of chain 701

machine: data

Chain 701 was interrupted. First put this same text back in queue/next/ as the next number up to 709, named NNN-resume-chain-701.md, committed alone and pushed. Then read queue/done/701-night-26-november-desktop-repairs-equities-large-load.md whole and docs/state/progress_c701.md, and continue chain 701 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests

As part A of chain 501, unchanged, at the start of every session and after each numbered step below. A desk with nothing requested takes two lines of the report. The windows of this run ask often: a requested row older than two numbered steps of this chain is a fault of this chain.

## Part B: the contract for the equities pages (done and pushed to main within this chain's first hour)

Window E builds the pages tonight and cannot start without this. `docs/state/page_files_equities.md`, in the form of `docs/state/page_files_conditions.md`: the files this chain will write under `site/data/equities/` (an index of companies and indices by segment; one file a company or index with its daily series; a board file of the rows the price board shows; a file of the energy prices set beside them), each file's fields with name, type, unit and an example row, how a held value is written (the field present, the value null, a `held` reason), and the date each file was last written. The shape is fixed here; which companies and which series fill it is part D's. One small example file of each kind, marked as an example and holding no invented price (its values null), is pushed with the contract so that window E can build against it. A later change to the contract is one dated line at its foot and a line in window E's file `docs/state/landing_request_portable.md` saying so.

## Part C: what broke this week, repaired at the cause (long end 2:30; past three hours, go on to part D and return between its pulls)

Read first: `queue/summary/2026-11-21-health.md` to `2026-11-24-health.md`, the commit messages of the daily runs of 21 to 25 November on main, and the data machine's own runs on the branches `wip/red-dm-2026-11-21` to `wip/red-dm-2026-11-25`. Each failure below gets its root cause written in one line, a fix at the cause, and a test or a check in the validator so that the next one is caught (stop the class, not the instance):

1. **The load into Supabase** has failed every day since at least 21 November on `datacenter_projects`, `energy_deals`, `news_index` and `sources`, so the pages that read them go stale. Find why. If the load's own guard is refusing a table and is right to (rule 4 of the owner's rules of 16 November: the guard stands while the key is closed), the guard is not overridden: the step is made to say "held" with its reason in place of "failed", and the question is one plain line for Samuel's ruling with the default "left as it is". No table is rebuilt or re-extracted with a model.
2. **The battery page's files:** `dm_battery_dispatch_export` (8 monthly sums differ from `battery_stack_monthly`), `dm_battery_scenario_steps` (October 2026: 30 days in the run, 29 in the table), and the tests that follow them (`dm_test_battery_dispatch`, `dm_test_battery_steps`, `dm_test_freeenergy`, `dm_test_replication`). The table and the files are brought to agree on the same whole months, the public file and the replication are written again for the window the page now shows (finding 11 of `docs/reviews/battery-model-audit-2026-11-20.md`), and the figure before and after is written in the report. No default and no rule of the model changes.
3. **The data machine's daily page files have not reached main since 20 November:** its push is refused by `test_session8613`. After the cause is fixed, today's page files land through the gate.
4. **`dm_live_set`:** "coverage.csv is older than the tables it describes". The order of the daily steps is fixed so that coverage is built before the live set is loaded.
5. **The package test** `package/tests/test_erw.py::test_info_summary_and_table` pins a row count that moves every day (180843586 against 180844738). The test is made to hold what it means to hold.
6. **`ercot_storage_dam`** (21 November): the monthly awards table is built before the monthly offers table.
7. **Hourly network** was 4 hours stale on 24 November against 3 allowed: the cause, or one line saying it was a single late run.
- The Digest and the Roundup stay stopped: the key is at its limit until 1 December and no model call is made.
- Then `python warehouse/metadata/build_status.py --gate`, its exit code and what still fails written in the progress file. A failure that cannot be closed without a ruling or the key is one plain line for Samuel's ruling, with the default taken, and the chain goes on.

## Part D: energy stocks and indices

1. **The ground (long end 0:45):** `docs/reviews/equities-sources-2026-11-26.md`. For every source that could give a list of listed energy companies, their daily prices and volumes, their share counts and financial statements, and the levels of energy indices: its address, how far back it goes, its robots file, its terms, its license code as `docs/price-sources.md` writes them, and the verdict: public, internal (held), or not pulled. To read, none assumed: the SEC's EDGAR (company list with SIC codes, filings, the XBRL company facts), the exchanges' own published files, FRED's series (public domain against third party), each index provider's own published levels, and any free end-of-day source whose terms are found. The paid licenses that would open a held series go into `docs/licenses_costs.md` with the publisher's printed price where there is one, and into "For Samuel's ruling" as one line.
2. **The universe, `equity_universe`:** every US-listed company whose business is energy, one row a company: its SEC number, ticker, exchange, SIC code, and its segment by a written rule (integrated oil and gas, exploration and production, midstream and pipelines, refining, oilfield services, LNG, coal, regulated electric and gas utilities, independent power producers, nuclear and uranium, solar, wind, storage, hydrogen and fuel cells, grid and electrical equipment). The rule that puts a company in a segment is in the method note; no company is added by judgment alone, and the list a reader could dispute (a company that fits two segments) is written with both. Matched to `company_directory` where it is the same company, by SEC number or exact legal name only.
3. **The tables:** `equity_prices_daily` (close, volume, and the adjusted close where the source prints it), `equity_fundamentals_quarterly` (revenue, net income, capital spending, debt, shares outstanding, as filed, with the filing's address), `equity_index_daily` (each energy index or its published proxy). Each pulled back as far as its source's public archive goes, in whole years, newest first, so that a short table is useful at once and deepens as the chain runs. Validated, registered with its license, archived, a method note each, a test each, and a step in the daily run.
4. **The roll-ups and the page files, by the contract of part B:** for each segment and each company, the change over a day, a week, a month, the year to date and a year; a segment's line computed two ways and labelled (equal weight; weighted by market value where the share count is public); each beside the energy prices the warehouse already holds for the same days (WTI, Brent, Henry Hub, the power hubs that are public, uranium, the carbon prices). Series side by side and a plain change: no score, no signal, no view. A held series is written null with its reason.
5. **To the done line** in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`: a replication under `replication/equities/` that a reader can run, and a cross-check of a sample of share counts and one statement line a company against the filings themselves.

## Part E: the large-load dataset, current and deeper

1. **The ground:** what stands today, from `docs/state/data_requests_large_load.md` (every row and its state), `docs/state/note_2026-11-17_oldlaptop_c302.md`, the fifteen large-load tables in `warehouse/metadata/coverage.csv`, and `https://erw-flame.vercel.app/cost-of-power?view=allgrids` as main has it. Written in the progress file: what is done, what is open, what is held and why.
2. **Every open request row** of `docs/state/data_requests_large_load.md`, in order of request.
3. **The rows of the All grids tab that say "no large-load rule read"** (11 on 17 November) and the utilities and states the tables do not reach yet: each utility's tariff book and each state commission's docket read, robots file and terms first, the rule taken as the document prints it with its cite, in the tables' own form. "No large-load rule found" only after the document was read; never "no law" for a state not reached.
4. **Queue totals:** every operator and utility that publishes how much large load has asked to connect (as ERCOT's monthly aggregate does), each period it has published, into `utility_large_load_queue_totals` and `large_load_waits`, with the document a period.
5. **What changed since 17 November**, into `utility_large_load_rule_changes`, newest first.
6. The page files the tab and `/policy?view=monitor` read are written again; a held rule stays drawn blank. The three tables whose license verdict is unsettled stay out of the live set (Samuel's default of 17 November).

## Part F: after part E, until the weekly limit

- Each equities table deepened a year at a time, oldest year last; the fundamentals back to the first XBRL filings.
- Part D's ground read again for any source whose terms were not found the first time.
- The equities page files traced to their rows by `check-values`; the large-load page files the same.
- Window B's forecast, once its data request rows are done: its daily step seen to run once under the data lock, and its files' figures traced.
- Each of this chain's new views read as its reader (five real cases each: an energy investor on a day oil falls, a utility analyst comparing two utilities, a student of one company, a datacenter developer reading a utility's large-load rule, a trader looking for what moved with gas), every gap a numbered row, every fault of this window's files fixed at its cause with a test.
- Part A after each.

## The last session

- `docs/state/note_2026-11-26_data_c701.md` in short bullets: every landing with what a reader now sees; each repair with its cause in one line and the figure before and after; each new table with its source, span, rows and license; every source not pulled and why; each new page file; what waits for Samuel with the default taken, in plain words, no codes without their meaning.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part F goes on.
