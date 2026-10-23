# Electricity of the U.S., Canada and Mexico, a year (EIA's International Energy Statistics)

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `eia_international_electricity_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), International Energy Statistics, through EIA's API v2, route
`international`:
`https://api.eia.gov/v2/international/data/?frequency=annual&data[]=value&start=1980&facets[countryRegionId][]=CAN,MEX,USA&facets[activityId][]=12,7,2,3,4,23,9&facets[unit][]=BKWH,MK`
(the key is never written). Page: `https://www.eia.gov/international/data/world`. Connector:
`warehouse/connectors/eia_international_electricity.py` (session 886).

## Vintage and revision

Annual, 1980 to 2024 when written (run `20261023T045557Z`). A snapshot: each run replaces the table whole, so EIA's
revisions arrive at the next run with `--fresh` (pages saved in `warehouse/raw/eia_international_electricity/` are
reused otherwise; `--offline` asks nothing). Ceiling 20 requests a run (pages of 5,000, 3 seconds apart; an HTTP 429 or
5xx answer is asked once more after 60 seconds). Session 886 made 5 requests of its 20: the route's description, two
facet lists, one year of Canada's records to read the products and units, and one page for the whole table. The write
made 0 requests: it reused the saved page.

## Shape and variables

Series. `entity` `eia_intl:<country>:<product>`, EIA's codes. Country: `CAN`, `MEX`, `USA`. Product, as EIA numbers
them: `2` electricity, `27` nuclear, `28` fossil fuels, `29` renewables, `30` coal, `31` natural gas, `32` oil, `2890`
other gases, `33` hydroelectricity, `34` non-hydroelectric renewables, `35` geothermal, `36` solar, tide, wave, fuel cell,
`37` wind, `38` biomass and waste, `82` hydroelectric pumped storage, `116` solar, `117` tide and wave. `ts_utc` the
year's 1 January, 00:00:00Z; `freq` `P1Y`; `geo` `CA`, `MX` or `US`; `node` "<country>, <product>" as EIA names them
(such as "Canada, Hydroelectricity"). EIA's own field: `x_data_flag`, EIA's flag where it gives one.

| Variable | Unit | EIA's activity and unit | Products |
|---|---|---|---|
| `generation` | `MWh` | 12, billion kWh (`BKWH`) times 1,000,000 | all 17 |
| `capacity` | `MW` | 7, million kW (`MK`) times 1,000 | all but coal, natural gas, oil and other gases |
| `consumption` | `MWh` | 2, billion kWh times 1,000,000 | `2` electricity |
| `imports` | `MWh` | 3, billion kWh times 1,000,000 | `2` electricity |
| `exports` | `MWh` | 4, billion kWh times 1,000,000 | `2` electricity |
| `net_imports` | `MWh` | 23, billion kWh times 1,000,000 | `2` electricity |
| `distribution_losses` | `MWh` | 9, billion kWh times 1,000,000 | `2` electricity |

A product's parts overlap: fossil fuels holds coal, gas and oil; renewables holds hydro, wind, solar and the rest. A sum
takes one level. Net imports are below zero where a country exports more than it imports (Canada in all 45 years, Mexico
in 30), and pumped storage generation is below zero in Canada's 45 rows and in 35 of the U.S.'s, as EIA gives them.

When written: 4,131 rows (of EIA's 4,501 records), 51 series (17 products for each of the three countries), 1980 to
2024. Generation 2,101 rows, capacity 1,355, each of the other five variables 135 (45 years for each country).
Generation in 2024: the U.S. 4,393 TWh, Canada 611 TWh (648 in 2015), Mexico 387 TWh (311 in 2015). Capacity in 2024:
1,284 GW, 162 GW and 100 GW.

`x_data_flag` is set on 315 rows, in EIA's words: 313 "A value exists, but rounds to zero; non-rounded values appear when
downloaded", one "Values derived using SMR estimation methodology. Appears as a superscript." (Canada's fossil fuel
capacity, 2024) and one "Values flagged perliminary by source. Appears as a superscript." (Mexico's fossil fuel capacity,
2024).

## Reading the API

- One query for the whole table: the three countries, the seven activities and the two units as facets, pages of 5,000
  sorted by period, country, product and activity. The rows read must equal the count EIA gives, or the run stops.
- Only billion kWh and million kW are asked. EIA gives the same energy again in quadrillion Btu, terajoules and million
  tonnes of oil equivalent, which are not taken.
- A value EIA leaves empty or marks ("NA", "--", "(s)") has no row. Nothing is filled.
- A country, activity or unit not in the map stops the run; so does an (entity, variable, ts_utc) given twice.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: may be
public, flag public, agrees). Cite "U.S. Energy Information Administration, International Energy Statistics".

## Cross-check (session 886)

- Imports less exports equal net imports in 45 of 45 years for each country. Nuclear, fossil fuels and renewables sum to
  the total within 2 percent in every year.
- The U.S.'s generation here against `eia_state_generation_monthly`'s states summed with their small-scale solar: 4,092.9
  TWh against 4,092.8 in 2015, 4,256.7 against 4,274.2 in 2023, 4,392.6 against 4,408.9 in 2024 (within 0.4 percent; EIA's
  two products are revised at different times).
- Canada's exports against the U.S.'s imports, two countries' reports of one flow: 43.6 and 45.1 TWh in 2010, 68.3 and
  75.8 in 2015, 49.3 and 38.9 in 2023, 35.6 and 33.3 in 2024.

## What it does not hold

- EIA's copies of the same energy in quadrillion Btu, terajoules and tonnes of oil equivalent.
- Any country but the U.S., Canada and Mexico, and years before 1980.
- Any value EIA leaves empty or marks; nothing is filled.
- Canada's trade by month and by province and state: the Canada Energy Regulator's record is in `cer_electricity_trade`
  (session 887). The U.S.'s generation by state is in `eia_state_generation_monthly`.
