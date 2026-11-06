# Session 2227 (chain 152, Ask) report: the gate, stopped for memory; nothing landed

6 November 2026, 02:55 to 03:08 UTC, on portable-laptop (code role), unattended. Chain `queue/done/152-night-5-november-portable-ask-quality.md`. Worktree `erw-2227` on `wip/2227-ask` (level with `wip/2226-ask`); the gate run from the main checkout on `wip/2226-ask`, as the prompt names it. Model spend **USD 0**. Chain so far: USD 9.72 of 15. **Nothing of this chain reached main; production was not touched (no snapshot, no push to `task/`).**

- **The gate**: `scripts/land_check.py --ref wip/2226-ask --task 2220-2226-ask --port 3220`, each step its own process with its exit read, the lines in `runs/land_check/<sha>.txt` (not in git). Fifteen tries from 02:56 to 03:02, a minute apart:
  - tries 1, 2 and 4 to 14: stopped at `db_probe` (the database answered in 3.1 to 3.5 seconds; the gate's line is 3);
  - try 3: `task_branches` failed on `git fetch origin task/c147-data` (the desktop's branch, landing at that minute);
  - after it main had moved: `main_merged` failed until `origin/main` was merged into `wip/2226-ask` (`202508dec`, pushed);
  - try 15 at 03:02: `freeze` pass (no freeze), `main_merged` pass, `task_branches` pass (none in flight), `db_probe` pass (under 3 s), `build_lock` pass (`land-202508de`), `worktree` pass (the clean copy), then the suite started, and **Claude Code stopped the retry loop because the machine was critically low on memory** (its own rule, not the gate's: "do not start it again on your own"). The suite, `ask_replay`, `npm ci`, the build and the page checks were not run.
- **Left clean**: the build lock released (`land-202508de`), the gate's clean worktree unlocked and removed, no server on port 3220, no `node` or `python` process left. Memory after: 2.5 GB free.
- **Why the memory ran short**: the gate's suite (every test, node tests among them) on a machine already holding the owner's Chrome (about 1.5 GB), Slack, an Edge web view and the Windows search indexer; this session's one build at 02:38 had passed with 2.7 GB free, and the memory line the chain's prompt gives (3 GB, 2 GB alone) was met at 03:02 only just (2.49 GB). Chain 096's item 15 (`docs/reviews/ask-board-rulings-2026-10-23.md`) is the same finding on the old laptop.
- **Not deleted, not removed**: the branches `wip/2220-ask` to `wip/2226-ask` stay on origin (none is an ancestor of main); the chain's worktrees are removed by session 2228 once its note is pushed, their branches being on origin.
- Pushed to `wip/2227-ask` (this report).

## To finish

The landing, when a person or a session with memory free runs it, each command its own, its exit read, not between 14:00 and 16:15 UTC:

```
cd C:\Users\samen\Documents\erw
git fetch origin
.venv\Scripts\python.exe scripts\freeze.py status
.venv\Scripts\python.exe scripts\land_check.py --ref wip/2226-ask --task 2220-2226-ask --port 3220
```

(`wip/2226-ask` must still hold `origin/main`: if main moved, `git merge origin/main` on it first and push.) When every step passes, the gate prints the rest, which it never runs:

```
node site\scripts\snapshot-live.mjs take before-2220-2226
git push origin wip/2226-ask:task/2220-2226-ask
(the workflow code-branch.yml merges the branch when its checks pass)
node site\scripts\snapshot-live.mjs take after-2220-2226
node site\scripts\snapshot-live.mjs compare before-2220-2226 after-2220-2226
```

The comparison's lines go into the landing's report, each marked expected or not; the pages are all in review, so a visitor's snapshot should not change. Then delete `wip/2220-ask` to `wip/2227-ask` on origin once they are ancestors of main.

## Decisions made without you

1. **The gate was not started again after Claude Code stopped it** for memory: the harness's note says to report and not restart on my own, and a build on a machine short of memory is what chain 096 found breaks landings. The chain's code waits on `wip/2226-ask`, whole, with main merged, and the commands above.
2. The gate was run again each minute while the probe closed it, and once more after main moved; fifteen tries in all, none of them the gate's own fault.
3. `wip/2227-ask` holds only this report; the gate's ref stays `wip/2226-ask`, the branch the prompt names.

## For Samuel's ruling

1. Whether a night chain on this laptop may close the owner's Chrome (about 1.5 GB) before a landing, or whether landings of this machine's chains should run on the desktop.
2. The probe's 3-second line against a database that answered in 2.6 to 3.5 seconds all night (it opened on 2 of 20 probes).
