# Session 2178 report: the NRC's inspection findings (Reactor Oversight Process)

24 October 2026, from about 01:20 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`. Model spend USD 0. Pulls: www.nrc.gov, 5 requests of 15:
- its robots file, in a call of its own;
- the old oversight page (404);
- the NRC Data page;
- the findings workbook;
- its data dictionary.

The trial and the write ran offline from the saved workbook. Also Supabase, for the locks and the archive.

## Read these first

- **One events table, `nrc_rop_findings`:** 18,240 inspection findings and violations at 66 reactor sites, issued 29 July 1999 to 12 May 2025. It comes from the NRC's dataset "Reactor Oversight Process: Findings and Violations", linked from the NRC Data page. Each row is one finding, with:
  - its issue date and the NRC's type (14,779 non-cited violations, 2,320 findings, 855 violations, 128 notices of violation, 107 and 2 at severity IV, 49 apparent violations);
  - its significance color (17,357 green, 609 white, 186 greater than green, 73 yellow, 15 red);
  - the site and its docket (`nrc_reactor:<docket>`, the ids of `nrc_power_reactors`);
  - the procedure, report number, cornerstone, title, cross-cutting aspect and area, who identified it, region, ADAMS accession, traditional enforcement, severity, year, quarter and the report's link.
- **The workbook ends at 12 May 2025.** The NRC last modified it on 2 September 2025 and has not updated it since, so the table holds what the NRC publishes and goes no further. The connector asks again on each run, since the address does not change.
- **Checks in the connector:** the 23 columns the data dictionary lists, or the run stops; no key given twice (docket, report, issue date, procedure, title, type and cornerstone attribute together are unique); every issue date reads. 819 issue dates are held as Excel serial numbers among the dates. They are read as serial numbers, counted in the header, and all agree with the NRC's own Year column (0 of 18,240 differ).
- **The report links point to `/docs/`** (ADAMS documents). They are kept as the NRC prints them and never asked. (Corrected in session 2181: the NRC's robots file disallows `/docs/` only to two named crawlers, Akamai-SiteSnapshot and Amazonbot. For every reader it disallows only its search pages, `ads.txt` and autodiscover. This report first said `/docs/` was disallowed to all. The connector's description and the table's header are corrected, and the table was written again.)
- **The cross-check** (`runs/c097/s2178/cross.py`):
  - 106 of the 108 dockets named are in `nrc_power_reactors`. The two not there are Three Mile Island 1 (05000289) and Pilgrim (05000293), both closed, which that table does not list.
  - All 13 dockets in `nrc_event_notifications` have findings here. The two tables do not overlap in time (the notifications start in May 2025), so no count by plant is compared.
  - The 15 red findings fall at five sites: Browns Ferry, Davis-Besse, Fort Calhoun, Indian Point and Point Beach.
  - Findings a year fell from about 1,000 (2008 to 2012) to 281 (2021) and rose to 523 (2024).
- **Registered:**
  - the sector rule (`power;uranium`, as for the NRC's event reports);
  - both holds;
  - the release package's rows (1 table, 28 variables);
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  No row is given twice in sources, coverage, the archive manifest or the license tables. The license is the NRC's existing verdict, as for `nrc_power_reactors`. The test is `tests/test_session2178.py` (3 tests).

## Errors

- **The NRC's old oversight page** (`/reactors/operating/oversight/listofrxsites.html`) answered 404, costing one request. The data page names the workbook.
- **The first draft of the connector left its publisher and license undefined.** It was found on reading the draft back, before any run.

## Decisions made without you

- **An Excel serial date is read as one**, not refused, since every such date agrees with the NRC's Year column; the header counts them.
- **`event_type` keeps the NRC's codes in lower case** (ncv, fin, vio, nov, ncviv, noviv, av), the header names each, and `status` holds the significance color.
- **Decision numbers:** chain 098 (erw-91) took 71 (`ft`) and 72 (`acre-ft`). This chain uses 70 and then 73 onward.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nrc_rop_findings.py`, `tests/test_session2178.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c097/s2178/`.

## Corrected by session 2185

- **"The two tables do not overlap in time" is wrong.** The findings run to 12 May 2025 and the event notifications start on 7 May 2025, so they overlap for six days. No count by plant was compared.
- **The finding's id hashed the issue date as the workbook stores it,** so a date the NRC changed from an Excel serial number to a date would have given the finding a new id. The key now uses the date as read (YYYY-MM-DD).
- **The table had no `retrieved_at` column,** though its header says each row carries one. It is now kept.
- **18 links have a space or tab after `/docs/`, 21 accession fields hold a note, and 234 are blank.** All are kept as the NRC prints them.

The table was written again in session 2185 (the same 18,240 findings, with new ids).
