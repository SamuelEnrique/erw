# Session 1722 report: the landing of session 1715

Energy Research Warehouse (ERW), session 1722, chain 191, samueloldlaptop, 6 November 2026, 18:06 to 18:32 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. The gate on `wip/1715-a11y`.

## What it did

- **The gate**, on `cfe6575dc`:
  - The suite passed (7955 tests, 343 skipped), as did the build.
  - `check_values` matched 7817 of 7817 values and failed only on the two known floors.
  - By hand, all passed: routes (0 failed), cross-checks (92 of 92), CSP (97 pages, 0 violations).
- **The landing**: no freeze; `s1722-before` at 18:12. Main had not moved. Pushed at 18:12:45; GitHub merged it as **`ae1c4eada` (18:30 UTC)**, and Vercel deployed it.
- **`s1722-before` to `s1722-after`: 25 pages, **0 differences**.**
- `wip/1715-a11y` is deleted on origin, and its worktree and the gate folder are removed.

## Decisions made without you

- None.

## For Samuel's ruling

- None.
