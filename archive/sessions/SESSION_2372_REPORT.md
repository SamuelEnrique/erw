# Session 2372 report: Nigeria not taken, and no replacement within the ceiling

24 October 2026, from 08:49 UTC, on lab-desktop (the data machine), the second session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. Precheck passed (`runs/c112/pre2372.out`). Model spend USD 0. Pulls: 12 of 15 to the web hosts, 6 to EIA's API (below).

## Read these first

- **No table this session.** Nigeria's sources and the replacements tried could not be read within the ceiling.
- **Nigeria:**
  - **NERC (nerc.gov.ng):** its robots file allows the reader (read 609). Its site holds fourteen pages and four posts (reads 611 and 613), and its "Statistics and Performance Data" section loads by script with no file linked (read 612). Its quarterly reports were not found.
  - **TCN (www.tcn.org.ng):** its robots file allows every path (read 614). Its site is a theme template's pages with no operational figures (read 615); it links nsong.org.
  - **The system operator's nsong.org** is a dispatch tools login behind a CAPTCHA (read 617). Not asked again.
- **Replacements tried:**
  - **EIA's natural gas routes not held** (one route list, three samples):
    - `natural-gas/move/state` answers only U.S. totals, which the held trade table has.
    - `natural-gas/prod/ngpl` ends in 2021.
    - `natural-gas/prod/off` holds only the Gulf's federal offshore withdrawals, which the held production summary carries.
  - **The Dominican Republic's coordinator (www.oc.do):** its robots file disallows `/Portals/`, where such sites keep their files (read 618). Its operation reports page loads its list by script, with no file linked (read 620).
- The route list's other new routes (coalbed methane, lease condensate, shale gas, wellhead value, supplemental supplies, residential and commercial prices by state) are left for a later session to read for currency.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| nerc.gov.ng | 5 | robots, three sitemaps, the resource page |
| www.tcn.org.ng | 2 | robots, the home page |
| nsong.org | 2 | robots (404), the login page |
| www.oc.do | 3 | robots, the home page, a reports page |
| api.eia.gov | 6 | the gas route lists (4 calls), metadata and samples of three routes |

## Errors

- None.

## Decisions made without you

- **No table written** rather than one from a source whose files could not be found or read.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (609 to 620), `docs/licenses.md`.
- On the data machine only: `runs/c112/s2372/`, `runs/license_reads/s2372/`.
