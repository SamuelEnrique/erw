# Inspection findings and violations at operating reactor sites, a finding, issued 29 July 1999 to 12 May 2025 (the NRC's Reactor Oversight Process: Findings and Violations)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2178).

Tables: `nrc_rop_findings`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC), the dataset "Reactor Oversight Process: Findings and Violations", linked from the NRC Data page (`https://www.nrc.gov/documents-reports/nrc-data`, read 366), with its data dictionary (read 367). One workbook, its first sheet:

`https://www.nrc.gov/sites/default/files/doc_library/cdn/data/reactors/operating/dataset/findings-violations.xlsx`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `nrc:rop_findings_violations`. Connector: `warehouse/connectors/nrc_rop_findings.py` (session 2178), its only table. www.nrc.gov's robots file (read 364) disallows, for every reader, its search pages, `ads.txt` and autodiscover; it disallows `/docs/` only to two named crawlers, Akamai-SiteSnapshot and Amazonbot. The report links in the table point to `/docs/` and are never asked.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written by run `20261024T013246Z` (session 2178) and written again, with the same rows, by run `20261024T015207Z` (session 2181, after the robots file's account in the connector and the header was corrected); the archive found no changed row.

## Vintage and revision

Issue dates from 29 July 1999 to 12 May 2025 (`event_date`). The workbook was retrieved at 2026-10-24T01:29:36Z by the session's probe, and both runs read that copy. The NRC last modified it on 2 September 2025 (06:15:52 GMT), and it holds nothing issued after 12 May 2025. The events table has no `retrieved_at` or `vintage` column; the header gives the retrieval time. `coverage.csv` gives the same 18,240 rows and the same first and last date.

Each run writes the whole table again (`ip.write_snapshot`), and the workbook is asked again unless `--offline`, since the NRC updates it at the same address.

## Shape and variables

Events, 18,240 rows, one a finding or violation, at 66 sites and 108 dockets. `event_id` `nrc_rop:<the first 14 hex digits of a SHA-1 hash>` of the docket, report number, issue date (as read, `YYYY-MM-DD`, since session 2185), procedure, title, type and cornerstone attribute, which together are unique; `event_date` the issue date (`YYYY-MM-DD`); `event_type` the NRC's type in lower case: ncv (non-cited violation) 14,779, fin (finding) 2,320, vio (violation) 855, nov (notice of violation) 128, ncviv 107 and noviv 2 (the same at severity IV), av (apparent violation) 49; `parties` the site as the NRC names it; `entity_ids` `nrc_reactor:<docket>` (05000... in 18,220 rows, 05200... in 20, all Vogtle AP 1000), the ids of `nrc_power_reactors`; `status` the significance color in lower case: green 17,357, white 609, greater than green 186, yellow 73, red 15; `mw`, `price`, `currency` empty.

- `x_procedure` the inspection procedure (blank in 1 row); `x_report_number`; `x_cornerstone` and `x_cornerstone_code` (Mitigating Systems 10,104, Initiating Events 2,780, Security 1,809, Barrier Integrity 1,711, Occupational Radiation Safety 849, Emergency Preparedness 547, Public Radiation Safety 305, Misc 135); `x_title`; `x_site_code`.
- `x_cross_cutting_aspect` (the NRC writes "None" in 15,024 rows and "N" in 674) and `x_cross_cutting_area` (N 15,698, H 1,999, P 539, U 2, S 1, X 1).
- `x_identified_by`: NRC - Identified 14,067, Self - Revealed 4,169, blank 4. `x_region` the NRC region, 1 to 4.
- `x_accession` the ADAMS accession number (blank in 234 rows; of the rest, 211 do not begin ML: 180 NS numbers, 8 M22217A111, 2 in lower case, and 21 notes such as "updates to sample" or "REOPEN UPDATE SAMPLE"; 21 are ML000000000) and `x_link` the NRC's link, `https://www.nrc.gov/docs/` and the accession in 18,222 rows (bare in the 234 without one). 18 links hold a space or a tab between `/docs/` and the accession, as the NRC prints them.
- `x_traditional_enforcement` True 169, False 18,071; `x_severity` None 18,074, IV 143, V 13, III 10; `x_cornerstone_attribute` (None in 16,126 rows); `x_year` and `x_quarter` the NRC's year and quarter, whose year is the year of `event_date` in every row.

By year of issue: 84 in 1999, about 1,000 a year in 2008 to 2012 (980, 884, 970, 1,075, 1,007), 281 in 2021, 523 in 2024 and 124 in 2025 to 12 May. 47 titles hold characters outside ASCII (curly quotes, a dash, the section sign). No `event_id` is given twice, and the rows are in (event_date, event_id) order. The counts were computed in session 2185 from the rows, read past the 10 header lines with pandas (every column as text).

## Checks the connector makes

- Before any request, the connector and www.nrc.gov are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- The sheet's columns must be exactly the 23 the data dictionary lists, in its order, or the run stops.
- A key (docket, report number, issue date, procedure, title, type and cornerstone attribute) given twice stops the run, and so does an issue date that is neither a date nor an Excel serial number between 20,000 and 80,000, or a sheet with no row.
- An issue date held as an Excel serial number is read as one and counted in the header: 819. Session 2178 found every such date agrees with the NRC's Year column, and the rows agree in full (0 of 18,240 differ).
- The report links are kept as printed and never asked. Nothing is filled.
- Ceiling: one request a run, a pause of 1 second after it.

## The cross-check

Session 2178's cross-check, `runs/c097/s2178/cross.py` (on the data machine, not in git), left no saved output (`runs/c097/s2178/` holds no `cross.out`), and the script as saved prints the types, the colors, the years, the serial dates against the Year column, the dockets against `nrc_power_reactors` and the columns of `nrc_event_notifications` only. Session 2185 computed the report's comparisons again from the tables in `warehouse/output/`:

- 106 of the 108 dockets are `entity_id`s of `nrc_power_reactors`. The two not there are Three Mile Island (05000289, 163 findings, the last on 9 May 2019) and Pilgrim (05000293, 247 findings, the last on 13 May 2019), both closed.
- All 13 dockets named in `nrc_event_notifications` have findings here. The notifications begin on 7 May 2025 and the findings end on 12 May 2025, so the two tables share six days and no count by plant is compared.
- The 15 red findings fall at five sites: Point Beach 4, Davis-Besse 3, Fort Calhoun 3, Indian Point 3 and Browns Ferry 2, issued from 30 October 2000 to 3 April 2014.

## License

The header: "License: the NRC's (see license_verdicts.csv). Cite the U.S. Nuclear Regulatory Commission." `license_verdicts.csv` records the NRC, read 16: "may be public", the same if the ERW sells anything: "NRC's website constitutes a U.S. Government Work under federal copyright law and as such, it is not subject to copyright." Its note: the NRC "would appreciate the courtesy of credit". The connector registers the source as `public`, as for `nrc_power_reactors` and `nrc_event_notifications`. `coverage.csv`: public.

## Found while writing this note

- Session 2178's cross-check left no output file, and its saved script does not compute the red sites, the closed dockets by name or the comparison with the event notifications that the report gives. Session 2185 computed them again from the tables and found the report's figures.
- Session 2178's report says the findings and the event notifications "do not overlap in time (the notifications start in May 2025)". They overlap from 7 to 12 May 2025.
- The table has no `retrieved_at` column, though its last header line says "Per row, source, source_url and retrieved_at say where it came from". The code puts `retrieved_at` in each row's base and then drops it, since the events columns it writes do not include it.
- The `event_id` hash takes the issue date as the workbook holds it, so a date the NRC stores as a serial number today and as a date later gives the finding a new `event_id`, though nothing else changed.
- 18 links hold a space or a tab inside, so they are not working addresses as printed; 21 accession fields hold a note instead of a number.

Acted on in session 2185: `retrieved_at` is kept, and the `event_id` hash now takes the issue date as read (YYYY-MM-DD), so a serial and a date give one id; the table was written again (the same 18,240 findings, with new ids); session 2178's report is corrected. The links and accession fields are kept as the NRC prints them.

## What it does not hold

- Findings issued after 12 May 2025: the NRC's workbook stops there.
- The inspection reports themselves (ADAMS documents), which are linked and never asked.
- Performance indicators, the action matrix or plant assessments: findings and violations only.
- Findings at sites other than operating reactor sites (fuel facilities, materials licensees).
