# Session 352 report: price years on the three economics pages

20 October 2026, from about 12:50 UTC, unattended, on samueloldlaptop (the code machine), the second session of the chain of 20 October, night (`queue/done/010-night-20-october-code.md`). Branch `wip/352-price-years` in the worktree `erw-296`, from main with session 351 (`a7abbcc7`); lands on main as `task/352-price-years`. Model spend USD 0; no warehouse data written; nothing pulled.

## Read these first

- **"Price years"** on `/cost-of-power/battery`, `/cost-of-power/seller` and `/cost-of-power`, read from the data machine's `price_years_by_window` (session 357), in the live set and readable as a visitor. The choice is in the box: the battery's under its Units, the generator's under "Your plant", the datacenter's under "Your load". The windows are the table's, for the page's own price point and configuration: the last twelve months (the default), each calendar year held, the averages of the last three and seven full years, every month held, and (on the battery) every month held with a stress event taken out. A year held in part says so ("2026, 9 months held (their sum, not a full year)").
- **The default writes nothing**: the last twelve months are the page's own figure, not a row of the table, and `py` is written into the address only away from the default. No default figure moved (check-values 1,313 of 1,313 on every `/cost-of-power` page; the three scenario checks and the two face checks as before).
- **What follows the window**: scenario A and B, the results table and the sensitivity; the headline says which window prices it ("Priced in 2021, a 100 MW, 4-hour battery in ERCOT earns USD 3,430.56 per kW a year"). The battery's figure under a window is the table's at the model's own efficiency and cycles; at another step the revenue row says "not held". The generator's energy under a window is the page's own months inside it (the contract rows read it). The datacenter's flat way reads `flat_<market>`, its second way the flexible run shown at the run's default (a run away from its default holds none), and scenario B at its own site reads that site's own rows.
- **A line under the results** gives the same project's highest and lowest whole calendar year held, each figure with its key (the battery's with scenario A's NPV in each): "earned USD 3,430.56 per kW in 2021 (scenario A's NPV USD 2.08 billion) in its highest whole year held and USD 87.44 per kW in 2025 (scenario A's NPV USD -65.9 million) in its lowest". The battery page's rule against words that judge (tests 179, 195, 297) forbids "best" and "worst", so the words are "highest" and "lowest", and the datacenter's "cheapest" and "dearest".
- **Pack section 6, item 1** of each tool rewritten to say what the page now shows (`docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md` item 2).

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first), after the landing:

1. https://erw-flame.vercel.app/cost-of-power/battery?py=year_2021 (and the choice in the box under Units).
2. https://erw-flame.vercel.app/cost-of-power/seller?py=avg_3y
3. https://erw-flame.vercel.app/cost-of-power?py=year_2021
4. `docs/brand/review-352/`: each page before and after at its default (the same), and one window each.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session352` and every test that reads a file this session changed (56 modules, 905 tests) | 1, then 0 | seven failures, each the session's own: the words "best" and "worst" (179, 195, 297: renamed); four pins of lines this session changed (236, 264, 268, 296: updated, each with a comment); then 124 of the seven modules and 352 OK |
| `tsc --noEmit`; the three forms' tests (16 modules, 301 tests) | 0 | |
| `finish_build.sh 352`, first build (`f1d33102`) | 0 | check-values **26 failed**: the high and low line wrote "USD " inside its Num, so the shown text did not read as the number. Fixed (`6b640c07`) |
| `finish_build.sh 352`, second build (`6b640c07`): build | 0 | no statement timeout |
| `check-values` on `/cost-of-power` (every economics page and its grids) | 0 | 1,313 of 1,313 |
| `check-routes` | 0 | every page |
| `check-seller-scenarios`, `check-datacenter-scenarios` (119), `check-battery-face`, `check-datacenter-face` (23) | 0 | all passed |
| `check-battery-scenarios` | 1 | **one failure, production's too**: "CAISO, 2 hours: the block opens at that duration's defaults, steps held". Run against production at 13:31 UTC: the same one failure, the same text. Not this session's; for the next session on the battery |
| `check-table-downloads` | 1 | asked of pages that carry no downloads line (the economics pages have their own CSV links): a mistake of the call, not a result |
| Impeccable `detect --json` on the ten files | 0 | no finding |
| The probe at 390 | 0 | 390 within 390 |
| Shots, 1280 and 390 | 0 | eighteen, `docs/brand/review-352/` |

## Landing of session 351 (recorded here)

- Pushed `task/351-answers` at 12:55:23 UTC (before snapshot `s351-before` at 12:55:12). Run 39426081280 succeeded and merged `bb7ec816` at 13:06. No new style sheet in ten minutes, so the after snapshot `s351-after` was taken at 13:17:24; the comparison: **0 differences on 25 pages**, expected. Production's `/terms` carries "Questions sent from Research" (read through the internal door at 13:19). `wip/351-answers` deleted; the workflow had deleted `task/351-answers`.

## Landing

Below, once it is done: no landing from 14:00 to 16:15 UTC.

## Decisions made without you

- **The default is the page's own last twelve months, not the table's `last_12` row.** They are built from the same tables and agree (the battery's 81.40 is both), but the page keeps reading its own, so the bare address cannot move if the two ever differ. The table's `last_12` row is offered as the default's label.
- **Under a window, what the table does not hold is said, not computed.** The battery's efficiency and cycle steps hold no window figure ("not held"); the "bad month" rows stay the last 36 months (said in the row); the generator's and the datacenter's other figures above the scenarios stay on the last twelve months (one sentence says so).
- **The windows with a stress event taken out are offered on the battery only.** On the generator and the datacenter they hold the revenue or the price and not the energy their rows read.
- **"Show" keeps the price years** on the three forms (one line each); a change of grid or asset still opens that case's default.

## For Samuel's ruling

- Nothing that would change a number at the default.
- `check-battery-scenarios`' CAISO 2-hour case fails on production since before this session: whether the check or the page is wrong is for the next session on the battery.

## Files

- `site/lib/priceyears.ts`, `site/lib/priceyearsread.ts`, `site/components/tool/PriceYearsChoice.tsx`, `site/components/tool/PriceYearsNav.tsx` (new).
- `site/lib/battery/view.ts`; `site/app/cost-of-power/battery/page.tsx`, `Scenarios.tsx`, `Settings.tsx`, `BatteryForm.tsx`; `site/app/cost-of-power/seller/model.ts`, `page.tsx`, `SellerForm.tsx`; `site/app/cost-of-power/model.ts`, `page.tsx`, `LoadForm.tsx`.
- `docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md`.
- `tests/test_session352.py` (new); `tests/test_session236.py`, `264`, `268`, `296` (pins).
- `docs/brand/review-352/` (shots).
