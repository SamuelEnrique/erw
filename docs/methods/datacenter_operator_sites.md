# Datacenter sites from the operators' own public lists

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 28 September 2026 (session 22).

Tables: `datacenter_operator_sites`

## Publisher and address

Nine operators' public pages, one connector each in `warehouse/datacenters/operators/` (`aws.py`, `azure.py`, `google.py`, `meta.py`, `oracle.py`, `digital_realty.py`, `equinix.py`, `vantage.py`, `switch.py`), run together by `warehouse/datacenters/operators/run.py` (session 22) with shared rules in `common.py`. `warehouse/run_daily.sh` runs it weekly with the queues, on Mondays (UTC) or with `QUEUES=1`.

| Operator | Source id | Address read |
|---|---|---|
| Amazon Web Services | `aws:locations` | `https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json` |
| Microsoft | `microsoft:azure-geographies` | `https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/` |
| Google | `google:datacenter-locations` | `https://datacenters.google/locations/` |
| Meta | `meta:datacenter-locations` | `https://datacenters.atmeta.com/all-locations/` |
| Oracle | `oracle:public-cloud-regions` | `https://www.oracle.com/cloud/public-cloud-regions/` |
| Digital Realty | `digitalrealty:data-centers` | `https://www.digitalrealty.com/data-centers` and each facility's page |
| Equinix | `equinix:us-data-centers` | `https://www.equinix.com/data-centers/americas-colocation/united-states-colocation` and its pages |
| Vantage Data Centers | `vantage:data-center-locations` | `https://vantage-dc.com/data-center-locations/` |
| Switch | `switch:locations` | `https://www.switch.com/colocation/` |

Three operators are skipped and their pages read each run only to log what they hold: QTS (the site redirects to q.com, which answers HTTP 503), CoreWeave (the region list is behind a login) and Crusoe (fleet totals only). Requests carry a plain browser User-Agent and pause 0.5 seconds; every answer is saved under `warehouse/raw/datacenter_operators/<run_id>/`.

## Vintage and revision

One snapshot, run `20261012T144848Z` (12 October 2026); every row's `retrieved_at` is 2026-10-12T14:52:31Z and `vintage` 20261012. Header: "File holds 275 rows, one snapshot; the previous file held 275 rows."

Each full run replaces the table (`write_snapshot`): a site an operator no longer lists leaves it. A run with `--only` replaces only those operators' rows and keeps the others from the last table. An operator whose connector fails is missing from that run's table, and the run log and run status say so. Sites repeated within a run (same operator, type and code) are kept once.

## Shape and variables

Entities, 275 rows, one per site; `entity_type` datacenter, `kind` operator. `entity_id` `dcsite:` plus the first 16 hex digits of the SHA-1 of `operator|site_type|operator_code` (the name where there is no code). `site_type`: facility 147, campus 89, region 38, announced_site 1.

| Operator | Sites | Type | With a state | Placed (`geo_precision`) | With MW |
|---|---|---|---|---|---|
| Digital Realty | 74 | facility | 71 | 74 operator | 0 |
| Equinix | 73 | facility | 44 | 42 place, 31 none | 0 |
| Google | 52 | 43 campus, 9 region | 52 | 9 operator, 29 place, 13 county, 1 none | 0 |
| Meta | 28 | campus | 28 | 24 place, 1 county, 3 none | 0 |
| Microsoft | 19 | 18 region, 1 announced_site | 5 | 19 none | 0 |
| Vantage Data Centers | 13 | campus | 13 | 12 place, 1 county | 12 |
| Amazon Web Services | 7 | region | 4 | 7 none | 0 |
| Switch | 5 | campus | 5 | 4 place, 1 none | 3 |
| Oracle | 4 | region | 0 | 4 none | 0 |

`state` is filled on 222 rows, 33 states (CA and VA 35 each, TX 33); `geo` is `US-<state>`, or US on the 53 rows without one. `lat` and `lon` are filled on 209 rows: the page's own coordinates (`operator`, 83), or the Census gazetteer's internal point of the stated place (111) or county (15); 66 rows are not placed, with the reason in `geo_note` ("no US state stated" 50, "no county or city stated" 10, and others). `status`: Google operating 23 and planned 20 (its `inDevelopment` flag), Oracle operating 4 (its "Live"); empty on the other 228 rows. `status_date` is empty on every row.

`capacity_mw` equals `mw` and is filled on 15 rows, 4,799 MW in all, each with the exact words in `mw_span`: Vantage 12 rows, 3,917 MW ("critical IT load"), Switch 3 rows, 882 MW ("up to ... MW of power"). The two operators state different quantities; a sum across them mixes IT load and power.

## Reading the source

- A state is kept only when the page names it (a full name, a postal code, or a state after a direction such as "N. Virginia"); a region named by a direction or a city keeps its words in `place_text` and has no state.
- MW is kept only when its span is in the page's visible text and states exactly one MW or GW figure (GW times 1,000).
- A status is kept only where the page states one (Oracle's Live or Coming soon, Google's `inDevelopment`).
- A non-200 answer is retried three times, five seconds apart, and then fails that operator; the others continue. A run with no facility from any connector writes nothing.

## License

`license_tables.csv` lists the table under the nine operators. `license_verdicts.csv` records each as "needs written permission": Amazon Web Services (read 32), Google (35), Meta (36), Microsoft (37), Oracle (38) and Vantage Data Centers (40) by a sentence of their terms; Digital Realty (33), Equinix (34, HTTP 403) and Switch (39) not read, permission by default. `docs/licenses.md` lists the table as flagged public, "ruled: license needed from 2026-10-21", ERW verdict unsettled, and names no person to write to at any of the nine. The table's header says "License: public (facts from the operators' public pages)."

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines. The `entity_id` rule, recomputed from each row's operator, type and code or name, gives the row's id in 275 of 275.
- Every one of the 15 `mw_span` values states one figure that equals its `mw`; every one of the 209 placed rows lies within latitude 18 to 72 and longitude -180 to -65.

## What it does not hold

- QTS, CoreWeave, Crusoe, and any operator not in the nine.
- Sites outside the United States: eight connectors keep US entries only, and Switch's five campuses all name a US state.
- AWS Local Zones and Wavelength Zones, which `aws.py` leaves out.
- Capacity for any site whose page states none, and any status date.
- Sites named only in the news: `datacenter_facilities` joins this table with `datacenter_projects` (`license_tables.csv`).
