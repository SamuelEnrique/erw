# Session 2505 report: Cyprus's electricity, not taken (CYSTAT's database holds no electricity table; TSO Cyprus's figures not reached); Tonga's table too old

24 October 2026, about 17:41 to 17:46 UTC, on lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2505.out`). Model spend USD 0. Pulls: 13 requests of 15 (12 by the probe, 1 by a fetch).

## Read these first

- **The ERW holds no Cypriot national source** (`sources.csv` searched for Cyprus, TSOC and CYSTAT); Eurostat's tables hold Cyprus among the EU's countries.
- **TSO Cyprus** (tsoc.org.cy) has no robots file (read 875). A web search found no download of its figures, and its site was not searched further within the ceiling.
- **The Statistical Service of Cyprus (CYSTAT):**
  - no robots file on www.cystat.gov.cy or cystatdb.cystat.gov.cy (reads 876, 881);
  - its energy theme and predefined tables hold petroleum products only (reads 878, 879);
  - its PxWeb database (CYSTAT-DB) has six energy tables, all petroleum products, and its industry folder holds indices (reads 882 to 885);
  - its terms of use are a disclaimer (read 880). Its "Data Reusability" page, read in session 2509, allows reuse for any purpose with the source acknowledged.
- **Not taken:** no CYSTAT table of electricity was found.
- **A replacement was tried within the ceiling:** the Tonga Statistics Department's "Energy and water statistics" (its robots file closes `/wp-admin/` and SemrushBot only, read 886). The file was fetched once: its electricity table covers 1991/92 to 2003/04, printed rotated. Not taken: too old to add what Ember's table does not hold.

## Requests (13 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | tsoc.org.cy and www.cystat.gov.cy robots files | 404 |
| 3 to 6 | CYSTAT's home, energy theme, energy tables, terms of use | 200 |
| 7 | cystatdb.cystat.gov.cy/robots.txt | 404 |
| 8 to 11 | CYSTAT-DB's databases, subjects, energy and industry folders | 200: no electricity table |
| 12 | tongastats.gov.to/robots.txt | 200 |
| 13 | Tonga's energy and water statistics (a fetch) | 200, 62 kB: 1991/92 to 2003/04 |

Reads recorded: 875 to 886 (on this branch). Two web searches (TSO Cyprus's data, CYSTAT's tables) reached no publisher's host. Test 205's bound was raised by 40 for chain 122's reads.

## Decisions made without you

- **No table for Cyprus** rather than figures from an aggregator; **none for Tonga** from a 2004 table.

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 875 to 886), `docs/licenses.md`, `tests/test_session205.py` (its bound). New: this report.
- On the data machine only: `runs/c122/s2505/`, `warehouse/raw/tongastats_energy/`.
