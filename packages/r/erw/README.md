# `erw` in R: the Energy Research Warehouse

The six calls of the ERW's packages as R functions: `erw_tables()`, `erw_coverage()`, `erw_fetch()`, `erw_cite()`,
`erw_license()`, `erw_standard()`, with `erw_column_type()` and `erw_requests()`. The Python and Stata packages take
the same calls; all three follow one specification, [`docs/methods/packages.md`](../../../docs/methods/packages.md).
Base R only (R 3.6 or later): `utils::download.file` with `method = "libcurl"` sends the headers the live set and
Redivis ask for.

## Install

```r
install.packages("remotes")
remotes::install_github("SamuelEnrique/erw", subdir = "packages/r/erw")
```

## Where the tables come from

| Backend | Holds | Set (environment) |
|---|---|---|
| `redivis` | the record: the Stanford dataset `datapages.erw:b9wm` | `REDIVIS_API_TOKEN` |
| `live` | the latest rows, a public subset (the price and demand tables for their last 35 days) | `ERW_LIVE_URL` and `ERW_LIVE_KEY` (the ERW gives them on request) |
| `local` | the CSV files of a folder | `ERW_DATA_DIR` |

`backend = "auto"` reads local files when the table's CSV is there, else the live set when it holds the window asked
for, else Redivis. The record files come from `ERW_REPO` (a clone) or else from GitHub.

## Example

```r
library(erw)
Sys.setenv(ERW_LIVE_URL = "the address the ERW gave you", ERW_LIVE_KEY = "the key the ERW gave you")
h <- erw_fetch("eia_fuel_spot_prices", entity = "eia:henry_hub", start = "2025-01-01", end = "2026-01-01")
nrow(h)                      # 247 (fixture 01, recorded from the live set on 23 October 2026)
attr(h, "erw_version")
erw_cite("eia_fuel_spot_prices", h)
erw_license("iso_rtm_hub_prices")$words
```

`vignette("erw")` reproduces two of the site's charts (the Grid tool's ERCOT demand, the price board's Henry Hub).

A series' `value` is a double and `ts_utc` a `POSIXct` in UTC; an entities table's numbers are doubles and its
`*_date` columns `Date`; an events table's `event_date` is a `POSIXct`. Every other column is text; from the live set
a table's own extra columns arrive in one text column, `extra` (JSON). A table whose license verdict is not public is
refused on the live set and Redivis with the license's words.

## How it is checked

R is not installed on the machine that wrote it. `python packages/r/check_r.py` checks the R files' brackets and
escapes, NAMESPACE, DESCRIPTION, and runs `.erw_live_url` through an interpreter of the R it is written in: for each
of the ten calls of the fixtures, the address equals the one the Python package requested. The owner's run in R (the
testthat tests and `R CMD check`) is the check this cannot make.
