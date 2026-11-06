# BOEM renewable energy leases and grants on the Outer Continental Shelf

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `boem_renewable_leases`

Connector: `warehouse/connectors/boem_leases.py` (session 493).

## Publisher and report

Bureau of Ocean Energy Management (BOEM), Lease and Grant Information (renewable energy): the table of every lease and grant BOEM has executed since its renewable energy program began. The connector reads one page:

`https://www.boem.gov/renewable-energy/lease-and-grant-information`

It parses the HTML tables on the page and takes the one table whose columns are the seven read on 21 October 2026: Lease or Grant Number, Lease or Grant Page, Authorization Resource Type, Resource Type, Lease Effective Year, Lessee or Grantee, Status.

## Vintage and revision rule

The page as BOEM publishes it on the day of the run; it carries no date of its own, and `vintage` is empty. The run of 21 October 2026 (retrieved 18:33 UTC) holds 52 leases and grants: by BOEM's status, Active 34, Cancelled 7, Relinquished 7, Expired 2, Consolidated 2.

The page is fetched fresh on every run (no saved copy is reused) and the table is written with `ip.write_snapshot`: each run replaces the whole table. A lease that leaves BOEM's page leaves the table. Ceiling: one request.

## Shape

Entities. One row per lease or grant.

- `entity_id`: `boem:<lease or grant number>`, lower case with spaces as underscores, for example `boem:ocs-a_0472`.
- `entity_type`: `project`. `name`: the Lease or Grant Page column's title. `geo`: `US` (the page names no state).
- `lat`, `lon`, `capacity_mw`, `status_date`: empty.
- `status`: `active` for BOEM's "Active"; empty for its other words (Cancelled, Relinquished, Expired, Consolidated), which the standard's vocabulary has no word for.
- `operator`: the lessee or grantee.
- `source`, `source_url`, `retrieved_at`, `vintage`.
- Beside them: `lease_number` (BOEM's, for example `OCS-A 0472`), `lessee`, `authorization` (BOEM's Authorization Resource Type with its "*" note mark: Commercial Lease, Interim Policy Lease, Research Lease, Right of Way Grant), `resource_type` (Wind, Marine Hydrokinetic, Marine Hydrokinetic Wind), `effective_year` (the Lease Effective Year, 2009 to 2024 in this run), `boem_status` (BOEM's own word).

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; credit BOEM as the source). The connector's docstring quotes BOEM: "Generally, materials produced by federal agencies are in the public domain" (record 86 of `license_reads.csv`).

## Cross-check

None in the connector. It stops when the page holds no single table with the seven columns, when a status is not in its map, and when a lease number is given twice.

## What it does not hold

- No state, area, acreage, location or capacity: the page names none. Nothing is filled.
- No date beyond the effective year; no status date.
- What the "*" note mark on an authorization means: it is kept as BOEM writes it.
- Oil and gas leases: see `boem_ogor_lease_production_monthly` for production by oil and gas lease.
