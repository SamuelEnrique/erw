# Session 1169 report: California's generation, the two sources side by side (not built: no table in the live set)

24 October 2026 (UTC), on samueloldlaptop (the old laptop), the sixth session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1169-grid`, cut from `wip/1168-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1169`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (`series` with `limit=2`, `catalogue` by name, below).

## Read these first

- **The session's condition is not met, so nothing was drawn.** No public CAISO own-generation table is in the live set:
  - `caiso_fuel_supply` (CAISO's Today's Outlook supply by fuel, hourly, June 2025 on, public in `site/data/license_status.json`): the live catalogue row says `in_live_set` "no" (ts_max 2026-10-23T06:00Z, 157,248 rows on the data machine); `series?table_name=eq.caiso_fuel_supply` returns `[]`. No rule of `warehouse/supabase/live_set.yaml` matches it.
  - `caiso_fuel_supply_history` (June 2018 to May 2025): under `catalogue_hold`, `[]` in `series`; it ends before the week in any case.
  - `generation_mix_hourly_caiso` is a source name (`erw:`), not a table; `[]` in `series`.
  - CAISO tables that are in the live set hold no total generation: `caiso_battery_storage` (batteries only), `caiso_curtailment_daily`, `caiso_reliability_daily`, `caiso_grid_emergencies`, `caiso_interconnection_queue`; `generation_mix_hourly_profile` and `generation_mix_records` ("review") are monthly and record rows.
- **Written down in two lines** in `docs/methods/generation_mix_hourly.md`, a new section "California's generation, EIA-930's and CAISO's own side by side: not built (chain 078, 24 October 2026)", with a Decisions block. California's hourly mix by fuel stays withheld (session 118); nothing on any page moves.
- **What opens it**: a `recent` rule for `caiso_fuel_supply` in `live_set.yaml` and a load (a data session's, the data lock's). Then this session's panel can be built as the chain file wrote it.

## What to review

1. Open `docs/methods/generation_mix_hourly.md` on the branch, the section named above: two paragraphs, no figure.
2. No page changed: nothing to open on production.
3. Screenshots: not taken, no build.

## Checks

- Anon reads: `series` for `caiso_fuel_supply`, `caiso_fuel_supply_history`, `generation_mix_hourly_caiso`: `[]` (HTTP 200); `eia930_all_generation`: rows (the read works). `catalogue` `table_name=like.caiso*` and `like.generation_mix*`: as above.
- `python -m unittest`, one at a time, the files that read the changed note and the join's test: `tests.test_session1162`, `1166`, `1167`, `133`, `94`, `78`: exit 0 each.
- No em dash in the note (grep count 0); the join's date is not written (test 78 passes).
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No node test added: no pure function was written (no fixture can be read from a table that is not in the live set).

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Nothing for this session at the combined landing (a note only).
- When `caiso_fuel_supply` is in the live set: the panel `grid_caisogen_caiso` as the chain file describes it (a later session).

## Decisions made without you

- Stopped at the condition, as the session's text says, rather than drawing the week from a committed file or the CSV: check-values could not recompute it from the live set, and no site file holds CAISO's own hourly week (`site/data/mixplus/caiso.json` is the mix views' build).
- The method note rather than the join's note (`eia930_caiso_break.md`): the panel was to sit on the Mix tab, whose note this is.

## For Samuel's ruling

- Whether to load `caiso_fuel_supply` into the live set (a `recent` rule, 35 days: about 13 variables times 840 hours, some 11,000 rows), so the Mix tab can draw CAISO's own total beside EIA-930's.

## Files

- Changed: `docs/methods/generation_mix_hourly.md` (the chain 078 section above).
- New: this report.
