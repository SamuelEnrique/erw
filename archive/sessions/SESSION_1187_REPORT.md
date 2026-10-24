# Session 1187 report: the stored answers, refreshed

23 October 2026, from 22:15 UTC, on samueloldlaptop (the code machine, the old laptop), unattended, session 1187 of chain 091 (`queue/done/091-day-25-october-code-grid-tool-3.md`). Branch `wip/1187-grid`, cut from `wip/1186-grid`, worktree `C:\Users\lossa\Documents\erw-1187`. Model spend USD 0: no model call in the script, the page or a test. Code, tests and documents only: no build, no server, no browser.

## Read these first

- **Chains 075 and 076 recorded four later runs that keep every tool call with its result** (the `trace`, session 1111's record), asked through `/api/ask` on 23 October: `eval_s1113_run.json` (session 320's thirty, 19:29 UTC), `eval_s1114_run.json` (session 1114's thirty, 19:43 UTC), and session 1133's two askings again, `eval_s1133_s320_run.json` (22:49 UTC) and `eval_s1133_s1114_run.json` (eight of 1114's set, 23:05 UTC). Their grades are in files of their own (`eval_s1113.py --grade`), not in the run: `eval_s1113_grades.json`, `eval_s1114_grades.json`, `eval_s1133_s320_grades.json`, `eval_s1133_s1114_grades.json`. Each grade row matches its run's question (status, count of calls, seconds, cost) for all 98 questions.
- **All four are added to `RUNS`** in `site/scripts/build-grid-ask-examples.mjs`, newest first, each with its `grades` file and its session (1133, 1133, 1114, 1113); `site/data/grid_ask_examples.json` rebuilt; `--check` passes.
- **How the files reached the branch:** `origin/main` merged into `wip/1187-grid` first (commit `f2b163cf`, a clean merge, 405 commits of main), so the script reads the eval files from the branch itself, as it does the older ones, and the CI `--check` has them.
- **The selection rule is unchanged** (graded right, every figure in a tool result of its own run, one grid, held tables dropped on the day by `lib/gridask.ts`, five a grid at most, the panel's route first, then the newest day, then figures before refusals, then id). Built with the old three runs only, the new script gives the committed file byte for byte.
- **Two additions, written in the script's head and tested:**
  - `joinGrades`: a run whose grade is in a file of its own has it joined by id, a row used only when it is of that asking. Right is the grade on the keys: `ok` with `grade.ok` (1114's set), `now_ok` with `grade_now.ok` (320's set). Right only under the hold (a license refusal: g07, g08, d05, d07) or only with session 320's rulings (b01 to b06, b08, b09, g03, g06, d10) is left out, and the file says which.
  - `newestAskings`: when two runs asked the same words, one asking is kept before the order: the panel's own route first (as before), then the latest asking by its time, then the later session. So SPP's t01 shows session 1133's asking, not 1114's.
- **What a reader sees, by grid, before and after:** ERCOT 5 of 23 usable, now 5 of 44 (the same five, the panel's own profile first); CAISO 5 of 10, now 5 of 17 (all five from 23 October); SPP 5 of 5, now 5 of 9 (four from 23 October, s302 q17); the Lower 48 3, now 5 of 6 (p02, p09, p10 added); MISO 1, now 2 (session 1133's paused-MISO refusal added); PJM 2, NYISO 4 (all held), ISO-NE 4 (two held): unchanged.
- Answers that name "EIA-930" are left out (d01, d02, d08, d09, and 1133's d03): the number check reads 930 as a figure no tool returned. The rule is the site's own (`lib/chat/ask.ts` numbers), so it is kept; 1113's d03 is shown in place of 1133's.

## What to review

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=caiso#ask`. Under the Ask box, "Five stored answers for CAISO": each says "From session 1113's evaluation" (or 1114's, 1133's), asked 2026-10-23, and names its run file, e.g. `warehouse/chat/eval/eval_s1114_run.json`, question f02.
3. Open `https://erw-flame.vercel.app/grid?grid=spp#ask`: the fourth is t01, from session 1133's asking (`eval_s1133_s1114_run.json`), not session 1114's.
4. Open `https://erw-flame.vercel.app/grid?grid=us48#ask`: "Five stored answers for the Lower 48" (was three).
5. Open `https://erw-flame.vercel.app/grid?grid=miso#ask`: "Two stored answers for MISO so far", both the paused-MISO refusal.
(Each address shows this only once the chain's combined landing has deployed; until then read it on `wip/1187-grid`.)

## Checks

- Precheck for session 1187: run by the orchestrator, exit 0.
- `git merge origin/main`: exit 0, no conflict.
- `node scripts/build-grid-ask-examples.mjs --check` before the change (after the merge): exit 0. The new script on the old three runs: the committed file exactly.
- `node scripts/build-grid-ask-examples.mjs`: exit 0 (ercot 5 of 44, caiso 5 of 17, pjm 2 of 2, miso 2 of 2, nyiso 4 of 4, isone 4 of 4, spp 5 of 9, us48 5 of 6); `--check`: exit 0.
- `node --import ./scripts/alias-register.mjs scripts/test-grid-ask.mjs`: exit 0, 349 of 349 (was 269; added: each new run in RUNS with its grades file, hashed, every answer traced; RUNS newest first; the hold-only, rulings-only and wrong answers left out with their reason; SPP t01 the newer asking; no shown example with a newer kept asking of the same words by the same route; `joinGrades` on fixtures, both forms of grade, a row of another asking, a missing row, `ok` without `grade.ok`; the order rule on fixtures: the later asking whatever the read order, the later session at the same time, the panel's route before a newer asking by another route, one usable question, refusal either side). The one changed assertion ("graded right by its run") reads the grades file for a run that has one, the run file otherwise.
- `python -m unittest tests.test_session1157`: exit 0 (6 tests; extended: the four runs read, each with its grades file, each with answers kept). `tests.test_session1158`: exit 0 (8). `tests.test_session1161`: exit 0 (9).
- `npm run content`, `npx next typegen`, `npx tsc --noEmit -p .` in `site/` through the junction: each exit 0; the junction removed with `cmd /c rmdir`.
- No build, no server, no browser, no screenshot (chain 078's rule).

## The landing

- None: waits for the chain's combined landing, with chain 077's landing B and chain 078's.

## To finish

- Land with the chain: `wip/1187-grid` carries the merge of `origin/main` at 22:17 UTC, so the next sessions stack on it as before.
- When chain 075 or 076 records another run with a trace: add it to the top of `RUNS` (with `grades` if its grade is in a file of its own), run `node site/scripts/build-grid-ask-examples.mjs`, then `--check`.

## Decisions made without you

- Graded right for these runs is the grade on the keys, not under the hold and not with session 320's rulings taken the answers' way: a license refusal is right only while the hold lasts, and the panel already puts the license words in place of a held answer on the day.
- A grade row is used only when its status, count of tool calls, seconds and cost equal the run's question (session 1133's grades file says "eval_s1113_run.json graded" in its `_about`, a wrapper's rename; the rows match 1133's run, not 1113's).
- The newest asking of the same words is kept by its full time, not its day, because the four runs were all asked on 23 October; the order of the five is the day rule as before.
- `origin/main` merged into the branch, rather than the script pointed at main's files: the run files then live where the script and CI read them.

## For Samuel's ruling

- None new.

## Files

- Changed: `site/scripts/build-grid-ask-examples.mjs` (four runs in `RUNS` with `grades`, `joinGrades`, `newestAskings`), `site/data/grid_ask_examples.json` (rebuilt), `site/scripts/test-grid-ask.mjs` (80 assertions added), `tests/test_session1157.py` (one test extended), this report.
- Merged from main: `warehouse/chat/eval/eval_s1113_*`, `eval_s1114_*`, `eval_s1133_*` among main's 405 commits (read only).
