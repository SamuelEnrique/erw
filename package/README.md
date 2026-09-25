# `erw`: a Python client for the Energy Research Warehouse (ERW)

`erw` reads the tables of the Energy Research Warehouse (ERW): harmonized
day-ahead and real-time power prices from US ISOs, every row traceable to the
ISO report it came from. It is modeled on the IRW's Python package
([itemresponsewarehouse/Python-pkg](https://github.com/itemresponsewarehouse/Python-pkg)).
For AI assistants, read [`llms.txt`](llms.txt) first.

## Install

From a clone of the erw repository:

```bash
python -m pip install -e package          # pandas is the only dependency
python -m pip install -e "package[test]"  # adds pytest, to run the tests
```

The client reads the CSV tables in the repository's `warehouse/output/`. To
read them from somewhere else, set `ERW_DATA_DIR` to that directory (and
`ERW_COVERAGE_CSV` to its coverage table if it is not at `../metadata/coverage.csv`).

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
| `erw.coverage()` | The coverage table as a DataFrame, one row per table |
| `erw.fetch(name)` | One table as a DataFrame, provenance header in `df.attrs["erw"]` |
| `erw.fetch([names])` | A dict of name to DataFrame |
| `erw.filter(iso=, market=, variable=, node=, start=, end=)` | Names of matching tables |
| `erw.sources(name)` | Source reports, report pages and every file URL behind a table |
| `erw.cite(name)` | A citation for the ISO report(s), naming the ERW table and data commit |
| `erw.version()` | The git commit of the data directory, and whether it has uncommitted changes |

## Storage backends

Every function reads through `erw.get_backend()`. Today that is
`erw.LocalBackend` (CSV files on disk). A Redivis backend can be added by
subclassing `erw.Backend` and calling `erw.set_backend(...)`; the public
functions do not change. `erw.set_backend("/path/to/output")` points the local
backend at another directory.

## Tests

```bash
python -m pytest package/tests -v
```

The tests run against the real files in `warehouse/output`, including a check
that every table's row count equals the count in `docs/coverage.md`.
