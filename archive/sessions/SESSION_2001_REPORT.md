# Session 2001 report: new reactor applications (the Nuclear Regulatory Commission)

23 October 2026, from 15:06 UTC, on lab-desktop (the data machine), a session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`. Model spend USD 0. Pulls: 15 requests of 15 (www.nrc.gov's robots file, asked in a call of its own and read first: for every reader it disallows only its search pages, ads.txt and autodiscover; the new reactors page, which redirects within the host to `/facilities-safety/new-reactors`; the advanced reactors page; "Who We're Working With"; the application projects list; the pre-application page; one project page; then the trial's eight: the two lists and the six project pages). The write, at 16:24 UTC when the lock was free, reused the saved pages.

## Read these first

- **Two tables written, validated, archived, in coverage (sectors power and uranium, public), in the release package, both holds:**
  - `nrc_new_reactor_applications` (events, 6): the advanced reactor applications under review, each with its applicant, kind, submittal date, place, reactor type, power and milestones: Long Mott Energy's Xe-100 construction permit (31 March 2025, Calhoun County, Texas, 320 MWe; its final safety evaluation targeted for November 2026), TVA's Clinch River construction permit (April 2025; its decision targeted for 28 September 2026), Duke Energy's Belews Creek early site permit (30 December 2025), Pioneer Units 1 and 2's limited work authorization (Palisades SMR, LLC, 31 December 2025), the University of Illinois's KRONOS research reactor (31 March 2026) and Eden Radioisotopes' isotope production reactor (5 May 2026, Lea County, New Mexico).
  - `nrc_advanced_reactor_preapplicants` (entities, 43): the applicants, vendors and research reactors in pre-application engagement, by technology (high temperature gas 12, light water 10, other 9, liquid metal 6, molten salt 5), 11 marked microreactor designs, 2 inactive.
- **The cross-check against `nrc_power_reactors`:** Pioneer Units 1 and 2 are at the Palisades site, whose reactor the list shows operating under Holtec Palisades, LLC; the pre-applicant Energy Northwest operates Columbia Generating Station. No other application names an operating site.
- **No docket numbers:** the pages carry none, and none is made.

## Errors

- **Two trial runs stopped on dates written in words** (Duke's "Application submitted December 30, 2025; ..." and TVA's "April 2025 to present"): the connector now reads the first date in the "When:" line, a month's first day where only a month is given, and keeps the words in `x_when`. Both reruns used the saved pages (no request).
- **The first pre-applicant run marked every row inactive** (the "Inactive Projects" words were found inside a block holding the whole table); the connector now takes only the links after the words.
- **The two tables' metadata patches conflicted** (the connector writes both; each was finished by its own run of `write_table.sh`); resolved with `runs/union_resolve.py`, each table checked once in `coverage.csv`, `archive_manifest.csv`, `docs/coverage.md` and the source row once in `sources.csv`. The first table's release check failed until the second table's rows were added (one difference), then passed.

## Decisions made without you

- **The advanced reactor pages only:** the large light water reactor licensing of earlier years (combined licenses, early site permits, design certifications) and the past licensing activities page are not taken within the ceiling.
- **Pre-applicants as `company` entities**, the technology and the microreactor mark in `x_` columns.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nrc_new_reactors.py`, `tests/test_session2001.py` (6 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c056/s2001/`, `runs/license_reads/s2001/`, `runs/s2001*`, `warehouse/raw/nrc_new_reactors/`.
