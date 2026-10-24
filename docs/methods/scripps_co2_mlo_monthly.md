# Carbon dioxide in the air at Mauna Loa, a month from March 1958 (the Scripps CO2 Program's monthly in situ record)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 23 October 2026 (session 2137).

Tables: `scripps_co2_mlo_monthly`

## Publisher and address

The Scripps CO2 Program, Scripps Institution of Oceanography, UC San Diego: the in situ record at Mauna Loa Observatory, Hawaii, that C. D. Keeling began (the Keeling Curve). The program's "Primary Mauna Loa CO2 Record" page, `https://scrippsco2.ucsd.edu/data/primary-mauna-loa-co2-record/`, links the monthly file, `https://keelinglabsites.ucsd.edu/websitedataco2/monthly_in_situ_co2_mlo.csv`, which the connector reads. Source id `scripps:co2_mlo_monthly`. Connector: `warehouse/connectors/scripps_co2_mlo.py` (session 2137), one step: it asks, reads and writes in one run, or reads the saved file only with `--offline`.

NOAA's Global Monitoring Laboratory keeps a separate record at the same observatory. Its monthly, global marine and growth files are under `/webdata/` and `/aftp/`, which gml.noaa.gov's robots file disallows for every reader (read 303), so no table comes from it (session 2137).

## Vintage and revision

Months from March 1958 to September 2026 in the file on the data machine, written by run `20261023T234211Z` (23 October 2026), offline, from the file session 2137's trial saved (87,054 bytes): every row's `retrieved_at` is 2026-10-23T23:40:15Z and its `vintage` 2026-10-21T21:16:30Z, the file's Last-Modified. The file's own line, copied into the header: "Baseline data in this file through 20-Oct-2026 from archive dated 21-Oct-2026 14:16:02". The file says its data "are subject to revision based on recalibration of standard gases". Each run replaces the table whole (`iso_prices.write_snapshot`), so a revised month changes at the next run. No job runs the connector, so the table holds the file of 21 October 2026.

## Shape and variables

Series, 1,636 rows: one entity, two variables of 818 months each. `entity` scripps:mlo; `variable` co2 (the file's column 5, the monthly mean, which the file says is "adjusted to 24:00 hours on the 15th of each month") and co2_seasonally_adjusted (column 6, the same after the program's seasonal adjustment); `unit` ppm (Decision 67: micromoles of CO2 per mole of dry air, on the 2012 SIO manometric scale, as the file states); `freq` P1M; `ts_utc` the month's first day; `geo` and `market` empty; `node` Mauna Loa Observatory. Extra column: `x_station`, MLO (1,630 rows) or MKO (6 rows: December 2022 to February 2023, when the file's note says Maunakea's summit filled the gap the 2022 eruption of Mauna Loa made).

| Year | Mean co2, ppm |
|---|---|
| 1959 | 315.98 |
| 1960 | 316.91 |
| 1970 | 325.68 |
| 1980 | 338.70 |
| 1990 | 353.99 |
| 2000 | 369.38 |
| 2010 | 389.91 |
| 2020 | 413.95 |
| 2024 | 424.35 |
| 2025 | 427.03 |

The mean of the year's twelve measured months; every year shown has twelve. co2 runs from 313.21 ppm to 432.00 (May 2026); September 2026, the last month, is 425.61. co2_seasonally_adjusted runs from 314.43 to 429.12 (September 2026).

The saved file holds 828 monthly lines, January 1958 to December 2026. Ten have -99.99 in both measured columns and so have no row: January, February, June and October 1958, February to April 1964, and October to December 2026. These are the header's "20 values marked -99.99".

The header's second line (code line 121) gives MKO "for the months after Mauna Loa's 2022 eruption"; its third line, and the rows, give the three months only. The file itself disagrees with its own note: its opening lines say "Since December 2022 sampling has temporarily been relocated to MaunuaKea", while its column 11 note says MKO was used "from Dec 2022 through Feb 2023", and the station column is MLO from March 2023 on. The table follows the station column.

## Reading the source

- The run stops at once, asking nothing, while `scripps_co2_mlo` is in `paused_sources.csv` or keelinglabsites.ucsd.edu is a paused host.
- The file goes through `iso_prices.fetch_raw`, asked fresh unless `--offline` (then only the saved copy is read). A request not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits 5, 10 and 15 seconds); HTTP 404 is not retried. Timeout 60 seconds; 1 second after the request. One document a run.
- `parse` skips blank lines and the quoted header lines (61 in this file), and the lines before the first that begins with a four-digit year and a comma (the three lines of column names). From there every line must match `LINE`: year, month, two dates, six numbers and a three-letter station. A line not of that form, or a station other than MLO or MKO, stops the run, and no file is written.
- Only columns 5 and 6 are taken. A value of -99.99 is no row and is counted. The fitted columns (7 and 8) and the filled ones (9 and 10, column 5 or 6 with the gaps filled from the fit) are not taken: a curve and a fill, not measurements. A file with no month, or a month given twice, stops the run. Nothing is filled. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records the Scripps CO2 Program, read 305 (its Usage Restrictions page, `https://scrippsco2.ucsd.edu/usage-restrictions/`, 23 October 2026): "may be public", for public and for commercial use. The sentence: "Scripps CO2 program data and graphics on scrippsco2.ucsd.edu are licensed under a CC BY license, Creative Commons Attribution 4.0 International License (creativecommons.org/licenses/by/4.0/), which clarifies appropriate uses and requirements, including that credit be given to the Scripps Institution of Oceanography at UC San Diego." The verdict's note: the monthly file is served from keelinglabsites.ucsd.edu and linked from the record page (read 306); the page also asks that intentions be disclosed early and that coauthorship be considered for publications that depend on the data, which bind no redistribution. The header carries the credit and the citation the file asks (Keeling et al., SIO Reference Series No. 01-06, 2001). The registry's word for CC BY 4.0 is `public`; `sources.csv` flags `scripps:co2_mlo_monthly` public, and `license_tables.csv` lists the table under the program. The read numbers are the branch's; the session reports say they are renumbered when the chain lands.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2137/trial/scripps_co2_mlo_monthly.csv` that session 2137's cross-check read. No month is given twice, and the ten months without a row are those the saved file marks -99.99.
- The seasonal adjustment against the measured months: in the 66 years with twelve months (1959 to 2025, without 1964), the year's mean of co2_seasonally_adjusted is 0.001 to 0.009 ppm below the year's mean of co2. The seasonal range (the year's highest month less its lowest) runs from 4.87 ppm (1965) to 7.19 (1991), 5.89 on average.
- Session 2137's growth check (`runs/c090/s2137/cross.out`), made in place of GML's annual growth file, which is under a disallowed path: over 64 years the growth of the annual means and the seasonally adjusted series' growth from one January to the next correlate at 0.741, with a mean absolute difference of 0.433 ppm (they measure different twelve-month windows). The annual means grow 0.95 ppm a year in the 1960s and 2.41 in the 2010s; the largest single year is 2024, 3.57 ppm.

## What it does not hold

- The fitted and filled columns of the file.
- NOAA GML's Mauna Loa record, its global marine surface mean and its growth file (robots file, above).
- Any other file of the program: only the monthly in situ file is read.
- Months after September 2026, until the connector is run again.
