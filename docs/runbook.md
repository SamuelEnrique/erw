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

`warehouse/supabase/load.py` runs a plain `VACUUM (ANALYZE)` on the shape tables after every load and prints their size before and after (session 29). Only `VACUUM FULL` returns space to the operating system, and it locks each table for seconds, so it stays a person's command:

```bash
python warehouse/supabase/load.py --vacuum-full
```
