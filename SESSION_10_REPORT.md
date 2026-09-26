# Session 10 report

Energy Research Warehouse (ERW), session 10, run 2026-09-26 (UTC). The human rulings were applied:
1. Redivis is the store of record for every table, and Supabase's free tier holds only a small live set.
2. Back up first.
3. Derived scripts skip with a warning in CI, and the workflow keeps committing `news_stories.csv`.

Every task was carried out except where a key was missing, as the session rules require. **The Supabase migrations could not be applied, so nothing was loaded into Supabase.** The reason is below. Nothing was pushed. No key was printed or committed: tokens are read from `.env` and passed only to their clients, and a search of new files and logs for key fragments found none.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | Backup of `warehouse/output`, verified. Ruling (3) applied in `ercot_peak_premium.py`, `run_daily.sh` and the workflow | `40eae34`, `6eb0326` |
| 2 | Redivis uploader (`warehouse/redivis/`). Every table was uploaded to the draft of `energy_research_warehouse`, and all **83 of 83 tables reconcile** (3,725,119 rows). The daily run uploads the tables it changed; CI restores the rolling windows first | `ad2d7a1` |
| 3 | Supabase migrations, live set, loader and RLS. **Not applied, not loaded: the key needed for DDL is missing** | `552b228`, `da1626f` |
| 4 | `latest_prices.py` and the 15-minute workflow. Four local runs: 39 of 39 hubs and zones from six ISOs. The Supabase upsert failed (no table), so the rows are in the local mirror | `702c6d2` |
| 5 | `RedivisBackend` and `SupabaseBackend` behind `ERW_BACKEND`. Redivis matches the local backend on all five tables; the Supabase tests skip with the reason | see git log |
| 6 | This report | final commit |

## Task 1: backup and the CI rulings

**Backup** (`C:\Users\samen\Documents\erw-backups\output-2026-09-25.zip`, outside the repository):

| Files | CSV tables | Source bytes | Zip bytes |
|---|---|---|---|
| 165 | 81 | 997,445,296 | 26,692,300 |

Verified three ways: `testzip` (every member's CRC), the member list equal to the files on disk, and the SHA-256 of every decompressed member equal to its file. It is recorded in `warehouse/output/README.md`. The CSVs compress about 37 to 1, because they repeat long source URLs and codes.

**Ruling 3:**
- In CI (`GITHUB_ACTIONS=true`), `ercot_peak_premium.py` checks for its 13 input tables. Without them it prints a `::warning::`, records status `skipped` (which never counts toward a 3-run failure streak), writes nothing and exits 0.
- Outside CI, missing inputs still fail (tested: exit 1).
- `run_daily.sh` records "skipped" lines.
- The workflow commits `warehouse/output/news_stories.csv` again, so CI does not re-ingest and re-score stories.

## Task 2: Redivis, the store of record

- **Where:** `warehouse/redivis/config.yaml` is the one place that names the owner (`REDIVIS_OWNER`, a Redivis *user* account, so `redivis.user`) and the dataset. `upload.py` follows the IRW's `red_up`.
- **Upload steps:**
  - the validator gate;
  - the provenance header out of the rows and into the table description, with the license;
  - a true replace (delete, then recreate);
  - a `count(*)` proof;
  - never a release.
- **Metadata tables:** `erw_coverage`, `erw_sources`, and `erw_headers` (every header line of every table in full).
- **Description limit:** Redivis caps a description at 2,000 characters. The first run failed on 14 tables whose headers are longer; descriptions are now cut with a pointer to `erw_headers`.
- **Line breaks in cells:** two queue tables failed on quoted line breaks in text fields; quoted newlines are now allowed for every table.
- **Result:** 17 tables failed on the first pass for these two reasons. All 17 were re-uploaded and then matched.

**Reconciliation** (`python warehouse/redivis/upload.py --reconcile`, a `count(*)` of every draft table against its CSV):

| Tables | Match | Mismatch | Rows in the CSVs | Rows on Redivis |
|---|---|---|---|---|
| 83 (81 ERW tables, `erw_coverage`, `erw_sources`) | 83 | 0 | 3,725,119 | 3,725,119 |

`erw_headers` holds 903 header lines. The dataset stays an **unreleased draft**. `warehouse/redivis/README.md` says how a human releases a version, how to cite it, and that nothing releases without a human.

**Daily run.** The last step of `run_daily.sh` (and so of the workflow) is `upload.py --changed`. It uploads only tables whose data rows' SHA-256 differs from `warehouse/metadata/redivis_uploads.csv`, which is tracked and committed by the workflow. After the full upload, `--changed` finds 0 tables.

**A problem the prompt did not name, and its fix.** Since session 9 the CI runner starts without the tables. Its ISO tables hold only the 3 days it just fetched. Uploading those as "changed" would replace the 30-day tables in the store of record with 3-day ones.
- **Fix:** with `RESTORE_FROM_REDIVIS=1` (set by the workflow), `run_daily.sh` first downloads the rolling-window tables from the draft: the ISO price tables and EIA-930, the tables the connectors merge into.
- **Formatting:** Redivis infers types on upload (`ts_utc` becomes dateTime, `value` becomes float), so the restore writes them back in the ERW's text form.
- **Tested:** `ercot_rtm_hub_prices` (17,280 rows) and `eia930_erco_demand` came back equal to the local files in every column.
- A failed restore stops the run, so a partial window is never uploaded.

## Task 3: Supabase live set (built, not applied)

**Why it was skipped.** The migrations are DDL (`create table`, `create policy`). Supabase runs DDL only over a Postgres connection or through its Management API. `SUPABASE_SERVICE_KEY` is a PostgREST key: it can read and write rows in tables that exist, but it cannot run SQL. I checked the project's REST schema: it exposes only one function, Supabase's own `rls_auto_enable` helper, and the `/pg` paths return 404. `.env` holds neither `SUPABASE_DB_URL` nor `SUPABASE_ACCESS_TOKEN`. So `apply.py` stops with exit 1 and applies nothing; `load.py` stops before writing anything; and the Supabase reconciliation and `pg_database_size` could not be measured.

**What is ready:**
- **`migrations/001_shapes.sql`:**
  - `series`, `entities` and `events`: the standard columns, plus `table_name`, `license` and `loaded_at`. Entities and events keep their other fields in `extra` (jsonb).
  - `latest_prices`, keyed by `entity, variable`.
  - `catalogue` (`coverage.csv` plus `in_live_set`), `sources`, and `headers`.
  - `erw_db_size()`, callable by the service role only.
- **`migrations/002_rls.sql`:** RLS on every table. `anon` and `authenticated` may select only `license = 'public'`. There are no write policies; the service role bypasses RLS.
- **`live_set.yaml`:** as the prompt defines it, with a 300 MB limit.
- **`load.py`:**
  - upserts in batches of 1,000;
  - deletes each table's rows that the run did not write (by `loaded_at`), so 90-day windows roll and a retired generator leaves;
  - reconciles `count(*)` per table against the filtered CSV;
  - writes `runs/supabase_reconcile.csv`;
  - fails over 300 MB.
- **Pipeline:** `run_daily.sh` runs the load after the validator and coverage.

**Dry run** (`load.py --dry-run`, no network): the live set is **66 tables, 331,850 rows**. 14 tables load whole; 52 load their last 90 days, including the 24 ERCOT yearly history tables, of which only 2026 has rows in the window.

| Part | Rows |
|---|---|
| Whole: 2 peak-premium tables | 25,704 |
| Whole: `news_index` | 714 |
| Whole: 3 EIA-860M and 6 queue tables | 45,737 |
| Whole: `eia_fuel_spot_prices`, `fred_daily_spot_prices` | 51,993 |
| Last 90 days: ISO price tables (including ERCOT 2026 history) | about 140,000 |
| Last 90 days: EIA-930 | about 68,000 |

**Supabase size:** not measured, because nothing could be loaded. It is guarded at 300 MB by `load.py` once the migrations are applied.

## Task 4: the latest-prices loop

- `warehouse/connectors/latest_prices.py` takes the newest real-time interval per hub or zone already in the ERW, using gridstatus's "latest" methods:
  - `Ercot.get_spp`;
  - `get_lmp` for CAISO, NYISO, MISO and ISO-NE;
  - `get_lmp_real_time_5_min_by_location` for SPP;
  all with `date="latest"`.
- Variables: ERCOT `spp_rtm` (its 15-minute settlement interval); the others `lmp_rtm_5min`. That is a distinct variable from the 15-minute means and hourly prices in the ERW tables.
- No completeness rule: a missing ISO is logged and skipped.
- `.github/workflows/latest-prices.yml` runs only this script, every 15 minutes.

Four local runs (three required, plus one later, to show the intervals advancing). Every run returned all 39 of 39 hubs and zones: ERCOT 6, CAISO 3, NYISO 11, MISO 8, SPP 2, ISO-NE 9. The upsert failed each time with `Could not find the table 'public.latest_prices'` (Task 3). The rows went to the local mirror `runs/latest_prices.csv`, which keeps one row per entity with its newest interval. After the fourth run:

| ISO | Entities | Newest interval (UTC) | Example |
|---|---|---|---|
| ERCOT | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 2026-09-26 04:00 | HB_HUBAVG 31.19 USD/MWh |
| CAISO | TH_NP15, TH_SP15, TH_ZP26 | 2026-09-26 04:30 | TH_SP15 36.24 |
| NYISO | 11 zones | 2026-09-26 04:25 | N.Y.C. |
| MISO | 8 hubs | 2026-09-26 04:25 | |
| SPP | SPPNORTH_HUB, SPPSOUTH_HUB | 2026-09-26 04:25 | |
| ISO-NE | .H.INTERNAL_HUB and 8 zones | 2026-09-26 04:25 | |

Between the first three runs (04:23 to 04:24 UTC) and the fourth (04:29), CAISO moved from 04:25 to 04:30 and NYISO, MISO, SPP and ISO-NE from 04:20 to 04:25. ERCOT's next 15-minute interval had not posted yet.

## Task 5: package backends

- **`erw.RedivisBackend`** reads the draft, all tables. It needs `REDIVIS_API_TOKEN` and `REDIVIS_OWNER`. Headers come from `erw_headers`, coverage from `erw_coverage` and sources from `erw_sources`. Values are written back in the ERW's text form using the variable types Redivis reports.
- **`erw.SupabaseBackend`** reads the live set: `SUPABASE_URL` with `SUPABASE_SERVICE_KEY`, or with `SUPABASE_ANON_KEY` and `ERW_SUPABASE_ROLE=anon` for public rows only.
- `ERW_BACKEND=local|redivis|supabase` selects one for `erw.set_backend()`. The code is in `package/src/erw/remote.py`, with optional extras `erw[redivis]` and `erw[supabase]`.

**Tests** (`package/tests/test_backends.py`) cover five tables: `ercot_peak_premium_annual` (derived), `eia860m_retired_generators` (entities), `news_index` (events), `eia_fuel_spot_prices` and `fred_daily_spot_prices`. They check `fetch` (every column and the header), `coverage`, `sources`, `cite` (identical up to the closing words, which name the data version) and five `filter` queries against the local backend.
- **Redivis:** 16 passed.
- **Supabase:** 16 skipped, with the reason "Could not find the table 'public.catalogue'". The backend is written but untested against a live database until the migrations are applied.
- The existing package suite still passes: 357 package tests, plus 11 repo tests. After a speed fix to `RedivisBackend` (it reads variable types from `list_variables()` instead of one call per column), the 11 Redivis fetch, coverage and sources comparisons were rerun and pass, in 34 seconds.

## What the public site reads

| Data | From | Key | Notes |
|---|---|---|---|
| Latest prices board (every 15 minutes) | Supabase `latest_prices` | `SUPABASE_ANON_KEY` | RLS shows public rows only (every ISO except PJM) |
| Recent prices and demand (90 days), peak premium, fuel spot prices, news index, generator and queue maps | Supabase `series`, `entities`, `events` | `SUPABASE_ANON_KEY` | only `license = 'public'` rows are visible; internal tables are not in the live set at all |
| Table list, coverage, citations, provenance | Supabase `catalogue`, `sources`, `headers` | `SUPABASE_ANON_KEY` | public rows only |
| Full history and every other table (ERCOT since 2015, full EIA series, capacity, carbon, PortWatch) | Redivis `energy_research_warehouse`, a **released** version | a Redivis API token for server-side reads, or Redivis's own public data pages | the site never reads the draft; internal tables stay in Redivis for internal use and are not shown |

Never in a browser: `SUPABASE_SERVICE_KEY`, which bypasses RLS, and `REDIVIS_API_TOKEN`. They are for `load.py`, `latest_prices.py`, `upload.py` and the scheduled workflows only. Until the migrations are applied, the Supabase rows of this table describe the design, not a running database.

## Decisions

1. **Restore before merge in CI** (Task 2, above). Without it, the daily upload would shrink the store of record.
2. **Descriptions and headers.** Redivis caps descriptions at 2,000 characters, so the full header of every table lives in `erw_headers` on Redivis and in `headers` on Supabase.
3. **Types on Redivis are inferred.** Redivis takes an explicit schema only for streaming uploads. Values are converted back to the ERW's text form on restore and in the backend, so the fetch results equal the local ones.
4. **Supabase keeps non-standard fields in `extra` (jsonb)**, so three shape tables hold every table's own columns.
5. **`loaded_at` and a delete of older rows** make the live set a snapshot of the current ERW tables, not an accumulation.
6. **`latest_prices` uses its own variables** (`lmp_rtm_5min`; ERCOT `spp_rtm`). A single newest 5-minute price is not a 15-minute mean, and is labeled so.
7. **`ARCHITECTURE.md`** now describes the uploader and the live set as built.

## Errors hit

1. Redivis rejected an explicit schema for file uploads and an empty null-marker list. Types are inferred instead, with `null_markers=[""]`.
2. On the first full upload, 17 tables failed: 14 on the 2,000-character description limit, 1 on a 2,007-character description, and 2 on quoted line breaks in queue tables. All were fixed and re-uploaded, and all matched.
3. **A heredoc patch broke `warehouse/supabase/load.py`:** `"\r\n"` became a real line break, and it was committed in `552b228`. It was caught by the dry run and fixed in `da1626f`; every new Python file was then checked for syntax.
4. **A heredoc edit to `warehouse/output/README.md`** failed on Windows backslashes, and the Task 1 commit went in without it. It was added in `6eb0326`.

## Rerun

```bash
python warehouse/redivis/upload.py --changed      # or --all, --reconcile, --restore
python warehouse/supabase/apply.py                # needs SUPABASE_DB_URL or SUPABASE_ACCESS_TOKEN
python warehouse/supabase/load.py                 # --dry-run to see the live set
python warehouse/connectors/latest_prices.py
ERW_BACKEND=redivis python -m pytest package/tests/test_backends.py -v
```

## Open questions for the human

1. **Add `SUPABASE_DB_URL`** (dashboard, Connect, Session pooler URI with the database password) **or `SUPABASE_ACCESS_TOKEN`** to `.env` and as repository secrets. Then run `apply.py` and `load.py`. Until then, the daily `supabase_load` step fails, and after three scheduled runs it will open a streak issue.
2. **Release the first Redivis version** once you have reviewed the draft (`warehouse/redivis/README.md`).
3. **Add the repository secrets** the workflows now read: `REDIVIS_API_TOKEN`, `REDIVIS_OWNER`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (plus, carried over, `EIA_API_KEY`, `ANTHROPIC_API_KEY`).
4. **The 15-minute workflow runs about 2,900 times a month.** Each run bills at least one minute and likely two, with the dependency install, so it uses about 3,000 to 6,000 GitHub Actions minutes a month. That is free for a public repository, and over the free allowance for a private one. Is the repository public?
