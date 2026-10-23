# New reactors: the advanced reactor applications under review and the pre-applicants (the Nuclear Regulatory Commission)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for tables first written on 23 October 2026.

Tables: `nrc_new_reactor_applications`, `nrc_advanced_reactor_preapplicants`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC), Advanced Reactors, "Who We're Working With": the list of advanced reactor application projects (`https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects`) and each project's page linked from it, and the pre-application activities page (`.../who-were-working-with/pre-application-activities`). Connector: `warehouse/connectors/nrc_new_reactors.py` (session 2001). The NRC's robots file disallows only its search pages, ads.txt and autodiscover for every reader.

## Vintage and revision

The pages as read on 23 October 2026 (the application list last reviewed 18 June 2026, the pre-application page 22 October 2026). Snapshots (ceiling eight requests on that day: the two lists and six project pages).

## Shape and variables

`nrc_new_reactor_applications`: events, 6 rows, one an application under review. `event_id` `nrc_app:<the page's name>`; `event_date` the application's submittal (the "When:" line's first date, a month's first day where it gives only a month, as for TVA's "April 2025 to present"; `x_when` keeps the words); `event_type` construction_permit_application (4), early_site_permit_application (1, Duke Energy at Belews Creek), limited_work_authorization_application (1, Pioneer Units 1 and 2); `parties` the applicant; `mw` the electric power the page states (Long Mott's 320 MWe), else empty; `status` the latest milestone marked done (A), `x_status_date` its date; `x_next_milestone` and `x_next_target`, the first marked a target (T) or TBD; `x_decision` and `x_decision_target`, the permit decision's row; `x_project` the page's title; `x_reactor_type`, `x_power_level`, `x_fuel`, `x_place` and `x_state` as written. Dates from 31 March 2025 to 5 May 2026.

`nrc_advanced_reactor_preapplicants`: entities, 43 rows, one an applicant, vendor or research reactor the pre-application table lists. `entity_id` `nrc_preapp:<the page's name>`; `entity_type` company; `name` as the table writes it; `x_technology` the table's column (high temperature gas 12, light water 10, other or not specified 9, liquid metal 6, molten salt 5, none 1); `x_microreactor` yes for the table's "*" (11); `x_active` no for the two "Inactive Projects" named after the table (Westinghouse eVinci, which is in no column, and Shepherd Power).

## Reading the pages

- The application pages are read by their "Who:", "What:", "When:" and "Where:" rows, the "Plant Characteristics" table and the "Milestones" table; a page with no "Who:" or no date of submittal stops the run, as does a list linking more than twelve projects (a ceiling to raise on purpose).
- The pages carry no docket numbers; none is made. A field a page leaves out stays blank (TVA's, Duke's and Pioneer's pages give no "Where:"). Nothing is filled.
- A link's text is kept as written: the NRC's "Advance Energy Bridge (AEB)" links to its Nuclear Vault System page.

## License

Public: the NRC's site disclaimer (read 16 of `license_reads.csv`): "a U.S. Government Work ... not subject to copyright".

## Cross-checks (sessions 2001 and 2009)

- Against `nrc_power_reactors`: Pioneer Units 1 and 2 (Palisades SMR, LLC, a Holtec company) are at the Palisades site, whose reactor the list shows operating under Holtec Palisades, LLC; the pre-applicant Energy Northwest operates Columbia Generating Station. No other application names an operating site.
- Session 2009, against the code: `KINDS`, `TECHNOLOGIES` and the milestone rules are as above; the counts computed from the rows.

## What they do not hold

- The large light water reactor licensing (combined licenses, early site permits and design certifications of earlier years), the past licensing activities page, each project's documents and dockets.
