# `erw` in Stata: the Energy Research Warehouse

The six calls of the ERW's packages, as Stata subcommands: `erw tables`, `erw coverage`, `erw fetch`, `erw cite`,
`erw license`, `erw standard`. The Python and R packages take the same calls; all three follow one specification,
[`docs/methods/packages.md`](../../docs/methods/packages.md). Stata 16 or later.

## Install

```stata
net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace
```

Or, from a clone of the repository, `adopath + "<the clone>/packages/stata"`. `help erw` then gives the syntax.

## Where the tables come from

| Backend | Holds | Set |
|---|---|---|
| `redivis` | the record: the Stanford dataset `datapages.erw:b9wm` | `global REDIVIS_API_TOKEN` (a token from your Redivis account) |
| `live` | the latest rows, a public subset (the price and demand tables for their last 35 days) | `global ERW_LIVE_URL` and `global ERW_LIVE_KEY` (the ERW gives them on request) |
| `local` | the CSV files of a folder | `global ERW_DATA_DIR` |

`backend(auto)`, the default, reads local files when the table's CSV is there, else the live set when it holds the
window asked for, else Redivis. The live set and Redivis are read with `curl` (Windows 10 and later, macOS and Linux
carry it), since Stata's `copy` cannot send the headers they ask for. The coverage table, the source registry and the
license record come from `global ERW_REPO` (a clone) or else from GitHub.

## Example

```stata
global ERW_LIVE_URL "the address the ERW gave you"
global ERW_LIVE_KEY "the key the ERW gave you"
erw tables, clear
erw coverage eia_fuel_spot_prices, clear
erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) clear
erw cite eia_fuel_spot_prices
erw license iso_rtm_hub_prices
erw standard eia860m_retired_generators, clear
```

The fetch says 247 rows (fixture 01 of `fixtures/`, recorded from the live set on 23 October 2026). `examples.do`
reproduces two of the site's charts and displays the figures each shows.

## Types, held tables, citation

- A series' `value` is a double and `ts_utc` a `%tc` time in UTC; an entities table's `lat`, `lon`, `capacity_mw` and
  every `*_mw` are doubles and every `*_date` a `%td` date; an events table's `event_date` is a `%tc` time. Every other
  column stays text. From the live set a table's own extra columns arrive together in one text column, `extra` (JSON).
- A table whose license verdict is not public is refused on the live set and Redivis with the license's words (error
  498); `erw license <table>` says why.
- `erw cite <table>` writes the citation in the release's words; cite the Redivis version you read.

## How it is checked

Stata is not installed on the machine that wrote it. `python packages/stata/check_ado.py` checks the command's
structure, its style (no line continuation; one empty line between commands outside a block, none inside), its help,
the install files and `examples.do`, and runs the command's address builder through an interpreter of the Stata it is
written in: for each of the ten calls of `fixtures/calls.json`, the address equals the one the Python package
requested. The owner's run in Stata is the check this cannot make.
