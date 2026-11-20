# Codebook: doe

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (1 entities, 2 events, 2 series; tiers: 5 source); 5 documented in full.

- [`doe_grip_selections`](#doe_grip_selections): One project selected in the first two rounds of DOE's Grid Resilience and Innovation Partnerships (GRIP) program, as the Office of Electricity's GRIP Program Projects page lists it.
- [`doe_lead_energy_burden`](#doe_lead_energy_burden): One county's or state's value of one measure of households, income or energy cost for one income bracket (a share of area median income), from DOE's LEAD Tool 2022 update, summed by the ERW from LEAD's cells.
- [`doe_lng_export_applications`](#doe_lng_export_applications): One application to export natural gas (as LNG, CNG or CGL) in DOE's Summary of LNG Export Applications of the Lower 48 States, with its FTA and non-FTA parts.
- [`doe_oe417_events`](#doe_oe417_events): One report of an electric emergency incident or disturbance in DOE's yearly summaries of Form DOE-417 (formerly OE-417), 2016 to 2025; DOE's summaries can list one event under several reports.
- [`doe_useer_employment`](#doe_useer_employment): One count of energy workers in 2025 (or 2024's national total) for one place, sector, technology and industry, from DOE's 2026 U.S. Energy and Employment Report (USEER) public data.

### `doe_grip_selections`

One project selected in the first two rounds of DOE's Grid Resilience and Innovation Partnerships (GRIP) program, as the Office of Electricity's GRIP Program Projects page lists it.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 105.

- **Time:** No time column; event_date is the round's announcement date for the program, as the program's page prints it.
- **Revisions:** A snapshot, written whole each run, all four pages asked fresh; no vintage column.
- **Source:** doe:grip_selections U.S. Department of Energy, Office of Electricity, GRIP Program Projects (https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects)
- **Method note:** [`docs/methods/doe_grip_selections.md`](../methods/doe_grip_selections.md)
- **Cite as:** U.S. Department of Energy (DOE). Grid Resilience and Innovation Partnerships (GRIP) Program Projects (Office of Electricity). Via the Energy Research Warehouse (ERW), table `doe_grip_selections`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: doe_grip:<round>:<12 hex of the SHA-1 of program\|applicant\|project>, the ERW's own (DOE gives none) | none | text | for example doe_grip:first:0ab9829b115d, doe_grip:first:0d5c5da6f61c, doe_grip:first:0da2c3abc8a7; 105 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2023-10-18, 2024-08-06, 2024-10-18 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: Always grip_selection | none | text | grip_selection | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The applicant or selectee | none | text | for example Alaska Energy Authority, Algonquin Power Fund America Inc., Allete Inc.; 100 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 105 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 105 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 105 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 105 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: DOE's status, lower-cased: awarded, selected or withdrawn | none | text | awarded, selected, withdrawn | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:grip_selections | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:08:05Z | 0 |
| `x_project` | The project's title as DOE lists it (the source's name: Project) | none | text | for example AEP Advance Distribution Management System and Distributed Energy Resource Management System (ADMS &amp; DERMS) Initiative, AI Grid-Enabled Transportation Electrification in America’s Automotive Heartland, Accelerating Building Thermal Electrification While Managing System Impacts; 105 distinct | 0 |
| `x_program` | The GRIP program: Grid Resilience Utility and Industry Grants, Smart Grid Grants or Grid Innovation Program (the source's name: program) | none | text | Grid Innovation Program, Grid Resilience Utility and Industry Grants, Smart Grid Grants | 0 |
| `x_round` | The selection round: first or second (the source's name: Round) | none | text | first, second | 0 |
| `x_federal_usd` | The federal cost share (the source's name: Federal Cost Share) | USD | integer | 1116174 to 700000000; 90 distinct | 0 |
| `x_recipient_usd` | The recipient's cost share (the source's name: Recipient Cost Share) | USD | integer | 1116174 to 3209440351; 104 distinct | 0 |
| `x_states` | The postal codes of the project's states, joined by ';' (the source's name: Locations) | none | text | for example AK, AL, AL;GA;KY;MO;MS;NC;TN;VA; 65 distinct | 0 |
| `x_state_names` | DOE's names of the project's states, as listed (the source's name: StateFull) | none | text | for example Alabama, Alabama, Georgia, Kentucky, Missouri, Mississippi, North Carolina, Tennessee, Virginia, Alaska; 65 distinct | 0 |
| `x_announced_on` | The round's announcement date for the program (the same as event_date) | none | date | 2023-10-18, 2024-08-06, 2024-10-18 | 0 |
| `x_dates_from` | The program page the announcement date was read from | none | text | https://www.energy.gov/oe/grid-innovation-program, https://www.energy.gov/oe/grid-resilience-utility-and-industry-grants, https://www.energy.gov/oe/smart-grid-grants | 0 |

### `doe_lead_energy_burden`

One county's or state's value of one measure of households, income or energy cost for one income bracket (a share of area median income), from DOE's LEAD Tool 2022 update, summed by the ERW from LEAD's cells.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 160419.

- **Time:** ts_utc is 2022-01-01, the year the files name (a year, not an instant); freq P1Y.
- **Revisions:** Each write replaces the table whole from the saved zips; a zip already saved is never asked again. vintage is the state zip's retrieval time, not its Last-Modified.
- **Source:** doe:lead_2022 DOE, LEAD Tool 2022 Update (https://data.openei.org/submissions/6219)
- **Method note:** [`docs/methods/doe_lead_energy_burden.md`](../methods/doe_lead_energy_burden.md)
- **Cite as:** U.S. Department of Energy (DOE). Low-Income Energy Affordability Data (LEAD Tool), 2022 Update. Via the Energy Research Warehouse (ERW), table `doe_lead_energy_burden`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: doe_lead:<county FIPS> or doe_lead:<state postal code> | none | text | for example doe_lead:10001, doe_lead:10003, doe_lead:10005; 3274 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 13749689.8385; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> (a county's row names its state) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 160419 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The county's name as LEAD writes it, or the state's postal code; not a pricing node | none | text | for example AK, AL, AR; 2012 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:lead_2022 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://data.openei.org/files/6219/AK-2022-LEAD-data.zip, https://data.openei.org/files/6219/AL-2022-LEAD-data.zip, https://data.openei.org/files/6219/AR-2022-LEAD-data.zip; 52 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:59:10Z to 2026-10-24T00:10:31Z; 52 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The state zip's retrieval time (UTC), the same as retrieved_at, not the publisher's Last-Modified | none | utc time | 2026-10-23T23:59:10Z to 2026-10-24T00:10:31Z; 52 distinct | 0 |
| `x_level` | Whether the row is a county or a state | none | text | county, state | 0 |
| `x_bracket` | The income bracket as LEAD writes it: household income as a percent of area median income (0-30%, 30-60%, 60-80%, 80-100%, 100-150%, 150%+), or all (the source's name: AMI150) | none | text | 0-30%, 100-150%, 150%+, 30-60%, 60-80%, 80-100%, all | 0 |
| `x_fips` | The county's FIPS code (LEAD's FIP), or on a state row the state's FIPS code (LEAD's STATE), leading zeros dropped (the source's name: FIP; STATE) | none | integer | 1 to 72153; 3274 distinct | 0 |
| `x_file` | The name of the LEAD CSV file the row was summed from | none | text | for example AK AMI Counties 2022.csv, AL AMI Counties 2022.csv, AR AMI Counties 2022.csv; 52 distinct | 0 |

Variables (49):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_cost_avg:ami_0_30` | Average household electricity cost a year, households at 0 to 30 percent of area median income, USD | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_100_150` | Average household electricity cost a year, households at 100 to 150 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_150_up` | Average household electricity cost a year, households at 150 percent of area median income or more, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_30_60` | Average household electricity cost a year, households at 30 to 60 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_60_80` | Average household electricity cost a year, households at 60 to 80 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_80_100` | Average household electricity cost a year, households at 80 to 100 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `electricity_cost_avg:ami_all` | Average household electricity cost a year, all households, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_0_30` | Energy burden: average energy cost as a percent of average income, households at 0 to 30 percent of area median income (computed by the ERW) | pct | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_100_150` | Energy burden: average energy cost as a percent of average income, households at 100 to 150 percent of area median income (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_150_up` | Energy burden: average energy cost as a percent of average income, households at 150 percent of area median income or more (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_30_60` | Energy burden: average energy cost as a percent of average income, households at 30 to 60 percent of area median income (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_60_80` | Energy burden: average energy cost as a percent of average income, households at 60 to 80 percent of area median income (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_80_100` | Energy burden: average energy cost as a percent of average income, households at 80 to 100 percent of area median income (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_burden:ami_all` | Energy burden: average energy cost as a percent of average income, all households (computed by the ERW) | pct | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_0_30` | Average household energy cost a year (electricity, gas and other fuels added), households at 0 to 30 percent of area median income, USD | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_100_150` | Average household energy cost a year (electricity, gas and other fuels added), households at 100 to 150 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_150_up` | Average household energy cost a year (electricity, gas and other fuels added), households at 150 percent of area median income or more, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_30_60` | Average household energy cost a year (electricity, gas and other fuels added), households at 30 to 60 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_60_80` | Average household energy cost a year (electricity, gas and other fuels added), households at 60 to 80 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_80_100` | Average household energy cost a year (electricity, gas and other fuels added), households at 80 to 100 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `energy_cost_avg:ami_all` | Average household energy cost a year (electricity, gas and other fuels added), all households, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_0_30` | Average household gas cost a year, households at 0 to 30 percent of area median income, USD | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_100_150` | Average household gas cost a year, households at 100 to 150 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_150_up` | Average household gas cost a year, households at 150 percent of area median income or more, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_30_60` | Average household gas cost a year, households at 30 to 60 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_60_80` | Average household gas cost a year, households at 60 to 80 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_80_100` | Average household gas cost a year, households at 80 to 100 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gas_cost_avg:ami_all` | Average household gas cost a year, all households, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_0_30` | Households with income 0 to 30 percent of area median income (the sum of LEAD's weighted UNITS) | count | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_100_150` | Households with income 100 to 150 percent of area median income (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_150_up` | Households with income 150 percent of area median income or more (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_30_60` | Households with income 30 to 60 percent of area median income (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_60_80` | Households with income 60 to 80 percent of area median income (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_80_100` | Households with income 80 to 100 percent of area median income (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `households:ami_all` | All households (the sum of LEAD's weighted UNITS) | count | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_0_30` | Average household income a year, households at 0 to 30 percent of area median income, USD | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_100_150` | Average household income a year, households at 100 to 150 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_150_up` | Average household income a year, households at 150 percent of area median income or more, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_30_60` | Average household income a year, households at 30 to 60 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_60_80` | Average household income a year, households at 60 to 80 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_80_100` | Average household income a year, households at 80 to 100 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `income_avg:ami_all` | Average household income a year, all households, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_0_30` | Average household cost of other fuels a year, households at 0 to 30 percent of area median income, USD | USD | 3273 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_100_150` | Average household cost of other fuels a year, households at 100 to 150 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_150_up` | Average household cost of other fuels a year, households at 150 percent of area median income or more, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_30_60` | Average household cost of other fuels a year, households at 30 to 60 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_60_80` | Average household cost of other fuels a year, households at 60 to 80 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_80_100` | Average household cost of other fuels a year, households at 80 to 100 percent of area median income, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `other_fuel_cost_avg:ami_all` | Average household cost of other fuels a year, all households, USD | USD | 3274 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `doe_lng_export_applications`

One application to export natural gas (as LNG, CNG or CGL) in DOE's Summary of LNG Export Applications of the Lower 48 States, with its FTA and non-FTA parts.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 135.

- **Time:** No time column; status_date is the summary's date (as of 30 September 2026).
- **Revisions:** A snapshot, written whole each run, so an application the Department drops leaves the table; no vintage column.
- **Source:** doe:lng_export_applications U.S. Department of Energy, Hydrocarbons and Geothermal Energy Office, Summary of LNG Export Applications of the Lower 48 States (https://www.energy.gov/fecm/articles/summary-lng-export-applications-lower-48-states)
- **Method note:** [`docs/methods/doe_lng_export_applications.md`](../methods/doe_lng_export_applications.md)
- **Cite as:** U.S. Department of Energy (DOE). Summary of LNG Export Applications of the Lower 48 States (Hydrocarbons and Geothermal Energy Office). Via the Energy Research Warehouse (ERW), table `doe_lng_export_applications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: doe_lng:<docket>, the row's FTA docket, else its non-FTA docket | none | text | for example doe_lng:10-160-LNG, doe_lng:10-85-LNG, doe_lng:11-115-LNG; 135 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The applicant as printed | none | text | for example Accel LNG Energy Llc, Advanced Energy Solutions, L.L.C., Air Flow North America Corp.; 112 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 135 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 135 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 135 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 135 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The ERW's: active when either part is approved, planned when a part is under review or in abeyance and none approved, withdrawn otherwise | none | text | active, planned, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The summary's date | none | date | 2026-09-30 | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 135 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:lng_export_applications | 0 |
| `x_section` | Which of the summary's three tables the row is in: lower48 (Lower-48 applications), canada_mexico (US gas exported as LNG from Canada and Mexico) or small_scale | none | text | canada_mexico, lower48, small_scale | 0 |
| `x_quantity_as_published` | The quantity cell's text as printed | none | text | for example 0.002 Bcf/d, 0.003 Bcf/d, 0.006 Bcf/d; 100 distinct | 0 |
| `x_fta_bcfd` | The quantity applied for to export to free trade agreement (FTA) countries, billion cubic feet a day | Bcf/d | number | 0.003 to 5.13; 76 distinct | 12: The application has no FTA part |
| `x_non_fta_bcfd` | The quantity applied for to export to countries without a free trade agreement (non-FTA), billion cubic feet a day | Bcf/d | number | 0.002 to 5.13; 77 distinct | 20: The application has no non-FTA part |
| `x_fta_status` | The Department's status of the FTA part (Approved, Vacated, Under DOE Review, Withdrawn, Dismissed, n/a) | none | text | Approved, Dismissed, Under DOE Review, Vacated, Withdrawn, n/a | 3: The summary prints no status (3 rows) |
| `x_fta_docket` | The FTA part's DOE docket number | none | text | for example 10-160-LNG, 10-85-LNG, 11-115-LNG; 123 distinct | 12: The application has no FTA docket |
| `x_non_fta_status` | The Department's status of the non-FTA part (Approved, Approved (F), Under DOE Review, Withdrawn, Expired, Vacated, Vacated (F), Dismissed, In Abeyance, n/a) | none | text | Approved, Approved (F), Dismissed, Expired, In Abeyance, Under DOE Review, Vacated, Vacated (F), Withdrawn, n/a | 1: The summary prints no status (1 row) |
| `x_non_fta_docket` | The non-FTA part's DOE docket number | none | text | for example 10-111-LNG, 10-161-LNG, 11-128-LNG; 115 distinct | 20: The application has no non-FTA docket |
| `x_nepa_pending` | yes where the summary marks the application with its '*': waiting for its NEPA (environmental) review | none | text | yes | 123: Not marked |
| `x_footnotes` | The footnote markers printed beside the name, joined by ';' | none | empty | no cell holds a value | 135: Every row: in this edition every marker is 7-point text, which the reader drops |
| `x_as_of` | The date the summary is as of | none | date | 2026-09-30 | 0 |
| `x_page` | The PDF page the row was read from | none | integer | 1, 14, 15, 16, 2, 3, 4, 5, 6 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/sites/default/files/2026-09/Summary%20of%20LNG%20Export%20Applications_9.30.26_1.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:41:41Z | 0 |

### `doe_oe417_events`

One report of an electric emergency incident or disturbance in DOE's yearly summaries of Form DOE-417 (formerly OE-417), 2016 to 2025; DOE's summaries can list one event under several reports.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 3313.

- **Time:** No time column; event_date is the day the event began. Days and times in the x_ columns are local as printed (the summaries name no zone).
- **Revisions:** Built whole and replaced each run; a year's workbook already saved is reused, so a revision is not read until the raw file is gone. vintage is the workbooks' Last-Modified.
- **Source:** doe:oe417 U.S. Department of Energy, DOE-417 Annual Summaries (https://doe417.pnnl.gov/)
- **Method note:** [`docs/methods/doe_oe417_events.md`](../methods/doe_oe417_events.md)
- **Cite as:** U.S. Department of Energy (DOE). Office of Cybersecurity, Energy Security, and Emergency Response (CESER), Electric Emergency Incident and Disturbance Reports (Form DOE-417): Annual Summaries. Via the Energy Research Warehouse (ERW), table `doe_oe417_events`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: doe417:<year>-<row in the year's summary> | none | text | for example doe417:2016-0001, doe417:2016-0002, doe417:2016-0003; 3313 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2016-01-04 to 2025-12-30; 1756 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: The first event type the summary lists, lower case with underscores; not_given where only the comment box's label is listed | none | text | for example actual_physical_attack, actual_physical_attack_vandalism, actual_physical_event; 63 distinct | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 3313 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 3313 |
| `mw` | The capacity involved, in megawatts. Here: The demand lost, where the summary prints a plain number | MW | number | 0.0 to 160000.0; 357 distinct | 1441 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 3313 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 3313 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: restored where a restoration day is printed, else empty | none | text | restored | 694 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:oe417 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://doe417.pnnl.gov/summaries/2016_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2017_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2018_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2019_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2020_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2021_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2022_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2023_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2024_Annual_Summary.xlsx, https://doe417.pnnl.gov/summaries/2025_Annual_Summary.xlsx | 0 |
| `x_year` | The year of the summary the row is in | none | integer | 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |
| `x_row` | The row's number in the year's summary | none | integer | 1 to 622; 622 distinct | 0 |
| `x_begin_date` | The day the event began, as printed, local time | none | date | 2016-01-04 to 2025-12-30; 1756 distinct | 0 |
| `x_begin_time` | The time the event began, as printed, local time (HH:MM) | none | text | for example 00:00, 00:01, 00:02; 1441 distinct | 0 |
| `x_restoration_date` | The day service was restored, or the words as printed (as Unknown) | none | text | for example - Unknown, 2016-01-05, 2016-01-11; 1648 distinct | 363: The summary's cell is empty |
| `x_restoration_time` | The time service was restored, as printed, local time | none | text | for example - Unknown, 00:00, 00:01; 1273 distinct | 363: The summary's cell is empty |
| `x_area_affected` | The area affected, as printed (counties, states or utilities' areas) | none | text | for example Ada County, Idaho, AitkinCounty, Minnesota, Alabama; 1366 distinct | 0 |
| `x_nerc_region` | The NERC reliability region, as printed (not merged: RF and RFC both kept) | none | text | for example FRCC, MPCC, MRO; 32 distinct | 1058: The summary prints no region: every row of 2024 and 2025, 9 of 2023 and 1 of 2016 |
| `x_alert_criteria` | The form's alert criteria the report met, as printed | none | text | for example - 10. Suspected Physical Attack, Actual Physical Attack, Bulk Electric System Emergency resulting in voltage deviation on a Facility; A voltage deviation equal to or greater than 10 percent of nominal voltage sustained for greater than or equal to 15 continuous minutes.; 117 distinct | 0 |
| `x_event_types` | Every event type the row lists, in order, lower case with underscores, joined by '; ' | none | text | for example actual_physical_attack, actual_physical_attack_vandalism, actual_physical_event; 158 distinct | 36: The row lists no type but the form's comment box label (36 rows of 2024 and 2025) |
| `x_event_type_as_published` | The event type cell's words as printed | none | text | for example - Cyber event (information technology), - Failure at high voltage substation or switchyard, - Failure at high voltage substation or switchyard - Other; 211 distinct | 0 |
| `x_demand_loss_mw_as_published` | The demand lost in MW as printed (a number, Unknown or other words) | none | text | for example 0, 0.757, 1; 361 distinct | 135: The summary's cell is empty |
| `x_customers_affected_as_published` | The number of customers affected as printed | none | text | for example 0, 1, 1,031; 830 distinct | 9: The summary's cell is empty |
| `x_customers_affected` | The number of customers affected, where printed as a plain number | count | integer | 0 to 50000000; 786 distinct | 853: Not printed as a plain number (Unknown, a range, words or empty) |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:15:05Z, 2026-10-23T18:15:06Z, 2026-10-23T18:15:07Z, 2026-10-23T18:15:09Z, 2026-10-23T18:15:10Z, 2026-10-23T18:15:11Z, 2026-10-23T18:15:12Z, 2026-10-23T18:15:14Z, 2026-10-23T18:15:15Z, 2026-10-23T18:15:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbooks' Last-Modified time, UTC | none | utc time | 2026-10-08T14:56:58Z | 0 |

### `doe_useer_employment`

One count of energy workers in 2025 (or 2024's national total) for one place, sector, technology and industry, from DOE's 2026 U.S. Energy and Employment Report (USEER) public data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3311.

- **Time:** ts_utc is 1 January of the year (a year, not an instant); freq P1Y.
- **Revisions:** A snapshot of one report, rewritten whole by each run; vintage is the workbook's Last-Modified (2 September 2026). DOE publishes a new report each year at a new address.
- **Source:** doe:useer_2026_public_data U.S. Department of Energy, U.S. Energy and Employment Report (https://www.energy.gov/policy/us-energy-employment-jobs-report-useer)
- **Method note:** [`docs/methods/doe_useer_employment.md`](../methods/doe_useer_employment.md)
- **Cite as:** U.S. Department of Energy (DOE). U.S. Energy and Employment Report 2026 (Office of Energy Jobs), public data. Via the Energy Research Warehouse (ERW), table `doe_useer_employment`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: useer2026:<geo>:<sector>:<subsector>:<industry> | none | text | for example useer2026:PR_VI:ee:advanced_materials:total, useer2026:PR_VI:ee:certified_and_efficient_lighting:total, useer2026:PR_VI:ee:high_efficiency_hvac_and_renewable_heating_and_cooling:total; 3229 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2633128.0600793697; 3272 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US, US-<state>, or empty for USEER's one row of Puerto Rico and the U.S. Virgin Islands | none | text | for example US, US-AK, US-AL; 52 distinct | 36 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3311 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: USEER's row label and column heading (as 'Advanced Natural Gas, 2024 Employment Total'), not a pricing node | none | text | for example Advanced Natural Gas, 2024 Employment Total, Advanced Natural Gas, 2025 Employment Total, Advanced Natural Gas, Construction (NAICS 23); 3269 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:useer_2026_public_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.gov/documents/2026-useer-public-data | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:04:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-02T15:54:14Z | 0 |
| `x_sector` | USEER's sector: fuels, epg (electric power generation), td (transmission and distribution), storage, tds (the state sheet's transmission, distribution and storage), ee (energy efficiency), mvcp (motor vehicles and component parts), or all (the state sheet's employment by industry) | none | text | all, ee, epg, fuels, mvcp, storage, td, tds | 0 |
| `x_subsector` | USEER's technology within the sector (solar, land_based_wind, battery and the others), or total | none | text | for example advanced_building_materials_insulation, advanced_materials, advanced_natural_gas; 102 distinct | 0 |
| `x_industry` | USEER's industry (agriculture, mining, utilities, construction, manufacturing, trade, pipeline, professional_services, other_services and the others), or total | none | text | agriculture, commodity_flows, construction, manufacturing, mining, other_services, pipeline, pipeline_and_commodity_flows, professional_services, total, trade, utilities | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `employment` | USEER's survey estimate of the number of workers, as published | count | 3311 | 2024-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

