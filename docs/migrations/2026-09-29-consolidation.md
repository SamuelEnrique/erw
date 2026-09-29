# Migration 2026-09-29: consolidating table families (session 29)

Energy Research Warehouse (ERW). Ben Domingue's review (`docs/feedback/ben-2026-09-28.md`, item 5) noted that one table per ERCOT year, per EIA-930 balancing authority and per ISO had brought the ERW to 112 tables in four days. Redivis caps a dataset at 1,000 tables, and the IRW now spreads across several datasets because it hit that cap. The standard already has the columns to tell such tables apart, so fewer, longer tables cost nothing. This page is the plan, written before any table moved, and the record of what moved.

**The map itself is [`warehouse/metadata/table_migrations.csv`](../../warehouse/metadata/table_migrations.csv)**: one line per old table, with its new table and partition. The consolidation code, the archive restore and the `erw` package all read it; this page lists it in full for a reader.

## The rule (session 29 prompt, Part B)

- A family is consolidated only when its members share the same columns and differ only by a value encoded in the table name (region, BA, ISO, market, year, hub).
- That value becomes a column. If a column already holds exactly that value in every row, the suffix is simply dropped.
- Tables with different licenses or tiers are never merged.
- Entities, events, digest and news tables are touched only if they meet the rule exactly.
- Required: the ERCOT history (24 tables into one), EIA-930 (one table per family, with a `ba` column) and the trader view (one table). The same rule applies to any other family of three or more.
- New in `docs/datastandard.md`: **partition keys are columns, never name suffixes.**

## Inventory: 113 tables before

From `warehouse/metadata/coverage.csv` at the start of the session:

- 90 series tables, all with the same 13 standard columns;
- 16 entities tables and 7 events tables, each with its own columns except the six ISO queues.

Every family of three or more that differs only by a name value:

| Family (pattern) | Members | Same columns | License, tier | Decision |
|---|---|---|---|---|
| `ercot_{dam,rtm}_hub_prices_<year>` | 24 | yes | public, source | **consolidated**: `ercot_all_hub_prices_history` |
| `eia930_<ba>_demand` | 8 | yes | public, source | **consolidated**: `eia930_all_demand` |
| `eia930_<ba>_generation` | 8 | yes | public, source | **consolidated**: `eia930_all_generation` |
| `<iso>_trader_daily` | 6 | yes | public, derived | **consolidated**: `iso_trader_daily` |
| `<iso>_dam_hub_prices` | 4 | yes | public, source | **consolidated**: `iso_dam_hub_prices` |
| `<iso>_rtm_hub_prices` | 4 | yes | public, source | **consolidated**: `iso_rtm_hub_prices` |
| `<iso>_interconnection_queue` | 6 | yes (entities) | public, source | **not consolidated**, see below |
| `eia860m_<status>_generators` | 3 | no: each status has its own date columns | public, source | not eligible |

Families of two are left as they are, as the rule asks:

- `isone` and `nyiso` zone prices, day-ahead and real-time: 2 each. `isone_rtm_zone_prices_hourly` is a different product (hourly final prices).
- `caiso` and `spp` curtailment.
- The two peak-premium tables: different frequencies, one method.
- The two weather tables: different products.

Every other table stands alone, including the events and news tables, the `*_evidence` tables and `eia930_generation_latest`, a snapshot.

### Left unconsolidated, and why

- **The six ISO interconnection queues** meet the rule exactly, but consolidating them would lose data:
  - Each is a weekly snapshot that replaces its own rows, and each ISO's pull succeeds or fails on its own.
  - `nyiso_interconnection_queue` can only be refreshed from a local machine (HTTP 202 on GitHub, a known gap since this session).
  - As one table, a Monday pull on GitHub that got five queues would write a table without NYISO and upload it over the full one.
  - The uploader's shrink gate covers rolling-window tables only, so nothing would stop it.
  - They stay six tables until the queue connector can carry a failed member's rows forward.
  - Reversible: adding them to the map is the whole change.
- **DAM and RTM hub prices are two families, not one.** `docs/datastandard.md` keeps day-ahead and real-time in different tables ("different products"). The ERCOT history is the exception, by the prompt's explicit ruling (24 tables into one), and its `market` column (`ercot_dam`, `ercot_rtm`) keeps them apart.
- No family mixed licenses or tiers, so none was refused on that ground.

## The families

| New table | Members | Rows (sum of members) | Partition columns | Column added | License | Tier |
|---|---|---|---|---|---|---|
| `iso_trader_daily` | 6 | 9,961 | `market` | none (`market` already holds it) | public | derived |
| `eia930_all_demand` | 8 | 12,720 | `ba` | `ba` | public | source |
| `eia930_all_generation` | 8 | 65,112 | `ba` | `ba` | public | source |
| `iso_dam_hub_prices` | 4 | 15,960 | `market` | none (`market` already holds it) | public | source |
| `iso_rtm_hub_prices` | 4 | 35,424 | `market` | none (`market` already holds it) | public | source |
| `ercot_all_hub_prices_history` | 24 | 3,063,570 | `market`, `year` | `year` | public | source |

Row counts are from `coverage.csv` at the start of the session; the rolling families grow with each daily run. Session 29's report has the counts at the build.

**54 tables become 6. The ERW goes from 113 tables to 65.** That is 58% of the start, a little more than half. The prompt's target was "roughly half or fewer, do not force it", and the queues are why it is not lower.

Names:

- `docs/datastandard.md`: `source_market_product`, with `all` where there is no single market.
- `iso_` is the ERW's name for a table spanning ISOs, as in `iso_curtailment_monthly` and `iso_rt_top_intervals`.

Partition columns:

- `market` already held the ISO (the trader view: `ercot`) or the ISO and market (the price tables: `ercot_dam`) on every row, so those suffixes were simply dropped.
- `ba` is new: EIA-930 has no column naming the balancing authority except inside `entity` (`eia930:CISO`). It holds the name's code (`ciso`), as the site and the connector use it.
- `year` is new: the ERCOT history is split by **operating year in Central time**. The first hours of 1 January UTC belong to the year before, so the year cannot be read off `ts_utc`.
- `ba` and `year` join the standard as reserved partition columns, after the provenance columns.

## The map

| Old table | New table | Partition | Rows at the start |
|---|---|---|---|
| `caiso_trader_daily` | `iso_trader_daily` | `market=caiso` | 789 |
| `ercot_trader_daily` | `iso_trader_daily` | `market=ercot` | 1,578 |
| `isone_trader_daily` | `iso_trader_daily` | `market=isone` | 2,367 |
| `miso_trader_daily` | `iso_trader_daily` | `market=miso` | 2,072 |
| `nyiso_trader_daily` | `iso_trader_daily` | `market=nyiso` | 2,893 |
| `spp_trader_daily` | `iso_trader_daily` | `market=spp` | 262 |
| `eia930_ciso_demand` | `eia930_all_demand` | `ba=ciso` | 1,632 |
| `eia930_erco_demand` | `eia930_all_demand` | `ba=erco` | 1,488 |
| `eia930_isne_demand` | `eia930_all_demand` | `ba=isne` | 1,632 |
| `eia930_miso_demand` | `eia930_all_demand` | `ba=miso` | 1,632 |
| `eia930_nyis_demand` | `eia930_all_demand` | `ba=nyis` | 1,488 |
| `eia930_pjm_demand` | `eia930_all_demand` | `ba=pjm` | 1,632 |
| `eia930_swpp_demand` | `eia930_all_demand` | `ba=swpp` | 1,584 |
| `eia930_us48_demand` | `eia930_all_demand` | `ba=us48` | 1,632 |
| `eia930_ciso_generation` | `eia930_all_generation` | `ba=ciso` | 7,920 |
| `eia930_erco_generation` | `eia930_all_generation` | `ba=erco` | 7,128 |
| `eia930_isne_generation` | `eia930_all_generation` | `ba=isne` | 8,040 |
| `eia930_miso_generation` | `eia930_all_generation` | `ba=miso` | 7,128 |
| `eia930_nyis_generation` | `eia930_all_generation` | `ba=nyis` | 7,128 |
| `eia930_pjm_generation` | `eia930_all_generation` | `ba=pjm` | 7,128 |
| `eia930_swpp_generation` | `eia930_all_generation` | `ba=swpp` | 7,920 |
| `eia930_us48_generation` | `eia930_all_generation` | `ba=us48` | 12,720 |
| `caiso_dam_hub_prices` | `iso_dam_hub_prices` | `market=caiso_dam` | 2,520 |
| `ercot_dam_hub_prices` | `iso_dam_hub_prices` | `market=ercot_dam` | 5,040 |
| `miso_dam_hub_prices` | `iso_dam_hub_prices` | `market=miso_dam` | 6,720 |
| `spp_dam_hub_prices` | `iso_dam_hub_prices` | `market=spp_dam` | 1,680 |
| `caiso_rtm_hub_prices` | `iso_rtm_hub_prices` | `market=caiso_rtm` | 9,504 |
| `ercot_rtm_hub_prices` | `iso_rtm_hub_prices` | `market=ercot_rtm` | 19,008 |
| `miso_rtm_hub_prices` | `iso_rtm_hub_prices` | `market=miso_rtm` | 6,144 |
| `spp_rtm_hub_prices` | `iso_rtm_hub_prices` | `market=spp_rtm` | 768 |
| `ercot_dam_hub_prices_2015` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2015` | 52,560 |
| `ercot_dam_hub_prices_2016` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2016` | 52,704 |
| `ercot_dam_hub_prices_2017` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2017` | 52,560 |
| `ercot_dam_hub_prices_2018` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2018` | 52,560 |
| `ercot_dam_hub_prices_2019` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2019` | 52,560 |
| `ercot_dam_hub_prices_2020` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2020` | 52,704 |
| `ercot_dam_hub_prices_2021` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2021` | 52,560 |
| `ercot_dam_hub_prices_2022` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2022` | 52,560 |
| `ercot_dam_hub_prices_2023` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2023` | 52,560 |
| `ercot_dam_hub_prices_2024` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2024` | 52,704 |
| `ercot_dam_hub_prices_2025` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2025` | 52,560 |
| `ercot_dam_hub_prices_2026` | `ercot_all_hub_prices_history` | `market=ercot_dam`, `year=2026` | 34,122 |
| `ercot_rtm_hub_prices_2015` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2015` | 210,240 |
| `ercot_rtm_hub_prices_2016` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2016` | 210,816 |
| `ercot_rtm_hub_prices_2017` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2017` | 210,240 |
| `ercot_rtm_hub_prices_2018` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2018` | 210,240 |
| `ercot_rtm_hub_prices_2019` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2019` | 210,240 |
| `ercot_rtm_hub_prices_2020` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2020` | 210,816 |
| `ercot_rtm_hub_prices_2021` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2021` | 210,240 |
| `ercot_rtm_hub_prices_2022` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2022` | 210,240 |
| `ercot_rtm_hub_prices_2023` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2023` | 210,240 |
| `ercot_rtm_hub_prices_2024` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2024` | 210,816 |
| `ercot_rtm_hub_prices_2025` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2025` | 210,240 |
| `ercot_rtm_hub_prices_2026` | `ercot_all_hub_prices_history` | `market=ercot_rtm`, `year=2026` | 136,488 |

## How each store moves

- **The daily run** (`warehouse/consolidate.py`). The connectors are unchanged: they still read and write the members, as working files.
  - After the restore, `consolidate.py split` writes the members from the consolidated tables.
  - After the last connector, `consolidate.py build` writes the consolidated tables from the members, checks rows and partition values, and moves the members to `warehouse/output/members/`.
  - Nothing after the build sees an old name: not the validator, coverage, the archive, Supabase or Redivis.
- **The archive** (`warehouse/archive/`). Existing partitions are never rewritten or renamed.
  - From the next daily run, appends go under the new names.
  - `restore.py` reads the map: a new table's rebuild replays its members' archived lines, adds the partition columns, then applies its own lines.
  - The new tables' change indexes are seeded from the consolidated rows, so the first run under the new names archives only what is new, not the history again.
- **Redivis.**
  - Every consolidated table is uploaded to the draft of its license's dataset (all six are public).
  - The old tables stay in both datasets. Their manifest entries are kept and marked `migrated_to`, so the history gate keeps their counts.
  - `upload.py --remove-migrated` removes them after checking every family; its exact command and checks are in the session report and `docs/runbook.md`.
- **Supabase.**
  - The live set loads the consolidated tables (all but the ERCOT history, which was never in it), and the old tables' rows are dropped in the same run.
  - Migration 009 adds the `ba` column to `series`.
- **The `erw` package.** The new names work with partition filters (`erw.fetch("eia930_all_demand", ba="ciso")`). An old name still works through the map, with a `DeprecationWarning`, until the first monthly release.
- **The site and the chat.** Every query that read an old table reads the new one, filtered by entity or market.
