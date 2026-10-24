# Session 2137 report: the atmosphere's carbon dioxide (the Scripps CO2 Program, not NOAA's GML)

23 October 2026, from 23:39 UTC, on lab-desktop (the data machine), chain 090, unattended. Model spend USD 0. Pulls: 10 requests of 10 (9 by the probe, 1 file; the write ran offline).

## Read these first

- **NOAA's Global Monitoring Laboratory was not asked for data.** gml.noaa.gov's robots file disallows `/webdata/` and `/aftp/` for every reader, and those are where its Mauna Loa monthly file, its global marine surface file and its annual growth file are. The ERW keeps a robots file, so no table comes from GML.
- **The same record from the Scripps CO2 Program instead:** Scripps has measured CO2 at Mauna Loa since 1958, the Keeling Curve; GML's measurements there are a separate record at the same observatory. Its page links the monthly file, and its Usage Restrictions page licenses its data CC BY 4.0, with credit to the Scripps Institution of Oceanography at UC San Diego.
- **A new table, `scripps_co2_mlo_monthly`** (series, 1,636 rows, `carbon`): CO2 and its seasonally adjusted value, a month from March 1958 to September 2026 (425.61 ppm). It is in a new unit, `ppm` (Decision 67, the number chain 090 kept for it), in micromoles per mole of dry air on the 2012 SIO manometric scale. Written, validated (0 errors, 0 warnings, with the branch's validator through the coverage step), archived, held from the Redivis storage and the live set, its release rows added.
- **What the table keeps and leaves out:**
  - 20 values the file marks -99.99 have no row.
  - Three months, December 2022 to February 2023, were measured at Maunakea's summit (MKO) after Mauna Loa's eruption; their `x_station` says so.
  - The fitted and filled columns are not taken: they are a curve and a fill, not measurements.
- **The global marine surface mean is not in the table.** Only GML publishes it, under the disallowed path.
- **The cross-check the chain file asks** (the growth against GML's annual growth file) could not be made: that file is under the same disallowed path. In its place, the yearly growth from the annual means (years with twelve months, 1959 to 2025) is set against the seasonally adjusted series' growth from one January to the next. Over 64 years they correlate at 0.741, with a mean absolute difference of 0.43 ppm: the two measure different twelve-month windows.
  - Growth by decade rises from 0.95 ppm a year in the 1960s to 2.41 in the 2010s and 2.60 in the 2020s.
  - The largest single year is 2024, at 3.57 ppm.
  - The 2025 mean is 427.03 ppm.

## Requests (10 of 10)

| n | What | Outcome |
|---|---|---|
| 1 | gml.noaa.gov/robots.txt | 200: disallows /webdata/, /aftp/ |
| 2 | scrippsco2.ucsd.edu/robots.txt | 200: /wp-admin/ only |
| 3, 4 | two guessed addresses of the Mauna Loa page | 404 |
| 5, 6 | the site's sitemap and its page list | 200 |
| 7 | the Usage Restrictions page | 200: CC BY 4.0 |
| 8 | the Primary Mauna Loa CO2 Record page | 200: the file's address, the citation |
| 9 | keelinglabsites.ucsd.edu/robots.txt | 404 |
| 10 | monthly_in_situ_co2_mlo.csv | 200, 87,054 bytes, last modified 21 October 2026 |

Reads recorded: 315 to 319 (probe requests 1, 2, 7, 8 and 9) (renumbered at session 2147's merge, after chains 069 and 079's).

## Decisions made without you

- **Scripps' record in GML's place.** It is the same observatory and the record the Keeling Curve is.
- **`ppm` as Decision 67.** The chains running beside this one agreed the number: 63 to 65 are chain 069's, 66 is chain 079's, and chain 092 numbers from 68.
- **The measured columns only.**
- **CC BY 4.0 registered as `public`,** the registry's word, as for GFZ's Kp (session 2136).

## For Samuel's ruling

- None new. A permission from NOAA GML for its `/webdata/` files would add the global marine mean.

## Files

- New: `warehouse/connectors/scripps_co2_mlo.py`, `tests/test_session2137.py`, this report.
- Changed:
  - `warehouse/validate/erw_validate.py` and `docs/datastandard.md` (`ppm`, Decision 67);
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - `docs/redivis/release-v1/`;
  - the license record.
- On the data machine only: `runs/c090/s2137/`, `warehouse/raw/scripps_co2_mlo/`, `warehouse/output/scripps_co2_mlo_monthly.csv`.
