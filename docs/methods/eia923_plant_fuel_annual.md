# EIA-923: each power plant's net generation and fuel consumed, by fuel, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia923_plant_fuel_annual`

Connector: `warehouse/connectors/eia923_plant_fuel.py` (session 510; extended back to 2001 in session 524).

## Publisher and report

U.S. Energy Information Administration (EIA), Form EIA-923, read through EIA's API v2, route `electricity/facility-fuel`, annual, prime mover ALL.

- Page: `https://www.eia.gov/electricity/data/eia923/`
- API: `https://api.eia.gov/v2/electricity/facility-fuel/data/?frequency=annual&data[]=generation&data[]=total-consumption-btu&facets[primeMover][]=ALL&start=<year>&end=<year>`, one year at a time, in pages of 5,000 sorted by plant, fuel2002 and fuel type. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 130 requests a run, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia923_plant_fuel/` is reused and not asked again (the run that wrote the present file asked 0 of 130).

## Vintage and revision rule

Years 2001 to 2024 (`--from 2001 --to 2024`, the defaults since session 524). The table is written by `write_snapshot`: each run replaces the whole table with the years it read. The connector checks that the rows read for a year equal the count EIA gives for it, and stops if they do not.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia923:<plantCode>:<fuel2002>:<fuelType>`. Fuel2002 and fuelType together are the key: a pumped-storage and a conventional hydro unit share fuel2002 WAT (session 510's probe). `eia923:<plantCode>:ALL:ALL` is the plant's own total, which EIA publishes beside its fuels: a sum over a plant's fuels must leave it out.
- `variable` and `unit`:
  - `net_generation`, MWh (EIA's "generation"; negative where a plant used more than it made, pumped storage);
  - `fuel_consumed`, TBtu (EIA's "total-consumption-btu" in MMBtu, times 0.000001).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state> (US where EIA gives no state); `node` "<plant name>: <fuel type description>".

A unit EIA gives that is not in the connector's map (megawatthours, MMBtu) stops the run, and so does a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 510's report (`runs/s510/crosscheck.py` on the data machine), rerun by session 524 on the full table:

- every plant's ALL row against the sum of its fuels: 180,659 plant-years, all within 1 MWh;
- 2023 against `egrid_power_plants` (eGRID2023), by plant: 12,226 plants in both; of the 10,609 over 1 GWh, a median ratio of 1.0000 and 99.9% within 1%;
- the U.S. total each year against `eia_state_generation_monthly`: equal to the tenth of a TWh from 2001 to 2016; from 2017 the plants run 0.2% to 0.5% above (2024: 4,325.0 against 4,308.6 TWh). Why was not established.

## What it does not hold

- Monthly figures: EIA imputes the monthly figures of plants outside its monthly sample, and the API marks no row as imputed, so only the annual figures, which every plant reports, are taken.
- Prime movers: only the facet ALL is read, so a plant's figures are by fuel, not by prime mover or unit.
- A blank value has no row; nothing is filled.
- Years before 2001 or after 2024.
- Plant characteristics (capacity, operator, location beyond the state): those are in other tables (for example `egrid_power_plants` and the EIA-860M tables).
