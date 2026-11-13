# Session 3848 report, with 3849: New York's large-load proceeding, the Boston rows' utility, Long Island

Energy Research Warehouse (ERW). Chain 221, data machine (lab-desktop), 13 November 2026 05:49 to 05:55 UTC. Opus 5.5. Model spend USD 0. Requests: 9 in session 3848 (dps.ny.gov 2, documents.dps.ny.gov 1, www.mass.gov 6) and 4 in session 3849 (www.lipower.org, 11 seconds apart under its 10-second crawl delay). Kept at `runs/license_reads/s3848/` and `s3849/` (not in git).

## Read these first

- **No further row closes.** Each of the three rows tried is closed to this reader or states no figure.
- **NYISO, time to connect: the Commission's proceeding states no step yet.**
  - Case 26-E-0045, "Proceeding on Motion of the Commission to Address Interconnection Reforms for Large Loads".
  - The Order Instituting Proceeding and Soliciting Comments (12 February 2026, 14 pages) was read whole. It asks questions about timelines and costs and names NYISO's Transmission Expansion and Interconnection Manual, but states no step with a duration.
  - The other document, the draft scope (comments due 4 November 2026), is a Generic Environmental Impact Statement's scoping document.
  - `large_load_connection_rules` takes a document's steps with their clocks, so nothing was written. The next file reads the case again when the Commission issues a proposal or an order with steps.
- **ISO-NE, transmission and 4CP (the Boston rows, Massachusetts Electric, EIA 11804): closed.**
  - mass.gov's robots file allows this reader outside its media, node and search paths.
  - Its Terms of Use forbid "any copying or use other than fair use" of the material in which the Commonwealth holds the copyright, and ask written permission for any other use. Under ruling 4, a schedule whose only copy were there would be held.
  - In any case, its electric tariffs page links National Grid's own site (closed by National Grid's terms, session 2937). The DPU's File Room is a script-driven application with no document address to name, so it was not searched blindly.
- **NYISO LONGIL (Long Island Power Authority): closed.**
  - LIPA's robots file allows every path (crawl delay 10 seconds).
  - Its Terms of Use (11 March 2024) "permit you to use the Website for your personal, non-commercial use only" and bar reproducing or republishing its material.
  - LIPA's tariff is not on the DPS's Electronic Tariff System (its list of effective electric tariffs names no LIPA or PSEG Long Island entry).

## Decisions made without you

- **A proceeding's order that asks questions adds no row:** only a stated step with its clock does.
- **mass.gov's fair-use clause is read as a request for permission** (ruling 4), as the ERW has read the same words elsewhere.

## For Samuel's ruling

- **Whether to ask mass.gov** (its contact for use beyond fair use) or National Grid for permission to reproduce Massachusetts Electric's filed rates. Default: not asked; the Boston rows read "not held".
