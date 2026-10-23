# Session 2086 report: the rural utilities' loans (USDA's Rural Utilities Service): refused, no table

23 October 2026, from 21:10 UTC, on lab-desktop (the data machine), the third session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: 1 request of 15.

## Read these first

- **www.rd.usda.gov refused the reader at its robots file:** HTTP 403, "Access Denied" from its Akamai edge (reference `18.e5a5dc17.1792789853.517adf3e`), on `/robots.txt` itself (read 228). Under the chain's rule a host that refused the ERW's reader is not asked again without a ruling, so the Electric Infrastructure Loan list and the New ERA and PACE selections were not read and no table was written.
- **Added to the refused hosts** for the next file (session 2097 updates it): www.rd.usda.gov.

## Decisions made without you

- **No other address tried:** USDA's selections are announced on www.usda.gov and www.rd.usda.gov; another host serving the same lists would be a new source, for a session that finds one.

## For Samuel's ruling

- Whether to ask USDA Rural Development for access, or read its lists by hand.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (228).
- On the data machine only: `runs/c068/s2086/`, `runs/license_reads/s2086/`.
