# Session 490 report: EIA's Annual Energy Outlook, electricity

21 October 2026, from 17:27 UTC, on lab-desktop (the data machine), the second session of `queue/done/022-evening-21-october-sources.md` (run before 489, whose writes wait for the lock). Model spend USD 0.

## Read these first

- **The newest release is AEO2026**, not 2025: the API lists `aeo/2026` (2025 to 2050).
- **AEO2026 names no "Reference case".** Its cases are `cb2026` (Counterfactual Baseline), `higheldmd` (High Electricity Demand), the oil and gas supply cases, the economic growth cases, the zero-carbon technology cost cases and the alternative electricity and transportation cases: 11 in all. Rather than pick one as central, every case is taken and named in the entity and in `x_scenario_name`.
- **`warehouse/connectors/eia_aeo.py`**:
  - one series table `eia_aeo_electricity`: Tables 8 (Electricity Supply, Disposition, Prices, and Emissions) and 9 (Electricity Generating Capacity), entity `eia_aeo_2026:<seriesId>:<case>`;
  - units into the standard: GW as MW, billion kWh as MWh, cents per kWh as USD/kWh, with `x_dollar_year` 2025 (real) or nominal;
  - Table 8's emissions (858 rows, in million short tons and short tons) are not taken, since short tons are not in the standard's vocabulary, and the header says so;
  - a unit not in the map stops the run;
  - the sector rule and `tests/test_session490.py` (4 tests).
- **EIA answered 429 (Too Many Requests)** on the first trial: this machine's daily run was pulling EIA with the same key. The connector now waits 3 seconds between requests and asks a 429 or a 5xx once more after 60 seconds. One request a table and case, never a deep offset: a sorted page at offset 10,000 had answered 504.
- **Trial**: 34,034 rows, 1,309 series by case, 11 cases, 24 requests; the validator passes; the key is in no output or log.
- **Cross-check**: every case's 2025 total sales are 4,069 TWh; EIA's monthly retail sales for 2025 give 4,058.0 TWh (0.3% apart). AEO2026's first year is EIA's estimate of 2025.

## To finish (session 489's part, when the lock is free)

`python warehouse/connectors/eia_aeo.py`, the validator, `build_coverage.py --only '^eia_aeo_electricity$'`, `archive.py write --tables '^eia_aeo_electricity$'`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | about 40 over the session, at most 24 in a run | the probe (the routes, tables, scenarios, two pages and one 504), the failed trial (8, then 429), the trial (24) |

## For Samuel's ruling

- Which AEO2026 case the pages should call central, if any (`cb2026` reads "Counterfactual Baseline").
- `tCO2e` and short tons in the unit vocabulary (Table 8's emissions; GHGRP's CO2e, session 492).

## Files

- New: `warehouse/connectors/eia_aeo.py`, `tests/test_session490.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
