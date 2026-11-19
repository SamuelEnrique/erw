# The whole country's page files (`site/data/regions/`)

Session 8001, chain 501 part B, 19 November 2026. Builder: `warehouse/derived/region_files.py`. The files' shapes, keys and units: `docs/state/page_files_regions.md` (the contract the three other windows code against). No table is written and no request is made; every figure is computed from tables in `warehouse/output`.

## Inputs

| Table | What is read |
|---|---|
| `eia930_ba_demand_hourly` | each balancing authority's hourly demand (EIA's adjusted value where printed) |
| `eia930_ba_supply_hourly` | each authority's net generation (the first and last hour of a generation-only authority) |
| `eia930_region_hourly` | each region's net generation and total interchange |
| `eia930_region_fuel_hourly` | each region's net generation by source (`docs/methods/eia930_region_fuel_hourly.md`) |
| `region_weather_hourly` | each region's population-weighted temperature (`docs/methods/region_weather.md`) |
| `eia930_region_pair_hourly` | each region pair's hourly flow, both sides' reports |
| EIA-930 reference tables | codes, names, time zones, regions, "Generation Only BA", activation and retirement dates |

## A region's demand

The sum of the demand of the region's balancing authorities that file demand: U.S. authorities that EIA's reference tables do not mark "Generation Only BA", each counted from its activation date to its retirement date. An hour is written only when every one of them active that hour holds a value. Generation-only authorities file no demand, so they are not waited for.

`eia930_region_hourly` writes a region's demand only when every authority of the region holds demand, the generation-only ones included, so it holds no demand at all for the Carolinas, the Northwest, the Southeast and the Southwest, and the Midwest's only from September 2022 to May 2025. That is why the page files sum the authorities themselves.

Time zones: the zone of most of the region's demand by EIA's reference (Pacific for California and the Northwest, Arizona for the Southwest, Eastern for the Carolinas, Florida, the Mid-Atlantic, New England and New York, Central for Central, the Southeast, Tennessee and Texas), and Central for the Midwest, as the seven grids' files count MISO's days (EIA gives MISO Eastern, its market's clock). An authority's own file uses EIA's zone for it, MISO again Central.

## Demand files

- **Hours used:** those that pass the impossible-value rule of the seven grids' files (`demand_growth.screened`: held, above zero, within a quarter of the median of the four hours around, within the authority's own range).
- **Daily:** each local day from the first held to the last; the day's demand (MWh) and peak (MW, with its hour) only for a day whose every hour is used.
- **Growth:** `demand_growth.summarize`, the function that builds `site/data/demand_growth.json`, its keys unchanged: each whole year's average, peak and hourly profile, the months, the year to date, growth since 2019.
- **Weather** (regions only, built with `--weather`; without it a file keeps the weather object it had): `demand_weather.analyse`, the function behind `site/data/demand_weather.json`, with the same 48 lines fitted on 2019 to 2021 and the same years left out in turn. Two differences: the region's heating and cooling degrees are taken from its weighted temperature (base 65 F), where the seven grids' are taken at each station and then weighted, since `region_weather_hourly` holds the weighted temperature only; and no dew point term is used. A figure is written only when at least 95 percent of its hours are used, as for the seven grids; `region_weather_hourly` holds 80 to 99 percent of each region's hours, so many regions' yearly energy figures are blank by that rule, not by any fault of the fit.
- **Where a region and a grid cover the same ground** (Texas and ERCOT, the Mid-Atlantic and PJM, New York and NYISO, New England and ISO-NE), the file's `alike` object sets the region's yearly average beside the grid's from `demand_growth.json`. Both stand. On the first build they were equal to the tenth of a megawatt in every whole year from 2019 to 2025 for all four pairs; the region sums the authorities EIA places in it from the six-month files and the grid's file reads that one authority's own workbook, so a difference would mean the region holds another authority's demand (the Mid-Atlantic also holds OVEC) or the two files hold an hour differently.

## Mix files

The form of `site/data/mix/*.json`. A day is complete when every one of its local hours is held in `eia930_region_fuel_hourly` (storage aside, which is blank before July 2024); a month is written when at least 90 percent of its days are complete. For each month and year, the mean of each local hour over the complete days, for each source, demand and net generation (the sum of the eight sources), and each source's energy and share. The newest 35 local days are carried hour by hour (`hourly`), with net imports (EIA's total interchange with its sign turned).

Check: Texas's monthly shares equal those of `site/data/mix/ercot.json` to the hundredth of a percent in every month read.

## Trade files

From `eia930_region_pair_hourly`, by EIA's Eastern month. For a pair A-B (A before B by EIA's code), the table's first report is A's, read as power from A to B, and its second report is B's with its sign turned to the same direction. For region A, net imports from B by its own report are the first report with its sign turned and the neighbour's report is the second turned; for region B, its own report is the second and the neighbour's the first. The gap is the region's own report less the neighbour's, over the hours both reported. A region's total net imports for a month are written only when every neighbour's own report holds at least half the month's hours.

## Event files

The nine events of `/events`, their windows and baselines from `warehouse/derived/event_window.py` (the definitions the event pages are built on): Uri against the same calendar days of 2019 and 2020; the other eight against the same weekday 364 and 728 days earlier. So that every region's local days are inside it, an event's window runs from midnight of its first day in Eastern time to midnight after its last day in Pacific time, hour by hour. For each region: demand, net generation, net imports and generation by source; for each region pair, the flow from the first region to the second (the first side's report where held, else the second's). The baseline of an hour is the mean of the same hour at each baseline offset that holds it. Values are whole megawatts.

## Sizes (first build)

107 files, 28.7 MB: 13 region and 58 authority demand files (about 260 KB each), 13 mix files (145 to 300 KB), 13 trade files (6 to 22 KB), 9 event files (360 KB to 3.6 MB, COVID-19's 92 days the largest), the index (22 KB) and the boundaries (979 KB, `docs/methods/ba_boundaries.md`).

## Build

    python warehouse/derived/region_files.py --weather       # every file
    python warehouse/derived/region_files.py                 # every file, each keeping the weather object it had

The data machine's daily run calls the second form after the EIA-930 tables are brought to the newest hour (`docs/machines.md`).
