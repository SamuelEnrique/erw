# The Grid Resilience and Innovation Partnerships selections, a project (DOE's GRIP Program Projects)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2050).

Tables: `doe_grip_selections`

## Publisher and address

U.S. Department of Energy (DOE), Office of Electricity (GRIP moved there from the Grid Deployment Office; the `/gdo/` addresses answer at `/oe/` ones), Grid Resilience and Innovation Partnerships (GRIP) Program Projects, `https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects`. The page draws its list by script from its own settings (`drupal-settings-json`, `datatableRows`), and the rows are read from there. Each round's announcement date is read from the three program pages: `https://www.energy.gov/oe/grid-resilience-utility-and-industry-grants`, `https://www.energy.gov/oe/smart-grid-grants`, `https://www.energy.gov/oe/grid-innovation-program`. Source id `doe:grip_selections`. Connector: `warehouse/connectors/doe_grip.py` (session 2050).

## Vintage and revision

The page says its content "reflects information available as of December 2024". The projects page was retrieved 2026-10-23T19:08:05Z; the table was written by run `20261023T192455Z` from the saved pages. Its data rows are identical, line for line, to the trial's (`runs/c059/s2050/trial/doe_grip_selections.csv`, run `20261023T190957Z`), as the write reused the same saved pages.

The table is a snapshot, written whole each run; all four pages are asked fresh each run (unless `--offline`).

## Shape and variables

Events, 105 rows, one a project. `event_id` `doe_grip:<round>:<12 hex of the SHA-1 of program|applicant|project>`, our own (DOE gives none), stable while DOE keeps the names; `event_date` the round's announcement for the program (also `x_announced_on`, with the page it was read from in `x_dates_from`); `event_type` grip_selection; `parties` the applicant or selectee; `status` DOE's, lower-cased; `entity_ids`, `mw`, `price`, `currency` empty.

| Round | Program | Announced | Projects | Federal share, USD |
|---|---|---|---|---|
| first | Grid Innovation Program | 2023-10-18 | 8 | 1,439,896,327 |
| first | Grid Resilience Utility and Industry Grants | 2023-10-18 | 16 | 919,420,073 |
| first | Smart Grid Grants | 2023-10-18 | 34 | 1,106,321,478 |
| second | Grid Innovation Program | 2024-08-06 | 8 | 2,229,626,313 |
| second | Grid Resilience Utility and Industry Grants | 2024-10-18 | 15 | 915,698,447 |
| second | Smart Grid Grants | 2024-10-18 | 24 | 1,073,623,306 |

- Federal share USD 7,684,585,944 in all, recipient share USD 14,969,455,142 (1.95 times the federal); neither is blank in any row. The largest award is the Montana Department of Commerce's North Plains Connector Interregional Innovation (Grid Innovation Program, second round), USD 700,000,000; the smallest the City of Naperville's (Smart Grid Grants), USD 1,116,174.
- `status`: awarded 60, selected 44, withdrawn 1 (Algonquin Power Fund America Inc., Smart Grid Grants, first round, USD 42,905,918, Illinois and Texas).
- `x_states` the postal codes joined by ";" (32 projects name more than one; 51 codes in all, the 50 states and DC); `x_state_names` DOE's names as listed.

## Reading the source

- A field not in the connector's list of ten, an amount not of the form `$1,234,567`, a round or program without its announcement date, or a project (program, applicant, project, round) given twice stops the run.
- The dates are read from each program page's "First Funding Opportunity ... On <date>" and "Second Funding Opportunity ... On <date>"; the first date given for a round is kept.
- Values as DOE publishes them, whitespace collapsed; a blank stays blank.
- Ceiling: four requests (the projects page and the three program pages).

## License

`license_verdicts.csv` records the U.S. Department of Energy (DOE), read 54: "may be public", for public and for commercial use: "Government information at DOE websites is in the public domain. [...] it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." `license_tables.csv` maps the table to the Department (the source registry), and `docs/licenses.md` gives it "may be public", agreeing with the flag; `sources.csv` names the source's license as public.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines; the six round and program counts match the header's, and the federal shares sum to the header's USD 7,684,585,944. No `event_id` is given twice; the rows are in (event_date, program, parties, event_id) order.
- Against DOE's announcements as session 2050's report quotes them: the first round's 58 projects sum to USD 3.466 billion ("up to $3.46 billion ... for 58 projects"); the second round's Grid Innovation Program to USD 2.230 billion ("$2.2 billion ... for eight projects"); its other two programs to USD 1.989 billion over 39 projects ("nearly $2 billion for 38 projects"). The extra project is untraced; none of the 39 is withdrawn (selected 35, awarded 4).

## What it does not hold

- The State and Tribal Formula Grants (session 2050 found no page for them).
- Award dates and amounts as negotiated: the announcement date and DOE's listed shares only.
- Any round after the second, and any change after December 2024 that the page does not show.
