# Session 2255 report: the Columbia River's federal dams (no table: every route is closed)

24 October 2026, from 04:01 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`. Model spend USD 0. Pulls: 8 requests of 15, each listed below. No table.

## Read these first

- **The Columbia's dam records could not be reached by any route the ERW may take.** Each was tried in turn, robots file first:
  1. **The Northwestern Division's water management data** (www.nwd-wc.usace.army.mil, the source the chain file names): the host fails certificate verification ("SSLCertVerificationError" at its robots file). Verification was not switched off, so nothing was asked.
  2. **The Corps' national CWMS Data API** (cwms-data.usace.army.mil): its robots file disallows `/cwms-data/timeseries/` and `/cwms-data/catalog/`, which is where the data are.
  3. **Columbia River DART** (www.cbr.washington.edu, the University of Washington's Columbia Basin Research, which republishes the Corps' operations): its query pages are allowed, but they only hold the form. The form submits to `/dart/cs/php/rpt/mg.php`, and its robots file disallows `/dart/cs/`.
  4. **Reclamation's Pacific Northwest Hydromet** (Grand Coulee, Hungry Horse): www.usbr.gov's robots file disallows `/pn-bin`, Hydromet's path.
  5. **NOAA's Northwest River Forecast Center** (www.nwrfc.noaa.gov, no robots file): its XML feed of the Corps' observations (outflow, inflow, forebay elevation, hourly) answers for Grand Coulee. It keeps only the last 10 days, whatever window is asked (476 observations, 14 to 24 October), so it holds no history. A table of 10 days that only a daily schedule could grow was not written.
- **The ERW's view of the Columbia's hydropower stays** BPA's balancing-authority generation (`bpa_ba_hourly`) and EIA-930's hydro for BPA. `usgs_streamflow_daily` holds discharge below eight dams.

## The pulls

1. www.nwd-wc.usace.army.mil/robots.txt: SSL certificate verification failed.
2. cwms-data.usace.army.mil/robots.txt: read; the time series disallowed.
3. www.cbr.washington.edu/robots.txt: read.
4. DART's river query for Bonneville's 2025 outflow: the form page.
5. www.usbr.gov/robots.txt: read; `/pn-bin` disallowed.
6. www.nwrfc.noaa.gov/robots.txt: HTTP 404, no file.
7. NWRFC's Grand Coulee station page.
8. NWRFC's XML feed of Grand Coulee's outflow, with `numdays=4000`: 10 days.

## Errors

- None in the ERW's code; no table was attempted.

## Decisions made without you

- **No table,** rather than a 10-day window.
- **The certificate failure not worked around:** a request without verification would accept any host claiming the name.

## For Samuel's ruling

- **The Columbia's federal dam data:** the Corps' Northwestern Division host has a certificate the machine does not trust (likely a DoD chain). Should the ERW install the DoD root certificates for `*.usace.army.mil`, or ask the Corps? Nothing is changed here.

## Files

- New: this report.
- On the data machine only: `runs/c102/s2255/`.
