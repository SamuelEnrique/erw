# ERW runbook: commands a person runs by hand

Energy Research Warehouse (ERW). The daily run is a GitHub Action (`.github/workflows/daily-prices.yml`, `warehouse/run_daily.sh`). This page holds the few things it cannot do itself, each as the exact commands to run from the repository root, in order. Started in session 29.

Before any of them:

```bash
git pull origin main
pip install -r requirements.txt   # once per machine; .env holds the keys (never committed)
```

After any of them, commit what changed under `warehouse/metadata/` (the upload and archive manifests) and push after merging origin/main (CLAUDE.md, non-negotiable 4).

## Known gaps refreshed from this machine

`warehouse/metadata/known_gaps.csv` lists the tables whose source refuses the GitHub runners. A table there does not close the health gate (`PRIORITIES.md`), but it goes stale unless someone refreshes it from a machine the source answers. Both below have answered GitHub with HTTP 202 and an empty body on every run since 2026-09-27, and download normally from a residential connection. Once a week is enough: CARB auctions are quarterly and the queues are weekly.

### CARB auction prices (`carb_auction_allowance_prices`, internal)

```bash
python warehouse/connectors/carbon_auctions.py --table carb
python warehouse/validate/erw_validate.py warehouse/output/carb_auction_allowance_prices.csv
python warehouse/archive/archive.py write --tables '^carb_auction_allowance_prices$'
python warehouse/redivis/upload.py carb_auction_allowance_prices
```

The table is internal: the upload goes to the private dataset `energy_research_warehouse_internal`, and it is not in the Supabase live set.

### NYISO interconnection queue (`nyiso_interconnection_queue`, public)

```bash
python warehouse/connectors/iso_queues.py nyiso
python warehouse/validate/erw_validate.py warehouse/output/nyiso_interconnection_queue.csv
python warehouse/archive/archive.py write --tables '^nyiso_interconnection_queue$'
python warehouse/supabase/load.py --only '^nyiso_interconnection_queue$'
python warehouse/redivis/upload.py nyiso_interconnection_queue
```

The queue stays its own table (session 29, `docs/migrations/2026-09-29-consolidation.md`): the six ISO queues are snapshots refreshed independently, and this one only from a local machine.

What each step does:

- **Validator.** Exit 0 or stop there.
- **Archive.** Appends the new rows to the durable archive, through the shared index in the bucket, so a local run and the GitHub runs never archive the same rows twice.
- **Upload.** Writes the Redivis draft only. Nothing is released.
## Session 30: the cost page and the shadow scorer

**The internal cost page, `/internal/costs`.**

- It answers 404 unless `?token=` equals the server's `INTERNAL_COSTS_TOKEN`.
- The database function behind it answers nothing unless the same token is in `erw_private.settings`.
- `python warehouse/supabase/apply.py` writes it there from `INTERNAL_COSTS_TOKEN` in `.env`.
- To turn the page on, set `INTERNAL_COSTS_TOKEN` in the Vercel project's environment (the value in `.env`, at least 24 characters) and redeploy.
- To change the token: a new value in `.env`, run `apply.py`, then set it on Vercel.

**The Haiku shadow scorer** (`warehouse/news/shadow.py`):

- **Stop it now:** delete the line `SHADOW_MODEL: claude-haiku-4-5` from `.github/workflows/daily-prices.yml` and `roundup.yml`.
- **It stops by itself** on the `expires` date in `warehouse/config/shadow.yaml`.
- **Recipients:** `SHADOW_RECIPIENT` (a repository secret, optional), else `DIGEST_RECIPIENTS`. Never subscribers.
- **Agreement with the published scores:** `python warehouse/news/shadow_agreement.py`.

**A local session and the two ledger-like tables.** `api_cost_ledger` and `news_scores_shadow` grow on GitHub and locally.

- Before a session's first model call, take the draft's copy, so the session adds to GitHub's rows rather than to an older local file. `--restore` downloads only a table missing locally, so move the local copy aside first:

  ```bash
  mv warehouse/output/api_cost_ledger.csv warehouse/output/api_cost_ledger.csv.bak
  mv warehouse/output/news_scores_shadow.csv warehouse/output/news_scores_shadow.csv.bak
  python warehouse/redivis/upload.py --restore
  ```

  The archive keeps every row either copy ever had.

- A session sets `ERW_SESSION=<n>` and `ERW_SPEND_CAP_USD=<cap>`, so its calls are its own rows and stop at its cap.

## Session 29: removing the migrated tables from Redivis

After the consolidation (`docs/migrations/2026-09-29-consolidation.md`), the old tables stay in both Redivis datasets until a person removes them. The command checks every family first and removes nothing if any count disagrees:

```bash
python warehouse/redivis/upload.py --remove-migrated --dry-run   # what it would remove, and the counts
python warehouse/redivis/upload.py --remove-migrated
```

For each of the six families it checks, in the draft, that the consolidated table holds its old tables' rows:

- either its `count(*)` equals the sum of the old tables' counts;
- or, once the daily run has added days to it, every old row's key is in it (one join per old table).

On any mismatch it removes nothing and says which family failed. It removes only the old tables and prints each one. The manifest (`warehouse/metadata/redivis_uploads.csv`) keeps their lines, marked `migrated_to`, so the history gate keeps their counts.

## Supabase: compacting the database

`warehouse/supabase/load.py` runs a plain `VACUUM (ANALYZE)` on the shape tables after every load and prints their size before and after (session 29; from session 29 to session 44 the code in fact ran `VACUUM (FULL, ANALYZE)`, and in daily run 12 it held the tables for about ten minutes, so session 45 made the plain vacuum the default). A plain vacuum takes no exclusive lock: the space of the rows a load replaced is marked for reuse by the next loads, but `pg_database_size` does not shrink. Only `VACUUM FULL` returns space to the operating system, and it locks each table while it rewrites it (seconds to minutes; the site's reads wait or time out meanwhile), so it stays a person's command, run when the site is quiet:

```bash
python warehouse/supabase/load.py --vacuum-full
```

The loader still warns above `warn_mb` (350 MB) and fails above `max_mb` in `warehouse/supabase/live_set.yaml`. When the warning shows and does not clear, run the command above once, or trim a live window.

**The weekly vacuum (session 49, approved by Samuel).** `.github/workflows/weekly-vacuum.yml` runs `warehouse/supabase/vacuum.py` every Sunday at 10:00 UTC:

- **What it does:** `VACUUM (FULL, ANALYZE)` of the six shape tables, with no load.
- **What it records:** `pg_database_size` before and after, and each table's size, in `warehouse/metadata/run_status.csv` (connector `supabase_vacuum`; the table `supabase` holds the database's two sizes). The workflow commits that file.
- **When:** in the daily run's concurrency group, so it never runs during a daily load, and four hours before the daily run's 14:00 UTC start. The site's reads may wait or time out while `series` is rewritten, a few minutes on a Sunday morning.
- **Run it now:** Actions, "weekly vacuum", Run workflow; or locally, with `SUPABASE_DB_URL` in `.env`: `python warehouse/supabase/vacuum.py` (no load, unlike `load.py --vacuum-full`).
- **Stop it:** delete the `schedule` lines of the workflow.
