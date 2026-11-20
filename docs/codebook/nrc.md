# Codebook: nrc

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 7 public tables (2 entities, 4 events, 1 series; tiers: 7 source); 1 documented in full.

- [`nrc_advanced_reactor_preapplicants`](#nrc_advanced_reactor_preapplicants): U.S. Nuclear Regulatory Commission, the applicants, vendors and research or test reactors in pre-application engagement for advanced reactors, by technology (session 2001)
- [`nrc_event_notifications`](#nrc_event_notifications): U.S. Nuclear Regulatory Commission, Event Notification Reports, power reactors: each report and unit, with the unit's power before and after and the 10 CFR sections it was reported under (session 2043)
- [`nrc_license_actions`](#nrc_license_actions): U.S. Nuclear Regulatory Commission, renewed reactor licenses and approved power uprates (session 2064)
- [`nrc_new_reactor_applications`](#nrc_new_reactor_applications): U.S. Nuclear Regulatory Commission, the advanced reactor applications under review, one row an application with its applicant, kind, place, design, power and milestones (session 2001)
- [`nrc_power_reactors`](#nrc_power_reactors): One US power reactor unit, operating (on the NRC's List of Power Reactor Units) or in decommissioning (the NRC's decommissioning dataset), with the NRC datasets' licensing dates and capacity.
- [`nrc_reactor_status`](#nrc_reactor_status): NRC Power Reactor Status, each US reactor's power by day (session 133)
- [`nrc_rop_findings`](#nrc_rop_findings): U.S. Nuclear Regulatory Commission, Reactor Oversight Process findings and violations, 18,240 findings at 66 sites, issued 1999-07-29 to 2025-05-12 (session 2178)

### `nrc_advanced_reactor_preapplicants`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 43.

- **Source:** nrc:new_reactors U.S. Nuclear Regulatory Commission, Advanced Reactors: Who We're Working With (https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with)
- **Method note:** [`docs/methods/nrc_new_reactors.md`](../methods/nrc_new_reactors.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Advanced Reactors: application projects and pre-application activities. Via the Energy Research Warehouse (ERW), table `nrc_advanced_reactor_preapplicants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example nrc_preapp:aalo-atomics-idaho-nuclear-project, nrc_preapp:abilene-christian-university, nrc_preapp:advanced-float-co-ltd; 43 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example ARC Clean Technology, Aalo Atomics, Abilene Christian University; 43 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 43 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 43 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 43 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 43 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 43 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 43 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 43 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:new_reactors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:09:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T13:32:13Z | 0 |
| `x_technology` | not yet written |  | text | High Temperature Gas Reactors, Light Water Reactors, Liquid Metal Cooled Reactors, Molten Salt Reactors / Molten Chloride Fast Reactors, Other Designs/ Not Specified | 1 |
| `x_microreactor` | not yet written |  | text | no, yes | 0 |
| `x_active` | not yet written |  | text | no, yes | 0 |
| `x_page` | not yet written |  | text | for example https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/aalo-atomics-idaho-nuclear-project, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/abilene-christian-university, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/advanced-float-co-ltd; 43 distinct | 0 |

### `nrc_event_notifications`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 25.

- **Source:** nrc:event_notification_reports U.S. Nuclear Regulatory Commission, Operations Center, Event Notification Reports (https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports)
- **Method note:** [`docs/methods/nrc_event_notifications.md`](../methods/nrc_event_notifications.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Event Notification Reports (power reactors). Via the Energy Research Warehouse (ERW), table `nrc_event_notifications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | nrc_en:57790:1, nrc_en:57793:3, nrc_en:57794:2, nrc_en:57800:1, nrc_en:57800:2, nrc_en:57804:2, nrc_en:57810:2, nrc_en:57813:1, nrc_en:57816:1, nrc_en:57820:1, nrc_en:57822:1, nrc_en:57831:1, nrc_en:57832:1, nrc_en:57833:1, nrc_en:57833:2, nrc_en:57836:1, nrc_en:57836:2, nrc_en:57839:1, nrc_en:57840:1, nrc_en:57840:2, nrc_en:57840:3, nrc_en:58489:1, nrc_en:58490:3, nrc_en:58498:2, nrc_en:58501:3 | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | utc time | 2025-05-07T01:08:00Z, 2025-05-30T05:00:00Z, 2025-06-06T16:00:00Z, 2025-06-30T21:41:00Z, 2025-07-02T12:42:00Z, 2025-07-03T00:22:00Z, 2025-07-07T19:45:00Z, 2025-07-13T18:18:00Z, 2025-07-16T14:59:00Z, 2025-07-17T15:00:00Z, 2025-07-21T20:48:00Z, 2025-07-22T19:10:00Z, 2025-07-28T17:33:00Z, 2025-07-29T01:58:00Z, 2025-07-29T04:29:00Z, 2025-07-30T17:30:00Z, 2026-10-10T20:14:00Z, 2026-10-12T12:24:00Z, 2026-10-15T17:05:00Z, 2026-10-17T03:45:00Z | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | reactor_event, reactor_scram | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | Constellation Nuclear, Detroit Edison Co., Dominion Generation, Entergy Nuclear, Exelon Nuclear Co., Indiana/Michigan Power Co., Nebraska Public Power District, Nuclear Management Company, Ppl Susquehanna Llc, Southern Nuclear Operating Company, Tennessee Valley Authority | 4 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 25 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 25 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 25 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 25 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 25 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:event_notification_reports | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261013en, https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261016en, https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261019en, https://www.nrc.gov/sites/default/files/doc_library/reading-rm/doc-collections/event-status/event/event-notification-rpt-lastmonth.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:35:06Z, 2026-10-23T18:38:04Z, 2026-10-23T18:38:05Z, 2026-10-23T18:38:07Z | 0 |
| `x_en_number` | not yet written |  | integer | 57790, 57793, 57794, 57800, 57804, 57810, 57813, 57816, 57820, 57822, 57831, 57832, 57833, 57836, 57839, 57840, 58489, 58490, 58498, 58501 | 0 |
| `x_facility` | not yet written |  | text | Braidwood, Browns Ferry, Calvert Cliffs, Cook, Cooper, Farley, Fermi, Grand Gulf, Hatch, Millstone, Monticello, North Anna, Prairie Island, River Bend, Robinson, Susquehanna, Waterford, Watts Bar | 0 |
| `x_unit` | not yet written |  | integer | 1, 2, 3 | 0 |
| `x_region` | not yet written |  | integer | 1, 2, 3, 4 | 0 |
| `x_state` | not yet written |  | text | AL, CT, GA, IL, LA, MD, MI, MN, MS, NE, PA, SC, TN, VA | 0 |
| `x_county` | not yet written |  | text | Berrien, Calvert, Claiborne, Goodhue, Houston, Limestone, Louisa, Luzerne, Monroe, Nemaha, New London, Rhea, West Feliciana, Will, Wright | 4 |
| `x_docket` | not yet written |  | integer | 05000259, 05000263, 05000282, 05000298, 05000315, 05000338, 05000341, 05000348, 05000387, 05000390, 05000416, 05000456, 05000458 | 7 |
| `x_reactor_type` | not yet written |  | text | [1] CE,[2] CE, [1] GE-3, [1] GE-3,[2] CE,[3] W-4-LP, [1] GE-4, [1] GE-4,[2] GE-4, [1] GE-4,[2] GE-4,[3] GE-4, [1] GE-6, [1] W-2-LP,[2] W-2-LP, [1] W-3-LP,[2] W-3-LP, [1] W-3-LP,[2] W-3-LP,[3] M-4-LP, [1] W-4-LP,[2] W-4-LP, [2] GE-4, [2] W-3-LP, [3] CE | 0 |
| `x_notification_et` | not yet written |  | text | 2025-06-30T20:35:00, 2025-07-02T11:38:00, 2025-07-02T12:11:00, 2025-07-03T17:27:00, 2025-07-07T22:36:00, 2025-07-13T17:10:00, 2025-07-16T13:57:00, 2025-07-17T11:38:00, 2025-07-21T22:51:00, 2025-07-22T17:22:00, 2025-07-29T03:44:00, 2025-07-29T03:45:00, 2025-07-29T09:19:00, 2025-07-29T13:00:00, 2025-07-30T17:20:00, 2025-07-30T23:19:00, 2026-10-10T19:22:00, 2026-10-12T14:37:00, 2026-10-15T16:56:00, 2026-10-17T03:00:00 | 0 |
| `x_notification_utc` | not yet written |  | utc time | 2025-07-01T00:35:00Z, 2025-07-02T15:38:00Z, 2025-07-02T16:11:00Z, 2025-07-03T21:27:00Z, 2025-07-08T02:36:00Z, 2025-07-13T21:10:00Z, 2025-07-16T17:57:00Z, 2025-07-17T15:38:00Z, 2025-07-22T02:51:00Z, 2025-07-22T21:22:00Z, 2025-07-29T07:44:00Z, 2025-07-29T07:45:00Z, 2025-07-29T13:19:00Z, 2025-07-29T17:00:00Z, 2025-07-30T21:20:00Z, 2025-07-31T03:19:00Z, 2026-10-10T23:22:00Z, 2026-10-12T18:37:00Z, 2026-10-15T20:56:00Z, 2026-10-17T07:00:00Z | 0 |
| `x_event_local` | not yet written |  | text | 2025-05-06T21:08:00, 2025-05-30T00:00:00, 2025-06-06T12:00:00, 2025-06-30T16:41:00, 2025-07-02T08:42:00, 2025-07-02T19:22:00, 2025-07-07T15:45:00, 2025-07-13T14:18:00, 2025-07-16T09:59:00, 2025-07-17T11:00:00, 2025-07-21T15:48:00, 2025-07-22T15:10:00, 2025-07-28T13:33:00, 2025-07-28T20:58:00, 2025-07-28T23:29:00, 2025-07-30T12:30:00, 2026-10-10T16:14:00, 2026-10-12T07:24:00, 2026-10-15T13:05:00, 2026-10-16T22:45:00 | 0 |
| `x_event_tz` | not yet written |  | text | CDT, EDT | 0 |
| `x_last_update` | not yet written |  | date | 2025-07-02, 2025-07-09, 2025-07-13, 2025-07-16, 2025-07-17, 2025-07-21, 2025-07-22, 2025-07-29, 2025-07-30, 2026-10-10, 2026-10-12, 2026-10-15, 2026-10-17 | 0 |
| `x_emergency_class` | not yet written |  | text | Non Emergency | 0 |
| `x_cfr` | not yet written |  | text | 21.21(d)(3)(i), 26.719, 50.72(b)(2)(iv)(A); 50.72(b)(2)(iv)(B); 50.72(b)(3)(iv)(A), 50.72(b)(2)(iv)(B), 50.72(b)(2)(iv)(B); 50.72(b)(3)(iv)(A), 50.72(b)(2)(iv)(B); 50.72(b)(3)(v)(C); 50.72(b)(3)(v)(D), 50.72(b)(2)(xi), 50.72(b)(3)(ii)(A), 50.72(b)(3)(iv)(A), 50.72(b)(3)(v)(C), 50.72(b)(3)(v)(D), 50.72(b)(3)(xiii), 50.73(a)(1) | 0 |
| `x_cfr_words` | not yet written |  | text | Accident Mitigation, Defects And Noncompliance, Degraded Condition, ECCS Injection; RPS Actuation - Critical; Valid Specif Sys Actuation, Fitness For Duty, Invalid Specif System Actuation, Loss Comm/Asmt/Response, Offsite Notification, Pot Uncntrl Rad Rel, RPS Actuation - Critical, RPS Actuation - Critical 50.72(b)(3)(iv)(A) - Valid Specif Sys Actuation, RPS Actuation - Critical; Pot Uncntrl Rad Rel; Accident Mitigation, RPS Actuation - Critical; Valid Specif Sys Actuation, Valid Specif Sys Actuation | 0 |
| `x_scram_code` | not yet written |  | text | A/R, M/R, N | 0 |
| `x_rx_crit` | not yet written |  | text | N, Y | 0 |
| `x_initial_power_pct` | not yet written |  | integer | 0, 100, 75, 91, 96 | 0 |
| `x_initial_mode` | not yet written |  | text | Cold Shutdown, Defueled, Hot Shutdown, Power Operation | 0 |
| `x_current_power_pct` | not yet written |  | integer | 0, 100, 91 | 0 |
| `x_current_mode` | not yet written |  | text | Defueled, Hot Shutdown, Hot Standby, Power Operation | 0 |
| `x_read_from` | not yet written |  | text | daily_page, raw_file | 0 |

### `nrc_license_actions`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 236.

- **Source:** nrc:license_renewals_uprates U.S. Nuclear Regulatory Commission, Status of License Renewal Applications and Approved Applications for Power Uprates
- **Method note:** [`docs/methods/nrc_license_actions.md`](../methods/nrc_license_actions.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Status of License Renewal Applications; Approved Applications for Power Uprates. Via the Energy Research Warehouse (ERW), table `nrc_license_actions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example nrc:renewal:arkansas_nuclear_one_1:20000201, nrc:renewal:arkansas_nuclear_one_2:20031015, nrc:renewal:beaver_valley_1_2:20070828; 236 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1977-09-09 to 2026-04-02; 175 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | license_renewal, power_uprate | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | NRC | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 236 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 236 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 236 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 236 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | approved, issued, withdrawn | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:license_renewals_uprates | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/reactors/operating/licensing/power-uprates/status-power-apps/approved-applications.html, https://www.nrc.gov/reactors/operating/licensing/renewal/applications.html | 0 |
| `x_plant` | not yet written |  | text | for example ANO-2, Arkansas Nuclear One 1, Arkansas Nuclear One 2; 156 distinct | 0 |
| `x_application_received` | not yet written |  | date | 1998-04-10 to 2024-02-14; 59 distinct | 172 |
| `x_extended_operation` | not yet written |  | text | for example 01/16/27 (Unit 1) 02/09/29 (Unit 2), 01/18/14, 01/29/16 (Unit 1) 05/27/27 (Unit 2); 61 distinct | 175 |
| `x_note` | not yet written |  | text | Fort Calhoun Station was permanently shut down on October 24, 2016., Kewaunee Power Station was permanently shut down on May 7, 2013., Oyster Creek Nuclear Generating Station was permanently shut down on September 7, 2018., Pilgrim 1 permanently shut down on May 31, 2019, The Crystal River Nuclear Generating Plant, Unit 3 application was withdrawn by the licensee on February 6, 2013. The facility was permanently shut down on February 20, 2013., The previous Diablo Canyon 1 & 2 license renewal application was submitted on November 7, 2018 and withdrawn by the licensee on March 7, 2018. On October 31, 2022, Pacific Gas and Electric sent in a letter to “Request to Resume Review of the Diablo Canyon Power Plant License Renewal Application or, Alternatively, for an Exemption from 10 CFR 2.109(b), Concerning a Timely Renewal Application. ” On March 2, 2023, the NRC granted the exemption., Vermont Yankee Nuclear Power Station was permanently shut down on December 29, 2014. | 229 |
| `x_uprate_type` | not yet written |  | text | E, E(1), MU, S | 64 |
| `x_uprate_pct` | not yet written |  | number | 0.4 to 20.0; 45 distinct | 64 |
| `x_uprate_mwt` | not yet written |  | number | 13.0 to 579.0; 81 distinct | 64 |
| `x_accession` | not yet written |  | text | for example 7907180064*, 7907240100*, 8008280223*; 119 distinct | 64 |
| `x_link` | not yet written |  | text | for example https://www.nrc.gov/licensing-applications/power-reactor-licensing/arkansas-nuclear-one-unit-1--license-renewal-application, https://www.nrc.gov/licensing-applications/power-reactor-licensing/arkansas-nuclear-one-unit-2---license-renewal-application, https://www.nrc.gov/licensing-applications/power-reactor-licensing/beaver-valley-power-station---license-renewal-application; 64 distinct | 172 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:36:10Z, 2026-10-23T20:36:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T19:36:07Z, 2026-10-23T19:51:29Z | 0 |

### `nrc_new_reactor_applications`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 6.

- **Source:** nrc:new_reactors U.S. Nuclear Regulatory Commission, Advanced Reactors: Who We're Working With (https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with)
- **Method note:** [`docs/methods/nrc_new_reactors.md`](../methods/nrc_new_reactors.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Advanced Reactors: application projects and pre-application activities. Via the Energy Research Warehouse (ERW), table `nrc_new_reactor_applications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | nrc_app:dukeenergy, nrc_app:eden-radioisotopes-llc-eden-isotope-production-complex, nrc_app:long-mott-energy-llc, nrc_app:pioneer-units-1-and-2-limited-work-authorization-application, nrc_app:tva-clinch-river-cpa, nrc_app:university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2025-03-31, 2025-04-01, 2025-12-30, 2025-12-31, 2026-03-31, 2026-05-05 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | construction_permit_application, early_site_permit_application, limited_work_authorization_application | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | Duke Energy, Eden Radioisotopes, LLC, Long Mott Energy, LLC, Palisades SMR, LLC, Tennessee Valley Authority (TVA), University of Illinois Urbana-Champaign | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 6 |
| `mw` | The capacity involved, in megawatts | MW | integer | 320 | 5 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 6 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 6 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | Draft Safety Evaluation Report (with information gaps), Finalize Final SEIS and Related Activities ( ML26035A285 ), Issue Environmental Assessment and Finding of No Significant Impact, Review Schedule Established/Schedule Letter Issued to Applicant | 1 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:new_reactors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/dukeenergy, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/eden-radioisotopes-llc-eden-isotope-production-complex, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/long-mott-energy-llc, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/pioneer-units-1-and-2-limited-work-authorization-application, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/tva-clinch-river-cpa, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:09:42Z, 2026-10-23T15:09:44Z, 2026-10-23T15:09:46Z, 2026-10-23T15:09:47Z, 2026-10-23T15:09:49Z, 2026-10-23T15:09:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T13:14:16Z, 2026-10-23T13:17:15Z, 2026-10-23T13:18:52Z, 2026-10-23T13:30:47Z, 2026-10-23T13:31:04Z, 2026-10-23T13:45:04Z | 0 |
| `x_project` | not yet written |  | text | Clinch River Nuclear Site Application, Duke Energy's Belews Creek Early Site Permit Application, Eden Radioisotopes, LLC – Eden Isotope Production Complex, Long Mott Energy, LLC – Long Mott Generating Station Xe-100 Power Reactor Application, Pioneer Units 1 and 2 Limited Work Authorization Application, University of Illinois Urbana-Champaign – KRONOS Micro Modular Reactor (KRONOS MMR™) | 0 |
| `x_when` | not yet written |  | text | Application submitted December 30, 2025; application accepted and currently under review, February 2025 - May 2027 (estimated), April 2025 to present (date of application submittal) February 2022 to April 2025 (pre-application), December 31, 2025 (date of application submittal) to present, March 31, 2025 (date of application submittal), March 31, 2026 (date of application submittal), May 5, 2026 (date of application submittal) | 0 |
| `x_place` | not yet written |  | text | Calhoun County, Texas, Champaign County, Illinois, Lea County, New Mexico | 3 |
| `x_state` | not yet written |  | text | IL, NM, TX | 3 |
| `x_what` | not yet written |  | text | Application for a Construction Permit for a small modular reactor (BWRX-300), Application for a construction permit for a non-power reactor and production facility, Application for a construction permit for a research reactor, Application for a construction permit for an advanced power reactor, Application for an Early Site Permit, Pioneer Units 1 and 2 Phased Construction Permit Application - Limited Work Authorization | 0 |
| `x_reactor_type` | not yet written |  | text | High-Temperature Gas-Cooled Reactor (HTGR), High-temperature gas-cooled reactor (HTGR), Pool-Type Reactor | 3 |
| `x_power_level` | not yet written |  | text | 2 MWth, 4-Module plant with 800 MWth/320 MWe, 45 MWth | 3 |
| `x_fuel` | not yet written |  | text | Annular cylindrical fuel pellets consisting of TRISO fuel particles embedded in ceramic matrix, Graphite Pebbles with TRISO Particle fuel | 4 |
| `x_status_date` | not yet written |  | date | 2026-04-06, 2026-05-18, 2026-06-15, 2026-06-16, 2026-08-31 | 1 |
| `x_next_milestone` | not yet written |  | text | Draft Environmental Impact Statement, Draft Safety Evaluation, Final Safety Evaluation | 2 |
| `x_next_target` | not yet written |  | text | February 2027 – T, May 2027 – T, November 2026 – T, October 31, 2026 – T | 2 |
| `x_decision` | not yet written |  | text | Construction Permit Decision, Construction Permit Decision ( ML26244A257 ) | 4 |
| `x_decision_target` | not yet written |  | text | September 28, 2026, TBD | 4 |
| `x_page` | not yet written |  | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/dukeenergy, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/eden-radioisotopes-llc-eden-isotope-production-complex, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/long-mott-energy-llc, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/pioneer-units-1-and-2-limited-work-authorization-application, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/tva-clinch-river-cpa, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |

### `nrc_power_reactors`

One US power reactor unit, operating (on the NRC's List of Power Reactor Units) or in decommissioning (the NRC's decommissioning dataset), with the NRC datasets' licensing dates and capacity.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 130.

- **Time:** No time column; status_date is the shutdown date for a retired unit. vintage is when the NRC's list or dataset was published or modified (UTC).
- **Revisions:** A snapshot; each run replaces the table whole, asking for the list again and reusing the saved datasets.
- **Source:** nrc:power_reactors U.S. Nuclear Regulatory Commission, List of Power Reactor Units and the operating and decommissioning reactors datasets (https://www.nrc.gov/reactors/operating/list-power-reactor-units.html)
- **Method note:** [`docs/methods/nrc_power_reactors.md`](../methods/nrc_power_reactors.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). List of Power Reactor Units; operating and decommissioning reactors datasets. Via the Energy Research Warehouse (ERW), table `nrc_power_reactors`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: nrc_reactor:<docket number> | none | text | for example nrc_reactor:00500010, nrc_reactor:05000003, nrc_reactor:05000016; 130 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always generator (a reactor unit) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The list's name (the dataset's for a retired unit) | none | text | for example Arkansas Nuclear 1, Arkansas Nuclear 2, Beaver Valley 1; 130 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> from the location's last two letters; empty where none is read | none | text | for example US-AL, US-AR, US-AZ; 36 distinct | 2 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 130 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 130 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The operating dataset's Capacity MWe | MW | number | 519.0 to 1401.0; 84 distinct | 37 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: operating (on the list) or retired (in decommissioning) | none | text | operating, retired | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: A retired unit's shutdown date | none | date | 1963-12-19 to 2021-04-30; 33 distinct | 95 |
| `operator` | The operator or owner, as the publisher writes it. Here: The list's owner and operator | none | text | for example Ameren UE, Arizona Public Service Co., Constellation Energy Generation, LLC; 29 distinct | 35 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:power_reactors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/reactors/operating/list-power-reactor-units.html, https://www.nrc.gov/sites/default/files/doc_library/cdn/legacy/reading-rm/doc-collections/datasets/reactors-decommissioning.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T09:52:20Z, 2026-10-23T09:53:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-09-02T06:28:09Z, 2026-10-22T21:29:39Z | 0 |
| `x_docket` | The NRC docket number of the unit | none | integer | 500010 to 50000289; 130 distinct | 0 |
| `x_license_number` | The unit's NRC license number, from the list (the source's name: License Number) | none | text | for example DPR-18, DPR-19, DPR-20; 95 distinct | 35: A unit in decommissioning (not on the list) |
| `x_reactor_type` | The reactor type (PWR, BWR and others), from the list or the dataset (the source's name: Reactor Type) | none | text | BWR, BWR-MARK 1, Experimental Superheat Reactor, HTG, PWR, PWR CE, SCF | 0 |
| `x_location` | The unit's location in the NRC's words (for example '11 miles SE of Ottawa, IL') (the source's name: Location) | none | text | for example 10 miles SE of Ft. Pierce, FL, 11 miles SE of Ottawa, IL, 12 miles WSW of San Luis Obispo, CA; 82 distinct | 0 |
| `x_nrc_region` | The NRC region (1 to 4), from the list (the source's name: NRC Region) | none | integer | 1, 2, 3, 4 | 35: A unit in decommissioning |
| `x_dataset_year` | The datasets' Year of Update (the source's name: Year of Update) | none | integer | 2022 | 2: On the list but not in the dataset (2 units) |
| `x_architect_engineer` | The unit's architect-engineer, as the operating dataset abbreviates it (the source's name: Architect-Engineer) | none | text | AEP, B&R, BECH, DBDB, DUKE, EBSO, FLUR, G&H, GIL, NIAG, PG&E, PSEG, S&L, S&W, SBEC, SSI, TVA, UE&C, Westinghouse | 37: A unit in decommissioning, or not in the dataset |
| `x_closure_estimate` | The estimated closure year of a unit in decommissioning (the source's name: Closure Date Est.) | none | integer | 2019, 2020, 2025, 2030, 2031, 2032, 2034, 2036, 2053, 2056, 2073, 2074, 2076, 2078, 2079, 2080 | 107: An operating unit, or no estimate given |
| `x_commercial_operation` | The date the unit began commercial operation (the source's name: Commercial Operation) | none | date | 1969-12-01 to 2016-10-19; 91 distinct | 38: A unit in decommissioning, or not in the dataset |
| `x_construction_permit` | The date the construction permit was issued (the source's name: Construction Permit Issued) | none | date | 1965-04-12 to 1978-01-27; 63 distinct | 38: A unit in decommissioning, or not in the dataset |
| `x_constructor` | The unit's constructor, as the operating dataset abbreviates it (the source's name: Constructor Name) | none | text | AEP, B&R, B&W, BALD, BECH, BRRT, CWE, DANI, DUKE, EBSO, GPC, KAIS, NSP, PG&E, S&W, SNC, TVA, UE&C | 37: A unit in decommissioning, or not in the dataset |
| `x_containment_type` | The reactor and containment type (the source's name: Reactor and Containment Type) | none | text | BWR-MARK 1, BWR-MARK 2, BWR-MARK 3, PWR - Freestanding steel vessel with shield building, PWR-DRYAMB, PWR-DRYSUB, PWR-ICECND | 37: A unit in decommissioning, or not in the dataset |
| `x_dataset_name` | The unit's name in the NRC dataset (the source's name: Plant Name, Unit Number (operating); Unit (decommissioning)) | none | text | for example Arkansas Nuclear One, Unit 1, Arkansas Nuclear One, Unit 2, Beaver Valley Power Station, Unit 1; 128 distinct | 2: On the list but not in the dataset (2 units) |
| `x_decommissioning_alternative` | The decommissioning alternative selected (DECON or SAFSTOR) (the source's name: Decommissioning Alternative Selected) | none | text | DECON, SAFSTOR | 95: An operating unit |
| `x_license_expires` | The date the operating license expires (the source's name: Operating License Expires) | none | date | 2024-11-02 to 2062-08-03; 90 distinct | 37: A unit in decommissioning, or not in the dataset |
| `x_license_status` | The current license status of a unit in decommissioning (DECON Completed, DECON In Progress, SAFSTOR) (the source's name: Current License Status) | none | text | DECON Completed, DECON In Progress, SAFSTOR | 96: An operating unit, or none given |
| `x_license_terminated` | The date the operating license was terminated (a unit in decommissioning) (the source's name: Operating License (OL) Terminated) | none | date | 1995-04-11, 1997-08-05, 2005-05-23, 2005-09-30, 2005-11-07, 2007-01-08, 2007-07-27, 2007-08-10, 2007-11-26, 2009-09-25 | 120: An operating unit, or the license not terminated |
| `x_licensed_mwt` | The licensed thermal power of the reactor (the source's name: Licensed MWt (operating); MWt (decommissioning)) | MWt | number | 12.5 to 4408.0; 79 distinct | 2: On the list but not in the dataset (2 units) |
| `x_licensee` | The licensee (the source's name: Licensee) | none | text | for example Arizona Public Service Company, Calvert Cliffs Nuclear Power Plant, LLC – Owner<br> Constellation Energy Generation, LLC – Operator, Comanche Peak Power Company LLC – Owner<br>Vistra Operations Company LLC – Operator; 30 distinct | 37: A unit in decommissioning, or not in the dataset |
| `x_nsss` | The nuclear steam system supplier and design type (the vendor, as the dataset abbreviates it) (the source's name: Nuclear Steam System Supplier and Design Type (operating); NSSS Vendor (decommissioning)) | none | text | AC, B&W, B&W LLP, B&W RLP, CE, CE80-2L, COMB CE, GA, GE, GE 2, GE 3, GE 4, GE 5, GE 6, WEST 2LP, WEST 3LP, WEST 4LP, West, West 2LP, Westinghouse | 2: On the list but not in the dataset (2 units) |
| `x_operating_license` | The date the operating license was issued (the source's name: Operating License Issued) | none | date | 1957-08-31 to 2022-08-03; 123 distinct | 2: On the list but not in the dataset (2 units) |
| `x_parent_company` | The parent company, as the dataset names it (its Parent Company Utility Name) (the source's name: Parent Company Utility Name) | none | text | AmerenUE, Arizona Public Service Company, Constellation Energy Corporation, DTE Electric Company (DTE), Dominion Generation, Duke Energy, Energy Harbor Corp., Energy Northwest, Entergy Nuclear Operations, Inc., Indiana Michigan Power Company, Nebraska Public Power District, NextEra Energy, Inc. with principal subsidiaries Florida Power & Light Co. and NextEra Energy Resources, LLC, Northern States Power Company Minnesota doing business as Xcel Energy, PSEG Nuclear, LLC, Pacific Gas & Electric Company, STP Nuclear Operating Company, Southern Nuclear Operating Company, Talen Energy Corporation, Tennessee Valley Authority, Vistra Energy Corp., Wolf Creek Nuclear Operating Corporation | 37: A unit in decommissioning, or not in the dataset |
| `x_renewed_license` | The date the renewed operating license was issued, or words where the dataset holds words (Application Withdrawn) (the source's name: Renewed Operating License Issued) | none | text | for example 2000-03-23, 2000-05-23, 2001-06-20; 49 distinct | 44: A unit in decommissioning, not in the dataset, or no renewal |
| `x_shut_down` | The date a unit in decommissioning shut down (the source's name: Shut Down) | none | date | 1963-12-19 to 2021-04-30; 33 distinct | 95: An operating unit |
| `x_subsequent_renewal` | The date the subsequent renewed operating license was issued (the source's name: Subsequent Renewed Operating License Issued) | none | date | 2019-12-04, 2020-03-05, 2021-05-04 | 124: No subsequent renewal issued |

### `nrc_reactor_status`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 237570.

- **Source:** nrc:power_reactor_status U.S. Nuclear Regulatory Commission, Power Reactor Status Reports (https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/index)
- **Method note:** [`docs/methods/nrc_reactor_status.md`](../methods/nrc_reactor_status.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Power Reactor Status Reports (daily). Via the Energy Research Warehouse (ERW), table `nrc_reactor_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example nrc:arkansas_nuclear_1, nrc:arkansas_nuclear_2, nrc:beaver_valley_1; 99 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-11-19T00:00:00Z; 2515 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; 101 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 237570 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Arkansas Nuclear 1, Arkansas Nuclear 2, Beaver Valley 1; 99 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:power_reactor_status | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2020/2020powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2021/2021powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2022/2022powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2023/2023powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2024/2024powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2025/2025powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/powerreactorstatusforlast365days.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:30:37Z to 2026-11-19T17:42:45Z; 45 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 237570 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `power_pct` |  | pct | 237570 | 2020-01-01T00:00:00Z | 2026-11-19T00:00:00Z |

### `nrc_rop_findings`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 18240.

- **Source:** nrc:rop_findings_violations U.S. Nuclear Regulatory Commission, NRC Data, Reactor Oversight Process: Findings and Violations (https://www.nrc.gov/documents-reports/nrc-data)
- **Method note:** [`docs/methods/nrc_rop_findings.md`](../methods/nrc_rop_findings.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). NRC Data: Reactor Oversight Process findings and violations. Via the Energy Research Warehouse (ERW), table `nrc_rop_findings`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example nrc_rop:000222b5adbf9c, nrc_rop:0003eb1212b4b0, nrc_rop:0005c1f6beeec2; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1999-07-29 to 2025-05-12; 3630 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | av, fin, ncv, ncviv, nov, noviv, vio | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | for example Arkansas Nuclear One, Beaver Valley, Braidwood; 66 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | text | for example nrc_reactor:05000206, nrc_reactor:05000219, nrc_reactor:05000220; 108 distinct | 0 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 18240 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 18240 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 18240 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | greater than green, green, red, white, yellow | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:rop_findings_violations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/sites/default/files/doc_library/cdn/data/reactors/operating/dataset/findings-violations.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:29:36Z | 0 |
| `x_procedure` | not yet written |  | text | for example 2201/004, 2515/140, 2515/148; 148 distinct | 1 |
| `x_report_number` | not yet written |  | integer | 1999003 to 2025420; 613 distinct | 0 |
| `x_cornerstone` | not yet written |  | text | Barrier Integrity, Emergency Preparedness, Initiating Events, Misc, Mitigating Systems, Occupational Radiation Safety, Public Radiation Safety, Security | 0 |
| `x_cornerstone_code` | not yet written |  | text | BI, EP, IE, MS, Misc, ORS, PRS, SEC | 0 |
| `x_title` | not yet written |  | text | for example "1A" PSW Pump High Vibration Failure, "A" CONTROL ROOM VENTILATION (CRV) TRIPPED DUE TO DIFFERENTIAL PRESSURE SWITCH SETPOINT DRIFT., "A" ESW Pump Power Supply Cables Submerged in Water; more than 5000 distinct | 0 |
| `x_site_code` | not yet written |  | text | for example ANO, BF, BRAI; 66 distinct | 0 |
| `x_cross_cutting_aspect` | not yet written |  | text | H.1 - Resources, H.10 - Bases for Decisions, H.11 - Challenge the Unknown, H.12 - Avoid Complacency, H.13 - Consistent Process, H.14 - Conservative Bias, H.2 - Field Presence, H.3 - Change Management, H.4 - Teamwork, H.5 - Work Management, H.6 - Design Margins, H.7 - Documentation, H.8 - Procedure Adherence, H.9 - Training, N, None, P.1 - Identification, P.2 - Evaluation, P.3 - Resolution, P.4 - Trending, P.5 - Operating Experience, P.6 - Self-Assessment, S.1 - SCWE Policy, U, X.12 - Accountability for Decisions | 0 |
| `x_cross_cutting_area` | not yet written |  | text | H, N, P, S, U, X | 0 |
| `x_identified_by` | not yet written |  | text | NRC - Identified, Self - Revealed | 4 |
| `x_region` | not yet written |  | integer | 1, 2, 3, 4 | 0 |
| `x_accession` | not yet written |  | text | for example M22217A111, ML000000000, ML003690419; more than 5000 distinct | 234 |
| `x_traditional_enforcement` | not yet written |  | boolean | False, True | 0 |
| `x_severity` | not yet written |  | text | III, IV, None, V | 0 |
| `x_cornerstone_attribute` | not yet written |  | text | Access Authorization, Access Control, Cladding Performance, Configuration Control, Cyber Security, Design Control, ERO Performance, ERO Readiness, Equipment Performance, Facilities and Equipment, Human Performance, Material Control and Accounting, None, Offsite EP, Physical Protection System, Plant Facilities/Equipment and Instrumentation, Procedure Quality, Program & Process, Protection Against External Factors, Protection of Safeguards Information, RCS Equipment and Barrier Performance, Response to Contingency Events, SSC Performance, SSC and Barrier Performance | 0 |
| `x_year` | not yet written |  | integer | 1999 to 2025; 27 distinct | 0 |
| `x_quarter` | not yet written |  | integer | 1, 2, 3, 4 | 0 |
| `x_link` | not yet written |  | text | for example https://www.nrc.gov/docs/, https://www.nrc.gov/docs/	 ML24093A260, https://www.nrc.gov/docs/ ML22286A160; more than 5000 distinct | 0 |

