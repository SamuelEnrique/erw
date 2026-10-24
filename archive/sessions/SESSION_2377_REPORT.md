# Session 2377 report: U.S. natural gas delivered for the account of others, by state and sector (EIA, natural-gas/cons/acct), the session's own choice

24 October 2026, from 09:00 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. Precheck passed (`runs/c112/pre2377.out`). Model spend USD 0. Pulls: EIA's API, 5 of 20 (below).

## Read these first

- **Two EIA routes the ERW does not hold were read first** (metadata):
  - `natural-gas/prod/shalegas` ends in 2021, so it was left.
  - `natural-gas/cons/acct` runs from 1982 to 2024, so it was taken.
- **One public table:** `eia_gas_for_others_annual`. It is written, validated, archived, in coverage (sector gas), and held from the live set and the release. 9,245 rows, 269 series, 1982 to 2024:
  - for the U.S., the 50 states and DC, the natural gas delivered to residential, commercial and industrial consumers for the account of others (MMcf);
  - EIA's share of each sector's deliveries made that way (ratio, EIA's percent divided by 100, as `eia_refinery_utilization_monthly` writes a percent).
- **Why this one:** it measures how far each state's gas customers buy their gas from marketers rather than their utility (customer choice and transportation). The ERW holds the deliveries but not this split.
- **License:** EIA's verdict is on record (public).

## The cross-check (`runs/c112/s2377/cross.py`, `cross.out`; tables read past their header lines)

- **The states add to the U.S.:** residential in 36 of 37 years within 0.5 per cent (the other has a U.S. figure of zero), commercial in 38 of 38, industrial in 43 of 43 (largest gap 0.04 per cent).
- **Every share is between 0 and 1** (3,996 values).
- **EIA's commercial share against the volume over the year's commercial consumption** in `eia_gas_consumption_state_monthly`: within 0.01 in all 1,200 state-years (median gap 0.0002). The U.S. share was 0.461 in 2021 and 0.472 in 2024, the same either way.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 5 of 20 | two routes' metadata, a year's sample, the trial's 2 pages |

## Errors

- None.

## Decisions made without you

- **EIA's gas delivered for the account of others chosen,** U.S. first and current to 2024.
- **The shares as ratios.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eia_gas_for_others.py`
  - `tests/test_session2377.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c112/s2377/`.
