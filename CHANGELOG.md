# Changelog

Energy Research Warehouse (ERW). Changes a user of the tables, the `erw` package or the site needs to know about, newest first. What a session did and why is in its report, `archive/sessions/SESSION_*_REPORT.md`.

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
