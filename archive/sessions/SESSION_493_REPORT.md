# Session 493 report: BOEM's offshore renewable energy leases

21 October 2026, from 17:45 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/022-evening-21-october-sources.md`. Model spend USD 0.

## Read these first

- **A new host, read first**:
  - `www.boem.gov/robots.txt` is a standard Drupal file: admin, user and search paths closed, content open.
  - BOEM's terms page was read into the record (record 86, `about-boem/copyright-restrictions-and-permissions`, 200): "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission. However, not all materials appearing on this web site are in the public domain. Some materials have been donated or obtained from individuals or organizations and may be subject to restrictions on use."
  - Verdict "may be public", since the lease table is BOEM's own record, written to `license_verdicts.csv`; `docs/licenses.md` written again (68 publishers, 84 requests, 0 problems).
- **The source**: the table on BOEM's Lease and Grant Information page: 52 leases and grants since the program began, each with number, page title, authorization, resource, effective year, lessee and status. The page names no state, area or acreage.
- **`warehouse/connectors/boem_leases.py`**:
  - an entities table `boem_renewable_leases`: entity_id `boem:<lease number>`, entity_type `project`, operator the lessee;
  - BOEM's status kept in `boem_status` (Active 34, Cancelled 7, Relinquished 7, Expired 2, Consolidated 2). The standard's `status` is `active` for Active and empty for the four words it has no equal for (forcing them into "withdrawn" or "retired" would misstate them);
  - an unknown status, a repeated lease number or a changed table stops the run;
  - the sector rule and `tests/test_session493.py` (4 tests).
- **Trial**: 52 rows; the validator passes.
- **No cross-check that means anything**: `energy_projects` holds no BOEM lease numbers. A loose match on lessees' first words (45 of 52) is not a check, and is not counted as one; joining the two needs a crosswalk.

## To finish (session 489's part, when the lock is free)

`python warehouse/connectors/boem_leases.py`, the validator, `build_coverage.py --only '^boem_renewable_leases$'`, `archive.py write --tables '^boem_renewable_leases$'`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.boem.gov | 4 | robots file, the copyright page (record 86), the lease page twice |

## Files

- New: `warehouse/connectors/boem_leases.py`, `tests/test_session493.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `license_reads.csv`, `license_verdicts.csv`, `docs/licenses.md`, `scripts/licenses.py`.
