# Session 298 report: the generator and datacenter pages, the section 9 rulings and the shared components

19 October 2026, from 07:23 UTC, unattended, on samueloldlaptop (the code machine), the fourth session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/298-generator-datacenter` in the worktree `erw-296`, from session 297's landed commit; lands on main as `task/298-generator-datacenter`. Model spend USD 0: no model call. No pull (one read of Potomac Economics' report, below), no warehouse data written.

## Read these first

- **The CAISO peaker's run rule counts California's allowance** (ruling 1a). The page's snapshot carries, for CAISO, the carbon cost of the fuel on its hour grid in USD per MMBtu: the latest current auction's settlement price (CARB, the internal table `carb_auction_allowance_prices`) times 53.06 kg CO2 per MMBtu (EPA, 40 CFR part 98, Table C-1): USD 1.37 to 1.72 per MMBtu, USD 32.48 per tCO2 at the latest auction. The peaker runs where `price > (Henry Hub + carbon) x heat rate + variable O&M`. At the defaults the CAISO peaker's margin over fuel over the last twelve months falls from USD 43.19 to 19.66 per kW and its hours run from 2,294 to 624; ERCOT is unchanged. The figures show on the page with the source; no settlement price is in a download.
- **The series was written into the committed snapshot by the same rule the builder now has**, from the table held on this machine (`warehouse/derived/merchant_revenue.py`, `allowance`): the data machine's next rebuild gives the same series, and its monthly table's CAISO peaker figures will then carry the allowance too (today the page always solves CAISO's peaker in the browser, so the rule holds whatever the table says).
- **Solar's degradation default is the ATB's 0.7 percent a year** (ruling 7a): the default solar case's NPV moved from USD -74.16 million to -76.66 million (USD -741.60 to -766.62 per kW); no IRR either way. The page's source line carries a decisions line saying so, and the methods note's row.
- **Potomac Economics' 2024 State of the Market Report is a cross-check row** (ruling 6a): the net revenues of a new combustion turbine in ERCOT averaged USD 68 per MWh in 2024 against a cost of new entry of 102 to 106 (page 80, Figure 56); ours, the ERCOT peaker's 2024 margin over fuel, is USD 34.01 per MWh run (71.59 per kW-year); the page counts 21 published figures. Read from the report's PDF (its page is a figure; the sentence is quoted).
- **Everything else moved nothing:** `check-seller-deeper.mjs` retired (4a, 4d); the PPA term's default was already the asset's life (5a); the datacenter page's 1a, 3a, 6a and 7a are as built; its 5c line appears only for a load that runs in under a tenth of the hours; 8a is in the shared field (every decision page's field now says a clamped value, the battery's words its own); the Financing fold and the hover tips are carried to the generator and datacenter pages (open to start, so nothing hides).

## What to review

In the internal view: open https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN> first.

1. https://erw-flame.vercel.app/cost-of-power/seller?iso=caiso&asset=peaker : "Margin over fuel, last twelve months: USD 19.66 per kW"; the panel's grey note ends with California's allowance and its source; type 9 into "Heat rate": the figures recompute with the allowance still in the rule.
2. https://erw-flame.vercel.app/cost-of-power/seller : "Is it worth building?": the panel sits under "Financing", open; close it and read its line. "Degradation, percent a year: 0.7, Default 0.7. NREL, Annual Technology Baseline 2025, utility-scale PV ...". The source line: "Checked against: 21 published figures (..., Potomac Economics)" and "Decisions of 18 October 2026 (session 298): ...".
3. Point at the two chart titles' marks: the hover tips.
4. https://erw-flame.vercel.app/cost-of-power : the panel under "Assumptions", open; type 99999 into "Capital cost" (or any field): the line "99,999 was typed: the field runs from ... so ... is used." under it.
5. https://erw-flame.vercel.app/cost-of-power?run=hours&n=8000 : a load off 8,000 hours a year: the line under the headline, "This load ran in N percent of the hours held, fewer than one in ten ...".
6. The notes: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generator_earns_algorithm.md ("Session 298" and the two new rows under "Cross-checks"); https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_pays_algorithm.md ("Session 298").
7. Screenshots: `docs/brand/review-298/`.

## What was done

- `site/lib/merchant.ts`: `co2` and `co2_source` on a grid's snapshot, `CO2_PER_MMBTU`, the run rule with the carbon cost, a grid with the series always solved in the browser. `warehouse/derived/merchant_revenue.py`: `allowance`, `CO2_GRIDS`, the hourly series and the monthly cost for CAISO, the snapshot's `co2`. `site/data/merchant_snapshot.json`: CAISO's `co2` (18,288 hours) and `co2_source`, written by `runs/chain_oct19` with the builder's rule from the table on this machine; nothing else in the file changed.
- `site/app/cost-of-power/seller/model.ts`: the allowance words in the panel's note; solar's `deg` and `degSource` from `SOLAR_DEG` (`site/lib/seller/finance.ts`). `page.tsx`: the count 21, Potomac among the publishers, the decisions line; the two chart notes as `Tip`s. `SellerScenarios.tsx`: the Financing fold. `scripts/check-seller-deeper.mjs` to `scripts/_retired/` (its README row). `scripts/check-seller-scenarios.mjs`: solar's default degradation.
- `site/app/cost-of-power/page.tsx`: the 5c line. `LoadScenarios.tsx`: the Assumptions fold. `site/components/decisions/ScenarioBlock.tsx`: `fold`, and `NumberField`'s own clamp words. `site/components/tool/ToolPage.tsx`: `ChartFrame`'s `tip`.
- Notes: the generator note's "Session 298" and two rows (solar's, Potomac's), the datacenter note's "Session 298", the generator pack's count. Tests: `tests/test_session298.py` (11); sessions 196, 253, 257 and 263 follow (each line marked).

## Checks

| Check | Exit | Notes |
|---|---|---|
| `tests/test_session298.py` and sessions 186, 194, 195, 196, 235, 253, 257, 263, 264, 296 | 0 | |
| `eslint`, the cost-of-power files | 1 | the errors are `LoadAnswers.tsx`'s (pre-existing, "Cannot create components during render", untouched); the files changed are clean |
| Impeccable `detect` on the six page and component files | 0 | no finding |
| `npm run build` (worktree), twice | 1, 0 | the first a typing slip in the datacenter fold's line, fixed |
| `check-values.mjs`, the cost-of-power pages | 0 | 1,287 of 1,287; against session 295's run: the generator's 234 and the datacenter's 225 keys identical in value, none gone, none new |
| `check-seller-scenarios.mjs` | 1, then 0 | 106 of 106 once the script learnt solar's 0.7 |
| `check-datacenter-scenarios.mjs` | 0 | 119 of 119 |
| `check-decisions-face.mjs` (the three pages) | 0 | 144 of 144 |
| Captures at 1280 and 390, three addresses | | no sideways scroll; `docs/brand/review-298/` |
| Suite, clean copy (`erw-check`) | SUITE | |
| `scripts/freeze.py status` | 0 | no freeze |

## Landing of session 297 (recorded here: session 297's report is in that landing's own commit)

- Pushed `task/297-battery-finance` at `94f66fd1` at 07:23 UTC; GitHub's checks passed (run 39215617893) and merged it as `c112456a` at 07:31; the after snapshot was taken at 07:42 (no new style sheet appeared within ten minutes, as the session changed no style; the script took it then).
- Snapshot `s297-before` (07:22:44) against `s297-after` (07:42:06): 25 pages, 0 differences. Expected: every page the session touched is in review. Nothing unexpected.
- The clean-copy suite of session 297 was stopped once by the harness for low memory while the session was idle (a background job); it was run again in the foreground and passed (4,329 tests).

## Landing

LANDING

## Decisions made without you

- **The allowance series is in the page's snapshot, in USD per MMBtu, not the settlement prices**: the page recomputes the peaker in the browser at the reader's heat rate, so the hourly carbon cost must reach it. The table is internal; what is public is a derived cost, with the latest auction's price named in the panel's note (CARB publishes the settlement prices itself). No download carries it. Reversible: the series and the words.
- **The emission factor is EPA's 53.06 kg per MMBtu** (40 CFR part 98, Table C-1), the one factor the rule needs; the ruling named none.
- **The CAISO peaker is always solved in the browser** while the grid has the series, so the rule holds at the default heat rate whatever the monthly table holds; its figures are not check-values keys on that address (the address is not a check-values page) until the data machine's table carries the allowance.
- **The folds on the generator and datacenter pages open to start**, so nothing hides and no number moves; the battery page's three closed sections are its own ruling.
- **The datacenter's chart note is not a tip** (it carries a legend, no note); its chart is session 303's.
- **Potomac's figure is quoted per MWh**, as the report states it in words; its per kW-year figure is a chart image and is not typed.

## For Samuel's ruling

- The data machine reruns `merchant_revenue.py` so `merchant_revenue_monthly` and the snapshot carry the allowance from its own build (the series here is the same rule run on this machine's copy of the table).
- Whether the allowance series (a derived cost, USD per MMBtu) may stay in the public snapshot, or must be served another way; the settlement prices themselves are not in any download.
- Ruling 8a's words on the generator and datacenter pages are the shared component's ("... the field runs from 0 to 10,000, so 10,000 is used."); whether each page should carry its own.

## Files

- New: `tests/test_session298.py`, `docs/brand/review-298/`, this report.
- Changed: `site/lib/merchant.ts`, `site/lib/seller/finance.ts`, `site/app/cost-of-power/seller/model.ts`, `page.tsx`, `SellerScenarios.tsx`, `site/app/cost-of-power/page.tsx`, `LoadScenarios.tsx`, `site/components/decisions/ScenarioBlock.tsx`, `site/components/tool/ToolPage.tsx`, `site/data/merchant_snapshot.json`, `warehouse/derived/merchant_revenue.py`, `site/scripts/check-seller-scenarios.mjs`, `site/scripts/_retired/README.md`, `docs/methods/generator_earns_algorithm.md`, `docs/methods/datacenter_pays_algorithm.md`, `docs/reviews/packs/generator.md`, `tests/test_session{196,253,257,263}.py`; moved: `site/scripts/check-seller-deeper.mjs` to `site/scripts/_retired/`.
