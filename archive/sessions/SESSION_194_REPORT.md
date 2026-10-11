# Session 194 report: What a datacenter pays, decisions

11 October 2026, 10:04 to about 11:00 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/194-datacenter-decisions`, landed as merge `22f1ec64`. Model spend USD 0, no model call. No pull: no request to any publisher. No data lock taken.

## Read these first

- Built: one new section on `/cost-of-power`, "Scenarios A and B", after "With your contract": eight assumptions with defaults and Resets, two scenarios on eight rows, a row that sets B against A in numbers, and a sensitivity chart that answers the mouse. Computed in the browser; the address keeps both scenarios. One tool, one page, one address.
- **No existing number moved.** The page's visible text at its bare address: 0 lines missing or changed, 136 added, all in one block. 3,289 of 3,289 checked values on the cost-of-power addresses equal the live set, twice. Session 190's 46 tests and its face check (23 of 23) pass unchanged.
- **Four defaults have no source in the repository:** no change of prices, no upfront cost, 20 years counted, and a hurdle rate of 8 percent (set equal to Lazard's interest rate, as on the battery and generator pages). The page says "No cited ..." beside each. They need your ruling.
- **The block puts no value on compute.** A flexible load buys less and runs fewer GPU-hours; the block states the breakeven value of a GPU-hour in the hours off (USD 0.4672 in the default case) and leaves the comparison to the reader. No cited price of a GPU-hour is held, so none is assumed.
- **Session 190's findings 1 and 2 are as they were**, flagged in both Method notes. Neither moves a figure of the block: it uses the rule's figures only, and it names the twelve months it stands on.

## What to review

All in the internal view. Figures are of the page's files as built on 10 October 2026 (twelve months October 2025 to September 2026).

1. Open `https://erw-flame.vercel.app/cost-of-power`. Scroll past "With your contract" to "Scenarios A and B".
   - A beige panel: "Scenario A" (filled) and "Scenario B", then "Copy A to B" and "Reset all of A".
   - Eight fields in this order: How the load runs (a list: "Flat: the same in every hour", "Flexible: off in the 100 most expensive hours of each year"), Power per GPU 1.3, Facility overhead ratio 1.56, Delivery and other charges 0, Change of prices 0, Upfront cost 0, Years counted 20, Hurdle rate 8. Under each: "Default ..." and its source. Each Reset is grey.
   - Under the panel, a table headed "For 100 MW at LZ_NORTH in ERCOT, real time", columns A and B, both the same:
     - Market energy, last twelve months: USD 33.73 (the first headline number).
     - A year's energy: USD 29.55 million, "876,000 MWh".
     - Power per GPU-hour: USD 0.0684, "49,310 GPUs" (the third headline number).
     - A bad month: USD 37.88, "August 2026, of 36 months" (the second headline number).
     - Hours off, and the breakeven value of a GPU-hour: "none", "a flat load runs in every hour".
     - Present value of the cost, at the hurdle rate: USD 290.09 million, "20 years at 8 percent".
     - Fixed price with the same present value: USD 33.73.
     - All-in power per GPU-hour, over the years counted: USD 0.0684, "431,952,663 GPU-hours a year".
     - What differs: "A and B hold the same assumptions." B against A: "No difference."
   - Under the table: "Scenario A, 100 MW at LZ_NORTH in ERCOT, real time: at a hurdle rate of 8 percent, 20 years of power cost USD 290.09 million today, USD 0.0684 per GPU-hour."
   - The address bar still has nothing after `/cost-of-power`.
2. In Facility overhead ratio type `1.2`.
   - Column A: Power per GPU-hour USD 0.0526, "64,103 GPUs". The year's energy stays USD 29.55 million. Column B does not move.
   - The headers read "overhead ratio 1.2" under A and "overhead ratio 1.56" under B. "What differs": "B: overhead ratio 1.56 against 1.2."
   - The address ends `?ap=1.2`. The Reset beside the field is now active.
3. Click "Scenario B". In "How the load runs" choose "Flexible: ...". Type Upfront cost `50` and Hurdle rate `10`.
   - Column B: market energy USD 31.46; a year's energy USD 27.24 million, "866,000 MWh"; a bad month USD 35.43, "August 2024"; hours off USD 0.4672, "off in 100 hours; USD 230.36 per MWh not bought"; present value USD 236.93 million; all-in USD 0.0652.
   - B against A: "A year's energy: USD 29.55 million in A, USD 27.24 million in B, so B is USD 2.3 million lower. B runs 134,516,765 fewer GPU-hours a year (427,021,696 against 561,538,462). Present value of the cost: B is USD 53.16 million lower, each over its own years and at its own hurdle rate. The two have the same present value when B's upfront cost is USD 581.58 per kW (it is 50). B costs USD 50 per kW more upfront, which returns 46.0 percent a year in lower yearly cost; B's hurdle rate is 10 percent."
4. The chart "How far each assumption moves all-in power per GPU-hour, scenario B": eight rows, largest first (Delivery and other charges, USD 0.0101). Point at "Facility overhead ratio (PUE)".
   - Under the chart: "Facility overhead ratio (PUE), moved by 0.1: all-in power per GPU-hour is USD 0.0610 at 1.46 and USD 0.0694 at 1.66; USD 0.0652 at 1.56."
   - Point at "How the load runs": "How the load runs, the other way (the same in every hour): USD 0.0698 per GPU-hour; USD 0.0652 as it is (off in the 100 most expensive hours of each year)."
   - Click "The chart as a table": the same figures in a table.
5. Copy the address and open it in a new tab: the same inputs and numbers, B in view. The full link:
   - `https://erw-flame.vercel.app/cost-of-power?ap=1.2&bw=1&bu=50&bh=10&v=b`
6. Click "Copy A to B": the headers empty, "What differs" reads "A and B hold the same assumptions.", the address ends `?ap=1.2&bp=1.2&v=b`.
7. Click "Reset all of B": every field of B returns to its default.
8. With B in view type Change of prices `2`: "Fixed price with the same present value" becomes USD 39.00, "the market's USD 33.73, rising 2 percent a year for 20 years".
9. A flexible load of your own: `https://erw-flame.vercel.app/cost-of-power?grid=ercot&region=LZ_NORTH&mw=50&run=hours&n=100&buy=rt&au=50&bh=9`
   - Both scenarios now default to flexible ("Default flexible."). Market energy reads USD 31.46 in both, the page's own sentence above.
   - In "Your load" type Size `200` and click Show: the table is headed "For 200 MW ..." and the address still holds `au=50` and `bh=9`.
   - Click CAISO in "Your load": the page opens California and the scenarios are still set.
10. Other grids, each at its bare address:
    - `https://erw-flame.vercel.app/cost-of-power?grid=caiso`: USD 28.58, "Oct 2025 to Sep 2026".
    - `https://erw-flame.vercel.app/cost-of-power?grid=nyiso`: USD 68.49, "Jul 2025 to Jun 2026" (finding 2 of session 190: the row names the months).
    - `https://erw-flame.vercel.app/cost-of-power?grid=isone`: USD 74.19, day-ahead.
    - `https://erw-flame.vercel.app/cost-of-power?grid=spp`: USD 30.80.
    - `https://erw-flame.vercel.app/cost-of-power?grid=isone&region=.Z.CONNECTICUT`: every row reads "not held" (hover for the reason), with no chart and no sentence: nothing is filled.
11. On a phone (390 px): each row's label runs across the width with A and B under it. Screenshots: `runs/session194/shots/block-compared-phone.png`, `datacenter-scenarios-default-phone.png`.
12. The contract's promise still holds: type a share and a price under "Your contract", then change a scenario. The address gains the scenario and no contract term.

`https://erw-flame.vercel.app/data/methods/datacenter_pays_algorithm` (internal view): section 4.14, "Scenarios A and B": every formula, with the default case worked. `https://erw-flame.vercel.app/data/methods/datacenter_cost`: "Scenarios A and B (session 194)", after "The contract".

## Every number changed, and why

- **Changed: none.** No figure the page showed before this session moved. Evidence: the text comparison (0 lines missing or changed), the value check (3,289 of 3,289, twice), session 190's tests and face check.
- **New, at the bare address** (all in the one new section; each is arithmetic on the page's own last twelve months):

| Number | Value | Why it is there |
|---|---|---|
| Market energy; a year's energy; power per GPU-hour; a bad month | 33.73; 29.55 million; 0.0684; 37.88 | the page's own headlines, repeated as the scenario's starting point |
| Present value of the cost | USD 290.09 million | 29,546,505 x 9.818147 (20 years at 8 percent): the hurdle-rate frame |
| Fixed price with the same present value | USD 33.73 | the breakeven of a contract for all the energy against the market |
| All-in power per GPU-hour | USD 0.0684 | the upfront cost and the energy over the GPU-hours run |
| GPU-hours a year | 431,952,663 | 876,000 MWh x 1,000 / (1.3 x 1.56) |
| The flexible way (list, chart, scenario B) | 31.46; 27.24 million; off in 100 hours; 230.36 per MWh not bought; 0.4672 per GPU-hour | the same rule as `?run=hours&n=100`, whose own page shows 31.46 |

## The defaults and their sources

| Assumption | Default | Source |
|---|---|---|
| How the load runs | as "Your load" | the reader's own input |
| Power per GPU | as "Your load": 1.3 kW | NVIDIA DGX H100 datasheet (`lib/datacenter.ts`, `ASSUMED`) |
| Facility overhead ratio | as "Your load": 1.56 | Uptime Institute, Global Data Center Survey 2024 (the same) |
| Delivery and other charges | USD 0 per MWh | the page's figure is market energy alone |
| Change of prices | 0 percent a year | **none held**: the last twelve months are repeated |
| Upfront cost | USD 0 per kW | **none held** |
| Years counted | 20 | **none held** |
| Hurdle rate | 8 percent | **none held**: set equal to Lazard's "60% debt at an 8% interest rate" |

## What was built

- `site/lib/datacenter/finance.ts`: pure module, no import. The price, the year's cost, the GPU-hour, the hours off and their breakeven, the costs by year, present value, the fixed price, the all-in figure, B against A, IRR by bisection, sensitivity, the address parameters.
- `site/app/cost-of-power/LoadScenarios.tsx`: the panel, the table, the chart.
- `site/app/cost-of-power/page.tsx`: one section added, and the two ways of running it hands the block (the load flat, the load flexible, over the same twelve months). `LoadForm.tsx`: Show and the choice of a grid carry the scenarios.
- `site/scripts/test-datacenter-finance.mjs` (72 assertions: hand cases; the generator page's library on 300 seeded cases, equal exactly; five grids against the page's own figures). `site/scripts/datacenter-ways.mjs` (the page's two ways, computed a second time for the checks).
- `site/scripts/check-datacenter-scenarios.mjs` (77 assertions in a browser, 1280 and 390 px).
- `tests/test_session194.py` (29 tests): a Python mirror of every formula against the library on 304 cases to 1e-6, the default page, the page's source, the notes.
- `docs/methods/datacenter_pays_algorithm.md`, section 4.14 and three rows of section 7; `docs/methods/datacenter_cost.md`, "Scenarios A and B (session 194)"; `docs/tools.md`, one line.

## The formulas in one place

- Per MW. A year's cost: the last twelve months' market energy, plus the other charges on every MWh consumed.
- Per GPU-hour: price x kW per GPU x overhead ratio / 1,000 (the page's own).
- Breakeven value of a GPU-hour: what a flat load paid in the hours off, over the energy not bought, per GPU-hour not run.
- Present value of the cost: the upfront cost, and each year's cost changed by the yearly rate, discounted at the hurdle rate.
- Fixed price with the same present value: market energy only.
- All-in per GPU-hour: present value of the cost over the present value of the GPU-hours run.
- B against A: the upfront cost of B at which the two present values are equal; and, when one costs more upfront and both count the same years, the rate that extra cost returns, stated beside that scenario's hurdle rate.

## Session 190's work

- Kept intact: no line of the replication, the CSV, the do-file, the mirror or the three downloads changed. `tests.test_session190` and `tests.test_session190_replication`: 46 tests pass. `check-datacenter-face`: 23 of 23.
- **Finding 1** (a year held in part gives the rule 100 hours and "if perfectly foreseen" 76): not changed. The block does not use the foreseen load. Flagged in section 4.14 of the algorithm note and in the Method note's new part.
- **Finding 2** (New York's real-time twelve months stay at July 2025 to June 2026): not changed. The block stands on those months for New York in real time and each row says so. Flagged in both notes.
- The algorithm note's numbered sections are unchanged (session 190's test pins the list), so the new text is 4.14, after 4.13.

## Pulls and spend

- Outside hosts: 0 requests. None approved, none made.
- Production: read only. One internal-view read of the page for the "before" text; after the landing, the browser checks and the snapshots.
- Supabase: anon reads only, through the local builds and the checks.
- Model spend: USD 0. No model call.
- Nothing under the data lock: no table written, no load, no migration.
- The precheck ran first (`python scripts/precheck.py --what "session 194"`): six of six passed, the machine on duty from 10:04 UTC.

## Checks run

Outputs under `runs/session194/`.

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit`, twice | 0, 0 | no type error |
| Site build, first and of the final library | 0, 0 | `build1.out`, `build2.out`; no "statement timeout" line in either |
| `test-datacenter-finance.mjs` | 0 | 72 of 72 |
| `tests.test_session194` | 0 | 29 of 29, first run |
| Neighbours (138, 140, 149, 163, 179, 186, 190, 190 replication, 194) | 0 | 246 tests |
| `check-datacenter-scenarios.mjs`, local | 1, then 0 | first run 76 of 77: my check pointed at a bar with no lower step; then 77 of 77 on the final build |
| `check-datacenter-face.mjs` (190's) | 0 | 23 of 23 |
| `check-datacenter.mjs` | 0 | 58 of 58 |
| `check-how-soon.mjs` | 0 | 42 of 42 |
| `check-values`, pages under `/cost-of-power`, twice | 0, 0 | 3,289 of 3,289 both times |
| `check-routes` | 0 | 159 pages in review asked as a visitor, 0 failed |
| Page text, production before against local after | 0 | 0 missing or changed, 136 added (`text_compare.out`) |
| Em dashes in the files written | 0 | none |

- **Not run:** the full `check-values` (cost-of-power pages only); `check-seller-scenarios.mjs` and `check-battery-scenarios.mjs` (no file of theirs was changed).
- **Not verified:**
  - The scenario numbers carry no `data-check` key, so `check-values` does not cover them. The browser check recomputes them with the library, and the library is held to the Python mirror.
  - Only headless Chrome. Not tried with JavaScript off: the block needs it, and the plain form then drops the scenarios.
  - No region on this build's files holds twelve months with no day-ahead price, so the "flexible way not held" branch of the browser check did not run. The library's test covers it.

## Open questions

Choices made without you, each reversible.

1. **The eight assumptions.** The prompt names none. I chose what moves a buyer's cost: how it runs, the two the page already cites, other charges, the change of prices, an upfront cost, the years and the hurdle rate.
2. **The four defaults with no source** (above). I used no figure from memory. If you hold a cited term or cost of capital for a datacenter, it replaces 20 years and 8 percent.
3. **No price of a GPU-hour is assumed.** The block gives the breakeven instead. With a cited price, a row "what the GPU-hours not run would have earned" could follow.
4. **No contract price among the assumptions.** The contract box promises its terms never leave the device; an assumption lives in the address. The fixed-price row is the breakeven a contract is set against.
5. **Power per GPU and the overhead ratio default to "Your load"**, not to 1.3 and 1.56, so that a scenario at its defaults always equals the headline. Two places hold one idea, as on the other two pages; I recommend letting scenario A drive the headline in a later session, on all three.
6. **The flexible way, when "Your load" is flat, is 100 hours a year** (the form's default). To compare another number of hours, set it under "Your load".
7. **The chart shows all-in power per GPU-hour, not present value.** Present value does not move with the GPU's power or the overhead ratio.
8. **A lower overhead ratio shows no rate of return.** It changes the GPUs a MW powers, not the energy bought. The GPU-hour rows carry it.
9. **No rate is stated when A and B count different years.**
10. **The "Reset" link of "Your load", the view switch and the region links in the folds drop the scenarios.** Show and the grid keep them.
11. **No usage count is sent from the block**, as on the battery and generator pages. Your ruling is still open for all three.
12. **The run bar of the chart uses the "lowered" and "raised" colours** for "to flat" and "to flexible". Its hover says which way it is.
13. **The delivery charges of Texas are not offered as a default** for "Delivery and other charges". Session 138 ruled they are never added to the market cost; the reader can type them.

## Found, not changed

- `CLAUDE.md` says three pages are live; `site/lib/release.ts` holds no live page (session 189 noted the same).
- The page builds its "last twelve months" for a flexible load's page and a flat load's page from the same months, so the two pages hand the block the same two ways. A test holds that.

## Landing

- Landed as merge `22f1ec64` on `main`, 11 October 2026.
- No freeze (`python scripts/freeze.py status`, exit 0).
- `origin/main` moved twice while the session ran, and was merged in each time with no conflict:
  - session 193 (`ad0307b1`, the `/network` map): merged as `76d60822`. On that commit: the whole suite in a clean copy, exit 0, 3,328 tests, 235 skipped (`suite_clean.out`); `npm run build` in the main copy, exit 0; `check-datacenter-scenarios` 77 of 77, `check-datacenter-face` 23 of 23, `check-routes` 0 failed, `check-values` on the cost-of-power pages 3,289 of 3,289.
  - session 185's night report (`a8067cca`, four report files and nothing else): merged as `d74a4ec3`, the commit pushed. On it: `npm run build`, exit 0; the tests of sessions 185, 190 to 194, exit 0, 95 tests. **The whole suite was not run a second time in the clean copy for those four report files**; GitHub's run of the whole suite on the pushed commit passed.
- `s194-before` at 10:38:25 UTC, its own command, exit 0, 25 pages, 0 failed.
- Pushed `task/194-datacenter-decisions` (`d74a4ec3`) at 10:38:35 UTC. "code branch" run 38132675274: success. Merge `22f1ec64`.
- Vercel production: "Deployment has completed", recorded 10:46:24 UTC.
- `s194-after` at 10:46:49 UTC. Comparison: **0 differences on the 25 pages** (`compare_194.out`, exit 0). Expected: every page is in review, so a visitor sees the in-review page before and after.
- On production, internal view: `check-datacenter-scenarios` 77 of 77, `check-datacenter-face` 23 of 23, `check-routes` 0 failed (`prod_check_*.out`).
- The remote branch was removed by the merge; no `task/194` or `wip/194` branch is left on GitHub but the one that carries this report.
- This report's landing lines reach `main` by a second push (`task/194-report`), a change to this file only, with a snapshot pair of its own (`s194r-before`, `s194r-after`). If that comparison shows any difference, a line is added at the very top of this report; no such line means 0 differences.

## The prompt

"Session 194: "What a datacenter pays" decisions layer. Unattended: do not stop to ask questions; make reasonable choices and list them under Open questions. Model spend USD 0. No pulls. No em dashes anywhere. Work on branch task/194-datacenter-decisions, land to main with the snapshot rules in CLAUDE.md. Mirror what 179 did for the battery and 186 did for the generator: an assumptions panel with cited defaults the user can change, two scenarios A and B side by side, breakeven and hurdle-rate framing, neutral wording that helps the user decide without recommending. Keep 190's correctness work intact; leave 190's findings 1 and 2 as they are and flagged in the Method notes. One tool, one page, one address. Charts hover. Report archive/sessions/SESSION_194_REPORT.md: short bullets, every number changed and why, click-by-click review steps with full URLs."
