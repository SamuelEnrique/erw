# Chain of 26 November 2026, night: sessions 10200 to 10399, samueloldlaptop (code role), one session, unattended, until the weekly limit: this weekend's review page sized to Samuel's hours, then the datacenter model and Automated Analysis audited as a hostile expert would

machine: samueloldlaptop

Written by Claude in chat with Samuel on 26 November 2026 at about 03:15 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\lossa\Documents\erw`. Model: Opus 5.5, high effort. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Two things. First, Samuel has this weekend (28 and 29 November) for review and did not get to last weekend's pack: `docs/reviews/weekend-2026-11-21.md` still stands with every ruling empty, and five more windows are building tonight. He needs one page, in order of what one minute of his frees, that he can finish. Second, Samuel wants five tools at a depth he could sell, and has said he wants to know the algorithm under each one cold. On 20 November "what a battery earns" and "what a generator earns" were each read by a hostile expert, and each audit found the arithmetic right and several sentences on the page false. "What a datacenter pays" (`/cost-of-power`), the tool an AI lab's siting team would use, and Automated Analysis, the tool his findings and posts come from, have had no such read. An audit that finds a wrong claim before a fund or a lab does moves the tool toward sellable more than a new page would.

## The six windows of this run (who owns what)

| Window | Chain | Folder | Owns tonight |
|---|---|---|---|
| A, desktop first window | 701 | `C:\Users\Shared\Documents\erw` | every landing; the data lock and every warehouse table; the equities tables; the large-load tables |
| B, desktop second window | 730 | `C:\Users\Shared\Documents\erw-w2` | the codebook's last steps; the ERW forecast of demand and price (`warehouse/predict/`, `site/data/predict/`) |
| C, desktop third window | 740 | `C:\Users\Shared\Documents\erw-w3` | datacenters in the Economic impact tool (`/impact`, `warehouse/forecast/`, `site/data/forecast/`) |
| D, old laptop (this one) | 710 | `C:\Users\lossa\Documents\erw` | `docs/reviews/weekend-2026-11-28.md`; `docs/reviews/datacenter-model-audit-2026-11-26.md` and `docs/reviews/analysis-model-audit-2026-11-26.md`; branches `wip/audit-datacenter-*` and `wip/audit-analysis-*` |
| E, personal laptop first window | 720 | `$HOME\Documents\erw` | the pages `site/app/forecast/` and `site/app/equities/`, the new group in `site/app/board/` |
| F, personal laptop second window | 750 | `$HOME\Documents\erw-w2` | the browser read of everything landed; its fixes on branches `wip/c750-*` |

A window edits only what it owns. A fault found in another window's files is a row for that window, never an edit. `/impact` is window C's tonight and is not audited here.

## Rules

- **The rules of chain 610 hold word for word** (`queue/done/610-night-20-november-oldlaptop-weekend-pack-security.md`, and through it chains 590 and 507 and the owner's rules of 16 November as `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md` has them), with these changes:
- **Session numbers** 10200 to 10399, each checked free on origin/main and every branch first. The four-digit numbers are nearly all taken, so this run's are five digits.
- **This machine is short of memory:** no site build, no hourly table rebuilt, no timer or sleep that waits. A page is read by drawing its components to HTML with the site's own code (`site/scripts/tsx-loader.mjs`, as chain 302 did) and by reading its page files. A thing not ready is skipped and returned to.
- **This machine does not land and writes no warehouse table.** A branch for landing is one row marked requested in `docs/state/landing_request_oldlaptop.md`, which window A's desk lands. A measurement that needs a table this machine does not hold is one row marked requested in `docs/state/data_requests_five_tools.md` with exactly what to compute; the audit goes on without it and says so.
- **No ruling is taken for Samuel.** No default on main changes. No `wip/alt-*` or `wip/switch-*` branch is landed or requested for landing.
- **What an audit may land and what it may not** (Samuel's word of 26 November). A fix that changes only words, where the page or its note says something the code does not do, is made on its own branch with a test and its landing is requested. A fix that would move any figure a reader sees is NOT made on main: the finding gets a test that shows it, on its own branch, not requested, and one plain line for Samuel's ruling with the default "left as it is" and the size of the effect, measured.
- **An audit changes no draft's state.** No finding of Automated Analysis is approved, rejected, sent or posted; no caption; no LinkedIn work of any kind.
- **The rule against a session whose only output is a record does not apply to part A.**
- **Plain words, full addresses, no codes without their meaning, no em dashes.**
- **Never end idle.** After part C, part D, until the weekly limit.

## The start (session 10200, long end 0:20)

1. Precheck. `git fetch origin`, `main` at `origin/main`. Free memory written down.
2. This chain's file taken (`queue/next/710-...` to `queue/done/`), if the command that started the session has not already done it.
3. **Chain 610 is closed:** its part A was written on the personal laptop and its parts B to D in the desktop's third window on 20 November; its part E is replaced by this chain. `queue/next/611-resume-chain-610.md` (and any later number of it) is removed in one commit, with one line in `docs/state/progress_c610.md` saying so.
4. The resume file `queue/next/711-resume-chain-710.md`, committed alone and pushed, its text the lines between BEGIN and END below without those two words. A session that takes a resume file first writes the same text under the next number up (to 719), its machine line unchanged. The chain's last session removes it.
5. `docs/state/progress_c710.md`: one line a step, its state and session, pushed after each.

BEGIN
# Resume of chain 710

machine: samueloldlaptop

Chain 710 was interrupted. This file is the old laptop's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 719, named NNN-resume-chain-710.md, committed alone and pushed. Then read queue/done/710-night-26-november-oldlaptop-weekend-page-model-audits.md whole and docs/state/progress_c710.md, and continue chain 710 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: this weekend's page, `docs/reviews/weekend-2026-11-28.md` on main (a first version pushed within this chain's first two hours)

1. **What is read:** `docs/reviews/weekend-2026-11-21.md` whole (nothing in it was ruled; it is the base); every note under `docs/state/` since 20 November (chains 601, 610, 620 and 630, the data machine's daily notes); `docs/reviews/battery-model-audit-2026-11-20.md` and `docs/reviews/generator-model-audit-2026-11-20.md`; `docs/security.md` as it now stands; every landing request file for rows that say "ready, not requested"; and, as they appear tonight, the notes and progress files of chains 701, 730, 740, 720 and 750. A question asked in three notes is one line with its three sources. An item that has been settled or overtaken since 21 November is dropped, with a count of how many were dropped at the foot.
2. **The page is sized to his time, not to the pile.** Three tiers, each complete without the next, each with the minutes it takes:
   - **Thirty minutes:** the ten decisions that free the most machine work or fix the most visible wrong thing, each in three lines: the question in plain words, the two choices, what follows from each, and the default that applies if he says nothing.
   - **Two hours:** the rest of the rulings that move a figure, grouped so that one line rules a group, each group with the branch that is ready to land the minute he rules; the two model audits' findings as a list of "the page says, the model does, the choice"; the word-only audit branches of 20 November that wait only for his yes, as one line.
   - **The whole weekend:** the findings to approve (how to run the Stata files and approve at `/internal/findings`); the method notes that wait for his signature, one line a tool with its do-file; the licenses and what each costs; and what was built to look at.
3. **What was built, to look at:** every page and view landed since 17 November that he has not opened, by its full address (`https://erw-flame.vercel.app/...`), each checked against main before it is written, with what to click, step by step, and what he should see. The pages built tonight are added as they land, newest at the top of that section.
4. **The words to paste:** a template with blanks, tier by tier, that he fills and pastes to Claude in chat to rule on a whole tier in one message.
5. Short bullets throughout. No line he would have to read twice. Its first line says when it was written. **Kept current:** after each numbered step of parts B to D, until Saturday 28 November 10:00 PST, the page is brought up to date from the other windows' notes and landing files, and the time on its first line changed.

## Part B: "what a datacenter pays" audited as a hostile expert would (`docs/reviews/datacenter-model-audit-2026-11-26.md`)

In the form of `docs/reviews/battery-model-audit-2026-11-20.md`, read first. Read as the energy procurement lead of an AI lab who is choosing a site with this page and wants to find it wrong.

1. **The ground:** the page `/cost-of-power` and each of its views (Grid by grid, All grids, the siting card and the rest); the code that computes each figure, in the warehouse and in the site's own arithmetic; the notes (`docs/methods/datacenter_pays_algorithm.md`, `docs/methods/datacenter_cost.md`, the cross-check and decisions block); the replication; the page files and public files the page reads. Listed at the top of the audit with what each does.
2. **The arithmetic re-done:** every figure the default case prints is computed again from the page's own files by an independent restatement, and must come out to the digit. Then one rule changed at a time to measure what each of the model's choices is worth.
3. **Each claim the page and its hovers make, set against what the code does:** what "all-in" holds and leaves out (energy, capacity, transmission and delivery, ancillary services, losses, taxes and riders, demand charges); how the load's shape and its flexibility enter; day-ahead against real time; a hub's price against the price where the load would sit; how a contract or an own plant is priced against the market; whether "will it be there" and "how soon" are measured or asserted; how carbon is counted (average against marginal, the hour against the year); what a figure for a held grid rests on; whether the load's own effect on price is said plainly; the dollars' year; the window the figures cover and whether the page says it.
4. **What a procurement lead's own number would hold that this does not,** each with its size where it can be measured from files this machine holds.
5. **Each finding:** numbered, with its severity, a test that shows it on its own branch `wip/audit-datacenter-<n>`, and its fix by the rule above (words: landing requested; figures: for Samuel's ruling, with the measured effect).
6. **In short**, at the top: eight bullets at most, the first saying whether the arithmetic is right.

## Part C: Automated Analysis audited as a hostile econometrician would (`docs/reviews/analysis-model-audit-2026-11-26.md`)

The findings' sentences were audited on 19 November (`docs/reviews/findings-audit-2026-11-19.md`); this audit is of the engine under them, and does not repeat that one.

1. **The ground:** `/analysis`, the engine and its templates, the scanner and the findings pipeline (`docs/methods/automated_analysis.md`, `automated_analysis_scanner.md`, `automated_analysis_findings.md`), the code each names, and the forty shortlisted findings with their data.
2. **Each template's statistic re-done by hand on its own data** for at least one finding: does the code compute what the note says, to the digit.
3. **What an econometrician would attack:** a scanner that tries many cuts and keeps the striking ones (how many were tried for each kept, and is that said or corrected for); a comparison whose two periods differ in more than the thing named; a trend from too few points; an average that hides a few extreme days; a "since" whose start date was chosen after looking; a correlation worded as a cause; units and the dollars' year; a held grid's data reaching a finding; a regression's standard errors and what they assume about hours that follow one another. Each as a test on the engine, not a rewrite of a finding's words.
4. **Each finding of the audit:** as in part B. A draft finding that the audit shows to be wrong is listed by its number with the reason, its state untouched.
5. **In short**, at the top.

## Part D: after part C, until the weekly limit

- The same audit, in the same form, one tool a session, in this order: the Grid tool's figures (how interchange is netted, how carbon intensity is computed, what "now" means); the price board's computed columns; the severance tool. Not `/impact`, not `/forecast`, not the equities pages: they are being built tonight.
- For each audit branch that changes only words: its page drawn to HTML and read once more before its row is marked requested.
- Part A kept current, as its item 5 says.

## The last session

- `docs/state/note_2026-11-26_oldlaptop_c710.md` in short bullets: where the weekend page is and the minutes each tier asks; each audit in five lines (is the arithmetic right, the three worst findings, how many fixes were words and how many wait for a ruling); what waits for Samuel, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part D goes on.
