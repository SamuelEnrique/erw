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

(filled in below)

## Rows for the coordinator

(filled in below)
