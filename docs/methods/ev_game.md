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
