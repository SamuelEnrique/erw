# The UK's major power producers' power stations, May 2026 (DESNZ's DUKES 5.11)

Energy Research Warehouse (ERW), method note written in session 2717 (chain 136) for a table first written on 25 October 2026 (session 2714).

Tables: `desnz_uk_power_stations`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Power stations in the United Kingdom, May 2026 (DUKES 5.11)", `https://assets.publishing.service.gov.uk/media/6a6a365b0ddb7e4831c629f3/DUKES_5.11.xlsx`, its sheet "5.11 Full list", with table 5.11.A from the sheet "5.11 Summary" for the checks. No key. Source id `desnz:dukes_5_11_power_stations`. Connector: `warehouse/connectors/desnz_dukes_power_stations.py` (session 2714), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1446); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T182127Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T17:09:21Z (last modified 2026-07-29T17:20:27Z). DESNZ published it on 30 July 2026; the next edition is due on 29 July 2027. The workbook also holds the editions back to DUKES 2004, in other layouts, which are not read.

## Shape and variables

Entities, 1,364 rows, one a station operational at the end of May 2026:
- `entity_id` `dukes:<DESNZ site code>`, unique on the sheet; `entity_type` plant; `name` the site; `operator` the company.
- `geo` GB-ENG, GB-SCT, GB-WLS or GB-NIR from the country.
- `capacity_mw` the installed capacity as stated.
- `status` operating; `status_date` 2026-05-31, the end of the month the title names.
- `lat` and `lon` (WGS84) converted from the sheet's X and Y, which are British National Grid eastings and northings (EPSG:27700) for every station, Northern Ireland's included.
- The sheet's other columns, as text: `technology`, `type`, `chp`, `primary_fuel`, `secondary_fuel`, `grid_connection_type`, `country`, `region`, `postcode`, `os_reference`, `x_coordinate`, `y_coordinate`, `year_commissioned`, `desnz_site_code`.

**Figures:**
- 85,099.5 MW in all.
- By country: England 837 stations and 54,973 MW; Scotland 336 and 18,137; Wales 137 and 9,171; Northern Ireland 54 and 2,818.
- By fuel: natural gas 33,676 MW, wind 29,837 (onshore 12,952.6, offshore 16,884.9), solar 6,454, nuclear 5,883, biomass 3,316, pumped hydro 2,900.
- Drax's biomass units are 2,580 MW; Dinorwig is 1,800 MW; Hornsea 1 and 2 are 1,218 and 1,386 MW.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The list covers the major power producers only** (DESNZ's note 1). Other generators, 28,758.6 MW in table 5.11.A, many renewable sites and autogenerators among them, are not listed.
- **The coordinates:** converted with pyproj, which is imported for the conversion only. They were checked on Belfast's SSE Arena (54.604, -5.915), Ballylumford (54.845, -5.787), Drax (53.736, -0.991) and Dinorwig (53.119, -4.102). A coordinate not a number leaves `lat` and `lon` empty; none was.
- **Checks,** all passing:
  - the header as named;
  - every site code unique;
  - every capacity a positive number;
  - the list's capacity by fuel equal to table 5.11.A's major power producer rows, wind split onshore and offshore by the sheet's type, MSW as waste, pumped hydro as pumped storage, and in all equal to its total, within 0.01 MW.
- A country or fuel not in the map stops the run. Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1, all generators, the fourth quarter of 2025): offshore wind 16,649.7 MW there against the major power producers' 16,884.9 MW here, five months later.
