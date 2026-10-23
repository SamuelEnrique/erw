# Disaster declarations and their designated areas (FEMA's OpenFEMA Disaster Declarations Summaries)

Energy Research Warehouse (ERW), method note written in session 2066 (chain 066) for a table first written on 23 October 2026 (session 2056).

Tables: `fema_disaster_declarations`

## Publisher and address

Federal Emergency Management Agency (FEMA), OpenFEMA Dataset: Disaster Declarations Summaries, version 2 (`https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2`), the whole data set as one CSV: `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv`. Source id `fema:openfema_disaster_declarations_v2`. Connector: `warehouse/connectors/fema_disasters.py` (session 2056). www.fema.gov's robots file (read 196) disallows no path under `/api/open/` and asks a crawl delay of 15 seconds.

## Vintage and revision

The file retrieved 23 October 2026 19:55:36 UTC (25,012,314 bytes, 70,572 rows, declarations from 2 May 1953 to 17 October 2026, its newest `lastRefresh` 23 October 2026 11:05 UTC), written by run `20261023T201255Z` from the saved file (`--offline`). FEMA sends no Last-Modified, so `vintage` is empty in every row.

Each run that is not `--offline` downloads the whole set again, and the table is written whole each time (a snapshot): a declaration closed since the last run changes its `status`, and a row FEMA no longer gives leaves the table. Rows declared before the start date (`--since`, 1 January 2015 by default) are left out.

## Shape and variables

Events, 26,199 rows, one a declaration and designated area, `event_id` `fema:<femaDeclarationString>:<state FIPS><county FIPS>:<place code>`, each once. `event_date` the declaration date, 7 January 2015 to 17 October 2026; `parties` FEMA; `mw`, `price` and `currency` empty.

| `event_type` | FEMA's type | Rows | Declarations | Declarations closed |
|---|---|---|---|---|
| major_disaster | DR | 14,950 | 750 | 107 |
| emergency | EM | 10,470 | 288 | 224 |
| fire_management | FM | 779 | 596 | 225 |
| all | | 26,199 | 1,634 | 556 |

| Column | Form |
|---|---|
| entity_ids | `US-<state>`, and `;fips:<state><county>` where the county code is not 000 (25,286 rows); the 913 rows with county code 000 have the state only (3 of them "Statewide", the rest reservations, tribes and other areas) |
| status | closed where FEMA gives a closeout date (9,733 rows), else open (16,466) |
| x_incident_type | FEMA's incident type: Biological 7,857 rows (167 declarations, 13 March 2020 to 28 March 2021), Hurricane 5,282, Severe Storm 4,700, Flood 2,768, Winter Storm 1,378, Tropical Storm 1,199, Severe Ice Storm 1,068, Fire 986, and 13 others |
| x_title, x_state, x_designated_area | as FEMA writes them; 56 states and territories (the 50 states, DC, PR, VI, GU, AS, MP) |
| x_incident_begin, x_incident_end | UTC days; the begin in every row (25 April 2014 to 16 October 2026), the end empty in 280 rows (156 declarations) |
| x_programs | the programs declared, joined by ";": PA 25,683 rows, HM 14,197, IH 6,965; IA in none since 2015 |
| x_disaster_number, x_region | FEMA's disaster number; FEMA region 1 to 10 |
| x_tribal | 1 for a tribal request (172 rows), else 0 |

Rows a year of declaration: 963 (2015), 1,194, 1,668, 1,184, 1,666, 9,712 (2020), 1,962, 1,141, 1,119, 2,364, 1,203 and 2,023 (2026 to 17 October).

## Reading the file

- Every one of the 20 columns the connector reads (`NEED`) must be in the file, or the run stops.
- A declaration date that is empty or does not read stops the run; an incident begin, incident end or closeout date that is empty is left empty, and one that does not read stops the run. Dates are kept as UTC days.
- A declaration type other than DR, EM or FM stops the run.
- The state code is padded to two digits and the county code to three; the place code is kept as FEMA writes it (one to five digits).
- A program counts as declared, and a request as tribal, where FEMA's flag is "1", "True" or "true".
- An `event_id` given twice stops the run; no declaration on or after the start date stops it too. Nothing is filled.
- Ceiling: one request, the whole set, tried up to four times, with 15 seconds after it as the robots file asks.

## License

May be public, with FEMA's statement. OpenFEMA's terms (read 197, FEMA's own verdict in `license_verdicts.csv`, session 2061) ask the endpoint and the time retrieved to be cited and the statement "This product uses the Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA. The Federal Government or FEMA cannot vouch for the data or analyses derived from these data after the data have been retrieved from the Agency's website(s).", and forbid FEMA's and DHS's logos and seals; the terms also let FEMA ask a user to cease using the data. The table's header: "License: public (OpenFEMA's terms)." followed by the statement. `license_tables.csv` maps the table to FEMA through the source registry.

## Cross-checks (session 2066)

- Session 2056: of FEMA's hurricane and severe storm major disasters with incident dates (358, 2015 to 2026), 334 (93 percent) have NCEI storm events in the same state within the incident's dates, and 132 (37 percent) a DOE-417 weather event naming the state, DOE-417 reporting only large outages. Session 2066 counted the same 358 declarations from the rows (77 hurricanes, 281 severe storms) and the same yearly spread (0 to 13 hurricane and 13 to 40 severe storm major disasters a year, 40 severe storms in 2024).
- The counts above were computed from the rows, read past the header lines. 14,950 + 10,470 + 779 = 26,199 and 750 + 288 + 596 = 1,634, the header's counts; the saved file holds 26,199 rows declared on or after 1 January 2015, and the rows of each of the 1,634 declarations number the same in the file and the table.
- The two letters of each `femaDeclarationString` match its `event_type` in all 26,199 rows, its number `x_disaster_number` and its state `x_state`. Within a declaration the date, type, state, title, incident type, incident begin, status and region are the same in every row.
- The incident end is never before the incident begin. The incident begins after the declaration in 162 rows, emergencies and fire management declared ahead of the incident (EM-3403-VA, declared 11 September 2018 for a hurricane beginning 13 September, for one).
- The 913 rows without a county FIPS are exactly the rows whose county code is 000.

## What it does not hold

- Declarations before 2015 (FEMA's set runs from 1953).
- FEMA's other columns: the fiscal year, the request number and date, the last IA filing date, the incident id, the designated incident types, `lastRefresh`, `hash` and `id`.
- Assistance amounts, applicants or projects: declarations only.
- A county FIPS for a statewide, tribal or other area whose county code is 000.
