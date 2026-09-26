# `erw`: a Python client for the Energy Research Warehouse (ERW)

`erw` reads the tables of the Energy Research Warehouse (ERW): day-ahead and
real-time power prices from six US ISOs (ERCOT back to 2015), EIA-930 hourly
demand and generation, EIA petroleum, gas and retail series, generator and
interconnection-queue entities, news events and derived tables, every row
traceable to the report it came from. It is modeled on the IRW's Python package
([itemresponsewarehouse/Python-pkg](https://github.com/itemresponsewarehouse/Python-pkg)).
For AI assistants, read [`llms.txt`](llms.txt) first.

## Install

The repository is public, so the package installs straight from GitHub:

```bash
pip install "git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"
pip install "erw[redivis] @ git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"   # with a backend extra
```

An install from GitHub has the code but not the tables: point it at data with
`ERW_BACKEND=redivis` or `ERW_BACKEND=supabase` (below), or with `ERW_DATA_DIR`.

From a clone of the erw repository, which reads the clone's tables:

```bash
python -m pip install -e package          # pandas is the only dependency
python -m pip install -e "package[test]"  # adds pytest, to run the tests
```

The client reads the CSV tables in the repository's `warehouse/output/`. To
read them from somewhere else, set `ERW_DATA_DIR` to that directory (and
`ERW_COVERAGE_CSV` and `ERW_SOURCES_CSV` if the coverage table and source
registry are not in `../metadata/`).

`internal` tables (PJM data, licensed for internal use only) must never be
shown publicly: filter with `erw.filter(license="public")`.

## Example

```python
import erw
erw.info()                                   # what the warehouse holds, and its data commit
df = erw.fetch("ercot_dam_hub_prices")      # ts_utc is the interval START, in UTC
print(df.attrs["erw"]["sources"])            # the ISO report(s) behind the numbers
print(erw.cite("ercot_dam_hub_prices"))      # cite the ISO report, and the ERW table
```

## Functions

| Function | Returns |
|---|---|
| `erw.info(name=None)` | Summary of the warehouse, or of one table (dict; prints unless `quiet=True`) |
| `erw.list_tables()` | Every table name |
| `erw.coverage()` | The coverage table as a DataFrame, one row per table, with `license` (`public` or `internal`) |
| `erw.fetch(name, start=, end=, node=)` | One table as a DataFrame, provenance header in `df.attrs["erw"]`; optional row subset by interval start in [start, end) and node or entity |
| `erw.fetch([names])` | A dict of name to DataFrame |
| `erw.filter(iso=, market=, variable=, node=, start=, end=, license=)` | Names of matching tables |
| `erw.sources(name)` | Source reports, report pages and every file URL behind a table |
| `erw.cite(name)` | A citation for the source report(s), from the source registry, naming the ERW table and data commit |
| `erw.version()` | The git commit of the data directory, and whether it has uncommitted changes |

## Storage backends

Every function reads through `erw.get_backend()`. Today that is
`erw.LocalBackend` (CSV files on disk) and, since session 10:

- **`erw.RedivisBackend`** reads the Redivis dataset `energy_research_warehouse` (every table). It needs `REDIVIS_API_TOKEN` and `REDIVIS_OWNER` (`pip install -e "package[redivis]"`).
- **`erw.SupabaseBackend`** reads the Supabase live set (`warehouse/supabase/live_set.yaml`). It needs `SUPABASE_URL` with `SUPABASE_SERVICE_KEY`. With `SUPABASE_ANON_KEY` and `ERW_SUPABASE_ROLE=anon`, it reads public rows only (`pip install -e "package[supabase]"`).

`ERW_BACKEND=local|redivis|supabase` picks one for `erw.set_backend()`. Any other backend subclasses `erw.Backend` and is passed to `erw.set_backend(...)`. The public functions do not change. `erw.set_backend("/path/to/output")` points the local
backend at another directory.

## Tests

```bash
python -m pytest package/tests -v
```

The tests run against the real files in `warehouse/output`, including a check
that every table's row count equals the count in `docs/coverage.md`.
