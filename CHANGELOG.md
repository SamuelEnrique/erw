# Changelog

Energy Research Warehouse (ERW). Changes a user of the tables, the `erw` package or the site needs to know about, newest first. What a session did and why is in its report, `archive/sessions/SESSION_*_REPORT.md`.

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
