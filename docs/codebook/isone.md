# Codebook: isone

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (1 entities, 3 series; tiers: 4 source); 3 documented in full.

- [`isone_dam_zone_prices`](#isone_dam_zone_prices): ISO-NE's day-ahead locational marginal price at one of its eight load zones or its Internal Hub for one hour.
- [`isone_interconnection_queue`](#isone_interconnection_queue): One position (a request, or a unit or phase of one) in ISO-NE's interconnection queue of generation and other projects asking to connect to the grid.
- [`isone_rtm_zone_prices`](#isone_rtm_zone_prices): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`isone_rtm_zone_prices_hourly`](#isone_rtm_zone_prices_hourly): ISO-NE's hourly real-time locational marginal price (final, or preliminary until the final is posted) at one of its eight load zones or its Internal Hub for one hour.

### `isone_dam_zone_prices`

ISO-NE's day-ahead locational marginal price at one of its eight load zones or its Internal Hub for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17505.

- **Time:** ts_utc is the start of the hour in UTC (gridstatus's reading of the file's hour ending, Eastern); operating days are America/New_York days.
- **Revisions:** Merged by (entity, variable, ts_utc); a day read again (as a forward day, then in up to three windows) replaces its rows, the latest published file winning, and the table grows past the window. vintage is the file's HTTP Last-Modified.
- **Source:** isone:da_lmp_hourly Day-Ahead Energy Market Hourly LMPs (https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-da-hourly)
- **Method note:** [`docs/methods/isone_dam_zone_prices.md`](../methods/isone_dam_zone_prices.md)
- **Cite as:** ISO New England (ISO-NE). Day-Ahead Energy Market Hourly LMPs. Via the Energy Research Warehouse (ERW), table `isone_dam_zone_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: isone:<node>, the node's ISO-NE name | none | text | isone:.H.INTERNAL_HUB, isone:.Z.CONNECTICUT, isone:.Z.MAINE, isone:.Z.NEMASSBOST, isone:.Z.NEWHAMPSHIRE, isone:.Z.RHODEISLAND, isone:.Z.SEMASS, isone:.Z.VERMONT, isone:.Z.WCMASS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T04:00:00Z to 2026-11-17T04:00:00Z; 1945 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4.07 to 93.67; 4583 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO-NE's six states in every row, also for a zone in one state | none | text | US-CT,US-MA,US-ME,US-NH,US-RI,US-VT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: isone_dam in every row: ISO-NE's day-ahead energy market | none | text | isone_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ISO-NE's name of the location: .H.INTERNAL_HUB (the Internal Hub) or .Z.<zone> for the eight load zones (CONNECTICUT, MAINE, NEMASSBOST, NEWHAMPSHIRE, RHODEISLAND, SEMASS, VERMONT, WCMASS) | none | text | .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE, .Z.NEMASSBOST, .Z.NEWHAMPSHIRE, .Z.RHODEISLAND, .Z.SEMASS, .Z.VERMONT, .Z.WCMASS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | isone:da_lmp_hourly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.iso-ne.com/histRpts/da-lmp/WW_DALMP_ISO_20260826.csv, https://www.iso-ne.com/histRpts/da-lmp/WW_DALMP_ISO_20260827.csv, https://www.iso-ne.com/histRpts/da-lmp/WW_DALMP_ISO_20260828.csv; 81 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T19:37:11Z to 2026-11-16T14:33:39Z; 81 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The HTTP Last-Modified of the day's file (WW_DALMP_ISO_<YYYYMMDD>.csv) | none | utc time | 2026-08-25T16:42:05Z to 2026-11-15T17:40:14Z; 81 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead locational marginal price (the price of energy at the location in the day-ahead market), as ISO-NE prints it | USD/MWh | 17505 | 2026-08-26T04:00:00Z | 2026-11-17T04:00:00Z |

### `isone_interconnection_queue`

One position (a request, or a unit or phase of one) in ISO-NE's interconnection queue of generation and other projects asking to connect to the grid.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1751.

- **Time:** No time column. Dates are ISO-NE's, YYYY-MM-DD; vintage is the retrieval date. The table is a snapshot of the queue as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each run (Mondays); earlier queues are kept in the archive and the raw files.
- **Source:** isone:interconnection_queue ISO-NE Interconnection Request Tracking Tool (IRTT) queue (https://irtt.iso-ne.com/reports/external?AspxAutoDetectCookieSupport=1)
- **Method note:** [`docs/methods/isone_interconnection_queue.md`](../methods/isone_interconnection_queue.md)
- **Cite as:** ISO New England (ISO-NE). Interconnection Request Tracking Tool (IRTT) queue. Via the Energy Research Warehouse (ERW), table `isone_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: isone_queue:<queue id>, with :<n> added where ISO-NE lists one queue id on several rows (units, phases), n in ISO-NE's row order | none | text | for example isone_queue:1, isone_queue:10, isone_queue:100; 1751 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example (Offshore wind Increase (Q700 +Q1154), 1000 MW HVDC, 1000 MW HVDC (import only); 987 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> from ISO-NE's State; empty where the state is not a US state or DC (New Brunswick's NB) or not given | none | text | US-CT, US-MA, US-ME, US-NH, US-NY, US-RI, US-VT | 32 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1751 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1751 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: ISO-NE's requested capacity as gridstatus reads it (Capacity (MW)); a negative value is a net reduction as ISO-NE states it | MW | number | -21.2 to 2400.0; 722 distinct | 278 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active, withdrawn or completed, mapped one to one from iso_status | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The withdrawn date of a withdrawn row; ISO-NE gives no in-service date, so no completed row has one | none | date | 2006-04-13 to 2026-10-29; 606 distinct | 556 |
| `operator` | The operator or owner, as the publisher writes it. Here: The interconnecting entity; empty in every row, ISO-NE does not give it | none | empty | no cell holds a value | 1751 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | isone:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://irtt.iso-ne.com/reports/external?AspxAutoDetectCookieSupport=1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:22:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval date (retrieved_at's day), not a publication date | none | date | 2026-11-05 | 0 |
| `queue_id` | ISO-NE's queue number of the request (the source's name: Queue ID) | none | integer | 1 to 1601; 1601 distinct | 0 |
| `county` | The county (or counties) of the project as ISO-NE writes it (the source's name: County) | none | text | for example Addison, Albany, Albany/Dutchess; 112 distinct | 116: ISO-NE gives no county |
| `state` | The state of the project, two-letter code as ISO-NE gives it (NB for New Brunswick kept) (the source's name: State) | none | text | CT, MA, ME, NB, NH, NY, RI, VT | 31: ISO-NE gives no state |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example (Same as Existing POI Vernon Substation No.13 69 KV Bus) Street Address: 152 Governor Hunt Road, 1. Singer 345kV Substation existing available circuit breaker position and new circuit breaker position. 2. Offshore platform at the MA/RI BOEM Wind Energy Areas, 101105 Augusta East w New Breaker; 1442 distinct | 27: ISO-NE gives no location |
| `zone` | ISO-NE's load zone of the project (ME, SEMA, WMA, CT, RI, NH, BHE, VT, SWCT, BOST, CMA, NOR, SME) (the source's name: Zone) | none | text | BHE, BOST, CMA, CT, ME, NH, NOR, RI, SEMA, SME, SWCT, VT, WMA | 43: ISO-NE gives no zone |
| `transmission_owner` | The transmission owner the project connects to, as ISO-NE writes it (the source's name: Transmission Owner) | none | text | BHE, CMP, ISO-NE, MPS, NGRID, NSTAR, NU, TEUS, UI | 1105: ISO-NE gives none (empty in most rows) |
| `fuel_technology` | The generation type in EIA's fuel codes, several joined by spaces for a hybrid (SUN solar, BAT battery, WND wind, NG natural gas, DFO distillate oil, WAT water and others) (the source's name: Generation Type) | none | text | for example BAT, BIT, BIT RFO; 36 distinct | 265: ISO-NE gives no generation type |
| `iso_status` | ISO-NE's own status of the request (Active, Withdrawn, Completed) (the source's name: Status) | none | text | Active, Completed, Withdrawn | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 1996-06-07 to 2025-01-14; 982 distinct | 0 |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2007-05-31 to 2033-03-27; 748 distinct | 225: ISO-NE gives no proposed date |
| `actual_in_service_date` | The date the project began operating (the source's name: Actual Completion Date, In-Service Date or Op Date (gridstatus)) | none | empty | no cell holds a value | 1751: Empty in every row: ISO-NE does not give it |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2006-04-13 to 2026-10-29; 606 distinct | 556: Not withdrawn, or withdrawn with no date given |

### `isone_rtm_zone_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 57924.

- **Source:** isone:rt_lmp_5min Real-Time Energy Market Five-Minute LMPs (https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final)
- **Method note:** [`docs/methods/isone_rtm_zone_prices.md`](../methods/isone_rtm_zone_prices.md)
- **Cite as:** ISO New England (ISO-NE). Real-Time Energy Market Five-Minute LMPs. Via the Energy Research Warehouse (ERW), table `isone_rtm_zone_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | isone:.H.INTERNAL_HUB, isone:.Z.CONNECTICUT, isone:.Z.MAINE, isone:.Z.NEMASSBOST, isone:.Z.NEWHAMPSHIRE, isone:.Z.RHODEISLAND, isone:.Z.SEMASS, isone:.Z.VERMONT, isone:.Z.WCMASS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-27T04:00:00Z to 2026-11-16T04:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -72.3467 to 163.0033; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CT,US-MA,US-ME,US-NH,US-RI,US-VT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | isone_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE, .Z.NEMASSBOST, .Z.NEWHAMPSHIRE, .Z.RHODEISLAND, .Z.SEMASS, .Z.VERMONT, .Z.WCMASS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | isone:rt_lmp_5min | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T23:33:09Z to 2026-11-16T14:33:51Z; 67 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 57924 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_rtm_15m_mean` |  | USD/MWh | 57924 | 2026-08-27T04:00:00Z | 2026-11-16T04:45:00Z |

### `isone_rtm_zone_prices_hourly`

ISO-NE's hourly real-time locational marginal price (final, or preliminary until the final is posted) at one of its eight load zones or its Internal Hub for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15993.

- **Time:** ts_utc is the start of the hour in UTC (ISO-NE's hour ending, Eastern, read with gridstatus's helper); operating days are America/New_York days.
- **Revisions:** Merged by (entity, variable, ts_utc); a preliminary day is replaced by the final one when a later run's three-day window holds it, and a final day is replaced only while it is in a run's window. vintage is the final file's Last-Modified.
- **Source:** isone:rt_lmp_hourly_prelim Real-Time Energy Market Hourly LMPs, preliminary (https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-hourly-final)
- **Method note:** [`docs/methods/isone_rtm_zone_prices_hourly.md`](../methods/isone_rtm_zone_prices_hourly.md)
- **Cite as:** ISO New England (ISO-NE). Real-Time Energy Market Hourly LMPs, final; Real-Time Energy Market Hourly LMPs, preliminary. Via the Energy Research Warehouse (ERW), table `isone_rtm_zone_prices_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: isone:<node>, the node's ISO-NE name | none | text | isone:.H.INTERNAL_HUB, isone:.Z.CONNECTICUT, isone:.Z.MAINE, isone:.Z.NEMASSBOST, isone:.Z.NEWHAMPSHIRE, isone:.Z.RHODEISLAND, isone:.Z.SEMASS, isone:.Z.VERMONT, isone:.Z.WCMASS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T04:00:00Z to 2026-11-16T04:00:00Z; 1777 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -59.2 to 112.65; 4969 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO-NE's six states in every row, also for a zone in one state | none | text | US-CT,US-MA,US-ME,US-NH,US-RI,US-VT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: isone_rtm in every row: ISO-NE's real-time energy market | none | text | isone_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ISO-NE's name of the location: .H.INTERNAL_HUB (the Internal Hub) or .Z.<zone> for the eight load zones (CONNECTICUT, MAINE, NEMASSBOST, NEWHAMPSHIRE, RHODEISLAND, SEMASS, VERMONT, WCMASS) | none | text | .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE, .Z.NEMASSBOST, .Z.NEWHAMPSHIRE, .Z.RHODEISLAND, .Z.SEMASS, .Z.VERMONT, .Z.WCMASS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: isone:rt_lmp_hourly_final for a final row, isone:rt_lmp_hourly_prelim for a preliminary row | none | text | isone:rt_lmp_hourly_final, isone:rt_lmp_hourly_prelim | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.iso-ne.com/histRpts/rt-lmp/lmp_rt_final_20260826.csv, https://www.iso-ne.com/histRpts/rt-lmp/lmp_rt_final_20260827.csv, https://www.iso-ne.com/histRpts/rt-lmp/lmp_rt_final_20260828.csv; 69 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T19:46:22Z to 2026-11-16T14:33:58Z; 74 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The final file's Last-Modified; empty on preliminary rows (publish time not given by the source) | none | utc time | 2026-08-27T17:35:33Z to 2026-11-13T21:30:13Z; 68 distinct | 1296 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_rtm` | Hourly real-time locational marginal price (the price of energy at the location in the real-time market), ISO-NE's own hourly figure | USD/MWh | 15993 | 2026-08-26T04:00:00Z | 2026-11-16T04:00:00Z |

