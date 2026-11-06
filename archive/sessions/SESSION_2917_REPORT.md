# Session 2917 report: the landing, stopped for memory

6 November 2026, about 04:21 to 04:33 UTC, on lab-desktop (the data machine), chain 151, unattended. Model spend USD 0. Pulls: GitHub only (fetches of origin).

## Read these first

- **Not landed.** `wip/c151-data` was merged with origin's main twice, at `9313c0b93` and then `e4db6e5c2`, because the code machine's chain 149 landed while this session ran.
  - **The gate's first run** (`runs/c151/land_c151.out`) failed at `main_merged`: main moved during the run.
  - **Its second run** (`runs/c151/land_c151b.out`, on `e0cc4b41`) was **stopped by Claude Code for low memory**, during the suite. That says nothing about the branch.
  - **Clean-up:** the gate's build lock was released and its worktree `erw-land-e0cc4b41` removed. The data lock was free throughout. Two python processes, started before this session and not children of it, were left alone.
- **The harness says not to start the gate again unasked.** So this chain stops here, and the queue step for 153 is not run.
- **The before snapshot** `s2917-before`: 25 pages at 04:22 UTC. No deploy followed, so there is no after snapshot.
- **The runner's board guard** (session 2913) is therefore **not on main for the 14:00 UTC run of 6 November.** If that run's board fails tests 1118 or 1139 again, the board is committed as it was on 6 November, and chain 147's session 2885 had to put it back.

## To finish

Run each command on its own and read its exit code. Landings are barred from 14:00 to 16:15 UTC.

1. `git -C C:\Users\Shared\Documents\erw pull --ff-only`, then merge origin/main into `wip/c151-data` in `C:\Users\Shared\Documents\erw-c151`.
2. `.venv\Scripts\python.exe scripts\land_check.py --ref wip/c151-data --task c151-data --port 3151`, with 3 GB free.
3. If check-values fails only on main's known floors (`.venv\Scripts\python.exe runs\c147\cv_diff.py <sha>` exits 0), take snapshot `s2917-before` again, push the commit to `task/c151-data`, wait for the merge sha's Vercel status, then take `s2917-after` and compare.
4. `.venv\Scripts\python.exe scripts\chain_queue.py next`, which takes 153; push the move.

## Decisions made without you

- **Main merged twice rather than landing on a stale base.**
- **Stopped instead of restarting the gate,** as the memory stop's notice says.

## For Samuel's ruling

- Whether to restart the landing now (before 14:00 UTC) so the board guard covers today's run.
