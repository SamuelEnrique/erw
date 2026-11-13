# Chain of 23 November 2026: sessions 3505 to 3520, samueloldlaptop (code role), unattended: chain 258's unfinished steps, the Daily Digest and the Weekly Roundup

machine: samueloldlaptop

Written first by session 3488 of chain 258 (`queue/done/258-day-22-november-oldlaptop-periodicals-continued.md`) on 13 November 2026 at about 20:50 UTC, as that chain's rules ask, and to be updated by its session 3504 with what chain 258 did not finish. The first queue number free on origin's main and every branch was 260 (259 is the portable laptop's). It takes sessions 3505 to 3520, sixteen numbers after chain 258's last (3504); none was named by a report, a commit subject or a queue file on origin's main or any branch when this was written. Session 3505 checks each is free again, skips a taken one upward and says so. The `machine:` line names this machine, not the role: portable-laptop, the second code machine, must never take this file. Model: Opus 5.5, high effort. Only one Claude Code window runs on this machine.

## Rules for every session

The rules of `queue/done/248-day-18-november-oldlaptop-periodicals-continued.md` hold word for word (chain 228's with its changes: no landing gate and no full test suite here, a landing request row instead; only the test files a change touches are run, which means every test file that imports or names the changed module, found by grep; no step waits on a landing; the grids view's public columns not touched; one window; no question asked; the weekly limit the only stop; a site build in the foreground and only with MemFree at 2.5 GB or more). Chain 219's addition holds too: if the list below is still empty when session 3505 starts, chain 258 stopped before its session 3504, and session 3505 rebuilds it from chain 258's report (`archive/sessions/SESSION_3488_REPORT.md`), its branches and its `runs/` folders, and says so.

Read first: chain 258's note (the name its session 3503 gave it), `docs/state/note_2026-11-13_oldlaptop_c254.md`, `docs/state/landing_request_oldlaptop.md` (the old laptop's rows), `docs/reviews/periodicals-faults-2026-11-05.md`, `docs/methods/digest_scoring.md`, `docs/methods/roundup_selection.md`, `docs/voice.md`, `CLAUDE.md`.

## Session 3505: the next file, the ground

Long end 1:00. The next file in `queue/next/` for this machine (the first queue number free on origin's main and every branch, `machine: samueloldlaptop`, at least fourteen sessions numbered from the first free numbers after 3520, this chain's unfinished steps first), committed alone and pushed. Then precheck, `git fetch origin`, disk and memory free, worktrees of landed branches removed (with their `.next` and `node_modules`), whether this machine's open landing row has landed, written to the report.

## Sessions 3506 to 3511: chain 258's unfinished steps

Long end 1:00 each. One step a session, in chain 258's order, as session 3504 lists them below. When the list is shorter, the free sessions take the periodicals below.

### Unfinished steps (written by session 3504 of chain 258)

Chain 258 ran all its sessions and added rows 180 to 185. Row 11 (`wip/3457-periodicals`) has landed rows 151 to 171 (`f71fda27e`, `ad7f16ca6`); rows 172 to 185 wait at head `f2ebae979` (merged with main as `7028d48ce`). The note is `docs/state/note_2026-11-13_oldlaptop_c258.md`. Every stored issue has been read against the stack, so new faults will come from the next issues written. What it did not reach, in this order (the first two are written after this file; a session that starts before them takes the periodicals below and comes back to them):

1. (Session 3506) The W46 Roundup as stored (Sunday 15 November, 23:00 UTC) read as a reader against a dry run of the same hour on the stack (`--no-model`; the worktree `erw-3457` needs `policy_actions.csv` and `policy_reads.csv` copied from the main copy after `scripts/sync.py --tables` restores them, and the run's own `energy_deals.csv` and `datacenter_projects.csv` swapped in, then checked out again). Each new fault is a numbered row from 186. Before it is written, skip it and say so.
2. (Session 3507) Whether `wip/red-daily-2026-11-13` (the 13 November Digest) has landed, and the Digest of 16 November (Monday, after the daily run) as stored against the stack's dry run: its window should open at 13 November 16:01 UTC if the red branch landed, else at 12 November 22:56 UTC, which would repeat 13 November's items (said so if it does). Before it is written, skip it and say so.
3. (Session 3508) If row 11 has landed in full: the clean-up. Remove the worktree `erw-3457` with its `site/.next` and `site/node_modules` (untracked copies of `.env`, `site/.env.local`, the 13 November fun fact item and two ignored tables, none to keep), delete `wip/3457-periodicals` on origin, and mark row 11 landed. If not, skip it and say so.
4. Rows 39, 65 and 109 and rulings item 13 stay the owner's; rows 61, 77 and 129 the data machine's. The note lists what waits for Samuel.

## Sessions 3512 to 3518: the periodicals, again

Long end 1:00 each. The Daily Digest and the Weekly Roundup: every row of the faults file still open (a row whose state is `ruling` or `data machine` is skipped, said so), each fixed with a test on this chain's stack, every figure traced (`site/scripts/digest-figures.mjs --dir` with `scripts/check_digest.py`, `scripts/check_roundup.py --dir`); then the newest stored issues read as a reader against a dry run of the same hour on the stack, each new fault a numbered row, fixed the same way. Dry runs only (`--no-model` unless the model's output is the point, under USD 2 a session): no email sent, no stored issue rewritten. When the stack is ready, its landing request row.

## Session 3519: the records and the note

Long end 1:00. The records and the note (`docs/state/note_<date>_oldlaptop.md` or a suffixed name, checked free first, short bullets: what landed, what waits in which landing row, what waits for Samuel with defaults).

## Session 3520: the next file, the queue

Long end 1:00. The next file (written by session 3505) updated with what this chain did not finish, pushed; then the queue step: `.venv\Scripts\python.exe scripts\chain_queue.py next`, and run whatever it prints the same way.
