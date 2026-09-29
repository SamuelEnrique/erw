# Session 31 report

Energy Research Warehouse (ERW), session 31, run 2026-09-29 from about 12:25 to 13:20 UTC, straight after session 30 (the chain clause).

**API spend: USD 0.00.** No model call of any kind: no script that calls the Anthropic API ran, and the cost ledger has no session 31 row.

- No existing table was re-pulled; nothing was deleted from Redivis.
- The deploy is live: routes 31 of 31, values 1,196 of 1,196.
- **Part A (emissions) was not built.** EIA does not publish the series the approved pull names (section 1).

## 1. Rows pulled against the 1.2M ceiling; routes and series starts

**Pulled: 70,416 new rows, 5.9% of the 1,200,000 ceiling.** All of it is EIA-930 battery storage; nothing else was pulled.

**Emissions: not found anywhere EIA publishes EIA-930.** I checked three places, reading metadata only:

- **The EIA API v2.** The route tree `electricity/rto` has 8 routes: region-data, fuel-type-data, region-sub-ba-data, interchange-data, and their daily versions. None carries emissions.
  - The `type` facet of region-data offers D, DF, NG and TI only.
  - The `fueltype` facet of fuel-type-data offers the generation fuels only.
- **The Grid Monitor's bulk files.** `electricity/gridmonitor/sixMonthFiles/EIA930_File_List_Meta.csv` lists 63 files, all BALANCE, INTERCHANGE or SUBREGION. The newest BALANCE file's 65 columns (read from its first 4 KB) are demand, forecast, generation, interchange and generation by fuel. None is CO2.
- **The Grid Monitor web app.** Its code (`main-62AHFAMH.js`, 4.9 MB, no lazy chunks) contains no "CO2" or "emission" string.

EIA's older articles describe hourly CO2 estimates in the Grid Monitor, but EIA serves none today by any of these means.

**What that means for Part A:**

- `eia930_all_emissions` and the three carbon-intensity tables were not built.
- `/emissions` was not built, and no nav link points to it.
- Computing emissions myself (generation by fuel times emission factors) would be a different, unapproved product (question 1).
- `package/llms.txt` now lists EIA-930 CO2 emissions as not in the warehouse.

**Battery storage (B1): a pull.**

- `eia930_all_generation` carries `net_generation_battery_mw`, but only for its rolling 30 days, not from the series start.
- So BAT was pulled into `eia930_all_storage`: route `electricity/rto/fuel-type-data`, facet `fueltype=BAT`, hourly, the existing EIA-930 key.

| BA | First BAT hour (EIA) | Hours written | Days left out (incomplete) |
|---|---|---|---|
| US48 | 2024-07-15 | 16,728 | 109 (2024-07-15 to 2024-10-31: 24 scattered hours in July, none in August to October; continuous from 2024-11-01) |
| ERCO | 2024-11-06 | 16,536 | 3 (the first day, and 2 others) |
| ISNE | 2024-11-06 | 16,584 | 1 (the first day) |
| MISO | 2025-01-15 | 14,904 | 1 (the first day) |
| SWPP | 2026-02-04 | 5,664 | 1 (the first day) |
| CISO, NYIS, PJM | none (the API returns 0 rows) | 0 | |

**How the pull ran:**

- One BA and one month per request, 5,000 rows a page.
- Every page saved raw under `warehouse/raw/eia930_storage/20260929T123511Z/`.
- Each finished past month checkpointed, so an interrupted pull resumes; it was not interrupted.
- The key is removed from every URL, log and row (grepped).

**Checks:**

- A 2-day smoke test in the scratchpad passed the validator first.
- Against the 120 overlapping hours of `eia930_all_generation`: 119 equal. The one difference is a US48 hour EIA revised between the two pulls (3,646 against 3,638 MW).

## 2. The two pages

**`/storage`** (nav: Grid, then Storage). Every number is a table value, or a sum of `storage_capacity` rows that `check-values.mjs` recomputes from Supabase. Tier chips, a citation on every block, a method link (`docs/methods/storage.md`), Stanford palette.

- **The fleet,** from `storage_capacity` (EIA-860M):

  | Status | MW | Units |
  |---|---|---|
  | Operating | 54,488.90 | 1,137 |
  | Under construction | 23,543.80 | 237 |
  | Planned | 40,914.30 | 245 |
  | Retired | 338.50 | 8 |

- **By ISO** (operating, under construction, planned). The ISO is the unit's balancing authority when it is one of the seven; 15,567.50 MW operate outside them.
- **By state:** the 15 with the most operating MW (TX 18,404.50, CA 16,333.70, AZ 6,648.80, ...).
- **Planned additions by year** (under construction and planned, by EIA's planned operation date): 2026 12,093; 2027 25,154.40; 2028 14,788.70; 2029 9,020.90; 2030 2,182.50; 2031 1,218.60 MW.
- **The daily cycle,** from `storage_daily_cycle`, the latest complete local day per BA (2026-09-27):
  - discharged and charged MWh, out over in, peak discharge and charge hour, and a 30-day sparkline;
  - for example ERCOT: 24,862 MWh out, 26,473 MWh in, discharge peak 19:00 and charge peak 09:00 Central. Checked by hand from the hourly rows.
- **Hour by hour, 30 days,** and **the last 24 hours,** from `eia930_all_storage`: ERCOT, ISO-NE, MISO and SPP on one chart, US48 on its own.

**What is missing on `/storage`, and why:**

- **CAISO, NYISO and PJM** report no BAT series in EIA-930; the page says so. CAISO's own battery output is `caiso_battery_storage`, which is not shown here.
- **Energy capacity (MWh)** is not in the ERW's EIA-860M tables, so it is not shown and not estimated.
- **ISO-NE and SPP report no charging** (no negative hour) on the latest day, so their "out over in" says none.
- **US48's out over in is 1.84:** BAs report charging differently. The method page says the ratio is not an efficiency.

**`/emissions`:** not built (section 1).

## 3. Reconciliation

- **Validator:** the three new tables pass. Coverage: **74 tables, all 74 pass, 4,906,923 rows** (62 public, 12 internal; 71 and 4,822,974 at session 30's end).
- **A new unit, `hour`:** an hour of the day, local, the hour's start. It is Decision 29 in `docs/datastandard.md`, added to the validator and the standard together.
- **Tiers:** `eia930_all_storage` source; `storage_daily_cycle` and `storage_capacity` derived (`storage_capacity` by a `TIER_RULES` line, as `energy_projects`).
- **Archive:** 83,949 rows appended (70,416 + 11,906 + 1,627), locally and in the bucket, with new names only. No existing partition touched.
- **Supabase:** 285.9 MB before, **300.0 MB after** the vacuum (limit 400). Every table matched:
  - `eia930_all_storage`, the last 90 days: 10,735 rows;
  - `storage_daily_cycle`, whole: 11,906;
  - `storage_capacity`, whole: 1,627.
- **Redivis draft, public dataset:** each `count(*)` equals its CSV (70,416; 11,906; 1,627), plus `erw_headers`, `erw_coverage` (74) and `erw_sources` (157). The license check finds 0 internal tables in the public dataset. Nothing released.
- **The daily run:**
  - `eia930_storage.py --days "$DAYS"` right after `eia930.py`, merging on (entity, variable, ts_utc) as EIA-930 demand does, then `storage_daily_cycle.py`;
  - `storage_capacity.py` after `energy_projects`. It skips cleanly on a day the runner has no EIA-860M tables.
  - `eia930_all_storage` is restored from the draft before the run. `storage_capacity` is not: it is a snapshot that may shrink, and the draft's shrink gate would then block the upload.
- **The rest:** `package/llms.txt` lists the three tables; the chat spec was regenerated and matches. `check-routes.mjs` and `check-values.mjs` include `/storage`, with new `storage|...` check kinds.
- **Tests:**
  - `tests/`: 51 of 51.
  - The package tests touching the new tables, filters, sectors, coverage, listing and backends: 138 passed, 0 failed (the rest deselected; they read no new table).

## 4. Decisions made without a human (each reversible)

1. **No emissions table, and no `/emissions` page.** EIA publishes no such series; computing one would be a new, unapproved derived product. `llms.txt` says it is not in the warehouse.
2. **Storage pulled into its own table** (`eia930_all_storage`, partition `ba`), because the generation table holds only 30 days.
   - Only the five BAs that report BAT; the three that do not are named in the header, the method and on the page.
   - The variable keeps the generation table's name, `net_generation_battery_mw`.
3. **Completeness per UTC day,** the EIA-930 generation rule of session 16. US48's sparse July 2024 hours are left out as 109 incomplete days, not filled.
4. **Local days for the daily cycle:**
   - US48 on America/New_York, the Eastern time EIA's Grid Monitor shows by default;
   - MISO on EST, as MISO publishes;
   - peak hours are hour-beginning, with the earliest hour on a tie.
5. **`round_trip_ratio`** is named as the prompt names it, and documented as out over in, not an efficiency.
6. **`storage_capacity` keeps** EIA's nameplate MW, its own status and code, `planned_year` from the planned operation date, and `iso` only for the seven ISOs.
7. **The page's hourly profile shows the hourly values themselves** for 30 days: no computed average-by-hour, so no number on the page is computed but the fleet sums.
8. **A formatter matching the value checker** (`shown()`: whole numbers without decimals) on `/storage` and, from session 30, `/board`. A whole-number value would otherwise have failed the check some day.

## 5. Run health, gate, the 14:00 UTC run

- **Gate:** open at the start and at the end. `build_status.py --gate` reads the GitHub run of 2026-09-28: 0 failed tables outside the known-gap list.
- **The 14:00 UTC daily run had not landed** by this report (13:20 UTC). `origin/main` had no new commit at either push.
- **Its first run with sessions 30 and 31's steps** will, besides the usual:
  - restore `eia930_all_storage`;
  - pull 3 days of BAT;
  - rebuild the cycle, and `storage_capacity` when the EIA-860M tables are there;
  - build the price board with carried rows;
  - run the Haiku shadow.
- **Run status:** this session's connector results were recorded in `warehouse/metadata/run_status.csv`, including the 115 storage gap rows.

## 6. Spend, open questions, what was skipped

**Spend:** USD 0.00, confirmed; the cost ledger has no session 31 row.

**Open questions for Samuel:**

1. **Emissions.** EIA-930 CO2 estimates are not published in any form I could reach (API v2 routes and facets, bulk file columns, the Grid Monitor's code). Three options:
   - an ERW-derived estimate: generation by fuel from EIA-930 times EIA's published CO2 emission factors, tier derived, clearly labelled as the ERW's estimate and not EIA's;
   - wait for EIA;
   - another source.
2. **CAISO's batteries on `/storage`:** add `caiso_battery_storage` (CAISO's own 5-minute data, since 2025-08) beside the EIA-930 series?
3. **Energy capacity in MWh:** the ERW's EIA-860M tables carry no battery energy capacity. The annual EIA-860 has it; I did not check whether the monthly 860M file does. Should a later session look, and add it if so (a change to an existing table's schema, so yours to approve)?

**Skipped:**

- All of Part A (section 1).
- The full package suite: only the tests that read the new tables or the catalogue were run (138 passed). The rest read no new table and passed at the end of session 30.
- Nothing else in B, C4 or D.
