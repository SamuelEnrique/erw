# The fuel used in UK electricity generation, 1996 to 2025 (DESNZ's DUKES 5.3)

Energy Research Warehouse (ERW), method note written in session 2745 (chain 138) for a table first written on 25 October 2026 (session 2748).

Tables: `desnz_uk_fuel_used_generation_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Fuel used in generation (DUKES 5.3)", `https://assets.publishing.service.gov.uk/media/6a6a35ef0ddb7e4831c629f0/DUKES_5.3.xlsx`, its sheet "5.3", tables 5.3.B and 5.3.C. No key. Source id `desnz:dukes_5_3_fuel_used`. Connector: `warehouse/connectors/desnz_dukes_fuel_used.py` (session 2748), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1480); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T210701Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T21:04:25Z, DUKES 2026's edition. Energy Trends 5.1 and 5.3 update these figures quarterly and monthly (DESNZ's note 1).

## Shape and variables

Series, 900 rows, 30 entities, each year from 1996 to 2025. `entity` `desnz_fuel:<group>:<fuel>`:
- **Groups:**
  - `mpp`, the major power producers;
  - `other_transport` and `other_industrial`, other generators: undertakings in transport, and in the industrial and commercial sectors;
  - `other`, their total;
  - `all`, all generating companies.
- **Fuels:** the row as a slug, `total` for a group's "All" row.
- **5.3.C:** `mpp:conventional_thermal_and_other_stations` and `mpp:combined_cycle_gas_turbine_stations`.

`variable` `fuel_used` (5.3.B, by fuel) or `fuel_used_by_plant` (5.3.C, by plant type); `unit` MWh; `ts_utc` the year's first day; `freq` P1Y; `geo` GB; `node` the sheet's labels.

**MWh is the sheet's million tonnes of oil equivalent times 11,630,000,** DESNZ's own 1 ktoe = 11.63 GWh (stated on the DUKES 5.11 workbook's cover sheet). The validator holds no MTOE, and the conversion is fixed. Table 5.3.A, the fuels in their original units (million tonnes and GWh), is not taken.

**Figures:**
- All companies used 925.6 TWh of fuel in 1996, 923.4 in 2010 and 545.1 in 2025.
- Coal fell from 391.0 TWh in 1996 to none in 2025.
- Gas was 202.0 TWh in 1996, 377.2 in 2010 and 192.2 in 2025.
- The major power producers' CCGTs used 145.4 TWh in 1996 and 167.2 in 2025.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **DESNZ's notes:**
  - Oil includes orimulsion, oil in gas turbines and diesel plant, oil for lighting up coal boilers (note 3) and refinery gas (note 4). Coal includes coke oven coke (note 5), and gas colliery methane (note 6).
  - The major power producers' other fuels are non-biodegradable waste, in other renewables before 2013. Other generators' are mainly that, coke oven gas, blast furnace gas and chemical waste, in other renewables before 2007 (note 8).
  - Net imports' fuel equivalent was removed when the UK became a net exporter in 2022 (note 9).
  - 5.3.C's conventional thermal stations include gas turbines, oil engines, coal and renewable plants other than hydro, and exclude nuclear (note 10).
  - Nuclear and the renewables follow the IEA's primary energy conventions (note 11).
- Each table is found by its title and its year row. A group not in the map, or an entity given twice, stops the run.
- A blank cell has no row; a zero stays a zero.
- **Checks,** within 0.02 MTOE, all passing:
  - each group's fuels add to its total;
  - the transport and industrial generators add to the other generators;
  - the major power producers and the others add to all companies.

  DESNZ's rows and totals differ by up to 0.0153 MTOE (all companies), a little beyond rounding; the tolerance is set above that.
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_gas_quarterly` (Energy Trends 4.1, gas for electricity generation, four quarters summed), TWh:

| Year | Energy Trends 4.1 | DUKES 5.3 (here) |
|---|---|---|
| 2015 | 212.3 | 212.6 |
| 2020 | 232.5 | 232.5 |
| 2024 | 179.6 | 179.6 |
| 2025 | 192.2 | 192.2 |
