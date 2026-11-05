# Renewable energy rights-of-way on public lands in California (the Bureau of Land Management)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for a table first written on 23 October 2026.

Tables: `blm_ca_renewable_rows`

## Publisher and address

U.S. Department of the Interior, Bureau of Land Management (BLM), California State Office, feature service "BLM CA Renewable Energy Projects" on gis.blm.gov (`https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer`), layer 0 (verified renewable energy rights-of-way) and layer 1 (preliminary), each asked once without geometry (`where=1=1&outFields=*&returnGeometry=false&f=json`). Connector: `warehouse/connectors/blm_renewable.py` (session 955). gis.blm.gov has no robots file (HTTP 404).

Session 955 found no national BLM layer of renewable projects: gis.blm.gov's public folders hold none, the national rights-of-way planning tool's group layer holds corridors and restriction areas, and the land records services answer the public with their root list only.

## Vintage and revision

Retrieved 23 October 2026; BLM updates the layers without notice. A snapshot (ceiling two requests; `--offline` reads the saved answers). An answer that says it holds more records than it gives stops the run.

## Shape and variables

Entities, 57 rights-of-way (46 verified, 11 preliminary). `entity_id` `blm_row:<BLM serial number, spaces removed>`; `entity_type` `project`; `name` BLM's project name (the holder or applicant as BLM writes it); `geo` US-CA; `capacity_mw` empty (BLM gives none); `status` empty, BLM's disposition in `x_disposition` (32 Authorized, 23 Pending, 2 Closed; Decision 20); `status_date` the effective date. `x_*`: the layer, serial number, case type (22 ROW-WIND DEV FAC, 19 ROW-WIND PROJ TEST, 16 ROW-SOLAR DEV FAC) and its code, commodity, project type (turbines, testing, CSP, PV), the application, effective and expiration dates, the expiration year, project and BLM acres, the data source, BLM's remarks and "in time".

## Reading the service

- The fields must be as read (layer 1 adds the section, township, range and meridian, kept out); a record without a serial number, or a serial number given twice, stops the run.
- BLM's dates are epoch milliseconds at the Pacific day's start; read as UTC days, they keep the day.
- A blank stays blank; nothing is filled.

## License

The Department of the Interior's notice (read 159 of `license_reads.csv`; verdict "may be public", session 956), and the service's own (read 156): data provided as is, BLM to be cited as the source, modifications described, nothing represented as approved by BLM.

## Cross-checks (sessions 955 and 960)

- By name in California, read by hand: of the 8 authorized solar rights-of-way, 5 are facilities of `uspvdb_solar_facilities` (Desert Sunlight, Stateline, McCoy, and Blythe and Desert Harvest, which BLM still types as concentrating solar, as authorized, though both were built as PV); Soda Mountain is not; Ivanpah and Genesis are solar thermal. 14 of the 24 authorized wind rights-of-way name a project of `uswtdb_wind_turbines`.
- Session 960, against the code: `FIELDS` and `PLSS` are the two layers' fields; the counts computed from the rows.

## What it does not hold

- Any state but California, and the rights-of-way' shapes.
- Capacity, and the projects' generation or interconnection (join by name to the EIA, USPVDB and USWTDB tables).
