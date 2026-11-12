# Chain of 11 November 2026: sessions 1850 to 1873, code machine (samueloldlaptop), unattended, about 24 hours: the five tools that landed on 6 and 7 November read as a reader and fixed, the first v2 Digest read, the board read on real data

machine: code

Written by the owner with Claude in chat on 11 November 2026 (Wednesday night, about 23:45 Pacific) and uploaded to `queue/next` by the owner. It takes sessions 1850 to 1873; session 1850 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Fable 5.1, high effort. One Claude Code window on this machine; the owner enables the chain worker so a dead session restarts. The desktop runs chain 211 beside it (main made green, the diverted bot commits re-landed, the daily run caught up, the backfill, the large-load tables); this chain touches none of that.

## Why this chain (the owner's words)

On 6 and 7 November five tools reached main for the first time, every one built in a window that could not build the site and landed through the gate by another machine: the deal tracker with its comparables and AI-power view (`task/2230-2295-deals`), the datacenter tracker's page (the same branch), the policy and regulatory monitor (`task/3054-3157-policy`), the company database and the first capital view (`task/3300-companies`), and the attention and friction indices (`task/3400-attention`). The gate proved their numbers trace and their tests pass. Nobody has read them: not the owner, not a second session, not a reader at a fund. The owner's standard for every tool page is fixed: dense and informative, never generic; every figure keyed to its table and row with its source as a hover; explanatory text only as hover tips, never visible grey text; inputs left, results right; charts that answer hover with values; the key assumptions editable in place; no point of view, the tool helps the reader compare and decide; nothing that reads as an image; nothing invented. This chain reads each of the five the way a reader at a lab or a fund reads it, writes every fault with the line that fixes it, fixes them, and lands. Then the periodicals: the first v2 Digest the desktop's catch-up writes, and the W45 Roundup as written, read the same way against the faults file. Then the price board on the real `board.json` after the catch-up.

## Rules for every session

The rules of `queue/done/149-day-5-november-code-periodicals-excellent.md` hold word for word (one window; `.venv\Scripts\python.exe`; precheck first; `git fetch origin` and `origin/main` merged before work, generated lines as the union; worktrees beside `C:\Users\lossa\Documents\erw`, removed once landed; landings through `scripts/land_check.py` with every printed command run as its own command and its exit read, 2 GB free enough with this the only window, never between 14:00 and 16:15 UTC, the snapshots before and after the only touch of production; a gate stopped for memory twice in one session is not tried a third time: a row appended to `docs/state/landing_request_oldlaptop.md` on main and the chain goes on from a branch cut from the unlanded one; default-neutral: `site/lib/release.ts` untouched, nothing sent or posted, no warehouse data written, no backfill, no layout redesign and no brand work; the model under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; the weekly limit the only stop). Also:

- **Never stop.** No session ends by stopping to ask; any wait over 20 minutes is stopped and the step done directly; no sleeping until a time of day.
- **Session 1850 writes the next file first** (`queue/next/<first free number at or above 214>-day-12-november-code-continued.md`, `machine: code`, at least fourteen sessions: this chain's unfinished steps first, then the faults files' open rows, then `queue/parked/207`'s and `queue/parked/210`'s live steps folded in, their stale steps dropped and said so), commits it alone and pushes it; session 1873 updates it.
- **Main may be red when this chain starts** (the push guard has refused every bot push since 6 November; the desktop's chain 211 repairs it in its first sessions). A landing of this chain waits for main to be green (the gate tests the merged tree): until then the chain builds, reads and fixes on its branches and lands at its next landing session. It never changes `scripts/push_guard.py` or `scripts/suite_gate.py` and never pushes anything to main that is not its own documents.
- **The desktop's files, not touched:** the warehouse's tables and connectors, `warehouse/derived/`, the daily run, the health summary, the large-load tables and the All grids tab's wiring, the backfill, Redivis. A fault in a table's data found by a read goes to the note for the desktop's chain, not fixed here.
- **A fault is a quoted line and the line that replaces it,** or a cell and what it should show, or a click and what should happen, numbered in one faults file a tool (`docs/reviews/<tool>-faults-2026-11-11.md`), each with its state. A read that finds nothing wrong says so and why that is credible (what was checked, at both widths, with the internal cookie).
- **The built site is read, not the code alone:** every read session builds the branch locally (`python scripts/db_probe.py` first), opens each page at 390 and 1280 with the internal cookie, hovers, clicks the filters, downloads the CSV, and keeps screenshots under `runs/<N>/shots/`.

Read first: `docs/reviews/state-of-the-erw-2026-11-06.md` (sections 1, 3 and 6), the five landings' notes (`docs/state/note_2026-11-07_portable.md` and the deals chains' notes, `note_2026-11-07_portable_window2.md` for the policy monitor, `note_2026-11-07_desktop_window3.md` for the companies, `note_2026-11-07_desktop_window4.md` for the attention indices, as main holds them), `docs/methods/deals.md`, `datacenter_tracker.md`, `policy_monitor.md`, `companies.md`, `attention.md`, `docs/reviews/periodicals-faults-2026-11-05.md`, `docs/reviews/board-audit-2026-11-06.md`, `docs/brand.md`, `docs/voice.md`, `CLAUDE.md`.

## Session 1850: the next file, the ground

Long end 0:45. The next file. Then: memory and disk; worktrees of landed branches removed; the chain worker's state read; main's state (green or red, from the newest `wip/red-*` branches and `docs/state/main_red_*.md`); the five tools' pages and their addresses listed with the commit that landed each; a first local build of origin/main (the probe first), its time and memory in the report.

## Sessions 1851 to 1853: the deal tracker, read and fixed

Long end 1:30 each. 1851: the read. `/deals` and its comparables and AI-power views at both widths: every filter clicked, every column sorted, the evidence and source hovers, the flags, the downloads opened and their columns checked against the page, the comparables' medians recomputed by hand for one technology and grid from the CSV, the ten largest AI-power deals' evidence read against their stories, the charts hovered; the faults file written. 1852 and 1853: the faults fixed with tests, in the order a reader would hit them; every figure's key kept.

## Sessions 1854 and 1855: the datacenter tracker, read and fixed

Long end 1:30 each. As 1851 to 1853 for the tracker's page: the map layer and the table, the by-grid view against each grid's peak and reserve margin (held cells as the owner's placeholder with the footnote), the timeline's medians recomputed from the CSV for one grid, the rollups' undisclosed counts beside each sum; the faults file; the fixes.

## Session 1856: the first landing

Long end 1:30. The stack merged with origin/main, the suite, the gate (`--port 3850`), the snapshots; or the request row if main is red or memory stops it twice.

## Sessions 1857 to 1859: the policy monitor, read and fixed

Long end 1:30 each. 1857: the read. The monitor's table (body, instrument, docket, status, next step, the impact read, the evidence hovers), the calendar (every next-step date against its document), the charts, the downloads; twenty actions' impact reads checked against their source text (a read that states more than the text does is a fault); the policy games and the Digest's policy row left untouched. 1858 and 1859: the fixes.

## Sessions 1860 and 1861: the company database and the capital view, read and fixed

Long end 1:30 each. 1860: the read. `/companies` search and filters, twenty company pages chosen across kinds (a utility, a developer, a lab, a lender, an OEM, a regulator): every footprint figure clicked through to its rows, the aliases checked for a wrong merge (two companies joined) or a missed one (one company under two names), the charts, the downloads; `/capital`'s thin places said plainly on the page, never padded. 1861: the fixes, the wrong merges and missed aliases foremost, each with its evidence row.

## Session 1862: the second landing

Long end 1:30. As 1856.

## Sessions 1863 and 1864: the attention and friction indices, read and fixed

Long end 1:30 each. 1863: the read. `/attention` by sector and state, the map for a chosen week, the rising places, each value's hover to its stories (ten values opened, their stories read: does the count match, is the opposition class right), the downloads, the method note's limits against what the page says; the research memo's three findings re-read against the page. 1864: the fixes.

## Session 1865: the first v2 Digest, read

Long end 1:30. The Digest issue the desktop's catch-up run writes on 12 November (the first issue written by the v2 code; if it does not exist on main yet when this session starts, this session is done after session 1869 and its slot taken by 1866): read as a reader at a lab or a fund reads it, against the v2 shape of chain 131 and the faults file (`docs/reviews/periodicals-faults-2026-11-05.md`, rows 49 to 54 first: the fold's length, the deal row's duplicates, "site not stated", the five numbers' confidence floor, the Roundup's subject, a bare figure in the Deals table): every fault quoted with its replacement, into the faults file; the counts of `scripts/periodicals_counts.py` on the issue. The W45 Roundup of 8 November read the same way (it was written on five-day-old data; a fault that is the data's is said so and left to the desktop).

## Sessions 1866 and 1867: the periodicals' faults fixed

Long end 1:30 each. The faults of 1865 and the open rows of the faults file fixed on fixtures and the stored issues (no past issue rewritten), tests; one dry run of the Digest on the newest scored day (cap USD 3) with the preview to the one fixed recipient, subject prefixed "[preview, dry run 1867]".

## Session 1868: the third landing

Long end 1:30. As 1856.

## Sessions 1869 and 1870: the price board on real data

Long end 1:30 each. After the desktop's catch-up has rebuilt `site/data/board.json` (if it has not by 1869's start, the board is read on the local builder's output from the warehouse's tables as chain 165 read it, said so): every row chain 165 added read on the built page (its figure, its step, its interval on hover, the extremes, the trend line, the 12-month mean, the held placeholders' words and no digit), `check-board.mjs` on the served page, `docs/reviews/board-audit-2026-11-06.md`'s open rows (28, the 4CP exposure row; 24 and 25 only if their ruling exists in `docs/state/rulings_*.md`), the one keyboard fault; the fixes.

## Session 1871: the paths walked again

Long end 1:30. The trader path on the completed board and Ask with the threshold (`docs/reviews/trader-path.md`), the lab's path on the datacenter tracker, the All grids tab as the desktop leaves it and `/ask`, the On.Energy walkthrough on the battery tool: each rewritten click by click against the pages as they are on the local build, a screenshot a step, the faults fixed or listed.

## Session 1872: the fourth landing, the records

Long end 1:30. As 1856; then every faults file's rows with their state; worktrees removed; the tests green on the chain's head; `docs/reviews/five-tools-read-2026-11-11.md`: one table, a row a tool: faults found, fixed, open, the three worst in plain words, the owner's five-minute check for each (the page, what to click, what he should see).

## Session 1873: the note, the next file, the landing, the queue

Long end 1:00. `docs/state/note_2026-11-12_code_c213.md` (chain 149's note's form: what landed with commits, the faults by tool before and after, the Digest's and the Roundup's reads, the board's rows, what did not finish and why, the decisions made without the owner, the questions for his ruling with the default taken, the cost); the next file updated and pushed alone; what is unlanded landed or requested; `python scripts/chain_queue.py next`, and run the file it prints the same way.
