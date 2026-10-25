# Installed renewable electricity capacity at year end by UK region and technology, 2003 to 2025 (DESNZ's Regional Renewable Statistics)

Energy Research Warehouse (ERW), method note written in session 2695 (chain 135) for a table first written on 25 October 2026 (session 2692).

Tables: `desnz_regional_renewable_capacity_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Regional Renewable Statistics (`https://www.gov.uk/government/statistics/regional-renewable-statistics`). The table reads the workbook "Regional installed capacity MW 2003-2025", `https://assets.publishing.service.gov.uk/media/6aba6ee6997a4b2950ccefec/Regional_installed_capacity_MW_2003-2025.xlsx`, a sheet a year, no key. Source id `desnz:regional_renewable_capacity_2003_2025`. Connector: `warehouse/connectors/desnz_regional_renewable_capacity.py` (session 2692, made from session 2684's generation connector), whose raw store is `warehouse/raw/desnz_regional/`. www.gov.uk's robots file closes only print and search paths (read 1418); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T130035Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T12:56:48Z. DESNZ republishes the whole series each year, with the generation workbook (`desnz_regional_renewables_annual`).

## Shape and variables

Series, 3,157 rows, 197 entities, each year from 2003 to 2025, the capacity at 31 December. `entity` `desnz_rc:<region>:<technology>`:
- **Regions:** England's nine regions (`north_east`, `north_west`, `yorkshire_humber`, `east_midlands`, `west_midlands`, `east_of_england`, `london`, `south_east`, `south_west`), `england`, `wales`, `scotland`, `northern_ireland`, `other_sites` (not attributed to a region), `uk`, and `co_firing`: the non-fossil capacity used in co-firing, which DESNZ gives after the UK total and leaves out of it.
- **Technologies,** as each year's columns give them: `onshore_wind`, `offshore_wind`, `wind`, `wave_tidal`, `solar`, `hydro`, `landfill_gas`, `sewage_gas`, `anaerobic_digestion`, `biomass_waste`, `other_bioenergy`, `other_bioenergy_incl_sewage` and `total`.

`variable` capacity; `unit` MW; `ts_utc` the year's first day (the capacity is at the year's end, DESNZ's note 2); `freq` P1Y; `geo` GB (the UK, the other sites and co-firing), GB-SCT, GB-WLS, GB-NIR or GB-ENG (England and its regions); `node` the region and the column.

**Figures:**
- The UK's renewable capacity was 3.5 GW in 2003, 9.3 in 2010, 48.0 in 2020 and 65.3 in 2025.
- In 2025: onshore wind 16.4 GW, offshore wind 16.6, solar 21.9.
- Scotland held 17.9 GW in 2025; its onshore wind went from 5.4 GW in 2015 to 10.5 in 2025.
- Solar in 2025: 4.4 GW in the South West, 3.5 in the East of England.

## Reading the source

- The run stops at once, asking nothing, while `desnz_regional` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The sheets differ from the generation workbook's,** each difference read, not forced:
  - The sheet names have no space ("MW2025").
  - Yorkshire's region is "Yorkshire and Humber" from 2015.
  - The 2022 sheet names three rows "Eastern", "Other" and "Total".
  - The 2003 to 2006 sheets head one column "Other bioenergy (incl Sewage gas", without its closing parenthesis.
- Each sheet is checked for its title ("Installed capacity of sites generating electricity from renewable sources, <year>"), its header, its fifteen region rows in order, then the co-firing row. The footnote rows after co-firing are not read, and any other row stops the run.
- **Blank cells:** "[x]" (too few sites to show, inside the total), "[y]" (not available, outside it) and a blank cell have no row. Nothing is filled.
- **Checks,** all passing:
  - a region's technologies add to its total within 1 MW, or no more than it where a cell is "[x]";
  - England's nine regions add to England;
  - the nations and the other sites add to the UK.
- The run stops for a column or region not in the map, a value not a quantity, or a check missed.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1), the fourth quarter of 2025:
- onshore wind 16,430.69 MW and solar 21,914.97 MW in both;
- the UK's total 65,271.2 MW here against 65,306.7 there, 0.05 per cent apart.
