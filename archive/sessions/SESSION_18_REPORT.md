# Session 18 report

Energy Research Warehouse (ERW), session 18, run 2026-09-27 (UTC). **API spend this session: USD 9.5589**, under the USD 15 stop. That is USD 9.0404 on this machine (scoring 7.5381, deals 1.4132, datacenters 0.0891) and USD 0.5185 in GitHub run 5, which I dispatched (scoring 0.4775, digest 0.0281, deals 0.0129). No key was printed or committed. `origin/main` was merged before each push.

**Four things to know first:**
- **Supabase is over the loader's 300 MB limit, at 362.1 MB of the free tier's 500 MB, and I could not fix that.** GitHub run 4's `supabase_load` failed on two causes (below). The fix needs rows deleted from, and a `VACUUM FULL` run on, the shared database. Claude Code's auto-mode classifier refused me that ("Modify Shared Resources"), so I built the fix for a person to run: `python warehouse/supabase/load.py --prune --vacuum-full`. Until someone runs it, every load reports the size failure.
- **The backfill is finished.** The deduplication now takes one bucket at a time against an on-disk set. The 47,578 saved items gave 28,615 new stories, and 3,000 were kept, scored and run through both extractors. Deals rose from 27 to 191, and datacenter facilities from 3 to 11.
- **Three new platform tools (21 to 23) have data and pages:** `/mix` (energy mix), `/curtailment` and `/consumption`. The value check matches 510 of 510 values, 93 of them on the new pages.
- **ERCOT and MISO publish no curtailment.** For ERCOT, the ERW writes "output below the High Sustained Limit", named as its own estimate, never as curtailment. For MISO, the page says there is none.

## What was built

| Task | Result | API cost | Commit |
|---|---|---|---|
| 0 | Memory-safe backfill; 3,000 stories scored and extracted; loader and map-builder fixes; Supabase load; run 5 dispatched | 9.0404 | `6d123e7` |
| 1 | Energy mix explorer: `eia_state_generation_monthly`, `state_generation_mix_monthly`, `eia930_generation_latest`, `/mix` | 0 | `40107aa` |
| 2 | Curtailment tracker: CAISO, SPP, ERCOT daily tables, `iso_curtailment_monthly`, `/curtailment`, method doc | 0 | `4e93a6d` |
| 3 | Consumption by sector: `eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly`, `/consumption` | 0 | `db9c9c5` |
| 4 | Validator, coverage, live set, briefing, tools 21 to 23, value check, screenshots, this report | 0 | final commit |

## Task 0

### The backfill, memory-safe

`ingest.py --backfill` no longer holds every item at once:
- It reads the 84 (month, sector) buckets one at a time. From saved responses (`--from-raw`), the manifest is grouped by bucket first, and each response is parsed only when its bucket is reached.
- Each bucket is deduplicated against an on-disk SQLite set (`warehouse/raw/news/<run_id>/backfill_seen.sqlite`). The set is seeded with the stored stories' event ids and normalized titles, and each bucket's new stories are written into it.
- The near-identical-title test is unchanged: difflib ratio of at least 0.92, with length difference under 20. A numpy character-count prefilter skips pairs whose `quick_ratio` is already below 0.92, which the test would reject anyway.
- A trial over one sector (1,399 titles) gave the same decisions as the old brute-force test: 0 mismatches.
- The round-robin cap is computed from per-bucket counts, and only the kept stories are read back into memory.
- Within a bucket, direct feeds come first, then publish time. Buckets run in (month, sector) order, so a story found in two buckets is kept in the earlier one. The docstring says so.

| Step | Count | Cost (USD) |
|---|---|---|
| Items read from `20260927T033451Z` (1,512 responses, 84 buckets) | 47,578 | 0 |
| Already stored or same URL | 13,848 | |
| Near-identical title | 3,304 | |
| Outside 2025-10-01 to 2026-09-22 | 1,811 | |
| New after deduplication | 28,615 | |
| Kept under the cap (round-robin) | 3,000 | |
| Google News links resolved to the outlet | 0 of 3,000 (Google served its own page every time) | |
| `score.py --days 400 --max-calls 70`: 70 calls, 3,000 of 3,000 scored, 3,837 clusters among 4,184 stories | 3,000 | 7.5381 |
| `deals/extract.py --max-calls 200`: 41 calls, 597 stories checked, 18 numbers or fields not kept | 191 deals (164 new) | 1.4132 |
| `datacenters/extract.py --max-calls 100`: 9 calls, 91 stories checked, 2 fields not kept | 11 facilities (8 new) | 0.0891 |

- **`news_stories` and `news_index`** now hold 4,184 stories, 2025-10-01 to 2026-09-27.
- **The deals by type:** M&A 64, fuel supply 31, other 27, equity raise 23, debt 11, joint venture 10, offtake 9, project finance 8, PPA 5, lease 1, nuclear restart 1, SMR 1.
- **"other" is the largest scored sector** (1,493 of 4,184). Many backfill stories that the site filters and sector terms found are outside the rubric's named sectors.
- **The 11 facilities** have gaps: 6 have no status and none states MW. Examples: QTS's Digital Gateway (VA, cancelled), Amazon at a GWU Virginia campus (announced), Chevron's West Texas Power Hub (no state stated), Google (AR), Vultr (OH).

### GitHub run 4's `supabase_load` failure

I read the run's log artifact (`daily-prices-log`) through the API.
- **Cause 1: `sources: CSV 100, Supabase 101`.** The loader only ever upserted sources, so a source that left `sources.csv` stayed in Supabase. That source is `epa.gov`.
- **Cause 2: `pg_database_size` 300.6 MB, over `max_mb` 300.** The `series` table held 315,740 live and 62,631 dead row versions, 218 MB with indexes. The `source_url` column alone averages 203 bytes a row, about half the row.

What I changed:
- **The loader now names stale sources on every run.** `--prune` deletes them, and also deletes the rows of any table in `coverage.csv` that no live-set rule matches.
- **`--vacuum-full`** compacts the shape tables through `SUPABASE_DB_URL`, because only `VACUUM FULL` shrinks `pg_database_size`. The scheduled run passes neither flag.
- **`live_set.yaml` `select`** also takes `include`, `since` and `days` (a per-table window), used for the new tables.

**Not done: the cleanup itself.** I tried to delete the stale source, drop two duplicated table groups from the live set, and run `VACUUM FULL`. The classifier refused it. Those groups are the ERCOT yearly tables (whose last 90 days repeat the rolling tables) and the EIA-860M operating and planned generators (which reach Supabase through `energy_projects`). I restored the live-set rules and left all of it to you (open question 1).

### Supabase load (Task 0)

A full load from this machine would have made Supabase equal my older local price tables, rolling back what CI loaded. So I loaded, with `--only`, the four tables this machine produced:

| Table | Rows | Written |
|---|---|---|
| `news_index` | 4,184 | 3,000 |
| `energy_deals` | 191 | 166 |
| `datacenter_projects` | 11 | 11 |
| `energy_projects` | 36,741 (withdrawn positions left out) | 36,741, first load |

- **Size:** `pg_database_size` 321,367,187 bytes (306.5 MB) after this load, 379,726,995 bytes (362.1 MB) after Task 4's load of the new tables, and **385.5 MB** after CI run 5's full load. The free tier stops writes at 500 MB.
- **The run 5 CI load** loads every live-set table from the runner (see below).

### NYISO and the map builder

`energy_projects.py` now needs the two EIA-860M tables and at least one queue:
- With some queues absent, it builds from the rest.
- It names each absent queue, with its latest failed run from `run_status.csv`, in an `Absent inputs:` header line and in the run status.
- The coverage builder repeats every `Absent inputs:` line in a note in `docs/coverage.md`.
- In CI with no queue at all, it still skips.

**Tested** with NYISO removed: 43,674 rows from five queues, and the header line names `nyiso_interconnection_queue`.

### GitHub run 5

`daily prices` run 5 (id 36309382650) was dispatched through the API with `queues=1`, on commit `6d123e7`. It ran 09:26 to 10:09 UTC. **Conclusion: success**, meaning every step of the workflow succeeded. Inside the run, from its log artifact:
- **NYISO's queue answered HTTP 202 again**, after 4 attempts. `energy_projects` was built from the other five queues (43,677 rows) and loaded to Supabase. Coverage carried the older `nyiso_interconnection_queue` row over.
- **Also failed, as known:** CARB's auction PDF (HTTP 202), and the ERCOT large-load watch (no request-level list; ruled a known gap).
- **`supabase_load` failed again,** on size and the stale source: every table matched, but `MISMATCH sources: CSV 126, Supabase 127`, and `pg_database_size` was 404,188,307 bytes (**385.5 MB**).
- **The commit, streak-issue and Redivis steps** succeeded. The run committed its metadata, docs and digest, merged here.

## Task 1: energy mix explorer (tool 21)

**`eia_state_generation_monthly`** (EIA-923 through `electricity/electric-power-operational-data`, public; added to `eia_series.py`):
- **Scope:** all sectors, 2001-01 to 2026-07, 200,030 rows. Locations: every state, DC, PR, US and EIA's census regions.
- **Energy sources:** ALL, COW, PET, NG, OOG, NUC, HYC, HPS, WND, SUN, GEO, BIO, OTH and DPV.
- **Unit:** MWh = EIA's thousand MWh x 1000.
- **Checked:** the twelve sources COW to OTH add up to ALL. For Texas, July 2026, that is 63,541,838.25 MWh to the digit. Over all 19,348 location-months, 254 differ by more than 0.1%, where EIA withheld a source.

**`state_generation_mix_monthly`** (derived, `docs/methods/generation_mix.md`):
- **Content:** eight fuel groups plus `not_itemized` (EIA's total minus the groups), in exact decimals, for 53 locations: states, DC, PR, US. 107,560 rows.
- **Checked:** groups plus `not_itemized` equal EIA's ALL everywhere, within 0.09 MWh (rounding to three decimals).
- **Why a derived table for Supabase:** it has half the source table's rows and a short `source_url` per row.

**`eia930_generation_latest`** (`eia930.py`):
- **What it is:** a snapshot of the last 48 hours' complete hours per BA. An hour is written only when net generation and every source the BA reports have a value.
- **This run:** 19 to 22 hours per BA, through 2026-09-26 02:00 to 05:00 UTC, because EIA publishes fuel data about 30 hours late.

**`/mix`:**
- **Selectors:** a grid-operator selector (hourly, EIA-930) and a state selector (monthly, EIA-923). EIA-930 has no states and EIA-923 has no ISOs, so the page keeps them apart and says why.
- **Today so far:** the latest day with complete hours, with the net generation MWh and a share strip.
- **The hourly chart:** the last 7 complete UTC days, stacked.
- **The monthly chart:** 2001 onward, stacked, with a fuel-share table for 2001, 2010, 2020, the latest full year and the latest 12 months, plus each group's MWh in the latest month.
- Every chart names its table.
- **New shared component:** `components/StackedArea.tsx`, server-rendered SVG with the existing fuel color tokens.

## Task 2: curtailment tracker (tool 22)

`warehouse/connectors/curtailment.py`, method `docs/methods/curtailment.md`:

| Table | Source | Rows | From |
|---|---|---|---|
| `caiso_curtailment_daily` | CAISO "Production and curtailments data" workbooks (11 files, 5-minute), then the Daily Renewable Report pages (chart arrays) from 2026-01-01 | 24,920 | 2014-05 |
| `spp_curtailment_daily` | SPP VER Curtailments: annual zips to 2024, daily files since; by BAA (SPP, SWPW) | 38,040 | 2014 |
| `ercot_wind_solar_hsl_daily` | ERCOT NP4-732-CD and NP4-745-CD: system-wide GEN and HSL, hourly, the week of reports ERCOT lists | 48 | 2026-09-19 |
| `iso_curtailment_monthly` (derived) | exact sums of complete months | 1,988 | |

**Checks.**
- **CAISO:** the ERW's 2026 monthly sums match CAISO's own year-to-date arrays. The two differ only by the rounding of the report's hourly values.

  | Month (2026) | ERW, MWh | CAISO, MWh |
  |---|---|---|
  | January | 26,573 | 26,573 |
  | February | 242,714 | 242,714 |
  | March | 774,415 | 774,416 |
  | April | 1,459,998 | 1,460,004 |
  | May | 1,448,985 | 1,448,995 |

- **CAISO by year:** 2.66 TWh curtailed in 2023 and 3.42 TWh in 2024.

**Three bugs found and fixed before the tables were kept.**
- **CAISO overlap.** CAISO's "June to December 2025" file starts on 2025-01-01 and repeats the 2025 workbook's curtailment. Each interval is now counted once (25,848 intervals).
- **Fall-back days.** My first dedup of production rows dropped the repeated hour of every fall-back day, whose intervals share local timestamps. Production is no longer deduplicated; it never overlaps.
- **SPP monthly files.** SPP's annual zips also hold monthly files that repeat the daily rows (377 files in the 2023 zip). Only the daily files are read now, and one row is kept per interval and BAA.

**Gaps, all logged.**
- **SPP's SWPW:** some days are missing a few 5-minute intervals and are not written.
- **CAISO 2026 output:** it comes from the reports' 5-minute telemetry, which misses a few values on many days. So the 2026 monthly shares show "not computable".
- **ERCOT** has no complete month yet.

**`/curtailment`:**
- **Per ISO:** what the figure means, the last 90 days (chart and totals), the monthly history (chart) and a 13-month table.
- **Share of available output:** CAISO as curtailed over curtailed plus produced; ERCOT as below-HSL over HSL; none for SPP (no output in the ERW).
- **MISO and the rest:** MISO publishes nothing (its market reports list hourly wind output only). NYISO, ISO-NE and PJM were not checked; the page says so.

## Task 3: consumption by sector (tool 23)

**New tables:**
- **`eia_retail_sales_monthly`** (EIA-861M through `electricity/retail-sales`): sales in MWh (EIA's million kWh x 1000) and customers, by state and sector, 2001 to 2026-07, 228,203 rows.
- **`eia_sector_energy_consumption_monthly`** (MER tables 2.3 and 2.4, 14 series, TBtu, 8,974 rows). "EIA's monthly industrial consumption" is the MER's industrial sector, total and by source. The commercial series are there for the page's second table. `TBtu` joins the unit vocabulary (Decision 25).

**`/consumption`:**
- **US:** 4,089,342,191 MWh in 2025-08 to 2026-07, +1.2% on the 12 months before. Residential 37.0%, commercial 37.3% (+3.1%), industrial 25.6% (+0.3%).
- **Fastest-growing industrial sales** (states that sold at least 1 TWh to the sector a year earlier): New Mexico +12.6%, Arkansas +9.9%, Iowa +7.6%, Tennessee +6.8%, Arizona +6.6%.
- **Fastest-growing commercial sales:** Nebraska +17.7%, Ohio +16.2%, Indiana +13.3%, Arizona +10.7%, Wyoming +7.8%, Virginia +6.7%.
- **By state:** sector shares for every state, with "no data" where EIA left a month empty.
- **MER:** the industrial and commercial series, the latest 12 months against the 12 before.

## Task 4

**Validator and coverage.**
- All 95 tables in `warehouse/output` pass.
- Coverage is rebuilt with 95 tables; the new tables have sector rules.

**Live set.**
- **Added:** `state_generation_mix_monthly`, `eia930_generation_latest`, the three daily curtailment tables (last 100 days), `iso_curtailment_monthly`, `eia_retail_sales_monthly` (retail sales only, last 850 days) and `eia_sector_energy_consumption_monthly` (last 850 days).
- **Loaded:** 123,486 rows, all matching.
- **Redivis:** the curtailment tables are in the restore list, so CI merges into their history.

**Redivis.**
- **Why:** the daily run merges each day's rows into the curtailment tables, and CI starts without tables. The runner restores them from the Redivis draft.
- **Uploaded to the draft** (nothing released): `caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`, `iso_curtailment_monthly` and `state_generation_mix_monthly`, with the metadata tables. Every count matches.

**Keeping Supabase churn down.** The daily run re-reads EIA's whole generation history. Before this fix, every row of `state_generation_mix_monthly` would get a new `retrieved_at`, and the loader, which compares every column, would rewrite all 107,560 rows each day. That would leave as many dead row versions, near the size cap.
- **The fix:** a row whose value is unchanged now keeps the `retrieved_at` of the run that first wrote it. Locally, 107,560 of 107,560 rows kept theirs, so the table's hash is unchanged and the loader skips it.
- **For CI:** the table is in the Redivis restore list, so the runner has the previous copy to compare against.

**Briefing.** `package/llms.txt` describes the new tables and routes questions to them. It says the three ISOs' curtailment figures are not one measure, and that ERCOT's is output below HSL.

**Tools list.**
- `docs/platform-tools.md` has tools 21 (yes), 22 (partial) and 23 (yes), and updated rows for 3, 4 and 6.
- `CLAUDE.md` now says 23 tools.

**Value check.**
- **510 of 510 values match Supabase:** `/mix` 18 (two selections), `/curtailment` 58, `/consumption` 26, `/weekly` 20 of 20.
- **New check kind:** `series_esum`, a sum over one entity in a time range.
- **What the check caught:**
  - **`/curtailment`:** monthly and daily rows shared one lookup, so a daily row on the 1st overwrote the month's total (8 failures).
  - **`/consumption` and the `/mix` hourly chart:** they compared Supabase's `+00:00` times with `Z` bounds as strings, which dropped the first month of every window.
- Both were fixed and re-checked.

**Screenshots.** `mix-`, `curtailment-` and `consumption-` desktop and mobile (new), and `home-` (re-shot).

## Decisions

1. **The backfill keeps the old title test exactly** and adds only a prefilter that cannot change a decision. The bucket order decides which of two copies is kept.
2. **No full local Supabase load.** It would roll CI's newer price rows back. The tables this machine produced were loaded with `--only`, and CI loads the rest.
3. **Deleting from, or compacting, the shared database is left to a person** (the classifier's refusal). The scheduled run never prunes or vacuums.
4. **The mix explorer keeps ISOs and states apart**, rather than mapping states into ISO footprints that do not follow state lines.
5. **Supabase gets the grouped monthly mix, not the EIA source table**, to limit size.
6. **ERCOT's figure is named `below_hsl`**, and the page and briefing call it an estimate. ERCOT publishes no curtailment.
7. **A month or share is written only when every day or value it needs is present.** The 2026 CAISO shares wait for complete telemetry days rather than being computed from partial ones.
8. **The curtailment monthly table is `iso_curtailment_monthly`.** The validator requires three name parts.

## Errors hit

1. **The auto-mode classifier refused the Supabase cleanup** (Task 0, above).
2. **Heredoc quoting broke a patch again.** Patches went through files instead.
3. **CAISO workbook overlap, fall-back-day dedup, and SPP monthly files in the zips.** All fixed before the tables were kept (Task 2).
4. **Two page bugs caught by the value check** (Task 4).
5. **A 2025 claim I first wrote was wrong.** I said CAISO had no output for June to December 2025; the 2025 workbook covers the whole year. It was corrected in the connector header, the method doc and the briefing.

## Open questions for the human

1. **Urgent: run the Supabase cleanup.** The database is at 385.5 MB of the free tier's 500 MB. Run: `python warehouse/supabase/load.py --prune --vacuum-full`, from a machine with `SUPABASE_DB_URL`.
   - As is, it deletes the stale `epa.gov` source and compacts the tables.
   - To also drop the duplicated groups, first narrow `live_set.yaml`: the ERCOT yearly tables (whose last 90 days repeat the rolling tables, about 42,000 rows) and `eia860m_operating_generators` and `eia860m_planned_generators` (about 31,000 rows, in `energy_projects` too).
   - Then either keep `max_mb` at 300 or raise it; the free tier's hard cap is 500 MB. Until then, every load reports the size failure.
2. **Is the SPP share wanted?** It needs SPP's wind and solar output by BAA (SPP's generation mix files), not yet in the ERW.
3. **ERCOT history before 2026-09-19** needs ERCOT's registered public API (a key). Should the ERW register?
4. **NYISO, ISO-NE and PJM curtailment** were not checked. Are they wanted?
5. **Release a Redivis version** when you have reviewed the draft. It now holds the new curtailment and mix tables.
6. **NYISO's queue answered HTTP 202 in runs 4 and 5.** The map now goes ahead without it and says so, but NYISO's positions are missing from the Supabase copy until NYISO answers.
