# Codebook: onrr

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 3 documented in full.

- [`onrr_production_annual`](#onrr_production_annual): One energy product (oil, gas, coal and its kinds, or geothermal electricity) produced on federal or Native American lands in one county or offshore region in one calendar year, 2003 to 2025, from ONRR's Natural Resources Revenue Data.
- [`onrr_production_monthly`](#onrr_production_monthly): Oil, gas or coal produced on federal or Native American lands, onshore or offshore, in one month, nationally, from ONRR's Natural Resources Revenue Data.
- [`onrr_revenue_monthly`](#onrr_revenue_monthly): The revenue ONRR collected of one revenue type (royalties, rents, bonuses and the rest) for one lease type, commodity and product, in one county, offshore region or no place, in one month, from ONRR's Natural Resources Revenue Data.

### `onrr_production_annual`

One energy product (oil, gas, coal and its kinds, or geothermal electricity) produced on federal or Native American lands in one county or offshore region in one calendar year, 2003 to 2025, from ONRR's Natural Resources Revenue Data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15068.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z (a calendar year, not an instant); freq P1Y.
- **Revisions:** A snapshot; each run replaces the table whole. vintage is the file's last-modified time. ONRR revises recent periods.
- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/blm_oil_gas_statistics_annual.md`](../methods/blm_oil_gas_statistics_annual.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: onrr_production:<class>:<category>:<FIPS code>_<county name> or :<offshore region>, then :<product> | none | text | for example onrr_production:federal:offshore:alaska:gas_mcf, onrr_production:federal:offshore:alaska:oil_bbl, onrr_production:federal:offshore:gulf_of_america:gas_mcf; 830 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 4430270751.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, Mcf, bbl, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>; empty for offshore rows and rows ONRR gives no state | none | text | for example US-AK, US-AL, US-AR; 29 distinct | 244 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15068 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: County, State: Product (or the offshore region), in ONRR's words, not a pricing node | none | text | for example Adams, Colorado: Gas (mcf), Adams, Colorado: Oil (bbl), Adams, Mississippi: Oil (bbl); 735 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/calendar_year_production.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's last-modified time, one value | none | utc time | 2026-10-21T17:11:22Z | 0 |
| `x_land_class` | ONRR's land class: Federal, Native American or Mixed Exploratory (the source's name: Land Class) | none | text | Federal, Mixed Exploratory, Native American | 0 |
| `x_land_category` | ONRR's land category: Onshore or Offshore (the source's name: Land Category) | none | text | Offshore, Onshore | 0 |
| `x_state` | The state, as ONRR names it (the source's name: State) | none | text | for example Alabama, Alaska, Arkansas; 29 distinct | 244: Offshore rows, or ONRR gives no state |
| `x_county` | The county, as ONRR names it (the source's name: County) | none | text | for example Adams, Albany, Alcona; 356 distinct | 244: Offshore rows, or ONRR gives no county |
| `x_fips` | The county's FIPS code (the source's name: FIPS Code) | none | integer | 1003 to 56045; 412 distinct | 244: Offshore rows, or ONRR gives no county |
| `x_offshore_region` | The offshore region (Alaska, Gulf of America, Pacific) (the source's name: Offshore Region) | none | text | Alaska, Gulf of America, Pacific | 14930: Onshore rows |
| `x_product` | ONRR's product with its unit (Oil (bbl), Gas (mcf), Coal (ton), Geothermal - electrical generation (kilowatt hours) and the others) (the source's name: Product) | none | text | Coal (ton), Coal waste (sub-econ) (ton), Coal-bituminous-raw (ton), Coal-fines circuit (ton), Gas (mcf), Geothermal - electrical generation (kilowatt hours), Oil (bbl) | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | The product produced in the year, in the row's unit: bbl, Mcf, short_ton (ONRR's tons) or MWh (geothermal electricity, ONRR's kilowatt hours over 1,000) | MWh; Mcf; bbl; short_ton | 15068 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `onrr_production_monthly`

Oil, gas or coal produced on federal or Native American lands, onshore or offshore, in one month, nationally, from ONRR's Natural Resources Revenue Data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2264.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M.
- **Revisions:** A snapshot; each run replaces the table whole. vintage is the file's last-modified time. ONRR revises recent months.
- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/onrr.md`](../methods/onrr.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: onrr_production:<federal\|native_american>:<onshore\|offshore>:<oil\|gas\|coal> | none | text | onrr_production:federal:offshore:gas, onrr_production:federal:offshore:oil, onrr_production:federal:onshore:coal, onrr_production:federal:onshore:gas, onrr_production:federal:onshore:oil, onrr_production:native_american:onshore:coal, onrr_production:native_american:onshore:gas, onrr_production:native_american:onshore:oil | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 283 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 92760.0 to 403639747.0; 2264 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Mcf, bbl, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2264 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Land class and category, product (Federal Offshore, gas), not a pricing node | none | text | Federal Offshore, gas, Federal Offshore, oil, Federal Onshore, coal, Federal Onshore, gas, Federal Onshore, oil, Native American Onshore, coal, Native American Onshore, gas, Native American Onshore, oil | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/monthly_production.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:09Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's last-modified time, one value | none | utc time | 2026-10-21T17:11:27Z | 0 |
| `x_land_class` | ONRR's land class: Federal or Native American (the source's name: Land Class) | none | text | Federal, Native American | 0 |
| `x_land_category` | ONRR's land category: Onshore or Offshore (the source's name: Land Category) | none | text | Offshore, Onshore | 0 |
| `x_commodity` | ONRR's commodity with its unit (Oil Prod Vol (bbl), Gas Prod Vol (mcf), Coal Prod Vol (tons)) (the source's name: Commodity) | none | text | Coal Prod Vol (tons), Gas Prod Vol (mcf), Oil Prod Vol (bbl) | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | The oil, gas or coal produced in the month, bbl, Mcf or short_ton (ONRR's tons) as the row's unit says | Mcf; bbl; short_ton | 2264 | 2003-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `onrr_revenue_monthly`

The revenue ONRR collected of one revenue type (royalties, rents, bonuses and the rest) for one lease type, commodity and product, in one county, offshore region or no place, in one month, from ONRR's Natural Resources Revenue Data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 413554.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M.
- **Revisions:** A snapshot; each run replaces the table whole. vintage is the file's last-modified time. A negative value is ONRR's adjustment of an earlier month, kept.
- **Source:** onrr:revenue_data U.S. Department of the Interior, Office of Natural Resources Revenue, Natural Resources Revenue Data, downloads (https://revenuedata.doi.gov/downloads/)
- **Method note:** [`docs/methods/onrr.md`](../methods/onrr.md)
- **Cite as:** U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR). Natural Resources Revenue Data (production and revenue downloads). Via the Energy Research Warehouse (ERW), table `onrr_revenue_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: onrr_revenue:<class>:<category>:<place>:<revenue type>:<lease type>:<commodity>:<product>, none where ONRR leaves a part empty | none | text | for example onrr_revenue:federal:not_tied_to_a_lease:none:bonus:none:not_tied_to_a_commodity:none, onrr_revenue:federal:not_tied_to_a_lease:none:civil_penalties:none:not_tied_to_a_commodity:none, onrr_revenue:federal:not_tied_to_a_lease:none:other_revenues:none:not_tied_to_a_commodity:none; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 284 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -507476156.7 to 4370000000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or empty (offshore, not tied to a lease, or Native American revenue ONRR gives no state for) | none | text | for example US-AK, US-AL, US-AR; 40 distinct | 20303 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 413554 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Place: revenue type, commodity in ONRR's words, not a pricing node | none | text | for example Abbeville, South Carolina: Other revenues, Hardrock, Abbeville, South Carolina: Rents, Hardrock, Abbeville, South Carolina: Royalties, Gold, Gold Ore; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | onrr:revenue_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://revenuedata.onrr.gov/downloads/monthly_revenue.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:11:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's last-modified time, one value | none | utc time | 2026-10-21T17:11:24Z | 0 |
| `x_land_class` | ONRR's land class: Federal or Native American (the source's name: Land Class) | none | text | Federal, Native American | 0 |
| `x_land_category` | ONRR's land category: Onshore, Offshore or Not Tied to a Lease (the source's name: Land Category) | none | text | Not Tied to a Lease, Offshore, Onshore | 0 |
| `x_state` | The state, as ONRR names it (the source's name: State) | none | text | for example Alabama, Alaska, Arizona; 40 distinct | 20303: Offshore, not tied to a lease, or ONRR gives no state |
| `x_county` | The county, as ONRR names it (the source's name: County) | none | text | for example Abbeville, Adams, Alamosa; 602 distinct | 20303: Offshore, not tied to a lease, or ONRR gives no county |
| `x_fips` | The county's FIPS code (the source's name: FIPS Code) | none | integer | 1003 to 56045; 745 distinct | 20303: Offshore, not tied to a lease, or ONRR gives no county |
| `x_offshore_region` | The offshore region (Alaska, Atlantic, Gulf of America, Pacific) (the source's name: Offshore Region) | none | text | Alaska, Atlantic, Gulf of America, Pacific | 403323: Not an offshore row |
| `x_revenue_type` | ONRR's revenue type: Royalties, Rents, Bonus, Other revenues, Civil penalties, Inspection fees (the source's name: Revenue Type) | none | text | Bonus, Civil penalties, Inspection fees, Other revenues, Rents, Royalties | 0 |
| `x_lease_type` | ONRR's mineral lease type (Coal, Asphalt, Clay and the others) (the source's name: Mineral Lease Type) | none | text | for example Asphalt, Chat, Cinders; 27 distinct | 753: ONRR gives none |
| `x_commodity` | ONRR's commodity the revenue is paid on (the source's name: Commodity) | none | text | for example Asbestos, Asphalt, Carbon dioxide; 43 distinct | 0 |
| `x_product` | ONRR's product the revenue is paid on (the source's name: Product) | none | text | for example Anhydrous Sodium Sulfate, Asbestos, Asphaltic Crude; 116 distinct | 122243: ONRR gives none |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `revenue` | The revenue ONRR collected in the month, USD (negative for an adjustment of an earlier month) | USD | 413554 | 2003-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

