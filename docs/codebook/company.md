# Codebook: company

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 entities; tiers: 3 model_extracted); 3 documented in full.

- [`company_aliases`](#company_aliases): One name a company of the company database goes by, as one input table writes it in one role, with the first row that uses it and the count of rows.
- [`company_directory`](#company_directory): One company named in any of 13 ERW tables (platform tool 10), with its kind, main segment, parent, states, grids, first and last dates, and its footprint of deals, plants, plans, queue positions, facilities and reactors.
- [`company_links`](#company_links): One company named in one row of an input table, with the role it has there, the name as written, the matching rule and confidence, the row's license, and the row's MW, dollars, date, fuel, state and grid.

### `company_aliases`

One name a company of the company database goes by, as one input table writes it in one role, with the first row that uses it and the count of rows.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 25986.

- **Time:** No time column; the table is a snapshot of the ERW's tables as built (vintage reads 20261116 on every row).
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/companies.py) from the tables held.
- **Source:** erw:companies, the ERW's resolution of the names in its own tables (each input's source in its own header).
- **Method note:** [`docs/methods/companies.md`](../methods/companies.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The company database: every company named in the warehouse's tables, its names and its rows (docs/methods/companies.md). Via the Energy Research Warehouse (ERW), table `company_aliases`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: company_alias:<16 hex characters of a SHA-1 of company, name, table and role> | none | text | for example company_alias:00013c92f190323f, company_alias:0001738c5449f18d, company_alias:0001e4cfb496c249; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always company_alias | none | text | company_alias | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The name as written in the input table (the same as alias) | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25986 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 25986 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 25986 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 25986 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25986 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 25986 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 25986 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:companies | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/companies.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:04:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | integer | 20261116 | 0 |
| `company_id` | The company the name belongs to: the entity_id of company_directory | none | text | for example company:174-power-global-properties, company:180-wind, company:1komma5grad; more than 5000 distinct | 0 |
| `company_name` | The company's name in company_directory | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `alias` | The name as the input table writes it | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `normalized` | The name normalized for matching: ASCII, lower case, punctuation and legal forms (Inc, LLC, Corp) dropped, EIA's abbreviations expanded | none | text | for example 0ham wham8 solar, 1000 mile solar, 1001 ebenezer church solar; more than 5000 distinct | 0 |
| `input_table` | The ERW table the name is written in | none | text | datacenter_facilities, datacenter_projects, eia860_generator_owners, eia860_plants_annual, eia860m_operating_generators, eia860m_planned_generators, eia861_utility_data, energy_deals, ercot_interconnection_queue, nrc_power_reactors, nyiso_interconnection_queue, policy_actions, utility_service_territories | 0 |
| `role` | What the company is in that table's rows (operator, owner, buyer, seller, utility, interconnection_customer, agency, licensee and the others) | none | text | agency, buyer, developer, interconnection_customer, licensee, operator, owner, parent, party, seller, service_territory, utility | 0 |
| `first_row` | The first input row with the name (its entity_id or event_id) | none | text | for example cpuc:6e3bde75ae48, datacenter:0403e02384dfcae9, datacenter:04a5a4836e54f365; more than 5000 distinct | 0 |
| `n_rows` | The number of input rows that write the name in that table and role | count | integer | 1 to 1115; 141 distinct | 0 |
| `match_rule` | The rule that matched the name to the company: eia_id, reviewed_alias, anchored_name, name or company_word | none | text | anchored_name, company_word, eia_id, name, reviewed_alias | 0 |
| `confidence` | The confidence of the match, set by its rule: eia_id 1.0, reviewed_alias 0.95, anchored_name 0.9, name 0.85, company_word 0.7 | none | number | 0.7, 0.85, 0.9, 0.95, 1.0 | 0 |
| `license` | The input table's license: internal where its publisher asks for written permission, else public | none | text | internal, public | 0 |

### `company_directory`

One company named in any of 13 ERW tables (platform tool 10), with its kind, main segment, parent, states, grids, first and last dates, and its footprint of deals, plants, plans, queue positions, facilities and reactors.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 14033.

- **Time:** No time column; the table is a snapshot of the ERW's tables as built (vintage reads 20261116 on every row). status_date is the latest date its rows state.
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/companies.py) from the tables held.
- **Source:** erw:companies, the ERW's resolution of the names in its own tables (each input's source in its own header).
- **Method note:** [`docs/methods/companies.md`](../methods/companies.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The company database: every company named in the warehouse's tables, its names and its rows (docs/methods/companies.md). Via the Energy Research Warehouse (ERW), table `company_directory`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: company:eia-<EIA utility id> where the company has one (company:eia-<id>-860 for EIA-860 rows of an id EIA-861 lists as another firm's power marketer), else company:<normalized name> | none | text | for example company:174-power-global-properties, company:180-wind, company:1komma5grad; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always company | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The reviewed aliases' canonical name, else EIA-861's newest name, else the NRC's parent field's, else the spelling its rows use most | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 14033 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 14033 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: plants_mw: nameplate of the operating generators it operates (EIA-860M); empty where it operates none | MW | number | 0.1 to 40818.1; 1665 distinct | 7973 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 14033 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The latest date its rows state (as last_seen) | none | date | 1906-11-01 to 2039-12-01; 1691 distinct | 1787 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 14033 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:companies | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/companies.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:04:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | integer | 20261116 | 0 |
| `kind` | What kind of company it is: the first of regulator, lab or hyperscaler, OEM, utility, IPP (independent power producer), lender or investor, developer, operator, power marketer, other that its rows show | none | text | IPP, OEM, developer, lab or hyperscaler, lender or investor, operator, other, power marketer, regulator, utility | 0 |
| `kind_basis` | The row or rule that gave the kind (for example 'EIA-860 sector Electric Utility') | none | text | for example EIA-860 sector Electric Utility, EIA-860 sector IPP CHP, EIA-860 sector IPP Non-CHP; 28 distinct | 0 |
| `segment` | The fuel or line with the most MW across the company's plants, plans, queue positions, facilities and deals, else with the most deals, else utility or government by kind | none | text | coal, datacenters, fusion, gas, geothermal, government, hydro, nuclear, oil, solar, storage, utility, wind | 3978: No segment could be set from its rows |
| `segment_basis` | How the segment was set: most MW, most rows, or kind | none | text | kind, most MW, most rows | 3978: No segment set |
| `parent` | The parent company, from the NRC's parent company field, a deal party written "X's Y", or the reviewed aliases only | none | text | ADNOC, Amazon, AmerenUE, BlackRock, Blackstone, Constellation Energy Corporation, Dominion Generation, Duke Energy, EIG, Energy Department, Energy Harbor Corp., Entergy Nuclear Operations, Inc., Interior Department, MAIRE, NextEra Energy, Inc., Talen Energy Corporation, Xcel Energy | 14007: None of those three places names a parent |
| `parent_id` | The parent's company_id where the parent is itself a company of the directory | none | text | company:adnoc, company:amazon, company:blackstone, company:dominion-generation, company:duke-energy, company:eia-61975, company:eia-6458, company:eig, company:energy-department, company:entergy-nuclear-operations, company:interior-department, company:talen-energy | 14015: No parent, or the parent is not a company of the directory |
| `parent_basis` | The input table and row that names the parent, with its words | none | text | energy_deals deal:030d9f3fabcf14ab: Blackstone's QTS, energy_deals deal:0dc43aeddcb3c631: BlackRock's GIP, energy_deals deal:0fd206cfe66ac078: MAIRE's Tecnimont, energy_deals deal:aaf126f54d7ddf2c: EIG's MidOcean, energy_deals deal:bfc0c4fa85e4b697: ADNOC's XRG, nrc_power_reactors nrc_reactor:05000237, nrc_power_reactors nrc_reactor:05000244, nrc_power_reactors nrc_reactor:05000250, nrc_power_reactors nrc_reactor:05000261, nrc_power_reactors nrc_reactor:05000263, nrc_power_reactors nrc_reactor:05000266, nrc_power_reactors nrc_reactor:05000269, nrc_power_reactors nrc_reactor:05000280, nrc_power_reactors nrc_reactor:05000313, nrc_power_reactors nrc_reactor:05000334, nrc_power_reactors nrc_reactor:05000336, nrc_power_reactors nrc_reactor:05000387, nrc_power_reactors nrc_reactor:05000395, nrc_power_reactors nrc_reactor:05000443, nrc_power_reactors nrc_reactor:05000483, reviewed_aliases.csv | 14007: No parent |
| `eia_utility_id` | The company's EIA utility id (EIA-861 utility number, EIA-860 operator or owner id) | none | integer | 7 to 99999; more than 5000 distinct | 2432: The company has no EIA utility id (matched by name) |
| `hq_state` | The state of the owner's address in EIA-860's owner schedule (the one held table that states an address) | none | text | for example AB, AK, AL; 54 distinct | 12002: The company owns no jointly owned generator, so no address is held |
| `hq_basis` | Where hq_state comes from: always 'EIA-860 owner address' where filled | none | text | EIA-860 owner address | 12002: No hq_state |
| `states` | The states its rows name, most first, joined by ';' | none | text | for example AK, AK;ME, AK;WA; 621 distinct | 571: No row names a two-letter state |
| `grids` | The grids (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP) its plants' balancing authorities, its queue positions and EIA-861's RTO flags name, joined by ';' | none | text | for example CAISO, CAISO;ERCOT, CAISO;ERCOT;ISO-NE; 76 distinct | 5496: No row names one of the seven grids |
| `first_seen` | The earliest date its rows state (an operating month, a planned month, a queue date, a deal's or policy action's date, a facility's first story, an EIA-861 year, a reactor's commercial operation) | none | date | 1891-01-01 to 2039-12-01; 2071 distinct | 1787: No row states a date |
| `last_seen` | The latest date its rows state, from the same dates as first_seen | none | date | 1906-11-01 to 2039-12-01; 1691 distinct | 1787: No row states a date |
| `n_deals` | Deals in energy_deals naming the company, each deal once | count | integer | 0, 1, 11, 13, 14, 16, 17, 19, 2, 27, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `deals_mw` | The MW of those deals, summed, each deal once | MW | number | 0.0 to 6000.0; 36 distinct | 0 |
| `deals_usd` | The dollars of those deals, summed, each deal once | USD | integer | 0 to 1281250000000; 164 distinct | 0 |
| `n_plants` | EIA plant ids of the operating generators it operates (EIA-860M) | count | integer | 0 to 243; 75 distinct | 0 |
| `n_generators` | Operating generators it operates (EIA-860M) | count | integer | 0 to 329; 114 distinct | 0 |
| `plants_mw` | Nameplate MW of the operating generators it operates (EIA-860M) | MW | number | 0.0 to 40818.1; 1666 distinct | 0 |
| `mw_solar` | Nameplate MW of its operating solar generators (EIA-860M, by EIA's energy source code) | MW | number | 0.0 to 8828.8; 528 distinct | 0 |
| `mw_wind` | Nameplate MW of its operating wind generators (EIA-860M) | MW | number | 0.0 to 7972.8; 432 distinct | 0 |
| `mw_gas` | Nameplate MW of its operating gas generators (EIA-860M) | MW | number | 0.0 to 26891.4; 858 distinct | 0 |
| `mw_coal` | Nameplate MW of its operating coal generators (EIA-860M) | MW | number | 0.0 to 7130.2; 147 distinct | 0 |
| `mw_nuclear` | Nameplate MW of its operating nuclear generators (EIA-860M) | MW | number | 0.0 to 23798.1; 31 distinct | 0 |
| `mw_hydro` | Nameplate MW of its operating hydro generators (EIA-860M) | MW | number | 0.0 to 14698.1; 257 distinct | 0 |
| `mw_storage` | Nameplate MW of its operating storage (EIA-860M) | MW | number | 0.0 to 1988.5; 232 distinct | 0 |
| `mw_oil` | Nameplate MW of its operating oil generators (EIA-860M) | MW | number | 0.0 to 3958.2; 302 distinct | 0 |
| `mw_geothermal` | Nameplate MW of its operating geothermal generators (EIA-860M) | MW | number | 0.0 to 1515.4; 29 distinct | 0 |
| `mw_other` | Nameplate MW of its operating generators of other or unmapped fuels (EIA-860M) | MW | number | 0.0 to 447.0; 254 distinct | 0 |
| `n_owned_generators` | Jointly owned generators it owns a share of (EIA-860 owner schedule) | count | integer | 0 to 49; 36 distinct | 0 |
| `owned_mw` | Nameplate MW times the percent owned, summed over those generators | MW | number | 0.0 to 6228.3; 719 distinct | 0 |
| `n_planned_plants` | Plants of the planned generators it operates (EIA-860M) | count | integer | 0, 1, 11, 12, 13, 15, 16, 18, 19, 2, 20, 26, 3, 31, 34, 35, 4, 5, 6, 7, 8, 9 | 0 |
| `planned_mw` | Nameplate MW of the planned generators it operates (EIA-860M) | MW | number | 0.0 to 11679.3; 443 distinct | 0 |
| `n_facilities` | Datacenter facilities it operates or develops (datacenter_facilities) | count | integer | 0, 1, 11, 2, 3, 32, 36, 4, 5, 62, 76, 8 | 0 |
| `facilities_mw` | The MW of those datacenter facilities, as stated | MW | number | 0.0 to 10400.0; 40 distinct | 0 |
| `n_queue` | Its interconnection queue positions (ERCOT, NYISO) neither withdrawn nor completed | count | integer | 0, 1, 2, 24, 3, 4, 5, 6, 8 | 0 |
| `queue_mw` | The MW of those queue positions, as stated (a negative figure is a position's own stated MW) | MW | number | -53.3 to 6017.6; 585 distinct | 0 |
| `n_reactors` | NRC power reactors it is licensee or operator of | count | integer | 0, 1, 2, 21, 3, 4, 5, 6, 7, 8 | 0 |
| `reactors_mw` | The MW of those reactors (nrc_power_reactors capacity_mw) | MW | number | 0.0 to 21425.0; 34 distinct | 0 |
| `n_policy_actions` | Policy actions (policy_actions) naming it as agency | count | integer | 0, 1, 1153, 141, 16, 17, 184, 2, 36, 37, 38, 4, 5, 506, 52, 7, 8, 9, 959 | 0 |
| `n_links` | Its links: rows of input tables naming it, by role (company_links) | count | integer | 1 to 1160; 178 distinct | 0 |
| `n_public_links` | Its links from inputs whose license is public | count | integer | 0 to 513; 176 distinct | 0 |
| `n_names` | The distinct names its rows write it as | count | integer | 1, 2, 3, 4, 5 | 0 |
| `tables` | The input tables that name it, joined by ';' | none | text | for example datacenter_facilities, datacenter_facilities;datacenter_projects, datacenter_facilities;datacenter_projects;eia860_generator_owners;eia860_plants_annual;eia860m_operating_generators;eia860m_planned_generators;eia861_utility_data;utility_service_territories; 101 distinct | 0 |
| `footprint_mw` | plants_mw, owned_mw, planned_mw, queue_mw, facilities_mw and deals_mw summed: a sort key only (a plant both operated and owned counts twice) | MW | number | 0.0 to 42934.1; 2442 distinct | 0 |
| `min_confidence` | The confidence of its weakest link (1.0 an EIA id down to 0.7 a company word added) | none | number | 0.7, 0.85, 0.9, 0.95, 1.0 | 0 |
| `license` | public, internal or mixed, by the licenses of its links | none | text | internal, mixed, public | 0 |

### `company_links`

One company named in one row of an input table, with the role it has there, the name as written, the matching rule and confidence, the row's license, and the row's MW, dollars, date, fuel, state and grid.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 97198.

- **Time:** No time column; the table is a snapshot of the ERW's tables as built (vintage reads 20261116 on every row). date and status_date are the input row's own date.
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/companies.py) from the tables held.
- **Source:** erw:companies, the ERW's resolution of the names in its own tables (each input's source in its own header).
- **Method note:** [`docs/methods/companies.md`](../methods/companies.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The company database: every company named in the warehouse's tables, its names and its rows (docs/methods/companies.md). Via the Energy Research Warehouse (ERW), table `company_links`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: company_link:<16 hex characters of a SHA-1 of table, row, role and name> | none | text | for example company_link:00003dca81695cc1, company_link:0000bdfd790667f8, company_link:0001643203a7304a; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always company_link | none | text | company_link | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The company's name in company_directory | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 97198 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 97198 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 97198 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The input row's MW (the same as mw) | MW | number | -53.3 to 10400.0; 4263 distinct | 57335 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 97198 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The input row's date (the same as date) | none | date | 1891-01-01 to 2039-12-01; 3010 distinct | 23300 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 97198 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:companies | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/companies.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:04:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | integer | 20261116 | 0 |
| `company_id` | The company: the entity_id of company_directory | none | text | for example company:174-power-global-properties, company:180-wind, company:1komma5grad; more than 5000 distinct | 0 |
| `input_table` | The ERW table the row is in | none | text | datacenter_facilities, datacenter_projects, eia860_generator_owners, eia860_plants_annual, eia860m_operating_generators, eia860m_planned_generators, eia861_utility_data, energy_deals, ercot_interconnection_queue, nrc_power_reactors, nyiso_interconnection_queue, policy_actions, utility_service_territories | 0 |
| `input_row` | The row of the input table: its entity_id or event_id | none | text | for example cpuc:09a9d3b07400, cpuc:0e961c301c0e, cpuc:1409cba401bd; more than 5000 distinct | 0 |
| `role` | What the company is in the row (operator, owner, buyer, seller, utility, service_territory, interconnection_customer, agency, licensee and the others) | none | text | agency, buyer, developer, interconnection_customer, licensee, operator, owner, parent, party, seller, service_territory, utility | 0 |
| `name_as_written` | The row's own words for the company | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `match_rule` | The rule that matched the name to the company: eia_id, reviewed_alias, anchored_name, name or company_word | none | text | anchored_name, company_word, eia_id, name, reviewed_alias | 0 |
| `confidence` | The confidence of the match, set by its rule: eia_id 1.0, reviewed_alias 0.95, anchored_name 0.9, name 0.85, company_word 0.7 | none | number | 0.7, 0.85, 0.9, 0.95, 1.0 | 0 |
| `license` | The input table's license: internal where its publisher asks for written permission, else public | none | text | internal, public | 0 |
| `mw` | The capacity involved, in megawatts. Here: The input row's MW as it states it; on owner rows nameplate times the percent owned | MW | number | -53.3 to 10400.0; 4263 distinct | 57335 |
| `usd` | The deal's dollars as the energy_deals row states them (the source's name: dollars) | USD | integer | 30000000 to 1250000000000; 151 distinct | 96724: Not a deal row, or the deal states no dollars |
| `date` | The row's date: a deal's or policy action's date, a generator's operating or planned month, a queue date, a facility's first story, an EIA-861 year, a reactor's commercial operation | none | date | 1891-01-01 to 2039-12-01; 3010 distinct | 23300: The input row states no date of these |
| `fuel` | The row's fuel or line (solar, gas, storage, datacenters, nuclear and the others), from EIA's energy source code or the row's technology words | none | text | coal, datacenters, fusion, gas, geothermal, hydro, nuclear, oil, other, solar, storage, transmission, wind | 61528: The input row states no fuel or technology (utilities, territories, policy rows) |
| `state` | The row's state or states, two-letter codes joined by ';' | none | text | for example AK, AL, AL;FL;MS; 115 distinct | 2376: The input row states no state |
| `grid` | The grid or grids (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP) the row names, joined by ';' | none | text | CAISO, ERCOT, ERCOT;MISO, ERCOT;SPP, ERCOT;SPP;MISO, ISO-NE, MISO, NYISO, PJM, PJM;MISO, SPP, SPP;MISO | 47614: The row names none of the seven grids |
| `detail` | One more field of the row: the deal type, a status, the EIA sector, the EIA-861 ownership, the owner's state, the county, the plant, or the policy action type, by input | none | text | for example AB, AK, AL; more than 5000 distinct | 739: The input row's field is empty |

