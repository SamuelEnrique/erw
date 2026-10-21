# Session 517 report: EIA's natural gas prices by state

21 October 2026, from 19:59 UTC, on lab-desktop (the data machine), the second session of `queue/done/027-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_prices_state.py`: natural gas prices by state, a month**, from EIA's API v2 (route `natural-gas/pri/sum`, the Natural Gas Monthly's prices), as the series table `eia_gas_prices_state_monthly`.
  - 72,550 rows: 257 series, January 2001 to July 2026.
  - Five prices: citygate, residential, commercial, industrial and electric power (EIA's processes PG1, PRS, PCS, PIN and PEU), for the 50 states, DC and the U.S. EIA's shares of sales (VFA, VFC, VRX) are not taken.
- **The unit stays EIA's: `USD/Mcf`** (dollars per thousand cubic feet), which the vocabulary has held since session 7. No heat content is stated beside these prices, so none is converted.
- **A figure EIA withholds has no row** (293 of 1,806 records in 2026 alone). Nothing is filled.
- **Negative prices are EIA's**: the electric power price in New Mexico (down to -3.26 in April 2026), Arizona (April 2026) and Wyoming (February 2022). They fall in months when West Texas and Rockies gas traded below zero, and they are kept.
- **Robots and terms**: EIA's API is allowed, and EIA's terms are record 1 of `license_reads.csv` (public).
- **Cross-check** (`runs/s517/crosscheck.py` on the data machine): the electric power price, divided by 1.036 MMBtu per Mcf (an approximate heat content), against `eia_power_plant_fuel_costs`' natural gas cost per MMBtu, by state and month. 2,621 state-months are in both (2019 to 2026). The median ratio is 0.997, and the middle half runs from 0.985 to 1.012.
- **Written under the data lock** (20:17 UTC) with `--offline`, from the trial's saved pages (0 requests). The validator, coverage and archive exited 0.
- **Held** from `/data`'s catalogue and Redivis v1 until uploaded. Not in the live set.
- Sector rule (`gas`). Tests: `tests/test_session517.py`, 5.
- EIA's API answered each page in 20 to 60 seconds, with one 504 asked again; the trial took ten minutes.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 20 of 30 | the probe (3); the trial (16 pages and one 504 asked again); the write reused them |

## Decisions made without you

1. From 2001, as EIA's other retail tables in the ERW, within the ceiling.
2. USD/Mcf kept, no conversion.

## Files

- New: `warehouse/connectors/eia_gas_prices_state.py`, `tests/test_session517.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
