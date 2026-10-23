# Generation with a signed interconnection agreement

Energy Research Warehouse (ERW), method note written in session 854 (chain 046) for tables first written on 23 October 2026.

Tables: `interconnection_agreements_signed`, `interconnection_agreements_by_grid`

## Sources and builder

Derived from `lbnl_interconnection_queue` (Lawrence Berkeley National Laboratory and GridTracker, Queued Up, 2026
edition: interconnection requests to the end of 2025), held in the warehouse; no request is made. Builder:
`warehouse/derived/interconnection_agreements.py`. This is the All grids tab's headroom row "generation with a signed
interconnection agreement" (`docs/reviews/siting-gaps.md`).

## Which requests count

A request counts when it is still in the queue (Berkeley Lab's status `active` or `suspended`), has a signed
interconnection agreement, and gives no operation date. Berkeley Lab marks an agreement two ways, and neither covers the
other: the study phase "IA Executed" (`ia_phase`) and an agreement date (`ia_date`). On 23 October 2026, of the 9,181
requests still in the queue, 1,101 had both, 1,188 the phase only and 357 the date only; a request with either counts.
124 of them give an operation date and are left out, leaving 2,522. The column `signed_by` says which mark a request
carries (`phase`, `date`, `phase+date`). Nothing is filled or estimated.

## Shape and variables

`interconnection_agreements_signed`: entities, one row a request, the queue table's own `entity_id`; `status` Berkeley
Lab's; `status_date` the agreement date where given; `capacity_mw` the request's MW; `grid` Berkeley Lab's region (the
seven ISOs, West, Southeast); `state`, `county`, `utility`, `transmission_provider`, `fuel` (Berkeley Lab's clean type),
`ia_date`, `ia_phase`, `request_date`, `proposed_date` (the proposed operation date), `signed_by`.

`interconnection_agreements_by_grid`: series, `freq` `P1Y`, `geo` `US`.

| Entity | ts_utc | Variable | Unit |
|---|---|---|---|
| `interconnection_agreements:<grid>` (and `:us`) | 2025-01-01 (the queue at the end of 2025) | `projects_signed`, `active_projects` | count |
| same | same | `mw_signed`, `active_mw` (every request still in the queue) | MW |
| same | same | `signed_share_pct` (signed MW over active MW) | pct |
| `interconnection_agreements:<grid>:<fuel>` | 2025-01-01 | `projects_signed`, `mw_signed` | count, MW |
| `interconnection_agreements:<grid>` (and `:us`) | the year of the agreement | `projects_signed_in_year`, `mw_signed_in_year` (requests that give an agreement date) | count, MW |

When written: 2,522 requests, 499,252 MW signed of 2,001,974 MW still in the queue (24.9 percent); ERCOT 623
requests and 132,566 MW (29.6 percent of its queue), CAISO 94,096 MW (49.3), MISO 67,073 MW (19.2), PJM 44,066 MW
(31.4). 438 summary rows.

## License

Public: Queued Up is CC BY 4.0 (attribute it to Lawrence Berkeley National Laboratory and GridTracker); the selection and
sums are the ERW's arithmetic on it.

## Cross-check (session 854)

The grids sum to the U.S. row (2,522 requests; MW within 0.01 of the U.S. sum, from rounding to two decimals); each
grid's fuels sum to the grid (within 0.02 MW); in every grid the signed MW are no more than the MW still in the queue.

## What it does not hold

- Nameplate MW as the request states it, not the capacity a grid counts toward its reserves (ERCOT's CDR counts wind,
  solar and storage at their ELCCs, `ercot_cdr_reserve_margins`).
- Requests whose agreement Berkeley Lab does not mark, and agreements signed after the file's end (2025).
- The year of agreement for the 1,188 requests marked by phase only.
