# Every state on one page (`/states`)

Session 8014, chain 581 (part B), 20 November 2026. Builder: `warehouse/derived/states_page.py`, a step of the data machine's daily run (`dm_states_page`, held by `dm_test_states`). Contract: `docs/state/page_files_states.md`. Page: `site/app/states/page.tsx`, reading `site/lib/states.ts`. Replication: `replication/states/replicate.py`. License: public (every table is a U.S. Energy Information Administration or U.S. Census Bureau publication, or the ERW's research files of public law).

## What a reader gets

Choose a state, the District of Columbia or the United States, and a second beside it. The page shows: what the place generates by source, by whole year since 2001 and month by month; each source's share of the newest twelve months and of chosen years since 2001; what its homes, businesses, industry and transportation bought, paid and the average price, with the number of customers; its operating capacity by source, its ten largest plants, what is planned by year and what is planned to retire; who operates the grid its people are on; its electricity's source and disposition from EIA's state profile; carbon dioxide from its power plants by fuel since 1990; natural gas used by sector and produced; total energy by source and sector; its large-load law and its severance tax where the ERW holds them.

## Monthly, not hourly

No public source gives a state's generation by the hour. EIA's hourly figures (Form EIA-930) are by balancing authority, and an authority's territory crosses state lines. The page says so once and links to the Grid tool at the region of the state's largest authority.

## Inputs

| Part | ERW table | Source |
|---|---|---|
| generation | `state_generation_mix_monthly` | EIA, Electric Power Monthly (Form EIA-923), net generation by state and source, in the groups of `docs/methods/generation_mix.md` |
| retail | `eia_retail_sales_monthly`, `eia_retail_electricity_prices` | EIA, Form EIA-861M: sales, customers and average price by state and sector |
| plants | `eia860m_operating_generators`, `eia860m_planned_generators`, `eia860m_retired_generators` | EIA, Form EIA-860M (the edition in the vintage column) |
| co2 | `eia_power_co2_state_annual` | EIA, State Electricity Profiles, emissions by state by fuel |
| gas | `eia_gas_consumption_state_monthly`, `eia_gas_production_state_monthly` | EIA, Natural Gas Monthly |
| energy | `eia_seds_state_energy`, `eia_seds_residential_annual`, `eia_seds_industrial_annual` | EIA, State Energy Data System |
| disposition | `eia_state_source_disposition_annual` | EIA, State Electricity Profiles, source and disposition |
| serving | `eia_county_region`, `census_county_population` | Census Bureau county estimates; Form EIA-861's utilities and authorities by county (`docs/methods/county_population_and_regions.md`) |
| large_load_laws | `state_large_load_laws` | the ERW's research files, each law read at its own page |
| severance | `site/data/severance_rules.json` | the severance tool's rules, each cited |

Net interstate trade (session 10223, the states audit, finding 1) is a line of EIA's disposition (`docs/methods/eia_state_source_disposition_annual.md`), so it is out less in: positive where a state sent more electricity to other states than it took in. Read that way, net generation and international imports less the trade equal the sales, losses and exports to within EIA's direct use in 51 of the 52 places (the median rest 2.7 percent of the disposition); read the other way, 23 places fall below zero (the median 43.9 percent). The page said "in less out" until session 10223.

## Arithmetic

- A twelve-month window is the newest twelve months the part holds, summed. A source with no figure in any of the twelve months is null, never zero.
- A whole year is the sum of its twelve months, and is null when any month is missing.
- A share is the source's sum over the sum of every source's for the same months. A source can be below zero (pumped storage uses more than it makes), so a share can be below zero, as EIA's figures make it.
- What the groups hold (session 10223, the states audit, finding 3): pumped storage is in "Oil and other" (EIA's code HPS, `docs/methods/generation_mix.md`), the line that falls below zero (132 whole state-years, Virginia's 2024 -906,229 MWh); solar is utility-scale only, small-scale solar is not in EIA's state figures. In the capacity table pumped storage is in "Batteries and pumped storage".
- A source is summed over the months EIA prints for it (finding 4): in a month EIA withholds a source, its generation is in "Not itemized by EIA", and the source's twelve months hold fewer than twelve. On the files of 20 November 2026, 44 places print such a source; in 27 it is only "Not itemized" itself, in 17 another source too. The District of Columbia's natural gas, its largest source, is 9 months (40.05 percent of the twelve months; the 3 withheld months' unitemized generation, 20,722 MWh, would make it 49.15).
- Revenue is EIA's sales times EIA's average price, month by month and sector by sector. EIA computes the price as revenue over sales; the product gives EIA's revenue to within the price's rounding (a tenth of a dollar a MWh). The warehouse holds no state revenue column: the utilities' rows of `eia861m_utility_sales_monthly` do not sum to the state totals (EIA's state figures include its estimates for the utilities it does not survey each month), so they are not used.
- Who operates the grid: each county counts whole for its primary authority (the one whose utilities serve most of the county's customers in EIA-861 of 2025), weighted by the Census Bureau's newest county population. A county whose utilities name no authority, or that EIA-861 lists with no utility, is counted under "No authority named" with its reason.
- Rounded once (session 11407, the states audit of 26 November 2026, finding 6, readied for Samuel's ruling): the files carry the twelve months' price and the shares already rounded to 0.01, so the page computes the twelve months' price as revenue over sales, a source's share of the twelve months as its MWh over the total, and an authority's share of the people as its people over the state's, from the same file, and rounds each once. On the files of 28 November 2026, 34 cells move by one in their last digit: 13 of 236 prices (Texas's homes 15.98 to 15.99 cents a kWh), 13 of 423 shares, 8 of 109 shares of the people (SPP's share of Texas 4.2 to 4.1 percent).
- Nothing else is computed: no estimate, no model, no fill.

## Run

`python warehouse/derived/states_page.py` (about 20 seconds); `--site-dir DIR` writes elsewhere for a trial; `--only CA TX` writes named places alone and no index.

## Cross-check against EIA's own state profiles (20 November 2026)

`replication/states/replicate.py` sets each of five states' 2024 figures, from the monthly tables the page reads, beside EIA's State Electricity Profile for 2024 (`eia_state_source_disposition_annual`), a separate publication:

| State | Net generation 2024, twelve months summed (MWh) | State profile (MWh) | Difference | Retail sales 2024, twelve months (MWh) | State profile, full-service and energy-only (MWh) | Difference |
|---|---|---|---|---|---|---|
| CA | 214,191,383 | 214,191,383 | 0.00% | 245,717,145 | 243,688,307 | +0.83% |
| TX | 566,502,688 | 566,502,688 | 0.00% | 505,431,317 | 495,165,178 | +2.07% |
| NY | 129,015,493 | 129,015,493 | 0.00% | 140,497,501 | 140,024,439 | +0.34% |
| WV | 50,594,818 | 50,594,818 | 0.00% | 32,990,570 | 32,990,570 | 0.00% |
| VT | 2,258,891 | 2,258,891 | 0.00% | 5,458,947 | 5,453,555 | +0.10% |

Generation agrees to the MWh in all five. Sales differ by up to 2.1 percent: Form EIA-861M's monthly figures hold EIA's estimates for the utilities it does not survey each month, which the annual Form EIA-861 behind the profile replaces with their reported sales. The page shows the monthly figures and says which form they come from.

The replication also reads the page for four choices of place (Texas alone, California with West Virginia, Vermont with the United States, the District of Columbia with New York) and computes every marked figure again from the files: 1,196 of 1,196 reproduced on the local build of 20 November 2026.

### Decisions (session 8014)

| Key | Decision | Default |
|---|---|---|
| `as-published` | The publishers' figures as the files hold them; only the sums, shares, revenue and population shares named above. The ERW fills nothing; EIA's monthly figures hold EIA's own estimates and its newest months are revised (session 10223, the states audit, finding 5) | as published |
| `not-held` | A figure a source does not print is "not held" with the reason, never zero | "not held" |
| `first-place` | The page opens on Texas, the largest generator of the fifty states, with no second place | Texas; no second place |
| `twelve-months` | Headlines and the sector table are the newest twelve months; a year only when all twelve months are held | newest twelve months |
| `revenue` | What a sector paid is sales times EIA's average price | sales times price |
| `who-operates` | Primary authority by county, weighted by county population | by population |
| `monthly` | Monthly, said once, with the link to the Grid tool | monthly |
| `opening-views` | Yearly generation from 2001; monthly charts from 2015; share chart on natural gas; price chart on homes | as listed |
| `nominal` | Nominal dollars; cents a kWh on the page | nominal |
| `places` | The fifty states, DC and the United States; Puerto Rico has no file. The United States' plants are EIA-860M's whole, Puerto Rico's 6,474 MW in them; its generation and sales leave Puerto Rico out (session 10223, the states audit, finding 7) | 52 places |
