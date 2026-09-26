# warehouse/output: where the data lives

Session 9 ruling: **the warehouse data leaves git.** A hosted Postgres becomes the live store in the next session. Git keeps code, docs, metadata (`warehouse/metadata/coverage.csv`, `sources.csv`, `run_status.csv`) and the news digests (`docs/digest/`).

## What is in this folder

- **Tables (`*.csv`)**: every ERW table, one file each, in the shapes of `docs/datastandard.md`. They are **not in git** (`.gitignore`: `warehouse/output/*.csv`). Two small files a doc links to stay in git:
  - `news_index.csv` (the public news index);
  - `news_stories.csv` (under 1 MB; linked from the digests).
- **Run logs (`logs/`)**: one log per connector run. Every table header names the log that wrote it.
- **Raw source files** are in `warehouse/raw/` (never in git), with a `manifest.csv` per run. They are pruned after 14 days, and the manifests are kept.

`docs/coverage.md` and `warehouse/metadata/coverage.csv` (in git) list every table, its rows, time range, source, license and validator status. They describe the tables even where the files are not present.

## Where the data is now

Until the Postgres live store exists, there is only one full copy of the tables: the working tree where the connectors ran. Tables that were committed before session 9 can still be recovered from git history:

```bash
git show bfed5a2:warehouse/output/<table>.csv > warehouse/output/<table>.csv
```

The scheduled workflow (`.github/workflows/daily-prices.yml`) starts from a fresh checkout. It rebuilds each table's recent window, validates it and commits only metadata, docs and digests. Its tables are kept for 90 days as the run's log artifact (`runs/`, `daily.log`), not as a table store.

## How to regenerate every table

From the repository root, with the environment in `requirements.txt` (Python 3.14: `pip install --no-deps -r requirements-py314.txt`). Keys go in `.env`: `EIA_API_KEY` and `ANTHROPIC_API_KEY`, plus `PJM_API_KEY` for PJM.

```bash
# the whole daily sequence: ISO prices (last 3 days), EIA-930, EIA series, capacity, carbon,
# FRED, PortWatch, EIA-860M, news, validator, coverage, digest; QUEUES=1 forces the queues
PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh

# ISO prices, a longer window (the live tables hold 30 days)
.venv/Scripts/python warehouse/connectors/iso_prices.py all --days 30

# ERCOT hub price history, yearly tables from 2015 (session 8)
.venv/Scripts/python warehouse/connectors/iso_prices.py ercot --backfill-from 2015

# EIA-930 demand and generation, 30 days
.venv/Scripts/python warehouse/connectors/eia930.py --days 30

# full-history series (each run replaces all of it)
.venv/Scripts/python warehouse/connectors/eia_fuels.py
.venv/Scripts/python warehouse/connectors/eia_series.py
.venv/Scripts/python warehouse/connectors/capacity_prices.py
.venv/Scripts/python warehouse/connectors/carbon_auctions.py
.venv/Scripts/python warehouse/connectors/fred_series.py
.venv/Scripts/python warehouse/connectors/portwatch.py

# entities snapshots
.venv/Scripts/python warehouse/connectors/eia860.py --force
.venv/Scripts/python warehouse/connectors/iso_queues.py

# derived tables (session 9)
.venv/Scripts/python warehouse/derived/ercot_peak_premium.py

# news: feeds, scoring (Claude API), public index, digest
.venv/Scripts/python warehouse/news/ingest.py
.venv/Scripts/python warehouse/news/score.py
.venv/Scripts/python warehouse/news/index.py
.venv/Scripts/python warehouse/news/brief.py

# checks
.venv/Scripts/python warehouse/validate/erw_validate.py warehouse/output/*.csv
.venv/Scripts/python warehouse/metadata/build_coverage.py
.venv/Scripts/python -m pytest package/tests -q
```

A table is only ever written from its source. A connector whose source is incomplete writes nothing for that market and says why in its run log and in `warehouse/metadata/run_status.csv`. The 30-day ISO windows cannot be rebuilt from further back than each ISO publishes (ERCOT's live real-time files, for one, reach back about a week, and the yearly archive covers the rest).
