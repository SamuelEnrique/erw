# Renewed reactor licenses and approved power uprates (the NRC's two lists)

Energy Research Warehouse (ERW), method note written in session 2066 (chain 066) for a table first written on 23 October 2026 (session 2064).

Tables: `nrc_license_actions`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC), two pages of www.nrc.gov:

- Status of License Renewal Applications, `https://www.nrc.gov/reactors/operating/licensing/renewal/applications.html`: its table of completed applications.
- Approved Applications for Power Uprates, `https://www.nrc.gov/reactors/operating/licensing/power-uprates/status-power-apps/approved-applications.html`.

Both addresses now answer at new ones (`https://www.nrc.gov/licensing-applications/status-initial-license-renewal-applications-and-industry-initiatives` and `https://www.nrc.gov/licensing-applications/operating-reactor-licensing/power-uprates/status-power-uprate-applications/approved-applications-power-uprates`, in the raw files' manifest); `source_url` keeps the addresses asked. Source id `nrc:license_renewals_uprates`. Connector: `warehouse/connectors/nrc_license_actions.py` (session 2064). www.nrc.gov's robots file disallows only its search and two files for every reader (session 2064).

## Vintage and revision

The renewal page last modified 23 October 2026 19:36:07 UTC and the uprate page 19:51:29 UTC, retrieved 20:36:10 and 20:36:12 UTC and written by run `20261023T203910Z` from the saved pages (`--offline`).

Each run that is not `--offline` asks both pages again, and the table is written whole each time (a snapshot): a row the NRC removes leaves the table.

## Shape and variables

Events, 236 rows, each `event_id` once; `parties` NRC; `entity_ids`, `mw`, `price` and `currency` empty.

| `event_type` | `event_id` | `status` | Rows | `event_date` |
|---|---|---|---|---|
| license_renewal | `nrc:renewal:<plant slug>:<YYYYMMDD received>` | issued | 63 | the renewed license's issue date, 23 March 2000 to 2 April 2026 |
| license_renewal | | withdrawn | 1 | Crystal River 3, the date received, 18 December 2008 |
| power_uprate | `nrc:uprate:<the NRC's number>` | approved | 172 | the approval date, 9 September 1977 to 9 November 2021 |

| Column | Form |
|---|---|
| x_plant | the plant and units as the NRC writes them (Calvert Cliffs 1 & 2, H.B. Robinson 2, Fermi, Unit 2) |
| x_application_received | renewals: the day received, 10 April 1998 to 14 February 2024 |
| x_extended_operation | renewals: as the NRC writes it, a date for each unit ("07/31/14 (Unit 1) 08/13/16 (Unit 2)"), two-digit years kept; empty for Crystal River 3, Kewaunee and Pilgrim 1 |
| x_note | renewals: the page's notes for the row's footnote marks, in 7 rows (the shut-down Fort Calhoun, Oyster Creek, Kewaunee, Vermont Yankee and Pilgrim 1, Crystal River 3's withdrawal, Diablo Canyon's earlier application) |
| x_link | renewals: the row's NRC page, in all 64 |
| x_uprate_type | uprates: MU 73 (measurement uncertainty recapture), S 65 (stretch), E 30 and E(1) 4 (extended), as the NRC writes them |
| x_uprate_pct | uprates: percent, 0.4 to 20.0 |
| x_uprate_mwt | uprates: MW thermal, 13 to 579; `mw` stays empty, these not being electric megawatts |
| x_accession | uprates: the ADAMS accession number as printed, 164 beginning ML and 8 older numbers ending in "*" |

| `x_uprate_type` | Rows | MWt | Percent |
|---|---|---|---|
| MU | 73 | 3,455.6 | 0.4 to 1.7 |
| S | 65 | 8,487.6 | 0.9 to 7.0 |
| E | 30 | 10,875.0 | 6.3 to 20.0 |
| E(1) | 4 | 1,328.0 | 11.9 to 15.0 |
| all | 172 | 24,146.2 | |

## Reading the pages

- The renewal page must hold exactly one table with a column "Renewed License Issued", or the run stops; its first four columns are read by position (Plant Name and Unit(s), Application Received, Renewed License Issued, Date Entering Extended Operation). The page's other three tables (one of letters of intent by fiscal year, two of plants and the dates their applications were received) are not taken.
- The page's notes are read from "* Fort Calhoun" to "Industry Activities" (or the page's end); a page without "* Fort Calhoun" stops the run. A trailing footnote mark (one or more "*", or "+++") is split from the plant, the issue date and the extended operation cells, and each mark must have its note, or the run stops; the row's notes are joined into `x_note`.
- A date is read as MM/DD/YY, or MM/DD/YYYY where it is written so (Diablo Canyon's issue date); one that does not read stops the run. The date received is read without splitting a mark.
- A row with no issue date must have a note saying "withdrawn", or the run stops; it is written with status withdrawn and dated its receipt.
- A plant (as a slug) given twice with the same date received stops the run. The completed table is the initial renewals: a row's link may point to a later subsequent renewal (Cooper's does), so the link does not classify a row.
- The uprate page must hold exactly one table with the columns PLANT, MWt, DATE APPROVED and TYPE, or the run stops; a row with a number (NO.) is a row of the table, and the page's two total rows (Total MWt and Total MWe) are not. There must be exactly one Total MWt row; it is printed in the header beside the rows' sum, and the two are not required to agree. A percent, MWt or number that does not read stops the run.
- An `event_id` given twice stops the run. Nothing is filled.
- Ceiling: two requests, the pages, each tried up to four times, with 2 seconds after each.

## License

May be public: the NRC's website is a U.S. Government Work, not subject to copyright (read 16, the NRC's verdict in `license_verdicts.csv`); the NRC "would appreciate the courtesy of credit". `license_tables.csv` maps the table to the NRC through the source registry. The table's header: "License: public (the NRC's website is a U.S. Government Work under federal copyright law, read 16)."

## Cross-checks (session 2066)

- Session 2064: the uprates' rows add to 24,146.2 MWt and the page's total row prints 24,089 (and 8,030 MWe); no single row accounts for the 57.2 MWt. By name against `nrc_power_reactors` (130 units), 54 of the 64 renewals and 157 of the 172 uprates match, the others the NRC's other spellings of the same plants. Session 2066 computed the same 24,146.2 from the rows: 3,455.6 + 8,487.6 + 10,875.0 + 1,328.0, by type, as in the table above.
- The counts above were computed from the rows, read past the header lines; 63 + 1 + 172 = 236, the header's counts (license_renewal 64, power_uprate 172).
- The uprates are numbered 1 to 172 with none missing, and the approval date never falls as the number rises.
- In all 63 issued renewals the issue date is after the date received: 505 to 5,973 days, median 762 (the longest Diablo Canyon's, received 24 November 2009, issued 2 April 2026).
- Each uprate's MWt divided by its percent gives the unit's thermal power before the uprate: 1,429 to 3,931 MWt in all 172 rows (median 3,287; the lowest Fort Calhoun's, 80 MWt at 5.6 percent, the highest Palo Verde's, 114 MWt at 2.9 percent), a reactor's size throughout, so the percent and MWt columns are read in their own places.

## What it does not hold

- The subsequent renewals, which the page lists only as links; the planned, received and under-review renewal applications; the uprates under review or expected.
- Electric megawatts: the uprates are MW thermal, and the page's Total MWe is not a row.
- Each unit as its own row: a renewal row names the plant's units together, as the NRC writes them; `entity_ids` names no reactor.
- A reading of the notes: they are kept as the NRC writes them, Diablo Canyon's saying its earlier application was "submitted on November 7, 2018 and withdrawn by the licensee on March 7, 2018".
