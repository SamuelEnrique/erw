# Page files of `/states`: every state on one page (contract)

Written by session 8014 (chain 581, part B, step 1) before the files land. The builder: `warehouse/derived/states_page.py`. The method: `docs/methods/states_page.md`. A shape that later has to change is changed here first, with a dated line saying what moved.

## The files

| Path | What |
|---|---|
| `site/data/states/index.json` | One row a place: the fifty states, the District of Columbia and the United States (`US`) |
| `site/data/states/<st>.json` | One place, `<st>` its two-letter code in lower case (`ca.json`, `dc.json`, `us.json`) |

Puerto Rico is in the generation table and in no other table the page reads, so it has no file.

## Rules every part keeps

- Every part names its ERW table (`table`, and `price_table`, `planned_table`, `retired_table`, `production_table`, `sector_tables`, `population_table` where a part reads more than one), its `vintage` (the newest month or year it holds, or the publisher's edition) and its `source` in words.
- A part a source does not cover for a place is present, with its arrays `null` and a `reason` (or `<key>_reason`) in plain words. A figure the source does not print is `null`, never `0`. A `0` is a zero the source printed.
- Months are `YYYY-MM`, years `YYYY`, UTC calendar months as EIA dates them. Each array is aligned to its part's `months` or `years`.
- Units: MWh for energy, MW for capacity, USD for money, USD per MWh for prices (EIA prints cents a kWh; the table holds USD per MWh), metric tons of CO2, kg of CO2 per MWh, MMcf for natural gas, trillion Btu for total energy.
- The only arithmetic of the ERW's own: sums of months into twelve-month windows and whole years (a year with any month missing is `null`), shares of a twelve-month total, revenue as sales times EIA's price, and the population shares of `serving`.

## `<st>.json`

| Key | Unit | What |
|---|---|---|
| `built`, `state`, `name`, `method`, `license`, `tables` | | when written, the code, the name, the method note, `public`, every table read |
| `generation.months`, `.by_source.<src>`, `.total` | MWh | net generation a month since January 2001, by `coal`, `natural_gas`, `nuclear`, `hydro`, `wind`, `solar`, `other_renewables`, `oil_and_other`, `not_itemized` (the groups of `docs/methods/generation_mix.md`); `total` is the sum of the sources a month |
| `generation.years`, `.annual.<src>` | MWh | whole years summed |
| `generation.last12` | MWh, percent | `from`, `to`, `total_mwh`, `mwh.<src>` and `share_pct.<src>` over the newest twelve months |
| `generation.hourly`, `.hourly_reason` | | always `null`, and why: no public source gives a state's generation by the hour |
| `retail.months`, `.sales_mwh.<sector>`, `.price_usd_per_mwh.<sector>`, `.revenue_usd.<sector>` | MWh, USD per MWh, USD | sectors `residential`, `commercial`, `industrial`, `transportation`, `all`; a month since January 2001 |
| `retail.years`, `.annual_sales_mwh`, `.annual_revenue_usd` | MWh, USD | whole years |
| `retail.last12.by_sector.<sector>` | | `sales_mwh`, `revenue_usd`, `price_usd_per_mwh` (revenue over sales) for the newest twelve months |
| `retail.customers` | count | `month` and `by_sector` for the newest month |
| `plants.capacity_by_technology.<group>` | MW, MWh | `nameplate_mw`, `net_summer_mw`, `generators` (and `energy_mwh` for storage) of the operating generators |
| `plants.capacity_total_mw`, `.plants` | MW, count | the sum and the number of plants |
| `plants.largest` | | the ten largest plants by nameplate: `plant_id`, `name`, `county`, `operator`, `balancing_authority`, `nameplate_mw`, `net_summer_mw`, `technology_group` (its largest), `technologies`, `lat`, `lon`, `generators` |
| `plants.coming_by_year.<year>.<group>` | MW | planned and under-construction generators by their planned year: `nameplate_mw`, `generators`, `under_construction_mw` |
| `plants.retiring_by_year.<year>.<group>` | MW | operating generators with a planned retirement date |
| `plants.retired_by_year.<year>.<group>` | MW | EIA-860M's retired sheet as the table holds it |
| `co2.years`, `.tons_by_fuel.<fuel>`, `.rate_kg_per_mwh` | t, kg/MWh | CO2 from power a year since 1990, by `all`, `coal`, `natural_gas`, `petroleum`, `other`; the rate for all fuels |
| `gas.months`, `.consumption.<use>`, `.marketed_production` | MMcf | `residential`, `commercial`, `industrial`, `electric_power` use, and marketed production, a month since January 2001; a use or production EIA does not print for the place is `null` with `consumption_reason.<use>` or `production_reason` |
| `energy.years`, `.by_source.<src>`, `.by_sector.<sector>` | trillion Btu | SEDS: `total`, `coal`, `natural_gas`, `petroleum`, `nuclear`, `renewables`, `electricity_retail_sales`; sectors `residential`, `industrial` (`commercial`, `transportation` null with `by_sector_reason`) |
| `disposition.years`, `.values.<v>` | MWh | the state profile's `total_net_generation`, `full_service_providers`, `energy_only_providers`, `estimated_losses`, `net_interstate_trade`, `total_international_imports`, `total_international_exports` |
| `serving.by_authority` | count, percent | each primary balancing authority of the place's counties: `code`, `name`, `region`, `grid` (one of the seven, or null), `counties`, `population`, `share_pct`, `shared_counties`, `reason` (for counties with no authority) |
| `serving.shares_reason`, `.counties_without_population`, `.counties_without_population_reason` | | where the counties of EIA-861 and of the Census Bureau do not match (Connecticut), the shares and populations are null and `shares_reason` says why; the unmatched county codes are listed |
| `serving.by_grid_pct` | percent | the population's share by grid of the seven, the rest under `none of the seven` |
| `large_load_laws.laws` | | each law: `law_id`, `bill`, `session`, `title`, `status`, `date`, `date_kind`, `effective`, `threshold`, `requirements`, `url`, `read`; an empty list with a `reason` where none is held |
| `severance` | | `in_tool`, and `address` and `products` where the severance tool holds the state, else `reason` |

## `index.json`

`built`, `method`, `license`, `tables`, `contract`, `generation_months` (first and last), and `states`: one row a place with `state`, `name`, `file`, `bytes`, `generation_last12_mwh`, `largest_source_last12`, `largest_source_share_pct`, `price_all_last12_usd_per_mwh`, `capacity_mw`, `grids`, `laws`.

## A real sample (Vermont, from the trial of 20 November 2026; arrays cut to their last three items, long strings cut and marked `[cut]`)

```json
{
 "state": "VT", "name": "Vermont", "method": "docs/methods/states_page.md", "license": "public",
 "generation": {"table": "state_generation_mix_monthly", "vintage": "2026-08", "unit": "MWh", "months": ["2026-06", "2026-07", "2026-08"], "by_source": {"coal": [null, null, null], "natural_gas": [188.6, 124.3, 0.0], "nuclear": [null, null, null], "hydro": [88448.3, 63442.3, 80383.9], "wind": [23400.0, 28636.0, 20175.0], "solar": [26177.2, 28549.7, 25956.3], "other_renewables": [29883.5, 31801.4, 48817.1], "oil_and_other": [0.0, 0.0, 0.0], "not_itemized": [275.3, 677.6, 223.0]}, "total": [168372.9, 153231.3, 175555.3], "years": ["2024", "2025", "2026"], "annual": {"hydro": [1283946.0, 1010947.0, null], "total": [2258890.5, 2052133.5, null]}, "last12": {"from": "2025-09", "to": "2026-08", "total_mwh": 1859457.7, "mwh": {"coal": null, "hydro": 864391.5, "wind": 357436.0}, "share_pct": {"coal": null, "hydro": 46.49, "wind": 19.22}}, "hourly": null, "hourly_reason": "No public source gives a state's generation by the hour; the hourly picture is by balancing authority, in the Grid tool."},
 "retail": {"table": "eia_retail_sales_monthly", "price_table": "eia_retail_electricity_prices", "vintage": "2026-08", "months": ["2026-06", "2026-07", "2026-08"], "sales_mwh": {"residential": [160597.5, 194017.8, 187367.2], "all": [429437.3, 491639.5, 480721.8]}, "price_usd_per_mwh": {"residential": [244.4, 237.5, 238.4], "all": [203.7, 201.7, 200.1]}, "revenue_usd": {"residential": [39250029.0, 46079228.0, 44668340.0], "all": [87476378.0, 99163687.0, 96192432.0]}, "last12": {"from": "2025-09", "to": "2026-08", "by_sector": {"residential": {"sales_mwh": 2223156.1, "revenue_usd": 531262676.0, "price_usd_per_mwh": 238.97}, "all": {"sales_mwh": 5486007.8, "revenue_usd": 1107208882.0, "price_usd_per_mwh": 201.82}}}, "customers": {"month": "2026-08", "by_sector": {"residential": 314483.0, "all": 380663.0}}},
 "plants": {"table": "eia860m_operating_generators", "vintage": "2026-09", "capacity_by_technology": {"hydro": {"nameplate_mw": 327.6, "net_summer_mw": 331.0, "generators": 129}, "storage": {"nameplate_mw": 20.9, "net_summer_mw": 20.9, "generators": 8, "energy_mwh": 53.3}}, "capacity_total_mw": 899.1, "plants": 117, "largest": [{"plant_id": "57979", "name": "Kingdom Community Wind", "county": "Orleans", "operator": "Green Mountain Power Corp", "balancing_authority": "ISNE", "nameplate_mw": 65.0, "net_summer_mw": 65.0, "technology_group": "wind", "technologies": {"wind": 65.0}, "lat": 44.7483, "lon": -72.4253, "generators": 1}], "coming_by_year": {"2028": {"solar": {"nameplate_mw": 90.0, "generators": 3, "under_construction_mw": 0.0}}}, "retiring_by_year": {}, "retired_by_year": {"2025": {"petroleum": {"nameplate_mw": 13.2, "generators": 1}}}},
 "co2": {"table": "eia_power_co2_state_annual", "vintage": "2024", "years": ["2022", "2023", "2024"], "tons_by_fuel": {"all": [13000.0, 9000.0, 8000.0], "natural_gas": [5000.0, 5000.0, 3000.0], "petroleum": [8000.0, 4000.0, 5000.0]}, "rate_kg_per_mwh": [5.9, 3.6, 3.6]},
 "gas": {"table": "eia_gas_consumption_state_monthly", "production_table": "eia_gas_production_state_monthly", "vintage": "2026-07", "unit": "MMcf", "months": ["2026-05", "2026-06", "2026-07"], "consumption": {"residential": [204.0, 109.0, 75.0], "electric_power": [null, 2.0, 2.0]}, "consumption_reason": {}, "marketed_production": null, "production_reason": "EIA prints no marketed production for Vermont: it is not a producing state in the Natural Gas Monthly"},
 "energy": {"table": "eia_seds_state_energy", "vintage": "2024", "unit": "trillion Btu", "years": ["2022", "2023", "2024"], "by_source": {"total": [116.3, 113.0, 114.2], "petroleum": [74.1, 72.7, 72.2]}, "by_sector": {"residential": [34.3, 33.0, 32.7], "industrial": [15.9, 14.6, 15.6], "commercial": null, "transportation": null}},
 "disposition": {"table": "eia_state_source_disposition_annual", "vintage": "2024", "unit": "MWh", "years": ["2022", "2023", "2024"], "values": {"total_net_generation": [2183829.0, 2480199.0, 2258891.0], "net_interstate_trade": [10126949.0, -1928985.0, 2683457.0]}},
 "serving": {"table": "eia_county_region", "population_table": "census_county_population", "vintage": "EIA-861 2025; population 2025", "population": 644663, "by_authority": [{"code": "ISNE", "name": "ISO New England", "region": "NE", "grid": "ISO-NE", "counties": 14, "population": 644663, "share_pct": 100.0, "shared_counties": 0, "reason": null}], "by_grid_pct": {"ISO-NE": 100.0}},
 "large_load_laws": {"table": "state_large_load_laws", "laws": [{"law_id": "laws_midwest_northeast-20", "bill": "H.727, Vermont Sustainable Data Centers Act", "status": "vetoed", "date": "2026-05-29", "threshold": "a data center uses or is able to use 20 MW or more [cut]", "url": "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/H-0727/ [cut]", "read": "2026-11-14"}]},
 "severance": {"file": "site/data/severance_rules.json", "in_tool": false, "reason": "the severance tool holds Texas, Louisiana, New Mexico only"}
}
```

Index row: `{"state": "VT", "name": "Vermont", "file": "vt.json", "bytes": 95342, "generation_last12_mwh": 1859457.7, "largest_source_last12": "hydro", "largest_source_share_pct": 46.49, "price_all_last12_usd_per_mwh": 201.82, "capacity_mw": 899.1, "grids": ["ISO-NE"], "laws": 1}`
