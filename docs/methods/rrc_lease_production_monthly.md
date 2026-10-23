# Texas oil and gas production by lease, Martin County, monthly

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 30 September 2026.

Tables: `rrc_lease_production_monthly`

## Publisher and address

Railroad Commission of Texas (RRC), Production Data Query dump (`PDQ_DSV.zip`), from the RRC's public file share:
`https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d` (a page whose form is posted to stream the zip).
The table read is `OG_COUNTY_LEASE_CYCLE`, each lease's production in each county and month as its operator reported it.
Connector: `warehouse/connectors/rrc_production.py` (session 49, approved pull e). Page (the data sets page):
`https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/`.

## Vintage and revision

Monthly. Held from coverage.csv: 2024-08-01 to 2026-07-01, last run 2026-10-01T04:46:13Z. The connector takes the
latest 24 production months the dump holds. The dump was downloaded 2026-10-01T04:38:43Z (3,847,917,794 bytes, SHA-256
in the header); `vintage` on every row is the dump's oil extract date, 18-SEP-26 (2026-09-18T00:00:00Z).

A snapshot: the connector deletes the old file and writes the dump's 24 months whole, since the dump revises. The
header warns that recent months may be incomplete, because operators file late and the RRC revises. No scheduled job
runs it: `--download` fetches the dump, otherwise the newest saved dump is read. The ceiling is 500,000 rows; the run
wrote 212,252. Not written: 8,343 lease-months with no report filed (`PROD_REPORT_FILED_FLAG` not Y). A filed zero is
written.

The pilot county is Martin, the county of the Permian districts (08, 7C, 8A) with the most oil over these months in the
dump's `OG_COUNTY_CYCLE` (Martin 510,799,965 bbl; Midland 482,773,827 bbl; Loving 222,533,157 bbl).

## Shape and variables

Series. `entity` `rrc:<oil or gas code>-<district no>-<lease no>`, the RRC's lease id (a gas lease is one gas well).
`ts_utc` the production month's first day; `freq` `P1M`; `geo` `US-TX`; `source` `rrc:pdq_dump`. Key (`entity`,
`variable`, `ts_utc`).

| Variable | Lease | Unit | RRC column |
|---|---|---|---|
| `oil_bbl` | oil (O) | `bbl` | `CNTY_LSE_OIL_PROD_VOL` |
| `casinghead_gas_mcf` | oil (O) | `Mcf` | `CNTY_LSE_CSGD_PROD_VOL` |
| `gas_mcf` | gas (G) | `Mcf` | `CNTY_LSE_GAS_PROD_VOL` |
| `condensate_bbl` | gas (G) | `bbl` | `CNTY_LSE_COND_PROD_VOL` |

Values are the RRC's whole barrels and thousand cubic feet as operators report them (the RRC's manual calls them
"estimated" values).

| x_* field | Holds |
|---|---|
| `x_county` | the county (MARTIN) |
| `x_district` | the district's name (08, 7C, 8A); the entity carries the district number (10, 09, 11) |
| `x_oil_gas_code` | O or G |
| `x_lease_no`, `x_lease_name` | the lease |
| `x_operator_no`, `x_operator_name` | the operator that reported the month |
| `x_field_no`, `x_field_name` | the field |
| `x_gas_well_no` | the gas well number, gas leases only |
| `x_wells` | the wells the RRC lists on the lease in `OG_WELL_COMPLETION` (any status, any county) |

As of 23 October 2026: 212,252 rows, 4,828 leases (4,819 oil, 9 gas), 24 months, 51 field numbers, 71 operator
numbers (683 leases have more than one operator over the months).

| Variable | Rows | Sum over the 24 months |
|---|---|---|
| `oil_bbl` | 105,935 | 510,799,965 bbl |
| `casinghead_gas_mcf` | 105,935 | 1,501,080,996 Mcf |
| `gas_mcf` | 191 | 8,853,401 Mcf |
| `condensate_bbl` | 191 | 1,142,543 bbl |

- Districts: 08 holds 209,998 rows, 8A 2,242, 7C 12.
- 47,947 values are zero; none is negative.
- Oil by month: 21,998,220 bbl in 2024-08, 19,833,432 bbl in 2026-07; rows a month from 8,264 to 9,298.
- `x_wells`: 1 to 919 (lease `rrc:O-10-04010`, MABEE UNIT); 2,714 leases list one well.
- The field SPRABERRY (TREND AREA) holds 497,153,070 bbl of the oil.

## License

ERW verdict (docs/licenses.md, "Every table"): verdict today "may be public"; flag in coverage.csv "public"; flag and
verdict "agrees"; if the ERW sells anything "needs written permission"; ERW verdict "public". The RRC's page (read 19):
"RRC grants permission to copy and distribute the information on its website for noncommercial use, as long as the
content remains unaltered and is not presented in a misleading way." Public since session 324 (internal before; the
header's first line still says "internal"). Noncommercial use only. Cite "Railroad Commission of Texas, Production
Data Query dump", with the extract date; the Commission asks for acknowledgment.

## Cross-check

None in the connector.

## What it does not hold

- One county only (Martin), and 24 months only: the approved pilot.
- No well-level production: the RRC reports by lease, so a lease of several wells is one entity (`x_wells` says how
  many).
- A lease's production in another county is not here: the rows are this county's share.
- No lease-month without a filed report; nothing is filled.
- Not in the live set: session 49 left it out of Supabase, and nothing in `warehouse/supabase/` names it.
