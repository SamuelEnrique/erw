# Session 896 report: EIA-860's environmental and multifuel schedules; Decision 54, the entity type equipment

23 October 2026, from 06:17 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: none (`eia8602025.zip`, saved by session 873).

## Read these first

- **Four entities tables written, validated, archived, in coverage (sector power, public), in the release package, both holds:**
  - `eia860_multifuel_generators` (3,785 rows: operable, proposed, retired and canceled): each generator's energy sources, cofiring, switching between oil and gas, its capacity with each fuel, the time to switch and what limits it. Added to session 885's connector (`eia860_schedules.py`) as a fifth schedule.
  - `eia860_boilers` (4,384 boilers): each boiler's design (firing, fuels, steam flow, efficiency) joined with its emission standards and strategies (sulfur, nitrogen oxides, particulates, mercury). From the association schedule, each boiler's generators, cooling systems, particulate, SO2, NOx and mercury controls and stacks are listed in their columns.
  - `eia860_cooling_systems` (1,797): type, water source and discharge, intake rate, ponds and towers, costs.
  - `eia860_emission_controls` (5,375): each piece of emissions control equipment, its type, the control ids it carries, status, in service and retirement dates, total cost (EIA's thousand dollars, named so).
- **Decision 54: the entity type `equipment`,** a part of a plant that is neither a generator nor the plant, added to the validator and the data standard together.
- **The cross-check, against `eia860m_operating_generators`:**
  - Multifuel generators: 2,842 of the 2,847 operable are in EIA-860M's list, all 2,842 with the same nameplate.
  - Boilers: the 3,034 operating boilers name 4,741 generators, of which 4,352 (91.8 percent) are in EIA-860M's operating list.
  - Five boilers name no generator.
- **The environmental schedules use status codes of their own:** CO (new unit under construction), PL (planned), SC (cold standby), OZ (operated only in the ozone season), read from EIA's layout file, plus a few codes in lower case. They are mapped to the data standard's words, the code kept as given. One control has no status, left empty.
- **Not taken:** the flue gas particulate (FGP) and desulfurization (FGD) design details, and the stacks, named in the headers.

## Decisions made without you

- **A new entity type rather than a misfitting one:** a boiler is neither a plant nor a generator, so Decision 54 adds `equipment`.
- **A boiler's associations as lists in its own row** (joined with ";"), not tables of their own.
- **A control's key:** the plant, its equipment type and the control ids it carries (for example `eia860_control:3:SR:nox_1`). EIA gives no single id for one piece of equipment.
- **A process fault, mended:** after the schedules' write, my metadata conflict was staged before it was resolved, so the environmental write's patch nested a second conflict inside it. A new resolver (`runs/c049/resolve_nested.py`) took every table's newest line once. All four metadata files were checked: no marker is left, and every table's row is present.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia860_environment.py`, `tests/test_session896.py` (3 tests), this report.
- Changed:
  - `warehouse/connectors/eia860_schedules.py` (the multifuel schedule)
  - `warehouse/validate/erw_validate.py`, `docs/datastandard.md` (Decision 54)
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`
- On the data machine only: `runs/c049/`, `runs/s896*`.

## Corrected by session 905

The method notes' checks (session 905) found these against the code and the tables:

- The example key `eia860_control:3:SR:nox_1` does not exist; plant 3's keys are of the form `eia860_control:3:SN:nox_1` or `eia860_control:3:SR:nox_5+mercury_5`.
- "The 3,034 operating boilers name 4,741 generators" counts each generator once for every boiler that names it: they are 2,296 distinct plant and generator pairs, 2,132 of them in EIA-860M's operating list. The 91.8 percent (4,352 of 4,741) is a share of the mentions.
- The control with no status also has no equipment type and no control ids (`eia860_control:50118::`); 23 other controls carry no control id, so their keys end in `:`. 27 controls have no plant name or state (`geo` US).
- Retired cooling systems have no `status_date`: the cooling sheet gives no retirement date. The docstring now says so.
- The multifuel table's header named session 885; session 905 wrote the five schedules again, each naming its own session.
