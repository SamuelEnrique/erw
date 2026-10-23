# The datacenter tracker's power side, read from the public queue tables: 23 October 2026

Energy Research Warehouse (ERW), session 2102 (chain `queue/done/084-day-23-october-portable-deals-4.md`, portable-laptop). `docs/reviews/datacenters-public-rows-2026-10-23.md` (session 827) found that no row of `datacenter_projects` can be shown and that the power side already draws the queue positions a public ISO stands behind (`datacenter_queue_positions`, 3 rows, 2 of them ERCOT's). This session reads the six ISO queue tables as this machine holds them (`scripts/sync.py`'s restored copies in `warehouse/output`, retrieved 26 to 30 September 2026) for every row that names a data center or a large load and is not yet a row of `datacenter_queue_positions`, and asks which `datacenter_projects` row each would stand behind. Read only; no request; no warehouse row changed; the rows the data chain would add are at the end as a CSV block in the positions table's own shape.

## Read these first

- **Two public rows name a data center and are not in the tracker: 2,800 MW of gas in Hill County, Texas.** ERCOT's queue holds `33INR0005` Bullock Gas (operator Bullock Data Center, LLC) and `33INR0006` Liberty Thermal Energy Center (operator Liberty Data Center I, LLC): each 1,400 MW combined-cycle, Hill County, TX, queued 12 June 2026, proposed in service 1 July 2032, status Active. ERCOT's terms read as public (`license_verdicts.csv`, "may be public").
- **Why the tracker misses them:** `warehouse/derived/datacenter_facilities.py` (session 22) matches its pattern on the queue's `name` and `fuel_technology` fields only (line 215; the table's header says so). Both rows carry "Data Center" in the `operator` field alone. Adding `operator` to the fields the pattern reads is one line of the derived script and a data-machine run; the `matched` word stays honest ("Data Center", from the operator).
- **Neither matches a `datacenter_projects` row.** The tracker's 154 projects name 10 in Texas (Lancaster, Amarillo twice, Hutto, Cedar Creek, Bryan, Willacy County, three with no place), none in Hill County and none with Bullock or Liberty as developer; the join by state and county, or by state and a shared name token, finds no candidate. So the two rows would join the power side as queue positions a public source stands behind, with no news row behind them, as the two ERCOT rows already drawn do.
- **Nothing else moves.** CAISO's and SPP's queues (public) hold no row whose name, fuel, operator or point of interconnection names a data center or a large load. NYISO's one hit (Suffern Quarry Data Center, withdrawn) is already the tracker's third row, and NYISO's terms ask for permission; MISO's queue has no hit; ISO-NE's six wide hits are the word "load" in points of interconnection, not large loads, and ISO-NE's terms ask.

## The counts

| Grid | Verdict (`license_verdicts.csv`) | Queue rows on this machine (retrieved) | Rows naming a data center or large load | Already in `datacenter_queue_positions` | New, public | Matched to a project |
|---|---|---|---|---|---|---|
| ERCOT | may be public | 1,778 (2026-09-30) | 4 | 2 | 2 | 0 |
| CAISO | may be public | 2,278 (2026-09-30) | 0 | 0 | 0 | 0 |
| SPP | may be public | 3,076 (2026-09-30) | 0 | 0 | 0 | 0 |
| NYISO | needs written permission | 1,814 (2026-09-26) | 1 | 1 | held | |
| MISO | needs written permission (paused) | 3,881 (2026-09-30) | 0 | 0 | held | |
| ISO-NE | needs written permission | 1,751 (2026-09-30) | 0 | 0 | held | |

The pattern is the derived script's own `QUEUE_PATTERN` (data center, datacenter, large load, co-located load, digital campus, hyperscale, crypto, bitcoin), applied here to `name`, `fuel_technology`, `operator` and `poi`. A wider pattern (campus, compute, AI, mining, load) was run beside it and found only two ERCOT solar rows (Aurelius 2 and 3, Deaf Smith County, "load" in the point of interconnection), which are not large loads and are not listed.

## The two rows, in full

| Queue id | Name | Operator | County, state | MW | Fuel | Status | Queued | Proposed in service | Point of interconnection |
|---|---|---|---|---|---|---|---|---|---|
| `ercot_queue:33INR0005` | Bullock Gas | Bullock Data Center, LLC | Hill, TX | 1,400.0 | Gas - Combined-Cycle | Active | 2026-06-12 | 2032-07-01 | BULLOCK 345 KV STATION (Bus# 68096) |
| `ercot_queue:33INR0006` | Liberty Thermal Energy Center | Liberty Data Center I, LLC | Hill, TX | 1,400.0 | Gas - Combined-Cycle | Active | 2026-06-12 | 2032-07-01 | LIBERTY 345 KV STATION (Bus# 68092) |

`capacity_mw` is the generation the position asks to connect, not the load it would serve (the positions table's own header says so); 1,400 MW of combined-cycle behind one data-center LLC is, by its name, generation for a co-located load, but the queue does not say so and the tracker should not either beyond the operator's name.

## What the data chain would do (the desktop; this machine writes no warehouse row)

1. `warehouse/derived/datacenter_facilities.py`: add `operator` to the fields `QUEUE_PATTERN` reads (line 215 and the header's sentence at line 229), with a test on a fixture row whose only data-center word is in the operator. The next daily run then writes the two rows into `datacenter_queue_positions` and, through the derived table, into `datacenter_facilities`, under the ERCOT queue's own source and license.
2. Until then, the rows below are what that run would add, taken from ERCOT's queue as this machine holds it (retrieved 2026-09-30T23:32:29Z); the live set's copy may be newer and should be the one written.
3. `energy_deals` holds a deal of 22 October 2026 with the one party "Liberty" (`deal:25e540d2acfd9f1e`, one evidence row from Hart Energy, held). Whether that deal is the Liberty Data Center I position is not known from the tracker's fields and was not looked up (no request); a reader of the held story could say.

## The rows the data chain would add (`datacenter_queue_positions`' shape)

```csv
entity_id,entity_type,name,geo,lat,lon,capacity_mw,status,status_date,operator,source,source_url,retrieved_at,vintage,queue_id,county,state,poi,zone,transmission_owner,fuel_technology,iso_status,queue_date,proposed_in_service_date,actual_in_service_date,withdrawn_date,matched
ercot_queue:33INR0005,project,Bullock Gas,US-TX,,,1400.0,active,,"Bullock Data Center, LLC",ercot:interconnection_queue,https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269363208,2026-09-30T23:32:29Z,2026-09-30T00:00:00Z,33INR0005,Hill,TX,BULLOCK 345 KV STATION (Bus# 68096),,,Gas - Combined-Cycle,Active,2026-06-12,2032-07-01,,,Data Center
ercot_queue:33INR0006,project,Liberty Thermal Energy Center,US-TX,,,1400.0,active,,"Liberty Data Center I, LLC",ercot:interconnection_queue,https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269363208,2026-09-30T23:32:29Z,2026-09-30T00:00:00Z,33INR0006,Hill,TX,LIBERTY 345 KV STATION (Bus# 68092),,,Gas - Combined-Cycle,Active,2026-06-12,2032-07-01,,,Data Center
```

## Decisions made without you (session 2102)

- The verdict column read is `license_verdicts.csv`'s `verdict`, as `public_rows.py` reads it; SPP's `if_commercial` column says "needs written permission", which does not change this review (SPP has no hit).
- The wider pattern's hits are counted in the text and not listed as rows.
- The queue tables read are this machine's restored copies, not the live set's: `scripts/sync.py --check` gave no answer within fifteen minutes and was left running.

## For Samuel's ruling

- None. The change is one field in a derived script's pattern (reversible, a data-machine run) and is listed for the desktop's chain.
