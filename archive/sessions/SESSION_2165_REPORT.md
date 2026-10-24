# Session 2165 report: coal and oil on the rivers (the Corps of Engineers' waterborne commerce): not taken

24 October 2026, from 00:31 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 3 requests of 15 (below). No table written.

## Read these first

- **The Waterborne Commerce Statistics Center's pages are closed or opaque to the ERW's reader:**
  - www.iwr.usace.army.mil, where the Center's pages live, answers its robots file with HTTP 403, Access Denied, from the same edge server that refused the reader at www.usace.army.mil in session 983 (read 296; read 165). Not asked again.
  - ndc.ops.usace.army.mil, the Navigation Data Center, has no robots file (read 297), and its waterborne commerce publication (`/wcsc/webpub/`) is a script-driven application whose page names no data file, no download and no terms (read 298). Its data come through an interface the scripts call, which is not a published file.
- **The Corps' terms are unread** (the National Inventory of Dams' home page held none, read 166) and are a standing question in the notes of chains 067 and 079 (`usace_nid_dams` is unsettled for the same reason). A table from the Corps would be internal until a ruling even if its files could be reached.
- **No replacement source** in this session: the three sessions of the chain's own choosing (2168, 2169, 2174) can take others.

## The pulls

1. `www.iwr.usace.army.mil/robots.txt` (read 296): HTTP 403.
2. `ndc.ops.usace.army.mil/robots.txt` (read 297): HTTP 404.
3. The waterborne commerce application's page (read 298).

## Errors

- None.

## Decisions made without you

- **The application's interface not reverse-engineered** from its scripts: it is not a published file, and the publisher's terms are unread.

## For Samuel's ruling

- **The Corps of Engineers' waterborne commerce** (and its terms, already a standing question): www.iwr.usace.army.mil refuses the reader; the Navigation Data Center's data are reached only through its application. A person's download of the Waterborne Commerce of the United States tables, or a request to the Center, would open them.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (296 to 298), `docs/licenses.md`.
- On the data machine only: `runs/c094/s2165/`, `runs/license_reads/s2165/`.
