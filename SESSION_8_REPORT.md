# Session 8 report

Energy Research Warehouse (ERW), session 8, run 2026-09-25 to 2026-09-26 (UTC). Every task in SESSION_8_PROMPT.md was carried out, with one storage decision in Task 4 explained below. The session 7 rulings were applied:
- no equities connector;
- no permission requests made from here;
- no rig counts;
- PortWatch is built and registered internal.

Nothing was pushed. No key is printed, logged or committed. The EIA key is removed from every stored URL (`redact`); no other source this session needs a key.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | Full daily sequence run end to end: exit 0, every stage ok except SPP real-time (a missing SPP file, not fixable without filling). Row counts before and after below | `8bdfc66` |
| 2 | `eia860.py`: the first entities tables, `eia860m_operating_generators` (28,605), `eia860m_planned_generators` (2,316), `eia860m_retired_generators` (249). The validator enforces the entities shape (Decisions 20 to 22). Monthly cadence in `run_daily.sh` | `f433610` |
| 3 | `iso_queues.py`: `<iso>_interconnection_queue` for ERCOT, CAISO, NYISO, MISO, SPP and ISO-NE (14,567 queue positions), harmonized status beside each ISO's own. Weekly in `run_daily.sh`. PJM skipped: no key | `a4f2bda` |
| 4 | ERCOT: HB_HUBAVG added to the hub list; real-time and day-ahead hub prices from 2015-01-01, complete, in yearly history tables. The human's 2015 and 2025 HB_HUBAVG numbers are reproduced exactly | `f52bb19` |
| 5 | EIA retail electricity prices (USD/MWh), first purchase prices (Mars, North Dakota), crude imports by country, PADD-to-PADD crude pipeline flows, and IMF PortWatch daily transits for Hormuz, Suez and Panama (internal) | `25da1ac` |
| 6 | Validator, coverage (entities rows, sector), `erw.fetch`, `filter`, `cite` and `info` for entities; tests for every new table; `docs/platform-tools.md` tools 2, 3, 4, 5 and 7 updated | `bb57342` |
| 7 | This report | final commit |

## Task 1: the daily run

`PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh`, 2026-09-25 23:45 to 2026-09-26 00:01 UTC, exit 0.
- **Connectors:** ercot, caiso, nyiso, miso and isone ok; spp failed on RTM only; eia930, eia_fuels, eia_series, capacity_prices, carbon_auctions and fred_series ok; news_ingest, news_score, news_index and news_brief ok.
- **SPP real-time:** SPP has no daily RTBM file for 2026-09-22, and one 5-minute interval file (14:05 CT) is missing (`SourceGap`). The market is not written. Filling it would break the real-data rule, so nothing was "fixed"; this is the same SPP publication gap sessions 2 to 7 report.
- **Checks:** the validator passed all 41 tables; coverage and the digest (`docs/digest/2026-09-26.md`, dated by UTC) were rebuilt; no market has failed three runs in a row.

Row counts before and after the run: every price, fuel and EIA-930 table has the same count, because the 3-day window was re-pulled and replaced (0 new rows). Only the news tables grew:

| Table | Before | After |
|---|---|---|
| `news_stories` | 655 | 714 |
| `news_index` | 655 | 714 |
| all other 39 tables | 324,194 rows | 324,194 rows |

## Task 2: EIA-860M generators (entities)

- **Source:** the newest published workbook on https://www.eia.gov/electricity/data/eia860m/, vintage 2026-08 (`august_generator2026.xlsx`, last modified 2026-09-23). EIA's page already links September to December 2026; those URLs return an HTML page with HTTP 200, so the connector checks for an xlsx (`PK`) and walks back to the newest real one.
- **Rows:** one per generator, `entity_id` `eia860:<plant id>:<generator id>`, the same id in all three tables. Puerto Rico sheets included.
  - operating: every row in EIA's operating inventory (EIA codes OP, SB, OA, OS), `status` `operating`, EIA's code kept in `eia_status`.
  - planned: `status` `planned` (P, L, T, OT) or `under_construction` (U, V, TS), EIA's code kept.
  - retired: retirement year 2025 or 2026 (the vintage year and the year before), `retirement_date` and `status_date` at the first of EIA's month.
- **Codes and labels:** EIA's codes are unchanged. `prime_mover_label` and `energy_source_label` come from the EIA-860 instructions, and `technology_group` groups EIA's technology text (solar, wind, storage, natural_gas, coal, nuclear, ...). An unknown code fails the run.
- **Vintage:** in every row. Tables are snapshots (Decision 21): a new vintage replaces the rows. `run_daily.sh` runs the connector daily; it writes only when EIA's newest vintage changes (verified: a second run said "vintage 2026-08 unchanged, nothing written").
- **Validator (entities shape):**
  - required columns and order;
  - `entity_id` format and uniqueness;
  - `entity_type` vocabulary;
  - `geo` format;
  - lat in [-90, 90] and lon in [-180, 180], numeric, both or neither;
  - every MW column numeric;
  - status vocabulary;
  - every date column `YYYY-MM-DD`.

## Task 3: interconnection queues (entities)

| ISO | Rows | active | withdrawn | completed | suspended | no status | Notes |
|---|---|---|---|---|---|---|---|
| ERCOT | 1,778 | 1,198 | 0 | 580 | 0 | 0 | ERCOT's GIS report lists no withdrawn projects |
| CAISO | 2,278 | 262 | 1,764 | 252 | 0 | 0 | The URL redirects to a lowercase path |
| NYISO | 1,814 | 210 | 1,453 | 151 | 0 | 0 | 1,350 blank rows dropped; 2 queue ids repeat (phases) |
| MISO | 3,870 | 1,165 | 2,148 | 557 | 0 | 0 | MISO's API gives no project names and leaves county, state and fuel empty on some new projects |
| SPP | 3,076 | 629 | 2,053 | 336 | 24 | 34 | No project names; 34 affected-system (ASGI) requests have no status in SPP's file |
| ISO-NE | 1,751 | 59 | 1,329 | 363 | 0 | 0 | 92 queue ids repeat over 242 rows (units) |

- **Status:** `iso_status` keeps each ISO's own vocabulary. For SPP that is the original status text (for example "IA FULLY EXECUTED/ON SUSPENSION", mapped to suspended). `status` is mapped by a per-ISO table in the connector, and a status not in that table fails the ISO.
- **Repeated queue ids** get `:<n>` in the ISO's row order.
- **Dates:** the ISO's own dates, as `YYYY-MM-DD`.
- **Negative capacities:** six rows have negative `capacity_mw`: ERCOT repowers 18INR0064 (-7.2 MW), 19INR0120, 20INR0019 and 24INR0372, and ISO-NE 438 and 148:4. These are net reductions as the ISO states them. The validator reports them and does not block them (Decision 20).
- **Raw capture and citation:** every response is captured raw, and each table cites the exact file it came from.
- **Cadence:** weekly, on Mondays (UTC) in `run_daily.sh`, or any day with `QUEUES=1`.

## Task 4: ERCOT history and the HB_HUBAVG comparison

**Storage decision.** The prompt asked for the backfill "into the existing ERCOT tables through the merge writer". I wrote it through the merge writer into yearly tables with the same columns, variables and sources: `ercot_rtm_hub_prices_<year>` and `ercot_dam_hub_prices_<year>`, 2015 to 2026. The existing tables stay the rolling live window. The reasons:
- A row is about 226 bytes, so the real-time history alone is about 2.5 million rows and 550 MB. GitHub refuses files over 100 MB, so the repository could no longer be pushed.
- The daily workflow rewrites and commits each live table every day. A 550 MB table would add a new large blob to git history daily.

Each yearly real-time table is about 48 MB (under GitHub's 50 MB warning) and each day-ahead table about 12 MB. The history is written once (`python warehouse/connectors/iso_prices.py ercot --backfill-from 2015`); the 2026 tables stop exactly where the live tables begin (2026-08-26 05:00 UTC), with no gap and no overlap (tested). `erw.filter(market="ercot_rtm")` returns the live table and all yearly tables.

**HB_HUBAVG:**
- It is in `ERCOT_HUBS`, so every ERCOT run now pulls it.
- The live tables were rerun for 30 days, so HB_HUBAVG covers the whole live window.
- All yearly tables include it.

**Sources:**
- Real-time: NP6-785-ER "Historical RTM Load Zone and Hub Prices", one zip per year (`RTMLZHBSPP_<year>.zip`).
- Day-ahead: NP4-180-ER "Historical DAM Load Zone and Hub Prices" (`DAMLZHBSPP_<year>.zip`), newly registered.
- Every row names its document (`source_url`, `vintage`); all zips were captured raw.

**Completeness.** Every hub, every year, exactly as the prompt expects:

| Years | Real-time per hub | Day-ahead per hub |
|---|---|---|
| 2015, 2017, 2018, 2019, 2021, 2022, 2023, 2025 | 35,040 | 8,760 |
| 2016, 2020, 2024 (leap) | 35,136 | 8,784 |
| 2026 to 2026-08-26 05:00 UTC | 22,748 | 5,687 |

All six hubs are complete in every year: HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON, HB_BUSAVG and HB_HUBAVG.

**DST.** Each yearly table covers the ERCOT operating year in America/Chicago, from Jan 1 00:00 to the next Jan 1 00:00, written in UTC.
- The spring-forward hour does not exist, so it has no rows.
- The fall-back hour occurs twice in local time. ERCOT marks the repeat with DSTFlag, and gridstatus turns the two into two distinct UTC hours.
- So a local year is always exactly 365 or 366 x 24 real hours, which is 35,040 or 35,136 quarter hours. A duplicate (hub, interval) would fail the table, and there were none.

**The comparison.**

| HB_HUBAVG, USD/MWh | Human's value | ERW, real-time 15-minute | Match |
|---|---|---|---|
| 2015 median | 20.49 | 20.49 | yes |
| 2025 median | 25.68 | 25.68 | yes |
| 2015 99.9th percentile | 583.96 | 583.96 | yes |
| 2025 99.9th percentile | 311.80 | 311.80 | yes |

- **How it was computed:** all 35,040 15-minute real-time settlement point prices of the ERCOT operating year, with numpy's default linear-interpolation percentile.
- **Other definitions do not match**, which pins down the human's method:
  - day-ahead hourly: 2015 median 21.73 and p99.9 525.05; 2025 median 27.83 and p99.9 273.51;
  - hourly means of real-time: 2015 median 20.53 and p99.9 533.41; 2025 median 25.90 and p99.9 294.05;
  - other percentile methods: for example, "higher" gives 584.09 for the 2015 p99.9.
- **The finding:** the median rose 25% from 2015 to 2025, while the 99.9th percentile fell by nearly half.

## Task 5: remaining free monthly series

| Table | Route | Rows | History | Unit | License |
|---|---|---|---|---|---|
| `eia_retail_electricity_prices` | `electricity/retail-sales`, price | 114,202 | 2001-01 to 2026-07 | USD/MWh | public |
| `eia_crude_first_purchase_prices` | `petroleum/pri/dfp2` (Mars F003075793), `dfp1` (North Dakota F002038__3) | 858 | 1977-07 to 2026-06 | USD/bbl | public |
| `eia_crude_imports_by_country` | `petroleum/move/impcus`, crude, the kbbl/d series | 22,615 | 1920-01 (US total) to 2026-06 | kbbl/d | public |
| `eia_padd_crude_pipeline_flows` | `petroleum/move/pipe`, crude, 8 PADD pairs | 4,550 | 1986-01 to 2026-06 | kbbl | public |
| `portwatch_chokepoint_transits` | IMF PortWatch ArcGIS Daily_Chokepoints_Data | 118,440 | 2019-01-01 to 2026-09-20 | count, dwt | internal |

- **Retail prices:**
  - EIA reports cents per kilowatt-hour; the table stores USD/MWh = EIA value x 10, which is exact. The conversion is stated in the header.
  - Entity: `eia:retail_price:<state>:<sector>`, covering all states, the US total and census divisions, and sectors ALL, RES, COM, IND, TRA and OTH.
  - Example: Texas all-sector July 2026 is 10.91 cents/kWh, stored as 109.1 USD/MWh.
- **PADD route.** docs/price-sources.md named `petroleum/move/ptb`. That route has only "Receipts by Pipeline, Tanker, Barge and Rail". The prompt asked for pipeline flows, so the table uses EIA's pipeline-only route, `petroleum/move/pipe`.
- **Where the code lives:** the EIA tables are under the existing `eia_series.py`. PortWatch is a new `portwatch.py`: it is its own source, and CLAUDE.md asks for one connector per source.
- **PortWatch:**
  - variables: `n_*` vessel transits per day (tanker, container, dry bulk, general cargo, ro-ro, cargo, total) and the `capacity*` deadweight tonnage of those transits;
  - completeness: all 2,820 days present for each chokepoint, no gaps;
  - license: registered internal, citation "IMF PortWatch".

## Task 6: validation, coverage, package

- **All 79 tables pass `erw_validate`:** 68 series, 9 entities, 2 events.
- **`coverage.csv`** has entities rows: interval `snapshot`, `ts_min` and `ts_max` at the snapshot's retrieval time, `n_nodes` = entities. The `sector` rules cover every new table.
- **The `erw` package** handles entities tables:
  - `fetch` types `lat`, `lon`, `capacity_mw` and `*_mw` as floats and `*_date` as dates;
  - `node=` selects entity ids or names, and `start`/`end` select on `status_date`;
  - `filter(variable=)` matches `entity_type` or `status`;
  - `cite` names the report from the registry;
  - `info` summarizes an entities table.
- **Tests:** 346 package tests pass (up from 189: every new table is parametrized, plus tests for the entities rules, EIA-860M vintage and statuses, the queue status mapping, and complete ERCOT years), and 11 repo tests pass. A full package run takes about 8 minutes now.
- **`docs/platform-tools.md`:**
  - tool 5 (signature explorer) is now **yes** for the ERCOT peak premium;
  - tools 2, 3, 4 and 7 are **partial**, with the new tables and the remaining gaps named.

## Row counts by shape

| Shape | Tables | Rows |
|---|---|---|
| series | 68 | 3,652,077 |
| entities | 9 | 45,737 |
| events | 2 | 1,428 |
| **total** | **79** | **3,699,242** |

At the start of the session: 41 tables, 325,504 rows. License: 73 tables public, 6 internal:
- `pjm_rpm_capacity_prices`;
- `carb_auction_allowance_prices` and `rggi_auction_allowance_prices`;
- `fred_imf_commodity_prices`;
- `portwatch_chokepoint_transits`;
- `news_stories`.

## Decisions

1. **ERCOT history in yearly tables** (Task 4, above). The skill file records the rule for large history.
2. **Entities tables are snapshots** (Decision 21): an inventory or queue replaces its rows. Merging would keep generators that retired and queue positions that were withdrawn.
3. **Entities status vocabulary** extended by `active`, `completed` and `suspended` (Decision 20), so that the prompt's harmonized queue statuses fit. EIA's and each ISO's own status stay in their own columns.
4. **Operating inventory status:** standby (SB) and out-of-service (OA, OS) generators are `operating` in `status`, because EIA lists them as existing capacity. The distinction is in `eia_status`.
5. **Negative MW** in queues is reported, not blocked. The validator never blocks a value the source states.
6. **Queue dates** keep the ISO's date. A CAISO timestamp such as `2004-05-24 07:00:00` (local midnight written in UTC) becomes 2004-05-24.
7. **New unit `dwt`** (Decision 22).
8. **The monthly cadence for EIA-860M** means a daily run that writes only on a new vintage. It still downloads the 14 MB workbook each day to read the vintage from it, because the page links months that do not exist yet.

## Errors hit

1. **CAISO's queue** was not found in the raw capture at first: the URL redirects to a lowercase path. The connector refused to write an uncited table, as designed. Fixed with a case-insensitive match.
2. **SPP's 34 status-less rows** failed the status table on the first try. They now keep an empty status rather than a guessed one.
3. **Negative capacities** blocked the ERCOT and ISO-NE queues in the first validator draft. It now reports them instead (reason above).
4. **A trial run's `--out-dir`,** given as a Git Bash path (`/c/Users/...`), wrote to `C:\c\Users\...` under Windows Python. That directory held only my 14 trial files; I removed it after validating the trial output. The skill file now warns about it.
5. **A long patch through a bash heredoc** failed to parse. Patches went through script files after that.

## Size of the repository

- `warehouse/output` is now about 950 MB, most of it the ERCOT history (about 660 MB, as `du` counts).
- No file is over 100 MB.
- Two files are over GitHub's 50 MB warning, and a push will print a warning for them:
  - `eia_product_spot_prices` (58 MB, session 7);
  - `eia_retail_electricity_prices` (52 MB).
- The validator now takes about 4 minutes over all tables.

## Rerun

```bash
PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh                      # daily; QUEUES=1 forces the queues
.venv/Scripts/python warehouse/connectors/eia860.py --force                  # rebuild EIA-860M now
.venv/Scripts/python warehouse/connectors/iso_queues.py                      # all queues
.venv/Scripts/python warehouse/connectors/iso_prices.py ercot --backfill-from 2015   # ERCOT history
.venv/Scripts/python warehouse/connectors/portwatch.py
.venv/Scripts/python -m pytest package/tests -q
```

## Open questions for the human

1. **ERCOT history storage.** Are the yearly history tables acceptable, or should the ERW move large tables to Parquet or Git LFS (the "size limit" item deferred in docs/datastandard.md) and fold the history into one table?
2. **Queue geography.** The ISO queues give county and POI but no coordinates. Should the ERW geocode county centroids for the project map (tool 3), or wait for ISO or EIA coordinates?
3. **Unnamed queue positions.** MISO and SPP give no project names. Should the ERW join queue positions to EIA-860M planned generators, and if so, by what key?
4. **Carried over:** a PJM API key (PJM energy prices and the PJM queue), a Tiingo key (equities), the repository secrets, and the eval sample.
