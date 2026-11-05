# Petroleum product stocks at refineries, bulk terminals and gas plants by state, a month (EIA, petroleum/stoc/st)

Energy Research Warehouse (ERW), method note written in session 2345 (chain 109) for a table first written on 24 October 2026 (sessions 2339 and 2342).

Tables: `eia_petroleum_stocks_state_monthly`

## Publisher and address

The U.S. Energy Information Administration, API v2, route `petroleum/stoc/st` ("EIA petroleum gas survey data"), process STR, "Stocks at Refineries, Bulk Terminals, and Natural Gas Plants":

    https://api.eia.gov/v2/petroleum/stoc/st/data/?frequency=monthly&data[]=value&facets[process][]=STR&start=2015-01

Pages of 5,000, sorted by period and series, with this machine's `EIA_API_KEY` (redacted in every record). Source id `eia:petroleum/stoc/st`. Connector: `warehouse/connectors/eia_petroleum_stocks_state.py` (session 2339, made from session 559's `eia_petroleum_stocks.py`).

## Vintage and revision

January 2015 to July 2026, written by run `20261024T074820Z`. That run read the 15 pages saved by session 2339's trial (12) and session 2342's (3), all asked on 24 October 2026; `retrieved_at` is the write's start, 2026-10-24T07:48:20Z, in every row. `vintage` is blank: EIA's answers carry no release date. A page a run saved is reused unless `--fresh`, so a run without `--fresh` writes EIA's figures as they were when the page was saved; `--fresh` asks every page again.

## Shape and variables

Series, 73,997 rows, 593 series, EIA's count met.

- `entity`: `eia_petroleum_stocks_state:<series>`, EIA's series id (one a product and area).
- `variable`: `stocks_refineries_terminals_gas_plants`, in kbbl (EIA's thousand barrels at the month's end).
- `ts_utc`: the month's first day. `freq` P1M.
- `geo`: `US-<state>` for a state, `US` for the U.S. (NUS) and the PADDs (R10 to R50).
- `node`: EIA's series name. `x_area` and `x_product`: EIA's area and product codes.

The areas: the 50 states EIA lists, the five PADDs and the U.S. (56).

The 13 products, with the U.S. stock at the end of July 2026 in kbbl:

| `x_product` | Product | kbbl |
|---|---|---|
| EPOBG | Gasoline blending components | 156,333 |
| EPOBGC0 | Conventional gasoline blending components | 123,340 |
| EPOBGR0 | Reformulated gasoline blending components | 32,993 |
| EPM0F | Finished motor gasoline | 9,279 |
| EPM0C | Conventional motor gasoline | 9,251 |
| EPM0R | Reformulated motor gasoline | 28 |
| EPD0 | Distillate fuel oil | 83,315 |
| EPDXL0 | Distillate, 0 to 15 ppm sulfur | 73,980 |
| EPDM10 | Distillate, above 15 to 500 ppm | 3,665 |
| EPD00H | Distillate, above 500 ppm | 5,670 |
| EPPK | Kerosene | 716 |
| EPPR | Residual fuel oil | 23,031 |
| EPLLPA | Propane | 86,545 |

Totals and parts are EIA's: a sum takes one level (areas, and products within gasoline and distillate). 100 values are 0 and are kept (69 of them reformulated gasoline blending components). None is negative.

## Reading the source

- 12 requests a run at most, 3 seconds apart. An HTTP 429 or 5xx answer is asked once more after 60 seconds; any other error stops the run. `--offline` asks nothing and stops at a page not saved.
- The run stops, and no file is written, for any of these:
  - a process other than STR;
  - a unit not in the map (MBBL to kbbl);
  - an area not the U.S., a PADD (or PADD 1's sub-districts) or a state code `S` plus two letters;
  - a key given twice;
  - EIA's count not met.
- A blank value has no row. Nothing is filled.
- The months 1993 to 2014 (about 50,000 rows) are not taken: the route's 15 pages from 2015 already exceeded one session's ceiling. `--from 1993-01` reaches them in a run with a ceiling to match.

## License

Public. EIA, read 1: "U.S. government publications are in the public domain". Cite "U.S. Energy Information Administration".

## Cross-checks (session 2342)

- Within the table:
  - the five PADDs sum to the U.S. within 0.0001 in every product and month;
  - the states sum to the U.S. at a median of 1.000 for every product (propane 0.991 to 1.000).
  - In some months a product's states run above the U.S. (reformulated motor gasoline up to 1.368, and distillate's sulfur grades up to 1.078), where EIA's state figures and its U.S. total are published separately.
- Against `eia_petroleum_stocks_monthly` (route `stoc/ts`, all stocks), the U.S. figures, 2015 to 2026:
  - residual fuel 1.000;
  - distillate 0.716 to 0.820;
  - propane 0.648 to 0.886.

  This route counts stocks at refineries, bulk terminals and gas plants only, not stocks in pipelines or at other primary terminals.

## What it does not hold

- Months before 2015; crude oil (not in this route); stocks in pipelines and at other primary terminals; stocks by type of storage (EIA's `stoc/typ`).
