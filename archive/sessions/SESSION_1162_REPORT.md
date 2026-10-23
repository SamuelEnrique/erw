# Session 1162 report: the method notes

23 October 2026, late evening UTC, on samueloldlaptop (the code machine, the old laptop), session 1162 of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075/076. Branch `wip/1162-grid`, cut from `wip/1161-grid` (sessions 1150 to 1161 merged with main, and the orchestrator's fixes `169e537a` and `35d2c31c`), worktree `C:\Users\lossa\Documents\erw-1162`. Model spend USD 0. No warehouse data written, no Supabase read or write, no web request. **No build, no server, no browser, no `tsc`** (the orchestrator's memory rule: this session changes documents and one `.mjs` script). The session was stopped once by the usage limit and continued on the orchestrator's word.

## Read these first

- **Every rule the chain set is now in a method note**, in a section dated "(chain 077, 23 October 2026)" with its own "Decisions (chain 077)" block (what was chosen, why, what the owner may change), extending what sessions 1153 to 1156 had already written, not repeating it:
  - `docs/methods/grid_network.md`: "The Grid tool's panels, every figure keyed": the rule of a server twin for each browser figure; the seven panels and their keys (`grid_network_<grid>`, `grid_gravity_<grid>`, `grid_clean24_<grid>`, and pointers for `grid_mix_<grid>`, `grid_scarcity_<grid>`, `grid_caisoalert_caiso`); the three key changes (`series_sum` with a comma list, `series_n`, `awe|last` and `awe|ndays`); the map and gravity cards on a phone and their ARIA roles (1158); California's join date through `caisoJoinDay()` (`169e537a`); the stored answers' selection (1157); what is not keyed yet (1151's list); the reads (1160). Plus one bullet in "The figures on the page and their keys".
  - `grid_network_v3.md`: "The day carried from grid to grid": the Gravity and Network tabs' picker carries `net=day&t` (1153, `35d2c31c`); the map's links carry the whole moment (1156).
  - `generation_mix_hourly.md`: "The Mix tab's energy mix, keyed, hourly and by month": the tables (no sub-region generation exists), the 24-hour window, each fuel's key with its comma list, the two share denominators, **the peak hour as the demand peak**, **the age said against the drawing clock**, the stack's fix, the monthly view (`mixp=month`), **CAISO's withheld mix said as the session 118 ruling**, the tables at 390 px, the reads trimmed in 1160. Plus one key bullet.
  - `generation_mix.md`: the Mix tab's three changes, and that its line "Negative values are not stacked" describes the chart before session 1152.
  - `grid_stress.md`: the three different "tight" hours on the tool (this note's tightest hours, the panel's demand peak, the scarcity hours).
  - `scarcity_hours_by_grid.md`: the panel's later changes (1155, 1158, 1159, 1160) and the decisions behind 1154's rules (**the window as the latest 30 days held**, standard-time days, the price on hover, `series_n`, SPP "not in the table yet").
  - `california_reliability.md`: the notices read once per render (1160), the face (1159), the scorecard's link back, and the decisions behind 1155's rules.
- **`check-methods.mjs` read a comma-list key as one figure** (session 1152's `series_sum` of a fuel group, such as `net_generation_wind_mw,net_generation_wind_with_battery_mw`), so the note could never name it. Now a key of several variables is a figure of each (`figures()`, one line and its comment); a key without a comma is read as before.
- **The chain's own keys checked against the notes `/grid` links**: 47 figures of every key form the chain's panels write, run through check-methods' own `figures()` and `named()`: 30 named before this session, 31 after the comma fix, **47 of 47** after the notes. The 16 missing were `generation_mix_hourly_profile`'s `<fuel>_mwh` and `<fuel>_share_pct`, now named as a list.
- **`docs/reviews/grid-rulings-2026-10-23.md`**: the 18 items under "For Samuel's ruling" in reports 1150 to 1161 (sessions 1150 to 1154 and 1157 put none), one a line, each with a recommendation and its session, in three groups (the page's words 6, the design 9, the data and licenses 3); then nine "To finish" items that need a person or a build.

## What to review

1. Read `docs/reviews/grid-rulings-2026-10-23.md` (on `wip/1162-grid` until the landing): answer each line yes or no.
2. Read each note's section "(chain 077, 23 October 2026)", starting with `docs/methods/grid_network.md`, "The Grid tool's panels, every figure keyed", and its "Decisions (chain 077)" block.
3. After the combined landing, open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**, then `https://erw-flame.vercel.app/data/methods/generation_mix_hourly`: scroll to "The Mix tab's energy mix, keyed, hourly and by month". The same for `https://erw-flame.vercel.app/data/methods/grid_network` and `https://erw-flame.vercel.app/data/methods/scarcity_hours_by_grid`.

## Checks

- Precheck for session 1162: run by the orchestrator, exit 0.
- `node scripts/check-methods.mjs` in `site/` (no server: the keys recorded in `check-methods-keys.json`): exit 0, 553 of 553 figures named, before and after the edits.
- The chain's keys against the notes (`chainkeys.mjs` in this session's scratch folder, check-methods' own functions): exit 1 (30, then 31 of 47), then exit 0, 47 of 47.
- Every file path the new sections name exists (checked from the diff); the one missing at the time, `docs/reviews/grid-rulings-2026-10-23.md`, was then written. No site link was added.
- `python -m unittest`, one file at a time: `tests.test_session1162` (new, 5 tests), `409`, `1154`, `467`, `468`, `1155`, `58`, `1152`, `102`, `118`, `133`, `156`, `310`, `94`, `109`, `1156`, `124`, `168_network`, `180`, `180b`, `193`, `247`, `266`, `299`, `381`, `538`, `78`, `123`, `207`, `306`, `322`, `324`, `1161`, `254`, `265`, `280` (every test that reads a note or script changed here): exit 0 each. No assertion changed.
- No em dash in any file changed (the new test checks the seven notes, the rulings file and the script).
- No `db_probe`, build lock, build, server, browser, screenshots or `tsc` (the memory rule; no TypeScript changed).

## The landing

- None in this session: documents and one checker script, landing with the chain's combined landing (B) once a build can be made. Pushed: `wip/1162-grid`.

## To finish

- The nine items of `docs/reviews/grid-rulings-2026-10-23.md`, "To finish": landing B with its snapshots; the floors and `check-methods-keys.json` rewritten from a passing run (then `check-methods.mjs` again: the recorded keys predate the chain, so today's 553 of 553 does not yet cover its panels; this session's 47 of 47 does, from the code); the build's checks and screenshots; the trader's path values; `tsc` unbounded; the queue pushes' after snapshot; the stored answers' rebuild.

## Decisions made without you

- The tool-level rules (the server-twin rule, the panels list, the stored answers, what is not keyed) went into `grid_network.md`, beside its section "One page, four tabs, and the Ask panel", as the Grid tool's main note; each panel's own rules stayed in the note of its table, with a pointer.
- Each new section stands before the note's "The figures on the page and their keys" (or "Checks"), so that list stays last, as session 409 set; notes without such a list got the section at their end.
- `generation_mix.md`'s line "Negative values (storage charging) are not stacked" was left as written and corrected in the new section (extend, never delete).
- `check-methods.mjs` was changed rather than writing each comma list into a note: the lists depend on which variables a grid's window holds, so a note could not name every one.
- The Clean tab's panel is described in `grid_network.md`, not `emissions.md` (not this chain's note); its keys were already named there.
- Session 1158's "colour contrast not judged" is listed as a check to run, not a ruling; session 1160's carried migration 036 is listed as it stands.

## For Samuel's ruling

- None new: the 18 earlier items are in `docs/reviews/grid-rulings-2026-10-23.md`.

## Files

- Changed: `docs/methods/grid_network.md`, `grid_network_v3.md`, `generation_mix.md`, `generation_mix_hourly.md`, `grid_stress.md`, `scarcity_hours_by_grid.md`, `california_reliability.md`; `site/scripts/check-methods.mjs` (`figures()`, a comma list).
- New: `docs/reviews/grid-rulings-2026-10-23.md`, `tests/test_session1162.py`, this report.
- On this machine only: `runs/s1162_*.out` (in the main checkout's `runs/`).
