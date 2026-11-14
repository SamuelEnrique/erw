# Session 4052 report: the old laptop's row 11 to `98df9760b`, window 4's row 7 to `829a1dfb6`

Energy Research Warehouse (ERW). Chain 230, the desktop's second window, 14 November 2026 from 01:25 UTC. Opus 5.5. Model spend: USD 0.

## What `wip/w2-land-m` holds

- **The commits:** `origin/main` (after land-l, `719a7f66d`), merged with:
  - `98df9760b` (row 11's head);
  - `829a1dfb6` (window 4's row 7 head, moved at 00:39 UTC);
  - `wip/w2-4000` (sessions 4050 to 4051's reports and the note).
- No conflicts: `0f04fb7a9`.
- **Before the gate:** the three checks exit 0. The changed test file with 4051, 414, 425 and 579 passes, and `test-waits-ledger.mjs` holds.
- **The gate:** started at 01:28 UTC, with the lock free.

## The gate

- **Every step of `land_check.py` passed** (`0f04fb7a9`, 01:28 to 01:58 UTC):
  - the suite: 9,245 tests OK;
  - the build passed;
  - check-values, check-routes, check-cross-checks and check-csp passed.
- **The landing:**
  - Snapshot `before-0f04fb7a`, then the push to `task/4052-landing` at 01:58.
  - **GitHub started no run for that push.** After nine minutes the branch was on origin and no run was listed.
  - The same commit was pushed again as `task/4052-landing-b` at 02:08, after snapshot `before-0f04fb7a-b`.
  - Run 43544592157 merged at 02:22 (`bb66c467b`); the deploy succeeded at 02:23.
  - Snapshot after: **0 differences**.
- **Marked** on main as `a4cddd694` (0 differences). Row 11 and window 4's row 7 are landed whole.
- **At 02:26 UTC no row was requested** on any request file.

## Decisions made without you

- None new.

## For Samuel's ruling

- None.
