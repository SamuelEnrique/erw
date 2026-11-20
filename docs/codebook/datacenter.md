# Codebook: datacenter

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 entities; tiers: 1 derived, 2 model_extracted, 1 source); 0 documented in full.

- [`datacenter_facilities`](#datacenter_facilities): Datacenter facilities from the news, the operators and the ISO queues (the datacenter power tracker, platform tool 4; session 22)
- [`datacenter_operator_sites`](#datacenter_operator_sites): Datacenter sites from the operators' own public lists (session 22)
- [`datacenter_projects`](#datacenter_projects): Datacenter facilities extracted from scored news stories (the datacenter power tracker, platform tool 4)
- [`datacenter_queue_positions`](#datacenter_queue_positions): ISO queue positions that name a datacenter or a large load (session 22)

### `datacenter_facilities`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 458.

- **Method note:** [`docs/methods/datacenter_facilities.md`](../methods/datacenter_facilities.md)
- **Cite as:** ERW. Datacenter facilities: news, operator lists and ISO queues, deduplicated. Via the Energy Research Warehouse (ERW), table `datacenter_facilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 458 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example AI Gigafactory, AWS GovCloud (US), AWS GovCloud (US-East); 303 distinct | 155 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 38 distinct | 180 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 25.775163 to 47.619335; 191 distinct | 227 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.935395 to -71.219029; 189 distinct | 227 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 1.0 to 10400.0; 46 distinct | 400 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, completed, operating, planned, under_construction, withdrawn | 301 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 458 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 5C Data Centers, AWS, AirTrunk; 78 distinct | 59 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | for example Bloomberg, Bloomberg.com, Data Center Dynamics; 26 distinct | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 350 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-15T15:22:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | date | 2026-11-15 | 0 |
| `kind` | not yet written |  | text | news, operator, queue | 0 |
| `kinds` | not yet written |  | text | news, operator, operator;news, queue | 0 |
| `site_type` | not yet written |  | text | announced_site, campus, facility, queue_position, region | 191 |
| `developer` | not yet written |  | text | for example AEP, AIB Data Centers, AdaniConneX; 69 distinct | 379 |
| `state` | not yet written |  | text | for example AK, AL, AR; 38 distinct | 180 |
| `county` | not yet written |  | text | for example Ada County, Armstrong County, Berkeley County; 30 distinct | 427 |
| `city` | not yet written |  | text | for example (Bldg D) Ashburn, (Bldg M) Ashburn, Aiken; 163 distinct | 207 |
| `country` | not yet written |  | text | US | 180 |
| `mw` | The capacity involved, in megawatts | MW | number | 1.0 to 10400.0; 46 distinct | 400 |
| `mw_span` | not yet written |  | text | up to 150 MW of power, up to 237 MW of power, up to 495 MW of power | 455 |
| `mw_from` | not yet written |  | text | for example news:datacenter:0403e02384dfcae9, news:datacenter:05e72e9231b9523b, news:datacenter:0b769e9a81932dac; 58 distinct | 400 |
| `queue_mw` | not yet written |  | number | 0.0, 133.0, 58.26 | 455 |
| `project_status` | not yet written |  | text | "inDevelopment": false, "inDevelopment": true, Active, Completed, Live, Withdrawn, announced, applied, cancelled, operating, permitted, under_construction | 301 |
| `phase` | not yet written |  | text | First, First building, First phase, First project, Second building, first 222MW, first data center, first phase, fourth data center, second 500MW phase, second building, second data center, third facility | 443 |
| `planned_year` | not yet written |  | integer | 2026, 2028, 2029, 2030 | 449 |
| `power_source` | not yet written |  | text | SMR, behind-the-meter, combined cycle turbines, distributed virtual power plant, fuel cell, fuel cells, gas, gas plants, gas power plant, gas turbines, gas-fired, gas-powered, gas-powered fuel cells, geothermal, multi-gigawatt centralized natural gas generation, natural gas, off-grid, solar panels, tidal energy | 434 |
| `utility` | not yet written |  | text | AEP, American Electric Power, Blue Whale Energy, Entergy Arkansas, FirstEnergy, NiSource, OGE Energy, WEC Energy | 450 |
| `confidence` | not yet written |  | number | 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.88, 0.9 | 265 |
| `first_story_at` | not yet written |  | utc time | 2025-01-07T08:00:00Z to 2026-11-12T17:10:30Z; 185 distinct | 265 |
| `geo_precision` | not yet written |  | text | county, none, operator, place | 0 |
| `geo_note` | not yet written |  | text | for example city 'Henrico' not a unique place in the gazetteer for VA, city 'North Bergen' not a unique place in the gazetteer for NJ, city 'Sarpy' not a unique place in the gazetteer for NE; 116 distinct | 0 |
| `n_members` | not yet written |  | integer | 1, 2 | 0 |
| `member_ids` | not yet written |  | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 458 distinct | 0 |
| `source_urls` | not yet written |  | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 352 distinct | 0 |
| `grid` | not yet written |  | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 280 |
| `grid_basis` | not yet written |  | text | queue, state | 280 |
| `mw_basis` | not yet written |  | text | tenant, total, unstated | 400 |
| `power_kind` | not yet written |  | text | behind_the_meter, behind_the_meter_gas, gas, nuclear, other, renewables_storage | 434 |
| `energized_year` | not yet written |  | empty | no cell holds a value | 458 |
| `utility_eia861` | not yet written |  | empty | no cell holds a value | 458 |
| `utility_eia861_number` | not yet written |  | empty | no cell holds a value | 458 |
| `utilities_in_county` | not yet written |  | empty | no cell holds a value | 458 |

### `datacenter_operator_sites`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 264.

- **Method note:** [`docs/methods/datacenter_operator_sites.md`](../methods/datacenter_operator_sites.md)
- **Cite as:** Amazon Web Services; Digital Realty; Equinix; Google; Meta; Microsoft; Oracle; Switch; Vantage Data Centers. Amazon Web Services public list of data center sites and regions; Digital Realty public list of data center sites and regions; Equinix public list of data center sites and regions; Google public list of data center sites and regions; Meta public list of data center sites and regions; Microsoft public list of data center sites and regions; Oracle public list of data center sites and regions; Switch public list of data center sites and regions; Vantage Data Centers public list of data center sites and regions. Via the Energy Research Warehouse (ERW), table `datacenter_operator_sites`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example dcsite:00143eafee858942, dcsite:0083759d2bd5cba7, dcsite:0099eabf0dc05dc8; 264 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example AWS GovCloud (US), AWS GovCloud (US-East), Azure Georgia (announced); 264 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AL, US-AR; 34 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 25.775163 to 47.619335; 160 distinct | 67 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.91838 to -71.219029; 158 distinct | 67 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | integer | 150, 237, 495 | 261 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned | 216 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 264 |
| `operator` | The operator or owner, as the publisher writes it | none | text | Amazon Web Services, Digital Realty, Equinix, Google, Meta, Microsoft, Oracle, Switch | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | aws:locations, digitalrealty:data-centers, equinix:us-data-centers, google:datacenter-locations, meta:datacenter-locations, microsoft:azure-geographies, oracle:public-cloud-regions, switch:locations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 159 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:26:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | integer | 20261105 | 0 |
| `kind` | not yet written |  | text | operator | 0 |
| `site_type` | not yet written |  | text | announced_site, campus, facility, region | 0 |
| `operator_code` | not yet written |  | text | for example ACC4, ACC5, ACC6; 165 distinct | 96 |
| `place_text` | not yet written |  | text | for example ACC4 44480 Hastings Drive Ashburn, VA 20147, ACC5 44521 Hastings Drive, Ashburn, VA 20147, ACC6 44461 Chilum Place Ashburn, VA 20147; 250 distinct | 0 |
| `state` | not yet written |  | text | for example AL, AR, AZ; 33 distinct | 54 |
| `county` | not yet written |  | text | Armstrong County, Berkeley County, Chesterfield County, Columbia County, Dorchester County, Douglas County, Jackson County, Loudoun County, Mayes County, Montgomery County, Morgan County, Muskogee County, Prince William County, Richland Parish, Storey County, Wilbarger County | 248 |
| `city` | not yet written |  | text | for example (Bldg D) Ashburn, (Bldg M) Ashburn, Aiken; 101 distinct | 89 |
| `mw` | The capacity involved, in megawatts | MW | integer | 150, 237, 495 | 261 |
| `mw_span` | not yet written |  | text | up to 150 MW of power, up to 237 MW of power, up to 495 MW of power | 261 |
| `status_text` | not yet written |  | text | "inDevelopment": false, "inDevelopment": true, Live | 216 |
| `detail` | not yet written |  | text | for example $1 billion+ investment; 2017 break ground; 1,500 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed, $1 billion+ investment; 2020 break ground; 1,200 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed, $1 billion+ investment; 2021 break ground; 2,000 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed; 54 distinct | 81 |
| `geo_precision` | not yet written |  | text | county, none, operator, place | 0 |
| `geo_note` | not yet written |  | text | for example city 'Henrico' not a unique place in the gazetteer for VA, city 'North Bergen' not a unique place in the gazetteer for NJ, city 'Sarpy' not a unique place in the gazetteer for NE; 87 distinct | 0 |

### `datacenter_projects`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 193.

- **Method note:** [`docs/methods/datacenter_projects.md`](../methods/datacenter_projects.md)
- **Cite as:** Bloomberg; Bloomberg.com; Data Center Dynamics; Data Center Frontier; Data Center Knowledge; Energy-Storage.news; Financial Times; Hart Energy; Heatmap News; Latitude Media; Natural Gas Intelligence; OilPrice.com; POWER Magazine; Reuters; U.S. Census Bureau; Utility Dive; WSJ. Gazetteer Files, counties (2025), county internal points; news stories; news stories via feed 'Bloomberg energy (via Google News)'; news stories via feed 'Data Center Frontier'; news stories via feed 'Data Center Knowledge'; news stories via feed 'Energy-Storage.news'; news stories via feed 'FT energy (via Google News)'; news stories via feed 'Hart Energy'; news stories via feed 'Latitude Media'; news stories via feed 'Natural Gas Intelligence'; news stories via feed 'POWER Magazine'; news stories via feed 'Reuters energy (via Google News)'; news stories via feed 'Utility Dive'; news stories via feed 'WSJ energy (via Google News)'. Via the Energy Research Warehouse (ERW), table `datacenter_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 193 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example AI Gigafactory, BCN1, Barber Lake; 34 distinct | 159 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 28 distinct | 126 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 26.481861 to 46.004354; 32 distinct | 160 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.935395 to -75.976053; 32 distinct | 160 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 1.0 to 10400.0; 44 distinct | 138 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned, under_construction, withdrawn | 87 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 193 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 5C Data Centers, AWS, AirTrunk; 74 distinct | 59 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | Bloomberg, Bloomberg.com, Data Center Dynamics, Data Center Frontier, Data Center Knowledge, Energy-Storage.news, Financial Times, Hart Energy, Heatmap News, Latitude Media, Natural Gas Intelligence, OilPrice.com, POWER Magazine, Reuters, Utility Dive, WSJ | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://heatmap.news/plus/the-fight/hotspots/arevia-idaho-solar-data-center, https://heatmap.news/plus/the-fight/spotlight/data-centers-ocean, https://heatmap.news/plus/the-fight/spotlight/the-most-important-data-center-election-youve-never-heard-of; 191 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T04:31:06Z, 2026-09-27T09:18:19Z, 2026-09-28T06:02:33Z, 2026-09-28T21:02:35Z, 2026-09-30T19:57:49Z, 2026-10-02T00:10:33Z, 2026-10-03T14:45:35Z, 2026-10-05T15:07:56Z, 2026-10-06T14:44:47Z, 2026-10-07T14:44:14Z, 2026-10-08T15:01:50Z, 2026-10-09T14:55:04Z, 2026-10-13T15:00:43Z, 2026-10-14T15:35:43Z, 2026-10-15T15:43:54Z, 2026-10-19T16:23:27Z, 2026-10-20T01:01:28Z, 2026-10-21T15:09:05Z, 2026-10-22T15:02:51Z, 2026-10-23T15:01:58Z, 2026-10-24T15:01:45Z, 2026-10-25T14:53:41Z, 2026-11-05T23:44:06Z, 2026-11-12T11:03:30Z, 2026-11-12T22:09:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 193 |
| `kind` | not yet written |  | text | datacenter | 0 |
| `developer` | not yet written |  | text | for example AEP, AIB Data Centers, AdaniConneX; 69 distinct | 114 |
| `site_name` | not yet written |  | text | for example AI Gigafactory, BCN1, Barber Lake; 37 distinct | 156 |
| `state` | not yet written |  | text | for example AK, AL, AR; 28 distinct | 126 |
| `county` | not yet written |  | text | Ada County, Effingham County, Indiana County, Licking County, Lowndes County, Luzerne County, Mason County, McCracken County, Montgomery County, Posey County, Roanoke County, Willacy | 181 |
| `city` | not yet written |  | text | for example Amarillo, Ansan, Ashburn; 73 distinct | 115 |
| `mw` | The capacity involved, in megawatts | MW | number | 1.0 to 10400.0; 44 distinct | 138 |
| `phase` | not yet written |  | text | First, First building, First phase, First project, Second building, first 222MW, first data center, first phase, fourth data center, second 500MW phase, second building, second data center, third facility | 178 |
| `project_status` | not yet written |  | text | announced, applied, cancelled, operating, permitted, under_construction | 87 |
| `planned_year` | not yet written |  | integer | 2026, 2028, 2029, 2030 | 184 |
| `power_source` | not yet written |  | text | SMR, behind-the-meter, combined cycle turbines, distributed virtual power plant, fuel cell, fuel cells, gas, gas plants, gas power plant, gas turbines, gas-fired, gas-powered, gas-powered fuel cells, geothermal, multi-gigawatt centralized natural gas generation, natural gas, off-grid, solar panels, tidal energy | 169 |
| `utility` | not yet written |  | text | AEP, American Electric Power, Blue Whale Energy, Entergy Arkansas, FirstEnergy, NiSource, OGE Energy, WEC Energy | 185 |
| `ai_power` | not yet written |  | boolean | True, true | 0 |
| `confidence` | not yet written |  | number | 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.88, 0.9 | 0 |
| `geo_precision` | not yet written |  | text | county, none, place | 0 |
| `geo_note` | not yet written |  | text | for example city 'Swansea' not a unique place in the gazetteer for MA, county Ada County (2025_Gaz_counties_national.txt), county Effingham County (2025_Gaz_counties_national.txt); 35 distinct | 0 |
| `first_story_at` | not yet written |  | utc time | 2025-01-07T08:00:00Z to 2026-11-12T17:10:30Z; 185 distinct | 0 |
| `n_stories` | not yet written |  | integer | 1, 2, 3, 4, 6 | 0 |
| `story_ids` | not yet written |  | text | for example news:002bc7ebc5774cab, news:015878c3647dbba9;news:28fe08f50e09de14, news:015eda2d18115a8b; 191 distinct | 0 |
| `story_urls` | not yet written |  | text | for example https://heatmap.news/plus/the-fight/hotspots/arevia-idaho-solar-data-center, https://heatmap.news/plus/the-fight/spotlight/data-centers-ocean, https://heatmap.news/plus/the-fight/spotlight/the-most-important-data-center-election-youve-never-heard-of; 191 distinct | 0 |
| `model_id` | not yet written |  | text | claude-sonnet-5, claude-sonnet-5-5 | 0 |
| `extracted_at` | not yet written |  | utc time | 2026-09-27T04:31:06Z, 2026-09-27T09:18:19Z, 2026-09-28T06:02:33Z, 2026-09-28T21:02:35Z, 2026-09-30T19:57:49Z, 2026-10-02T00:10:33Z, 2026-10-03T14:45:35Z, 2026-10-05T15:07:56Z, 2026-10-06T14:44:47Z, 2026-10-07T14:44:14Z, 2026-10-08T15:01:50Z, 2026-10-09T14:55:04Z, 2026-10-13T15:00:43Z, 2026-10-14T15:35:43Z, 2026-10-15T15:43:54Z, 2026-10-19T16:23:27Z, 2026-10-20T01:01:28Z, 2026-10-21T15:09:05Z, 2026-10-22T15:02:51Z, 2026-10-23T15:01:58Z, 2026-10-24T15:01:45Z, 2026-10-25T14:53:41Z, 2026-11-05T23:44:06Z, 2026-11-12T11:03:30Z, 2026-11-12T22:09:20Z | 0 |
| `mw_basis` | not yet written |  | text | tenant, total, unstated | 138 |
| `power_kind` | not yet written |  | text | behind_the_meter, behind_the_meter_gas, gas, nuclear, other, renewables_storage | 169 |
| `grid` | not yet written |  | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 155 |
| `grid_basis` | not yet written |  | text | state | 155 |
| `utility_eia861` | not yet written |  | empty | no cell holds a value | 193 |
| `utility_eia861_number` | not yet written |  | empty | no cell holds a value | 193 |
| `utilities_in_county` | not yet written |  | empty | no cell holds a value | 193 |
| `energized_year` | not yet written |  | empty | no cell holds a value | 193 |
| `country` | not yet written |  | text | Australia, Denmark, Finland, Germany, India, Singapore, South Korea, UK | 180 |
| `fields_version` | not yet written |  | text | 2236, upgraded | 0 |

### `datacenter_queue_positions`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 3.

- **Method note:** [`docs/methods/datacenter_facilities.md`](../methods/datacenter_facilities.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT); New York Independent System Operator (NYISO). Generation Interconnection Status (GIS) report; NYISO Interconnection Queue. Via the Energy Research Warehouse (ERW), table `datacenter_queue_positions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | ercot_queue:25INR0688, ercot_queue:28INR0499, nyiso_queue:1630 | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | Alpha Digital Campus Combined-cycle and Co-located Load, Giga Texas Data Center, Suffern Quarry Data Center | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY, US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.0, 133.0, 58.26 | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2023-12-31 | 2 |
| `operator` | The operator or owner, as the publisher writes it | none | text | Giga Texas Energy, LLC, Orange & Rockland, PowerBridge LLC | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:interconnection_queue, nyiso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078, https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:50Z, 2026-11-05T23:21:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026-09-26T00:00:00Z, 2026-11-05 | 0 |
| `queue_id` | not yet written |  | text | 1630, 25INR0688, 28INR0499 | 0 |
| `county` | not yet written |  | text | Reeves, Rockland, Travis | 0 |
| `state` | not yet written |  | text | NY, TX | 0 |
| `poi` | not yet written |  | text | 38044 TNCOWPEN__3 345kV, HORNSBY Substation POIB# 7047   Site will be connected behind the meter at Medium Voltage  24.9 kV with non export controls  GSU TRANSFORMER 80/106/133MVA 345kV DELTA PRIMARY 24.9kV WYE-G SECONDARY Z=XX%, 65DEG C RISE, We anticipate a new substation being built on our site off of a transmission line tower that abuts our property. Additionally, we may need to tie in for redundancy to the Hillburn Area Substation | 0 |
| `zone` | not yet written |  | text | G | 2 |
| `transmission_owner` | not yet written |  | text | O&R | 2 |
| `fuel_technology` | not yet written |  | text | Gas - Combined-Cycle, Other - Battery Energy Storage | 1 |
| `iso_status` | not yet written |  | text | Active, Completed, Withdrawn | 0 |
| `queue_date` | not yet written |  | date | 2023-11-03, 2024-08-27, 2026-04-28 | 0 |
| `proposed_in_service_date` | not yet written |  | date | 2027-08-13, 2027-12-31 | 1 |
| `actual_in_service_date` | not yet written |  | empty | no cell holds a value | 3 |
| `withdrawn_date` | not yet written |  | date | 2023-12-31 | 2 |
| `matched` | not yet written |  | text | Data Center, Digital Campus | 0 |

