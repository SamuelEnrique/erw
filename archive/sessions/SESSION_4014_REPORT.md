# Session 4014 report: P2's row 27 (holding 23), P4's row 26, P1's row 25 to `986402209`, the old laptop's row 11 to `6047f82d1`

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 20:58 UTC. Opus 5.5. Model spend: USD 0.

## What `wip/w2-land-j` holds

- **The commits:** land-i's gated commit `2765f24c1`, merged with each requested head exactly:
  - `6047f82d1` (row 11);
  - `986402209` (row 25);
  - `33c490eb8` (row 26: P4's large-load research documents and one test; its branch has since added another test, not requested);
  - `6ecf26bbd` (row 27: row 23 whole, then the verifier's steps 7 to 9 and seven test files);
  - `wip/w2-4000`.
- No conflicts: `cebf51a33`, and `4c1be727a` once the gate merged main.
- **Before the gate:** the three checks exit 0. The 14 changed test files with 4010 and 579 pass.

## The gate

- **Every step of `land_check.py` passed** (`4c1be727a`, 21:02 to 21:32 UTC):
  - the suite: 9,129 tests OK, 383 skipped;
  - check-values passed;
  - check-routes, check-cross-checks and check-csp passed.
- **Pushed** to `task/4014-landing` at 21:32 UTC, after snapshot `before-4c1be727`.
- **Run 43511638880** merged at 21:59 (`9bd04cfad`); the deploy succeeded at 22:00.
- **Snapshot after: 0 differences.**
- **Marked** on main as `6ad21f85e` (0 differences). Rows 25, 26 and 27 (row 23 whole within 27) and row 11 are landed in part: each row had named a newer head by the time this landed.

## Decisions made without you

- None new.

## For Samuel's ruling

- None. Row 27 names two rulings of its own (Dependabot alerts off; a public repository with a fault written before its fix lands), and they are in P2's list (`docs/reviews/security-faults-2026-11-13.md`, rows 33 and 34).
