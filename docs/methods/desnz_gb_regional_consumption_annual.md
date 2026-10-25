# Great Britain's electricity consumption and meters a year by country and region, 2005 to 2024 (DESNZ's Subnational electricity consumption statistics)

Energy Research Warehouse (ERW), method note written in session 2695 (chain 135) for a table first written on 25 October 2026 (session 2693).

Tables: `desnz_gb_regional_consumption_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Regional and local authority electricity consumption statistics (`https://www.gov.uk/government/statistics/regional-and-local-authority-electricity-consumption-statistics`). The table reads the workbook "Subnational electricity consumption statistics 2005-2024", `https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/Subnational_electricity_consumption_statistics_2005-2024.xlsx`, a sheet a year, no key. Source id `desnz:subnational_electricity_consumption_2005_2024`. Connector: `warehouse/connectors/desnz_subnational_consumption.py` (session 2693), whose raw store is `warehouse/raw/desnz_regional/`. www.gov.uk's robots file closes only print and search paths (read 1419); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T130818Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T13:03:48Z (last updated 18 December 2025, read 1421). DESNZ republishes the workbook with each new year.

## Shape and variables

Series, 2,608 rows, 190 entities, each year from 2005 to 2024. `entity` `desnz_sub:<area>:<item>`:
- **Areas, as each sheet names them:**
  - to 2014: `great_britain`, `scotland` and `unallocated`;
  - from 2015: `great_britain_inc_unallocated`, `england_and_wales_inc_unallocated` and `scotland_inc_unallocated`, whose rows include the consumption not placed in a local authority;
  - throughout: `england`, `wales` and England's nine regions (`north_east`, `north_west`, `yorkshire_humber`, `east_midlands`, `west_midlands`, `east_of_england`, `london`, `south_east`, `south_west`);
  - `inner_london` and `outer_london` where a sheet gives them.
- **Items:** `consumption_domestic`, `consumption_non_domestic` and `consumption_total`, and from 2012 `consumption_domestic_standard` and `consumption_domestic_e7` (Economy 7); the same for `meters_`.

`variable` consumption (`unit` MWh, the workbook's GWh times 1,000) or meters (`unit` count, its thousands times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` GB, GB-ENG (England and its regions), GB-WLS, GB-SCT, or GB-ENG,GB-WLS for England and Wales; `node` the area and the column.

**Figures:**
- Great Britain's consumption was 320.3 TWh in 2005 and 292.2 in 2014; with the unallocated, 287.5 in 2015 and 249.2 in 2024.
- In 2024: domestic 97.5 TWh of the 249.2; 31.8 million meters.
- In 2024: London 34.8 TWh, Scotland (with its unallocated) 21.7, Wales 13.0.

## Reading the source

- The run stops at once, asking nothing, while `desnz_regional` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Only the rows of whole countries and regions ("All local authorities") are read; the local authorities are not taken.
- **The areas are not joined across 2014 and 2015:** from 2015 DESNZ adds the unallocated consumption to Great Britain's and Scotland's rows, which earlier sheets give in a row of their own. The names are separate series and nothing is moved between them.
- **Columns are read by their headings.** "Domestic" (to 2011) and "All Domestic" (from 2012) are one item, as are "Non-Domestic" and "All Non-Domestic". The means, medians and consumption per household are not taken.
- **Checks,** each within 1 GWh or 0.01 thousand meters, all passing:
  - an area's domestic and non-domestic parts add to its total;
  - from 2012, its standard and Economy 7 parts add to its domestic;
  - England's nine regions add to England.
- The run stops for a heading or area not in the map, a sheet not a year, a value not a quantity, or a check missed. Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_nations_electricity_annual` (session 2678), England's sales:
- 243.1 TWh here in 2015 against 240.5 there;
- 212.0 in 2024 against 209.0.

The two count differently (meter-level consumption here, suppliers' sales there); the gap is 1.1 per cent in 2015 and 1.4 in 2024.
