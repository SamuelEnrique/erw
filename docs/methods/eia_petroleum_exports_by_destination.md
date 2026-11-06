# U.S. exports of crude oil and petroleum products by destination

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `eia_petroleum_exports_by_destination`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, exports by destination, through EIA's API v2,
route `petroleum/move/expc`:
`https://api.eia.gov/v2/petroleum/move/expc/data/?frequency=monthly&data[]=value&start=2015-01&facets[product][]=EPC0&facets[product][]=EPP0`
(the key is never written), and since session 884 the same with `facets[product][]=` each of `EPD0`, `EPM0F`,
`EPJK`, `EPLLPA`, `EPPR`, `EPLLEA`, `EPPC`, sorted by product. Page: `https://www.eia.gov/dnav/pet/pet_move_expc_a_EP00_EEX_mbblpd_m.htm`. Connector:
`warehouse/connectors/eia_petroleum_exports.py` (session 860).

## Vintage and revision

Monthly, January 2015 to July 2026 when written (139 months). Session 860's pages were retrieved 2026-10-23T02:17:24Z
(for session 884's write, see below). A snapshot: each run replaces the table whole, so EIA's revisions arrive at the
next run with `--fresh` (pages saved in `warehouse/raw/eia_petroleum_exports/` are reused otherwise; `--offline` asks
nothing). Ceiling 11 requests a run in
session 860, 30 since session 884, with `--ceiling` to set fewer (pages of 5,000, 3 seconds apart). Session 860 made 18 of its 20 requests: route listings, metadata, counts, the product facet,
the trial's nine pages and one more; the write reused them.

## Shape and variables

Series. `entity` `eia_petroleum_exports:<destination>:<product>`, EIA's codes. Destination: `NUS-Z00` the U.S. total,
`NUS-N<country>` a country. Product: `EPC0` crude oil, `EPP0` total petroleum products, and since session 884 `EPD0`
distillate fuel oil, `EPM0F` finished motor gasoline, `EPJK` kerosene-type jet fuel, `EPLLPA` propane, `EPPR` residual
fuel oil, `EPLLEA` ethane and `EPPC` petroleum coke. The seven are part of `EPP0`'s total: a sum over products leaves
`EPP0` out. `ts_utc` the month's first day,
00:00:00Z; `freq` `P1M`; `geo` `US` (the exporter); `node` EIA's area name and product name (for a country, EIA gives a
three-letter code, such as "CAN, Crude Oil"; the total is "U.S.").

| Variable | Unit | EIA's unit |
|---|---|---|
| `exports` | `kbbl` (the month's barrels) | MBBL |
| `exports_per_day` | `kbbl/d` | MBBL/D |

`exports_per_day` is named as `eia_petroleum_snd_monthly` names it. A value EIA leaves empty has no row; nothing is
filled. A unit not in the map, or a key given twice, stops the run.

When session 860 wrote it: 45,058 rows (all 45,058 of EIA's records), 281 series (since session 884: 112,478 rows,
1,145 series, below). Crude oil: 79 destinations (the U.S. total
included), 3,278 rows for each variable. Total products: 202 destinations (201 countries and the U.S. total), 19,251 rows
for each variable. A series runs from 1 to 139 months.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of the license reads, `docs/licenses.md`). Verdict
in `docs/licenses.md`: public. Cite "U.S. Energy Information Administration, Petroleum Supply Monthly".

## Cross-check (session 860)

- The U.S. crude total equals `eia_petroleum_snd_monthly`'s U.S. crude exports in every one of the 139 months
  (difference 0).
- The destinations sum to the U.S. total at a median of 1.0000 (0.993 to 1.063 by month and product).

## Session 884: seven products

Session 884 (chain 048) added the seven products session 860 left out, from January 2015 to July 2026: distillate fuel
oil (`EPD0`), finished motor gasoline (`EPM0F`), kerosene-type jet fuel (`EPJK`), propane (`EPLLPA`), residual fuel oil
(`EPPR`), ethane (`EPLLEA`) and petroleum coke (`EPPC`). The table was extended in place rather than a table of its own
written, since no page reads it (held from the live set); the archive holds the 67,420 new rows.

How they are asked: the seven as a query of their own, sorted by product, then by period and series, so that a ceiling
reached part way leaves out the product it cut, whole, and names it in the header ("left out whole, the ceiling
reached"); a product EIA gives no record is named "no record from EIA". Crude oil's and the total's pages, saved by
session 860, were reused. Session 884 made 16 of its 20 requests (the API host's robots address, which answers only with
a key error, so there is no robots file to read there; the product list; 14 pages). All seven fitted in 14 pages. The
write, run `20261023T044326Z`, asked nothing (its header: 0 requests of 30) and read the saved pages; that write
stamped every row's `retrieved_at` with its own time, 2026-10-23T04:43:26Z, the crude oil and total rows included. Session
891 corrected the connector (a page reused from `warehouse/raw` carries the time it was really fetched) and wrote the table
again: crude oil's and the total's rows now carry session 860's times (02:15:57 to 02:16:39 UTC), the seven products'
session 884's (04:41:53 to 04:42:56 UTC). Each row's `source_url` is the
query it came from (the key redacted).

When written: 112,478 rows (all 112,478 of EIA's records read; 45,058 before), 1,145 series, 202 destinations, every
product from January 2015 to July 2026 (139 months).

| Product | Rows for each variable | Destinations (the U.S. total included) |
|---|---|---|
| `EPC0` crude oil | 3,278 | 79 |
| `EPP0` total petroleum products | 19,251 | 202 |
| `EPD0` distillate fuel oil | 7,525 | 159 |
| `EPM0F` finished motor gasoline | 6,150 | 147 |
| `EPJK` kerosene-type jet fuel | 3,812 | 121 |
| `EPLLPA` propane | 5,520 | 120 |
| `EPPR` residual fuel oil | 3,256 | 129 |
| `EPLLEA` ethane | 1,641 | 74 |
| `EPPC` petroleum coke | 5,806 | 114 |

Cross-check (session 884), against `EPP0`, EIA's total of petroleum products:

- Over the destinations, the seven are 77 to 83 percent of the total each year (2025: 2,491 million barrels in all,
  propane 649, distillate 456, finished gasoline 284, ethane 211, coke 199, jet fuel 79, residual 41).
- By destination and month, the seven stay within the total in 12,238 of 12,311 destination-months; in 73 (0.6
  percent) EIA's products exceed its own total for that destination (for example the United Kingdom, August 2024, by
  2.3 million barrels; Australia, September 2025, where the total is 0). The table keeps EIA's figures as EIA gives them.
  Recomputed from the table in session 891: the 12,311 include the U.S. total's 139 months; 73 destination-months
  exceed the total by more than 0.1 percent, 88 by any amount.

What changed in this note (session 891): the address now names the second query; the retrieval line names session 860's
pages and the ceiling is 30 since session 884 (it said "Retrieved 2026-10-23T02:17:24Z" and "Ceiling 11 requests a
run"); the product list names the seven; the row and series counts are marked as session 860's (45,058 rows, 281
series); and the route's products not held are 33, not 40.

## What it does not hold

- The route's other 33 products (40 until session 884): its 42 products since 2015 are 407,028 records (82 pages), more
  than session 860's ceiling. Left for a later session.
- Months before January 2015.
- Imports: crude imports by country of origin are in `eia_crude_imports_by_country` and
  `eia_crude_imports_detail_monthly`.
- Any month EIA leaves empty; nothing is filled.
