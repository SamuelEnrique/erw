# Session 1171 report: revisions and preliminary figures, said

23 October 2026, on samueloldlaptop (the old laptop), session 1171 of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1171-grid`, cut from `wip/1170-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1171`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; two light reads of Supabase's REST API with the anon key (whether `series` rows carry a load time the anon role can read: they do).

## Read these first

- **Each Grid tab's data line now says EIA-930's figures are preliminary**, in one sentence, the same words on all four tabs, held in one constant (`EIA930_PRELIMINARY`, `site/lib/gridPreliminary.ts`, drawn by `site/components/grid/Preliminary.tsx`): "EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this page was drawn, so a later read of the same hour can differ."
  - Network and Gravity tabs (the network's source line, `components/grid/NetworkView.tsx`): the clock is written after "drawn", "(2026-10-24 09:15 UTC)", the same clock the lag line above already writes ("hours before this page was drawn").
  - Mix tab (the Now blocks' source line, `components/grid/NowView.tsx`): no clock in the words (the tab's source line wrote none).
  - Clean tab: it had no source line; it now has one (`app/grid/page.tsx`), naming the tables the tab reads from `lib/gridtables.ts` (the list its license line already shows), with the sentence.
  - Every tab carries the drawing time on the sentence's element, `data-eia930-drawn="<ISO>"`, for the checker. On the Gravity tab the sentence stands once (the Exchange blocks' source line under it does not repeat it).
- **check-values now tells a revised EIA-930 hour from a wrong figure.** Before: a revised hour failed the run as a value difference, like any other. The live set's `series` rows hold `loaded_at`, the load run that last wrote the row (`load.py` writes only new or changed rows), readable with the anon key. So for a key `series|eia930_<table>|<entity>|<variable>|<hour>` whose page value differs, check-values reads the row's `loaded_at` and `freq`: an hourly row rewritten after the page's drawing time, on a page whose text is its own value, is a `revised` line, on its own line and counted in the summary, and passes only for a table the method note names on its line "Revised hours tolerated by check-values: `eia930_all_demand`, `eia930_all_generation`." (check-values reads that line). A row written at or before the drawing time fails as before, the line adding "the row was last written ..., before the page was drawn ...: not a revision". Every other difference fails as before (no drawing time on the page, a sum, a max, a calc, a `net|` snapshot key, a table not named).
- **The rule** is in `site/scripts/check-revised.mjs`; check-values reads the row and the note. `check-methods.mjs`'s `keysFromValues` reads a `revised` line's key as it reads ok, late and FAIL lines.
- **No figure moves**: no key or value changed; the new words carry no number but the clock.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=miso&view=network`. Scroll to the grey source line at the foot of the network: "... EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this page was drawn (YYYY-MM-DD HH:MM UTC), so a later read of the same hour can differ." The clock is the one in the lag line above it.
3. Open `https://erw-flame.vercel.app/grid?grid=miso&view=gravity&shape=gravity`: the same sentence in the network's source line; the Exchange blocks' line below it does not repeat it.
4. Open `https://erw-flame.vercel.app/grid?grid=miso` (the Mix tab): the Now blocks' source line ends with the same sentence, without a clock.
5. Open `https://erw-flame.vercel.app/grid?grid=miso&view=clean`: at the foot of the tab, a new source line naming the tab's tables, then the sentence.
6. View source on any of them, search `data-eia930-drawn`.
7. Read `docs/methods/grid_network.md`, "Revisions, said and checked (session 1171)", and its Decisions.
8. Screenshots: not taken, no build.

## Checks

- `node site/scripts/test-check-revised.mjs` (new): exit 0, 12 tests: the rule's functions with a revised row (reported revised, passes) and a wrong row (fails, "not a revision"), a table the note does not name (fails, says so), the cases the rule leaves alone; then end to end, check-values run against a server of the test's own answering as the page and as Supabase's REST API: the revised hour a `revised` line and the wrong one a FAIL, exit 1; without the wrong one exit 0 with "1 EIA-930 hours revised" in the summary; the same figure with its row written before the drawing time fails; no floor written.
- Node tests that read the changed files, one at a time: `test-caiso-alerts`, `test-check-values-run`, `test-check-values-slow`, `test-grid-balance`, `test-grid-exchange`, `test-grid-keys`, `test-mix-hourly`, `test-scarcity-strip`: exit 0 each; `test-grid-file-keys`, `test-grid-reads`, `test-grid-replay` (with `--import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs`, through the junction): exit 0 each.
- `python -m unittest`, one file at a time, on the 106 test files that read `NetworkView.tsx`, `NowView.tsx`, `app/grid/page.tsx`, `check-values.mjs`, `check-methods.mjs` or `grid_network.md`: 106 of 106 exit 0. `tests.test_session323` (reads the Grid pack): exit 0.
- `tests.test_session1171` (new, 7 tests; it runs the node test): first run exit 1 (its own drift check counted the node test, which pins the words, as a second copy); the check now skips `test-*` files: exit 0.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values run against a page, no check-methods run: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build, check-values on `/grid,/network` (expected: no key changes; a revised hour, if the daily load rewrote one between the build and the run, now prints `revised` and passes), check-390 on the four tabs' source lines, the screenshots at 1280 and 390 under `docs/brand/review-1171/` (each tab's source line), the snapshots before and after, every difference listed (expected: the sentence in the source line of the Network, Gravity and Mix tabs of `/grid` and of `/network`'s redirect, and the Clean tab's new source line; nothing else).

## Decisions made without you

- **New words a visitor sees, on pages in review**: the sentence on revisions in each Grid tab's data line, and a whole new source line at the foot of the Clean tab (it had none), naming the 25 tables the tab reads (`lib/gridtables.ts`'s list).
- The clock is written into the words on the Network and Gravity tabs only, where the lag line already says when the page was drawn; the Mix and Clean tabs' sentence has none (each tab still carries it as `data-eia930-drawn`, unseen).
- On the Gravity tab the sentence is in the network's source line only, not repeated in the Exchange blocks' line under it.
- The revision is told by the row's `loaded_at` (the load run that last wrote it), not `retrieved_at`; a later `loaded_at` says the row may have moved, and the rule is asked only of a figure whose value already differs.
- The drawing time is the page's own clock in the render, not a build time (none is on the page or in the run's state); a read served from the fetch cache before a load and drawn after it fails, so the rule leans to a failure, never a pass.
- Tolerated tables: `eia930_all_demand` and `eia930_all_generation`, the two the Grid tabs key by the hour; any other EIA-930 table's revised hour fails with its line saying so, until the note names it.
- Only single-row keys are judged; a sum, maximum or window key (`series_sum|`, `series_max|`, `netbal|`) that moved with a revised hour still fails.
- A revised line counts among the values read and not among those that match, as the latest prices' superseded lines do.

## For Samuel's ruling

- Whether a figure over many hours (a 24-hour sum, a week's mean gap) that moved with one revised hour should be told apart too (it needs every row's load time in its window).

## Files

- New: `site/lib/gridPreliminary.ts`, `site/components/grid/Preliminary.tsx`, `site/scripts/check-revised.mjs`, `site/scripts/test-check-revised.mjs`, `tests/test_session1171.py`, this report.
- Changed: `site/components/grid/NetworkView.tsx`, `site/components/grid/NowView.tsx`, `site/app/grid/page.tsx` (the Clean tab's source line), `site/scripts/check-values.mjs` (the rule, the row's read, the summary), `site/scripts/check-methods.mjs` (`keysFromValues` reads `revised` lines), `docs/methods/grid_network.md` ("Revisions, said and checked"), `docs/reviews/packs/grid.md` (item 9).
