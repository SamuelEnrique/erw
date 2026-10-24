# Session 1168 report: how hard the system works, in the Mix tab

23 to 24 October 2026, on samueloldlaptop (the old laptop), the fifth session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1168-grid`, cut from `wip/1167-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1168`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher.

## Read these first

- **The four measures of `docs/methods/grid_stress.md` are charts with a point a year** on the view "How hard the system works" (`/grid?view=mix&mix=stress`, `components/mix/views.tsx` `StressView`), the values picked from the committed file `site/data/stress/<grid>.json` by a new pure file, `site/lib/gridStress.ts`:
  1. **The evening ramp**: the chart that stood (bars for one grid, a line a grid in two cards for several), its series and values as they were; its hover now adds the year's MW in one hour with the hour it started, over three hours, and the peak demand.
  2. **The lowest net load** (new block under it, "The lowest net load of each year, as a share of peak demand"): a line a grid, the share to one decimal on hover, with the MW, the hour and the peak.
  3. **The tightest hours** (new chart above each grid's fuel table): each fuel's output in the year's 100 tightest hours as a share of installed capacity, a line a fuel, by year; the hover adds the hours' mean net load.
  4. **Dark, calm stretches** (new chart above each grid's table): the longest stretch of each year, in hours; the hover adds when it began, the energy missing, the battery fleet's hours at full power and the year's dark, calm hours.
- **The tip**: every one of these charts' hover cards ends with the line of what the figure is not, and a link under each chart, "What this chart is not", carries the line on hover and opens the method note's new section `#what-each-chart-is-not-session-1168`. The lines for the tightest hours and the stretches are the note's "What the figures are not" in short; that section had no line for the ramp or the lowest net load, so two were written from the note's own definitions (ruling 2).
- **Keys**: the two large tables are keyed whole through `Num` with session 1166's kind (`fmt|<form>|file|stress/<grid>.json|years.<year>.<variable>`): the fuels in the tightest hours (mean MW, capacity, share) and the dark, calm stretches (all seven figures), and "The longest" (words such as "4 days 5 hours") in a new form, `span`, in the grid's table and in "The seven grids". **612 keys added** (616 to 1,228 over the seven grids drawn one at a time: 91 for CAISO, ERCOT, ISO-NE, MISO; 84 NYISO; 90 PJM; 74 SPP). `test-grid-file-keys.mjs` (every view, every grid, every key recomputed from the file) ran in **1.37 s before, 1.71 to 1.77 s after**. check-values adds no request: its table comparison reads one row set per grid and year (`fileTableRows`), which the ramp table's keys already read.
- **Held grids**: `grid_stress_yearly` is public in `site/data/license_status.json` (from EIA-930, EIA-860M and `storage_buildout_monthly`, all public); `lib/gridHeld.ts` holds no stress figure. Every grid is drawn, said in the note. The node test asserts the table is not held for any of the seven.
- **No figure that stood moved**: a one-off comparison (scratch, not committed) drew every view of the Mix tab with the branch's former `views.tsx` and the new one, for each grid, two selections of several grids and three years: 30,417 table cells, all equal in text; every view but the stress view byte for byte the same HTML; the stress view gains one heading, the charts and the four links.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=mix&mix=stress`. Hover the first chart's 2025 bar: "In one hour 19.07 % of peak demand", the note "in one hour 15,940 MW, starting 19 January 2025, 16:00; over three hours 27,450 MW; peak demand 83,597 MW", then the line "Not a reliability study: ...". Hover "What this chart is not" under it: the same line; click it: the method note's section.
3. Same page, "The lowest net load of each year, as a share of peak demand": hover 2025: "Lowest net load 11.5 % of peak demand", "9,586 MW, 2 March 2025, 09:00; peak demand 83,597 MW", the line "One hour, not a level held: ...".
4. Scroll to "ERCOT: what each fuel gave in the 100 tightest hours, 2025": the chart by year above the table (solar from 71.1 in 2019 to 5.0 in 2025, on hover); the table's figures dotted, hover names `grid_stress_yearly, iso:ercot` and the file.
5. "ERCOT: dark, calm stretches, by year": the chart of the longest stretch; the table's figures and "The longest" dotted.
6. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=mix&mix=stress&grids=ercot,caiso,spp,pjm` (or pick four grids): the ramp's two cards and the lowest net load a line a grid, each hover naming each grid's MW; a tightest-hours and a stretches chart for each grid.
7. Open `https://erw-flame.vercel.app/grid?grid=isone&view=mix&mix=stress`: ISO-NE drawn (public table).
8. View source, search `fmt|span|` and `data-stress-not`.
9. Screenshots: not taken, no build.

## Checks

- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-stress.mjs` (new, 7 tests): exit 0.
- `... scripts/test-grid-file-keys.mjs` (two tests added, none changed; 14 tests): exit 0, 1.71 s (1.37 s before the change).
- `... scripts/test-grid-held.mjs`: exit 0. `node --import ./scripts/alias-register.mjs scripts/test-ask-ready.mjs`: exit 0. `test-mix.mjs`: exit 0. `node scripts/test-check-values-run.mjs`: exit 0. `node --check scripts/check-format.mjs`, `scripts/check-values.mjs`: exit 0.
- `python -m unittest`, one file at a time, each exit 0: `tests.test_session1168` (new, 7 tests, it runs both node tests) and the 31 files that read a changed file or walk `site/lib` or `site/components`: 1162, 1166, 1167, 123, 133, 144_page, 154_page, 156, 157_page, 168_mix, 215, 241a, 241c, 306, 317, 324, 411, 473, 188_waits, 78, 149, 161, 177, 182_flow, 196, 238, 258, 274, 301, 355, 502.
- Every new key named by the method notes: check-methods' own `figures()` and `named()` over the 1,228 keys against `grid_stress.md` and `generation_mix_hourly.md`: first 14 not named (the fuels' MW and capacity), the note's list written out (`tight_<natural_gas, ...>_mw`), then 0.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values or check-methods run against a page, no check-links: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build; check-values on `/grid,/network`, and, if wanted, `/grid?grid=ercot&view=mix&mix=stress` and the other views' addresses with floors (they are not in its list today: session 1166's note); expect "same" lines for the 612 new stress keys; the floors rewritten from a passing restricted run (`CHECK_VALUES_WRITE_FLOOR=1`); `check-methods.mjs --values <the run> --write`; check-links (the new anchor `#what-each-chart-is-not-session-1168`); check-390 on the stress view (four charts a grid); screenshots at 1280 and 390 under `docs/brand/review-1168/` (each chart with its hover card); the snapshots before and after, every difference listed (expected: on the stress view only, the new heading, the charts, the four links and the dotted rule under the keyed cells; no word or number of a table moves).

## Decisions made without you

- The ramp's chart kept as it stood (bars for one grid, its series, its hover's values to two decimals); the new charts give one decimal on hover, as the tables (ruling 1).
- The lowest net load drawn as a share of peak (as the ramp and "The seven grids" compare grids), the MW on hover.
- Two lines written for the ramp and the lowest net load, in a new section of the note; "What the figures are not" left as it stood (ruling 2). The join's date in the net load line is `caisoJoinDay()` (test 78: one constant).
- The tightest hours and the stretches drawn per grid above each grid's table; the ramp and the lowest net load across the grids chosen, as the ramp's chart was.
- The line in the hover card and on a link's hover, not written on the face (the view's rule since session 133, `test_the_page_face_carries_no_method`).
- `Lines` and `Bars` (`components/mix/Charts.tsx`) take two optional props, `notes` and `tip`, off by default; `Series` takes `digits`. No other chart passes them, so no other card moves.
- The large tables keyed whole (no added request, 0.4 s of the node test); "The longest" keyed in a new form `span`, a copy of `lib/stress.ts span` in `check-format.mjs` (no import there), pinned line for line by `tests/test_session1168.py`.
- The hours of each record ("When it started", "When", "It began") stay unkeyed: times, as session 1166 left them.

## For Samuel's ruling

1. The ramp chart's hover gives two decimals ("19.07 % of peak demand") where the table gives one ("19.1%"). Recommendation: one decimal (a hover only; no figure on the face moves).
2. The two lines written for the ramp and the lowest net load (the note's section "What each chart is not (session 1168)"). Recommendation: keep, or word them; they could also join "What the figures are not".
3. A finding, not changed: the note's "As built on 5 October 2026" says California 2019 and 2020 are not written; the committed file `site/data/stress/caiso.json` holds both (and the view draws them). Recommendation: rebuild the "As built" lines from the table at the next data session.

## Files

- New: `site/lib/gridStress.ts`, `site/scripts/test-grid-stress.mjs`, `tests/test_session1168.py`, this report.
- Changed: `site/components/mix/views.tsx` (`StressView`, the `span` form), `site/components/mix/Charts.tsx` (`notes`, `tip`, `digits`), `site/scripts/check-format.mjs` (`span`), `site/scripts/test-grid-file-keys.mjs` (two tests added), `docs/methods/grid_stress.md` (three subsections and a Decisions block in the chain 078 section).
