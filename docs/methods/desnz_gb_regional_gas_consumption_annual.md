# Great Britain's gas consumption and meters a year by country and region, 2005 to 2024, weather corrected (DESNZ's Subnational gas consumption statistics)

Energy Research Warehouse (ERW), method note written in session 2695 (chain 135) for a table first written on 25 October 2026 (session 2698).

Tables: `desnz_gb_regional_gas_consumption_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Regional and local authority gas consumption statistics (`https://www.gov.uk/government/statistics/regional-and-local-authority-gas-consumption-statistics`). The table reads the workbook "Subnational gas consumption statistics 2005-2024", `https://assets.publishing.service.gov.uk/media/69f9bf208f3213f7384ecae6/Subnational_gas_consumption_statistics_2005-2024.xlsx`, a sheet a year, no key. Source id `desnz:subnational_gas_consumption_2005_2024`. Connector: `warehouse/connectors/desnz_subnational_gas_consumption.py` (session 2698), whose raw store is `warehouse/raw/desnz_regional/`. www.gov.uk's robots file closes only print and search paths (read 1422); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T131751Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T13:14:17Z (last modified 5 May 2026). DESNZ's cover sheet:
- published 18 December 2025, next update December 2026;
- the years from 2015 revised each year;
- the 2005 to 2013 tables revised on 5 May 2026, moving some Welsh consumption between local authorities (Wales's total unchanged).

The same page lists a workbook not corrected for weather, for 2015 to 2024, which the ERW does not hold.

## Shape and variables

Series, 1,966 rows, 130 entities, each gas year from 2005 to 2024. `entity` `desnz_subgas:<area>:<item>`:
- **Areas, as each sheet names them:**
  - to 2014: `great_britain`, `scotland` and `unallocated`;
  - from 2015: `great_britain_inc_unallocated`, `england_and_wales_inc_unallocated` and `scotland_inc_unallocated`, whose rows include the consumption not placed in a local authority;
  - throughout: `england`, `wales` and England's nine regions (`north_east`, `north_west`, `yorkshire_humber`, `east_midlands`, `west_midlands`, `east_of_england`, `london`, `south_east`, `south_west`), except `london` in 2014;
  - `inner_london` and `outer_london` from 2014 (the 2014 sheet gives these two and no London).
- **Items:** `consumption_domestic`, `consumption_non_domestic` and `consumption_total`; the same for `meters_` (the consuming meters only); and from 2015 `meters_non_consuming`, outside the meters' total.

`variable` consumption (`unit` MWh, the workbook's GWh times 1,000) or meters (`unit` count, its thousands times 1,000); `ts_utc` the first day of the year DESNZ labels the gas year with; `freq` P1Y; `geo` GB, GB-ENG (England and its regions), GB-WLS, GB-SCT, or GB-ENG,GB-WLS for England and Wales; `node` the area and the column.

**What the figures are:**
- **Weather corrected:** from Xoserve's annual quantities for each meter, which take out the year's temperatures and wind.
- **Gas years, not calendar years** (the cover sheet):
  - 2014 is October 2013 to September 2014, and 2015 is October 2014 to September 2015; the years before 2014 use the same October to September period;
  - 2016 is mid-July 2016 to mid-July 2017, and 2017 is mid-June 2017 to mid-June 2018;
  - from 2018, mid-May to mid-May (2024 is mid-May 2024 to mid-May 2025).
- **Domestic is a consumption band:** a meter using under 73,200 kWh a year, the industry cut-off, so small businesses count as domestic.

**Figures:**
- Great Britain's consumption was 667.6 TWh in 2005 and 501.3 in 2014; with the unallocated, 488.4 in 2015 and 438.0 in 2024.
- In 2024: domestic 280.6 TWh of the 438.0; 24.9 million consuming meters and 0.38 million non-consuming.
- In 2024: the North West 56.0 TWh, London 54.3, Scotland (with its unallocated) 41.7, Wales 20.7.

## Reading the source

- The run stops at once, asking nothing, while `desnz_regional` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Only the rows of whole countries and regions ("All local authorities") are read. The local authorities, and from 2015 the rows of unallocated consumption by country, are not taken.
- **The areas are not joined across 2014 and 2015,** as in `desnz_gb_regional_consumption_annual`: the names are separate series.
- **Columns are read by their headings.** The Notes column, the means and the medians are not taken. A note on a country's or region's row stops the run; DESNZ's one note (a large consumer left out) is given to local authorities only.
- **Checks,** each within 1 GWh or 0.01 thousand meters, all passing:
  - an area's domestic and non-domestic parts add to its total;
  - England's nine regions add to England (in 2014, Inner and Outer London stand for London);
  - Inner and Outer London add to London where all three are given.
- The run stops for a heading or area not in the map, a sheet not a year, a value not a quantity, or a check missed. Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_gas_quarterly` (Energy Trends 4.1, the UK's final consumption, four quarters summed, not weather corrected):
- 2015: Great Britain's 488.4 TWh here against the UK's 495.3 there, 1.4 per cent apart;
- 2024: 438.0 against 428.2, 2.3 per cent apart.

The bases differ: Great Britain against the UK, gas years against calendar years, weather corrected against not. The domestic figures do not compare (280.6 TWh here in 2024 against 252.3 there), because the subnational domestic band takes in small businesses.
