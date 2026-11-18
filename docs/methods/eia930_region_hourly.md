# EIA-930 by region and by balancing authority, hour by hour, July 2018 on

Energy Research Warehouse (ERW). Session 7801, chain 401 part C, tables 1 to 3. Internal tier: registered, validated, archived and in coverage; read by no page and not in the live set. The data are public (U.S. Energy Information Administration).

## What the five tables hold

| Table | Rows (first build, 18 November 2026) | What |
|---|---|---|
| `eia930_region_hourly` | 3,064,131 | EIA's thirteen regions of the lower 48 (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX): demand, demand forecast, net generation and total interchange, each the sum of the region's balancing authorities |
| `eia930_ba_demand_hourly` | 7,829,972 | every balancing authority: demand and demand forecast |
| `eia930_ba_supply_hourly` | 9,137,257 | every balancing authority: net generation and total interchange |
| `eia930_ba_interchange_hourly` | see its header | interchange between each pair of directly connected balancing authorities, each side's report its own row |
| `eia930_region_pair_hourly` | see its header | interchange between each pair of regions with a tie, each region's report summed from table 4, side by side |

All hourly, UTC, from 2018-07-01 (the first hour of the July to December 2018 file) to the newest hour of the current six-month file. MW, which for an hour is EIA's MWh.

## Source

EIA's six-month files of the Hourly Electric Grid Monitor (Form EIA-930), `https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/`: `EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv` for tables 1 to 3 and `EIA930_INTERCHANGE_<year>_<half>.csv` for tables 4 and 5, every file from 2018 July to December to the current half-year. EIA rewrites the files as balancing authorities revise (the file of July to December 2018 was last modified 17 November 2026), so each build reads the newest copies. The robots file of www.eia.gov allows the folder (read 18 November 2026); the license record holds EIA's data as public.

## The balancing authority tables

- `ts_utc` is the hour's start: the file's "UTC Time at End of Hour" minus one hour. Checked against data: ERCOT's and CAISO's demand here equal `eia930_all_demand` (EIA's API, which is labelled by the hour's end and converted by its connector) at the same `ts_utc` to 0.01 MW on average over 1 to 7 September 2026, and differ by about 1,410 MW an hour either side.
- For demand, net generation and total interchange the file prints the value as the balancing authority submitted it and EIA's adjusted value (EIA's published series after its own checks and imputation). Both are kept, in `x_value_reported` and `x_value_adjusted`. `value` is the adjusted value where EIA prints one, else the reported value, and `x_basis` says which. The forecast has one column (`x_basis` reported).
- An hour without a value is not written. Values are as published: a few reported values are far out of range (demand of -992,136 MW for one balancing authority and hour with no adjusted value) and are kept, with their basis, for a reader to see; nothing is clipped.
- `x_region` is the region the file names for the balancing authority in that file. `x_file` names the file a row was read from; the header gives each file's URL, its Last-Modified time and when it was downloaded. Rows carry no URL: twenty million copies of it would be most of the tables' bytes.

## The regions

- A region's row is the sum of its balancing authorities' rows of that hour (each at its own basis), written only when every balancing authority the files list in that region for that hour has a value; `x_bas` says how many were summed. Otherwise nothing is written for that region and hour, and the header counts the region-hours left out per variable. Nothing is filled or scaled.
- `x_value_reported` and `x_value_adjusted` are the sums of the reported and adjusted columns where every balancing authority has that column; `x_basis` is adjusted when every summed value was adjusted, else mixed.
- The balancing authorities of a region change over the years (some begin or stop filing; the file names each one's region). A region's sum is of the ones filing in that hour.
- The six-month files are cut at each balancing authority's local midnight, so one UTC hour can sit in two files. The last 60 hours of each file are carried into the next and a region's sums wait 30 hours before a file's end, so a split hour is summed whole.
- A region's total interchange is the sum of its balancing authorities' totals. Flows between two balancing authorities of the same region cancel only as far as both sides report them alike; the region pair table shows how far the two sides of each region boundary differ.

## The interchange tables

- Table 4 keeps each report as filed: entity `eia930:<reporting BA>-<neighbour>`, positive when the reporting balancing authority sends power to the neighbour (EIA's sign). The neighbour's report on the same tie is its own row. Nothing is netted, averaged or made to agree.
- Table 5, for each pair of different regions with a tie (first region before second by EIA's code), sums by hour every report a balancing authority of the first region filed about one of the second (`x_first_report`), and every report one of the second filed about one of the first, its sign turned so both read as power from the first region to the second (`x_second_report`). A side is summed only when every tie between the two regions that appears in that hour has its value; `x_ties` is how many ties appear. `x_gap` is the first side less the second where both are held. `value` is the first side where held, else the second (`x_basis`). A pair-hour with neither side whole is not written.

## Why five tables and not two

One table of every balancing authority and region, hourly since July 2018, is about twenty million rows and more than five gigabytes, which this machine's validator cannot read in memory. The tables are split by measurement, as `eia930_all_demand`, `_generation` and `_interchange` already are, never by a value in the name (decision 28 of `docs/datastandard.md`).

## Build

    python warehouse/connectors/eia930_region_hourly.py --download-only --skip-saved
    python warehouse/lock.py run --task <task> -- <python> warehouse/connectors/eia930_region_hourly.py --from-raw
    python warehouse/connectors/eia930_ba_interchange_hourly.py --download-only --skip-saved
    python warehouse/lock.py run --task <task> -- <python> warehouse/connectors/eia930_ba_interchange_hourly.py --from-raw

Each run rebuilds its tables whole from the saved files, one file at a time. To bring them to a newer hour, download the current half-year's file again (without `--skip-saved` for it) and rebuild. They are not in the daily run.
