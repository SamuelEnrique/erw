# ERW Data Standard v0

The data standard of the Energy Research Warehouse (ERW). It tells a person or an agent exactly what to produce when turning a source into ERW tables. Read it before writing a connector.

Modeled on the Item Response Warehouse (IRW) data standard (`datastandard.md` in github.com/ben-domingue/irw), which defines one long table shape, `id, item, resp`. That shape does not fit energy data, so the ERW defines three shapes instead. The IRW's habits carry over unchanged: long format, fixed column names, required columns first, one table per coherent product, short lowercase file names, and a validator that enforces what this page states.

> **v0 will change as sources are added.** Only the `series` shape has a connector and a validator today. `entities` and `events` are specified here so that the first connectors for them start from a shared draft, and they are expected to change once real sources meet them. A change to a required column or a unit convention bumps the version at the top of this file and gets a line in Decisions.

`warehouse/validate/erw_validate.py` enforces the `series` rules below. Where this page and the validator disagree, raise it and fix one of them; do not follow either silently.

---

## General rules (all shapes)

- **CSV, UTF-8, comma separated, one header row.** Long format: one row per observation, thing, or event.
- **Provenance header.** A file may begin with comment lines starting with `#`. Every file a connector writes **must** have them, naming at least: the source organization, the source report or product and its identifier, the source URL, the retrieval timestamp in UTC, and the connector that wrote it. Readers skip these lines (`pandas.read_csv(path, comment="#")`).
- **Column names** are lowercase `snake_case`. Required columns come first, in the order given below. Optional columns use the reserved names below exactly; never invent a variant such as `timestamp` or `price_usd`. Source-specific extra columns go after the reserved ones and are prefixed `x_`.
- **Timestamps are UTC**, ISO 8601, with a trailing `Z`: `2026-09-01T05:00:00Z`. A timestamp for an interval marks the **start** of the interval. Local market time is never stored; convert it, handling daylight saving explicitly.
- **Dates** (no time of day) are ISO 8601 `YYYY-MM-DD`.
- **Units.** Power in MW, energy in MWh, prices in USD per MWh, money in USD, unless a `unit` column (or the field definition) says otherwise. Unit strings are written as `MW`, `MWh`, `USD/MWh`, `USD`, `degF`, `pct`.
- **Missing values** are empty cells. No sentinel codes (`-999`, `NA`, `null`). In `series`, a missing observation is an omitted row, not a row with an empty `value`.
- **No invented numbers.** Every value comes from a source named in the file. Nothing is interpolated, imputed, or filled. A derived value (an average, a spread) is its own `variable` with its method documented in the connector, never a silent fill.

## File naming

`source_market_product.csv`, for example `ercot_dam_hub_prices.csv`.

- `source` is the publishing organization or system (`ercot`, `caiso`, `eia`, `ferc`).
- `market` is the market or program within it (`dam`, `rtm`, `form860`). Use `all` when there is none.
- `product` is a short label for what the table holds (`hub_prices`, `load_zone_prices`, `plants`).
- Lowercase letters, digits and underscores only; at least three underscore-separated parts.
- **40 characters or fewer**, excluding `.csv`. Shorten `product` first; never shorten `source`.
- One table per coherent product. Day-ahead and real-time prices are different products and go in different files.

---

## Shape (a): `series`

One row per observation of one variable, for one entity, at one time.

| Column | Required | Type | Rules |
|---|---|---|---|
| `entity` | yes | string | What was observed. Written `namespace:native_id`, where `namespace` is the `source` part of the file name and `native_id` is the source's own identifier, unchanged: `ercot:HB_NORTH`. Stable across files so tables can be joined |
| `variable` | yes | string | What was measured, `snake_case`: `spp_dam`, `spp_rtm`, `load`, `net_generation` |
| `ts_utc` | yes | string, ISO 8601 UTC | Start of the observation interval, `YYYY-MM-DDTHH:MM:SSZ` |
| `value` | yes | float | The number, in `unit`. Never empty |
| `unit` | reserved | string | Required by the validator in v0. `USD/MWh`, `MW`, `MWh` |
| `freq` | reserved | string | Interval length as an ISO 8601 duration: `PT5M`, `PT15M`, `PT1H`, `P1D`, `P1M` |
| `geo` | reserved | string | ISO 3166-2 code for the smallest region that contains the entity: `US-TX` |
| `market` | reserved | string | Market the value belongs to, lowercase: `ercot_dam`, `ercot_rtm` |
| `node` | reserved | string | Pricing node, hub or zone name exactly as the source writes it: `HB_NORTH` |
| `source` | reserved | string | Required by the validator in v0. `organization:report_id`: `ercot:NP4-190-CD` |
| `source_url` | reserved | string | URL of the exact document the value was read from, or of the report page when there is no stable document URL |
| `retrieved_at` | reserved | string, ISO 8601 UTC | When the connector fetched the document |
| `vintage` | reserved | string, ISO 8601 UTC | When the source published the document the value came from. Distinguishes revisions of the same observation |

The key of a `series` table is `(entity, variable, ts_utc)`, plus `vintage` when a table deliberately keeps more than one revision. Duplicate keys are an error.

## Shape (b): `entities`

One row per physical or corporate thing: a plant, a project, a datacenter, a counterparty.

| Column | Required | Type | Rules |
|---|---|---|---|
| `entity_id` | yes | string | `namespace:native_id`, same rule as `series.entity`. Unique within the table |
| `entity_type` | yes | string | `plant`, `generator`, `project`, `datacenter`, `substation`, `utility`, `company`, `counterparty` |
| `name` | yes | string | Name as the source writes it |
| `geo` | no | string | ISO 3166-2 code |
| `lat` | no | float | WGS84 decimal degrees |
| `lon` | no | float | WGS84 decimal degrees |
| `capacity_mw` | no | float | Nameplate capacity in MW, as the source states it (say which rating in the connector) |
| `status` | no | string | Source status, lowercased: `operating`, `planned`, `under_construction`, `retired`, `withdrawn` |
| `status_date` | no | date | Date the status took effect, or was reported if the effective date is unknown (say which in the connector) |
| `operator` | no | string | Operator or owner name as the source writes it. An `entity_id` when the operator is itself in an entities table |
| `source` | yes | string | `organization:report_id` |

## Shape (c): `events`

One row per deal, filing, or announcement.

| Column | Required | Type | Rules |
|---|---|---|---|
| `event_id` | yes | string | `namespace:native_id` when the source has an id (a docket number); otherwise a stable hash documented by the connector |
| `event_date` | yes | date | Date the event happened or was announced (say which in the connector) |
| `event_type` | yes | string | `ppa`, `interconnection_request`, `filing`, `announcement`, `acquisition`, `financing` |
| `parties` | no | string | Parties as named by the source, separated by `;` |
| `entity_ids` | no | string | `entities.entity_id` values involved, separated by `;` |
| `mw` | no | float | Capacity in MW |
| `price` | no | float | Price in `currency` per MWh unless the connector says otherwise |
| `currency` | no | string | ISO 4217: `USD` |
| `status` | no | string | `announced`, `signed`, `approved`, `terminated`, and so on |
| `source` | yes | string | `organization:report_id` or publication name |
| `source_url` | yes | string | The filing or article the row was read from |

---

## Decisions in v0

What was chosen, and why:

1. **Three shapes, not one.** The IRW fits everything into `id, item, resp`. Energy data is a mix of time series, registries of things, and dated transactions; forcing a plant list into a time series (or a PPA into either) would lose meaning. Three shapes is the smallest number that keeps each one honest.
2. **`ts_utc` is interval start.** Most ISOs publish "hour ending"; the ERW converts to interval start so that hourly and 15-minute series align on the same instants. The original local labels are dropped.
3. **Entity ids are namespaced source ids** (`ercot:HB_NORTH`), not ERW-minted ids. Minting ids needs a registry and a human to resolve conflicts. Namespacing keeps ids stable and collision-free now, and a crosswalk can be added later without changing any table.
4. **`unit` and `source` are optional in the schema but required by the validator.** They are listed as reserved optional columns because a future table may carry the unit in its variable definition. In v0 every table carries both, and the validator blocks a table without them.
5. **One row per revision only when the table says so.** v0 tables keep the value the connector retrieved and record the publication time in `vintage`. Keeping full revision history is deferred.
6. **Provenance is both per file and per row.** The header comment names the report and retrieval time for a reader of the file; `source`, `source_url`, `retrieved_at` and `vintage` let a row survive being copied out of its file.

Deferred to a later version:

- A controlled vocabulary for `variable`, `entity_type`, `event_type` and `status`, enforced by the validator the way the IRW enforces its tag vocabulary.
- Validator checks for `entities` and `events`.
- An entity crosswalk between namespaces (the same plant in EIA-860 and in an ISO queue).
- Revision history as a first-class concept, and a rule for which vintage the live layer serves.
- Parquet alongside CSV for large tables, and a size limit that forces it.
- Sharding rules for Redivis, which caps a dataset at 1000 tables (the reason the IRW shards).
