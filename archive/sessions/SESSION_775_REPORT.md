# Session 775 report: "Your load" and All grids, side by side

22 October 2026, from 20:40 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-775` on `wip/775-allgrids` (cut from `wip/774-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 775. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: a local build's two views.

## Read these first

- **`docs/reviews/siting-two-views.md`**: every figure both views draw for ERCOT LZ_NORTH, read from one build.
  - **Equal**: ERCOT's large loads approved to energize (8,927 MW in both).
  - **Equal by construction**: energy, one function for both, held by test 701 (OK).
  - **Different on purpose, and said so in the tips**:
    - carbon: twelve months consumption-based on "Your load", 303.14 kg, against eGRID's annual generation-based rate on the tab, 332.87; rulings item 7;
    - transmission: "Your load" shows the wires utilities' delivery tariffs, the tab the four-peak charge.
- **No fault found**, so nothing was fixed.

## What to review

1. `docs/reviews/siting-two-views.md`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s775`, beat) | 0 | |
| `runs/chain_062/keys775.mjs` on both views | 0 | 234 and 519 keys |
| `tests.test_session701` | 0 | OK |

## The landing

Sessions 766 to 777 landed in one push at 21:13 UTC: see `SESSION_777_REPORT.md`, "The landing".

## Decisions made without you

1. **ERCOT LZ_NORTH, the default of "Your load"**, as the place both views draw most of.

## For Samuel's ruling

- Nothing new (rulings item 7 covers the carbon measure).

## Files

- New: `docs/reviews/siting-two-views.md`, this report.
