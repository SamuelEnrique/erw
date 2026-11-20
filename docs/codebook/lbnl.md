# Codebook: lbnl

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (2 entities, 3 events, 3 series; tiers: 8 source); 8 documented in full.

- [`lbnl_hybrid_ppa_prices`](#lbnl_hybrid_ppa_prices): One PV plus battery hybrid power purchase agreement in Berkeley Lab's Utility-Scale Solar, 2025 Data Update, either greenfield (PV and battery contracted together) or a retrofit (a battery added to an operating PV plant).
- [`lbnl_interconnection_queue`](#lbnl_interconnection_queue): One interconnection request (a project's request to connect to the grid) in Berkeley Lab and GridTracker's Queued Up data file, 2026 edition, requests through the end of 2025, across the seven ISOs and the West and Southeast outside them.
- [`lbnl_ppa_prices`](#lbnl_ppa_prices): One wind or PV-only solar power purchase agreement in Berkeley Lab's wind (2026 Edition) and solar (2025 Data Update) data files; LBNL names no project.
- [`lbnl_solar_projects`](#lbnl_solar_projects): One utility-scale solar project (PV or concentrating solar) in Berkeley Lab's Utility-Scale Solar, 2025 Data Update, with its place, technology, size, design, storage, offtaker, value, cost, PPA price and yearly capacity factors.
- [`lbnl_tracking_the_sun`](#lbnl_tracking_the_sun): One state's customer segment's installed distributed solar systems in one year of installation, one measure, summarised from Berkeley Lab's Tracking the Sun 2024 public data file (one record a system).
- [`lbnl_wind_capacity_factors`](#lbnl_wind_capacity_factors): One land-based wind plant's capacity factor in calendar year 2025, from Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition.
- [`lbnl_wind_costs`](#lbnl_wind_costs): One wind cost measure for one year from Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition: a turbine maker's or LBNL's average turbine price, or the installed cost or levelized cost of the projects of a commercial operation year.
- [`lbnl_wind_turbine_orders`](#lbnl_wind_turbine_orders): One reported US wind turbine order and its price, from the 'Wind Turbine Prices' sheet of Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition; LBNL names no buyer, maker or size.

### `lbnl_hybrid_ppa_prices`

One PV plus battery hybrid power purchase agreement in Berkeley Lab's Utility-Scale Solar, 2025 Data Update, either greenfield (PV and battery contracted together) or a retrofit (a battery added to an operating PV plant).

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 113.

- **Time:** No time column; event_date is the PPA's execution date (greenfield) or the retrofit's execution date (retrofit), a date.
- **Revisions:** Rewritten whole by each run from the data file lbnl_ppa_prices.py saves; one edition, no vintage column.
- **Source:** lbnl:hybrid_ppa_prices Lawrence Berkeley National Laboratory, Utility-Scale Solar, 2025 Data Update (October 2025), sheet 'PV+Battery Hybrid PPA Price' (https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data)
- **Method note:** [`docs/methods/lbnl_ppa_prices.md`](../methods/lbnl_ppa_prices.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Utility-Scale Solar Data Update (PV+Battery Hybrid PPA Price). Via the Energy Research Warehouse (ERW), table `lbnl_hybrid_ppa_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example lbnl_hybrid:0:greenfield, lbnl_hybrid:0:greenfield-10, lbnl_hybrid:0:greenfield-11; 113 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2015-09-09 to 2025-06-13; 78 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: Always ppa_hybrid | none | text | ppa_hybrid | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 113 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: lbnl_solar:<EIA ID> for each EIA id the row names; a retrofit names the PV plant and the battery | none | text | for example lbnl_solar:0, lbnl_solar:57242, lbnl_solar:58462; 82 distinct | 0 |
| `mw` | The capacity involved, in megawatts. Here: The PV capacity, MW-AC | MW | number | 7.0 to 700.0; 61 distinct | 0 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: The PV plus battery price levelized over the term, real 2024 USD per MWh of PV output (the sheet's PV+BESS_$_per_MWh-PV_real) | the row's currency per MWh, unless the table's file says otherwise | number | 18.48697031937399 to 206.40673223651368; 113 distinct | 0 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | text | USD | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 113 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:hybrid_ppa_prices | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:21Z | 0 |
| `x_kind` | Whether the PPA is greenfield (PV and battery contracted together) or a retrofit (a battery added to an operating PV plant) | none | text | greenfield, retrofit | 0 |
| `x_state` | The plant's state, two-letter postal code (the source's name: State) | none | text | AZ, CA, CO, FL, GA, HI, NM, NV, NY, OR | 0 |
| `x_plant` | The plant's name as LBNL writes it, underscores turned to spaces (the source's name: Plant_Name) | none | text | for example AES Kekaha, AES Lawai, Arica PPA1; 113 distinct | 0 |
| `x_eia_id` | The EIA id or ids LBNL gives for the plant (a retrofit gives the PV plant's and the battery's, as 58542/65857); 0 as the sheet gives it (the source's name: EIA ID) | none | text | for example 0, 57242, 58462; 82 distinct | 0 |
| `x_year_added` | LBNL's 'Year added' field as the sheet gives it (2025 or 0) (the source's name: Year added) | none | integer | 0, 2025 | 0 |
| `x_pv_mwh_year` | The PV plant's average annual output (the source's name: Avg Annual PV MWh) | MWh | number | 22221.810000000045 to 2097970.296116577; 109 distinct | 0 |
| `x_bess_mw` | The battery's power capacity (the source's name: BESS MW) | MW | number | 1.0 to 700.0; 54 distinct | 0 |
| `x_bess_mwh` | The battery's energy capacity (the source's name: BESS MWh) | MWh | number | 2.0 to 2800.0; 56 distinct | 0 |
| `x_bess_duration_h` | The battery's duration: hours it can discharge at full power (the source's name: BESS Duration) | hour | number | 2.0, 2.5, 3.0, 3.726315789473684, 4.0, 5.0, 8.0 | 0 |
| `x_bess_pv_ratio` | The ratio of battery power capacity to PV capacity (the source's name: BESS:PV Ratio) | ratio | number | 0.042016806722689 to 1.0; 51 distinct | 0 |
| `x_pv_equivalent_duration_h` | The PV-equivalent duration: battery energy capacity over PV capacity (the source's name: PV-Equivalent Duration (Storage Energy / PV Capacity)) | hour | number | 0.0909090909090909 to 8.0; 53 distinct | 0 |
| `x_pv_usd_mwh` | The PV part of the price, levelized, real 2024 USD per MWh (the source's name: PV_$_per_MWh_real) | USD/MWh | number | 12.397981981671771 to 148.40069722446546; 72 distinct | 39: LBNL's cell is blank |
| `x_bess_adder_usd_mwh_pv` | The battery adder to the price, real 2024 USD per MWh of PV output (the source's name: BESS_$_per_MWh-PV_real) | USD/MWh | number | 2.338283787247718 to 58.58756991183108; 75 distinct | 38: LBNL's cell is blank |
| `x_bess_adder_usd_mwh_stored` | The battery adder, real 2024 USD per MWh stored (the source's name: BESS_$_per_MWh-stored_real) | USD/MWh | number | 38.14808048331824 to 115.23324026159628; 73 distinct | 38: LBNL's cell is blank |
| `x_bess_adder_usd_mw_month` | The battery adder, real 2024 USD per MW of battery a month (the source's name: BESS_$_per_MW-month_real) | USD/MW-month | number | 4481.475301109149 to 14031.761477159243; 73 distinct | 38: LBNL's cell is blank |
| `x_pv_ppa_execution` | The date the PV PPA was executed (the source's name: PV PPA Execution) | none | date | 2009-08-17 to 2025-06-13; 82 distinct | 0 |
| `x_bess_ppa_execution` | The date the battery PPA was executed (the source's name: BESS PPA Execution) | none | date | 2015-09-09 to 2025-06-13; 78 distinct | 0 |
| `x_pv_cod` | The PV plant's commercial operation date (the source's name: PV COD) | none | date | 2014-10-22 to 2029-07-01; 80 distinct | 0 |
| `x_bess_cod` | The battery's commercial operation date (the source's name: BESS COD) | none | date | 2017-03-31 to 2029-07-01; 77 distinct | 0 |
| `x_retrofit_execution` | The date the retrofit's contract was executed (the source's name: Retrofit_Execution) | none | date | 2020-04-09, 2020-04-22, 2020-05-13, 2020-05-29, 2021-10-18, 2021-11-19, 2023-09-27 | 102: Not a retrofit |
| `x_retrofit_cod` | The retrofit battery's commercial operation date (the source's name: Retrofit_COD) | none | date | 2021-03-31, 2021-05-31, 2021-07-31, 2021-09-01, 2021-10-01, 2022-03-31, 2022-08-28, 2022-10-01, 2026-02-01 | 102: Not a retrofit |
| `x_dollar_year` | The year of the real dollars the prices are in | none | integer | 2024 | 0 |

Waiting for a second look: x_year_added: LBNL's 'Year added' holds 2025 on 9 rows and 0 on 104; no note or connector says what 0 means (presumably earlier editions, not confirmed)..

### `lbnl_interconnection_queue`

One interconnection request (a project's request to connect to the grid) in Berkeley Lab and GridTracker's Queued Up data file, 2026 edition, requests through the end of 2025, across the seven ISOs and the West and Southeast outside them.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 38201.

- **Time:** No time column; status_date is the online date (operating), the withdrawal date (withdrawn) or the request date; vintage is the edition ('2026 edition (through 2025)').
- **Revisions:** A snapshot of one edition; a run replaces the table. Rebuilt from the ERW archive in session 305.
- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/lbnl_interconnection_queue.md`](../methods/lbnl_interconnection_queue.md)
- **Cite as:** Lawrence Berkeley National Laboratory and GridTracker. Queued Up: 2026 Edition, data file (requests through 2025). Via the Energy Research Warehouse (ERW), table `lbnl_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: lbnl:<Berkeley Lab's entity>:<q_id>; a repeated pair takes its row number after a colon | none | text | for example lbnl:AEC:GI-100, lbnl:AEC:GI-101, lbnl:AEC:GI-102; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The project name, else the q_id | none | text | for example (Offshore wind Increase (Q700 +Q1154), (SolarReserve), 0; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>; empty where the file gives no state | none | text | for example US-AL, US-AR, US-AZ; 52 distinct | 1235 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 38201 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 38201 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: mw_1 + mw_2 + mw_3, as Berkeley Lab adds them for a hybrid; 16 rows negative as the file gives them | MW | number | -75.0 to 16875.0; more than 5000 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: From q_status: active, withdrawn, suspended, operational written operating; empty for unknown | none | text | active, operating, suspended, withdrawn | 10 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: on_date for operating, wd_date for withdrawn, else q_date | none | date | 1982-06-30 to 2026-01-16; more than 5000 distinct | 10230 |
| `operator` | The operator or owner, as the publisher writes it. Here: The utility | none | text | for example ABB Equity Ventures Inc, AEC, AECC; 386 distinct | 7855 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:queued_up | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The edition, as text | none | text | 2026 edition (through 2025) | 0 |
| `q_id` | The request's queue identifier as Berkeley Lab's file gives it (9 are dates as Excel turned them) | none | text | for example 0, 0089A, 0089B; more than 5000 distinct | 0 |
| `q_status` | Berkeley Lab's status of the request: active, suspended, operational, withdrawn or unknown | none | text | active, operational, suspended, unknown, withdrawn | 0 |
| `q_date` | The date the request entered the queue | none | date | 1995-11-08 to 2025-12-24; more than 5000 distinct | 665: The file gives no request date |
| `prop_date` | The proposed operation date of the request | none | date | 1980-12-31 to 2057-09-01; 3723 distinct | 5265: The file gives no proposed date |
| `on_date` | The date the project began operating (its online date) | none | date | 1982-06-30 to 2025-12-31; 1891 distinct | 34492: Not operating, or no online date given |
| `wd_date` | The date the request was withdrawn | none | date | 1999-06-26 to 2026-01-16; 4119 distinct | 22578: Not withdrawn, or no withdrawal date given |
| `ia_date` | The date of the signed interconnection agreement | none | date | 1999-08-25 to 2025-12-31; 2741 distinct | 33368: The file gives no agreement date |
| `ia_phase` | The study phase of the request (Feasibility Study, System Impact Study, Facility Study, IA Executed meaning a signed agreement, and the others) (the source's name: IA_phase_clean) | none | text | Cluster Study, Construction, Facility Study, Feasibility Study, IA Executed, IA Pending, In Progress (unknown study), Not Started, Suspended, System Impact Study, Withdrawn | 7167: The file gives no phase |
| `region` | Berkeley Lab's region: the seven ISOs, West and Southeast (outside the ISOs) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP, Southeast, West | 0 |
| `lbnl_entity` | The transmission provider whose queue holds the request: Berkeley Lab's entity field (the source's name: entity) | none | text | for example AEC, APS, Avista; 57 distinct | 0 |
| `utility` | The file's own utility field | none | text | for example ABB Equity Ventures Inc, AEC, AECC; 386 distinct | 7855: The file names no utility |
| `state` | The state as the file gives it | none | text | for example AL, AR, AZ; 52 distinct | 1235: The file gives no state |
| `county` | The county as the file gives it | none | text | for example Abbeville, Acadia Parish, Accomack; 1673 distinct | 2063: The file gives no county |
| `fips_code` | The FIPS code the file gives, which places the request with its state and county (filled values end in '.0' on the data machine) | none | number | 1001.0 to 3610136003.0; 2637 distinct | 1770: The file gives no code |
| `poi_name` | not documented by the source | none | text | for example "18CAMPBELLW‚Äù, ‚Äú18CAMPBELLB, # 7044 Marion 345kV, # 79601 Stillman Substation 138 kV; more than 5000 distinct | 2813: The file's cell is blank |
| `service` | not documented by the source | none | text | ERIS, NRIS, NRIS/ERIS, Other | 10797: The file's cell is blank |
| `project_type` | not documented by the source | none | text | Generation, Replacement, Surplus, Upgrade | 1224: The file's cell is blank |
| `type_clean` | Berkeley Lab's clean type of the request (Solar, Battery, Gas, Wind, Solar+Battery and the others) | none | text | for example Battery, Battery+Other Storage, Coal; 49 distinct | 0 |
| `type_1` | The type of the request's first part | none | text | Battery, Coal, Diesel, Gas, Geothermal, Hydro, Hydrogen, Nuclear, Offshore Wind, Oil, Other, Other Storage, Solar, Wind | 0 |
| `type_2` | The type of the request's second part (a hybrid's) | none | text | Battery, Coal, Diesel, Gas, Geothermal, Hydro, Oil, Other, Other Storage, Wind | 33144: The request has one part |
| `type_3` | The type of the request's third part | none | text | Battery, Diesel, Other, Other Storage | 38091: The request has fewer than three parts |
| `mw_1` | The capacity of the request's first part, as filed | MW | number | -75.0 to 16875.0; more than 5000 distinct | 0 |
| `mw_2` | The capacity of the request's second part, as filed | MW | number | 1.0 to 2107.4; 431 distinct | 37105: The request has one part |
| `mw_3` | The capacity of the request's third part, as filed | MW | number | 1.0, 100.0, 1200.0, 1403.0, 151.6, 1650.0, 185.0, 203.94, 204.16, 204.93, 205.92, 207.92, 252.0, 28.38, 304.668, 310.3, 375.0, 405.9, 406.098, 500.0, 515.1, 60.0, 600.0, 90.0, 990.0 | 38156: The request has fewer than three parts |
| `q_year` | The year the request entered the queue (filled values end in '.0' on the data machine) | none | number | 1995.0 to 2025.0; 30 distinct | 665: The file gives no year entered |
| `prop_year` | not documented by the source | none | number | 1980.0 to 2057.0; 50 distinct | 5265: The file gives none (as prop_date) |

Waiting for a second look: poi_name, service (ERIS, NRIS, NRIS/ERIS, Other) and project_type (Generation, Replacement, Surplus, Upgrade): Berkeley Lab's own codebook sheet ('04. Data Codebook') defines them, but the repository holds no copy of it and no method note or connector says what they mean.; prop_year: no note says it is the year of prop_date, though it is empty on exactly the rows prop_date is (5,265)..

### `lbnl_ppa_prices`

One wind or PV-only solar power purchase agreement in Berkeley Lab's wind (2026 Edition) and solar (2025 Data Update) data files; LBNL names no project.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 1133.

- **Time:** No time column; event_date is the PPA's execution date.
- **Revisions:** Rewritten whole by each run from the two data files; one edition each, no vintage column.
- **Source:** lbnl:ppa_prices Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update (2026 Edition) and Utility-Scale Solar (2025 Data Update), https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0 and (https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data)
- **Method note:** [`docs/methods/lbnl_ppa_prices.md`](../methods/lbnl_ppa_prices.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Land-Based Wind Energy Technology Data Update; Utility-Scale Solar Data Update (PPA prices). Via the Energy Research Warehouse (ERW), table `lbnl_ppa_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: lbnl_ppa:<wind\|solar>:<12 hex of the row's date, MW, term, region and price>, -2 for a second identical row | none | text | for example lbnl_ppa:solar:001ddbf2dd21, lbnl_ppa:solar:004e49177129, lbnl_ppa:solar:0077932d1984; 1133 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1996-09-06 to 2025-06-13; 827 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: Always ppa | none | text | ppa | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 1133 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 1133 |
| `mw` | The capacity involved, in megawatts. Here: The contract capacity | MW | number | 1.98 to 700.0; 440 distinct | 0 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Levelized over the term after escalation and time-of-delivery factors, 4 percent real discount rate, in real USD of x_dollar_year per MWh | the row's currency per MWh, unless the table's file says otherwise | number | 9.6475 to 363.3955; 1076 distinct | 0 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | text | USD | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1133 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:ppa_prices | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx, https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:19Z, 2026-10-23T08:30:21Z | 0 |
| `x_technology` | The technology: wind or solar (PV only) | none | text | solar, wind | 0 |
| `x_term_years` | The contract's term (the source's name: Term (years)) | year | number | 3.0 to 35.0; 34 distinct | 0 |
| `x_region` | LBNL's region: an ISO (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP), West (non-ISO), Southeast (non-ISO) or Hawaii (the source's name: Region (wind); the region column holding the price (solar)) | none | text | CAISO, ERCOT, Hawaii, ISO-NE, MISO, NYISO, PJM, SPP, Southeast (non-ISO), West (non-ISO) | 0 |
| `x_macro_region` | LBNL's consolidated region (wind: West, Central, East; solar: Hawaii, West, Central, Northeast, Southeast) (the source's name: Macro Region) | none | text | Central, East, Hawaii, Northeast, Southeast, West | 0 |
| `x_price_unit` | The price's unit in words: USD/MWh, levelized, real dollars of the dollar year | none | text | USD/MWh, levelized, real 2024 dollars, USD/MWh, levelized, real 2025 dollars | 0 |
| `x_dollar_year` | The year of the real dollars the price is in: 2025 for wind, 2024 for solar | none | integer | 2024, 2025 | 0 |

### `lbnl_solar_projects`

One utility-scale solar project (PV or concentrating solar) in Berkeley Lab's Utility-Scale Solar, 2025 Data Update, with its place, technology, size, design, storage, offtaker, value, cost, PPA price and yearly capacity factors.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1775.

- **Time:** No time column; status_date is the solar commercial operation date. vintage is the data file's time (UTC).
- **Revisions:** Rewritten whole by each run from the data file lbnl_ppa_prices.py saves; one edition.
- **Source:** lbnl:solar_projects Lawrence Berkeley National Laboratory, Utility-Scale Solar, 2025 Data Update (October 2025) (https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data)
- **Method note:** [`docs/methods/forecast.md`](../methods/forecast.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Utility-Scale Solar Data Update (Individual_Project_Data). Via the Energy Research Warehouse (ERW), table `lbnl_solar_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: lbnl_solar:<EIA ID as LBNL writes it, suffixes such as ret, a, b kept>, or lbnl_solar:none-<name> where it gives none | none | text | for example lbnl_solar:10437, lbnl_solar:10437ret, lbnl_solar:10438; 1775 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always plant | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The project's name | none | text | for example (City of) Corcoran Solar (formerly Cottonwood 2), (City of) Phoenix (Desert Star) (Landfill SR85), (Tenaska) Imperial Solar Energy Center South (CSolar IV South); 1775 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 48 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 19.90201 to 61.587441; 1758 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -159.759451 to -68.364341; 1760 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The AC capacity (MW-AC) | MW | number | 5.001 to 690.0; 497 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: LBNL lists projects that reached commercial operation | none | empty | no cell holds a value | 1775 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The solar commercial operation date | none | date | 1984-12-31 to 2024-12-31; 367 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 1775 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:solar_projects | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-10-15T19:03:15Z | 0 |
| `eia_id` | The project's EIA ID as LBNL writes it (a suffix such as 'ret' kept) (the source's name: EIA ID) | none | text | for example 10437, 10437ret, 10438; 1772 distinct | 3: LBNL gives no EIA id |
| `cod_year` | The year of the solar commercial operation date (the source's name: Solar COD Year) | none | integer | 1984, 1985, 1986, 1987, 1988, 1989, 1990, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 0 |
| `region` | LBNL's region: an ISO, Southeast (non-ISO), West (non-ISO), AK or HI (the source's name: Region) | none | text | AK, CAISO, ERCOT, HI, ISO-NE, MISO, NYISO, PJM, SPP, Southeast (non-ISO), West (non-ISO) | 0 |
| `state` | The state, two-letter postal code (the source's name: State) | none | text | for example AK, AL, AR; 48 distinct | 0 |
| `ghi_kwh_m2_day` | The site's average irradiance (GHI), in kWh per square metre a day (the source's name: Avg GHI) | kWh/m2/day | number | 3.4574997717 to 5.9509810502; 1300 distinct | 1: LBNL's cell is blank |
| `technology` | The main solar technology: PV or CSP (the source's name: Solar Tech Main) | none | text | CSP, PV | 0 |
| `technology_sub` | The technology's sub-type (c-Si, Thin-Film, CPV, Trough, Tower and combinations) (the source's name: Solar Tech Sub) | none | text | CPV, Combo (c-Si, CPV), Combo (c-Si, Thin-Film, CPV), Thin-Film, Tower, Trough, c-Si | 6: LBNL's cell is blank |
| `capacity_dc_mw` | The project's DC capacity (the source's name: Solar Capacity MW-DC) | MW | number | 5.4 to 966.8; 1210 distinct | 49: LBNL's cell is blank |
| `ilr` | The inverter loading ratio, as LBNL gives it (the source's name: ILR) | ratio | number | 1.0 to 2.3291341731653668; 1229 distinct | 49: LBNL's cell is blank |
| `mount` | The mount: Fixed Tilt, Tracking or Combo (the source's name: Mount) | none | text | Combo, Fixed Tilt, Tracking | 0 |
| `tracking` | The tracking type as LBNL writes it (Single Axis, Dual Axis, Fixed Tilt and variants) (the source's name: Tracking Type) | none | text | Dual Axis, Dual-Axis, Fixed Tilt, Fixed, Single, Fixed, Single, Double, Single Asis, Single Axis | 0 |
| `tilt` | The panels' tilt as LBNL gives it (text; no unit is stated) (the source's name: Tilt) | none | text | for example 0, 10, 12; 28 distinct | 189: LBNL's cell is blank |
| `azimuth_deg` | The panels' azimuth, in degrees (the source's name: Azimuth) | degree | number | 52.0 to 238.0; 48 distinct | 21: LBNL's cell is blank |
| `hybrid` | The hybrid configuration (PV+Storage, PV+Fossil and others), or LBNL's note (the source's name: Hybrid?) | none | text | CSP+Storage, PV+Fossil, PV+Geothermal, PV+Geothermal+CSP, PV+Hydrogen, PV+Storage, PV+Storage+Backup Generator, PV+Storage+Fossil, PV+Wind, Wind+PV, Wind+PV+Storage, colocated with nearby Atrisco Energy Storage - not sure whether they share same POI, has different EIA ID | 1577: Not a hybrid |
| `storage_technology` | The storage technology as LBNL writes it (LIB, Lithium-Ion, LFP and others) (the source's name: Storage Tech) | none | text | Battery, LFP, LIB, Lead Acid, Lithium iron phosphate, Lithium-Ion, Lithium-ion, Molten Salt, NIB, Zinc | 1586: No storage, or not given |
| `storage_coupling` | How the storage is coupled: AC or DC (the source's name: Storage Coupling) | none | text | AC, DC | 1593: No storage, or not given |
| `storage_cod_year` | The year the storage began commercial operation (the source's name: Storage COD Year) | none | integer | 2012, 2013, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 1570: No storage, or not given |
| `storage_mw` | The storage's power capacity (the source's name: Storage Capacity MW) | MW | number | 0.0 to 409.0; 97 distinct | 1569: No storage, or not given |
| `storage_mwh` | The storage's energy capacity (the source's name: Storage Energy MWh) | MWh | number | 0.0 to 1680.0; 122 distinct | 1571: No storage, or not given |
| `energy_value_2024_usd_mwh` | The project's 2024 energy value, in 2024 USD per MWh (the source's name: 2024 Energy Value ($/MWh)) | USD/MWh | number | -56.23 to 174.08; 1061 distinct | 322: LBNL's cell is blank |
| `capacity_value_2024_usd_mwh` | The project's 2024 capacity value, in 2024 USD per MWh (the source's name: 2024 Capacity Value ($/MWh)) | USD/MWh | number | 0.64 to 51.16; 979 distinct | 453: LBNL's cell is blank |
| `lcoe_no_credits_2024_usd_mwh` | The PV levelized cost of energy without tax credits, in 2024 USD per MWh (the source's name: PV LCOE no Tax Credits (2024$/MWh)) | USD/MWh | number | 20.35 to 484.76; 1508 distinct | 146: LBNL's cell is blank |
| `lcoe_with_credits_2024_usd_mwh` | The PV levelized cost of energy with federal tax credits, in 2024 USD per MWh (the source's name: PV LCOE with Federal Tax Credits (2024$/MWh)) | USD/MWh | number | 14.88 to 315.1; 1460 distinct | 146: LBNL's cell is blank |
| `offtaker` | The type of buyer of the output (Investor-owned Utility, Corporate, Public Utilities, Merchant and others) (the source's name: Offtaker Type) | none | text | Corporate, Education, Investor-owned Utility, Investor-owned Utility and Corporate, Merchant, Military, Monopoly Investor-owned Utility, Non-IOU Retailer, Other, Public Utilities, Public Utilities and Corporate, Unknown | 0 |
| `ppa_2024_usd_mwh` | The levelized PPA (power purchase agreement) price, in 2024 USD per MWh (the source's name: Levelized PV PPA 2024$/MWh) | USD/MWh | number | 15.864736186255652 to 363.3954928781191; 412 distinct | 1350: No PPA price given |
| `cf_2008` | The project's capacity factor in 2008, a fraction, as LBNL gives it (the source's name: 2008 Capacity Factor) | ratio | number | 0.0883110926321902, 0.106405585913782, 0.175282538499751, 0.19451947756251, 0.212025110590684, 0.218235926115664, 0.218436117616445, 0.229723899913718, 0.23073584081637, 0.230809073381693, 0.308325743776563 | 1764: LBNL's cell for 2008 is blank |
| `cf_2009` | The project's capacity factor in 2009, a fraction, as LBNL gives it (the source's name: 2009 Capacity Factor) | ratio | number | 0.0709094368340943, 0.0747220567798292, 0.170550539643005, 0.181294105437941, 0.192270058708414, 0.199671553312504, 0.204664057403783, 0.210189190632593, 0.211449482628081, 0.212165211354108, 0.247271689497716, 0.30441400304414 | 1763: LBNL's cell for 2009 is blank |
| `cf_2010` | The project's capacity factor in 2010, a fraction, as LBNL gives it (the source's name: 2010 Capacity Factor) | ratio | number | 0.0868683409436834, 0.08808153001125, 0.181339955673048, 0.191898238747553, 0.200369168736147, 0.202279213366542, 0.207358121330724, 0.210566370263558, 0.212612858032378, 0.221644502216445, 0.241392694063926, 0.243566210045662, 0.271010002174385, 0.297762842465753 | 1761: LBNL's cell for 2010 is blank |
| `cf_2011` | The project's capacity factor in 2011, a fraction, as LBNL gives it (the source's name: 2011 Capacity Factor) | ratio | number | 0.0923499437495863, 0.0996879756468797, 0.159319054867, 0.187142857142857, 0.192541856925418, 0.193499673842139, 0.194575895945758, 0.197777864259028, 0.201777751074795, 0.204778498758311, 0.208211394769613, 0.209511125607016, 0.213750291637502, 0.215091324200913, 0.235200880391577, 0.236735159817351, 0.245958904109589, 0.253265197849231, 0.256953957382039, 0.27872907153729, 0.293571256909396, 0.305598458904109 | 1753: LBNL's cell for 2011 is blank |
| `cf_2012` | The project's capacity factor in 2012, a fraction, as LBNL gives it (the source's name: 2012 Capacity Factor) | ratio | number | 0.0953476017000607 to 0.3091985428051; 51 distinct | 1724: LBNL's cell for 2012 is blank |
| `cf_2013` | The project's capacity factor in 2013, a fraction, as LBNL gives it (the source's name: 2013 Capacity Factor) | ratio | number | 0.0777827410495665 to 0.32707248297594; 91 distinct | 1684: LBNL's cell for 2013 is blank |
| `cf_2014` | The project's capacity factor in 2014, a fraction, as LBNL gives it (the source's name: 2014 Capacity Factor) | ratio | number | 0.0289611872146118 to 0.349160143509458; 133 distinct | 1642: LBNL's cell for 2014 is blank |
| `cf_2015` | The project's capacity factor in 2015, a fraction, as LBNL gives it (the source's name: 2015 Capacity Factor) | ratio | number | 0.103914367017404 to 0.357354859752119; 192 distinct | 1583: LBNL's cell for 2015 is blank |
| `cf_2016` | The project's capacity factor in 2016, a fraction, as LBNL gives it (the source's name: 2016 Capacity Factor) | ratio | number | 0.0991412958626073 to 0.373428961748633; 271 distinct | 1500: LBNL's cell for 2016 is blank |
| `cf_2017` | The project's capacity factor in 2017, a fraction, as LBNL gives it (the source's name: 2017 Capacity Factor) | ratio | number | 0.0436166459111664 to 0.352345890410958; 414 distinct | 1354: LBNL's cell for 2017 is blank |
| `cf_2018` | The project's capacity factor in 2018, a fraction, as LBNL gives it (the source's name: 2018 Capacity Factor) | ratio | number | 0.0826247834986616 to 0.354343835616438; 568 distinct | 1205: LBNL's cell for 2018 is blank |
| `cf_2019` | The project's capacity factor in 2019, a fraction, as LBNL gives it (the source's name: 2019 Capacity Factor) | ratio | number | 0.0232800608828006 to 0.361480365296803; 664 distinct | 1110: LBNL's cell for 2019 is blank |
| `cf_2020` | The project's capacity factor in 2020, a fraction, as LBNL gives it (the source's name: 2020 Capacity Factor) | ratio | number | 0.0528460837887067 to 0.364961986220004; 765 distinct | 1009: LBNL's cell for 2020 is blank |
| `cf_2021` | The project's capacity factor in 2021, a fraction, as LBNL gives it (the source's name: 2021 Capacity Factor) | ratio | number | 0.0469634703196347 to 0.350644977168949; 918 distinct | 852: LBNL's cell for 2021 is blank |
| `cf_2022` | The project's capacity factor in 2022, a fraction, as LBNL gives it (the source's name: 2022 Capacity Factor) | ratio | number | 0.0361757990867579 to 0.369908675799086; 1052 distinct | 720: LBNL's cell for 2022 is blank |
| `cf_2023` | The project's capacity factor in 2023, a fraction, as LBNL gives it (the source's name: 2023 Capacity Factor) | ratio | number | 0.0620267614588752 to 0.353754794520547; 1237 distinct | 533: LBNL's cell for 2023 is blank |
| `cf_2024` | The project's capacity factor in 2024, a fraction, as LBNL gives it (the source's name: 2024 Capacity Factor) | ratio | number | 0.0699704295496991 to 0.377132513661202; 1417 distinct | 355: LBNL's cell for 2024 is blank |

### `lbnl_tracking_the_sun`

One state's customer segment's installed distributed solar systems in one year of installation, one measure, summarised from Berkeley Lab's Tracking the Sun 2024 public data file (one record a system).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8762.

- **Time:** ts_utc is 1 January of the year of installation (a year, not an instant); freq P1Y. The edition holds systems installed to 2023; 2024 is a partial year.
- **Revisions:** Rewritten whole by each run; vintage is the Last-Modified time of the state's file in the data lake (28 February 2025).
- **Source:** lbnl:tracking_the_sun Lawrence Berkeley National Laboratory, Tracking the Sun, public data file, on the Open Energy Data Initiative (https://data.openei.org/submissions/3)
- **Method note:** [`docs/methods/lbnl_tracking_the_sun.md`](../methods/lbnl_tracking_the_sun.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Tracking the Sun: installed distributed solar systems, public data file. Via the Energy Research Warehouse (ERW), table `lbnl_tracking_the_sun`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: tts:<state>_<segment>, lowercase | none | text | for example tts:ar_com, tts:ar_gov, tts:ar_non_profit; 135 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1983-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 41 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 280412.0; 3811 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, USD/kW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AR, US-AZ, US-CA; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8762 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The customer segment as the file writes it (RES, COM, NON-RES, GOV, NON-PROFIT, SCHOOL, or unknown for the file's -1), not a pricing node | none | text | COM, GOV, NON-PROFIT, NON-RES, RES, SCHOOL, unknown | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:tracking_the_sun | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oedi-data-lake.s3.amazonaws.com/tracking-the-sun/2024/state=AR/part-00006-975d0624-ef42-4442-a6b6-46e6cbd8f20b.c000.snappy.parquet, https://oedi-data-lake.s3.amazonaws.com/tracking-the-sun/2024/state=AZ/part-00000-975d0624-ef42-4442-a6b6-46e6cbd8f20b.c000.snappy.parquet, https://oedi-data-lake.s3.amazonaws.com/tracking-the-sun/2024/state=CA/part-00002-975d0624-ef42-4442-a6b6-46e6cbd8f20b.c000.snappy.parquet; 27 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:22:00Z to 2026-10-23T18:50:50Z; 27 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The state's file's Last-Modified time, UTC | none | utc time | 2025-02-28T17:44:25Z, 2025-02-28T17:44:26Z, 2025-02-28T17:44:29Z, 2025-02-28T17:44:30Z, 2025-02-28T17:44:32Z, 2025-02-28T17:44:33Z, 2025-02-28T17:44:34Z, 2025-02-28T17:44:36Z, 2025-02-28T17:44:38Z, 2025-02-28T17:44:41Z | 0 |
| `x_segment` | The customer segment as the file writes it: RES residential, COM commercial, NON-RES non-residential, GOV government, NON-PROFIT, SCHOOL, or unknown for the file's -1 (the source's name: customer_segment) | none | text | COM, GOV, NON-PROFIT, NON-RES, RES, SCHOOL, unknown | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_dc` | The sum of the systems' DC size, in MW DC (the file's kW over 1,000) | MW | 1872 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `price_median` | The median of total installed price over DC size, priced systems only, unscreened, USD per kW (not Berkeley Lab's reported figure) | USD/kW | 1217 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `systems` | The number of systems installed in the year (systems with an installation year) | count | 1891 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `systems_battery` | The systems with a battery (battery_rated_capacity_kwh above zero) | count | 1891 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `systems_priced` | The systems whose installed price and DC size are both above zero | count | 1891 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `lbnl_wind_capacity_factors`

One land-based wind plant's capacity factor in calendar year 2025, from Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1210.

- **Time:** ts_utc is 2025-01-01 (the calendar year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run from the data file lbnl_ppa_prices.py saves; one edition. vintage is the data file's time (UTC).
- **Source:** lbnl:wind_capacity_factors Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026), sheet 'Capacity Factor in 2025 by COD' (https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0)
- **Method note:** [`docs/methods/forecast.md`](../methods/forecast.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Land-Based Wind Energy Technology Data Update (Capacity Factor in 2025 by COD). Via the Energy Research Warehouse (ERW), table `lbnl_wind_capacity_factors`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: lbnl_wind:<EIA plant code> | none | text | for example lbnl_wind:10823, lbnl_wind:1172, lbnl_wind:1998; 1210 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0374804850277611 to 0.624374864100891; 1200 distinct | 0 |
| `unit` | The unit of the row's value | none | text | ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1210 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA plant <code>, not a pricing node: LBNL names no project | none | text | for example EIA plant 10823, EIA plant 1172, EIA plant 1998; 1210 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:wind_capacity_factors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The data file's time, UTC | none | utc time | 2026-08-31T00:14:36Z | 0 |
| `x_cod` | LBNL's commercial operation year or period of the plant (1998-99, 2000-01 and the years after) | none | text | 1998-99, 2000-01, 2002-03, 2004-05, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 0 |
| `x_repower` | Whether the plant was repowered: partial repower or full repower | none | text | full repower, partial repower | 1087: Not repowered |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` | The plant's capacity factor in calendar year 2025, a fraction (ratio) | ratio | 1210 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `lbnl_wind_costs`

One wind cost measure for one year from Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition: a turbine maker's or LBNL's average turbine price, or the installed cost or levelized cost of the projects of a commercial operation year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 119.

- **Time:** ts_utc is 1 January of the year (a year, not an instant); freq P1Y. For capex and lcoe the year is the projects' commercial operation year; for maker turbine prices it is from LBNL's mid-year dates.
- **Revisions:** Rewritten whole by each run from the data file lbnl_ppa_prices.py saves; one edition. vintage is the data file's time (UTC).
- **Source:** lbnl:wind_costs Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026) (https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0)
- **Method note:** [`docs/methods/lbnl_projects.md`](../methods/lbnl_projects.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Land-Based Wind Energy Technology Data Update (turbine prices, CapEx, LCOE). Via the Energy Research Warehouse (ERW), table `lbnl_wind_costs`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: lbnl_wind_cost:<turbine_price\|capex\|lcoe>:<vestas\|sgre\|nordex\|lbnl\|us> | none | text | lbnl_wind_cost:capex:us, lbnl_wind_cost:lcoe:us, lbnl_wind_cost:turbine_price:lbnl, lbnl_wind_cost:turbine_price:nordex, lbnl_wind_cost:turbine_price:sgre, lbnl_wind_cost:turbine_price:vestas | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1983-01-01T00:00:00Z to 2025-06-30T00:00:00Z; 52 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 39.83157083728906 to 5618.100071623097; 119 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, USD/kW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US; empty on the makers' global average turbine prices (40 rows) | none | text | US | 40 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 119 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not a pricing node: the sheet's block heading for turbine prices (as 'Vestas global average', 'Average Turbine Price'), else 'projects of COD <year>' | none | text | for example Average Turbine Price, Nordex global average, SGRE global average; 35 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:wind_costs | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The data file's time, UTC | none | utc time | 2026-08-31T00:14:36Z | 0 |
| `x_sample` | The number of projects in the year's sample | count | integer | 4 to 131; 31 distinct | 60: Empty on turbine price rows |
| `x_sample_mw` | The capacity of the LCOE sample's projects | MW | number | 46.67 to 17184.1; 28 distinct | 91: Empty on turbine price and capex rows (LCOE only) |
| `x_dollar_year` | The year of the real dollars the values are in | none | integer | 2025 | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capex` | The capacity-weighted installed project cost of the commercial operation year's projects, real 2025 USD per kW | USD/kW | 31 | 1983-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `lcoe` | The generation-weighted levelized cost of energy of the commercial operation year's projects, real 2025 USD per MWh | USD/MWh | 28 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `turbine_price` | The wind turbine price in real 2025 USD per kW: a maker's global average (Vestas, SGRE, Nordex) at LBNL's mid-year dates, or LBNL's US average a year | USD/kW | 60 | 2005-06-30T00:00:00Z | 2025-06-30T00:00:00Z |

### `lbnl_wind_turbine_orders`

One reported US wind turbine order and its price, from the 'Wind Turbine Prices' sheet of Berkeley Lab's Land-Based Wind Energy Technology Data Update, 2026 Edition; LBNL names no buyer, maker or size.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 122.

- **Time:** No time column; event_date is the order date.
- **Revisions:** Rewritten whole by each run from the data file lbnl_ppa_prices.py saves; one edition, no vintage column.
- **Source:** lbnl:wind_costs Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026) (https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0)
- **Method note:** [`docs/methods/lbnl_projects.md`](../methods/lbnl_projects.md)
- **Cite as:** Lawrence Berkeley National Laboratory (Berkeley Lab). Land-Based Wind Energy Technology Data Update (turbine prices, CapEx, LCOE). Via the Energy Research Warehouse (ERW), table `lbnl_wind_turbine_orders`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: lbnl_turbine_order:<12 hex of the date and price> | none | text | for example lbnl_turbine_order:0121b0cee60b, lbnl_turbine_order:062d49ea1b06, lbnl_turbine_order:070a511dac68; 122 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1997-02-01 to 2016-07-01; 93 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: Always turbine_order | none | text | turbine_order | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 122 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 122 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 122 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: USD per kW (real 2025 dollars), not per MWh | the row's currency per MWh, unless the table's file says otherwise | number | 843.3067 to 2947.8718; 121 distinct | 0 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | text | USD | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 122 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | lbnl:wind_costs | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:30:19Z | 0 |
| `x_price_unit` | The price's unit in words: USD/kW, real 2025 dollars | none | text | USD/kW, real 2025 dollars | 0 |
| `x_dollar_year` | The year of the real dollars the price is in | none | integer | 2025 | 0 |

