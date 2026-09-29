# warehouse/redivis: the store of record

Session 10 ruling: **Redivis, Stanford-owned and free, is the store of record for every ERW table**, updated daily. The dataset is `energy_research_warehouse`, owned by the Redivis account named in `.env` as `REDIVIS_OWNER`. `config.yaml` is the only file that names them; every script reads it.

## The rule: nothing releases without a human

`upload.py` only ever writes the dataset's **unreleased draft** (version `next`). No script, workflow or scheduled job in this repository releases a version, and none may. Releasing is a human click on Redivis, after reading what the draft changes. Until a version is released, an upload has not happened for anyone reading the dataset: a matching row count proves the draft, nothing else. (Modeled on the IRW's `red_up`: `ARCHITECTURE.md` section 1 and the IRW's `ARCHITECTURE.md` section 4.)

## What the uploader does

Every run takes these steps:
- **Gate:** the validator must pass for a table, or it is not uploaded.
- **Header:** the provenance header (the leading `#` lines of the CSV) is not uploaded as rows. It becomes the table's description, with its license from `coverage.csv`. Redivis caps a description at 2,000 characters, so a longer header is cut with a note, and every header line of every table is also stored in full in the table `erw_headers` (`table`, `line_no`, `line`).
- **True replace:** Redivis uploads append, so an existing draft table is deleted and recreated before its upload (the IRW's `red_up` finding: otherwise rows inherited from a released version double the table).
- **Proof:** `select count(*)` on the draft table must equal the CSV's data rows.
- **Metadata:** two more tables, `erw_coverage` (`warehouse/metadata/coverage.csv`) and `erw_sources` (`warehouse/metadata/sources.csv`).
- **Types:** Redivis infers column types (`ts_utc` and `retrieved_at` as dateTime in UTC, `value` as float). It takes an explicit schema only for streaming uploads.

```bash
python warehouse/redivis/upload.py --all          # every table, plus erw_headers, erw_coverage, erw_sources
python warehouse/redivis/upload.py --changed      # only tables whose data changed since their last upload (run_daily.sh)
python warehouse/redivis/upload.py --reconcile    # count(*) of every draft table against its CSV
python warehouse/redivis/upload.py --restore      # download the rolling-window tables missing locally (CI)
```

**Changed tables** are found by comparing the SHA-256 of each table's data rows with `warehouse/metadata/redivis_uploads.csv`, which each upload rewrites and the workflow commits.

**Restore.** The CI runner has no tables (they are not in git). So before the connectors run, the daily workflow restores the rolling-window tables (`restore_before_run` in `config.yaml`: the ISO price tables and EIA-930) from the draft, and the connectors merge into the full tables. Without this, a 3-day window would be uploaded over the 30-day table. A failed restore stops the run. A restored table equals the original file row for row, and was tested on `ercot_rtm_hub_prices` and `eia930_erco_demand`.

**History gates (session 28, from Ben Domingue's review).** The draft holds the rolling-window tables' history, so three gates stop that history from being lost without a failure:

- **Restore fails on a missing table.** `--restore` fails when a table that `redivis_uploads.csv` lists, and `restore_before_run` matches, is absent from the draft. It also fails when the draft holds fewer rows than the manifest last recorded. A failed restore stops the daily run.
- **Upload refuses to shrink.** An upload refuses to shrink a rolling-window table below the row count the manifest last recorded, before the draft table is deleted. To shrink one on purpose, name it: `upload.py TABLE --allow-shrink TABLE`.
- **Existence is read from metadata.** A table exists when fetching its metadata succeeds. `list_tables()` alone is never trusted (in the IRW it under-reported a large dataset by about half), and an error other than a 404 fails the check instead of reading as "absent".

Tests: `tests/test_redivis_gates.py`, against a mocked client.

**Two datasets, routed by license (session 28, review item 3).** Redivis sets access per dataset, not per table.

- **Routing:** a table whose license in `warehouse/metadata/coverage.csv` is `public` goes to `energy_research_warehouse`. Every other table goes to `energy_research_warehouse_internal`, a private dataset (no public access) under the same owner. `push()` refuses a non-public license for the public dataset, whatever the caller asked.
- **Metadata:** each dataset gets the provenance header lines of its own tables only (`erw_headers`). `erw_coverage` and `erw_sources` go to the public dataset.
- **Restore and reconcile** read each table from its own dataset.
- **The check:** `upload.py --check-license` fails when any internal table is in the public dataset, checked by metadata table by table, not by `list_tables()` alone. It also fails when any table there is not a public table in `coverage.csv`, or when the internal dataset has any public access. `run_daily.sh` runs it after every upload and fails the run on it.
- **Creating the dataset and moving tables is a human's job:** `python warehouse/redivis/upload.py --check-license --fix`. It creates the private dataset if needed, uploads each internal table found in the public draft, confirms its `count(*)` there, and only then deletes it from the public draft. A scheduled run never creates a dataset; until the internal dataset exists, uploads of internal tables fail and are named in the run.

## How to release a version (a human, on Redivis)

1. Check the draft first. Every table must match: `python warehouse/redivis/upload.py --reconcile` compares `count(*)` for each table with its CSV and writes `runs/redivis_reconcile.csv`.
2. Open the dataset on redivis.com, signed in as the owner, and switch to the draft version (`next`).
3. Review what the draft changes against the last release, table by table. In the IRW's words, look for a *wrong* answer, not only an incomplete one: a table whose rows doubled, a window that shrank, a license that changed.
4. Click **Release**, and give the version a note naming the ERW commit (`git rev-parse HEAD`) and the date of the daily run it holds.
5. After a release, the next upload opens a new draft by itself (`create_next_version(if_not_exists=True)`).

Batching is fine: the draft can collect several days of daily uploads before a human releases it. The exception is a released table that gives a wrong answer: release its fix as soon as the fix lands (`ARCHITECTURE.md`).

## How to cite it

Cite the organization that published the data, then the ERW table and the Redivis version you read. For example:

> Electric Reliability Council of Texas (ERCOT). NP6-785-ER: Historical RTM Load Zone and Hub Prices. Via the Energy Research Warehouse (ERW), table `ercot_rtm_hub_prices_2025`, Redivis dataset `energy_research_warehouse`, version vN (released YYYY-MM-DD).

`erw.cite("<table>")` writes the first part from the table's provenance. The version is the released Redivis version you read; the draft has no version number and is not citable. Each table's license is in its description and in `erw_coverage`. A table marked `internal` (PJM, CARB, RGGI, the FRED IMF series, PortWatch, `news_stories`) is licensed for internal use only and must not be republished.

## Session 29: consolidated tables

54 tables became 6 (`docs/migrations/2026-09-29-consolidation.md`; the map is `warehouse/metadata/table_migrations.csv`).

- **Manifest.** `redivis_uploads.csv` has a column `migrated_to`: the consolidated table an old table moved into. Its line is kept, never removed, so the history gate keeps its count.
- **Restore.** `--restore` neither expects nor restores a migrated table. Its rows come back inside the consolidated table, and `warehouse/consolidate.py split` writes it for the connectors.
- **License check.** `--check-license` allows a migrated public table in the public draft until it is removed.
- **Removal.** `--remove-migrated [--dry-run]` removes the old tables after checking every family (`docs/runbook.md`). A human runs it; no scheduled run does.
- **Large tables** (the ERCOT history is 0.65 GB) are streamed to the upload, never held whole as text or as a frame.
