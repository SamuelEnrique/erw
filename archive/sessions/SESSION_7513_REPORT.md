# Session 7513 report: What a battery saves a customer, read as the reader it is for (chain 304, part B)

16 November 2026, samueloldlaptop (code role), unattended. Worktree `erw-7504`, branch `wip/7504-battery-customer`, stacked on session 7504's commits, not pushed. Model spend: USD 0. Tool: `/battery/customer` (in review). The read: `docs/reviews/battery-customer-read-2026-11-16.md`.

## At the top

- **No figure of the arithmetic changed.** `saving` is as it was; the page's 331 figures are as committed.
- **Three things a real case met on the page, fixed with a test:** a rate typed as its sheet prints it, in cents, was refused with a range and no reason; the field "How long your peak lasts" did not say whose hours, on a rate that calls three spans peak; the decisions block said no customer's battery figure was read while the home battery game cites one.
- **The field that moves the answer most is the one no bill prints.** For one real store and one battery, the demand saving is USD 1,658, USD 829 or USD 553 a month at 2, 4 and 6 hours typed (the store's own 2013 rate); on Seattle City Light's rate USD 295, USD 147 or USD 33 at 2, 4 and 18.
- **No file of another page was edited.** `/learn/bill` and `/play/battery` (the portable laptop's) and `/cost-of-power/battery` were read, not changed. Rows 7 and 8 are for their own reads.
- **Not run:** no site build, no browser, `check-no-request.mjs` (it needs a served build). The promise that nothing typed is sent or stored is held by the code tests only: no request, no storage write and no address parameter was added. Part A's browser row 1 still stands for the landing machine.
- **No web request was made.** Every rate and every fact of the store came from a file session 7504 had read (`runs/7504/dl/`, ignored).
- **Part A's rows were not reopened** and its faults file is untouched.

## The reader and the five cases

- **The reader:** the energy manager of a grocery chain, with an installer's quote in hand. Why: the page takes twelve months alike, one discharge a day and a peak inside the peak-rate hours; a store's refrigeration runs every day of every month and into the evening; and the one commercial building with a published size, peak and battery in the documents read is a grocery store.
- **The store, in every case:** 27,625 square feet, a peak of about 247 kW in 2012 (EnerNOC facility 384, Los Angeles; NREL/TP-6A20-64987, page 7). The batteries: 55 kW and 110 kWh (that report's table 9) and 100 kW and 400 kWh (a 4 hour commercial unit). The store on another city's rate is the case, not data.
  1. Seattle City Light, medium, time of use, City of Seattle (rates as read 16 November 2026): USD 3,519 a year for the small battery, USD 12,795 for the unit.
  2. The same, Downtown Network (USD 12.19 per kW): USD 5,977 and USD 21,733. The rate does not change which battery saves more for each kWh.
  3. Salt River Project E-32 (November 2025 billing cycle): the page reads USD 13,376, USD 8,917 or USD 7,164 by the season typed; the year by the plan's seasons, USD 8,784, is never printed.
  4. Austin Energy, 10 kW to under 300 kW (bills from 1 October 2026): USD 9,824 a year, all of it from the peak; the energy is a cost of USD 26 a month.
  5. The store's own rate in NREL's work (Southern California Edison TOU-GS-2 Option B, about April 2013): typed as printed, in cents, nothing; in dollars USD 1,840 a month. The published figure for this store is a net present value with solar in it, so the two cannot be set side by side.

## The rows by kind (10)

- **Site, fixed: 3.** Row 1 (a rate in cents), row 2 (whose hours), row 3 (the round trip on three pages).
- **Rulings: 6.** Row 4 (a rate under 5 typed in cents is taken as dollars), row 5 (Salt River Project's 5 kW allowance and "the demand charge was"), row 6 (a peak outside the peak-rate hours: USD 522 or USD 1,897 a year less), row 7 (`/learn/bill` has no demand charge), row 8 (What a battery earns does not point here), row 9 ("Round trip" against "Round-trip efficiency").
- **Browser: 1.** Row 10.
- **Data machine: 0.** The tool reads no table. **License, key: 0.**
- **Part A's three rulings on the five cases, in dollars a year** (the table is in the read):
  - Twelve of the month typed: USD 0 at Seattle and Austin; USD 4,593 over (twelve Julys) at Salt River Project; USD 8,175 over (twelve summer months) on the 2013 sheet.
  - Energy not capped by the store's use: USD 0 while the store draws 27.5 to 100 kW on average in the peak-rate hours (11 to 40 percent of its peak); USD 64 to USD 71 a year for each kW short at Seattle.
  - The demand saving as an upper bound, at NREL's 85 percent: USD 265 to USD 2,984 a year less by case (USD 965 and USD 2,194 for the 4 hour unit at Seattle).

## What was fixed

- `site/lib/customerbattery.ts`: `inDollars` (a refused rate per kWh is told "The rate is typed in dollars: 12 cents is 0.12." after its range); the off-peak field's line ends "in dollars"; the line under "How long your peak lasts" reads "How long your own demand stays near its highest, in the hours your demand charge counts. The battery must hold its discharge this long to lower the peak."
- `site/app/battery/customer/Calc.tsx`: the refusal line uses it. Imports are as they were (React and the arithmetic).
- `site/app/battery/customer/Decisions.tsx`: two sources say more (the 18 hours Seattle City Light's peak demand charge counts; 86 here and on What a battery earns, 90 in the home battery game, and what was not read).
- `docs/methods/battery_customer.md`: the two cells of its choices table, a tests line, and section 12 on this read.

## Tests

Each file in its own process, one at a time, `ERW_SPEND_CAP_USD=0`, output under `runs/7513/`.

| File | Count | Result |
|---|---|---|
| `site/scripts/test-battery-customer-read.mjs` (new) | 29 checks | 29 of 29 |
| `tests/test_session7513_battery_customer_read.py` (new) | 8 | pass |
| `site/scripts/test-battery-customer-page.mjs` | 31 checks | 31 of 31 |
| `site/scripts/battery-customer-figures.mjs --check` | 331 figures | as committed |
| `tests/test_session7504_battery_customer.py` | 16 | pass |
| `tests/test_session88.py` | 11 | pass, 1 skipped by its own rule (no served build) |
| `test_session203`, `241a`, `242`, `5162` (they name the page) | 15, 17, 12, 9 | pass |
| `test_session142`, `147`, `158`, `160`, `301` (they sweep the method notes) | 42, 65, 58, 40, 9 | pass |
| `test_session149`, `1502`, `177`, `182_flow`, `196`, `215`, `371`, `473`, `5155`, `5163`, `5169`, `462`, `465` (they sweep the site's files) | 39, 4, 28, 19, 9, 12, 10, 7, 10, 6, 9, 8, 10 | pass (one skipped by its own rule in `149`, `1502` and `465`) |

- A narrow type check (`tsc --noEmit` on `page.tsx`, `Calc.tsx`, `Decisions.tsx`, `lib/customerbattery.ts` and what they import, the site's settings less Next's plugin): exit 0, no message. Not a build.
- Not run: `check-no-request.mjs`, `check-routes.mjs` (a served build and a browser), `test_session161` (part A found it failing on the `/ask` tool's fixture; it names no file changed here).
- One test of part A failed on the first form of the fix (it holds `range(f)` in `Calc.tsx`); the fix was reshaped to keep it, and the test passes unchanged.

## What to review

`https://erw-flame.vercel.app/battery/customer` (in review: open it with the review cookie), once this branch has landed.

1. As it opens, the line under "How long your peak lasts": "How long your own demand stays near its highest, in the hours your demand charge counts. The battery must hold its discharge this long to lower the peak." The line under "Energy rate, off-peak hours" ends "in dollars."
2. Type: peak 247; demand charge 30.14; peak rate 14.66; off-peak rate 5.82. Under each rate: "Not a number this page can use (0 to 5). The rate is typed in dollars: 12 cents is 0.12." and "2 of 9 still needed" once the battery is typed (55 and 110).
3. Change the rates to 0.1466 and 0.0582: "lowers the bill by $1,840 a month, $22,080 a year"; "At $30.14 per kW that is $1,658 a month." Change the hours to 4: "$829 a month". To 6: "$553 a month".
4. Type: 247; 5.36; 0.1218; 0.0609; 55; 110; hours 4; days 26: "$293 a month, $3,519 a year". Hours 18: "6.1 kW off a 247 kW peak", "$33 a month".
5. Open "Decisions on this page". The first line's tip ends "The hours to type are those your own demand stays near its highest inside them." The round trip's tip: "the same 86 percent as on What a battery earns. The home battery game of this site starts at 90 percent".
6. The network panel while typing: no request.

`https://erw-flame.vercel.app/data/methods/battery_customer`: section 12, "The tool read as its reader".

## Data request rows

None. The tool reads no table and no file a builder writes.

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 | 7513 | wip/7504-battery-customer | /battery/customer | Type 14.66 in "Energy rate, peak hours" and 5.82 in "Energy rate, off-peak hours", at 1280 px and at 390 px; the network panel | Under each: "Not a number this page can use (0 to 5). The rate is typed in dollars: 12 cents is 0.12.", wrapped inside the field column, no sideways scroll; no request | wanted |
| 2026-11-16 | 7513 | wip/7504-battery-customer | /battery/customer | The line under "How long your peak lasts" as the page opens, at 1280 px and at 390 px; then type 247, 5.36, 0.1218, 0.0609, 55, 110, hours 4, days 26, and change the hours to 18 | The two new sentences wrapped inside the column; "$293 a month, $3,519 a year"; at 18 hours "6.1 kW off a 247 kW peak" and "$33 a month" | wanted |
| 2026-11-16 | 7513 | wip/7504-battery-customer | /battery/customer | "Decisions on this page": hover and tap the "i" of the first line and of the round trip's line, at 390 px | Each tip, now longer, stays inside the screen; the round trip's names 86 percent, 90 percent and "88 to 91 percent" | wanted |

## Landing request

- **Head:** the commit that holds this report on `wip/7504-battery-customer` (its hash is in the reply to the orchestrator). It lands with session 7504's stack on the same branch, on `wip/7500-done-line`.
- **Tests:** the table above; `site/scripts/test-battery-customer-read.mjs` (29 of 29), `tests/test_session7513_battery_customer_read.py` (8).
- **What changes:** on `/battery/customer`, the line under two fields, the line under a refused rate, and two tips of the decisions fold. New: the read, its two tests, section 12 of the method note.
- **What does not:** the arithmetic, the nine fields and their limits, the 331 figures, the promise and its browser proof, `release.ts`, every table, every other page.
- **Snapshot:** no difference expected on the 25 addresses read as a visitor (every page is in review). With the review cookie: `/battery/customer` differs by those lines; `/data/methods/battery_customer` gains a section.
- **Before landing:** part A's build and `check-no-request.mjs` on the landing machine cover this change as well.

## Needs the key

- Nothing. No step of this tool needs a model.

## Decisions made without you

- The reader is a grocery chain's energy manager, and every case uses the one store NREL's report describes. No building's peak was invented: 247 kW is the report's figure; the 2,000 kW and 1,000 kW customers of part A's cases were not used.
- The line under "How long your peak lasts" was reworded. It is an existing line of the page, not a new grey note, and its old sentence is kept whole as the second sentence. It is the row that moves the answer most, so it was changed and not left for a ruling (ruling 7 below puts it back if wanted).
- No new tariff was read and no web request made. The 2013 sheet's winter rates and its cents are from NREL/TP-5400-63162, table 1, a file part A had downloaded.
- `site/lib/pages.ts`, `/cost-of-power/battery`, `/learn/bill` and `/play/battery` were not edited (rows 7 and 8).
- The field's name "Round trip" was left (row 9): it is in the page's words, part A's script and the browser proof.
- The method note was extended (two cells, one line, one section), not rewritten. Part A's faults file was not touched.
- The scratch script (`site/scripts/_bc_read.mjs`, 19 draws) is ignored by git and stays in the worktree.

## For Samuel's ruling

1. **A rate typed in cents under 5.** The energy-rate fields take up to USD 5 per kWh, so 4.9 typed for 4.9 cents is taken as USD 4.90 and the page prints USD 70,169 a year without a word. Default taken: unchanged. The other way: a limit of USD 1 per kWh (the highest rate of the nine cases is USD 0.1924).
2. **"The demand charge was" on a plan with an allowance.** Salt River Project charges all kW over 5 kW, so the store's bill prints USD 1,633.50 where the page prints USD 1,667. Default taken: left.
3. **The rate of the hours of the peak.** When the store's highest demand is outside the peak-rate hours, the discharge that lowers the peak is paid at another rate (USD 522 to USD 1,897 a year less at Seattle). The fold says the assumption; the field does not. Default taken: left. The other way: one clause under "Energy rate, peak hours".
4. **`/learn/bill` as this page's related page.** It builds five home bills and has no demand charge, nor the term. Default taken: left; it is the portable laptop's tool.
5. **A way from What a battery earns to this page.** That page's related links do not include it. Default taken: left for that page's own read.
6. **One name for the round trip.** "Round trip" here, "Round-trip efficiency" on the other two pages. Default taken: left.
7. **The reworded line under "How long your peak lasts".** Default taken: the new words. The other way: the old line alone, and the meaning said only in the decisions fold.
