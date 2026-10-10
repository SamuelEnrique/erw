# Session 179 report: What a battery earns, decisions

10 October 2026. Branch `wip/179-battery-decide` (worktree `erw-144`), on top of session 178's `5a84f3d`. Not pushed. Model spend USD 0. No request to an outside host.

## Read these first

- Built: one new section on `/cost-of-power/battery`, "Scenarios A and B": ten assumptions with defaults and Resets, two scenarios on seven rows, a sensitivity chart. Computed in the browser; both scenarios are kept in the address.
- **No existing number moved.** 1,808 of 1,808 checked values on the seven battery addresses equal the live set, the same count as session 178. The page's visible text at its bare address: 0 lines missing or changed, 114 lines added, all in one block.
- **Two defaults have no source in the repository: the hurdle rate and the degradation rate.** The page says so beside each. They need your ruling (below).
- **Efficiency and cycles are not a formula.** The model itself was run at 12 pairs of steps for 12 cases; the page offers exactly those steps. The file is static, dated 10 October 2026, and goes out of date about the 28th of each month: the page then offers the default step alone and says so.
- **One conflict for your ruling:** the usage count `track("scenario compared")` would be the only request a reader's action causes on this page, whose contract box says nothing typed there is sent. Not added by me; the place is marked.

## What to review

`https://erw-flame.vercel.app/cost-of-power/battery` (internal view). Figures are as of the tables retrieved 5 to 8 October 2026.

1. Open the address with nothing after it. Scroll past "With your contract" to "Scenarios A and B".
   - A beige panel: two buttons "Scenario A" (filled) and "Scenario B", then "Copy A to B" and "Reset all of A".
   - Ten fields in this order: Capital cost 1110, Debt share 60, Interest rate 8, Term of the debt 20, Fixed O&M 22, Round-trip efficiency 86, Cycles a day 1, Degradation 0, Project life 20, Hurdle rate 8. Under each: "Default ..." and its source. Each Reset is grey.
   - Under the panel, a table with columns A and B, both the same: revenue USD 81.40; the 10th-percentile month USD 475,477 (December 2024); debt coverage 0.88 times; NPV USD -52.68 million; IRR none; breakeven toll USD 8.90; merchant tail USD 0. Last row: "A and B hold the same assumptions."
   - The first three equal the page's own headline numbers above.
   - The address bar still has nothing after `/battery`.
2. In Capital cost type `1300`.
   - Column A: NPV USD -71.68 million, coverage 0.75 times, toll USD 10.11. Column B does not move.
   - The headers now read "capex 1,300 USD/kW" under A and "capex 1,110 USD/kW" under B.
   - Last row: "B: capex USD 1,110 per kW against 1,300."
   - The address ends `?ac=1300`. The Reset beside Capital cost is now active (cardinal, no longer grey).
3. Click "Scenario B". Type Hurdle rate `10`, Term of the debt `10`. Choose Round-trip efficiency `92` and Cycles a day `2`.
   - Column B: revenue USD 88.24; 10th-percentile month USD 533,523; coverage 0.67 times; NPV USD -48.99 million; IRR -1.2 percent; toll USD 12.17; merchant tail USD 15.69 million, "years 11 to 20".
   - Sentence under the table: "Scenario B, 100 MW, 4-hour: at a hurdle rate of 10 percent, NPV is USD -48.99 million."
4. The chart "How far each assumption moves NPV, scenario B": ten rows, largest first (Capital cost, USD 9.49 million). Point at the first row.
   - Under the chart: "Capital cost, moved by USD 100 per kW: NPV is USD -39.5 million at 1,010 and USD -58.49 million at 1,210; USD -48.99 million at 1,110."
   - Click "The chart as a table": the same figures in a table.
5. Copy the address and open it in a new tab. The same inputs and the same numbers, B in view. The full link:
   - `https://erw-flame.vercel.app/cost-of-power/battery?ac=1300&bt=10&be=92&by=2&bh=10&v=b`
6. Click "Copy A to B": the headers empty, the last row reads "A and B hold the same assumptions.", the address ends `?ac=1300&bc=1300&v=b`.
7. Click "Reset all of B": every field of B returns to its default.
8. In "Your battery" on the left, type Size `200` and click Show: the page reloads for 200 MW and the scenarios are still set.
9. Click "8 hours": Capital cost becomes 2110 and Fixed O&M 43.6 in both scenarios (a typed capital cost or fixed O&M is dropped with the duration; any other typed assumption stays).
10. Click CAISO and Show: the block works the same. In the internal view click NYISO: efficiency and cycles offer one step, and the panel says "only the model's own step is held for NYISO".
11. On a phone (390 px): each row's label runs across the width with A and B under it. Screenshots: `runs/session179/shots/scenarios-compared-phone.png`, `scenarios-default-phone.png`.

`https://erw-flame.vercel.app/data/methods/battery_earns_algorithm` (internal view): section 11.1, "Scenarios A and B": every formula.

## The defaults and their sources

| Assumption | Default | Source |
|---|---|---|
| Capital cost | 610, 1,110, 2,110 USD per kW (2, 4, 8 hours) | Lazard LCOE+ June 2025, LCOS v10.0, midpoints (`lib/batterystack.ts`, `COSTS`) |
| Debt share | 60 percent | Lazard: "60% debt at an 8% interest rate" (`docs/methods/cost_of_power.md`) |
| Interest rate | 8 percent | the same |
| Term | 20 years | Lazard: "Economic life sets debt amortization schedule"; 20 years for storage |
| Fixed O&M | 11.2, 22, 43.6 USD per kW a year | the same Lazard cases |
| Round-trip efficiency | 86 percent | Lazard LCOS v10.0, 86 to 92 percent; the model's value |
| Cycles a day | 1 | the model's rule |
| Degradation | 0 percent a year | **none held** |
| Project life | 20 years | Lazard, storage |
| Hurdle rate | 8 percent | **none held**: set equal to the interest rate |

## What could not be cited (for Samuel)

- **Hurdle rate.** The repository quotes no cost of equity and no hurdle rate anywhere. Default 8, equal to the cited interest rate. The page prints "No cited rate is held. The default is set equal to the interest rate." To be confirmed by Samuel. I did not use a figure from memory.
- **Degradation.** No rate is cited. Default 0, which is what the model does. The page prints "The model has no capacity fade. No cited rate is held, so the default is none." To be confirmed by Samuel.
- **Cycle steps 0.5, 1.5 and 2.** Not from a source: the reader's steps. The page says so.
- **Efficiency step 89.** The midpoint of Lazard's cited range, not a Lazard figure.
- Already known from 178: the 8-hour capital cost and fixed O&M are an extrapolation.

## How efficiency and cycles were handled

- Option (a) of the brief. `warehouse/derived/battery_scenario_steps.py` runs the model's own `solve_day` over each case's 36-month window.
- Steps: efficiency 86, 89, 92 percent; cycle limit 0.5, 1, 1.5, 2 a day. 12 pairs.
- Cases: ERCOT and CAISO, both strategies, 2, 4 and 8 hours. 12 cases. ERCOT 1,096 days each, CAISO 755.
- Output: `site/data/battery_scenario_steps.json`, 56,832 bytes, built 2026-10-10T08:43:26Z, about 13 minutes.
- **The model file is not changed.** Efficiency is `solve_day`'s own argument. The cycle limit is one bound of the model's constraint matrix, multiplied by the step through a wrapper that first asserts the row is the cycle row.
- The script refuses to write unless its (86, 1) run equals `battery_stack_monthly` month by month to USD 0.005 per MW with the same days. It passed for all 12 cases.
- Nothing is interpolated. No scaling formula.
- Default case, last twelve months, USD per kW: one cycle: 81.40 at 86 percent, 83.06 at 89, 84.67 at 92. At 86 percent: 64.08 at half a cycle, 83.57 at 1.5, 83.87 at 2. At 92 percent and 2 cycles: 88.24.
- **Freshness: a static file with a date, not rebuilt by the daily run.**
  - The page uses a step only while every held month of its 36-month window is in the file with the same days and the same default total. Otherwise both controls offer the default alone and the panel says to which month the file reaches.
  - It will go out of date when October 2026 becomes a held month, about 28 October.
  - `tests/test_session179.py` then fails on this machine with the rebuild command (it skips on GitHub).
  - NYISO and SPP (in review) have no case: default step only.

## What was built

- `site/lib/battery/finance.ts`: pure module, no React, no import. Debt payment, flows to equity, NPV, IRR by bisection (-99 to 1,000 percent, null when no sign change), coverage, breakeven toll, merchant tail, sensitivity, the address parameters, the steps' freshness rule.
- `site/app/cost-of-power/battery/Scenarios.tsx`: the panel, the table, the chart.
- `site/app/cost-of-power/battery/page.tsx`: one section added after "With your contract". `BatteryForm.tsx`: Show and the duration links carry the scenarios.
- `warehouse/derived/battery_scenario_steps.py` and `site/data/battery_scenario_steps.json`; `.gitattributes` (LF for the JSON).
- `site/scripts/test-battery-finance.mjs` (50 hand cases); `site/scripts/check-battery-scenarios.mjs` (68 assertions in a browser).
- `tests/test_session179.py` (32 tests): a Python mirror of every formula against the library on 308 cases to 1e-6.
- `docs/methods/battery_earns_algorithm.md`, section 11.1: every formula, the address, the steps, what the block is not.

## Pulls and spend

- Outside hosts: 0 requests. None approved, none made.
- Production: read only. Two internal-view reads of the battery page: the "before" text, and one more to try the check's text-only mode after a fix. The two texts are identical.
- Supabase: anon reads only, through the local build and `check-values`.
- Model spend: USD 0 of USD 0. No model call.

## Checks run

Outputs under `runs/session179/`.

| Check | Exit | Output |
|---|---|---|
| Site build of the final tree | 0 | `build3.out`, `build3.exit` |
| `test-battery-finance.mjs` | 0, 50 of 50 | `test_battery_finance.out` |
| `tests.test_session179`, worktree | 0, 32 run, 1 skipped | `test_session179_worktree.out` |
| `tests.test_session179`, main copy's tables read only | 0, 32 of 32 | `test_session179_final.out` |
| Neighbours (50, 56, 66, 67, 70, 74, 86, 89, 92, 101, 102, 115, 116, 120, 122, 123, 148, 178, 179) | 0, 340 run, 42 skipped | `tests_neighbours_final.out` |
| Whole suite, worktree | 0, 2,818 run, 218 skipped | `suite_worktree.out` |
| `check-values`, battery pages only | 0, 1,808 of 1,808, first run | `check_values_battery_final.out` |
| `check-routes` | 0, 0 failed | `check_routes_final.out` |
| `check-battery-face.mjs` (178's) | 0, 20 of 20 | `check_battery_face_final.out` |
| `check-battery-scenarios.mjs`, 1280 and 390 px | 0, 68 of 68 | `check_battery_scenarios.out`, `shots/` |
| `test-battery.mjs` | 0 | `test_battery.out` |
| `test-battery-stack.mjs` | 1 | `test_battery_stack.out` |
| Page text, production before against local after | 0: 0 missing or changed, 114 added | `text_compare.out`, `page_text_before_production.txt`, `page_text_after_local.txt` |
| Steps builder, one case then all | 0 and 0 | `steps_trial.out`, `steps_build.out` |

- `test-battery-stack.mjs` fails at the same line as in session 178: it opens the page as a visitor and gets the in-review page. Not caused by this session. Its contract assertions (no request, address unchanged, nothing stored, no term in a request) are now held in `check-battery-scenarios.mjs` for the internal view. Its visitor-gate half was not rewritten.
- The full `check-values` was not run: it stops on `datacenters|counted` on main (178's finding). Only the battery pages were checked.
- **Not verified:**
  - The check's allowance for a usage count has never met a real one: `site/lib/usage.ts` is not in this worktree. That path runs for the first time at the landing.
  - The scenario numbers carry no `data-check` key, so `check-values` does not cover them. The browser check recomputes them with the library, and the library is held to the Python mirror.
  - The "before" text is production and the "after" is the local build: two environments, the same live data.
  - Only headless Chrome. Not tried with JavaScript off.
- The check's text-only mode left its browser profile in the temp directory on its first two runs (it exited before its cleanup). Fixed in `bd51722`, tried once (`text_only_recheck.out`: exit 0, nothing left), and the two leftover profiles removed. No process was left running. The full 68-assertion run predates that five-line fix, which sits in a branch the full run does not enter; it was not rerun.
- One line in the suite's output, "FAILED request 1 of 30 ... HTTP 403", is printed by an older test, not mine. The suite passed. I did not trace it.

## Decisions made without you

- **NPV and IRR are to equity, after debt payments.** Otherwise debt share, interest rate and term would not move NPV and three chart rows would be empty.
- **Revenue repeats the last twelve months every year of the life**, falling by the degradation rate. An assumption, stated in the note.
- **Degradation is a yearly cut to revenue.** The model has no fade.
- **The breakeven toll is for a toll on the whole battery.** So it does not depend on revenue.
- **The merchant tail assumes the toll runs as long as the debt.** At the defaults (term 20, life 20) it is zero years. The row's note says "the years after the debt's term".
- **The contract panel's share, price and end month are not read by the scenarios.** They stay on the device since session 67 and are never in the address, so a shared link could not carry them.
- **The scenarios do not read the "Your battery" panel's Fixed O&M and Annual debt payments.** Those still set the headline coverage. At the defaults both give 0.88.
- A term longer than the life is cut to the life.
- A scenario with no parameter is the defaults, not a copy of A.
- A change of duration drops a typed capital cost and fixed O&M in both scenarios, as the page already does for its own costs.
- The note's new text is section 11.1, not a section 12: session 178's test holds section 11 to be the last numbered one, and I did not change that test.
- The chart is HTML rows, not one scaled SVG, so its labels stay readable at 390 px.
- Chart colours: the site's categorical slots 1 and 2 (`#2a78d6`, `#eb6834`), which pass the dataviz validator on all five checks. Not red and green.
- The 10th-percentile month is in USD for the reader's size, as the page's headline shows it.

## For Samuel's ruling

1. The hurdle rate's default and its source.
2. The degradation rate's default and its source.
3. Whether the usage count belongs on this page (next section, item 2).
4. "Your battery" now has Fixed O&M and Annual debt payments, and the scenarios have their own. Two places for one idea. I recommend removing the two old fields in a later session and letting scenario A drive the headline. Not done: it changes what the page shows.
5. Whether the merchant tail should read the contract panel's end month when one is typed. It would then differ from a shared link.
6. Whether the steps file joins the daily run (see "To finish").

## For the coordinator

1. Nothing under the data lock. No migration. No table of the warehouse written. No load.
2. **The usage call.** `site/lib/usage.ts` is not in this worktree, so no call was added. The place: `site/app/cost-of-power/battery/Scenarios.tsx`, function `update`, at the line `// session 179: track("scenario compared") goes here once site/lib/usage.ts is on main`. The exact code is in the comment under it (a `useRef` guard, once a page view).
   - **Read before adding it.** In session 177's worktree (`erw-142`, read only, as it stood at about 09:05 UTC) `components/Usage.tsx` sends nothing after the page view on a page whose text matches "sent or stored". This page matches: the contract box says "Nothing you type here is sent or stored." So this call would be the only request a reader's action causes here.
   - It carries the event and the path only, and the block sits outside the contract box, which `lib/usage.ts`'s own comment allows.
   - `check-battery-scenarios.mjs` allows exactly that: one POST to `/api/usage` a page view after a scenario change, and no other request. Typing the contract terms is held to no request at all.
   - If you hold the call, nothing else needs changing.
3. Merge `wip/179-battery-decide`. Files other sessions may touch: `.gitattributes` (two lines added at the end), `site/app/cost-of-power/battery/page.tsx`, `BatteryForm.tsx`. Not touched: `release.ts`, `check-routes.mjs`, `check-values.mjs`, `package.json`, the root layout, `next.config.ts`, `proxy.ts`, `site/app/network/`.
4. In the main copy after the merge, tables present: `.venv/Scripts/python.exe -m unittest tests.test_session179` (expect 32 run, 0 skipped).
5. If `TheStepsFile.test_the_file_still_describes_the_table` fails (the daily run revised a month, or October became held): `.venv/Scripts/python.exe warehouse/derived/battery_scenario_steps.py`, then commit `site/data/battery_scenario_steps.json`. About 13 minutes. No lock: it reads `warehouse/output` and writes a site file. Not between 14:04 and 15:30 UTC, while the daily run writes the tables.
6. Build under the mutex, start, then, each its own command:
   - `node scripts/test-battery-finance.mjs`
   - `node scripts/check-routes.mjs <base>`
   - `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/cost-of-power/battery node scripts/check-values.mjs <base>`
   - `node scripts/check-battery-face.mjs <base> <dir>`
   - `node scripts/check-battery-scenarios.mjs <base> <dir>`
7. Snapshot before and after (rule 8). Expected for a visitor: no difference (the page is in review). Internal view: the one new section.
8. The whole suite in a clean worktree of the merged commit before the task push, as usual. Here it ran in my worktree only.

## To finish

- Rebuild the steps file when the window moves (about the 28th of each month) or a month is revised: the command of item 5 above.
- To make that automatic, the script would join `warehouse/run_daily.sh` after `battery_stack`, and `site/data/battery_scenario_steps.json` the commit step. Not done: GitHub's runner does not hold the ERCOT history, so the script would first need the model's keep-the-fuller-month rule, and a daily commit of a site file is a daily deploy. The same question the coordinator raised for 178's CSV.
- Rewrite the visitor-gate half of `site/scripts/test-battery-stack.mjs` for a site with no live page (not this tool's).
- A reader for `datacenters|counted`, `no_us_state`, `cancelled` in `check-values.mjs` (178's item, still open).
- Run `check-battery-scenarios.mjs` once on a tree that holds `site/lib/usage.ts` with the call added: its usage branch is untried.

## The landing


- Landed by the chain's coordinator from `wip/179-land` (`wip/178-land`, `origin/main` and `wip/179-battery-decide`
  merged; no conflict). Outputs under `runs/session179/`.
- In the main copy at the merged tree (`4c93ecc`): tests 179 and 178: 66 tests OK, 0 skipped (`land_tests.out`);
  `npm run build` exit 0 (`land_build.out`); the finance hand cases: all passed; `check-routes`: 155 pages in review,
  0 failed; the battery pages' values: 1,808 of 1,808, twice; `check-battery-face` 20 of 20;
  `check-battery-scenarios` 68 of 68; the whole suite in the clean worktree: 2,842 tests OK, 232 skipped.
- **The first push failed GitHub's tests, and nothing deployed.** `179_before` at 09:29:41 UTC; pushed as
  `task/179-battery-decide`; run 38041584650: "Tests (tests/)" failed, the merge step was skipped, production untouched.
  The cause (the job's log, `gh_job.log`): `test-battery-finance.mjs --cases` printed 308 results with `console.log`
  and called `process.exit(0)` at once; on Linux a pipe takes 64 KiB at a time, so the JSON arrived cut at byte 65,536
  and the Python mirror could not read it. Windows does not cut it, which is why the clean-copy suite here passed. The
  script now waits until stdout has taken every byte before it exits (`3fa27b5`); the page and the library are
  unchanged by the fix.
- **The second push landed.** No freeze. `179_before2` at 09:35:11 UTC, its own command; run 38041917785 success;
  merge `dacb81d`; Vercel production "Deployment has completed" at 09:44:55 UTC; `179_after` at 09:45:07 UTC;
  comparison with `179_before2` and with `179_before`: **0 differences on the 25 pages** both times (`compare_179.out`,
  `compare_179_first.out`). Expected: the page is in review.
- On production in the internal view: `check-battery-scenarios.mjs https://erw-flame.vercel.app`: 68 of 68, exit 0
  (`prod_check_scen.out`): the ten inputs and Resets, the seven rows in order, "Copy A to B", the address round trip,
  the chart's hover, 1280 and 390 px, no request on an input change.
- **The usage count is not on the page.** `track("scenario compared")` was left out at this landing: session 177's
  `site/lib/usage.ts` was not on main yet, and the call would be the one request a reader's action causes on a page
  whose contract box says nothing typed there is sent. The coordinator's note on it is in session 177's report.
