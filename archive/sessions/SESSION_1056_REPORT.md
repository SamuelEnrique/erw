# Session 1056 report: the package's errors, read by a stranger

23 October 2026, about 08:00 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1056. Model spend USD 0. Requests: 7 to the live set (ceiling 10), the anon key only. Stata and R are not on this machine: their changes are checked by `packages/stata/check_ado.py`, `packages/r/check_r.py` and test 1056's source checks.

## Read these first

Each failure was provoked once in Python (`runs/chain_072/errs1056.py`) and read as a researcher who has never seen the ERW:

| Failure | What it said | Verdict | Now |
|---|---|---|---|
| a held table | "iso_rtm_hub_prices is not public: unsettled. MISO's terms ask for written permission ..." | says what and why | unchanged |
| an empty window (1900) | a warning: "No rows of ... start in [...); its rows run from 1986-01-02 to 2026-10-20" | says what and where the rows are | unchanged |
| a misspelt table | "No ERW table named eia_fuel_spot_price ...; with a close name: eia_fuel_spot_prices" | good | unchanged |
| **a table not in the live set** (`ercot_node_places`, asked of the live set) | "No ERW table named ercot_node_places" | **wrong**: it is a table of the record | "ercot_node_places is not in the live set: erw.tables() says which tables are (in_live); read it from the Stanford dataset or a clone's tables instead." In Stata and R it returned an empty dataset; now the same sentence |
| **a bad date** (`start="2026-13-45"`) | pandas' "month must be in 1..12, not 13" | **says nothing of what to do** | "The start 2026-13-45 is not a date the ERW reads: write it as YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SSZ in UTC, then try again." |
| **a start after the end** | an empty-window warning with the window reversed | **easy to miss** | "The start 2026-10-01 is not before the end 2026-09-01, so the window [start, end) holds no time: give a start before the end, then try again." |
| no Redivis token | "Set REDIVIS_API_TOKEN to a token from ..., then try again." | good | unchanged |

The three new sentences are in `erw/errors.py`, `erw.ado` and the R package, and in the conformance file's `errors` block. The two window errors are raised before any request (Python `erw.ERWBadWindow`, a `ValueError`; Stata error 198; R `stop`). `docs/methods/packages.md`, "Errors, in words", lists them.

## Checks

| Check | Exit | Result |
|---|---|---|
| tests 1056, 1013, 1006, 1001 | 0 | 32 passed |
| `check_ado.py` | 0 | 22 programs, 0 problems |
| `check_r.py` | 0 | 0 problems |

## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. **A start equal to the end is refused too** (the window [start, end) holds no time).
2. **The Stata date check follows the command's own filter** (`clock` of the first 19 characters, else the date); a value longer than a date whose 11th character is not "T" or a space is refused, as Python refuses it.

## For Samuel's ruling

- None new. Your Stata and R run (packages-open item 1) exercises these three sentences too.
