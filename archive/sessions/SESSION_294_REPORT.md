# Session 294 report: the EV game

15 October 2026, unattended, on samueloldlaptop (the code machine), the last session of the afternoon chain. Branch `wip/games-v2`, pushed, **not landed**. Model spend USD 0. No warehouse data written. Requests outside the ERW: the IRS's page (one read) and fueleconomy.gov's public web service (five requests: two menus, two vehicles, its robots file, which did not answer), and three web searches for the cars' prices.

## Read these first

- **"Should your family get an EV?" is at `/play/ev`** (ruling 17), fifth in the Games menu as ruled (14). Five screens: where you live, your car, the money, the verdict, show your parents. EV only; no solar.
- **Every price is a table's.** Each state's home electricity (`eia_retail_electricity_prices`, July 2026) and regular gasoline (`eia_regional_retail_fuel_prices`, the week of 5 October 2026). Nine states have their own gasoline series; the other 42 take their region's, and the card says "EIA does not publish a weekly price for New Jersey, so this is its region's". All 67 prices in the game's file equal their table rows.
- **The federal credit: confirmed on the IRS site**, so the game says "No federal credit for cars bought after 30 September 2025" (irs.gov, "Credits for new clean vehicles purchased in 2023 or after", reviewed 13 July 2026: "not available for vehicles acquired" after that date). The toggle is off; switched on, the amount is labelled the family's assumption.
- **The car prices are the weakest defaults, and say "To confirm":** $28,600 (2025 Equinox LT) and $33,600 (2025 Equinox EV LT1), before destination, read through search results of Chevrolet's own page and car listings, not from a page fetched in full.
- **The worked example, by hand and on the page:** California at the defaults: 100 miles costs $23.06 on gasoline and $10.42 on electricity; $1,897 saved a year; payback 2.6 years; NPV $7,258 over 8 years at 5 percent.

## What to review

Screenshots: https://github.com/SamuelEnrique/erw/tree/wip/games-v2/docs/reviews/games-2026-10-14/294 (before: the address did not exist; after: 16).

1. `after/02-where-california-1280.png`, `after/03-where-new-jersey-region-390.png` (a state priced by its region, said).
2. `after/04-your-car-1280.png`, `after/05-the-money-1280.png` (the credit off, with the IRS's line).
3. `after/06-verdict-390.png`, `after/07-verdict-gasoline-changed-1280.png` (what would change the answer).
4. `after/08-show-your-parents-1280.png` (every number, its table or "changed by you", and "Print for my parents").

Locally: `C:\Users\lossa\Documents\erw-279\site`, `npx next start -p 3289`, unlock at http://localhost:3289/internal/unlock?token=<INTERNAL_COSTS_TOKEN>, then http://localhost:3289/play/ev .

## What was done

- `site/scripts/build-ev-prices.mjs` reads the two tables from `warehouse/output/` (they are not in the live set) and writes `site/data/ev_prices.json`: each state's newest power and gasoline price with table, entity and date, the region where the state has no series, and each table's source line.
- `site/lib/ev.ts`: the defaults, each with its source; cost per 100 miles, a year, the saving, payback (or "at once", or "never") and NPV.
- `site/app/play/ev/`: the page (inside `<Brand noUsage>`: nothing typed is sent or counted) and the five screens (`EvGame.tsx`): a progress bar, sliders with their default and source in grey and a reset named for each, the two bars (gasoline in ink, the EV in cardinal), payback and NPV each with one line on what it means, the rate slider (5 percent, labelled), the gasoline and power sliders ("changed by you"), and the parents' table with a print button.
- `docs/methods/ev_game.md`; the menu (`site/lib/pages.ts`), `docs/tools.md` (its inventory test), `check-routes.mjs`.
- Tests: `site/scripts/test-ev.mjs` (the hand-computed example and the edges, 14 checks) and `tests/test_session294.py` (11); the menu tests of sessions 203, 237, 239 and 288 follow the fifth entry.
- Found by the screenshots and fixed: the parents' table was 410 px wide at 390; the sliders drew in the browser's blue.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `build-ev-prices.mjs` | 0 | 51 states, 9 with their own gasoline |
| The 67 prices against `warehouse/output` | | 0 differ |
| `node scripts/test-ev.mjs` | 0 | 14 of 14 |
| `tsc`, `eslint` | 0, 0 | |
| `test_session294` and the menu tests | 0 | 93 (one skipped in the worktree, which has no warehouse files: the same comparison was run against the main copy's, above) |
| `npm run build` (worktree) | 0 | `/play/ev` static |
| `check-values.mjs`, Games pages | 0 | 105 of 105 (the EV game's prices come from a file, not the live set: checked by the comparison above) |
| `check-tour.mjs` | 0 | 47 of 47 |
| Screenshots after | 0 | 16, no sideways overflow |
| The whole suite, clean copy of the branch | see the chain's note below | |

## Decisions made without you

- **Defaults: one car, two power trains.** fueleconomy.gov's 2025 Chevrolet Equinox FWD (27 mpg) and Equinox EV FWD (31.24 kWh per 100 miles), so a child compares like with like; 15,000 miles a year is fueleconomy.gov's own assumption.
- **The prices are read from a file built from the warehouse**, as the price board's are: the tables are kept out of the live set.
- **fueleconomy.gov's robots file did not answer**; its web service is published for this use, and five requests were made, with the ruled contact string. Listed above.
- **Years kept, 8, and the rate, 5 percent**, are labelled assumptions.
- **Charging is at the home price**; away-from-home charging is named as left out.

## For Samuel's ruling

- The car prices: keep Chevrolet's starting prices (to confirm), or set them from a national average transaction price (Kelley Blue Book's, a licensed source).
- Whether the game should offer a few cars by name (fueleconomy.gov holds them all) instead of the one pair.

## Files

- New: `site/app/play/ev/page.tsx`, `EvGame.tsx`, `site/lib/ev.ts`, `site/data/ev_prices.json`, `site/scripts/build-ev-prices.mjs`, `site/scripts/test-ev.mjs`, `docs/methods/ev_game.md`, `tests/test_session294.py`, `docs/reviews/games-2026-10-14/294/`, this report.
- Changed: `site/lib/pages.ts`, `site/scripts/check-routes.mjs`, `docs/tools.md`, `tests/test_session{203,237,239,288}.py`.
