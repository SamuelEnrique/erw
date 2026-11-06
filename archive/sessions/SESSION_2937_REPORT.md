# Session 2937 report: the tariff registry, the next utilities

6 November 2026, about 07:17 to 07:24 UTC, on lab-desktop (the data machine), chain 155, unattended. Model spend USD 0. Pulls: 7 requests of the 25 allowed (`runs/s2937/probe.csv`; bodies in `runs/license_reads/s2937/`), robots first at each host and terms before any tariff.

## Read these first

- **No schedule added: each utility's own site bars this table's use, or this reader.** These are the next utilities under the All grids tab's rows that chains 147 to 153 had not read:
  - **Southern California Edison** (the SP15 row, Los Angeles County): robots leaves `/regulatory/` and the files path open, and names no AI agent. But its Website Terms of Use say that content designated for downloading "may be downloaded or copied only for non-commercial, personal use unless otherwise specified", and they forbid bots that load the site. That is AEP's case (session 2872): not read.
  - **Evergy** (the SPP North row, Sedgwick County, Kansas): its robots address answered an F5 bot script with a 404 page. A challenge served in place of the robots file closes the host.
  - **National Grid** (Niagara Mohawk; the NYISO CAPITL, WEST, GENESE and CENTRL rows): there is no robots file (the site's page is served at its address). Its Terms and Conditions say "The content of our site and app may be used for informational purposes only. Any other use ... including the reproduction ... republication ... without our prior written consent is expressly forbidden": not read.
  - **NYSEG** (Avangrid; the WEST and CENTRL rows): the connection was reset at its robots file. Closed.
- **The registry stays at 5 schedules of 4 utilities** (`utility_large_load_tariffs`, 13 rows). Nothing was written.
- **Every utility under the tab's priced rows has now been tried by chains 147 to 155.** Only PG&E's site was open, and no row sits in PG&E's territory. The commissions' own copies are the remaining route: the CPUC for SCE, the KCC for Evergy, the NY PSC for National Grid and NYSEG. Each needs a docket or document address that is not known here.

## Decisions made without you

- **No commission search guessed**, as session 2921 decided. 18 requests were left unspent.

## For Samuel's ruling

- **SCE, National Grid (and Con Edison, Eversource):** whether to ask for written permission, or to read the commissions' docket copies by hand.
- **Hosts closed by this session, not asked again without a ruling:** www.evergy.com (a bot script at its robots address) and www.nyseg.com (the connection reset at its robots file).
