# Session 1176 report: the method notes and the rulings list

24 October 2026 (UTC), on samueloldlaptop (the old laptop), the thirteenth session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1176-grid`, cut from `wip/1175-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1176`. Code-only, as the brief sets chain 078: no build, no server, no browser. Documents and tests only: no site code changed. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher.

## Read these first

- **Every rule chain 078 set is in a method note, dated, with its decisions.** Read against reports 1164 to 1175; what was missing was added, nothing repeated:
  - `grid_network.md`: 1165's fixture decision; 1167's `shownPrice` and `check-network-v3.mjs` ring decisions; a new subsection "Every old address, tested (session 1172)" with its four decisions (1172 had only a paragraph, no block); 1175's four decisions (the TypeScript scan, the whole page, the line on the server, the fallback).
  - `generation_mix_hourly.md`: 1167's ISO-NE queue block and "What it costs" words, with a Decisions (session 1167) block (the section had the clean table and the Price factor but no block); 1169's "this note, not the join's".
  - `grid_stress.md`: 1168's chart props, the `span` copy, `caisoJoinDay()`, and its finding on "As built" (not changed).
  - `grid_network_v3.md`: 1170's check-methods rule for a path ending at `@<day>`.
  - `ercot_grid_notices.md`: 1174's hourly mix not marked, the table lines, the fixture without `x_text`, the schedule put to the owner.
  - `scarcity_hours_by_grid.md`: a section "The panel in chain 078" (1174's prop shared by both grids; calls only marked).
  - `california_reliability.md`: a section for 1166's `awe|rows|any` and `awe|newest|any` (named only in the Mix tab's note until now) and 1174's `ercotn|` kept apart, with decisions.
  - `eia930_balance.md`: a Decisions line pointing to `grid_network.md`'s block.
- **Each note's chain 078 section opens with one index line**, "Chain 078 in this note (sessions 1164 to 1177): ...", naming the sessions it holds and where the others sit.
- **The rulings list** (`docs/reviews/grid-rulings-2026-10-23.md`): one line says none of the 18 items has been ruled (no owner input since 23 October), none struck; 19 new lines from reports 1165 to 1175 (1164 put none; 1173's is 1166's first, on one line), in the three groups, the weightiest first: in the data group 1167's held NYISO and MISO queue rows, 1167's missing `entity_id` filter in `site/lib/supabase.ts`, 1169's `caiso_fuel_supply` not loaded, 1174's ERCOT connector not on a schedule. Three items had no recommendation in their report (1165, 1169, 1171): each line says its recommendation is this list's.
- **"To finish"**: landing B first, now `wip/1162-grid` with 1164 to 1176 stacked as `wip/1176-grid`; then chain 078's expected differences, floors, check-methods keys, build checks, the Vercel file-tracing check, screenshots, the pack's walk, the phone traces and the `caiso_fuel_supply` panel; 1161's `tsc` item marked done (chain 078 ran it ten times, exit 0).

## What to review

1. Read `docs/reviews/grid-rulings-2026-10-23.md` on `wip/1176-grid` (until it lands): the line under the opening, then the first four lines of "The data and licenses".
2. Read the index line at the top of each chain 078 section: `docs/methods/grid_network.md` ("The balance, said where the figures are"), `generation_mix_hourly.md`, `grid_stress.md`, `grid_network_v3.md`, `ercot_grid_notices.md` (section 6), `scarcity_hours_by_grid.md`, `california_reliability.md`, `eia930_balance.md`.
3. After the landing, on production: `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**, then `https://erw-flame.vercel.app/data/methods/grid_network` and search "Every old address, tested".
4. Screenshots: not taken, no build (documents only).

## Checks

- `node site/scripts/check-methods.mjs` (no server; the keys recorded): exit 0, 553 of 553 figures named, 57 pages.
- `python -m unittest`, one file at a time, the 52 test files that name a changed note or the rulings list (grep of `tests/`) and `tests.test_session1176` (new, 7 tests): all 53 exit 0 (`tests.test_session1162` after its assertion was extended, below).
- Node tests that read a changed note: `test-check-revised.mjs` exit 0 (12 of 12), `test-scarcity-strip.mjs` exit 0, `test-check-links.mjs` exit 0; with the `node_modules` junction: `test-grid-stress.mjs` (tsx loader) exit 0, `test-grid-addresses.mjs` exit 0 (8 tests, 61 addresses). The junction removed with `cmd /c rmdir`; the main copy's `node_modules` intact.
- No `tsc`: no TypeScript changed. No em dash in any changed file (tested).

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it. The rulings list's first "to finish" line says how.

## To finish

- Land with the combined landing (landing B, `wip/1176-grid` or its successor). Expected differences: the method pages `/data/methods/grid_network`, `generation_mix_hourly`, `grid_stress`, `grid_network_v3`, `ercot_grid_notices`, `scarcity_hours_by_grid`, `california_reliability`, `eia930_balance` gain the index lines and the added decisions; no figure or key moves.
- At that landing, `check-methods.mjs --values <the run> --write`, then `check-methods.mjs` again: chain 078's keys are named in these notes, but today's run read only the keys recorded before both chains.

## Decisions made without you

- **`tests/test_session1162.py` extended, not loosened in what it held**: it counted exactly 18 rulings, each ending with a session of 1155 to 1161. It now counts 18 lines of those sessions (as before) and holds every line, old and new, to a recommendation and a session of 1155 to 1175; `tests/test_session1176.py` counts chain 078's 19.
- **Two "to finish" lines updated in place, not added beside**: landing B's line (now the combined branch, with the person needed), and 1161's `tsc` line (marked done, its words kept). Every ruling line of chain 077 stands word for word; some moved within their group to put the weightiest first.
- **1166's first ruling and 1173's are one line** (the held rows on production): 1167 applied the standing rule on the branch, so what is left to rule is whether to wait for landing B.
- **Where a report gave no recommendation** (1165 signed mean, 1169 load `caiso_fuel_supply`, 1171 revised windows), the line gives one and says it is this list's.
- **`awe|rows` and `awe|newest` named in `california_reliability.md` too**: the table's own note listed every other `awe|` form.
- **1168's finding on "As built" written in `grid_stress.md`** as a finding, the "As built" lines left as they stand (a data session rebuilds them).
- **No test or decision that is only about a test's mechanics was copied into a note** (pinned lines kept by adding branches, a figure count split): those stay in the reports.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session1176.py`, this report.
- Changed: `docs/reviews/grid-rulings-2026-10-23.md`, `docs/methods/grid_network.md`, `docs/methods/grid_network_v3.md`, `docs/methods/generation_mix_hourly.md`, `docs/methods/grid_stress.md`, `docs/methods/scarcity_hours_by_grid.md`, `docs/methods/ercot_grid_notices.md`, `docs/methods/eia930_balance.md`, `docs/methods/california_reliability.md`, `tests/test_session1162.py`.
