# warehouse/supabase: the live set

Session 10 ruling: Supabase's free tier holds **only a small live set**, well under its 500 MB cap. Redivis holds every table (`warehouse/redivis/README.md`). This database is derived from the ERW tables: it is rebuilt from them, and never edited by hand.

## Tables

| Table | Holds | Key |
|---|---|---|
| `series` | series-shape rows of the live set: the standard columns, plus `table_name` and `license` | `table_name, entity, variable, ts_utc` |
| `entities` | entities-shape rows: standard columns, plus `extra` (jsonb: the source's own fields such as `eia_status`, `iso_status`, `queue_id`) | `table_name, entity_id` |
| `events` | events-shape rows (`news_index`): standard columns, plus `extra` (headline, sector, significance, ...) | `table_name, event_id` |
| `latest_prices` | the newest real-time price per ISO hub and zone, every 15 minutes (`warehouse/connectors/latest_prices.py`) | `entity, variable` |
| `catalogue` | `coverage.csv`: one row per ERW table, including tables not in the live set (`in_live_set`), and for live-set tables `columns`, the table's own columns in CSV order (migration 003) | `table_name` |
| `sources` | `sources.csv`: the report behind every source id, for citations | `source` |

Schema: `migrations/001_shapes.sql`, `migrations/003_columns.sql` and `migrations/004_rows_sha256.sql`. Row-level security: `migrations/002_rls.sql`.

## The live set

`live_set.yaml` decides what goes in:
- **Whole:** the two derived peak-premium tables, `news_index`, the EIA-860M and interconnection-queue entities tables, `eia_fuel_spot_prices` and `fred_daily_spot_prices`.
- **Last 90 days only:** every ISO price table (including the ERCOT yearly history, which contributes its last 90 days) and every EIA-930 table.

`load.py` reads the rows Supabase already holds for each table, compares them column by column with the selected CSV rows, and writes only the difference: it upserts rows that are new or changed, and deletes rows the selection no longer has, so the window rolls and a generator that left EIA's inventory leaves here too. It then reconciles `count(*)` per table against the filtered CSV and reads `pg_database_size` (function `erw_db_size`). It fails if the database is over `max_mb` in `live_set.yaml` (300 MB until session 19, 400 MB since).

Unchanged tables are skipped (session 13): the loader hashes each table's selected rows (SHA-256 of its license and the rows as CSV) and compares the hash with `catalogue.rows_sha256`, stored by the last successful load of that table. An unchanged table is not read back or written; its `count(*)` is still reconciled. A table whose load fails gets a null hash, so the next run loads it in full.

Why only the difference (session 11): the session 10 loader upserted every row on every run. Postgres keeps the old version of an updated row until a vacuum, so each full rewrite added the size of the live set again. The first load measured 219.4 MB; a second full load (needed once, to fill `catalogue.columns`) took it to 339.3 MB. The incremental loader then wrote 2 rows and deleted 12. The space already taken is not returned by autovacuum; see "Reclaiming space" below.

## Row-level security

RLS is enabled on every table. There is one policy per table: `select` for `anon` and `authenticated`, restricted to rows where `license = 'public'`. There are no insert, update or delete policies.

| Reader | Key | Sees |
|---|---|---|
| The public site, anyone | `SUPABASE_ANON_KEY` | public rows only. Internal rows (PJM, CARB, RGGI, FRED IMF, PortWatch, `news_stories`) are invisible, even by `table_name` |
| `load.py`, `latest_prices.py`, `erw` with the service key | `SUPABASE_SERVICE_KEY` | everything (the service role bypasses RLS); used only on the server and in CI, never in a browser |

## Applying the migrations

The migrations are DDL. Supabase runs DDL only over a Postgres connection or through its Management API; the service key (a PostgREST key) cannot. `apply.py` needs one of:
- `SUPABASE_DB_URL`: the Postgres connection string, from the dashboard, Connect, "Session pooler", with the database password;
- `SUPABASE_ACCESS_TOKEN`: a personal access token for the Management API.

Put it in `.env` (never in git) and run:

```bash
python warehouse/supabase/apply.py      # idempotent: create if not exists, drop policy if exists
python warehouse/supabase/load.py       # load, reconcile, size check
python warehouse/supabase/load.py --dry-run   # what would be loaded, no network
```

### A record of the migrations applied by hand

A migration beyond the live set's own (the site's tables and functions: the game, the subscribers, the ledger, the Thesis Builder, the analysis queue) is applied by a person with `apply.py --only <number>`, and the session that applies it records it here and in the session report. Two migrations with one number collide in `--only`, so a session that finds two renumbers the later one before applying either (session 172: `026_analysis_requests.sql` of session 170 became `027_analysis_requests.sql`; session 169's `026_thesis_gate.sql` kept its number).

| Migration | What it adds | Applied | By |
|---|---|---|---|
| `024_thesis.sql` | `thesis_runs`, `thesis_submit`, `thesis_list`, `thesis_get`, `thesis_token_ok`, `thesis_pitchbook_accept` | before 10 October 2026 (the functions were in the project when session 172 read it) | the owner |
| `025_thesis_providers.sql` | `thesis_provider_results`, `thesis_provider_accept`, `thesis_provider_results` | before 10 October 2026 (the same reading) | the owner |
| `026_thesis_gate.sql` | `thesis_runs.gate`, `thesis_submit_forced`, the step `site_thesis_gate` in the ledger's check | 10 October 2026, about 02:05 UTC (`runs/session172/apply_026.out`) | session 172 (the chain prompt of 9 October, part B) |
| `027_analysis_requests.sql` | `analysis_requests`, `analysis_request`, `analysis_requests_list` | 10 October 2026, about 02:05 UTC (`runs/session172/apply_027.out`), from branch `wip/170-analysis` before its landing | session 172 (the same) |
| `028_security_usage.sql` | row-level security asserted on every table (no change where it holds); `site_rate_counts` and `site_rate_admit` (limits per visitor across instances); `site_usage_events`, `site_usage_daily`, `site_usage_salt`, `site_usage_record`, `internal_usage` (the usage counts); three helpers in `erw_private`. Rollback: `rollbacks/028_security_usage.sql` (`apply.py --rollback 028`) | 10 October 2026, 10:37:56 UTC, by the chain's coordinator at session 177's landing (`apply.py --only 028`, exit 0; `verify_rls.py --catalog`: PASS, 0 mismatches, 23 tables with row-level security on); session 177 wrote it and tried it in a transaction it rolled back (`runs/session177/sql_trial.out`) | |
| `029_scanner_drafts.sql` | `scanner_drafts` (the scanner's review list: internal, row-level security on, no privilege for the anon key), `scanner_drafts_list`, `scanner_draft_set_state`, and `analysis_request_card` (one request of `analysis_requests` with its card; a read). Rollback: `rollbacks/029_scanner_drafts.sql` (`apply.py --rollback 029`): the drafts and their rulings go with the table; migration 027's table is not touched. Tried in one rolled-back transaction on 10 October 2026 (`runs/session181/sql_trial.out`) | 10 October 2026, 18:01:09 UTC, by the chain's coordinator at session 181's landing (`apply.py --only 029`, exit 0; `verify_rls.py --catalog`: PASS, 0 mismatches, 24 tables with row-level security on, `scanner_drafts` blocked); the first run's 8 drafts loaded at 18:02 UTC | session 181 (written), the coordinator (applied) |

### Who reads what with the anon key (session 177)

`verify_rls.py` holds the list and proves it: it asks one row of each table with the anon key, exactly as a visitor could, and fails on any difference. Public (the site, the `erw` package and `check-values` read them): `series`, `entities`, `events`, `latest_prices`, `catalogue`, `sources`, `headers` (rows whose license is public) and `game_scores`. Every other table is internal: no select policy and no select privilege. A table added by a later migration must be added to the list in `verify_rls.py`, as public or blocked, or `verify_rls.py --catalog` fails.

```bash
python warehouse/supabase/verify_rls.py --catalog      # exit 0: every table answers as the list says, and one internal read is refused
```

In session 10, `.env` held neither of the two, so the migrations were not applied and nothing was loaded. In session 11, with `SUPABASE_DB_URL` in `.env`, all three migrations were applied and the live set loaded: 66 tables and the catalogue and sources, every count matching the filtered CSVs (`archive/sessions/SESSION_11_REPORT.md`).

## Reclaiming space (a human, once)

After session 11 the database is 339 MB, over `load.py`'s 300 MB guard, because of the dead row versions left by the two full loads. Until the space is reclaimed, `load.py` still loads and reconciles every table but exits 1 at the size check. `VACUUM FULL` rewrites each table without the dead versions. It takes a lock on each table for a few seconds and is not run by any script here. In the Supabase dashboard, SQL editor:

```sql
vacuum full analyze public.series;
vacuum full analyze public.entities;
vacuum full analyze public.events;
vacuum full analyze public.headers;
vacuum full analyze public.catalogue;
vacuum full analyze public.sources;
vacuum full analyze public.latest_prices;
```

Then `python warehouse/supabase/load.py` should report about 220 MB and exit 0.
