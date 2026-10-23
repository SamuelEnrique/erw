# Session 869 report: advanced meters and net metering by utility

23 October 2026, from 03:16 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **Two tables written, validated, archived (1,005,044 rows), in coverage (sector power, public), in the release package, both holds:**
  - `eia861_advanced_meters`: 497,838 rows, 2,932 utilities, 2015 to 2025, 45 variables: meters by kind (AMR, AMI, home area network, standard) and sector, energy served by AMI (MWh), and from 2020 customers with daily digital access and with direct load control.
  - `eia861_net_metering`: 507,206 rows, 1,336 utilities, 170 variables: net-metered capacity (MW), customers or installations (EIA's word changed in 2023), energy sold back (MWh) by technology and sector, storage paired with PV, virtual net metering, and from 2024 batteries with and without PV. Only the utility-level sheets: EIA's TPO and state-level sheets are aggregates.
- **The variables carry EIA's own headings** (group and sector), so a name changes where EIA's heading changed; the unit is read from the heading (MW, MWh, else a count). A first trial gave "virtual customers, 1 MW and over" the unit MW; a count is now a count whatever its heading names.
- **The cross-checks against the ERW's state tables:** AMI meters summed by state equal `eia_meters_state_annual` in all 255 state-years (2015 to 2019 in common); net-metered PV capacity equals `eia_net_metering_state_annual` at a median of 1.0000, 77 percent within 1 percent (the state table carries EIA's state-level figures, which hold more than the utilities' rows).

## Decisions made without you

- EIA's headings as variable names rather than a fixed map, since the net metering file changed its layout five times in eleven years; the header names the one column read past ("photovoltaic / capacity mw / type", a text field).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_meters_netmetering.py`, `tests/test_session869.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s869/`, `runs/s869*`.
