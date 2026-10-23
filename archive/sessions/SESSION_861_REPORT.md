# Session 861 report: natural gas consumers by state and sector

23 October 2026, from 02:19 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`eia_gas_consumers_state_annual` is written: 12,864 rows, 52 areas (the states, DC and the U.S.), 1986 to 2024**: the number of natural gas consumers, residential, commercial and industrial, and from 1997 (residential) and 1998 (commercial and industrial) each split between those bought from a utility (sales) and those whose gas is transported for them (route `natural-gas/cons/num`, the Natural Gas Annual). Validated, archived, in coverage (sector gas, public), in the release package, both holds.
- **Why this source:** the ERW holds natural gas consumption by state (`eia_gas_consumption_state_monthly`) but not the consumers behind it, which a per-customer figure needs; it is outside chain 047's list.
- **Counts only:** the route also gives average consumption per consumer (unit MCF, 5,707 records), a ratio of two series the warehouse holds; it is left out and counted in the header.
- **The cross-check:** the states sum to EIA's U.S. row at a median of 1.0000 for all nine variables; the residential and commercial totals match exactly every year; transported industrial consumers fall to 0.82 in one year (states that withhold the split).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 6 of 20 | the route's metadata and newest records, a first trial that stopped at the MCF unit (its page kept), then the trial's three more pages, which the write reused |

Corrected by session 862: this report first said the split starts in 2000; the file starts it in 1997 and 1998 (session 862's note).

## Decisions made without you

- Per-consumer averages not taken (a ratio; the unit `Mcf` alone would misdescribe it).
- Variables named from EIA's process names ("Number of Residential Consumers" as `residential_consumers`).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_consumers.py`, `tests/test_session861.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s861/`, `runs/s861_*`.
