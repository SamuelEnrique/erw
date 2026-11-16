# Session 7533 report: What is on an electricity bill at the done line (chain 304, second run)

16 November 2026, samueloldlaptop (code role), unattended. Worktree `erw-7533`, branch `wip/7533-learn-bill`, pushed. Model spend: USD 0 (`ERW_SPEND_CAP_USD=0`, no model API called). Tool: `/learn/bill` (in review), tool 13 of the claims file.

## At the top

- **The page's five headline figures did not show.** Since the license hold of 21 October, all five default bills' totals, wholesale sums and shares (15 figures) printed "license needed", here and on the problem set "Prices and your bill". A bill's check key names no grid, so `cost_of_power_monthly` (held by grid for ISO-NE, MISO and NYISO only) was asked about whole. No bill is in a held grid and a total reads no table. Fixed in `site/components/Num.tsx` with a test. This touches a shared component: only `bill|` keys change.
- **Two lines printed floating-point kWh**: "506.99999999999994 kWh within the Region 9 baseline" (SCE, summer, the default region) and "432.90000000000003 kWh" (SDG&E, a 333 kWh allowance). Fixed: printed to a tenth.
- **No figure of the arithmetic is wrong.** The replication: 669 of 669 figures, 20 cases. On origin/main the same morning: 652 of 669, the 17 being the two faults above (`replication/bill/replicate_on_origin_main.txt`).
- **Cross-check:** the Texas defaults equal EIA's Texas average by construction (15.88 against 15.91 cents, EPM Table 5.6.A, August 2026). PG&E's default is 38.27 cents a kWh against EIA's 39.62 for PG&E's bundled homes in 2024. SDG&E's is 55.48 against 43.63, mostly because the default bill has no baseline credit (ruling, row 7).
- **The tariffs read again today:** PG&E E-TOU-C is unchanged. CenterPoint's TC5 Refund went to 0 on 13 November, so its bill is USD 0.17 low at 600 kWh. The page states its read date, so this is left to a ruling (row 6). Oncor was not read: its robots file did not answer.
- **Data machine:** `cost_of_power_monthly` was last built on 4 October, so the wholesale month is September 2026 (data request row 69).
- **Not run:** no site build, no browser (this machine's rule). Six browser reads asked (rows 96 to 101).

## The five parts

- **The method note** (`docs/methods/bill.md`): session 335's note is kept as written. Session 7533 added "The tool as a reader meets it": the views, the fields and their defaults, the arithmetic line by line, the 14 choices by key, the cross-check table, the replication, what the tool does not hold, and the tests.
- **The replication** (`replication/bill/`): `replicate.py` (standard library, no request, writes nothing) reads the rules file, the note's arithmetic and `source_rows.csv` (the live set's rows of `cost_of_power_monthly`, read with the anon key on 16 November). The page's side is `site/scripts/bill-figures.mjs`: it draws the whole page with the site's own code, the table answered from those rows, and the calculator for each of 19 cases in `cases.json` (the five defaults, EIA's 2024 average month in each state, and cases that move every field). Result: 669 of 669, counting the numbers inside each line's words, and the PG&E lines equal Sheet 2's totals in every PG&E case. `replicate.do` holds the five default bills and their shares, with the expected values at its top. Not run (no Stata here); its Python mirror printed the same values. Also `--texas-default` (the Texas energy charges derived from EIA's row) and `--crosscheck`.
- **The cross-check:** a table in the note, ten rows. Sources: EIA Electric Power Monthly Table 5.6.A (August 2026, released 23 October 2026); EIA Electric Sales, Revenue, and Average Price 2024, Tables 5A and 6 (released October 2025); PG&E E-TOU-C and CenterPoint's tariff as posted on 16 November 2026. Robots files and terms read first.
- **The decisions block** (`site/app/learn/bill/Decisions.tsx`, mounted above the downloads): 14 choices, each with its default and source on hover. The calculator already computes in place, so each line names the field where a reader changes it. The days and SCE's share of weekdays are said not to be fields.
- **The faults** (`docs/reviews/bill-faults-2026-11-16.md`): 15 rows. 4 site faults fixed, 1 for the data machine, 10 rulings.

## Tests

Command, one file at a time: `.venv\Scripts\python.exe -m unittest tests.<file>` with `ERW_SPEND_CAP_USD=0`, in the worktree. The files that name the page, its library, its rules file, the shared `Num` component or the decisions blocks, and the four note sweeps: 55 files (`runs/s7533/tests.txt`, results in `runs/s7533/sweep/`). Results: see "Test sweep" below.

- `node --import ./scripts/tsx-register.mjs scripts/test-bill-render.mjs`: 53 of 53.
- `node --import ./scripts/battery-awards-page-register.mjs scripts/bill-figures.mjs --check`: 439 figures, as committed.
- `node scripts/test-bill.mjs` (the hand-computed bills, run by `test_session43`, `52` and `288`).
- `node scripts/check-methods.mjs`: 544 of 544 figures named, exit 0.

## What to review

- `https://erw-flame.vercel.app/learn/bill` (in review: open it with the review cookie).
  1. The five cards: "Total: 229.63 USD for 600 kWh." (PG&E), 224.76 (SCE), 332.91 (SDG&E), 95.27 (Oncor), 95.28 (CenterPoint). Each has "Wholesale energy: ... USD, ... percent of the bill, at ... USD/MWh (2026-09)": PG&E 26.91 and 11.72, SCE 23.11 and 10.28, SDG&E 23.11 and 6.94, both Texas 23.70 and 24.88. Before: "license needed" in all 15 places.
  2. Build a bill: press the SCE button and set Season to Summer. Open "Baseline credit": "507 kWh within the Region 9 baseline at -$0.10099". Under "Share in super off-peak hours" a line now reads "Not billed in summer: ...". Set Season back to Winter and the line is gone.
  3. Press SDG&E and type 333 in "Your baseline allowance". Open "Baseline credit": "432.9 kWh (up to 130 percent of your 333 kWh allowance)".
  4. Press CenterPoint and open "Inflation Reduction Act 2022 (IRA)": "Effective Rider IRA (original sheet, effective 04/28/25; ...)".
  5. Scroll to the foot. "Decisions on this page (each with its default and its source on hover)" sits above "Download the tables". Open it: 14 lines. Hover or tap an "i": Default and Source.
- `https://erw-flame.vercel.app/learn/problems/prices-and-your-bill`: the bills' totals, wholesale sums and shares are numbers.
- `https://erw-flame.vercel.app/data/methods/bill`: the note's new section.

## Needs the key

- Nothing. The page calls no model.

## Decisions made without you

- **The license fix sits in the shared `Num` component, not in the page's keys.** The fix maps each bill to the grid of its wholesale price (`BILL_GRID`), which a test holds equal to the rules file's `iso`. The other route was to put the entity into each `bill|` key, which would have changed the keys that `check-values.mjs`, `lib/problems.ts` and `check-methods-keys.json` read.
- **`BillCalc` takes an optional `first` prop** (the bill it opens on). The page passes none, so it still opens on PG&E. It exists so a script can draw each bill without a click.
- **The CenterPoint IRA rider's label is corrected, its rate (0) unchanged.** The TC5 Refund's new rate is not taken (ruling, row 6).
- **The cross-check reads EIA's 2024 utility table, not a newer one.** EIA has discontinued the product, so 2024 is the last year it publishes.

## For Samuel's ruling

Each with the default taken. The faults file has the detail.

1. **Re-reading the tariffs.** CenterPoint's TC5 Refund went to 0 on 13 November, so its bill is USD 0.17 low at 600 kWh. Default: the page keeps the rates of its stated read date. Your call: whether the rules file is re-read on a schedule, and whether the Texas default energy charges are derived again when it is.
2. **SDG&E's default bill has no baseline credit** (55.48 cents a kWh against EIA's 43.63 for SDG&E's homes in 2024). Default: as it is, said on the page.
3. **The wholesale share** counts metered kWh (line losses of about 5 percent are left out) and sets both Texas homes against ERCOT's hub average. Default: as it is, said in the fold.
4. **A month missing one hour is "partial"**, so the page falls back a month. Default: the rule stays.
5. **Grey notes and one bill at a time** (the page standard). Default: left as they are.
6. **No "demand charge" among the ten terms; no SDG&E climate credit; the Texas default is from July's EIA figure**, not August's. Default: as they are.

## Test sweep

- 55 files, each in its own process: all exit 0, 699 tests, 3 skipped by their own rules (`test_session298`, `465`, `7509`) and 8 in `test_session7518_interconnection_read` (its table is not on this copy). Among them `test_session43`, `52` and `288` (the hand-computed bills, `test-bill.mjs`), `335` (the note and the page), `215`, `315`, `329`, `382`, `4005`, `405`, `408`, `474`, `505`, `1855`, `1898`, `2200` to `2202` (they name `Num.tsx` and the holds), the decisions-block sweeps (`237`, `298`, `299`, `462`, `463`, `465`, `1743`, `7405`, `7501` to `7518`, `7601`), the four note sweeps (`142`, `147`, `158`, `160`), `409` (keys against notes), and `test_session7533_bill` (11, new).
- A narrow type check: `tsc -p` on the page, `BillCalc.tsx`, `Decisions.tsx`, `lib/bill.ts`, `components/Num.tsx` and the problem sets' page, with what they import and the site's settings less Next's plugin. Exit 2, one message, about a file outside this change: `app/network/Network.tsx(253,70)`, no declaration for `three`. Nothing in the changed files. Not a build.
- The branch merges with `origin/main` at `900fa95fc` with no conflict (`git merge-tree`). It is based on `64da63865`; the three commits of main since touch only the shared state files and a queue file, none of this branch's files.

## Rows for the coordinator

### (a) Landing request (`docs/state/landing_request_oldlaptop.md`)

| 31 | `wip/7533-learn-bill` | (the branch's tip; given in the session's return) | `7533-learn-bill` | 7533 | 2026-11-16 | `tests/test_session7533_bill.py` (11 passed) and `site/scripts/test-bill-render.mjs` (53 of 53, the page's parts drawn to HTML without a build); `bill-figures.mjs --check` (the whole page drawn on the committed rows, 439 figures as committed); 54 older test files that name the page, its library, its rules file, `components/Num.tsx` or the decisions blocks, or sweep the notes, each in its own process: all pass (699 tests in the 55 files); `check-methods.mjs` 544 of 544; `replication/bill/replicate.py`: 669 of 669 figures over 20 cases, exit 0; a narrow `tsc` with one message outside the change (`app/network/Network.tsx`, `three`); not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 31: what it holds (chain 304, session 7533, What is on an electricity bill at the done line)

- **Stacked on** `64da63865` (origin/main of the morning). Six commits. Report: `archive/sessions/SESSION_7533_REPORT.md` on the branch.
- **What changes:**
  - `site/components/Num.tsx`, a shared component: `heldBy` for `bill|` keys only. A bill's total is never held, and its wholesale sum and share are held by its grid (`BILL_GRID`). Since 21 October the five cards of `/learn/bill` and the bill figures of `/learn/problems/prices-and-your-bill` printed "license needed"; they print numbers again. Every other key is untouched (the hold tests pass).
  - `site/lib/bill.ts`: a computed kWh in a line's words is printed to a tenth (`kwhs`). The amounts are unchanged.
  - `site/app/learn/bill/BillCalc.tsx`: an optional `first` prop, which the page does not pass, and the SCE summer line under the super off-peak share.
  - `page.tsx`: one import and one mount of the new `Decisions.tsx` (14 choices, server-drawn words, no handler, no state, no request).
  - `site/data/bill_rules.json`: version 2026-11-16.1, one rider's effective words; no rate changed.
  - New: `docs/methods/bill.md` (a section added), `replication/bill/`, `site/scripts/bill-figures.mjs`, `site/scripts/test-bill-render.mjs`, `tests/test_session7533_bill.py`, `docs/reviews/bill-faults-2026-11-16.md`.
- **What does not change:** the bills' arithmetic, every rate, the five defaults, `check-values.mjs` and its `bill|` keys, `lib/problems.ts`, `site/lib/release.ts`, every table and builder.
- **Before landing:** a site build on the landing machine (the first whole build of `Num.tsx` with the change). `check-values` on `/learn/bill` and `/learn/problems/prices-and-your-bill`: the `bill|` keys come back as checked numbers. `check-methods.mjs` with a base URL.
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review; a visitor is shown the in-review page). With the review cookie: on `/learn/bill` the 15 card figures change from "license needed" to numbers, the fold is new, and two kWh words change in the calculator; on `/learn/problems/prices-and-your-bill` the bill figures change from "license needed" to numbers. **Tables:** none.
- **After the landing:** rows 96 to 101 of `docs/state/browser_reads_wanted.md`. Row 69 of `docs/state/data_requests_done_line.md` is the data machine's and does not hold this row.

### (b) Browser reads (`docs/state/browser_reads_wanted.md`)

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 96 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | The five cards under "The default bills", at 1280 and 390 px | Each card has a number in "Total" (229.63, 224.76, 332.91, 95.27, 95.28 USD), in "Wholesale energy" and in its percent; "license needed" appears nowhere; hovering a number shows its source | wanted |
| 97 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/problems/prices-and-your-bill` | The problems that use the two bills' totals, wholesale sums and shares | Numbers, not "license needed" | wanted |
| 98 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | Build a bill: SCE, Season "Summer"; open "Baseline credit". Then SDG&E, type 333 in "Your baseline allowance"; open "Baseline credit" | "507 kWh within the Region 9 baseline at -$0.10099"; "432.9 kWh (up to 130 percent of your 333 kWh allowance) at -$0.10702"; no long decimals anywhere in the opened lines | wanted |
| 99 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | Build a bill: SCE, switch Season between Summer and Winter, at 390 px | In summer a line under "Share in super off-peak hours" begins "Not billed in summer"; in winter it is gone; the field column does not run past the screen | wanted |
| 100 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | The fold "Decisions on this page" above "Download the tables"; open it; hover and tap an "i"; at 390 px | Closed to start; 14 lines; each tip shows "Default:" and "Source:" and stays inside the screen; no sideways scroll | wanted |
| 101 | 2026-11-16 | 7533 | `wip/7533-learn-bill` (row 31) | `https://erw-flame.vercel.app/learn/bill` | Build a bill: press each of the five bills, then "Reset this bill to its defaults" | Each bill's total equals its card's (PG&E 229.63, SCE 224.76, SDG&E 332.91, Oncor 95.27, CenterPoint 95.28) | wanted |

### (c) Data request (`docs/state/data_requests_done_line.md`)

| 69 | 2026-11-16 | 7533 (chain 304, samueloldlaptop; branch `wip/7533-learn-bill`) | `cost_of_power_monthly` (`warehouse/derived/cost_of_power.py`) | Last built 4 October 2026 (header: retrieved 20261004T022612Z); the live set holds the same rows, so on 16 November the latest complete month is September 2026 and October 2026 holds 48 hours. Rebuild it through October 2026, load it to the live set, and put it in the daily run if it is not there. `/learn/bill`, `/learn/problems`, `/cost-of-power` and `/grid` read it | `docs/reviews/bill-faults-2026-11-16.md`, row 5 | requested |

### (d) Progress (`docs/state/progress_c304.md`)

| 13 | `/learn/bill` | done (the branch's tip) on `wip/7533-learn-bill` (landing row 31). **The note:** `docs/methods/bill.md` completed, session 335's note kept. **The replication:** 669 of 669 figures over 20 cases (the page drawn whole on the live set's rows of `cost_of_power_monthly`, and the calculator for 19 cases, five of them the defaults and two EIA's 2024 average month); on origin/main 652 of 669. **The cross-check:** against EIA EPM Table 5.6.A (August 2026), EIA ESRAP 2024 Tables 5A and 6, and the PG&E and CenterPoint tariffs as posted on 16 November 2026. The Texas defaults equal EIA's average by construction (15.88 against 15.91 cents); PG&E 38.27 against 39.62; SDG&E 55.48 against 43.63 (no baseline credit by default). **The decisions block:** 14 choices. **Faults:** 15 found, 4 fixed (the five cards' 15 figures printed "license needed" since 21 October, here and on a problem set; floating-point kWh in two lines; the SCE summer super off-peak field moved nothing silently; a rider's label), 1 data machine (`cost_of_power_monthly` built 4 October, data request row 69), 10 rulings. Browser reads rows 96 to 101. Not read: Oncor (its robots file did not answer) | 7533 |
