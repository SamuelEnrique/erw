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

## The game at the done line (session 7536, chain 304, 16 November 2026)

### Which section of this note holds

This note has grown by sessions and keeps every section. Where two disagree, the later holds: the five screens of
session 294 and the "words beside it" rule of session 2402 were replaced by the one screen of sessions 3275 to 3278
(above, "One screen, sources on hover"), and session 2402's line that no figure carries a check key was replaced by
"The figures keyed for check-values" (above). One correction to that section: a state chosen in the browser at the
defaults draws the same four keys under its own code (`ev|KY|payback`); `check-values` never sees them, because it reads
the server's page, which is always the United States.

### Every view and every figure, as a player meets them

One screen. On the left, "Your family": the state menu; the electricity and gasoline sliders, each with the state's
price as its default; the sliders for miles, mpg, kWh a mile, the two cars' prices and the share charged at home; the
public charger's price box (shown only below 100 percent at home); the years and the rate; the credit switch with its
amount (shown only when on); "Reset everything". Each slider shows its value in grey while it is the default and in ink,
with "changed by you" and a reset named for it, once moved; its tip says the default and its source. On the right:

| Figure | Rule (the note's "The model") | Shown as |
|---|---|---|
| Payback | extra to buy / a year's saving; "at once" when extra <= 0; "never" when the saving <= 0 | years, one decimal |
| Payback's tip | what the EV costs more to buy, after the credit when it is on | whole dollars |
| Net present value, N years | sum over t = 1..N of saving / (1 + rate)^t, less the extra | whole dollars, a minus before the dollar below zero |
| Net present value's tip | the rate | percent, one decimal |
| Net present value's tip (session 7550) | the yearly saving the value is computed from: gasoline less electricity | dollars and cents |
| A year of gasoline | miles / mpg x gasoline price | whole dollars |
| A year of electricity | miles x kWh a mile x the price a kWh (home share at the home price, the rest at the typed public price) | whole dollars |
| Saved a year with the EV, or Extra a year with the EV | gasoline less electricity; the name turns to "Extra" below zero and the amount is shown without its sign | whole dollars |
| The chart's summary (its spoken label) | each car at year 0 (its price, the EV's less the credit) and at year N (plus N years of fuel), and the crossing | whole dollars; the crossing to one decimal |
| "they cross at X years" | the payback, drawn only when 0 < payback <= the years kept | years, one decimal |
| The chart's hover | each car at the year pointed at | whole dollars (not drawn without a pointer: a browser read) |
| "Every number, for your parents" | every input's value with its source, or "changed by you"; the credit; the day the prices were built | as the sliders |
| In place of the results | when some charging is away from home and no valid public price is typed: "Type a public charger's price on the left to see the results."; when the state has no held price (none today): that the warehouse holds no price for it | words |

### The chart's axes

The money axis runs from $0 to the first step at or above the dearest point of either line, in steps of $5k, or $10k
when the dearest point is above $40,000, or $20k above $100,000. The year axis labels every year from 0 to the years
kept, and every second year (the even ones) when more than 10 years are kept.

### The choices that move a figure

The page's fold "Decisions in this game" (`site/app/play/ev/Decisions.tsx`, session 7536) lists eleven, each with its
default and its source on hover: `home-price` (the state's residential average, every utility and hour, not an EV
rate), `gasoline-price` (regular, the state's weekly series or its PADD region's), `prices-held` (both prices flat for
every year), `home-share` (100 percent at home; a public price only as typed), `miles` (15,000), `cars` (the 2025
Equinox pair at 27 mpg and 0.31 kWh a mile, wall to wheels), `car-prices` (before destination, $28,600 and $33,600),
`payback` (undiscounted), `npv` (5 percent, end of each year, 8 years), `credit` (off; $7,500 when on), and `left-out`
(repairs, insurance, a charger, incentives, fees and resale). Every one a player can change is changed in place, in the
slider the line names.

### What the game does not hold

No public charging price (the player types one), no time-of-use or EV rate of any utility, no price for a state's
own gasoline outside EIA's nine states, no forecast of either price, no model year after 2025, no state or utility
incentive, no used car, no lease, and nothing about the player: what is typed stays in the browser.

### The replication

`replication/ev_game/replicate.py`, written from this note and the two tables, not from the page's code. The game is
drawn to HTML with the site's own code (`site/scripts/ev-game-figures.mjs`) as it opens, for each of the 51 states at
the defaults, and for eleven players' cases (`replication/ev_game/cases.json`: the hand-worked Texas and Ohio
households, an EV that never pays back, 15 years at 0 percent, 2 years with no crossing, the two waiting cases, a
$3,000 credit, Hawaii at 30,000 miles and 10 percent, New York with both prices moved, and an $80,000 EV). On
16 November 2026: **5,141 of 5,141 figures** inside half the page's last shown digit over 63 cases; the prices of
`site/data/ev_prices.json` against the tables' rows, 104 checked, **102 equal and 2 named** (EIA revised New York's July
2026 residential price from 299.0 to 298.9 USD/MWh and Pennsylvania's from 217.2 to 217.1 after the file was built). It
also names that the file is older than the tables: electricity July 2026 where the table holds August, gasoline the week
of October 5 where the table holds November 2. `replicate.do` rebuilds the five headline figures of the opening page
(a year of gasoline 2,418.89, of electricity 851.41, saved 1,567.47, payback 3.19 years, net present value 5,130.92).

### The cross-check (read 16 November 2026; robots files read first)

| Figure | Ours | Theirs (publisher, document, date) | Difference | Why |
|---|---|---|---|---|
| US regular gasoline, week of October 5, 2026 | $4.354 | $4.354: EIA, Weekly U.S. Regular All Formulations Retail Gasoline Prices, series EMM_EPMR_PTE_NUS_DPG | 0 | the same survey |
| US regular gasoline, newest | $4.354 (October 5) | $3.995 (November 9): the same EIA series | +$0.359 | the game's file was built 15 October and not since (fault 5) |
| US regular gasoline, 1 to 15 July 2026 | $3.816 (the table's weeks of July 6 and 13) | $3.84: DOE Alternative Fuels Data Center, Alternative Fuel Price Report, July 2026 | -$0.024 | AFDC's own survey of stations over the fortnight, not EIA's Monday survey |
| Residential electricity, August 2026, 13 places | the table: US 18.16, CA 29.75, TX 15.91, OH 19.38, NY 28.65, MA 30.48, HI 47.18, FL 14.99, WA 14.63, AL 16.33, LA 12.87, ND 13.31, CT 24.51 cents | the same, each: EIA, Electric Power Monthly, Table 5.6.A (released October 23, 2026) | 0.00 each | the table is EIA's; the game still shows July (fault 5) |
| California's home price | 33.61 cents (July 2026); a year of charging $1,563 at the defaults | PG&E E-TOU-C off-peak total rates, 36.757 cents winter and 39.940 summer, as read 30 September 2026 (`site/data/bill_rules.json`): $1,709 and $1,857 | -3.15 and -6.33 cents | the state's average spreads every utility, hour and baseline credit; PG&E is the dearest of the three large utilities and its rates are before the baseline credit of 8.14 cents |
| The federal credit | off; $7,500 when switched on | the IRS, Credits for new clean vehicles purchased in 2023 or after (Page Last Reviewed or Updated: 13-Jul-2026): "not available for vehicles acquired after Sept. 30, 2025"; "up to $7,500" | none | |

Not read: fueleconomy.gov (its robots file twice refused the connection, so no request was made to it; the mpg, the
kWh a mile and the 15,000 miles stand as read on 15 October 2026); PG&E's EV2-A schedule (fetched, but no PDF reader
on this machine); Chevrolet's prices (no request: the defaults stay "to confirm").

## The read as a household and a student (session 7550, chain 304 part B, 16 November 2026)

`docs/reviews/ev-game-read-2026-11-16.md`: five cases (a commuter in Phoenix, a family in Minneapolis, a driver in Fresno on
PG&E, a student checking the United States' answer, and A and B), 13 rows. What it changed on the page, held by
`site/scripts/test-ev-game-read.mjs`: the gasoline tip of a state given its region's price spells out the Petroleum
Administration for Defense District (PADD) and names the states the game gives that price; every electricity tip says
the state's average is every utility's homes together, every hour, fixed charges included, and California's links
`/learn/bill` for PG&E's, SCE's and SDG&E's own tariffs; the decisions fold no longer calls PG&E's E-TOU-C a rate made
for EV owners (both its off-peak rates stand above California's average); the net present value's tip gives the yearly
saving to the cent. No figure the game shows changed; the replication checks the new gasoline words from EIA's PADD
definitions (5,245 of 5,245).
