# ERW Data Standard v0

The data standard of the Energy Research Warehouse (ERW). It tells a person or an agent exactly what to produce when turning a source into ERW tables. Read it before writing a connector.

Modeled on the Item Response Warehouse (IRW) data standard (`datastandard.md` in github.com/ben-domingue/irw), which defines one long table shape, `id, item, resp`. That shape does not fit energy data, so the ERW defines three shapes instead. The IRW's habits carry over unchanged: long format, fixed column names, required columns first, one table per coherent product, short lowercase file names, and a validator that enforces what this page states.

> **v0 will change as sources are added.** Only the `series` shape has a connector and a validator today. `entities` and `events` are specified here so that the first connectors for them start from a shared draft, and they are expected to change once real sources meet them. A change to a required column or a unit convention bumps the version at the top of this file and gets a line in Decisions.

`warehouse/validate/erw_validate.py` enforces the `series` rules below. Where this page and the validator disagree, raise it and fix one of them; do not follow either silently.

---

## General rules (all shapes)

- **CSV, UTF-8, comma separated, one header row.** Long format: one row per observation, thing, or event.
- **Provenance header.** A file may begin with comment lines starting with `#`. Every file a connector writes **must** have them, naming at least: the source organization, the source report or product and its identifier, the source URL, the retrieval timestamp in UTC, and the connector that wrote it. Comment lines appear only before the header row. Readers skip them by counting them (`pandas.read_csv(path, skiprows=n)`); do not use `comment="#"`, which would also cut any value containing `#`, such as a URL.
- **Column names** are lowercase `snake_case`. Required columns come first, in the order given below. Optional columns use the reserved names below exactly; never invent a variant such as `timestamp` or `price_usd`. Source-specific extra columns go after the reserved ones and are prefixed `x_`.
- **Timestamps are UTC**, ISO 8601, with a trailing `Z`: `2026-09-01T05:00:00Z`. A timestamp for an interval marks the **start** of the interval. Local market time is never stored; convert it, handling daylight saving explicitly.
- **Dates** (no time of day) are ISO 8601 `YYYY-MM-DD`. In a `series` table with a daily or longer `freq` (`P1D`), `ts_utc` is the date at `00:00:00Z`: it names the date the source reports (a trading date, for example), not an instant.
- **Units.** Power in MW, energy in MWh, prices in USD per MWh, money in USD, unless a `unit` column (or the field definition) says otherwise. Unit strings come from a closed vocabulary, enforced by the validator: `MW`, `MWh`, `USD/MWh`, `USD`, `USD/MMBtu` (natural gas), `USD/bbl` (crude oil), `degF`, `pct`, and since session 7 (Decision 17) `USD/gal`, `USD/short_ton`, `USD/t`, `USD/lb`, `USD/MW-day`, `USD/tCO2`, `USD/Mcf`, `count`, `kbbl`, `kbbl/d`, `MMcf`, `bcf`, `bcf/d`, since session 24 (Decision 27) `mph`, since session 31 (Decision 29) `hour`, an hour of the day (0 to 23, local time, the hour's start), since session 32 (Decision 30) `tCO2` (metric tons of CO2) and `kgCO2/MWh` (kilograms of CO2 per MWh), and since session 49 (Decision 33) `degF-day` (heating or cooling degree days at 65 F), `bbl` (barrels) and `Mcf` (thousand cubic feet), and since session 51 (Decision 34) `USD/MW` and `MWh/MW` (revenue and energy per MW of installed capacity, `merchant_revenue_monthly`). A new unit is added here and to the validator together.
- **Missing values** are empty cells. No sentinel codes (`-999`, `NA`, `null`). In `series`, a missing observation is an omitted row, not a row with an empty `value`.
- **License.** Every source has a license in `warehouse/metadata/sources.csv`, the source registry: `internal` (licensed for internal use only; never shown on the public site or redistributed) or `public`. PJM data are `internal`; every other source is `public`. A table is `internal` if any of its sources is. The table-level value is the `license` column of `warehouse/metadata/coverage.csv`, which `erw.coverage()` exposes so the public site can filter on it. The rule's one home in code is `license_of` in `warehouse/connectors/iso_prices.py`.
- **No invented numbers.** Every value comes from a source named in the file. Nothing is interpolated, imputed, or filled. A derived value (an average, a spread) is its own `variable` with its method documented in the connector, never a silent fill.

## File naming

`source_market_product.csv`, for example `ercot_dam_hub_prices.csv`.

- `source` is the publishing organization or system (`ercot`, `caiso`, `eia`, `ferc`).
- `market` is the market or program within it (`dam`, `rtm`, `form860`). Use `all` when there is none.
- `product` is a short label for what the table holds (`hub_prices`, `load_zone_prices`, `plants`).
- Lowercase letters, digits and underscores only; at least three underscore-separated parts.
- **40 characters or fewer**, excluding `.csv`. Shorten `product` first; never shorten `source`.
- One table per coherent product. Day-ahead and real-time prices are different products and go in different files. The one exception is the ERCOT yearly history, `ercot_all_hub_prices_history`, by the session 29 ruling; its `market` column keeps them apart.
- **Partition keys are columns, never name suffixes** (session 29, decision 28). Tables that share their columns and differ only by a value (an ISO, a balancing authority, a market, a year, a hub) are one table, with that value in a column: `market` where it already holds it, else a reserved partition column (`ba`, `year`, and since session 36B `event`). Never `eia930_ciso_demand` beside `eia930_erco_demand`; always `eia930_all_demand` with `ba`. The map of the tables consolidated in session 29 is `warehouse/metadata/table_migrations.csv`.

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
| `geo` | reserved | string | ISO 3166-2 code for the smallest region that contains the entity: `US-TX`. Where no single code applies, a comma-separated list with no spaces: `US-CT,US-MA,US-ME`. Checked by the validator |
| `market` | reserved | string | Market the value belongs to, lowercase: `ercot_dam`, `ercot_rtm` |
| `node` | reserved | string | Pricing node, hub or zone name exactly as the source writes it: `HB_NORTH` |
| `source` | reserved | string | Required by the validator in v0. `organization:report_id`: `ercot:NP4-190-CD` |
| `source_url` | reserved | string | URL of the exact document the value was read from, or of the report page when there is no stable document URL |
| `retrieved_at` | reserved | string, ISO 8601 UTC | When the connector fetched the document |
| `vintage` | reserved | string, ISO 8601 UTC | When the source published the document the value came from. Distinguishes revisions of the same observation |
| `ba` | partition | string | Session 29: the EIA-930 balancing authority code, lowercase, as the table name used to carry it: `ciso`, `erco`, `us48` |
| `year` | partition | string | Session 29: the operating year a history table was published by (ERCOT: the year in Central time), `2024`. Not derivable from `ts_utc`, whose first hours of 1 January UTC belong to the year before |

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
| `status` | no | string | One of `operating`, `planned`, `under_construction`, `retired`, `withdrawn`, `active`, `completed`, `suspended` (Decision 20). The source's own status goes in its own column (`eia_status`, `iso_status`) |
| `status_date` | no | date | Date the status took effect, or was reported if the effective date is unknown (say which in the connector) |
| `operator` | no | string | Operator or owner name as the source writes it. An `entity_id` when the operator is itself in an entities table |
| `source` | yes | string | `organization:report_id` |

## Shape (c): `events`

One row per deal, filing, or announcement.

| Column | Required | Type | Rules |
|---|---|---|---|
| `event_id` | yes | string | `namespace:native_id` when the source has an id (a docket number); otherwise a stable hash documented by the connector |
| `event_date` | yes | date or UTC time | `YYYY-MM-DD`, or `YYYY-MM-DDTHH:MM:SSZ` when the time matters (news publish time). Date the event happened or was announced (say which in the connector) |
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

## Provenance tiers

Session 28, from Ben Domingue's review (`docs/feedback/ben-2026-09-28.md`, item 6). Every table has one tier, the `tier` column of `warehouse/metadata/coverage.csv`. It tells a user citing a number what kind of number it is.

| Tier | Means | Examples |
|---|---|---|
| `source` | Every value is as the publisher published it. The ERW reshapes, renames, converts units by a stated rule and merges runs, but writes no value of its own | ISO prices, EIA-930, EIA series, the queues, NWS weather |
| `derived` | Computed by ERW code from other tables, with a method in `docs/methods/`. No model is involved | the trader view, the ERCOT peak premium, the curtailment sums, `energy_projects` |
| `model_extracted` | At least one column was written by a model reading text: extracted from news or filings, scored, or researched on the web. The row links the text it was read from | `energy_deals`, `datacenter_projects`, `policy_reads`, `energy_companies`, the scores in `news_stories`, `news_index` and `policy_actions` |

Rules:

- **The lowest tier wins.** A table is `model_extracted` if any of its columns is a model's, even when most columns are a source's: `policy_actions` holds Federal Register records, but its `significance`, `sector` and `why` are the model's. For these mixed tables, the model's columns are the ones the table's header names as the scorer's or extractor's.
- **Tiers are inherited.** A table built from a `model_extracted` table (its `Derived from:` header line) is `model_extracted` (`datacenter_facilities`).
- **Where it is set.** `warehouse/metadata/build_coverage.py` sets the tier by its `TIER_RULES`, else `derived` for a derived table, else `source`. The build fails if a table's rows name a model (a `model_id` column), or its header names a Claude model, but no rule makes it `model_extracted`. So a model's output cannot be labelled as a source's by omission.
- **Where it shows.**
  - The Supabase catalogue (migration 008).
  - `erw.tier()`, `erw.cite()` and `erw.info()`.
  - The site's `/data` table.
  - Every citation on the site: a short "model-extracted" label next to such a table.
  - The chat's tool results and citations. The chat is told to say "model-extracted" next to a number from such a table.
- **How to cite one.** A `model_extracted` number is cited with the source the row links, not as the publisher's figure. The spot checks in the session reports give its measured accuracy (for example, 0.95 of deal fields correct in session 15's check).

---

## Decisions in v0

What was chosen, and why:

1. **Three shapes, not one.** The IRW fits everything into `id, item, resp`. Energy data is a mix of time series, registries of things, and dated transactions; forcing a plant list into a time series (or a PPA into either) would lose meaning. Three shapes is the smallest number that keeps each one honest.
2. **`ts_utc` is interval start.** Most ISOs publish "hour ending"; the ERW converts to interval start so that hourly and 15-minute series align on the same instants. The original local labels are dropped.
3. **Entity ids are namespaced source ids** (`ercot:HB_NORTH`), not ERW-minted ids. Minting ids needs a registry and a human to resolve conflicts. Namespacing keeps ids stable and collision-free now, and a crosswalk can be added later without changing any table.
4. **`unit` and `source` are optional in the schema but required by the validator.** They are listed as reserved optional columns because a future table may carry the unit in its variable definition. In v0 every table carries both, and the validator blocks a table without them.
5. **One row per revision only when the table says so.** v0 tables keep the value the connector retrieved and record the publication time in `vintage`. Keeping full revision history is deferred.
6. **Provenance is both per file and per row.** The header comment names the report and retrieval time for a reader of the file; `source`, `source_url`, `retrieved_at` and `vintage` let a row survive being copied out of its file.
7. **`geo` may be a comma-separated list of ISO 3166-2 codes, and the validator checks it** (session 2, error `geo_format`). Reason: multi-state ISOs (MISO, SPP, ISO-NE) have no single code, and an unchecked free-text `geo` would drift.
8. **`ts_utc` must sit on the grid its `freq` declares, for fixed sub-daily `freq`** (session 2, error `ts_freq_alignment`). Reason: NYISO publishes real-time prices at irregular off-grid times (for example 09:47:51), and a table passing them through under `PT5M` would misstate its own frequency.
9. **A 15-minute mean of 5-minute prices is its own variable, `<variable>_15m_mean`** (session 2, for example `lmp_rtm_15m_mean`), per the no-invented-numbers rule that a derived value is never labeled as a published one. Not a validator check.
10. **Units are a closed vocabulary, and `USD/MMBtu` and `USD/bbl` join it** (session 5, error `unit_vocabulary`). Reason: EIA fuel prices arrive as `$/MMBTU` and `$/BBL`; without a vocabulary each connector would spell units its own way and nothing would catch it.
11. **A daily or longer `freq` puts `ts_utc` at `00:00:00Z` of the reported date** (session 5, error `ts_freq_alignment` extended). Reason: EIA daily spot prices are trading dates, not instants; one fixed convention keeps daily series joinable and stops a local-midnight conversion from shifting a date.
12. **Completeness for trading-day series** (session 5, connector rule, not a validator check). A calendar-day completeness rule cannot apply to prices published on trading days only, so for such series every date the source lists must carry a number, a date listed without a value is an omitted observation (and is logged), and the series must be current (the connector sets the staleness limit).
13. **Human rulings, session 5**, each applied where noted:
    - A market failing three scheduled daily runs in a row opens a GitHub issue (`warehouse/metadata/run_status.py streaks`, run by the workflow).
    - No retention window: tables keep their full history; history moves to Redivis later.
    - Each run's per-connector, per-table status is appended to the tracked `warehouse/metadata/run_status.csv`.
    - The source registry `warehouse/metadata/sources.csv` is merged like the tables (never loses a report), and `erw.cite()` reads it.
    - CAISO real-time stays on RTD 15-minute means for now.
    - ISO-NE also gets its hourly final real-time LMPs as `isone_rtm_zone_prices_hourly` (variable `lmp_rtm`); the 5-minute-derived `isone_rtm_zone_prices` is kept and written when complete.
    - The `erw` package stays installable from the repository only until Redivis exists.
    - `erw.fetch` takes optional `start`, `end` and `node` arguments that subset rows.
    - Raw files stay local; runs older than 14 days are pruned, every `manifest.csv` kept (`warehouse/prune_raw.py`).
    - The geo footprint lists and the SPP footprint are checked by the human separately.
    - PJM data are licensed for internal use only: the `license` column above. A PJM connector is throttled to at most 5 requests per minute (not built yet: no PJM key).

14. **EIA-930: a gappy per-fuel series is dropped, not the table** (session 6 human ruling a). In an EIA-930 table, `demand_mw`, `demand_forecast_mw` and `net_generation_mw` must be complete for the window or the table is not written. A `net_generation_<fuel>_mw` series missing any hour is dropped for that run, named in the table header and in `warehouse/metadata/run_status.csv` (status `ok`, detail `dropped series: ...`), and rows for it from earlier complete runs are kept. Reason: one sporadic fuel series (for example EIA's unknown-storage category) should not withhold complete demand and generation data.

15. **News stories in the events shape, and validator checks for events** (session 6). `news_stories` holds one row per story: the events columns in order, then `title`, `summary` (at most 500 characters; never an article body), `feed`, `feed_sector`, `feed_region` (the feed's beat, from `warehouse/news/feeds.yaml`), `retrieved_at`, and the model's scores `significance`, `ai_power_relevance` (0 to 10), `sector`, `region`, `price_mentioned`, `why`, `cluster_id`, `model_id`, `scored_at`; the model's `mw` and `parties` fill the standard columns. `event_date` may carry a time: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` (UTC), because a news brief needs the publish time. An events table is named `domain_product` with at least two parts (it has no market; series keep `source_market_product`). Third-party news text is `internal` in the source registry: stored for scoring and linking, not republished. The validator now enforces the events shape: standard columns first and in order, unique non-empty `event_id`, `event_date` format, `source` and an http(s) `source_url` present, numeric `mw`, `price` and scores (scores 0 to 10), ISO 4217 `currency`. Reason: news is the first events source, and a shape without checks would drift.

16. **Human rulings, session 7, on news.** (a) Significance is judged across the whole energy industry; an AI or datacenter angle earns no significance credit by itself; `ai_power_relevance` is the only place AI counts (`warehouse/news/rubric.md`, verbatim in the scoring prompt). Headlines and why lines may not mention AI, datacenters or compute unless the source's title or summary does. Stories scored before the change are not re-scored. (b) Google News links are followed once per story and the result is cached in the row: `source_url` becomes the outlet URL when the redirect reaches the outlet, the Google link moves to `google_news_url`, and `url_resolved` records `yes` or `no: <reason>`. (c) `news_index` is a public companion to `news_stories` holding only `event_id`, `event_date`, `event_type` (required by the events shape), `source`, `source_url`, `sector`, `region`, `significance`, `ai_power_relevance`, `cluster_id` and the model's `headline`; `news_stories` stays internal. (d) A table may declare its own license in a `License: public` or `License: internal` header line; the coverage builder uses the declared value, and otherwise derives the license from the table's sources in the registry.

17. **Units for the price board** (session 7, error `unit_vocabulary`). Added to the closed vocabulary, each with the table that first needs it:
    - `USD/gal`: US dollars per US gallon (refined product spot and retail prices; EIA `$/GAL`). `eia_product_spot_prices`, `eia_retail_fuel_prices`.
    - `kbbl/d`: thousand barrels per day (EIA `MBBL/D`; EIA's "M" is thousand). `eia_petroleum_trade_weekly`.
    - `kbbl`: thousand barrels (EIA `MBBL`). `eia_petroleum_stocks_weekly`.
    - `MMcf`: million cubic feet (EIA `MMCF`). `USD/Mcf`: US dollars per thousand cubic feet (EIA `$/MCF`). `eia_lng_exports_monthly`.
    - `USD/MW-day`: US dollars per megawatt of capacity per day (capacity auction clearing prices). `pjm_rpm_capacity_prices`.
    - `USD/tCO2`: US dollars per metric ton of CO2 or CO2e (California allowances). `carb_auction_allowance_prices`.
    - `USD/short_ton`: US dollars per short ton (2,000 lb). RGGI allowances cover one short ton of CO2. `rggi_auction_allowance_prices`.
    - `USD/t`: US dollars per metric ton (IMF coal and nickel on FRED). `USD/lb`: US dollars per pound (uranium U3O8). `fred_imf_commodity_prices`.
    - `count`: a number of things, named by the variable (allowances offered and sold; later rig counts). Carbon auction tables.
    - `bcf` and `bcf/d`: billion cubic feet, and per day. In the vocabulary for gas storage and flow series; no table uses them yet.
    Reason: the price board brings units the power tables never needed; the vocabulary grows with named tables and never admits a unit spelled two ways (`MMBtu` stays `USD/MMBtu`, never `$/MMBTU`). Values keep the publisher's unit: nothing is converted.

18. **Sector per table** (session 7). `coverage.csv` has a `sector` column, one or more of `power`, `gas`, `oil`, `products`, `lng`, `coal`, `uranium`, `carbon`, `capacity`, `metals`, `equities`, `news` (since then also `deals`, `datacenters`, and since session 30 `platform`, the ERW's own operating tables such as `api_cost_ledger`), separated by `;`, and `erw.filter(sector=...)` matches any of them. The sector is set per table by `SECTOR_RULES` in `warehouse/metadata/build_coverage.py`; a table no rule matches fails the build, so a new table's sector is always chosen, never defaulted. Reason: with oil, gas, carbon and capacity tables beside the ISO prices, `iso` and `market` no longer describe what a table is about.

19. **Table names on the price board** (session 7). The session 7 prompt asked for a table `capacity_prices`; the naming rule needs three parts and a publisher first, so PJM's is `pjm_rpm_capacity_prices` with the variable the prompt names (`capacity_price_usd_per_mw_day`) and entity `iso:zone` (`pjm:RTO`, `pjm:COMED`). ISO-NE and MISO would get `isone_fca_capacity_prices` and `miso_pra_capacity_prices` with the same variable. Series freq for auctions: `P1Y` (capacity, ts_utc at the delivery year's first day) and `P3M` (quarterly carbon auctions, ts_utc at the auction date, or the first of the month where only the month is published).

20. **Entities: first tables and validator checks** (session 8). `eia860m_*_generators` (EIA-860M) and `<iso>_interconnection_queue` (gridstatus) are the first `entities` tables. The validator now enforces the shape:
    - the standard columns first, in order; `entity_id`, `entity_type` and `source` never empty; `name` may be empty only where the source gives no name (MISO and SPP queues), and the count is reported;
    - `entity_id` is `namespace:id` and unique; `entity_type` is in the vocabulary above;
    - `geo` is ISO 3166; `lat` in [-90, 90] and `lon` in [-180, 180], numeric, and both or neither;
    - `capacity_mw` and every `*_mw` column numeric. A negative value is reported, not blocked: ISO queues list repowering requests as a net reduction (ERCOT `18INR0064`, -7.2 MW), and the ERW keeps what the source states;
    - `status` in the vocabulary `operating`, `planned`, `under_construction`, `retired`, `withdrawn`, `active`, `completed`, `suspended`; empty where the source gives none (34 SPP affected-system requests);
    - `status_date` and every `*_date` column `YYYY-MM-DD` and a real date; `source_url` http(s).
    Tables are named `source_product` with at least two parts (like events), since they have no market.
    Reason: the queue harmonization the session 8 prompt asks for (active, withdrawn, completed, suspended) needs the last three statuses; `operating` and `planned` alone cannot say that a queue position was withdrawn or finished.

21. **Entities tables are snapshots** (session 8). An inventory or a queue is one vintage of the source: a new vintage replaces the table's rows (`iso_prices.write_snapshot`) instead of merging, because a generator that retired or a queue position that was withdrawn must leave the table it left at the source. Earlier vintages remain in git history and the raw files. Each row carries `vintage` (EIA-860M: the inventory month; queues: the retrieval date) and `retrieved_at`. EIA-860M runs daily but writes only when EIA's newest published vintage changes; the queues run weekly (Mondays, UTC).

22. **Units for session 8.** `dwt` (deadweight tonnage, metric tons) joins the unit vocabulary for IMF PortWatch transit capacity. `USD/MWh` is reused for EIA retail electricity prices, converted from EIA's cents per kilowatt-hour by x10 (stated in the table header).

23. **Derived tables** (session 9). A derived table is computed by the ERW from other ERW tables, never from a source directly. Its code lives in `warehouse/derived/`, and its method is written out in `docs/methods/`. Rules:
    - It is an ordinary table of its shape (here `series`) and passes the same validator.
    - `source` is `erw:<method>` and `source_url` links the method doc.
    - The header names every input table on a `Derived from:` line. `coverage.csv` marks it `derived` = `yes`.
    - **License:** a derived table inherits the most restrictive license of its inputs (internal if any input source is internal, else public). The script writes it into the header and the registry, and `build_coverage.py` recomputes it from the input tables and fails if the two disagree.
    - It is written through the merge writer; a past period must be complete, and the current period is marked partial by an `n_intervals` variable.
    - The unit `ratio` (dimensionless) joins the vocabulary for metrics such as the worst-interval multiple.
    First derived tables: `ercot_peak_premium_annual` and `ercot_peak_premium_monthly` (`docs/methods/ercot_peak_premium.md`).

24. **Human rulings, session 16.** (a) **EIA-930 generation tables are complete per UTC day**, as the ERCO and NYIS demand tables have been since session 13: each day of the window whose `net_generation_mw` has all 24 hours is written; a day without is not, earlier runs' rows for it are kept, and it is a `gap` row in `warehouse/metadata/run_status.csv`. Within the days written, a `net_generation_<fuel>_mw` series missing any hour is dropped for the run, as in decision 14. Reason: EIA publishes net generation a day or more after demand, so the whole-window rule wrote no generation on most days. (b) **Extracted fields are never inferred beyond the stated words.** In `energy_deals`, `state`, `country` and `status` are kept only when the model returns a span of the story that is in the story and names the value (for a state, its name or postal code); otherwise they are empty, and empty is the correct answer. (c) Evidence sentences stay in the internal companion table (session 15 decision confirmed).

25. **Session 18: energy units, snapshots of partial days, curtailment.**
    - **Units.**
      - `TBtu` (trillion British thermal units) joins the unit vocabulary, for `eia_sector_energy_consumption_monthly` (EIA Monthly Energy Review), as EIA publishes it.
      - `MWh` is reused for EIA generation (published in thousand megawatthours) and EIA retail sales (published in million kilowatt hours). Both are converted by x1000, exact, and the conversion is stated in the table header, as in decision 22.
      - `count` is reused for EIA's number of customers.
    - **Snapshots of complete hours.** `eia930_generation_latest` is a `series` table written as a snapshot, replaced every run, like an entities table (decision 21). It holds hours of a day that is not yet complete. Each hour it holds is complete in itself: net generation and every energy source the balancing authority reports. The per-day rule of decision 24 (a) still governs `eia930_<ba>_generation`.
    - **A figure a source does not publish is named for what it is.** ERCOT publishes no curtailment. The ERW's variable is `<fuel>_below_hsl_mwh` (output below the High Sustained Limit), never `curtailed_*`, and its method says why it differs from curtailment (`docs/methods/curtailment.md`).
    - **Derived monthly sums** (`iso_curtailment_monthly`, `state_generation_mix_monthly`) use exact decimal arithmetic. A month is written only when every input value it needs is present. `state_generation_mix_monthly` carries the part of EIA's total that EIA does not itemize by source as its own variable, `net_generation_not_itemized_mwh`, so the groups add up to the published total.

26. **Session 19: the trader view.**
    - `MMBtu/MWh` joins the unit vocabulary, for the implied heat rate in `<iso>_trader_daily`.
    - On-peak is the standard 5x16 block: hours starting 06:00 to 21:00 local, on weekdays that are not NERC holidays.
    - A derived table recomputed from rolling windows keeps an unchanged row's `retrieved_at`, so the Supabase loader, which compares every column, rewrites only new or revised rows. The same rule applies to `state_generation_mix_monthly` since session 18.
27. **Session 24: weather.** `mph` joins the unit vocabulary, for wind speed in `weather_obs_hourly` and `weather_forecast_hourly` (National Weather Service); temperature is `degF`, already in the vocabulary. The NWS API gives metric values (degC, km/h); the connector converts them (F = C x 9/5 + 32; mph = km/h / 1.609344) and rounds to 0.1.
28. **Session 29: partition keys are columns, never name suffixes.** From Ben Domingue's review (item 5): one table per ERCOT year, per EIA-930 balancing authority and per ISO had made 113 tables in four days, against Redivis's cap of 1,000 per dataset. A family whose members share their columns and differ only by a value in the name is one table with that value in a column. `market` carries it where it already holds that value on every row (the trader view, the ISO hub prices, the ERCOT history's market); `ba` and `year` join the standard as reserved partition columns, placed after the provenance columns (`vintage`). Licenses and tiers are never mixed in one table. Session 29 consolidated 54 tables into 6 (`docs/migrations/2026-09-29-consolidation.md`; the map is `warehouse/metadata/table_migrations.csv`). The validator accepts `ba` and `year` as reserved names.
29. **Session 31: the hour of the day.** `hour` joins the unit vocabulary: an hour of the day, 0 to 23, in the local time the table names, as the hour's start (15 is 15:00 to 15:59). `storage_daily_cycle` reports the hour of the day's largest battery discharge and charge with it. It is a label of a clock hour, never a duration; a duration in hours is not written with it.
30. **Session 32: emissions.** `tCO2` (metric tons of carbon dioxide) and `kgCO2/MWh` join the unit vocabulary, for EIA-930's CO2 estimates (`eia930_all_emissions`, which EIA states in metric tons) and the ERW's carbon intensities. `USD/tCO2` already names the ton the same way. EIA's own intensities are in lbs/kWh; the ERW writes kg per MWh (1 lb/kWh = 453.59237 kg/MWh) and never mixes the two.
31. **Session 36B: `event` joins the reserved partition columns.** `event_window_daily` (the Historical Event Analyzer, `docs/methods/events.md`) holds the days around several events in one table; its `event` column names the event a row belongs to (`uri_2021`), placed after `ba`, as `ba` and `year` are. The validator accepts it as a reserved name. The table key was then (entity, variable, ts_utc), so overlapping events would have failed the build; decision 32 changed that.
32. **Session 36C: a table with an `event` column is keyed by it too.** Its key is (entity, variable, ts_utc, event), so events and their baselines can share days (a baseline year of one event may be another event's days). The validator, the archive's key hashes, the package's tests and the Supabase live set (migration 011: `series` gains an `event` column, `''` for every other table, and its primary key includes it) all use the wider key. Every other series table keeps (entity, variable, ts_utc). `event_window_daily`'s Uri rows were rebuilt under the new key and are unchanged.
33. **Session 49: degree days, barrels, Mcf.** `degF-day` joins the unit vocabulary for heating and cooling degree days at 65 F (`event_window_daily`'s station rows: for a day, the larger of zero and 65 less the day's mean temperature, or the mean less 65, the mean being (max + min) / 2 as the National Weather Service computes it). `bbl` and `Mcf` join it for well-level oil and gas volumes as the Texas Railroad Commission publishes them (`rrc_well_production_monthly`); `kbbl` and `MMcf` stay for national aggregates.
34. **Session 51: USD/MW and MWh/MW.** Revenue and energy per MW of installed capacity (`merchant_revenue_monthly`: what 1 MW of a solar, wind, battery or peaker asset earned and delivered in a month at an ISO hub). Per MW, because the page scales by the reader's size and every result is linear in it; `USD/MW-day` stays for capacity prices, which are per day.
35. **Session 58: grid notices in the events shape.** `caiso_grid_emergencies` holds one row per notice type, region and local day of CAISO's Grid Emergencies History Report. Its `event_type` is the grid operator's notice type, lower case: `flex_alert`, `rmo`, `transmission_emergency`, `eea_watch`, `eea1` to `eea3`, `alert`, `warning`, `stage1` to `stage3`, `vlrp`, `load_interruption`. An older name the operator's own summary counts under a newer one is filed under it (Power Watch as `flex_alert`, No Touch as `rmo`), with the printed name in `x_label`. `event_date` is the local operating day the notice covered, and a notice of several days is one row per day, because the operator's yearly counts are days. Reason: the events shape's types (ppa, filing, announcement) do not say what kind of emergency a day saw, and the reliability section counts days by type.
36. **Session 62: `year`, a duration.** `year` joins the unit vocabulary for a span of time measured in years, such as the median time from an interconnection request to commercial operation (`ai_power_regions`, `lbnl_median_years_to_cod`: days divided by 365.25). Reason: the measure is read in years (Berkeley Lab reports it so), and `count` would misstate it.
37. **Session 65: USD/kW-month and USD/MW-hour; capacity prices as published.** Two units join the vocabulary. `USD/kW-month`: US dollars per kilowatt of capacity per month, as NYISO and ISO-NE publish capacity prices. `USD/MW-hour`: US dollars per megawatt of capacity held for one hour, the day-ahead ancillary service clearing prices (`ercot_as_prices`, `caiso_as_prices`); it is not `USD/MWh`, which prices energy delivered. `iso_all_capacity_prices` keeps each market's clearing price in the unit its publisher prints (`USD/MW-day` for PJM and MISO, `USD/kW-month` for NYISO and ISO-NE): a table may hold more than one unit when the `unit` column says which, and nothing is converted in the table. The conversion to USD/kW-month is in `docs/methods/capacity_and_ancillary.md`. The session 65 prompt's name `capacity_prices` has two parts; by Decision 19 the table is `iso_all_capacity_prices` with the market in `market` (Decision 28). Its extra columns: `x_auction`, `x_period_end`, `x_note`, `x_license` (the row's own license; the table is internal as a whole).
38. **Session 67: the battery revenue stack; a variable that carries its dimensions.** `battery_stack_monthly` and `battery_stack_stress_daily` hold one hub's results for two strategies and three durations. The series key is (entity, variable, ts_utc), so the strategy and the duration are part of the variable, `<strategy>_<N>h_<metric>` (for example `foresight_4h_revenue_total_usd_per_mw`), and are repeated in the extra columns `x_strategy`, `x_duration_hours` and `x_metric` so a reader can filter without parsing. The session 67 prompt listed the columns market, hub, duration_hours, strategy and month: in the series shape they are `market`, `node`, `x_duration_hours`, `x_strategy` and `ts_utc` (the first day of the local month). Units `USD/MW` and `MWh/MW` (Decision 34) and `count`. The stress table carries `event` and is keyed by it too (Decision 32). A month with no held day has no revenue row: absence, never a zero. Method: `docs/methods/battery_stack.md`.
39. **Session 114: a day's statistics are rows, not columns.** `ercot_hub_prices_daily` holds, for each ERCOT hub, market and complete local operating day since 2015, the day's mean, peak and off-peak means, lowest and highest interval price, and its hours priced below zero and above 200 USD/MWh. Each statistic is a row of its own, with the market and the statistic in the variable (`da_mean`, `rt_max`, `rt_hours_below_zero`, as Decision 38 puts a dimension in the variable): the Supabase loader keeps only the standard columns of a series table, so a statistic written in an `x_` column would not reach the site. The session 114 prompt counted about 51,000 rows, one a hub, market and day; the table holds those 51,534 hub-days as 345,228 rows. The two counts of hours carry the unit `count` (a number of hours, where a 15-minute interval counts 0.25); `hour` stays a label of a clock hour (Decision 29). A day without a peak hour has no `peak_mean` row: absence, never a zero. A day with a missing interval is not written. Method: `docs/methods/ercot_hub_prices_daily.md`.
40. **Session 115: a row per resource and hour, the awards in `x_` columns.** `ercot_dam_esr_awards` holds ERCOT's 60-Day DAM Disclosure file for Energy Storage Resources as ERCOT prints it: one row per resource and hour, about 7,500 a day. The row's `value` is the resource's High Sustained Limit (`hsl_mw`), which every row has; the day-ahead energy award, its settlement point price, and each Ancillary Service's award and clearing price are `x_` columns, because most hours have no award, a blank award is no award, and a series `value` may not be empty. One row per value would be about fifteen times the rows. A table that needs its `x_` columns to be read does not go to the site's database, which keeps only the standard columns (Decision 39): this one is under `catalogue_hold`, and the page reads `ercot_storage_dam_awards_monthly`, built from it, one statistic a row (Decision 39), the fleet by local month. Its per-capacity figures are `USD/MW` (Decision 34), as `battery_stack_monthly`'s are, so the two can be set side by side; the session 115 prompt asked for per kW, which the page shows as this over 1,000. Its `revenue_*` variables are day-ahead awards valued at day-ahead prices, never what a battery earned, and the table's header says so. A month with fewer days held than the calendar has is never scaled: `days_held`, `days_missing` and `days_in_month` say what it rests on. Method: `docs/methods/ercot_storage_dam_awards.md`.

Deferred to a later version:

- A controlled vocabulary for `variable`, `entity_type`, `event_type` and `status`, enforced by the validator the way the IRW enforces its tag vocabulary.
- An entity crosswalk between namespaces (the same plant in EIA-860 and in an ISO queue).
- Revision history as a first-class concept, and a rule for which vintage the live layer serves.
- Parquet alongside CSV for large tables, and a size limit that forces it.
- Sharding rules for Redivis, which caps a dataset at 1000 tables (the reason the IRW shards). Session 29's consolidation (decision 28) puts the cap far away: 65 tables.
