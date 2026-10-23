# Offshore oil and gas platforms (the Bureau of Ocean Energy Management's platform files)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for a table first written on 23 October 2026.

Tables: `boem_offshore_platforms`

## Publisher and address

Bureau of Ocean Energy Management (BOEM), Data Center, Platform (`https://www.data.boem.gov/Main/Platform.aspx`): three fixed-width files, each read by the layout BOEM publishes beside it: Platform Structures (`/Platform/Files/platstrufixed.zip`, layout `/Main/HtmlPage.aspx?page=platformStructures`), Platform Locations (`platlocfixed.zip`, `page=platformLocations`) and Platform Masters (`platmastfixed.zip`, `page=platformMasters`). Connector: `warehouse/connectors/boem_platforms.py` (session 2007). www.data.boem.gov's robots file names only other readers.

## Vintage and revision

The structures file last modified 1 October 2026, retrieved 23 October 2026. A snapshot (ceiling six requests).

## Shape and variables

Entities, 7,092 rows, one a structure of a complex, in 6,181 complexes. `entity_id` `boem_platform:<complex id>-<structure number>`; `entity_type` platform (Decision 58 of `docs/datastandard.md`); `name` the structure's name (one has none); `geo` US (federal waters); `lat`, `lon` from the locations file (7,084 structures; 8 have no location row); `capacity_mw` empty; `status` retired where BOEM gives a removal date (5,780), else active (1,312); `status_date` the removal date, else the install date (installs from 1942 to 2025); `operator` empty: BOEM gives a company number (`x_company_num`), not a name.

`x_` columns: complex id and structure number, area code and block, district, structure type (fixed 3,796, caisson 2,584, well protector 642, and SEMI, SPAR, TLP, MTLP, MOPU, CT and FPSO as BOEM codes them), install and removal dates, deck and slot counts, major structure flag, authority status; from the complex's masters row, water depth (ft), distance to shore (nautical miles), lease number, field name code, the production, oil production and gas production flags, manned 24 hours, and "to be removed" (BOEM's abandon flag).

## Reading the files

- A layout's start positions and lengths are read from its page, never assumed; a column the connector needs not in the layout, a structure given twice, or a date not as BOEM writes it (DD-MON-YYYY, DD-MON-YY, MM/DD/YYYY, YYYYMMDD) stops the run. Each zip must hold one file.
- A structure with no location row keeps empty coordinates; a complex with no masters row keeps empty complex fields (none here); both counted in the header. Nothing is filled.

## License

Public: BOEM (read 86 of `license_reads.csv`): "materials produced by federal agencies are in the public domain".

## Cross-checks (sessions 2007 and 2009)

- Against `boem_ogor_lease_production_monthly` (BOEM's lease production, to June 2026): of the 335 leases on the masters rows of the 666 active structures flagged producing, 201 report production in 2026. The masters row names one lease for a complex; production from a unit or a neighbouring lease is reported under other leases.
- Session 2009, against the code: `NEED` names the columns taken; the counts computed from the rows.

## What it does not hold

- The platform approvals and removals files, the rig list, and the companies' names.
