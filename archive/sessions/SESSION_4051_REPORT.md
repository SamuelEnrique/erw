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

## Decisions made without you

- None new.

## For Samuel's ruling

- None.
