# Should your family get an EV? (`/play/ev`): method

Energy Research Warehouse (ERW), session 294 (Samuel's ruling 17 of 14 October 2026: the EV game, EV only; the solar half is a later game). For a middle-schooler of about 12, to work through and show their parents. Five screens, about five minutes. The arithmetic is `site/lib/ev.ts`; the page `site/app/play/ev/`.

## The prices: real, from the warehouse

| Price | Table | Entity | Which value |
|---|---|---|---|
| Electricity for homes | `eia_retail_electricity_prices` (EIA, Electric Power Monthly) | `eia:retail_price:<state>:RES` | the newest month (July 2026 when built), USD/MWh; shown as cents a kWh (USD/MWh / 10) |
| Regular gasoline | `eia_regional_retail_fuel_prices` (EIA, Gasoline and Diesel Fuel Update) | `eia:EMM_EPMR_PTE_S<state>_DPG` | the newest week (5 October 2026 when built), USD a gallon |

- **Gasoline by state where EIA publishes it, else by region.** EIA's weekly survey publishes nine states (California, Colorado, Florida, Massachusetts, Minnesota, New York, Ohio, Texas, Washington). Every other state takes its PADD region's price: the East Coast by its three sub-regions (New England, PADD 1A; the Central Atlantic, 1B; the Lower Atlantic, 1C), the Midwest (2), the Gulf Coast (3), the Rocky Mountains (4), and the West Coast without California (PADD 5 except California) for Alaska, Arizona, Hawaii, Nevada and Oregon. The card says which, and why.
- **How the game reads them.** The two tables are in the warehouse but not in the live set (`warehouse/supabase/live_set.yaml`: the price board's series are read from the site's own files). So `site/scripts/build-ev-prices.mjs <warehouse/output>` writes `site/data/ev_prices.json`: each state's two newest values with their table, entity and date, and each table's source line. To refresh the game's prices: run it on a machine that holds the tables, and commit the file.

## The defaults: sourced, and the family's to change

| Default | Value | Source |
|---|---|---|
| Miles a year | 15,000 | fueleconomy.gov's fuel cost estimates assume 15,000 miles a year (its 2025 Fuel Economy Guide) |
| The gasoline car | 27 mpg | the 2025 Chevrolet Equinox FWD, combined (fueleconomy.gov web service, vehicle 48061, read 15 October 2026) |
| The EV | 0.31 kWh a mile | the 2025 Chevrolet Equinox EV FWD, 31.24 kWh per 100 miles combined (vehicle 48697) |
| The gasoline car's price | $28,600 | Chevrolet's starting price for the 2025 Equinox LT before destination, as a search read chevrolet.com on 15 October 2026. **To confirm** |
| The EV's price | $33,600 | the 2025 Equinox EV LT1 before destination ($34,995 with GM's $1,395 destination charge), from listings a search read on 15 October 2026. **To confirm** |
| Years kept | 8 | an assumption for the family to change |
| Interest rate | 5 percent a year | a simple rate, labelled; the family changes it |
| Federal tax credit | off | **No federal credit for cars bought after 30 September 2025.** Confirmed on the IRS's page "Credits for new clean vehicles purchased in 2023 or after" (reviewed 13 July 2026): the credit "is not available for vehicles acquired" after that date. When the family switches it on, the amount (default $7,500, the old maximum) is labelled as their assumption |

The same small SUV, gasoline and electric, so the comparison is like for like. The prices are the least certain defaults: the game says "To confirm" beside them and asks the family to type a dealer's price.

## The arithmetic

- Cost to drive 100 miles on gasoline: 100 / mpg x the gasoline price.
- On electricity: 100 x kWh a mile x the power price (USD/MWh / 1,000 = USD/kWh). Charging at home, at the home price.
- A year: each times miles a year / 100. The saving: gasoline less electricity.
- **Payback:** what the EV costs more to buy (less any credit), divided by the yearly saving. "At once" when the EV costs no more; "never" when it saves nothing.
- **Net present value:** each year's saving, for the years kept, divided by (1 + rate) to the power of the year, added up, less what the EV costs more to buy. Above zero, the EV comes out ahead at these prices.

A worked example, the defaults in California (the test, `site/scripts/test-ev.mjs`, works it by hand): 100 miles costs 100 / 27 x $6.227 = $23.06 on gasoline and 100 x 0.31 x $0.3361 = $10.42 on electricity; a year, $3,459 against $1,563, a saving of $1,897; the EV costs $5,000 more, so payback takes 2.6 years; over 8 years at 5 percent the net present value is $7,258.

## What it leaves out, and says so

Insurance, repairs, charging away from home (dearer), a home charger, state incentives, and what the car is worth when sold. It never says "you should": it shows what each choice costs at these prices, and what would change the answer (a gasoline price slider and a power price slider).

## What is stored

Nothing. The page reads its prices when it is built; what the family types stays in the browser (the page carries `data-no-usage`).

## Where each figure says it comes from (session 2402, 23 October 2026)

- **No figure of this page carries a check key**, and that is by design. The two prices are `data/ev_prices.json`, a
  file built from the warehouse's two EIA tables (above), not the live set; and the page shows no price until a state is
  chosen, so the server's page, which `check-values` reads, carries no figure. Every other figure is the game's own
  arithmetic (`site/lib/ev.ts`) on what the family typed.
- **Every figure says its source in words beside it**, not on hover: the page is for a child of about 12 to show their
  parents (session 294's rule for this page). Each price card prints the table, the entity and the month or week; the
  gasoline card says whether it is the state's own series or its region's, and why; every default prints its source and
  "changed by you" when moved; the verdict's sentences say what each figure is; "Show your parents" lists every number
  with where it comes from, and the credit line cites the IRS's page.
- **At 390 px** (session 2403): the five screens draw inside the window; nothing is wider than the page and no control
  is without its name. The review of every game figure is `docs/reviews/games-figures-2026-10-23.md`.

## One screen, sources on hover (sessions 3275 to 3278, 6 November 2026)

The owner's ruling of 14 October 2026, as chain 198 read it (`queue/done/198-day-6-november-portable-evgame.md`):
one page under Games, the household's inputs on the left and the results on the right, the verdict as payback years and
net present value with the upfront cost included, the federal credit off by default behind a toggle, and every
default's source as a hover tip, never as visible grey text. This replaces the five screens of session 294 and the
"words beside it" rule of session 2402 for this page. The address stays `/play/ev`, the one the Games menu uses.

### The tables the game reads (session 3275's survey)

| Table | Held where | Key the game uses | Grain |
|---|---|---|---|
| `eia_retail_electricity_prices` | the warehouse (`coverage.csv`: 372 entities, monthly, 2001-01 to 2026-08, 114,574 rows); not in the live set | entity `eia:retail_price:<ST>:RES` (and `:US:RES`), variable the average price, USD/MWh | P1M |
| `eia_regional_retail_fuel_prices` | the warehouse (`coverage.csv`: 29 entities, weekly, 2019-01-07 to 2026-11-02, 16,359 rows); in `live_set.yaml` under session 132's list, but nothing reads it from Supabase | entity `eia:EMM_EPMR_PTE_S<ST>_DPG` (nine states), `..._R<PADD>_DPG` (regions), `..._NUS_DPG` (US) | P1W |
| `eia_retail_fuel_prices` | the warehouse (3 entities, weekly from 1990); not used: it holds only US series | | P1W |

The page reads neither table from Supabase: `site/scripts/build-ev-prices.mjs` writes `site/data/ev_prices.json` from
the two tables on a machine that holds them, and the page reads the file when it is built. The file in the repository
was built on 15 October 2026 (electricity July 2026, gasoline the week of 5 October 2026). The code laptop holds neither
table, so chain 198 did not rebuild it: a refresh is a data machine's run of the script.

### The model

- **Fuel a year, gasoline:** miles a year / mpg x the gasoline price.
- **Fuel a year, electricity:** miles a year x kWh a mile x the price per kWh, where the price per kWh is the home
  price for the home share of charging and the price the family types for a public charger for the rest:
  `home share x home price + (1 - home share) x public price`.
- **The upfront cost:** each car's price; the EV's less the federal credit when the toggle is on.
- **Cumulative cost by year** (the chart): price at year 0, then price plus that many years of fuel. Not discounted, so
  the year the two lines cross is the payback year.
- **Payback, in years:** what the EV costs more to buy (after any credit), divided by the yearly saving on fuel. "At
  once" when the EV costs no more; "never" when it saves nothing a year.
- **Net present value over the years kept:** each year's saving divided by (1 + rate) to the power of the year, added
  up, less what the EV costs more to buy. Above zero, the EV comes out ahead at these prices.
- **Left out, and the page says so in a hover:** maintenance and repairs, insurance, a home charger, state and utility
  incentives, registration fees, what each car is worth when sold, and any change in prices over the years (today's
  prices are held for every year).

### Every input, its default and its source

| Input | Default | Source (shown on hover) |
|---|---|---|
| State | the United States as a whole | so the page shows a full result before a state is chosen; the US rows of the two tables |
| Electricity price | the state's newest month | `eia_retail_electricity_prices`, entity `eia:retail_price:<ST>:RES` |
| Gasoline price | the state's newest week, else its region's | `eia_regional_retail_fuel_prices`, the entity named on hover |
| Miles a year | 15,000 | fueleconomy.gov's fuel cost estimates assume 15,000 miles (its 2025 Fuel Economy Guide) |
| Gasoline car's mpg | 27 | 2025 Chevrolet Equinox FWD, combined (fueleconomy.gov vehicle 48061) |
| EV's kWh a mile | 0.31 | 2025 Chevrolet Equinox EV FWD, 31.24 kWh per 100 miles combined (vehicle 48697) |
| Gasoline car's price | $28,600 | Chevrolet's starting price for the 2025 Equinox LT, before destination (read 15 October 2026) |
| EV's price | $33,600 | the 2025 Equinox EV LT1 before destination (read 15 October 2026) |
| Home charging share | 100 percent | an assumption: every mile charged at home, at the home price |
| Public charger price | none: the family types it | no table in the warehouse holds what public chargers charge, so the game invents none. Below 100 percent at home, the result waits for this price |
| Years kept | 8 | an assumption for the family to change |
| Discount rate | 5 percent | a round rate the game chooses. OMB's rates for 2026 are lower: nominal 3.6 percent (7-year Treasury) and 3.7 (10-year), real 1.4 and 1.6 (Circular A-94, Appendix C, revised 6 March 2026, read 6 November 2026). For Samuel's ruling |
| Federal tax credit | off; $7,500 when switched on | the IRS: no credit for new clean vehicles acquired after 30 September 2025; $7,500 was its most. On, it is the family's assumption |

### The figures keyed for check-values

The page opens on the United States at the defaults, so the server's page carries the figures and
`scripts/check-values.mjs` can read them. Keys (`ev|<state>|<figure>`), each recomputed by check-values from
`data/ev_prices.json` and `lib/ev.ts` at the defaults: `power_cents` (the home price in cents a kWh, two decimals),
`gas` (USD a gallon, as held), `payback` (years, one decimal) and `npv` (USD, whole). A state chosen in the browser is the
family's own reading and is not keyed.
