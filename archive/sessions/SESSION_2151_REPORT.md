# Session 2151 report: the next season's outlook (not taken: no data file by climate division)

23 October 2026, from 23:49 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: www.cpc.ncep.noaa.gov, 4 requests of 10: its robots address (404, there is none), the long-lead forecast archive's index, the 90-day outlook page, and lead 1's probability of exceedance page.

## Read these first

- **No table.** The Climate Prediction Center publishes its official three-month temperature outlook by climate division only as pages, one a division and lead (102 divisions, 13 leads: 1,326 pages an issue), under `poe_graph_index.php`. Its forecast archive since 1995 (`llarc.ind.php`) is a form that posts to `llarc.php` with a CSRF token, which a connector should not drive. Neither fits the session's ceiling of 10 requests, and the session did not try to scrape them.
- **What a later session could take:** the outlooks' GIS files (`/products/GIS/GIS_DATA/us_tempprcpfcst/seasonal.php`, shapefiles of the probability contours for each issue and lead). They are polygons, not climate divisions, so a table by division would need the divisions' boundaries and an overlay, a session's work of its own. It is written into chain 094's file at this chain's end.
- **The cross-check** the file asked for (winter outlooks in strong El Nino and La Nina seasons against `noaa_cpc_oni_monthly`) needs the table, so it was not run.

## Errors

- None.

## Decisions made without you

- **No scraping of 1,326 pages and no driving of a form,** within the session's ceiling; the GIS route said for a later session.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c092/s2151/`.
