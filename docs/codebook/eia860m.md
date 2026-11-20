# Codebook: eia860m

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 entities; tiers: 4 source); 3 documented in full.

- [`eia860m_operating_generators`](#eia860m_operating_generators): One generator in service (operating, standby or out of service) in EIA's monthly inventory, Form EIA-860M, for one vintage month, the 50 states, DC and Puerto Rico.
- [`eia860m_planned_generators`](#eia860m_planned_generators): One planned generator (planned or under construction) in EIA's monthly inventory, Form EIA-860M, for one vintage month, the 50 states, DC and Puerto Rico.
- [`eia860m_retired_generators`](#eia860m_retired_generators): One generator retired in the vintage year or the year before, from EIA's monthly inventory, Form EIA-860M, for one vintage month.
- [`eia860m_retired_generators_all`](#eia860m_retired_generators_all): EIA-860M, every retired generator EIA lists, vintage 2026-08 (session 133)

### `eia860m_operating_generators`

One generator in service (operating, standby or out of service) in EIA's monthly inventory, Form EIA-860M, for one vintage month, the 50 states, DC and Puerto Rico.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 28712.

- **Time:** No time column; vintage is EIA's month (YYYY-MM). status_date is the first day of the generator's operating month; EIA gives months, not days.
- **Revisions:** A snapshot of one vintage; a new vintage replaces its rows. Earlier vintages are in the raw files and the archive.
- **Source:** eia:860m EIA-860M Monthly Update to the Annual Electric Generator Report, sheets Operating, Operating_PR (Inventory of Operating Generators as of September 2026; Inventory of Operating Generators as of September 2026 - Puerto Rico) (https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx)
- **Method note:** [`docs/methods/eia860m_operating_generators.md`](../methods/eia860m_operating_generators.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-860M, Monthly Update to the Annual Electric Generator Report. Via the Energy Research Warehouse (ERW), table `eia860m_operating_generators`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia860:<plant id>:<generator id> | none | text | for example eia860:10003:GEN1, eia860:10003:GEN2, eia860:10003:GEN3; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always generator | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: EIA's plant name | none | text | for example (3K) 59 Hetcheltown Rd, 0 Hammond St CSG, 0 Middle; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<plant state> | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 17.947115 to 71.292; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -171.7124 to -65.27956; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EIA's nameplate capacity, the same as nameplate_mw | MW | number | 0.1 to 2561.2; 1968 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Always operating: EIA codes OP, SB, OA and OS, with EIA's own code in eia_status | none | text | operating | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The first day of EIA's operating month | none | date | 1891-01-01 to 2026-09-01; 1327 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: EIA's Entity Name, the utility that operates the generator | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:860m | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:49:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: EIA's inventory month, YYYY-MM | none | text | 2026-09 | 0 |
| `plant_id` | EIA's plant identifier (the source's name: Plant ID) | none | integer | 1 to 70578; more than 5000 distinct | 0 |
| `generator_id` | EIA's generator identifier within the plant (the source's name: Generator ID) | none | text | for example 00001, 00003, 0000A; more than 5000 distinct | 1: EIA gives no generator id (1 row) |
| `utility_id` | EIA's identifier of the operating utility (its Entity ID) (the source's name: Entity ID) | none | integer | 7 to 68094; more than 5000 distinct | 0 |
| `state` | The plant's state, two-letter postal code (the source's name: Plant State) | none | text | for example AK, AL, AR; 52 distinct | 0 |
| `county` | The plant's county, as EIA names it (the source's name: County) | none | text | for example Abbeville, Acadia, Accomack; 1514 distinct | 78: EIA gives no county |
| `balancing_authority` | The balancing authority (the grid operator of the area) the plant is in, EIA's code (the source's name: Balancing Authority Code) | none | text | for example AECI, AVA, AVRN; 66 distinct | 963: EIA gives none, or writes NA |
| `sector` | EIA's sector of the plant: Electric Utility, IPP (independent power producer), Commercial or Industrial, each CHP (combined heat and power) or Non-CHP (the source's name: Sector) | none | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP CHP, IPP Non-CHP, Industrial CHP, Industrial Non-CHP | 0 |
| `technology` | EIA's technology text for the generator (the source's name: Technology) | none | text | for example All Other, Batteries, Coal Integrated Gasification Combined Cycle; 27 distinct | 0 |
| `technology_group` | An ERW grouping of EIA's technology text for maps and filters (solar, wind, natural_gas, storage and the others) | none | text | biomass, coal, geothermal, hydro, natural_gas, nuclear, other, petroleum, solar, storage, wind | 0 |
| `prime_mover` | EIA's prime mover code: the kind of engine or turbine (GT gas turbine, PV photovoltaic, BA battery and the others) (the source's name: Prime Mover Code) | none | text | BA, BT, CA, CE, CP, CS, CT, FC, FW, GT, HY, IC, OT, PS, PV, ST, WS, WT | 0 |
| `prime_mover_label` | The prime mover code's meaning, from the EIA-860 instructions | none | text | Combined cycle combustion turbine part, Combined cycle single shaft, Combined cycle steam part, Combustion (gas) turbine, Energy storage, battery, Energy storage, compressed air, Energy storage, concentrated solar power, Energy storage, flywheel, Energy storage, reversible hydraulic turbine (pumped storage), Fuel cell, Hydraulic turbine (conventional hydro), Internal combustion engine, Other, Photovoltaic, Steam turbine, Turbines used in a binary cycle (geothermal), Wind turbine, offshore, Wind turbine, onshore | 0 |
| `energy_source` | EIA's energy source code: the generator's main fuel or energy (NG natural gas, SUN solar, MWH electricity stored and the others) (the source's name: Energy Source Code) | none | text | for example AB, BFG, BIT; 35 distinct | 0 |
| `energy_source_label` | The energy source code's meaning, from the EIA-860 instructions | none | text | for example Agricultural by-products, Bituminous coal, Black liquor; 35 distinct | 0 |
| `nameplate_mw` | EIA's nameplate capacity: the generator's rated output (the source's name: Nameplate Capacity (MW)) | MW | number | 0.1 to 2561.2; 1968 distinct | 0 |
| `net_summer_mw` | EIA's net summer capacity: the output the generator can deliver in summer, net of its own use (the source's name: Net Summer Capacity (MW)) | MW | number | 0.0 to 2561.2; 2136 distinct | 66: EIA gives none |
| `net_winter_mw` | EIA's net winter capacity: the output the generator can deliver in winter, net of its own use (the source's name: Net Winter Capacity (MW)) | MW | number | 0.0 to 2561.2; 2122 distinct | 74: EIA gives none |
| `eia_status` | EIA's status code: OP operating, SB standby, OA out of service but expected back next year, OS out of service and not expected back (the source's name: Status) | none | text | OA, OP, OS, SB | 0 |
| `eia_status_label` | The status code's words as EIA prints them (the source's name: Status) | none | text | Operating, Out of service and NOT expected to return to service in next calendar year, Out of service but expected to return to service in next calendar year, Standby/Backup: available for service but not normally used | 0 |
| `operating_year` | The year the generator began commercial operation, as EIA gives it (the source's name: Operating Year) | none | integer | 1891 to 2026; 132 distinct | 0 |
| `operating_month` | The month (1 to 12) the generator began commercial operation, as EIA gives it (the source's name: Operating Month) | none | integer | 1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `planned_retirement_date` | The first day of the month EIA reports the generator is planned to retire (the source's name: Planned Retirement Year and Month) | none | date | 2026-10-01 to 2072-08-01; 87 distinct | 28200: No planned retirement reported |
| `energy_capacity_mwh` | EIA's nameplate energy capacity: the energy a storage unit holds (the source's name: Nameplate Energy Capacity (MWh)) | MWh | number | 0.2 to 2000.0; 315 distinct | 27551: EIA gives none (not a storage unit, mostly) |

### `eia860m_planned_generators`

One planned generator (planned or under construction) in EIA's monthly inventory, Form EIA-860M, for one vintage month, the 50 states, DC and Puerto Rico.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 2361.

- **Time:** No time column; vintage is EIA's month (YYYY-MM). status_date is empty (no operating month yet); planned_operation_date is the first day of EIA's planned month.
- **Revisions:** A snapshot of one vintage; a new vintage replaces its rows. Earlier vintages are in the raw files and the archive.
- **Source:** eia:860m EIA-860M Monthly Update to the Annual Electric Generator Report, sheets Planned, Planned_PR (Inventory of Planned Generators as of September 2026; Inventory of Planned Generators as of September 2026 - Puerto Rico) (https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx)
- **Method note:** [`docs/methods/eia860m_planned_generators.md`](../methods/eia860m_planned_generators.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-860M, Monthly Update to the Annual Electric Generator Report. Via the Energy Research Warehouse (ERW), table `eia860m_planned_generators`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia860:<plant id>:<generator id> | none | text | for example eia860:1024:8, eia860:10328:GEN11, eia860:10748:FUTR1; 2361 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always generator | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: EIA's plant name | none | text | for example 100a Swiss Dale Farm, 20525 Nordhoff PV (North), 4786A George Washington, LLC; 1610 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<plant state> | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 18.134597 to 57.9449; 1544 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -159.45 to -65.82234; 1542 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EIA's nameplate capacity, the same as nameplate_mw | MW | number | 0.1 to 2640.0; 518 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: planned or under_construction, mapped from EIA's code in eia_status | none | text | planned, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Not filled: a planned generator has no operating month yet | none | empty | no cell holds a value | 2361 |
| `operator` | The operator or owner, as the publisher writes it. Here: EIA's Entity Name, the utility that will operate the generator | none | text | for example 174 Power Global Corp., 201LC 8me LLC, 229HD 8me, LLC; 1000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:860m | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:49:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: EIA's inventory month, YYYY-MM | none | text | 2026-09 | 0 |
| `plant_id` | EIA's plant identifier (the source's name: Plant ID) | none | integer | 56 to 70587; 1610 distinct | 0 |
| `generator_id` | EIA's generator identifier within the plant (the source's name: Generator ID) | none | text | for example 02B, 03A, 03B; 2007 distinct | 1: EIA gives no generator id (1 row) |
| `utility_id` | EIA's identifier of the operating utility (its Entity ID) (the source's name: Entity ID) | none | integer | 189 to 68108; 1000 distinct | 0 |
| `state` | The plant's state, two-letter postal code (the source's name: Plant State) | none | text | for example AK, AL, AR; 52 distinct | 0 |
| `county` | The plant's county, as EIA names it (the source's name: County) | none | text | for example Acadia, Ada, Adams; 643 distinct | 3: EIA gives no county |
| `balancing_authority` | The balancing authority (the grid operator of the area) the plant is in, EIA's code (the source's name: Balancing Authority Code) | none | text | for example AECI, AVA, AVRN; 46 distinct | 10: EIA gives none, or writes NA |
| `sector` | EIA's sector of the plant: Electric Utility, IPP (independent power producer), Commercial or Industrial, each CHP (combined heat and power) or Non-CHP (the source's name: Sector) | none | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP CHP, IPP Non-CHP, Industrial CHP, Industrial Non-CHP | 0 |
| `technology` | EIA's technology text for the generator (the source's name: Technology) | none | text | All Other, Batteries, Conventional Hydroelectric, Geothermal, Hydroelectric Pumped Storage, Landfill Gas, Municipal Solid Waste, Natural Gas Fired Combined Cycle, Natural Gas Fired Combustion Turbine, Natural Gas Internal Combustion Engine, Natural Gas Steam Turbine, Nuclear, Offshore Wind Turbine, Onshore Wind Turbine, Other Waste Biomass, Petroleum Liquids, Solar Photovoltaic, Solar Thermal without Energy Storage | 4: EIA gives no technology |
| `technology_group` | An ERW grouping of EIA's technology text for maps and filters (solar, wind, natural_gas, storage and the others) | none | text | biomass, geothermal, hydro, natural_gas, nuclear, other, petroleum, solar, storage, wind | 4: EIA gives no technology |
| `prime_mover` | EIA's prime mover code: the kind of engine or turbine (GT gas turbine, PV photovoltaic, BA battery and the others) (the source's name: Prime Mover Code) | none | text | BA, BT, CA, CC, CE, CS, CT, GT, HY, IC, OT, PS, PV, ST, WS, WT | 0 |
| `prime_mover_label` | The prime mover code's meaning, from the EIA-860 instructions | none | text | Combined cycle combustion turbine part, Combined cycle single shaft, Combined cycle steam part, Combined cycle total unit, Combustion (gas) turbine, Energy storage, battery, Energy storage, compressed air, Energy storage, reversible hydraulic turbine (pumped storage), Hydraulic turbine (conventional hydro), Internal combustion engine, Other, Photovoltaic, Steam turbine, Turbines used in a binary cycle (geothermal), Wind turbine, offshore, Wind turbine, onshore | 0 |
| `energy_source` | EIA's energy source code: the generator's main fuel or energy (NG natural gas, SUN solar, MWH electricity stored and the others) (the source's name: Energy Source Code) | none | text | AB, DFO, GEO, H2, LFG, MSW, MWH, NG, NUC, OBG, OBL, OBS, OTH, SUN, WAT, WH, WND | 0 |
| `energy_source_label` | The energy source code's meaning, from the EIA-860 instructions | none | text | Agricultural by-products, Distillate fuel oil, Electricity used for energy storage, Geothermal, Hydrogen, Landfill gas, Municipal solid waste, Natural gas, Nuclear, Other, Other biomass gas, Other biomass liquids, Other biomass solids, Solar, Waste heat, Water, Wind | 0 |
| `nameplate_mw` | EIA's nameplate capacity: the generator's rated output (the source's name: Nameplate Capacity (MW)) | MW | number | 0.1 to 2640.0; 518 distinct | 0 |
| `net_summer_mw` | EIA's net summer capacity: the output the generator will deliver in summer, net of its own use (the source's name: Net Summer Capacity (MW)) | MW | number | 0.1 to 2640.0; 518 distinct | 0 |
| `net_winter_mw` | EIA's net winter capacity: the output the generator will deliver in winter, net of its own use (the source's name: Net Winter Capacity (MW)) | MW | number | 0.1 to 2640.0; 519 distinct | 0 |
| `eia_status` | EIA's status code of a planned generator: P planned, L regulatory approvals pending, T approvals received, U and V under construction (up to or over half done), TS construction complete, not yet operating (the source's name: Status) | none | text | L, P, T, TS, U, V | 0 |
| `eia_status_label` | The status code's words as EIA prints them (the source's name: Status) | none | text | Construction complete, but not yet in commercial operation, Planned for installation, but regulatory approvals not initiated, Regulatory approvals pending. Not under construction, Regulatory approvals received. Not under construction, Under construction, less than or equal to 50 percent complete, Under construction, more than 50 percent complete | 0 |
| `planned_operation_date` | The first day of the month EIA reports the generator is planned to begin operation (the source's name: Planned Operation Year and Month) | none | date | 2026-09-01 to 2039-12-01; 62 distinct | 0 |
| `energy_capacity_mwh` | EIA's nameplate energy capacity of a storage unit: EIA's Planned sheet carries no such column | MWh | empty | no cell holds a value | 2361: Always empty: EIA's Planned sheet has no such column |

### `eia860m_retired_generators`

One generator retired in the vintage year or the year before, from EIA's monthly inventory, Form EIA-860M, for one vintage month.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 260.

- **Time:** No time column; vintage is EIA's month (YYYY-MM). retirement_date and status_date are the first day of EIA's retirement month.
- **Revisions:** A snapshot of one vintage; a new vintage replaces its rows. Earlier vintages are in the raw files and the archive.
- **Source:** eia:860m EIA-860M Monthly Update to the Annual Electric Generator Report, sheets Retired, Retired_PR (Inventory of Retired Generators as of September 2026; Inventory of Retired Generators as of September 2026 - Puerto Rico) (https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx)
- **Method note:** [`docs/methods/eia860m_retired_generators.md`](../methods/eia860m_retired_generators.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-860M, Monthly Update to the Annual Electric Generator Report. Via the Energy Research Warehouse (ERW), table `eia860m_retired_generators`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia860:<plant id>:<generator id> | none | text | for example eia860:10004:TG1, eia860:1073:1, eia860:113:1; 260 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always generator | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: EIA's plant name | none | text | for example Aera San Ardo Cogen Facility, Allen, Alliant SBG 9802 Toyota; 117 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<plant state> | none | text | for example US-AK, US-AZ, US-CA; 40 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 18.454087 to 66.837778; 117 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -163.7291 to -66.14353; 116 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EIA's nameplate capacity, the same as nameplate_mw | MW | number | 0.1 to 820.0; 79 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Always retired | none | text | retired | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The first day of EIA's retirement month (the same as retirement_date) | none | date | 2025-01-01, 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01, 2025-06-01, 2025-07-01, 2025-08-01, 2025-09-01, 2025-10-01, 2025-11-01, 2025-12-01, 2026-01-01, 2026-02-01, 2026-03-01, 2026-05-01, 2026-06-01, 2026-07-01, 2026-08-01, 2026-09-01 | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: EIA's Entity Name, the utility that operated the generator | none | text | for example AES Distributed Energy, Acciona Energy USA Global, LLC, Aera Energy LLC-San Ardo; 110 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:860m | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:49:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: EIA's inventory month, YYYY-MM | none | text | 2026-09 | 0 |
| `plant_id` | EIA's plant identifier (the source's name: Plant ID) | none | integer | 113 to 69979; 117 distinct | 0 |
| `generator_id` | EIA's generator identifier within the plant (the source's name: Generator ID) | none | text | for example 0002, 01, 0385; 140 distinct | 0 |
| `utility_id` | EIA's identifier of the operating utility (its Entity ID) (the source's name: Entity ID) | none | integer | 221 to 67818; 110 distinct | 0 |
| `state` | The plant's state, two-letter postal code (the source's name: Plant State) | none | text | for example AK, AZ, CA; 40 distinct | 0 |
| `county` | The plant's county, as EIA names it (the source's name: County) | none | text | for example Adams, Allegany, Anne Arundel; 99 distinct | 0 |
| `balancing_authority` | The balancing authority (the grid operator of the area) the plant was in, EIA's code (the source's name: Balancing Authority Code) | none | text | for example AZPS, BANC, BPAT; 30 distinct | 17: EIA gives none, or writes NA |
| `sector` | EIA's sector of the plant: Electric Utility, IPP (independent power producer), Commercial or Industrial, each CHP (combined heat and power) or Non-CHP (the source's name: Sector) | none | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP CHP, IPP Non-CHP, Industrial CHP, Industrial Non-CHP | 0 |
| `technology` | EIA's technology text for the generator (the source's name: Technology) | none | text | All Other, Batteries, Conventional Hydroelectric, Conventional Steam Coal, Geothermal, Landfill Gas, Natural Gas Fired Combined Cycle, Natural Gas Fired Combustion Turbine, Natural Gas Internal Combustion Engine, Natural Gas Steam Turbine, Onshore Wind Turbine, Other Gases, Other Waste Biomass, Petroleum Liquids, Solar Photovoltaic, Wood/Wood Waste Biomass | 0 |
| `technology_group` | An ERW grouping of EIA's technology text for maps and filters (solar, wind, natural_gas, storage and the others) | none | text | biomass, coal, geothermal, hydro, natural_gas, other, petroleum, solar, storage, wind | 0 |
| `prime_mover` | EIA's prime mover code: the kind of engine or turbine (GT gas turbine, PV photovoltaic, BA battery and the others) (the source's name: Prime Mover Code) | none | text | BA, BT, CA, CT, GT, HY, IC, PV, ST, WT | 0 |
| `prime_mover_label` | The prime mover code's meaning, from the EIA-860 instructions | none | text | Combined cycle combustion turbine part, Combined cycle steam part, Combustion (gas) turbine, Energy storage, battery, Hydraulic turbine (conventional hydro), Internal combustion engine, Photovoltaic, Steam turbine, Turbines used in a binary cycle (geothermal), Wind turbine, onshore | 0 |
| `energy_source` | EIA's energy source code: the generator's main fuel or energy (NG natural gas, SUN solar, MWH electricity stored and the others) (the source's name: Energy Source Code) | none | text | BIT, BLQ, DFO, GEO, LFG, MWH, NG, OBG, OG, SUB, SUN, WAT, WDS, WH, WND | 0 |
| `energy_source_label` | The energy source code's meaning, from the EIA-860 instructions | none | text | Bituminous coal, Black liquor, Distillate fuel oil, Electricity used for energy storage, Geothermal, Landfill gas, Natural gas, Other biomass gas, Other gas, Solar, Subbituminous coal, Waste heat, Water, Wind, Wood/wood waste solids | 0 |
| `nameplate_mw` | EIA's nameplate capacity: the generator's rated output (the source's name: Nameplate Capacity (MW)) | MW | number | 0.1 to 820.0; 79 distinct | 0 |
| `net_summer_mw` | EIA's net summer capacity: the output the generator could deliver in summer, net of its own use (the source's name: Net Summer Capacity (MW)) | MW | number | 0.0 to 900.0; 87 distinct | 1: EIA gives none |
| `net_winter_mw` | EIA's net winter capacity: the output the generator could deliver in winter, net of its own use (the source's name: Net Winter Capacity (MW)) | MW | number | 0.0 to 900.0; 89 distinct | 0 |
| `eia_status` | EIA's status code: always RE, retired (the source's name: Status) | none | text | RE | 0 |
| `eia_status_label` | The status code's words as EIA prints them (the source's name: Status) | none | text | Retired | 0 |
| `retirement_date` | The first day of the month the generator retired, as EIA gives it (the source's name: Retirement Year and Month) | none | date | 2025-01-01, 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01, 2025-06-01, 2025-07-01, 2025-08-01, 2025-09-01, 2025-10-01, 2025-11-01, 2025-12-01, 2026-01-01, 2026-02-01, 2026-03-01, 2026-05-01, 2026-06-01, 2026-07-01, 2026-08-01, 2026-09-01 | 0 |
| `operating_year` | The year the generator began commercial operation, as EIA gives it (the source's name: Operating Year) | none | integer | 1908 to 2024; 67 distinct | 0 |
| `operating_month` | The month (1 to 12) the generator began commercial operation, as EIA gives it (the source's name: Operating Month) | none | integer | 1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `energy_capacity_mwh` | EIA's nameplate energy capacity: the energy a storage unit held (the source's name: Nameplate Energy Capacity (MWh)) | MWh | number | 0.5, 1200, 16, 2, 4.1, 5, 8 | 252: EIA gives none (not a storage unit, mostly) |

### `eia860m_retired_generators_all`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 7334.

- **Source:** eia:860m:retired EIA-860M Monthly Update to the Annual Electric Generator Report, sheets Retired, Retired_PR (Inventory of Retired Generators as of August 2026; Inventory of Retired Generators as of August 2026 - Puerto Rico) (https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx)
- **Method note:** [`docs/methods/eia860m_retired_generators_all.md`](../methods/eia860m_retired_generators_all.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-860M, Monthly Update to the Annual Electric Generator Report: the Retired sheets, every year. Via the Energy Research Warehouse (ERW), table `eia860m_retired_generators_all`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example eia860:10002:GEN1, eia860:10003:VBPT, eia860:10004:TG1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1420 Coil Av #C, 1515 S Caron Road, 2 AC Station; 2654 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 18.003 to 71.292; 2603 distinct | 44 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -171.7124 to -65.6952; 2598 distinct | 44 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.1 to 1425.6; 776 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | retired | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 1972-11-01 to 2026-08-01; 309 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 3 MW LLC, 31st Street Energy LLC, 5 Research Parkway Wallingford LLC; 1721 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:860m:retired | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:55:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026-08 | 0 |
| `plant_id` | not yet written |  | integer | 1 to 69979; 2662 distinct | 0 |
| `generator_id` | not yet written |  | text | for example 00001, 0001, 0002; 1743 distinct | 0 |
| `utility_id` | not yet written |  | integer | 25 to 67826; 1728 distinct | 0 |
| `state` | not yet written |  | text | for example AK, AL, AR; 52 distinct | 0 |
| `county` | not yet written |  | text | for example ANOKA, Ada, Adair; 927 distinct | 2 |
| `balancing_authority` | not yet written |  | text | for example AECI, AVA, AZPS; 58 distinct | 1425 |
| `sector` | not yet written |  | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP CHP, IPP Non-CHP, Industrial CHP, Industrial Non-CHP | 4 |
| `technology` | not yet written |  | text | All Other, Batteries, Conventional Hydroelectric, Conventional Steam Coal, Flywheels, Geothermal, Hydroelectric Pumped Storage, Landfill Gas, Municipal Solid Waste, Natural Gas Fired Combined Cycle, Natural Gas Fired Combustion Turbine, Natural Gas Internal Combustion Engine, Natural Gas Steam Turbine, Nuclear, Onshore Wind Turbine, Other Gases, Other Natural Gas, Other Waste Biomass, Petroleum Coke, Petroleum Liquids, Solar Photovoltaic, Solar Thermal without Energy Storage, Wood/Wood Waste Biomass | 0 |
| `technology_group` | not yet written |  | text | biomass, coal, geothermal, hydro, natural_gas, nuclear, other, petroleum, solar, storage, wind | 0 |
| `prime_mover` | not yet written |  | text | BA, BT, CA, CS, CT, FC, FW, GT, HY, IC, OT, PS, PV, ST, WT | 0 |
| `prime_mover_label` | not yet written |  | text | Combined cycle combustion turbine part, Combined cycle single shaft, Combined cycle steam part, Combustion (gas) turbine, Energy storage, battery, Energy storage, flywheel, Energy storage, reversible hydraulic turbine (pumped storage), Fuel cell, Hydraulic turbine (conventional hydro), Internal combustion engine, Other, Photovoltaic, Steam turbine, Turbines used in a binary cycle (geothermal), Wind turbine, onshore | 0 |
| `energy_source` | not yet written |  | text | for example AB, BFG, BIT; 34 distinct | 0 |
| `energy_source_label` | not yet written |  | text | for example Agricultural by-products, Bituminous coal, Black liquor; 34 distinct | 0 |
| `nameplate_mw` | not yet written |  | number | 0.1 to 1425.6; 776 distinct | 0 |
| `net_summer_mw` | not yet written |  | number | 0.0 to 1305.0; 804 distinct | 56 |
| `net_winter_mw` | not yet written |  | number | 0.0 to 1333.0; 806 distinct | 57 |
| `eia_status` | not yet written |  | text | RE | 0 |
| `eia_status_label` | not yet written |  | text | Retired | 0 |
| `retirement_date` | not yet written |  | date | 1972-11-01 to 2026-08-01; 309 distinct | 0 |
| `operating_year` | not yet written |  | integer | 1898 to 2024; 124 distinct | 0 |
| `operating_month` | not yet written |  | integer | 0, 1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 88, 9, 99 | 0 |

