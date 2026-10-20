# Session 365 report: the queue knows which machine a file is for

20 October 2026, day, unattended, on samueloldlaptop (the code machine), the first session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`). Branch `wip/365-queue-machine` in the worktree `erw-365`, from origin/main at `5b4f13b9` (the queue's move of 012). Roadmap item 1, "The loop runs itself". Model spend USD 0. No pull, no warehouse data written, no Supabase write, no page changed.

## Read these first

- **This session's landing also records the landing of sessions 352 to 356 and of the two queue commits of 18:05 UTC** (`25a6c727`, the two day chains 011 data and 012 code; `5b4f13b9`, 012 taken by this machine). The orchestrator writes that part, under "Landing".
- **`scripts/chain_queue.py next` now reads a prompt file's machine**: a line `machine: code` or `machine: data` within its first ten lines. It takes the lowest-numbered file for this machine's role (`.erw/machine.json`) or with no such line, names and leaves the others, and when only other machines' files wait it idles with a line that says so ("queue/next/ holds nothing for samueloldlaptop (code): 1 file there waits for another machine (011-day-20-october-data.md)").
- **Without this change the code machine's queue step would have taken the data machine's chain**: `queue/next/011-day-20-october-data.md` (machine: data) is the only file waiting, and the old `next` takes the lowest number whatever its line. Today's `next --dry-run` in the worktree leaves it and would idle (`runs/chain_oct20d/s365/chain_queue_next_dry_run.out`). Session 372's queue step needs this landed first.
- **`next --file NNN-<slug>.md`** takes one named file with the same move and commit; `list` shows each file's machine. The planner marks the chain it drafts with `machine: <role>` and its own check refuses a draft without it.
- No page changed: no build, no shots, no Impeccable, no check-values (none was asked; the session touched no file of `site/`).

## What to review

No page. The files, in order:

1. `scripts/chain_queue.py`: `mark_of`, `split`, `for_this`, `by_name`, `listing`, and `take` (the skip, the idle line, the planner path).
2. `scripts/planner.py`: the line in `chain()`, `problems_of(..., role)`, the queue held only by this machine's files in `refusals`.
3. `queue/CHAIN_TEMPLATE.md` (the line under the title and the sentence above the rule), `queue/README.md` ("Which machine (session 365)"), `docs/machines.md` ("Continuous work", the chain queue's list).
4. What the commands print today: `runs/chain_oct20d/s365/chain_queue_list.out`, `chain_queue_next_dry_run.out`, `chain_queue_next_file_dry_run.out`.

## Checks

| Check | Exit | Result |
|---|---|---|
| Precheck | (chain) | passed for the chain before this session started, as its prompt says |
| `tests.test_session365` (new, 17 tests) | 0 | OK |
| `tests.test_planner` (34 tests, 4 new) | 0 | OK, after one existing test followed the new rule (below) |
| `tests.test_session188_queue` | 0 | OK |
| The modules that read `CHAIN_TEMPLATE.md`, `queue/README.md`, `docs/machines.md` or the two scripts: `test_session148`, `188_precheck`, `199`, `243`, `59`, `116_alerts`, `149`, `185`, `188_idle`, `188_waits`, `202`, `204`, `206`, `247`, `51`, `91` | 0 each | OK (skips as before: 148 five, 149 one, 51 four) |
| `python scripts/chain_queue.py list` (worktree, read-only) | 0 | `1 waiting in queue/next/ (0 for samueloldlaptop, a code machine):` / `011-day-20-october-data.md  machine: data  (left for another machine)` |
| `python scripts/chain_queue.py next --dry-run` | 3 | leaves 011 (machine: data), would idle with the line above; the planner is off, so no draft |
| `python scripts/chain_queue.py next --dry-run --file 011-day-20-october-data.md` | 2 | refused: marked machine: data, and samueloldlaptop is a code machine |

Every output is in `runs/chain_oct20d/s365/` (one `.out` a module or command).

## Landing

Written by the chain's orchestrator. Three landings are recorded here.

- **Sessions 352 to 356** (`task/352-356-economics`, recorded here as session 356's report said): the freeze status read "no freeze"; the before snapshot `s356-before` at 16:15:43 UTC; GitHub's run 39455892956 passed and merged it (`af5d8b4f`); no new style sheet was seen in ten minutes (the landing changed no style), so the after snapshot `s356-after` was taken at 16:38:01: **0 differences in all** (every page in review).
- **The two queue commits of 18:05 UTC**, pushed straight to main as the owner's prompt asked: `25a6c727` (the two day chains, 011 data and 012 code) and `5b4f13b9` (012 taken by samueloldlaptop, the move alone, made by `chain_queue.py`'s own `move()`: `next` would have taken 011, the lowest number). Freeze status "no freeze"; snapshots `q011-012-before` (18:04:47) and `q011-012-after` (18:05:33): 0 differences. That after snapshot may have been read before Vercel had built the two commits; they change no file a page reads.
- **Sessions 365 and 366 together** (`task/365-366`, `e807631f`): origin/main merged first (the data machine's queue move `ae894d37`); the remote `task/` branches listed (`task/198-battery-data` only, standing since 11 October, not in flight); freeze status "no freeze"; the whole suite in the clean copy at `2bbfdc68` exit 0 (4,679 tests, OK); before snapshot `s366-before` at 19:00:10; GitHub's run 39479695256 passed and merged it at 19:10 (`e468065a`); the after snapshot `s366-after` at 19:20:55. **The comparison: 25 differences, one a page, each expected**: the in-review page's menu gained "Economic impact in review" (session 347's `/impact` in the Economics menu). That line is also production's mark that it served the landing (no style sheet changed). The branches `wip/345-impact`, `wip/365-queue-machine` and `task/365-366` are deleted.

## Decisions made without you

- **A machine whose role is not known takes only files with no line**: it cannot tell whose a marked file is; the line says so and names the files it left.
- **`--file` refuses a file marked for the other role** (exit 2, nothing moved), unless this machine's role is not known: then a person named the file, it is taken, and the output says so.
- **A line whose value is this machine's own name** (as the roadmap's items already allow, `machine: samueloldlaptop`) counts as this machine's; any other value (another name, the template's unfilled `<code or data>`) is left for another machine and named with its value.
- **A file for another machine no longer holds the queue for the planner**: with only the data machine's chain waiting and the planner on, the code machine's planner may draft. The chain it drafts is the one `next` takes, even on a machine whose role file says otherwise (it was drafted for the role the planner was given). `test_planner`'s cap test, which used a drafted code chain to show a data machine is refused, now strips the chain's line first to show the same refusal; the new class `TheMachineLine` shows the marked case.
- **`--file` takes a bare name or `queue/next/<name>`**; anything else with a slash is refused. `--file` with `list` is refused (exit 2).
- **The line counts only alone on its line in the first ten** ("machine: code", any case and spacing); a sentence that contains "machine:" does not.

## For Samuel's ruling

- Nothing new. One note for the data machine: its role file must say `data` for it to take `011-day-20-october-data.md` through `next` once this lands; a data machine with no role file takes only unmarked files (and `--file` still takes 011 by name there).

## Files

- New: `tests/test_session365.py`, this report.
- Changed: `scripts/chain_queue.py`, `scripts/planner.py`, `tests/test_planner.py`, `queue/CHAIN_TEMPLATE.md`, `queue/README.md`, `docs/machines.md`.
- Outputs (not in git): `runs/chain_oct20d/s365/`.
