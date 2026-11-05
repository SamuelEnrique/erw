# Renewable electricity generation a year by UK region and technology, 2003 to 2025 (DESNZ's Regional Renewable Statistics)

Energy Research Warehouse (ERW), method note written in session 2681 (chain 134) for a table first written on 25 October 2026 (session 2684).

Tables: `desnz_regional_renewables_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Regional Renewable Statistics (`https://www.gov.uk/government/statistics/regional-renewable-statistics`). The table reads the workbook "Regional generation GWh 2003-2025", `https://assets.publishing.service.gov.uk/media/6aba6ef6fe72ed1e2b02f152/Regional_generation_GWh_2003-2025.xlsx`, a sheet a year, no key. Source id `desnz:regional_renewable_generation_2003_2025`. Connector: `warehouse/connectors/desnz_regional_renewables.py` (session 2684), whose raw store is `warehouse/raw/desnz_regional/`. www.gov.uk's robots file closes only print and search paths (read 1399); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T120249Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T12:00:30Z. DESNZ republishes the whole series each year.

## Shape and variables

Series, 3,002 rows, 194 entities, each year from 2003 to 2025. `entity` `desnz_re:<region>:<technology>`:
- **Regions:** England's nine regions (`north_east`, `north_west`, `yorkshire_humber`, `east_midlands`, `west_midlands`, `east_of_england`, `london`, `south_east`, `south_west`), `england`, `wales`, `scotland`, `northern_ireland`, `other_sites` (not attributed to a region) and `uk`.
- **Technologies,** as each year's columns give them: `onshore_wind`, `offshore_wind`, `wind`, `wave_tidal`, `solar`, `hydro`, `landfill_gas`, `sewage_gas`, `anaerobic_digestion`, `biomass_waste`, `other_bioenergy`, `other_bioenergy_incl_sewage` and `total`.

`variable` generation; `unit` MWh (the workbook's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` GB, GB-SCT, GB-WLS, GB-NIR or GB-ENG (England and its regions: ISO 3166-2 has no code for them); `node` the region and the column.

**Figures:**
- UK renewable generation was 10.6 TWh in 2003, 26.2 in 2010, 133.5 in 2020 and 152.9 in 2025.
- In 2025:
  - Scotland made 39.0 TWh, 22.0 of it onshore wind.
  - Yorkshire and the Humber made 34.8, 18.2 of it biomass and waste.
  - The East of England made 11.4 of offshore wind; London 1.5 in all.

## Reading the source

- The run stops at once, asking nothing, while `desnz_regional` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The columns change over the years:** one "Wind" column early, then onshore and offshore; "Other bioenergy" early, then sewage gas, anaerobic digestion and biomass and waste apart. Each column is kept as its own technology; none is merged or split.
- Each sheet is checked for its title ("Generation of electricity from renewable sources, <year>"), its header and its fifteen region rows in order.
- "[x]" (too few sites to show) and a blank cell have no row. Nothing is filled. DESNZ's note 1: components may not add exactly to totals because of rounding.
- **Checks,** all passing:
  - a region's technologies add to its total within 1 GWh, or no more than it where a cell is "[x]";
  - England's nine regions add to England within 1 GWh;
  - the nations and the other sites add to the UK within 1 GWh.
- The run stops for a column or region not in the map, a value not a quantity, or a check missed.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1, four quarters summed), the UK in 2025, in TWh:
- in all, 152.9 against 153.0;
- onshore wind 34.4 in both, offshore wind 52.0 in both, solar 20.1 in both.
