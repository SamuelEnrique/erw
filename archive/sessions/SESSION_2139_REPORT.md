# Session 2139 report: the licenses' nineteenth round

23 and 24 October 2026, from 23:58 UTC, on lab-desktop (the data machine), chain 090, unattended. Run beside session 2140's long pull, after 2140's connector was written, so that its publisher is in the round. Model spend USD 0. Pulls: 2 requests of 20.

## Read these first

- **Four verdicts, from reads made in sessions 2134 to 2139** (`warehouse/metadata/license_verdicts.csv`; `license_verdicts.csv` read first, and none of the four had one):
  - **National Interagency Fire Center (NIFC), read 305: may be public.** The WFIGS item's license field is a disclaimer of liability ("The National Interagency Fire Center shall not be held liable for improper or incorrect use of the data...") and places no restriction on use. Its access information names the federal and state wildland fire agencies whose record it is. `wfigs_wildfires` becomes public.
  - **GFZ Helmholtz Centre for Geosciences, read 311: may be public.** The Kp file's own header: "LICENSE: CC BY 4.0". The file asks two citations, both carried in the table's header.
  - **Scripps CO2 Program, read 317: may be public.** Its Usage Restrictions page licenses "data and graphics on scrippsco2.ucsd.edu" CC BY 4.0, with credit to the Scripps Institution of Oceanography at UC San Diego. The monthly file is served from keelinglabsites.ucsd.edu, linked from the site's record page (read 318). The page's asks about disclosing intentions and coauthorship are in the note; neither binds a redistribution.
  - **International Renewable Energy Agency (IRENA), read 321: needs written permission.** Chain 068 could not read IRENA's terms because www.irena.org refused the reader. The chain file asked for them from another address, and IRENASTAT's own page (pxweb.irena.org) states: "© IRENA - International Renewable Energy Agency. All Rights Reserved." That grants no license, so `irena_capacity_annual` stays internal. A license IRENA may grant on www.irena.org is still unread.
- **DOE's LEAD Tool, read 320:** the submission page (data.openei.org/submissions/6219) shows the submission's license, CC BY 4.0, and the OEDI footer: "Content is available under Creative Commons Attribution 4.0 unless otherwise noted". The table (session 2140) is filed under DOE, whose verdict (read 54) already stands, so no new verdict row was written.
- **EPA** has its verdict (read 55), and `epa_ghg_inventory_annual` is public under it.
- **The license record:** 421 tables, 97 publishers with a verdict, 273 requests in the record, 0 problems (`scripts/licenses.py check`). The 646 tests of `tests/test_session205.py` and the release package's tests pass (7 skipped).

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | data.openei.org/submissions/6219 | 200: CC BY 4.0 (its robots file: 404, session 2140) |
| 2 | pxweb.irena.org/pxweb/en/IRENASTAT/ | 200: "All Rights Reserved" (its robots file: 404, session 2085) |

Reads recorded: 320 and 321 (renumbered at session 2147's merge, after chains 069 and 079's).

## Decisions made without you

- **IRENA's verdict from IRENASTAT's own page.** The page that serves the data states its rights, and states them as reserved.
- **NIFC public on a disclaimer that restricts nothing.** The record is a federal interagency one.
- **No new DOE row for the LEAD Tool.** DOE's verdict covers it, and CC BY 4.0 asks only credit, which the table's header gives.

## For Samuel's ruling

- IRENA: whether to write to IRENA (www.irena.org refuses the reader) for its terms. Until then `irena_capacity_annual` stays internal.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_verdicts.csv`, `license_reads.csv`, `license_tables.csv` (rebuilt), `docs/licenses.md`.
- On the data machine only: `runs/c090/s2139/`.
