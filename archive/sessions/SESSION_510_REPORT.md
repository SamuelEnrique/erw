# Session 510 report: Form EIA-923, each plant's generation and fuel by year

21 October 2026, from 19:24 UTC, on lab-desktop (the data machine), the first session of `queue/done/026-night-21-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia923_plant_fuel.py`: each power plant's net generation and fuel consumed, by fuel, a year.** It reads EIA's API v2, route `electricity/facility-fuel`, and writes the series table `eia923_plant_fuel_annual`.
  - 268,344 rows: 13,846 plants over 2020 to 2024, with 10,472 plants in 2020 and 13,258 in 2024.
  - Variables: `net_generation` (MWh, negative where a plant used more than it made) and `fuel_consumed` (TBtu, from EIA's MMBtu).
- **Annual only.** EIA imputes the monthly figures of plants outside its monthly sample, and the API marks no row as imputed, so no monthly row is taken. Prime mover ALL.
- **The key**: (plant, fuel2002) repeats, because a pumped-storage and a conventional hydro unit share fuel2002 `WAT`. (plant, fuel2002, fuelType) is unique, and it is the entity: `eia923:<plant>:<fuel2002>:<fuelType>`.
  - EIA publishes each plant's own total beside its fuels, as fuel2002 and fuelType `ALL`. Its entity is kept, and the header says to leave it out of a sum over fuels.
- **Robots and terms**: EIA's API is allowed, and EIA's terms are record 1 of `license_reads.csv` (public).
- **Cross-checks** (`runs/s510/crosscheck.py` on the data machine):

  | Check | Result |
  |---|---|
  | each plant's ALL row against the sum of its fuels | 59,002 plant-years, all within 1 MWh |
  | 2023 against `egrid_power_plants` (eGRID2023), by plant | 12,226 plants in both; of the 10,609 over 1 GWh, median ratio 1.0000 and 99.9% within 1% |
  | the U.S. total against `eia_state_generation_monthly` | 2020: 4,023.6 against 4,009.8 TWh; 2023: 4,200.8 against 4,183.3; 2024: 4,325.0 against 4,308.6 (0.3% to 0.5% above) |

- **Written under the data lock** (19:33 UTC, `runs/s510_write.sh`). The real run reused the trial's 29 saved pages (0 requests): the connector now reuses a page already in `warehouse/raw/eia923_plant_fuel/`.
  - The validator exited 0, `build_coverage.py --only` exited 0, and the archive exited 0 (with session 511's table: 448,505 rows).
- **Held** from `/data`'s catalogue and from Redivis v1 until a person uploads it, as session 489's tables are. Not in the live set.
- Sector rule (`power;gas;oil;coal`). Tests: `tests/test_session510.py`, 7, on real rows of the probe's page.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 31 of 40 | the route's metadata and a 2023 page (the probe); 29 pages for 2020 to 2024 (the trial); the write reused them |

## Decisions made without you

1. 2020 to 2024, as the chain asks; the plant total kept as its own entity rather than dropped.
2. A page already saved is reused, so a write after a trial asks nothing.

## Files

- New: `warehouse/connectors/eia923_plant_fuel.py`, `tests/test_session510.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, the metadata and holds of session 511's commit.
