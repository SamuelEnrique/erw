# Session 195 report: the decisions layer becomes one system on the three pages

11 October 2026, 19:38 to about 21:00 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/195-decisions-one-system`, pushed as `wip/195-decisions-one-system`. Model spend USD 0, no model call. No pull: no request to any publisher. No data lock taken.

## Read these first

- **Not landed. `main` fails GitHub's own check, so no code branch can merge.** Five tests fail on `main` since the data machine's page files of this morning (`483c412d`, "Page files 2026-10-11"): the committed questions of session 153, the generator's replication CSV against `capture.json` (two tests of session 183), and the datacenter note's "if perfectly foreseen" figures (two tests of session 190). The other machine's push `task/198-battery-data` was refused for exactly these five at 20:24 UTC (run 38172045438). None is this session's, and none is this machine's to repair (data files, pages outside the three). The work is complete and checked locally; the landing is the commands under "To finish".
- Built: one shared component, `site/components/decisions/ScenarioBlock.tsx`, for the assumptions panel, the two columns, the rows in words and the sensitivity chart of `/cost-of-power/battery`, `/cost-of-power/seller` and `/cost-of-power`. Each page hands it its own rows, defaults, sources and formulas.
- **Scenario A sets the headline on all three.** The duplicate fields are gone (fixed O&M and annual debt payments in "Your battery" and "Your plant"; power per GPU and overhead ratio in "Your load"). **At the defaults every headline number is what it was** (table below; 3,289 of 3,289 checked values equal the live set, three times).
- **A link that already held scenario A's parameters now shows A in the headline.** Session 179's link: coverage 0.88 becomes 0.75. That is the ruling at work, not a defect; each such figure is listed below.
- The battery's last twelve months end with the last complete month. Today that moves nothing: September 2026 is whole. It first acts about 28 October.

## What to review

On production after the landing (internal view); until then the same states are the screenshots under `runs/session195/shots/` (`<page>-<state>-<width>.png`, 1280 and 390 px).

1. `https://erw-flame.vercel.app/cost-of-power/battery`
   - "Your battery" on the left: Grid, Duration, Strategy, Size, Show. No "Fixed O&M", no "Annual debt payments", no "Reset the costs". Under Show: "The costs and the debt are set under Scenarios A and B: scenario A gives the headline."
   - Headline: USD 81.40 per kW; USD 475,477 (December 2024); 0.88 times, "debt payments of USD 6.78 million a year".
   - Scroll to "Scenarios A and B". In Capital cost type `1300`.
     - The headline's third number becomes 0.75 times, "debt payments of USD 7.94 million a year". The sentence at the top reads "covered its debt 0.75 times".
     - Column A: coverage 0.75 times, NPV USD -71.68 million. Column B does not move.
     - Under the table: "Scenario A, 100 MW, 4-hour: at a hurdle rate of 8 percent, NPV is USD -71.68 million."
   - Click "Scenario B", type Hurdle rate `10`. The headline does not move. The sentence under the table still states scenario A. The chart is headed "scenario B".
   - Click "Scenario A", choose Round-trip efficiency `92`. The first headline number rises above 81.40, and its note reads "Scenario A: round-trip efficiency 92 percent, at most 1 cycle a day. The sections below are the model's own run, at 86 percent and one cycle a day."
2. `https://erw-flame.vercel.app/cost-of-power/battery?fom=30&ds=4000000` (an older link's two names)
   - The headline's coverage is on "debt payments of USD 4 million a year"; scenario A's Fixed O&M reads 30.
   - The address becomes `?ac=...&af=30`: the two old names are gone.
3. `https://erw-flame.vercel.app/cost-of-power/battery?ac=1300&bt=10&be=92&by=2&bh=10&v=b` (session 179's link)
   - Column B: revenue USD 88.24, USD 533,523, coverage 0.67 times, as in session 179's report.
   - Headline: 0.75 times (it was 0.88: scenario A's capital cost is 1,300).
4. `https://erw-flame.vercel.app/cost-of-power/seller`
   - "Your plant": no "Annual debt payments", no "Fixed O&M". Headline: 59.85 USD/kW; 23.27 USD/MWh; 0.67 times on USD 7.08 million.
   - In "Scenarios A and B" type Capital cost `1500`: the headline's coverage becomes 0.61 times on USD 7.72 million. Scroll to "Month by month" and "Debt coverage": both now read USD 7.72 million.
5. `https://erw-flame.vercel.app/cost-of-power/seller?ac=1500&bt=10&bd=0.5&bh=10&v=b` (session 186's link): column B coverage 0.39 times, as then; headline 0.61 times (it was 0.67).
6. `https://erw-flame.vercel.app/cost-of-power`
   - "Your load": no "Power per GPU", no "Facility overhead ratio". Headline: USD 33.73 per MWh; USD 37.88 (August 2026); USD 0.0684 per GPU-hour, "100 MW powers 49,310 GPUs".
   - In "Scenarios A and B" type Facility overhead ratio `1.2`: the third headline number becomes USD 0.0526, "powers 64,103 GPUs"; the sentence at the top reads USD 0.0526 per GPU-hour.
   - In "How the load runs" choose "Flexible": the first headline number becomes USD 31.46, with the note "Scenario A runs flexible (off in the 100 most expensive hours of each year). The sections below are the load as "Your load" describes it."
7. `https://erw-flame.vercel.app/cost-of-power?ap=1.2&bw=1&bu=50&bh=10&v=b` (session 194's link): column B USD 31.46, USD 35.43, as then; headline USD 0.0526 per GPU-hour (it was 0.0684).
8. `https://erw-flame.vercel.app/cost-of-power?gpu=1&pue=1.2` (an older link's two names): both scenarios hold 1 kW and 1.2; the address becomes `?ag=1&ap=1.2&bg=1&bp=1.2`.
9. Method notes: `https://erw-flame.vercel.app/data/methods/battery_earns_algorithm`, section 11.1, "The block the three pages share (session 195)"; section 5, "A month so far". The generator's note, section 11, and the datacenter's, section 4.14, point to it.

## Numbers on the page, before and after

At the bare address of each page (read from the page's own text, `runs/session195/face_1.out`; "before" is production, `before_production_*.txt`):

| Page | Number | Before | After |
|---|---|---|---|
| Battery | Last twelve months, USD per kW | 81.40 | 81.40 |
| Battery | A bad month, USD | 475,477 (December 2024) | 475,477 (December 2024) |
| Battery | Debt coverage, times; debt payments | 0.88; USD 6.78 million | 0.88; USD 6.78 million |
| Battery | The last twelve months | October 2025 to September 2026 | October 2025 to September 2026 |
| Generator | Revenue, USD per kW | 59.85 | 59.85 |
| Generator | Price received, USD per MWh | 23.27 | 23.27 |
| Generator | Debt coverage, times; debt payments | 0.67; USD 7.08 million | 0.67; USD 7.08 million |
| Datacenter | Market energy, USD per MWh | 33.73 | 33.73 |
| Datacenter | A bad month, USD per MWh | 37.88 (August 2026) | 37.88 (August 2026) |
| Datacenter | Power per GPU-hour, USD; GPUs | 0.0684; 49,310 | 0.0684; 49,310 |

- Text of each bare page, production before against local after (`diff` of the two files): only the removed field labels, the battery's "Reset the costs", and one new line under each panel. No number.

What moved, and why (each is the ruling "scenario A drives the headline"):

| Address | Number | Before | After | Why |
|---|---|---|---|---|
| Battery, `?ac=1300&bt=10&be=92&by=2&bh=10&v=b` | headline coverage; debt payments | 0.88; USD 6.78 million | 0.75; USD 7.94 million | A's capital cost is 1,300 |
| Generator, `?ac=1500&bt=10&bd=0.5&bh=10&v=b` | headline coverage; debt payments | 0.67; USD 7.08 million | 0.61; USD 7.72 million | A's capital cost is 1,500 |
| Datacenter, `?ap=1.2&bw=1&bu=50&bh=10&v=b` | power per GPU-hour; GPUs | 0.0684; 49,310 | 0.0526; 64,103 | A's overhead ratio is 1.2 |
| All three, any link with `v=b` | the sentence under the table | "Scenario B, ..." | "Scenario A, ..." | the sentence states scenario A |
| Datacenter, a link with `gpu=` or `pue=` | the default beside the two fields | "Default 1. The value under "Your load"..." | "Default 1.3. NVIDIA DGX H100..." | the two are the scenarios' own |

- The scenario tables of the three shared links are as the reports of 179, 186 and 194 gave them (B: 88.24 and 533,523 and 0.67; 0.39; 31.46 and 35.43).
- The whole-month rule: before and after 81.40, 475,477, 0.88. No number moved today.

## What was built

- `site/components/decisions/ScenarioBlock.tsx`: the panel, the table, "What differs", "B against A" (when a page hands it one), the chart; `ScenarioState` holds the two scenarios above the page's sections and writes the address.
- `battery/Scenarios.tsx`, `seller/SellerScenarios.tsx`, `LoadScenarios.tsx`: each page's fields, rows and chart figures, and the figures that follow scenario A. `LoadHeadline.tsx`, `battery/nums.tsx`, `seller/nums.tsx`: new small files.
- What follows scenario A in the browser:
  - Battery: the summary sentence, the three headline numbers, each month's coverage, the contract's coverage.
  - Generator: the headline's coverage, the line of one month of debt payments, the section "Debt coverage", each month's coverage.
  - Datacenter: the three headline numbers; the power per GPU-hour of the summary sentence and of "What will it cost".
- The old names, in the three finance libraries (`parseScenarios`): `fom`, `ds`, `gpu`, `pue`.
- `site/lib/batterystack.ts`: a month is `whole` when every day is in the table; `lastTwelve` ends with a whole month.
- The three Method notes: the shared block described once in `battery_earns_algorithm.md`, section 11.1; the other two point to it. `datacenter_cost.md`: one sentence.
- Checks: `check-decisions-face.mjs` (new, 144 assertions), `test-decisions-195.mjs` (new, 30), `tests/test_session195.py` (new, 18 tests); the three scenario checks gained a part for the headline; `check-seller.mjs` and the tests of sessions 86, 138, 145, 162, 179, 186, 194 follow the change.

## Neutral wording

- Read: every sentence the three blocks print in the 24 states of the face check (44 distinct patterns, numbers masked), and the headline and panel text.
- Rewrites needed: none. No sentence holds "should", "better", "worth", "attractive" or a like word; `check-decisions-face.mjs` and `tests/test_session195.py` now hold that.
- New sentences, each a number or a condition:
  - "The costs and the debt are set under Scenarios A and B: scenario A gives the headline." (battery, generator)
  - "Power per GPU and the facility overhead ratio are set under Scenarios A and B: scenario A gives the headline."
  - "Scenario A: round-trip efficiency 92 percent, at most 1 cycle a day. The sections below are the model's own run, at 86 percent and one cycle a day."
  - "Scenario A runs flexible (off in the 100 most expensive hours of each year). The sections below are the load as "Your load" describes it."
  - "With USD 5 per MWh of other charges, as scenario A has them."
  - Battery summary at another step: "earned USD X per kW at a round-trip efficiency of 92 percent and at most 2 cycles a day, and covered its debt Y times."

## Checks run

Outputs under `runs/session195/`. Local production build on port 3195.

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit`, twice | 0, 0 | no type error |
| Site build, twice | 0, 0 | no "statement timeout" line |
| `check-battery-scenarios.mjs` | 1, 0, 0 | first run 3 failed, all on what the rulings changed; then 81 of 81, twice |
| `check-seller-scenarios.mjs` | 1, 0, 0 | first run 1 failed (the sentence); then 89 of 89, twice |
| `check-datacenter-scenarios.mjs` | 1, 1, 0, 0 | 1 failed (the sentence); 1 failed (my new assertion read a note into a number); then 86 of 86, twice |
| `check-battery-face.mjs`, `check-seller-face.mjs`, `check-datacenter-face.mjs` | 0 each, twice | 20, 24, 23 |
| `check-decisions-face.mjs`, 1280 and 390 px | 0, 0 | 144 of 144, twice |
| `check-seller.mjs` | 1, 0, 0 | first run 1 failed (it pinned "Annual debt payments, USD"); then 45 of 45 |
| `check-seller-deeper.mjs`, `check-datacenter.mjs`, `check-how-soon.mjs` | 0 each | 51, 58, 42 |
| `check-routes.mjs` | 0, 0 | 159 pages in review asked as a visitor, 0 failed |
| `check-values`, pages under `/cost-of-power` | 0, 0, 0 | 3,289 of 3,289, three times |
| `test-battery-finance`, `test-seller-finance`, `test-datacenter-finance` | 0 each | all passed |
| `test-decisions-195.mjs` | 0 | 30 of 30 |
| Tests of 178, 179, 186, 194 | 1, 1, 0 | 19 failures and 1 error (source pins), then 1, then 118 tests OK |
| `tests.test_session195` | 0 | 18 tests |
| Whole suite, clean copy, first | 1 | 3,346 tests, 12 failures: 6 mine (older tests pinning the removed fields; two test scripts building months without the new flag), 6 on `main` |
| Whole suite, clean copy, at `09825a68` | 1 | 3,346 tests, 6 failures, **the same 6 that fail on a clean copy of `origin/main`** (`main_tests_a.out`) |

- The 6 on `main`: `test_session153` (1), `test_session183_replication` (2), `test_session190` (1), `test_session190_replication` (1), and `test_session149` (1: a clean copy holds no role file; it passes on GitHub).
- The last build is of the tree before the final commit, which changed tests only.
- **Not run:** the full `check-values`; `test-battery-stack.mjs` (its visitor half fails since session 178); every check on production (not landed).
- **Not verified:** only headless Chrome. The face check used the repository's own browser helper, not Playwright (below).

## The landing

- **Not made.** `python scripts/freeze.py status` was not reached: the push would be refused by "Tests (tests/)" on GitHub for the five tests above, as `task/198-battery-data` was.
- No snapshot taken, none needed: nothing was pushed to `main` or to a `task/` branch. Production is untouched by this session.
- Pushed: `wip/195-decisions-one-system` (no deploy).
- Sessions 196 and 197 look again before their own landings; if `main` passes by then, this session is landed first, with its own snapshot pair.

## To finish

- When the five tests pass on `main` (`python -m unittest tests.test_session153 tests.test_session183_replication tests.test_session190 tests.test_session190_replication`), each its own command:
  1. `git fetch origin`, `git checkout task/195-decisions-one-system`, `git merge origin/main`
  2. `cd site && npm run build` (exit 0), then the whole suite in a clean copy of the merged commit
  3. `python scripts/freeze.py status` (exit 0)
  4. `node site/scripts/snapshot-live.mjs take s195-before`
  5. `git push origin task/195-decisions-one-system`
  6. after "code branch" succeeds and Vercel says "Deployment has completed": `node site/scripts/snapshot-live.mjs take s195-after`
  7. `node site/scripts/snapshot-live.mjs compare s195-before s195-after` (expected: 0 differences, every page is in review)
  8. on production: `check-battery-face.mjs`, `check-seller-face.mjs`, `check-datacenter.mjs`, the three scenario checks and `check-decisions-face.mjs`, each with `https://erw-flame.vercel.app`
  9. delete the remote `wip/195-decisions-one-system`

## Decisions made without you

- **Not landing on a red `main`, and not repairing it.** The five tests are another machine's files and pages outside the three. The reversible choice: a `wip/` branch and the commands above.
- **The old `ds` becomes scenario A's capital cost**, at A's debt share, rate and term, so that A's debt payment is the link's to the dollar. Tried on 180 links of many sizes. The other choice was the debt share, which cannot hold a payment above full debt.
- **A scenario's own parameter wins over an old name.** A link with both `ds` and `ac` opens A's capital cost, so its headline coverage is not the one it showed before.
- **`gpu` and `pue` are read as both scenarios'**, because "Your load" was the default of both.
- **The sentence under the table always states scenario A**, read literally. The chart stays the scenario in view's.
- **"B against A" stays the datacenter page's row.** The battery and the generator keep "What differs" only; nothing a reader sees was added there.
- **Each page's headline is scenario A's rows.** On the battery page that includes A's efficiency and cycle step; on the datacenter page, how A runs and A's other charges. The page then says the sections below are the model's own run, or the load as "Your load" describes it.
- **The whole-month rule is in `lastTwelve`**, so the headline, the first column of "Income by stream", the contract, the bad month's window and the scenarios move together. The averages of every year held and the chart still take a month from 90 percent of its days.
- **"Reset the costs" left the battery panel** with its two fields. The generator's stays: it also resets the sizes and the peaker's heat rate.
- **No new Method note file.** A new one needs `site/lib/release.ts`, which this chain does not edit. The shared block is described in the battery note; the other two point to it.
- **The face check ran without Playwright.** It is not installed on this machine, and an install is a download nobody approved. The repository's `scripts/browser.mjs` drives the same headless Chrome at 1280 and 390 px.
- The first precheck exited 1: it was started with the system Python, which has no `requests`. Run again with the repository's own Python it passed, six of six. One "precheck failed" line was sent before that.

## Found, not changed

- The generator's "Your plant" clamped fixed O&M at 200; scenario A allows 500. A page opened with A's fixed O&M above 200 shows it, and its check keys would be recomputed at 200. No listed page does this.
- `test_session190` holds the note's "if perfectly foreseen" figure to the library's. The figure moves each day October 2026 grows (29.72 in the note, 29.80 from today's files), so the test fails with every daily run.

## For Samuel's ruling

1. `main` fails GitHub's check since the page files of 11 October (`483c412d`): five tests of sessions 153, 183 and 190. Which machine repairs them, and whether a test that moves with each day's data belongs in the check a landing must pass.
2. Session 195 is on `wip/195-decisions-one-system`, complete and not landed: land it once `main` passes ("To finish").
3. An older link's `ds` is read as scenario A's capital cost (not its debt share). Confirm.
4. A link holding both `ds` and scenario A's own capital cost opens A's: its headline coverage differs from before. Confirm.
5. The sentence under the table always states scenario A, also with B in view. Confirm.
6. Whether the battery and the generator pages get a "B against A" row in numbers, as the datacenter page has.
7. Whether the averages of every year held and the chart by year should wait for whole months too, as the last twelve months now do.
8. Whether Playwright is installed on the code machine, or the repository's own browser helper stays the face check's tool.
9. Whether the generator's scenario A should keep the old bound of 200 on fixed O&M.

## The prompt

Chain of 11 October (day), sessions 195 to 197, the code machine; its text for this session: "Session 195: the decisions layer becomes one system on the three pages. Long end 3:00. Model spend USD 0. Pulls: none. Branch task/195-decisions-one-system." with six rulings: one shared component; scenario A drives the headline, with the old parameter names kept as aliases of A's; no usage count; the hurdle rate and degradation defaults stay; the battery headline counts whole months only; a neutral wording check.
