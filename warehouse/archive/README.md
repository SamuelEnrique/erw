# warehouse/archive: the append-only durable store

Session 28, from Ben Domingue's review (item 1, `docs/feedback/ben-2026-09-28.md`). The tables in `warehouse/output` and the Redivis draft are a working store: the daily run rewrites them. This folder, and its copy in the private Supabase storage bucket `erw-archive`, keeps every version of every row where no rewrite reaches it.

| Path | What it is | Rewritten? |
|---|---|---|
| `<table>/<YYYY-MM>.csv` | The rows a run found new or changed, and the keys it found gone, in the month of the run (UTC) | Never. Runs only append |
| `_runs/<YYYY-MM>.csv` | One line per table and run: rows added, keys deleted, the table's row count, data SHA-256, columns and its full provenance header | Never. Runs only append |
| `_state/<table>.npz` | The index of row hashes that decides "new or changed" | Yes: it is an index, not the archive. `restore.py` rebuilds it from the archive |

In the bucket, each run's lines are one object, `<table>/<YYYY-MM>/<run_id>.csv.gz` (and `_runs/<YYYY-MM>/<run_id>.csv.gz`). An object is written once, and the upload refuses a name that exists. The month files and run logs are not in git; the bucket is the durable copy.

## Commands

```bash
python warehouse/archive/archive.py write            # the daily step (run_daily.sh, after coverage)
python warehouse/archive/archive.py pull             # bring in the runs other machines archived (append only)
python warehouse/archive/archive.py sync             # upload local runs the bucket lacks
python warehouse/archive/archive.py status           # month files, parts and sizes
python warehouse/archive/restore.py TABLE            # rebuild TABLE as of the latest run
python warehouse/archive/restore.py TABLE --as-of 2026-09-28T23:00:00Z --from-bucket
python warehouse/archive/restore.py --all --check --no-write   # every table against warehouse/output
```

`restore.py` writes to `runs/archive_restore/` unless `--out` names a path. It replaces a file in `warehouse/output` only when `--out` names that file.

## Rules

- **What is compared.** A row is archived when its hash was never archived, or when its key is not in the table as last archived (a row that comes back). Keys: `(entity, variable, ts_utc)` for series, `event_id` for events, `entity_id` for entities (`docs/datastandard.md`). Values are compared as a Redivis restore writes them (12 and 12.0 are equal), so a restored table is not archived again for formatting alone.
- **Deletes.** A key that has disappeared is written as a delete line, except in the rolling-window tables (`restore_before_run` in `warehouse/redivis/config.yaml`), which only merge: there, a missing key means a stale copy, not a deletion.
- **Order in the daily run.** The archive step runs before the Supabase load and the Redivis upload. If it fails, the Redivis upload is skipped that day.
- **Two writers.** GitHub runs and local runs both write to the bucket. The index in the bucket is the shared one. A local machine runs `pull` to see the GitHub runs in its month files.
- **Credentials.** `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` (the bucket is private). Never printed.

Tests: `tests/test_archive.py`.
