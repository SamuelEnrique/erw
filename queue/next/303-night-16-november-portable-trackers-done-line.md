# Chain of the night of 16 November 2026: sessions 7400 to 7429, portable-laptop (code role), unattended, about 12 hours: the datacenter tracker and the deal tracker taken to the five tools' done line

machine: portable-laptop

Written by Claude in chat with Samuel on 16 November 2026, from a read of origin/main at `f0360123` and of every branch. It is not a machine's successor file, and no machine writes a successor to it (rule 3). Folder: `$HOME\Documents\erw`. Model: Fable, high effort. One Claude Code session. This laptop runs at night only: when the two goals are done the chain ends, and nothing is queued after it.

## Why this chain

The five tools of roadmap item 2 (battery, generator, datacenter cost, Automated Analysis, Grid) each reached a done line on 14 November: a complete method note, a replication that reproduces every figure of the page, a cross-check against published figures, a decisions block, and a signature pack Samuel can sign in one sitting. The datacenter tracker (`/datacenters`, master plan tool 4: the dataset AI labs and their investors ask for most) and the deal tracker (`/deals`, tool 6) had a faults read on 11 November and nothing more. This chain takes those two to the same line, so that Samuel can say of each figure on them where it came from and what it was checked against.

## The owner's rules of 16 November 2026 (they win over anything older, in this file or any file it names)

1. **Model spend USD 0.** The owner's Anthropic API key is at its limit until 1 December and he is not raising it. No session runs any script that calls a model: no extraction, no re-extraction of deals or datacenters, no scoring, no chat, no evaluation. Set `ERW_SPEND_CAP_USD=0` in the session's environment. A step that cannot be done without a model call is not run: it goes under "Needs the key" in the report and the progress file, with one line on what it would do and its estimated cost in US dollars. No other key or route is tried.
2. **No waiting.** Never wait on a time of day, a scheduled run, a landing, the data machine or Samuel. A step that needs something not yet here is marked waiting in the progress file and skipped; the session takes the next step at once. A commit that says only "waiting" is a fault of this chain. Never stop to ask: a reversible choice goes under "Decisions made without you", the rest under "For Samuel's ruling", each with the default taken, in plain words (no item codes without their meaning).
3. **No machine writes a chain.** No session writes a successor file, a "continued" file or any new goals. The one file a session may put in `queue/next/` is the resume pointer of the section "Restart safety", with its text exactly as given there.
4. **No redundant work.** The faults read of 11 November is not done again: `docs/reviews/datacenter-faults-2026-11-11.md` and `docs/reviews/deals-faults-2026-11-11.md` are the ground, and a row marked `not a fault` or `fixed` there is not reopened without a figure that shows it wrong. The method notes that exist are completed, not rewritten. Before each step, check whether it is already on origin/main and say what was checked.
5. **Paused or out of bounds.** No LinkedIn work of any kind. No Digest or Roundup work. Nothing is sent, posted or published. `site/lib/release.ts` is not touched and no page opens to visitors. **The license holds stand:** `energy_deals`, `datacenter_projects` and `news_index` are held whole ("license needed", since 21 October); no hold is lifted, switched off or worked around. The rows are read through the pages' own functions on the live set's rows, as session 1851 read them.
6. **This machine does not land and writes no warehouse table.** No landing gate and no full suite here: the test files a change touches (every test file that imports or names the changed module, found by grep), then a row in `docs/state/landing_request_portable.md` for the data machine's desk. A site build only in the foreground and only with 2 GB of memory free. **The data machine is fixing these two tools' data faults tonight** (chain 301: deals rows 9 to 13, datacenter row 8): do not edit a connector, an extraction or a derived builder. A data fault found here is a new row marked `data machine` in the tool's faults file, and the work goes on.
7. **Procedures by reference, goals from here.** How a chain works on this laptop is as in `CLAUDE.md` and `queue/done/269-night-14-november-portable-p1-closeout.md`; the done line's form is that chain's (`docs/state/note_2026-11-14_portable_p1.md`, `docs/reviews/five-tools-signature-pack-2026-11-14.md`, `replication/battery/`). Where they differ from this file, this file wins. Never force a push.
8. **The worker's clock.** If a chain worker runs on this laptop it closes a session that shows no commit for 30 minutes. Commit real partial work at least every 25 minutes; an empty commit is allowed only while a named long step is running, and its message names that step.
9. **Web reads for the cross-checks:** each host's robots file and terms read first; a host that refuses is not read and is named. No figure is taken from a page that could not be read; a cross-check with no public figure to stand against says so.
10. **Reports.** One report a session, `archive/sessions/SESSION_<N>_REPORT.md`, short bullets. "Needs the key", "Decisions made without you", "For Samuel's ruling". No em dashes anywhere.
11. **Session numbers.** 7400 to 7429, each checked free on origin/main and every branch before it is used; a taken one is skipped upward and said so.

## Restart safety

- Session 7400 writes `queue/next/330-resume-chain-303.md`, commits it alone and pushes it. Its whole text is the block below, unchanged.
- A session started by a chain worker that takes a resume file first writes the same block again under the next number up (331, then 332, to 339), commits and pushes it, then does what the block says.
- The chain's last session removes the resume file from `queue/next/` (one commit).

```
# Resume of chain 303

machine: portable-laptop

Chain 303 was interrupted. First put this same text back in queue/next/ as the next number up to 339, named NNN-resume-chain-303.md, committed alone and pushed. Then read queue/done/303-night-16-november-portable-trackers-done-line.md whole and docs/state/progress_c303.md, and continue chain 303 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
```

## The progress file

`docs/state/progress_c303.md`, started by session 7400 and pushed after every step: one line a step, with its state (`done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for) and the session.

Read first: `CLAUDE.md`, the two faults files, `docs/methods/datacenter_projects.md`, `docs/methods/datacenter_facilities.md`, `docs/methods/datacenter_operator_sites.md`, `docs/methods/datacenter_tracker_rollups.md`, `docs/methods/ercot_large_load_status.md`, `docs/methods/energy_deals.md`, `docs/methods/deal_counterparties.md`, `docs/reviews/five-tools-signature-pack-2026-11-14.md`.

## Session 7400: the ground (long end 0:30)

- Precheck; `git fetch`; memory and disk; worktrees of landed branches removed (ignored files listed first). Remove any `*-resume-chain-*` file of this machine from `queue/next/`.
- The resume file and the progress file. Then goal 1 at once, in the same session.

## Goal 1: the datacenter tracker, `/datacenters` (about six hours)

Each of the five parts below is done to the form the battery tool's has.

- **The method note, complete:** one note for the tool as a reader meets it (`docs/methods/datacenter_tracker.md`, pointing to the tables' own notes, not repeating them): every view of the page, every figure's table and rule (what counts as a facility, as operating, as planned; how MW is read when a story gives a range; how a facility is placed on a grid; how the ERCOT large-load section and the queue sites are built), and what the tracker does not hold.
- **The replication:** `replication/datacenter_tracker/replicate.py`, written from the method note and the rows alone, not from the page's code: every figure the page shows recomputed (the totals, the by-operator, by-grid and by-region tables, the timeline, the shares, the rollups), N of N compared, each difference inside half the page's last shown digit or named. A Stata do-file beside it that reproduces the tool's five headline figures, with the expected values at its top.
- **The cross-check:** the tracker's totals beside the figures a lab's or a fund's reader would know, each with its publisher, document and date: Lawrence Berkeley National Laboratory's datacenter energy report, the EIA's figures, ERCOT's own large-load status totals, the grid operators' load forecasts, the largest utilities' stated contracted and pipeline megawatts. One table: ours, theirs, the difference, and why they differ (definition, date, what each counts). No figure adjusted to match.
- **The decisions block on the page:** the handful of choices that move the tracker's figures (the same form as the five tools': each choice, its default, its source, on hover), drawn where the battery page draws its own.
- **The faults this work finds:** a site fault fixed with a test; a data fault a new row marked `data machine`; the four rows marked `ruling` restated in plain words with their defaults for the signature pack.

Done when the replication prints N of N or names every difference, the cross-check table stands with its sources, the note and the decisions block are on the stack, and the stack has a landing request row.

## Goal 2: the deal tracker, `/deals` (about five hours)

The same five parts, for `/deals` and its views (the table, the tracker tab, comparables, the AI view, the charts) and `/deals/capital`.

- **The method note** (`docs/methods/deal_tracker.md`): what a deal is and is not (the rule that a deal is energy's where the asset is energy), how two stories of one deal are folded, how MW, US dollars and price are read and when they are left empty, how the medians of the comparables are taken and on how many deals, how a deal is tagged AI power, what the "Sure" column means.
- **The replication** (`replication/deals/replicate.py` and its do-file): every count, median, share and top-ten of every view recomputed from the rows, N of N.
- **The cross-check:** the tracker's counts and megawatts by year and kind beside published tallies of power purchase agreements and datacenter power deals, each with its publisher and date, and the twenty largest rows each against its own story's headline figure (session 1851 did this for twenty on 5 November's rows: do it for the rows as they stand now, and only the ones that changed).
- **The decisions block on the page**, and the faults as in goal 1 (the three rows marked `ruling` restated in plain words with their defaults).
- **What the re-extraction would change** is not run (rule 1): under "Needs the key", how many of the 529 rows the stricter rule would drop or reclass by this session's own reading of their stories' titles, and the estimated cost of the run.

Done as goal 1.

## The last session

- **The signature pack for the two trackers:** `docs/reviews/trackers-signature-pack-2026-11-16.md`, in the five tools' pack's form: per tool, what Samuel signs, the five choices that matter most with their defaults and sources, the cross-check in one table, the Stata commands with what each should print. One sitting.
- The progress file complete; `docs/state/note_2026-11-17_portable_c303.md` in short bullets: each tool against its done line, what needs the key with the costs summed, what waits for Samuel with defaults.
- The landing request row for the final stack; the resume file removed from `queue/next/`.
- Then `.venv\Scripts\python.exe scripts\chain_queue.py next`. Exit 3 is expected: say "CHAIN DONE" and stop. If goal 2 ends with hours of the night left, take the same five parts for `/companies` only if `replication/companies/` does not exist on origin/main and no branch of the data machine holds it; otherwise stop.
