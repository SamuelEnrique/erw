# Chain of 16 November 2026: sessions 7000 to 7049, data machine (lab-desktop), unattended: the open data faults of ten tools, the large-load waits brought current, three replication mirrors

machine: data

Written by Claude in chat with Samuel on 16 November 2026, from a read of origin/main at `f0360123` and of every branch. It is not a machine's successor file, and no machine writes a successor to it (rule 3). Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. One Claude Code session on the desktop. Sized for about 30 hours.

## Why this chain

From Saturday 14 November 16:57 PST to Sunday 15 November 22:56 PST the desktop spent about 26 of 30 hours on empty "waiting" commits, while 37 rows marked `data machine` stood open in the tools' faults files. Each of those rows is a wrong, missing or stale figure on a page Samuel shows to funds, developers and AI labs. This chain closes them, brings the large-load waits (the dataset no one else publishes) up to date, and gives three more tools a replication mirror. Every step moves a page or a table a reader sees.

## The owner's rules of 16 November 2026 (they win over anything older, in this file or any file it names)

1. **Model spend USD 0.** The owner's Anthropic API key is at its limit until 1 December and he is not raising it. No session runs any script that calls a model: no extraction, no scoring, no Digest, no Roundup, no chat, no evaluation, no Thesis Builder, no backfill. Set `ERW_SPEND_CAP_USD=0` in the session's environment. A step that cannot be done without a model call is not run: it goes under "Needs the key" in the report and the progress file, with one line on what it would do and its estimated cost in US dollars. No other key or route is tried.
2. **No waiting.** Never wait on a time of day, a scheduled run, a date, a publisher or Samuel. A step that needs something not yet here is marked waiting in the progress file and skipped; the session takes the next step at once and returns to the skipped one only when it starts a later session and finds the thing has come. A commit that says only "waiting" is a fault of this chain. Never stop to ask: a reversible choice goes under "Decisions made without you", the rest under "For Samuel's ruling", each with the default taken, in plain words (no item codes without their meaning).
3. **No machine writes a chain.** No session writes a successor file, a "continued" file or any new goals. The goals are in this file alone. The one file a session may put in `queue/next/` is the resume pointer of the section "Restart safety", with its text exactly as given there.
4. **No redundant work.** Before each row or step, check whether it is already done on origin/main and in the live set, and say what was checked. Not in this chain: re-reading `docs/reviews/siting-gaps.md` (its open rows are held by terms; the one dated read is in goal 3); rebuilding or re-extracting `datacenter_projects`, `energy_deals` or `news_index` (not while the key is closed; the load's guard stands); a session whose only output is a note, a record or a count; reading the daily runs for their own sake.
5. **Paused or out of bounds.** No work on the Digest's or the Roundup's writing (the news is paused this week). No LinkedIn work of any kind. Nothing is sent, posted or published. `site/lib/release.ts` is not touched and no page opens to visitors. Nothing is released on Redivis (the release is Samuel's click).
6. **The landing desk.** At the start of every session: `git fetch`, then every `docs/state/landing_request_*.md` read for rows marked requested, each landed in order of request through `scripts/land_check.py`, as chain 267 did. The old laptop and the portable laptop cannot land; this machine lands for them. Then every row marked requested since 16 November in `docs/state/data_requests_*.md` (the laptops' chains 302 and 303 ask there for a table loaded or a builder run), done under the data lock in order of request. A desk with nothing requested takes two lines of the report and no more.
7. **Procedures by reference, goals from here.** How to land, the data lock, the gates, the snapshots, the worktrees, the pulls' probe of robots and terms, and the hours with no landing (14:00 to 16:15 UTC) are as in `CLAUDE.md` and `queue/done/267-day-21-november-data-continued.md`. Where they differ from this file, this file wins. Before removing a worktree, list its ignored files. Never force a push.
8. **The worker's clock.** The chain worker closes a session that shows no commit for 30 minutes. While a long step runs (a gate's suite, a pull, a build), commit real partial work at least every 25 minutes; an empty commit is allowed only while a named long step is running, and its message names that step.
9. **Reports.** One report a session, `archive/sessions/SESSION_<N>_REPORT.md`, short bullets: what a reader of the page now sees that was wrong before (the figure before and after), each commit, each row's new state, "Needs the key", "Decisions made without you", "For Samuel's ruling". No em dashes anywhere.
10. **Session numbers.** 7000 to 7049, each checked free on origin/main and every branch before it is used; a taken one is skipped upward and said so.

## Restart safety

- Session 7000 writes `queue/next/310-resume-chain-301.md`, commits it alone and pushes it. Its whole text is the block below, unchanged.
- A session started by the chain worker that takes a resume file first writes the same block again under the next number up (311, then 312, to 319), commits and pushes it, then does what the block says.
- The chain's last session removes the resume file from `queue/next/` (one commit) before its queue step.

```
# Resume of chain 301

machine: data

Chain 301 was interrupted. First put this same text back in queue/next/ as the next number up to 319, named NNN-resume-chain-301.md, committed alone and pushed. Then read queue/done/301-day-16-november-desktop-open-faults.md whole and docs/state/progress_c301.md, and continue chain 301 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
```

## The progress file

`docs/state/progress_c301.md`, started by session 7000 and pushed after every row: one line a row or step, with its state (`done` with the commit, `not a fault now` with what was checked, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for) and the session. It is the only record a restarted session needs.

Read first: `CLAUDE.md`, `docs/state/note_2026-11-15_data_c279.md`, `docs/state/rulings_2026-11-06.md` and any newer rulings file, the faults files named in goal 1.

## Session 7000: the ground (long end 0:45)

- Precheck; `git fetch`; memory and disk; worktrees of landed branches removed (ignored files listed first).
- Park the machines' own files, one commit, pushed: `queue/next/286-day-26-november-data-continued.md`, `queue/next/284-day-18-november-oldlaptop-ask-continued.md` and `queue/next/300-day-26-november-oldlaptop-periodicals-continued.md` moved to `queue/parked/`. Remove any `*-resume-chain-*` file of the data machine from `queue/next/`.
- The resume file and the progress file, as above. The landing desk.
- Then goal 1 at once, in the same session.

## Goal 1: every open `data machine` row of the faults files (sessions 7001 onward, one tool a session or two)

The 37 rows, in this order:

| Tool and page | Faults file in `docs/reviews/` | Rows |
|---|---|---|
| Deal tracker `/deals` | `deals-faults-2026-11-11.md` | 9, 10, 11, 12, 13 |
| Datacenter tracker `/datacenters` | `datacenter-faults-2026-11-11.md` | 8 |
| Companies `/companies` | `companies-faults-2026-11-11.md` | 17, 18, 19, 20, 21, 22, 23, 24 |
| Policy monitor `/policy` | `policy-faults-2026-11-11.md` | 5, 7, 12, 13, 15, 18, 25 |
| Attention `/attention` | `attention-faults-2026-11-11.md` | 2, 7, 15, 16, 17, 18, 20 |
| Battery | `battery-faults-2026-11-13.md` | 7, 10 |
| Generator | `generator-faults-2026-11-13.md` | 2 |
| Grid | `grid-faults-2026-11-13.md` | 2 |
| Datacenter cost | `datacenter-cost-faults-2026-11-13.md` | 4 |
| Digest and Roundup (data only) | `periodicals-faults-2026-11-05.md` | 48, 61, 77, 129 |

For each row:

- **Check first.** Read the row, then today's origin/main and the live set: is the fault still there? The rows were written on 11 to 13 November, when main had been red since 6 November; some may have closed with the daily run of 15 November. A row already right is marked `not a fault now` with the figure read and where.
- **Fix at the cause** in the data code (the connector, the derived builder, the page-file builder), with a test that fails before and passes after. Never in the page file by hand.
- **Rebuild and load** what the fix touches, under the data lock, validated, archived, coverage rebuilt. No pull from a new host without its robots file and terms read first.
- **A row that needs a model call** (the deals' re-extraction with the v2 prompt is one; decide the others by reading the code) is not run: `needs the key`, with the estimated cost, and what a reader sees until then.
- **Land** each tool's stack through the gate when its rows are done, then read the page on production with the internal cookie and write the figure before and after in the report. Mark the row in its faults file: `fixed (<commit>)`.
- **A site change the fix needs** (a hover, a column the page must read) is not made here: one row in `docs/state/data_ready_c301.md` for the code machines, naming the file and field now carried.

The laptops add rows tonight: any row marked `data machine` that appears after 16 November in the two tracker faults files or in `docs/reviews/allgrids-read-2026-11-16.md` is taken the same way, at the start of the next session.

Done when all 37 rows and every row added since are `fixed`, `not a fault now`, `needs the key` or `ruling`, and each tool's page has been read on production after its landing.

## Goal 2: the large-load waits, current and with a public summary (about four sessions)

The table `large_load_waits` (internal, 2,622 rows, method `docs/methods/large_load_waits.md`, summary `docs/accelerator/large_load_waits.md`) was last built on 9 October 2026.

- **Current.** For each of the six publishers already followed (New York ISO, Grant County PUD, ERCOT, Bonneville, Alberta, ISO New England): the dated copies published since the last one held, under the same rule and labels. Ceilings for this goal in all: 300 requests and 1 GB. Each host's robots file and terms read again first; a publisher held or paused in `docs/licenses.md` or `warehouse/metadata/paused_sources.csv` is not pulled. The table rebuilt; the counts before and after in the report.
- **More publishers.** From `docs/research/large_load/utilities_2026-11-13.csv` (the 35 rows that point to a queue figure) and its notes files: any utility or operator that publishes dated copies of a list of load requests with its own identifiers is followed by the same rule. One that prints only a total is kept as a dated total in a new table `utility_large_load_queue_totals` (one row a publisher and date, the figure as printed, its document cited), public where its terms allow, internal with the reason where they do not.
- **The public summary.** A derived table `large_load_wait_summary`: by publisher and interval, the count of requests, the measured range of the median in days, and the lower bounds counted apart, with no request named and no megawatt of a request. Public only for a publisher whose terms allow derived statistics, the verdict written beside each from its terms word for word; where the terms are unclear the rows stay internal and the question goes under "For Samuel's ruling" with that default. Validated, in coverage, with its method note.
- **For the code machines:** one row in `docs/state/data_ready_c301.md` saying the summary exists and which column of the All grids tab ("Time to connect") it can fill.

Done when the table is rebuilt with every new copy, each new publisher is followed or written down with the reason it cannot be, and the summary table is in coverage with a license verdict for every publisher.

## Goal 3: one dated read (inside any session, ten minutes, never waited on)

- The CAISO's FERC compliance filing on large loads, due 16 November 2026: when a session starts and the filing is on the CAISO's process page, read it once, add its timed steps to the large-load rules, and write one dated section in `docs/reviews/siting-gaps.md`. Not filed: skipped, checked again only at the start of a later session. No other row of that file is read again.

## Goal 4: replication mirrors for three more tools (two sessions a tool)

The five tools of roadmap item 2 each have `replication/<tool>/replicate.py`: an independent script that recomputes every figure the page shows from the public tables and compares. Companies, the policy monitor and attention have none. (The datacenter tracker and the deal tracker are the portable laptop's this week; do not take them.)

For `/companies`, then `/policy`, then `/attention`:

- `replication/<tool>/replicate.py`, written from the method note and the tables alone, not from the page builder's code: every figure of the page files recomputed, N of N compared, a held table read only where the page itself may show it.
- Each mismatch is a new row in the tool's faults file and is fixed as in goal 1.
- A Stata do-file beside it that reproduces the tool's five headline figures, with the expected values at its top (Samuel runs Stata himself).
- The method note in `docs/methods/` brought to the pages as they now stand.

Done when each of the three prints N of N, or every mismatch is fixed or written as `needs the key` or `ruling`.

## If goals 1 to 4 are done and no new file waits

Take goal 4's work for the next tool in the site's menu order that has no folder under `replication/`, one tool at a time, until a new chain file is in `queue/next/`. Never a waiting commit, never a file of new goals.

## The last session

- The progress file complete; `docs/state/note_2026-11-17_data_c301.md` in short bullets: what a reader now sees right that was wrong, by tool; what needs the key, with the costs summed; what waits for Samuel, each with its default.
- This chain's branch landed through the gate (never between 14:00 and 16:15 UTC).
- The resume file removed from `queue/next/`; then `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. Exit 3: run the precheck again (the queue step takes the machine off duty), continue with the section above, and run the queue step again at the end of each tool.
