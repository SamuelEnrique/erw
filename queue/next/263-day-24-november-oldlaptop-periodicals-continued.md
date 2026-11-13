# Chain of 24 November 2026: sessions 3521 to 3536, samueloldlaptop (code role), unattended: chain 260's unfinished steps, the Daily Digest and the Weekly Roundup

machine: samueloldlaptop

Written first by session 3505 of chain 260 (`queue/done/260-day-23-november-oldlaptop-periodicals-continued.md`) on 13 November 2026 at about 21:35 UTC, as that chain's rules ask, and to be updated by its session 3520 with what chain 260 did not finish. The first queue number free on origin's main and every branch was 263 (261 and 262 are the portable laptop's). It takes sessions 3521 to 3536, sixteen numbers after chain 260's last (3520); none was named by a report, a commit subject or a queue file on origin's main or any branch when this was written. Session 3521 checks each is free again, skips a taken one upward and says so. The `machine:` line names this machine, not the role: portable-laptop, the second code machine, must never take this file. Model: Opus 5.5, high effort. Only one Claude Code window runs on this machine.

## Rules for every session

The rules of `queue/done/248-day-18-november-oldlaptop-periodicals-continued.md` hold word for word (chain 228's with its changes: no landing gate and no full test suite here, a landing request row instead; only the test files a change touches are run, which means every test file that imports or names the changed module, found by grep; no step waits on a landing; the grids view's public columns not touched; one window; no question asked; the weekly limit the only stop; a site build in the foreground and only with MemFree at 2.5 GB or more). Chain 219's addition holds too: if the list below is still empty when session 3521 starts, chain 260 stopped before its session 3520, and session 3521 rebuilds it from chain 260's report (`archive/sessions/SESSION_3505_REPORT.md`), its branches and its `runs/` folders, and says so.

Read first: chain 260's note (the name its session 3519 gave it), `docs/state/note_2026-11-13_oldlaptop_c258.md`, `docs/state/landing_request_oldlaptop.md` (the old laptop's rows), `docs/reviews/periodicals-faults-2026-11-05.md`, `docs/methods/digest_scoring.md`, `docs/methods/roundup_selection.md`, `docs/voice.md`, `CLAUDE.md`.

## Session 3521: the next file, the ground

Long end 1:00. The next file in `queue/next/` for this machine (the first queue number free on origin's main and every branch, `machine: samueloldlaptop`, at least fourteen sessions numbered from the first free numbers after 3536, this chain's unfinished steps first), committed alone and pushed. Then precheck, `git fetch origin`, disk and memory free, worktrees of landed branches removed (with their `.next` and `node_modules`), whether this machine's open landing row has landed, written to the report.

## Sessions 3522 to 3527: chain 260's unfinished steps

Long end 1:00 each. One step a session, in chain 260's order, as session 3520 lists them below. When the list is shorter, the free sessions take the periodicals below.

### Unfinished steps (written by session 3520 of chain 260)

(Session 3520 fills this list.)

## Sessions 3528 to 3534: the periodicals, again

Long end 1:00 each. The Daily Digest and the Weekly Roundup: every row of the faults file still open (a row whose state is `ruling` or `data machine` is skipped, said so), each fixed with a test on this chain's stack, every figure traced (`site/scripts/digest-figures.mjs --dir` with `scripts/check_digest.py`, `scripts/check_roundup.py --dir`); then the newest stored issues read as a reader against a dry run of the same hour on the stack, each new fault a numbered row, fixed the same way. Dry runs only (`--no-model` unless the model's output is the point, under USD 2 a session): no email sent, no stored issue rewritten. When the stack is ready, its landing request row.

## Session 3535: the records and the note

Long end 1:00. The records and the note (`docs/state/note_<date>_oldlaptop.md` or a suffixed name, checked free first, short bullets: what landed, what waits in which landing row, what waits for Samuel with defaults).

## Session 3536: the next file, the queue

Long end 1:00. The next file (written by session 3521) updated with what this chain did not finish, pushed; then the queue step: `.venv\Scripts\python.exe scripts\chain_queue.py next`, and run whatever it prints the same way.
