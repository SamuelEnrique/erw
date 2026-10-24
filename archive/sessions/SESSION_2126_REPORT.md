# Session 2126 report: the world's electricity by country (Our World in Data, Ember's columns)

23 October 2026, from 23:06 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 1 request of 10 (the data; the codebook and the licenses were read in session 2125).

## Read these first

- **One table written, validated, archived, in coverage (sectors power and carbon), in the release package, both holds:** `owid_ember_electricity_annual`, each country's and region's electricity demand (MWh, 1990 to 2025, 6,378 rows) and its power sector's greenhouse gas emissions (tCO2e, 2000 to 2025, 6,028 rows), 239 countries and regions, 12,406 rows. The figures are Ember's yearly electricity data (global and European, 2026) as Our World in Data's energy dataset compiles them; Our World in Data last modified the file on 30 September 2026.
- **Two of the dataset's 130 columns, and why** (session 2125's reading): a column is taken only when every source the codebook names for it has a verdict in the license record that allows it. Only three columns draw on Ember alone; every other draws on the Energy Institute's Statistical Review (its site refuses the ERW's reader, so its terms are unread), on Our World in Data's population series (based on sources the record has not read), on Pinto et al. (2023) or on the UK's historical statistics. Of the three, the carbon intensity (gCO2e/kWh) needs a CO2-equivalent intensity unit the data standard does not hold (kgCO2/MWh is CO2 alone) and was left: it is the emissions over generation, and new decision numbers from 67 belong to chain 090. **The connector reads the codebook on every run and stops if a taken column's sources are no longer Ember's alone or its unit changed.**
- **The cross-check** (`runs/c079/s2126/cross.py`):
  - The United States' demand is 0.998 to 1.000 of EIA's generation plus net imports in every year 2015 to 2024 (`eia_international_electricity_annual`; 4,404,830,000 MWh in 2024). Canada's runs 1.019 to 1.071 of EIA's, Mexico's 0.875 to 1.070 (Ember takes those countries from their own national sources).
  - The United States' power sector emissions are 1.015 (2015) to 1.096 (2024) of EIA's power sector CO2 (`eia_power_co2_state_annual`, EIA's own US total): Ember counts CO2 equivalent, EIA CO2 alone, and the gap widens as gas, whose methane counts in CO2 equivalent, replaces coal. The two units are never summed.

## The pulls

1. The energy dataset (9.1 MB CSV) from catalog.ourworldindata.org, saved and reused by the write (`--offline`); the codebook came from session 2125's probe (seeded into the raw store).

## Errors

- **The first trial stopped on a pandas name clash** (a summary column named `first`); renamed and run again offline.
- **The first emissions comparison summed every fuel row of EIA's table** (each state's ALL with its parts, about four times the total); the comparison now reads EIA's own US total.

## Decisions made without you

- **Ember's columns through Our World in Data's catalog** (session 2125's decision), credited to both.
- **TWh and million tonnes written as MWh and tCO2e** (times 1,000,000), the standard's units.
- **Countries keyed by ISO alpha-3 with `geo` blank,** as `irena_capacity_annual` does; Our World in Data's and Ember's regions keyed by their names.
- **The carbon intensity column left out** rather than a new unit numbered into chain 090's range.

## For Samuel's ruling

- None new (session 2125's two).

## Files

- New: `warehouse/connectors/owid_energy.py`, `tests/test_session2126.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, the coverage, sources (Our World in Data and Ember), archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c079/s2126/`, `runs/s2126_*`, `warehouse/raw/owid_energy/`.
