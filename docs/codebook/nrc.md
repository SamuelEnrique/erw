# Codebook: nrc

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 7 public tables (2 entities, 4 events, 1 series; tiers: 7 source); 7 documented in full.

- [`nrc_advanced_reactor_preapplicants`](#nrc_advanced_reactor_preapplicants): One applicant, vendor or research or test reactor that the NRC's pre-application table for advanced reactors lists, by technology.
- [`nrc_event_notifications`](#nrc_event_notifications): One unit named in one power reactor event report the NRC's Operations Center published (a report about two or three units is a row a unit).
- [`nrc_license_actions`](#nrc_license_actions): One reactor license renewal the NRC completed (or one withdrawn application), or one power uprate the NRC approved.
- [`nrc_new_reactor_applications`](#nrc_new_reactor_applications): One advanced reactor application under the NRC's review, with its applicant, kind, place, design, power and milestones.
- [`nrc_power_reactors`](#nrc_power_reactors): One US power reactor unit, operating (on the NRC's List of Power Reactor Units) or in decommissioning (the NRC's decommissioning dataset), with the NRC datasets' licensing dates and capacity.
- [`nrc_reactor_status`](#nrc_reactor_status): One US power reactor's power level on one day, as the NRC's Power Reactor Status Report gives it.
- [`nrc_rop_findings`](#nrc_rop_findings): One inspection finding or violation the NRC issued at an operating reactor site under its Reactor Oversight Process.

### `nrc_advanced_reactor_preapplicants`

One applicant, vendor or research or test reactor that the NRC's pre-application table for advanced reactors lists, by technology.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 43.

- **Time:** No time column; the table is a snapshot of the NRC's pre-application page as read; vintage is the page's last-modified time (UTC).
- **Revisions:** A snapshot, written whole by each run from the page as read.
- **Source:** nrc:new_reactors U.S. Nuclear Regulatory Commission, Advanced Reactors: Who We're Working With (https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with)
- **Method note:** [`docs/methods/nrc_new_reactors.md`](../methods/nrc_new_reactors.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Advanced Reactors: application projects and pre-application activities. Via the Energy Research Warehouse (ERW), table `nrc_advanced_reactor_preapplicants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: nrc_preapp:<the name as the page writes it> | none | text | for example nrc_preapp:aalo-atomics-idaho-nuclear-project, nrc_preapp:abilene-christian-university, nrc_preapp:advanced-float-co-ltd; 43 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always company | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it. Here: As the NRC's table writes it; a link's text kept as written | none | text | for example ARC Clean Technology, Aalo Atomics, Abilene Christian University; 43 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 43 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 43 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 43 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 43 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value (activity is in x_active) | none | empty | no cell holds a value | 43 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 43 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 43 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:new_reactors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:09:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The page's last-modified time as the NRC's server gave it, UTC | none | utc time | 2026-10-23T13:32:13Z | 0 |
| `x_technology` | The technology column of the NRC's table the name sits in (High Temperature Gas Reactors, Light Water Reactors, Liquid Metal Cooled Reactors, Molten Salt Reactors, Other Designs) | none | text | High Temperature Gas Reactors, Light Water Reactors, Liquid Metal Cooled Reactors, Molten Salt Reactors / Molten Chloride Fast Reactors, Other Designs/ Not Specified | 1: In no column of the table (Westinghouse eVinci, named only among the inactive projects) |
| `x_microreactor` | yes where the NRC's table marks the design a microreactor (its '*'), else no | none | text | no, yes | 0 |
| `x_active` | no for the 'Inactive Projects' the page names after the table, else yes | none | text | no, yes | 0 |
| `x_page` | The address of the NRC page the name links to | none | text | for example https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/aalo-atomics-idaho-nuclear-project, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/abilene-christian-university, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities/advanced-float-co-ltd; 43 distinct | 0 |

### `nrc_event_notifications`

One unit named in one power reactor event report the NRC's Operations Center published (a report about two or three units is a row a unit).

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 25.

- **Time:** event_date is the event's time in UTC, from the NRC's event date, time and zone (EDT, CDT; ET read with daylight saving); x_event_local and x_event_tz keep the NRC's.
- **Revisions:** A snapshot, written whole by each run from the raw data file and every saved daily page; a report in both keeps the daily page's row.
- **Source:** nrc:event_notification_reports U.S. Nuclear Regulatory Commission, Operations Center, Event Notification Reports (https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports)
- **Method note:** [`docs/methods/nrc_event_notifications.md`](../methods/nrc_event_notifications.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Event Notification Reports (power reactors). Via the Energy Research Warehouse (ERW), table `nrc_event_notifications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: nrc_en:<event number>:<unit>, or nrc_en:<event number> where the report names no unit | none | text | nrc_en:57790:1, nrc_en:57793:3, nrc_en:57794:2, nrc_en:57800:1, nrc_en:57800:2, nrc_en:57804:2, nrc_en:57810:2, nrc_en:57813:1, nrc_en:57816:1, nrc_en:57820:1, nrc_en:57822:1, nrc_en:57831:1, nrc_en:57832:1, nrc_en:57833:1, nrc_en:57833:2, nrc_en:57836:1, nrc_en:57836:2, nrc_en:57839:1, nrc_en:57840:1, nrc_en:57840:2, nrc_en:57840:3, nrc_en:58489:1, nrc_en:58490:3, nrc_en:58498:2, nrc_en:58501:3 | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The event's time in UTC (YYYY-MM-DDTHH:MM:SSZ) | none | utc time | 2025-05-07T01:08:00Z, 2025-05-30T05:00:00Z, 2025-06-06T16:00:00Z, 2025-06-30T21:41:00Z, 2025-07-02T12:42:00Z, 2025-07-03T00:22:00Z, 2025-07-07T19:45:00Z, 2025-07-13T18:18:00Z, 2025-07-16T14:59:00Z, 2025-07-17T15:00:00Z, 2025-07-21T20:48:00Z, 2025-07-22T19:10:00Z, 2025-07-28T17:33:00Z, 2025-07-29T01:58:00Z, 2025-07-29T04:29:00Z, 2025-07-30T17:30:00Z, 2026-10-10T20:14:00Z, 2026-10-12T12:24:00Z, 2026-10-15T17:05:00Z, 2026-10-17T03:45:00Z | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: reactor_scram where the unit's scram code is not N or the report cites 50.72(b)(2)(iv)(B), else reactor_event | none | text | reactor_event, reactor_scram | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The licensee; empty in the rows read from the daily pages, which name none | none | text | Constellation Nuclear, Detroit Edison Co., Dominion Generation, Entergy Nuclear, Exelon Nuclear Co., Indiana/Michigan Power Co., Nebraska Public Power District, Nuclear Management Company, Ppl Susquehanna Llc, Southern Nuclear Operating Company, Tennessee Valley Authority | 4 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 25 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 25 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 25 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 25 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:event_notification_reports | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261013en, https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261016en, https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports/2026/20261019en, https://www.nrc.gov/sites/default/files/doc_library/reading-rm/doc-collections/event-status/event/event-notification-rpt-lastmonth.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:35:06Z, 2026-10-23T18:38:04Z, 2026-10-23T18:38:05Z, 2026-10-23T18:38:07Z | 0 |
| `x_en_number` | The NRC's event notification number of the report (the source's name: Event Num) | none | integer | 57790, 57793, 57794, 57800, 57804, 57810, 57813, 57816, 57820, 57822, 57831, 57832, 57833, 57836, 57839, 57840, 58489, 58490, 58498, 58501 | 0 |
| `x_facility` | The site (plant) as the NRC names it (the source's name: Site Name) | none | text | Braidwood, Browns Ferry, Calvert Cliffs, Cook, Cooper, Farley, Fermi, Grand Gulf, Hatch, Millstone, Monticello, North Anna, Prairie Island, River Bend, Robinson, Susquehanna, Waterford, Watts Bar | 0 |
| `x_unit` | The unit number at the site the row is about | none | integer | 1, 2, 3 | 0 |
| `x_region` | The NRC region (1 to 4) of the site (the source's name: Region No) | none | integer | 1, 2, 3, 4 | 0 |
| `x_state` | The site's state, two-letter postal code (the source's name: State Cd) | none | text | AL, CT, GA, IL, LA, MD, MI, MN, MS, NE, PA, SC, TN, VA | 0 |
| `x_county` | The site's county as the NRC writes it (the source's name: County Name) | none | text | Berrien, Calvert, Claiborne, Goodhue, Houston, Limestone, Louisa, Luzerne, Monroe, Nemaha, New London, Rhea, West Feliciana, Will, Wright | 4: The report gives no county |
| `x_docket` | The NRC docket number of the site's license, as printed (05000...) (the source's name: Docket No) | none | integer | 05000259, 05000263, 05000282, 05000298, 05000315, 05000338, 05000341, 05000348, 05000387, 05000390, 05000416, 05000456, 05000458 | 7: The report gives no docket |
| `x_reactor_type` | The NRC's reactor type field for the site's units, each unit's type after its number in brackets ([1] GE-4,[2] GE-4), as printed (the source's name: Reactor Type) | none | text | [1] CE,[2] CE, [1] GE-3, [1] GE-3,[2] CE,[3] W-4-LP, [1] GE-4, [1] GE-4,[2] GE-4, [1] GE-4,[2] GE-4,[3] GE-4, [1] GE-6, [1] W-2-LP,[2] W-2-LP, [1] W-3-LP,[2] W-3-LP, [1] W-3-LP,[2] W-3-LP,[3] M-4-LP, [1] W-4-LP,[2] W-4-LP, [2] GE-4, [2] W-3-LP, [3] CE | 0 |
| `x_notification_et` | The time the licensee notified the NRC, in Eastern time as the NRC gives it (no zone) (the source's name: Notification Dt and Notification Time) | none | text | 2025-06-30T20:35:00, 2025-07-02T11:38:00, 2025-07-02T12:11:00, 2025-07-03T17:27:00, 2025-07-07T22:36:00, 2025-07-13T17:10:00, 2025-07-16T13:57:00, 2025-07-17T11:38:00, 2025-07-21T22:51:00, 2025-07-22T17:22:00, 2025-07-29T03:44:00, 2025-07-29T03:45:00, 2025-07-29T09:19:00, 2025-07-29T13:00:00, 2025-07-30T17:20:00, 2025-07-30T23:19:00, 2026-10-10T19:22:00, 2026-10-12T14:37:00, 2026-10-15T16:56:00, 2026-10-17T03:00:00 | 0 |
| `x_notification_utc` | The time the licensee notified the NRC, in UTC | none | utc time | 2025-07-01T00:35:00Z, 2025-07-02T15:38:00Z, 2025-07-02T16:11:00Z, 2025-07-03T21:27:00Z, 2025-07-08T02:36:00Z, 2025-07-13T21:10:00Z, 2025-07-16T17:57:00Z, 2025-07-17T15:38:00Z, 2025-07-22T02:51:00Z, 2025-07-22T21:22:00Z, 2025-07-29T07:44:00Z, 2025-07-29T07:45:00Z, 2025-07-29T13:19:00Z, 2025-07-29T17:00:00Z, 2025-07-30T21:20:00Z, 2025-07-31T03:19:00Z, 2026-10-10T23:22:00Z, 2026-10-12T18:37:00Z, 2026-10-15T20:56:00Z, 2026-10-17T07:00:00Z | 0 |
| `x_event_local` | The event's local date and time as the NRC gives it (no zone) (the source's name: Event Dt and Event Time) | none | text | 2025-05-06T21:08:00, 2025-05-30T00:00:00, 2025-06-06T12:00:00, 2025-06-30T16:41:00, 2025-07-02T08:42:00, 2025-07-02T19:22:00, 2025-07-07T15:45:00, 2025-07-13T14:18:00, 2025-07-16T09:59:00, 2025-07-17T11:00:00, 2025-07-21T15:48:00, 2025-07-22T15:10:00, 2025-07-28T13:33:00, 2025-07-28T20:58:00, 2025-07-28T23:29:00, 2025-07-30T12:30:00, 2026-10-10T16:14:00, 2026-10-12T07:24:00, 2026-10-15T13:05:00, 2026-10-16T22:45:00 | 0 |
| `x_event_tz` | The time zone the NRC names for the event time (EDT, CDT) (the source's name: Time Zone) | none | text | CDT, EDT | 0 |
| `x_last_update` | The date of the report's last update (the source's name: Last Updated Dt) | none | date | 2025-07-02, 2025-07-09, 2025-07-13, 2025-07-16, 2025-07-17, 2025-07-21, 2025-07-22, 2025-07-29, 2025-07-30, 2026-10-10, 2026-10-12, 2026-10-15, 2026-10-17 | 0 |
| `x_emergency_class` | The emergency class of the report (all Non Emergency) (the source's name: Emergency Class) | none | text | Non Emergency | 0 |
| `x_cfr` | Every section of 10 CFR (federal regulations) the report was made under, joined by '; ' | none | text | 21.21(d)(3)(i), 26.719, 50.72(b)(2)(iv)(A); 50.72(b)(2)(iv)(B); 50.72(b)(3)(iv)(A), 50.72(b)(2)(iv)(B), 50.72(b)(2)(iv)(B); 50.72(b)(3)(iv)(A), 50.72(b)(2)(iv)(B); 50.72(b)(3)(v)(C); 50.72(b)(3)(v)(D), 50.72(b)(2)(xi), 50.72(b)(3)(ii)(A), 50.72(b)(3)(iv)(A), 50.72(b)(3)(v)(C), 50.72(b)(3)(v)(D), 50.72(b)(3)(xiii), 50.73(a)(1) | 0 |
| `x_cfr_words` | The NRC's short words for each of those sections (RPS Actuation, Fitness For Duty and the others), joined by '; ' | none | text | Accident Mitigation, Defects And Noncompliance, Degraded Condition, ECCS Injection; RPS Actuation - Critical; Valid Specif Sys Actuation, Fitness For Duty, Invalid Specif System Actuation, Loss Comm/Asmt/Response, Offsite Notification, Pot Uncntrl Rad Rel, RPS Actuation - Critical, RPS Actuation - Critical 50.72(b)(3)(iv)(A) - Valid Specif Sys Actuation, RPS Actuation - Critical; Pot Uncntrl Rad Rel; Accident Mitigation, RPS Actuation - Critical; Valid Specif Sys Actuation, Valid Specif Sys Actuation | 0 |
| `x_scram_code` | The unit's scram (rapid shutdown) code: A/R automatic, M/R manual, N none (the source's name: Scram Code) | none | text | A/R, M/R, N | 0 |
| `x_rx_crit` | Whether the reactor was critical (sustaining a chain reaction): Y or N (the source's name: RX CRIT) | none | text | N, Y | 0 |
| `x_initial_power_pct` | The unit's power before the event, percent of its licensed power (the source's name: Initial PWR) | pct | integer | 0, 100, 75, 91, 96 | 0 |
| `x_initial_mode` | The unit's operating mode before the event (Power Operation, Hot Shutdown, Cold Shutdown, Defueled) (the source's name: Initial RX Mode) | none | text | Cold Shutdown, Defueled, Hot Shutdown, Power Operation | 0 |
| `x_current_power_pct` | The unit's power at the time of the report, percent of its licensed power (the source's name: Current PWR) | pct | integer | 0, 100, 91 | 0 |
| `x_current_mode` | The unit's operating mode at the time of the report (Power Operation, Hot Standby, Hot Shutdown, Defueled) (the source's name: Current RX Mode) | none | text | Defueled, Hot Shutdown, Hot Standby, Power Operation | 0 |
| `x_read_from` | Which NRC publication the row was read from: raw_file (the data file) or daily_page | none | text | daily_page, raw_file | 0 |

### `nrc_license_actions`

One reactor license renewal the NRC completed (or one withdrawn application), or one power uprate the NRC approved.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 236.

- **Time:** event_date is the renewed license's issue date, the uprate's approval date, or for the withdrawn application the date received (a date).
- **Revisions:** A snapshot, written whole by each run from the two pages; a row the NRC removes leaves the table. vintage is each page's last-modified time.
- **Source:** nrc:license_renewals_uprates U.S. Nuclear Regulatory Commission, Status of License Renewal Applications and Approved Applications for Power Uprates
- **Method note:** [`docs/methods/nrc_license_actions.md`](../methods/nrc_license_actions.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Status of License Renewal Applications; Approved Applications for Power Uprates. Via the Energy Research Warehouse (ERW), table `nrc_license_actions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: nrc:renewal:<plant slug>:<YYYYMMDD received> or nrc:uprate:<the NRC's number> | none | text | for example nrc:renewal:arkansas_nuclear_one_1:20000201, nrc:renewal:arkansas_nuclear_one_2:20031015, nrc:renewal:beaver_valley_1_2:20070828; 236 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1977-09-09 to 2026-04-02; 175 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: license_renewal (initial renewals) or power_uprate | none | text | license_renewal, power_uprate | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: Always NRC | none | text | NRC | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 236 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 236 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 236 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 236 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: issued or withdrawn (renewals), approved (uprates) | none | text | approved, issued, withdrawn | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:license_renewals_uprates | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/reactors/operating/licensing/power-uprates/status-power-apps/approved-applications.html, https://www.nrc.gov/reactors/operating/licensing/renewal/applications.html | 0 |
| `x_plant` | The plant and units as the NRC writes them (Calvert Cliffs 1 & 2) | none | text | for example ANO-2, Arkansas Nuclear One 1, Arkansas Nuclear One 2; 156 distinct | 0 |
| `x_application_received` | Renewals: the date the NRC received the renewal application (the source's name: Application Received) | none | date | 1998-04-10 to 2024-02-14; 59 distinct | 172: An uprate row |
| `x_extended_operation` | Renewals: the date each unit enters extended operation, as the NRC writes it (two-digit years kept) (the source's name: Date Entering Extended Operation) | none | text | for example 01/16/27 (Unit 1) 02/09/29 (Unit 2), 01/18/14, 01/29/16 (Unit 1) 05/27/27 (Unit 2); 61 distinct | 175: An uprate row, or the NRC gives none (Crystal River 3, Kewaunee, Pilgrim 1) |
| `x_note` | Renewals: the page's notes for the row's footnote marks (a shutdown, a withdrawal, an earlier application) | none | text | Fort Calhoun Station was permanently shut down on October 24, 2016., Kewaunee Power Station was permanently shut down on May 7, 2013., Oyster Creek Nuclear Generating Station was permanently shut down on September 7, 2018., Pilgrim 1 permanently shut down on May 31, 2019, The Crystal River Nuclear Generating Plant, Unit 3 application was withdrawn by the licensee on February 6, 2013. The facility was permanently shut down on February 20, 2013., The previous Diablo Canyon 1 & 2 license renewal application was submitted on November 7, 2018 and withdrawn by the licensee on March 7, 2018. On October 31, 2022, Pacific Gas and Electric sent in a letter to “Request to Resume Review of the Diablo Canyon Power Plant License Renewal Application or, Alternatively, for an Exemption from 10 CFR 2.109(b), Concerning a Timely Renewal Application. ” On March 2, 2023, the NRC granted the exemption., Vermont Yankee Nuclear Power Station was permanently shut down on December 29, 2014. | 229: The row carries no footnote mark |
| `x_uprate_type` | Uprates: MU (measurement uncertainty recapture), S (stretch), E or E(1) (extended), as the NRC writes them (the source's name: TYPE) | none | text | E, E(1), MU, S | 64: A renewal row |
| `x_uprate_pct` | Uprates: the increase as a percent of the unit's thermal power | pct | number | 0.4 to 20.0; 45 distinct | 64: A renewal row |
| `x_uprate_mwt` | Uprates: the increase in thermal megawatts (not electric) (the source's name: MWt) | MWt | number | 13.0 to 579.0; 81 distinct | 64: A renewal row |
| `x_accession` | Uprates: the ADAMS (NRC document library) accession number as printed; 8 older numbers end in '*' | none | text | for example 7907180064*, 7907240100*, 8008280223*; 119 distinct | 64: A renewal row |
| `x_link` | Renewals: the row's NRC page | none | text | for example https://www.nrc.gov/licensing-applications/power-reactor-licensing/arkansas-nuclear-one-unit-1--license-renewal-application, https://www.nrc.gov/licensing-applications/power-reactor-licensing/arkansas-nuclear-one-unit-2---license-renewal-application, https://www.nrc.gov/licensing-applications/power-reactor-licensing/beaver-valley-power-station---license-renewal-application; 64 distinct | 172: An uprate row |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:36:10Z, 2026-10-23T20:36:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The page's last-modified time (UTC): one for the renewal page, one for the uprate page | none | utc time | 2026-10-23T19:36:07Z, 2026-10-23T19:51:29Z | 0 |

### `nrc_new_reactor_applications`

One advanced reactor application under the NRC's review, with its applicant, kind, place, design, power and milestones.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 6.

- **Time:** event_date is the application's submittal date (the 'When:' line's first date, a month's first day where it gives only a month).
- **Revisions:** A snapshot, written whole by each run from the list and each project's page; vintage is the project page's last-modified time.
- **Source:** nrc:new_reactors U.S. Nuclear Regulatory Commission, Advanced Reactors: Who We're Working With (https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with)
- **Method note:** [`docs/methods/nrc_new_reactors.md`](../methods/nrc_new_reactors.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Advanced Reactors: application projects and pre-application activities. Via the Energy Research Warehouse (ERW), table `nrc_new_reactor_applications`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: nrc_app:<the page's name> | none | text | nrc_app:dukeenergy, nrc_app:eden-radioisotopes-llc-eden-isotope-production-complex, nrc_app:long-mott-energy-llc, nrc_app:pioneer-units-1-and-2-limited-work-authorization-application, nrc_app:tva-clinch-river-cpa, nrc_app:university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2025-03-31, 2025-04-01, 2025-12-30, 2025-12-31, 2026-03-31, 2026-05-05 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: construction_permit_application, early_site_permit_application or limited_work_authorization_application | none | text | construction_permit_application, early_site_permit_application, limited_work_authorization_application | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The applicant | none | text | Duke Energy, Eden Radioisotopes, LLC, Long Mott Energy, LLC, Palisades SMR, LLC, Tennessee Valley Authority (TVA), University of Illinois Urbana-Champaign | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 6 |
| `mw` | The capacity involved, in megawatts. Here: The electric power the page states (MWe), else empty | MW | integer | 320 | 5 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 6 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 6 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The latest milestone the page marks done (A), in the NRC's words; empty where none is done | none | text | Draft Safety Evaluation Report (with information gaps), Finalize Final SEIS and Related Activities ( ML26035A285 ), Issue Environmental Assessment and Finding of No Significant Impact, Review Schedule Established/Schedule Letter Issued to Applicant | 1 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:new_reactors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/dukeenergy, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/eden-radioisotopes-llc-eden-isotope-production-complex, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/long-mott-energy-llc, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/pioneer-units-1-and-2-limited-work-authorization-application, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/tva-clinch-river-cpa, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:09:42Z, 2026-10-23T15:09:44Z, 2026-10-23T15:09:46Z, 2026-10-23T15:09:47Z, 2026-10-23T15:09:49Z, 2026-10-23T15:09:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The project page's last-modified time, UTC | none | utc time | 2026-10-23T13:14:16Z, 2026-10-23T13:17:15Z, 2026-10-23T13:18:52Z, 2026-10-23T13:30:47Z, 2026-10-23T13:31:04Z, 2026-10-23T13:45:04Z | 0 |
| `x_project` | The project page's title | none | text | Clinch River Nuclear Site Application, Duke Energy's Belews Creek Early Site Permit Application, Eden Radioisotopes, LLC – Eden Isotope Production Complex, Long Mott Energy, LLC – Long Mott Generating Station Xe-100 Power Reactor Application, Pioneer Units 1 and 2 Limited Work Authorization Application, University of Illinois Urbana-Champaign – KRONOS Micro Modular Reactor (KRONOS MMR™) | 0 |
| `x_when` | The page's 'When:' line as written | none | text | Application submitted December 30, 2025; application accepted and currently under review, February 2025 - May 2027 (estimated), April 2025 to present (date of application submittal) February 2022 to April 2025 (pre-application), December 31, 2025 (date of application submittal) to present, March 31, 2025 (date of application submittal), March 31, 2026 (date of application submittal), May 5, 2026 (date of application submittal) | 0 |
| `x_place` | The page's 'Where:' line (county and state) as written | none | text | Calhoun County, Texas, Champaign County, Illinois, Lea County, New Mexico | 3: The page gives no 'Where:' |
| `x_state` | The state of the 'Where:' line, two-letter postal code | none | text | IL, NM, TX | 3: The page gives no 'Where:' |
| `x_what` | The page's 'What:' line: the kind of application as written | none | text | Application for a Construction Permit for a small modular reactor (BWRX-300), Application for a construction permit for a non-power reactor and production facility, Application for a construction permit for a research reactor, Application for a construction permit for an advanced power reactor, Application for an Early Site Permit, Pioneer Units 1 and 2 Phased Construction Permit Application - Limited Work Authorization | 0 |
| `x_reactor_type` | The reactor type from the page's Plant Characteristics table, as written (the source's name: Reactor Type) | none | text | High-Temperature Gas-Cooled Reactor (HTGR), High-temperature gas-cooled reactor (HTGR), Pool-Type Reactor | 3: The page's table gives none |
| `x_power_level` | The power level from the page's Plant Characteristics table, as written (MWth thermal, MWe electric) | none | text | 2 MWth, 4-Module plant with 800 MWth/320 MWe, 45 MWth | 3: The page's table gives none |
| `x_fuel` | The fuel from the page's Plant Characteristics table, as written (the source's name: Fuel) | none | text | Annular cylindrical fuel pellets consisting of TRISO fuel particles embedded in ceramic matrix, Graphite Pebbles with TRISO Particle fuel | 4: The page's table gives none |
| `x_status_date` | The date of the latest milestone the page marks done (status) | none | date | 2026-04-06, 2026-05-18, 2026-06-15, 2026-06-16, 2026-08-31 | 1: No milestone marked done |
| `x_next_milestone` | The first milestone the page marks a target (T) or TBD | none | text | Draft Environmental Impact Statement, Draft Safety Evaluation, Final Safety Evaluation | 2: No milestone marked a target |
| `x_next_target` | That milestone's target date as written | none | text | February 2027 – T, May 2027 – T, November 2026 – T, October 31, 2026 – T | 2: No milestone marked a target |
| `x_decision` | The permit or license decision's milestone row as written | none | text | Construction Permit Decision, Construction Permit Decision ( ML26244A257 ) | 4: The page's milestones hold no decision row |
| `x_decision_target` | The decision row's date as written (or TBD) | none | text | September 28, 2026, TBD | 4: The page's milestones hold no decision row |
| `x_page` | The address of the project's NRC page | none | text | https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/dukeenergy, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/eden-radioisotopes-llc-eden-isotope-production-complex, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/long-mott-energy-llc, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/pioneer-units-1-and-2-limited-work-authorization-application, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/tva-clinch-river-cpa, https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects/university-of-illinois-urbana-champaign-kronos-micro-modular-reactor-kronos-mmr | 0 |

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

One US power reactor's power level on one day, as the NRC's Power Reactor Status Report gives it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 237570.

- **Time:** ts_utc is the report date at 00:00:00Z (a date, not an instant); the power is the reactor's on that report's morning.
- **Revisions:** Merged on (entity, variable, ts_utc) by each run, so a day the NRC restates replaces the old row and earlier years stay; the 365-day file wins over a yearly file within a run. vintage is not filled.
- **Source:** nrc:power_reactor_status U.S. Nuclear Regulatory Commission, Power Reactor Status Reports (https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/index)
- **Method note:** [`docs/methods/nrc_reactor_status.md`](../methods/nrc_reactor_status.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). Power Reactor Status Reports (daily). Via the Energy Research Warehouse (ERW), table `nrc_reactor_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nrc:<unit name lower-cased, other characters as one underscore> | none | text | for example nrc:arkansas_nuclear_1, nrc:arkansas_nuclear_2, nrc:beaver_valley_1; 99 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-11-19T00:00:00Z; 2515 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; 101 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 237570 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The NRC's unit name as written, not a pricing node | none | text | for example Arkansas Nuclear 1, Arkansas Nuclear 2, Beaver Valley 1; 99 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:power_reactor_status | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2020/2020powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2021/2021powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2022/2022powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2023/2023powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2024/2024powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/2025/2025powerstatus.txt, https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/powerreactorstatusforlast365days.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:30:37Z to 2026-11-19T17:42:45Z; 45 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 237570 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `power_pct` | The reactor's power as a percent of its licensed power on the morning of the report (whole numbers, 0 to 100) | pct | 237570 | 2020-01-01T00:00:00Z | 2026-11-19T00:00:00Z |

### `nrc_rop_findings`

One inspection finding or violation the NRC issued at an operating reactor site under its Reactor Oversight Process.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 18240.

- **Time:** event_date is the issue date (a date).
- **Revisions:** A snapshot, written whole by each run from the NRC's workbook (updated at the same address).
- **Source:** nrc:rop_findings_violations U.S. Nuclear Regulatory Commission, NRC Data, Reactor Oversight Process: Findings and Violations (https://www.nrc.gov/documents-reports/nrc-data)
- **Method note:** [`docs/methods/nrc_rop_findings.md`](../methods/nrc_rop_findings.md)
- **Cite as:** U.S. Nuclear Regulatory Commission (NRC). NRC Data: Reactor Oversight Process findings and violations. Via the Energy Research Warehouse (ERW), table `nrc_rop_findings`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: nrc_rop:<first 14 hex digits of a SHA-1 hash of docket, report number, issue date, procedure, title, type and cornerstone attribute> | none | text | for example nrc_rop:000222b5adbf9c, nrc_rop:0003eb1212b4b0, nrc_rop:0005c1f6beeec2; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1999-07-29 to 2025-05-12; 3630 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: The NRC's type in lower case: ncv (non-cited violation), fin (finding), vio (violation), nov (notice of violation), ncviv and noviv (the same at severity IV), av (apparent violation) | none | text | av, fin, ncv, ncviv, nov, noviv, vio | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The site as the NRC names it | none | text | for example Arkansas Nuclear One, Beaver Valley, Braidwood; 66 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: nrc_reactor:<docket> | none | text | for example nrc_reactor:05000206, nrc_reactor:05000219, nrc_reactor:05000220; 108 distinct | 0 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 18240 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 18240 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 18240 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The significance color in lower case: green, white, yellow, red, greater than green | none | text | greater than green, green, red, white, yellow | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nrc:rop_findings_violations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nrc.gov/sites/default/files/doc_library/cdn/data/reactors/operating/dataset/findings-violations.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:29:36Z | 0 |
| `x_procedure` | The NRC inspection procedure the finding came from (the source's name: Procedure) | none | text | for example 2201/004, 2515/140, 2515/148; 148 distinct | 1: The NRC gives none (1 row) |
| `x_report_number` | The inspection report number (the source's name: Report Number) | none | integer | 1999003 to 2025420; 613 distinct | 0 |
| `x_cornerstone` | The Reactor Oversight Process cornerstone the finding falls under (Mitigating Systems, Initiating Events, Security, Barrier Integrity and the others) (the source's name: Cornerstone) | none | text | Barrier Integrity, Emergency Preparedness, Initiating Events, Misc, Mitigating Systems, Occupational Radiation Safety, Public Radiation Safety, Security | 0 |
| `x_cornerstone_code` | The cornerstone's code (MS, IE, SEC, BI, ORS, EP, PRS, Misc) (the source's name: CornerstoneCode) | none | text | BI, EP, IE, MS, Misc, ORS, PRS, SEC | 0 |
| `x_title` | The finding's title (the source's name: Title) | none | text | for example "1A" PSW Pump High Vibration Failure, "A" CONTROL ROOM VENTILATION (CRV) TRIPPED DUE TO DIFFERENTIAL PRESSURE SWITCH SETPOINT DRIFT., "A" ESW Pump Power Supply Cables Submerged in Water; more than 5000 distinct | 0 |
| `x_site_code` | The NRC's code of the site (the source's name: Site Code) | none | text | for example ANO, BF, BRAI; 66 distinct | 0 |
| `x_cross_cutting_aspect` | The cross-cutting aspect the NRC assigns, code and words (H.1 - Resources and the like); None or N where none (the source's name: CrossCuttingAspect) | none | text | H.1 - Resources, H.10 - Bases for Decisions, H.11 - Challenge the Unknown, H.12 - Avoid Complacency, H.13 - Consistent Process, H.14 - Conservative Bias, H.2 - Field Presence, H.3 - Change Management, H.4 - Teamwork, H.5 - Work Management, H.6 - Design Margins, H.7 - Documentation, H.8 - Procedure Adherence, H.9 - Training, N, None, P.1 - Identification, P.2 - Evaluation, P.3 - Resolution, P.4 - Trending, P.5 - Operating Experience, P.6 - Self-Assessment, S.1 - SCWE Policy, U, X.12 - Accountability for Decisions | 0 |
| `x_cross_cutting_area` | The cross-cutting area code as the NRC prints it (H, P, N, U, S, X) (the source's name: CrossCutting Area) | none | text | H, N, P, S, U, X | 0 |
| `x_identified_by` | Who identified the finding: NRC - Identified or Self - Revealed (the source's name: Idby) | none | text | NRC - Identified, Self - Revealed | 4: The NRC gives none (4 rows) |
| `x_region` | The NRC region (1 to 4) of the site (the source's name: Region) | none | integer | 1, 2, 3, 4 | 0 |
| `x_accession` | The ADAMS (NRC document library) accession number of the report, as printed; some hold a note instead (the source's name: Accession Number) | none | text | for example M22217A111, ML000000000, ML003690419; more than 5000 distinct | 234: The NRC gives none |
| `x_traditional_enforcement` | Whether the item is handled under traditional enforcement (True or False) (the source's name: IsTraditionalEnforcement) | none | boolean | False, True | 0 |
| `x_severity` | The item's severity level (III, IV, V), or None (the source's name: Item Severity Type Code) | none | text | III, IV, None, V | 0 |
| `x_cornerstone_attribute` | The cornerstone attribute (Equipment Performance, Design Control, Human Performance and the others), or None (the source's name: Cornerstone Attribute Type) | none | text | Access Authorization, Access Control, Cladding Performance, Configuration Control, Cyber Security, Design Control, ERO Performance, ERO Readiness, Equipment Performance, Facilities and Equipment, Human Performance, Material Control and Accounting, None, Offsite EP, Physical Protection System, Plant Facilities/Equipment and Instrumentation, Procedure Quality, Program & Process, Protection Against External Factors, Protection of Safeguards Information, RCS Equipment and Barrier Performance, Response to Contingency Events, SSC Performance, SSC and Barrier Performance | 0 |
| `x_year` | The NRC's year of the finding (the year of event_date in every row) (the source's name: Year) | none | integer | 1999 to 2025; 27 distinct | 0 |
| `x_quarter` | The NRC's quarter of the finding (1 to 4) (the source's name: Quarter) | none | integer | 1, 2, 3, 4 | 0 |
| `x_link` | The NRC's link to the report (https://www.nrc.gov/docs/ and the accession), as printed; some hold a space or tab (the source's name: Link) | none | text | for example https://www.nrc.gov/docs/, https://www.nrc.gov/docs/	 ML24093A260, https://www.nrc.gov/docs/ ML22286A160; more than 5000 distinct | 0 |

Waiting for a second look: x_cross_cutting_area: the letters (H, P, N, U, S, X) are not explained in any note or connector; the NRC's data dictionary is read but not held in the repository. Read again on 20 November 2026 in the saved findings workbook under warehouse/raw/nrc_rop_findings (one sheet; the letter is the first letter of CrossCuttingAspect, for example H with 'H.14 - Conservative Bias', but no row or sheet says what a letter stands for): not found..

