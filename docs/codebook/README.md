# The ERW codebook

What every public table of the Energy Research Warehouse holds: what a row is, and what each column and each variable means, its unit, the values it takes and what an empty cell means. Drawn from `warehouse/metadata/variables/` (one file a table) by `warehouse/codebook/build_docs.py`; never written by hand. The same metadata answers `erw.describe(table)` and `erw.variables(table)` in the Python package. Nothing in it is guessed: a label comes from the method note, the connector, the source's documentation or the data, and where none of them says, it reads "not documented by the source".

## The counts

- Public tables with a metadata file: 582; documented in full (what a row is, and every column's label and unit): 582.
- Columns: 10453; documented: 10453 (a shared column is documented once, below).
- Variables of the series tables (values of `variable`): 6924; labelled: 6924.
- Entries that read "not documented by the source": 3.
- Column names that two or more tables label differently (names that may mean two things): 301.

## The families

| Family | Tables | Documented in full |
|---|---|---|
| [afdc](afdc.md) | 3 | 3 |
| [ba](ba.md) | 3 | 3 |
| [battery](battery.md) | 4 | 4 |
| [boem](boem.md) | 3 | 3 |
| [caiso](caiso.md) | 15 | 15 |
| [carbon](carbon.md) | 3 | 3 |
| [census](census.md) | 6 | 6 |
| [cer](cer.md) | 3 | 3 |
| [company](company.md) | 3 | 3 |
| [cost](cost.md) | 3 | 3 |
| [datacenter](datacenter.md) | 4 | 4 |
| [desnz](desnz.md) | 17 | 17 |
| [doe](doe.md) | 5 | 5 |
| [eia](eia.md) | 112 | 112 |
| [eia860](eia860.md) | 9 | 9 |
| [eia860m](eia860m.md) | 4 | 4 |
| [eia861](eia861.md) | 13 | 13 |
| [eia923](eia923.md) | 3 | 3 |
| [eia930](eia930.md) | 37 | 37 |
| [energy](energy.md) | 8 | 8 |
| [epa](epa.md) | 8 | 8 |
| [ercot](ercot.md) | 38 | 38 |
| [erw_derived](erw_derived.md) | 30 | 30 |
| [eurostat](eurostat.md) | 27 | 27 |
| [ferc714](ferc714.md) | 2 | 2 |
| [grid](grid.md) | 5 | 5 |
| [interchange](interchange.md) | 3 | 3 |
| [interconnection](interconnection.md) | 5 | 5 |
| [iso](iso.md) | 11 | 11 |
| [isone](isone.md) | 4 | 4 |
| [large](large.md) | 4 | 4 |
| [lbnl](lbnl.md) | 8 | 8 |
| [news](news.md) | 1 | 1 |
| [noaa](noaa.md) | 21 | 21 |
| [nrc](nrc.md) | 7 | 7 |
| [nyiso](nyiso.md) | 7 | 7 |
| [onrr](onrr.md) | 3 | 3 |
| [ornl](ornl.md) | 5 | 5 |
| [other_sources](other_sources.md) | 94 | 94 |
| [policy](policy.md) | 3 | 3 |
| [price](price.md) | 4 | 4 |
| [spp](spp.md) | 5 | 5 |
| [statcan](statcan.md) | 8 | 8 |
| [statec](statec.md) | 4 | 4 |
| [storage](storage.md) | 4 | 4 |
| [usbr](usbr.md) | 3 | 3 |
| [usgs](usgs.md) | 3 | 3 |
| [utility](utility.md) | 5 | 5 |
| [wb](wb.md) | 2 | 2 |

## The shared column names

Defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml), in the data standard's words ([`docs/datastandard.md`](../datastandard.md)).

| Column | Label | Type | Unit | Rule |
|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | text | none | Written namespace:native_id, where the namespace is the publisher part of the table name and native_id is the publisher's own identifier, unchanged (ercot:HB_NORTH). Stable across tables, so tables can be joined on it. |
| `variable` | What was measured (a price, a load, a count), in snake_case | text | none | Each table's file lists the values its variable column takes, with the unit of each. |
| `ts_utc` | The time of the observation, in UTC | utc time | none | ISO 8601 in UTC with a trailing Z (2026-09-01T05:00:00Z). For an interval it marks the start of the interval. For a daily or longer frequency it is the date at 00:00:00Z and names the date the publisher reports (a trading date, a month, a year), not an instant. |
| `value` | The number observed, in the row's unit | number | the row's unit column | Never empty. A missing observation is an omitted row, not a row with an empty value. Nothing is interpolated, imputed or filled; a derived value is its own variable. |
| `unit` | The unit of the row's value | text | none | A word of the closed vocabulary of the data standard (MW, MWh, USD/MWh, pct, count and the others it lists), enforced by the validator. |
| `freq` | How long the interval of the row is | text | none | An ISO 8601 duration (PT5M five minutes, PT15M, PT1H an hour, P1D a day, P1M a month, P3M a quarter, P1Y a year). |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | text | none | The smallest region that contains the entity. Where no single code applies, a comma-separated list with no spaces (US-CT,US-MA,US-ME). Checked by the validator. |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | text | none | The market or program within the publisher, as the table's file says. |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | text | none | The publisher's own name for the price location, unchanged. |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | text | none | Names the report the row was read from. For a table the ERW computes, erw:<builder>. |
| `source_url` | The address of the exact document the row was read from | text | none | The document's own address, or the report page where the document has no stable address. |
| `retrieved_at` | When the ERW fetched the document, in UTC | utc time | none | ISO 8601 in UTC with a trailing Z. |
| `vintage` | When the publisher published the document the value came from, in UTC | utc time | none | Distinguishes revisions of the same observation. Where a table keeps more than one revision on purpose, vintage is part of its key. |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | text | none | The EIA-930 balancing authority code, lowercase, as the table name used to carry it before tables were joined (session 29). |
| `year` | The operating year a history table was published by | text | none | The publisher's year (for ERCOT, the year in Central time). Not derivable from ts_utc, whose first hours of 1 January UTC belong to the year before. |
| `entity_id` | The identifier of the thing, as namespace:native_id | text | none | The same rule as the series entity. Unique within the table. |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | text | none | A word of the standard's list of entity types. |
| `name` | The thing's name, as the publisher writes it | text | none | Unchanged from the publisher. |
| `lat` | Latitude, in decimal degrees (WGS84) | number | degree | WGS84 decimal degrees, north positive. |
| `lon` | Longitude, in decimal degrees (WGS84) | number | degree | WGS84 decimal degrees, east positive (so the United States is negative). |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | number | MW | The rating the publisher states; each table's file says which rating where its source says. |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | text | none | In an entities table, one of the eight words of Decision 20; the publisher's own status is kept in a column of its own. In an events table, the state of the deal or filing (announced, signed, approved, terminated and so on). |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | date | none | YYYY-MM-DD. Each table's file says which of the two dates it is, where its source says. |
| `operator` | The operator or owner, as the publisher writes it | text | none | The publisher's name, or an entity_id where the operator is itself in an entities table. |
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | text | none | The publisher's id (a docket number) where it has one; otherwise a stable hash documented by the connector. Unique within the table. |
| `event_date` | The date the event happened or was announced (each table's file says which) | date or utc time | none | YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SSZ where the time matters (a story's publication time). |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | text | none | A short snake_case word; each table's file lists the values it takes. |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | text | none | Names unchanged, joined by ";". |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | text | none | Values of an entities table's entity_id, joined by ";". |
| `mw` | The capacity involved, in megawatts | number | MW | As the publisher states it. |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | number | the row's currency per MWh, unless the table's file says otherwise | As the publisher states it. |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | text | none | ISO 4217. |

