# Session 2181 report: the licenses' twenty-second round

24 October 2026, from 01:46 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, run beside session 2180 (whose six notes a helper drafts). Model spend USD 0. Pulls: 7 requests of 20 (below). Also Supabase, for the lock and the archive.

## Read these first

- **This chain's publishers first: three new verdicts.**
  - **Statistics Canada** (may be public in both columns, read 346): the Statistics Canada Open Licence grants "a worldwide, royalty-free, non-exclusive licence to: use, reproduce, publish, freely distribute, or sell the Information". It asks for a notice of source on a value-added product ("Adapted from Statistics Canada ... This does not constitute an endorsement by Statistics Canada of this product"), which both StatCan headers carry.
  - **BSEE** (may be public in both columns): the Interior's notice (read 159), as for ONRR, BLM and Reclamation. Its incident workbooks are its own record, marked "Public Access Level: Public" (read 348).
  - **The FTA** (may be public in both columns, read 359): the license field of the transit fuel and energy dataset's record in DOT DataHub's catalog, `https://www.usa.gov/government-works`, as for the FHWA (read 214). This is session 2182's source.
- **The NRC's verdict is on record** (read 16), and so are EPA's (read 55) and the USGS's (read 87).
- **Sources chosen for the own-choice sessions, so this round could read their terms:**
  - **Session 2182: the National Transit Database's fuel and energy data** ("2022 - 2025 NTD Annual Data - Fuel and Energy", 8ehq-7his on data.transportation.gov). It gives each transit agency's fuel and electricity used, by mode. The ERW holds no transit energy. DOT DataHub's robots file asks a crawl delay of 1 second and does not disallow `/api/views/` (read 355).
  - **Session 2183: EPA's National Electric Energy Data System (NEEDS),** the inventory of generating units behind EPA's power sector model. Its page (read 361) links NEEDS for the 2025 reference case (December 2025). www.epa.gov's robots file does not disallow its pages or `/system/files/` (read 360).
  - **Considered and left:**
    - USGS's thermoelectric water use, on www.sciencebase.gov, whose robots file ends "Block everything for all bots by default" (`User-agent: *`, `Disallow: /`, read 356) after a managed section that allows all. Taken as a bar, not asked further.
    - PHMSA's pipeline incidents, whose host refused the reader before (sessions 554 and 890).
    - The earthquake and geomagnetic sources, which chains 079 and 090 hold.
- **A correction to session 2178:** the NRC's robots file disallows `/docs/` only to two named crawlers (Akamai-SiteSnapshot and Amazonbot). For every reader it disallows only its search pages, `ads.txt` and autodiscover (read 349). The connector's description, the table's header and session 2178's report said `/docs/` was barred to all. They are corrected, and `nrc_rop_findings` was written again (same rows; the archive found no changed row).
- **The record:** 18 reads are added from the chain's probes, sessions 2176 to 2181: 302 to 319 on this branch when written, 344 to 361 since session 2185's merge of main, after chain 094's 302 to 322 and chain 090's 323 to 343 (each read named in this chain's reports is renumbered). `tests/test_session205.py`'s bound was set to main's (raised by chain 094), which held this round on the branch; session 2185's merge raised it by 20 more. The license check shows 439 tables, 101 publishers with a verdict, 317 requests and no problem.

## The pulls

1. `data.transportation.gov/robots.txt` (read 355).
2. `www.sciencebase.gov/robots.txt` (read 356): a bar, as above.
3. and 4. Two searches of DOT DataHub's catalog API (reads 357 and 358): no result on this host.
5. DOT DataHub's `data.json` (read 359): 1,609 datasets, the transit one among them.
6. `www.epa.gov/robots.txt` (read 360).
7. The NEEDS page (read 361).

## Errors

- **Two requests spent on a catalog search** that this host answers empty (pulls 3 and 4). The site's `data.json` listing answered instead.
- **Session 2178's statement about the NRC's robots file was wrong.** It was found here and corrected.
- **The first record wrote "read: ..." as the outcome of the two pages the new verdicts quote.** `tests/test_session205` requires such a read's outcome to be exactly `read`. Corrected.

## Decisions made without you

- **ScienceBase's robots file read as a bar for every reader,** though an earlier group allows all: the file's own words say all bots are blocked by default.
- **The FTA's verdict taken from the dataset record's license field,** as session 2035 took the FHWA's.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed:
  - `warehouse/metadata/license_reads.csv` (302 to 319, 344 to 361 since session 2185's merge);
  - `warehouse/metadata/license_verdicts.csv` (Statistics Canada, BSEE, the FTA);
  - `warehouse/metadata/license_tables.csv` and `docs/licenses.md`;
  - `tests/test_session205.py` (the bound);
  - `warehouse/connectors/nrc_rop_findings.py` (its description and header);
  - `archive/sessions/SESSION_2178_REPORT.md`;
  - the NRC table's rows in `docs/coverage.md`, `coverage.csv` and `archive_manifest.csv`.
- On the data machine only: `runs/c097/s2181/`, `runs/license_reads/s2181/`.
