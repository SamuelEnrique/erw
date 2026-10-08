# Changelog

Energy Research Warehouse (ERW). Changes a user of the tables, the `erw` package or the site needs to know about, newest first. What a session did and why is in its report, `archive/sessions/SESSION_*_REPORT.md`.

## 2026-10-08, session 151: eighty entities' large-load statements, and the wait figures

- `large_load_statements` (internal) holds 796 statements: 761 from 70 of 80 utilities and operators and 35 from 13 regulators, federal bodies and other parties that state a figure. 200 of them state a duration: 171 distinct wait figures, 12 of them measured.
- Seven new columns (`docs/datastandard.md`, Decision 45): `entity_list`, `source_flag`, `wait_basis`, `load_scope`, `wait_counted`, `wait_figure`, `wait_figure_holder`. The 434 rows held before keep their ids.
- One page: `docs/accelerator/large_load_eighty.md`.

## 2026-10-07, sessions 140, 141 and 144: load zone and zone price histories, New York's load queue, forty entities' large-load statements

**Five new public tables and two internal ones** (`docs/datastandard.md`, Decision 43):

| Table | Tier, license | What |
|---|---|---|
| `ercot_zone_prices_history` | source, public | ERCOT's eight load zones: day-ahead from 2015; real time (15-minute) from 2015 for Houston, North, South and West |
| `iso_zone_prices_history` | source, public | NYISO's eleven zones by the hour from 2019 (day-ahead, and NYISO's own hourly real-time price); CAISO's ZP26 (day-ahead from June 2023, real time from September 2024); SPP South day-ahead, the days pulled so far |
| `isone_zone_prices_history` | source, internal | ISO-NE's eight load zones by the hour, day-ahead and real time, 2019 to August 2026 |
| `nyiso_load_queue` | source, public | NYISO's load interconnection requests, one row a request (74), with zone, megawatts, dates and status in NYISO's words |
| `texas_transmission_matrix` | model extracted, internal | The Texas commission's transmission charge matrices for 2025 (approved) and 2026 (filed, not approved): each provider's cost of service, rate and four-peak demand, each figure with its line |
| `ercot_wind_solar_hsl_hourly` | source, public | ERCOT's hourly wind and solar output and, system-wide, the high sustained limit, from 28 September 2026 (ERCOT lists about a week) |
| `ercot_wind_solar_output_hourly` | source, public | ERCOT's system-wide hourly wind and solar output, 2023 to 2025 (no limit) |

**Changed:**

- `large_load_statements` (internal) holds 434 statements from 38 of 40 utilities and operators, with six new columns (the PDF page, the kind of row, the stage class beside the document's own words).
- `iso_curtailment_monthly` gains the share of available output for CAISO (every month) and SPP (from September 2018).
- `texas_delivery_charges`: nothing changed in the table; the site's file now shows all four utilities' charges for a transmission-voltage load.
- The site's `/cost-of-power` judges a flexible load on a rule decided from day-ahead prices, with the same load "if perfectly foreseen" beside it; a Texas load prices at its load zone. Method: `docs/methods/datacenter_cost.md`.

## 2026-10-07, sessions 138 and 139: hourly load by zone, Texas delivery charges, large-load statements

**Three new public tables and three internal ones** (`docs/datastandard.md`, Decision 42):

| Table | Tier, license | What |
|---|---|---|
| `ercot_zone_load_hourly` | source, public | ERCOT's hourly native load by weather zone (eight) and its system total, from 2015 |
| `nyiso_zone_load_hourly` | source, public | NYISO's hourly integrated load, eleven zones, from 2019 |
| `caiso_area_load_hourly` | source, public | CAISO's hourly actual load, five transmission access charge areas and the system, from September 2021 |
| `isone_zone_load_hourly` | source, internal | ISO-NE's hourly demand, eight zones and the system, from 2025 |
| `texas_delivery_charges` | model extracted, internal | The four large Texas wires utilities' delivery charges for a transmission-voltage customer, each with the tariff line it was read from |
| `large_load_statements` | source, internal | 49 public statements of large load waiting for power from ten utilities and operators, each with its exact sentence: a pilot |

**Also:**

- The site's `/cost-of-power` is "What a datacenter pays" (in review); what it showed before is its view `?view=grids`. Method: `docs/methods/datacenter_cost.md`.
- The intervening sessions (32 to 137) are in their reports; this file was not kept between them.

## 2026-09-29, session 31: battery storage

**Three new public tables,** behind the site's new `/storage` (method `docs/methods/storage.md`):

| Table | Tier | What |
|---|---|---|
| `eia930_all_storage` | source | EIA-930 hourly battery net generation (fuel type BAT), MW, positive discharging; `ba` = erco, isne, miso, swpp, us48, from each series' start (November 2024 for three of them) |
| `storage_daily_cycle` | derived | Per BA and complete local day: MWh discharged and charged, the hours of peak discharge and charge, energy out over energy in |
| `storage_capacity` | derived | Every battery unit in the ERW's EIA-860M tables: operating, under construction, planned, retired |

**Also:**

- The unit `hour` (an hour of the day) joins the vocabulary (`docs/datastandard.md`, Decision 29).
- **Not in the warehouse: EIA-930 CO2 emissions.** EIA publishes no hourly emissions series in its API v2 or its EIA-930 bulk files, so none was pulled.

## 2026-09-29, session 30: price board v2 and the cost layer

**Four new derived tables, public,** behind the site's new `/board` (method `docs/methods/price_board.md`):

| Table | What |
|---|---|
| `price_board_latest` | Every hub and zone of the six ISOs, day-ahead and real-time: daily means of the last 30 complete days, the latest day, its change, 7- and 30-day averages, 30-day low and high, the newest interval, day-ahead minus real-time |
| `price_board_peak_offpeak` | Each ISO's main hub: peak and off-peak means per day (each ISO's peak definition), and ERCOT per year since 2015 |
| `price_board_spreads` | Henry Hub, spark spreads at an assumed 7.0 MMBtu/MWh, implied heat rates, Brent minus WTI, daily for a year |
| `price_board_carbon` | The latest CARB and RGGI auction results; **internal**, like its inputs |

Variables carry the market (`da_`, `rt_`), since a hub is one entity in both markets.

**Two new internal tables,** never public:

- `api_cost_ledger`: every Anthropic API call the ERW makes, with its tokens and cost (`docs/methods/api_cost_ledger.md`).
- `news_scores_shadow`: a second model's scores of the same news stories, for comparison.

A new sector, `platform`, holds the ERW's operating tables.

Also:

- **SPP real time exists.** `iso_rtm_hub_prices`, market `spp_rtm`, has held it since 2026-09-24; `package/llms.txt` said it did not.
- **The digest, Roundup and analysis templates read the consolidated tables by their new names.** The old names still work through the map until the first monthly release.

## 2026-09-29, session 29: fewer, longer tables

**54 tables became 6. The ERW has 65 tables, not 113, and the same 4,812,358 rows.** From Ben Domingue's review (`docs/feedback/ben-2026-09-28.md`, item 5). The rule, now in `docs/datastandard.md` (decision 28): partition keys are columns, never name suffixes.

| New table | Replaces | Partition column |
|---|---|---|
| `ercot_all_hub_prices_history` | `ercot_{dam,rtm}_hub_prices_<2015..2026>` (24) | `market`, `year` (new) |
| `eia930_all_demand` | `eia930_<ba>_demand` (8) | `ba` (new) |
| `eia930_all_generation` | `eia930_<ba>_generation` (8) | `ba` (new) |
| `iso_trader_daily` | `<iso>_trader_daily` (6) | `market` |
| `iso_dam_hub_prices` | `{caiso,ercot,miso,spp}_dam_hub_prices` (4) | `market` |
| `iso_rtm_hub_prices` | `{caiso,ercot,miso,spp}_rtm_hub_prices` (4) | `market` |

The full map is `warehouse/metadata/table_migrations.csv` and `docs/migrations/2026-09-29-consolidation.md`. The six ISO interconnection queues stay separate tables; the migration page says why.

What changes for you:

- **`erw` package.**
  - Filter a consolidated table by partition: `erw.fetch("eia930_all_demand", ba="ciso")`, `erw.fetch("iso_trader_daily", market="ercot")`, `erw.fetch("ercot_all_hub_prices_history", market="ercot_rtm", year=2024)`.
  - Old names still work until the first monthly release, with a `DeprecationWarning`: `erw.fetch("eia930_ciso_demand")` returns the same rows, columns and header as before.
  - `erw.migrations()` is the map.
- **Redivis.** The six tables are in the draft. The old tables stay until a human runs `python warehouse/redivis/upload.py --remove-migrated` (`docs/runbook.md`). Nothing is released.
- **Supabase and the site.** The live set holds the consolidated tables. The site's pages read them by entity or market.
- **Archive.** Nothing was rewritten or renamed. `warehouse/archive/restore.py` rebuilds a consolidated table from its members' archived lines through the map.

Also in session 29:

- CARB and the NYISO queue are known gaps, refreshed from a local machine (`docs/runbook.md`).
- The Supabase loader vacuums after every load.
- The daily workflow rebuilds `sources.csv` from both copies after its pull.
- The `erw` package tests run in the daily workflow.
