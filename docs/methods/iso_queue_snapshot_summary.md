# The ISO queues summarized from their own snapshots

Energy Research Warehouse (ERW), method note written in session 2953 (chain 157, 6 November 2026) for the table first
written that day.

Table: `iso_queue_snapshot_summary` (series, public). Builder: `warehouse/derived/iso_queue_snapshot_summary.py`. It is
not session 95's `interconnection_queue_summary`, which summarizes Berkeley Lab's queue file (`lbnl_interconnection_queue`).

## Sources

The ISO queue snapshots the warehouse holds whose license allows them out, as `warehouse/connectors/iso_queues.py`
reads them through gridstatus: `caiso_` and `ercot_interconnection_queue` (19 October 2026) and `spp_` (26 October).
**ISO-NE's, MISO's and NYISO's queue tables are held whole for a license since 21 October 2026** (release v1: "license
needed ... needs written permission"), so their figures are not summarized here (session 2957; the first build of
session 2953 took all six, and was rebuilt). Each table holds one
snapshot, which its next pull replaces, so the moves between two snapshots cannot be counted: the queues' own dates stand
for them. NYISO's large-load queue (`nyiso_load_queue`) is not an input.

## What a row is

- **The snapshot** (`iso_queue:<grid>:<fuel group>`, at the snapshot's day): MW and requests by the queue's status
  (active, completed, withdrawn, suspended; a blank status is "unknown").
- **By year** (`iso_queue:<grid>`, the year's first day): MW and requests entered (by queue date), completed (by
  in-service date) and withdrawn (by withdrawn date).
- **The months from request to in-service** by request year: `in_service_dated` (the requests with both dates) and their
  median, only at 5 or more, as session 95's table writes one. Months are days / 30.4375.

## Rules

- **An in-service date counts only on a completed request, on or before the snapshot's day.** SPP's
  `actual_in_service_date` holds the requested dates of active and withdrawn requests too: 1,321 of its 1,969 dated
  rows lie after its snapshot. ERCOT gives dates to 6 active requests, which are not counted.
- **A recent request year's median counts only the requests already in service**, the fastest; it understates that
  year's wait until the rest connect.
- **Fuel groups:** each queue's own label, by the first of these rules that matches (case ignored): solar and storage;
  wind and storage; storage (storage, battery, BAT, BES, ES); solar (solar, photovoltaic, SUN, PV); wind (wind, WND,
  WT); gas (gas, NG, combustion, combined cycle, CC, CT); nuclear; hydro (hydro, WAT, pumped); hybrid (MISO's
  unspecified hybrids); else other; a blank label is unknown.

## License

Public, as its three inputs are (CAISO, ERCOT, SPP).
