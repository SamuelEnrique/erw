# Session 4051 report: the urgent row's regate, and land-l behind it

Energy Research Warehouse (ERW). Chain 230, the desktop's second window, 13 November 2026 from 22:22 UTC. Opus 5.5. Model spend: USD 0.

## Land-k (portable row 28, urgent), regated

- **`32ee41fb1`**: row 28 with session 4050's move of its report's table, waiting for the lock from 22:22. Window A's `c227-gate5` held it, and land-k took it at 22:53 UTC (`47cf25d5c` once main was merged; `build_llms.py --check` exit 0).
- **Every step of `land_check.py` passed** (22:53 to 23:24 UTC):
  - the suite: 9,223 tests OK, with tests 414 and 425 now passing;
  - the build passed;
  - check-values, check-routes, check-cross-checks and check-csp passed.
- **The landing:**
  - Snapshot `before-47cf25d5`, then the push to `task/4015-landing` at 23:24.
  - Run 43526862481 merged at 23:40 (`f44d37628`); the deploy succeeded at 23:41.
  - Snapshot after: **0 differences**.
- **The row's proof, on the landed tree from `site/`:** `node --import ./scripts/alias-register.mjs scripts/eval-tool.mjs query '{"table":"isone_interconnection_queue","aggregation":"count"}'` printed `"isError":true` with the error "table isone_interconnection_queue is license needed: ISO-NE: the publisher's own page asks for permission; none is recorded yet." **The chat refuses the held table.**
- **Marked** on main as `582226a76` (0 differences).

## Land-l, stacked on land-k (`8c01f39c0`)

- **The requested heads, each exact:**
  - portable 25 `98a356edc`, 26 `dab4c005d` and 27 `7204e8ba2`;
  - old laptop 11 `f2ebae979`;
  - **window 4's row 7, `wip/4290-forecast` at `c869252b6`**. Its branch's code past that head (property and sales rules, the model, a cross-check) is not requested and is not in it.
- **With them:** `wip/w2-4000` (chain 228's and 230's reports and the note).
- **Checks:** the three checks exit 0. The 9 changed test files with 414, 425, 4010 and 579 pass. `test-waits-ledger.mjs` holds 3,000 of 3,000.
- **Its gate was queued at 22:53**, behind land-k's.
- **The gate passed every step** (`56a46041c`, 23:28 to 23:58 UTC):
  - the suite: 9,235 tests OK;
  - the build passed;
  - check-values, check-routes, check-cross-checks and check-csp passed.
- **GitHub's run of `task/4051-landing` failed** (run 43531064396, 00:13 UTC). The step was "Site build and check-routes": `/learn/problems/know-your-grid` printed "unexpected error: Cannot read properties of undefined (reading 'value')", and `/learn/problems/storage-and-taxes` printed "invalid input syntax for type timestamp with time zone: undefined-01T00:00:00Z" (the job's log, read through the API).
- **Read as a failed read on the runner, not a fault of the branch:**
  - The same pages passed in the gate's build 20 minutes before.
  - Main gained only land-k and two request lines in between, and land-k's own run passed its build at 23:35.
  - The live set answers both pages' tables now. `cost_of_power_monthly` has September 2026 whole and October not (48 of 744 hours), and the hourly profile holds every month to October, all retrieved on 4 October.
  - An empty read gives exactly these errors (the month of an empty list, the `.value` of an absent row).
- **Run again** as `task/4051-landing-b`, the same commit, at 00:16 UTC, after snapshot `before-56a46041-b`.
- **The second run failed the same way** (run 43533062834, 00:31 UTC). So the cause was not the runner.
- **Reproduced here** with `problemSet()` under node against the live set, at 00:33 UTC on 14 November. Both sets threw, and `site/lib/problems.ts` is the same on main, **so every build from midnight failed these two pages, on main and for every window's landing.**
  - **Set A** ("know your grid") looks for "the latest day both ERCOT and CAISO are held" in the last 10 days (lines 111 and 123). The live set lacks 5 to 8 November of EIA-930, so at midnight the window lost 4 November, the last day both held. The `find` returned `undefined`, and `row()` read `.value` of it.
  - **Set D** ("storage and taxes") reads WTI's months over 75 days and needs one with a certified Texas gas price. At midnight the window lost 31 August, the last such month, so the month was `undefined`.
- **The fix, small and plainly correct, on land-l:**
  - lookbacks of 45 days (both set A windows) and 400 days (set D's months). "Latest" means what it meant;
  - test 4051;
  - under node both sets build with 5 questions each; `tsc` 0 errors; the 14 problem-set test files pass.
  - Commit `2d32f6de4`, regated from 00:35 UTC.
- (the regate's result and the landing: written when they come)

## Decisions made without you

- None new.

## For Samuel's ruling

- None.
