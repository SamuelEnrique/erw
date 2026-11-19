# Net generation by source, the thirteen regions (`eia930_region_fuel_hourly`)

Session 8001, chain 501 step B5, 19 November 2026. Connector: `warehouse/connectors/eia930_region_fuel_hourly.py`. Read by the page files `site/data/regions/mix/<region>.json` and `events/<event>.json` (`docs/methods/regions_pages.md`).

## Why a new table

The chain asked for each region's generation by source "from `eia930_ba_supply_hourly`". That table holds each balancing authority's net generation and total interchange only: chain 401 kept the demand, generation and interchange columns of EIA's six-month files and left their energy source columns. The source columns are in the same saved files (`warehouse/raw/eia930_region_hourly/`), so this table reads them; no request is made.

## The source

EIA's six-month files of the Hourly Electric Grid Monitor (Form EIA-930), `EIA930_BALANCE_<year>_<Jan_Jun|Jul_Dec>.csv`, July 2018 to the current half-year, the newest saved copy of each. Public (U.S. Government data).

## The sources of generation

The eight of the site's energy mix (`site/data/mix/*.json`, `generation_mix_hourly_profile`), from EIA's columns "Net Generation (MW) from ...". Each balancing authority's value is EIA's adjusted column where the file prints one, else the column as reported.

| Source | EIA's columns |
|---|---|
| `natural_gas` | Natural Gas |
| `coal` | Coal |
| `nuclear` | Nuclear |
| `wind` | Wind; from July 2024, Wind without and with Integrated Battery Storage |
| `solar` | Solar; from July 2024, Solar without and with Integrated Battery Storage |
| `hydro` | Hydropower and Pumped Storage; from July 2024, Hydropower Excluding Pumped Storage and Pumped Storage |
| `storage` | from July 2024, Battery Storage, Other Energy Storage and Unknown Energy Storage (negative while charging) |
| `other` | All Petroleum Products, Other Fuel Sources and Unknown Fuel Sources; from July 2024, Geothermal |

Before July 2024 EIA's files have no storage columns and count batteries under Other Fuel Sources, so `storage` is not written before then (blank, not zero), and `other` carries them. The adjusted solar column of the file of July to December 2024 is printed "Solar witho Integrated Battery Storage (Adjusted)"; it is read as "with".

## The rule

- A balancing authority's hour is **held** when its net generation (adjusted, else reported) is held, at least one of its sources is held, and its sources add up to its net generation within 5 percent of it, or within 1 MW (the rule `mix_profile.hours_of` applies to a grid, applied to one authority). A source the authority does not print that hour counts as zero in the sum.
- A region's hour is written when every balancing authority the file lists in that region for that hour is held; `x_bas` is how many were summed. Otherwise nothing is written for the region and hour, and the run log counts the region-hours left out.
- `ts_utc` is the hour's start (the file's UTC Time at End of Hour minus one hour). The last day and a half of each file is carried into the next, as `eia930_region_hourly.py` does, so a UTC hour split between two files is summed whole. Run with `--files` for one file, the rows are merged into the table and the first 30 hours of that file are left as the whole build wrote them.
- Nothing is filled, scaled or estimated.

## A check against the seven grids

Texas is one balancing authority (ERCOT). The region's monthly shares, built from this table by `region_files.py`, equal those of `site/data/mix/ercot.json`, built from EIA's API by `mix_profile.py`, to the hundredth of a percent in each month read (August 2025: natural gas 50.39, coal 12.81, nuclear 7.50, wind 14.39, solar 15.01 percent in both; January 2024 and March 2019 likewise), except storage before July 2024, which this table leaves blank and the ERCOT file shows as zero.

## The first build (19 November 2026)

6,282,393 rows, 13 regions, 2018-07-01T04:00Z to 2026-11-17T07:00Z, validated. Each region holds about 12,000 of the roughly 12,060 hours of the newest year and a half; the Northwest, with 23 authorities, about 9,400.

## Build

    python warehouse/connectors/eia930_region_hourly.py --download-only --files EIA930_BALANCE_<current half-year>.csv
    python warehouse/lock.py run --task fuel -- <python> warehouse/connectors/eia930_region_fuel_hourly.py --files EIA930_BALANCE_<current half-year>.csv

The whole table: the second command without `--files`.
