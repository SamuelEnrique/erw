# Chain of 16 November 2026: sessions 7050 to 7149, data machine (lab-desktop), unattended: the laptops' data requests as they come, then the desktop's eight tools read as their reader

machine: data

Written by Claude in chat with Samuel on 16 November 2026 at about 02:40 PST. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. One Claude Code session. It is taken by chain 301's own queue step when chain 301 has finished its goals and its eight tools of `docs/state/done_line_claims.md`; it does not interrupt chain 301.

## Why this chain

Tonight the two laptops take sixteen tools to the done line and read each as its reader (chains 304 and 305). Every data fault they find is a row for this machine: by 02:10 PST the old laptop alone had filed twelve (rows 18 to 29 of `docs/state/data_requests_large_load.md`), and their stacks wait on this machine's desk to land. A fault found and not fixed is still on the page. This chain keeps the desk and the requests moving all day, and in between gives this machine's own eight tools the reader's read the laptops give theirs.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10: model spend USD 0 and what "Needs the key" means; no waiting, and a "waiting" commit is a fault; no machine writes a chain; no redundant work; nothing published, no LinkedIn, no Redivis release, no hold lifted; the landing desk and the data requests at the start of every session; procedures by reference; the worker's clock; reports), with these changes:
- **Session numbers** 7050 to 7149, each checked free first (chain 301 may have used some: skip upward and say so).
- **The data lock is never waited on.** If another process of this machine holds it, find which (`scripts/` lock status), and if it is a finished or dead process's, say so and clear it as `CLAUDE.md` allows; otherwise take the next step that needs no lock and come back.
- **The page standard** is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`.
- **No duplicate of a laptop's tool:** `docs/state/done_line_claims.md` is read before any tool is started.
- **Never end idle.** When part B is done and no new chain file waits, part C; the queue step is run at the end of each tool of part C.

## Restart safety and the progress file

- The first session writes `queue/next/380-resume-chain-370.md` (the block below, unchanged), committed alone and pushed, and removes any other `*-resume-chain-*` file of the data machine from `queue/next/`; a session that takes a resume file first writes the same block under the next number up (to 389); the chain's last session removes it.
- `docs/state/progress_c370.md`: one line a request, landing or tool, its state and session, pushed after each.

```
# Resume of chain 370

machine: data

Chain 370 was interrupted. First put this same text back in queue/next/ as the next number up to 389, named NNN-resume-chain-370.md, committed alone and pushed. Then read queue/done/370-day-16-november-desktop-requests-and-reads.md whole and docs/state/progress_c370.md, and continue chain 370 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
```

## Part A: the desk and the requests (the start of every session, before anything else)

- **Land** every row marked requested in `docs/state/landing_request_*.md`, in order of request, through the gate (never between 14:00 and 16:15 UTC). After each landing, read the changed pages on production with the internal cookie at 1280 and 390 px and write in the report what a reader now sees; a row of `docs/state/browser_reads_wanted.md` that the landing makes readable is read here too if the portable laptop has not marked it.
- **Do** every row marked requested in `docs/state/data_requests_*.md` since 16 November, in order of request: the table loaded to the live set, the builder run under the data lock, the figure corrected at its cause with a test, validated, archived, coverage rebuilt. A row that needs a model call is `needs the key` with its cost. A row a license or a ruling stops is written with the default taken.
- **Fix** every row marked `data machine` in any `docs/reviews/*-faults-2026-11-16.md` and `*-read-2026-11-16.md` file, the same way, and mark it `fixed (<commit>)`.
- Nothing requested: two lines of the report, then part B.

## Part B: this machine's eight tools read as the reader they are for (about 40 minutes a tool)

`/board`, `/prices`, `/prices/compare`, `/supply`, `/storage`, `/demand`, `/curtailment`, `/queues`, each after its done line of chain 301's last section is finished (a tool whose done line is not yet done gets that first, in chain 301's form).

- As chain 302's read of the All grids tab (`docs/reviews/allgrids-read-2026-11-16.md`): five real cases a named reader would bring, written first in three lines, each taken start to finish on the built page. The readers here are a power trader, a gas analyst, a storage developer and a utility planner: named hubs, named days, real sizes (the day-ahead against real-time spread at HB_WEST on the days of the January 2026 cold; what curtailment did to midday prices in CAISO in May 2026; how much storage came online in ERCOT in 2026 against the queue).
- Can the reader get the answer without leaving the page, without a figure that contradicts another page or the warehouse table behind it, and without a word they would not know? Each gap is a numbered row in `docs/reviews/<tool>-read-2026-11-16.md`.
- Every fault is fixed at its cause with a test (this machine holds the data and lands its own code); a gap only a license, the key or a ruling closes is written as such, with the default.
- Two pages that share a figure must agree: each disagreement is a row and is fixed at its cause.

## Part C: if parts A and B are done and no new file waits

Part A again at the start of each session. Then part B's read for the tools marked `done line` in the claims file that have no `docs/reviews/<tool>-read-2026-11-16.md` on any branch and are not marked `read:` by a laptop, one tool at a time, the claims file marked `read: lab-desktop` first. The queue step after each tool.

## The last session

- `docs/state/note_2026-11-17_data_c370.md` in short bullets: every landing with what a reader now sees, every request done, by tool what the reads found and fixed, what needs the key with the costs summed, what waits for Samuel with defaults.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. Exit 3: run the precheck again and go on with part C.
