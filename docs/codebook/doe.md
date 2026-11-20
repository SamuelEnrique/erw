# Codebook: doe

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (1 entities, 2 events, 2 series; tiers: 5 source); 0 documented in full.

- [`doe_grip_selections`](#doe_grip_selections): U.S. Department of Energy, Office of Electricity, Grid Resilience and Innovation Partnerships (GRIP) Program Projects: each project selected in the first two rounds (session 2050)
- [`doe_lead_energy_burden`](#doe_lead_energy_burden): U.S. Department of Energy, Low-Income Energy Affordability Data (LEAD Tool), 2022 update: households, their average income and energy costs, and their energy burden, by county and state and by income as a share of area median income (session 2140)
- [`doe_lng_export_applications`](#doe_lng_export_applications): U.S. Department of Energy, Summary of LNG Export Applications of the Lower 48 States, as of 2026-09-30: each long-term (and small-scale) application to export LNG, CNG or CGL, with its FTA and non-FTA parts (session 2044)
- [`doe_oe417_events`](#doe_oe417_events): U.S. Department of Energy, Office of Cybersecurity, Energy Security, and Emergency Response, Electric Emergency Incident and Disturbance Reports (Form DOE-417, formerly OE-417), the yearly summaries 2016 to 2025: each reported event's start, restoration, area, NERC region, alert criteria, event type, demand lost and customers affected (session 2028)
- [`doe_useer_employment`](#doe_useer_employment): U.S. Department of Energy, 2026 U.S. Energy and Employment Report (USEER), public data: energy employment in 2025 by sector, technology (subsector) and industry, nationally (with 2024's totals), and by sector and technology in each state (session 2000)

### `doe_grip_selections`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 105.

- **Source:** doe:grip_selections U.S. Department of Energy, Office of Electricity, GRIP Program Projects (https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects)
- **Method note:** [`docs/methods/doe_grip_selections.md`](../methods/doe_grip_selections.md)
- **Cite as:** U.S. Department of Energy (DOE). Grid Resilience and Innovation Partnerships (GRIP) Program Projects (Office of Electricity). Via the Energy Research Warehouse (ERW), table `doe_grip_selections`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example doe_grip:first:0ab9829b115d, doe_grip:first:0d5c5da6f61c, doe_grip:first:0da2c3abc8a7; 105 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2023-10-18, 2024-08-06, 2024-10-18 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | grip_selection | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | for example Alaska Energy Authority, Algonquin Power Fund America Inc., Allete Inc.; 100 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 105 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 105 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 105 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 105 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | awarded, selected, withdrawn | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:grip_selections | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:08:05Z | 0 |
| `x_project` | not yet written |  | text | for example AEP Advance Distribution Management System and Distributed Energy Resource Management System (ADMS &amp; DERMS) Initiative, AI Grid-Enabled Transportation Electrification in America’s Automotive Heartland, Accelerating Building Thermal Electrification While Managing System Impacts; 105 distinct | 0 |
| `x_program` | not yet written |  | text | Grid Innovation Program, Grid Resilience Utility and Industry Grants, Smart Grid Grants | 0 |
| `x_round` | not yet written |  | text | first, second | 0 |
| `x_federal_usd` | not yet written |  | integer | 1116174 to 700000000; 90 distinct | 0 |
| `x_recipient_usd` | not yet written |  | integer | 1116174 to 3209440351; 104 distinct | 0 |
| `x_states` | not yet written |  | text | for example AK, AL, AL;GA;KY;MO;MS;NC;TN;VA; 65 distinct | 0 |
| `x_state_names` | not yet written |  | text | for example Alabama, Alabama, Georgia, Kentucky, Missouri, Mississippi, North Carolina, Tennessee, Virginia, Alaska; 65 distinct | 0 |
| `x_announced_on` | not yet written |  | date | 2023-10-18, 2024-08-06, 2024-10-18 | 0 |
| `x_dates_from` | not yet written |  | text | https://www.energy.gov/oe/grid-innovation-program, https://www.energy.gov/oe/grid-resilience-utility-and-industry-grants, https://www.energy.gov/oe/smart-grid-grants | 0 |

### `doe_lead_energy_burden`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 160419.

- **Source:** doe:lead_2022 DOE, LEAD Tool 2022 Update (https://data.openei.org/submissions/6219)
- **Method note:** [`docs/methods/doe_lead_energy_burden.md`](../methods/doe_lead_energy_burden.md)
- **Cite as:** U.S. Department of Energy (DOE). Low-Income Energy Affordability Data (LEAD Tool), 2022 Update. Via the Energy Research Warehouse (ERW), table `doe_lead_energy_burden`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example doe_lead:10001, doe_lead:10003, doe_lead:10005; 3274 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 13749689.8385; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 160419 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example AK, AL, AR; 2012 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:lead_2022 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://data.openei.org/files/6219/AK-2022-LEAD-data.zip, https://data.openei.org/files/6219/AL-2022-LEAD-data.zip, https://data.openei.org/files/6219/AR-2022-LEAD-data.zip; 52 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:59:10Z to 2026-10-24T00:10:31Z; 52 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T23:59:10Z to 2026-10-24T00:10:31Z; 52 distinct | 0 |
| `x_level` | not yet written |  | text | county, state | 0 |
| `x_bracket` | not yet written |  | text | 0-30%, 100-150%, 150%+, 30-60%, 60-80%, 80-100%, all | 0 |
| `x_fips` | not yet written |  | integer | 1 to 72153; 3274 distinct | 0 |
| `x_file` | not yet written |  | text | for example AK AMI Counties 2022.csv, AL AMI Counties 2022.csv, AR AMI Counties 2022.csv; 52 distinct | 0 |

Variables (49):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_cost_avg:ami_0_30` |  | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_100_150` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_150_up` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_30_60` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_60_80` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_80_100` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_all` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_0_30` |  | pct | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_100_150` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_150_up` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_30_60` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_60_80` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_80_100` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_all` |  | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_0_30` |  | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_100_150` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_150_up` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_30_60` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_60_80` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_80_100` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_all` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_0_30` |  | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_100_150` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_150_up` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_30_60` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_60_80` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_80_100` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_all` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_0_30` |  | count | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_100_150` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_150_up` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_30_60` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_60_80` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_80_100` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_all` |  | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_0_30` |  | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_100_150` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_150_up` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_30_60` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_60_80` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_80_100` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_all` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_0_30` |  | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_100_150` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_150_up` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_30_60` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_60_80` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_80_100` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_all` |  | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `doe_lng_export_applications`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 135.

- **Source:** doe:lng_export_applications U.S. Department of Energy, Hydrocarbons and Geothermal Energy Office, Summary of LNG Export Applications of the Lower 48 States (https://www.energy.gov/fecm/articles/summary-lng-export-applications-lower-48-states)
- **Method note:** [`docs/methods/doe_lng_export_applications.md`](../methods/doe_lng_export_applications.md)
- **Cite as:** U.S. Department of Energy (DOE). Summary of LNG Export Applications of the Lower 48 States (Hydrocarbons and Geothermal Energy Office). Via the Energy Research Warehouse (ERW), table `doe_lng_export_applications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example doe_lng:10-160-LNG, doe_lng:10-85-LNG, doe_lng:11-115-LNG; 135 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example Accel LNG Energy Llc, Advanced Energy Solutions, L.L.C., Air Flow North America Corp.; 112 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 135 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 135 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 135 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 135 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, planned, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2026-09-30 | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 135 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:lng_export_applications | 0 |
| `x_section` | not yet written |  | text | canada_mexico, lower48, small_scale | 0 |
| `x_quantity_as_published` | not yet written |  | text | for example 0.002 Bcf/d, 0.003 Bcf/d, 0.006 Bcf/d; 100 distinct | 0 |
| `x_fta_bcfd` | not yet written |  | number | 0.003 to 5.13; 76 distinct | 12 |
| `x_non_fta_bcfd` | not yet written |  | number | 0.002 to 5.13; 77 distinct | 20 |
| `x_fta_status` | not yet written |  | text | Approved, Dismissed, Under DOE Review, Vacated, Withdrawn, n/a | 3 |
| `x_fta_docket` | not yet written |  | text | for example 10-160-LNG, 10-85-LNG, 11-115-LNG; 123 distinct | 12 |
| `x_non_fta_status` | not yet written |  | text | Approved, Approved (F), Dismissed, Expired, In Abeyance, Under DOE Review, Vacated, Vacated (F), Withdrawn, n/a | 1 |
| `x_non_fta_docket` | not yet written |  | text | for example 10-111-LNG, 10-161-LNG, 11-128-LNG; 115 distinct | 20 |
| `x_nepa_pending` | not yet written |  | text | yes | 123 |
| `x_footnotes` | not yet written |  | empty | no cell holds a value | 135 |
| `x_as_of` | not yet written |  | date | 2026-09-30 | 0 |
| `x_page` | not yet written |  | integer | 1, 14, 15, 16, 2, 3, 4, 5, 6 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/sites/default/files/2026-09/Summary%20of%20LNG%20Export%20Applications_9.30.26_1.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:41:41Z | 0 |

### `doe_oe417_events`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 3313.

- **Source:** doe:oe417 U.S. Department of Energy, DOE-417 Annual Summaries (https://doe417.pnnl.gov/)
- **Method note:** [`docs/methods/doe_oe417_events.md`](../methods/doe_oe417_events.md)
- **Cite as:** U.S. Department of Energy (DOE). Office of Cybersecurity, Energy Security, and Emergency Response (CESER), Electric Emergency Incident and Disturbance Reports (Form DOE-417): Annual Summaries. Via the Energy Research Warehouse (ERW), table `doe_oe417_events`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example doe417:2016-0001, doe417:2016-0002, doe417:2016-0003; 3313 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2016-01-04 to 2025-12-30; 1756 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | for example actual_physical_attack, actual_physical_attack_vandalism, actual_physical_event; 63 distinct | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 3313 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 3313 |
| `mw` | The capacity involved, in megawatts | MW | number | 0.0 to 160000.0; 357 distinct | 1441 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 3313 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 3313 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | restored | 694 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:oe417 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://doe417.pnnl.gov/summaries/2016_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2017_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2018_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2019_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2020_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2021_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2022_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2023_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2024_Annual_Summary.xlsx, https://doe417.pnnl.gov/summaries/2025_Annual_Summary.xlsx | 0 |
| `x_year` | not yet written |  | integer | 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |
| `x_row` | not yet written |  | integer | 1 to 622; 622 distinct | 0 |
| `x_begin_date` | not yet written |  | date | 2016-01-04 to 2025-12-30; 1756 distinct | 0 |
| `x_begin_time` | not yet written |  | text | for example 00:00, 00:01, 00:02; 1441 distinct | 0 |
| `x_restoration_date` | not yet written |  | text | for example - Unknown, 2016-01-05, 2016-01-11; 1648 distinct | 363 |
| `x_restoration_time` | not yet written |  | text | for example - Unknown, 00:00, 00:01; 1273 distinct | 363 |
| `x_area_affected` | not yet written |  | text | for example Ada County, Idaho, AitkinCounty, Minnesota, Alabama; 1366 distinct | 0 |
| `x_nerc_region` | not yet written |  | text | for example FRCC, MPCC, MRO; 32 distinct | 1058 |
| `x_alert_criteria` | not yet written |  | text | for example - 10. Suspected Physical Attack, Actual Physical Attack, Bulk Electric System Emergency resulting in voltage deviation on a Facility; A voltage deviation equal to or greater than 10 percent of nominal voltage sustained for greater than or equal to 15 continuous minutes.; 117 distinct | 0 |
| `x_event_types` | not yet written |  | text | for example actual_physical_attack, actual_physical_attack_vandalism, actual_physical_event; 158 distinct | 36 |
| `x_event_type_as_published` | not yet written |  | text | for example - Cyber event (information technology), - Failure at high voltage substation or switchyard, - Failure at high voltage substation or switchyard - Other; 211 distinct | 0 |
| `x_demand_loss_mw_as_published` | not yet written |  | text | for example 0, 0.757, 1; 361 distinct | 135 |
| `x_customers_affected_as_published` | not yet written |  | text | for example 0, 1, 1,031; 830 distinct | 9 |
| `x_customers_affected` | not yet written |  | integer | 0 to 50000000; 786 distinct | 853 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:15:05Z, 2026-10-23T18:15:06Z, 2026-10-23T18:15:07Z, 2026-10-23T18:15:09Z, 2026-10-23T18:15:10Z, 2026-10-23T18:15:11Z, 2026-10-23T18:15:12Z, 2026-10-23T18:15:14Z, 2026-10-23T18:15:15Z, 2026-10-23T18:15:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-08T14:56:58Z | 0 |

### `doe_useer_employment`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3311.

- **Source:** doe:useer_2026_public_data U.S. Department of Energy, U.S. Energy and Employment Report (https://www.energy.gov/policy/us-energy-employment-jobs-report-useer)
- **Method note:** [`docs/methods/doe_useer_employment.md`](../methods/doe_useer_employment.md)
- **Cite as:** U.S. Department of Energy (DOE). U.S. Energy and Employment Report 2026 (Office of Energy Jobs), public data. Via the Energy Research Warehouse (ERW), table `doe_useer_employment`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example useer2026:PR_VI:ee:advanced_materials:total, useer2026:PR_VI:ee:certified_and_efficient_lighting:total, useer2026:PR_VI:ee:high_efficiency_hvac_and_renewable_heating_and_cooling:total; 3229 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2633128.0600793697; 3272 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 36 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3311 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Advanced Natural Gas, 2024 Employment Total, Advanced Natural Gas, 2025 Employment Total, Advanced Natural Gas, Construction (NAICS 23); 3269 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:useer_2026_public_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/documents/2026-useer-public-data | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:04:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-02T15:54:14Z | 0 |
| `x_sector` | not yet written |  | text | all, ee, epg, fuels, mvcp, storage, td, tds | 0 |
| `x_subsector` | not yet written |  | text | for example advanced_building_materials_insulation, advanced_materials, advanced_natural_gas; 102 distinct | 0 |
| `x_industry` | not yet written |  | text | agriculture, commodity_flows, construction, manufacturing, mining, other_services, pipeline, pipeline_and_commodity_flows, professional_services, total, trade, utilities | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `employment` |  | count | 3311 | 2024-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

