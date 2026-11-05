# Session 1072 report: the three paths, walked again, and the spill fixed

23 October 2026, about 09:55 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1064` on `wip/1064-allgrids`. Chain `queue/done/073-evening-23-october-code-allgrids-packages-3.md`, session 1072. Model spend USD 0. No request; a local build of the branch (`next start` on port 3164, the internal view), stopped after.

## Read these first

- **The spill fixed**: when the hub table is scrolled sideways, its first column (the row's name) stays in place, sticky with a white background (tokens.css, "its first column stays in place"), but had no stacking level, so a later cell's text was drawn over the name ("load: rule 2026-06" over "TH_NP15_GEN-APND"; session 1027's shot shows it too). The name column of the All grids hub table now has `z-index: 1` (tokens.css, a rule of its own, the hub table only): the scrolled cells pass under it. Before: `docs/brand/review-1048/n05_reserve_tip_1280.png`; after: `docs/brand/review-1072/s01_spill_tip_1280.png` and `_390.png`. No figure moved.
- **The three walks** against chain 072's (1050 to 1052): 17, 12 and 11 steps; 2 differ, each only by session 1069's new line on BBREEZE_1_2's panel (its county, WILLACY, has no planned generator in the window). No step fails; no new fault. Each path file gains "Walked again (session 1072, chain 073)".
- **Session 1069's panel line**, at 1280 and 390: `docs/brand/review-1072/s02_panel_planned_*.png` (7RNCHSLR_ALL, FAYETTE: "201 MW under construction (1)", written whole; the file's 200.5).


## The landing

Lands with the next landing of this chain.

## Checks

| Check | Exit | Result |
|---|---|---|
| `npm run build` | 0 | no statement timeout |
| `walk.mjs`, 4 steps (the fix and 1069's line) | 0 | `docs/brand/review-1072/` |
| `walk.mjs` with steps 778, 779, 780; `walkcmp.py` against `runs/chain_072/walk1050_*` | 0 | 2 of 40 steps differ, 1069's line only |

## Decisions made without you

1. **The fix scoped to the All grids hub table** (`[data-allgrids-table]`), not every sticky first column of the site: the others were not seen to spill; a wider rule is a session of its own.

## For Samuel's ruling

- None new.
