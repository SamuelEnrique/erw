# Chain of 20 November 2026: sessions 3456 to 3471, samueloldlaptop (code role), unattended: chain 251's unfinished steps, the Daily Digest and the Weekly Roundup

machine: samueloldlaptop

Written first by session 3440 of chain 251 (`queue/done/251-day-19-november-oldlaptop-periodicals-continued.md`) on 13 November 2026 at about 13:55 UTC, as that chain's rules ask, and to be updated by its session 3455 with what chain 251 did not finish. The first queue number free on origin's main and every branch was 252. It takes sessions 3456 to 3471, sixteen numbers after chain 251's last (3455); none was named by a report, a commit subject or a queue file on origin's main when this was written (3500 is a backfill report's). Session 3456 checks each is free again, skips a taken one upward and says so. The `machine:` line names this machine, not the role: portable-laptop, the second code machine, must never take this file. Model: Opus 5.5, high effort. Only one Claude Code window runs on this machine.

## Rules for every session

The rules of `queue/done/248-day-18-november-oldlaptop-periodicals-continued.md` hold word for word (chain 228's with its changes: no landing gate and no full test suite here, a landing request row instead; only the test files a change touches are run, which means every test file that imports or names the changed module, found by grep; no step waits on a landing; the grids view's public columns not touched; one window; no question asked; the weekly limit the only stop; a site build in the foreground and only with MemFree at 2.5 GB or more).

Read first: chain 251's note (the name its session 3454 gave it), `docs/state/landing_request_oldlaptop.md` (row 10), `docs/reviews/periodicals-faults-2026-11-05.md`, `docs/methods/digest_scoring.md`, `docs/methods/roundup_selection.md`, `docs/voice.md`, `CLAUDE.md`.

## Session 3456: the next file, the ground

Long end 1:00. The next file in `queue/next/` for this machine (the first queue number free on origin's main and every branch, `machine: samueloldlaptop`, at least fourteen sessions numbered from the first free numbers after 3471, this chain's unfinished steps first), committed alone and pushed. Then precheck, `git fetch origin`, disk and memory free, worktrees of landed branches removed (with their `.next` and `node_modules`), whether row 10 has landed, written to the report.

## Sessions 3457 to 3462: chain 251's unfinished steps

Long end 1:00 each. One step a session, in chain 251's order, as session 3455 lists them below. When the list is shorter, the free sessions take the periodicals below.

### Unfinished steps (written by session 3455 of chain 251)

(Session 3455 fills this list.)

## Sessions 3463 to 3469: the periodicals, again

Long end 1:00 each. The Daily Digest and the Weekly Roundup: every row of the faults file still open (a row whose state is `ruling` or `data machine` is skipped, said so), each fixed with a test on this chain's stack, every figure traced (`site/scripts/digest-figures.mjs --dir` with `scripts/check_digest.py`, `scripts/check_roundup.py --dir`); then the newest stored issues read as a reader against a dry run of the same hour on the stack, each new fault a numbered row, fixed the same way. Dry runs only (`--no-model` unless the model's output is the point, under USD 2 a session): no email sent, no stored issue rewritten. When the stack is ready, its landing request row.

## Session 3470: the records and the note

Long end 1:00. The records and the note (`docs/state/note_<date>_oldlaptop.md` or a suffixed name, checked free first, short bullets: what landed, what waits in which landing row, what waits for Samuel with defaults).

## Session 3471: the next file, the queue

Long end 1:00. The next file (written by session 3456) updated with what this chain did not finish, pushed; then the queue step: `.venv\Scripts\python.exe scripts\chain_queue.py next`, and run whatever it prints the same way.
