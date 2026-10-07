# Evidence pack: the Energy Research Warehouse (ERW)

Facts for a reader who will write from them and check them. Written on 7 October 2026 (UTC) from the repository at commit `64d7b83` (branch `wip/138-datacenter`). Every number below was computed or read on that day; each says from which file and how. Nothing was recalled, and no table, build, connector, loader or test was run: files were read and counted. Where files disagree both are given, with the one `ARCHITECTURE.md` section 2 says governs.

Three limits on what follows:

- **The table files on this machine trail `coverage.csv` by up to two days for some tables.** `warehouse/metadata/coverage.csv` is rebuilt by the daily run on GitHub and committed; the files in `warehouse/output` on this machine are older copies for some rolling tables (for example `eia930_all_emissions`: 4,326,048 rows in `coverage.csv`, 4,323,144 in the file here). Whole-table counts and dates are from `coverage.csv`. Per-grid dates inside a multi-grid table are from the file here and are marked so.
- **Redivis itself was not read.** What is said of the Redivis datasets is what the repository records.
- **Five session reports are not in this working tree** (125, 126, 129, 130, 131): `git log --all` finds them on other branches. They are used in one place only and named there.

## 1. What the ERW is

In the repository's words:

- `CLAUDE.md`, "What the ERW is": "The **Energy Research Warehouse (ERW)** is the live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets included. AI's demand for power is the sharpest current lens on that system, not its boundary. Coverage is US first, world later. Every source is reshaped into a small number of standard table shapes so that they can be joined and compared."
- `README.md`, first paragraph: "Every source is reshaped into three standard table shapes (series, entities, events), and every row names the report it came from and when it was retrieved."
- `docs/OVERVIEW.md`, "What it is": "One connector per source reshapes each source into one of three table shapes (series, entities, events); a validator gates every table; every row names its source report and retrieval time. Redivis is the store of record (a human releases each version), Supabase holds a live subset for the public site, and GitHub Actions runs everything on a schedule."
- `README.md`, "Lineage": "The ERW is modeled on the Item Response Warehouse (IRW) of Ben Domingue and colleagues at Stanford (itemresponsewarehouse.org). Its owner allowed the ERW to copy its infrastructure and documents." and "The ERW is built as a Stanford independent study."
- `README.md`, session log: session 1 is dated 2026-09-24/25. The newest report in the working tree is session 137 (`archive/sessions/`, 210 files).

The stack, from the table in `CLAUDE.md`, "The stack":

| Layer | Tool | Role, as `CLAUDE.md` states it |
|---|---|---|
| Ingestion | Python 3 | "One connector per source in `warehouse/connectors/`, writing standard CSVs to `warehouse/output/`" |
| Warehouse of record | Redivis | "The published, versioned copy of every table (`warehouse/redivis/`). Uploads write a draft; what Redivis has released is what the ERW says" |
| Live layer | Supabase Postgres | "A small live set (`warehouse/supabase/`): public reads through row-level security. Derived from the warehouse, never the other way round" |
| Public site | Next.js on Vercel (`site/`) | "Reads Supabase with the anon key only" |
| Schedules | GitHub Actions | "Everything that runs on a clock (`.github/workflows/`...). No crontabs on anyone's machine" |
| Scoring and chat | Claude API | "News scoring, the weekday digest with its fun fact and the Sunday Roundup (`warehouse/news/`), the chart-of-the-week note (`warehouse/analysis/`), and question answering over the warehouse (`warehouse/chat/`, `/ask`)" |

A third store sits beside these (`ARCHITECTURE.md` section 1a): the durable archive, `warehouse/archive` and the private Supabase storage bucket `erw-archive`, "every row every run found new or changed, and every key it found gone, one file per table per month, append only".

Model use, as recorded: the models named in the cost ledger's rows are `claude-sonnet-5-5` and `claude-haiku-4-5-20251001` (column `model` of `warehouse/output/api_cost_ledger.csv`, read 7 October 2026). The chat's rule (`ARCHITECTURE.md` section 1): "every number in an answer must appear in a tool result".

## 2. Its tables

All counts in this section: `warehouse/metadata/coverage.csv`, read 7 October 2026 (171 data lines; newest `last_run` 2026-10-06T20:38:42Z).

| Measure | Tables | Rows | How |
|---|---|---|---|
| All tables | 171 | 22,367,753 | count of lines; sum of `n_rows` |
| Shape: series | 134 | 21,595,574 | see the note on shape below |
| Shape: entities | 21 | 164,870 | |
| Shape: events | 16 | 607,309 | |
| Tier: source | 105 | 19,557,324 | column `tier` |
| Tier: derived | 54 | 2,772,252 | |
| Tier: model_extracted | 12 | 38,177 | |
| License: public | 145 | 21,277,210 | column `license` |
| License: internal | 26 | 1,090,543 | |
| Validator: pass | 171 | 22,367,753 | column `validator_status` |

- **Shape** is not a column of `coverage.csv`. It was derived by reading the column row of each table's file in `warehouse/output` and applying the validator's own test (`warehouse/validate/erw_validate.py` lines 291 and 298: entities when the first two columns are `entity_id, entity_type`; events when an `event_id` column exists; series otherwise). The result agrees with `coverage.csv`'s `interval` column: 21 tables are `snapshot` and 16 are `event`.
- **Tier** is defined in `docs/datastandard.md`, "Provenance tiers": `source` ("every value is as the publisher published it"), `derived` ("computed by ERW code from other tables... No model is involved"), `model_extracted` ("at least one column was written by a model reading text").
- **Tier by license:** source 87 public and 18 internal; derived 51 and 3; model_extracted 7 and 5 (cross count of the two columns).
- **Not in coverage:** `warehouse/output` on this machine holds 179 CSV files; eight are not in `coverage.csv`: `census_metro_population`, `eia930_demand_weather`, `noaa_grid_weather_daily`, `noaa_grid_weather_hourly`, `noaa_grid_weather_stations`, `noaa_station_weather_hourly`, `power_deals`, `power_deals_evidence`. They belong to sessions whose branches are not merged here; they are counted nowhere above.

**Other documents give other totals, each stale.** `README.md`: "As of 2026-09-29: 65 tables, 4,812,358 rows". `docs/OVERVIEW.md`: 113 tables, 4,812,358 rows. `STATUS.md` ("Generated 2026-09-30 23:49 UTC"): 82 tables, 10,425,611 rows. `docs/state_2026-10-04.md`: 132 tables, 16,048,958 rows. `ARCHITECTURE.md` section 2 names `warehouse/metadata/coverage.csv` and `docs/coverage.md` as the authority on "what the warehouse holds today".

The ten largest tables (`coverage.csv`, sorted by `n_rows`):

| Table | Rows | First | Last | License | Tier |
|---|---|---|---|---|---|
| `eia930_all_emissions` | 4,326,048 | 2018-07-02 | 2026-10-03 | public | source |
| `ercot_all_hub_prices_history` | 3,063,570 | 2015-01-01 | 2026-08-26 | public | source |
| `ercot_dam_esr_awards` | 1,849,293 | 2025-12-06 | 2026-08-08 | public | source |
| `ercot_sced_esr_hourly` | 1,458,735 | 2026-02-01 | 2026-08-06 | public | source |
| `carbon_intensity_hourly` | 1,121,493 | 2018-07-02 | 2026-10-03 | public | derived |
| `eia930_daily_interchange` | 946,750 | 2019-01-01 | 2026-10-04 | public | source |
| `caiso_fuel_supply_history` | 782,808 | 2018-06-01 | 2025-06-01 | public | source |
| `iso_hub_prices_history` | 486,388 | 2024-09-01 | 2026-10-08 | public | source |
| `caiso_curtailment_intervals` | 484,819 | 2019-01-01 | 2026-10-03 | public | source |
| `clean_energy_hourly` | 471,232 | 2019-01-01 | 2026-10-04 | public | derived |

**The Supabase live set.** 87 of the 171 tables match a rule of `warehouse/supabase/live_set.yaml` (75 under `full`, 12 under `recent`, which keeps the last 35 days): 84 public and 3 internal (`api_cost_ledger`, `ferc_eqr_contracts`, `price_board_carbon`, which row-level security hides from the anonymous key, per the file's comments). Computed by matching the file's patterns against the table names of `coverage.csv`. Of the 87, 16 are under `review_hold` (loaded, and in no count a visitor sees). A further 35 tables are named under `catalogue_hold` and are not loaded. `latest_prices`, which the 15-minute job writes, is a Supabase table and not an ERW table in coverage. Size limit: `max_mb: 7500` ("Supabase is on the Pro plan with the spend cap on", session 59 comment in the file).

**Redivis.** Two datasets, routed by license (`warehouse/redivis/README.md`; `warehouse/redivis/config.yaml`): `energy_research_warehouse` for public tables and `energy_research_warehouse_internal`, private, for the rest. The manifest `warehouse/metadata/redivis_uploads.csv` (221 lines, read 7 October 2026) records:

- 145 current lines in the public dataset, the 145 public tables of coverage, 21,277,210 rows;
- 22 current lines in the internal dataset, 712,018 rows; four internal tables of coverage have no line (`ferc_eqr_contract_terms`, `ferc_eqr_contracts_history`, `ferc_eqr_party_mw`, `ferc_eqr_quarter_changes`);
- 54 lines marked `migrated_to`: the tables session 29 folded into 6, which stay in the public draft "until a human runs `python warehouse/redivis/upload.py --remove-migrated`" (`CHANGELOG.md`);
- uploads dated from 2026-09-26T04:16:54Z to 2026-10-06T20:42:05Z.

**Released or drafted: drafted only, as far as the repository records.** `warehouse/redivis/README.md`: "`upload.py` only ever writes the dataset's **unreleased draft** (version `next`)". `docs/state_2026-10-04.md` line 83: "no released version exists to cite". `archive/sessions/SESSION_134_REPORT.md` line 23 (6 October 2026): tables "already in the Redivis drafts, unreleased". The checklist for a first release is `docs/accelerator/redivis_release_checklist.md`.

## 3. Its sources and licenses

`warehouse/metadata/sources.csv` as committed at `64d7b83`, read 7 October 2026: 250 rows, one per source report or news outlet; columns `source, publisher, report, report_url, document_list, license, tables, first_seen, last_seen`. (Another session was adding rows to the uncommitted file in the working tree on the same day: it held 254 rows at 01:53 UTC, four more data sources for tables not yet in coverage. The counts below are of the committed file.)

| Measure | Count | How |
|---|---|---|
| Sources (rows) | 250 | every `source` value is distinct |
| Data sources | 176 | rows whose `report` does not begin "news stories" |
| of them public / internal | 155 / 21 | column `license` |
| News outlets | 74 | rows whose `report` begins "news stories"; all internal |
| Distinct publisher names | 114 | distinct `publisher` strings: 43 among data sources, 74 among news outlets, three shared |

- **The publisher count overstates.** The same organization is written more than one way: "California ISO (CAISO)" and "California Independent System Operator (CAISO)"; "New York ISO (NYISO)" and "New York Independent System Operator (NYISO)"; "U.S. Energy Information Administration" with and without "(EIA)"; the ERW itself under four forms. No file gives a deduplicated count.
- **Other documents give other counts, each older.** `docs/OVERVIEW.md`: "Sources in the registry: 153: 83 data sources (74 public, 9 internal) and 70 news outlets". `docs/state_2026-10-04.md`: "210 sources in the registry". The registry file is the record.
- **Rows by publisher, data sources** (the same count): EIA 38 (36 public, 2 internal); the ERW's own derived sources 45; ERCOT 15; CAISO 12; ISO-NE 8; the St. Louis Fed (FRED) 8; SPP 7; MISO 6; NYISO 6; then one or two each for 28 other publisher names (31 rows).

**License classes.** Two: `public` and `internal` ("licensed for internal use only; never shown on the public site or redistributed", `docs/datastandard.md`, General rules). Tables in each: 145 public, 26 internal (`coverage.csv`). "A table is `internal` if any of its sources is." A table may also declare its license in a header line (Decision 16d).

**Publishers held internal, and why.** From the `License:` line of each table's header in `warehouse/output` and the registry:

| Publisher | Tables | Reason, as the repository states it |
|---|---|---|
| PJM Interconnection | `pjm_rpm_capacity_prices`, rows of `iso_all_capacity_prices` | "PJM data terms bar non-members from republishing." `docs/price-sources.md` line 184: "PJM, ISO-NE and MISO terms bar republication by non-members" |
| ISO New England | `isone_as_prices`, `isone_dam_cleared_energy`, rows of `iso_all_capacity_prices` | Its legal notice: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws" (`https://www.iso-ne.com/legal-privacy`). Its zone price tables are public |
| MISO | `miso_as_prices`, rows of `iso_all_capacity_prices` | Its terms forbid republishing (quoted below). Its hub prices and queue are marked public in the registry; see the pause |
| California Air Resources Board | `carb_auction_allowance_prices` | "CARB terms for this summary are unconfirmed." (`carb_lcfs_credit_prices` is public) |
| RGGI, Inc. | `rggi_auction_allowance_prices` | "The page says only '(c) RGGI'; terms unconfirmed." |
| IMF, through FRED | `fred_imf_commodity_prices` (5 series) | "IMF data on FRED; non-personal use needs the owner's permission." The registry's report names carry "(Copyrighted: Citation Required)" |
| IMF PortWatch | `portwatch_chokepoint_transits` | "IMF terms unconfirmed (terms page 403), so internal until confirmed (session 8 ruling)" |
| EIA, NYMEX futures only | `eia_all_futures_prices` | "internal, by session 127's reading, for a person to rule": EIA names NYMEX as the source and stopped republishing on 5 April 2024 |
| FERC | `ferc_eqr_*` (8 tables) | "its license statement could not be read by this machine (ferc.gov answers automated requests with HTTP 403), and session 83's instruction is an internal table" |
| Railroad Commission of Texas | `rrc_lease_production_monthly` | "The RRC offers its data sets "free of charge"; no page read grants reuse or redistribution." |
| News outlets (74) | `news_stories`, the `*_evidence` tables, `news_scores_shadow` | "Titles and summaries are the outlets' text, kept for scoring and linking, not for republication." |
| Anthropic (usage records) | `api_cost_ledger` | "Operating costs of the ERW, never shown on the public site or in the public Redivis dataset." |

`price_board_carbon` is internal because its inputs are (a derived table "takes the most restrictive license of its inputs", `README.md`, "License rule").

**The paused publisher.** `warehouse/metadata/paused_sources.csv` holds one row: MISO, `paused_on` 2026-10-04, reason "MISO's terms forbid automated access", ruled by "Samuel, 4 October 2026 (the closing ruling of session 89)", until "a review of MISO's terms by a person". The terms it quotes: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." `docs/methods/miso_pause.md`: seven pulls are paused (hub prices, the latest real-time price, the queue, the Planning Resource Auction results, the reserve prices, the hub price history, the MISO newsroom feed); "Every MISO table and every page stays exactly as it is. Nothing is deleted."; not paused are the figures for the MISO balancing authority from EIA, NOAA and Berkeley Lab. Every connector asks `iso_prices.paused()` first (`warehouse/connectors/iso_prices.py` line 102); the test is `tests/test_session89_miso_pause.py`.

**Terms sentences.** The registry holds a license class per source and no terms text; the only terms sentence in a metadata file is MISO's, above. The sentences for the other main publishers are quoted in method notes:

- **ERCOT** (`docs/methods/capacity_and_ancillary.md` line 71; `https://www.ercot.com/help/terms`, item 5): "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses". License: public.
- **California ISO** (`docs/methods/generation_mix_hourly.md` line 222; `caiso.com/privacy-terms-of-use`, read 6 October 2026): materials are "freely available for public use consistent with the general policies of the Public Records Act [...] and may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." License: public, credited.
- **EIA** (`docs/price-sources.md` line 22; `https://www.eia.gov/about/copyrights_reuse.php`): "Public domain, credit requested ("Source: U.S. Energy Information Administration")". License: public.
- **SPP** (`docs/methods/capacity_and_ancillary.md` line 127; `https://www.spp.org/terms-conditions/`): "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication". License: public, with citation; the note adds "If the platform sells anything built on these rows, the table must be ruled on again".
- **NYISO** (same file, line 124; `https://www.nyiso.com/legal-notice`): "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site". License: "public, with a caution", by the ERW's standing rule (every ISO but PJM).
- **MISO**, on republishing (same file, line 126): "You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content on this Website or the App in whole or in part."

Two terms pages could not be read when tried (HTTP 403): the IMF's (`SESSION_132_REPORT.md` line 26) and the NRC's (`SESSION_133_REPORT.md` line 38).

## 4. Coverage by grid and year

Dates are days (UTC). "Rolling" means the table keeps a recent window that the daily run merges into. Sources: `coverage.csv` (`ts_min`, `ts_max`) for a table that holds one grid; for a table that holds several, the first and last `ts_utc` of that grid's rows in the file in `warehouse/output` on this machine, read 7 October 2026 (see the first limit at the top: the last day can trail `coverage.csv` by up to two days). A snapshot table shows the day of the snapshot. Day-ahead tables can end after today because a published next-day auction is included (`docs/coverage.md`).

### Held for all seven grids, from EIA

| Kind | Table | First | Last | Notes |
|---|---|---|---|---|
| Demand, hourly, with EIA's day-ahead forecast | `eia930_all_demand` | 2026-08-26 (ERCOT, NYISO: 2026-08-27) | 2026-10-03 (file); 2026-10-05 (`coverage.csv`) | rolling; public |
| Demand and net generation, hourly, first half of 2018 | `eia930_all_history` | 2018-01-01 | 2018-07-01 | public |
| Demand, daily | `eia930_daily_demand` | 2019-01-01 | 2026-10-03 (file); 2026-10-05 (`coverage.csv`) | 71 balancing authorities and regions; public |
| Demand by year, average and peak, by hour and month | `eia930_demand_growth` | 2019 | 2026 | derived; hours screened by the rule for impossible values |
| Generation by fuel, hourly | `eia930_all_generation` | 2026-08-26 | 2026-10-03 (file); 2026-10-05 (`coverage.csv`) | rolling; 9 to 11 series a grid, the total included; public |
| Generation mix by hour of day, monthly | `generation_mix_hourly_profile` | 2019-01 | 2026-09 | derived |
| Generation by state and fuel, monthly | `eia_state_generation_monthly`, `state_generation_mix_monthly` | 2001-01 | 2026-07 | by state, not by grid |
| CO2 emissions, hourly (generated, consumed, imported, exported, by fuel) | `eia930_all_emissions` | 2018-07-02 (ERCOT: 2018-07-03) | 2026-10-01 (file); 2026-10-03 (`coverage.csv`) | public |
| Carbon intensity, hourly, daily, monthly | `carbon_intensity_hourly`, `_daily`, `_monthly` | 2018-07-02 (SPP daily: 2018-09-01) | 2026-10-03 | derived; California's generation side is CAISO's own from 2025-12-16 (`docs/methods/eia930_caiso_break.md`) |
| Interchange with each neighbour, daily | `eia930_daily_interchange` | 2019-01-01 | 2026-09-29 (file); 2026-10-04 (`coverage.csv`) | ties in the file: CAISO 12, MISO 13, SPP 11, PJM 7, NYISO 4, ISO-NE 3, ERCOT 2 |
| Interchange, hourly | `eia930_all_interchange` | 2026-09-13 | 2026-10-02 (file); 2026-10-04 (`coverage.csv`) | rolling |
| Interchange, hourly, event windows | `eia930_event_hourly_interchange` | 2021-02-07 | 2025-06-29 | the windows of the dated events only |
| Interconnection requests, national file | `lbnl_interconnection_queue` | snapshot 2026-10-02 | | Berkeley Lab, Queued Up 2026 edition; 38,201 requests |
| Battery units and the fleet by month | `storage_capacity`, `storage_buildout_monthly` | 2015-01 | 2026-08 | derived from EIA-860M |

Hourly demand and generation between July 2018 and August 2026 are not held as a table: the derived tables for those years are built from EIA's workbooks saved under `warehouse/raw/` (`SESSION_73_REPORT.md` line 60).

### Held by grid, from each operator and others

| Grid | Kind | Table | First | Last | License and notes |
|---|---|---|---|---|---|
| ERCOT | Prices, day-ahead and real-time, 6 hubs | `ercot_all_hub_prices_history` | 2015-01-01 | 2026-08-26 | public; day-ahead hourly, real-time 15-minute |
| ERCOT | Prices, hubs, rolling | `iso_dam_hub_prices`, `iso_rtm_hub_prices` | 2026-08-26 | 2026-10-05, 2026-10-04 (file) | public |
| ERCOT | Prices, hubs, by day | `ercot_hub_prices_daily` | 2015-01-01 | 2026-10-06 | derived |
| ERCOT | Prices, 310 settlement points, real-time | `ercot_rtm_node_prices` | 2026-09-28 | 2026-10-05 | public; one week (ERCOT lists seven days) |
| ERCOT | Ancillary prices | `ercot_as_prices` | 2018-01-01 | 2026-10-07 | public |
| ERCOT | Ancillary quantities | `ercot_as_quantities` | 2026-09-03 | 2026-10-05 | public |
| ERCOT | Capacity prices | none | | | no table (`iso_all_capacity_prices` holds ISO-NE, MISO, NYISO and PJM only) |
| ERCOT | Interconnection queue | `ercot_interconnection_queue` | snapshot 2026-10-05 | | public; 1,758 positions |
| ERCOT | Large loads, status reports | `ercot_large_load_status` | 2025-05-28 | 2026-03-26 | public; 29 rows from 9 reports. No request-level list exists (`known_gaps.csv`) |
| ERCOT | Curtailment | `ercot_wind_solar_hsl_daily` | 2026-09-19 | 2026-10-05 | public; output below the High Sustained Limit, "the ERW's estimate" (`docs/platform-tools.md`, tool 22) |
| ERCOT | Wind and solar forecast | `ercot_wind_solar_forecast` | 2026-09-27 | 2026-10-13 | public |
| ERCOT | Day-ahead energy cleared | `ercot_dam_cleared_energy` | 2026-09-23 | 2026-10-08 | public |
| ERCOT | Storage, EIA hourly | `eia930_all_storage` | 2024-11-07 | 2026-10-03 (file) | public |
| ERCOT | Storage, day-ahead awards by resource | `ercot_dam_esr_awards` | 2025-12-06 | 2026-08-08 | public; ERCOT's 60-day disclosure |
| ERCOT | Storage, real-time by resource | `ercot_sced_esr_hourly` | 2026-02-01 | 2026-08-06 | public |
| CAISO | Prices, day-ahead and real-time, 2 hubs | `iso_hub_prices_history` | 2024-09-01 | 2026-10-05, 2026-10-04 (file) | public; real-time is a 15-minute mean of 5-minute prices, its own variable |
| CAISO | Prices, 3 hubs, rolling | `iso_dam_hub_prices`, `iso_rtm_hub_prices` | 2026-08-26 | 2026-10-05, 2026-10-04 (file) | public |
| CAISO | Prices, day-ahead, alert days | `caiso_dam_alert_day_hub_prices` | 2023-07-14 | 2025-08-25 | public |
| CAISO | Generation by fuel, CAISO's own | `caiso_fuel_supply_history`, `caiso_fuel_supply` | 2018-06-01 | 2026-10-06 | public |
| CAISO | Wind and solar forecast | `caiso_wind_solar_forecast` | 2023-06-01 | 2026-10-06 | public |
| CAISO | Ancillary prices | `caiso_as_prices` | 2024-09-01 | 2026-10-07 | public |
| CAISO | Capacity prices | none | | | no table |
| CAISO | Interconnection queue | `caiso_interconnection_queue` | snapshot 2026-10-05 | | public; 2,278 positions |
| CAISO | Curtailment, daily | `caiso_curtailment_daily` | 2014-05-01 | 2026-10-04 | public; CAISO's own figure |
| CAISO | Curtailment, by interval | `caiso_curtailment_intervals` | 2019-01-01 | 2026-10-03 | public |
| CAISO | Storage, CAISO's own 5-minute series | `caiso_battery_storage` | 2025-08-24 | 2026-10-06 | public. EIA-930 itemizes no battery series for CAISO |
| CAISO | Day-ahead energy cleared | `caiso_dam_cleared_energy` | 2025-09-01 | 2026-10-07 | public |
| CAISO | Grid emergencies and Flex Alerts | `caiso_grid_emergencies` | 1998-05-30 | 2025-04-30 | public; events |
| PJM | Prices | none | | | **Not held: needs a license** (`README.md`: "Not in it yet: PJM energy prices") |
| PJM | Ancillary prices | none | | | not held |
| PJM | Capacity prices | `pjm_rpm_capacity_prices` | delivery year 2007-06 | delivery year 2028-06 | **internal**; 234 rows |
| PJM | Interconnection queue | in `lbnl_interconnection_queue` only | | | no PJM queue table |
| PJM | Curtailment, storage series | none | | | EIA-930 itemizes no battery series for PJM |
| MISO | Prices, 1 hub, history | `iso_hub_prices_history` | 2024-09-01 | 2026-10-04, 2026-10-03 (file) | public in the registry; **paused**: ends at the last pull |
| MISO | Prices, 8 hubs, rolling | `iso_dam_hub_prices`, `iso_rtm_hub_prices` | 2026-08-26 | 2026-10-04, 2026-10-03 (file) | public in the registry; **paused** |
| MISO | Ancillary prices | `miso_as_prices` | 2024-09-01 | 2026-10-04 | **internal, paused** |
| MISO | Capacity prices | `iso_all_capacity_prices` (`miso_pra`) | 2024-06-01 | 2027-03-01 | **internal, paused** |
| MISO | Interconnection queue | `miso_interconnection_queue` | snapshot 2026-09-30 | | public in the registry; **paused**; 3,881 positions |
| MISO | Curtailment | none | | | not held |
| MISO | Storage, EIA hourly | `eia930_all_storage` | 2025-01-16 | 2026-10-03 (file) | public; EIA's, not paused |
| NYISO | Prices, 11 zones, day-ahead and real-time | `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices` | 2026-08-26 | 2026-10-08, 2026-10-06 | public; rolling |
| NYISO | Prices, New York City, history | `iso_hub_prices_history` | 2024-09-01 | 2026-10-06, 2026-10-04 (file) | public |
| NYISO | Ancillary prices | `nyiso_as_prices` | 2024-09-01 | 2026-10-05 | public, "with a caution" |
| NYISO | Capacity prices | `iso_all_capacity_prices` (`nyiso_icap_spot`) | 2018-01-01 | 2026-10-01 | inside an **internal** table; NYISO's own rows are marked public per row |
| NYISO | Interconnection queue | `nyiso_interconnection_queue` | snapshot 2026-09-26 | | public; 1,814 positions; refreshed by hand (`known_gaps.csv`) |
| NYISO | Day-ahead energy cleared | `nyiso_dam_cleared_energy` | 2025-09-01 | 2026-10-08 | public |
| NYISO | Curtailment, storage series | none | | | EIA-930 itemizes no battery series for NYISO |
| ISO-NE | Prices, 9 nodes, day-ahead and real-time | `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly` | 2026-08-26 | 2026-10-07, 2026-10-06, 2026-10-05 | public; rolling |
| ISO-NE | Prices, internal hub, history | `iso_hub_prices_history` | 2024-09-01 | 2026-10-05, 2026-10-04 (file) | public |
| ISO-NE | Ancillary prices | `isone_as_prices` | 2025-03-01 | 2026-10-05 | **internal** |
| ISO-NE | Capacity prices | `iso_all_capacity_prices` (`isone_fca`) | 2010-06-01 | 2027-06-01 | **internal** |
| ISO-NE | Interconnection queue | `isone_interconnection_queue` | snapshot 2026-10-05 | | public; 1,751 positions |
| ISO-NE | Day-ahead energy cleared | `isone_dam_cleared_energy` | 2026-09-01 | 2026-10-08 | **internal** |
| ISO-NE | Storage, EIA hourly | `eia930_all_storage` | 2024-11-07 | 2026-10-03 (file) | public |
| ISO-NE | Curtailment | none | | | not held |
| SPP | Prices, 1 hub, history | `iso_hub_prices_history` | 2024-09-01 | 2026-10-05, 2026-10-04 (file) | public |
| SPP | Prices, 2 hubs, rolling | `iso_dam_hub_prices`, `iso_rtm_hub_prices` | 2026-08-26 (real-time: 2026-09-24) | 2026-10-05, 2026-10-04 (file) | public |
| SPP | Ancillary prices and quantities | `spp_as_prices`, `spp_as_quantities` | 2024-09-01 | 2026-10-04, 2026-10-05 | public, with citation |
| SPP | Capacity prices | none | | | no table |
| SPP | Interconnection queue | `spp_interconnection_queue` | snapshot 2026-10-05 | | public; 3,076 positions |
| SPP | Curtailment, daily | `spp_curtailment_daily` | 2014-03-01 | 2026-10-05 | public; SPP's own figure |
| SPP | Storage, EIA hourly | `eia930_all_storage` | 2026-02-05 | 2026-10-03 (file) | public |
| SPP | Day-ahead energy cleared | `spp_dam_cleared_energy` | 2025-09-01 | 2026-10-08 | public |

Derived tables across grids that a reader may want by name: `cost_of_power_monthly` (2018-07 to 2026-10, six grids, no PJM), `merchant_revenue_monthly` (2018-06 to 2026-10), `battery_stack_monthly` (ERCOT and CAISO, 2018-01 to 2026-10), `shoulder_hours_monthly` (ERCOT and CAISO, 2019-01 to 2026-10), `ba_supply_monthly` (2019-01 to 2026-09), `clean_energy_summary` (2019 to 2026-09), `grid_stress_yearly` (2019 to 2026), `interconnection_queue_summary` (1995 to 2025). All dates: `coverage.csv`.

## 5. The validator and the tests

**The validator** is `warehouse/validate/erw_validate.py` (475 lines, read whole on 7 October 2026). `ARCHITECTURE.md` section 1: "exit 0 or the table does not move". Exit codes (its docstring, lines 13 to 14): `0` pass, `1` blocked (at least one error), `2` bad input (a file that cannot be read as a CSV); with several files the worst code wins. `--strict` makes warnings block. It uses pandas and the standard library only: "no network, no credentials".

What it checks, by shape (the check's name in brackets):

*Every file:* the extension is `.csv` [`file_extension`]; the name is 40 characters or fewer [`file_name_length`] and matches the shape's pattern [`file_name_pattern`]; the file is UTF-8 with a header row and parses as CSV (else exit 2); a missing `#` provenance header is a warning [`provenance_header`]; no column name twice [`duplicate_columns`]; at least one data row [`empty`].

*Series:*
1. `entity, variable, ts_utc, value` present [`required_columns`] and first, in that order [`required_order`].
2. `unit` and `source` present and never empty [`unit_present`, `source_present`].
3. `ts_utc` is `YYYY-MM-DDTHH:MM:SSZ` [`ts_utc_format`] and a real time [`ts_utc_parse`].
4. `value` never empty [`value_missing`], numeric and finite [`value_numeric`].
5. No two rows share `(entity, variable, ts_utc)`, plus `event` where the table has that column [`duplicate_key`].
6. A fixed sub-daily `freq` matches the timestamps' grid, and a daily or longer `freq` puts `ts_utc` at `00:00:00Z` [`ts_freq_alignment`].
7. `unit` is in a closed vocabulary of 37 strings (the `UNITS` set, lines 35 to 51) [`unit_vocabulary`].
8. `geo` is an ISO 3166-2 code or a comma-separated list of them [`geo_format`].
9. Warnings only: a column that is neither reserved nor prefixed `x_` [`unknown_columns`]; reserved columns out of order [`reserved_order`]; an entity not written `namespace:id` [`entity_namespace`]; `retrieved_at`, `vintage` or `freq` badly formed.

*Events:* `event_id, event_date, event_type, source, source_url` present [`required_columns`]; standard columns first and in order [`required_order`]; `event_id` never empty and unique [`event_id_missing`, `duplicate_key`]; `event_date` a date or a UTC time, and real [`event_date_format`, `event_date_parse`]; `event_type`, `source`, `source_url` never empty; `source_url` begins `http://` or `https://` [`source_url_format`]; `mw`, `price` and the news scores numeric, the scores from 0 to 10; `currency` three capital letters [`currency_format`].

*Entities:* `entity_id, entity_type, name, source` present; standard columns first and in order; `entity_id`, `entity_type`, `source` never empty; `entity_id` written `namespace:id` and unique; `entity_type` in a vocabulary of 8; `geo` well formed; `lat` and `lon` numeric, in range and given together [`lat_lon_pair`]; every `*_mw` column numeric; `status` in a vocabulary of 8; every `*_date` column a real `YYYY-MM-DD`; `source_url` http(s).

**Passing today:** 171 of 171 tables carry `validator_status` = `pass` in `coverage.csv` (read 7 October 2026). The validator was not run for this document.

**Tests.** Counted on 7 October 2026:

- `tests/`: 103 files named `test_*.py`; 1,475 tests collected by `python -m pytest --collect-only -q -p no:cacheprovider tests` (exit 0, "1475 tests collected in 7.11s"; the tests themselves were not run). Reading the files gives the same 1,475 `def test_` lines, in 432 classes.
- `package/tests/`: 2 files, 39 `def test_` lines (`test_erw.py` 35, `test_backends.py` 4; the second is marked `remote` and "skipped by default since session 34", `package/README.md` line 64).
- `site/scripts/`: 30 `check-*.mjs` and 16 `test-*.mjs` files. The main ones, from each file's opening comment:
  - `check-routes.mjs`: gets every page; fails on a status other than 200, the word "undefined" in visible text, or more "no data" blocks than the same page shows on the live site. Run twice, with and without the internal cookie (`docs/release-gate.md`, "The checks").
  - `check-values.mjs`: every number a page renders through `components/Num.tsx` is checked against its own query to Supabase; fails if a value differs or fewer than ten were checked.
  - `snapshot-live.mjs`: takes a snapshot of the live pages as a visitor and compares two snapshots (`CLAUDE.md` rule 8; 25 addresses).
  - `check-review-pages.mjs`: each page in review answers the in-review page to a visitor and renders with figures in the internal view.
  - `check-no-request.mjs`: a real browser types into `/battery/customer` and the script asserts no network request, no change of address, no cookie or storage write.
  - `check-series.mjs`: every chart Ask ERCOT would draw is set against the rows it fetched, point by point.
  - `test-battery-stack.mjs`, `test-network.mjs`: browser tests of the two live tools' controls.
  - `warm-live.mjs`: asks for every live page once after a build, before the route check.

**What GitHub runs** (`.github/workflows/`, 9 files, read 7 October 2026):

| Workflow | Trigger | Checks it runs |
|---|---|---|
| `code-branch.yml` | a push to `task/**` | `python -m unittest discover -s tests`; the site build and `check-routes`; then opens and merges the pull request |
| `daily-prices.yml` | `0 14 * * *` | a secrets check; `python -m unittest discover -s tests -v` before the run ("Merge tests"); the validator inside `warehouse/run_daily.sh` ("a blocked table stops the run", `README.md`); `upload.py --check-license` (line 406 of `run_daily.sh`); the package tests (`package/tests/test_erw.py`) on the run's tables; a three-run failure streak check; a health summary |
| `latest-prices.yml` | `*/15 * * * *` | a secrets check; a duplicate-start guard |
| `roundup.yml` | `0 23 * * 0` | the data lock; "was this week's Roundup already sent" |
| `hourly-network.yml` | `0 0-13,15-23 * * *` | a duplicate-start guard |
| `weekly-vacuum.yml` | `0 10 * * 0` | records the database sizes in `run_status.csv` |
| `chain-watch.yml` | `*/15 * * * *` | whether a marked session chain has saved anything in 30 minutes |
| `thesis.yml`, `issues.yml` | by hand | none |

`docs/state_2026-10-04.md` line 88 records a gap: "three Node-backed tests skip on GitHub because the workflow runs tests before installing the site".

## 6. Its tools and their status

**The plan.** `docs/platform-tools.md` lists 31 tools with the status of each tool's data layer: `yes` 6, `partial` 19, `no` 2, `planned` 4 (counted from its table on 7 October 2026). Its own definitions: "**yes** = the tables the tool needs exist and refresh daily; **partial** = some exist, the gap is named; **no** = the shape or source is not built; **planned** = a tool of the plan not started". Some of its cells describe earlier sessions (tool 18: "30 days of power data"; tool 3: 45,488 rows of `energy_projects`, where `coverage.csv` holds 39,784); the file itself names `docs/coverage.md` as "the authority on what exists".

| # | Tool | Data layer in `docs/platform-tools.md` |
|---|---|---|
| 1 | Energy Digest | yes |
| 2 | Real-time price board | partial |
| 3 | Energy project map | partial |
| 4 | Datacenter power tracker | partial |
| 5 | Signature data explorers (ERCOT peak premium) | yes |
| 6 | Energy deal tracker | partial |
| 7 | Grid stress and real-time conditions | partial |
| 8 | Regional power-price heatmap | partial |
| 9 | Flagship newsletter | partial |
| 10 | Energy-intelligence company database | partial (seeded) |
| 11 | Capital flows tracker | no |
| 12 | Policy and regulatory monitor | partial |
| 13 | Deep-dive report library | partial |
| 14 | Weekly state-of-energy brief (the Energy Roundup) | yes |
| 15 | Data downloads and methodology | partial |
| 16 | Cost-of-power model | partial |
| 17 | Economic forecasting tool | no |
| 18 | Predictive and scenario layer | partial |
| 19 | Data and API products | partial ("No Redivis version released yet; no public API") |
| 20 | AI chat over the warehouse | partial |
| 21 | Energy mix explorer | yes |
| 22 | Curtailment tracker | partial |
| 23 | Consumption by sector | yes |
| 24 | Trader view | partial |
| 25 | Email digest | partial |
| 26 | Automated Analysis | yes |
| 27 | Thesis Builder | partial |
| 28 | Problem set builder for educators | planned |
| 29 | Run the grid | planned |
| 30 | Case study builder | planned |
| 31 | Energy meme generator | planned |

**What a visitor can open.** `site/lib/release.ts` is "the one list" (`docs/release-gate.md`). Read 7 October 2026: three entries are `live`: `/cost-of-power/battery`, `/network`, `/storage`. 71 entries are `review`, and "a path with no entry is in review". Its comment: "Session 126 (the owner's instruction, 5 October 2026): the home page, About, Terms, the seller's tab and the four methods notes are in review." The gate is "a curtain for visitors, not security" (`docs/release-gate.md`). Two older documents count differently and are superseded by the list: `docs/tools.md` (session 53: "34 public tools") and `docs/state_2026-10-04.md` ("Open to visitors (6 tools)").

**A freeze is in force on the day of writing.** `REVIEW_FREEZE` in the repository root: `start: 2026-10-05`, `end: 2026-10-07` (`CLAUDE.md` rule 9).

**Scheduled jobs.** The cron lines in the table of section 5: the daily run at 14:00 UTC, the latest prices every 15 minutes, the hourly network refresh (every hour but 14:00), the Energy Roundup on Sundays at 23:00 UTC, the vacuum on Sundays at 10:00 UTC, the chain watch every 15 minutes. `README.md`, "How it refreshes", lists the daily run's seven steps. `ARCHITECTURE.md`: "Everything on a clock is a GitHub Action. There is no crontab on any machine."

## 7. Known data faults and what was done

Sources: the table `warehouse/output/known_data_faults.csv` (28 rows, built 2026-10-05T07:57:29Z, read 7 October 2026), its register `warehouse/faults/faults.yaml`, `docs/methods/known_data_faults.md`, the site's copy `site/data/data_faults.json`, `docs/methods/eia930_caiso_break.md`, `docs/methods/impossible_hours.md`. The table and the site's copy agree: 28 faults.

A fault here is "something the publisher's data holds, not something the ERW did" (`docs/methods/known_data_faults.md`). "Nothing is estimated": every figure is one a session measured and wrote down.

| Count | By | Source |
|---|---|---|
| 28 | faults in all | rows of the table |
| 10 / 3 / 1 / 14 | `screened` (left out by a stated rule) / `corrected` (read as it should have been, by a stated rule) / `worked_around` (another source is read for the period) / `held_as_published` | column `status` |
| 11 / 8 / 9 | `fixed` / `held_for_approval` (the fix is built and waits for a person, because applying it moves a number on a live page) / `open` | column `x_resolution` |
| 18 / 5 / 2 / 1 / 1 / 1 | EIA (17 in Form EIA-930, 1 across EIA-930 and EIA-860M) / CAISO / ERCOT / FERC / ISO-NE and NYISO / Berkeley Lab | column `parties` |
| 29 | ERW tables touched | `site/data/data_faults.json`, `tables_touched` |

The method note's own opening count ("24 faults", as built on 4 October) is the first state; the same note records the additions of sessions 106 and 118 that bring it to 28.

Each fault (title and figures as the table's `x_title` and `x_evidence` give them; "found" is `x_recorded_in`):

| Fault | Publisher's report | Dates | What the ERW did | Found in |
|---|---|---|---|---|
| EIA's California generation changed in one hour: gas falls from a daily mean of 251.7 GWh to 118.3 | EIA-930 | from 2025-12-16 | Worked around: from that hour California's generation by fuel is read from CAISO's own supply, never blended. Fixed | session 73 |
| EIA's California hours sit one hour late; best match at a shift of one hour on 182 of 182 days | EIA-930 | 2023-11-01 to 2025-12-02 | Corrected: moved one hour earlier where read, in seven derived tables. Held for approval | sessions 80, 82 |
| No hydro for California in 7,869 hours in a row | EIA-930 | 2019-10-01 to 2020-08-24 | Screened: an hour is not used when a main source is blank. Held for approval | session 94 |
| California's demand holds runs of hours near half its level (for example 12,193 MW between hours of 21,843) | EIA-930 | 2019-02-13 to 2026-01-25 | Screened by the rule for impossible hours. Held for approval | session 97 |
| New York's demand holds twelve hours of exactly zero | EIA-930 | 2019-04-18 to 2026-02-10 | Screened: an hour at or below zero is not used. Held for approval | session 97 |
| PJM's demand holds seven hours that did not happen (155,276 MW between hours of 103,637) | EIA-930 | 2019-12-12 to 2024-11-21 | Screened. Held for approval | session 97 |
| SPP's demand holds two impossible hours (1,505 MW between hours of 34,479) | EIA-930 | 2024-07-19 to 2025-06-21 | Screened. Held for approval | session 97 |
| Net generation holds impossible hours in five grids (California: 29 hours, and twelve more on 2023-11-10 sliding to 727 MW) | EIA-930 | 2018-07-20 to 2026-08-20 | Screened by rule A. Held for approval | session 118 |
| Unadjusted demand and net generation in the millions and billions of MW (PJM: 2,147,480,000 MW at 2021-10-19T03:00Z) | EIA-930 | 2019-12-11 to 2023-06-13 | Screened by rule A. Held for approval | session 118 |
| Daily interchange holds days no tie can carry (SPP to MISO 2,159,056 MWh on 2026-07-21; 2,732 of 945,130 pair-days left out) | EIA-930 daily interchange | 2019-01-01 to 2026-09-30 | Screened: beyond 10 median absolute deviations and 500 MWh of the pair's median. Fixed | sessions 62, 68, 93 |
| Daily interchange is missing for 47 to 53 days of the year in six regions, 156 in SPP | EIA-930 daily interchange | not dated | Held as published: a month says how many days it rests on. Open | sessions 62, 68, 96 |
| Four of California's ties are reported differently by the two sides (largest mean daily gap about 8,400 MWh) | EIA-930 daily interchange | not dated | Held as published: both reports are in the table. Fixed | session 68 |
| EIA's "other" for ERCOT repeats the batteries' output | EIA-930 | 2025-12-06 to 2025-12-14 | Screened: Texas's December 2025 mix is not written. Fixed | session 94 |
| PJM's sources and its total part by 5 to 15 percent in 2,689 hours | EIA-930 | 2020 to 2024 | Held as published; PJM is held to a 15 percent test (91 of 93 months written). Open | sessions 73, 94 |
| EIA's California solar runs about 13 percent below CAISO's own | EIA-930 | standing | Held as published. Open | session 73 |
| 24 hours of demand in the Winter Storm Uri window have no number | EIA-930 | February 2021 | Held as published: not written, nothing filled. Fixed | session 68 |
| The Lower 48's demand is a sum with the faulty hours inside it | EIA-930 | 2020-04-10 to 2020-07-13 | Held as published: the Lower 48 gets an average and no peak. Open | session 97 |
| ERCOT's solar output stands above installed capacity on two days (1.0429 and 1.0318 of nameplate) | EIA-930 against EIA-860M | 2023-08-10, 2026-08-29 | Held as published: flagged, not explained. Open | session 72 |
| CAISO's supply by fuel is empty or short on four days | CAISO Today's Outlook | 2025-11-02 to 2026-09-22 | Held as published: a day that is not whole is not written. Open | sessions 73, 82 |
| CAISO's two curtailment workbooks of 2025 repeat January to May (25,848 rows in both) | CAISO production and curtailments | 2025-01 to 2025-05 | Corrected: the rows are read once. Fixed | session 98 |
| CAISO's curtailment file gives no reason for 9,241 rows of 2022 | CAISO production and curtailments | 2022 | Held as published: a blank reason stays blank. Open | session 98 |
| CAISO's Daily Renewable Report has 24 hours on the day the clocks went forward (64,906 MWh, 8.38 percent of March's curtailment, was first left out) | CAISO Daily Renewable Report | 2026-03-08 | Corrected: dated by clock hour, the day is held. Fixed | session 98 |
| CAISO's OASIS leaves out the last hour of the autumn clock-change day | CAISO OASIS | 2024-11-03, 2025-11-02 | Held as published: the day is not written. Fixed | sessions 49, 64 |
| ERCOT's large-load reports of early 2026 name their months as 2025, and March 2026 is stated twice | ERCOT Large Load Interconnection Status Update | 2026-01-21 to 2026-03-26 | Held as published: dated by the report's own day. Fixed | session 106 |
| ERCOT's report of August 2025 states a simultaneous peak (3,733 MW) above the non-simultaneous one (3,694 MW) | the same | 2025-08-27 | Held as published, with a note. Open | session 106 |
| A storage contract rate of 132000 in $/MW-MO for 1.056 MW | FERC EQR | not dated | Held as filed (internal table). Fixed | session 81 |
| ISO-NE's and NYISO's real-time price files miss intervals (ISO-NE 31 days, NYISO 11 days) | ISO-NE, NYISO | not dated | Held as published: a day with a missing interval is not written. Open | sessions 49, 64, 65, 96 |
| Berkeley Lab's queue file: of 38,201 requests, 665 have no year, 48 are dated as operating before their request | Berkeley Lab, Queued Up 2026 | to 2025-12-31 | Screened by stated minimums. Fixed | session 95 |

The one rule for impossible values (`docs/methods/impossible_hours.md`): an hour of demand or net generation is used when it is held, above zero, within 25 percent of the median of the four hours around it, and within one third to three times the grid's own median; a zero is a missing value; a day of interchange is used when within ten median absolute deviations of its pair's median. "Nothing is filled, smoothed or replaced: the value becomes a blank."

How the two largest were found: the December 2025 break by adding up EIA's daily generation by fuel on each side of the date and setting it beside CAISO's own supply (`SESSION_73_REPORT.md` lines 28 to 41); the late hours by matching EIA's solar against CAISO's 5-minute data day by day at each shift (`SESSION_82_REPORT.md` line 96).

Later reports qualify one count: `SESSION_124_REPORT.md` line 13 finds that of the 2,732 pair-days rule C leaves out, "in **1,911 the two reports agree within 5 percent**", so the rule is too strict for those days; the change to `ba_supply_monthly` is "held for your approval" (same report, line 28).

## 8. Findings

Chosen from the session reports of sessions 60 to 137 in this working tree, the findings brief `docs/briefs/findings_2026-10-04.md` (session 89) and the method notes. Each is computed from held data by a documented method. Numbers are quoted as the report states them; none was recomputed. "Row read today" means the table's row for the brief's check key holds the same value in the file in `warehouse/output` on 7 October 2026 (28 of the brief's 28 `series` keys do; its 7 `bs|` keys are figures the battery page's code computes and were not re-read).

### The ten

1. **EIA's hourly figures for California sat one hour late for 25 months, and the seller tab's California solar was overstated by 10.3 percent for 16 months because of it.** "EIA's hourly values for California sit one hour late from 1 November 2023 to 2 December 2025"; "September 2024 to December 2025: USD 45,617 per MW before, 40,916 after"; best match "at a shift of one hour on **182 of 182 days**". Table: `merchant_revenue_monthly`. Method: `docs/methods/eia930_caiso_break.md`. Report: `SESSION_82_REPORT.md` lines 7 and 96; "25 months" is the brief's wording (`docs/briefs/findings_2026-10-04.md` line 127). Corrects session 80, which had the end date two weeks late (line 90). In the fault register the correction is `held_for_approval` for the tables behind live pages.

2. **Since 16 December 2025 EIA's own figures for California no longer add up.** "Imports measured as demand less generation were 19.1 percent of demand in October 2025 against 18.4 by interchange, a gap under one point; in January 2026 they were 40.6 against 28.5." Table: `ba_supply_monthly`. Method: `docs/methods/eia930_caiso_break.md`. Report: the brief, finding 10; `SESSION_89_REPORT.md` line 104; the break itself at `SESSION_73_REPORT.md` lines 28 to 30 (gas "from a daily mean of 251.7 GWh ... to 118.3"; EIA's balance "80.7 GWh a day short after (about 12 percent of demand)"). Rows read today. Caveat in the brief: "a change in what EIA-930 reports as California's generation, not power that went missing". This corrects session 62's "27.02 percent" import share: `SESSION_68_REPORT.md` line 9, "The 16.6 percent is right on the evidence".

3. **What ERCOT's batteries were awarded day-ahead is 22 percent of what the ERW's own battery model earns.** "Over the seven whole months of 2026 held (January to July), the fleet's day-ahead awards come to USD 6.53 per kW: 3.75 energy net of charging, 2.78 ancillary services." The model, same months: "USD 30.14 per kW". Table: `ercot_storage_dam_awards_monthly` (from `ercot_dam_esr_awards`; the model is `battery_stack_monthly`). Method: `docs/methods/ercot_storage_dam_awards.md`. Report: `SESSION_115_REPORT.md` line 7. Caveat, line 8: "That is not what the batteries earned... A floor on market revenue." One figure of that report was corrected: its "netted USD 44.50 per MWh" is "USD 45.16 on the page" (`SESSION_116_REPORT.md` line 11).

4. **Two thirds of what ERCOT's battery fleet discharges is not sold day-ahead.** "Over the 186 days it discharged 4,623,251 MWh in real time and had sold 1,483,064 MWh day-ahead: 32 percent." Day-ahead awards plus real-time deviations, February to July 2026: "USD 7.17" per kW, "38 percent of the model's figure" (USD 18.81). Table: `ercot_storage_rt_monthly` (from `ercot_sced_esr_hourly`). Method: `docs/methods/ercot_storage_realtime.md`. Report: `SESSION_120_REPORT.md` lines 9 and 10. Caveat, line 3: real-time energy is valued at the hub average's price, not at each battery's node.

5. **Almost all the energy ERCOT's storage offered day-ahead was priced not to clear.** "The curves offered to sell 10.7 MWh per MW per day at any price; 88 percent of it was priced above USD 1,000 per MWh and 92 percent above USD 100. At each hour's own day-ahead price they offered 0.41, and 0.39 was awarded." Tables: `ercot_storage_dam_offers_daily`, `ercot_storage_dam_offers_monthly`. Method: `docs/methods/ercot_storage_dam_offers.md`. Report: `SESSION_116_REPORT.md` line 9 (January to July 2026). Caveat, line 59: "The 10.68 is power offered hour by hour, not energy."

6. **One month is more than half of everything a four-hour battery would have earned in Texas since 2018, and on the last twelve months it did not cover its debt.** "February 2021 is 57 percent of all the revenue in the months held; an average year is USD 614.58 per kW with it and USD 269.68 without"; "USD 81.40 per kW from October 2025 to September 2026... debt coverage 0.88 times". Table: `battery_stack_monthly`. Method: `docs/methods/battery_stack.md`. Report: the brief, findings 7 and 8; `SESSION_67_REPORT.md` line 13; `SESSION_89_REPORT.md` lines 101 and 102. Caveat in the brief: "the upper bound (perfect foresight, reserves paid and never called), and the debt payment is a cost assumption". Not re-read today: the twelve-month figure is the battery page's statistic as of 4 October, and the table has been rebuilt since (`coverage.csv`, `last_run` 2026-10-06).

7. **On the average evening Texas's net-load shoulder asks about twice the hours its batteries hold, and on the ten hardest evenings four times.** "3.17 hours needed on the average evening of 2026; the fleet stores 1.65 hours and covers 1.58"; "6.58 hours needed on average over the ten worst days of 2026, 8.61 at the worst". Table: `shoulder_hours_monthly`. Method: `docs/methods/shoulder_hours.md`. Report: the brief, findings 4 and 5; `SESSION_82_REPORT.md` line 85; `SESSION_89_REPORT.md` lines 98 and 99. Rows read today. Caveat in the brief: a narrower measure of the same evenings asks 1.01 hours; the ten are of January to September 2026 only. Session 82 revises session 80's answer for Texas (line 207).

8. **The US battery fleet grew by 48 percent in twelve months, and California builds four-hour batteries while Texas builds batteries of under two hours.** "54,489 MW operating in August 2026, 17,689 MW more than the 36,800 MW of August 2025"; "California's fleet averages 3.46 hours and Texas's 1.65"; six hours or more: "129 MW of 54,489 MW". Table: `storage_buildout_monthly` (from EIA-860M). Method: `docs/methods/storage_buildout.md`. Report: the brief, findings 1 to 3; `SESSION_89_REPORT.md` lines 95 to 97; `SESSION_69_REPORT.md` line 98. Rows read today. Caveat in the brief: the history is rebuilt from EIA's one newest inventory.

9. **A weather-and-calendar model finds no demand reduction on California's Flex Alert days that it can tell apart from its own error.** "Across 38 alert days and 204 alert hours, the estimated cut is **-503.2 MW**, with a 90 percent interval of **-1,274.9 to 247.4 MW**... The interval includes zero." Tables: `flex_alert_effects`, `flex_alert_model`. Method: `docs/methods/flex_alert_scorecard.md`. Report: `SESSION_60_REPORT.md` line 55, and line 96 for the sentence in bold ("finds **no demand reduction on alert days that it can tell apart from its own error**"). Caveat, same report, line 97: "The sign of the pooled estimate depends on the specification." No later correction found in sessions 60 to 131.

10. **In Texas the 100 tightest hours of the year moved off the sun.** "Solar's output in the 100 tightest hours as a share of its installed capacity: 71.1 percent in 2019, 48.7 in 2023, 33.1 in 2024, 5.0 in 2025." Table: `grid_stress_yearly`. Method: `docs/methods/grid_stress.md`. Report: `SESSION_123_REPORT.md` line 10. Caveat, line 11: "The page says this is what the fleet did, not what it could do."

### Ten more candidates

11. A 100 percent annual clean purchase covered, hour by hour in 2025, "PJM 95.2 percent ... California 78.5"; delivered as solar "41 to 51 percent" (`clean_energy_summary`; `SESSION_122_REPORT.md` line 11).
12. ERCOT's average demand rose from 43,798 MW in 2019 to 55,717 in 2025, "+27.22" percent; NYISO's fell "-2.73" (`eia930_demand_growth`; `SESSION_97_REPORT.md` lines 56 and 62; weather not removed; "0 values differ" after the shared rule, `SESSION_103_REPORT.md` line 65).
13. "Of 22,344 requests that entered from 2000 to 2020, 18.78 percent reached operation and 70.89 percent were withdrawn"; the median wait "rose from 3.15 years in 2015 to 5.44 in 2025" (`interconnection_queue_summary`; `SESSION_95_REPORT.md` line 56).
14. "Nine months of 2026 hold more curtailment than all of 2025, and four fifths of it is for local congestion" in California: 4,790,395 MWh of solar to September 2026 (`caiso_curtailment_profile`; `SESSION_98_REPORT.md` lines 80 and 82).
15. "By ERCOT's report of 26 March 2026, 9,042 MW of large load had its approval to energize and ERCOT had observed 4,004 MW of it running, 44 percent" (`ercot_large_load_status`; `SESSION_106_REPORT.md` line 8; the series stops in March 2026).
16. EIA's workbook gives PJM's demand as "2,147,480,000 MW" in an hour of 19 October 2021, which made `carbon_intensity_monthly` say "4.47 kg CO2 per MWh" for that month "between months of 316 to 411" (`SESSION_118_REPORT.md` lines 7 and 8; the fix is held for approval).
17. Of the 2,732 pair-days of interchange the screening rule leaves out, "in **1,911 the two reports agree within 5 percent**" (`eia930_daily_interchange`; `SESSION_124_REPORT.md` line 13).
18. Day-ahead averages over twelve months to September 2026: CAISO SP15 28.92 USD per MWh with 12.82 percent of hours below zero; ISO-NE's internal hub 74.19 (`hub_price_comparison`; `SESSION_96_REPORT.md` lines 57 and 67; eleven hubs only, no PJM, MISO held and not shown).
19. "On 15 February 2021, Texas imported 1.77 percent of its demand" (`eia930_daily_demand`, `eia930_daily_interchange`; `SESSION_109_REPORT.md` line 8).
20. Texas's largest one-hour evening rise of net load, as a share of the year's peak demand: "7.9 percent in 2019, 19.1 in 2025" (`grid_stress_yearly`; `SESSION_123_REPORT.md` line 9).

Held back by the brief itself (`docs/briefs/findings_2026-10-04.md`, "Held back, and why"): the battery model in New York and SPP ("every duration rule is assumed"), and who owns the batteries ("a reporting company is often a project company"). Not used here because its report is on another branch and its table is not in coverage: session 129's demand growth with weather removed.

## 9. Scale and cost of operation

**Model spend recorded.** `warehouse/output/api_cost_ledger.csv` on this machine, read 7 October 2026: 2,730 rows, one per Messages API call made by ERW code, from 2026-09-29T10:08:33Z to 2026-10-06T19:54:24Z. Sum of column `usd`: **USD 40.66**, no row without a cost. By model: `claude-sonnet-5-5` USD 36.57 (2,587 calls), `claude-haiku-4-5-20251001` USD 4.09 (143 calls). By day the sum runs from USD 0.64 (1 October) to USD 10.38 (6 October). Rows written by the daily run on GitHub (`session` = `daily`): USD 8.81 over the eight days. Largest steps: `thesis` USD 10.40, `news_score` 5.34, `chat_ercot_eval_after` 4.20. Tokens summed: 4,524,030 input, 40,228,711 cached input, 2,869,416 cache write, 1,786,783 output; 261 web searches.

What the ledger does not hold, per `docs/methods/api_cost_ledger.md` and the file's header:

- calls before session 30 (the ledger begins 29 September 2026);
- the site's `/ask` calls, which "go to the Supabase table `site_api_calls` instead" (not read for this document);
- the Claude Code sessions that built the repository; no file in the repository totals their cost.

`coverage.csv` gives the ledger 2,222 rows as of the daily run of 6 October; the file here has grown since.

**Evaluation costs** (`docs/OVERVIEW.md`, "Evaluation to date"): five chat evaluation runs, USD 0.55 to 1.30 each, scoring 27 of 30 to 45 of 45.

**The daily run.** Scheduled at 14:00 UTC with a job limit of 180 minutes (`.github/workflows/daily-prices.yml`). From `warehouse/metadata/run_status.csv`, the time of the first and last status row written by GitHub between 14:00 and 19:00 UTC on each of the last three days, leaving out the 15-minute, hourly, vacuum and Roundup jobs: 4 October 14:06 to 14:58, 5 October 14:07 to 15:42, 6 October 14:06 to 15:16 (52, 95 and 70 minutes; the upload and the commit follow the last row, so these are lower bounds). The same file: 3,321 rows over 611 run ids from 25 September to 6 October 2026: 2,180 `ok`, 988 `gap`, 95 `failed`, 58 `skipped`.

**Storage.**

- On this machine (`du -sh`, 7 October 2026): `warehouse/output` 7.7 GB, `warehouse/archive` 6.3 GB, `warehouse/raw` 16 GB.
- Supabase: "pg_database_size 514.3 MB -> 437.4 MB" at the vacuum of 2026-10-04T15:27:00Z (`run_status.csv`, connector `supabase_vacuum`); `live_set.yaml` allows 7,500 MB.
- Redivis: the largest table, the ERCOT history, "is 0.65 GB" as a CSV (`warehouse/redivis/README.md`). The size of the datasets on Redivis is not recorded in the repository.

**Size of the work.** 210 files in `archive/sessions/` (prompts and reports); 103 test files; 53 method notes in `docs/methods/`; 9 workflows.

## 10. What is not done

**Sources missing or stopped.**

- **PJM energy and ancillary prices: not held.** PJM's data license bars non-members from republishing (`docs/price-sources.md` line 184); "A PJM connector is throttled to at most 5 requests per minute (not built yet: no PJM key)" (`docs/datastandard.md`, Decision 13). PJM's capacity prices are held, internal. `docs/state_2026-10-04.md` line 88 lists "PJM's price license" among the next things.
- **MISO: paused since 4 October 2026**, pending a person's review of its terms (section 3). Its tables stop at the last pull.
- **Known gaps** (`warehouse/metadata/known_gaps.csv`): ERCOT publishes no request-level large-load list; CARB's auction summary and NYISO's queue workbook answer GitHub's runners with HTTP 202 and are refreshed by hand.
- **Greyed on the price board for want of a licensed source** (`SESSION_132_REPORT.md` line 28; `docs/methods/supply_and_trade.md` line 143; `docs/methods/price_board.md` line 225): futures after 5 April 2024 (CME), ICE Brent positioning, coal spot prices.
- **Not found or not open** (`docs/methods/generation_mix_hourly.md` line 212): NYISO, ISO-NE and SPP wind and solar forecasts.

**Tables held internal:** 26 of 171 (section 2), 1,090,543 rows.

**Tools not built** (`docs/platform-tools.md`): `no`: 11 Capital flows tracker, 17 Economic forecasting tool. `planned`: 28 to 31. `partial`: 19 others. Open to visitors: 3 pages.

**The Redivis release:** none (section 2 and the checklist).

**Documents behind the data:** `README.md`, `STATUS.md`, `docs/OVERVIEW.md` and `CHANGELOG.md` (newest entry: session 31, 29 September 2026) state earlier sizes of the warehouse (section 2).

**Faults not settled:** 9 `open` and 8 `held_for_approval` of 28 (section 7).

**Rulings waiting on the owner.** Only the three newest reports have a section titled "For Samuel"; for the seven before them the nearest section is named. The ten newest reports in this working tree are 137, 136, 135, 134, 133, 132, 128, 127, 124 and 123 (125, 126, 129, 130 and 131 are on other branches).

| Session | Section | What waits, in one line |
|---|---|---|
| 137 | "For Samuel" (line 146) | Set `ASK_VISITOR_SALT`; say whether 17 seconds for a number is acceptable; rule on the Python reference loop; rule on loading `eia930_daily_demand` |
| 136 | "For Samuel" (line 105) | Rule on ISO-NE's row; read SPP's commercial-publication exception; after 10 October's daily run look for the step `supply` |
| 135 | "For Samuel" (line 249) | Set `ASK_VISITOR_SALT` in Vercel; run the PitchBook stage once from claude.ai; rule on the internal method note staying in the repository; look at the board's first scheduled refresh |
| 134 | "Verdict" (line 30) | Schedule the refresh; day-ahead energy cleared was not pulled; whether MISO and PJM rows from EIA's file should show values |
| 133 | "Verdict" (line 36) | Confirm the NRC's terms or take the note off; ERCOT's forecast view rests on 146 hours; SPP's wind forecast not settled |
| 132 | "Verdict" (line 22) | Read the IMF's terms before the board opens; decide where the workbench's 16 MB of files live; the futures stay internal and unshown |
| 128 | "Verdict" (line 26) | A secret, three numbers and a deploy; a spending limit in the model provider's console; the words on `/terms` |
| 127 | "Verdict" (line 21) | The license of EIA's futures; whether the board reads the live set daily or stays a copy |
| 124 | "Held for your approval" (line 28) | The confirmed-days rule in `ba_supply_monthly`; MISO's price in the replay's files |
| 123 | "What is left" (line 84) | A pull of EIA's annual retired-generator list, for approval; whether rule A's 25 percent should tighten (it would move numbers on live pages) |

Older rulings still listed as open: ownership of the Redivis dataset by an organization, and the rights question on `energy_companies` (`SESSION_29_REPORT.md` line 260); the first monthly release (`SESSION_28_REPORT.md` line 262).

## 11. Since this pack was counted: sessions 138 and 139 (7 October 2026)

The sections above were counted at commit `64d7b83`, before the two sessions of 7 October. What they changed, from
`warehouse/metadata/coverage.csv` and `warehouse/metadata/sources.csv` as committed after them, and from
`archive/sessions/SESSION_138_REPORT.md`:

- **Tables: 177** (was 171), **24,434,036 rows** (was 22,367,753), all 177 with validator `pass`. License: 148 public
  (23,212,052 rows), 29 internal (1,221,984 rows). Tier: 109 source, 54 derived, 14 model_extracted. Sources in the
  registry: 260 (was 250).
- **Six new tables.** Public: `ercot_zone_load_hourly` (920,358 rows, ERCOT's hourly load by weather zone and its
  system total, from 2015), `nyiso_zone_load_hourly` (748,660 rows, eleven zones, from 2019), `caiso_area_load_hourly`
  (265,824 rows, five areas and the system, from September 2021). Internal: `isone_zone_load_hourly` (131,319 rows),
  `texas_delivery_charges` (73 rows, each with the tariff line it was read from), `large_load_statements` (49 rows,
  each with its sentence).
- **Pulls against the ceiling of session 138:** 2,083,495 rows read of 4,000,000 allowed.
- **A new page, locked:** `/cost-of-power`, "What a datacenter pays" (method `docs/methods/datacenter_cost.md`). Its
  first deploy changed nothing on the live pages (0 differences on 25 addresses).
- **Coverage by grid, added to section 4:** hourly demand from the operator itself for ERCOT, NYISO and CAISO
  (public) and ISO-NE (internal); none for SPP, MISO or PJM.
- **Findings of session 138** (`SESSION_138_REPORT.md`, "The five numbers"; each is computed from held tables by
  `docs/methods/datacenter_cost.md`, and each flexible figure is an upper bound chosen with hindsight):
  1. A flat load at ERCOT's hub average paid USD 32.20 per MWh in real time from October 2025 to September 2026; the
     same year day-ahead in New York City cost USD 73.10 and at New England's hub USD 74.19.
  2. Off in the year's 100 dearest hours, such a load paid USD 28.97 against 32.20 over those twelve months; in 2021,
     USD 47.93 against 148.19.
  3. In 2023 ERCOT had 157 hours within 5 percent of its peak, at a mean real-time price of USD 525 per MWh, and a
     load off in the year's 100 dearest hours was off in 46 of them; in 2025, 140 such hours at USD 42.82, and the
     load was off in 3.
  4. Oncor's transmission cost recovery factor for a transmission-voltage customer is USD 6.260839 per 4CP kW a month
     from 4 October 2026 (USD 8.58 per MWh for a flat load); the same sheet prints 3.491759 from 1 August 2026.
  5. Far West Texas's average demand: 2,070 MW in 2015, 7,478 MW in 2025.
- **A fault found and handled:** the model read Oncor's energy efficiency factor from the non-profit column of a
  many-column table; the figure is held and not shown, and such figures are shown only where the column was checked
  against the header (`docs/methods/datacenter_cost.md`).
- **Not done, added to section 10:** the Public Utility Commission of Texas's transmission charge matrix was not
  obtained; ERCOT's load zone prices are not held; a full `build_coverage.py` fails on the data machine because
  `census_metro_population` names a source that is only on another branch.
- **Tests:** sessions 138 and 139 added 68 tests (`tests/test_session138.py` 24, `test_session138_demand.py` 29,
  `test_session138_delivery.py` 9, `test_session139.py` 6) to the 1,475 collected above.

## How the counts were made

Short scripts, run on 7 October 2026 and kept outside the repository, read `coverage.csv`, `sources.csv`, `redivis_uploads.csv`, `run_status.csv`, `live_set.yaml`, the header lines of each file in `warehouse/output`, and, for the per-grid dates and the brief's check keys, the `entity`, `variable`, `ts_utc`, `value`, `ba` and `market` columns of the tables named. Line numbers of session reports were checked with a search for the quoted words. The three ranges of session reports (60 to 85, 86 to 111, 112 to 131) were read by helpers whose quotations were then checked against the files for every line cited above.
