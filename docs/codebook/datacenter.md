# Codebook: datacenter

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 entities; tiers: 1 derived, 2 model_extracted, 1 source); 4 documented in full.

- [`datacenter_facilities`](#datacenter_facilities): One datacenter facility the ERW knows of, joined from three kinds of source (news stories, the operators' own lists, the ISO interconnection queues) with duplicates removed by operator plus location (the datacenter power tracker, platform tool 4).
- [`datacenter_operator_sites`](#datacenter_operator_sites): One datacenter site (a region, campus, facility or announced site) on one of nine operators' own public lists (AWS, Microsoft, Google, Meta, Oracle, Digital Realty, Equinix, Vantage, Switch).
- [`datacenter_projects`](#datacenter_projects): One datacenter facility that scored news stories name (a named site, or a named operator or developer at a stated place), extracted by a model and checked against the stories' words.
- [`datacenter_queue_positions`](#datacenter_queue_positions): One ISO interconnection queue position whose name or fuel field names a datacenter or a large load, copied with the queue table's own columns (ERCOT and NYISO rows in this edition).

### `datacenter_facilities`

One datacenter facility the ERW knows of, joined from three kinds of source (news stories, the operators' own lists, the ISO interconnection queues) with duplicates removed by operator plus location (the datacenter power tracker, platform tool 4).

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 458.

- **Time:** No time column; a snapshot, vintage the build's date (YYYY-MM-DD) and retrieved_at its time in UTC. first_story_at is the UTC time of the first news story.
- **Revisions:** Rewritten whole as a snapshot by each run of the builder (warehouse/derived/datacenter_facilities.py) from its input tables.
- **Method note:** [`docs/methods/datacenter_facilities.md`](../methods/datacenter_facilities.md)
- **Cite as:** ERW. Datacenter facilities: news, operator lists and ISO queues, deduplicated. Via the Energy Research Warehouse (ERW), table `datacenter_facilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 458 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always datacenter | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example AI Gigafactory, AWS GovCloud (US), AWS GovCloud (US-East); 303 distinct | 155 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> where a source states a US state; empty otherwise (no source records a country) | none | text | for example US-AK, US-AL, US-AR; 38 distinct | 180 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 25.775163 to 47.619335; 191 distinct | 227 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.935395 to -71.219029; 189 distinct | 227 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: mw, as a source states it (mw_from names the member) | MW | number | 1.0 to 10400.0; 46 distinct | 400 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: From the news member where there is one (dated), else the operator's stated status; empty where none is stated | none | text | active, completed, operating, planned, under_construction, withdrawn | 301 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 458 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 5C Data Centers, AWS, AirTrunk; 78 distinct | 59 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | for example Bloomberg, Bloomberg.com, Data Center Dynamics; 26 distinct | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 350 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-15T15:22:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The build's date, YYYY-MM-DD | none | date | 2026-11-15 | 0 |
| `kind` | The kind of source of the facility's first member: news, operator or queue | none | text | news, operator, queue | 0 |
| `kinds` | Every member's kind of source, joined by ';' | none | text | news, operator, operator;news, queue | 0 |
| `site_type` | What the operator lists the site as: region, campus, facility, announced_site, or queue_position for a queue row | none | text | announced_site, campus, facility, queue_position, region | 191: A news row: news gives no site type |
| `developer` | The company building or owning the site, as a news story names it | none | text | for example AEP, AIB Data Centers, AdaniConneX; 69 distinct | 379: No member names a developer |
| `state` | The US state, two-letter postal code, where a source names it | none | text | for example AK, AL, AR; 38 distinct | 180: No source names a US state |
| `county` | The county, as a source names it | none | text | for example Ada County, Armstrong County, Berkeley County; 30 distinct | 427: No source names a county |
| `city` | The city or place, as a source names it | none | text | for example (Bldg D) Ashburn, (Bldg M) Ashburn, Aiken; 163 distinct | 207: No source names a city |
| `country` | US where a row states a US state (or the District of Columbia); no source records a country | none | text | US | 180: No US state is stated |
| `mw` | The capacity involved, in megawatts | MW | number | 1.0 to 10400.0; 46 distinct | 400 |
| `mw_span` | The operator page's exact words for the MW (for example 'up to 495 MW of power') | none | text | up to 150 MW of power, up to 237 MW of power, up to 495 MW of power | 455: The MW is not from an operator's page, or no MW is stated |
| `mw_from` | The member the MW comes from, as <kind>:<member id> | none | text | for example news:datacenter:0403e02384dfcae9, news:datacenter:05e72e9231b9523b, news:datacenter:0b769e9a81932dac; 58 distinct | 400: No member states a MW |
| `queue_mw` | A queue position's generation or storage MW: what it asks to connect, not the datacenter's load | MW | number | 0.0, 133.0, 58.26 | 455: Not a queue row |
| `project_status` | The source's own status word (the news extractor's word, Oracle's Live, Google's inDevelopment flag, the queue's status) | none | text | "inDevelopment": false, "inDevelopment": true, Active, Completed, Live, Withdrawn, announced, applied, cancelled, operating, permitted, under_construction | 301: The source states no status |
| `phase` | The phase or building of the facility as a news story states it; a model's extraction, checked against the story | none | text | First, First building, First phase, First project, Second building, first 222MW, first data center, first phase, fourth data center, second 500MW phase, second building, second data center, third facility | 443: Not a news facility, or no phase stated |
| `planned_year` | The year the facility or phase is planned to start, as a news story states it; a model's extraction, checked against the story | none | integer | 2026, 2028, 2029, 2030 | 449: Not a news facility, or no year stated |
| `power_source` | How the facility will be powered, as a news story states it; a model's extraction, checked against the story | none | text | SMR, behind-the-meter, combined cycle turbines, distributed virtual power plant, fuel cell, fuel cells, gas, gas plants, gas power plant, gas turbines, gas-fired, gas-powered, gas-powered fuel cells, geothermal, multi-gigawatt centralized natural gas generation, natural gas, off-grid, solar panels, tidal energy | 434: Not a news facility, or no power source stated |
| `utility` | The utility or power supplier as a news story names it; a model's extraction, checked against the story | none | text | AEP, American Electric Power, Blue Whale Energy, Entergy Arkansas, FirstEnergy, NiSource, OGE Energy, WEC Energy | 450: Not a news facility, or no utility named |
| `confidence` | The news extractor model's confidence, 0 to 1, that the facility is real and specific and its fields right | none | number | 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.88, 0.9 | 265: Not a news facility |
| `first_story_at` | The time of the first news story naming the facility, UTC | none | utc time | 2025-01-07T08:00:00Z to 2026-11-12T17:10:30Z; 185 distinct | 265: Not a news facility |
| `geo_precision` | How lat and lon were placed: operator (the page's own coordinates), county or place (the Census gazetteer's internal point of the stated county or city), or none | none | text | county, none, operator, place | 0 |
| `geo_note` | Why the row was placed as it was, or not placed (for example a city not unique in the gazetteer) | none | text | for example city 'Henrico' not a unique place in the gazetteer for VA, city 'North Bergen' not a unique place in the gazetteer for NJ, city 'Sarpy' not a unique place in the gazetteer for NE; 116 distinct | 0 |
| `n_members` | The input rows joined into this facility | count | integer | 1, 2 | 0 |
| `member_ids` | The ids of the input rows joined into this facility, joined by ';' | none | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 458 distinct | 0 |
| `source_urls` | Every address the members were read from (stories, operator pages, queue files), joined by ';' | none | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 352 distinct | 0 |
| `grid` | The grid the facility belongs to: the grid its stories name, else its queue's own ISO, else the grid that serves most of its state | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 280: No grid named and no state, or a state split between grids |
| `grid_basis` | How grid was set: named (a story names it), queue (its queue position's ISO) or state (the grid that serves most of its state) | none | text | queue, state | 280: No grid set |
| `mw_basis` | What the stated MW measures, from the member it comes from: it (IT load), total, tenant, phase or unstated | none | text | tenant, total, unstated | 400: No MW stated, or a MW from an operator page |
| `power_kind` | How the facility is powered, read by code from power_source: behind_the_meter_gas, nuclear, renewables_storage, gas, behind_the_meter, grid or other | none | text | behind_the_meter, behind_the_meter_gas, gas, nuclear, other, renewables_storage | 434: No power source stated |
| `energized_year` | The year the facility or its first phase is to be energized, as a news story states it | none | empty | no cell holds a value | 458: Not filled: no cell holds a value |
| `utility_eia861` | The one EIA-861 utility that serves the stated county | none | empty | no cell holds a value | 458: Not filled: no cell holds a value |
| `utility_eia861_number` | That utility's EIA-861 utility number | none | empty | no cell holds a value | 458: Not filled: no cell holds a value |
| `utilities_in_county` | The number of EIA-861 utilities that serve the stated county | count | empty | no cell holds a value | 458: Not filled: no cell holds a value |

### `datacenter_operator_sites`

One datacenter site (a region, campus, facility or announced site) on one of nine operators' own public lists (AWS, Microsoft, Google, Meta, Oracle, Digital Realty, Equinix, Vantage, Switch).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 264.

- **Time:** No time column; one snapshot a run, vintage the run's date (YYYYMMDD) and retrieved_at its time in UTC.
- **Revisions:** Each full run replaces the table (a site an operator no longer lists leaves it); a run with --only replaces only those operators' rows; sites repeated within a run are kept once.
- **Method note:** [`docs/methods/datacenter_operator_sites.md`](../methods/datacenter_operator_sites.md)
- **Cite as:** Amazon Web Services; Digital Realty; Equinix; Google; Meta; Microsoft; Oracle; Switch; Vantage Data Centers. Amazon Web Services public list of data center sites and regions; Digital Realty public list of data center sites and regions; Equinix public list of data center sites and regions; Google public list of data center sites and regions; Meta public list of data center sites and regions; Microsoft public list of data center sites and regions; Oracle public list of data center sites and regions; Switch public list of data center sites and regions; Vantage Data Centers public list of data center sites and regions. Via the Energy Research Warehouse (ERW), table `datacenter_operator_sites`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: dcsite: plus the first 16 hex digits of the SHA-1 of operator\|site_type\|operator_code (the name where there is no code) | none | text | for example dcsite:00143eafee858942, dcsite:0083759d2bd5cba7, dcsite:0099eabf0dc05dc8; 264 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always datacenter | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example AWS GovCloud (US), AWS GovCloud (US-East), Azure Georgia (announced); 264 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US where the page names no state | none | text | for example US, US-AL, US-AR; 34 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 25.775163 to 47.619335; 160 distinct | 67 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.91838 to -71.219029; 158 distinct | 67 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: mw, only where the page states it, with its words in mw_span | MW | integer | 150, 237, 495 | 261 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Only where the page states one: Google's inDevelopment flag, Oracle's Live or Coming soon | none | text | operating, planned | 216 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 264 |
| `operator` | The operator or owner, as the publisher writes it | none | text | Amazon Web Services, Digital Realty, Equinix, Google, Meta, Microsoft, Oracle, Switch | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | aws:locations, digitalrealty:data-centers, equinix:us-data-centers, google:datacenter-locations, meta:datacenter-locations, microsoft:azure-geographies, oracle:public-cloud-regions, switch:locations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/, https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json, https://cloud.google.com/compute/docs/regions-zones; 159 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:26:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The run's date, YYYYMMDD | none | integer | 20261105 | 0 |
| `kind` | Always operator: the row is from an operator's own list | none | text | operator | 0 |
| `site_type` | What the operator lists: region, campus, facility or announced_site | none | text | announced_site, campus, facility, region | 0 |
| `operator_code` | The operator's own code for the site, where its page gives one (for example ACC4) | none | text | for example ACC4, ACC5, ACC6; 165 distinct | 96: The page gives no code (the name keys the row) |
| `place_text` | The page's own words for the place | none | text | for example ACC4 44480 Hastings Drive Ashburn, VA 20147, ACC5 44521 Hastings Drive, Ashburn, VA 20147, ACC6 44461 Chilum Place Ashburn, VA 20147; 250 distinct | 0 |
| `state` | The US state, two-letter postal code, only where the page names it | none | text | for example AL, AR, AZ; 33 distinct | 54: The page names no state (a region named by a direction or a city) |
| `county` | The county, as the page names it | none | text | Armstrong County, Berkeley County, Chesterfield County, Columbia County, Dorchester County, Douglas County, Jackson County, Loudoun County, Mayes County, Montgomery County, Morgan County, Muskogee County, Prince William County, Richland Parish, Storey County, Wilbarger County | 248: The page names no county |
| `city` | The city, as the page names it | none | text | for example (Bldg D) Ashburn, (Bldg M) Ashburn, Aiken; 101 distinct | 89: The page names no city |
| `mw` | The capacity involved, in megawatts | MW | integer | 150, 237, 495 | 261 |
| `mw_span` | The page's exact words for the MW, checked against the page text (Vantage's critical IT load, Switch's power) | none | text | up to 150 MW of power, up to 237 MW of power, up to 495 MW of power | 261: The page states no MW |
| `status_text` | The page's own status words: Oracle's Live or Coming soon, Google's inDevelopment flag | none | text | "inDevelopment": false, "inDevelopment": true, Live | 216: The page states no status |
| `detail` | More words from the page: the location card or sentence (Azure, Meta, Switch) or the metro (Digital Realty, Equinix) | none | text | for example $1 billion+ investment; 2017 break ground; 1,500 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed, $1 billion+ investment; 2020 break ground; 1,200 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed, $1 billion+ investment; 2021 break ground; 2,000 skilled trade workers on site at peak construction; 200+ operational jobs supported once completed; 54 distinct | 81: The connector keeps no more words for that operator |
| `geo_precision` | How lat and lon were placed: operator (the page's coordinates), county or place (the Census gazetteer's internal point of the stated county or city), or none | none | text | county, none, operator, place | 0 |
| `geo_note` | Why the row was placed as it was, or not placed (for example 'no US state stated') | none | text | for example city 'Henrico' not a unique place in the gazetteer for VA, city 'North Bergen' not a unique place in the gazetteer for NJ, city 'Sarpy' not a unique place in the gazetteer for NE; 87 distinct | 0 |

### `datacenter_projects`

One datacenter facility that scored news stories name (a named site, or a named operator or developer at a stated place), extracted by a model and checked against the stories' words.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 193.

- **Time:** No time column; first_story_at is the UTC time of the first story, extracted_at the UTC time of the first extraction.
- **Revisions:** The whole table is rewritten each run from the facilities already extracted and the new stories; vintage is not filled.
- **Method note:** [`docs/methods/datacenter_projects.md`](../methods/datacenter_projects.md)
- **Cite as:** Bloomberg; Bloomberg.com; Data Center Dynamics; Data Center Frontier; Data Center Knowledge; Energy-Storage.news; Financial Times; Hart Energy; Heatmap News; Latitude Media; Natural Gas Intelligence; OilPrice.com; POWER Magazine; Reuters; U.S. Census Bureau; Utility Dive; WSJ. Gazetteer Files, counties (2025), county internal points; news stories; news stories via feed 'Bloomberg energy (via Google News)'; news stories via feed 'Data Center Frontier'; news stories via feed 'Data Center Knowledge'; news stories via feed 'Energy-Storage.news'; news stories via feed 'FT energy (via Google News)'; news stories via feed 'Hart Energy'; news stories via feed 'Latitude Media'; news stories via feed 'Natural Gas Intelligence'; news stories via feed 'POWER Magazine'; news stories via feed 'Reuters energy (via Google News)'; news stories via feed 'Utility Dive'; news stories via feed 'WSJ energy (via Google News)'. Via the Energy Research Warehouse (ERW), table `datacenter_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: datacenter:<16 hex> | none | text | for example datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365, datacenter:05e72e9231b9523b; 193 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always datacenter | none | text | datacenter | 0 |
| `name` | The thing's name, as the publisher writes it. Here: A model's extraction, checked against the story | none | text | for example AI Gigafactory, BCN1, Barber Lake; 34 distinct | 159 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 28 distinct | 126 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 26.481861 to 46.004354; 32 distinct | 160 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -122.935395 to -75.976053; 32 distinct | 160 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: mw, as a story states it | MW | number | 1.0 to 10400.0; 44 distinct | 138 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The extractor's word mapped to the entities vocabulary: announced, applied and permitted to planned, cancelled to withdrawn | none | text | operating, planned, under_construction, withdrawn | 87 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 193 |
| `operator` | The operator or owner, as the publisher writes it. Here: The company that will run or use the datacenter, as a story names it; a model's extraction, checked against the story | none | text | for example 5C Data Centers, AWS, AirTrunk; 74 distinct | 59 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: The outlet of the first story | none | text | Bloomberg, Bloomberg.com, Data Center Dynamics, Data Center Frontier, Data Center Knowledge, Energy-Storage.news, Financial Times, Hart Energy, Heatmap News, Latitude Media, Natural Gas Intelligence, OilPrice.com, POWER Magazine, Reuters, Utility Dive, WSJ | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://heatmap.news/plus/the-fight/hotspots/arevia-idaho-solar-data-center, https://heatmap.news/plus/the-fight/spotlight/data-centers-ocean, https://heatmap.news/plus/the-fight/spotlight/the-most-important-data-center-election-youve-never-heard-of; 191 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T04:31:06Z, 2026-09-27T09:18:19Z, 2026-09-28T06:02:33Z, 2026-09-28T21:02:35Z, 2026-09-30T19:57:49Z, 2026-10-02T00:10:33Z, 2026-10-03T14:45:35Z, 2026-10-05T15:07:56Z, 2026-10-06T14:44:47Z, 2026-10-07T14:44:14Z, 2026-10-08T15:01:50Z, 2026-10-09T14:55:04Z, 2026-10-13T15:00:43Z, 2026-10-14T15:35:43Z, 2026-10-15T15:43:54Z, 2026-10-19T16:23:27Z, 2026-10-20T01:01:28Z, 2026-10-21T15:09:05Z, 2026-10-22T15:02:51Z, 2026-10-23T15:01:58Z, 2026-10-24T15:01:45Z, 2026-10-25T14:53:41Z, 2026-11-05T23:44:06Z, 2026-11-12T11:03:30Z, 2026-11-12T22:09:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 193 |
| `kind` | Always datacenter | none | text | datacenter | 0 |
| `developer` | The company building or owning the site, as named, if not the operator; written by the model (claude-sonnet), the name checked in the story | none | text | for example AEP, AIB Data Centers, AdaniConneX; 69 distinct | 114: The stories name no developer, or the name failed the check |
| `site_name` | The site or campus name; written by the model, checked in the story | none | text | for example AI Gigafactory, BCN1, Barber Lake; 37 distinct | 156: No site name stated |
| `state` | The state; written by the model, its span checked in the story | none | text | for example AK, AL, AR; 28 distinct | 126: No state stated, or its span failed the check |
| `county` | The county; written by the model, its span checked in the story | none | text | Ada County, Effingham County, Indiana County, Licking County, Lowndes County, Luzerne County, Mason County, McCracken County, Montgomery County, Posey County, Roanoke County, Willacy | 181: No county stated, or its span failed the check |
| `city` | The city; written by the model, its span checked in the story | none | text | for example Amarillo, Ansan, Ashburn; 73 distinct | 115: No city stated, or its span failed the check |
| `mw` | The capacity involved, in megawatts | MW | number | 1.0 to 10400.0; 44 distinct | 138 |
| `phase` | The phase or building as stated ('phase one', 'first 200 MW'); written by the model | none | text | First, First building, First phase, First project, Second building, first 222MW, first data center, first phase, fourth data center, second 500MW phase, second building, second data center, third facility | 178: No phase stated |
| `project_status` | The extractor's own status word (announced, applied, permitted, under_construction, operating, cancelled); written by the model, its span checked in the story | none | text | announced, applied, cancelled, operating, permitted, under_construction | 87: No status stated, or its span failed the check |
| `planned_year` | The year the facility or phase is planned to start, as stated; written by the model, its span checked in the story | none | integer | 2026, 2028, 2029, 2030 | 184: No year stated |
| `power_source` | How it will be powered, as stated (gas turbines, nuclear, solar and storage, grid); written by the model, checked in the story | none | text | SMR, behind-the-meter, combined cycle turbines, distributed virtual power plant, fuel cell, fuel cells, gas, gas plants, gas power plant, gas turbines, gas-fired, gas-powered, gas-powered fuel cells, geothermal, multi-gigawatt centralized natural gas generation, natural gas, off-grid, solar panels, tidal energy | 169: No power source stated |
| `utility` | The utility or power supplier as named; written by the model, checked in the story | none | text | AEP, American Electric Power, Blue Whale Energy, Entergy Arkansas, FirstEnergy, NiSource, OGE Energy, WEC Energy | 185: No utility named |
| `ai_power` | True on every row: the table is the platform's AI and datacenter power subset | none | boolean | True, true | 0 |
| `confidence` | The model's confidence, 0 to 1, that this is a real, specific facility and its fields are right | none | number | 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.88, 0.9 | 0 |
| `geo_precision` | How lat and lon were placed by code: county or place (the Census gazetteer's internal point of the stated county or city), or none | none | text | county, none, place | 0 |
| `geo_note` | Why the row was placed as it was, or not placed | none | text | for example city 'Swansea' not a unique place in the gazetteer for MA, county Ada County (2025_Gaz_counties_national.txt), county Effingham County (2025_Gaz_counties_national.txt); 35 distinct | 0 |
| `first_story_at` | The time of the first story naming the facility, UTC | none | utc time | 2025-01-07T08:00:00Z to 2026-11-12T17:10:30Z; 185 distinct | 0 |
| `n_stories` | The stories that name the facility | count | integer | 1, 2, 3, 4, 6 | 0 |
| `story_ids` | The event_ids of those stories in news_stories, joined by ';' | none | text | for example news:002bc7ebc5774cab, news:015878c3647dbba9;news:28fe08f50e09de14, news:015eda2d18115a8b; 191 distinct | 0 |
| `story_urls` | The addresses of those stories, joined by ';' | none | text | for example https://heatmap.news/plus/the-fight/hotspots/arevia-idaho-solar-data-center, https://heatmap.news/plus/the-fight/spotlight/data-centers-ocean, https://heatmap.news/plus/the-fight/spotlight/the-most-important-data-center-election-youve-never-heard-of; 191 distinct | 0 |
| `model_id` | The model of the facility's first extraction | none | text | claude-sonnet-5, claude-sonnet-5-5 | 0 |
| `extracted_at` | When the facility was first extracted, UTC | none | utc time | 2026-09-27T04:31:06Z, 2026-09-27T09:18:19Z, 2026-09-28T06:02:33Z, 2026-09-28T21:02:35Z, 2026-09-30T19:57:49Z, 2026-10-02T00:10:33Z, 2026-10-03T14:45:35Z, 2026-10-05T15:07:56Z, 2026-10-06T14:44:47Z, 2026-10-07T14:44:14Z, 2026-10-08T15:01:50Z, 2026-10-09T14:55:04Z, 2026-10-13T15:00:43Z, 2026-10-14T15:35:43Z, 2026-10-15T15:43:54Z, 2026-10-19T16:23:27Z, 2026-10-20T01:01:28Z, 2026-10-21T15:09:05Z, 2026-10-22T15:02:51Z, 2026-10-23T15:01:58Z, 2026-10-24T15:01:45Z, 2026-10-25T14:53:41Z, 2026-11-05T23:44:06Z, 2026-11-12T11:03:30Z, 2026-11-12T22:09:20Z | 0 |
| `mw_basis` | What the stated MW measures: it (IT or critical load), total, tenant, phase or unstated; given by the model with the words that say it, else unstated | none | text | tenant, total, unstated | 138: No MW stated |
| `power_kind` | How the facility is powered, read by code from power_source: behind_the_meter_gas, nuclear, renewables_storage, gas, behind_the_meter, grid or other | none | text | behind_the_meter, behind_the_meter_gas, gas, nuclear, other, renewables_storage | 169: No power source stated |
| `grid` | A US grid operator the stories name, else the grid that serves most of the facility's state (set by code) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 155: No grid named and no state, or a state split between grids |
| `grid_basis` | How grid was set: named (in a story) or state (the state's main grid) | none | text | state | 155: No grid set |
| `utility_eia861` | The one EIA-861 utility that serves the stated county | none | empty | no cell holds a value | 193: Not filled: no cell holds a value |
| `utility_eia861_number` | That utility's EIA-861 utility number | none | empty | no cell holds a value | 193: Not filled: no cell holds a value |
| `utilities_in_county` | The number of EIA-861 utilities that serve the stated county | count | empty | no cell holds a value | 193: Not filled: no cell holds a value |
| `energized_year` | The year the facility or its first phase is to be energized or come online, as stated; written by the model | none | empty | no cell holds a value | 193: Not filled: no cell holds a value |
| `country` | The country where the facility is, as the story names it; written by the model, its span checked | none | text | Australia, Denmark, Finland, Germany, India, Singapore, South Korea, UK | 180: The story names no country, or its span failed the check |
| `fields_version` | 2236, or upgraded for a row extracted before session 2236's fields (its power_kind, grid and utility read from its own values) | none | text | 2236, upgraded | 0 |

### `datacenter_queue_positions`

One ISO interconnection queue position whose name or fuel field names a datacenter or a large load, copied with the queue table's own columns (ERCOT and NYISO rows in this edition).

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 3.

- **Time:** No time column; the queue tables' dates (queue_date, proposed_in_service_date, withdrawn_date) as the ISOs print them. vintage is the queue table's own (a retrieval date or day).
- **Revisions:** Rebuilt by each run from the six ISO queue tables; when a queue table is absent, its matched rows are kept from the last datacenter_queue_positions.
- **Method note:** [`docs/methods/datacenter_facilities.md`](../methods/datacenter_facilities.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT); New York Independent System Operator (NYISO). Generation Interconnection Status (GIS) report; NYISO Interconnection Queue. Via the Energy Research Warehouse (ERW), table `datacenter_queue_positions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: The queue table's own (<iso>_queue:<queue_id>) | none | text | ercot_queue:25INR0688, ercot_queue:28INR0499, nyiso_queue:1630 | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | Alpha Digital Campus Combined-cycle and Co-located Load, Giga Texas Data Center, Suffern Quarry Data Center | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY, US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The generation or storage the position asks to connect, not the load | MW | number | 0.0, 133.0, 58.26 | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The queue table's: active, completed or withdrawn, mapped from iso_status | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2023-12-31 | 2 |
| `operator` | The operator or owner, as the publisher writes it | none | text | Giga Texas Energy, LLC, Orange & Rockland, PowerBridge LLC | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:interconnection_queue, nyiso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078, https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:50Z, 2026-11-05T23:21:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The queue table's own, as text: ERCOT's the retrieval date (YYYY-MM-DD), NYISO's the retrieval day at 00:00:00Z; not a publication date | none | text | 2026-09-26T00:00:00Z, 2026-11-05 | 0 |
| `queue_id` | The ISO's identifier of the interconnection request (ERCOT's INR number, NYISO's queue number) (the source's name: Queue ID) | none | text | 1630, 25INR0688, 28INR0499 | 0 |
| `county` | The county of the project as the ISO writes it (the source's name: County) | none | text | Reeves, Rockland, Travis | 0 |
| `state` | The state of the project as the ISO writes it (the source's name: State) | none | text | NY, TX | 0 |
| `poi` | The point of interconnection: the substation or line where the project would connect, as the ISO writes it (may run over several lines) (the source's name: Interconnection Location) | none | text | 38044 TNCOWPEN__3 345kV, HORNSBY Substation POIB# 7047     Site will be connected behind the meter at Medium Voltage  24.9 kV with non export controls    GSU TRANSFORMER  80/106/133MVA  345kV DELTA PRIMARY  24.9kV WYE-G SECONDARY  Z=XX%, 65DEG C RISE, We anticipate a new substation being built on our site off of a transmission line tower that abuts our property. Additionally, we may need to tie in for redundancy to the Hillburn Area Substation | 0 |
| `zone` | NYISO's load zone letter of the project (the source's name: Zone) | none | text | G | 2: ERCOT's report gives no zone |
| `transmission_owner` | The transmission owner the project connects to, as the ISO writes it (the source's name: Transmission Owner) | none | text | O&R | 2: ERCOT's report gives no transmission owner |
| `fuel_technology` | The project's fuel and technology in the ISO's words (Gas - Combined-Cycle, Other - Battery Energy Storage) (the source's name: Generation Type) | none | text | Gas - Combined-Cycle, Other - Battery Energy Storage | 1: The ISO gives no type |
| `iso_status` | The ISO's own status of the request (Active, Completed, Withdrawn); for ERCOT, Completed means a signed interconnection agreement, not a plant in operation (the source's name: Status) | none | text | Active, Completed, Withdrawn | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 2023-11-03, 2024-08-27, 2026-04-28 | 0 |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2027-08-13, 2027-12-31 | 1: The ISO gives no proposed date |
| `actual_in_service_date` | The date the project began operating (the source's name: Actual Completion Date) | none | empty | no cell holds a value | 3: Every row: not in service, or no date given |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2023-12-31 | 2: Not withdrawn |
| `matched` | The words of the name or fuel field that matched the datacenter or large-load pattern | none | text | Data Center, Digital Campus | 0 |

