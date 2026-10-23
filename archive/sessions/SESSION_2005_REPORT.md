# Session 2005 report: the licenses' tenth round

23 October 2026, from 15:18 UTC, on lab-desktop (the data machine), a session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`. Model spend USD 0. Pulls: 2 requests of 20 (Reclamation's Disclaimer and Notices pages; www.usbr.gov's robots file was read in session 2003); sessions 2000 to 2003's five robots reads recorded with them (reads 167 to 173).

## Read these first

- **This chain's one new publisher is the Bureau of Reclamation.** The Department of Energy (read 54), the NRC (read 16) and ERCOT (read 2) have verdicts; ERCOT published no table (session 2002).
- **One verdict: "U.S. Bureau of Reclamation (USBR)", may be public** (read 172). Reclamation's Disclaimer page: "The Bureau of Reclamation is part of the U. S. Department of the Interior and therefore utilizes the same Disclaimer Policy". The Department's notice is read 159, on which ONRR and BLM are "may be public" (session 956): "Generally, materials produced by federal agencies are in the public domain ... not all materials appearing on this web site are in the public domain. Some materials have been donated". The plant performance workbook (`usbr_hydropower_monthly`) is Reclamation's own record of its own plants, not donated material.
- **Recorded:** www.energy.gov (2000), www.nrc.gov (2001), www.ercot.com (2002), data.usbr.gov and www.usbr.gov (2003), and this session's two pages. data.usbr.gov's file disallows `/rise/api` and the time series queries, which is why session 2003 took Reclamation's workbook instead of RISE.
- **The record's bound is not raised:** `tests/test_session205.py` allows 183 reads; the record holds 173.
- **`license_tables.csv` gains this chain's four tables when they are written** (each table's finish step runs `licenses.py tables`, `write` and `check`).

## Errors

- **The verdict's read first carried a descriptive outcome** ("read: ..."); `test_session205` requires a read behind a quoted sentence to be exactly "read". Reads 172 and 173 are "read"; the robots reads keep their descriptions, as reads 161 and 162 do.

## Decisions made without you

- **Reclamation's verdict follows the Department's notice,** as ONRR's and BLM's do, since its own page defers to it.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (167 to 173), `license_verdicts.csv` (Reclamation), `docs/licenses.md`.
- On the data machine only: `runs/c056/s2005/`, `runs/license_reads/s2005/`.
