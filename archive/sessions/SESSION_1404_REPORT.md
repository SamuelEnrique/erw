# Session 1404 report: the Grid's source-text tests, sturdier

24 October 2026, from about 06:40 to 07:00 UTC, on samueloldlaptop (the code machine, the old laptop), the fifth session of `queue/done/100-day-26-october-code-grid-tool-4.md`. Branch `wip/1404-grid`, cut from `wip/1403-grid` (sessions 1152 to 1403 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1404`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher, and no Supabase read: everything ran on committed fixtures. The session's agent could not write this file (the harness refused the write); the orchestrator committed it from the agent's text.

## Read these first

- **The inventory.**
  - 69 python test files read Grid tool source files (`site/app/grid/`, `site/app/network/`, `site/components/grid/`, `site/components/mix/`, `site/lib/grid*`, `network*`, `mix*`, `scarcityStrip`, `caisoAlerts`, `ercotNotices`, `cleanWeek`, `lower48`) and assert text in them: **751 assertions**, or 869 strings once the `for w in (...)` loops are expanded.
  - **Pins (a word-for-word line): 530.** 488 pin a line of markup or code, 42 a plain sentence.
  - **Rules: 221.** 105 say something is absent, 39 say no em dash, 4 match a pattern, 55 count, 18 hold an order.
  - The counts come from a script that traces each assertion's haystack back to a read of a Grid file, not from a grep. Data assertions on a run's output are not counted.
- **`site/scripts/test-grid-render.mjs` (new).** 66 cases, a panel and a grid kind each, plus 2 checks of the cases themselves: 68 of 68 hold.
  - Each case draws `/grid` on the committed fixtures and checks: the block's name; its own figures by key kind and count, each with a value; its rendered words (the pinned sentences, then its headings, else its first sentence); its held lines ("license needed" and the reason on hover); its anchor, method link and files.
  - Grid kinds: ERCOT (an ISO with prices), CAISO, ISO-NE as the held grid, MISO as the held grid on the Clean tab (the fixture holds MISO's week, not ISO-NE's), the Lower 48, and PJM where a panel has a "no price held" line.
  - Panels: network, balance, replayed day, gravity, Exchange, gravity day, clean24, cleanweek, mix (hourly and by month), hubprice, scarcity, caisoalert, ercotnotice, ISO-NE's two held lines, stress, ask. 8 older blocks are cases only where a pin reads them.
  - A family check fails when a `grid_<panel>_` family drawn on these pages has no case.
- **`site/scripts/grid-render-standin.mjs` (new).** Session 1182's stand-in for PostgREST and Storage and its walk, on the same fixtures; it also keeps each block's words, its hover words, its headings and the id of the element that holds it alone. Two existing fixtures are added to its rows: `grid_units.json` (session 1180) and `grid_yesterday.json` (session 1166). No fixture is new, and the two older tests are unchanged.
- **63 assertions in 19 files carry `# also covered by site/scripts/test-grid-render.mjs: <case name>`.** The diff of `tests/` is those 63 comment lines only. A pin counts as covered when each string it holds is rendered in one case's block: a sentence, the literal prefix of a key template, a panel name, an anchor or a method link.
- **467 pins are not covered:** 413 pin code no render shows; 28 hold words the fixtures' pages do not draw (failure branches, which `test-grid-failed-reads` covers; client components; `/grid/caiso/alerts` and `/network`); 26 hold words or keys drawn, but not in one block, not on one page, or only on another day of data.
- **`tests/test_session1404.py` (new, 5 tests).** Runs the node test, skipped with a reason without node or `site/node_modules`; holds every comment line to a case that exists and ran, directly above an assertion, one line an assertion; checks the four grid kinds and every panel family have cases, and the new files carry no em dash.
- **Mutation checks:** with the balance's `id={GRID_ANCHOR.balance}` dropped and "last 30 days held" changed: exit 1, 7 cases named. With "session 360 found the gap" and the held hub reason changed: exit 1, 2 cases named. The components were restored with `git checkout` each time.

## The inventory, by file

Each cell reads markup or code pins / sentence pins / absent / no em dash / pattern / counts / order / covered now.

54 5/2/0/1/0/0/0/0; 55 0/0/0/1/0/0/0/0; 58 1/0/0/1/0/0/0/0; 78 3/0/1/0/0/0/0/1; 92 1/0/1/0/1/0/0/0; 93 7/0/0/1/0/1/0/0; 94 0/0/0/1/0/0/0/0; 109 3/1/2/0/0/0/0/0; 118 7/1/0/0/0/1/0/0; 122 0/0/1/0/0/0/0/0; 123 0/0/1/0/0/0/0/0; 124 6/1/1/1/0/1/0/0; 133 2/2/2/1/0/0/0/0; 137 4/0/0/0/0/2/0/0; 143 0/0/1/0/0/0/0/0; 148 2/0/0/0/0/0/0/0; 163 0/0/2/0/0/0/0/0; 164 0/0/2/0/0/0/0/0; 177 0/0/1/0/0/0/0/0; 180 4/1/2/1/0/0/0/0; 193 4/2/2/1/0/0/1/0; 215 2/0/0/0/0/0/0/0; 237 15/1/4/2/0/2/0/0; 266 10/1/1/2/0/0/0/3; 299 16/3/1/1/0/2/0/2; 317 1/1/2/1/0/0/0/0; 369 0/0/1/0/0/0/0/0; 411 0/0/2/0/0/0/0/0; 416 1/0/0/0/1/0/0/1; 428 6/1/0/0/0/1/0/0; 473 1/0/2/0/0/1/0/0; 502 4/0/5/0/1/0/0/0; 538 0/0/1/0/0/0/0/0; 583 0/0/0/1/0/0/0/0; 1152 10/1/3/0/0/1/2/2; 1153 21/1/1/1/0/3/0/0; 1154 12/1/0/1/0/1/2/2; 1155 25/3/4/0/0/4/1/8; 1156 28/2/3/1/0/1/0/0; 1157 3/0/3/0/0/0/1/1; 1158 11/0/6/1/0/2/0/0; 1159 7/0/3/1/0/4/1/2; 1160 10/0/1/1/0/0/1/0; 1165 15/0/0/1/0/0/2/7; 1166 24/0/1/1/0/1/0/6; 1167 11/0/1/1/0/3/1/2; 1168 11/0/1/1/0/2/0/0; 1170 22/1/0/1/0/1/0/5; 1171 11/1/2/0/0/3/0/3; 1174 40/2/3/0/0/4/2/8; 1175 4/1/2/1/0/2/0/0; 1179 15/0/3/1/0/0/4/0; 1180 13/0/3/1/0/0/0/1; 1181 27/4/1/0/0/0/0/2; 1182 10/1/3/1/0/2/0/0; 1183 5/0/1/1/0/2/0/0; 1184 4/0/1/1/1/1/0/0; 1185 9/4/5/1/0/2/0/6; 1402 8/0/0/1/0/1/0/0; 1403 9/0/1/1/0/0/0/0; 180b 0/0/2/0/0/0/0/0; 241a 1/0/2/0/0/1/0/0; 241c 4/1/1/1/0/1/0/0; 168_mix 2/2/1/1/0/1/0/0; 120_page 0/0/1/0/0/0/0/0; 146_page 0/0/1/0/0/0/0/0; 154_page 1/0/2/0/0/0/0/0; 157_page 1/0/2/0/0/0/0/0; 168_network 9/0/3/1/0/1/0/1; **all 69: 488/42/105/39/4/55/18/63**.

## The inventory, by panel

Assertions / pins / rules, counts and order / covered now. An assertion reading several files counts under each file's panel.

| Panel | Assertions | Pins | Rules | Covered |
|---|---|---|---|---|
| network view | 215 | 139 | 76 | 6 |
| mix | 84 | 48 | 36 | 2 |
| the page | 78 | 38 | 40 | 1 |
| scarcity | 59 | 44 | 15 | 7 |
| network, balance, gravity | 42 | 30 | 12 | 2 |
| conditions | 39 | 27 | 12 | 5 |
| YourGrid's blocks | 39 | 22 | 17 | 3 |
| mix views | 38 | 22 | 16 | 1 |
| now view | 34 | 18 | 16 | 2 |
| ercotnotice | 34 | 25 | 9 | 7 |
| reads | 32 | 22 | 10 | 1 |
| caisoalert | 31 | 19 | 12 | 6 |
| clean24 | 30 | 15 | 15 | 5 |
| ask | 25 | 13 | 12 | 1 |
| replay | 19 | 16 | 3 | 5 |
| exchange | 18 | 8 | 10 | 2 |
| anchors and methods | 16 | 12 | 4 | 0 |
| Lower 48 by month | 15 | 6 | 9 | 3 |
| charts | 14 | 6 | 8 | 0 |
| keys | 11 | 9 | 2 | 5 |
| mix data | 10 | 6 | 4 | 0 |
| CAISO reliability | 10 | 4 | 6 | 0 |
| preliminary | 7 | 6 | 1 | 1 |
| files | 7 | 4 | 3 | 0 |
| hubprice | 6 | 1 | 5 | 0 |
| cleanweek | 6 | 1 | 5 | 0 |
| stress | 4 | 2 | 2 | 0 |
| held | 2 | 1 | 1 | 0 |
| the day | 1 | 0 | 1 | 0 |

## What to review

There is no landing yet, and nothing a visitor sees changed: no site source was touched.

1. Read `site/scripts/test-grid-render.mjs`: its header lists every check, and `CASES` lists each case. Then read `site/scripts/grid-render-standin.mjs`.
2. From `site/`, run `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs`: "every case holds (68 cases)".
3. Run `git diff wip/1403-grid -- tests/ ':!tests/test_session1404.py'`: 63 comment lines added and nothing else.
4. Screenshots: not taken, no build.

## Checks

- Precheck: run by the orchestrator, exit 0.
- `test-grid-render.mjs`: exit 0, 68 of 68. Both mutation runs exit 1; components restored.
- `test-grid-files.mjs`: exit 0, 103 cases. `test-grid-failed-reads.mjs`: exit 0.
- `python -m unittest`, one module at a time, each exit 0: the 19 annotated modules (`test_session1152`, `1154`, `1155`, `1157`, `1159`, `1165`, `1166`, `1167`, `1170`, `1171`, `1174`, `1180`, `1181`, `1185`, `168_network`, `266`, `299`, `416`, `78`); the modules that read changed test files (`109`, `122`, `237`); `1404`, new, 5 tests.
- `node --check` and `npx eslint` on both new scripts: exit 0.
- Type check through the junction: `npm run content`, `npx next typegen`, `npx tsc --noEmit -p .`: exit 0 each. Junction removed with `rmdir`; the main copy's `node_modules` is intact.
- Not run (the brief): build, check-values, check-routes, same-figures (no site source changed), screenshots.

## The landing

- None in this session. It lands with the chain's combined landing. Pushed: `wip/1404-grid`.

## To finish

- Land with the chain. The gate's suite runs `tests/test_session1404`, which runs the node test (about 5 seconds).
- A session that adds a Grid panel adds its case to `CASES`; until then the family check fails and names the panel.

## Decisions made without you

- **A new shared module for the render, and the two older tests left alone:** python tests pin lines of `test-grid-files.mjs` and `test-grid-failed-reads.mjs`, so moving their stand-ins into the module would change pinned files.
- **The cases were written from the pages as drawn on the fixtures.** Words are the pinned sentences first, then headings, then the first sentence. Sentences a pin holds stand per grid.
- **"Covered" means every string the pin holds is rendered in one block.** A key template counts by its literal prefix, and a prefix of 4 characters or fewer (`fmt|`, `net|`) covers nothing. A pin is looked for only in its panel's family, when the file it reads names one.
- **The held grid is ISO-NE on the Mix, Network and Gravity tabs, and MISO on the Clean tab.**
- **The Lower 48's Clean and stress cases draw ERCOT's blocks,** because the views fall back to the first ISO; the block names in the cases say so.
- **Each comment names one case,** the first in the order ERCOT, CAISO, ISO-NE, the Lower 48, PJM, MISO, then the older blocks, taking the smallest block that holds the pin.
- **No pin is retired.** Retiring one is the owner's ruling.

## For Samuel's ruling

- Whether the 63 covered pins may be retired. Recommendation: retire the 42 that hold a sentence or a key template; keep the panel-name, anchor and method pins.
- Whether the 413 code-line pins stay as they are. Recommendation: keep them; a render test cannot read code.

## Files

- New: `site/scripts/test-grid-render.mjs`, `site/scripts/grid-render-standin.mjs`, `tests/test_session1404.py`, this report.
- Changed, one comment line above each covered assertion: `tests/test_session1152`, `1154`, `1155`, `1157`, `1159`, `1165`, `1166`, `1167`, `1170`, `1171`, `1174`, `1180`, `1181`, `1185`, `168_network`, `266`, `299`, `416`, `78`.
- On this machine only, in `runs/s1404/`: the inventory script and its full list of assertions, the drawn pages, the case writer, every test's output.
