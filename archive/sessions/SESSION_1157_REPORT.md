# Session 1157 report: Ask your grid, on stored answers

23 October 2026, from 18:05 UTC, on samueloldlaptop (the code machine, the old laptop), session 1157 of `queue/done/077-day-23-october-code-grid-tool.md`, beside session 1151 (the Network and Clean tabs' keys) and chain 075. Branch `wip/1157-grid`, cut from `wip/1150-grid`, worktree `C:\Users\lossa\Documents\erw-1157`. Model spend USD 0: no model call in the page, the build script or a test.

## Read these first

- **The Ask panel of `/grid` now shows stored answers under the live box**, for the grid on screen: up to five, each a closed `<details>` (the question as its summary), holding the answer as stored, each figure with the table and filter of the call that returned it and the day it was asked, and the run it came from (file, question id). The panel is `data-grid-panel="grid_ask_<grid>"`. The live box (`components/grid/AskView.tsx`) and its routes are not touched.
- **Where they come from:** `site/data/grid_ask_examples.json`, written by `site/scripts/build-grid-ask-examples.mjs` from `warehouse/chat/eval/eval_s302_fixtures.json` (19 October) and `eval_s267_fixtures.json` (14 October), the two recorded runs that kept every tool call with its result. `eval_s320_first_run.json` kept the count of calls only, so none of its figures can be traced: it is left out whole, and the file says so. The `results/*.jsonl` runs kept no results and no grade either.
- **What is kept:** graded right by its run (verdict right, grade ok), one grid (the five comparisons of two grids are left out), every figure of the answer found in a non-error tool result at the rounding it is written to (the number check of `lib/chat/ask.ts`, ported; dates, years, list markers and the question's own numbers are not figures). Order: the route the panel itself sends first (ERCOT the panel's profile, the Lower 48 the general chat, the others the grid's own chat), then the newest run, then answers with figures before refusals.
- **What a reader sees, by grid, today:** ERCOT 5 (of 23 usable), CAISO 5 (of 10), SPP 5, ISO-NE 4 (two shown, two refused), NYISO 4 (all four refused), PJM 2 (one refusal "not in the warehouse", one carbon answer), the Lower 48 3, MISO 1 (the paused-MISO refusal). Fewer than five is said in words: "Four stored answers for NYISO so far".
- **Held tables:** `lib/gridask.ts` applies `lib/license.ts` on the day the page is drawn. An example any figure of which comes from a table held for its grid (`licenseHeldRow`, the figure's entity, or the example's grid when the call named no grid's entity) is not shown; in its place the live Ask's words for that read, `licenseReason(table)` (what `lib/supabase.ts` LicenseNeeded gives the tools): "license needed: ISO-NE; MISO; NYISO: the publisher's own page asks for permission; none is recorded yet."
- **No `data-check` key:** these are stored texts of a past evaluation, not figures read from the database, so check-values has nothing to recompute in them; the panel carries `data-ask-stored="1"` and says the figures are as of the day asked.

## What to review

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=spp#ask`. Under the Ask box, "Stored answers": "Five stored answers for SPP". Click the first question: the answer, then one line a call ("24.78: cost_of_power_monthly, query with aggregation=..., read 19 October 2026."), then "From session 302's evaluation ...: warehouse/chat/eval/eval_s302_fixtures.json, question q17."
3. Open `https://erw-flame.vercel.app/grid?grid=nyiso#ask`: "Four stored answers for NYISO so far". Click any: the license words in place of the answer, and the table it read.
4. Open `https://erw-flame.vercel.app/grid?grid=isone#ask`: two carbon answers shown, two refused.
5. Open `https://erw-flame.vercel.app/grid?grid=miso#ask`: "One stored answer for MISO so far", the paused-MISO refusal, "No figure".
6. Open `https://erw-flame.vercel.app/grid?grid=ercot#ask`: the Ask ERCOT box first, then five stored answers of the panel's own profile.
(Each address shows this only once the chain's combined landing has deployed; until then read it on `wip/1157-grid`.)

## Checks

- Precheck for session 1157: run by the orchestrator, exit 0.
- `node site/scripts/build-grid-ask-examples.mjs`: exit 0 (ercot 5 of 23 usable, caiso 5 of 10, pjm 2, miso 1, nyiso 4, isone 4, spp 5, us48 3); `--check`: exit 0.
- `node --import ./scripts/alias-register.mjs scripts/test-grid-ask.mjs`: exit 0, 269 of 269 (the committed file is the build's; five or fewer a grid; each example graded right, its question and answer as stored, every figure in a non-error tool result of its own run; fixtures for a wrong grade, an untraced figure, a figure only an error held, a comparison, a run without results, dates; at most five with the panel's route first; NYISO all held after 21 October and none before; ISO-NE's carbon kept; a table held whole held for any grid; the count's words; no model, request or chat module imported).
- `node --import ./scripts/alias-register.mjs scripts/test-session502.mjs`: exit 0, 11 of 11.
- `python -m unittest tests.test_session1157`: exit 0 (6 tests, the node test and `--check` among them); `tests.test_session137`, `test_session168_network`, `test_session299`, `test_session473`, `test_session502`, `test_session538` (the tests that read `app/grid/page.tsx` or the grid components): each exit 0.
- `npx tsc --noEmit -p .` in `site/`: exit 0 (after `npm run content` and `npx next typegen`, which a fresh worktree needs: without them it reports the generated files and `PageProps` missing, none of them this session's).
- `scripts/db_probe.py`: exit 1 from the worktree (no `.env` there), then exit 0 from the main copy at 18:15 and 18:18 UTC (0.57 s, 0.45 s), so a build was allowed.
- `scripts/buildlock.py acquire 1157-grid`: waited for 1151-grid, held from 18:17:52 UTC; released (exit 0) after the build and the reads.
- `npm run build` in the worktree: exit 0; no "statement timeout" in its log.
- The eight `/grid?grid=<grid>` pages of that build, through the internal view (`next start -p 3157`): each 200; each has its `data-grid-panel="grid_ask_<grid>"`, after the live box; examples ercot 5, caiso 5, pjm 2, miso 1, nyiso 4 (4 held), isone 4 (2 held), spp 5, us48 3; no `data-check` inside the panel; no em dash on the pages.
- check-values not run: no figure was added or changed, and the panel holds none.
- Screenshots under `docs/brand/review-1157/`: before (production, `#ask`) `before-spp-1280.png`, `before-spp-390.png`; after (the local build) `after-spp-1280.png`, `after-spp-390.png`, `after-nyiso-1280.png`, `after-nyiso-390.png`, and with the first answer opened `after-spp-390-open.png`, `after-nyiso-1280-open.png` (the license words in place).

## The landing

- None: waits for the chain's combined landing (the sessions stack on one another's branches, as the chain note records).

## To finish

- Land `wip/1157-grid` with the chain's combined landing: `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the commit, `compare` (expected: the Ask panel of every `/grid` page gains the "Stored answers" block; no figure moves).
- When a later evaluation records its tool results (chain 075's), run `node site/scripts/build-grid-ask-examples.mjs` after adding the file to `RUNS` in the script; the test's `--check` fails until the data file is rebuilt.

## Decisions made without you

- Only runs that recorded each tool call's result are used (s302, s267); s320's 30 answers, 17 of them graded right, are left out because no figure of theirs can be traced to a tool result. The data file names the file and the reason.
- Dates and clock times ("2025-05-01", "1 May 2025", "16:00") are not counted as figures; years and list markers neither, as `lib/chat/ercot.ts` already treats years. Every other number of an answer must be in a tool result of its own run.
- A comparison of two grids (s302 q21 to q25) is shown for neither grid: "for the selected grid" read as about that grid alone.
- Refusals graded right ("not in the warehouse") are shown, after the answers with figures; they carry no figure.
- The refusal words are `licenseReason(table)`, the sentence the live Ask's tools receive for a held read (`lib/supabase.ts` LicenseNeeded), followed by the table's name; `lib/chat/` is not imported or edited.
- When a call named no entity of a grid (eia930:ISNE, a market filter, none), the figure's grid for the hold is the example's own grid.
- The examples sit in a new component, `site/components/grid/AskExamples.tsx`, drawn by `site/app/grid/page.tsx` right after `AskView`; `AskView.tsx` is unchanged.
- The source file hashes in the data file are of the text with LF line ends (git's blob), so a Windows checkout and the Linux runner agree.

## For Samuel's ruling

- None new.

## Files

- New: `site/components/grid/AskExamples.tsx`, `site/lib/gridask.ts`, `site/data/grid_ask_examples.json`, `site/scripts/build-grid-ask-examples.mjs`, `site/scripts/test-grid-ask.mjs`, `tests/test_session1157.py`, `docs/brand/review-1157/` (eight screenshots), this report.
- Changed: `site/app/grid/page.tsx` (two lines: the import and `<AskExamples grid={grid} />` after the live box).
