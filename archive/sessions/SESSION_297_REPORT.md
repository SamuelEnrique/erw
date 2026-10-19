# Session 297 report: the battery's finance model, passes 2 to 4

19 October 2026, from 06:42 UTC, unattended, on samueloldlaptop (the code machine), the third session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/297-battery-finance` in the worktree `erw-296` (reused: its packages and build), from session 296's landed commit; lands on main as `task/297-battery-finance`. Model spend USD 0: no model call. No pull, no warehouse data written.

## Read these first

- **Every figure at the defaults is what it was** (660 of 660 check-values keys on the eight battery pages, no key gone, none new, no value changed): the six new assumptions default to values that move nothing (no credit, the page's own revenue cut, no augmentation, no stress repeat).
- **The investment tax credit** is a share of the capital cost taken at year 0 against the equity paid in, nothing else (no depreciation, no tax). Its hover names the IRS's credit for energy storage (section 48E) and says to confirm it before use. At 30 percent the default case's NPV rises by USD 333 per kW.
- **The fade method** is the alternative the reader switches on under Financing: the capacity fades by a rate each year, revenue follows it (an assumption: the model is not run again at a shorter duration), and augmentation restores it every 3, 5, 7 or 10 years at a cost per kWh added. Defaults: Lazard's 2.6 percent (the ATB states no fade rate of its own, "a function of the usage rate"), no augmentation, the ATB's energy component USD 241 per kWh. The cross-check row in the methods note states what it does to NPV: USD -613.19 per kW at the ATB's convention (no fade), -768.12 with augmentation every 5 years, against -697.80 by the revenue cut.
- **The stress repeats** ("what if Uri happened again") sit in "Is it worth building?" as a number for the scenario in view: each repeat adds the grid's peak stress event's window revenue once, spread evenly over the life. One repeat of Winter Storm Uri (USD 3,105.51 per kW for the default battery) takes the default case's NPV from -697.80 to +584 per kW: stated, not judged.
- **The one stress-day rule is written, not applied** (`docs/methods/battery_stress_days.md`): no rule for every grid was recorded (ERCOT's were three named events; CAISO's a rule from its notices), so the chain's rule stands: a day whose mean real-time hub price is above the 98th percentile of the trailing 365 days, or a day with an operator's emergency notice. The table that feeds the "leave out" boxes and the repeats is the data machine's to rebuild; the warehouse holds no table of ERCOT's notices, so for ERCOT the price test alone applies until one is held.

## What to review

In the internal view: open https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN> first.

1. https://erw-flame.vercel.app/cost-of-power/battery : under "Is it worth building?", the row "Stress test: scenario A repeats Winter Storm Uri, February 2021 [0] times over its life". Type 1: NPV in the results table moves from USD -69.78 million to about +58 million; coverage does not move (it reads the last twelve months). Reset.
2. In the box, open "Financing": after "Hurdle rate", "Investment tax credit" (0); type 30: NPV rises by USD 33.3 million for 100 MW. Below, the sub-group "Degradation and augmentation": set "Degradation method" to "capacity fade with augmentation" (nothing moves at the same 2.6 percent), then "Augmentation" to "every 5 years": NPV falls (three augmentations at USD 241 per kWh).
3. The shared address with all three: https://erw-flame.vercel.app/cost-of-power/battery?ai=30&ao=1&am=5&ax=1 ; the box's Financing line reads "..., no contract, 30% tax credit, capacity fade 2.6% a year restored every 5 years".
4. "What matters most", in the box "Sensitivity: Percent step": the credit's row and the fade's three rows join the chart when they are set; the sourced range draws none of them (no published range) and the line under the chart says which.
5. The methods note: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_earns_algorithm.md ("Session 297" under 11.1; the new cross-check row); the rule: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stress_days.md.
6. Screenshots: `docs/brand/review-297/` (before and after at 1280 and 390, with `after_set_*` for the shared address above).

## What was done

- `site/lib/battery/finance.ts`: six keys (`itc`, `method`, `fade`, `aug`, `augcost`, `stress`; letters `i`, `o`, `g`, `m`, `k`, `x`), `OPTIONS` for the two choices, `Ctx` (the peak event's revenue and the hours), `augmentationCost`, `sensitivityKeys`; `revenueInYear`, `incomeInYear`, `flows`, `merchantTail`, `resultOf`, `projection`, `sensitivityIn` take the context; `bound`, `scenarioNotes`, `movedValue` know a choice.
- `site/app/cost-of-power/battery/Scenarios.tsx`: the context from the page (the peak event, the hours) handed to every figure; the fields under Financing with "Degradation and augmentation" as a sub-group; `StressRepeats` in the second question. `page.tsx`: the peak event from the stress rows; "Checked against: 15 published figures". `Settings.tsx`: the Financing line names the credit and the fade method when set.
- `scripts/check-values.mjs`: the page at `?ai=30`, `?ao=1`, `?ao=1&am=5` and `?ax=2`. `test-battery-finance.mjs`: 21 cases more. `check-battery-scenarios.mjs`: the eighteen, the stress control, a choice's default in words.
- Notes: `docs/methods/battery_stress_days.md` (new); `battery_earns_algorithm.md` ("Session 297" under 11.1, the cross-check row); `docs/reviews/packs/battery.md` (the count). Tests: `tests/test_session297.py` (7); sessions 179, 196, 263 and 296 follow (each line marked).
- "worst" is "peak" everywhere: the page's tests forbid judging words, and the event is the one whose window paid the most.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `node scripts/test-battery-finance.mjs` | 0 | 106 cases |
| `eslint`, the changed files | 0 | the one pre-existing warning |
| `tests/test_session297.py` and sessions 179, 195, 196, 249, 263, 296 | 0 | |
| Impeccable `detect` on the three page files | 0 | no finding |
| `npm run build` (worktree), three times (the first, the no-range line, the count) | 0, 0, 0 | no "statement timeout" |
| `check-values.mjs`, the battery pages, twice (the last on the final commit) | 0, 0 | 660 of 660; against session 296's run: no key gone, none new, no value differs |
| `check-battery-scenarios.mjs` | 0 | 95 of 95 (after two pins of this session's own were fixed: a choice's default in words, the no-range line) |
| Captures at 1280 and 390, four addresses | | no sideways scroll; `docs/brand/review-297/` |
| Suite, clean copy (`erw-check`), first run `94e41668` | 1 | three pins of session 196 (the defaults line, the cross-check count): fixed in the next commit |
| Suite, clean copy, the final commit | SUITE2 | |
| `scripts/freeze.py status` | 0 | no freeze |

## Landing of session 296 (recorded here: session 296's report is in that landing's own commit)

- Pushed `task/296-battery-pass1` at `ab7441b0` at 06:40 UTC; GitHub's checks passed (run 39211194713) and merged it as `49903729` at 06:51; production served the new build at 06:52:10.
- Snapshot `s296-before` (06:39:28) against `s296-after` (06:52:30): 25 pages, 0 differences. Expected: every battery page is in review, so a visitor sees nothing of the session. Nothing unexpected.
- The session 296 review screenshots (`docs/brand/review-296/`) show every section of the box open: the capture opened the folds for the text and did not close them again (fixed in `runs/chain_oct19/capture296.mjs` for this session's shots, which are in the default state).

## Landing

LANDING

## Decisions made without you

- **The fade rate's default is Lazard's 2.6 percent**, since the ATB states no rate of its own (its page: degradation "a function of the usage rate"; its fixed O&M pays for augmentation). The prompt named the ATB; the hover says what each source holds. Reversible: one number.
- **The augmentation cost's default is the ATB's energy component, USD 241 per kWh (2024 dollars)**, the ATB's own cost of a kWh of battery; the ATB prints no augmentation cost as such. Reversible.
- **Under the fade method revenue is taken proportional to the capacity**, and the revenue cut is not applied; augmentation restores the capacity at the end of each period and is never paid in the last year. Stated in the note.
- **A stress repeat is spread evenly over the life's years** and added before the contract's share; coverage and the breakeven toll, which read the last twelve months, do not move.
- **The stress control sits in the second question**, beside the results it moves, for the scenario in view; it is an assumption like the others in the address (`ax`, `bx`) and the sensitivity's percent step moves it when set.
- **The stress-day rule is the chain's** (no rule for every grid was recorded); it is written, not applied, the table being the data machine's. For ERCOT the notice test waits for a notices table (none is held: nothing invented).
- **The sensitivity draws the new rows only when set** (the credit above 0, a repeat above 0, the fade's three under the fade method), as the contract's rows are drawn only with a contract; the method, a choice, is never a row.
- **"Checked against" counts 15** with the new cross-check row (the test counts the note's rows).

## For Samuel's ruling

- The data machine applies the stress-day rule to `battery_stack_stress_daily` (`warehouse/derived/battery_stack.py`), so every grid's events come from one rule; until then ERCOT's three named events and CAISO's notice days stand.
- Whether a stress repeat should fall in named years (say the first) rather than spread evenly; whether the contracted share should be paid nothing from it (today the repeat is market revenue, so the merchant share earns it).
- The credit's rate and eligibility are the reader's to confirm; whether the page should name a default rate (30 percent) rather than 0.

## Files

- New: `docs/methods/battery_stress_days.md`, `tests/test_session297.py`, `docs/brand/review-297/`, this report.
- Changed: `site/lib/battery/finance.ts`, `site/app/cost-of-power/battery/page.tsx`, `Scenarios.tsx`, `Settings.tsx`, `site/scripts/test-battery-finance.mjs`, `check-battery-scenarios.mjs`, `check-values.mjs`, `docs/methods/battery_earns_algorithm.md`, `docs/reviews/packs/battery.md`, `tests/test_session{179,196,263,296}.py`.
