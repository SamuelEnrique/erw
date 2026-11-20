# Codebook: onrr

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 0 documented in full.

- [`onrr_production_annual`](#onrr_production_annual): Office of Natural Resources Revenue (ONRR), energy produced on federal lands by state and county (and offshore region), a year (session 951)
- [`onrr_production_monthly`](#onrr_production_monthly): Office of Natural Resources Revenue (ONRR), oil, gas and coal produced on federal and Native American lands, a month, nationally (session 951)
- [`onrr_revenue_monthly`](#onrr_revenue_monthly): Office of Natural Resources Revenue (ONRR), the revenue ONRR collects (royalties, rents, bonuses and the rest) by county, revenue type, lease type and commodity, a month (session 951)

### `onrr_production_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15068.

- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/blm_oil_gas_statistics_annual.md`](../methods/blm_oil_gas_statistics_annual.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example onrr_production:federal:offshore:alaska:gas_mcf, onrr_production:federal:offshore:alaska:oil_bbl, onrr_production:federal:offshore:gulf_of_america:gas_mcf; 830 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 4430270751.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, Mcf, bbl, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 29 distinct | 244 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 15068 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Adams, Colorado: Gas (mcf), Adams, Colorado: Oil (bbl), Adams, Mississippi: Oil (bbl); 735 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/calendar_year_production.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-21T17:11:22Z | 0 |
| `x_land_class` | not yet written |  | text | Federal, Mixed Exploratory, Native American | 0 |
| `x_land_category` | not yet written |  | text | Offshore, Onshore | 0 |
| `x_state` | not yet written |  | text | for example Alabama, Alaska, Arkansas; 29 distinct | 244 |
| `x_county` | not yet written |  | text | for example Adams, Albany, Alcona; 356 distinct | 244 |
| `x_fips` | not yet written |  | integer | 1003 to 56045; 412 distinct | 244 |
| `x_offshore_region` | not yet written |  | text | Alaska, Gulf of America, Pacific | 14930 |
| `x_product` | not yet written |  | text | Coal (ton), Coal waste (sub-econ) (ton), Coal-bituminous-raw (ton), Coal-fines circuit (ton), Gas (mcf), Geothermal - electrical generation (kilowatt hours), Oil (bbl) | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` |  | MWh; Mcf; bbl; short_ton | 15068 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `onrr_production_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2264.

- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/onrr.md`](../methods/onrr.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | onrr_production:federal:offshore:gas, onrr_production:federal:offshore:oil, onrr_production:federal:onshore:coal, onrr_production:federal:onshore:gas, onrr_production:federal:onshore:oil, onrr_production:native_american:onshore:coal, onrr_production:native_american:onshore:gas, onrr_production:native_american:onshore:oil | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 283 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 92760.0 to 403639747.0; 2264 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Mcf, bbl, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2264 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Federal Offshore, gas, Federal Offshore, oil, Federal Onshore, coal, Federal Onshore, gas, Federal Onshore, oil, Native American Onshore, coal, Native American Onshore, gas, Native American Onshore, oil | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/monthly_production.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:09Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-21T17:11:27Z | 0 |
| `x_land_class` | not yet written |  | text | Federal, Native American | 0 |
| `x_land_category` | not yet written |  | text | Offshore, Onshore | 0 |
| `x_commodity` | not yet written |  | text | Coal Prod Vol (tons), Gas Prod Vol (mcf), Oil Prod Vol (bbl) | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` |  | Mcf; bbl; short_ton | 2264 | 2003-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `onrr_revenue_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 413554.

- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/onrr.md`](../methods/onrr.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_revenue_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example onrr_revenue:federal:not_tied_to_a_lease:none:bonus:none:not_tied_to_a_commodity:none, onrr_revenue:federal:not_tied_to_a_lease:none:civil_penalties:none:not_tied_to_a_commodity:none, onrr_revenue:federal:not_tied_to_a_lease:none:other_revenues:none:not_tied_to_a_commodity:none; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 284 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -507476156.7 to 4370000000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 40 distinct | 20303 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 413554 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Abbeville, South Carolina: Other revenues, Hardrock, Abbeville, South Carolina: Rents, Hardrock, Abbeville, South Carolina: Royalties, Gold, Gold Ore; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/monthly_revenue.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-21T17:11:24Z | 0 |
| `x_land_class` | not yet written |  | text | Federal, Native American | 0 |
| `x_land_category` | not yet written |  | text | Not Tied to a Lease, Offshore, Onshore | 0 |
| `x_state` | not yet written |  | text | for example Alabama, Alaska, Arizona; 40 distinct | 20303 |
| `x_county` | not yet written |  | text | for example Abbeville, Adams, Alamosa; 602 distinct | 20303 |
| `x_fips` | not yet written |  | integer | 1003 to 56045; 745 distinct | 20303 |
| `x_offshore_region` | not yet written |  | text | Alaska, Atlantic, Gulf of America, Pacific | 403323 |
| `x_revenue_type` | not yet written |  | text | Bonus, Civil penalties, Inspection fees, Other revenues, Rents, Royalties | 0 |
| `x_lease_type` | not yet written |  | text | for example Asphalt, Chat, Cinders; 27 distinct | 753 |
| `x_commodity` | not yet written |  | text | for example Asbestos, Asphalt, Carbon dioxide; 43 distinct | 0 |
| `x_product` | not yet written |  | text | for example Anhydrous Sodium Sulfate, Asbestos, Asphaltic Crude; 116 distinct | 122243 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `revenue` |  | USD | 413554 | 2003-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

