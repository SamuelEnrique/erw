# Session 2245 report: the heat content of the gas each state burns (EIA), a second source of the session's own choosing

24 October 2026, from 03:42 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: EIA's API, 4 requests of 20 (below).

## Read these first

- **Why this source:** the ERW holds EIA's natural gas volumes by state in cubic feet. Turning them into energy, to compare with power or oil, needs each state's heat content, which the ERW did not hold. No queue file plans it, and EIA's verdict is on record.
- **One table written, validated, archived, in coverage (sector gas), in the release package, both holds:** `eia_gas_heat_content_monthly`, January 2013 to July 2026, 8,476 rows.
  - 52 series: the U.S., every state and DC.
  - The geo is `US` or `US-<state>`, from EIA's `S<state>` areas.
  - The route's metadata says it starts in 2012-01; its first value is 2013-01.
- **A new unit, `Btu/ft3` (Decision 74),** in the data standard and the validator together. It was agreed with chain 102's agent, whose Decisions now start at 75. EIA's unit is "BTU/CF".
- **The cross-check** (`runs/c101/s2245/cross.py`, `cross.out`):
  - **Against the states:** the U.S. figure against the states' figures weighted by their deliveries to consumers (residential, commercial, industrial and electric power, `eia_gas_consumption_state_monthly`) agrees to a median 0.30 Btu/ft3 (at most 1.58) over 163 months. It never falls outside the states' range.
  - **Against SEDS:** a year's U.S. mean against SEDS's implied figure (total consumption in TBtu, `eia_seds_state_energy`, over the year's consumption in MMcf) agrees within 1.3 Btu/ft3 in every year from 2013 to 2024. For example, 2024 is 1,036.2 against 1,036.6.
- **A correction to session 2244** (also in its report): the crude quality connector carried a guessed EIA page address. The command meant to replace it had failed unseen, and it reached the first write's header and `sources.csv`. It is now the API route itself, and the table was written again offline (the same rows).

## The pulls

1. The route's metadata (frequencies, facets, 2012-01 to 2026-07).
2. One page of 2025, to read the process, areas and unit.
3. and 4. The trial's two pages. The write reused them (0 requests).

## Errors

- **The connector's template carried the crude table's areas and a fixed geo.** They were replaced with the states before the trial.
- **Session 2244's guessed address** (above).

## Decisions made without you

- **EIA's heat content as the session's own choice,** for the reasons above.
- **`Btu/ft3` as Decision 74,** not written under another unit.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_heat_content.py`, `tests/test_session2245.py`, this report.
- Changed:
  - `docs/datastandard.md` and `warehouse/validate/erw_validate.py` (Decision 74)
  - `warehouse/connectors/eia_crude_quality.py` (the address)
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/s2245/`, `runs/s2245*`, `warehouse/raw/eia_gas_heat_content/`.
