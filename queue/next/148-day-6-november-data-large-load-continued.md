# Chain of 6 November 2026: sessions 2886 to 2903, data machine (lab-desktop), unattended: chain 147's unfinished steps, the siting gaps a public US source can close, the daily run's week, the records

machine: data

Written by session 2862, the first session of `queue/done/147-day-5-november-data-daily-run-landings-large-load.md`, at the owner's instruction in that file ("at least fourteen sessions numbered from the first free numbers after 2885"). The next free number in `queue/next`, `queue/todo`, `queue/parked` and `queue/done`, on origin's main and on every branch, was 148 (147 taken by this machine at 20:41 UTC on 5 November 2026). This file takes sessions 2886 to 2903, the first eighteen numbers after 2885; no commit message and no file on origin's main or on any of its 216 remote branches named a session from 2862 to 2905 when this was written. The first session checks again, skips a taken one upward and says so. Session 2885 of chain 147 updated this file at chain 147's end (6 November 2026, its step 2): sessions 2886 to 2888 below hold the steps chain 147's note (`docs/state/note_2026-11-06_data_c147.md`) says did not finish, in chain 147's order. Numbers 149 and 150 were taken by the code machine's chains on 5 and 6 November, so this file's successor takes the first free number after them (151 when this was updated). Model: Opus 5.5, high effort. This machine runs one Claude Code session, this chain, and nothing else.

## Why this chain

Chain 147 (the owner's file of 5 November 2026) repaired the daily run, landed the stuck branches and started the large-load dataset: the tariff registry (`utility_large_load_tariffs`), the connection rules, HIFLD's substations and lines, a zone's own demand growth, reserve margins and ERCOT's settlement point mapping. This chain finishes what chain 147 did not, then takes the open rows of `docs/reviews/siting-gaps.md` that a public US source can close without a ruling, one row a session, then reads the daily run's first week since its repair and brings the records up to date. The owner's rule of 24 October and 5 November holds first: no new foreign country's or foreign operator's source.

## Rules for every session

The rules of `queue/next/146-day-16-december-data-mepso-cges-kostt-ost.md` (parked by session 2862, readable at `queue/parked/`) and of `queue/done/145-day-15-december-data-seps-ast-ems-nosbih.md` hold, word for word, except where a line below replaces one; among them the robots and terms rule, the closed hosts (not asked again), the keys not held (a session that needs one stops that step and says so, without signing up), `scripts/precheck.py` first from the main checkout, the data lock, the union merge of generated lines, no character typed as an escape, no em or en dash in any file, a push to main never piped and followed by `git status -sb`, the Redivis request cap between tables, a currency other than USD a standing question. Also:

- **No new country or foreign operator source** (above). A source session of this chain takes only US sources (federal, state commission, ISO, utility) and only the ones named.
- **Never stop.** No session ends by stopping to ask the owner; it takes the most reasonable reading, writes it under "Decisions made without you" in its report, and goes on. A session whose step cannot be done writes why and goes to the next step. Any wait over 20 minutes (a deploy watcher, a build that is not building, an agent that has not answered) is stopped and the step done directly. The chain never sleeps until a time of day; where a landing window is closed it does the next session's non-landing work and comes back.
- **Session 2862 writes the next file first** (below), before any other work, and session 2885 updates it. The queue must never be empty for this machine.
- **The python is `.venv\Scripts\python.exe`** in every command; the main checkout is `C:\Users\Shared\Documents\erw`; worktrees go beside it as `C:\Users\Shared\Documents\erw-<task>` and are removed once their branch is an ancestor of main (the old laptop's disk filled from fifty worktrees on 21 October).
- **Landings on this machine** (the owner's ruling of 5 November): a code branch is landed here through `scripts/land_check.py` exactly as `docs/machines.md`, "The landing gate", says, with its printed commands each run as its own command and its exit read; never between 14:00 and 16:15 UTC and never on a Sunday between 22:30 and 23:45 UTC; the build needs 3 GB of memory free (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory` before the gate); one landing at a time; the snapshot before and after is the only touch of production (the owner's ruling of 24 October: no `check-values` against production, only against the local build). Each branch is merged with origin/main first, conflicts resolved as the rules say (generated lines as the union with their true count; coverage rows row by row from the side holding the newer row). A gate that fails on a fault of the branch's code is fixed on the branch, with a test, within the session's long end, and run again; a gate that cannot pass by the long end is written up (the step, the first error line, what was tried) in the chain's note and the session moves on. A branch is never landed with `--force`, never by skipping a step, and never with a page's default figure moved.
- **The daily run's steps are repaired, never bypassed:** no test is skipped or marked expected-failure to make the run green; the fault is found and fixed with its test. A warning that became an error (a dependency's new version) is fixed in the code that raises it, and the dependency pinned where the repository pins the others.
- **Default-neutral:** no page's default figure moves, no ruling is made, nothing is released on Redivis, no letter or email is sent, nothing is posted, no page opens to visitors (`site/lib/release.ts` untouched), no backfill of a periodical is run (the owner approves backfills himself).
- **The report of every session** in the form of chain 145's sessions: what it did, with commits; what it found; "Decisions made without you"; "For Samuel's ruling". Short bullets, not prose paragraphs. Each figure the session writes to a table is traced to its source document and page or endpoint.
- **GitHub reads** with this machine's token, at most 60 requests a session; the `gh` CLI where it is signed in, else the API.
- **The weekly Claude limit:** stop at it and resume at its reset, nothing else stops the chain.

Read first: `docs/state/review_2026-10-31_portable.md`, `docs/state/review_2026-10-30_code_ask_board.md`, `docs/state/review_2026-10-29_portable.md`, `docs/state/review_2026-10-29_code.md`, `docs/reviews/siting-gaps.md` (its table and its last state section), `queue/summary/2026-11-04-health.md`, `docs/machines.md` ("The landing gate", "The chain worker"), `CLAUDE.md`.
In the rules above, read "Session 2862" as session 2886 and "session 2885" as session 2903 (the rules are chain 147's, carried word for word).

Also read first: `docs/state/note_2026-11-06_data_c147.md` (chain 147's note; `note_2026-11-06_data.md` is chain 058's), and chain 147's session reports under `archive/sessions/`.

## Session 2886: the next file, the ground, chain 147's first unfinished step

Long end 1:30. Pulls: GitHub only.

1. Write `queue/next/<the first free number, 151 or later>-...` for this machine in this file's form: `machine: data`, Opus 5.5 high effort, at least fourteen sessions numbered from the first free numbers after 2903; its content: every step of this chain that its note says did not finish, then the siting gaps rows still open that a public US source can close without a ruling, then the daily run's seven days and the records; it carries these rules word for word. Commit it alone, push it to main, `git status -sb`.
2. `scripts/precheck.py` from the main checkout; memory and disk free; `scripts/freeze.py status`; the Anthropic key's state as chain 147's session 2862 read it.
3. **Chain 147's first unfinished step, the Ask evaluation's rest** (chain 147's session 2867, "To finish"; cap USD 3.50 in all, the Claude API only): in `warehouse/chat/eval/eval_s1113.py` a set `s1133` whose questions are `eval_s1133_s1114_questions.yaml` and whose run is `eval_s1133_s1114_run.json`, with its test; then on a served build of main with `ASK_EVAL_DAILY_USD` and `ASK_EVAL_TOKEN` in its `site/.env.local` (never committed), t09 to t11 asked (cap USD 2.50). An asking script for the board's five questions (`questions_s1122.yaml`, cap USD 1), modelled on `eval_s1113.py --ask`, with its test. Each run added to `runs.json`; the branch landed through the gate.

## Sessions 2887 and 2888: chain 147's other unfinished steps

Long end 2:30 each. Pulls: as the step of chain 147 says.

**Session 2887, the tariff registry continued** (chain 147's sessions 2872 to 2874; at most 25 requests, robots and terms first): first the utilities the tab's rows sit in, so `tariffs.json` can be wired (chain 147's session 2880): Duquesne Light (Pennsylvania PUC, `puc.pa.gov`, read before by the data machine), AES Indiana (the IURC's terms need written permission: say so and skip), Oncor and CenterPoint (the PUCT is restricted: say so). Then the named utilities not reached: Ameren Missouri and Evergy (EFIS runs its search in the page's script; try the case's own address if a filing names it), Entergy Louisiana, Xcel Colorado, APS (the ACC's eDocket API), SRP. Each figure into `warehouse/sources/large_load_tariffs/` with its page; the table written with `runs/c147/write_table.sh` (VALIDATOR=branch while the `filing_cited` check is on a branch). If a held tab row's utility gets a schedule, session 2888 wires it.

**Session 2888, the wiring and the run's catch-up** (no pulls but GitHub's API, 20 requests): if session 2887 filled a tab row's utility, `tariffs.json` written by `siting_page.py` and read by `lib/sitingdata.ts`, the Transmission cell drawn from `tariffFor` and `tariffParts` (a branch, the gate). Then the daily run dispatched by chain 147 with `days=7` (run 42120465428): its steps read; if any table still lacks the days 30 October to 5 November, say which. A step that waits on a ruling (the ERCOT DAM list at `/misapp`, the tariff table's license) is not done: its question goes to this chain's note.

## Session 2889: ERCOT nodes, the wires utility (TSP)

Long end 1:30. Pulls: at most 15 requests, through ERCOT's public API and its public reports pages as chain 147's session 2879 reached them; never `/misapp` or `/misdownload`.

Siting gaps row "ERCOT nodes | Utility | a node's wires utility (TSP)". **First:** `ercot_node_wires_utilities` is already held on this machine (chain 147's session 2881); wire it into `nodes.json` if it holds what the row needs, and pull nothing. ERCOT's public resource lists (the Resource Asset Registration summaries ERCOT posts publicly, or the settlement point list's own TSP field if NP4-160 carries one) joined to `ercot_node_places` and chain 147's settlement point mapping. One column added where the mapping table is, not a new table, if the mapping carries it. ERCOT: public (licenses.md #2). A source reachable only through a path the robots file closes: said, and the row left open.

## Session 2890: ERCOT nodes, the county

Long end 1:30. Pulls: none (the warehouse's own tables), or at most 10 requests if a crosswalk is needed.

Siting gaps row "ERCOT nodes | Node panel | a node's county": each placed node's county from its latitude and longitude against the Census county boundaries the warehouse holds (or the ERCOT resource registration's county, where session 2889 read one), and EIA-860's plants matched to the resource where the node is a resource node. `warehouse/derived/` with its test and method note. EIA and Census: public domain.

## Session 2891: ERCOT nodes, transmission projects by county

Long end 2:00. Pulls: at most 15 requests.

Siting gaps row "ERCOT nodes | Node panel | transmission projects by county": ERCOT's Transmission Project and Information Tracking report (TPIT), public, robots and terms first. `ercot_tpit_projects`: project, TSP, counties, voltage, in-service date as stated, status, cost where stated, the report's month and address. The PUCT's CCN filings are not read (PUCT: restricted).

## Session 2892: ERCOT nodes, the price in the four peak intervals

Long end 1:30. Pulls: at most 10 requests.

Siting gaps row "ERCOT nodes | Node panel | a node's price in the four peak intervals": the four intervals of summer 2026 from `ercot_4cp` (if ERCOT has posted them; if not, the session says so and the row waits), the 15-minute real-time settlement point prices of those intervals (NP6-905-CD) kept for the four intervals only, by ERCOT's public API as `ercot_rt_spp.py` reaches it.

## Session 2893: ERCOT, the controllable load's faster path

Long end 1:30. Pulls: at most 10 requests.

Siting gaps row "ERCOT | Time to connect | the faster path for a controllable load": ERCOT's Controllable Load Resource registration rules (Nodal Protocols section 3.8 and the large-load interconnection guide), one row in `large_load_connection_rules` (chain 147's session 2875) with the stated steps and durations, the document and page. ERCOT: public.

## Session 2894: CenterPoint's own revenue

Long end 1:30. Pulls: at most 10 requests, EIA only.

Siting gaps row "ERCOT | Utility | a Texas wires utility's own revenue". **First:** `eia861_delivery_only` is already held on this machine (chain 147's session 2881). EIA-861's delivery-only rows for Texas (the Sales to Ultimate Customers file's delivery-only sheet, if `eia861_sales.py` does not read it yet), for CenterPoint, Oncor, AEP Texas and TNMP. EIA: public domain. The tab's Utility cell for Harris County read after.

## Session 2895: CAISO's utilities, the large-load delivery charge

Long end 2:00. Pulls: at most 25 requests, the CPUC's and each utility's host's robots and terms first.

Siting gaps row "CAISO | Transmission and 4CP": PG&E's E-20 (or B-20), SCE's TOU-8 and SDG&E's AL-TOU transmission-voltage schedules, read from the tariff each utility files with the CPUC, added to `utility_large_load_tariffs` with the registry files chain 147's session 2871 set up, each figure with its sheet and page. A utility site whose terms bar the reader is not read; the CPUC's filed copy is.

## Session 2896: NYISO's utilities, the large-load service classifications

Long end 2:00. Pulls: at most 25 requests, the PSC's (DPS) host's robots and terms first.

Siting gaps row "NYISO | Transmission and 4CP": the large-load service classifications of Con Edison (SC 9 high tension), National Grid (SC 3A), NYSEG and RG&E (SC 7), Central Hudson (SC 13) and O&R (SC 9), from the tariffs filed with the New York PSC, into `utility_large_load_tariffs`. NYISO's own figures are not read (no license conferred).

## Session 2897: ISO-NE's utilities, the large-load rates

Long end 2:00. Pulls: at most 25 requests, each commission's host's robots and terms first.

Siting gaps row "ISO-NE | Transmission and 4CP": Eversource (Massachusetts DPU and Connecticut PURA filed tariffs), National Grid Massachusetts, Unitil and Central Maine Power, their largest general service schedules, into `utility_large_load_tariffs`. ISO-NE's regional network service rate is not read (permission to request).

## Session 2898: interruptible riders

Long end 2:00. Pulls: at most 25 requests.

Siting gaps row "All but ERCOT, CAISO, SPP | Capacity, heavy industry | an interruptible load's capacity charge": the interruptible or curtailable riders of the utilities already in `utility_large_load_tariffs`, read from the same filed tariff books (no new host where one already read serves), one row a rider, the credit or charge as the rider prints it. A new table `utility_interruptible_riders` only if the tariffs table's shape cannot carry it.

## Session 2899: generation with a signed interconnection agreement

Long end 1:30. Pulls: none if `lbnl_interconnection_queue` holds `ia_date`, else at most 5 requests to eta-publications.lbl.gov (emp.lbl.gov answers 403).

Siting gaps row "All | Headroom | generation with a signed interconnection agreement". **First:** `interconnection_agreements_signed` and `interconnection_agreements_by_grid` are already held (session 854, chain 147's session 2881). for each grid and each zone the warehouse can place, the MW with an `ia_date` and no operation date, by year of agreement, derived from Berkeley Lab's queue file. `warehouse/derived/` with its test and method note. Berkeley Lab's license as `license_verdicts.csv` records it; if it is not public, the table is internal and the row says "held".

## Session 2900: the daily run's seven days

Long end 1:00. Pulls: GitHub's API, at most 30 requests.

As chain 147's session 2884: each scheduled job's last seven days, the daily run's runs opened one by one, each failed step with its first error line, a fault of this repository's code fixed with its test; the "Stale on main" line of the newest health summary quoted in the report.

## Session 2901: the siting gaps file and the records

Long end 1:30. Pulls: none.

A new state section in `docs/reviews/siting-gaps.md`, dated, every row this chain moved; `package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009 against this chain's tables, rebuilt if stale; this chain's tables' method notes checked against their code.

## Session 2902: the Stanford draft

Long end 2:00. Pulls: Redivis's API only, at most 150 requests, the branch merged with main first.

As chain 147's session 2882: `--reconcile`; this chain's public tables into the Stanford draft in a plain upload; `--reconcile`; the release note and `docs/state/redivis_v1_ready.md` extended. Nothing released.

## Session 2903: the note, the next file, the landing, the queue

Long end 1:00.

1. `docs/state/note_2026-11-07_data.md` in session 683's form: what landed, what did not and why, the decisions made without the owner, the questions for his ruling, the cost of any model calls.
2. The successor file (written by session 2886) updated with what this chain did not finish, first in its order; pushed to main alone.
3. Land this chain's own data branch: merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`, and run the file it prints the same way.
