# Session 2751 report: the Western Area Power Administration's energy sold and power rate by project, FY 2008 to 2025

25 October 2026, about 21:58 to 22:07 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2751.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 fetch of the workbook, read offline by the trial and the write); two web searches.

## Read these first

- **`wapa_energy_sales_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/wapa_rates_sales.py`, 307 rows, 12 entities):
  - From WAPA's workbook "Rates and Sales Data FY 2008-2025" (sheet "Energy Sales and Rates Data", last modified 20 March 2026), found through WAPA's WordPress media listing.
  - `energy_sold` (MWh) for eleven projects and WAPA's total, and `power_rate` (USD/MWh, WAPA's cents/kWh times 10, an exact change of unit) for six projects. Each federal fiscal year, stamped on its first day (1 October of the year before), as EPRA's fiscal years are (chain 120's form).
  - WAPA's total energy sold: FY 2008 36,446,147 MWh; FY 2016 30,770,428; FY 2025 27,821,288 (FY 2011 the peak, 42,428,128; corrected in session 2759, which first gave FY 2012's 40,857,445).
  - **The projects add to WAPA's total exactly in all 18 years** (checked by the connector; within 0.5 MWh stops the run otherwise).
  - "N/A" has no row (the Central Arizona Project after FY 2019, as Navajo ceased generating on 19 November 2019; Olmsted before FY 2019). Washoe's FY 2008 zero stays a zero.
  - **The transmission rate** (the sheet's third table, dollars a kW a month) **is not taken:** the data standard has no unit for it.
  - WAPA's footnotes are in the header (Central Valley's energy includes custom product purchases; the LCRBDF surcharge is excluded from the Boulder Canyon and Parker-Davis rates; Boulder Canyon's 2018 to 2024 rates were restated; a drought adder is in the Loveland and Pick-Sloan rates to FY 2024).
- **Cross-check** against `usbr_hydropower_monthly`, Reclamation's net generation summed over each fiscal year's twelve months:
  - The Boulder Canyon Project's sales against Hoover's net generation: 3.1 to 4.7 per cent below in FY 2014 to 2018, 1.1 to 2.0 per cent above in FY 2019 to 2025 (FY 2025: 2,939,453 against 2,907,310 MWh).
  - The Parker-Davis Project's sales are near a fixed 1.42 TWh every year from FY 2011 (1,421,463 to 1,424,160 MWh; FY 2008 1,343,545, corrected in session 2759), while Parker's and Davis's net generation together ran from 1,307,744 (FY 2024) to 1,623,308 MWh (FY 2014): sales are contract amounts, met with purchases or surplus, not the plants' output. Stated in the report; not a fault of either table.
- **Terms:** www.wapa.gov's robots file closes only `/wp-admin/` and names no Claude agent (read 1485); the bare name wapa.gov fails its TLS handshake (read 1486), so its robots file could not be read and nothing was asked of it. WAPA's Web Policies state no copyright or reuse term (read 1490). WAPA is part of the Department of Energy, whose notice says government information at DOE websites is in the public domain (read 54, the DOE verdict on record). Recorded as public; **no WAPA verdict row was added here**, left to the licenses' round (session 2755).
- **Written under the data lock** (`runs/c057/write_table.sh`): validated, archived (307 rows), in coverage; the patch applied cleanly, no conflict marker, and the table appears once in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`. `finish_table.sh`: the release check and the license check pass (600 tables, 0 problems).

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.wapa.gov's robots file (its own request) | 200 |
| 2 | wapa.gov's robots file (its own request) | TLS handshake failure |
| 3 | WAPA's media listing, spreadsheets | 200, 60 workbooks |
| 4 | WAPA's pages searched for a disclaimer | 200, none |
| 5 | WAPA's home page, for its policy links | 200 |
| 6 | WAPA's Web Policies | 200 |
| 7 | 3-Rates-and-Sales-Data-FY-2008-2025.xlsx (the fetch) | 200, 74,117 bytes |

Reads recorded: 1485 to 1490. One request (read 1488) asked for three fields, but the probe's list cut the URL at its comma, so it asked only for links; noted, no harm.

## Decisions made without you

- **The fiscal year stamped on its first day,** 1 October of the year before, as chain 120's EPRA table does.
- **The power rate stated in USD/MWh** (times 10) rather than a new cents/kWh unit.
- **The transmission rate not taken** (no unit for dollars a kW a month).
- **The rolling 12-month forecasts not taken:** they are forecasts, each month's file replacing the last.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/wapa_rates_sales.py`, `tests/test_session2751.py`, this report.
- Changed: `build_coverage.py` (the sector rule), `release_v1.py` and `live_set.yaml` (the holds), `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1485 to 1490), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c139/s2751/`, `runs/license_reads/s2751/`, `warehouse/raw/wapa/s2751ratessales/`.
