# Session 2080 report: the Stanford draft, and the merge with main

23 October 2026, from 20:29 UTC, on lab-desktop (the data machine), the eleventh session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: Redivis's API, 91 requests of 150 (two reconciles stopped at a cap of 6, 12; one plain upload, 72; a reconcile under a cap of 10, 7), and Supabase for the lock.

## Read these first

- **Origin's main merged into this branch first** (chain 057 had landed after the branch was cut): eight files in conflict, resolved.
  - The coverage builder's rules, the holds and the siting review took both sides' lines.
  - The license reads took main's 192 to 195 (chain 057's), and this chain's became 196 to 209 (216 to 229 after chain 058 landed, session 2083), with the two verdicts that cite them (the IESO's read 218, JODI's 229) and the reports of sessions 2070 to 2077 corrected.
  - The release README's list of tables held from the dataset became the union of both sides with its true count, 167: main's line said 158 but listed 163, chain 057's merge having joined the lists without the count.
  - The release check, the license check and the package records agree after.
- **The upload** (`runs/c067/s2080/run.sh`, in the foreground, under the data lock from 20:30 to 20:33 UTC, the main checkout pulled to origin's main first): this chain's four public tables, each proved by the draft's own count: `ieso_ontario_demand_hourly` (31,680), `aeso_alberta_load_hourly` (15,853), `epa_ghgrp_facility_emissions` (70,338), `noaa_ncei_billion_disasters` (403). The run also refreshed the metadata tables from this branch's files: **`erw_coverage` now holds 401 rows, chains 057, 059 and 067's tables among them** (chain 059's upload had left main's 385), `erw_sources` 489, `erw_headers` 3,860 lines. The upload record (4 rows) is carried to the branch.
- **The reconciles:** the first and last stopped at a cap of 6, the reconcile now needing a seventh request for the draft's longer listing; a third under a cap of 10 read 292 tables: 248 match, 44 differ (the tables daily runs have grown since their upload), none missing. It counted only the tables main's upload record lists, so this chain's four, uploaded and proved above, are not in its count.
- **Chain 066's tables are not uploaded here:** chain 066 runs beside this chain, unlanded.
- **The draft holds `epa_ghgrp_facility_emissions` and `noaa_ncei_billion_disasters` with their earlier headers** (session 2079 wrote them again after the upload; their rows are the same).
- The release note is extended. Nothing released.

## Errors

- **The two reconciles under a cap of 6 stopped at their seventh request** (12 requests spent for nothing): the cap was taken from earlier sessions without allowing for the draft's growth.

## Decisions made without you

- **The upload run in the foreground** (chain 059's in the background was stopped for low memory).
- **The README's held list merged as a union with its true count.**

## For Samuel's ruling

- **The Stanford draft:** `erw_coverage` is whole again; chains 058 and 066's tables follow with their own uploads. Do not click before they land.

## Files

- New: this report.
- Changed: the merge's files (above), `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c067/s2080/`, `runs/c067/merge_*`, `runs/c067/reads_mapping.json`.
