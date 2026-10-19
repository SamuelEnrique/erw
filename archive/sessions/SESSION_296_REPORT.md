# Session 296 report: the battery page, pass 1 (Samuel's ten rulings of 15 October)

19 October 2026, from 05:15 UTC, unattended, on samueloldlaptop (the code machine), the second session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/296-battery-pass1` in the worktree `erw-296`, from session 295's merge; lands on main as `task/296-battery-pass1`. Model spend USD 0: no model call. No pull (one read of NREL's cost report, below), no warehouse data written.

## Read these first

- **The page's structure, its three questions and every figure at the defaults are as they were**, with three things the rulings move: the 8-hour page's cost figures (item 8: NREL's Annual Technology Baseline 2025, a capital cost of USD 2,300 per kW and fixed O&M of 92, where a straight line through Lazard's 2- and 4-hour midpoints gave 2,110 and 43.6), the sensitivity chart (item 7: the sourced range by default, six rows, where ten rows moved by one step each), and the income table's columns (item 6: the calendar years, the last twelve months and your own window; "last three full years" and "without February 2021" are gone, no window being the ERW's).
- **The ATB's figures were read from NREL's own cost report** (Cole, Karmakar and Mann, "Cost Projections for Utility-Scale Battery Storage: 2025 Update", NREL/TP-6A40-93281, June 2025, section 2.2: energy USD 241 per kWh, power USD 372 per kW, 2024 dollars; fixed O&M 4 percent; 85 percent round trip; a 15-year life; no fade rate of its own), the ATB web page holding no figure in its text. The report's PDF was fetched once from docs.nlr.gov; `atb.nrel.gov` and `docs.nrel.gov` do not resolve from this machine (as session 213 found on 1 October).
- **The left box is "Assumptions", five sections** (Assumptions, Headline figures, Charts, Financing, Sensitivity), two open; the twelve scenario assumptions moved into Financing with the contract as a sub-group, and the second question draws the results table alone. Every choice is in the address with the scenarios, so a view can be shared as a link.
- **`site/data/sourced_ranges.json` does not exist yet** (the data machine's session 306): the ranges are typed in `rangesOf` in `site/lib/battery/finance.ts`, in the shape that file will take, each with its source.
- **The check-values keys:** the page's default keys are the ones of before minus the two windows that left (`y3:*`, `y3_kw:total`, `avg_without:*`, `avg_without_kw:total`), plus one a stream a calendar year (`yr:<year>:<stream>`) and the per-kW keys. The 8-hour pages' keys carry the new fixed O&M and debt payment in their inputs.

## What to review

In the internal view: open https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN> first.

1. https://erw-flame.vercel.app/cost-of-power/battery : the box "Assumptions" on the left. Close "Assumptions" (press its title): the line "ERCOT, 4 hours, perfect foresight, 100 MW; this battery". Open "Financing": the twelve fields, scenario A and B, the contract as a sub-group; the line while closed reads "Scenario A: 20% debt at 8%, 12% hurdle, no contract".
2. "Headline figures": tick NPV, IRR and Payback year (six at most: the rest grey out): three more figures join the row, each scenario A's. "Charts": tick "Cash after debt" and "Debt": three charts side by side; "Scale": Log or Linear. Each chart's "Table" button.
3. "Income by stream": the columns are 2018 to 2026, the last twelve months, and "Your window" (2018 to 2026 by default, the old "every year held" average). Set "From" to 2024; tick "Uri" under "Leave out" (it takes its days out of 2021's months, so with a window from 2018 the average falls). "Chart" draws the same columns.
4. "What matters most": six rows, each at its published low and high case (point at a row: the two NPVs and the source); under the chart, the four with no published range. In the box, "Sensitivity": Percent step, 10: twelve rows... ten rows (the contract's two join with a contract); "Measured in: IRR".
5. https://erw-flame.vercel.app/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead : the 8-hour defaults (Financing: capital cost 2,300, fixed O&M 92, each "NREL, Annual Technology Baseline 2025 ..."); the headline's coverage and the results table moved with them, the revenue did not.
6. Point at "Duration" and "Strategy" marks, and at the year chart's title mark: the hover tips.
7. The code: https://github.com/SamuelEnrique/erw/compare/main@%7B2026-10-19T06:00Z%7D...main (the session's two commits); the methods note, "Session 296" under 11.1: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_earns_algorithm.md.

## What was done

- `site/lib/battery/finance.ts`: `ATB` (the report's figures), `atbCapex`, `atbFom`; `equityIn`, `paybackYear`, `npvPerEquity`, `projection` (the years for the charts); `movedValue`, `sensitivityIn` (the two modes, the two measures), `rangesOf`, `NO_RANGE`, `LAZARD_CASES`. Nothing above them changed.
- `site/lib/batterystack.ts`: `COSTS[8]` from the ATB, with `source` on each duration; `eventMonths`, `windowMonths`, `windowAverage`, `yearStream`, `windowKey`; `stat` answers `yr`, `yr_kw`, `win`, `win_kw`.
- `site/lib/battery/view.ts` (new, pure): the view and its address parameters, defaulted and bounded.
- `site/app/cost-of-power/battery/`: `Settings.tsx` (the box), `Income.tsx` (the table and its window), `ViewState.tsx`; `Scenarios.tsx` (the view held with the scenarios, the headline's eight figures, `BatteryCharts`, `BatteryFinancing`, the two modes); `page.tsx` (wires them; the year chart's sentence and the one-month share stay the page's); `BatteryForm.tsx` (the hovers; its defaults line moved to the box).
- `site/components/tool/ToolPage.tsx`: `SettingsFold`, `Tip`; `site/components/tool/SeriesChart.tsx` (new: stacked bars or lines, direct labels, three scales, Chart | Table); `site/components/decisions/ScenarioBlock.tsx`: `ScenarioPanel` on its own, `panel={false}`, a field's `clamp` words drawn by the field (no ref read in render), the legend's words from the chart; `site/app/tokens.css`: the fold and the tip.
- Checks and tests: `test-battery-finance.mjs` (21 more cases), `check-battery-scenarios.mjs` and `check-decisions-face.mjs` (the moved panel, the six rows, the percent step), `tests/test_session296.py` (15 tests), four older tests follow (178, 179, 195, 263: each line marked; session 102's pin on the year chart's sentence holds as it was, the sentence staying the page's).
- Notes: `docs/methods/battery_earns_algorithm.md` (4.5, section 6, 11.1's table and a "Session 296" part), `docs/reviews/packs/battery.md` (section 3).

## Checks

| Check | Exit | Notes |
|---|---|---|
| `npx tsc --noEmit` (worktree, before its first build) | 2 | every error a fresh worktree's (`PageProps`, `@/content/docs.json`); none in the session's files |
| `eslint` on the files changed | 0 | one pre-existing warning in `check-battery-scenarios.mjs` |
| `node scripts/test-battery-finance.mjs` | 0 | 85 cases, 21 of them this session's |
| `tests/test_session296.py` and the ten older modules whose pins or inputs moved | 0 | 232 tests |
| Impeccable `detect` on the nine files | 0 | no finding |
| `node scripts/check-battery-figures.mjs` | 0 | all 32 figures are the pack's |
| `npm run build` (worktree), three times: the first build, the chart's label fix, the merged commit `a945bad9` | 0, 0, 0 | no "statement timeout"; a junction to the main copy's packages is refused by Turbopack, so the worktree has its own |
| `check-values.mjs`, the eight battery pages, before and after the merge | 0, 0 | 660 of 660 (279 before the session: every key both runs share carries the same value; gone: `y3`, `y3_kw`, `avg_without`, `avg_without_kw`, and the 8-hour pages' keys under their old `fom=43.6`, which return under `fom=92`; new: `yr`, `yr_kw`) |
| `check-battery-scenarios.mjs`, twice (the merged build last) | 0 | 94 of 94 |
| `check-decisions-face.mjs` (the three decision pages) | 0 | 144 of 144 |
| `check-battery-face.mjs` | 0 | 22 of 22, after its two pre-existing pins were fixed (production too has five downloads; the cookie is httpOnly) |
| Captures at 1280 and 390, three addresses | | no sideways scroll (page width 390 in a 390 window); `docs/brand/review-296/` |
| Suite, clean copy (`erw-check`), `008a656f` | 0 | 4,322 tests, 244 skipped |
| `scripts/freeze.py status` | 0 | no freeze |

## Landing of session 295 (recorded here: session 295's report is in that landing's own commit)

- Pushed `task/295-games-land` at `d435b6d6` at 06:16 UTC; GitHub's checks passed (run 39208906861) and merged it as `cd2f523f` at 06:26; production served the new build at 06:28:16 (a new style sheet in the home page's HTML).
- Snapshot `s295-before` (06:15:39) against `s295-after` (06:28:36): 25 pages, 25 differences, each one line of text, after only: "The EV game in review", the menu's new Games entry (session 294's `/play/ev`) drawn in every page's in-review view. Expected: the one line the landing adds to the menu; no checked number on a visitor page (none is live). Nothing unexpected.
- The prompt expected 0 differences; the menu line is the one the EV game's entry makes, as session 288's landing saw for the Games menu.

## Landing

LANDING

## Decisions made without you

- **The box's first section is titled "Assumptions"**, as the ruling lists it, under the box's own title "Assumptions"; it holds the battery (grid, duration, strategy, size) and the units toggle. Reversible: one word.
- **The twelve scenario assumptions are "Financing"** (the ruling's summary line names the debt, the hurdle and the contract): capital cost, fixed O&M, efficiency, cycles, degradation and life are in it too, so the twelve keep their order and the panel is the shared one. Reversible.
- **At the default one chart is drawn, the year chart**, so the page's density is unchanged; the reader adds up to two more. "Adjusted" is the default scale, the page's own break rule. Reversible: `DEFAULT_VIEW`.
- **The sourced range for 8 hours** is the straight lines through Lazard's 2- and 4-hour low cases and high cases (an extrapolation, said in the hover), with the ATB's 8-hour figures inside them; for fixed O&M at every duration the high case is the larger of Lazard's high and the ATB's 4 percent of its own cost. Reversible: `rangesOf`.
- **In the sourced range the contract's two rows are not drawn** (no published case for the reader's own term); they are named under the chart, and the percent step draws them with a contract (session 211). Reversible.
- **A percent step on efficiency or cycles goes to the nearest step the model was run at**, in that direction, within the steps held (86 up by 10 percent is 94.6: the step 92); the hover and the line say so.
- **The payback year is undiscounted** (the first year the running sum of the cash flows to equity is no longer negative), "none" within the life otherwise; NPV per dollar of equity is NPV over the equity paid in at year 0.
- **A grey note that carries a checked number, a link or a download stays in view** (the one-month share, the CSV line, the awards line); the notes that explained are hover tips. The field notes "Default X. Source" stay under the fields (rule 6 of the chain, the ruling of 12 October).
- **The two ERW windows left the table** as item 6 asks; their keys (`y3`, `avg_without`) left check-values with them (listed under "Checks").
- **The ATB's figures were read from the PDF of its cost report**, one fetch, as the ATB page's text holds none.

## For Samuel's ruling

- Whether the charts' default should be the three cash charts beside the year chart (today one, the year chart, so nothing moves at the defaults).
- Whether the sourced range should give the contract a range (none is published; the percent step moves it).
- Whether the 8-hour range should take Lazard's extrapolated lines at all, or the ATB's figure alone with no range for 8 hours.

## Files

- New: `site/lib/battery/view.ts`, `site/app/cost-of-power/battery/Settings.tsx`, `Income.tsx`, `ViewState.tsx`, `site/components/tool/SeriesChart.tsx`, `tests/test_session296.py`, `docs/brand/review-296/`, this report.
- Changed: `site/lib/battery/finance.ts`, `site/lib/batterystack.ts`, `site/app/cost-of-power/battery/page.tsx`, `Scenarios.tsx`, `BatteryForm.tsx`, `site/components/tool/ToolPage.tsx`, `site/components/decisions/ScenarioBlock.tsx`, `site/app/tokens.css`, `site/scripts/test-battery-finance.mjs`, `check-battery-scenarios.mjs`, `check-decisions-face.mjs`, `docs/methods/battery_earns_algorithm.md`, `docs/reviews/packs/battery.md`, `tests/test_session{178,179,195,263}.py`, `site/scripts/check-battery-face.mjs`.
