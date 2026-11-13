# Session 4013 report: P1's rows 24 and 25, P2's row 23 to `f300710e7`, the old laptop's row 11 to `48b5fb1df`

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 20:23 UTC. Opus 5.5. Model spend: USD 0.

## What `wip/w2-land-i` holds

- **The commits:** land-h's gated commit `f73b6f3c3`, merged with:
  - `f300710e7`: row 23's new requested head, exactly. P2's branch past it is main merged in;
  - `48b5fb1df`: row 11's head;
  - `2adcd44dd`: P1's row 25, holding row 24 and its four branches `wip/5072-requests`, `-crosscheck`, `-parity` and `-analysis`;
  - `wip/w2-4000`.
- No conflicts: `671e8b3ae`, and `2765f24c1` once the gate merged main.
- **Before the gate:** the three checks exit 0. The 12 changed test files with 4010, 2207, periodicals_3457 and 579 pass.

## The gate

- **Every step of `land_check.py` passed** (`2765f24c1`, 20:27 to 20:57 UTC):
  - the suite: 9,055 tests OK, 383 skipped;
  - check-values passed;
  - check-routes, check-cross-checks and check-csp passed.
- **Pushed** to `task/4013-landing` at 20:58 UTC, after snapshot `before-2765f24c`.
- **Run 43506395644** (GitHub ran the suite again because main had moved) merged at 21:24 (`8d44ea156`); the deploy succeeded at 21:25.
- **Snapshot after: 0 differences.**
- **Marked** on main as `0cc1ca1c7` (0 differences):
  - rows 23 and 24 landed;
  - row 25 landed in part (to `2adcd44dd`);
  - row 11 landed in part (to `48b5fb1df`).
  - The newer heads of rows 25 and 11, with rows 26 and 27, are in session 4014's gate.

## Decisions made without you

- **A row whose requested head moves while its branch keeps growing is landed at the head the row names.** For row 23 that was `f300710e7`; past it, main merged in.

## For Samuel's ruling

- None.
