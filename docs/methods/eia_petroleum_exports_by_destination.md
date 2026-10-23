# U.S. exports of crude oil and petroleum products by destination

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `eia_petroleum_exports_by_destination`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, exports by destination, through EIA's API v2,
route `petroleum/move/expc`:
`https://api.eia.gov/v2/petroleum/move/expc/data/?frequency=monthly&data[]=value&start=2015-01&facets[product][]=EPC0&facets[product][]=EPP0`
(the key is never written). Page: `https://www.eia.gov/dnav/pet/pet_move_expc_a_EP00_EEX_mbblpd_m.htm`. Connector:
`warehouse/connectors/eia_petroleum_exports.py` (session 860).

## Vintage and revision

Monthly, January 2015 to July 2026 when written (139 months). Retrieved 2026-10-23T02:17:24Z. A snapshot: each run
replaces the table whole, so EIA's revisions arrive at the next run with `--fresh` (pages saved in
`warehouse/raw/eia_petroleum_exports/` are reused otherwise; `--offline` asks nothing). Ceiling 11 requests a run (pages
of 5,000, 3 seconds apart). Session 860 made 18 of its 20 requests: route listings, metadata, counts, the product facet,
the trial's nine pages and one more; the write reused them.

## Shape and variables

Series. `entity` `eia_petroleum_exports:<destination>:<product>`, EIA's codes. Destination: `NUS-Z00` the U.S. total,
`NUS-N<country>` a country. Product: `EPC0` crude oil, `EPP0` total petroleum products. `ts_utc` the month's first day,
00:00:00Z; `freq` `P1M`; `geo` `US` (the exporter); `node` EIA's area name and product name (for a country, EIA gives a
three-letter code, such as "CAN, Crude Oil"; the total is "U.S.").

| Variable | Unit | EIA's unit |
|---|---|---|
| `exports` | `kbbl` (the month's barrels) | MBBL |
| `exports_per_day` | `kbbl/d` | MBBL/D |

`exports_per_day` is named as `eia_petroleum_snd_monthly` names it. A value EIA leaves empty has no row; nothing is
filled. A unit not in the map, or a key given twice, stops the run.

When written: 45,058 rows (all 45,058 of EIA's records), 281 series. Crude oil: 79 destinations (the U.S. total
included), 3,278 rows for each variable. Total products: 202 destinations (201 countries and the U.S. total), 19,251 rows
for each variable. A series runs from 1 to 139 months.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of the license reads, `docs/licenses.md`). Verdict
in `docs/licenses.md`: public. Cite "U.S. Energy Information Administration, Petroleum Supply Monthly".

## Cross-check (session 860)

- The U.S. crude total equals `eia_petroleum_snd_monthly`'s U.S. crude exports in every one of the 139 months
  (difference 0).
- The destinations sum to the U.S. total at a median of 1.0000 (0.993 to 1.063 by month and product).

## What it does not hold

- The route's other 40 products: its 42 products since 2015 are 407,028 records (82 pages), more than the session's
  ceiling. Left for a later session.
- Months before January 2015.
- Imports: crude imports by country of origin are in `eia_crude_imports_by_country` and
  `eia_crude_imports_detail_monthly`.
- Any month EIA leaves empty; nothing is filled.
