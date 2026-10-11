# Session 186 report: What a generator earns, decisions

11 October 2026, 04:12 to about 05:05 UTC, unattended. Branch `wip/186-generator-decide`, landed as merge `2c0be0cf`. Model spend USD 0, no model call. No pull: no request to any publisher.

## Read these first

- Built: one new section on `/cost-of-power/seller`, "Scenarios A and B", after "With your contract": eight assumptions with defaults and Resets, two scenarios on eight rows, a sensitivity chart. Computed in the browser; the address keeps both scenarios.
- **No existing number moved.** 1,398 of 1,398 checked values on the seller addresses equal the model. The page's visible text at its bare address: 0 lines missing or changed, 133 added, all in one block. Snapshot comparison of the landing: 0 differences on 25 pages.
- **Four of the eight rows are the same in A and B by construction.** None of the eight assumptions is inside the model, so revenue, the capture price, the worst month's amount and the pair with a battery are the page's own in both columns. Coverage, NPV, IRR, the contract price and the worst month's coverage differ.
- **Two defaults have no source in the repository: the hurdle rate and degradation**, as on the battery page. The page says so beside each. They need your ruling (below).
- **Two older checks of this page were changed.** Both banned the word "assum" anywhere on the page's face. They now leave the new block out of that one scan and hold the rest as before.

## What to review

`https://erw-flame.vercel.app/cost-of-power/seller` (internal view). Figures are of the model's snapshot as it stood on 11 October 2026.

1. Open the address with nothing after it. Scroll past "With your contract" to "Scenarios A and B".
   - A beige panel: "Scenario A" (filled) and "Scenario B", then "Copy A to B" and "Reset all of A".
   - Eight fields in this order: Capital cost 1375, Debt share 60, Interest rate 8, Term of the debt 35, Fixed O&M 12.5, Degradation 0, Project life 35, Hurdle rate 8. Under each: "Default ..." and its source. Each Reset is grey.
   - Under the panel, a table headed "For 100 MW of solar", columns A and B, both the same:
     - Revenue, last twelve months: USD 59.85 (the first headline number).
     - Capture price and ratio: USD 23.27, "72.3 percent of USD 32.17" (the second headline number).
     - The worst month: USD 139,299, "February 2024, of 99 months; coverage that month 0.06 times".
     - Debt coverage: 0.67 times (the third headline number).
     - NPV at the hurdle rate: USD -82.31 million.
     - IRR: none.
     - Contract price at which coverage reaches 1.25 times: USD 39.14, "on 2,580 MWh a year per MW".
     - Revenue with and without the battery beside it: USD 11.64 million with, USD 6.33 million without.
     - What differs: "A and B hold the same assumptions."
   - The address bar still has nothing after `/seller`.
2. In Capital cost type `1500`.
   - Column A: coverage 0.61 times, NPV USD -94.81 million, contract price USD 42.26. Column B does not move.
   - The headers read "capex 1,500 USD/kW" under A and "capex 1,375 USD/kW" under B.
   - Last row: "B: capex USD 1,375 per kW against 1,500."
   - The address ends `?ac=1500`. The Reset beside Capital cost is now active.
3. Click "Scenario B". Type Hurdle rate `10`, Term of the debt `10`, Degradation `0.5`.
   - Column B: coverage 0.39 times ("debt payments USD 12.29 million a year"), NPV USD -87.3 million, IRR -1.3 percent, contract price USD 64.42.
   - Sentence under the table: "Scenario B, 100 MW of solar: at a hurdle rate of 10 percent, NPV is USD -87.3 million."
4. The chart "How far each assumption moves NPV, scenario B": eight rows, largest first (Capital cost, USD 9.49 million). Point at the first row.
   - Under the chart: "Capital cost, moved by USD 100 per kW: NPV is USD -77.81 million at 1,275 and USD -96.8 million at 1,475; USD -87.3 million at 1,375."
   - Click "The chart as a table": the same figures in a table.
5. Copy the address and open it in a new tab: the same inputs and numbers, B in view. The full link:
   - `https://erw-flame.vercel.app/cost-of-power/seller?ac=1500&bt=10&bd=0.5&bh=10&v=b`
6. Click "Copy A to B": the headers empty, the last row reads "A and B hold the same assumptions.", the address ends `?ac=1500&bc=1500&v=b`.
7. Click "Reset all of B": every field of B returns to its default.
8. In "Your plant" on the left choose "West hub (HB_WEST)" and click Show: revenue in both columns becomes USD 47.51, "priced at the West hub (real-time prices)". The scenarios are still set.
9. Choose asset Wind: Capital cost becomes 2100 and the life 30 in both scenarios (a typed capital cost, fixed O&M, term or life is dropped with the asset; a typed debt share, interest rate, degradation or hurdle rate stays).
10. The other assets, each at its bare address (the hub average, the defaults):
    - `https://erw-flame.vercel.app/cost-of-power/seller?asset=wind`: revenue USD 83.57, contract price USD 56.85 "on 3,028 MWh a year per MW".
    - `https://erw-flame.vercel.app/cost-of-power/seller?asset=battery`: the contract row reads "a toll on the whole of the capacity, USD per kW-month", USD 8.90; NPV USD -75.13 million; the battery row reads "not modeled" (hover for the reason).
    - `https://erw-flame.vercel.app/cost-of-power/seller?asset=peaker`: "Margin over fuel" USD 48.15, toll USD 8.34.
11. Other grids:
    - `https://erw-flame.vercel.app/cost-of-power/seller?iso=caiso&asset=solar`: USD 28.45; USD 6.87 million with the battery, USD 2.98 million without.
    - `https://erw-flame.vercel.app/cost-of-power/seller?iso=nyiso&asset=wind`: the battery row reads "not modeled".
    - `https://erw-flame.vercel.app/cost-of-power/seller?iso=isone&asset=solar&hub=.Z.MAINE`: every row reads "not held", with no chart (no twelve months are held there).
12. On a phone (390 px): each row's label runs across the width with A and B under it. Screenshots: `runs/session186/shots/seller-scenarios-compared-phone.png`, `seller-scenarios-default-phone.png`.

`https://erw-flame.vercel.app/data/methods/generator_earns_algorithm` (internal view): section 11, "Scenarios A and B": every formula.

## The defaults and their sources

| Assumption | Default | Source |
|---|---|---|
| Capital cost, USD per kW | solar 1,375; wind 2,100; battery 610 and 1,110; peaker 1,300 | Lazard LCOE+ June 2025, midpoints (`lib/merchant.ts`, `DEFAULTS`) |
| Debt share | 60 percent | Lazard: "60% debt at an 8% interest rate" (`docs/methods/cost_of_power.md`) |
| Interest rate | 8 percent | the same |
| Term | the asset's life | Lazard: "Economic life sets debt amortization schedule" |
| Fixed O&M, USD per kW a year | 12.5; 32.25; 11.2 and 22; 13.5 | Lazard, midpoints |
| Degradation | 0 percent a year | **none held** |
| Project life, years | 35; 30; 20; 30 | Lazard |
| Hurdle rate | 8 percent | **none held**: set equal to the interest rate |

## What was built

- `site/lib/seller/finance.ts`: pure module, no import. Debt payment, flows to equity, NPV, IRR by bisection, coverage, a month's coverage, the contract price, the toll, sensitivity, the address parameters.
- `site/app/cost-of-power/seller/SellerScenarios.tsx`: the panel, the table, the chart.
- `site/app/cost-of-power/seller/page.tsx`: one section added, and the figures it hands the block. `SellerForm.tsx`: Show, the grid, the asset and "Reset the costs" carry the scenarios.
- `site/scripts/test-seller-finance.mjs` (36 hand cases, and the battery page's library on 400 seeded cases: equal exactly).
- `site/scripts/check-seller-scenarios.mjs` (78 assertions in a browser, 1280 and 390 px).
- `tests/test_session186.py` (23 tests): a Python mirror of every formula against the library on 309 cases to 1e-6, and the page's source.
- `docs/methods/generator_earns_algorithm.md`, section 11; `docs/tools.md`, one line.

## The formulas in one place

- Per kW. Debt payment: capex x share x crf(rate, min(term, life)). Solar default: USD 70.79 per kW, USD 7,078,769 for 100 MW, the page's own.
- Revenue of the last twelve months repeats every year of the life, falling by the degradation rate.
- NPV and IRR are to equity, after debt payments.
- Contract price, solar and wind: (1.25 x debt + fixed O&M) / the last twelve months' energy, USD per MWh, for the whole of the energy.
- Contract price, battery and peaker: a toll, (1.25 x debt + fixed O&M) / 12, USD per kW-month.
- The worst month's coverage: (the month less a twelfth of fixed O&M) over a twelfth of the debt payment.

## Pulls and spend

- Outside hosts: 0 requests. None approved, none made.
- Production: read only. One internal-view read of the page for the "before" text; after the landing, the two browser checks and the two snapshots.
- Supabase: anon reads only, through the local build and the checks.
- Model spend: USD 0 of USD 0. No model call.
- Nothing under the data lock: no table written, no load, no migration.

## Checks run

Outputs under `runs/session186/`.

| Check | Exit | Result |
|---|---|---|
| Site build, first; and of the committed tree | 0, 0 | `build1.out`, `build2.out` |
| `test-seller-finance.mjs` | 0 | 36 of 36 |
| `tests.test_session186` | 1, then 0 | first run: 2 failed, both mine (a slip in the mirror's hurdle step; a field named `worst`); then 23 of 23 |
| Neighbours (51, 107, 145, 162, 178, 179, 183, 186) | 0 | 192 tests |
| `check-seller-scenarios.mjs`, local | 0 | 78 of 78 |
| `check-seller.mjs`, local | 1, then 0 | first run stopped: I left out its loader flag; then 44 of 44 |
| `check-seller-deeper.mjs`, local | 1, then 0 | first run: 1 failed ("assum" on the face); after the change 51 of 51 |
| `check-seller-face.mjs`, local | 0 | 24 of 24 |
| `check-routes`, local | 1, then 0 | first run: `/prices` showed 17 "no data" blocks against 8; second run on the same build 159 of 159 |
| `check-values`, seller pages | 0 | 1,398 of 1,398 |
| Page text, production before against local after | 0 | 0 missing or changed, 133 added (`text_compare.out`) |
| Whole suite, clean copy at `0fe7ba99` | 0 | 3,085 tests, 233 skipped |
| Whole suite, clean copy at `d7655083` (the commit pushed) | 0 | 3,085 tests, 233 skipped |

- `/prices` is not this session's page. The first request after a local build read short; I did not trace it further.
- **Not run:** the full `check-values` (seller pages only); `check-battery-scenarios.mjs` (no battery file was changed, and a test holds that).
- **Not verified:**
  - The scenario numbers carry no `data-check` key, so `check-values` does not cover them. The browser check recomputes them with the library, and the library is held to the Python mirror.
  - Only headless Chrome. Not tried with JavaScript off: the block needs it, and the plain form then drops the scenarios.

## The landing

- No freeze (`freeze.py status` exit 0). `origin/main` had not moved.
- `186_before` at 04:41:01 UTC, its own command, exit 0, 25 pages.
- Pushed `task/186-generator-decide` (`d7655083`) at 04:41:18. "code branch" run 38112372162: success. Merge `2c0be0cf`.
- Vercel production: "Deployment has completed", recorded 04:50:34 UTC.
- `186_after` at 04:50:53 UTC. Comparison: **0 differences on the 25 pages** (`compare_186.out`, exit 0). Expected: every page is in review, so a visitor sees the in-review page before and after.
- On production, internal view: `check-seller-scenarios` 78 of 78, `check-seller-face` 24 of 24 (`prod_check_*.out`).
- This report reaches main by a second push (`task/186-report`) with its own before and after snapshot. It changes this file only. If that comparison shows any difference, a line is added at the very top of this report; no such line means 0 differences.

## Decisions made without you

- **The block stands after "With your contract"**, where the battery page has it.
- **The capture price row is the headline's "price received"** (23.27, from the capture file), not the span table's 23.20, so the row equals a headline number. Item 8 of session 183's list is still open.
- **"The worst month" is the lowest of every month held** (the first of the page's "worst three months"), not of the last twelve.
- **The contract price is for the whole of the energy** (solar, wind), so it does not depend on the market price. **For a battery and a peaker it is a toll per kW-month**, the battery page's formula: their energy depends on the price.
- **"With and without the battery" is the co-optimized pair against the plant alone, both at day-ahead prices**, the first row of "With a battery beside it". Revenue only: a scenario holds no battery cost.
- **The scenarios do not read the "Your plant" panel's fixed O&M and debt payments, or the typed contract**, as on the battery page. At the defaults the panel and the scenarios agree.
- **A change of asset drops a typed capital cost, fixed O&M, term and life**; the grid and the hub keep everything.
- **The links in the capture table open a hub afresh without the scenarios**, as they already dropped the size. The hub list in "Your plant" with Show keeps them.
- **No usage count is sent from the block.** The contract box says nothing typed there is sent; the same question is open for the battery page.
- **The chart's code is a twin of the battery page's**, not shared. Sharing it meant changing the battery page's file, which session 179's tests pin. The arithmetic is held equal by a test.
- **The two older checks leave the block out of their method-word scan.** The reversible choice: the rule stays for every other part of the face.
- Chart colours: the site's categorical slots 1 and 2, as on the battery page. Not red and green.

## For Samuel's ruling

1. The hurdle rate's default and its source. As I recall it, Lazard's sentence continues "and 40% equity at a 12% cost". I could not check it here (no pull, and the repository quotes only the debt half), so I did not use it. If the PDF says so, 12 percent is the cited default for both pages.
2. The degradation rate's default and its source (0 today, on both pages).
3. Whether a scenario should also hold its own hub, or the battery beside it with the battery's cost. Either would make more rows differ between A and B. Not done: the brief names eight assumptions.
4. "Your plant" has Fixed O&M and Annual debt payments, and the scenarios have their own. I recommend letting scenario A drive the headline in a later session, on both pages.
5. Whether the usage count belongs on these two pages.
6. One shared chart component for the two pages. I recommend it, with session 179's test updated in the same session.

## Found, not changed

- In "Your plant", changing Size and clicking Show keeps the old size's debt payment in the address (50 MW to 200 MW kept `ds=3539385`). The headline coverage is then for the wrong debt until "Reset the costs" is clicked. This is older than this session. The scenarios are not affected: they compute their own debt.

## To finish

- Nothing is held. Rule on the six items above.

## The prompt

"Session 186 (long end 3:00): What a generator earns (/cost-of-power/seller), decisions, exactly as session 179 did for the battery: (1) an assumptions panel with only what matters, each with its cited default and a Reset: capex USD per kW by asset (Lazard), debt share, interest rate, term, fixed O&M, degradation percent a year, project life, hurdle rate; computed in the browser. (2) Two scenarios, A and B, as columns with the same rows: revenue last twelve months (USD per kW), capture price and ratio, the worst month, debt coverage, NPV at the hurdle rate, IRR, the contract price at which coverage reaches 1.25x, revenue with and without the battery beside it; each header shows only the inputs that differ; a last row says in words what differs; "Copy A to B"; the address keeps both. No commentary, no recommendation, sentences state numbers. (3) A sensitivity chart of NPV against each assumption for the scenario in view. Land, report in short bullets with click-by-click steps, stop." Unattended; the rules of CHAIN_OCT8_PROMPT.md and CHAIN_OCT10_PROMPT.md; model spend USD 0; no pull; deploys allowed.
