# Session 685 report: coal production, a public source the ERW did not hold

22 October 2026, from 10:50 UTC, on lab-desktop (the data machine), a session of `queue/done/044-night-24-october-data.md` (chain 041's sessions 642 and 643), on chain 041's branch. Model spend USD 0.

## Read these first

- **`eia_coal_production_annual` is written: 22,630 rows, 422 series, 2001 to 2024**, EIA's coal production (short tons), mines and average employees by producing state or region, coal rank and mine type (route `coal/aggregate-production`). Validated, archived, in coverage (sector coal, public), in the release package, both holds; method `docs/methods/eia_coal_production_annual.md`.
- **Why this source:** coal production is the one coal series the ERW lacked beside four coal price tables; session 519 left it out because the unit vocabulary held no short tons. **`short_ton` joins the vocabulary** (Decision 50), with the validator and the data standard.
- **The cross-check:** the states sum to 99.75 to 99.95 percent of EIA's U.S. production in every year; the ranks sum to the U.S. total exactly. The U.S. produced 578.0 million short tons in 2023 and 512.5 million in 2024.
- EIA's labor hours and productivity are not taken: `hour` in the vocabulary is an hour of the day.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 4 of 20 | the coal route list, the route's metadata, and the two pages of the trial (the write reused them) |

## Decisions made without you

- One source, not two: the session's 20 requests covered it with room, and its unit needed a Decision of its own.
- A new unit rather than thousands of barrels' kind of rescaling: EIA publishes short tons, and the ERW keeps the publisher's unit.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_coal_production.py`, `docs/methods/eia_coal_production_annual.md`, `tests/test_session685.py`, this report. Changed: `warehouse/validate/erw_validate.py`, `docs/datastandard.md`, `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, and the metadata, license and release files.
