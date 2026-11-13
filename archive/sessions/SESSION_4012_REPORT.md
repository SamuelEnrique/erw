# Session 4012 report: P2's security list (row 23), window 4's row 6, the old laptop's row 11 to its newer head

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 19:37 UTC. Opus 5.5. Model spend: USD 0.

## The requests read (19:37 UTC)

- The portable laptop's row 23: `wip/5150-security` at `5411fef7d` (P2, sessions 5150 to 5158: the security list of 13 November, rows 2 to 24).
- Window 4's row 6: `wip/4270-forecast` at `11542a585` (Virginia).
- The old laptop's row 11 at `91cc7525c`.

## What `wip/w2-land-h` holds

- **The commits:** land-g's gated commit `896229157`, merged with:
  - `wip/4270-forecast` at `9e4ba9870`; past `11542a585` only reports, a note and the method note;
  - `91cc7525c`;
  - `wip/w2-4000`;
  - **`5411fef7d` exactly.** P2's branch has gone on to `ddcee4e5d`, with code the row does not name (`site/next.config.ts`, tests 5102, 5159 and 5160), so that waits for a later row. `wip/5157-retire-link` is not in it, as the row says.
- No conflicts: `f7416bb7f`, and `f73b6f3c` once the gate merged main.
- **Before the gate:** `build_llms.py --check`, `licenses.py check` and `check_spec.py` exit 0. The 11 changed test files with 4010, 2207, 4000, 579 and 5101 pass.
- **A risk named before the gate:** the row's new per-address limits touch routes that check-routes, check-security and check-csp read a few times each, and P2 read that and did not run it.

## The gate

- **Every step of `land_check.py` passed** (`f73b6f3c3`, 19:50 to 20:22 UTC):
  - the suite: 8,951 tests OK;
  - the build passed;
  - check-values passed, with the `/policy` license floor accepted;
  - check-routes, check-cross-checks and check-csp (97 pages) passed. **Row 23's new limits did not trip the gate's checks.**
- **The landing:**
  - Snapshot `before-f73b6f3c`, then the push to `task/4012-landing` at 20:23.
  - Run 43501083643 merged at 20:47 (`ad7f16ca6`); the deploy succeeded at 20:48.
  - Snapshot after: **0 differences**.
- **Marked** on main as `e73b31e46` (0 differences):
  - window 4's row 6 landed;
  - row 23 landed in part (to `5411fef7d`);
  - row 11 landed in part (to `91cc7525c`).
  - The newer heads of rows 23 and 11 are in session 4013's gate.

## Decisions made without you

- **A security row is combined with others, with the plan written down:** if its limits trip the gate's own checks, it is taken out and the rest gated again.

## For Samuel's ruling

- None.
