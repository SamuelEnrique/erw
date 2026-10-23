# `erw`: the Energy Research Warehouse in Python

`erw` reads the tables of the Energy Research Warehouse (ERW): power prices from the US grid operators (ERCOT back to
2015), EIA's hourly demand and generation, fuel, retail and petroleum series, generators, interconnection queues,
deals and derived tables, every row traceable to the report it came from. The same six calls exist in Stata and R
(`packages/stata/`, `packages/r/`); all three follow one specification,
[`docs/methods/packages.md`](../docs/methods/packages.md). For AI assistants, read [`llms.txt`](llms.txt) first.

## Install

```bash
pip install "git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"
pip install "erw-energy[redivis] @ git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"   # to read Redivis
```

pandas is the only dependency. The distribution is named `erw-energy` and imported as `erw`; it is not on PyPI yet.

## Where the tables come from

| Backend | What it holds | What it needs |
|---|---|---|
| `redivis` | the record: every public table, each released version kept, in the Stanford dataset `datapages.erw:b9wm` (DOI `10.57761/4f55-6d55`) | a Redivis account's token in `REDIVIS_API_TOKEN`, and the `redivis` extra |
| `live` | the latest rows: a public subset, the price and demand tables for their last 35 days, some small tables whole | the live set's address and anon key in `ERW_LIVE_URL` and `ERW_LIVE_KEY` (the ERW gives them on request) |
| `local` | the CSV files of a clone's `warehouse/output`, or of `ERW_DATA_DIR` | the files |

Each call takes `backend=`: `"auto"`, `"local"`, `"live"` or `"redivis"`. `auto` reads a table from local files when its
CSV is on disk, else from the live set when the live set holds the window asked for, else from Redivis's latest
released version. Without `backend=`, a call uses the session's backend: `ERW_BACKEND` (`local`, `live`, `redivis`,
`supabase` or `auto`) picks one on first use; else local files in a clone; else `auto`. `erw.SupabaseBackend` reads the
live set through the `supabase` client with the service key, or with `SUPABASE_ANON_KEY` and `ERW_SUPABASE_ROLE=anon`.

Until the ERW's first full release is clicked on Redivis, its latest released version (`v1.0`) holds one starter
table; the editors of the dataset read the draft with `erw.RedivisBackend(version="next")`, which is never citable.

## Example

The six calls, each once:

```python
import erw

erw.tables()                     # every table: shape, interval, first and last time, rows, license verdict, in the live set, title
erw.coverage("eia_fuel_spot_prices")   # one table's coverage row, with its verdict and what the live set keeps of it

df = erw.fetch("eia_fuel_spot_prices", entity="eia:henry_hub", start="2025-01-01", end="2026-01-01")
df.attrs["erw"]["version_line"]  # 'ERW eia_fuel_spot_prices: local files; ERW commit ...; fetched ...Z; 247 rows'

erw.cite("eia_fuel_spot_prices")
# 'U.S. Energy Information Administration (EIA). Natural Gas Spot and Futures Prices (NYMEX), daily; Spot Prices for
#  Crude Oil and Petroleum Products. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, ...'

erw.license("eia_fuel_spot_prices")["verdict"]   # 'public'
erw.standard("eia_fuel_spot_prices")["columns"]  # each column: its type (number, utc time, date, text) and whether it is required
```

- **`fetch(table, entity=, variable=, start=, end=, backend=)`**: `entity` is an entity (`ercot:HB_NORTH`) or a node as
  the grid operator writes it (`HB_NORTH`); `variable` a series variable, an entity type or an event type; `start`
  and `end` a window of interval starts in UTC, `[start, end)`. The partitioned tables also take `market=`, `ba=` and
  `year=` (`erw.fetch("eia930_all_demand", ba="ciso")`). `ts_utc` is a timezone-aware UTC time marking the START of
  each interval; `value` is a float.
- **A table that is not public** (`erw.license(t)["verdict"]` is `internal` or `unsettled`) is refused on the live set
  and on Redivis with the license's words (`erw.ERWLicenseHeld`); read from your own local files, it is returned with an
  `erw.ERWLicenseWarning` in the same words. `erw.tables()` lists every table, held ones too, with its verdict.
- **The citation** names the publishers and reports, then the ERW table and where the rows came from: the Redivis
  version, the live set with its fetch time, or the ERW commit of local files. Cite a released Redivis version, in the
  release's words: "\<the publishers\>. \<the reports\>. Via the Energy Research Warehouse (ERW), table `<table>`,
  Redivis dataset `datapages.erw`, version <tag> (released <YYYY-MM-DD>)."
- **`erw.requests()`** counts the requests the package has made to Redivis and the live set.

## Older calls, kept

`erw.info()`, `erw.list_tables()`, `erw.filter(iso=, market=, variable=, node=, start=, end=, license=, sector=)`,
`erw.sources(table)`, `erw.tier(table)`, `erw.version()` and `erw.migrations()` work as before. An old table name
(`ercot_dam_hub_prices`, now the `ercot_dam` partition of `iso_dam_hub_prices`) still reads, with a
DeprecationWarning, through `warehouse/metadata/table_migrations.csv`.

## The license record

Inside a clone the package reads the repository's own license record (`docs/licenses.md`,
`warehouse/metadata/license_status.csv`); an installed package reads the copy it carries, `erw/data/tables.csv`,
written by `python package/tools/build_tables.py` before a build. `internal` tables (PJM's data among them, licensed
for internal use only) are never shown publicly. From 21 October 2026 a table flagged public whose publisher asks for
permission is **held: license needed** unless a permission is recorded (42 tables in
`warehouse/metadata/license_status.csv`). The reader's guide, [`docs/guide.md`](../docs/guide.md), says what held
means and how to download a table from the site.

## Tests

```bash
python -m pytest package/tests -v                                   # against the clone's tables, no network
ERW_REMOTE_TESTS=1 python -m pytest package/tests -m remote -v      # Redivis and the live set, over the network
```

`package/tests/test_backends_three.py` reads five tables through the three backends and writes what it found to
`package/tests/three_backends.json`. The repository's own suite (`python -m unittest discover -s tests`) holds the
specification's checks without the network (`tests/test_session1001.py`).
