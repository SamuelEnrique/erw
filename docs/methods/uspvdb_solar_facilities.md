# U.S. Large-Scale Solar Photovoltaic Database: the large solar facilities, their outlines' places and design

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `uspvdb_solar_facilities`

## Publisher and address

U.S. Geological Survey (USGS) and Lawrence Berkeley National Laboratory (LBNL), U.S. Large-Scale Solar Photovoltaic
Database (USPVDB), API v1. Source code `usgs:uspvdb`; the database's page is `https://energy.usgs.gov/uspvdb/`. The
connector reads USGS's public API, which needs no key:

`https://energy.usgs.gov/api/uspvdb/v1/projects?limit=10000&offset=<k>`

in pages of 10,000 facilities, 3 seconds apart, until a page comes back short. The host has no robots file (HTTP 404,
session 890). Connector: `warehouse/connectors/uspvdb.py` (session 890), the solar sibling of `uswtdb.py`
(`uswtdb_wind_turbines.md`).

## Vintage and revision

One snapshot of the whole database as the API gives it on the run's day. When written: one page, retrieved
2026-10-23T05:19:06Z, written by run `20261023T051957Z` from the saved page. `vintage` is empty. A run replaces the table
whole, so a facility the database drops leaves the table. Ceiling 10 requests a run; without `--offline` every page is
asked fresh. Session 890 made 5 requests of its 20: one to PHMSA (below) and four to USGS.

The database's newest year is not complete: 217 facilities have `project_year` 2025, against 647 in 2024.

## Shape and variables

Entities, one row a facility. The standard columns: `entity_id, entity_type, name, geo, lat, lon, capacity_mw, status,
status_date, operator, source, source_url, retrieved_at, vintage`.

- `entity_id` `uspvdb:<case_id>`, the database's id of the facility, for example `uspvdb:400004`. A `case_id` given
  twice stops the run.
- `entity_type` `plant`; `name` the facility's name (`p_name`); `geo` `US-<state>`; `lat`, `lon` from `ylat`, `xlong`,
  the outline's centroid.
- `capacity_mw` the facility's AC capacity (`p_cap_ac`, MW), as EIA rates a solar plant; the DC capacity is in
  `capacity_dc_mw`.
- `status`, `status_date` and `operator` empty: the database lists facilities in operation, gives no status and names no
  owner.

The database's own fields follow, renamed with their units:

| Column | USGS field | What it is |
|---|---|---|
| `case_id` | `case_id` | the database's id |
| `eia_plant_id` | `eia_id` | EIA's plant id |
| `project_name` | `p_name` | the facility's name |
| `project_year` | `p_year` | the year of operation |
| `state`, `county` | `p_state`, `p_county` | where it is |
| `power_region` | `p_pwr_reg` | the power region (PJM, MISO, ISNE, CISO, ERCO and others) |
| `capacity_ac_mw`, `capacity_dc_mw` | `p_cap_ac`, `p_cap_dc` | AC and DC capacity (MW) |
| `area_m2` | `p_area` | the outline's area (square meters) |
| `technology_primary`, `technology_secondary` | `p_tech_pri`, `p_tech_sec` | the primary technology (PV on every row) and the secondary (c-si, thin-film, cpv, other) |
| `axis` | `p_axis` | tracking (single-axis, fixed-tilt, dual-axis) |
| `azimuth_deg`, `tilt_deg` | `p_azimuth`, `p_tilt` | azimuth and tilt (degrees) |
| `battery` | `p_battery` | "batteries" where the facility has them, else blank |
| `agrivoltaic` | `p_agrivolt` | non-agrivoltaic, or es, grazing, crop and their combinations, as USGS gives them |
| `site_type` | `p_type` | greenfield, landfill, superfund and others |
| `system_type` | `p_sys_type` | ground, rooftop, canopy, floating, or more than one |
| `image_date` | `p_img_date` | the image's date, as YYYY-MM-DD |
| `digitizing_confidence` | `p_dig_conf` | the digitizing confidence (1 to 4) |
| `zscore` | `p_zscore` | USGS's z-score |
| `multi_polygon` | `multi_poly` | single or multi, as USGS gives it |
| `comments` | `p_comm` | USGS's comments |
| `image_date_usgs` | `p_img_date` | the image date as USGS gives it (YYYYMMDD) |

When written: 6,611 facilities in 50 states; AC capacity 131,574 MW; an EIA plant id on all 6,611; a battery at 375.
`project_year` runs from 1985 to 2025. Session 890's report and first header described the table as every
ground-mounted facility of 1 MW (AC) and more; as written, 52 facilities have an AC capacity under 1 MW (0.2 MW the least; each is 1 MW DC or more), and 619 have a
system type that does not name ground (rooftop 407, canopy 148, canopy and rooftop 62, floating 2). Session 891 corrected the docstring and the header (the
large-scale facilities as the database selects them, the two counts given) and wrote the table again, the same rows.

## Reading the API

- A field the connector maps that is missing from the API's records stops the run, as does a `case_id` given twice.
- Values as USGS publishes them: a blank stays blank, and nothing is filled. A whole number given as a decimal is
  written without its decimal point.
- The image date is written as a date where USGS's YYYYMMDD is one, and kept as given in `image_date_usgs` on every row.
  A value of eight digits that is no calendar date leaves `image_date` empty, is never mended, and is named in the
  header; the run goes on. When written: one, 20240231 (`uspvdb:406661`, Spencer (NY)). A value not of eight digits
  stops the run. The wind database's connector, by contrast, stops on a bad date.

## License

Public: USGS states that "USGS-authored or produced data and information are considered to be in the U.S. Public
Domain" (record 87 of `license_reads.csv`). The publisher, "U.S. Geological Survey (USGS), with LBNL", resolves by
session 888's name rule to USGS's verdict, "may be public", agreeing with the flag (`docs/licenses.md`: public, agrees).
Cite "U.S. Large-Scale Solar Photovoltaic Database, U.S. Geological Survey and Lawrence Berkeley National Laboratory".

## Cross-check (session 890)

Against `eia860_solar_generators` (session 885, EIA-860 2025, operable), by EIA plant id:

- 6,569 of the 6,611 facilities (99.4 percent) are EIA-860 solar plants.
- Their AC capacity agrees within 1 percent in 6,042 and within 5 percent in 6,199; in total 131,186 MW against EIA's
  131,738.
- 728 of EIA's 7,256 solar plants of 1 MW and more are not in the database. The database's 2025 is not yet complete
  (above).

## What it does not hold

- A facility's outline itself: only its centroid (`lat`, `lon`), its area and USGS's single or multi flag.
- No status, commissioning date or retirement: the database lists facilities in operation, and `project_year` is the
  year of operation.
- No owner or operator.
- No generation or capacity factor.
- A date for the one image date that is no calendar date (USGS's value is kept in `image_date_usgs`).
- PHMSA's pipeline incident data, which session 890 tried first: the pipeline safety office's host (www.phmsa.dot.gov)
  answered HTTP 403 to its robots file, so nothing else was asked.
