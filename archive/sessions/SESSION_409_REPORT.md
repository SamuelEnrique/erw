# Session 409 report: the method notes against the pages

21 October 2026, about 03:10 to 04:35 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-409` on `wip/409-s` (cut from `wip/381-382-land` at `61c4c309`). The chain `queue/done/015-day-20-october-code-pm.md`, "Session 409". Three helper agents wrote part of the notes' lines from the pages' code (the brief: `runs/chain_oct21/s409/BRIEF_NOTES.md`); this session wrote the rest, the script, its test and this report, and read every helper's lines before the commit.

## Read these first

- **`site/scripts/check-methods.mjs`** lists, for every page of `site/scripts/check-values-floor.json` whose code links a method note, each figure the page shows (by its check-values key) and whether a note of the page names it. It exits 0 when every figure is named, 1 when one is not, 2 when its input cannot be read. Its header states the rule in four parts: which notes are a page's (the `/data/methods/<slug>` links of the page's code whose words hold "method", or "Every number, step by step"), what a figure is (a table and a variable, or a family of the page's own arithmetic such as `bs|` and its measure), what "named" means (the note holds the table and the variable, or the family as a key starts it and the measure, as whole words), and where the keys come from.
- **It runs without a site.** With no argument it reads `site/scripts/check-methods-keys.json`: one key a figure a page, written with `--write` from the check-values run that wrote the floor at 20 October 23:15 UTC (`runs/chain_oct20d/s372land/values_floor.out`). With a base URL it reads the pages as check-values does (the internal cookie posted, never in an address); with `--values <file>` it reads a check-values output. Both together merge.
- **21 method notes gained a last section, "The figures on the page and their keys"**: 469 of 469 figures of 47 pages are now named (before: 194 of 468). Every line says what the page shows and where, from the code that draws it: the label, the table and variable it reads, or the arithmetic. No data number was added; the game's fleet constants (10,000 homes, 5 kW, 13.5 kWh) and "the 15 states" are the code's own constants as the page prints them.
- **One caveat on the keys file**: check-values reports a key once, under the first page that carried it, so from its output a key two routes share is listed for the first only (the home page takes the latest prices and some storage figures). The script lists each figure once a route, so the query views of one page add up; a read of the running site gives every page its own keys. That read waits: the site did not build tonight (three tries, each stopped by Supabase statement timeouts on the home page's required reads), so it is under "To finish".

## What to review

- The script: `https://github.com/SamuelEnrique/erw/blob/wip/409-s/site/scripts/check-methods.mjs` (the rule is its header).
- The notes, each at its end: `docs/methods/` on `wip/409-s`: `flex_alert_scorecard.md`, `shoulder_hours.md`, `datacenter_cost.md`, `datacenter_facilities.md`, `cost_of_power.md` (the AI gigawatts draft), `storage.md`, `generation_mix_hourly.md`, `grid_network.md`, `price_board.md`, `battery_game.md`, `battery_earns_algorithm.md`, `generator_earns_algorithm.md`, `economic_impact.md`, `energy_deals.md`, `energy_projects.md`, `event_study.md`, `automated_analysis_findings.md`, `automated_analysis_scanner.md`, `bill.md`, `consumption.md`, `power_prices.md`. On the site after a landing: `/data/methods/<slug>` for each.
- No page changed: nothing under `site/app/`, `site/components/` or `site/lib/` was touched, so no screenshot was taken.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s409/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `npm ci` in the worktree's `site/` (under the mutex) | 0 | |
| `npm run build`, try 1 (03:30 to 03:48) | 1 | "Export encountered an error on /": `Supabase entities: HTTP 500 ... statement timeout` (14 timeouts in the log); the mutex was let go |
| `npm run build`, try 2 (03:59 to 04:06; 11 minutes after try 1, when the mutex came free) | 1 | the same, `Supabase series: HTTP 500 ... statement timeout` (11 in the log) |
| `npm run build`, try 3 (04:22 to 04:27) | 1 | the same (23 timeouts); no server was started, nothing listens on port 3409 |
| `node scripts/check-methods.mjs --values .../values_floor.out` before the notes | 1 | 194 of 468 figures named; 274 MISSING (47 pages) |
| `node scripts/check-methods.mjs --values .../values_floor.out --write` (the keys file) | 0 | 469 of 469 |
| `node scripts/check-methods.mjs` (offline, the keys file) | 0 | 469 of 469 figures named by a note of their page; 47 pages checked |
| `tests.test_session409` | 0 | 6 tests OK |
| The tests near the change after the fix (`test_session178`, `196`, `253`, `301`, `409`, `190`, `298`, `235`, `263`) | 0 | 123 tests OK |
| Whole suite, `ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests` (04:07 to 04:14) | 1 | 4,788 tests, 5 failures: `test_session156` (the ask fixtures, the rules' known failure tonight), and four of this session's own, fixed in `43fd0b46`: the step-by-step notes must end with "Cross-checks" (178, 196, 253: the figure lines moved into section 4 as 4.12 and 4.20) and a script that calls `unlockPost` must import it from `./browser.mjs` by name (301). The whole suite was not run again; the nine modules above were |
| `duty.py beat` before each build | 0 | |

## Decisions made without you

1. **The keys file is the offline input, not the floor file.** The floor file holds a count a page, not its keys; the prompt's note took it to hold them. The script takes its pages from the floor file and its keys from `check-methods-keys.json` (one key a figure a page, about 80 KB), which `--write` writes from a site read or a check-values output. `check-values.mjs` was left as it is, so no other session's work on it collides.
2. **A page's notes are every note its code links with a word "method"** (or "Every number, step by step"), in its `page.tsx` and every file of `app/` or `components/` it imports, an address that redirects in `next.config.ts` read at its destination. `/grid` therefore has ten notes (each of its views links its own), and a figure is named when any of them names it; each line was put in the note whose link stands nearest the figure in the code.
3. **"Named" is the table and the variable, or the family and the measure, as whole words.** A label alone does not count: the notes do not quote the pages' labels, and a label moves with a page's wording. A number in a name may be written as a placeholder (`rt_mean_h<hour>`), and a list in angle brackets (`year_mean_<a, b>`) names each, as `shoulder_hours.md` already wrote them.
4. **The Digest's chart of the day is a family** (`digest_chart|`), not a table figure: its table is the day's chart's, so a note cannot name every table it may be. The line names the record's figures from `numbers_from_flag` of the scanner.
5. **The lines are one new section at each note's end**, headed "The figures on the page and their keys" (numbered where the note numbers its sections), not spread into the sections above: a reader of the note sees the figures in one place, and a later session can move a line up.
6. **Pages with no method link are listed, not failed**: `/`, `/data`, the five problem sets, `/prices/ercot%3AHB_HUBAVG`, `/reports/draft/shape-premium`, the two research cards and `/roundup`. Pages whose keys are not in the file (none at the end) would be listed too.
7. **The notes commit says 22 notes; it is 21.** Not amended.
8. **Three placements by the helpers, kept**: the figures of the Mix tab's latest hour and of "yesterday" (`components/grid/NowView.tsx`, `Conditions.tsx`) link no note of their own and went into `generation_mix_hourly.md`, the Mix view's note; the "In the news" block (`gridnews|`) links none and went into `datacenter_facilities.md`, whose link stands just above it (the line says so); the build-out tab's figures went into `storage.md`, which names `storage_buildout.md` as their method.
9. **In the two step-by-step notes** (`battery_earns_algorithm.md`, `generator_earns_algorithm.md`) the lines are subsections 4.12 and 4.20 of "Every number on the page", not a last section: three earlier tests hold "Cross-checks" as those notes' last section.
10. **The second build came 11 minutes after the first**, not 15, when the mutex came free; the third came 15 minutes after the second.

## For Samuel's ruling

- Whether a page with no Method link (the home page, `/data`, the problem sets, a price's own page, the research cards, the Roundup) should link one; check-methods passes them by.
- Whether a figure's label on the page should also count as naming it (rule 3 counts the table and variable only).
- Whether the step-by-step notes of the cost-of-power tools should carry the figure lines rather than the Method notes: the script accepts either, and the helpers put the datacenter page's lines in `datacenter_cost.md`.

## To finish

- **The landing checks.** `docs/machines.md` lists no landing checks (its "Code work" section names the workflow's), so the script is named here. In the orchestrator's `runs/chain_oct20d/land_checks.sh` (outside git), add `check-methods.mjs` to the scripts named after the port: `bash runs/chain_oct20d/land_checks.sh <label> <port> check-methods.mjs`. The script then reads every page of the floor at the landing's server and exits 0 when every figure is named. It also runs with no server: `cd site && node scripts/check-methods.mjs > ../runs/<label>/check-methods.out 2>&1; echo exit=$?`.
- **The keys file after a landing's floor is written**: `cd site && node scripts/check-methods.mjs http://localhost:<port> --values ../runs/<label>/values_floor.out --write > ../runs/<label>/check-methods-write.out 2>&1; echo exit=$?`, then commit `site/scripts/check-methods-keys.json`.
- **The site read of every page's keys** (the build did not pass tonight): under the mutex, `cd site && npm run build > ../runs/chain_oct21/s409/build4.out 2>&1; echo exit=$?`, then `npx next start -p 3409`, then `node scripts/check-methods.mjs http://localhost:3409 --values ../../erw/runs/chain_oct20d/s372land/values_floor.out --write > ../../erw/runs/chain_oct21/s409/cm_site.out 2>&1; echo exit=$?`. A figure the site read adds that no note names prints as `MISSING`: write its line in the page's note as the others are written, run the script again until it exits 0, commit `site/scripts/check-methods-keys.json` and the notes, and stop the server on port 3409.

## Files

- `site/scripts/check-methods.mjs` (new), `site/scripts/check-methods-keys.json` (new), `tests/test_session409.py` (new).
- The 21 notes above, each with one new section at its end (`datacenter_facilities.md` and `energy_projects.md` two: one for their own page, one for `/grid`).
- This report.
